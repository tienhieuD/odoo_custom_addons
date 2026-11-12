# -*- coding: utf-8 -*-
"""TG-26: due soon theo definition, khoá model, audit, smart button, list definition,
tab Escalation, nút Open Source Record, list task, widget light mode.

Refs: docs/plan-improvement-sla-01-review.md §6.6, §6.7, §6.10..§6.15
"""
from lxml import etree

from odoo.exceptions import UserError, ValidationError
from odoo.tests import HttpCase, tagged
from odoo.tools import file_open

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')


class Tg26Case(SlaCase):

    def arch(self, model, view_type):
        return etree.fromstring(self.env[model].get_view(view_type=view_type)['arch'])

    def raw_task(self, definition, partner=None, stage='in_progress', **extra):
        partner = partner or self.Partner.create({'name': "TG26 P"})
        vals = {
            'sla_id': definition.id, 'res_model': 'res.partner', 'res_id': partner.id,
            'stage': stage, 'start_time': T0, 'target_duration': 4,
            'planned_end_time': T0 + hours(4)}
        if stage == 'in_progress':
            vals['running_since'] = T0
        elif stage == 'paused':
            vals['pause_time'] = T0
        else:
            vals['end_time'] = T0 + hours(1)
        vals.update(extra)
        return self.Task.sudo().create(vals)


@tagged(*TAGS, 'tg_26')
class TestDueSoonPerDefinition(Tg26Case):

    def setUp(self):
        super().setUp()
        self.now = T0 + hours(1)
        self.env['ir.config_parameter'].sudo().set_param('dwo_sla_core.due_soon_hours', '4')
        self.d_default = self.make_definition(name="Default")
        self.d_short = self.make_definition(name="Short", due_soon_hours=1)
        self.d_long = self.make_definition(name="Long", due_soon_hours=10)
        end = self.now + hours(3)  # trong 3 giờ tới
        self.t_default = self.raw_task(self.d_default, planned_end_time=end)
        self.t_short = self.raw_task(self.d_short, planned_end_time=end)
        self.t_long = self.raw_task(self.d_long, planned_end_time=end)
        self.all = self.t_default | self.t_short | self.t_long

    def test_compute_uses_definition_then_settings(self):
        with self.at(self.now):
            self.all.invalidate_recordset(['is_due_soon'])
            self.assertEqual(
                (self.t_default.is_due_soon, self.t_short.is_due_soon, self.t_long.is_due_soon),
                (True, False, True))

    def test_settings_change_applies_to_empty_only(self):
        self.env['ir.config_parameter'].sudo().set_param('dwo_sla_core.due_soon_hours', '2')
        with self.at(self.now):
            self.all.invalidate_recordset(['is_due_soon'])
            self.assertEqual(
                (self.t_default.is_due_soon, self.t_short.is_due_soon, self.t_long.is_due_soon),
                (False, False, True))

    def test_search_operators(self):
        base = [('id', 'in', self.all.ids)]
        with self.at(self.now):
            for domain, expected in (
                ([('is_due_soon', '=', True)], self.t_default | self.t_long),
                ([('is_due_soon', '!=', False)], self.t_default | self.t_long),
                ([('is_due_soon', 'in', [True])], self.t_default | self.t_long),
                ([('is_due_soon', '=', False)], self.t_short),
                ([('is_due_soon', '!=', True)], self.t_short),
                ([('is_due_soon', 'in', [False])], self.t_short),
                ([('is_due_soon', 'not in', [True])], self.t_short),
                ([('is_due_soon', 'not in', [False])], self.t_default | self.t_long),
            ):
                self.assertEqual(self.Task.search(base + domain), expected, domain)

    def test_search_excludes_breached_and_paused(self):
        paused = self.raw_task(self.d_long, stage='paused', planned_end_time=self.now + hours(1))
        breached = self.raw_task(self.d_long, has_breached=True, planned_end_time=self.now + hours(1))
        with self.at(self.now):
            found = self.Task.search([('id', 'in', (paused | breached).ids), ('is_due_soon', '=', True)])
            self.assertFalse(found)
            not_found = self.Task.search([('id', 'in', (paused | breached).ids), ('is_due_soon', '=', False)])
            self.assertEqual(not_found, paused | breached)

    def test_negative_value_rejected(self):
        with self.assertRaises(Exception):  # noqa: B017 -- CHECK constraint của DB
            with self.env.cr.savepoint():
                self.d_default.due_soon_hours = -1


