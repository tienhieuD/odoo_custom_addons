# -*- coding: utf-8 -*-
"""TG-28: nút "Apply Current Settings" (action_recalculate) ghi event và báo kết quả.

Refs: docs/plan-improvement-sla-01.md mục 17, docs/plan-improvement-sla-01-review.md §6.17
"""
from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')


@tagged(*TAGS, 'tg_28')
class TestApplyCurrentSettings(SlaCase):

    def setUp(self):
        super().setUp()
        self.manager = self.make_user('tg28_manager', 'manager')
        self.d = self.make_definition(duration=8)

    def apply(self, tasks, now):
        with self.at(now):
            return tasks.with_user(self.manager).action_recalculate()

    def recalc_events(self, task):
        return task.event_ids.filtered(lambda e: e.event == 'recalculate')

    def test_running_task_gets_new_target_and_event(self):
        task = self.task_of(self.make_partner('NEW'), self.d)
        original = task.original_breach_time
        self.d.duration = 4
        now = T0 + hours(1)
        action = self.apply(task, now)
        self.assertEqual(task.target_duration, 4)
        self.assertEqual(task.planned_end_time, now + hours(4))  # business_duration chưa chốt = 0
        self.assertEqual(task.original_breach_time, original)
        event = self.recalc_events(task)
        self.assertEqual(len(event), 1)
        self.assertIn(self.manager.name, event.note)
        self.assertIn("8.00 h -> 4.00 h", event.note)
        self.assertEqual(action['tag'], 'display_notification')
        self.assertEqual(action['params']['next'], {'type': 'ir.actions.client', 'tag': 'reload'})
        self.assertIn("1 task(s) updated, 0 skipped", action['params']['message'])

    def test_breached_task_keeps_deadline(self):
        task = self.task_of(self.make_partner('NEW'), self.d)
        planned, original = task.planned_end_time, task.original_breach_time
        self.Engine._check_breach(task, T0 + hours(9))
        self.assertTrue(task.has_breached)
        self.d.duration = 4
        self.apply(task, T0 + hours(10))
        self.assertEqual(task.target_duration, 4)
        self.assertEqual((task.planned_end_time, task.original_breach_time), (planned, original))
        self.assertEqual(len(self.recalc_events(task)), 1)

    def test_paused_task_keeps_deadline(self):
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        task = self.task_of(p, self.d)
        planned, original = task.planned_end_time, task.original_breach_time
        self.d.duration = 4
        self.apply(task, T0 + hours(2))
        self.assertEqual((task.stage, task.target_duration), ('paused', 4))
        self.assertEqual((task.planned_end_time, task.original_breach_time), (planned, original))

    def test_unchanged_task_has_no_event_but_counts_updated(self):
        task = self.task_of(self.make_partner('NEW'), self.d)
        self.assertEqual(task.planned_end_time, T0 + hours(8))
        action = self.apply(task, T0)  # cùng cấu hình, cùng thời điểm: không gì đổi
        self.assertFalse(self.recalc_events(task))
        self.assertIn("1 task(s) updated, 0 skipped", action['params']['message'])

    def test_closed_tasks_skipped(self):
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        task = self.task_of(p, self.d)
        self.assertEqual(task.stage, 'achieved')
        self.d.duration = 4
        action = self.apply(task, T0 + hours(2))
        self.assertEqual(task.target_duration, 8)
        self.assertFalse(self.recalc_events(task))
        self.assertIn("0 task(s) updated, 1 skipped", action['params']['message'])

    def test_many_tasks_one_event_each(self):
        tasks = self.task_of(self.make_partner('NEW'), self.d) | self.task_of(
            self.make_partner('NEW'), self.d)
        self.d.duration = 4
        action = self.apply(tasks, T0 + hours(1))
        self.assertEqual(len(tasks.mapped('event_ids').filtered(lambda e: e.event == 'recalculate')), 2)
        self.assertIn("2 task(s) updated, 0 skipped", action['params']['message'])
