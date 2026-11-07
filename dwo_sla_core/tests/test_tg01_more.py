# -*- coding: utf-8 -*-
"""TG-01, TG-02 bổ sung: lưu điều kiện, attach/stop biên, pause/resume biên (docs/060 TC-ATT-*, TC-PAU-*).

Refs: REQ-FUNC-001..008, 012, 013, 015, 016, 034
"""
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')


@tagged(*TAGS, 'tg_01')
class TestConditionSaving(SlaCase):

    def test_att_003_unknown_field_rejected(self):
        """TC-ATT-003: domain có field không tồn tại bị từ chối, thông báo nêu tên field."""
        n0 = self.Definition.search_count([])
        with self.assertRaisesRegex(ValidationError, 'x_khong_ton_tai'), self.env.cr.savepoint():
            self.make_definition(start_domain="[('x_khong_ton_tai','=',1)]")
        self.assertEqual(self.Definition.search_count([]), n0)

    def test_att_004_function_call_rejected(self):
        """TC-ATT-004: domain gọi hàm `context_today()` bị từ chối (giới hạn literal)."""
        with self.assertRaisesRegex(ValidationError, 'literal'):
            self.make_definition(start_domain="[('create_date','<',context_today())]")

    def test_att_005_variable_rejected(self):
        """TC-ATT-005: domain dùng biến `uid` bị từ chối."""
        with self.assertRaisesRegex(ValidationError, 'literal'):
            self.make_definition(stop_domain="[('user_id','=',uid)]")

    def test_att_006_literal_saved(self):
        """TC-ATT-006: domain literal hợp lệ (kể cả ngày giờ) lưu được và đọc lại đúng."""
        d = self.make_definition(
            start_domain="[('ref','=','NEW')]",
            stop_domain="[('create_date','<','2026-01-01 00:00:00')]")
        self.assertEqual(eval(d.start_domain), [('ref', '=', 'NEW')])  # noqa: S307
        self.assertEqual(eval(d.stop_domain), [('create_date', '<', '2026-01-01 00:00:00')])  # noqa: S307


