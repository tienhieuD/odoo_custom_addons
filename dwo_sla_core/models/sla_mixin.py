# -*- coding: utf-8 -*-
from odoo import fields, models


class SlaMixin(models.AbstractModel):
    """Mixin dùng chung: nút thông minh nêu số task SLA đang chạy/đã vi phạm.

    Logic: model kế thừa `sla.mixin` (opt-in, không tự động áp dụng cho mọi
    model như Hook ở REQ-FUNC-004) để có sẵn trường đếm và hành động mở
    danh sách task lọc đúng record; model kế thừa tự thêm nút
    `action_view_sla_tasks` lên form view của mình (1 nút `oe_stat_button`
    duy nhất trong `oe_button_box`, số = `sla_task_active_count`, đổi màu đỏ
    khi `sla_task_breach_count > 0` qua `decoration-danger`), kèm `groups`
    giới hạn nhóm SLA (AC2) — mixin chỉ cung cấp dữ liệu/hành động, không ép
    view.
    Refs: REQ-INT-014, D13 (TASKS.md, smart button trên record gốc)
    """
    _name = 'sla.mixin'
    _description = "SLA Mixin"

    sla_task_count = fields.Integer(
        string="SLA Task Count", compute='_compute_sla_task_count',
        help=('Total number of SLA tasks ever run on this record (any '
              'stage). Example: 3 across several past tickets reopened.'))
    sla_task_active_count = fields.Integer(
        string="Active SLA Tasks", compute='_compute_sla_task_count',
        help=('Number of SLA tasks currently running or paused on this '
              'record; shown as the number on the smart button. Example: 2 '
              'when both a response and a resolution SLA are in progress.'))
    sla_task_breach_count = fields.Integer(
        string="Breached SLA Tasks", compute='_compute_sla_task_count',
        help=('Number of active SLA tasks on this record already past their '
              'deadline; a positive value turns the smart button red. '
              'Example: 1 when the resolution SLA is late.'))

    def _compute_sla_task_count(self):
        """Đếm task SLA của từng record theo `(res_model, res_id)`.

        Logic: dùng `sudo()` vì `group_sla_user` không có quyền đọc trực
        tiếp `sla.task` qua ACL chuẩn của model kế thừa (ACL của `sla.task`
        độc lập, xem T4) — nút chỉ hiện số, không lộ chi tiết task ngoài
        nhóm SLA do view của model kế thừa đã giới hạn `groups`. 3 field
        đếm 3 tập khác nhau (tổng/đang hoạt động/đang vi phạm) nên gom
        thành 3 `_read_group` riêng, mỗi cái rẻ vì đã lọc theo `res_model`.
        Refs: REQ-INT-014, D13
        """
        Task = self.env['sla.task'].sudo()
        total = dict(Task._sla_read_group(
            [('res_model', '=', self._name), ('res_id', 'in', self.ids)],
            ['res_id'], ['__count']))
        active = dict(Task._sla_read_group(
            [('res_model', '=', self._name), ('res_id', 'in', self.ids),
             ('stage', 'in', ('in_progress', 'paused'))],
            ['res_id'], ['__count']))
        breached = dict(Task._sla_read_group(
            [('res_model', '=', self._name), ('res_id', 'in', self.ids),
             ('stage', 'in', ('in_progress', 'paused')), ('has_breached', '=', True)],
            ['res_id'], ['__count']))
        for record in self:
            record.sla_task_count = total.get(record.id, 0)
            record.sla_task_active_count = active.get(record.id, 0)
            record.sla_task_breach_count = breached.get(record.id, 0)

    def action_view_sla_tasks(self):
        """Mở danh sách task SLA của record đang xem, lọc đúng record đó.

        Refs: REQ-INT-014
        """
        self.ensure_one()
        action = self.env.ref(
            'dwo_sla_core.action_sla_task').sudo().read()[0]  # Odoo 13: no `_for_xml_id`
        action['domain'] = [('res_model', '=', self._name), ('res_id', '=', self.id)]
        action['context'] = {}
        return action
