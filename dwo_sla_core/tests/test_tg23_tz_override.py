# -*- coding: utf-8 -*-
"""TG-23: `calendar_tz_override` -- scope-add (Cách A: tự tạo bản sao calendar theo tz).

Refs: 031_scope_additions_contract_sla_fields.md "calendar_tz_override"
"""
from datetime import datetime

from odoo.tests import tagged

from .common import SlaCase, T0

TAGS = ('post_install', '-at_install', 'dwo_sla_core')


@tagged(*TAGS, 'tg_23')
class TestCalendarTzOverride(SlaCase):

    def test_override_shifts_working_hours(self):
        """Lịch FX-CAL-VN (tz Asia/Ho_Chi_Minh, T2-T6 08:00-17:00) gắn vào 1 định
        nghĩa dùng override tz='UTC': giờ làm vẫn 08:00-17:00 nhưng theo UTC, nên
        planned_end_time khác hẳn định nghĩa không override trên cùng lịch gốc."""
        cal = self.make_calendar()
        d_plain = self.make_definition(
            name="D-plain", schedule_source='definition', schedule_id=cal.id, duration=2)
        d_override = self.make_definition(
            name="D-override", schedule_source='definition', schedule_id=cal.id,
            duration=2, calendar_tz_override='UTC')
        t_plain = self.task_of(self.make_partner('NEW'), d_plain)
        t_override = self.task_of(self.make_partner('NEW'), d_override)
        # T0 = 2026-03-02 02:00 UTC = 09:00 ICT (trong giờ làm ICT 08-17).
        self.assertEqual(t_plain.planned_end_time, datetime(2026, 3, 2, 4, 0))
        # Với override UTC, 02:00 UTC đứng TRƯỚC giờ làm 08:00-17:00 UTC của bản sao
        # -> plan_hours dời tới 08:00 UTC rồi cộng 2h.
        self.assertEqual(t_override.planned_end_time, datetime(2026, 3, 2, 10, 0))
        self.assertNotEqual(t_plain.planned_end_time, t_override.planned_end_time)

    def test_override_reuses_cached_clone_no_duplicate(self):
        """2 định nghĩa khác nhau, cùng calendar gốc, cùng tz override -> chỉ 1 bản
        sao calendar được tạo (tìm-hoặc-tạo, không tạo trùng)."""
        cal = self.make_calendar()
        self.make_definition(
            name="D-1", schedule_source='definition', schedule_id=cal.id,
            calendar_tz_override='UTC')
        self.make_definition(
            name="D-2", schedule_source='definition', schedule_id=cal.id,
            calendar_tz_override='UTC')
        self.make_partner('NEW')  # attach cho cả 2 định nghĩa (cùng start_domain)
        clones = self.env['resource.calendar'].search([
            ('sla_tz_override_source_id', '=', cal.id), ('tz', '=', 'UTC')])
        self.assertEqual(len(clones), 1)

    def test_override_does_not_mutate_source_calendar(self):
        """Lịch gốc không bị đổi tz -- chỉ bản sao mới đổi."""
        cal = self.make_calendar()
        self.make_definition(
            schedule_source='definition', schedule_id=cal.id, calendar_tz_override='UTC')
        self.make_partner('NEW')
        cal.invalidate_cache(None, ids=cal.ids)
        self.assertEqual(cal.tz, 'Asia/Ho_Chi_Minh')

    def test_clone_copies_attendance_pattern(self):
        """Bản sao có cùng số dòng giờ làm (attendance_ids) với lịch gốc."""
        cal = self.make_calendar()
        self.make_definition(
            schedule_source='definition', schedule_id=cal.id, calendar_tz_override='UTC')
        self.make_partner('NEW')
        clone = self.env['resource.calendar'].search([
            ('sla_tz_override_source_id', '=', cal.id), ('tz', '=', 'UTC')])
        self.assertEqual(len(clone), 1)
        self.assertEqual(len(clone.attendance_ids), len(cal.attendance_ids))

    def test_no_override_no_clone_created(self):
        """Không cấu hình override -> không tạo bản sao nào (đường phổ biến, không
        tốn chi phí cho định nghĩa không dùng tính năng này)."""
        cal = self.make_calendar()
        self.make_definition(schedule_source='definition', schedule_id=cal.id)
        self.make_partner('NEW')
        clones = self.env['resource.calendar'].search([
            ('sla_tz_override_source_id', '=', cal.id)])
        self.assertFalse(clones)
