# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from ..constants.message import MessageCode, get_message


class ResConfigSettings(models.TransientModel):
    """Màn hình cấu hình SLA trong Settings: 3 tham số của module.

    Logic: đọc/ghi 3 khóa `ir.config_parameter` của module (số ngày lưu
    nhật ký, khoảng "Sắp đến hạn", kích thước lô xử lý nền); chỉ
    `group_sla_manager` được sửa (REQ-SEC-001). Giá trị phải dương, nếu
    không PHẢI bị từ chối (REQ-INT-010 AC2, REQ-INT-012 liên quan X giờ,
    REQ-REL-002 AC3).
    Refs: REQ-INT-010, REQ-INT-012, REQ-REL-002
    """
    _inherit = 'res.config.settings'

    # Refs: REQ-INT-010, REQ-FUNC-035
    sla_event_retention_days = fields.Integer(
        string="SLA Event Log Retention (days)",
        config_parameter='dwo_sla_core.event_retention_days',
        default=365,
        help=('How many days SLA events are kept before being deleted '
              'automatically. Must be greater than 0. Example: 365 keeps one '
              'year of history.'))
    # Refs: REQ-INT-012
    sla_due_soon_hours = fields.Integer(
        string="\"Due Soon\" Window (hours)",
        config_parameter='dwo_sla_core.due_soon_hours',
        default=4,
        help=('Size of the "Due Soon" window in hours: running, not yet '
              'breached tasks whose deadline falls within this window appear '
              'in the Due Soon filter. Example: 4 lists tasks due within 4 '
              'hours.'))
    # Refs: REQ-REL-002
    sla_batch_size = fields.Integer(
        string="Background Processing Batch Size",
        config_parameter='dwo_sla_core.batch_size',
        default=50,
        help=('Maximum number of tasks the background process handles per '
              'run, so a large backlog is worked off over several runs '
              'without blocking the server. Must be greater than 0. Example: '
              '50.'))

    @api.constrains('sla_event_retention_days', 'sla_due_soon_hours', 'sla_batch_size')
    def _check_sla_params_positive(self):
        """Từ chối giá trị tham số SLA <= 0.

        Logic: cả 3 tham số đều là số đếm (ngày, giờ, số task) nên PHẢI
        dương; giá trị 0 hoặc âm không có ý nghĩa và PHẢI bị từ chối.
        Refs: REQ-INT-010 AC2, REQ-REL-002 AC3
        """
        for settings in self:
            if settings.sla_event_retention_days <= 0:
                raise ValidationError(get_message(
                    MessageCode.VAL_LOG_RETENTION_DAYS_POSITIVE))
            if settings.sla_due_soon_hours <= 0:
                raise ValidationError(get_message(
                    MessageCode.VAL_DUE_SOON_HOURS_POSITIVE))
            if settings.sla_batch_size <= 0:
                raise ValidationError(get_message(
                    MessageCode.VAL_BATCH_SIZE_POSITIVE))
