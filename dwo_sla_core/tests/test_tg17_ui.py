# -*- coding: utf-8 -*-
"""TG-17: giao diện và báo cáo (docs/060 TC-UIX-*), kiểm ở mức view/arch/domain/read_group.

Không thể kiểm bằng TransactionCase (xem TASKS.md): UIX-003, 006, 007, 008, 012, 017, 028, 030
(trình diễn trên trình duyệt); UIX-029..031 (cần model kế thừa `sla.mixin`, `demo.ticket` không có
trong DB test). Các bộ lọc lấy domain từ search view thật.
Refs: REQ-INT-001..004, 006, 011..014, 020..023, REQ-FUNC-036, 042, 062, REQ-SEC-001
"""
from lxml import etree

from odoo.exceptions import AccessError
from odoo.tests import Form, tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')
TASK_LIST_FIELDS = ('res_id', 'sla_id', 'stage', 'start_time', 'planned_end_time', 'end_time',
                    'business_duration', 'target_duration', 'has_breached')


class UiCase(SlaCase):

    def setUp(self):
        super().setUp()
        self.manager = self.make_user('sla_mgr_ui', 'manager')
        self.viewer = self.make_user('sla_usr_ui', 'user')
        self.none_user = self.make_user('sla_none_ui')

    def arch(self, model, view_type, user=None):
        env = self.env[model].with_user(user or self.manager)
        return etree.fromstring(env.get_view(view_type=view_type)['arch'])

    def filter_domain(self, model, name):
        root = self.arch(model, 'search')
        node = root.xpath("//filter[@name='%s']" % name)[0]
        return eval(node.get('domain'))  # noqa: S307 -- domain literal của view module

    def raw_task(self, definition, stage='in_progress', partner=None, planned_end_time=None,
                 has_breached=False, end_time=None, **extra):
        partner = partner or self.Partner.create({'name': "UI P"})
        vals = {
            'sla_id': definition.id, 'res_model': 'res.partner', 'res_id': partner.id,
            'stage': stage, 'start_time': T0, 'target_duration': 4,
            'planned_end_time': planned_end_time or T0 + hours(4), 'has_breached': has_breached}
        if stage == 'in_progress':
            vals['running_since'] = T0
        elif stage == 'paused':
            vals['pause_time'] = T0
        else:
            vals['end_time'] = end_time or T0 + hours(1)
        vals.update(extra)
        return self.Task.sudo().create(vals)


@tagged(*TAGS, 'tg_17')
class TestDefinitionForm(UiCase):

    def test_uix_001_save_via_form(self):
        """TC-UIX-001: lưu định nghĩa qua Form và đọc lại."""
        form = Form(self.Definition.with_user(self.manager))
        form.name = "UI-DEF-1"
        form.model_id = self.partner_model
        form.start_domain = "[('is_company', '=', True)]"
        form.duration = 4
        record = form.save()
        record.invalidate_recordset()
        self.assertEqual((record.model_name, record.start_domain, record.duration),
                         ('res.partner', "[('is_company', '=', True)]", 4.0))

    def test_uix_002_viewer_readonly(self):
        """TC-UIX-002: group_sla_user không sửa được định nghĩa."""
        d = self.make_definition()
        as_viewer = d.with_user(self.viewer)
        self.assertFalse(as_viewer.has_access('write'))
        self.assertFalse(self.Definition.with_user(self.viewer).has_access('create'))
        with self.assertRaises(Exception):  # noqa: B017 -- readonly hoặc AccessError
            with Form(as_viewer) as form:
                form.name = "changed"

    def test_uix_004_005_help_warnings(self):
        """TC-UIX-004/005 + CMP-009: help của start/pause nêu cảnh báo; cancel/resume thì không; cả 6 nêu giới hạn."""
        info = self.Definition.with_user(self.manager).fields_get(
            [name + '_domain' for name in ('start', 'cancel', 'pause', 'resume', 'stop', 'reset')],
            attributes=['help'])
        for name in ('start', 'pause'):
            text = info[name + '_domain']['help'].lower()
            self.assertIn('subset', text, name)
            self.assertIn('mutually exclusive', text, name)
        for name in ('cancel', 'resume'):
            text = info[name + '_domain']['help'].lower()
            self.assertNotIn('subset', text, name)
            self.assertNotIn('mutually exclusive', text, name)
        for name, values in info.items():
            text = values['help'].lower()
            self.assertIn('non-stored computed', text, name)
            self.assertIn('re-evaluate', text, name)

    def test_uix_009_calendar_fallback_note_in_arch(self):
        """TC-UIX-009: ghi chú lịch dự phòng chỉ hiện khi schedule_source = record."""
        root = self.arch('sla.definition', 'form')
        notes = root.xpath("//div[contains(@class, 'alert-warning')][@invisible]")
        notes = [n for n in notes if 'schedule_source' in n.get('invisible')]
        self.assertEqual(len(notes), 1)
        self.assertIn("!= 'record'", notes[0].get('invisible'))
        text = ' '.join(''.join(notes[0].itertext()).split()).lower()
        self.assertIn('default working calendar', text)
        self.assertIn('24x7', text)


