# -*- coding: utf-8 -*-
"""TG-04 bổ sung: cancel, reset, reset theo field (docs/060 TC-CAN-*).

Refs: REQ-FUNC-007, 010..013, 050
"""
from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')
START_RESET = "[('ref', 'in', ['NEW', 'WORK', 'HOLD', 'RESET'])]"
RESET_REF = "[('ref', '=', 'RESET')]"


class ResetCase(SlaCase):

    def reset_def(self, **vals):
        base = {'start_domain': START_RESET, 'reset_domain': RESET_REF}
        base.update(vals)
        return self.make_definition(**base)

    def field_reset_def(self, fields_, **vals):
        names = fields_ if isinstance(fields_, (list, tuple)) else [fields_]
        ids = self.env['ir.model.fields'].search([
            ('model', '=', 'res.partner'), ('name', 'in', names)]).ids
        base = {'start_domain': START_RESET, 'reset_domain': "[('id', '!=', 0)]", 'reset_field_ids': [(6, 0, ids)]}
        base.update(vals)
        return self.make_definition(**base)

    def reset_count(self, partner, d):
        return sum(self.events(t).count('reset') for t in self.tasks(partner, d))

    def event_count(self, partner, d, name):
        return sum(self.events(t).count(name) for t in self.tasks(partner, d))


@tagged(*TAGS, 'tg_04')
class TestCancelRules(ResetCase):

    def test_can_006_cancel_beats_reset(self):
        """TC-CAN-006: cancel (condition), reset và start cùng khớp -> hủy, không reset."""
        d = self.reset_def(cancel_mode='condition', cancel_domain=RESET_REF)
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'RESET'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'cancelled')
        self.assertEqual((self.events(t).count('cancel'), self.events(t).count('reset')), (1, 0))

    def test_can_010_condition_mode_needs_cancel_match(self):
        """TC-CAN-010: chế độ condition, start hết khớp nhưng cancel không khớp -> không hủy."""
        d = self.make_definition(cancel_mode='condition')
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'OTHER'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'in_progress')
        self.assertEqual(self.events(t).count('cancel'), 0)

    def test_can_011_start_unmatched_needs_start_gone(self):
        """TC-CAN-011: start_unmatched, cancel khớp nhưng start vẫn khớp -> không hủy."""
        d = self.make_definition(cancel_domain="[('ref', '=', 'WORK')]")
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'WORK'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'in_progress')
        self.assertEqual(self.events(t).count('cancel'), 0)


