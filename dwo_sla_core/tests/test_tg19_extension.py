# -*- coding: utf-8 -*-
"""TG-19: điểm mở rộng của `sla.definition` (docs/060 TC-EXT-*).

Không tạo addon `dwo_sla_test_ext` (mở rộng phạm vi repo); thay vào đó `patch.object` trực
tiếp 5 điểm mở rộng: `_get_calendar`, `_get_target_hours`, `_get_start_dt`, `_get_domain`,
`_after_transition`. `demo.ticket` không có trong DB test nên dùng `res.partner` với field
`function` ('p1'/'p2') thay cho priority và `parent_id.function`='T' thay cho team.
Refs: REQ-INT-007, 015, 016, 017, 018, REQ-REUSE-001, REQ-CM-001
"""
import inspect
from unittest.mock import patch

from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')
SIGNATURES = {
    '_get_calendar': '(self, record)',
    '_get_target_hours': '(self, record)',
    '_get_start_dt': '(self, record, now)',
    '_get_domain': '(self, cond)',
    '_after_transition': '(self, task, old_stage, new_stage, event)',
}
PRIORITY_START = "[('function', 'in', ['p1', 'p2'])]"


class ExtCase(SlaCase):

    def override(self, name, func):
        """Thay điểm mở rộng `name` bằng `func(original, definition, *args)`."""
        model_class = type(self.env['sla.definition'])
        original = getattr(model_class, name)

        def wrapper(definition, *args, **kwargs):
            return func(original, definition, *args, **kwargs)

        patcher = patch.object(model_class, name, wrapper)
        patcher.start()
        self.addCleanup(patcher.stop)

    def priority_definition(self, **vals):
        return self.make_definition(start_domain=PRIORITY_START, stop_domain=False, **vals)

    def ticket(self, priority='p1', **vals):
        return self.make_partner(False, function=priority, **vals)


@tagged(*TAGS, 'tg_19')
class TestCalendarExtension(ExtCase):

    def setUp(self):
        super().setUp()
        self.cal = self.make_calendar()
        self.company_cal = self.make_calendar(hour_from=9, hour_to=18)
        self.env.company.resource_calendar_id = self.company_cal

    def team_definition(self, calendar_of):
        self.override('_get_calendar', lambda original, d, record: (
            calendar_of(record) if d.schedule_source == 'record' else original(d, record)))
        return self.priority_definition(schedule_source='record', schedule_path='parent_id.company_id.resource_calendar_id')

    def test_ext_001_team_calendar(self):
        """TC-EXT-001: task dùng calendar do điểm mở rộng trả (team)."""
        d = self.team_definition(lambda record: self.cal)
        t = self.task_of(self.ticket(), d)
        self.assertEqual((t.schedule_id, t.planned_end_time), (self.cal, T0 + hours(4)))

    def test_ext_002_005_fallback_on_unusable(self):
        """TC-EXT-002/005: calendar flexible hoặc rỗng -> lịch công ty, note nêu lý do."""
        flexible = self.env['resource.calendar'].create({
            'name': "FX-CAL-FLEX", 'tz': 'Asia/Ho_Chi_Minh', 'flexible_hours': True})
        for calendar in (flexible, self.env['resource.calendar']):
            d = self.team_definition(lambda record, c=calendar: c)
            t = self.task_of(self.ticket(), d)
            self.assertEqual(t.schedule_id, self.company_cal)
            self.assertTrue(t.event_ids.filtered(lambda e: e.event == 'attach').note)
            d.active = False

    def test_ext_004_default_sources(self):
        """TC-EXT-004: mặc định schedule_source chỉ có 3 giá trị none/definition/record."""
        selection = self.env['sla.definition']._fields['schedule_source'].selection
        self.assertEqual([value for value, _label in selection], ['none', 'definition', 'record'])