@tagged(*TAGS, 'tg_17')
class TestTaskViews(UiCase):

    def setUp(self):
        super().setUp()
        self.d = self.make_definition()

    def test_uix_010_list_fields(self):
        """TC-UIX-010: danh sách task có đủ 9 field; search_read đúng giá trị."""
        root = self.arch('sla.task', 'list', self.viewer)
        names = {node.get('name') for node in root.iter('field')}
        self.assertLessEqual(set(TASK_LIST_FIELDS), names)
        t = self.task_of(self.make_partner('NEW'), self.d)
        rows = self.Task.with_user(self.viewer).search_read([('id', '=', t.id)], list(TASK_LIST_FIELDS))
        self.assertEqual((rows[0]['stage'], rows[0]['target_duration'], rows[0]['planned_end_time'],
                          rows[0]['business_duration'], rows[0]['has_breached'], rows[0]['sla_id'][0]),
                         ('in_progress', 4.0, T0 + hours(4), 0.0, False, self.d.id))

    def test_uix_011_form_readonly(self):
        """TC-UIX-011: form task không có edit/create/delete và không có nút Xóa/Lưu."""
        root = self.arch('sla.task', 'form')
        self.assertEqual([root.get(a) for a in ('edit', 'create', 'delete')], ['0', '0', '0'])
        labels = ' '.join(b.get('string', '') for b in root.iter('button')).lower()
        self.assertNotIn('delete', labels)
        self.assertNotIn('save', labels)
        task = self.Task.with_user(self.manager)
        self.assertEqual([task.has_access(m) for m in ('write', 'create', 'unlink')], [False] * 3)

    def test_uix_013_to_016_action_binding(self):
        """TC-UIX-013..016: action SLA gắn theo model, giữ khi còn task, gỡ khi hết, ẩn với người ngoài nhóm."""
        def names(user):
            return [a['name'] for a in self.env['ir.actions.actions'].with_user(user).get_bindings(
                'res.partner').get('action', [])]

        p = self.make_partner('NEW')
        self.assertIn('SLA', names(self.viewer))
        self.assertNotIn('SLA', names(self.none_user))
        action = self.env['ir.actions.act_window'].sudo().search([
            ('binding_model_id.model', '=', 'res.partner'), ('name', '=', 'SLA')])
        self.assertEqual(len(action), 1)
        domain = eval(action.domain, {'active_id': p.id})  # noqa: S307
        self.assertEqual(self.Task.sudo().search(domain), self.task_of(p, self.d))
        self.d.active = False  # còn task in_progress -> giữ action
        self.assertIn('SLA', names(self.viewer))
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        self.d.active = True
        self.d.active = False  # hết task hoạt động -> gỡ action
        self.assertNotIn('SLA', names(self.viewer))
        self.d.active = True
        self.assertIn('SLA', names(self.viewer))


