# Changelog `dwo_sla_core`

Ghi tóm tắt cải tiến để AI agent cập nhật lại docs 010-070 sau (docs chưa được sửa theo các mục dưới đây).

## 2026-11-13 - 12.0.1.1.1: hook không cài hai lớp (task 028; task 025 không áp dụng cho 12)

Sửa lỗi, không đổi field/view/migration.

### Lỗi 2 (task 028): hook cài hai lớp
Định nghĩa SLA tạo/sửa TRONG LÚC nạp module (data/demo): `_register_sla_hook` chạy giữa chừng, rồi bước cuối `load_modules` gọi `_register_hook` lần nữa mà không gỡ trước. `patch()` lấy `origin = getattr(model_class, name)` mà không bóc lớp patch của ta nên `create`, `write`, `_write` (bản 12 không có `_compute_field_value`) bị hai lớp chồng nhau: một lần `write` field reset ra nhiều reset hơn (đo: 4 task, 3 reset thay vì 2 task, 1 reset). Khởi động lại server thì chỉ một lớp.
Sửa (`models/sla_hook.py`, `patch()`): bóc mọi lớp có `sla_patch` khỏi `origin` trước khi gán (vòng `while`, Python thuần).

### Lỗi 1 (task 025): không áp dụng cho Odoo 12
Odoo 12 tính lại field lưu NGAY cuối mỗi `write` (hàng đợi `env.all.todo`, không tính lười tới flush như 13+), nên hai lần `write` liên tiếp (field nguồn rồi field lưu) không có trạng thái "đang chờ tính lại" ở giữa: lần ghi thứ hai thấy giá trị đã tính, hai reset là hai thay đổi thật. Đã đo: `test_rst_005` ở 12 cho 3 task, 2 reset với code cũ và vẫn đúng hành vi. Không sửa code.
Ghi chú (chưa sửa, ngoài phạm vi): trong `with env.norecompute():` ghi field nguồn rồi field khác, hook `write` ở 12 đọc các field lưu tính được đang theo dõi trước và sau khi ghi nên có thể bắn thừa reset; kịch bản hiếm, chưa có yêu cầu.

### Test
`tests/test_tg35_reset_writable_compute.py` (9 test, `SavepointCase`; field thử dùng `selection` dạng chuỗi; không có flush ở 12; `test_rst_005` kỳ vọng (3 task, 2 reset) vì 12 tính lại ngay; `test_rst_008` đếm lớp của `create`, `write`, `_write`). Chạy trước khi sửa: đỏ `test_rst_008`, `test_rst_009`; sau khi sửa: xanh.
