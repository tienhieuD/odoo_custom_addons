# -*- coding: utf-8 -*-
"""TG-12 bổ sung: lỗi engine, cô lập, nhãn số event lỗi (docs/060 TC-ERR-*).

Refs: REQ-FUNC-030, 031, 040, REQ-OBS-001, REQ-INT-021, 022, REQ-SEC-003
"""
from unittest.mock import patch

from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import SlaCase, T0, hours
from .test_tg12_errors import BROKEN, LOGGER

TAGS = ('post_install', '-at_install', 'dwo_sla_core')


@tagged(*TAGS, 'tg_12')
class TestEngineErrorsMore(SlaCase):

    def setUp(self):
        super().setUp()
        self.manager = self.make_user('sla_mgr_err2', 'manager')
        self.none_user = self.make_user('sla_none_err2')

    def errors(self):
        return self.Event.sudo().search([('event', '=', 'error')], order='id')

    def broken_definition(self, **vals):
        d = self.make_definition(**vals)
        self.env.cr.execute("UPDATE sla_definition SET start_domain=%s WHERE id=%s", (BROKEN, d.id))
        d.invalidate_cache(None, ids=d.ids)
        return d

    def calendar_error_definition(self):
        cal = self.make_calendar()
        d = self.make_definition(schedule_source='definition', schedule_id=cal.id)
        cal.attendance_ids.unlink()
        return d

    def test_err_003_007_empty_calendar(self):
        """TC-ERR-003/007: lịch bị xóa hết giờ làm -> record vẫn lưu, không task, 1 event error đủ ngữ cảnh."""
        d = self.calendar_error_definition()
        with self.assertLogs(LOGGER, 'ERROR'):
            p = self.make_partner('NEW', company_id=self.env.user.company_id.id)
        self.assertEqual(p.ref, 'NEW')
        self.assertFalse(self.tasks(p))
        err = self.errors()
        self.assertEqual(len(err), 1)
        self.assertFalse(err.task_id)
        self.assertEqual((err.res_model, err.res_id, err.definition_id), ('res.partner', p.id, d))
        self.assertTrue(err.note)
        self.assertEqual(err.company_id, p.company_id)

    def test_err_004_isolation_per_record(self):
        """TC-ERR-004: lỗi ở R1 không ngăn R2 được attach trong cùng lô."""
        r1, r2 = self.make_partner('NEW'), self.make_partner('NEW')
        d = self.make_definition()
        original = type(d)._get_start_dt

        def start_time(definition, record, now):
            if record.id == r1.id:
                raise ValueError('plan failed')
            return original(definition, record, now)

        with patch.object(type(d), '_get_start_dt', start_time), self.assertLogs(LOGGER, 'ERROR'):
            self.evaluate(r1 | r2, T0)
        self.assertFalse(self.tasks(r1, d))
        e1 = self.Event.sudo().search([('res_id', '=', r1.id), ('definition_id', '=', d.id)])
        self.assertEqual(e1.mapped('event'), ['error'])
        t2 = self.task_of(r2, d)
        self.assertEqual((t2.stage, t2.start_time, t2.planned_end_time), ('in_progress', T0, T0 + hours(4)))
        self.assertEqual(self.events(t2), ['attach'])
        self.assertFalse(self.errors().filtered(lambda e: e.res_id == r2.id))

    def make_errors(self, count=3):
        self.broken_definition()
        for _ in range(count):
            with self.assertLogs(LOGGER, 'ERROR'):
                self.make_partner('NEW')

    def test_err_021_retroactive_reevaluate(self):
        """TC-ERR-021: đánh giá lại hàng loạt với retroactive lấy start từ create_date."""
        d = self.broken_definition()
        with self.assertLogs(LOGGER, 'ERROR'):
            p = self.make_partner('NEW')
        self.env.cr.execute("UPDATE res_partner SET create_date=%s WHERE id=%s", (T0, p.id))
        p.invalidate_cache(None, ids=p.ids)
        d.write({'start_domain': "[('ref', 'in', ['NEW'])]", 'retroactive': True,
                 'start_field_id': self.env['ir.model.fields']._get('res.partner', 'create_date').id})
        with self.at(T0 + hours(1)):
            self.errors().filtered(lambda e: e.res_id == p.id).with_user(
                self.manager).action_reevaluate_batch()
        self.assertTrue(self.errors().filtered(lambda e: e.res_id == p.id).is_resolved)
        t = self.task_of(p, d)
        self.assertEqual((t.stage, t.start_time, t.planned_end_time), ('in_progress', T0, T0 + hours(4)))

    def test_err_022_023_unresolved_count(self):
        """TC-ERR-022/023: nhãn số = số event error chưa xử lý, giảm sau khi đánh dấu."""
        self.make_errors(3)
        domain = [('event', '=', 'error'), ('is_resolved', '=', False)]
        self.assertEqual(self.Event.with_user(self.manager).search_count(domain), 3)
        self.errors()[2].with_user(self.manager).action_mark_resolved()
        self.assertTrue(self.errors()[2].is_resolved)
        self.assertEqual(self.Event.with_user(self.manager).search_count(domain), 2)

    def test_err_024_non_group_hidden(self):
        """TC-ERR-024: người dùng ngoài nhóm SLA không đếm được và không thấy menu."""
        self.make_errors(1)
        with self.assertRaises(AccessError):
            self.Event.with_user(self.none_user).search_count(
                [('event', '=', 'error'), ('is_resolved', '=', False)])
        visible = self.env['ir.ui.menu'].with_user(self.none_user)._visible_menu_ids()
        for xmlid in ('menu_sla_root', 'menu_sla_event_error_unresolved'):
            self.assertNotIn(self.env.ref('dwo_sla_core.' + xmlid).id, visible)
        visible = self.env['ir.ui.menu'].with_user(self.manager)._visible_menu_ids()
        self.assertIn(self.env.ref('dwo_sla_core.menu_sla_event_error_unresolved').id, visible)