@tagged(*TAGS, 'tg_17')
class TestTaskFilters(UiCase):

    def setUp(self):
        super().setUp()
        self.d = self.make_definition()
        self.d2 = self.make_definition(name="D2", start_domain="[('ref', '=', 'ZZ')]")

    def count(self, filter_name, user=None):
        domain = self.filter_domain('sla.task', filter_name)
        return self.Task.with_user(user or self.viewer).search_count(domain)

    def test_uix_018_019_status_filters(self):
        """TC-UIX-019: bộ lọc rỗng không lỗi; TC-UIX-018: đếm đúng 2, 1, 2."""
        self.assertEqual([self.count(n) for n in ('in_progress', 'paused', 'breached')], [0, 0, 0])
        self.raw_task(self.d)
        self.raw_task(self.d)
        self.raw_task(self.d, 'paused')
        self.raw_task(self.d, has_breached=True)             # C: đang chạy, đã vi phạm
        self.raw_task(self.d, 'breached', has_breached=True)  # D
        self.assertEqual(self.count('in_progress'), 3)
        self.assertEqual((self.count('paused'), self.count('breached')), (1, 2))

    def due_soon_tasks(self, now, offsets):
        return [self.raw_task(self.d, planned_end_time=now + hours(offset)) for offset in offsets]

    def test_uix_020_to_024_due_soon(self):
        """TC-UIX-020..024: Sắp đến hạn theo X, biên, loại trừ, đổi X, mặc định 4."""
        now = T0 + hours(1)
        self.env['ir.config_parameter'].sudo().set_param('dwo_sla_core.due_soon_hours', '6')
        near, edge, over = self.due_soon_tasks(now, (2, 6, 6 + 1 / 3600.0))
        with self.at(now):
            result = self.Task.with_user(self.viewer).search(self.filter_domain('sla.task', 'due_soon'))
            self.assertEqual(result & (near | edge | over), near | edge)
            self.raw_task(self.d, 'paused', planned_end_time=now + hours(1))
            self.raw_task(self.d, 'achieved', planned_end_time=now + hours(1))
            self.raw_task(self.d, has_breached=True, planned_end_time=now + hours(1))
            self.assertEqual(self.count('due_soon'), 2)
            self.env['ir.config_parameter'].sudo().set_param('dwo_sla_core.due_soon_hours', '1')
            self.assertEqual(self.count('due_soon'), 0)  # X = 1: không còn task nào trong 1 giờ
            self.env['ir.config_parameter'].sudo().search([('key', '=', 'dwo_sla_core.due_soon_hours')]).unlink()
            default = self.env['res.config.settings'].default_get(['sla_due_soon_hours'])
            self.assertEqual(default['sla_due_soon_hours'], 4)

    def test_uix_023_025_setting_roles(self):
        """TC-UIX-023/025: đổi X qua Settings (quản trị) lưu được; SLA User bị từ chối."""
        admin = self.make_user('sla_admin_ui')
        admin.group_ids += self.env.ref('base.group_system')
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('dwo_sla_core.due_soon_hours', '4')
        with self.assertRaises(AccessError):
            self.env['res.config.settings'].with_user(self.viewer).create({'sla_due_soon_hours': 1}).execute()
        self.assertEqual(param.get_param('dwo_sla_core.due_soon_hours'), '4')
        self.env['res.config.settings'].with_user(admin).create({'sla_due_soon_hours': 1}).execute()
        self.assertEqual(param.get_param('dwo_sla_core.due_soon_hours'), '1')

    def test_uix_026_027_grouping(self):
        """TC-UIX-026/027: nhóm theo định nghĩa, model, stage."""
        for _ in range(3):
            self.raw_task(self.d)
        self.raw_task(self.d2)
        self.raw_task(self.d2, 'paused')
        Task = self.Task.with_user(self.viewer)
        by_def = dict(Task._read_group([], ['sla_id'], ['__count']))
        self.assertEqual((by_def[self.d], by_def[self.d2]), (3, 2))
        self.assertEqual(dict(Task._read_group([], ['stage'], ['__count'])),
                         {'in_progress': 4, 'paused': 1})
        self.assertEqual(dict(Task._read_group([], ['res_model'], ['__count'])), {'res.partner': 5})


