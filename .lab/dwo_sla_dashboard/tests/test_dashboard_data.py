# -*- coding: utf-8 -*-
"""get_dashboard_data: số liệu, kỳ, bộ lọc, quyền, tên record, đa công ty, hiệu năng."""
import os
import time
from datetime import timedelta

from odoo import fields
from odoo.addons.dwo_sla_core.tests.common import SlaCase
from odoo.tests import new_test_user, tagged

TAGS = ('post_install', '-at_install', 'dwo_sla_dashboard')


class DashboardCase(SlaCase):
    """Dựng task trực tiếp (quan hệ stage/end_time hợp lệ) để biết chính xác số liệu."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.now = fields.Datetime.now()
        cls.d_resp = cls.env['sla.definition'].create({
            'name': "DB Response", 'model_id': cls.partner_model.id, 'duration': 4,
            'type': 'sla', 'target': 'response', 'due_soon_hours': 2,
            'start_domain': "[('ref', '=', 'NEW')]"})
        cls.d_res = cls.env['sla.definition'].create({
            'name': "DB Resolution OLA", 'model_id': cls.partner_model.id, 'duration': 8,
            'type': 'ola', 'target': 'resolution', 'due_soon_hours': 2,
            'start_domain': "[('ref', '=', 'NEW')]"})
        cls.user = new_test_user(cls.env, login='sla_dash_user', groups='dwo_sla_core.group_sla_user')
        cls.manager = new_test_user(cls.env, login='sla_dash_mgr', groups='dwo_sla_core.group_sla_manager')

    @classmethod
    def mk(cls, definition, kind, ended_days_ago=None, started_days_ago=40, company=False):
        """kind: on_time, late, breached_open, running, due_soon, paused, cancelled."""
        now = cls.now
        partner = cls.Partner.create({'name': "DashP %s" % kind})
        start = now - timedelta(days=started_days_ago)
        vals = {
            'sla_id': definition.id, 'res_model': 'res.partner', 'res_id': partner.id,
            'target_duration': definition.duration, 'start_time': start,
            'company_id': company, 'source_name': partner.display_name,
        }
        end = now - timedelta(days=ended_days_ago) if ended_days_ago is not None else None
        if kind == 'on_time':
            vals.update(stage='achieved', end_time=end, planned_end_time=start + timedelta(hours=4),
                        business_duration=1.0)
        elif kind == 'late':
            vals.update(stage='breached', has_breached=True, end_time=end,
                        planned_end_time=start + timedelta(hours=4), business_duration=6.0)
        elif kind == 'cancelled':
            vals.update(stage='cancelled', end_time=end, planned_end_time=start + timedelta(hours=4))
        elif kind == 'breached_open':
            vals.update(stage='in_progress', has_breached=True, running_since=start,
                        planned_end_time=now - timedelta(hours=3), business_duration=5.0)
        elif kind == 'paused':
            vals.update(stage='paused', pause_time=start, planned_end_time=now + timedelta(days=2),
                        business_duration=1.0)
        elif kind == 'due_soon':
            vals.update(stage='in_progress', running_since=now - timedelta(hours=3),
                        start_time=now - timedelta(hours=3), planned_end_time=now + timedelta(hours=1))
        else:  # running, còn xa hạn
            vals.update(stage='in_progress', running_since=now - timedelta(hours=1),
                        start_time=now - timedelta(hours=1), planned_end_time=now + timedelta(days=2))
        return cls.Task.sudo().create(vals)

    def data(self, period=30, filters=None, user=None):
        return self.Task.with_user(user or self.env.user).get_dashboard_data(period, filters)


@tagged(*TAGS, 'dash_data')
class TestDashboardData(DashboardCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Task.sudo().search([]).unlink()
        # kỳ này (30 ngày): 3 đúng hạn + 1 trễ, định nghĩa response; 1 trễ OLA
        for days in (2, 5, 10):
            cls.mk(cls.d_resp, 'on_time', ended_days_ago=days)
        cls.mk(cls.d_resp, 'late', ended_days_ago=3)
        cls.mk(cls.d_res, 'late', ended_days_ago=40 - 38)  # 2 ngày trước
        # kỳ trước (30-60 ngày): 1 đúng hạn, 1 trễ
        cls.mk(cls.d_resp, 'on_time', ended_days_ago=40, started_days_ago=45)
        cls.mk(cls.d_resp, 'late', ended_days_ago=45, started_days_ago=50)
        # đang mở
        cls.mk(cls.d_resp, 'breached_open')
        cls.mk(cls.d_res, 'running')
        cls.mk(cls.d_res, 'paused')
        cls.mk(cls.d_resp, 'due_soon')
        cls.mk(cls.d_resp, 'cancelled', ended_days_ago=1)

    def test_kpis(self):
        k = self.data()['kpis']
        self.assertEqual(k['running']['value'], 3)       # breached_open + running + due_soon (in_progress)
        self.assertEqual(k['due_soon']['value'], 1)
        self.assertEqual(k['breached']['value'], 1)
        self.assertEqual(k['late']['value'], 2)          # 2 task trễ trong 30 ngày
        # 3 đúng hạn / (3 + 2 trễ)
        self.assertEqual(k['achieved_rate']['value'], 60.0)
        # kỳ trước: 1/2
        self.assertEqual(k['achieved_rate']['previous'], 50.0)
        self.assertEqual(k['achieved_rate']['delta'], 10.0)
        self.assertEqual(k['late']['previous'], 1)
        self.assertEqual(k['late']['delta'], 1)

    def test_kpi_domains_match_counts(self):
        data = self.data()
        for key, kpi in data['kpis'].items():
            if key == 'achieved_rate':
                continue
            self.assertEqual(self.Task.search_count(kpi['domain']), kpi['value'], key)
        self.assertEqual(self.Task.search_count(data['kpis']['achieved_rate']['domain']), 5)

    def test_previous_snapshot(self):
        # hai task đang mở từ 40 ngày trước, vẫn mở khi kỳ 30 ngày bắt đầu
        before = self.data()['kpis']['breached']
        old = self.mk(self.d_resp, 'breached_open', started_days_ago=40)
        old.planned_end_time = old.start_time + timedelta(hours=4)
        k = self.data()['kpis']['breached']
        self.assertEqual(k['value'], before['value'] + 1)
        # mở từ 40 ngày trước và hạn (start + 4h) đã qua trước đầu kỳ: tính vào kỳ trước
        self.assertEqual(k['previous'], before['previous'] + 1)

    def test_period(self):
        k7 = self.data(7)['kpis']
        self.assertEqual(k7['late']['value'], 2)
        self.assertEqual(k7['achieved_rate']['value'], 50.0)   # 2 đúng hạn (2 và 5 ngày) / (2+2 trễ)
        self.assertEqual(self.data(7)['period'], 7)
        self.assertEqual(self.data(5)['period'], 30)   # kỳ không hợp lệ về 30
        k90 = self.data(90)['kpis']
        self.assertEqual(k90['late']['value'], 3)

    def test_filters(self):
        k = self.data(30, {'sla_type': 'ola'})['kpis']
        self.assertEqual((k['late']['value'], k['running']['value']), (1, 1))
        k = self.data(30, {'sla_target': 'response'})['kpis']
        self.assertEqual((k['late']['value'], k['running']['value']), (1, 2))
        k = self.data(30, {'sla_ids': [self.d_res.id]})['kpis']
        self.assertEqual(k['late']['value'], 1)
        # bộ lọc rác bị bỏ qua, không lỗi
        d = self.data(30, {'sla_type': 'x; drop', 'sla_ids': ['a', None, self.d_res.id]})
        self.assertFalse(d['filters']['sla_type'])
        self.assertEqual(d['filters']['sla_ids'], [self.d_res.id])
        # bộ lọc cũng áp cho biểu đồ
        d = self.data(30, {'sla_ids': [self.d_res.id]})
        self.assertEqual({b['id'] for b in d['bars']}, {self.d_res.id})
        self.assertEqual(sum(s['count'] for s in d['donut']), 3)

    def test_charts(self):
        d = self.data()
        donut = {s['key']: s['count'] for s in d['donut']}
        self.assertEqual(donut, {'on_time': 3, 'late': 2, 'breached_open': 1, 'running': 2,
                                 'paused': 1, 'cancelled': 1})
        bars = {b['id']: b for b in d['bars']}
        self.assertEqual((bars[self.d_resp.id]['on_time'], bars[self.d_resp.id]['late'],
                          bars[self.d_resp.id]['breached_open']), (3, 1, 1))
        self.assertEqual(bars[self.d_res.id]['late'], 1)
        # domain khoan sâu cho lát donut khớp số lượng
        for key, count in donut.items():
            self.assertEqual(self.Task.search_count(d['scope_domain'] + [('outcome', '=', key)]), count)
        self.assertTrue(d['weekly'])
        self.assertLessEqual(len(d['weekly']), 12)
        self.assertEqual(len(self.data(90)['weekly']) <= 12, True)
        for w in d['weekly']:
            self.assertTrue(w['rate'] is None or 0 <= w['rate'] <= 100)

    def test_attention(self):
        d = self.data()
        rows = d['attention']
        self.assertEqual(len(rows), 2)
        self.assertTrue(rows[0]['breached'])      # vi phạm trước
        self.assertFalse(rows[1]['breached'])
        self.assertEqual(self.Task.search_count(d['attention_domain']), 2)

    def test_attention_limit(self):
        for _i in range(12):
            self.mk(self.d_resp, 'breached_open')
        self.assertEqual(len(self.data()['attention']), 10)

    def test_security_source_name(self):
        row = self.data(user=self.manager)['attention'][0]
        self.assertTrue(row['source_name'].startswith("DashP"))
        d = self.data(user=self.user)
        self.assertFalse(d['is_manager'])
        for row in d['attention']:
            self.assertNotIn('source_name', row)
            self.assertTrue(row['definition'] and row['model'])
        self.assertNotIn("DashP", str(d))
        self.assertEqual(d['kpis']['late']['value'], 2)

    def test_no_access(self):
        outsider = new_test_user(self.env, login='sla_dash_none', groups='base.group_user')
        from odoo.exceptions import AccessError
        with self.assertRaises(AccessError):
            self.Task.with_user(outsider).get_dashboard_data(30, {})

    def test_multi_company(self):
        other = self.env['res.company'].create({'name': "Dash Other Co"})
        self.mk(self.d_resp, 'breached_open', company=other.id)
        user = new_test_user(self.env, login='sla_dash_mc', groups='dwo_sla_core.group_sla_user')
        self.assertEqual(user.company_ids, self.env.company)
        self.assertEqual(self.data(user=user)['kpis']['breached']['value'], 1)  # chưa thuộc công ty kia
        user.write({'company_ids': [(4, other.id)]})
        both = self.Task.with_user(user).with_context(allowed_company_ids=[self.env.company.id, other.id])
        only_main = self.Task.with_user(user).with_context(allowed_company_ids=[self.env.company.id])
        self.assertEqual(both.get_dashboard_data(30, {})['kpis']['breached']['value'], 2)
        self.assertEqual(only_main.get_dashboard_data(30, {})['kpis']['breached']['value'], 1)

    def test_empty(self):
        self.Task.sudo().search([]).unlink()
        d = self.data()
        self.assertFalse(d['has_data'])
        self.assertEqual((d['donut'], d['bars'], d['weekly'], d['attention']), ([], [], [], []))
        self.assertEqual(d['kpis']['running']['value'], 0)
        self.assertIsNone(d['kpis']['achieved_rate']['value'])
        self.assertIsNone(d['kpis']['achieved_rate']['delta'])

    def test_due_soon_default_hours(self):
        """Định nghĩa không đặt giờ: dùng ngưỡng Settings; thẻ khớp field is_due_soon."""
        self.d_res.due_soon_hours = 0
        self.env['ir.config_parameter'].sudo().set_param('dwo_sla_core.due_soon_hours', '1.5')
        t = self.mk(self.d_res, 'running')
        t.planned_end_time = self.now + timedelta(hours=1)
        k = self.data()['kpis']
        self.assertEqual(k['due_soon']['value'], 2)


@tagged(*TAGS, 'dash_perf')
class TestDashboardPerformance(DashboardCase):

    def test_10k_tasks_under_one_second(self):
        self.Task.sudo().search([]).unlink()
        n = int(os.environ.get('SLA_DASH_TASKS', 10000))
        kinds = ['on_time', 'late', 'breached_open', 'running', 'paused', 'due_soon']
        now = self.now
        partner = self.Partner.create({'name': "DashPerf"})
        rows = []
        for i in range(n):
            kind = kinds[i % len(kinds)]
            definition = self.d_resp if i % 2 else self.d_res
            start = now - timedelta(days=1 + i % 60)
            rows.append((definition.id, kind, start))
        # bulk insert qua ORM create (một lần), res_id lặp lại: dùng id khác nhau để qua unique index
        partners = self.Partner.create([{'name': 'DP %d' % i} for i in range(n)])
        vals_list = []
        for (def_id, kind, start), p in zip(rows, partners):
            v = {'sla_id': def_id, 'res_model': 'res.partner', 'res_id': p.id, 'target_duration': 4,
                 'start_time': start, 'planned_end_time': start + timedelta(hours=4)}
            if kind in ('on_time', 'late'):
                v.update(stage='achieved' if kind == 'on_time' else 'breached',
                         has_breached=kind == 'late', end_time=start + timedelta(hours=3),
                         business_duration=2.0 if kind == 'on_time' else 6.0)
            elif kind == 'paused':
                v.update(stage='paused', pause_time=start, planned_end_time=now + timedelta(days=1))
            elif kind == 'breached_open':
                v.update(stage='in_progress', has_breached=True, running_since=start)
            elif kind == 'due_soon':
                v.update(stage='in_progress', running_since=start, planned_end_time=now + timedelta(hours=1))
            else:
                v.update(stage='in_progress', running_since=start, planned_end_time=now + timedelta(days=3))
            vals_list.append(v)
        self.Task.sudo().create(vals_list)
        self.env.flush_all()
        self.env.cr.execute("ANALYZE sla_task")
        start_t = time.perf_counter()
        queries_before = self.env.cr.sql_log_count
        d = self.Task.get_dashboard_data(90, {})
        elapsed = time.perf_counter() - start_t
        queries = self.env.cr.sql_log_count - queries_before
        import logging
        logging.getLogger(__name__).info("SLA-DASH %d tasks: %.3fs, %d queries", n, elapsed, queries)
        self.assertEqual(sum(s['count'] for s in d['donut']) > 0, True)
        self.assertLess(elapsed, 1.0)
        self.assertLess(queries, 50)
