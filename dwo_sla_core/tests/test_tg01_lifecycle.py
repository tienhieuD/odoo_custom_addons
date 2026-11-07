# -*- coding: utf-8 -*-
"""TG-01, TG-02, TG-04, TG-05, TG-09, TG-10: vòng đời task (P1 trong docs/060).

Refs: REQ-FUNC-004, 006..012, 014..016, 029, 037, 044, 048, 001 (docs/060 TC-ATT/PAU/CAN/MIS/MUL/GEN)
"""
from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tools import mute_logger

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')


@tagged(*TAGS, 'tg_01')
class TestAttachStop(SlaCase):
    """TC-ATT-*: gắn, kết thúc, kích hoạt đánh giá."""

    def test_att_007_attach(self):
        """TC-ATT-007: start khớp, stop/cancel không khớp -> 1 task in_progress, 1 event attach."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'in_progress')
        self.assertEqual(t.start_time, T0)
        self.assertEqual(t.planned_end_time, T0 + hours(4))
        self.assertEqual(t.running_since, T0)
        self.assertEqual(self.events(t), ['attach'])

    def test_att_019_create_record_attaches(self):
        """TC-ATT-019: tạo record khớp start qua hook -> có 1 task."""
        d = self.make_definition()
        self.make_partner('NEW')
        self.assertEqual(len(self.tasks(definition=d)), 1)

    def test_att_017_stop_achieved(self):
        """TC-ATT-017: stop khi chưa quá hạn -> achieved, end_time = lúc stop, 1 event complete."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'achieved')
        self.assertEqual(t.end_time, T0 + hours(1))
        self.assertEqual(t.business_duration, 1.0)
        self.assertEqual(self.events(t), ['attach', 'complete'])
        self.assertFalse(t.next_due_at)

    def test_att_012_achieved_not_reattached(self):
        """TC-ATT-012: task achieved, start khớp lại -> không tạo task mới."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        self.write(p, {'ref': 'NEW'}, T0 + hours(2))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'achieved')
        self.assertEqual(self.events(t), ['attach', 'complete'])

    def test_att_014_achieved_not_reset(self):
        """TC-ATT-014: task achieved, reset và start cùng khớp -> không reset, không task mới."""
        d = self.make_definition(reset_domain="[('ref', '=', 'NEW')]")
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        self.write(p, {'ref': 'NEW'}, T0 + hours(2))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'achieved')
        self.assertNotIn('reset', self.events(t))

    def test_att_015_cancelled_reattach(self):
        """TC-ATT-015: task cancelled, start khớp lại -> task mới in_progress."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'OTHER'}, T0 + hours(1))   # start hết khớp -> cancel
        first = self.task_of(p, d)
        self.assertEqual(first.stage, 'cancelled')
        self.write(p, {'ref': 'NEW'}, T0 + hours(2))
        tasks = self.tasks(p, d)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[1].stage, 'in_progress')
        self.assertEqual(tasks[1].start_time, T0 + hours(2))
        self.assertEqual(self.events(tasks[1]), ['attach'])

    def test_att_022_unrelated_field_no_change(self):
        """TC-ATT-022: sửa field không thuộc điều kiện nào -> số task, số event không đổi."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        t = self.task_of(p, d)
        before = (len(self.Task.search([])), len(self.Event.search([])))
        self.write(p, {'comment': 'x'}, T0 + hours(1))
        self.assertEqual((len(self.Task.search([])), len(self.Event.search([]))), before)
        self.assertEqual(self.events(t), ['attach'])

    def test_att_023_reevaluate_idempotent(self):
        """TC-ATT-023: đánh giá lại ngay sau attach -> không task mới, không event mới."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        t = self.task_of(p, d)
        snapshot = t.read(['stage', 'planned_end_time', 'running_since', 'next_due_at'])
        for now in (T0, T0 + hours(1)):
            self.evaluate(p, now)
        self.assertEqual(len(self.tasks(p, d)), 1)
        self.assertEqual(t.read(['stage', 'planned_end_time', 'running_since', 'next_due_at']), snapshot)
        self.assertEqual(self.events(t), ['attach'])

    def test_att_001_empty_stop_never_matches(self):
        """TC-ATT-001: stop rỗng (chưa cấu hình) không bao giờ khớp dù ref=DONE."""
        d = self.make_definition(stop_domain=False, start_domain='[]')
        p = self.make_partner('DONE')
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'in_progress')
        self.assertNotIn('complete', self.events(t))

    def test_att_002_empty_list_matches_all(self):
        """TC-ATT-002: start = [] khớp mọi record."""
        d = self.make_definition(start_domain='[]')
        ps = [self.make_partner(r) for r in ('A', 'B', False)]
        for p in ps:
            self.assertEqual(len(self.tasks(p, d)), 1)


