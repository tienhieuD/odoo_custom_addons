# -*- coding: utf-8 -*-
"""TG-03, TG-07, TG-08: vi phạm, retroactive, escalation, thử lại, xử lý nền (P1 trong docs/060).

Thời gian điều khiển bằng `sla.processor._process_task(task, now)` (xử lý đúng một
task tại `now`) hoặc `process_due()` với `fields.Datetime.now` bị patch.
Refs: REQ-FUNC-009, 017, 022..028, 044, 046, 053..059, REQ-INT-008, REQ-REL-001, 002
"""
from unittest.mock import patch

from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')
MIN = 1 / 60.0


class BreachCase(SlaCase):

    def process(self, task, now):
        self.Processor._process_task(task, now)

    def breaches(self, task):
        return self.events(task).count('breach')


@tagged(*TAGS, 'tg_03')
class TestBreach(BreachCase):

    def setUp(self):
        super().setUp()
        self.d = self.make_definition()
        self.p = self.make_partner('NEW')
        self.t = self.task_of(self.p, self.d)

    def test_bre_002_at_planned_end(self):
        """TC-BRE-002: xử lý nền đúng planned_end_time (biên `>=`) -> bật dấu vi phạm, 1 event breach."""
        self.process(self.t, T0 + hours(4))
        self.assertTrue(self.t.has_breached)
        self.assertEqual(self.breaches(self.t), 1)

    def test_bre_before_planned_end(self):
        """Ngay dưới biên (1 giây trước planned_end_time) chưa vi phạm."""
        self.process(self.t, T0 + hours(4) - hours(1 / 3600.0))
        self.assertFalse(self.t.has_breached)

    def test_bre_003_004_once_only(self):
        """TC-BRE-003/004: breach event_dt = now xử lý, vẫn in_progress, chạy lại không thêm event."""
        now = T0 + hours(4) + hours(MIN)
        self.process(self.t, now)
        self.process(self.t, now + hours(1))
        self.assertTrue(self.t.has_breached)
        self.assertEqual(self.t.stage, 'in_progress')
        self.assertEqual(self.breaches(self.t), 1)
        breach = self.t.event_ids.filtered(lambda e: e.event == 'breach')
        self.assertEqual(breach.event_dt, now)

    def test_bre_005_pause_before_processor(self):
        """TC-BRE-005: pause sau planned_end_time, xử lý nền chưa chạy -> breach ghi lúc pause rồi paused."""
        self.write(self.p, {'ref': 'HOLD'}, T0 + hours(5))
        self.assertEqual(self.t.stage, 'paused')
        self.assertTrue(self.t.has_breached)
        self.assertEqual(self.events(self.t), ['attach', 'breach', 'pause'])

    def test_bre_009_stop_after_planned_end(self):
        """TC-BRE-009: stop khi đã quá planned_end_time nhưng xử lý nền chưa chạy -> breached."""
        self.write(self.p, {'ref': 'DONE'}, T0 + hours(5))
        self.assertEqual(self.t.stage, 'breached')
        self.assertTrue(self.t.has_breached)
        self.assertEqual(self.events(self.t), ['attach', 'breach', 'complete'])

    def test_bre_013_flag_survives_pause_resume(self):
        """TC-BRE-013 / PAU-010: đã vi phạm rồi pause/resume -> cờ giữ nguyên, planned_end_time giữ nguyên."""
        self.process(self.t, T0 + hours(5))
        planned_end_time = self.t.planned_end_time
        self.write(self.p, {'ref': 'HOLD'}, T0 + hours(6))
        self.write(self.p, {'ref': 'WORK'}, T0 + hours(8))
        self.assertTrue(self.t.has_breached)
        self.assertEqual(self.t.stage, 'in_progress')
        self.assertEqual(self.t.planned_end_time, planned_end_time)

    def test_bre_paused_task_not_breached_by_processor(self):
        """Task paused không bị so với planned_end_time."""
        self.write(self.p, {'ref': 'HOLD'}, T0 + hours(1))
        self.process(self.t, T0 + hours(10))
        self.assertFalse(self.t.has_breached)

    def test_bre_023_cross_check_constraints(self):
        """CHECK chéo: achieved không được có dấu vi phạm; breached phải có dấu."""
        from psycopg2 import IntegrityError
        from odoo.tools import mute_logger
        self.write(self.p, {'ref': 'DONE'}, T0 + hours(1))
        self.assertEqual(self.t.stage, 'achieved')
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'), \
                self.env.cr.savepoint():
            self.t.has_breached = True
            self.t.flush()


