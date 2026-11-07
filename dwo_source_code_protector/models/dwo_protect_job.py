import base64
import io
import json
import logging
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import config

_logger = logging.getLogger(__name__)

MAX_ZIP_SIZE_BYTES = 200 * 1024 * 1024  # 200 MB
RESULT_RETENTION_DAYS = 1  # file ket qua (va file goc) chi giu 1 ngay, xem _cron_cleanup_expired
STALE_RUNNING_MINUTES = 30  # xem _cron_fail_stale_jobs


class DwoProtectJob(models.Model):
    """Một phiên protect-module. Chạy ĐỒNG BỘ trong cùng một request (xem ``run_sync``, gọi
    bởi ``wizards/protect_source_wizard.py::action_protect``) — phiên bản Odoo này không có
    sẵn cơ chế background job hiện đại (OWL service registry / ``ir.cron._trigger()``) nên
    không resume qua nhiều cron tick được; nếu zip lớn/nhiều module, request có thể mất một
    lúc, trong lúc đó UI chỉ hiện trạng thái đang tải (hành vi mặc định của Odoo khi chờ phản
    hồi server) chứ không có progress % theo thời gian thực.

    Vẫn là Model thường (không phải Transient): giữ lại lịch sử các lần protect, cho phép
    download lại kết quả, và cho phép dọn dẹp file đã hết hạn qua cron.
    """

    _name = "dwo.protect.job"
    _description = "Source Code Protector — Job"
    _order = "create_date desc"
    _rec_name = "name"

    name = fields.Char(required=True, readonly=True)
    state = fields.Selection(
        [
            ("queued", "Queued"),
            ("running", "Running"),
            ("done", "Done"),
            ("error", "Error"),
        ],
        default="queued",
        required=True,
        readonly=True,
        index=True,
    )
    progress = fields.Float(default=0.0, readonly=True, help="0 to 100.")
    step_description = fields.Char(readonly=True)

    password = fields.Char(
        readonly=True,
        help="Cleared automatically once the job finishes (success or error), to minimise how "
        "long it stays stored.",
    )

    zip_attachment_id = fields.Many2one("ir.attachment", readonly=True)
    zip_size = fields.Integer(readonly=True, help="Size of the uploaded zip, in bytes.")
    module_count = fields.Integer(readonly=True)
    module_index = fields.Integer(readonly=True, help="How many modules have been processed so far.")
    current_module_name = fields.Char(readonly=True)
    module_roots_json = fields.Text(readonly=True)  # danh sach duong dan tuong doi, JSON
    python_version = fields.Char(
        readonly=True,
        help="Python interpreter version of THIS server process (sys.version_info), i.e. the "
        "version the compiled .so/.pyd artifacts in the output zip were built for. Set once "
        "extraction starts; shown so users compiling for several Python versions (e.g. "
        "different Odoo major versions) know which run produced which zip.",
    )

    result_attachment_id = fields.Many2one("ir.attachment", readonly=True)
    result_file = fields.Binary(
        compute="_compute_result_file", readonly=True,
        help="Mirrors result_attachment_id's content so the form view can offer it as a "
        "download without exposing ir.attachment directly.",
    )
    result_filename = fields.Char(compute="_compute_result_file", readonly=True)
    result_rows_json = fields.Text(
        readonly=True,
        help="Per-module results accumulated while running, as JSON -- kept in a plain Text "
        "field (not result_info itself) because an Html field is sanitized on write, which "
        "silently mangles a JSON string. Only _step_finalize turns this into result_info.",
    )
    result_info = fields.Html(readonly=True)
    error_message = fields.Text(readonly=True)

    work_dir = fields.Char(readonly=True)

    date_started = fields.Datetime(readonly=True)
    date_done = fields.Datetime(readonly=True)
    expires_at = fields.Datetime(
        readonly=True,
        help="The uploaded and result zip are deleted after this time (metadata/history stays).",
    )

    zip_size_human = fields.Char(compute="_compute_display_helpers")
    progress_label = fields.Char(compute="_compute_display_helpers")
    is_expired = fields.Boolean(compute="_compute_display_helpers")

    @api.depends(
        "zip_size", "module_count", "module_index", "current_module_name", "state", "expires_at"
    )
    def _compute_display_helpers(self):
        now = fields.Datetime.now()
        for job in self:
            job.zip_size_human = job._human_size(job.zip_size)
            if job.state == "running" and job.module_count:
                job.progress_label = _(
                    "Processing module %(index)s of %(total)s: %(name)s"
                ) % {
                    "index": job.module_index + 1,
                    "total": job.module_count,
                    "name": job.current_module_name or "…",
                }
            else:
                job.progress_label = job.step_description or ""
            job.is_expired = bool(job.expires_at and job.expires_at < now)

    @api.depends("result_attachment_id")
    def _compute_result_file(self):
        for job in self:
            attachment = job.result_attachment_id.sudo()
            # result_file la Binary field thuong (khong phai attachment.datas), nen phai tu
            # base64-encode noi dung "raw" (bytes that, khong qua base64) cua attachment.
            job.result_file = base64.b64encode(attachment.raw) if attachment and attachment.raw else False
            job.result_filename = attachment.name if attachment else False

    @staticmethod
    def _binary_field_to_bytes(value):
        """Normalize a value read from a plain fields.Binary (e.g. the wizard's upload_file)
        to raw bytes. str/bytes/bytearray/memoryview carry base64 TEXT here -- the standard
        Binary-field wire contract on this Odoo version."""
        if not value:
            return b""
        if isinstance(value, (str, bytes, bytearray, memoryview)):
            return base64.b64decode(value)
        return bytes(value)

    @staticmethod
    def _current_python_version():
        """'3.12.3' -- phien ban interpreter dang chay process nay (nen dang COMPILE cho
        phien ban nay, khong phai phien ban zip goc duoc viet)."""
        return ".".join(str(part) for part in sys.version_info[:3])

    @staticmethod
    def _python_version_tag(version_str):
        """'3.12.16' -> 'py31216' (day du major.minor.micro, khong co dau cham de tranh lan
        voi phan ten/timestamp khac trong _output_zip_name)."""
        return "py" + "".join(version_str.split("."))

    @staticmethod
    def _human_size(num_bytes):
        size = float(num_bytes or 0)
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024.0:
                return "{0:.1f} {1}".format(size, unit) if unit != "B" else "{0:.0f} B".format(size)
            size /= 1024.0
        return "{0:.1f} TB".format(size)

    # ------------------------------------------------------------------ #
    # Giới hạn runtime hiện tại của server (hiển thị cho người dùng)      #
    # ------------------------------------------------------------------ #

    @api.model
    def get_runtime_limits(self):
        """Các giới hạn CPU/thời gian hiện đang CẤU HÌNH trên server này, áp dụng cho CHÍNH
        request đang protect module (chế độ đồng bộ, không có cron riêng ở đây).

        Lưu ý: ``limit_time_cpu``/``limit_memory_*`` chỉ thực sự được ÁP DỤNG khi server chạy
        đa worker (``--workers`` > 0); ở chế độ một tiến trình, các số này vẫn hiển thị nhưng
        KHÔNG bị ép buộc.
        """
        workers = config.get("workers", 0) or 0
        return {
            "workers": workers,
            "limits_enforced": bool(workers),
            "limit_time_cpu": config.get("limit_time_cpu", 0),
            "limit_time_real": config.get("limit_time_real", 0),
            "limit_memory_soft": config.get("limit_memory_soft", 0),
            "limit_memory_hard": config.get("limit_memory_hard", 0),
        }

    # ------------------------------------------------------------------ #
    # Tạo job từ wizard, rồi chạy đồng bộ ngay trong cùng request          #
    # ------------------------------------------------------------------ #

    @api.model
    def create_from_upload(self, upload_file_b64, filename, password):
        """Tạo job ở trạng thái 'queued' và lưu zip gốc thành ir.attachment. Chưa xử lý gì
        thêm -- gọi ``run_sync()`` trên record trả về để thực sự chạy."""
        if not upload_file_b64:
            raise UserError(_("Please upload a zip file."))
        filename = filename or ""
        if not filename.lower().endswith(".zip"):
            raise UserError(_("Only .zip files are supported."))

        zip_bytes = self._binary_field_to_bytes(upload_file_b64)
        if len(zip_bytes) > MAX_ZIP_SIZE_BYTES:
            raise UserError(
                _("Zip file is too large (max %d MB).") % (MAX_ZIP_SIZE_BYTES // 1024 // 1024)
            )

        try:
            import jprotect  # noqa: F401
            import pyzipper  # noqa: F401
        except ImportError as exc:
            raise UserError(
                _("Missing Python dependency on the server: %s.\nAsk your administrator to "
                  "run: pip install jprotect pyzipper") % (exc.name or "jprotect/pyzipper")
            )

        attachment = self.env["ir.attachment"].sudo().create({
            "name": filename,
            "raw": zip_bytes,
            "res_model": self._name,
            "mimetype": "application/zip",
        })
        job = self.create({
            "name": filename,
            "state": "queued",
            "password": password or False,
            "zip_attachment_id": attachment.id,
            "zip_size": len(zip_bytes),
            "step_description": _("Queued."),
        })
        attachment.res_id = job.id
        return job

    def run_sync(self):
        """Chạy HẾT các bước (extract, protect từng module, finalize) trong CÙNG MỘT request
        -- gọi ngay sau create_from_upload. Không resume được: nếu request bị server kill
        giữa chừng (chạm limit_time_cpu/limit_time_real), job ở lại 'running' và sẽ được
        _cron_fail_stale_jobs() đánh dấu lỗi sau đó."""
        self.ensure_one()
        while self.state in ("queued", "running"):
            self._process_one_step()

    def _process_one_step(self):
        self.ensure_one()
        try:
            if self.state == "queued":
                self._step_extract_and_discover()
            elif self.module_index < self.module_count:
                self._step_protect_one_module()
            else:
                self._step_finalize()
        except Exception as exc:  # noqa: BLE001 - bat moi loi de job luon ket thuc ro rang
            _logger.exception("dwo_protect_job: job %s failed", self.id)
            self._fail(str(exc))
            return
        self._checkpoint()

    def _checkpoint(self):
        """Commit tien do -- neu request bi server kill NGAY SAU buoc nay, it nhat buoc da
        xong khong bi mat (job o lai 'running' dung cho, _cron_fail_stale_jobs se don sau).
        Bo qua duoi test runner, noi TransactionCase chu dong chan cr.commit() (xem
        odoo/tests/common.py) -- test se rollback toan bo nen khong can bao ve o day."""
        if not config["test_enable"]:
            self.env.cr.commit()

    def _temp_base(self):
        base = os.path.join(config.get("data_dir", tempfile.gettempdir()), "dwo_protect_jobs")
        os.makedirs(base, exist_ok=True)
        return base

    def _step_extract_and_discover(self):
        from jprotect.errors import JProtectError  # noqa: F401 - bao dam dependency co that

        work_dir = tempfile.mkdtemp(dir=self._temp_base(), prefix="job%s_" % self.id)
        extract_dir = os.path.join(work_dir, "src")
        os.makedirs(extract_dir)

        zip_bytes = self.zip_attachment_id.sudo().raw
        password_bytes = self.password.encode() if self.password else None
        self._safe_extract(zip_bytes, extract_dir, password_bytes)

        roots = self._find_module_roots(extract_dir)
        if not roots:
            raise UserError(
                _("No Odoo module found in the zip. Each module must contain a __manifest__.py file.")
            )
        rel_roots = [os.path.relpath(r, extract_dir) for r in roots]

        self.write({
            "state": "running",
            "work_dir": work_dir,
            "module_roots_json": json.dumps(rel_roots),
            "module_count": len(rel_roots),
            "module_index": 0,
            "date_started": fields.Datetime.now(),
            "progress": 5.0,
            "step_description": _("Extracted the zip, found %d module(s).") % len(rel_roots),
            "python_version": self._current_python_version(),
        })
        # Mat khau chi can dung mot lan nua luc nen ket qua (buoc finalize) -- da dung roi thi
        # giu nguyen, se xoa han o _step_finalize.

    def _step_protect_one_module(self):
        from jprotect.config.schema import ProtectConfig
        from jprotect.core.pipeline import run_pipeline
        from jprotect.errors import JProtectError

        extract_dir = os.path.join(self.work_dir, "src")
        rel_roots = json.loads(self.module_roots_json or "[]")
        idx = self.module_index
        rel_root = rel_roots[idx]
        root = os.path.join(extract_dir, rel_root)
        module_name = os.path.basename(root)

        out_base = os.path.join(self.work_dir, "out")
        os.makedirs(out_base, exist_ok=True)
        out_path = os.path.join(out_base, module_name)

        # result_info giu tam JSON trong luc chay (xem _load_result_rows/_save_result_rows),
        # chi doi sang HTML that o _step_finalize khi job xong.
        rows = self._load_result_rows()

        if os.path.normpath(root) == os.path.normpath(extract_dir):
            rows.append({
                "name": module_name, "status": "Skipped", "transformed": 0, "compiled": 0,
                "reason": _(
                    "__manifest__.py is at the root of the zip, with no enclosing module "
                    "folder. Re-zip with the module's technical folder name at the top, e.g. "
                    "my_module.zip containing my_module/__manifest__.py, my_module/models/... "
                    "(not the files directly at the zip root)."
                ),
            })
        else:
            try:
                cfg = ProtectConfig(input_path=Path(root), output_path=Path(out_path), compile=True)
                report = run_pipeline(cfg)
                transformed = report.get("transformed_count", 0)
                compiled = report.get("compiled_count", 0)
                if transformed == 0:
                    rows.append({
                        "name": module_name, "status": "Skipped", "transformed": 0, "compiled": 0,
                        "reason": _("No protectable methods found (no models/ with business logic?)"),
                    })
                else:
                    shutil.rmtree(root)
                    shutil.move(out_path, root)
                    rows.append({
                        "name": module_name, "status": "Protected",
                        "transformed": transformed, "compiled": compiled, "reason": "",
                    })
            except JProtectError as exc:
                rows.append({
                    "name": module_name, "status": "Skipped", "transformed": 0, "compiled": 0,
                    "reason": str(exc),
                })
            except Exception as exc:  # noqa: BLE001 - mot module loi khong duoc lam hong ca job
                _logger.exception("dwo_protect_job: module %s failed", module_name)
                rows.append({
                    "name": module_name, "status": "Skipped", "transformed": 0, "compiled": 0,
                    "reason": str(exc),
                })

        self._save_result_rows(rows)
        new_index = idx + 1
        self.write({
            "module_index": new_index,
            "current_module_name": module_name,
            "progress": 5.0 + 85.0 * new_index / max(self.module_count, 1),
            "step_description": _("Protected module %(i)s of %(n)s: %(name)s") % {
                "i": new_index, "n": self.module_count, "name": module_name,
            },
        })

    def _step_finalize(self):
        extract_dir = os.path.join(self.work_dir, "src")
        password_bytes = self.password.encode() if self.password else None
        output_zip_bytes = self._zip_dir(extract_dir, password_bytes)
        output_filename = self._output_zip_name(
            self.name, record_id=self.id, python_version=self.python_version
        )

        attachment = self.env["ir.attachment"].sudo().create({
            "name": output_filename,
            "raw": output_zip_bytes,
            "res_model": self._name,
            "res_id": self.id,
            "mimetype": "application/zip",
        })
        rows = self._load_result_rows()
        self.write({
            "state": "done",
            "progress": 100.0,
            "step_description": _("Done."),
            "result_attachment_id": attachment.id,
            "result_info": self._format_result(rows),
            "date_done": fields.Datetime.now(),
            "expires_at": fields.Datetime.now() + self._retention_timedelta(),
            "password": False,  # khong can giu mat khau nua, xoa som nhat co the
        })
        self._cleanup_work_dir()

    def _fail(self, message):
        self.write({
            "state": "error",
            "step_description": _("Failed."),
            "error_message": message,
            "date_done": fields.Datetime.now(),
            "expires_at": fields.Datetime.now() + self._retention_timedelta(),
            "password": False,
        })
        self._cleanup_work_dir()
        self._checkpoint()

    @api.model
    def _retention_timedelta(self):
        from datetime import timedelta
        return timedelta(days=RESULT_RETENTION_DAYS)

    def _cleanup_work_dir(self):
        if self.work_dir and os.path.isdir(self.work_dir):
            shutil.rmtree(self.work_dir, ignore_errors=True)

    # ------------------------------------------------------------------ #
    # Luu danh sach ket qua tam thoi trong qua trinh chay (result_rows_json, #
    # chi KET QUA CUOI CUNG moi duoc doi sang result_info (HTML) o finalize) #
    # ------------------------------------------------------------------ #

    def _load_result_rows(self):
        raw = self.result_rows_json
        if not raw:
            return []
        return json.loads(raw)

    def _save_result_rows(self, rows):
        self.result_rows_json = json.dumps(rows)

    # ------------------------------------------------------------------ #
    # Helper giai nen an toan, tim module, nen ket qua                    #
    # ------------------------------------------------------------------ #

    def _safe_extract(self, zip_bytes, dest, password):
        import pyzipper

        dest_path = Path(dest).resolve()
        try:
            with pyzipper.AESZipFile(io.BytesIO(zip_bytes)) as zf:
                if password:
                    zf.setpassword(password)
                for member in zf.infolist():
                    member_path = (dest_path / member.filename).resolve()
                    if not str(member_path).startswith(str(dest_path) + os.sep) and member_path != dest_path:
                        _logger.warning("dwo_protect_job: skipping suspicious zip entry %s", member.filename)
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

    def _find_module_roots(self, root):
        found = []
        root_path = Path(root)
        for manifest in sorted(root_path.rglob("__manifest__.py")):
            module_dir = manifest.parent
            if any(
                str(module_dir).startswith(str(existing) + os.sep)
                for existing in map(Path, found)
            ):
                continue
            found.append(str(module_dir))
        return found

    def _zip_dir(self, source_dir, password):
        import pyzipper

        buf = io.BytesIO()
        source_path = Path(source_dir)
        with pyzipper.AESZipFile(buf, "w", compression=pyzipper.ZIP_DEFLATED) as zf:
            if password:
                zf.setpassword(password)
                zf.setencryption(pyzipper.WZ_AES, nbits=256)
            for file_path in sorted(source_path.rglob("*")):
                if file_path.is_file():
                    zf.write(file_path, file_path.relative_to(source_path))
        return buf.getvalue()

    def _output_zip_name(self, upload_filename, record_id=None, timestamp=None, python_version=None):
        """Ten file ket qua gom tag phien ban Python da compile (de biet .so/.pyd trong zip
        danh cho ban Python nao) + timestamp + id cua record job (khi co record_id), de 2 ban
        download tu 2 job khac nhau (hoac tai lai cung 1 job) khong bao gio trung ten tren
        may nguoi dung."""
        stem = upload_filename
        if stem.lower().endswith(".zip"):
            stem = stem[:-4]
        py_tag = self._python_version_tag(python_version or self._current_python_version())
        if not record_id:
            return "{0}_compile_{1}.zip".format(stem, py_tag)
        ts = (timestamp or fields.Datetime.now()).strftime("%Y%m%d%H%M%S")
        return "{0}_compile_{1}_{2}_{3}.zip".format(stem, py_tag, ts, record_id)

    def _format_result(self, rows):
        row_html = []
        for r in rows:
            if r["status"] == "Protected":
                badge = '<span style="color:#1a7e37;font-weight:bold;">Protected</span>'
                detail = "methods protected: {0}, compiled: {1}".format(r["transformed"], r["compiled"])
            else:
                badge = '<span style="color:#b55a00;font-weight:bold;">Skipped</span>'
                detail = r["reason"] or "No protectable methods"
            row_html.append(
                "<tr>"
                "<td style='padding:10px 16px;font-family:monospace;border-bottom:1px solid #eee'>{0}</td>"
                "<td style='padding:10px 16px;border-bottom:1px solid #eee'>{1}</td>"
                "<td style='padding:10px 16px;color:#555;border-bottom:1px solid #eee'>{2}</td>"
                "</tr>".format(r["name"], badge, detail)
            )
        return (
            "<table style='border-collapse:collapse;width:100%;table-layout:fixed'>"
            "<thead><tr style='background:#f5f5f5'>"
            "<th style='padding:10px 16px;text-align:left;width:25%'>Module</th>"
            "<th style='padding:10px 16px;text-align:left;width:15%'>Status</th>"
            "<th style='padding:10px 16px;text-align:left;width:60%'>Detail</th>"
            "</tr></thead><tbody>" + "".join(row_html) + "</tbody></table>"
        )

    # ------------------------------------------------------------------ #
    # Don dep: file het han (1 ngay), work_dir mo coi, va job "mo coi"     #
    # (ket o running/queued vi request bi server kill giua chung)         #
    # ------------------------------------------------------------------ #

    @api.model
    def _cron_cleanup_expired(self):
        now = fields.Datetime.now()
        jobs = self.sudo().search([
            ("state", "in", ("done", "error")),
            ("expires_at", "<=", now),
            "|", ("zip_attachment_id", "!=", False), ("result_attachment_id", "!=", False),
        ])
        for job in jobs:
            attachments = job.zip_attachment_id | job.result_attachment_id
            attachments.sudo().unlink()
            job.write({
                "zip_attachment_id": False,
                "result_attachment_id": False,
                "step_description": _("Expired — the uploaded and result files were deleted after %d day(s).")
                % RESULT_RETENTION_DAYS,
            })
        # Don luon work_dir mo coi (job bi kill giua chung, chua kip _cleanup_work_dir) qua 1 ngay.
        base = self._temp_base()
        cutoff = time.time() - 86400
        for entry in os.scandir(base):
            if entry.is_dir() and entry.stat().st_mtime < cutoff:
                shutil.rmtree(entry.path, ignore_errors=True)

    @api.model
    def _cron_fail_stale_jobs(self):
        """Che do dong bo khong co gi resume job bi do dang: neu request bi server kill giua
        chung (cham limit_time_cpu/limit_time_real), job o lai 'queued'/'running' vinh vien.
        Danh dau loi sau STALE_RUNNING_MINUTES de nguoi dung thay va thu lai, thay vi job
        "treo" trong lich su khong bao gio ket thuc."""
        from datetime import timedelta

        cutoff = fields.Datetime.now() - timedelta(minutes=STALE_RUNNING_MINUTES)
        stale_jobs = self.sudo().search([
            ("state", "in", ("queued", "running")),
            ("create_date", "<=", cutoff),
        ])
        for job in stale_jobs:
            job._fail(_(
                "This job did not finish within %d minutes and is assumed to have been "
                "interrupted (e.g. the server hit its request time/memory limit partway "
                "through). Try again with a smaller zip, or check the server's limits in "
                "Settings > Source Code Protector."
            ) % STALE_RUNNING_MINUTES)