@tagged(*TAGS, 'tg_02')
class TestPauseResume(SlaCase):
    """TC-PAU-*: pause và resume."""

    def test_pau_001_pause(self):
        """TC-PAU-001: pause sau 1 giờ -> paused, đã trôi 1 giờ, 1 event pause."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'paused')
        self.assertEqual(t.business_duration, 1.0)
        self.assertEqual(t.pause_time, T0 + hours(1))
        self.assertFalse(t.running_since)
        self.assertFalse(t.next_due_at)
        self.assertEqual(self.events(t), ['attach', 'pause'])

    def test_pau_004_and_009_resume_replans_deadline(self):
        """TC-PAU-004/009: resume (condition) -> in_progress, planned_end_time = resume + phần còn lại."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        self.write(p, {'ref': 'WORK'}, T0 + hours(9))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'in_progress')
        self.assertEqual(t.running_since, T0 + hours(9))
        self.assertEqual(t.planned_end_time, T0 + hours(12))  # còn 3 giờ
        self.assertEqual(t.business_duration, 1.0)
        self.assertFalse(t.pause_time)
        self.assertEqual(self.events(t), ['attach', 'pause', 'resume'])

    def test_pau_008_011_full_lifecycle(self):
        """TC-PAU-008/011: attach, pause, resume, stop -> đúng 4 event theo thứ tự, achieved."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        self.write(p, {'ref': 'WORK'}, T0 + hours(2))
        self.write(p, {'ref': 'DONE'}, T0 + hours(3))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'achieved')
        self.assertEqual(self.events(t), ['attach', 'pause', 'resume', 'complete'])
        self.assertEqual(t.business_duration, 2.0)  # 1h + 1h
        dts = t.event_ids.sorted('id').mapped('event_dt')
        self.assertEqual(dts, sorted(dts))

    def test_pau_resume_pause_unmatched_mode(self):
        """TC-PAU-008: resume_mode=pause_unmatched resume khi pause hết khớp."""
        d = self.make_definition(resume_mode='pause_unmatched', resume_domain=False)
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        self.assertEqual(self.task_of(p, d).stage, 'paused')
        self.write(p, {'ref': 'NEW'}, T0 + hours(2))
        self.assertEqual(self.task_of(p, d).stage, 'in_progress')

    def test_pau_resume_condition_not_matching_stays_paused(self):
        """Resume (condition) không khớp -> task vẫn paused, không event mới."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        self.write(p, {'comment': 'still waiting'}, T0 + hours(2))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'paused')
        self.assertEqual(self.events(t), ['attach', 'pause'])


