# -*- coding: utf-8 -*-
"""Nâng cấp lên 13.0.1.2.0: tính các field báo cáo mới cho task có sẵn.

Logic: Odoo thường tự tính field lưu mới khi thêm cột, nhưng chạy lại ở đây để
chắc chắn (kể cả khi bước đó bị bỏ qua) và để một câu SQL duy nhất cho mỗi
nhóm field, không đọc từng task qua ORM (an toàn với hàng chục nghìn task).
Công thức PHẢI trùng `_compute_outcome`/`_compute_usage`/`_compute_usage_bucket`
trong models/sla_task.py. `source_name` cần tên hiển thị của model nguồn nên
chỉ điền cho task còn trống, theo lô, qua ORM. Idempotent.
Refs: task 006 C1
"""
from odoo import SUPERUSER_ID, api

BATCH = 2000


def migrate(cr, version):
    cr.execute("""
        UPDATE sla_task
           SET outcome = CASE
                   WHEN stage = 'achieved' THEN 'on_time'
                   WHEN stage = 'breached' THEN 'late'
                   WHEN stage = 'cancelled' THEN 'cancelled'
                   WHEN has_breached THEN 'breached_open'
                   WHEN stage = 'paused' THEN 'paused'
                   ELSE 'running' END,
               final_percent_used = pct.v,
               overdue_duration = CASE WHEN has_breached
                   THEN GREATEST(business_duration - target_duration, 0) ELSE 0 END,
               usage_bucket = CASE
                   WHEN pct.v < 50 THEN '0_50'
                   WHEN pct.v < 75 THEN '50_75'
                   WHEN pct.v < 100 THEN '75_100'
                   WHEN pct.v <= 150 THEN '100_150'
                   ELSE '150_plus' END
          FROM (
              SELECT t.id,
                     CASE WHEN t.has_breached THEN GREATEST(raw.v, 100) ELSE raw.v END AS v
                FROM sla_task t,
                     LATERAL (SELECT CASE
                         WHEN t.target_duration <> 0
                              THEN t.business_duration / t.target_duration * 100.0
                         WHEN t.business_duration <> 0 THEN 100.0
                         ELSE 0.0 END AS v) raw
          ) pct
         WHERE pct.id = sla_task.id
    """)
    cr.execute("""
        UPDATE sla_task t
           SET sla_type = d.type, sla_target = d.target
          FROM sla_definition d
         WHERE d.id = t.sla_id
    """)
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute("SELECT id FROM sla_task WHERE source_name IS NULL ORDER BY id")
    ids = [row[0] for row in cr.fetchall()]
    for i in range(0, len(ids), BATCH):
        env['sla.task'].browse(ids[i:i + BATCH])._refresh_source_names()
        env['sla.task'].flush(['source_name'])
        env['sla.task'].invalidate_cache()
