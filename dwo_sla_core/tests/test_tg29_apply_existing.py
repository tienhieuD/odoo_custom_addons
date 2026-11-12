# -*- coding: utf-8 -*-
"""TG-29: "Apply to Existing Records": wizard, job theo lô, cron, huỷ, dọn, backfill escalation.

Refs: docs/plan-improvement-sla-01.md mục 16, docs/plan-improvement-sla-01-review.md §6.16
"""
from datetime import timedelta

from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')


@tagged(*TAGS, 'tg_29')
class TestApplyExisting(SlaCase):

    def setUp(self):
        super().setUp()
        self.no_commit_progress()
        self.manager = self.make_user('tg29_manager', 'manager')
        self.viewer = self.make_user('tg29_viewer', 'user')
        self.Job = self.env['sla.apply.job']
        self.Wizard = self.env['sla.apply.wizard']

    def existing_records(self, count=10, definition_kwargs=None):
        """Definition tắt, `count` record khớp Start tạo TRƯỚC khi bật, rồi bật."""
        d = self.make_definition(active=False, **(definition_kwargs or {}))
        partners = self.Partner
        for _i in range(count):
            partners |= self.make_partner('NEW')
        self.assertFalse(self.tasks(definition=d))
        d.action_enable()
        self.assertFalse(self.tasks(definition=d))  # bật không tự quét record cũ
        return d, partners

    def apply(self, definition, filter_domain=None, now=T0):
        vals = {'definition_id': definition.id}
        if filter_domain is not None:
            vals['filter_domain'] = filter_domain
        wizard = self.Wizard.with_user(self.manager).create(vals)
        with self.at(now):
            action = wizard.action_apply()
        job = self.Job.sudo().search([('definition_id', '=', definition.id)], order='id desc', limit=1)
        return job, action

    def test_all_matching_records_get_task_and_rerun_has_no_duplicates(self):
        d, partners = self.existing_records(10)
        wizard = self.Wizard.with_user(self.manager).create({'definition_id': d.id})
        self.assertEqual(wizard.match_count, 10)
        job, action = self.apply(d)
        self.assertEqual((job.state, job.total, job.processed, job.attached, job.error_count),
                         ('done', 10, 10, 10, 0))
        self.assertEqual(self.tasks(definition=d).mapped('res_id'), partners.sorted('id').ids)
        self.assertEqual(action['tag'], 'display_notification')
        self.assertEqual(action['params']['next'], {'type': 'ir.actions.act_window_close'})
        job2, _action = self.apply(d)
        self.assertNotEqual(job2, job)
        self.assertEqual((job2.state, job2.processed, job2.attached), ('done', 10, 0))
        self.assertEqual(len(self.tasks(definition=d)), 10)
        self.assertEqual(len(self.Job.sudo().search([('definition_id', '=', d.id)])), 2)

    def test_filter_domain_narrows_set(self):
        d, partners = self.existing_records(10)
        subset = partners.sorted('id')[:3]
        job, _action = self.apply(d, "[('id', 'in', %s)]" % subset.ids)
        self.assertEqual((job.total, job.processed, job.attached), (3, 3, 3))
        self.assertEqual(self.tasks(definition=d).mapped('res_id'), subset.ids)

    def test_filter_cannot_widen_start_condition(self):
        d, partners = self.existing_records(2)
        other = self.make_partner('DONE')  # không khớp Start
        job, _action = self.apply(d, "[('id', 'in', %s)]" % (partners | other).ids)
        self.assertEqual((job.processed, job.attached), (2, 2))
        self.assertFalse(self.tasks(other, d))

    def test_unconfigured_start_loads_nothing(self):
        d = self.make_definition(start_domain='[]')
        self.make_partner('NEW')
        job, _action = self.apply(d)
        self.assertEqual((job.state, job.total, job.processed, job.attached), ('done', 0, 0, 0))
        self.assertFalse(self.tasks(definition=d))

    def test_inactive_definition_rejected(self):
        d = self.make_definition(active=False)
        wizard = self.Wizard.with_user(self.manager).create({'definition_id': d.id})
        with self.assertRaises(UserError):
            wizard.action_apply()

    def test_batching_first_batch_now_rest_by_cron(self):
        self.env['ir.config_parameter'].sudo().set_str('dwo_sla_core.batch_size', '3')
        d, partners = self.existing_records(10)
        ids = partners.sorted('id').ids
        job, _action = self.apply(d)
        self.assertEqual((job.state, job.processed, job.attached, job.last_id), ('running', 3, 3, ids[2]))
        self.assertTrue(self.env['ir.cron.trigger'].sudo().search_count(
            [('cron_id', '=', self.env.ref('dwo_sla_core.ir_cron_sla_apply').id)]))
        # Còn job chạy: không cho tạo job mới.
        wizard = self.Wizard.with_user(self.manager).create({'definition_id': d.id})
        with self.assertRaises(UserError):
            wizard.action_apply()
        with self.at(T0):
            self.Job._cron_run()
        self.assertEqual((job.state, job.processed, job.attached, job.last_id), ('done', 10, 10, ids[-1]))
        self.assertEqual(self.tasks(definition=d).mapped('res_id'), ids)
        self.assertEqual(len(self.tasks(definition=d)), 10)

    def test_queued_job_also_blocks_new_job(self):
        d, _partners = self.existing_records(1)
        self.Job.sudo().create({'definition_id': d.id, 'state': 'queued'})
        wizard = self.Wizard.with_user(self.manager).create({'definition_id': d.id})
        with self.assertRaises(UserError):
            wizard.action_apply()

    def test_cancel_stops_job(self):
        self.env['ir.config_parameter'].sudo().set_str('dwo_sla_core.batch_size', '3')
        d, _partners = self.existing_records(10)
        job, _action = self.apply(d)
        self.assertEqual(job.state, 'running')
        job.with_user(self.manager).action_cancel()
        self.assertEqual(job.state, 'cancelled')
        self.assertTrue(job.end_time)
        with self.at(T0):
            self.Job._cron_run()
        self.assertEqual((job.state, job.processed), ('cancelled', 3))
        self.assertEqual(len(self.tasks(definition=d)), 3)
        # Hết job chạy thì tạo job mới được.
        job2, _action = self.apply(d)
        self.assertNotEqual(job2, job)

    def test_failed_batch_marks_job_failed(self):
        d, _partners = self.existing_records(2)
        job = self.Job.sudo().create({'definition_id': d.id, 'filter_domain': "[('bad_field', '=', 1)]"})
        self.Job._cron_run()
        self.assertEqual(job.state, 'failed')
        self.assertTrue(job.note)

    def test_autovacuum_removes_old_finished_keeps_running(self):
        d = self.make_definition()
        now = T0
        old = now - timedelta(days=400)
        Job = self.Job.sudo()
        done_old = Job.create({'definition_id': d.id, 'state': 'done', 'end_time': old})
        cancelled_old = Job.create({'definition_id': d.id, 'state': 'cancelled', 'end_time': old})
        running_old = Job.create({'definition_id': d.id, 'state': 'running'})
        queued_old = Job.create({'definition_id': d.id, 'state': 'queued'})
        done_recent = Job.create({'definition_id': d.id, 'state': 'done', 'end_time': now - timedelta(days=1)})
        with self.at(now):
            self.Job._gc_old_jobs()
        self.assertFalse((done_old | cancelled_old).exists())
        self.assertEqual((running_old | queued_old | done_recent).exists(),
                         running_old | queued_old | done_recent)

    def test_backfill_retroactive_leaves_no_pending_passed_escalation(self):
        retro = self.make_x_field('x_retro_dt', 'datetime')
        d = self.make_definition(active=False, retroactive=True, start_field_id=retro.id)
        partner = self.Partner.create({
            'name': "Old", 'ref': 'NEW', 'x_retro_dt': T0 - hours(10)})  # 250% của 4 giờ
        esc_50 = self.make_escalation(d, 50)
        esc_100 = self.make_escalation(d, 100)
        esc_300 = self.make_escalation(d, 300)
        d.action_enable()
        job, _action = self.apply(d)
        self.assertEqual(job.attached, 1)
        task = self.task_of(partner, d)
        self.assertTrue(task.has_breached)
        self.assertEqual(task.done_escalation_ids, esc_50 | esc_100)
        self.assertNotIn(esc_300, task.done_escalation_ids)  # 250% chưa tới mốc 300%
        self.assertFalse(self.Processor._next_due_escalation(task, T0))
        self.assertGreater(task.next_due_at, T0)
        # Chạy xử lý nền: không bắn mốc đã vượt.
        self.Processor._process_task(task, T0)
        self.assertEqual(task.done_escalation_ids, esc_50 | esc_100)
        self.assertFalse(task.event_ids.filtered(lambda e: e.event in ('escalate', 'escalate_failed')))

    def test_security(self):
        d = self.make_definition()
        with self.assertRaises(AccessError):
            self.Wizard.with_user(self.viewer).create({'definition_id': d.id})
        job = self.Job.sudo().create({'definition_id': d.id})
        self.assertEqual(self.Job.with_user(self.manager).browse(job.id).state, 'queued')
        with self.assertRaises(AccessError):
            self.Job.with_user(self.viewer).browse(job.id).state
        with self.assertRaises(AccessError):
            self.Job.with_user(self.manager).browse(job.id).write({'state': 'done'})