@tagged(*TAGS, 'tg_26')
class TestModelLock(Tg26Case):

    def test_model_change_blocked_with_tasks(self):
        d = self.make_definition()
        self.raw_task(d)
        with self.assertRaises(ValidationError):
            d.model_id = self.env['ir.model']._get('res.partner.category')
        self.assertEqual(d.model_name, 'res.partner')

    def test_same_model_write_allowed_with_tasks(self):
        d = self.make_definition()
        self.raw_task(d)
        d.write({'model_id': self.partner_model.id, 'duration': 6})
        self.assertEqual(d.duration, 6)

    def test_model_change_allowed_without_tasks(self):
        d = self.make_definition(start_domain="[('id', '!=', 0)]")
        d.write({'model_id': self.env['ir.model']._get('res.partner.category').id,
                 'start_domain': "[('id', '!=', 0)]", 'pause_domain': '[]',
                 'resume_domain': '[]', 'stop_domain': '[]', 'cancel_domain': '[]'})
        self.assertEqual(d.model_name, 'res.partner.category')


@tagged(*TAGS, 'tg_26')
class TestAuditTrail(Tg26Case):

    def test_tracked_change_posts_message(self):
        d = self.make_definition(duration=4)
        self.env.cr.precommit.run()  # bản ghi vừa tạo trong cùng giao dịch thì không được theo dõi
        d.with_context(tracking_disable=False, mail_notrack=False).duration = 8
        self.env.cr.precommit.run()  # tracking ghi ở precommit
        tracking = d.message_ids.tracking_value_ids
        self.assertIn('duration', tracking.field_id.mapped('name'))

    def test_condition_change_is_tracked(self):
        d = self.make_definition()
        self.env.cr.precommit.run()
        d.with_context(tracking_disable=False, mail_notrack=False).stop_domain = (
            "[('ref', '=', 'CLOSED')]")
        self.env.cr.precommit.run()
        self.assertIn('stop_domain', d.message_ids.tracking_value_ids.field_id.mapped('name'))

    def test_form_has_chatter(self):
        self.assertTrue(self.arch('sla.definition', 'form').xpath('//chatter'))


@tagged(*TAGS, 'tg_26')
class TestSmartButton(Tg26Case):

    def test_running_task_count_counts_in_progress_and_paused(self):
        d = self.make_definition()
        other = self.make_definition(name="Other")
        self.raw_task(d)
        self.raw_task(d, stage='paused')
        self.raw_task(d, stage='achieved')
        self.raw_task(other)
        (d | other).invalidate_recordset(['running_task_count'])
        self.assertEqual((d.running_task_count, other.running_task_count), (2, 1))

    def test_count_zero_without_tasks(self):
        self.assertEqual(self.make_definition().running_task_count, 0)

    def test_action_opens_all_tasks_of_definition(self):
        d = self.make_definition()
        self.raw_task(d)
        self.raw_task(d, stage='achieved')
        self.raw_task(self.make_definition(name="Other"))
        action = d.action_view_tasks()
        self.assertEqual(action['res_model'], 'sla.task')
        self.assertEqual(len(self.Task.search(action['domain'])), 2)
        self.assertEqual(action['context'], {})

    def test_form_arch_button_and_js_class(self):
        root = self.arch('sla.definition', 'form')
        self.assertEqual(root.get('js_class'), 'sla_definition_form')
        button = root.xpath("//div[@name='button_box']//button[@name='action_view_tasks']")
        self.assertEqual(len(button), 1)
        self.assertTrue(root.xpath("//field[@name='running_task_count']"))


@tagged(*TAGS, 'tg_26')
class TestDefinitionListView(Tg26Case):

    def test_list_arch(self):
        root = self.arch('sla.definition', 'list')
        self.assertEqual(root.get('decoration-muted'), 'not active')
        self.assertEqual(
            [b.get('name') for b in root.xpath('//button')], ['action_enable', 'action_disable'])
        for button in root.xpath('//button'):
            self.assertTrue(button.get('confirm'))
        default_cols = [
            f.get('name') for f in root.xpath('//field') if not f.get('optional')
            and not f.get('column_invisible') and f.get('widget') != 'handle']
        self.assertEqual(default_cols, [
            'name', 'model_id', 'type', 'duration', 'schedule_source', 'calendar_tz_override'])
        self.assertNotIn('running_task_count', [f.get('name') for f in root.xpath('//field')])

    def test_action_shows_inactive_without_grouping(self):
        action = self.env.ref('dwo_sla_core.action_sla_definition')
        self.assertNotIn('search_default_group_model', action.context or '')
        draft = self.make_definition(active=False)
        result = self.Definition.search(eval(action.domain))  # noqa: S307 -- domain literal của action
        self.assertIn(draft, result)


