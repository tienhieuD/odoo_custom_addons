# -*- coding: utf-8 -*-
"""TG-11: đổi cấu hình khi đang chạy, tính lại, archive, xóa định nghĩa (docs/060 TC-CHG-*).

Refs: REQ-FUNC-021, 031, 044, 052, 053, 060, 061, REQ-INT-005
"""
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')


@tagged(*TAGS, 'tg_11')
class TestChangeConfig(SlaCase):

    def setUp(self):
        super().setUp()
        self.d = self.make_definition()
        self.manager = self.make_user('sla_mgr_chg', 'manager')
        self.viewer = self.make_user('sla_usr_chg', 'user')

    def test_chg_001_running_task_keeps_target(self):
        """TC-CHG-001: sửa mục tiêu 4 -> 8 giờ không đổi task đang chạy."""
        p = self.make_partner('NEW')
        t = self.task_of(p, self.d)
        planned_end_time = t.planned_end_time
        self.d.duration = 8
        self.assertEqual(t.target_duration, 4)
        self.assertEqual(t.planned_end_time, planned_end_time)

    def test_chg_003_new_task_uses_new_target(self):
        """TC-CHG-003: task gắn mới sau khi sửa dùng mục tiêu mới."""
        self.d.duration = 8
        t = self.task_of(self.make_partner('NEW'), self.d)
        self.assertEqual(t.target_duration, 8)
        self.assertEqual(t.planned_end_time, T0 + hours(8))

    def test_chg_007_recalculate_applies_new_target(self):
        """TC-CHG-007: Tính lại áp mục tiêu mới, planned_end_time = hiện tại + phần còn lại."""
        t = self.task_of(self.make_partner('NEW'), self.d)
        self.d.duration = 8
        now = T0 + hours(1)
        with self.at(now):
            t.with_user(self.manager).action_recalculate()
        self.assertEqual(t.target_duration, 8)
        self.assertEqual(t.planned_end_time, now + hours(8))

    def test_chg_006_recalculate_keeps_elapsed(self):
        """TC-CHG-006: Tính lại giữ phần đã trôi (3 giờ) khi đổi mục tiêu."""
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(3))
        self.write(p, {'ref': 'WORK'}, T0 + hours(3))
        t = self.task_of(p, self.d)
        self.assertAlmostEqual(t.business_duration, 3.0, places=2)
        self.d.duration = 5
        now = T0 + hours(3)
        with self.at(now):
            t.with_user(self.manager).action_recalculate()
        self.assertAlmostEqual(t.business_duration, 3.0, places=2)
        self.assertEqual(t.planned_end_time, now + hours(2))

    def test_chg_008_010_recalculate_ignores_finished(self):
        """TC-CHG-008/009/010: task achieved/breached/cancelled không đổi khi Tính lại."""
        achieved = self.make_partner('NEW')
        self.write(achieved, {'ref': 'DONE'}, T0 + hours(1))
        breached = self.make_partner('NEW')
        self.write(breached, {'ref': 'DONE'}, T0 + hours(5))
        cancelled = self.make_partner('NEW')
        self.write(cancelled, {'ref': 'CANCEL'}, T0 + hours(1))
        self.d.duration = 10
        for partner, stage in ((achieved, 'achieved'), (breached, 'breached'),
                               (cancelled, 'cancelled')):
            t = self.task_of(partner, self.d)
            self.assertEqual(t.stage, stage)
            before = (t.target_duration, t.planned_end_time)
            with self.at(T0 + hours(6)):
                t.with_user(self.manager).action_recalculate()
            self.assertEqual((t.target_duration, t.planned_end_time), before)

    def test_chg_011_recalculate_paused(self):
        """TC-CHG-011: task paused đổi mục tiêu ngay, planned_end_time xếp lại khi resume."""
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        t = self.task_of(p, self.d)
        planned_end_time = t.planned_end_time
        self.d.duration = 8
        with self.at(T0 + hours(2)):
            t.with_user(self.manager).action_recalculate()
        self.assertEqual(t.target_duration, 8)
        self.assertEqual(t.stage, 'paused')
        self.assertEqual(t.planned_end_time, planned_end_time)
        self.write(p, {'ref': 'WORK'}, T0 + hours(3))
        self.assertEqual(t.planned_end_time, T0 + hours(3) + hours(7))

    def test_chg_028_viewer_cannot_recalculate(self):
        """TC-CHG-028: group_sla_user gọi Tính lại -> AccessError."""
        t = self.task_of(self.make_partner('NEW'), self.d)
        with self.assertRaises(AccessError):
            t.with_user(self.viewer).action_recalculate()

    def test_chg_012_013_escalation_added_late(self):
        """TC-CHG-012/013: mốc thêm khi đã vượt % không bắn bù; mốc chưa tới bắn khi tới."""
        self.make_escalation(self.d, 50)
        t = self.task_of(self.make_partner('NEW'), self.d)
        self.Processor._process_task(t, T0 + hours(3.2))  # 80%
        self.assertEqual(self.events(t).count('escalate'), 1)
        # Mốc mới tạo lúc 80% (đồng hồ test) -> đánh dấu đã qua, không bắn bù.
        with self.at(T0 + hours(3.2)):
            self.make_escalation(self.d, 75)
        self.Processor._process_task(t, T0 + hours(3.3))
        self.assertEqual(self.events(t).count('escalate'), 1)
        with self.at(T0 + hours(3.2)):
            self.make_escalation(self.d, 90)
        self.Processor._process_task(t, T0 + hours(3.7))  # 92.5%
        self.assertEqual(self.events(t).count('escalate'), 2)


