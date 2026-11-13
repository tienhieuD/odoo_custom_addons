# -*- coding: utf-8 -*-
"""TG-33: field lưu cho báo cáo (task 006 C1): outcome, final_percent_used,
usage_bucket, overdue_duration, source_name, sla_type, sla_target, migration."""
import importlib.util
import os

from odoo.tests import tagged

from .common import SlaCase, T0, hours


@tagged('post_install', '-at_install', 'tg_33')
class TestReportingFields(SlaCase):

    def setUp(self):
        super().setUp()
        self.d = self.make_definition()  # mục tiêu 4 giờ, 24x7

    def _task(self, ref='NEW'):
        p = self.make_partner(ref)
        return p, self.task_of(p, self.d)

    def test_running(self):
        _p, t = self._task()
        self.assertEqual(t.outcome, 'running')
        self.assertEqual(t.final_percent_used, 0.0)
        self.assertEqual(t.usage_bucket, '0_50')
        self.assertEqual(t.overdue_duration, 0.0)

    def test_on_time(self):
        p, t = self._task()
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        self.assertEqual((t.stage, t.outcome), ('achieved', 'on_time'))
        self.assertAlmostEqual(t.final_percent_used, 25.0)
        self.assertEqual(t.usage_bucket, '0_50')
        self.assertEqual(t.overdue_duration, 0.0)

    def test_late(self):
        p, t = self._task()
        self.write(p, {'ref': 'DONE'}, T0 + hours(5))
        self.assertEqual((t.stage, t.outcome), ('breached', 'late'))
        self.assertAlmostEqual(t.final_percent_used, 125.0)
        self.assertEqual(t.usage_bucket, '100_150')
        self.assertAlmostEqual(t.overdue_duration, 1.0)

    def test_breached_open_and_complete_later(self):
        p, t = self._task()
        self.Processor._process_task(t, T0 + hours(5))
        self.assertTrue(t.has_breached)
        self.assertEqual((t.stage, t.outcome), ('in_progress', 'breached_open'))
        self.assertGreaterEqual(t.final_percent_used, 100.0)
        self.assertEqual(t.usage_bucket, '100_150')
        self.write(p, {'ref': 'DONE'}, T0 + hours(7))
        self.assertEqual(t.outcome, 'late')
        self.assertAlmostEqual(t.final_percent_used, 175.0)
        self.assertEqual(t.usage_bucket, '150_plus')
        self.assertAlmostEqual(t.overdue_duration, 3.0)

    def test_pause_resume_updates(self):
        p, t = self._task()
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        self.assertEqual((t.stage, t.outcome), ('paused', 'paused'))
        self.assertAlmostEqual(t.final_percent_used, 25.0)
        self.write(p, {'ref': 'WORK'}, T0 + hours(2))
        self.assertEqual(t.outcome, 'running')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(6))
        # đã vượt hạn trước khi tạm dừng: breached_open dù đang paused
        self.assertEqual((t.stage, t.outcome), ('paused', 'breached_open'))
        self.assertGreaterEqual(t.final_percent_used, 100.0)
        self.write(p, {'ref': 'DONE'}, T0 + hours(8))
        self.assertEqual(t.outcome, 'late')

    def test_cancelled(self):
        p, t = self._task()
        self.write(p, {'ref': 'CANCEL'}, T0 + hours(1))
        self.assertEqual((t.stage, t.outcome), ('cancelled', 'cancelled'))
        self.assertEqual(t.overdue_duration, 0.0)

    def test_bucket_boundaries(self):
        _p, t = self._task()
        cases = [(0, '0_50'), (1.99, '0_50'), (2, '50_75'), (2.99, '50_75'),
                 (3, '75_100'), (3.99, '75_100'), (4, '100_150'), (6, '100_150'),
                 (6.01, '150_plus'), (40, '150_plus')]
        for elapsed, bucket in cases:
            t.business_duration = elapsed
            self.assertEqual(t.usage_bucket, bucket, "elapsed=%s" % elapsed)

    def test_zero_target(self):
        _p, t = self._task()
        t.write({'target_duration': 0, 'business_duration': 0})
        self.assertEqual((t.final_percent_used, t.usage_bucket), (0.0, '0_50'))
        t.business_duration = 0.5
        self.assertEqual((t.final_percent_used, t.usage_bucket), (100.0, '100_150'))

    def test_group_and_search_by_outcome(self):
        p1, _t1 = self._task()
        p2, _t2 = self._task('NEW')
        self.write(p2, {'ref': 'DONE'}, T0 + hours(1))
        groups = dict(self.Task._read_group(
            [('sla_id', '=', self.d.id)], ['outcome'], ['__count']))
        self.assertEqual(groups, {'running': 1, 'on_time': 1})
        avg = self.Task._read_group(
            [('sla_id', '=', self.d.id)], [], ['final_percent_used:avg'])
        self.assertAlmostEqual(avg[0][0], 25.0)  # chỉ task đã kết thúc

    def test_source_name_type_target(self):
        d = self.make_definition(name="SLA ola", type='ola', target='response',
                                 start_domain="[('ref', '=', 'OLA')]")
        p = self.make_partner('OLA', name="Azure Reporting")
        t = self.task_of(p, d)
        self.assertEqual(t.source_name, "Azure Reporting")
        self.assertEqual((t.sla_type, t.sla_target), ('ola', 'response'))
        d.target = 'resolution'
        self.assertEqual(t.sla_target, 'resolution')
        p.name = "Renamed"
        self.assertEqual(t.source_name, "Azure Reporting")  # không tự đổi tên
        t._refresh_source_names()
        self.assertEqual(t.source_name, "Renamed")

    def test_source_name_hidden_from_sla_user(self):
        """source_name lộ tên record nguồn: chỉ SLA Manager đọc được (TC-SEC-017)."""
        p = self.make_partner('NEW', name="Secret Co")
        t = self.task_of(p, self.d)
        user = self.make_user('sla_u33', 'user')
        manager = self.make_user('sla_m33', 'manager')
        self.assertNotIn('source_name', t.with_user(user).read()[0])
        self.assertEqual(t.with_user(manager).read(['source_name'])[0]['source_name'],
                         "Secret Co")

    def test_source_name_missing_record_falls_back(self):
        _p, t = self._task()
        t.res_id = 999999999
        self.assertEqual(t.source_name, "res.partner#999999999")

    def test_migration_recomputes(self):
        """Migration 18.0.1.2.0: xoá giá trị trên task đủ loại rồi chạy lại."""
        p1, t1 = self._task()
        p2, t2 = self._task()
        self.write(p2, {'ref': 'DONE'}, T0 + hours(6))
        p3, t3 = self._task()
        self.write(p3, {'ref': 'HOLD'}, T0 + hours(1))
        p4, t4 = self._task()
        self.write(p4, {'ref': 'CANCEL'}, T0 + hours(1))
        tasks = t1 | t2 | t3 | t4
        expected = {t.id: (t.outcome, round(t.final_percent_used, 4), t.usage_bucket,
                           round(t.overdue_duration, 4), t.source_name,
                           t.sla_type, t.sla_target) for t in tasks}
        self.env.flush_all()
        self.env.cr.execute(
            "UPDATE sla_task SET outcome=NULL, final_percent_used=NULL, "
            "usage_bucket=NULL, overdue_duration=NULL, source_name=NULL, "
            "sla_type=NULL, sla_target=NULL WHERE id IN %s", (tuple(tasks.ids),))
        tasks.invalidate_recordset()
        path = os.path.join(os.path.dirname(__file__), '..', 'migrations',
                            '18.0.1.2.0', 'post-migrate.py')
        spec = importlib.util.spec_from_file_location('sla_post_migrate_1_2_0', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.migrate(self.env.cr, '18.0.1.1.0')
        module.migrate(self.env.cr, '18.0.1.1.0')  # idempotent
        tasks.invalidate_recordset()
        for t in tasks:
            got = (t.outcome, round(t.final_percent_used, 4), t.usage_bucket,
                   round(t.overdue_duration, 4), t.source_name, t.sla_type,
                   t.sla_target)
            self.assertEqual(got, expected[t.id], "task %s" % t.id)
