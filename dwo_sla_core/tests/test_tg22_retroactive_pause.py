# -*- coding: utf-8 -*-
"""TG-22: `retroactive_pause` -- scope-add (ServiceNow Fluent SLA API `retroactive.pause`).

Refs: 031_scope_additions_contract_sla_fields.md "retroactive_pause"
"""
from datetime import datetime

from odoo.tests import tagged

from .common import SlaCase, T0, hours

TAGS = ('post_install', '-at_install', 'dwo_sla_core')


def ict(day, hour, minute=0):
    """Datetime UTC của (ngày tháng 3 năm 2026, giờ ICT), giống test_tg07_retroactive.py."""
    return datetime(2026, 3, day, hour, minute) - hours(7)


@tagged(*TAGS, 'tg_22')
class TestRetroactivePauseWarning(SlaCase):
    """`retroactive_pause_warning` -- không bao giờ chặn lưu, chỉ cảnh báo."""

    def test_warning_model_not_trackable(self):
        """Model không có mail.thread -> cảnh báo nêu rõ model."""
        model = self.env['ir.model']._get('res.partner.category')
        d = self.Definition.create({
            'name': "D-not-trackable",
            'model_id': model.id,
            'duration': 4,
            'schedule_source': 'none',
            'start_domain': "[('name', '=', 'x')]",
            'pause_domain': "[('name', '=', 'y')]",
            'retroactive_pause': True,
        })
        self.assertIn('not change-tracked', d.retroactive_pause_warning)
        self.assertIn('res.partner.category', d.retroactive_pause_warning)

    def test_warning_field_not_tracked(self):
        """Model trackable (res.partner) nhưng field 'ref' (dùng trong pause_domain
        của FX-DEF-STD) không có tracking=True -> cảnh báo nêu tên field."""
        d = self.make_definition(retroactive_pause=True)
        self.assertTrue(d.retroactive_pause_warning)
        self.assertIn('ref', d.retroactive_pause_warning)

    def test_no_warning_when_all_pause_fields_tracked(self):
        flag = self.make_x_field('x_hold_w1', 'boolean', track_visibility='onchange')
        d = self.make_definition(
            retroactive_pause=True, pause_domain="[('x_hold_w1', '=', True)]")
        self.assertFalse(d.retroactive_pause_warning)

    def test_no_warning_when_feature_off(self):
        """retroactive_pause tắt -> không tính cảnh báo, dù field pause không tracking."""
        d = self.make_definition(retroactive_pause=False)
        self.assertFalse(d.retroactive_pause_warning)

    def test_warning_recomputes_when_pause_domain_changes(self):
        flag = self.make_x_field('x_hold_w2', 'boolean', track_visibility='onchange')
        d = self.make_definition(retroactive_pause=True)  # pause_domain = ref, chưa tracking
        self.assertTrue(d.retroactive_pause_warning)
        d.pause_domain = "[('x_hold_w2', '=', True)]"
        self.assertFalse(d.retroactive_pause_warning)