@tagged(*TAGS, 'tg_04')
class TestPriorityCancelReset(SlaCase):
    """TC-CAN-*: bảng ưu tiên stop → cancel → reset → pause → resume."""

    def test_can_001_stop_beats_pause(self):
        """TC-CAN-001: stop và pause cùng khớp -> complete, không event pause."""
        d = self.make_definition(pause_domain="[('ref', 'in', ['HOLD', 'DONE'])]")
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'achieved')
        self.assertEqual(self.events(t), ['attach', 'complete'])

    def test_can_002_stop_beats_cancel(self):
        """TC-CAN-002: stop và cancel (condition) cùng khớp -> complete."""
        d = self.make_definition(
            cancel_mode='condition', cancel_domain="[('ref', 'in', ['CANCEL', 'DONE'])]")
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        self.assertEqual(self.task_of(p, d).stage, 'achieved')

    def test_can_003_cancel_beats_pause(self):
        """TC-CAN-003: cancel (condition) và pause cùng khớp -> cancelled."""
        d = self.make_definition(
            cancel_mode='condition', cancel_domain="[('ref', '=', 'HOLD')]")
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'cancelled')
        self.assertNotIn('pause', self.events(t))

    def test_can_004_reset_beats_pause(self):
        """TC-CAN-004: reset, start, pause cùng khớp -> reset; task mới paused; task cũ không event pause."""
        d = self.make_definition(reset_domain="[('ref', '=', 'HOLD')]")
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        tasks = self.tasks(p, d)
        self.assertEqual(len(tasks), 2)
        old, new = tasks
        self.assertEqual(old.stage, 'cancelled')
        self.assertNotIn('pause', self.events(old))
        self.assertIn('reset', self.events(old))
        self.assertEqual(new.stage, 'paused')
        self.assertEqual(self.events(new), ['attach'])

    def test_can_005_nothing_matches_no_change(self):
        """TC-CAN-005: không điều kiện nào khớp -> giữ nguyên task, không event mới."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'WORK'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'in_progress')
        self.assertEqual(self.events(t), ['attach'])

    def test_can_007_start_unmatched_cancels(self):
        """TC-CAN-007: cancel_mode=start_unmatched, start hết khớp -> cancelled."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'OTHER'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'cancelled')
        self.assertEqual(t.end_time, T0 + hours(1))
        self.assertEqual(self.events(t), ['attach', 'cancel'])

    def test_can_008_condition_cancels_while_start_matches(self):
        """TC-CAN-008: cancel_mode=condition, cancel khớp dù start vẫn khớp -> cancelled."""
        d = self.make_definition(
            cancel_mode='condition', cancel_domain="[('ref', '=', 'WORK')]")
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'WORK'}, T0 + hours(1))
        self.assertEqual(self.task_of(p, d).stage, 'cancelled')

    def test_can_009_never_does_not_cancel(self):
        """TC-CAN-009: cancel_mode=never -> không hủy dù start hết khớp và cancel khớp."""
        d = self.make_definition(cancel_mode='never')
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'CANCEL'}, T0 + hours(1))
        self.assertEqual(self.task_of(p, d).stage, 'in_progress')

    def test_reset_complete_action(self):
        """Reset với reset_action=complete: task cũ achieved rồi gắn task mới."""
        d = self.make_definition(reset_domain="[('ref', '=', 'WORK')]", reset_action='complete')
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'WORK'}, T0 + hours(1))
        old, new = self.tasks(p, d)
        self.assertEqual(old.stage, 'achieved')
        self.assertEqual(new.stage, 'in_progress')
        self.assertEqual(self.events(old)[-1], 'reset')

    def test_reset_only_when_tracked_field_changes(self):
        """REQ-FUNC-013/050: có field theo dõi -> chỉ reset khi field đó đổi giá trị."""
        field = self.env['ir.model.fields']._get('res.partner', 'ref')
        d = self.make_definition(
            reset_domain="[('ref', '=', 'WORK')]", reset_field_ids=[(6, 0, field.ids)])
        p = self.make_partner('WORK')
        self.write(p, {'comment': 'x'}, T0 + hours(1))      # field khác: không reset
        self.write(p, {'ref': 'WORK'}, T0 + hours(2))        # cùng giá trị: không reset
        self.assertEqual(len(self.tasks(p, d)), 1)
        self.write(p, {'ref': 'NEW'}, T0 + hours(3))
        self.write(p, {'ref': 'WORK'}, T0 + hours(4))        # đổi giá trị: reset
        self.assertEqual(len(self.tasks(p, d)), 2)


@tagged(*TAGS, 'tg_05')
class TestMisconfig(SlaCase):
    """TC-MIS-*: ba cấu hình dễ sai."""

    def test_mis_001_start_subset_of_stop(self):
        """TC-MIS-001: start là tập con của stop -> không gắn SLA."""
        d = self.make_definition(start_domain="[('ref', '=', 'DONE')]")
        p = self.make_partner('DONE')
        self.assertFalse(self.tasks(p, d))

    def test_mis_004_attach_paused(self):
        """TC-MIS-004: pause là tập con của start -> attach thẳng vào paused, chỉ 1 event attach."""
        d = self.make_definition()
        p = self.make_partner('HOLD')
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'paused')
        self.assertEqual(self.events(t), ['attach'])
        self.assertFalse(t.next_due_at)

    def test_mis_005_leaving_hold_cancels(self):
        """TC-MIS-005: rời hold -> pause hết khớp kéo theo start hết khớp -> cancelled."""
        d = self.make_definition(start_domain="[('ref', '=', 'HOLD')]")
        p = self.make_partner('HOLD')
        self.write(p, {'ref': 'NEW'}, T0 + hours(1))
        self.assertEqual(self.task_of(p, d).stage, 'cancelled')

    def test_mis_006_exclusive_start_pause_cancel_no_pause_event(self):
        """TC-MIS-006: start/pause loại trừ nhau, start_unmatched -> cancelled, không event pause."""
        d = self.make_definition(
            start_domain="[('ref', '=', 'NEW')]", pause_domain="[('ref', '=', 'HOLD')]")
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'cancelled')
        self.assertNotIn('pause', self.events(t))

    def test_mis_007_exclusive_never_pauses(self):
        """TC-MIS-007: start/pause loại trừ nhau, cancel never -> task chuyển paused."""
        d = self.make_definition(
            start_domain="[('ref', '=', 'NEW')]", pause_domain="[('ref', '=', 'HOLD')]",
            cancel_mode='never')
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        self.assertEqual(self.task_of(p, d).stage, 'paused')


