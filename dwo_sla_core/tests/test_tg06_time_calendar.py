# -*- coding: utf-8 -*-
"""TG-06 và TG-15: giờ làm việc và nguồn lịch (docs/060 TC-TIM-*, TC-CAL-*).

Lịch FX-CAL-VN: T2–T6 08:00–17:00 giờ Asia/Ho_Chi_Minh (UTC+7, không nghỉ trưa).
`T0` = thứ Hai 2026-03-02 09:00 ICT; thứ Sáu 2026-03-06 16:00 ICT = 09:00 UTC.
Refs: REQ-FUNC-018..020, 039, 043, 044, 046, 055, REQ-INT-007
"""
from datetime import datetime

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')
FRI_16 = datetime(2026, 3, 6, 9, 0)   # thứ Sáu 16:00 ICT
FRI_17 = datetime(2026, 3, 6, 10, 0)  # thứ Sáu 17:00 ICT
MON_09 = datetime(2026, 3, 9, 2, 0)   # thứ Hai 09:00 ICT
MON_10 = datetime(2026, 3, 9, 3, 0)   # thứ Hai 10:00 ICT


@tagged(*TAGS, 'tg_06')
class TestTimePlanning(SlaCase):

    def setUp(self):
        super().setUp()
        self.cal = self.make_calendar()

    def definition(self, **vals):
        return self.make_definition(
            schedule_source='definition', schedule_id=self.cal.id, **vals)

    def test_tim_001_over_weekend(self):
        """TC-TIM-001: 8 giờ từ thứ Sáu 16:00 -> thứ Hai 15:00 ICT (08:00 UTC)."""
        d = self.definition(duration=8)
        t = self.task_of(self.make_partner('NEW', FRI_16), d)
        self.assertEqual(t.start_time, FRI_16)
        self.assertEqual(t.planned_end_time, datetime(2026, 3, 9, 8, 0))

    def test_tim_002_global_leave(self):
        """TC-TIM-002: thứ Hai là global leave -> dời sang thứ Ba 15:00 ICT."""
        self.env['resource.calendar.leaves'].create({
            'name': "Leave", 'calendar_id': self.cal.id,
            'date_from': datetime(2026, 3, 8, 17, 0), 'date_to': datetime(2026, 3, 9, 10, 0),
        })
        d = self.definition(duration=8)
        t = self.task_of(self.make_partner('NEW', FRI_16), d)
        self.assertEqual(t.planned_end_time, datetime(2026, 3, 10, 8, 0))

    def test_tim_003_zero_target(self):
        """TC-TIM-003: mục tiêu 0 giờ -> planned_end_time = start."""
        d = self.definition(duration=0)
        t = self.task_of(self.make_partner('NEW', T0), d)
        self.assertEqual(t.planned_end_time, T0)

    def test_tim_004_start_at_closing_time(self):
        """TC-TIM-004: bắt đầu đúng 17:00 thứ Sáu, 1 giờ -> thứ Hai 09:00 ICT."""
        d = self.definition(duration=1)
        t = self.task_of(self.make_partner('NEW', FRI_17), d)
        self.assertEqual(t.planned_end_time, MON_09)

    def test_tim_005_local_timezone(self):
        """TC-TIM-005: 2 giờ từ 09:00 ICT -> 11:00 ICT = 04:00 UTC."""
        d = self.definition(duration=2)
        t = self.task_of(self.make_partner('NEW', T0), d)
        self.assertEqual(t.planned_end_time, datetime(2026, 3, 2, 4, 0))

    def test_tim_006_no_calendar_24x7(self):
        """TC-TIM-006: không có lịch -> cộng thẳng 4 giờ."""
        d = self.make_definition()
        t = self.task_of(self.make_partner('NEW', FRI_17), d)
        self.assertEqual(t.planned_end_time, FRI_17 + hours(4))

    def test_tim_007_unplannable_calendar(self):
        """TC-TIM-007: lịch bị nghỉ phủ kín -> không tạo task, ghi event error."""
        self.env['resource.calendar.leaves'].create({
            'name': "Closed", 'calendar_id': self.cal.id,
            'date_from': datetime(2020, 1, 1), 'date_to': datetime(2040, 1, 1),
        })
        d = self.definition(duration=8)
        with self.assertLogs('odoo.addons.dwo_sla_core', 'ERROR'):
            p = self.make_partner('NEW', T0)
        self.assertFalse(self.tasks(p, d))
        self.assertTrue(self.Event.sudo().search([('event', '=', 'error'), ('res_id', '=', p.id)]))


