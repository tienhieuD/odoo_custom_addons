# -*- coding: utf-8 -*-
"""TG-07: retroactive start (docs/060 TC-RET-*).

Field mốc `x_retro_dt` là field Datetime manual trên res.partner (FX-RETRO-DT).
Refs: REQ-FUNC-017, 018, 039
"""
from datetime import datetime

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')


def ict(day, hour, minute=0):
    """Datetime UTC của (ngày tháng 3 năm 2026, giờ ICT)."""
    return datetime(2026, 3, day, hour, minute) - hours(7)


@tagged(*TAGS, 'tg_07')
class TestRetroactiveStart(SlaCase):

    def setUp(self):
        super().setUp()
        self.retro = self.make_x_field('x_retro_dt', 'datetime')

    def definition(self, **vals):
        return self.make_definition(
            retroactive=True, start_field_id=self.retro.id, **vals)

    def test_ret_001_start_from_field(self):
        """TC-RET-001: start_time lấy từ field mốc, planned_end_time = mốc + 4 giờ, chưa vi phạm."""
        d = self.definition()
        p = self.make_partner('NEW', x_retro_dt=ict(2, 8))
        t = self.task_of(p, d)
        self.assertEqual((t.start_time, t.planned_end_time, t.has_breached),
                         (ict(2, 8), ict(2, 12), False))
        self.assertEqual(self.events(t).count('breach'), 0)

    def test_ret_003_empty_field_uses_now(self):
        """TC-RET-003: field mốc trống -> dùng thời điểm hiện tại, event attach có ghi chú."""
        d = self.definition()
        t = self.task_of(self.make_partner('NEW'), d)
        self.assertEqual((t.start_time, t.planned_end_time), (T0, T0 + hours(4)))
        self.assertTrue(t.event_ids.filtered(lambda e: e.event == 'attach').note)

    def test_ret_004_breach_at_attach(self):
        """TC-RET-004: planned_end_time đúng bằng thời điểm attach -> bật dấu vi phạm, 1 event breach."""
        d = self.definition()
        t = self.task_of(self.make_partner('NEW', x_retro_dt=ict(2, 5)), d)
        self.assertEqual((t.planned_end_time, t.has_breached), (T0, True))
        self.assertEqual(self.events(t).count('breach'), 1)

    def test_ret_005_one_minute_left(self):
        """TC-RET-005: planned_end_time còn 1 phút so với thời điểm attach -> chưa vi phạm."""
        d = self.definition()
        t = self.task_of(self.make_partner('NEW', x_retro_dt=ict(2, 5, 1)), d)
        self.assertEqual((t.planned_end_time, t.has_breached), (ict(2, 9, 1), False))
        self.assertEqual(self.events(t).count('breach'), 0)

    def test_ret_006_paused_before_attach(self):
        """TC-RET-006: attach ở paused, planned_end_time = mốc + 4 giờ (không cộng thời gian paused)."""
        d = self.definition()
        t = self.task_of(self.make_partner('HOLD', x_retro_dt=ict(2, 6)), d)
        self.assertEqual((t.stage, t.start_time, t.planned_end_time), ('paused', ict(2, 6), ict(2, 10)))

    def test_ret_007_calendar_across_weekend(self):
        """TC-RET-007: lịch T2–T6, mốc thứ Sáu 16:00 -> planned_end_time thứ Hai 11:00, chưa vi phạm."""
        cal = self.make_calendar()
        d = self.definition(schedule_source='definition', schedule_id=cal.id)
        t = self.task_of(self.make_partner('NEW', x_retro_dt=datetime(2026, 2, 27, 9, 0)), d)
        self.assertEqual((t.start_time, t.planned_end_time, t.has_breached),
                         (datetime(2026, 2, 27, 9, 0), ict(2, 11), False))


@tagged(*TAGS, 'tg_07')
class TestRetroactiveFieldValidation(SlaCase):

    def field(self, model, name):
        return self.env['ir.model.fields']._get(model, name)

    def rejects(self, **vals):
        n0 = self.Definition.search_count([])
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.make_definition(name="D-1", **vals)
        self.assertEqual(self.Definition.search_count([]), n0)

    def test_ret_008_char_field_rejected(self):
        """TC-RET-008: field retroactive là Char bị từ chối."""
        self.rejects(retroactive=True, start_field_id=self.field('res.partner', 'name').id)

    def test_ret_009_other_model_rejected(self):
        """TC-RET-009: field retroactive thuộc model khác bị từ chối."""
        self.rejects(retroactive=True,
                     start_field_id=self.field('res.users', 'login_date').id)

    def test_ret_010_reset_field_other_model_rejected(self):
        """TC-RET-010: field kích hoạt reset thuộc model khác bị từ chối."""
        self.rejects(reset_domain="[]",
                     reset_field_ids=[(6, 0, self.field('res.users', 'login').ids)])

    def test_ret_011_012_valid_fields(self):
        """TC-RET-011/012: Datetime của đúng model và field reset đúng model lưu được."""
        retro = self.make_x_field('x_retro_dt', 'datetime')
        user_id = self.field('res.partner', 'user_id')
        d = self.make_definition(name="D-1", retroactive=True, start_field_id=retro.id,
                                 reset_domain="[]", reset_field_ids=[(6, 0, user_id.ids)])
        d.invalidate_cache(None, ids=d.ids)
        self.assertEqual((d.start_field_id, d.reset_field_ids), (retro, user_id))
