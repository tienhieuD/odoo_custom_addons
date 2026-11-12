# -*- coding: utf-8 -*-
from lxml import etree

from odoo.tests import tagged

from .common import SlaCase, T0, hours


@tagged('post_install', '-at_install', 'tg_32')
class TestDurationLive(SlaCase):
    """Hai field live: giá trị đã chốt cộng đoạn đang chạy, chỉ để hiển thị."""

    def setUp(self):
        super().setUp()
        self.d = self.make_definition()

    def test_running_adds_current_period(self):
        """Task đang chạy: cột lưu đứng yên, bản live cộng đoạn tới hiện tại."""
        t = self.task_of(self.make_partner('NEW'), self.d)
        with self.at(T0 + hours(1.5)):
            t.invalidate_cache(None, ids=t.ids)
            self.assertEqual((t.business_duration, t.duration), (0.0, 0.0))
            self.assertAlmostEqual(t.business_duration_live, 1.5)
            self.assertAlmostEqual(t.duration_live, 1.5)

    def test_paused_equals_stored(self):
        """Task tạm dừng: không có đoạn đang chạy nên live = giá trị đã lưu."""
        p = self.make_partner('NEW')
        self.write(p, {'ref': 'HOLD'}, T0 + hours(1))
        t = self.task_of(p, self.d)
        self.assertEqual(t.stage, 'paused')
        with self.at(T0 + hours(3)):
            t.invalidate_cache(None, ids=t.ids)
            self.assertAlmostEqual(t.business_duration_live, t.business_duration)
            self.assertAlmostEqual(t.duration_live, t.duration)
            self.assertAlmostEqual(t.business_duration_live, 1.0)

    def test_calendar_counts_working_hours_only(self):
        """Có lịch: live theo giờ làm khác live theo giờ đồng hồ."""
        calendar = self.make_calendar()  # T2-T6 08:00-17:00 giờ VN
        d = self.make_definition(
            name="SLA cal", schedule_source='definition', schedule_id=calendar.id,
            start_domain="[('ref', '=', 'CAL')]")
        t = self.task_of(self.make_partner('CAL'), d)
        with self.at(T0 + hours(24)):
            t.invalidate_cache(None, ids=t.ids)
            self.assertAlmostEqual(t.duration_live, 24.0)
            self.assertLess(t.business_duration_live, 24.0)
            self.assertGreater(t.business_duration_live, 0.0)

    def test_list_shows_live_and_hides_stored(self):
        """List task: hai field live hiện mặc định, hai cột lưu vẫn có nhưng ẩn."""
        arch = self.Task.fields_view_get(view_type='tree')['arch']
        root = etree.fromstring(arch)
        optional = {f.get('name'): f.get('optional') for f in root.iter('field')}
        self.assertEqual(optional['business_duration_live'], 'show')
        self.assertEqual(optional['duration_live'], 'show')
        self.assertEqual(optional['business_duration'], 'hide')
        self.assertEqual(optional['duration'], 'hide')
