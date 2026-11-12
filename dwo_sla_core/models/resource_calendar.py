# -*- coding: utf-8 -*-
from odoo import fields, models


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

    sla_tz_override_source_id = fields.Many2one(
        'resource.calendar', ondelete='cascade', index=True, copy=False,
        help=('Internal: set only on a calendar auto-created by Source Code '
              'Protector\'s SLA module as a timezone variant of another '
              'calendar (same working hours, different timezone). Deleting '
              'the source calendar deletes this variant too. Leave empty on '
              'every normal calendar.'))
    _sql_constraints = [
        ('sla_tz_override_uniq', 'unique(sla_tz_override_source_id, tz)', "Only one timezone-variant calendar per (source calendar, timezone)."),
    ]


    def _sla_is_fully_fixed(self):
        """Lịch có khung giờ cố định (ở 17 luôn đúng: chưa có lịch linh hoạt; 18 có `flexible_hours`, 19 là `schedule_type == 'fully_fixed'`."""
        self.ensure_one()
        # Odoo 17 has no flexible-hours calendar: every calendar has working hours (18 adds `flexible_hours`)
        return True

    def _sla_get_tz_variant(self, source, tz):
        """Tìm-hoặc-tạo bản sao của `source` cùng mẫu giờ làm, đổi `tz` thành `tz`.

        Logic: scope-add "calendar_tz_override" (Cách A đã chốt). Tìm trước
        bằng `sla_tz_override_source_id`/`tz` (unique index ở trên đảm bảo
        tối đa 1 bản sao cho mỗi (source, tz)); không có mới tạo, copy
        `attendance_ids`/`global_leave_ids`/
        `two_weeks_calendar` của `source`. Ngày nghỉ chung chỉ được copy lúc
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
                return Calendar.create({
                    'name': "%s (%s)" % (source.name, tz),
                    'tz': tz,
                    'two_weeks_calendar': source.two_weeks_calendar,
                    'sla_tz_override_source_id': source.id,
                    'attendance_ids': [
                        (0, 0, {
                            'name': att.name, 'dayofweek': att.dayofweek,
                            'hour_from': att.hour_from, 'hour_to': att.hour_to,
                            'day_period': att.day_period,
                            'week_type': att.week_type,
                            'display_type': att.display_type,
                            'sequence': att.sequence,
                        })
                        for att in source.attendance_ids
                    ],
                    'global_leave_ids': [
                        (0, 0, {
                            'name': leave.name, 'date_from': leave.date_from,
                            'date_to': leave.date_to, 'time_type': leave.time_type,
                        })
                        for leave in source.global_leave_ids
                    ],
                })
        except Exception:  # noqa: BLE001 -- giao dịch khác thắng unique constraint trước
            return Calendar.search([
                ('sla_tz_override_source_id', '=', source.id), ('tz', '=', tz)], limit=1)
