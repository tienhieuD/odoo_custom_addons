# -*- coding: utf-8 -*-
"""TG-25: mặc định tắt + Enable/Disable, `[]` = chưa cấu hình, timezone bắt buộc.

Refs: docs/plan-improvement-sla-01-review.md §6.0, §6.3, §6.5, §6.8
"""
from unittest.mock import patch

from odoo.tests import Form, tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')
MATCH_ALL = "[('id', '!=', 0)]"


@tagged(*TAGS, 'tg_25')
class TestEnableDisable(SlaCase):

    def test_new_definition_is_disabled_by_default(self):
        d = self.Definition.create({
            'name': "Draft", 'model_id': self.partner_model.id, 'duration': 4})
        self.assertFalse(d.active)
        self.assertEqual(d.start_domain, '[]')

    def test_model_name_related_stored(self):
        """model_name có ngay khi tạo và đổi theo model_id, không cần truyền tay."""
        d = self.make_definition()
        self.assertEqual(d.model_name, 'res.partner')
        d.model_id = self.env['ir.model']._get('res.partner.category')
        self.assertEqual(d.model_name, 'res.partner.category')

    def test_enable_disable_toggle_and_reload(self):
        d = self.make_definition(active=False)
        res = d.action_enable()
        self.assertTrue(d.active)
        self.assertEqual(res['tag'], 'soft_reload')
        res = d.action_disable()
        self.assertFalse(d.active)
        self.assertEqual(res['tag'], 'soft_reload')

    def test_enable_without_start_warns_but_enables(self):
        d = self.make_definition(active=False, start_domain='[]')
        res = d.action_enable()
        self.assertTrue(d.active)
        self.assertEqual(res['tag'], 'display_notification')
        self.assertEqual(res['params']['type'], 'warning')
        self.assertEqual(res['params']['next']['tag'], 'soft_reload')

    def test_enabled_attaches_disabled_does_not(self):
        d = self.make_definition(active=False)
        p = self.make_partner('NEW')
        self.assertFalse(self.tasks(p, d))
        d.action_enable()
        self.write(p, {'ref': 'WORK'}, T0 + hours(1))
        self.assertEqual(len(self.tasks(p, d)), 1)


