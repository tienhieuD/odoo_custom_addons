# -*- coding: utf-8 -*-
"""Bổ sung TG-11, TG-15, TG-09, TG-05 (docs/060 TC-GEN-*, TC-MIS-*, TC-MUL-*, TC-CHG-*, TC-CAL-*).

Refs: REQ-FUNC-001, 003, 006, 008, 019..021, 033, 034, 039, 052, 053, 060, REQ-SEC-005
"""

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tools import mute_logger

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')


@tagged(*TAGS, 'tg_01')
class TestDefinitionSaving(SlaCase):

    def test_gen_002_full_definition_roundtrip(self):
        """TC-GEN-002: lưu định nghĩa đủ tùy chọn và đọc lại đúng giá trị."""
        cal = self.make_calendar()
        ref_field = self.env['ir.model.fields']._get('res.partner', 'ref')
        create_date = self.env['ir.model.fields']._get('res.partner', 'create_date')
        d = self.make_definition(
            duration=6, schedule_source='definition', schedule_id=cal.id,
            start_domain="[('ref','=','NEW')]", reset_domain="[('ref','=','RESET')]",
            reset_action='cancel', reset_field_ids=[(6, 0, ref_field.ids)],
            retroactive=True, start_field_id=create_date.id,
            company_id=self.env.company.id, sequence=5,
            escalation_ids=[(0, 0, {'percent': 75, 'action_type': 'server_action',
                                     'action_id': self.make_server_action("pass").id}),
                            (0, 0, {'percent': 100, 'action_type': 'server_action',
                                     'action_id': self.make_server_action("pass").id})])
        d.invalidate_recordset()
        self.assertEqual((d.duration, d.schedule_source, d.schedule_id), (6, 'definition', cal))
        self.assertEqual((d.cancel_mode, d.resume_mode, d.reset_action),
                         ('start_unmatched', 'condition', 'cancel'))
        self.assertEqual(d.reset_field_ids, ref_field)
        self.assertEqual((d.retroactive, d.start_field_id), (True, create_date))
        self.assertEqual(sorted(d.escalation_ids.mapped('percent')), [75, 100])
        self.assertEqual((d.company_id, d.active, d.sequence), (self.env.company, True, 5))

    def test_gen_003_model_required(self):
        """TC-GEN-003: thiếu model bị từ chối."""
        n0 = self.Definition.search_count([])
        with self.assertRaises(Exception), \
                mute_logger('odoo.sql_db'), self.env.cr.savepoint():
            self.Definition.create({'name': "No model", 'duration': 4,
                                    'start_domain': "[('ref','=','NEW')]"})
        self.assertEqual(self.Definition.search_count([]), n0)

    def test_gen_004_negative_target_rejected(self):
        """TC-GEN-004: duration = -1 bị từ chối."""
        n0 = self.Definition.search_count([])
        with self.assertRaises(Exception), \
                mute_logger('odoo.sql_db'), self.env.cr.savepoint():
            self.make_definition(duration=-1)
        self.assertEqual(self.Definition.search_count([]), n0)

    def test_gen_005_zero_target_accepted(self):
        """TC-GEN-005: duration = 0 được chấp nhận."""
        d = self.make_definition(duration=0)
        d.invalidate_recordset()
        self.assertEqual(d.duration, 0)


@tagged(*TAGS, 'tg_05')
class TestMisconfigMore(SlaCase):

    def subset_def(self, **vals):
        return self.make_definition(
            start_domain="[('ref','in',['NEW','WORK'])]",
            stop_domain="[('ref','in',['NEW','WORK','DONE'])]", **vals)

    def test_mis_002_003_start_subset_of_stop(self):
        """TC-MIS-002/003: start là tập con của stop -> không gắn (cancel condition và never)."""
        for mode in ('condition', 'never'):
            d = self.subset_def(name="sub-%s" % mode, cancel_mode=mode)
            p = self.make_partner('NEW')
            self.assertFalse(self.tasks(p, d), mode)
            self.assertFalse(self.Event.sudo().search([('definition_id', '=', d.id)]), mode)
            d.active = False

    def test_mis_008_exclusive_start_pause(self):
        """TC-MIS-008: start/pause loại trừ nhau, cancel condition chưa khớp -> giữ task, chuyển paused."""
        d = self.make_definition(start_domain="[('ref','in',['NEW','WORK'])]",
                                 cancel_mode='condition')
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'paused')
        names = self.events(t)
        self.assertEqual((names.count('cancel'), names.count('pause')), (0, 1))


