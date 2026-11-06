from odoo import _, fields, models


class DwoProtectSourceWizard(models.TransientModel):
    """Chỉ để UPLOAD. Việc giải nén/protect/nén thật sự chạy NGẦM qua
    ``dwo.protect.job`` (model thường, xem ``models/dwo_protect_job.py``) — bấm nút là wizard
    tạo job rồi ĐÓNG NGAY, không bắt người dùng chờ xử lý trong popup.
    """

    _name = "dwo.protect.source.wizard"
    _description = "Source Code Protector — Upload"

    upload_file = fields.Binary("Module Zip", attachment=False)
    upload_filename = fields.Char()
    password = fields.Char(
        help="Used to decrypt the input zip (if encrypted) and to encrypt the output zip with "
        "the same password.",
    )

    def action_protect(self):
        self.ensure_one()
        job = self.env["dwo.protect.job"].create_from_upload(
            self.upload_file, self.upload_filename, self.password
        )
        # Dong popup ngay va bao bang toast: xu ly that chay ngam qua cron, nguoi dung theo doi
        # tien do o man hinh job (menu rieng trong Settings, hoac toast luc xong se dan toi do).
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Queued"),
                "message": _(
                    "%s was queued for protection. It now runs in the background — you can "
                    "close this and do something else; you'll get a notification when it's done."
                ) % (self.upload_filename or ""),
                "type": "success",
                "next": {
                    "type": "ir.actions.act_window_close",
                    "infos": {"job_id": job.id},
                },
            },
        }
