# -*- coding: utf-8 -*-
from odoo import models


class IrHttp(models.AbstractModel):
    """Đưa danh sách model có SLA vào `session_info` cho chip trạng thái SLA.

    Logic: client chỉ gọi RPC `get_record_sla_summary` khi model của form nằm
    trong danh sách này, nên form của model không có SLA không tốn request.
    Danh sách rỗng khi cờ `dwo_sla_core.show_form_sla_status` tắt hoặc người
    dùng không thuộc `group_sla_user`. Hệ quả chấp nhận: thêm definition cho
    model mới thì phải tải lại trang mới thấy chip.
    Refs: plan-improvement-sla-01-review §6.9
    """
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        result['dwo_sla_models'] = self._dwo_sla_models()
        return result

    def _dwo_sla_models(self):
        """Danh sách tên model được đo SLA mà người dùng hiện tại được thấy chip."""
        enabled = self.env['res.config.settings']._sla_show_form_status()
        if not enabled or not self.env.user.has_group('dwo_sla_core.group_sla_user'):
            return []
        return sorted(self.env['sla.definition'].sudo()._get_hook_models())
