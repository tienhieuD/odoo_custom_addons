# Changelog `dwo_sla_core`

Ghi tóm tắt cải tiến để AI agent cập nhật lại docs 010-070 sau (docs chưa được sửa theo các mục dưới đây).

## 2026-11-13 - 16.0.1.2.4: hook không cài hai lớp, reset không bắn hai lần (task 028, port từ 17.0.1.2.4)

Sửa lỗi, không đổi field/view/migration.

### Lỗi và nguyên nhân
Định nghĩa SLA tạo/sửa TRONG LÚC nạp module (data/demo của module cài hoặc nâng cấp): `_register_sla_hook` chạy giữa chừng, rồi bước cuối `load_modules` gọi `_register_hook` MỘT LẦN NỮA mà không gỡ trước. `patch()` (`models/sla_hook.py`) lấy `origin = getattr(model_class, name)` mà không bóc lớp patch của ta, nên `create`, `write`, `_compute_field_value` bị hai lớp hook chồng nhau: một lần `write` field reset ra 2 lần `sla.engine._reset` (3 task thay vì 2). Khởi động lại server thì chỉ một lớp.

### Sửa
Trong `patch()` bóc mọi lớp có `sla_patch` khỏi `origin` trước khi gán (vòng `while`, Python thuần, không phụ thuộc API). Không đổi Engine.

### Test
`tests/test_tg35_reset_writable_compute.py`: `test_rst_008` (mỗi hàm đúng một lớp sau `_register_hook` lần hai), `test_rst_009` (một lần sửa field reset: 1 reset, 2 task). Chạy trước khi sửa: đỏ cả hai; sau khi sửa: xanh.

## 2026-11-13 - 16.0.1.2.2: báo cáo (field lưu C1, 10 màn hình C2, màu và trục % task 023, đường không xếp chồng task 029) (task 006 C5c-1)

Port từ bản 17 (17.0.1.2.1 + 17.0.1.2.2 + 17.0.1.2.3) sang bản 16 gộp một lần. Chưa có dashboard Overview (`dwo_sla_dashboard`) và CHƯA port bản sửa hook task 027. Chi tiết field/màn hình/bộ lọc/đánh đổi: xem changelog bản 17 và 19 (cùng nội dung).

### Có trong bản này
- Field lưu mới trên `sla.task`: `outcome`, `final_percent_used`, `usage_bucket`, `overdue_duration`, `source_name` (chỉ SLA Manager), `sla_type`, `sla_target`; `migrations/16.0.1.2.0/post-migrate.py` (SQL + ORM theo lô, idempotent; thư mục giữ tên 16.0.1.2.0 để chạy khi nâng từ 1.1.x).
- Menu SLA > Reporting 10 màn hình (`views/sla_report_views.xml`: `<tree>`, `invisible="1"` thay `column_invisible`), view graph/pivot cho `sla.event`, bộ lọc và group-by mới trong search view `sla.task`/`sla.event`, ja_JP.
- `static/src/graph_colors/sla_graph_colors.js` (bundle `web.assets_backend`): vá `GraphRenderer` bằng `patch(obj, "tên", {...})` và `this._super` (Odoo 16 dùng cú pháp patch cũ); màu cố định theo giá trị outcome/stage/usage_bucket/event, thứ tự xếp chồng theo selection, pie theo selection, `formatValue` phần trăm cho `achieved_rate` (graph 16 không đọc `widget` của measure). `stacked="0"` cho R2 và R9.

### Khác biệt API so với bản 17
- Odoo 16 không có `_read_group_select` (17+): trung bình `final_percent_used`/`overdue_duration` (chỉ task đã kết thúc) làm trong `read_group` ghi đè sẵn có (cùng chỗ `achieved_rate`, thêm một `read_group` phụ cho mỗi nhóm); đã sửa `row['__domain']` không có khi `groupby` rỗng.
- Test: không có `formatted_read_group` / `_read_group(domain, groupby, aggregates)`; helper `_fgroup` dùng `read_group(..., lazy=False)`. Chart.js 2.9.4: tour tìm biểu đồ bằng `Chart.instances` (không có `Chart.getChart`), trục `options.scales.yAxes[0]`, `chart.scales['y-axis-0']`; breadcrumb `.breadcrumb-item.active`, dropdown `.dropdown-menu .dropdown-item`.

### Test
`tests/test_tg33_reporting_fields.py` (13), `test_tg34_reporting_views.py` (16 + tour `dwo_sla_reporting_menu`, `dwo_sla_graph_colors`), `test_tg36_graph_colors.py` (5); toàn module 476 test xanh. Migration thật `sla_migration_check_120.py 16`: PASS 15/15. Thử tay Playwright (tz Europe/Brussels, 96 task seed): Status Mix và Compliance Trend đúng màu, trục 0-100%.

## 2026-11-13 - 16.0.1.1.1: reset theo field lưu ghi được không bắn hai lần (task 025)

Bản 16 (port từ 19.0.1.2.1, task 025). Sửa lỗi, không đổi field/view/migration.

### Điều kiện tái hiện
Field lưu có compute và ghi tay được (ví dụ `sale.order.validity_date`, `compute` phụ thuộc `company_id`, `store`, `readonly=False`), định nghĩa có `reset_field_ids` chứa field đó. Trong CÙNG giao dịch: (1) ghi field nguồn (ví dụ đổi `company_id`) nên field lưu chờ tính lại (tính lười), (2) ghi tay field lưu, chưa flush/đọc ở giữa. Kết quả cũ: hai event `reset`, ba task. Không tái hiện khi chỉ ghi tay một lần, ghi qua Form, ghi cả hai trong một lệnh `write`, hay `reset_action` khác (`cancel`/`complete` đều như nhau).

### Nguyên nhân
Hook `write` đọc giá trị cũ (`record[name]`) TRƯỚC khi ghi. Đọc field lưu đang chờ tính lại ép ORM tính ngay, tức gọi `_compute_field_value` giữa chừng: hook compute đánh giá với `changed={validity_date}` (reset lần 1, trước cả khi lần ghi được áp dụng), rồi sau khi ghi hook `write` đánh giá lại (reset lần 2). Lần ghi tay thay đúng giá trị đó nên tính lại là thừa.

### Cách sửa
`sla_hook.make_write`: với field lưu tính được đang chờ tính lại trên các record sắp ghi, tạm bỏ cờ chờ tính (`env.remove_to_compute`) khi đọc giá trị cũ (đọc giá trị đang lưu, không ép tính), rồi đặt lại cờ (`add_to_compute`) để ORM tự xử lý khi ghi. Dùng API Odoo 16 (`env.records_to_compute`, `remove_to_compute`, `add_to_compute` trong `odoo/api.py`, `env.all.tocompute`), cùng tên với 19.

### Hành vi còn lại (đúng thiết kế)
Hai thay đổi thật vẫn cho hai reset: đổi `company_id` rồi flush (field tính lại đổi giá trị: một reset) rồi ghi tay field đó (reset thứ hai).

### Test
`tests/test_tg35_reset_writable_compute.py` (7 test): `test_rst_005` đã đo đỏ với code cũ, xanh sau khi sửa (ba task, hai reset).