@tagged(*TAGS, 'tg_17')
class TestReevaluateAndEvents(UiCase):

    def test_uix_032_033_034_reevaluate_action(self):
        """TC-UIX-032/033/034: Đánh giá lại kết thúc task theo điều kiện qua quan hệ; viewer bị từ chối; task đã kết thúc không đổi."""
        d = self.make_definition(stop_domain="[('parent_id.ref', '=', 'DONE')]")
        parent = self.make_partner(False)
        child = self.make_partner('NEW', parent_id=parent.id)
        task = self.task_of(child, d)
        self.write(parent, {'ref': 'DONE'}, T0 + hours(1))
        self.assertEqual(task.stage, 'in_progress')  # điều kiện qua quan hệ không tự đánh giá
        with self.at(T0 + hours(2)):
            task.with_user(self.manager).action_reevaluate()
        self.assertEqual((task.stage, task.end_time, task.business_duration), ('achieved', T0 + hours(2), 2.0))
        self.assertEqual(self.events(task).count('complete'), 1)
        snapshot = (task.stage, task.end_time, task.business_duration, len(task.event_ids))
        with self.at(T0 + hours(5)):
            task.with_user(self.manager).action_reevaluate()
        self.assertEqual((task.stage, task.end_time, task.business_duration, len(task.event_ids)), snapshot)
        with self.assertRaises(AccessError):
            task.with_user(self.viewer).action_reevaluate()
        names = lambda user: [b.get('name') for b in self.arch('sla.task', 'form', user).iter('button')]  # noqa: E731
        self.assertNotIn('action_reevaluate', names(self.viewer))
        self.assertIn('action_reevaluate', names(self.manager))

    def test_uix_035_to_038_event_filters_grouping(self):
        """TC-UIX-035..038: lọc event theo loại/trạng thái, nhóm, danh sách chỉ đọc."""
        d1, d2 = self.make_definition(), self.make_definition(name="D2", start_domain="[('ref', '=', 'ZZ')]")
        task = self.task_of(self.make_partner('NEW'), d1)       # 1 event attach (d1)
        self.Event._log_error(definition=d1, res_model='res.partner', res_id=1, message="e1")
        self.Event._log_error(definition=d2, res_model='res.partner', res_id=2, message="e2")
        self.Event.sudo().search([('note', '=', 'e2')]).write({'is_resolved': True})
        self.Event.sudo().create({'event': 'escalate', 'event_dt': T0, 'task_id': task.id,
                                  'definition_id': d2.id})
        Event = self.Event.with_user(self.manager)
        count = lambda name: Event.search_count(self.filter_domain('sla.event', name))  # noqa: E731
        self.assertEqual((count('error'), count('error_unresolved'), count('escalate')), (2, 1, 1))
        by_def = dict(Event._read_group([], ['definition_id'], ['__count']))
        self.assertEqual((by_def[d1], by_def[d2]), (2, 2))
        by_type = dict(Event._read_group([], ['event'], ['__count']))
        self.assertEqual((by_type['error'], by_type['attach'], by_type['escalate']), (2, 1, 1))
        root = self.arch('sla.event', 'list')
        self.assertEqual([root.get('create'), root.get('delete')], ['0', '0'])
        self.assertEqual([Event.has_access('create'), Event.has_access('unlink')], [False, False])


