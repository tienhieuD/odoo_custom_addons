# -*- coding: utf-8 -*-
"""TG-34: màn hình báo cáo R2-R10 (task 006 C2): action mở được cho SLA User và
Manager, group-by của view đúng, bộ lọc của search view, số liệu mẫu, bản ghi rỗng,
menu Reporting, ja_JP, tour."""
import os
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo import fields
from odoo.modules.module import get_module_path
from odoo.tests import new_test_user, tagged
from odoo.tools.safe_eval import safe_eval

from .common import SlaCase, SlaHttpCase

TAGS = ('post_install', '-at_install', 'dwo_sla_core', 'tg_34')
MODULE = 'dwo_sla_core'
KEYS = ('trend', 'distribution', 'status', 'backlog', 'performance', 'source',
        'pause', 'escalation', 'heatmap', 'calendar')


def _fgroup(model, domain, groupby, aggregates):
    """Cách `formatted_read_group` của Odoo 19/20 (list dict, khoá = đặc tả nhóm / aggregate) trên `_read_group`
    của Odoo 17/18, vì hai bản này chưa có `formatted_read_group`."""
    rows = []
    for row in model._read_group(domain, list(groupby), list(aggregates)):
        keys = list(groupby) + list(aggregates)
        item = {}
        for key, value in zip(keys, row):
            if key in groupby and hasattr(value, '_name'):
                value = (value.id, value.display_name) if value else False
            item[key] = value
        rows.append(item)
    return rows


def _action(env, key):
    return env.ref('%s.action_sla_report_%s' % (MODULE, key))


def _view_specs(env, action):
    """(view_type, arch) của từng view do action khai báo (kèm view mặc định)."""
    model = env[action.res_model]
    views = model.get_views([(False, vt) for vt in action.view_mode.split(',')])
    return views


def _groupby_and_aggregates(model, view_type, arch):
    """Suy ra groupby/aggregates mà client sẽ gọi cho graph/pivot từ arch."""
    root = etree.fromstring(arch)
    groupby, aggregates = [], []
    for node in root.iter('field'):
        name = node.get('name')
        if node.get('type') == 'measure':
            field = model._fields[name]
            aggregates.append('%s:%s' % (name, getattr(field, 'aggregator', None) or field.group_operator or 'sum'))
        elif view_type == 'graph' or node.get('type') in ('row', 'col'):
            groupby.append('%s:%s' % (name, node.get('interval')) if node.get('interval') else name)
    return groupby, aggregates + ['__count']