@tagged(*TAGS, 'tg_25')
class TestHotPath(SlaCase):

    def test_hook_models_disabled_with_running_task(self):
        """Định nghĩa tắt còn task đang chạy vẫn được patch; hết task thì không."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        d.active = False
        self.assertIn('res.partner', self.Definition._get_hook_models())
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        self.assertEqual(self.task_of(p, d).stage, 'achieved')
        self.assertNotIn('res.partner', self.Definition._get_hook_models())

    def test_disabled_without_running_task_skips_condition_matching(self):
        d = self.make_definition(active=False)
        p = self.make_partner('NEW')
        with patch.object(type(self.Engine), '_match_sets', autospec=True) as match:
            self.evaluate(p, T0)
        match.assert_not_called()
        self.assertFalse(self.tasks(p, d))

    def test_disabled_with_running_task_still_evaluated(self):
        d = self.make_definition()
        p = self.make_partner('NEW')
        d.active = False
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        self.assertEqual(self.task_of(p, d).stage, 'achieved')


@tagged(*TAGS, 'tg_25')
class TestEmptyListNotConfigured(SlaCase):

    def test_get_domain_empty_list_is_none(self):
        d = self.make_definition(start_domain='[]')
        self.assertIsNone(d._get_domain('start'))
        self.assertEqual(d._get_domain('stop'), [('ref', '=', 'DONE')])

    def test_start_empty_list_never_attaches(self):
        d = self.make_definition(start_domain='[]')
        p = self.make_partner('NEW')
        self.assertFalse(self.tasks(p, d))

    def test_start_match_all_attaches(self):
        d = self.make_definition(start_domain=MATCH_ALL)
        self.assertEqual(len(self.tasks(self.make_partner(False), d)), 1)

    def test_stop_empty_list_never_completes(self):
        d = self.make_definition(stop_domain='[]', start_domain=MATCH_ALL)
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'in_progress')

    def test_new_definition_has_no_star_watch(self):
        """Mọi domain mặc định `[]` thì hook không đặt '*' (không chạy engine mỗi lần write)."""
        self.Definition.create({
            'name': "Draft", 'model_id': self.partner_model.id, 'duration': 4})
        self.assertNotIn('*', self.Definition._get_watched_field_names('res.partner'))

    def test_reset_condition_without_fields_watches_all(self):
        self.make_definition(reset_domain="[('ref', '=', 'RESET')]")
        self.assertIn('*', self.Definition._get_watched_field_names('res.partner'))


@tagged(*TAGS, 'tg_25')
class TestTimezoneRequired(SlaCase):

    def test_create_fills_user_tz_or_utc(self):
        d = self.make_definition()
        self.assertEqual(d.calendar_tz_override, self.env.user.tz or 'UTC')

    def test_create_fills_fixed_calendar_tz(self):
        cal = self.make_calendar(tz='Asia/Tokyo')
        d = self.make_definition(schedule_source='definition', schedule_id=cal.id)
        self.assertEqual(d.calendar_tz_override, 'Asia/Tokyo')

    def test_create_keeps_explicit_tz(self):
        d = self.make_definition(calendar_tz_override='Europe/Paris')
        self.assertEqual(d.calendar_tz_override, 'Europe/Paris')

    def test_onchange_new_record_takes_calendar_tz(self):
        """Bản ghi chưa lưu: luôn lấy tz calendar, kể cả khi ô đã có default."""
        cal = self.make_calendar(tz='Asia/Tokyo')
        d = self.Definition.new({
            'schedule_source': 'definition', 'schedule_id': cal.id,
            'calendar_tz_override': 'UTC'})
        d._onchange_schedule_suggest_tz()
        self.assertEqual(d.calendar_tz_override, 'Asia/Tokyo')

    def test_onchange_saved_record_fills_only_when_empty(self):
        cal = self.make_calendar(tz='Asia/Tokyo')
        d = self.make_definition(
            schedule_source='definition', schedule_id=cal.id,
            calendar_tz_override='UTC')
        d._onchange_schedule_suggest_tz()
        self.assertEqual(d.calendar_tz_override, 'UTC')
        d.calendar_tz_override = False
        d._onchange_schedule_suggest_tz()
        self.assertEqual(d.calendar_tz_override, 'Asia/Tokyo')

    def test_onchange_ignores_non_definition_source(self):
        cal = self.make_calendar(tz='Asia/Tokyo')
        d = self.Definition.new({'schedule_source': 'none', 'schedule_id': cal.id})
        d._onchange_schedule_suggest_tz()
        self.assertNotEqual(d.calendar_tz_override, 'Asia/Tokyo')

    def test_form_new_has_default_tz_and_follows_calendar(self):
        """Form mới mở ra đã có tz (default); chọn nguồn definition + calendar thì = tz calendar."""
        cal = self.make_calendar(tz='Asia/Tokyo')
        form = Form(self.Definition)
        self.assertEqual(form.calendar_tz_override, self.env.user.tz or 'UTC')
        form.name = "Form TZ"
        form.model_id = self.partner_model
        form.schedule_source = 'definition'
        form.schedule_id = cal
        self.assertEqual(form.calendar_tz_override, 'Asia/Tokyo')
        self.assertEqual(form.save().calendar_tz_override, 'Asia/Tokyo')

    def test_tz_variant_copies_global_leaves(self):
        cal = self.make_calendar()
        self.env['resource.calendar.leaves'].create({
            'name': "Holiday", 'calendar_id': cal.id,
            'date_from': '2026-03-03 00:00:00', 'date_to': '2026-03-03 23:59:59'})
        variant = self.env['resource.calendar']._sla_get_tz_variant(cal, 'UTC')
        self.assertEqual(variant.global_leave_ids.mapped('name'), ["Holiday"])
        self.assertEqual(variant.global_leave_ids.date_from, cal.global_leave_ids.date_from)

    def test_changing_definition_tz_keeps_running_task_deadline(self):
        """Snapshot: task đang chạy trỏ vào calendar đã resolve nên đổi tz không đổi hạn."""
        cal = self.make_calendar()
        d = self.make_definition(
            schedule_source='definition', schedule_id=cal.id, duration=2)
        t = self.task_of(self.make_partner('NEW'), d)
        planned, schedule = t.planned_end_time, t.schedule_id
        d.calendar_tz_override = 'UTC'
        t.invalidate_recordset()
        self.assertEqual((t.planned_end_time, t.schedule_id), (planned, schedule))
