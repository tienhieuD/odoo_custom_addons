import base64
import io
import logging
import os
import shutil
import tempfile
from pathlib import Path

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import config

_logger = logging.getLogger(__name__)

MAX_ZIP_SIZE_BYTES = 200 * 1024 * 1024  # 200 MB


class DwoProtectSourceWizard(models.TransientModel):
    _name = "dwo.protect.source.wizard"
    _description = "Source Code Protector"

    state = fields.Selection(
        [("choose", "choose"), ("get", "get")],
        default="choose",
    )
    upload_file = fields.Binary("Module Zip", attachment=False)
    upload_filename = fields.Char()
    password = fields.Char(
        "Zip Password",
        help="Used to decrypt the input zip (if encrypted) and to encrypt the output zip with the same password.",
    )
    output_file = fields.Binary("Protected Zip", readonly=True, attachment=False)
    output_filename = fields.Char(readonly=True)
    result_info = fields.Html("Result", readonly=True)

    # ------------------------------------------------------------------ #
    # Public action                                                        #
    # ------------------------------------------------------------------ #

    def action_protect(self):
        self.ensure_one()
        if not self.upload_file:
            raise UserError(_("Please upload a zip file."))
        filename = self.upload_filename or ""
        if not filename.lower().endswith(".zip"):
            raise UserError(_("Only .zip files are supported."))

        try:
            import pyzipper  # noqa: F401
        except ImportError:
            raise UserError(
                _(
                    "Missing Python dependency: pyzipper.\n"
                    "Run: pip install pyzipper"
                )
            )
        try:
            from jprotect.config.schema import ProtectConfig
            from jprotect.core.pipeline import run_pipeline
            from jprotect.errors import JProtectError
        except ImportError:
            raise UserError(
                _(
                    "Missing Python dependency: jprotect.\n"
                    "Run: pip install jprotect"
                )
            )

        zip_bytes = base64.b64decode(self.upload_file)
        if len(zip_bytes) > MAX_ZIP_SIZE_BYTES:
            raise UserError(
                _("Zip file is too large (max %d MB).") % (MAX_ZIP_SIZE_BYTES // 1024 // 1024)
            )

        password_bytes = self.password.encode() if self.password else None
        work_dir = tempfile.mkdtemp(dir=self._temp_base(), prefix="jp_")
        try:
            extract_dir = os.path.join(work_dir, "src")
            os.makedirs(extract_dir)
            self._safe_extract(zip_bytes, extract_dir, password_bytes)

            roots = self._find_module_roots(extract_dir)
            if not roots:
                raise UserError(
                    _(
                        "No Odoo module found in the zip. "
                        "Each module must contain a __manifest__.py file."
                    )
                )

            out_base = os.path.join(work_dir, "out")
            os.makedirs(out_base)

            results = []
            for root in roots:
                module_name = os.path.basename(root)
                out_path = os.path.join(out_base, module_name)
                try:
                    cfg = ProtectConfig(
                        input_path=Path(root),
                        output_path=Path(out_path),
                        compile=True,
                    )
                    report = run_pipeline(cfg)
                    transformed = report.get("transformed_count", 0)
                    compiled = report.get("compiled_count", 0)
                    if transformed == 0:
                        results.append(
                            {
                                "name": module_name,
                                "status": "Skipped",
                                "reason": "No protectable methods found (no models/ with business logic?)",
                                "transformed": 0,
                                "compiled": 0,
                            }
                        )
                    else:
                        shutil.rmtree(root)
                        shutil.move(out_path, root)
                        results.append(
                            {
                                "name": module_name,
                                "status": "Protected",
                                "reason": "",
                                "transformed": transformed,
                                "compiled": compiled,
                            }
                        )
                        _logger.info("jProtect: protected module %s (%d methods)", module_name, transformed)
                except JProtectError as exc:
                    results.append(
                        {
                            "name": module_name,
                            "status": "Skipped",
                            "reason": str(exc),
                            "transformed": 0,
                            "compiled": 0,
                        }
                    )
                    _logger.warning("jProtect: skipped %s — %s", module_name, exc)
                except Exception as exc:  # noqa: BLE001
                    results.append(
                        {
                            "name": module_name,
                            "status": "Skipped",
                            "reason": str(exc),
                            "transformed": 0,
                            "compiled": 0,
                        }
                    )
                    _logger.exception("jProtect: unexpected error on %s", module_name)

            output_zip_bytes = self._zip_dir(extract_dir, password_bytes)
            output_filename = self._output_zip_name(filename)
            result_html = self._format_result(results)

            self.write(
                {
                    "output_file": base64.b64encode(output_zip_bytes),
                    "output_filename": output_filename,
                    "result_info": result_html,
                    "state": "get",
                }
            )
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _temp_base(self):
        base = os.path.join(config.get("data_dir", tempfile.gettempdir()), "jprotect_tmp")
        os.makedirs(base, exist_ok=True)
        return base

    def _safe_extract(self, zip_bytes: bytes, dest: str, password: bytes | None):
        import pyzipper

        dest_path = Path(dest).resolve()
        try:
            with pyzipper.AESZipFile(io.BytesIO(zip_bytes)) as zf:
                if password:
                    zf.setpassword(password)
                for member in zf.infolist():
                    # zip-slip guard
                    member_path = (dest_path / member.filename).resolve()
                    if not str(member_path).startswith(str(dest_path) + os.sep) and member_path != dest_path:
                        _logger.warning("jProtect: skipping suspicious zip entry %s", member.filename)
                        continue
                    try:
                        zf.extract(member, dest)
                    except RuntimeError as exc:
                        if "password" in str(exc).lower():
                            raise UserError(
                                _("Wrong zip password or the zip is encrypted — please check your password.")
                            ) from exc
                        raise
        except UserError:
            raise
        except Exception as exc:
            if "password" in str(exc).lower() or "encrypted" in str(exc).lower():
                raise UserError(_("Wrong zip password or the zip is encrypted.")) from exc
            raise UserError(_("Failed to open zip file: %s") % exc) from exc

    def _find_module_roots(self, root: str) -> list[str]:
        """Return all Odoo module directories (non-nested) under root."""
        found = []
        root_path = Path(root)
        for manifest in sorted(root_path.rglob("__manifest__.py")):
            module_dir = manifest.parent
            # skip if already inside a found module
            if any(
                str(module_dir).startswith(str(existing) + os.sep)
                for existing in map(Path, found)
            ):
                continue
            found.append(str(module_dir))
        return found

    def _zip_dir(self, source_dir: str, password: bytes | None) -> bytes:
        import pyzipper

        buf = io.BytesIO()
        compression = pyzipper.ZIP_DEFLATED
        source_path = Path(source_dir)
        with pyzipper.AESZipFile(buf, "w", compression=compression) as zf:
            if password:
                zf.setpassword(password)
                zf.setencryption(pyzipper.WZ_AES, nbits=256)
            for file_path in sorted(source_path.rglob("*")):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_path)
                    zf.write(file_path, arcname)
        return buf.getvalue()

    def _output_zip_name(self, upload_filename: str) -> str:
        stem = upload_filename
        if stem.lower().endswith(".zip"):
            stem = stem[:-4]
        return f"{stem}_compile.zip"

    def _format_result(self, results: list[dict]) -> str:
        rows = []
        for r in results:
            if r["status"] == "Protected":
                badge = '<span style="color:#1a7e37;font-weight:bold;">✔ Protected</span>'
                detail = f"methods protected: {r['transformed']}, compiled: {r['compiled']}"
            else:
                badge = '<span style="color:#b55a00;font-weight:bold;">⚠ Skipped</span>'
                detail = r["reason"] or "No protectable methods"
            rows.append(
                f"<tr>"
                f"<td style='padding:4px 8px;font-family:monospace'>{r['name']}</td>"
                f"<td style='padding:4px 8px'>{badge}</td>"
                f"<td style='padding:4px 8px;color:#555;font-size:0.9em'>{detail}</td>"
                f"</tr>"
            )
        table = (
            "<table style='border-collapse:collapse;width:100%'>"
            "<thead><tr style='background:#f5f5f5'>"
            "<th style='padding:6px 8px;text-align:left'>Module</th>"
            "<th style='padding:6px 8px;text-align:left'>Status</th>"
            "<th style='padding:6px 8px;text-align:left'>Detail</th>"
            "</tr></thead>"
            "<tbody>" + "".join(rows) + "</tbody>"
            "</table>"
        )
        return table

    # ------------------------------------------------------------------ #
    # Vacuum                                                               #
    # ------------------------------------------------------------------ #

    @api.autovacuum
    def _gc_temp_dirs(self):
        import time

        base = self._temp_base()
        cutoff = time.time() - 86400  # 1 day
        for entry in os.scandir(base):
            if entry.name.startswith("jp_") and entry.stat().st_mtime < cutoff:
                shutil.rmtree(entry.path, ignore_errors=True)
                _logger.info("jProtect autovacuum: removed %s", entry.path)