@tagged(*TAGS, 'tg_06')
class TestTimeElapsed(SlaCase):

    def test_tim_008_accumulate_across_pause(self):
        """TC-TIM-008/010/011: cộng dồn 1h + 2h = 3h; paused không tăng; không cắt ở mục tiêu."""
        d = self.make_definition()
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        t = self.task_of(p, d)
        self.assertAlmostEqual(t.business_duration, 1.0, places=3)
        self.evaluate(p, T0 + hours(7))  # đang paused: không tăng
        self.assertAlmostEqual(t.business_duration, 1.0, places=3)
        self.write(p, {'ref': 'WORK'}, T0 + hours(9))
        self.write(p, {'ref': 'HOLD'}, T0 + hours(11))
        self.assertAlmostEqual(t.business_duration, 3.0, places=3)
        self.write(p, {'ref': 'WORK'}, T0 + hours(12))
        self.write(p, {'ref': 'HOLD'}, T0 + hours(14))
        self.assertAlmostEqual(t.business_duration, 5.0, places=3)  # > mục tiêu 4h, không cắt

    def test_tim_009_working_hours_only(self):
        """TC-TIM-009: thứ Sáu 16:00 -> thứ Hai 10:00 trên lịch T2–T6 = 3 giờ."""
        cal = self.make_calendar()
        d = self.make_definition(schedule_source='definition', schedule_id=cal.id)
        p = self.make_partner('NEW', FRI_16)
        self.write(p, {'ref': 'HOLD'}, MON_10)
        self.assertAlmostEqual(self.task_of(p, d).business_duration, 3.0, places=3)


@tagged(*TAGS, 'tg_15')
class TestCalendarSource(SlaCase):

    def setUp(self):
        super().setUp()
        self.cal = self.make_calendar()
        self.empty = self.env['resource.calendar'].create({
            'name': "Empty", 'tz': 'Asia/Ho_Chi_Minh', 'schedule_type': 'fully_fixed',
            'attendance_ids': [(5, 0, 0)]})

    def test_cal_001_empty_calendar_rejected(self):
        """TC-CAL-001: nguồn definition + lịch không có giờ làm -> từ chối lưu."""
        with self.assertRaises(ValidationError):
            self.make_definition(schedule_source='definition', schedule_id=self.empty.id)

    def test_cal_002_valid_calendar_saved(self):
        """TC-CAL-002: lịch fully_fixed T2–T6 lưu thành công."""
        d = self.make_definition(schedule_source='definition', schedule_id=self.cal.id)
        self.assertEqual(d.schedule_id, self.cal)

    def test_cal_003_flexible_calendar_rejected(self):
        """TC-CAL-003: lịch flexible không được chọn làm lịch cố định."""
        flexible = self.env['resource.calendar'].create({
            'name': "Flex", 'tz': 'Asia/Ho_Chi_Minh', 'schedule_type': 'flexible'})
        with self.assertRaises(ValidationError):
            self.make_definition(schedule_source='definition', schedule_id=flexible.id)

    def test_cal_006_007_invalid_paths(self):
        """TC-CAL-006/007: đường dẫn có bước giữa One2many hoặc bước cuối không phải resource.calendar."""
        for path in ('child_ids.company_id', 'company_id'):
            with self.assertRaises(ValidationError, msg=path):
                self.make_definition(schedule_source='record', schedule_path=path)

    def test_cal_008_none_is_24x7(self):
        """TC-CAL-008: nguồn none -> task không có lịch."""
        d = self.make_definition()
        self.assertFalse(self.task_of(self.make_partner('NEW'), d).schedule_id)

    def test_cal_005_009_path_resolves_record_calendar(self):
        """TC-CAL-005/009: đi theo đường dẫn tới lịch của công ty record."""
        company = self.env['res.company'].create({
            'name': "Cal Co", 'resource_calendar_id': self.cal.id})
        d = self.make_definition(schedule_source='record',
                                 schedule_path='company_id.resource_calendar_id')
        p = self.make_partner('NEW', company_id=company.id)
        self.assertEqual(self.task_of(p, d).schedule_id, self.cal)

    def test_cal_011_013_fallbacks(self):
        """TC-CAL-011/013: đường dẫn trống -> lịch công ty + ghi lý do; công ty cũng không dùng được -> 24x7 + lý do."""
        # Timezone của định nghĩa đặt trùng tz lịch công ty để không sinh bản sao tz.
        d = self.make_definition(schedule_source='record',
                                 schedule_path='company_id.resource_calendar_id',
                                 calendar_tz_override=self.env.company.resource_calendar_id.tz)
        p = self.make_partner('NEW', company_id=False)
        t = self.task_of(p, d)
        self.assertEqual(t.schedule_id, self.env.company.resource_calendar_id)
        self.assertTrue(t.event_ids.filtered(lambda e: e.event == 'attach').note)

        self.env.company.resource_calendar_id = self.empty
        p2 = self.make_partner('NEW', company_id=False)
        t2 = self.task_of(p2, d)
        self.assertFalse(t2.schedule_id)
        self.assertTrue(t2.event_ids.filtered(lambda e: e.event == 'attach').note)