@tagged(*TAGS, 'tg_26')
class TestTaskEscalationHistory(Tg26Case):

    def test_only_escalation_events(self):
        d = self.make_definition()
        task = self.raw_task(d)
        for event in ('escalate', 'escalate_failed', 'pause', 'error'):
            self.Event.sudo().create({'task_id': task.id, 'event': event, 'event_dt': T0})
        self.assertEqual(
            sorted(task.escalation_event_ids.mapped('event')), ['escalate', 'escalate_failed'])
        self.assertEqual(len(task.event_ids), 4)

    def test_newest_first(self):
        task = self.raw_task(self.make_definition())
        old = self.Event.sudo().create({'task_id': task.id, 'event': 'escalate', 'event_dt': T0})
        new = self.Event.sudo().create({'task_id': task.id, 'event': 'escalate', 'event_dt': T0 + hours(2)})
        self.assertEqual(task.escalation_event_ids, new | old)

    def test_form_arch_lists_events(self):
        root = self.arch('sla.task', 'form')
        cols = root.xpath("//page[@name='escalation']//field[@name='escalation_event_ids']//field/@name")
        self.assertEqual(cols, ['event_dt', 'event', 'note'])


@tagged(*TAGS, 'tg_26')
class TestOpenSourceRecord(Tg26Case):

    def test_opens_source_record(self):
        p = self.Partner.create({'name': "Src"})
        action = self.raw_task(self.make_definition(), partner=p).action_open_source_record()
        self.assertEqual(
            (action['type'], action['res_model'], action['res_id'], action['view_mode'], action['target']),
            ('ir.actions.act_window', 'res.partner', p.id, 'form', 'current'))

    def test_missing_record_friendly_error(self):
        p = self.Partner.create({'name': "Gone"})
        task = self.raw_task(self.make_definition(), partner=p)
        p.unlink()
        with self.assertRaisesRegex(UserError, "no longer exists"):
            task.action_open_source_record()

    def test_unknown_model_friendly_error(self):
        task = self.raw_task(self.make_definition())
        task.sudo().res_model = 'x.not.installed'
        with self.assertRaisesRegex(UserError, "no longer exists"):
            task.action_open_source_record()

    def test_button_in_form_header_always_visible(self):
        root = etree.fromstring(self.env['sla.task'].get_view(view_type='form')['arch'])
        button = root.xpath("//header/button[@name='action_open_source_record']")
        self.assertEqual(len(button), 1)
        self.assertIsNone(button[0].get('invisible'))
        self.assertFalse(root.xpath("//list//button[@name='action_open_source_record']"))


@tagged(*TAGS, 'tg_26')
class TestTaskListView(Tg26Case):

    def test_default_columns_and_progressbar(self):
        root = self.arch('sla.task', 'list')
        self.assertEqual(root.get('decoration-danger'), 'has_breached')
        default_cols = [
            f.get('name') for f in root.xpath('//field') if f.get('optional') != 'hide']
        self.assertEqual(default_cols, [
            'sla_id', 'target_duration', 'schedule_id', 'stage', 'start_time',
            'planned_end_time', 'business_duration_live', 'duration_live',
            'business_percent_used'])
        bar = root.xpath("//field[@name='business_percent_used']")[0]
        self.assertEqual(bar.get('widget'), 'progressbar')
        self.assertIn('overflow_class', bar.get('options'))
        for name in ('display_name', 'res_model', 'res_id'):
            self.assertEqual(root.xpath("//field[@name='%s']" % name)[0].get('optional'), 'hide')


@tagged(*TAGS, 'tg_26')
class TestLightModeOnly(Tg26Case):

    def test_scss_has_no_dark_block(self):
        with file_open('dwo_sla_core/static/src/sla_progress/sla_progress_widget.scss') as scss:
            self.assertNotIn('prefers-color-scheme', scss.read())


@tagged(*TAGS, 'tg_26')
class TestDefinitionFormTour(HttpCase):
    """Mở form definition thật trên trình duyệt: bundle JS không vỡ, confirm khi lưu hoạt động."""

    def test_confirm_save_with_running_tasks(self):
        env = self.env
        definition = env['sla.definition'].create({
            'active': True, 'name': "Tour SLA", 'model_id': env['ir.model']._get('res.partner').id,
            'duration': 4, 'start_domain': "[('ref', '=', 'NEVER')]", 'stop_domain': "[('ref', '=', 'DONE')]"})
        partner = env['res.partner'].create({'name': "Tour P"})
        env['sla.task'].sudo().create({
            'sla_id': definition.id, 'res_model': 'res.partner', 'res_id': partner.id,
            'stage': 'in_progress', 'start_time': T0, 'running_since': T0,
            'target_duration': 4, 'planned_end_time': T0 + hours(4)})
        self.start_tour(
            '/odoo/action-dwo_sla_core.action_sla_definition/%s' % definition.id,
            'dwo_sla_definition_confirm_save', login='admin')