@tagged(*TAGS, 'tg_04')
class TestResetAction(ResetCase):

    def test_can_012_reset_cancel(self):
        """TC-CAN-012: reset_action cancel -> task cũ cancelled, task mới in_progress từ 10:00."""
        d = self.reset_def(reset_action='cancel')
        p = self.make_partner('NEW')
        old = self.task_of(p, d)
        self.assertEqual(old.planned_end_time, T0 + hours(4))
        self.write(p, {'ref': 'RESET'}, T0 + hours(1))
        self.assertEqual((old.stage, old.end_time), ('cancelled', T0 + hours(1)))
        new = self.tasks(p, d, 'in_progress')
        self.assertEqual((new.start_time, new.planned_end_time), (T0 + hours(1), T0 + hours(5)))
        names = self.events(old)
        self.assertEqual(names.count('reset'), 1)
        self.assertGreater(names.index('reset'), names.index('cancel'))
        self.assertNotIn('pause', names)

    def test_can_013_reset_complete(self):
        """TC-CAN-013: reset_action complete trước hạn -> task cũ achieved, task mới chạy."""
        d = self.reset_def(reset_action='complete')
        p = self.make_partner('NEW')
        old = self.task_of(p, d)
        self.write(p, {'ref': 'RESET'}, T0 + hours(1))
        self.assertEqual((old.stage, old.end_time), ('achieved', T0 + hours(1)))
        names = self.events(old)
        self.assertGreater(names.index('reset'), names.index('complete'))
        self.assertEqual(self.tasks(p, d, 'in_progress').start_time, T0 + hours(1))

    def test_can_014_new_task_paused(self):
        """TC-CAN-014: reset và pause cùng khớp -> task mới attach ở paused."""
        d = self.reset_def(reset_action='complete', pause_domain="[('ref', 'in', ['HOLD', 'RESET'])]")
        p = self.make_partner('NEW')
        old = self.task_of(p, d)
        self.write(p, {'ref': 'RESET'}, T0 + hours(1))
        self.assertEqual(old.stage, 'achieved')
        self.assertEqual(len(self.tasks(p, d, 'paused')), 1)

    def test_can_015_latest_achieved_not_reset(self):
        """TC-CAN-015: task gần nhất achieved -> reset + start khớp không đổi gì."""
        d = self.reset_def(reset_action='cancel')
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertEqual((t.stage, t.end_time, len(t.event_ids)), ('achieved', T0 + hours(1), 2))
        self.write(p, {'ref': 'RESET'}, T0 + hours(2))
        self.assertEqual((len(self.tasks(p, d)), t.stage, len(t.event_ids)), (1, 'achieved', 2))
        self.assertEqual(self.reset_count(p, d), 0)

    def test_can_016_reset_without_start_no_branch(self):
        """TC-CAN-016: reset khớp nhưng start không khớp (cancel_mode never) -> không làm gì."""
        d = self.make_definition(reset_domain=RESET_REF, cancel_mode='never')
        p = self.make_partner('NEW')
        t = self.task_of(p, d)
        self.write(p, {'ref': 'RESET'}, T0 + hours(1))
        self.assertEqual((len(self.tasks(p, d)), t.stage, bool(t.end_time), len(t.event_ids)),
                         (1, 'in_progress', False, 1))

    def test_can_017_reset_paused_task(self):
        """TC-CAN-017: reset task đang paused -> hủy task cũ, task mới in_progress."""
        d = self.reset_def(reset_action='cancel')
        p = self.make_partner('HOLD')
        old = self.task_of(p, d)
        self.assertEqual(old.stage, 'paused')
        self.write(p, {'ref': 'RESET'}, T0 + hours(1))
        self.assertEqual(old.stage, 'cancelled')
        self.assertEqual(self.tasks(p, d, 'in_progress').start_time, T0 + hours(1))

    def test_can_018_reset_complete_after_planned_end(self):
        """TC-CAN-018: reset complete khi đã quá planned_end_time -> task cũ breached."""
        d = self.reset_def(reset_action='complete')
        p = self.make_partner('NEW')
        old = self.task_of(p, d)
        self.write(p, {'ref': 'RESET'}, T0 + hours(5))
        self.assertEqual((old.stage, old.end_time), ('breached', T0 + hours(5)))
        names = self.events(old)
        self.assertGreater(names.index('reset'), names.index('complete'))
        new = self.tasks(p, d, 'in_progress')
        self.assertEqual((new.start_time, new.planned_end_time), (T0 + hours(5), T0 + hours(9)))

    def test_can_019_attach_after_cancelled_not_reset(self):
        """TC-CAN-019: task gần nhất cancelled, reset + start khớp -> attach mới, không reset."""
        d = self.reset_def(reset_action='cancel', cancel_mode='condition',
                           cancel_domain="[('ref', '=', 'CANCEL')]",
                           start_domain="[('ref', 'in', ['NEW', 'WORK', 'HOLD', 'RESET', 'CANCEL'])]")
        p = self.make_partner('NEW')
        t1 = self.task_of(p, d)
        self.write(p, {'ref': 'CANCEL'}, T0 + hours(1))
        self.assertEqual(t1.stage, 'cancelled')
        self.write(p, {'ref': 'RESET'}, T0 + hours(2))
        t2 = self.tasks(p, d, 'in_progress')
        self.assertEqual(t2.start_time, T0 + hours(2))
        self.assertEqual((self.reset_count(p, d), self.event_count(p, d, 'attach')), (0, 2))

    def test_can_032_reset_then_reattach_unique_index(self):
        """TC-CAN-032: reset rồi attach lại sau cancelled -> không vi phạm chỉ mục duy nhất, không event error."""
        d = self.reset_def(reset_action='cancel')
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'RESET'}, T0 + hours(1))
        self.assertEqual(len(self.tasks(p, d, 'in_progress')), 1)
        self.write(p, {'ref': 'CANCEL'}, T0 + hours(2))
        self.assertFalse(self.tasks(p, d, 'in_progress'))
        self.write(p, {'ref': 'RESET'}, T0 + hours(3))
        self.assertEqual(len(self.tasks(p, d)), 3)
        self.assertEqual(len(self.tasks(p, d, 'in_progress')), 1)
        self.assertFalse(self.Event.sudo().search([('event', '=', 'error'), ('res_id', '=', p.id)]))
        self.env['base'].flush()
        self.env.cr.execute(
            "SELECT count(*) FROM sla_task WHERE sla_id=%s AND res_id=%s "
            "AND stage IN ('in_progress','paused')", (d.id, p.id))
        self.assertEqual(self.env.cr.fetchone()[0], 1)


