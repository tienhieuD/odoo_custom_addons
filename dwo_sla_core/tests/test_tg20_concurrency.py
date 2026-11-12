# -*- coding: utf-8 -*-
"""Ca nhiều giao dịch (cursor thật, dữ liệu commit, tự dọn): docs/060 TC-ERR-005, 026, 027, 029,
TC-ESC-009, 059, TC-MUL-007.

Không dùng TransactionCase (cursor của nó dùng chung một giao dịch). Mỗi ca mở các cursor
độc lập; "barrier" được mô phỏng tuần tự bằng mã (không thread, không sleep) nên xác định.
Mọi dữ liệu tạo ra đều bị xóa ở `tearDown`.
Refs: REQ-FUNC-014, 024, REQ-REL-001, 002, AD-07, AD-08, AD-12
"""
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from unittest.mock import patch

import psycopg2

from odoo.modules.registry import Registry
from odoo import SUPERUSER_ID, api, fields
from odoo.tests import tagged
from odoo.tests.common import BaseCase, get_db_name

T0 = datetime(2026, 3, 2, 2, 0)
STD = {
    'active': True, 'duration': 4, 'schedule_source': 'none', 'cancel_mode': 'start_unmatched',
    'resume_mode': 'condition',
    'start_domain': "[('ref', 'in', ['NEW', 'WORK', 'HOLD'])]", 'stop_domain': "[('ref', '=', 'DONE')]",
    'pause_domain': "[('ref', '=', 'HOLD')]", 'resume_domain': "[('ref', '=', 'WORK')]",
    'cancel_domain': "[('ref', '=', 'CANCEL')]",
}


@tagged('post_install', '-at_install', 'dwo_sla_core')
class ConcurrentCase(BaseCase):
    """Cursor thật; dữ liệu commit; dọn dẹp bằng SQL ở tearDown."""

    def setUp(self):
        self.reg = Registry(get_db_name())
        self.cursors = []
        self.partner_ids, self.definition_ids = [], []
        self.calls = []
        self.addCleanup(self.cleanup)

    # ---- hạ tầng -----------------------------------------------------
    def new_env(self, isolation=None):
        cr = self.reg.cursor()
        self.cursors.append(cr)
        if isolation:
            cr.execute("SET TRANSACTION ISOLATION LEVEL %s" % isolation)
        cr.execute("SET LOCAL lock_timeout = '5s'")
        return api.Environment(cr, SUPERUSER_ID, {})

    def cleanup(self):
        for cr in self.cursors:
            try:
                cr.rollback()
                cr.close()
            except Exception:  # noqa: BLE001 -- đã đóng
                pass
        with self.reg.cursor() as cr:
            if self.definition_ids:
                ids = tuple(self.definition_ids)
                cr.execute("DELETE FROM sla_event WHERE definition_id IN %s", (ids,))
                cr.execute("DELETE FROM sla_event WHERE res_model='res.partner' AND res_id IN %s",
                           (tuple(self.partner_ids) or (0,),))
                cr.execute("DELETE FROM sla_task WHERE sla_id IN %s", (ids,))
                cr.execute("DELETE FROM sla_escalation WHERE definition_id IN %s", (ids,))
                cr.execute("DELETE FROM sla_definition WHERE id IN %s", (ids,))
            if self.partner_ids:
                cr.execute("DELETE FROM res_partner WHERE id IN %s", (tuple(self.partner_ids),))
            cr.execute("DELETE FROM ir_act_server WHERE id IN (SELECT id FROM ir_actions "
                       "WHERE name LIKE 'SLA-CONC %%')")
            cr.execute("DELETE FROM ir_actions WHERE name LIKE 'SLA-CONC %%'")
        self.reg.clear_caches()
        for model_class in self.reg.values():
            for name in ('create', 'write', '_compute_field_value', '_write'):
                try:
                    delattr(model_class, name)
                except AttributeError:
                    pass

    @contextmanager
    def at(self, now):
        with patch.object(fields.Datetime, 'now', return_value=now):
            yield

    def seed(self, count=1, ref='NEW', escalation=None, **definition_vals):
        """Tạo (commit) `count` partner TRƯỚC, rồi định nghĩa; trả (definition_id, [partner_id])."""
        env = self.new_env()
        partners = env['res.partner'].create([{'name': 'SLA-CONC P%s' % i, 'ref': ref} for i in range(count)])
        definition = env['sla.definition'].create({
            'name': 'SLA-CONC D', 'model_id': env['ir.model']._get('res.partner').id,
            **STD, **definition_vals})
        if escalation:
            action = env['ir.actions.server'].create({
                'name': 'SLA-CONC action', 'model_id': env['ir.model']._get('res.partner').id,
                'state': 'code', 'code': "record.write({'comment': 'N75'})"})
            env['sla.escalation'].create({
                'definition_id': definition.id, 'percent': escalation,
                'action_type': 'server_action', 'action_id': action.id})
            self.action_id = action.id
        env.cr.commit()
        self.partner_ids += partners.ids
        self.definition_ids.append(definition.id)
        return definition.id, partners.ids

    def count_actions(self):
        """Đếm lần chạy server action theo record (bọc `ir.actions.server.run`)."""
        case = self
        original = type(self.new_env()['ir.actions.server']).run

        def run(actions, *args, **kwargs):
            case.calls.append(actions.env.context.get('active_id'))
            return original(actions, *args, **kwargs)

        patcher = patch.object(type(self.new_env()['ir.actions.server']), 'run', run)
        patcher.start()
        self.addCleanup(patcher.stop)

    def fresh(self, sql, params=()):
        with self.reg.cursor() as cr:
            cr.execute(sql, params)
            return cr.fetchall()

    def due_env_processor(self, env, now):
        with self.at(now), patch.object(
                type(env['ir.cron']), '_commit_progress', return_value=float('inf')):
            env['sla.processor'].process_due()
        env.cr.commit()


