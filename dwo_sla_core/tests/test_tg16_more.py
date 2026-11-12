# -*- coding: utf-8 -*-
"""TG-16 bổ sung: menu, quyền cron, đa công ty, view chỉ đọc (docs/060 TC-SEC-*).

Refs: REQ-SEC-001..006, REQ-FUNC-023, 026
"""
from lxml import etree

from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')
DENY = "env['res.users'].create({'name': 'x', 'login': 'x@sla.test'})"


@tagged(*TAGS, 'tg_16')
class TestSecurityMore(SlaCase):

    def setUp(self):
        super().setUp()
        self.manager = self.make_user('sla_mgr_sec2', 'manager')
        self.viewer = self.make_user('sla_usr_sec2', 'user')
        self.none_user = self.make_user('sla_none_sec2')

    def test_sec_admin_default_sla_manager(self):
        """Quản trị hệ thống mặc định có quyền SLA Manager (và SLA User qua implied)."""
        manager = self.env.ref('dwo_sla_core.group_sla_manager')
        self.assertIn(manager, self.env.ref('base.group_system').implied_ids)
        admin = self.env.ref('base.user_admin')
        self.assertTrue(admin.has_group('dwo_sla_core.group_sla_manager'))
        self.assertTrue(admin.has_group('dwo_sla_core.group_sla_user'))
        sysadmin = self.make_user('sla_sysadmin')
        sysadmin.group_ids += self.env.ref('base.group_system')
        self.assertTrue(sysadmin.has_group('dwo_sla_core.group_sla_manager'))
        visible = self.env['ir.ui.menu'].with_user(sysadmin)._visible_menu_ids()
        self.assertIn(self.env.ref('dwo_sla_core.menu_sla_root').id, visible)

    def test_sec_015_escalation_permission_note(self):
        """TC-SEC-015: tab Note của form định nghĩa ghi: action chạy theo quyền user xử lý nền, không phải người sửa record."""
        root = etree.fromstring(
            self.env['sla.definition'].with_user(self.manager).get_view(view_type='form')['arch'])
        pages = root.xpath("//page[@name='note']")
        self.assertEqual(len(pages), 1)
        text = ' '.join(''.join(pages[0].itertext()).split())
        self.assertIn('permissions of the user assigned to the SLA background job', text)
        self.assertIn('not the permissions of the user who edits the source record', text)

    def test_sec_001_menu_hidden(self):
        """TC-SEC-001: menu SLA ẩn với người dùng không thuộc nhóm SLA."""
        root = self.env.ref('dwo_sla_core.menu_sla_root')
        children = self.env['ir.ui.menu'].sudo().search([('id', 'child_of', root.id)])
        hidden = self.env['ir.ui.menu'].with_user(self.none_user)._visible_menu_ids()
        self.assertFalse(set(children.ids) & set(hidden))
        shown = self.env['ir.ui.menu'].with_user(self.viewer)._visible_menu_ids()
        self.assertIn(root.id, shown)

    def cron_case(self):
        self.no_commit_progress()
        cron = self.make_user('sla_cron_sec', 'user')
        d = self.make_definition()
        esc = self.make_escalation(d, 75, action=self.make_server_action(DENY))
        t = self.task_of(self.make_partner('NEW'), d)
        with self.assertLogs('odoo.addons.dwo_sla_core', 'ERROR'), self.at(T0 + hours(3)):
            self.Processor.with_user(cron).process_due()
        return t, esc

    def test_sec_013_denied_action_fails(self):
        """TC-SEC-013: action vượt quyền U-CRON -> escalate_failed, mốc coi là xong."""
        t, esc = self.cron_case()
        names = self.events(t)
        self.assertEqual((names.count('escalate_failed'), names.count('escalate')), (1, 0))
        self.assertTrue(t.event_ids.filtered(lambda e: e.event == 'escalate_failed').note)
        self.assertIn(esc, t.done_escalation_ids)

    def test_sec_021_recalculate_by_manager(self):
        """TC-SEC-021: SLA Manager Tính lại: target 8, planned_end_time 17:00 ICT."""
        cal = self.make_calendar()
        d = self.make_definition(schedule_source='definition', schedule_id=cal.id)
        t = self.task_of(self.make_partner('NEW'), d)
        self.assertEqual(t.planned_end_time, T0 + hours(4))
        d.duration = 8
        with self.at(T0):
            t.with_user(self.manager).action_recalculate()
        self.assertEqual((t.target_duration, t.business_duration, t.planned_end_time), (8, 0, T0 + hours(8)))

    def test_sec_023_readonly_views(self):
        """TC-SEC-023: view task/event không có tạo/sửa/xóa; manager chỉ có quyền đọc task."""
        for model, view_types in (('sla.task', ('list', 'form')), ('sla.event', ('list',))):
            for view_type in view_types:
                arch = self.env[model].with_user(self.manager).get_view(view_type=view_type)['arch']
                root = etree.fromstring(arch)
                self.assertIn(root.get('create'), ('0', 'false'), (model, view_type))
                self.assertIn(root.get('delete'), ('0', 'false'), (model, view_type))
                if model == 'sla.task':
                    self.assertIn(root.get('edit'), ('0', 'false'), (model, view_type))
        access = self.env['ir.access'].sudo().search([
            ('model_id.model', '=', 'sla.task'),
            ('group_id', '=', self.env.ref('dwo_sla_core.group_sla_manager').id)])
        self.assertEqual(access.mapped(lambda a: (a.for_create, a.for_write, a.for_unlink)),
                         [(False, False, False)])


