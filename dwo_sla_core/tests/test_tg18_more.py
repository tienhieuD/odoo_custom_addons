# -*- coding: utf-8 -*-
"""TG-18 bổ sung: số truy vấn theo kích thước lô, cron, patch theo model (docs/060 TC-PRF-*).

TC-PRF-001/002 (hai database A/B trước-sau khi cài module), PRF-006..008 ở quy mô đầy đủ cần
môi trường benchmark riêng; ở đây có bản thu nhỏ để bắt hồi quy (ghi chú lệch ở TASKS.md).
Refs: REQ-PERF-001, REQ-PERF-002, REQ-REL-002
"""
import time

from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')
MAX_EXTRA_QUERIES = 5


@tagged(*TAGS, 'tg_18')
class TestQueryCount(SlaCase):

    def queries(self, records, now, changed=None):
        """Số truy vấn của một lần `evaluate` (đã flush trước và sau để đo đủ)."""
        self.env.flush_all()
        before = self.env.cr.sql_log_count
        self.Engine.evaluate(records, now=now, changed=changed)
        self.env.flush_all()
        return self.env.cr.sql_log_count - before

    def batch(self, size, ref):
        partners = self.Partner
        for _ in range(size):
            partners |= self.make_partner(False)
        # đặt ref bằng SQL để không kích hoạt hook; engine được gọi tường minh
        self.env.cr.execute("UPDATE res_partner SET ref=%s WHERE id IN %s", (ref, tuple(partners.ids)))
        partners.invalidate_recordset()
        return partners

    def compare(self, prepare, label):
        """Q(100) - Q(10) <= 5 (TC-PRF-003..005); lần đo đầu là warm-up cache."""
        self.queries(self.batch(2, 'ZZZ'), T0)
        results = {}
        for size in (10, 100):
            records, now = prepare(size)
            results[size] = self.queries(records, now, {'ref'})
        _logger_msg = "%s: Q10=%s Q100=%s" % (label, results[10], results[100])
        self.assertLessEqual(results[100] - results[10], MAX_EXTRA_QUERIES, _logger_msg)

    def test_prf_003_attach_batch(self):
        """TC-PRF-003: lô khớp start 10 và 100 record -> chênh số truy vấn <= 5."""
        self.make_definition()
        self.compare(lambda size: (self.batch(size, 'NEW'), T0), "attach")

    def test_prf_004_no_match_batch(self):
        """TC-PRF-004: lô không khớp điều kiện nào."""
        self.make_definition()
        self.compare(lambda size: (self.batch(size, 'ZZZ'), T0), "no match")

    def test_prf_005_stop_batch(self):
        """TC-PRF-005: kết thúc hàng loạt 10 và 100 record."""
        self.make_definition()

        def prepare(size):
            partners = self.batch(size, 'NEW')
            self.Engine.evaluate(partners, now=T0)
            self.env.cr.execute("UPDATE res_partner SET ref='DONE' WHERE id IN %s", (tuple(partners.ids),))
            partners.invalidate_recordset()
            return partners, T0 + hours(1)

        self.compare(prepare, "stop")


@tagged(*TAGS, 'tg_18')
class TestBackgroundScale(SlaCase):

    def setUp(self):
        super().setUp()
        self.no_commit_progress()
        self.d = self.make_definition()
        self.make_escalation(self.d, 75)

    def make_due_tasks(self, count, due):
        """`count` task in_progress (mốc 75% đến hạn tại `due`), dựng bằng ORM theo lô."""
        with self.at(T0):
            partners = self.Partner.create([{'name': "P %s" % i, 'ref': 'NEW'} for i in range(count)])
        tasks = self.Task.sudo().search([('sla_id', '=', self.d.id)])
        tasks.write({'next_due_at': due})
        return partners, tasks

    def drain(self, now):
        calls = 0
        with self.at(now):
            while self.Task.sudo().search_count([('stage', '=', 'in_progress'), ('next_due_at', '<=', now)]):
                self.Processor.process_due()
                calls += 1
                self.assertLess(calls, 20)
        return calls

    def test_prf_007_200_escalations_four_calls(self):
        """TC-PRF-007: 200 mốc đến hạn, batch_size 50 -> đúng 4 lần gọi, 200 event escalate."""
        _partners, tasks = self.make_due_tasks(200, T0 + hours(3))
        start = time.perf_counter()
        calls = self.drain(T0 + hours(3) + hours(1 / 60.0))
        elapsed = time.perf_counter() - start
        self.assertEqual(calls, 4)
        self.assertEqual(sum(t.event_ids.filtered(lambda e: e.event == 'escalate').__len__() for t in tasks), 200)
        self.assertLessEqual(elapsed, 60.0, "200 mốc phải xử lý xong trong 60 giây")

    def test_prf_008_200_breaches_four_calls(self):
        """TC-PRF-008: 200 task đến hạn vi phạm, batch_size 50 -> 4 lần gọi, 200 event breach."""
        self.d.escalation_ids.unlink()
        _partners, tasks = self.make_due_tasks(200, T0 + hours(4))
        start = time.perf_counter()
        calls = self.drain(T0 + hours(4) + hours(1 / 60.0))
        elapsed = time.perf_counter() - start
        self.assertEqual(calls, 4)
        self.assertEqual(len(tasks.filtered('has_breached')), 200)
        self.assertEqual(self.Event.sudo().search_count(
            [('task_id', 'in', tasks.ids), ('event', '=', 'breach')]), 200)
        self.assertLessEqual(elapsed, 60.0)

    def test_prf_006_cycle_time_independent_of_total(self):
        """TC-PRF-006 (thu nhỏ): chu kỳ xử lý 10 task đến hạn không tăng quá 2 lần khi tổng task x10."""
        def cycle(total):
            self.Task.sudo().search([]).unlink()
            _partners, tasks = self.make_due_tasks(total, T0 + hours(9))
            tasks[:10].write({'next_due_at': T0 + hours(3)})
            start = time.perf_counter()
            with self.at(T0 + hours(3)):
                self.Processor.process_due()
            return time.perf_counter() - start

        cycle(20)  # warm-up
        small, large = min(cycle(100) for _ in range(3)), min(cycle(1000) for _ in range(3))
        self.assertLessEqual(large / small, 2.0, "small=%.3fs large=%.3fs" % (small, large))


@tagged(*TAGS, 'tg_18')
class TestCronAndPatches(SlaCase):

    def test_prf_009_cron_every_minute(self):
        """TC-PRF-009: cron xử lý nền chạy mỗi 1 phút và đang bật."""
        cron = self.env['ir.cron'].sudo().search([
            ('ir_actions_server_id.code', 'like', 'process_due')], limit=1)
        self.assertTrue(cron)
        self.assertEqual((cron.active, cron.interval_number, cron.interval_type), (True, 1, 'minutes'))

    def test_prf_010_patch_only_models_with_definition(self):
        """TC-PRF-010: chỉ model có định nghĩa bị patch; hết định nghĩa thì gỡ patch."""
        names = ('create', 'write', '_compute_field_value')

        def patched(model):
            model_class = type(self.env[model])
            return [bool(getattr(getattr(model_class, name), 'sla_patch', False)) for name in names]

        self.assertEqual((patched('res.partner'), patched('res.country')), ([False] * 3, [False] * 3))
        d = self.make_definition()
        self.assertEqual((patched('res.partner'), patched('res.country')), ([True] * 3, [False] * 3))
        d.active = False
        self.assertEqual(patched('res.partner'), [False] * 3)
