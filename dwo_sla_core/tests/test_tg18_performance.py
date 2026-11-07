# -*- coding: utf-8 -*-
"""TG-18: hiệu năng với tải lớn (docs/060 TC-PRF-*, kịch bản tải do người dùng yêu cầu).

Kịch bản: 300 ticket đang mở, mỗi ticket có 30 task SLA (30 định nghĩa cùng
khớp); 6 định nghĩa có escalation gửi email cho admin ở mức 50%, 75%, 100%
=> 9000 task, 1800 task có escalation, 5400 email khi chạy hết.
Chỉ chạy khi đặt biến môi trường `SLA_PERF=1` (chạy lâu, không nằm trong bộ test thường):
    SLA_PERF=1 odoo-bin ... --test-tags /dwo_sla_core:TestPerformanceLoad
Kết quả (thời gian, số truy vấn) được ghi ở log mức INFO với tiền tố "SLA-PERF".
Refs: REQ-PERF-001, REQ-PERF-002, REQ-REL-002
"""
import logging
import os
import time
import unittest
from datetime import datetime, timedelta

from odoo.tests import tagged

from .common import SlaCase, T0, hours

_logger = logging.getLogger(__name__)
TICKETS = int(os.environ.get('SLA_PERF_TICKETS', 300))
DEFINITIONS = 30
ESCALATING = 6
EMAIL_CODE = (
    "env['mail.mail'].create({'subject': 'SLA escalation: %s' % record.name, "
    "'email_to': 'admin@example.com', 'body_html': '<p>SLA escalation</p>'})")


