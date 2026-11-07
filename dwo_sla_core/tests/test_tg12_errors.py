# -*- coding: utf-8 -*-
"""TG-12: lỗi engine, event error, đánh giá lại hàng loạt (docs/060 TC-ERR-*).

Điều kiện lỗi dựng bằng cách ghi thẳng SQL một domain trỏ field không tồn tại
(bỏ qua constraint khi lưu), mô phỏng field bị gỡ sau khi đã lưu định nghĩa.
Refs: REQ-FUNC-030, 031, 040, REQ-OBS-001..003, REQ-SEC-006
"""
from unittest.mock import patch

from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')
BROKEN = "[('field_was_removed', '=', 'x')]"
LOGGER = 'odoo.addons.dwo_sla_core'


@tagged(*TAGS, 'tg_12')
class TestEngineErrors(SlaCase):

    def setUp(self):
        super().setUp()
        self.d = self.make_definition()
        self.manager = self.make_user('sla_mgr_err', 'manager')
        self.viewer = self.make_user('sla_usr_err', 'user')

    def break_definition(self):
        self.env.cr.execute(
            "UPDATE sla_definition SET start_domain = %s WHERE id = %s",
            (BROKEN, self.d.id))
        self.d.invalidate_recordset()

    def fix_definition(self):
        self.d.start_domain = "[('ref', 'in', ['NEW', 'WORK', 'HOLD'])]"

    def errors(self, resolved=None):
        domain = [('event', '=', 'error')]
        if resolved is not None:
            domain.append(('is_resolved', '=', resolved))
        return self.Event.sudo().search(domain, order='id')

    def broken_partner(self, ref='NEW', **vals):
        self.break_definition()
        with self.assertLogs(LOGGER, 'ERROR'):
            return self.make_partner(ref, **vals)

    def test_err_001_002_record_saved_with_error_event(self):
        """TC-ERR-001/002/006/012: record vẫn lưu, không task, 1 event error đủ ngữ cảnh, chưa xử lý."""
        p = self.broken_partner()
        self.assertTrue(p.exists())
        self.assertFalse(self.tasks(p))
        err = self.errors()
        self.assertEqual(len(err), 1)
        self.assertEqual((err.res_model, err.res_id), ('res.partner', p.id))
        self.assertEqual(err.definition_id, self.d)
        self.assertTrue(err.note)
        self.assertFalse(err.is_resolved)

    def test_err_008_log_line(self):
        """TC-ERR-008: đúng 1 dòng log ERROR chứa model, id, tên định nghĩa."""
        self.break_definition()
        with self.assertLogs(LOGGER, 'ERROR') as cm:
            p = self.make_partner('NEW')
        self.assertEqual(len(cm.records), 1)
        msg = cm.records[0].getMessage()
        for token in ('res.partner', str(p.id), self.d.name):
            self.assertIn(token, msg)

    def test_err_009_011_no_field_values_leak(self):
        """TC-ERR-009/011: giá trị field (SECRET-123) không xuất hiện trong event và log."""
        self.break_definition()
        with self.assertLogs(LOGGER, 'ERROR') as cm:
            self.make_partner('NEW', comment='SECRET-123', street='SECRET-123')
        self.assertNotIn('SECRET-123', ''.join(r.getMessage() for r in cm.records))
        for event in self.errors():
            self.assertNotIn('SECRET-123', event.note or '')

    def test_err_011c_engine_error_value_in_message(self):
        """TC-ERR-011: exception của engine trích giá trị field -> event và log không còn giá trị."""
        failing = patch.object(
            type(self.env['sla.time']), 'plan', side_effect=ValueError('cannot plan for SECRET-123'))
        with failing, self.assertLogs(LOGGER, 'ERROR') as cm:
            self.make_partner('NEW', street='SECRET-123')
        self.assertNotIn('SECRET-123', ''.join(r.getMessage() for r in cm.records))
        errors = self.errors()
        self.assertTrue(errors)
        for event in errors:
            self.assertNotIn('SECRET-123', event.note or '')
            self.assertIn('<redacted>', event.note or '')

    def test_err_011b_raw_exception_values_redacted(self):
        """REQ-OBS-003: exception gốc trích giá trị field -> note và log chỉ có <redacted>."""
        action = self.make_server_action("raise UserError('failed for ' + record.comment)")
        self.make_escalation(self.d, 50, action=action)
        p = self.make_partner('NEW', comment='SECRET-123')
        t = self.task_of(p, self.d)
        with self.assertLogs('odoo.addons.dwo_sla_core', 'ERROR') as cm:
            self.Processor._process_task(t, T0 + hours(2))
        self.assertNotIn('SECRET-123', ''.join(r.getMessage() for r in cm.records))
        note = t.event_ids.filtered(lambda e: e.event == 'escalate_failed').note
        self.assertIn('failed for', note)
        self.assertIn('<redacted>', note)
        self.assertNotIn('SECRET-123', note)

    def test_err_013_mark_resolved(self):
        """TC-ERR-013: đánh dấu đã xử lý làm giảm số event chưa xử lý đúng 1."""
        self.broken_partner()
        self.broken_partner()
        before = len(self.errors(resolved=False))
        self.errors()[0].with_user(self.manager).action_mark_resolved()
        self.assertEqual(len(self.errors(resolved=False)), before - 1)

    def test_err_014_reevaluate_resolves(self):
        """TC-ERR-014/016: sửa lỗi rồi đánh giá lại -> task được tạo, event chuyển đã xử lý."""
        partners = [self.broken_partner() for _ in range(3)]
        self.fix_definition()
        with self.at(T0 + hours(1)):
            self.errors().with_user(self.manager).action_reevaluate_batch()
        for p in partners:
            self.assertEqual(len(self.tasks(p, self.d)), 1)
        self.assertFalse(self.errors(resolved=False))

    def test_err_015_still_broken(self):
        """TC-ERR-015: vẫn lỗi -> event cũ giữ chưa xử lý, có event error mới."""
        self.broken_partner()
        old = self.errors()
        with self.assertLogs(LOGGER, 'ERROR'), self.at(T0 + hours(1)):
            old.with_user(self.manager).action_reevaluate_batch()
        self.assertFalse(old.is_resolved)
        self.assertEqual(len(self.errors()), 2)

    def test_err_017_keeps_achieved_task(self):
        """TC-ERR-017: đánh giá lại hàng loạt giữ nguyên task đã achieved."""
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        t = self.task_of(p, self.d)
        self.Event._log_error(definition=self.d, res_model='res.partner',
                              res_id=p.id, message="x")
        with self.at(T0 + hours(2)):
            self.errors().with_user(self.manager).action_reevaluate_batch()
        self.assertEqual(t.stage, 'achieved')
        self.assertEqual(len(self.tasks(p)), 1)

    def test_err_018_ignores_non_error_events(self):
        """TC-ERR-018: event không phải error bị bỏ qua khi đánh giá lại hàng loạt."""
        p = self.make_partner('NEW')
        attach = self.task_of(p, self.d).event_ids
        with self.at(T0 + hours(1)):
            attach.with_user(self.manager).action_reevaluate_batch()
        self.assertFalse(attach.is_resolved)

    def test_err_019_viewer_denied(self):
        """TC-ERR-019: group_sla_user không gọi được đánh giá lại hàng loạt."""
        self.broken_partner()
        with self.assertRaises(AccessError):
            self.errors().with_user(self.viewer).action_reevaluate_batch()

    def test_err_020_start_now_without_retroactive(self):
        """TC-ERR-020: không bật retroactive -> start_time = thời điểm đánh giá lại."""
        self.broken_partner()
        p = self.Partner.search([], order='id desc', limit=1)
        now = T0 + hours(2)
        self.fix_definition()
        with self.at(now):
            self.errors().with_user(self.manager).action_reevaluate_batch()
        self.assertEqual(self.task_of(p, self.d).start_time, now)