@tagged(*TAGS)
class TestReportingViews(SlaCase):

    def setUp(self):
        super().setUp()
        self.user = self.make_user('rep_user', 'user')
        self.manager = self.make_user('rep_mgr', 'manager')
        self.d_resp = self.make_definition(name="REP response SLA", type='sla', target='response')
        self.d_reso = self.make_definition(name="REP resolution OLA", type='ola', target='resolution')
        today = fields.Date.context_today(self.env['sla.task'])
        self.monday = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())
        now = fields.Datetime.now()
        self.now = now
        mk = self._raw
        # on_time: đã xong trong 1 giờ / 4 giờ, bắt đầu 10 ngày trước
        mon = self.monday
        self.t_ontime = mk(self.d_resp, 'achieved', start=mon - timedelta(days=10), end=mon - timedelta(days=9),
                           business=1.0)
        # late: trễ 2 giờ, bắt đầu tuần này
        self.t_late = mk(self.d_resp, 'breached', start=self.monday + timedelta(hours=10),
                         end=self.monday + timedelta(hours=18), business=6.0, breached=True)
        # breached_open: đang chạy, đã quá hạn, hạn hôm qua
        self.t_bopen = mk(self.d_resp, 'in_progress', start=mon - timedelta(days=3), planned=mon - timedelta(days=1),
                          business=5.0, breached=True)
        # running: hạn Thứ Tư tuần này
        self.t_running = mk(self.d_reso, 'in_progress', start=self.monday + timedelta(hours=9),
                            planned=self.monday + timedelta(days=2, hours=12))
        # paused: hạn tuần trước (ngoài tuần này), model nguồn khác
        self.t_paused = mk(self.d_reso, 'paused', start=mon - timedelta(days=40),
                           planned=self.monday - timedelta(days=3, hours=-12), res_model='res.users')
        self.t_cancel = mk(self.d_reso, 'cancelled', start=mon - timedelta(days=2), end=mon - timedelta(days=1))
        self.all = (self.t_ontime | self.t_late | self.t_bopen | self.t_running | self.t_paused | self.t_cancel)

    def _raw(self, definition, stage, start, end=None, planned=None, business=0.0, breached=False,
             res_model='res.partner'):
        vals = {
            'sla_id': definition.id, 'res_model': res_model, 'res_id': self.make_partner().id,
            'stage': stage, 'start_time': start, 'target_duration': 4.0,
            'planned_end_time': planned or start + timedelta(hours=4),
            'business_duration': business, 'has_breached': breached}
        if stage in ('achieved', 'breached', 'cancelled'):
            vals['end_time'] = end
        elif stage == 'paused':
            vals['pause_time'] = start + timedelta(hours=1)
        else:
            vals['running_since'] = start
        return self.Task.sudo().create(vals)

    # ------------------------------------------------------------------
    # Action mở được (SLA User và Manager)
    # ------------------------------------------------------------------

    def test_actions_open_and_group_by(self):
        """Mọi action: get_views không lỗi, formatted_read_group đúng groupby/measure của view."""
        for who in (self.user, self.manager):
            env = self.env(user=who)
            for key in KEYS:
                action = _action(env, key)
                self.assertTrue(env['ir.actions.actions']._for_xml_id('%s.action_sla_report_%s' % (MODULE, key)), key)
                model = env[action.res_model]
                domain = safe_eval(action.domain or '[]')
                views = _view_specs(env, action)['views']
                self.assertTrue(views, key)
                for vt in action.view_mode.split(','):
                    self.assertIn(vt, views, '%s: no %s view' % (key, vt))
                for view_type in action.view_mode.split(','):
                    if view_type not in ('graph', 'pivot'):
                        continue
                    arch = views[view_type]['arch']
                    groupby, aggregates = _groupby_and_aggregates(model, view_type, arch)
                    self.assertTrue(groupby, '%s/%s has no groupby' % (key, view_type))
                    rows = _fgroup(model, domain, groupby, aggregates)
                    if key != 'escalation':
                        self.assertTrue(rows, '%s/%s empty with sample data' % (key, view_type))
                    # bản ghi rỗng
                    self.assertEqual(
                        _fgroup(model, domain + [('id', '=', 0)], groupby, aggregates), [],
                        '%s/%s on empty set' % (key, view_type))

    def test_action_identity(self):
        """Tên rõ ràng, res_model đúng, mỗi action có search view và view riêng."""
        names = {
            'trend': 'Compliance Trend', 'distribution': 'Response Time Distribution',
            'status': 'Status Mix', 'backlog': 'Open Backlog & Ageing',
            'performance': 'Performance by Definition and Source', 'source': 'Performance by Source',
            'pause': 'Pause Analysis', 'escalation': 'Escalation Activity',
            'heatmap': 'Source Heatmap', 'calendar': 'Calendar Impact'}
        for key, name in names.items():
            action = _action(self.env, key)
            self.assertEqual(action.name, name)
            self.assertEqual(action.res_model, 'sla.event' if key == 'escalation' else 'sla.task')
            self.assertTrue(action.search_view_id)
            self.assertTrue(action.view_ids, key)

    def test_source_name_only_for_manager(self):
        """List của backlog: source_name có cho Manager, không có cho SLA User."""
        view = self.env.ref('%s.view_sla_report_backlog_list' % MODULE)
        arch_m = self.env(user=self.manager)['sla.task'].get_view(view.id, 'tree')['arch']
        arch_u = self.env(user=self.user)['sla.task'].get_view(view.id, 'tree')['arch']
        self.assertIn('name="source_name"', arch_m)
        self.assertNotIn('name="source_name"', arch_u)
        # và cả hai đọc được danh sách
        domain = [('stage', 'in', ('in_progress', 'paused')), ('id', 'in', self.all.ids)]
        self.assertEqual(len(self.env(user=self.user)['sla.task'].search(domain)), 3)
        self.assertEqual(len(self.env(user=self.manager)['sla.task'].search(domain)), 3)

    def test_menus_visible_to_sla_user(self):
        visible = self.env['ir.ui.menu'].with_user(self.user)._visible_menu_ids()
        outsider = new_test_user(self.env, login='rep_outsider', groups='base.group_user')
        hidden = self.env['ir.ui.menu'].with_user(outsider)._visible_menu_ids()
        reporting = self.env.ref('%s.menu_sla_reporting' % MODULE)
        self.assertEqual(reporting.parent_id, self.env.ref('%s.menu_sla_root' % MODULE))
        self.assertEqual(len(reporting.child_id), len(KEYS))
        self.assertIn(reporting.id, visible)
        for child in reporting.child_id:
            self.assertIn(child.id, visible)
            self.assertTrue(child.action)
            self.assertNotIn(child.id, hidden)

    # ------------------------------------------------------------------
    # Số liệu mẫu
    # ------------------------------------------------------------------

    def _count(self, groupby, extra=None, aggregates=('__count',)):
        domain = [('id', 'in', self.all.ids)] + (extra or [])
        rows = _fgroup(self.env(user=self.user)['sla.task'], domain, [groupby], list(aggregates))
        return rows

    def test_status_mix_counts_by_outcome(self):
        """R4: đếm theo outcome."""
        got = {r['outcome']: r['__count'] for r in self._count('outcome')}
        self.assertEqual(got, {'on_time': 1, 'late': 1, 'breached_open': 1, 'running': 1, 'paused': 1,
                               'cancelled': 1})

    def test_distribution_by_bucket(self):
        """R3: action chỉ lấy task đã kết thúc; bộ lọc Response mặc định giữ d_resp."""
        action = _action(self.env, 'distribution')
        self.assertIn("search_default_response", action.context)
        domain = safe_eval(action.domain) + [('id', 'in', self.all.ids), ('sla_target', '=', 'response')]
        rows = _fgroup(self.env['sla.task'], domain, ['sla_id', 'usage_bucket'], ['__count'])
        got = {(r['sla_id'][1], r['usage_bucket']): r['__count'] for r in rows}
        self.assertEqual(got, {("REP response SLA", '0_50'): 1, ("REP response SLA", '100_150'): 1})

    def test_performance_by_definition_and_source(self):
        """R6: outcome on_time/late/breached_open theo định nghĩa."""
        action = _action(self.env, 'performance')
        domain = safe_eval(action.domain) + [('id', 'in', self.all.ids)]
        rows = _fgroup(self.env['sla.task'], domain, ['sla_id', 'outcome'], ['__count'])
        got = {(r['sla_id'][1], r['outcome']): r['__count'] for r in rows}
        self.assertEqual(got, {("REP response SLA", 'on_time'): 1, ("REP response SLA", 'late'): 1,
                               ("REP response SLA", 'breached_open'): 1})
        rows = _fgroup(self.env['sla.task'], 
            domain, ['res_model', 'outcome'], ['overdue_duration:avg'])
        self.assertEqual({r['res_model'] for r in rows}, {'res.partner'})

    def test_compliance_trend_weekly(self):
        """R2: % đạt trung bình theo tuần của end_time (1 task đúng hạn, 1 trễ)."""
        action = _action(self.env, 'trend')
        domain = safe_eval(action.domain) + [('id', 'in', self.all.ids)]
        rows = _fgroup(self.env['sla.task'], domain, ['end_time:week'], ['achieved_rate:avg', '__count'])
        self.assertTrue(rows)
        rates = sorted(r['achieved_rate:avg'] for r in rows)
        self.assertEqual(sum(r['__count'] for r in rows), 2)
        self.assertTrue(all(0.0 <= r <= 1.0 for r in rates))
        total = _fgroup(self.env['sla.task'], domain, [], ['achieved_rate:avg'])
        self.assertAlmostEqual(total[0]['achieved_rate:avg'], 0.5)

    def test_backlog_open_tasks_and_deadline_group(self):
        """R5: chỉ task đang mở; nhóm theo tuần của planned_end_time."""
        action = _action(self.env, 'backlog')
        domain = safe_eval(action.domain) + [('id', 'in', self.all.ids)]
        rows = _fgroup(self.env['sla.task'], 
            domain, ['sla_id', 'res_model', 'planned_end_time:week'], ['__count'])
        self.assertEqual(sum(r['__count'] for r in rows), 3)
        listed = self.env['sla.task'].search(domain, order='planned_end_time asc')
        self.assertEqual(listed, self.t_paused | self.t_bopen | self.t_running)

    def test_pause_calendar_heatmap_event_measures(self):
        """R7, R9, R10: các measure đọc được và cộng đúng."""
        Task = self.env['sla.task']
        domain = [('id', 'in', self.all.ids)]
        self.t_late.sudo().write({'business_pause_duration': 1.5, 'pause_duration': 2.0})
        rows = _fgroup(Task, domain, ['sla_id'], ['business_pause_duration:sum', 'pause_duration:sum'])
        got = {r['sla_id'][1]: r['business_pause_duration:sum'] for r in rows}
        self.assertEqual(got["REP response SLA"], 1.5)
        rows = _fgroup(Task, domain, ['sla_id'], ['duration:sum', 'business_duration:sum'])
        got = {r['sla_id'][1]: r['business_duration:sum'] for r in rows}
        self.assertEqual(got["REP response SLA"], 12.0)
        rows = _fgroup(Task, domain, ['res_model', 'start_time:month'], ['achieved_rate:avg', '__count'])
        self.assertTrue(rows)
        self.assertEqual(sum(r['__count'] for r in rows), 6)

    def test_escalation_activity(self):
        """R8: event theo loại x định nghĩa x tuần; action chỉ lấy breach/escalate/escalate_failed."""
        Event = self.env['sla.event'].sudo()
        now = self.now
        for ev, definition in (('breach', self.d_resp), ('escalate', self.d_resp), ('escalate', self.d_reso),
                               ('escalate_failed', self.d_resp), ('pause', self.d_resp)):
            Event.create({'event': ev, 'event_dt': now, 'definition_id': definition.id})
        action = _action(self.env, 'escalation')
        domain = safe_eval(action.domain) + [('definition_id', 'in', (self.d_resp | self.d_reso).ids)]
        rows = _fgroup(self.env(user=self.user)['sla.event'], 
            domain, ['event', 'definition_id', 'event_dt:week'], ['__count'])
        got = {(r['event'], r['definition_id'][1]): r['__count'] for r in rows}
        self.assertEqual(got, {('breach', "REP response SLA"): 1, ('escalate', "REP response SLA"): 1,
                               ('escalate', "REP resolution OLA"): 1, ('escalate_failed', "REP response SLA"): 1})
        search_arch = self.env['sla.event'].get_views([(False, 'search')])['views']['search']['arch']
        for name in ('escalation_activity', 'last_30', 'group_week', 'group_month', 'group_model'):
            self.assertIn('name="%s"' % name, search_arch)

    # ------------------------------------------------------------------
    # Bộ lọc của search view sla.task
    # ------------------------------------------------------------------

    def _filter_domain(self, name):
        arch = self.env['sla.task'].get_views([(False, 'search')])['views']['search']['arch']
        node = etree.fromstring(arch).xpath('//filter[@name="%s"]' % name)
        self.assertTrue(node, "missing filter %s" % name)
        today = fields.Date.context_today(self.env['sla.task'])
        return safe_eval(node[0].get('domain'), {
            'context_today': lambda: today, 'relativedelta': relativedelta, 'datetime': datetime,
            'uid': self.env.uid})

    def _filtered(self, name):
        domain = self._filter_domain(name) + [('id', 'in', self.all.ids)]
        return self.env['sla.task'].search(domain)

    def test_search_filters(self):
        t = self
        self.assertEqual(self._filtered('open'), t.t_bopen | t.t_running | t.t_paused)
        self.assertEqual(self._filtered('breached_open'), t.t_bopen)
        self.assertEqual(self._filtered('late'), t.t_late)
        self.assertEqual(self._filtered('response'), t.t_ontime | t.t_late | t.t_bopen)
        self.assertEqual(self._filtered('resolution'), t.t_running | t.t_paused | t.t_cancel)
        self.assertEqual(self._filtered('type_sla'), t.t_ontime | t.t_late | t.t_bopen)
        self.assertEqual(self._filtered('type_ola'), t.t_running | t.t_paused | t.t_cancel)
        self.assertEqual(self._filtered('last_30'), self.all - t.t_paused)
        self.assertEqual(self._filtered('this_week'), t.t_late | t.t_running)
        self.assertEqual(self._filtered('due_this_week'), t.t_running)

    def test_search_groupbys_exist(self):
        arch = self.env['sla.task'].get_views([(False, 'search')])['views']['search']['arch']
        for name in ('group_outcome', 'group_usage_bucket', 'group_sla_type', 'group_sla_target',
                     'group_start_week', 'group_start_month', 'group_end_week', 'group_end_month',
                     'group_planned_end_day', 'group_planned_end_week'):
            self.assertIn('name="%s"' % name, arch)
        # mỗi group-by đọc được qua read_group
        for spec in ('outcome', 'usage_bucket', 'sla_type', 'sla_target', 'start_time:week', 'start_time:month',
                     'end_time:week', 'end_time:month', 'planned_end_time:day', 'planned_end_time:week'):
            rows = _fgroup(self.env(user=self.user)['sla.task'], 
                [('id', 'in', self.all.ids)], [spec], ['__count'])
            self.assertEqual(sum(r['__count'] for r in rows), 6, spec)

    def test_empty_database_actions(self):
        """Không có task nào: mọi action vẫn mở được, nhóm rỗng không lỗi."""
        self.all.unlink()
        for key in KEYS:
            action = _action(self.env, key)
            model = self.env[action.res_model]
            views = model.get_views([(False, vt) for vt in action.view_mode.split(',')])['views']
            for view_type in ('graph', 'pivot'):
                if view_type in views:
                    groupby, aggregates = _groupby_and_aggregates(model, view_type, views[view_type]['arch'])
                    domain = safe_eval(action.domain or '[]') + [('id', '=', 0)]
                    self.assertEqual(_fgroup(model, domain, groupby, aggregates), [])

    def test_ja_translations_present(self):
        """ja_JP.po có chuỗi mới (menu, tên action, bộ lọc)."""
        path = os.path.join(get_module_path(MODULE), 'i18n', 'ja_JP.po')
        with open(path, encoding='utf-8') as f:
            content = f.read()
        for msgid in ('Reporting', 'Compliance Trend', 'Response Time Distribution', 'Status Mix',
                      'Open Backlog & Ageing', 'Performance by Definition and Source', 'Performance by Source',
                      'Pause Analysis', 'Escalation Activity', 'Source Heatmap', 'Calendar Impact',
                      'Last 30 Days', 'This Week', 'Due This Week', 'Response SLAs', 'Resolution SLAs',
                      'Breached Open', 'Late', 'Open', 'Outcome', 'Usage Range'):
            self.assertIn('msgid "%s"\nmsgstr "' % msgid, content, msgid)
            idx = content.index('msgid "%s"\nmsgstr "' % msgid)
            line = content[idx:].split('\n')[1]
            self.assertNotEqual(line, 'msgstr ""', "ja_JP missing for %s" % msgid)


