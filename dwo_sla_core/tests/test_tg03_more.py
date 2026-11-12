# -*- coding: utf-8 -*-
"""TG-03 bổ sung: vi phạm, phần trăm đã dùng, ràng buộc CSDL (docs/060 TC-BRE-*).

Refs: REQ-FUNC-009, 022, 043, 044, 046, REQ-INT-023
"""
from datetime import datetime

from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tools import mute_logger

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')
MIN = 1 / 60.0


@tagged(*TAGS, 'tg_03')
class TestBreachMore(SlaCase):

    def setUp(self):
        super().setUp()
        self.d = self.make_definition()

    def process(self, task, now):
        self.Processor._process_task(task, now)

    def test_bre_001_before_planned_end(self):
        """TC-BRE-001: xử lý nền 12:59 (trước 13:00) -> chưa vi phạm."""
        t = self.task_of(self.make_partner('WORK'), self.d)
        self.process(t, T0 + hours(4) - hours(MIN))
        self.assertFalse(t.has_breached)
        self.assertEqual(self.events(t).count('breach'), 0)
        self.assertEqual(t.stage, 'in_progress')

    def test_bre_006_pause_at_target(self):
        """TC-BRE-006: pause đúng 13:00 -> breach rồi pause."""
        p = self.make_partner('WORK')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(4))
        t = self.task_of(p, self.d)
        self.assertTrue(t.has_breached)
        self.assertEqual(t.stage, 'paused')
        self.assertAlmostEqual(t.business_duration, 4.0, places=3)
        self.assertEqual(self.events(t), ['attach', 'breach', 'pause'])

    def test_bre_008_breach_before_escalate(self):
        """TC-BRE-008: mốc 120% cùng lần xử lý với vi phạm -> breach ghi trước escalate."""
        self.make_escalation(self.d, 120)
        t = self.task_of(self.make_partner('WORK'), self.d)
        self.process(t, T0 + hours(4 + 50 * MIN))
        names = self.events(t)
        self.assertEqual((names.count('breach'), names.count('escalate')), (1, 1))
        self.assertLess(names.index('breach'), names.index('escalate'))

    def test_bre_010_long_pause_then_stop(self):
        """TC-BRE-010: paused 5 ngày làm việc (còn dư 2 giờ) rồi stop -> achieved."""
        cal = self.make_calendar()
        d = self.make_definition(name="VN", schedule_source='definition', schedule_id=cal.id)
        p = self.make_partner('WORK')
        t = self.task_of(p, d)
        self.assertEqual(t.planned_end_time, T0 + hours(4))
        self.write(p, {'ref': 'HOLD'}, T0 + hours(2))
        self.assertAlmostEqual(t.business_duration, 2.0, places=3)
        self.assertFalse(t.has_breached)
        stop_at = datetime(2026, 3, 9, 4, 0)
        self.write(p, {'ref': 'DONE'}, stop_at)
        self.assertEqual((t.stage, t.has_breached, t.end_time), ('achieved', False, stop_at))
        self.assertAlmostEqual(t.business_duration, 2.0, places=3)
        self.assertEqual(self.events(t).count('complete'), 1)

    def test_bre_011_stop_paused_breached(self):
        """TC-BRE-011: stop task paused khi đã breach -> breached."""
        p = self.make_partner('WORK')
        t = self.task_of(p, self.d)
        self.process(t, T0 + hours(4 + MIN))
        self.write(p, {'ref': 'HOLD'}, T0 + hours(4.5))
        self.assertAlmostEqual(t.business_duration, 4.5, places=3)
        self.write(p, {'ref': 'DONE'}, T0 + hours(6))
        self.assertEqual((t.stage, t.end_time), ('breached', T0 + hours(6)))
        self.assertAlmostEqual(t.business_duration, 4.5, places=3)
        self.assertEqual(self.events(t).count('complete'), 1)

    def test_bre_012_stop_after_breach_no_duplicate(self):
        """TC-BRE-012: stop sau khi xử lý nền đã breach -> breached, không breach trùng."""
        p = self.make_partner('WORK')
        t = self.task_of(p, self.d)
        self.process(t, T0 + hours(4 + MIN))
        self.write(p, {'ref': 'DONE'}, T0 + hours(4.5))
        self.assertEqual((t.stage, t.end_time), ('breached', T0 + hours(4.5)))
        names = self.events(t)
        self.assertEqual((names.count('breach'), names.count('complete'), len(names)), (1, 1, 3))

    def pause_and_read(self, minutes, definition=None):
        p = self.make_partner('WORK')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(minutes * MIN))
        t = self.task_of(p, definition or self.d)
        self.assertEqual(t.stage, 'paused')
        return t

    def test_bre_015_016_percent_used(self):
        """TC-BRE-015/016: 1 giờ/4 giờ = 25%; 5 giờ/4 giờ = 125% (không cắt ở 100)."""
        t = self.pause_and_read(60)
        self.assertAlmostEqual(t.business_duration, 1.0, places=3)
        self.assertEqual(t.business_percent_used, 25)
        self.assertEqual(self.pause_and_read(300).business_percent_used, 125)

    def test_bre_017b_running_percent_live(self):
        """REQ-INT-023: task in_progress tính cả đoạn đang chạy tới thời điểm xem."""
        t = self.task_of(self.make_partner('WORK'), self.d)
        for now, expected in ((T0 + hours(1), 25), (T0 + hours(5), 125)):
            with self.at(now):
                t.invalidate_cache(None, ids=t.ids)
                self.assertEqual(t.stage, 'in_progress')
                self.assertEqual(t.business_percent_used, expected)
                self.assertEqual(t.business_duration, 0.0)

    def test_bre_017c_settle_batch_equals_settle(self):
        """settle_batch cho kết quả bằng settle từng task (lịch có ngày nghỉ, nhiều start khác nhau)."""
        cal = self.make_calendar()
        self.env['resource.calendar.leaves'].create({
            'name': "Holiday", 'calendar_id': cal.id,
            'date_from': T0 + hours(24), 'date_to': T0 + hours(48)})
        sla_time = self.env['sla.time']
        starts = [T0, T0 + hours(5), T0 + hours(30), T0 + hours(100), T0 + hours(400)]
        end = T0 + hours(300)
        for calendar in (cal, self.env['resource.calendar']):
            batch = sla_time.settle_batch(calendar, starts, end)
            for start, got in zip(starts, batch):
                self.assertAlmostEqual(got, sla_time.settle(calendar, start, end), places=6)

    def test_bre_017_paused_percent_stable(self):
        """TC-BRE-017: task paused xem lại cách 2 giờ làm việc -> phần trăm không đổi."""
        cal = self.make_calendar()
        d = self.make_definition(name="VN", schedule_source='definition', schedule_id=cal.id)
        t = self.pause_and_read(60, d)
        for now in (T0 + hours(2), T0 + hours(4)):
            with self.at(now):
                t.invalidate_cache(None, ids=t.ids)
                self.assertEqual(t.business_percent_used, 25)
                self.assertAlmostEqual(t.business_duration, 1.0, places=3)

    def test_bre_018_021_percent_boundaries(self):
        """TC-BRE-018..021: làm tròn xuống 49/99, đúng 100, vừa attach 0."""
        self.assertEqual(self.pause_and_read(119).business_percent_used, 49)
        self.assertEqual(self.pause_and_read(239).business_percent_used, 99)
        self.assertEqual(self.pause_and_read(240).business_percent_used, 100)
        with self.at(T0):
            self.assertEqual(self.task_of(self.make_partner('WORK'), self.d).business_percent_used, 0)

    def test_bre_022_failed_action_note(self):
        """TC-BRE-022: action mốc 100% lỗi -> escalate_failed, note chứa thông báo lỗi."""
        action = self.make_server_action(
            "raise UserError('boom: gateway down')")
        self.make_escalation(self.d, 100, action=action)
        t = self.task_of(self.make_partner('WORK'), self.d)
        with self.assertLogs('odoo.addons.dwo_sla_core', 'ERROR'):
            self.process(t, T0 + hours(4 + MIN))
        names = self.events(t)
        self.assertEqual((names.count('breach'), names.count('escalate_failed'),
                          names.count('escalate')), (1, 1, 0))
        failed = t.event_ids.filtered(lambda e: e.event == 'escalate_failed')
        self.assertIn('boom: gateway down', failed.note)

    def test_bre_023_task_db_constraints(self):
        """TC-BRE-023: CHECK chéo trên sla_task từ chối trạng thái không nhất quán."""
        t1 = self.task_of(self.make_partner('NEW'), self.d)
        t2 = self.task_of(self.make_partner('HOLD'), self.d)
        self.env['base'].flush()
        cases = [
            ("UPDATE sla_task SET stage='breached', end_time=now(), running_since=NULL, "
             "next_due_at=NULL WHERE id=%s", t1.id, 'sla_task_breached_check'),
            ("UPDATE sla_task SET stage='achieved', has_breached=true, end_time=now(), "
             "running_since=NULL, next_due_at=NULL WHERE id=%s", t1.id, 'sla_task_achieved_check'),
            ("UPDATE sla_task SET stage='cancelled', running_since=NULL, next_due_at=NULL "
             "WHERE id=%s", t1.id, 'sla_task_end_dt_check'),
            ("UPDATE sla_task SET next_due_at=now() WHERE id=%s", t2.id,
             'sla_task_next_due_at_check'),
        ]
        for sql, task_id, name in cases:
            with self.assertRaises(IntegrityError) as ctx, \
                    mute_logger('odoo.sql_db'), self.env.cr.savepoint():
                self.env.cr.execute(sql, (task_id,))
            self.assertIn(name, str(ctx.exception))
        t1.invalidate_cache(None, ids=t1.ids)
        t2.invalidate_cache(None, ids=t2.ids)
        self.assertEqual((t1.stage, t1.has_breached, t2.stage), ('in_progress', False, 'paused'))