@tagged(*TAGS, 'tg_01')
class TestAttachEdges(SlaCase):

    def test_att_008_start_and_pause_attach_paused(self):
        """TC-ATT-008: start và pause cùng khớp -> attach thẳng vào paused, chỉ 1 event attach."""
        d = self.make_definition()
        t = self.task_of(self.make_partner('HOLD'), d)
        self.assertEqual(t.stage, 'paused')
        self.assertEqual(t.pause_time, T0)
        self.assertFalse(t.next_due_at)
        self.assertEqual(t.business_duration, 0)
        self.assertEqual(self.events(t), ['attach'])

    def test_att_009_start_and_stop_no_attach(self):
        """TC-ATT-009: start `[]` và stop cùng khớp -> không task, không event."""
        d = self.make_definition(start_domain="[]")
        p = self.make_partner('DONE')
        self.assertFalse(self.tasks(p, d))
        self.assertFalse(self.Event.sudo().search([('definition_id', '=', d.id)]))

    def test_att_010_start_and_cancel_no_attach(self):
        """TC-ATT-010: start `[]` và cancel cùng khớp (cancel_mode condition) -> không task."""
        d = self.make_definition(start_domain="[]", cancel_mode='condition')
        p = self.make_partner('CANCEL')
        self.assertFalse(self.tasks(p, d))
        self.assertFalse(self.Event.sudo().search([('definition_id', '=', d.id)]))

    def test_att_011_020_start_unmatched(self):
        """TC-ATT-011/020: start không khớp -> không task, không event."""
        d = self.make_definition()
        p = self.make_partner('OTHER')
        self.assertFalse(self.tasks(p, d))
        self.assertFalse(self.Event.sudo().search([('definition_id', '=', d.id)]))

    def test_att_013_breached_not_reattached(self):
        """TC-ATT-013: task breached, start khớp lại -> không tạo task mới, event không đổi."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'DONE'}, T0 + hours(5))
        t = self.task_of(p, d)
        self.assertTrue(t.has_breached)
        n_events = len(t.event_ids)
        self.write(p, {'ref': 'NEW'}, T0 + hours(6))
        self.assertEqual(self.task_of(p, d).stage, 'breached')
        self.assertEqual(len(t.event_ids), n_events)

    def test_att_016_cancelled_start_and_stop(self):
        """TC-ATT-016: task cancelled, start `[]` khớp nhưng stop khớp -> không task mới."""
        d = self.make_definition(start_domain="[]", cancel_mode='condition')
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'CANCEL'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'cancelled')
        n_events = len(t.event_ids)
        self.write(p, {'ref': 'DONE'}, T0 + hours(2))
        self.assertEqual(len(self.tasks(p, d)), 1)
        self.assertEqual(t.stage, 'cancelled')
        self.assertEqual(len(t.event_ids), n_events)

    def test_att_018_stop_again_noop(self):
        """TC-ATT-018: stop khớp lần nữa trên task achieved -> không đổi."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertEqual((t.stage, t.end_time, len(t.event_ids)), ('achieved', T0 + hours(1), 2))
        self.write(p, {'ref': 'DONE'}, T0 + hours(2))
        self.assertEqual((t.stage, t.end_time, len(t.event_ids)), ('achieved', T0 + hours(1), 2))
        self.assertAlmostEqual(t.business_duration, 1.0, places=3)
        self.assertEqual(len(self.tasks(p, d)), 1)

    def test_att_021_stop_running_task(self):
        """TC-ATT-021: sửa field stop khi đang chạy -> achieved, elapsed 0.5."""
        d = self.make_definition()
        p = self.make_partner('WORK')
        self.write(p, {'ref': 'DONE'}, T0 + hours(0.5))
        t = self.task_of(p, d)
        self.assertEqual((t.stage, t.end_time), ('achieved', T0 + hours(0.5)))
        self.assertAlmostEqual(t.business_duration, 0.5, places=3)

    def test_att_024_paused_reevaluate_noop(self):
        """TC-ATT-024: đánh giá lại task paused khi dữ liệu không đổi -> không event, không đổi."""
        d = self.make_definition()
        p = self.make_partner('HOLD')
        t = self.task_of(p, d)
        snapshot = (t.stage, t.pause_time, t.business_duration, t.planned_end_time, len(t.event_ids))
        self.evaluate(p, T0 + hours(1))
        self.assertEqual(
            (t.stage, t.pause_time, t.business_duration, t.planned_end_time, len(t.event_ids)), snapshot)
        self.assertEqual(len(self.tasks(p, d)), 1)

    def test_att_025_026_no_change_no_event(self):
        """TC-ATT-025/026: đổi giữa hai giá trị cùng khớp start, hoặc ghi lại giá trị cũ -> không event."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        t = self.task_of(p, d)
        planned_end_time = t.planned_end_time
        self.write(p, {'ref': 'WORK'}, T0 + hours(1))
        self.assertEqual((t.stage, t.planned_end_time, len(t.event_ids)), ('in_progress', planned_end_time, 1))
        self.assertEqual(planned_end_time, T0 + hours(4))
        self.write(p, {'ref': 'WORK'}, T0 + hours(2))
        self.assertEqual(len(t.event_ids), 1)

    def test_att_027_hook_self_heals(self):
        """TC-ATT-027: patch hook bị xóa -> process_due đăng ký lại (log WARNING), record mới có task."""
        d = self.make_definition()
        self.no_commit_progress()
        model_class = type(self.env['res.partner'])
        self.assertTrue(getattr(model_class.create, 'sla_patch', False))
        for name in ('create', 'write', '_compute_field_value'):
            delattr(model_class, name)
        self.assertFalse(getattr(model_class.create, 'sla_patch', False))
        p1 = self.make_partner('NEW')
        self.assertFalse(self.tasks(p1, d))
        with self.assertLogs('odoo.addons.dwo_sla_core', 'WARNING') as cm, self.at(T0):
            self.Processor.process_due()
        self.assertTrue(any('res.partner' in r.getMessage() for r in cm.records))
        self.assertTrue(getattr(model_class.create, 'sla_patch', False))
        p2 = self.make_partner('NEW')
        t2 = self.task_of(p2, d)
        self.assertEqual((t2.stage, self.events(t2)), ('in_progress', ['attach']))
        self.evaluate(p1, T0)
        self.assertEqual(self.task_of(p1, d).stage, 'in_progress')


@tagged(*TAGS, 'tg_02')
class TestPauseResumeEdges(SlaCase):

    def setUp(self):
        super().setUp()
        self.d = self.make_definition()

    def test_pau_002_pause_again_noop(self):
        """TC-PAU-002: paused, pause vẫn khớp -> không event mới."""
        p = self.make_partner('WORK')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        t = self.task_of(p, self.d)
        self.assertEqual(len(t.event_ids), 2)
        self.write(p, {'ref': 'HOLD'}, T0 + hours(2))
        self.assertEqual((t.stage, t.pause_time, len(t.event_ids)), ('paused', T0 + hours(1), 2))
        self.assertAlmostEqual(t.business_duration, 1.0, places=3)

    def test_pau_003_achieved_ignores_pause(self):
        """TC-PAU-003: task achieved, pause khớp -> không đổi."""
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        t = self.task_of(p, self.d)
        self.write(p, {'ref': 'HOLD'}, T0 + hours(2))
        self.assertEqual((t.stage, t.end_time, len(t.event_ids)), ('achieved', T0 + hours(1), 2))
        self.assertEqual(len(self.tasks(p, self.d)), 1)

    def test_pau_005_condition_mode_needs_resume_match(self):
        """TC-PAU-005: chế độ condition, pause hết khớp nhưng resume chưa khớp -> vẫn paused."""
        p = self.make_partner('WORK')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        self.write(p, {'ref': 'NEW'}, T0 + hours(2))
        t = self.task_of(p, self.d)
        self.assertEqual(t.stage, 'paused')
        self.assertEqual(self.events(t).count('resume'), 0)
        self.assertEqual(len(t.event_ids), 2)

    def test_pau_006_pause_unmatched_resumes(self):
        """TC-PAU-006: pause_unmatched, pause hết khớp -> resume dù resume không khớp."""
        d = self.make_definition(name="PU", resume_mode='pause_unmatched')
        p = self.make_partner('WORK')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        self.write(p, {'ref': 'NEW'}, T0 + hours(2))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'in_progress')
        self.assertEqual(self.events(t), ['attach', 'pause', 'resume'])
        self.assertEqual(t.event_ids.filtered(lambda e: e.event == 'resume').event_dt, T0 + hours(2))

    def test_pau_007_pause_unmatched_still_paused(self):
        """TC-PAU-007: pause_unmatched, pause còn khớp dù resume `[]` khớp -> vẫn paused."""
        d = self.make_definition(name="PU2", resume_mode='pause_unmatched', resume_domain="[]")
        p = self.make_partner('WORK')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        self.write(p, {'ref': 'HOLD'}, T0 + hours(2))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'paused')
        self.assertEqual(self.events(t).count('resume'), 0)
        self.assertEqual(len(t.event_ids), 2)

    def test_pau_010_resume_keeps_planned_end_after_breach(self):
        """TC-PAU-010: resume khi đã breach -> planned_end_time giữ nguyên 13:00."""
        p = self.make_partner('WORK')
        t = self.task_of(p, self.d)
        self.Processor._process_task(t, T0 + hours(4) + hours(1 / 60.0))
        self.assertTrue(t.has_breached)
        planned_end_time = t.planned_end_time
        self.assertEqual(planned_end_time, T0 + hours(4))
        self.write(p, {'ref': 'HOLD'}, T0 + hours(4.5))
        self.assertEqual(t.stage, 'paused')
        self.assertAlmostEqual(t.business_duration, 4.5, places=3)
        self.write(p, {'ref': 'WORK'}, T0 + hours(5))
        self.assertEqual((t.stage, t.planned_end_time, t.has_breached), ('in_progress', planned_end_time, True))