@tagged(*TAGS)
class TestReportingTour(SlaHttpCase):
    """Tour: mở app SLA, menu Reporting và từng màn hình."""

    browser_size = '1366,768'

    def test_reporting_menu_tour(self):
        env = self.env
        definition = env['sla.definition'].create({
            'active': True, 'name': "Tour SLA", 'model_id': env['ir.model']._get('res.partner').id,
            'duration': 4, 'start_domain': "[('ref', '=', 'NEVER')]"})
        now = fields.Datetime.now()
        for i, (stage, breached) in enumerate((('achieved', False), ('breached', True), ('in_progress', False))):
            partner = env['res.partner'].create({'name': "Tour P%d" % i})
            vals = {
                'sla_id': definition.id, 'res_model': 'res.partner', 'res_id': partner.id,
                'stage': stage, 'start_time': now - timedelta(days=1), 'target_duration': 4,
                'planned_end_time': now + timedelta(hours=4), 'has_breached': breached,
                'business_duration': 1.0 + i * 3}
            if stage == 'in_progress':
                vals['running_since'] = now - timedelta(hours=1)
            else:
                vals['end_time'] = now
            env['sla.task'].sudo().create(vals)
        self.start_tour('/web', 'dwo_sla_reporting_menu', login='admin')
        self.start_tour('/web', 'dwo_sla_graph_colors', login='admin')