@tagged(*TAGS, 'tg_19')
class TestValueExtensions(ExtCase):

    def p1_hours(self, value):
        self.override('_get_target_hours', lambda original, d, record: (
            value if record.function == 'p1' else original(d, record)))

    def test_ext_006_007_010_target_hours(self):
        """TC-EXT-006/007/010: P1 nhận 3 giờ từ điểm mở rộng; P2 và khi không override lấy 4 giờ."""
        d = self.priority_definition()
        t_default = self.task_of(self.ticket('p1'), d)
        self.assertEqual((t_default.target_duration, t_default.planned_end_time), (4, T0 + hours(4)))
        self.p1_hours(3)
        p1_task = self.task_of(self.ticket('p1'), d)
        self.assertEqual((p1_task.target_duration, p1_task.planned_end_time), (3, T0 + hours(3)))
        self.assertEqual(self.task_of(self.ticket('p2'), d).target_duration, 4)

    def test_ext_008_negative_hours(self):
        """TC-EXT-008: thời lượng âm -> không tạo task, 1 event error, không chặn lưu."""
        d = self.priority_definition()
        self.p1_hours(-1)
        with self.assertLogs('odoo.addons.dwo_sla_core', 'ERROR'):
            p = self.ticket('p1')
        self.assertFalse(self.tasks(p, d))
        self.assertEqual(self.Event.sudo().search_count(
            [('event', '=', 'error'), ('res_id', '=', p.id), ('definition_id', '=', d.id)]), 1)

    def test_ext_009_zero_hours(self):
        """TC-EXT-009: thời lượng 0 -> task có planned_end_time = start_time."""
        d = self.priority_definition()
        self.p1_hours(0)
        t = self.task_of(self.ticket('p1'), d)
        self.assertEqual((t.target_duration, t.planned_end_time, t.start_time), (0, T0, T0))

    def test_ext_011_012_start_dt(self):
        """TC-EXT-011/012: start_time = now - 2h khi override; = now khi không."""
        d = self.make_definition()
        self.assertEqual(self.task_of(self.make_partner('NEW'), d).start_time, T0)
        d2 = self.make_definition(name="Ext", start_domain="[('ref', '=', 'X')]")
        self.override('_get_start_dt', lambda original, definition, record, now: (
            now - hours(2) if definition == d2 else original(definition, record, now)))
        p = self.make_partner('X')
        t = self.task_of(p, d2)
        self.assertEqual((t.start_time, t.planned_end_time), (T0 - hours(2), T0 + hours(2)))

    def test_ext_013_retroactive_field(self):
        """TC-EXT-013: không override, retroactive theo create_date."""
        d = self.make_definition(
            retroactive=True,
            start_field_id=self.env['ir.model.fields']._get('res.partner', 'create_date').id)
        p = self.make_partner(False)
        self.env.cr.execute("UPDATE res_partner SET create_date=%s WHERE id=%s", (T0 - hours(1), p.id))
        p.invalidate_recordset()
        self.write(p, {'ref': 'NEW'}, T0)
        self.assertEqual(self.task_of(p, d).start_time, T0 - hours(1))

    def test_ext_014_015_016_domain_override(self):
        """TC-EXT-014/015/016: domain do điểm mở rộng thay domain đã lưu; điều kiện khác giữ domain lưu."""
        d = self.make_definition()
        p1, p2 = self.make_partner('NEW'), self.make_partner('WORK')
        self.assertEqual((len(self.tasks(p1, d)), len(self.tasks(p2, d))), (1, 1))  # EXT-015
        d.active = False
        d2 = self.make_definition(name="Ext2")
        self.override('_get_domain', lambda original, definition, cond: (
            [('ref', '=', 'WORK')] if definition == d2 and cond == 'start' else original(definition, cond)))
        q1, q2 = self.make_partner('NEW'), self.make_partner('WORK')
        self.assertEqual((len(self.tasks(q1, d2)), len(self.tasks(q2, d2))), (0, 1))  # EXT-014
        self.write(q2, {'ref': 'DONE'}, T0 + hours(1))  # stop dùng domain đã lưu (EXT-016)
        t = self.task_of(q2, d2)
        self.assertEqual((t.stage, t.end_time), ('achieved', T0 + hours(1)))


@tagged(*TAGS, 'tg_19')
class TestTransitionHook(ExtCase):

    def setUp(self):
        super().setUp()
        self.log = []
        self.override('_after_transition', lambda original, d, task, old, new, event: (
            self.log.append((old, new, event)), original(d, task, old, new, event))[1])
        self.d = self.make_definition()

    def test_ext_017_pause_calls_hook_once(self):
        """TC-EXT-017: pause gọi điểm mở rộng 1 lần (in_progress, paused, pause)."""
        p = self.make_partner('NEW')
        self.log.clear()
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        self.assertEqual(self.log, [('in_progress', 'paused', 'pause')])

    def test_ext_018_no_transition_no_call(self):
        """TC-EXT-018: đánh giá không đổi trạng thái -> không gọi điểm mở rộng."""
        p = self.make_partner('NEW')
        self.log.clear()
        self.write(p, {'ref': 'NEW'}, T0 + hours(1))
        self.assertEqual(self.log, [])

    def test_ext_019_complete_calls_hook(self):
        """TC-EXT-019: hoàn thành gọi điểm mở rộng 1 lần (in_progress, achieved, complete)."""
        p = self.make_partner('NEW')
        self.log.clear()
        self.write(p, {'ref': 'DONE'}, T0 + hours(1))
        self.assertEqual(self.log, [('in_progress', 'achieved', 'complete')])

    def test_ext_attach_calls_hook(self):
        """TC-EXT-021 (S1): attach gọi điểm mở rộng với (False, in_progress, attach)."""
        self.make_partner('NEW')
        self.assertEqual(self.log, [(False, 'in_progress', 'attach')])


@tagged(*TAGS, 'tg_19')
class TestSignatureContract(SlaCase):

    def signatures(self):
        model_class = type(self.env['sla.definition'])
        return {name: str(inspect.signature(getattr(model_class, name))) for name in SIGNATURES}

    def check_contract(self):
        actual = self.signatures()
        for name, expected in SIGNATURES.items():
            self.assertEqual(actual[name], expected, "Điểm mở rộng %s đổi chữ ký" % name)

    def test_ext_022_contract(self):
        """TC-EXT-022: test hợp đồng chữ ký đạt, và thất bại nêu tên điểm bị đổi khi chữ ký đổi."""
        self.check_contract()
        model_class = type(self.env['sla.definition'])
        with patch.object(model_class, '_get_target_hours', lambda self, record, extra: 0):
            with self.assertRaisesRegex(AssertionError, '_get_target_hours'):
                self.check_contract()

    def test_ext_020_default_hook_noop(self):
        """TC-EXT-020: mặc định không làm gì: chỉ 2 event attach, pause."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        self.assertEqual(self.events(self.task_of(p, d)), ['attach', 'pause'])