@tagged(*TAGS, 'tg_22')
class TestRetroactivePauseAlgorithm(SlaCase):
    """Thuật toán dựng lại timeline pause từ `mail.tracking.value` khi attach."""

    def setUp(self):
        super().setUp()
        self.flag = self.make_x_field('x_hold3', 'boolean', track_visibility='onchange')
        self.retro = self.make_x_field('x_retro3', 'datetime')

    def definition(self, **vals):
        return self.make_definition(
            retroactive=True, start_field_id=self.retro.id,
            pause_domain="[('x_hold3', '=', True)]", duration=4,
            schedule_source='none', **vals)

    def test_excludes_tracked_pause_history(self):
        """Lịch sử x_hold3: False (08:00-09:00) -> True (09:00 trở đi, còn giữ tới lúc
        attach 11:00); retroactive_pause bật -> trừ đúng 2h đã pause (09:00-11:00) khỏi
        business_duration/duration, dời planned_end_time ra đúng 2h.

        Chỉ dùng 1 lần đổi giá trị (không đổi lại về False) để tránh vướng cách
        mail.thread gộp các lần đổi giá trị cho tới lần flush kế tiếp (chỉ so giá trị
        ĐẦU với giá trị TẠI LÚC FLUSH) -- 2 lần đổi ngược nhau trong cùng 1 giao dịch
        có thể bị gộp thành "không đổi" tùy thời điểm flush, không cần thiết cho việc
        kiểm thuật toán cốt lõi (chỉ cần ĐÚNG 1 đoạn khớp pause được dựng lại đúng).
        """
        # Dựng lịch sử TRƯỚC khi tạo định nghĩa: nếu tạo định nghĩa trước, hook sẽ
        # attach ngay khi x_hold3 đổi giá trị thật qua write() (do pause_domain đã
        # dùng x_hold3) -- phải tách biệt "dựng lịch sử" khỏi "attach lần duy nhất".
        #
        # Tạo thẳng `mail.message`/`mail.tracking.value` bằng create() (không đi
        # qua write() thật của partner) để kiểm soát chính xác thời điểm: dựa vào
        # cơ chế tracking thật của mail.thread (gộp nhiều lần đổi tới lần flush kế
        # tiếp, default `date` chụp sẵn hàm gốc lúc module nạp nên patch
        # `self.at()` không ảnh hưởng) không cho điều khiển thời điểm chính xác
        # trong 1 giao dịch test -- đây chỉ là CÁCH TẠO FIXTURE cho thuật toán đọc,
        # không phải đường người dùng thật đi qua (người dùng thật vẫn tạo tracking
        # value qua write() bình thường, thuật toán đọc lại đúng bảng
        # mail.tracking.value chuẩn của Odoo bất kể cách nó được tạo ra).
        p = self.make_partner('NEW', x_retro3=ict(2, 8))
        x_hold3_field = self.env['ir.model.fields'].sudo()._get('res.partner', 'x_hold3')
        message = self.env['mail.message'].sudo().create({
            'model': 'res.partner', 'res_id': p.id, 'date': ict(2, 9), 'body': "x_hold3 change"})
        self.env['mail.tracking.value'].sudo().create({
            'field': x_hold3_field.name, 'field_desc': 'x_hold3', 'field_type': 'boolean', 'mail_message_id': message.id,
            'old_value_integer': 0, 'new_value_integer': 1})
        p.x_hold3 = True  # giá trị thật hiện tại trên record phải khớp "new_value" ở trên
        d = self.definition(retroactive_pause=True)
        self.evaluate(p, now=ict(2, 11))
        t = self.task_of(p, d)
        self.assertEqual(t.start_time, ict(2, 8))
        self.assertAlmostEqual(t.business_duration, 1.0, places=3)
        self.assertAlmostEqual(t.duration, 1.0, places=3)
        self.assertAlmostEqual(t.business_pause_duration, 2.0, places=3)
        self.assertAlmostEqual(t.pause_duration, 2.0, places=3)
        self.assertEqual(t.planned_end_time, ict(2, 8) + hours(6))
        self.assertEqual(t.original_breach_time, t.planned_end_time)
        self.assertFalse(t.has_breached)

    def test_flag_off_counts_full_backdated_window(self):
        """Cùng lịch sử pause, nhưng retroactive_pause TẮT -> không trừ gì, hạn chót
        không dời (so sánh trực tiếp với kịch bản bật ở test trên)."""
        p = self.make_partner('NEW', x_retro3=ict(2, 8))
        self.write(p, {'x_hold3': True}, ict(2, 9))
        self.write(p, {'x_hold3': False}, ict(2, 10))
        d = self.definition(retroactive_pause=False)
        self.evaluate(p, now=ict(2, 11))
        t = self.task_of(p, d)
        self.assertAlmostEqual(t.business_duration, 3.0, places=3)
        self.assertEqual(t.business_pause_duration, 0.0)
        self.assertEqual(t.planned_end_time, ict(2, 8) + hours(4))

    def test_no_history_in_window_no_effect(self):
        """Không có thay đổi nào của field tracking trong khoảng -> không trừ gì
        (field vẫn giữ giá trị hiện tại suốt khoảng, mặc định False nên không khớp
        pause_domain ở bất kỳ đoạn nào)."""
        p = self.make_partner('NEW', x_retro3=ict(2, 8))
        d = self.definition(retroactive_pause=True)
        self.evaluate(p, now=ict(2, 11))
        t = self.task_of(p, d)
        self.assertAlmostEqual(t.business_duration, 3.0, places=3)
        self.assertEqual(t.business_pause_duration, 0.0)

    def test_untracked_pause_field_falls_back_no_effect(self):
        """pause_domain dùng field KHÔNG tracking ('ref') -> eligible=False, không
        trừ gì dù retroactive_pause bật (giống hành vi tắt, đã cảnh báo ở form)."""
        other_retro = self.make_x_field('x_retro4', 'datetime')
        p = self.make_partner('NEW', x_retro4=ict(2, 8))
        d = self.make_definition(
            retroactive=True, start_field_id=other_retro.id,
            pause_domain="[('ref', '=', 'HOLD')]", duration=4,
            schedule_source='none', retroactive_pause=True)
        self.evaluate(p, now=ict(2, 11))
        t = self.task_of(p, d)
        self.assertAlmostEqual(t.business_duration, 3.0, places=3)
        self.assertEqual(t.business_pause_duration, 0.0)
