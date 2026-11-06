import base64
import io
import json
import logging
import os
import shutil
import tempfile
import time
from pathlib import Path

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import config

_logger = logging.getLogger(__name__)

MAX_ZIP_SIZE_BYTES = 200 * 1024 * 1024  # 200 MB
RESULT_RETENTION_DAYS = 1  # file ket qua (va file goc) chi giu 1 ngay, xem _cron_cleanup_expired
BUS_CHANNEL_TYPE = "dwo_protect_job"
MAX_STEP_ATTEMPTS = 3  # xem step_attempts / _step_protect_one_module


class DwoProtectJob(models.Model):
    """Một phiên protect-module chạy NGẦM qua cron, có thể resume qua nhiều lượt cron (xem
    ``_cron_process_queue``): một lượt cron chỉ làm ĐÚNG MỘT BƯỚC nhỏ (giải nén, HOẶC protect
    một module, HOẶC nén kết quả) rồi commit và tự kích hoạt lượt kế tiếp — nhờ vậy một job lớn
    (nhiều module) không bao giờ chạy quá lâu trong MỘT lần gọi cron, giảm rủi ro chạm giới hạn
    CPU/thời gian của server (xem ``get_runtime_limits``), và tiến độ luôn được lưu lại ngay cả
    khi lượt cron đó bị dừng giữa chừng — lượt sau sẽ tiếp tục đúng chỗ dang dở, không mất việc
    đã làm.

    Là Model thường (không phải Transient): phải sống được qua nhiều request/cron tick, và
    người dùng cần xem lại tiến độ/kết quả sau khi rời màn hình rồi quay lại.
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
    step_attempts = fields.Integer(
        default=0, readonly=True,
        help="Retries of the CURRENT module's step. If the server kills the process mid-step "
        "(CPU/time/memory limit), the job is found again still 'running' at the same "
        "module_index with no trace of the failed attempt -- without this counter the cron "
        "would retry the same module forever. See MAX_STEP_ATTEMPTS.",
    )
    module_roots_json = fields.Text(readonly=True)  # danh sach duong dan tuong doi, JSON

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
                    "Processing module %(index)s of %(total)s: %(name)s",
                    index=job.module_index + 1,
                    total=job.module_count,
                    name=job.current_module_name or "…",
                )
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
        to raw bytes, across Odoo's old and new Binary field representations.

        str/bytes/bytearray/memoryview ALWAYS carry base64 TEXT here -- that is the standard
        Binary-field wire contract, true both for Odoo <= 19 (reading the field returns
        exactly that) and for Odoo >= 20 when a caller passes a raw value as a plain argument
        (e.g. tests calling create_from_upload directly) rather than reading it off a record.
        The only thing holding ALREADY-DECODED content is a genuine BinaryValue/BinaryBytes
        instance (see odoo/tools/binary.py), which Odoo >= 20's new ORM (odoo/orm/
        fields_binary.py) returns when you read record.binary_field_name off an actual
        record -- it implements the buffer protocol (__bytes__/__buffer__), so naively
        checking "is this bytes-like" is not enough to tell the two apart; it must be
        distinguished by NOT being one of the plain built-in types above.
        """
        if not value:
            return b""
        if isinstance(value, (str, bytes, bytearray, memoryview)):
            return base64.b64decode(value)
        return bytes(value)  # BinaryValue/BinaryBytes (Odoo 20+ record read): already raw

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
        """Các giới hạn CPU/thời gian/bộ nhớ hiện đang CẤU HÌNH trên server này.

        Lưu ý: ``limit_time_cpu``/``limit_memory_*`` chỉ thực sự được ÁP DỤNG khi server chạy
        đa worker (``--workers`` > 0); ở chế độ một tiến trình (thường gặp lúc phát triển),
        các số này vẫn hiển thị nhưng KHÔNG bị ép buộc. ``limit_time_real_cron`` áp dụng riêng
        cho cron, không phụ thuộc số worker.
        """
        workers = config.get("workers", 0) or 0
        limit_time_real_cron = config.get("limit_time_real_cron", -1)
        if limit_time_real_cron in (None, -1):
            limit_time_real_cron = config.get("limit_time_real", 0)
        return {
            "workers": workers,
            "limits_enforced": bool(workers),
            "limit_time_cpu": config.get("limit_time_cpu", 0),
            "limit_time_real": config.get("limit_time_real", 0),
            "limit_time_real_cron": limit_time_real_cron,
            "limit_memory_soft": config.get("limit_memory_soft", 0),
            "limit_memory_hard": config.get("limit_memory_hard", 0),
        }

    # ------------------------------------------------------------------ #
    # Tạo job từ wizard                                                    #
    # ------------------------------------------------------------------ #

    @api.model
    def create_from_upload(self, upload_file_b64, filename, password):
        """Tạo job ở trạng thái 'queued' và lưu zip gốc thành ir.attachment.

        Chỉ làm việc NHẸ (lưu file, không giải nén/protect gì) để wizard trả lời ngay, đóng
        popup, không bắt người dùng chờ xử lý thật.
        """
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
            "step_description": _("Queued — waiting for the background job to start."),
        })
        attachment.res_id = job.id
        job._trigger_cron_soon()
        return job

    def _trigger_cron_soon(self):
        cron = self.env.ref("dwo_source_code_protector.ir_cron_protect_job_queue", raise_if_not_found=False)
        if cron:
            cron.sudo()._trigger()

    # ------------------------------------------------------------------ #
    # Cron: xu ly hang doi, moi lan goi chi lam DUNG MOT BUOC              #
    # ------------------------------------------------------------------ #

    @api.model
    def _cron_process_queue(self):
        # sudo(): cron co the chay duoi user bat ky tuy cau hinh ir.cron, nhung viec xu ly job
        # (write tien do, tao attachment ket qua...) phai luon thuc hien duoc du la user nao.
        job = self.sudo().search([("state", "in", ("queued", "running"))], order="create_date asc", limit=1)
        if not job:
            return
        job._process_one_step()

    def _process_one_step(self):
        self.ensure_one()
        is_protect_step = self.state == "running" and self.module_index < self.module_count

        if not is_protect_step:
            # Buoc extract (state=="queued") hoac finalize (module_index >= module_count)
            # khong co co che "skip phan nay, di tiep" nhu _step_protect_one_module -- neu bi
            # kill giua chung (limit CPU/thoi gian/memory) nhieu lan lien tiep thi FAIL ca job
            # thay vi de cron thu lai vo han (step_attempts khong con dau vet loi nao de bat,
            # chi la khong tien trien, nen phai dem o day TRUOC khi lam viec nang).
            if self.step_attempts >= MAX_STEP_ATTEMPTS:
                self._fail(
                    _("This step did not complete after %d attempt(s) -- it likely hit a "
                      "server CPU/time/memory limit. See Settings > Source Code Protector "
                      "for this server's current limits.") % self.step_attempts
                )
                return
            self.step_attempts += 1
            self._checkpoint()

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

        if not is_protect_step:
            self.step_attempts = 0  # buoc thanh cong, reset dem cho buoc ke tiep
        self._checkpoint()
        if self.state == "running":
            self._trigger_cron_soon()

    def _checkpoint(self):
        """Commit progress so a kill mid-job (CPU/memory limit, server restart...) does not
        lose steps already done. Skipped under the test runner, where TransactionCase
        deliberately patches cr.commit() to raise (see odoo/tests/common.py) -- a test rolls
        back the whole transaction anyway, so there is nothing to protect there."""
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
        # Xoa output do cua lan thu truoc (neu co) -- tranh retry vap vao file dang do.
        shutil.rmtree(out_path, ignore_errors=True)

        # result_info giu tam JSON trong luc chay (xem _load_result_rows/_save_result_rows),
        # chi doi sang HTML that o _step_finalize khi job xong.
        rows = self._load_result_rows()

        if self.step_attempts >= MAX_STEP_ATTEMPTS:
            # Da thu MAX_STEP_ATTEMPTS lan va lan nao cung bi kill giua chung (khong con dau
            # vet loi nao de bat, chi la module_index/step_attempts khong doi khi cron quay
            # lai) -- rat co kha nang module nay vuot qua limit_time_cpu/limit_time_real_cron/
            # limit_memory_* cua server (xem get_runtime_limits). Bo qua module nay va DI TIEP,
            # khong de job ket thuc khong bao gio.
            rows.append({
                "name": module_name, "status": "Skipped", "transformed": 0, "compiled": 0,
                "reason": _(
                    "Skipped after %d attempt(s) that did not complete -- this usually means "
                    "the server killed the background step partway through (CPU time, real "
                    "time, or memory limit). See Settings > Source Code Protector for this "
                    "server's current limits."
                ) % self.step_attempts,
            })
            self._save_result_rows(rows)
            self.write({
                "module_index": idx + 1,
                "current_module_name": module_name,
                "step_attempts": 0,
                "progress": 5.0 + 85.0 * (idx + 1) / max(self.module_count, 1),
                "step_description": _("Skipped module %(i)s of %(n)s (exceeded retry limit): %(name)s") % {
                    "i": idx + 1, "n": self.module_count, "name": module_name,
                },
            })
            return

        # Ghi nhan LAN THU truoc khi lam viec nang (bien doi + compile Cython) va commit ngay --
        # neu tien trinh bi kill giua chung, lan cron sau se thay step_attempts da tang, chu
        # khong phai bat dau tu 0, va biet day la mot retry (xem kiem tra o tren).
        self.write({"step_attempts": self.step_attempts + 1})
        self._checkpoint()

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
            "step_attempts": 0,
            "progress": 5.0 + 85.0 * new_index / max(self.module_count, 1),
            "step_description": _("Protected module %(i)s of %(n)s: %(name)s") % {
                "i": new_index, "n": self.module_count, "name": module_name,
            },
        })

    def _step_finalize(self):
        extract_dir = os.path.join(self.work_dir, "src")
        password_bytes = self.password.encode() if self.password else None
        output_zip_bytes = self._zip_dir(extract_dir, password_bytes)
        output_filename = self._output_zip_name(self.name, record_id=self.id)

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
        self._notify_user(success=True)

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
        self._notify_user(success=False)

    @api.model
    def _retention_timedelta(self):
        from datetime import timedelta
        return timedelta(days=RESULT_RETENTION_DAYS)

    def _cleanup_work_dir(self):
        if self.work_dir and os.path.isdir(self.work_dir):
            shutil.rmtree(self.work_dir, ignore_errors=True)

    def _notify_user(self, success):
        user = self.create_uid
        if not user or not user.partner_id:
            return
        message = {
            "job_id": self.id,
            "name": self.name,
            "success": success,
            "state": self.state,
            "error_message": self.error_message if not success else False,
        }
        self.env["bus.bus"]._sendone(user.partner_id, BUS_CHANNEL_TYPE, message)

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
    # Helper tai su dung tu wizard cu (giai nen an toan, tim module, nen)  #
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

    def _output_zip_name(self, upload_filename, record_id=None, timestamp=None):
        """Ten file ket qua gom timestamp + id cua record job (khi co record_id), de 2 ban
        download tu 2 job khac nhau (hoac tai lai cung 1 job sau khi retry) khong bao gio
        trung ten tren may nguoi dung."""
        stem = upload_filename
        if stem.lower().endswith(".zip"):
            stem = stem[:-4]
        if not record_id:
            return "{0}_compile.zip".format(stem)
        ts = (timestamp or fields.Datetime.now()).strftime("%Y%m%d%H%M%S")
        return "{0}_compile_{1}_{2}.zip".format(stem, ts, record_id)

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
                "<td style='padding:4px 8px;font-family:monospace'>{0}</td>"
                "<td style='padding:4px 8px'>{1}</td>"
                "<td style='padding:4px 8px;color:#555;font-size:0.9em'>{2}</td>"
                "</tr>".format(r["name"], badge, detail)
            )
        return (
            "<table style='border-collapse:collapse;width:100%'>"
            "<thead><tr style='background:#f5f5f5'>"
            "<th style='padding:6px 8px;text-align:left'>Module</th>"
            "<th style='padding:6px 8px;text-align:left'>Status</th>"
            "<th style='padding:6px 8px;text-align:left'>Detail</th>"
            "</tr></thead><tbody>" + "".join(row_html) + "</tbody></table>"
        )

    # ------------------------------------------------------------------ #
    # Don dep: file het han (1 ngay) va work_dir mo coi                   #
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
