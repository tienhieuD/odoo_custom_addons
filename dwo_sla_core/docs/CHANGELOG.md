# Changelog `dwo_sla_core`

Ghi tóm tắt cải tiến để AI agent cập nhật lại docs 010-070 sau (docs chưa được sửa theo các mục dưới đây).

## 2026-11-13 - 13.0.1.1.1: reset không bắn hai lần (task 025 + task 028, port từ 14.0.1.1.1/14.0.1.2.4)

Sửa hai lỗi, không đổi field/view/migration.

### Lỗi 1 (task 025): field lưu tính được đang chờ tính lại
Điều kiện: field lưu có compute và ghi tay được (ví dụ `sale.order.validity_date`), định nghĩa có `reset_field_ids` chứa field đó; trong CÙNG giao dịch ghi field nguồn (field lưu chờ tính lại) rồi ghi tay field lưu, chưa flush. Kết quả cũ: hai event `reset`, ba task thay vì hai.
Nguyên nhân: hook `write` đọc giá trị cũ (`record[name]`) trước khi ghi; đọc field đang chờ tính ép ORM tính ngay, tức gọi `_compute_field_value` giữa chừng (reset lần 1), rồi hook `write` đánh giá lại sau khi ghi (reset lần 2).
Sửa (`models/sla_hook.py`, `make_write`): tạm bỏ cờ chờ tính khi đọc giá trị cũ rồi đặt lại. Odoo 13 dùng đúng API như 14: `env.records_to_compute(field)`, `env.remove_to_compute`, `env.add_to_compute` (`env.all.tocompute`).

### Lỗi 2 (task 028): hook cài hai lớp
Định nghĩa SLA tạo/sửa TRONG LÚC nạp module (data/demo): `_register_sla_hook` chạy giữa chừng, rồi bước cuối `load_modules` gọi `_register_hook` lần nữa mà không gỡ trước. `patch()` lấy `origin = getattr(model_class, name)` mà không bóc lớp patch của ta nên `create`, `write`, `_compute_field_value` bị hai lớp chồng nhau: một lần `write` field reset ra 2 reset (3 task thay vì 2). Khởi động lại server thì chỉ một lớp.
Sửa: trong `patch()` bóc mọi lớp có `sla_patch` khỏi `origin` trước khi gán (vòng `while`, Python thuần).

### Test
`tests/test_tg35_reset_writable_compute.py` (9 test, `SavepointCase`, `env['base'].flush()`). Chạy trước khi sửa: đỏ `test_rst_005`, `test_rst_008`, `test_rst_009`; sau khi sửa: xanh.