class TestConcurrentAttach(ConcurrentCase):

    def test_err_005_mul_007_two_transactions_attach_same_record(self):
        """TC-ERR-005/MUL-007: hai giao dịch cùng attach: 1 task, bên thua ghi 1 event error, không ném lỗi."""
        definition_id, (pid,) = self.seed()
        c2 = self.new_env('REPEATABLE READ')
        c2.cr.execute("SELECT count(*) FROM sla_task WHERE res_id=%s", (pid,))  # cố định snapshot
        self.assertEqual(c2.cr.fetchone()[0], 0)
        c1 = self.new_env()
        with self.at(T0):
            c1['sla.engine'].evaluate(c1['res.partner'].browse(pid), now=T0)
        c1.cr.commit()
        with self.at(T0):
            c2['sla.engine'].evaluate(c2['res.partner'].browse(pid), now=T0)  # không ném lỗi
        c2.cr.commit()
        self.assertEqual(self.fresh(
            "SELECT count(*) FROM sla_task WHERE sla_id=%s AND stage IN ('in_progress','paused')",
            (definition_id,))[0][0], 1)
        events = dict(self.fresh(
            "SELECT event, count(*) FROM sla_event WHERE definition_id=%s GROUP BY 1", (definition_id,)))
        self.assertEqual((events.get('attach'), events.get('error')), (1, 1))
        self.assertEqual(self.fresh("SELECT ref FROM res_partner WHERE id=%s", (pid,))[0][0], 'NEW')


