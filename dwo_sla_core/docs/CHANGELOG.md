# Changelog `dwo_sla_core`

Ghi tóm tắt cải tiến để AI agent cập nhật lại docs 010-070 sau (docs chưa được sửa theo các mục dưới đây).

## 2026-11-13 - 20.0.1.1.1: reset theo field lưu ghi được không bắn hai lần (task 025)

Bản 20 (port từ 19.0.1.2.1, task 025). Sửa lỗi, không đổi field/view/migration.

### Điều kiện tái hiện
Field lưu có compute và ghi tay được (ví dụ `sale.order.validity_date`, `compute` phụ thuộc `company_id`, `store`, `readonly=False`), định nghĩa có `reset_field_ids` chứa field đó. Trong CÙNG giao dịch: (1) ghi field nguồn (ví dụ đổi `company_id`) nên field lưu chờ tính lại (tính lười), (2) ghi tay field lưu, chưa flush/đọc ở giữa. Kết quả cũ: hai event `reset`, ba task. Không tái hiện khi chỉ ghi tay một lần, ghi qua Form, ghi cả hai trong một lệnh `write`, hay `reset_action` khác (`cancel`/`complete` đều như nhau).

### Nguyên nhân
Hook `write` đọc giá trị cũ (`record[name]`) TRƯỚC khi ghi. Đọc field lưu đang chờ tính lại ép ORM tính ngay, tức gọi `_compute_field_value` giữa chừng: hook compute đánh giá với `changed={validity_date}` (reset lần 1, trước cả khi lần ghi được áp dụng), rồi sau khi ghi hook `write` đánh giá lại (reset lần 2). Lần ghi tay thay đúng giá trị đó nên tính lại là thừa.

### Cách sửa
`sla_hook.make_write`: với field lưu tính được đang chờ tính lại trên các record sắp ghi, tạm bỏ cờ chờ tính (`env.remove_to_compute`) khi đọc giá trị cũ (đọc giá trị đang lưu, không ép tính), rồi đặt lại cờ (`add_to_compute`) để ORM tự xử lý khi ghi. Dùng API Odoo 20 (`env.records_to_compute`, `remove_to_compute`, `add_to_compute` trong `odoo/orm/environments.py`), cùng tên với 19.

### Hành vi còn lại (đúng thiết kế)
Hai thay đổi thật vẫn cho hai reset: đổi `company_id` rồi flush (field tính lại đổi giá trị: một reset) rồi ghi tay field đó (reset thứ hai).

### Test
`tests/test_tg35_reset_writable_compute.py` (7 test): `test_rst_005` đã đo đỏ với code cũ, xanh sau khi sửa (ba task, hai reset).
