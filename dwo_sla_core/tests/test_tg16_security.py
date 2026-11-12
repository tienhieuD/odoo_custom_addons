# -*- coding: utf-8 -*-
"""TG-16: phân quyền và đa công ty (docs/060 TC-SEC-*).

Refs: REQ-SEC-001..006
"""
from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')


@tagged(*TAGS, 'tg_16')
class TestSecurity(SlaCase):

    def setUp(self):
        super().setUp()
        self.d = self.make_definition()
        self.viewer = self.make_user('sla_usr_sec', 'user')
        self.manager = self.make_user('sla_mgr_sec', 'manager')
        self.plain = self.make_user('sla_plain_sec')

    def test_sec_002_003_definition_write(self):
        """TC-SEC-002/003: viewer không sửa được định nghĩa, manager sửa được."""
        with self.assertRaises(AccessError):
            self.d.with_user(self.viewer).write({'name': "x"})
        self.d.with_user(self.manager).write({'name': "Renamed"})
        self.assertEqual(self.d.name, "Renamed")

    def test_sec_004_viewer_reads(self):
        """TC-SEC-004: viewer đọc được định nghĩa và task."""
        p = self.make_partner('NEW')
        self.assertEqual(self.Definition.with_user(self.viewer).search([('id', '=', self.d.id)]), self.d)
        self.assertEqual(self.Task.with_user(self.viewer).search([('res_id', '=', p.id)]),
                         self.task_of(p, self.d))

    def test_sec_005_007_plain_user_denied(self):
        """TC-SEC-005/007: người dùng ngoài nhóm SLA không đọc được mọi model SLA."""
        self.make_partner('NEW')
        for model in ('sla.definition', 'sla.escalation', 'sla.task', 'sla.event'):
            with self.assertRaises(AccessError, msg=model):
                self.env[model].with_user(self.plain).search([])

    def test_sec_006_task_created_with_record_rights_only(self):
        """TC-SEC-006: người dùng chỉ có quyền ghi record gốc vẫn kích hoạt tạo task."""
        editor = self.make_user('sla_editor_sec')
        editor.groups_id += self.env.ref('base.group_partner_manager')
        with self.at(T0):
            p = self.Partner.with_user(editor).create({'name': "By editor", 'ref': 'NEW'})
        self.assertEqual(len(self.tasks(p, self.d)), 1)

    def test_sec_018_manager_cannot_write_tasks(self):
        """TC-SEC-018: manager không tạo/sửa/xóa task trực tiếp."""
        t = self.task_of(self.make_partner('NEW'), self.d)
        Task = self.Task.with_user(self.manager)
        with self.assertRaises(AccessError):
            Task.create({'sla_id': self.d.id, 'res_model': 'res.partner',
                         'res_id': 1, 'start_time': T0})
        with self.assertRaises(AccessError):
            t.with_user(self.manager).write({'stage': 'cancelled'})
        with self.assertRaises(AccessError):
            t.with_user(self.manager).unlink()

    def test_sec_019_020_event_rights(self):
        """TC-SEC-019/020: manager không tạo/xóa/sửa event, nhưng đánh dấu đã xử lý được."""
        self.Event._log_error(definition=self.d, res_model='res.partner', res_id=1, message="m")
        event = self.Event.sudo().search([('event', '=', 'error')], limit=1)
        Event = self.Event.with_user(self.manager)
        with self.assertRaises(AccessError):
            Event.create({'event': 'error', 'event_dt': T0})
        with self.assertRaises(AccessError):
            event.with_user(self.manager).write({'note': "changed"})
        with self.assertRaises(AccessError):
            event.with_user(self.manager).unlink()
        event.with_user(self.manager).action_mark_resolved()
        self.assertTrue(event.is_resolved)

    def test_sec_022_viewer_cannot_mark_resolved(self):
        """TC-SEC-022: group_sla_user không đánh dấu event đã xử lý."""
        self.Event._log_error(definition=self.d, res_model='res.partner', res_id=1, message="m")
        event = self.Event.sudo().search([('event', '=', 'error')], limit=1)
        with self.assertRaises(AccessError):
            event.with_user(self.viewer).action_mark_resolved()
        self.assertFalse(event.is_resolved)

    def test_sec_024_viewer_cannot_create_escalation(self):
        """TC-SEC-024: viewer không tạo được mốc escalation."""
        action = self.make_server_action("pass")
        with self.assertRaises(AccessError):
            self.Escalation.with_user(self.viewer).create({
                'definition_id': self.d.id, 'percent': 50, 'action_id': action.id})
        self.assertFalse(self.d.escalation_ids)


@tagged(*TAGS, 'tg_16')
class TestMultiCompany(SlaCase):

    def setUp(self):
        super().setUp()
        self.company_a = self.env.user.company_id
        self.company_b = self.env['res.company'].create({'name': "SLA Company B"})
        self.user_a = self.make_user('sla_usr_a', 'user', company_id=self.company_a.id,
                                     company_ids=[(6, 0, self.company_a.ids)])

    def test_sec_008_009_hidden_other_company(self):
        """TC-SEC-008/009: user thuộc công ty A không thấy task/event của công ty B."""
        d = self.make_definition()
        pa = self.make_partner('NEW', company_id=self.company_a.id)
        pb = self.make_partner('NEW', company_id=self.company_b.id)
        tasks = self.Task.with_user(self.user_a).search([('sla_id', '=', d.id)])
        self.assertEqual(tasks, self.task_of(pa, d))
        self.assertTrue(self.task_of(pb, d))
        events = self.Event.with_user(self.user_a).search([('task_id.sla_id', '=', d.id)])
        self.assertEqual(events.task_id, tasks)

    def test_sec_010_definition_visibility(self):
        """TC-SEC-010: định nghĩa gán công ty B không hiện với user công ty A."""
        db = self.make_definition(name="B only", company_id=self.company_b.id)
        dn = self.make_definition(name="All companies")
        visible = self.Definition.with_user(self.user_a).search([])
        self.assertNotIn(db, visible)
        self.assertIn(dn, visible)

    def test_sec_011_012_definition_company_scope(self):
        """TC-SEC-011/012: định nghĩa gán công ty chỉ gắn task cho record cùng công ty."""
        da = self.make_definition(name="A only", company_id=self.company_a.id)
        dn = self.make_definition(name="Global")
        pb = self.make_partner('NEW', company_id=self.company_b.id)
        self.assertFalse(self.tasks(pb, da))
        self.assertEqual(len(self.tasks(pb, dn)), 1)
