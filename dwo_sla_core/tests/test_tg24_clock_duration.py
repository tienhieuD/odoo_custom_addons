# -*- coding: utf-8 -*-
"""TG-24: `original_breach_time`, `duration`/`pause_duration` (bản giờ đồng hồ) --
scope-add, khớp `task_sla.original_breach_time`/`duration`/`pause_duration` của SN.

Refs: 032_task_sla_field_gaps.md
"""
from datetime import datetime

from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')


def ict(day, hour, minute=0):
    return datetime(2026, 3, day, hour, minute) - hours(7)


@tagged(*TAGS, 'tg_24')
class TestOriginalBreachTime(SlaCase):

    def test_set_once_at_attach_never_rewritten_on_resume(self):
        d = self.make_definition(schedule_source='none')
        p = self.make_partner('NEW')
        t = self.task_of(p, d)
        original = t.original_breach_time
        self.assertEqual(original, T0 + hours(4))

        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        self.write(p, {'ref': 'WORK'}, T0 + hours(3))  # resume sau 2h paused
        t.invalidate_cache(None, ids=t.ids)
        # planned_end_time bị dời ra 2h (giống _resume bình thường); original_breach_time
        # giữ nguyên deadline hứa lúc attach.
        self.assertEqual(t.original_breach_time, original)
        self.assertEqual(t.planned_end_time, original + hours(2))
        self.assertNotEqual(t.planned_end_time, t.original_breach_time)

    def test_unaffected_by_action_recalculate(self):
        d = self.make_definition(schedule_source='none')
        p = self.make_partner('NEW')
        t = self.task_of(p, d)
        original = t.original_breach_time
        mgr = self.make_user('mgr-recalc', sla_group='manager')
        t.with_user(mgr).action_recalculate()
        t.invalidate_cache(None, ids=t.ids)
        self.assertEqual(t.original_breach_time, original)


@tagged(*TAGS, 'tg_24')
class TestClockDuration(SlaCase):

    def test_equals_business_without_calendar(self):
        """Không có calendar (24x7) -> duration/pause_duration (clock) bằng đúng
        business_duration/business_pause_duration."""
        d = self.make_definition(schedule_source='none')
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(2))
        self.write(p, {'ref': 'WORK'}, T0 + hours(5))
        self.write(p, {'ref': 'DONE'}, T0 + hours(9))
        t = self.task_of(p, d)
        self.assertEqual(t.business_duration, t.duration)
        self.assertEqual(t.business_pause_duration, t.pause_duration)
        self.assertAlmostEqual(t.pause_duration, 3.0, places=3)
        self.assertAlmostEqual(t.duration, 6.0, places=3)  # 9h - 3h paused

    def test_differs_from_business_across_weekend(self):
        """Lịch T2-T6 08:00-17:00 ICT; pause đúng từ thứ Sáu 17:00 tới thứ Hai 08:00
        (giờ làm = 0h, giờ đồng hồ = 63h) -> business_pause_duration != pause_duration."""
        cal = self.make_calendar()
        d = self.make_definition(schedule_source='definition', schedule_id=cal.id)
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, ict(6, 17))   # Thứ Sáu 17:00 ICT (hết giờ làm)
        self.write(p, {'ref': 'WORK'}, ict(9, 8))    # Thứ Hai kế tiếp 08:00 ICT (vào giờ làm)
        t = self.task_of(p, d)
        self.assertAlmostEqual(t.business_pause_duration, 0.0, places=3)
        self.assertAlmostEqual(t.pause_duration, 63.0, places=3)
        self.assertNotEqual(t.business_pause_duration, t.pause_duration)
