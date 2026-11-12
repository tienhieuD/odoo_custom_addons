# -*- coding: utf-8 -*-
"""TG-27: nút "Re-check Conditions" (action_reevaluate) giới hạn đúng một definition.

Refs: docs/plan-improvement-sla-01.md mục 18, docs/plan-improvement-sla-01-review.md §6.18
"""
from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')
REL_STOP = "[('parent_id.ref', '=', 'DONE')]"


@tagged(*TAGS, 'tg_27')
class TestRecheckConditions(SlaCase):

    def setUp(self):
        super().setUp()
        self.manager = self.make_user('tg27_manager', 'manager')
        self.viewer = self.make_user('tg27_viewer', 'user')

    def recheck(self, tasks, now):
        with self.at(now):
            return tasks.with_user(self.manager).action_reevaluate()

    def test_scope_is_one_definition(self):
        """Re-check trên task của B không đổi task của A và không tạo task mới của A."""
        a = self.make_definition(name="A", stop_domain=REL_STOP)
        b = self.make_definition(name="B", stop_domain=REL_STOP)
        parent = self.make_partner(False)
        child = self.make_partner('NEW', parent_id=parent.id)
        task_a, task_b = self.task_of(child, a), self.task_of(child, b)
        # Record chưa từng có task của C: engine "mọi definition" sẽ gắn nó.
        c = self.make_definition(name="C", stop_domain=REL_STOP)
        self.assertFalse(self.tasks(child, c))
        self.write(parent, {'ref': 'DONE'}, T0 + hours(1))  # child không được ghi lại
        self.assertEqual((task_a.stage, task_b.stage), ('in_progress', 'in_progress'))

        action = self.recheck(task_b, T0 + hours(2))

        self.assertEqual(task_b.stage, 'achieved')
        self.assertEqual(task_a.stage, 'in_progress')
        self.assertFalse(self.tasks(child, c))
        self.assertEqual(action['tag'], 'display_notification')
        self.assertEqual(action['params']['next'], {'type': 'ir.actions.client', 'tag': 'reload'})
        self.assertIn("1 task(s) checked, 1 changed", action['params']['message'])

    def test_closed_task_unchanged_with_event(self):
        """Task đã đóng không đổi; vẫn có event reevaluate ghi "No change" và người bấm."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        task = self.task_of(p, d)
        self.assertEqual(task.stage, 'achieved')
        snapshot = (task.stage, task.end_time, task.business_duration)
        action = self.recheck(task, T0 + hours(3))
        self.assertEqual((task.stage, task.end_time, task.business_duration), snapshot)
        self.assertIn("1 task(s) checked, 0 changed", action['params']['message'])
        event = task.event_ids.filtered(lambda e: e.event == 'reevaluate')
        self.assertEqual(len(event), 1)
        self.assertIn("No change", event.note)
        self.assertIn(self.manager.name, event.note)

    def test_changed_event_records_old_and_new_stage(self):
        d = self.make_definition(stop_domain=REL_STOP)
        parent = self.make_partner(False)
        child = self.make_partner('NEW', parent_id=parent.id)
        task = self.task_of(child, d)
        self.write(parent, {'ref': 'DONE'}, T0 + hours(1))
        self.recheck(task, T0 + hours(2))
        event = task.event_ids.filtered(lambda e: e.event == 'reevaluate')
        self.assertEqual(event.event_dt, T0 + hours(2))
        self.assertIn("In Progress -> Achieved", event.note)
        self.assertEqual(event.definition_id, d)

    def test_many_tasks_grouped_per_definition(self):
        """Nhiều task (hai definition) trong một lần bấm: mỗi task theo đúng definition của nó."""
        a = self.make_definition(name="A", stop_domain=REL_STOP)
        b = self.make_definition(name="B", stop_domain=REL_STOP)
        parent = self.make_partner(False)
        child = self.make_partner('NEW', parent_id=parent.id)
        tasks = self.task_of(child, a) | self.task_of(child, b)
        self.write(parent, {'ref': 'DONE'}, T0 + hours(1))
        action = self.recheck(tasks, T0 + hours(2))
        self.assertEqual(set(tasks.mapped('stage')), {'achieved'})
        self.assertEqual(len(tasks.mapped('event_ids').filtered(lambda e: e.event == 'reevaluate')), 2)
        self.assertIn("2 task(s) checked, 2 changed", action['params']['message'])

    def test_viewer_cannot_recheck(self):
        d = self.make_definition()
        task = self.task_of(self.make_partner('NEW'), d)
        with self.assertRaises(AccessError):
            task.with_user(self.viewer).action_reevaluate()

    def test_engine_definitions_param_limits_scope(self):
        """`evaluate(definitions=...)` chỉ chạm định nghĩa đó, kể cả khi nó đã tắt."""
        a = self.make_definition(name="A")
        p = self.make_partner('NEW')
        self.assertEqual(len(self.tasks(p, a)), 1)
        b = self.make_definition(name="B")  # tạo sau record nên p chưa có task B
        self.Engine.evaluate(p, now=T0, definitions=a)
        self.assertFalse(self.tasks(p, b))
        self.Engine.evaluate(p, now=T0)
        self.assertEqual(len(self.tasks(p, b)), 1)