@tagged(*TAGS, 'tg_09')
class TestMultipleMore(SlaCase):

    def test_mul_003_independent_tasks(self):
        """TC-MUL-003: mỗi record một task riêng và độc lập."""
        d = self.make_definition()
        p1, p2 = self.make_partner('NEW'), self.make_partner('NEW')
        self.assertEqual((len(self.tasks(p1, d)), len(self.tasks(p2, d))), (1, 1))
        self.write(p1, {'ref': 'DONE'}, T0 + hours(1))
        self.assertEqual(self.task_of(p1, d).stage, 'achieved')
        self.assertEqual(self.task_of(p2, d).stage, 'in_progress')

    def test_mul_005_new_active_after_cancelled(self):
        """TC-MUL-005: chỉ mục duy nhất không chặn task mới khi task trước cancelled."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        t1 = self.task_of(p, d)
        self.write(p, {'ref': 'OTHER'}, T0 + hours(1))
        self.assertEqual(t1.stage, 'cancelled')
        t2 = self.Task.sudo().create({
            'sla_id': d.id, 'res_model': 'res.partner', 'res_id': p.id,
            'stage': 'in_progress', 'start_time': T0 + hours(2),
            'target_duration': 4, 'planned_end_time': T0 + hours(6), 'next_due_at': T0 + hours(6),
            'running_since': T0 + hours(2)})
        self.assertEqual(t2.stage, 'in_progress')
        self.assertEqual((len(self.tasks(p, d)), len(self.tasks(p, d, 'in_progress'))), (2, 1))


@tagged(*TAGS, 'tg_11')
class TestChangeCalendar(SlaCase):

    def setUp(self):
        super().setUp()
        self.cal_am = self.make_calendar()
        self.cal_pm = self.make_calendar(hour_from=13, hour_to=18)
        self.manager = self.make_user('sla_mgr_cal', 'manager')

    def test_chg_002_definition_calendar_snapshot(self):
        """TC-CHG-002: đổi lịch của định nghĩa không đổi lịch/planned_end_time của task đang chạy."""
        d = self.make_definition(schedule_source='definition', schedule_id=self.cal_am.id)
        t = self.task_of(self.make_partner('NEW'), d)
        self.assertEqual((t.schedule_id, t.planned_end_time), (self.cal_am, T0 + hours(4)))
        d.schedule_id = self.cal_pm
        self.evaluate(self.Partner.browse(t.res_id), T0 + hours(1))
        self.assertEqual((t.schedule_id, t.planned_end_time), (self.cal_am, T0 + hours(4)))

    def _path_setup(self):
        self.make_x_field('x_calendar_id', 'many2one', relation='resource.calendar')
        d = self.make_definition(schedule_source='record', schedule_path='parent_id.x_calendar_id')
        parent = self.make_partner(False, x_calendar_id=self.cal_am.id)
        child = self.make_partner('NEW', parent_id=parent.id)
        return d, parent, child

    def test_chg_004_005_path_calendar_snapshot_and_recalculate(self):
        """TC-CHG-004/005: lịch theo đường dẫn giữ nguyên khi lịch cha đổi, trừ khi Tính lại."""
        d, parent, child = self._path_setup()
        t = self.task_of(child, d)
        self.assertEqual(t.schedule_id, self.cal_am)
        self.write(parent, {'x_calendar_id': self.cal_pm.id}, T0 + hours(1))
        self.evaluate(child, T0 + hours(1))
        self.assertEqual((t.schedule_id, t.planned_end_time), (self.cal_am, T0 + hours(4)))
        self.write(child, {'ref': 'WORK'}, T0 + hours(1))
        with self.at(T0 + hours(1)):
            t.with_user(self.manager).action_recalculate()
        self.assertEqual(t.schedule_id, self.cal_pm)

    def test_chg_018_archived_stop_one_of_30(self):
        """TC-CHG-018: archive định nghĩa; stop trên 1 trong 30 record chỉ kết thúc đúng task đó."""
        partners = self.Partner
        d = self.make_definition()
        self.make_definition(name="Other", start_domain="[('ref','=','ZZZ')]")
        for _ in range(30):
            partners |= self.make_partner('NEW')
        d.active = False
        self.assertEqual(len(self.Task.sudo().search([('sla_id', '=', d.id),
                                                      ('stage', '=', 'in_progress')])), 30)
        self.write(partners[0], {'ref': 'DONE'}, T0 + hours(1))
        t = self.task_of(partners[0], d)
        self.assertEqual((t.stage, t.end_time), ('achieved', T0 + hours(1)))
        self.assertEqual(self.events(t).count('complete'), 1)
        self.assertEqual(len(self.Task.sudo().search([('sla_id', '=', d.id),
                                                      ('stage', '=', 'in_progress')])), 29)

    def test_chg_020_archived_no_new_task(self):
        """TC-CHG-020: định nghĩa archive không gắn task cho record mới, task cũ vẫn chạy."""
        d = self.make_definition()
        p1 = self.make_partner('NEW')
        d.active = False
        p2 = self.make_partner('NEW', now=T0 + hours(1))
        self.evaluate(p2, T0 + hours(1))
        self.assertFalse(self.tasks(p2, d))
        self.assertEqual(self.task_of(p1, d).stage, 'in_progress')


@tagged(*TAGS, 'tg_15')
class TestCalendarFallbacks(SlaCase):

    def setUp(self):
        super().setUp()
        self.cal = self.make_calendar()
        self.cal_pm = self.make_calendar(hour_from=13, hour_to=18)
        self.flex = self.env['resource.calendar'].create({
            'name': "FX-CAL-FLEX", 'tz': 'Asia/Ho_Chi_Minh', 'flexible_hours': True})
        self.empty = self.env['resource.calendar'].create({
            'name': "FX-CAL-EMPTY", 'tz': 'Asia/Ho_Chi_Minh', 'flexible_hours': False,
            'attendance_ids': [(5, 0, 0)]})
        self.env.company.resource_calendar_id = self.cal
        self.make_x_field('x_calendar_id', 'many2one', relation='resource.calendar')
        self.d = self.make_definition(schedule_source='record',
                                      schedule_path='parent_id.x_calendar_id')

    def attach_note(self, task):
        return task.event_ids.filtered(lambda e: e.event == 'attach').note

    def with_parent_calendar(self, calendar):
        parent = self.make_partner(False, x_calendar_id=calendar.id)
        return self.make_partner('NEW', parent_id=parent.id, company_id=self.env.company.id)

    def test_cal_004_flexible_falls_back(self):
        """TC-CAL-004: calendar flexible -> lịch công ty + ghi lý do vào event attach."""
        t = self.task_of(self.with_parent_calendar(self.flex), self.d)
        self.assertEqual(t.schedule_id, self.cal)
        self.assertIn('FX-CAL-FLEX', self.attach_note(t))

    def test_cal_010_empty_step(self):
        """TC-CAL-010: record không có công ty mẹ -> lịch công ty record, note nêu đường dẫn."""
        p = self.make_partner('NEW', company_id=self.env.company.id)
        t = self.task_of(p, self.d)
        self.assertEqual(t.schedule_id, self.cal)
        self.assertIn('parent_id', self.attach_note(t))

    def test_cal_012_no_working_hours(self):
        """TC-CAL-012: calendar không có giờ làm -> lịch công ty, note nêu tên calendar."""
        t = self.task_of(self.with_parent_calendar(self.empty), self.d)
        self.assertEqual(t.schedule_id, self.cal)
        self.assertIn('FX-CAL-EMPTY', self.attach_note(t))

    def test_cal_014_record_without_company_uses_current(self):
        """TC-CAL-014: record không có công ty -> lịch của công ty hiện tại (CO-B)."""
        co_b = self.env['res.company'].create({
            'name': "CO-B", 'resource_calendar_id': self.cal_pm.id})
        with self.at(T0):
            p = self.Partner.with_company(co_b).create({'name': "NoCo", 'ref': 'NEW'})
        self.assertFalse(p.company_id)
        self.assertEqual(self.task_of(p, self.d).schedule_id, self.cal_pm)

    def test_cal_015_user_without_read_access(self):
        """TC-CAL-015: người dùng nghiệp vụ sửa record: tính lịch đúng, không AccessError/event error."""
        biz = self.make_user('sla_biz_cal')
        parent = self.make_partner(False, x_calendar_id=self.cal_pm.id)
        p = self.make_partner(False, parent_id=parent.id, company_id=self.env.company.id)
        self.write(p, {'ref': 'NEW'}, T0)
        self.Task.sudo().search([('res_id', '=', p.id)]).unlink()
        self.Engine.with_user(biz).evaluate(p.with_user(biz), now=T0)
        self.assertEqual(self.task_of(p, self.d).schedule_id, self.cal_pm)
        self.assertFalse(self.Event.sudo().search([('event', '=', 'error'), ('res_id', '=', p.id)]))
