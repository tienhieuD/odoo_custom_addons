# -*- coding: utf-8 -*-
"""Nâng cấp lên 19.0.1.1.0: chuẩn bị dữ liệu cũ cho hai thay đổi hành vi.

Logic: chạy TRƯỚC khi schema áp dụng, nên cột `calendar_tz_override` còn
NULL phải được điền trước khi Odoo đặt NOT NULL (Odoo không có default để
tự điền). Hai câu SQL idempotent, chạy lại không đổi gì thêm.
Refs: plan-improvement-sla-01-review §6.5 (timezone bắt buộc), §6.8 + Q1
(Start `[]` cũ nghĩa là "khớp mọi record", từ nay `[]` là "chưa cấu hình")
"""


def migrate(cr, version):
    # §6.5: timezone = tz của calendar cố định nếu có, nếu không 'UTC'.
    cr.execute("""
        UPDATE sla_definition d
           SET calendar_tz_override = COALESCE(
               (SELECT c.tz FROM resource_calendar c WHERE c.id = d.schedule_id), 'UTC')
         WHERE d.calendar_tz_override IS NULL
    """)
    # §6.8 / Q1: giữ hành vi cũ của Start `[]` (khớp mọi record) để task đang
    # chạy không bị huỷ hàng loạt. Chỉ start_domain; 5 domain còn lại không cần.
    cr.execute("""
        UPDATE sla_definition
           SET start_domain = '[(''id'', ''!='', 0)]'
         WHERE btrim(start_domain) = '[]'
    """)