@tagged('post_install', '-at_install', 'dwo_sla_perf')
@unittest.skipUnless(os.environ.get('SLA_PERF'), "đặt SLA_PERF=1 để chạy test hiệu năng")
class TestPerformanceLoad(SlaCase):

    def measure(self, label, func):
        """Chạy `func`, ghi thời gian và số truy vấn; trả (kết quả, giây, truy vấn)."""
        self.env.flush_all()
        queries0, start = self.env.cr.sql_log_count, time.perf_counter()
        result = func()
        self.env.flush_all()
        elapsed = time.perf_counter() - start
        queries = self.env.cr.sql_log_count - queries0
        _logger.info("SLA-PERF %-34s %8.2fs %9d queries", label, elapsed, queries)
        return result, elapsed, queries

    def drain(self, now):
        """Gọi process_due đến khi hết task đến hạn tại `now`; trả số lần gọi."""
        calls = 0
        with self.at(now):
            while self.Task.sudo().search_count([
                    ('stage', '=', 'in_progress'), ('next_due_at', '<=', now)]):
                self.Processor.process_due()
                calls += 1
                self.assertLess(calls, 10000)
        return calls

    def test_prf_load_300_tickets_30_tasks(self):
        """300 ticket x 30 task, 6 task/ticket có escalation email 50/75/100%: đo từng pha."""
        self.no_commit_progress()
        self.env['ir.config_parameter'].sudo().set_param('dwo_sla_core.batch_size', '100000')
        action = self.make_server_action(EMAIL_CODE)
        definitions = self.Definition
        for index in range(DEFINITIONS):
            definition = self.make_definition(name="SLA-PERF %02d" % index, duration=8)
            if index < ESCALATING:
                for percent in (50, 75, 100):
                    self.make_escalation(definition, percent, action=action)
            definitions |= definition
        n_tasks = TICKETS * DEFINITIONS
        n_escalating = TICKETS * ESCALATING

        with self.at(T0):
            partners, t_attach, q_attach = self.measure(
                "attach %d tickets" % TICKETS,
                lambda: self.Partner.create([
                    {'name': "Ticket %04d" % i, 'ref': 'NEW'} for i in range(TICKETS)]))
        self.assertEqual(self.Task.sudo().search_count([('sla_id', 'in', definitions.ids)]),
                         n_tasks)

        mails0 = self.env['mail.mail'].sudo().search_count([('email_to', '=', 'admin@example.com')])
        for percent, now in ((50, T0 + hours(4)), (75, T0 + hours(6)), (100, T0 + hours(8))):
            calls, elapsed, queries = self.measure(
                "process_due at %d%%" % percent, lambda now=now: self.drain(now))
            _logger.info("SLA-PERF   -> %d lần gọi, %.1f ms/lần", calls, 1000 * elapsed / max(calls, 1))
        mails = self.env['mail.mail'].sudo().search_count(
            [('email_to', '=', 'admin@example.com')]) - mails0
        self.assertEqual(mails, n_escalating * 3)
        self.assertEqual(self.Task.sudo().search_count([
            ('sla_id', 'in', definitions.ids), ('has_breached', '=', True)]), n_tasks)

        _res, t_write, q_write = self.measure(
            "write %d tickets (ref=WORK)" % TICKETS,
            lambda: self.write_all(partners, {'ref': 'WORK'}, T0 + hours(9)))
        _res, t_stop, q_stop = self.measure(
            "stop %d tickets (ref=DONE)" % TICKETS,
            lambda: self.write_all(partners, {'ref': 'DONE'}, T0 + hours(10)))
        self.assertEqual(self.Task.sudo().search_count([
            ('sla_id', 'in', definitions.ids), ('stage', '=', 'breached')]), n_tasks)

    def write_all(self, partners, vals, now):
        with self.at(now):
            partners.write(vals)

    def test_prf_percent_used_list_80(self):
        """Đọc `business_percent_used` của 80 task đang chạy (một trang list), có lịch và không lịch."""
        cal = self.make_calendar()
        for label, vals in (("no calendar", {}),
                            ("with calendar", {'schedule_source': 'definition',
                                               'schedule_id': cal.id})):
            definition = self.make_definition(name="SLA-PERF %s" % label, **vals)
            with self.at(T0):
                self.Partner.create([
                    {'name': "List %s %02d" % (label, i), 'ref': 'NEW'} for i in range(80)])
            tasks = self.Task.sudo().search([('sla_id', '=', definition.id)], limit=80)
            self.assertEqual(len(tasks), 80)
            with self.at(T0 + hours(2)):
                tasks.invalidate_recordset()
                _res, elapsed, queries = self.measure(
                    "read business_percent_used x80 (%s)" % label, lambda: tasks.mapped('business_percent_used'))
                # Mục tiêu mặc định 4 giờ, đã chạy 2 giờ làm việc/giờ thường
                self.assertEqual(set(tasks.mapped('business_percent_used')), {50})

    def test_prf_percent_used_list_80_holidays(self):
        """Như trên nhưng lịch có ngày nghỉ lễ (11 ngày/năm x 3 năm) và task đã chạy 120 ngày."""
        cal = self.make_calendar()
        holidays = ((1, 1), (2, 16), (2, 17), (2, 18), (2, 19), (2, 20),
                    (4, 27), (4, 30), (5, 1), (9, 2), (9, 3))
        self.env['resource.calendar.leaves'].create([{
            'name': "Holiday %d-%02d-%02d" % (year, month, day),
            'schedule_id': cal.id,
            'date_from': datetime(year, month, day, 0, 0) - timedelta(hours=7),
            'date_to': datetime(year, month, day, 23, 59) - timedelta(hours=7),
        } for year in (2026, 2027, 2028) for month, day in holidays])
        definition = self.make_definition(
            name="SLA-PERF holidays", schedule_source='definition', schedule_id=cal.id)
        with self.at(T0):
            self.Partner.create([
                {'name': "Holiday %02d" % i, 'ref': 'NEW'} for i in range(80)])
        tasks = self.Task.sudo().search([('sla_id', '=', definition.id)], limit=80)
        self.assertEqual(len(tasks), 80)
        with self.at(T0 + timedelta(days=120)):
            tasks.invalidate_recordset()
            _res, elapsed, queries = self.measure(
                "read business_percent_used x80 (holidays)", lambda: tasks.mapped('business_percent_used'))
            self.assertGreater(min(tasks.mapped('business_percent_used')), 100)