class TestConcurrentProcessing(ConcurrentCase):

    def attached(self, count=1):
        definition_id, partner_ids = self.seed(count=count, escalation=75)
        env = self.new_env()
        with self.at(T0):
            env['sla.engine'].evaluate(env['res.partner'].browse(partner_ids), now=T0)
        env.cr.commit()
        self.count_actions()
        return definition_id, partner_ids

    def escalate_count(self, definition_id):
        return self.fresh("SELECT count(*) FROM sla_event WHERE definition_id=%s AND event='escalate'",
                          (definition_id,))[0][0]

    def test_esc_009_locked_task_skipped(self):
        """TC-ESC-009: C2 bỏ qua task đang bị C1 khóa; không bắn hai lần."""
        definition_id, (pid,) = self.attached()
        now = T0 + timedelta(hours=3)
        c1 = self.new_env()
        task = c1['sla.task'].search([('sla_id', '=', definition_id)])
        with self.at(now):
            c1['sla.processor']._process_task(task, now)  # chạy action + ghi event, CHƯA commit (giữ khóa)
        self.assertEqual(self.calls, [pid])
        c2 = self.new_env()
        self.due_env_processor(c2, now)  # SKIP LOCKED
        c2.cr.commit()
        self.assertEqual(self.calls, [pid])
        c1.cr.commit()
        self.due_env_processor(self.new_env(), now)
        self.assertEqual(self.calls, [pid])
        self.assertEqual(self.escalate_count(definition_id), 1)

    def test_esc_059_stop_other_task_not_blocked(self):
        """TC-ESC-059: stop T2 khi C1 giữ khóa T1 (action chậm): lần lưu không phải chờ."""
        definition_id, (p1, p2) = self.attached(2)
        now = T0 + timedelta(hours=3)
        tasks = {row[1]: row[0] for row in self.fresh(
            "SELECT id, res_id FROM sla_task WHERE sla_id=%s", (definition_id,))}
        c1 = self.new_env()
        t1 = c1['sla.task'].browse(tasks[p1])
        with self.at(now):
            c1['sla.processor']._process_task(t1, now)  # giữ khóa dòng T1
        c3 = self.new_env()
        c3.cr.execute("SELECT id FROM sla_task WHERE id=%s FOR UPDATE NOWAIT", (tasks[p2],))  # T2 chưa bị khóa
        c3.cr.rollback()
        c3.cr.execute("SET LOCAL lock_timeout = '5s'")
        with self.assertRaises(psycopg2.errors.LockNotAvailable):
            c3.cr.execute("SELECT id FROM sla_task WHERE id=%s FOR UPDATE NOWAIT", (tasks[p1],))
        c3.cr.rollback()
        c2 = self.new_env()
        started = time.monotonic()
        with self.at(now):
            c2['res.partner'].browse(p2).write({'ref': 'DONE'})
        c2.cr.commit()
        self.assertLess(time.monotonic() - started, 5.0)
        c1.cr.commit()
        stage = self.fresh("SELECT stage FROM sla_task WHERE id=%s", (tasks[p2],))[0][0]
        self.assertEqual(stage, 'achieved')
        self.assertEqual(self.calls, [p1])
        self.assertEqual(self.escalate_count(definition_id), 1)

    def test_err_027_029_task_stopped_before_lock(self):
        """TC-ERR-027/029: task bị stop (commit) giữa lúc chọn và khóa thì không bắn mốc; task còn lại bắn đúng 1 lần."""
        definition_id, (p1, p2) = self.attached(2)
        now = T0 + timedelta(hours=3)
        env = self.new_env()
        original = type(env['sla.task']).try_lock_for_update
        state = {'done': False}

        def lock_after_competitor_stops(records, *args, **kwargs):
            if not state['done']:
                state['done'] = True
                other = self.new_env()
                with self.at(now):
                    other['res.partner'].browse(p1).write({'ref': 'DONE'})
                other.cr.commit()
            return original(records, *args, **kwargs)

        with patch.object(type(env['sla.task']), 'try_lock_for_update', lock_after_competitor_stops):
            try:
                self.due_env_processor(env, now)
                env.cr.commit()
            except psycopg2.errors.SerializationFailure:
                # Giao dịch cron (REPEATABLE READ) thấy dòng đã bị sửa: hủy, cron chạy lại (kết quả "lỗi" của 060).
                env.cr.rollback()
        self.due_env_processor(self.new_env(), now)
        self.due_env_processor(self.new_env(), now)
        self.assertEqual(sorted(self.calls), [p2])
        stage = dict(self.fresh("SELECT res_id, stage FROM sla_task WHERE sla_id=%s", (definition_id,)))
        self.assertEqual((stage[p1], stage[p2]), ('achieved', 'in_progress'))
        self.assertEqual(self.escalate_count(definition_id), 1)

    def test_err_026_stop_conflicts_with_committed_processing(self):
        """TC-ERR-026: stop trong giao dịch cũ xung đột với xử lý nền đã commit: không lưu dở dang; giao dịch mới thành công."""
        definition_id, (pid,) = self.attached()
        now = T0 + timedelta(hours=3)
        c2 = self.new_env('REPEATABLE READ')
        c2.cr.execute("SELECT stage FROM sla_task WHERE sla_id=%s", (definition_id,))  # snapshot
        c1 = self.new_env()
        self.due_env_processor(c1, now)
        c1.cr.commit()
        try:
            with self.at(now):
                c2['res.partner'].browse(pid).write({'ref': 'DONE'})
            c2.cr.commit()
        except psycopg2.Error:
            c2.cr.rollback()
        else:
            c2.cr.rollback()
        stage, completes = self.fresh(
            "SELECT t.stage, (SELECT count(*) FROM sla_event e WHERE e.task_id=t.id AND e.event='complete') "
            "FROM sla_task t WHERE t.sla_id=%s", (definition_id,))[0]
        self.assertIn((stage, completes), (('in_progress', 0), ('achieved', 1)))  # nhất quán, không dở dang
        retry = self.new_env()  # giao dịch mới, lặp lại đúng thao tác
        with self.at(now):
            retry['res.partner'].browse(pid).write({'ref': 'DONE'})
        retry.cr.commit()
        stage, completes = self.fresh(
            "SELECT t.stage, (SELECT count(*) FROM sla_event e WHERE e.task_id=t.id AND e.event='complete') "
            "FROM sla_task t WHERE t.sla_id=%s", (definition_id,))[0]
        self.assertEqual((stage, completes, self.escalate_count(definition_id)), ('achieved', 1, 1))
        self.assertEqual(self.fresh("SELECT ref FROM res_partner WHERE id=%s", (pid,))[0][0], 'DONE')