@tagged(*TAGS, 'tg_11')
class TestArchiveDelete(SlaCase):

    def setUp(self):
        super().setUp()
        self.d = self.make_definition()

    def test_chg_015_017_archive_unarchive(self):
        """TC-CHG-015/016/017: archive không gắn task mới; bỏ archive thì gắn lại."""
        self.d.active = False
        self.assertFalse(self.tasks(self.make_partner('NEW')))
        self.d.active = True
        p = self.make_partner('NEW')
        self.assertEqual(len(self.tasks(p, self.d)), 1)
        self.write(p, {'name': "Renamed"}, T0 + hours(1))
        self.assertEqual(len(self.tasks(p, self.d)), 1)

    def test_chg_019_archived_keeps_breach(self):
        """TC-CHG-019: task của định nghĩa archive vẫn vi phạm và bắn escalation."""
        self.make_escalation(self.d, 100)
        p = self.make_partner('NEW')
        t = self.task_of(p, self.d)
        self.d.active = False
        self.Processor._process_task(t, T0 + hours(4.1))
        self.assertTrue(t.has_breached)
        self.assertIn('escalate', self.events(t))

    def test_chg_021_023_archived_still_transitions(self):
        """TC-CHG-021/022/023: task của định nghĩa archive vẫn cancel/pause/resume/stop."""
        pause = self.make_partner('NEW')
        cancel = self.make_partner('NEW')
        stop = self.make_partner('NEW')
        self.d.active = False
        self.write(pause, {'ref': 'HOLD'}, T0 + hours(1))
        self.assertEqual(self.task_of(pause, self.d).stage, 'paused')
        self.write(pause, {'ref': 'WORK'}, T0 + hours(2))
        self.assertEqual(self.task_of(pause, self.d).stage, 'in_progress')
        self.write(cancel, {'ref': 'CANCEL'}, T0 + hours(1))
        self.assertEqual(self.task_of(cancel, self.d).stage, 'cancelled')
        self.write(stop, {'ref': 'DONE'}, T0 + hours(1))
        self.assertEqual(self.task_of(stop, self.d).stage, 'achieved')

    def test_chg_024_027_reject_delete_with_tasks(self):
        """TC-CHG-024/026/027: không xóa định nghĩa còn task (mọi stage)."""
        running = self.make_partner('NEW')
        done = self.make_partner('NEW')
        self.write(done, {'ref': 'DONE'}, T0 + hours(1))
        with self.assertRaisesRegex(ValidationError, "(?i)archive"):
            self.d.unlink()
        self.d.active = False
        with self.assertRaises(ValidationError):
            self.d.unlink()
        self.assertTrue(running)

    def test_chg_025_delete_without_tasks(self):
        """TC-CHG-025: xóa được định nghĩa chưa từng có task."""
        d = self.make_definition(name="Unused")
        d.unlink()
        self.assertFalse(d.exists())
