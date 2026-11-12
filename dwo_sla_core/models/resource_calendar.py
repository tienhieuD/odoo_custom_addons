# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.addons.base.models.res_partner import _tz_get


class ResourceCalendar(models.Model):
    """Thêm field kỹ thuật để tìm lại bản sao calendar theo tz (Cách A đã
    chốt cho scope-add "calendar_tz_override"): `resource.calendar.plan_hours()`/
    `get_work_hours_count()` diễn giải giờ làm theo `tz` lưu sẵn trên chính
    bản ghi calendar, không nhận tham số override từ ngoài -- làm đúng cần
    một BẢN SAO calendar cùng mẫu giờ làm (`attendance_ids`) nhưng đổi `tz`.
    `sla_tz_override_source_id` đánh dấu "bản ghi này là bản sao tz của
    calendar kia", dùng để tìm-hoặc-tạo không trùng (xem `sla.time`); không
    ảnh hưởng gì tới calendar bình thường (field luôn trống).
    Refs: scope-add "calendar_tz_override"
    """
    _inherit = 'resource.calendar'

    # Odoo 20 bỏ field `tz` của resource.calendar (múi giờ giờ nằm ở resource.resource
    # và công ty). Module thêm lại để mỗi calendar (và bản sao đổi múi giờ) giữ múi giờ
    # mà SLA đọc giờ làm theo; `sla.time` tự dựng khoảng làm việc theo tz này.
    tz = fields.Selection(
        _tz_get, string="Timezone", required=True,
        default=lambda self: (self.env.context.get('tz') or self.env.company.tz
                              or self.env.user.tz or 'UTC'),
        help=('Timezone in which the working hours of this calendar are read by '
              'the SLA engine. Example: "Asia/Ho_Chi_Minh".'))

    sla_tz_override_source_id = fields.Many2one(
        'resource.calendar', ondelete='cascade', index=True, copy=False,
        help=('Internal: set only on a calendar auto-created by Source Code '
              'Protector\'s SLA module as a timezone variant of another '
              'calendar (same working hours, different timezone). Deleting '
              'the source calendar deletes this variant too. Leave empty on '
              'every normal calendar.'))
    _sla_tz_override_uniq = models.Constraint(
        'unique(sla_tz_override_source_id, tz)',
        "Only one timezone-variant calendar per (source calendar, timezone).")

    def _sla_is_fully_fixed(self):
        """Lịch có khung giờ làm việc xác định (không phải loại `undefined`/linh hoạt).

        Logic: Odoo 20 bỏ `schedule_type`; `calendar_type == 'undefined'` là lịch
        linh hoạt (không có ca làm cố định). Cùng ý nghĩa với `schedule_type ==
        'fully_fixed'` ở 19.
        """
        self.ensure_one()
        return self.calendar_type != 'undefined'

    def _sla_get_tz_variant(self, source, tz):
        """Tìm-hoặc-tạo bản sao của `source` cùng mẫu giờ làm, đổi `tz` thành `tz`.

        Logic: scope-add "calendar_tz_override" (Cách A đã chốt). Tìm trước
        bằng `sla_tz_override_source_id`/`tz` (unique index ở trên đảm bảo
        tối đa 1 bản sao cho mỗi (source, tz)); không có mới tạo, copy
        `attendance_ids`/`global_leave_ids`/`calendar_type` của `source` (bằng
        `copy()` của core). Ngày nghỉ chung chỉ được copy lúc
        tạo; bản sao không tự đồng bộ khi calendar gốc đổi sau đó (hạn chế đã
        biết, plan-improvement-sla-01-review Q2). Hai giao dịch cùng tạo lần đầu có
        thể đụng unique constraint -- bắt `IntegrityError`, rollback tới
        savepoint, tìm lại (giao dịch thắng đã commit xong bản ghi).
        Refs: scope-add "calendar_tz_override"
        """
        Calendar = self.env['resource.calendar'].sudo()
        existing = Calendar.search([
            ('sla_tz_override_source_id', '=', source.id), ('tz', '=', tz)], limit=1)
        if existing:
            return existing
        try:
            with self.env.cr.savepoint():
                return source.copy({
                    'name': "%s (%s)" % (source.name, tz),
                    'tz': tz,
                    'sla_tz_override_source_id': source.id,
                    'global_leave_ids': [(5, 0, 0)] + [
                        (0, 0, {
                            'name': leave.name, 'date_from': leave.date_from,
                            'date_to': leave.date_to, 'count_as': leave.count_as,
                        })
                        for leave in source.global_leave_ids
                    ],
                })
        except Exception:  # noqa: BLE001 -- giao dịch khác thắng unique constraint trước
            return Calendar.search([
                ('sla_tz_override_source_id', '=', source.id), ('tz', '=', tz)], limit=1)