@tagged(*TAGS, 'tg_16')
class TestSecurityLinkedRecord(SlaCase):

    def setUp(self):
        super().setUp()
        self.cal = self.make_calendar()
        self.co_a = self.env.company
        self.co_b = self.env['res.company'].create({
            'name': "CO-B Secret", 'resource_calendar_id': self.cal.id})
        self.biz = self.make_user('sla_biz_s', 'user', company_id=self.co_a.id,
                                  company_ids=[(6, 0, self.co_a.ids)])
        self.d = self.make_definition(
            schedule_source='record', schedule_path='parent_id.company_id.resource_calendar_id')
        parent = self.make_partner(False, name="PM-Secret", company_id=self.co_b.id)
        self.parent = parent
        self.child = self.make_partner('NEW', parent_id=parent.id, company_id=self.co_a.id)

    def test_sec_016_calendar_resolved_without_read_access(self):
        """TC-SEC-016: tính đúng lịch của công ty mẹ dù người dùng không đọc được record mẹ."""
        with self.assertRaises(AccessError):
            self.parent.with_user(self.biz).read(['name'])
        self.Task.sudo().search([('res_id', '=', self.child.id)]).unlink()
        self.Engine.with_user(self.biz).evaluate(self.child.with_user(self.biz), now=T0)
        t = self.task_of(self.child, self.d)
        self.assertEqual((t.schedule_id, t.start_time, t.planned_end_time), (self.cal, T0, T0 + hours(4)))
        note = t.event_ids.filtered(lambda e: e.event == 'attach').note or ''
        self.assertNotIn('fallback', note.lower())

    def test_sec_017_no_leak_of_linked_record(self):
        """TC-SEC-017: đọc task/event không lộ dữ liệu record liên kết khác công ty."""
        t = self.task_of(self.child, self.d)
        values = t.with_user(self.biz).read()[0]
        events = t.event_ids.with_user(self.biz).read(['note', 'res_model', 'res_id'])
        blob = repr(values) + repr(events)
        self.assertNotIn('PM-Secret', blob)
        self.assertNotIn('CO-B Secret', blob)
        with self.assertRaises(AccessError):
            self.parent.with_user(self.biz).read(['name'])