@tagged(*TAGS, 'tg_09')
class TestMultipleDefinitions(SlaCase):
    """TC-MUL-*: nhiều SLA song song và một task hoạt động cho mỗi (định nghĩa, record)."""

    def test_mul_001_002_independent_tasks(self):
        """TC-MUL-001/002: hai định nghĩa -> hai task độc lập; stop của một không đụng task kia."""
        resp = self.make_definition(name="Response", stop_domain="[('ref', '=', 'WORK')]")
        reso = self.make_definition(name="Resolution")
        p = self.make_partner('NEW')
        self.assertEqual(len(self.tasks(p)), 2)
        self.write(p, {'ref': 'WORK'}, T0 + hours(1))
        self.assertEqual(self.task_of(p, resp).stage, 'achieved')
        self.assertEqual(self.task_of(p, reso).stage, 'in_progress')

    def test_mul_004_second_active_task_rejected(self):
        """TC-MUL-004/006: chỉ một task hoạt động cho mỗi (định nghĩa, record) -> unique index chặn."""
        d = self.make_definition()
        p = self.make_partner('HOLD')
        self.task_of(p, d)
        match = self.Engine._match_sets(d, p)
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'), \
                self.env.cr.savepoint():
            self.Engine._attach(d, p, T0, match)

    def test_mul_008_conflict_logged_as_error_event(self):
        """TC-MUL-008: gắn trùng trong evaluate -> ghi event error, record/task gốc nguyên vẹn."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        t = self.task_of(p, d)
        # Mô phỏng bên thua: Engine không thấy task hoạt động (cache cũ) rồi gắn lại.
        match = self.Engine._match_sets(d, p)
        with mute_logger('odoo.sql_db', 'odoo.addons.dwo_sla_core.models.sla_event'):
            with self.env.cr.savepoint():
                try:
                    with self.env.cr.savepoint():
                        self.Engine._maybe_attach(d, p, T0, False, match)
                except IntegrityError as exc:
                    self.Event._log_error(
                        definition=d, res_model=p._name, res_id=p.id, message=str(exc))
        errors = self.Event.search([('event', '=', 'error'), ('res_id', '=', p.id)])
        self.assertEqual(len(errors), 1)
        self.assertEqual(self.tasks(p, d), t)


@tagged(*TAGS, 'tg_10')
class TestGeneric(SlaCase):
    """TC-GEN-001: cấu hình cho model bất kỳ chỉ bằng dữ liệu."""

    def test_gen_001_two_models(self):
        """TC-GEN-001: hai model khác nhau cùng gắn SLA chỉ bằng cấu hình."""
        categ_model = self.env['ir.model']._get('res.partner.category')
        d1 = self.make_definition(name="Partners")
        d2 = self.Definition.create({
            'name': "Categories", 'model_id': categ_model.id, 'duration': 2,
            'start_domain': "[('name', '=', 'VIP')]",
        })
        p = self.make_partner('NEW')
        with self.at(T0):
            c = self.env['res.partner.category'].create({'name': 'VIP'})
        t1 = self.task_of(p, d1)
        t2 = self.Task.search([('sla_id', '=', d2.id), ('res_id', '=', c.id)])
        self.assertEqual(len(t2), 1)
        self.assertEqual(t2.res_model, 'res.partner.category')
        self.assertEqual(t2.planned_end_time, T0 + hours(2))
        self.assertEqual(t1.planned_end_time, T0 + hours(4))
