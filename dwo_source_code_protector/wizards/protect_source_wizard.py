from odoo import fields, models


class DwoProtectSourceWizard(models.TransientModel):
    """Upload rồi chạy protect NGAY trong cùng request (xem ``dwo.protect.job.run_sync``,
    model thường, xem ``models/dwo_protect_job.py``) -- phiên bản Odoo này không có cơ chế
    background job hiện đại, nên bấm nút sẽ đợi đến khi xong (UI hiện trạng thái đang tải
    mặc định của Odoo), rồi mở thẳng kết quả (Done hoặc Error đều mở form job, để nguoi dùng
    luôn thấy chi tiết thay vì chỉ một popup lỗi chung chung)."""

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
        job.run_sync()
        return {
            "type": "ir.actions.act_window",
            "res_model": "dwo.protect.job",
            "res_id": job.id,
            "view_mode": "form",
            "target": "current",
        }
