# -*- coding: utf-8 -*-
"""TG-30: chip trạng thái SLA trên form (RPC tóm tắt, session_info, tour).

Refs: docs/plan-improvement-sla-01-review.md §6.9
"""
import json
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests import HttpCase, new_test_user, tagged

from .common import SlaCase, SlaHttpCase

TAGS = ('post_install', '-at_install', 'dwo_sla_core')


class Tg30Case(SlaCase):

    def raw_task(self, definition, partner, stage='in_progress', **extra):
        """Task dựng thẳng (không qua engine) với mốc tính theo đồng hồ thật."""
        now = fields.Datetime.now()
        vals = {
            'sla_id': definition.id, 'res_model': 'res.partner', 'res_id': partner.id,
            'stage': stage, 'start_time': now - timedelta(hours=1),
            'target_duration': 4, 'planned_end_time': now + timedelta(hours=10)}
        if stage == 'in_progress':
            vals['running_since'] = now - timedelta(minutes=10)
        elif stage == 'paused':
            vals['pause_time'] = now
        else:
            vals['end_time'] = now
        vals.update(extra)
        return self.Task.sudo().create(vals)

    def summary(self, partner):
        return self.Task.get_record_sla_summary('res.partner', partner.id)


@tagged(*TAGS, 'tg_30')
class TestRecordSlaSummary(Tg30Case):

    def setUp(self):
        super().setUp()
        self.definition = self.make_definition(name="Chip SLA")
        self.partner = self.Partner.create({'name': "Chip P"})

    def test_no_task_is_none(self):
        self.assertEqual(self.summary(self.partner)['state'], None)

    def test_missing_id_is_none(self):
        self.assertEqual(self.Task.get_record_sla_summary('res.partner', False), {'state': None})

    def test_running(self):
        self.raw_task(self.definition, self.partner)
        data = self.summary(self.partner)
        self.assertEqual(data['state'], 'running')
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['late_count'], 0)
        self.assertEqual(len(data['lines']), 1)

    def test_due_soon(self):
        now = fields.Datetime.now()
        self.raw_task(self.definition, self.partner, planned_end_time=now + timedelta(hours=1))
        self.assertEqual(self.summary(self.partner)['state'], 'due_soon')

    def test_paused(self):
        self.raw_task(self.definition, self.partner, stage='paused', business_duration=1)
        data = self.summary(self.partner)
        self.assertEqual(data['state'], 'paused')
        self.assertEqual(data['percent'], 25)

    def test_breached_running_percent_capped(self):
        now = fields.Datetime.now()
        self.raw_task(self.definition, self.partner, has_breached=True, business_duration=10,
                      start_time=now - timedelta(hours=6), planned_end_time=now - timedelta(hours=2))
        data = self.summary(self.partner)
        self.assertEqual(data['state'], 'breached')
        self.assertEqual(data['late_count'], 1)
        self.assertEqual(data['percent'], 100)
        self.assertTrue(all(line['percent'] <= 100 for line in data['lines']))

    def test_met(self):
        self.raw_task(self.definition, self.partner, stage='achieved')
        data = self.summary(self.partner)
        self.assertEqual((data['state'], data['count'], data['late_count']), ('met', 1, 0))

    def test_missed(self):
        self.raw_task(self.definition, self.partner, stage='breached', has_breached=True)
        data = self.summary(self.partner)
        self.assertEqual((data['state'], data['late_count']), ('missed', 1))

    def test_cancelled_only_is_none(self):
        self.raw_task(self.definition, self.partner, stage='cancelled')
        self.assertEqual(self.summary(self.partner)['state'], None)

    def test_multiple_tasks_pick_most_urgent(self):
        other = self.make_definition(name="Chip SLA 2")
        self.raw_task(self.definition, self.partner, business_duration=3)
        now = fields.Datetime.now()
        self.raw_task(other, self.partner, has_breached=True,
                      start_time=now - timedelta(hours=6), planned_end_time=now - timedelta(hours=1))
        data = self.summary(self.partner)
        self.assertEqual(data['state'], 'breached')
        self.assertEqual((data['count'], data['late_count']), (2, 1))

    def test_active_task_wins_over_done_ones(self):
        self.raw_task(self.definition, self.partner, stage='breached', has_breached=True)
        self.raw_task(self.definition, self.partner)
        self.assertEqual(self.summary(self.partner)['state'], 'running')

    def test_no_sudo_user_without_group_is_refused(self):
        self.raw_task(self.definition, self.partner)
        user = new_test_user(self.env, 'chip_nogroup', groups='base.group_user')
        with self.assertRaises(AccessError):
            self.Task.with_user(user).get_record_sla_summary('res.partner', self.partner.id)

    def test_sla_user_can_read(self):
        self.raw_task(self.definition, self.partner)
        user = new_test_user(self.env, 'chip_user', groups='base.group_user,dwo_sla_core.group_sla_user')
        data = self.Task.with_user(user).get_record_sla_summary('res.partner', self.partner.id)
        self.assertEqual(data['state'], 'running')