@tagged(*TAGS, 'tg_07')
class TestRetroactive(BreachCase):

    def _retro_definition(self):
        field = self.env['ir.model.fields']._get('res.partner', 'create_date')
        return self.make_definition(retroactive=True, start_field_id=field.id)

    def _partner_created_at(self, created):
        p = self.make_partner(False)
        self.env.cr.execute("UPDATE res_partner SET create_date=%s WHERE id=%s", (created, p.id))
        p.invalidate_cache(None, ids=p.ids)
        return p

    def test_ret_002_retroactive_breach_on_attach(self):
        """TC-RET-002: mốc start đã quá hạn khi attach -> breach ngay, event attach rồi breach."""
        d = self._retro_definition()
        p = self._partner_created_at(T0)
        self.write(p, {'ref': 'NEW'}, T0 + hours(5))
        t = self.task_of(p, d)
        self.assertEqual(t.start_time, T0)
        self.assertEqual(t.planned_end_time, T0 + hours(4))
        self.assertTrue(t.has_breached)
        self.assertEqual(self.events(t), ['attach', 'breach'])

    def test_ret_retroactive_not_yet_due(self):
        """Mốc start trong quá khứ nhưng chưa tới hạn -> không breach."""
        d = self._retro_definition()
        p = self._partner_created_at(T0)
        self.write(p, {'ref': 'NEW'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertFalse(t.has_breached)
        self.assertEqual(t.planned_end_time, T0 + hours(4))


@tagged(*TAGS, 'tg_08')
class TestEscalation(BreachCase):

    def setUp(self):
        super().setUp()
        self.d = self.make_definition()
        self.mark = lambda pct: self.make_server_action(
            "record.write({'function': (record.function or '') + 'E%s;'})" % pct,
            name="mark %s" % pct)
        self.esc = {pct: self.make_escalation(self.d, pct, self.mark(pct)) for pct in (75, 100, 120)}
        self.p = self.make_partner('NEW')
        self.t = self.task_of(self.p, self.d)

    def test_esc_001_three_milestones(self):
        """TC-ESC-001: mốc 75/100/120% bắn khi đã trôi 3h / 4h / 4,8h; breach trước escalate 100%."""
        self.process(self.t, T0 + hours(3))
        self.assertEqual(self.events(self.t), ['attach', 'escalate'])
        self.process(self.t, T0 + hours(4))
        self.process(self.t, T0 + hours(4.8))
        self.assertEqual(self.events(self.t),
                         ['attach', 'escalate', 'breach', 'escalate', 'escalate'])
        self.assertEqual(self.p.function, 'E75;E100;E120;')
        self.assertEqual(self.t.done_escalation_ids, self.d.escalation_ids)

    def test_bre_007_breach_before_100_escalation(self):
        """TC-BRE-007: breach không muộn hơn escalate của mốc 100%."""
        self.process(self.t, T0 + hours(5))
        ids = {e.event: e.id for e in self.t.event_ids.sorted('id')}
        self.assertLess(self.t.event_ids.filtered(lambda e: e.event == 'breach').id,
                        self.t.event_ids.filtered(lambda e: e.event == 'escalate')[1].id)
        self.assertEqual(self.events(self.t).count('escalate'), 3)
        self.assertTrue(ids)

    def test_esc_008_not_refired(self):
        """TC-ESC-008: xử lý nền chạy hai lần liên tiếp -> mốc đã xử lý không bắn lại."""
        self.process(self.t, T0 + hours(3))
        self.process(self.t, T0 + hours(3))
        self.assertEqual(self.events(self.t).count('escalate'), 1)
        self.assertEqual(self.p.function, 'E75;')

    def test_esc_not_before_threshold(self):
        """Chưa tới 75% thì không bắn."""
        self.process(self.t, T0 + hours(2.9))
        self.assertEqual(self.events(self.t), ['attach'])

    def test_bre_014_elapsed_survives_pause(self):
        """TC-BRE-014: đã trôi 4,4h rồi pause/resume -> mốc 120% bắn khi tổng đã trôi đạt 4,8h."""
        self.process(self.t, T0 + hours(4.4))
        self.write(self.p, {'ref': 'HOLD'}, T0 + hours(4.4))
        self.write(self.p, {'ref': 'WORK'}, T0 + hours(10))
        self.assertAlmostEqual(self.t.business_duration, 4.4)
        self.process(self.t, T0 + hours(10.3))   # tổng 4,7h
        self.assertEqual(self.p.function, 'E75;E100;')
        self.process(self.t, T0 + hours(10.4))   # tổng 4,8h
        self.assertEqual(self.p.function, 'E75;E100;E120;')

    def test_esc_048_context_and_record(self):
        """TC-ESC-048/049: active_model/id/ids đúng; mỗi record nhận ghi chú của chính nó."""
        d2 = self.make_definition(name="ctx")
        action = self.make_server_action(
            "record.write({'function': '%s|%s|%s' % (env.context.get('active_model'),"
            " env.context.get('active_id'), env.context.get('active_ids'))})")
        self.make_escalation(d2, 50, action)
        p2 = self.make_partner('NEW')
        t2 = self.task_of(p2, d2)
        self.process(t2, T0 + hours(2))
        self.assertEqual(p2.function, 'res.partner|%s|[%s]' % (p2.id, p2.id))
        self.assertFalse(self.p.function)

    def test_esc_018_019_failure_isolated(self):
        """TC-ESC-018/019: action lỗi -> escalate_failed 1 lần; task khác vẫn escalate."""
        d2 = self.make_definition(name="fail")
        bad = self.make_escalation(d2, 50, self.make_server_action("raise UserError('boom')"))
        p_bad = self.make_partner('NEW')
        t_bad = self.task_of(p_bad, d2)
        self.process(t_bad, T0 + hours(2))
        self.process(self.t, T0 + hours(3))
        self.assertEqual(self.events(t_bad), ['attach', 'escalate_failed'])
        self.assertIn('boom', t_bad.event_ids.filtered(lambda e: e.event == 'escalate_failed').note)
        self.assertEqual(self.events(self.t), ['attach', 'escalate'])
        self.process(t_bad, T0 + hours(3))
        self.assertEqual(self.events(t_bad).count('escalate_failed'), 1)
        self.assertIn(bad, t_bad.done_escalation_ids)


@tagged(*TAGS, 'tg_08')
class TestProcessDue(BreachCase):
    """Hàm cron `process_due`: khóa/lưu từng task, trần batch_size (REQ-REL-001, 002)."""

    def setUp(self):
        super().setUp()
        # `_commit_progress` gọi cr.commit() — bị cấm trong test; thay bằng "không giới hạn thời gian".
        patcher = patch.object(
            type(self.env['ir.cron']), '_commit_progress', return_value=float('inf'))
        self.commit_mock = patcher.start()
        self.addCleanup(patcher.stop)

    def test_process_due_handles_due_tasks(self):
        """process_due xử lý task đến hạn: bật breach, tính lại next_due_at."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        t = self.task_of(p, d)
        self.assertEqual(t.next_due_at, T0 + hours(4))
        with self.at(T0 + hours(5)):
            self.Processor.process_due()
        self.assertTrue(t.has_breached)
        self.assertFalse(t.next_due_at)

    def test_process_due_skips_tasks_not_due(self):
        d = self.make_definition()
        t = self.task_of(self.make_partner('NEW'), d)
        with self.at(T0 + hours(1)):
            self.Processor.process_due()
        self.assertFalse(t.has_breached)

    def test_process_due_batch_size_caps_each_call(self):
        """batch_size là trần mỗi lần gọi; lần gọi sau xử lý nốt phần còn lại."""
        self.env['ir.config_parameter'].sudo().set_param('dwo_sla_core.batch_size', '2')
        d = self.make_definition()
        tasks = self.Task
        for _ in range(3):
            tasks |= self.Task.search([('res_id', '=', self.make_partner('NEW').id)])
        with self.at(T0 + hours(5)):
            self.Processor.process_due()
            self.assertEqual(len(tasks.filtered('has_breached')), 2)
            self.Processor.process_due()
        self.assertEqual(len(tasks.filtered('has_breached')), 3)