@tagged(*TAGS, 'tg_17')
class TestReportMeasures(UiCase):

    def setUp(self):
        super().setUp()
        self.d1 = self.make_definition()
        self.d2 = self.make_definition(name="D2", start_domain="[('ref', '=', 'ZZ')]")
        self.Task = self.Task.with_user(self.viewer).with_context(tz='Asia/Ho_Chi_Minh')

    def rate_groups(self, extra_group='end_time:month'):
        rows = self.Task._read_group(
            [('stage', 'in', ('achieved', 'breached', 'cancelled'))],
            ['sla_id', extra_group], ['achieved_rate:avg', '__count'])
        return {(d.id, month.strftime('%Y-%m') if month else None): (rate, count)
                for d, month, rate, count in rows}

    def test_uix_039_achieved_rate_excludes_cancelled(self):
        """TC-UIX-039: tỷ lệ đạt = 80% (8/10), task cancelled không tính."""
        end = T0 + hours(1)
        for _ in range(8):
            self.raw_task(self.d1, 'achieved', end_time=end)
        for _ in range(2):
            self.raw_task(self.d1, 'breached', has_breached=True, end_time=end)
        for _ in range(5):
            self.raw_task(self.d1, 'cancelled', end_time=end)
        rate, count = self.rate_groups()[(self.d1.id, '2026-03')]
        self.assertAlmostEqual(rate, 0.8)
        self.assertEqual(count, 15)

    def test_uix_040_no_ended_tasks_is_undefined(self):
        """TC-UIX-040: kỳ không có task kết thúc -> giá trị rỗng, không ZeroDivisionError."""
        self.raw_task(self.d1, 'cancelled')
        self.raw_task(self.d1)
        rows = self.Task._read_group([('sla_id', '=', self.d1.id)], ['sla_id'],
                                     ['achieved_rate:avg'])
        self.assertFalse(rows[0][1])

    def test_uix_041_month_boundary_timezone(self):
        """TC-UIX-041: kết thúc 30/9 23:30 và 1/10 00:30 giờ VN rơi vào hai tháng khác nhau."""
        sep = self.raw_task(self.d1, 'achieved', end_time=datetime_utc(2026, 9, 30, 16, 30))
        octo = self.raw_task(self.d1, 'achieved', end_time=datetime_utc(2026, 9, 30, 17, 30))
        groups = self.rate_groups()
        self.assertEqual((groups[(self.d1.id, '2026-09')], groups[(self.d1.id, '2026-10')]),
                         ((1.0, 1), (1.0, 1)))
        self.assertTrue(sep and octo)

    def breaching(self):
        rows = self.Task._read_group([], ['sla_id'], ['breaching_count:sum'])
        return {d.id: value for d, value in rows}

    def test_uix_042_043_044_breaching_counts(self):
        """TC-UIX-042..044: số đang vi phạm theo định nghĩa; loại task đã breached; 0 khi không có."""
        self.raw_task(self.d1)
        self.assertEqual(self.breaching().get(self.d1.id, 0), 0)
        self.assertEqual(self.Task.search_count(self.filter_domain('sla.task', 'breached')), 0)
        for _ in range(2):
            self.raw_task(self.d1, has_breached=True)
        self.raw_task(self.d1, 'paused', has_breached=True)
        self.raw_task(self.d1, 'breached', has_breached=True)
        self.raw_task(self.d1, 'achieved')
        self.raw_task(self.d2, has_breached=True)
        self.assertEqual(self.breaching(), {self.d1.id: 3, self.d2.id: 1})
        self.assertEqual(self.Task.search_count(
            self.filter_domain('sla.task', 'breached') + [('sla_id', '=', self.d1.id)]), 4)


def datetime_utc(year, month, day, hour, minute):
    from datetime import datetime
    return datetime(year, month, day, hour, minute)