@tagged(*TAGS, 'tg_30')
class TestSessionInfo(SlaHttpCase):

    def setUp(self):
        super().setUp()
        self.env['sla.definition'].create({
            'active': True, 'name': "Session SLA", 'model_id': self.env['ir.model']._get('res.partner').id,
            'duration': 4, 'start_domain': "[('ref', '=', 'NEVER')]"})

    def session_models(self, login, password):
        self.authenticate(login, password)
        response = self.url_open(
            '/web/session/get_session_info', headers={'Content-Type': 'application/json'},
            data=json.dumps({'jsonrpc': '2.0', 'method': 'call', 'id': 1}))
        return response.json()['result']['dwo_sla_models']

    def test_flag_on_when_never_configured(self):
        """Chưa có bản ghi tham số = bật (không cần seed, -u không bật lại cờ đã tắt)."""
        self.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'dwo_sla_core.show_form_sla_status')]).unlink()
        self.assertTrue(self.env['res.config.settings']._sla_show_form_status())

    def test_setting_off_is_stored_explicitly(self):
        """Tắt qua Settings lưu chuỗi 'False' tường minh, không xoá bản ghi."""
        self.env['res.config.settings'].create({'sla_show_form_status': False}).execute()
        self.assertEqual(self.env['ir.config_parameter'].sudo().get_param(
            'dwo_sla_core.show_form_sla_status'), 'False')
        self.assertFalse(self.env['res.config.settings']._sla_show_form_status())

    def test_models_listed_for_sla_user(self):
        self.assertIn('res.partner', self.session_models('admin', 'admin'))

    def test_empty_when_setting_off(self):
        self.env['ir.config_parameter'].sudo().set_param('dwo_sla_core.show_form_sla_status', 'False')
        self.assertEqual(self.session_models('admin', 'admin'), [])

    def test_empty_without_sla_group(self):
        new_test_user(self.env, 'chip_plain', password='chip_plain', groups='base.group_user')
        self.assertEqual(self.session_models('chip_plain', 'chip_plain'), [])


@tagged(*TAGS, 'tg_30')
class TestFormStatusTour(SlaHttpCase):
    """Form thật trên trình duyệt: chip xuất hiện, bấm mở list task; model không có SLA thì không có chip."""

    def test_chip_on_partner_form(self):
        env = self.env
        definition = env['sla.definition'].create({
            'active': True, 'name': "Chip Tour SLA", 'model_id': env['ir.model']._get('res.partner').id,
            'duration': 4, 'start_domain': "[('ref', '=', 'NEVER')]"})
        partner = env['res.partner'].create({'name': "Chip Tour P"})
        now = fields.Datetime.now()
        env['sla.task'].sudo().create({
            'sla_id': definition.id, 'res_model': 'res.partner', 'res_id': partner.id,
            'stage': 'in_progress', 'start_time': now, 'running_since': now,
            'target_duration': 4, 'planned_end_time': now + timedelta(hours=4)})
        self.start_tour('/web#id=%s&model=res.partner&view_type=form' % partner.id, 'dwo_sla_form_status_chip', login='admin')

    def test_no_chip_without_sla(self):
        categ = self.env['res.partner.category'].create({'name': "No SLA categ"})
        self.start_tour(
            '/web#id=%s&model=res.partner.category&view_type=form' % categ.id, 'dwo_sla_form_status_chip_absent', login='admin')