@tagged(*TAGS, 'tg_04')
class TestResetOnField(ResetCase):

    def setUp(self):
        super().setUp()
        self.u1 = self.make_user('sla_reset_u1')
        self.u2 = self.make_user('sla_reset_u2')

    def partner(self, **vals):
        return self.make_partner('NEW', user_id=self.u1.id, **vals)

    def test_can_020_30_field_changed_resets(self):
        """TC-CAN-020/030: user_id đổi, reset `[]` -> reset; note chứa tên field."""
        d = self.field_reset_def('user_id')
        p = self.partner()
        old = self.task_of(p, d)
        self.write(p, {'user_id': self.u2.id}, T0 + hours(1))
        self.assertEqual(old.stage, 'cancelled')
        self.assertEqual(self.tasks(p, d, 'in_progress').start_time, T0 + hours(1))
        notes = old.event_ids.filtered(lambda e: e.event == 'reset').mapped('note')
        self.assertEqual(self.reset_count(p, d), 1)
        self.assertIn('user_id', notes[0])

    def test_can_021_25_unchanged_values_no_reset(self):
        """TC-CAN-021/025: ghi lại đúng giá trị cũ -> không reset."""
        d = self.field_reset_def(['user_id', 'comment'])
        p = self.partner(comment='A')
        t = self.task_of(p, d)
        self.write(p, {'user_id': self.u1.id, 'comment': 'A'}, T0 + hours(1))
        self.assertEqual((len(self.tasks(p, d)), t.stage, self.reset_count(p, d)), (1, 'in_progress', 0))
        d2 = self.field_reset_def('user_id', name="empty")
        p2 = self.make_partner('NEW')
        self.write(p2, {'user_id': False}, T0 + hours(1))
        self.assertEqual((len(self.tasks(p2, d2)), self.reset_count(p2, d2)), (1, 0))

    def test_can_022_computed_stored_field(self):
        """TC-CAN-022: field compute có lưu (complete_name) đổi do tính lại -> reset."""
        d = self.field_reset_def('complete_name')
        p = self.make_partner('NEW', name="P-01")
        old = self.task_of(p, d)
        self.write(p, {'name': "P-01-X"}, T0 + hours(1))
        with self.at(T0 + hours(1)):
            self.env['base'].flush()  # complete_name tính lại lúc flush -> hook compute đánh giá
        self.assertEqual(old.stage, 'cancelled')
        self.assertEqual(self.reset_count(p, d), 1)

    def test_can_023_reset_condition_unmatched(self):
        """TC-CAN-023: field theo dõi đổi nhưng điều kiện reset không khớp -> không reset."""
        d = self.field_reset_def('user_id', reset_domain=RESET_REF)
        p = self.partner()
        t = self.task_of(p, d)
        self.write(p, {'user_id': self.u2.id}, T0 + hours(1))
        self.assertEqual((len(self.tasks(p, d)), t.stage, self.reset_count(p, d)), (1, 'in_progress', 0))

    def test_can_024_one_of_two_fields(self):
        """TC-CAN-024/031: chỉ một trong hai field đổi vẫn reset; note nêu field đã đổi."""
        d = self.field_reset_def(['user_id', 'comment'])
        p = self.partner(comment='A')
        old = self.task_of(p, d)
        self.write(p, {'comment': 'B'}, T0 + hours(1))
        self.assertEqual(old.stage, 'cancelled')
        self.assertEqual(self.reset_count(p, d), 1)
        p2 = self.partner(comment='A')
        old2 = self.task_of(p2, d)
        self.write(p2, {'user_id': self.u2.id, 'comment': 'B'}, T0 + hours(1))
        note = old2.event_ids.filtered(lambda e: e.event == 'reset').note
        self.assertIn('user_id', note)
        self.assertIn('comment', note)

    def test_can_026_other_field_no_reset(self):
        """TC-CAN-026: ghi field không theo dõi -> không reset."""
        d = self.field_reset_def('user_id')
        p = self.partner()
        t = self.task_of(p, d)
        self.write(p, {'phone': '0901234567'}, T0 + hours(1))
        self.assertEqual((len(self.tasks(p, d)), t.stage, self.reset_count(p, d)), (1, 'in_progress', 0))

    def test_can_027_28_manual_and_background_no_reset(self):
        """TC-CAN-027/028: Đánh giá lại thủ công và xử lý nền không reset."""
        d = self.field_reset_def('user_id')
        p = self.partner()
        t = self.task_of(p, d)
        manager = self.make_user('sla_mgr_reset', 'manager')
        with self.at(T0 + hours(1)):
            t.with_user(manager).action_reevaluate()
        self.Processor._process_task(t, T0 + hours(2))
        # Event `reevaluate` là dấu vết của chính nút Re-check Conditions, không tính.
        engine_events = t.event_ids.filtered(lambda e: e.event != 'reevaluate')
        self.assertEqual((len(self.tasks(p, d)), t.stage, self.reset_count(p, d), len(engine_events)),
                         (1, 'in_progress', 0, 1))

    def test_can_029_empty_reset_domain(self):
        """TC-CAN-029: reset_domain rỗng (chưa cấu hình) dù field theo dõi đổi -> không reset."""
        d = self.field_reset_def('user_id', reset_domain=False)
        p = self.partner()
        t = self.task_of(p, d)
        self.write(p, {'user_id': self.u2.id}, T0 + hours(1))
        self.assertEqual((len(self.tasks(p, d)), t.stage, self.reset_count(p, d)), (1, 'in_progress', 0))
