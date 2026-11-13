# Changelog `dwo_sla_core`

Ghi tóm tắt cải tiến để AI agent cập nhật lại docs 010-070 sau (docs chưa được sửa theo các mục dưới đây).

## 2026-11-13 - 15.0.1.2.2: báo cáo (field lưu C1, 10 màn hình C2, màu và trục % task 023, đường không xếp chồng task 029) (task 006 C5c-1)

Port từ bản 16 (16.0.1.2.2) sang bản 15. Chưa có dashboard Overview và CHƯA port bản sửa hook task 027. Chi tiết field/màn hình/bộ lọc/đánh đổi: xem changelog bản 17 và 19 (cùng nội dung) và bản 16.

### Có trong bản này
- Field lưu mới trên `sla.task`: `outcome`, `final_percent_used`, `usage_bucket`, `overdue_duration`, `source_name` (chỉ SLA Manager), `sla_type`, `sla_target`; `migrations/15.0.1.2.0/post-migrate.py` (SQL + ORM theo lô, idempotent; dùng `flush()` / `invalidate_cache()` của Odoo 15; thư mục giữ tên 15.0.1.2.0 để chạy khi nâng từ 1.1.x). Trung bình `final_percent_used`/`overdue_duration` chỉ tính task đã kết thúc: trong `read_group` ghi đè sẵn có (giống `achieved_rate`).
- Menu SLA > Reporting 10 màn hình (`views/sla_report_views.xml`), view graph/pivot cho `sla.event`, bộ lọc và group-by mới, ja_JP.
- `static/src/graph_colors/sla_graph_colors.js` (bundle `web.assets_backend`, module ES `@odoo-module`): vá `GraphRenderer` của `@web/views/graph/graph_renderer` bằng `patch(obj, "tên", {...})` + `this._super`: màu cố định theo giá trị outcome/stage/usage_bucket/event, thứ tự xếp chồng, pie theo selection, `formatValue` phần trăm cho `achieved_rate` (graph 15 không đọc `widget` của measure).

### Khác biệt API
- Odoo 15 đã có graph/pivot Owl mới (`@web/views/graph/*`, Chart.js 2.9.4) nằm trong `web.assets_backend`; graph legacy (`web.GraphView`, bundle `web.assets_backend_legacy_lazy`) chỉ còn cho wrapper cũ và KHÔNG được dùng cho view thường: patch legacy không có tác dụng (đã đo). `formatPercentage` ở `@web/fields/formatters` (16: `@web/views/fields/formatters`).
- Odoo 15 không có `get_views`/`get_view`/`flush_all`/`invalidate_recordset`: test dùng `fields_view_get`, `env['base'].flush()`, `invalidate_cache()`; `_fgroup` dùng `read_group(..., lazy=False)`.
- Tour viết `odoo.define` + `web_tour.tour` (style legacy như các tour khác của module), tìm biểu đồ bằng `Chart.instances` (Chart.js 2.9), nút apps menu `.o_navbar_apps_menu .dropdown-toggle`.

### Test
`tests/test_tg33_reporting_fields.py` (13), `test_tg34_reporting_views.py` (16 + tour `dwo_sla_reporting_menu`, `dwo_sla_graph_colors`), `test_tg36_graph_colors.py` (5). Toàn module 476 test xanh; migration thật `sla_migration_check_120.py 15` PASS 15/15; thử tay Playwright (tz Europe/Brussels, 96 task seed): pie và bar đúng màu và thứ tự, trục 0-100%.

## 2026-11-13 - 15.0.1.1.1: reset theo field lưu ghi được không bắn hai lần (task 025)

Bản 15 (port từ 19.0.1.2.1, task 025). Sửa lỗi, không đổi field/view/migration.

### Điều kiện tái hiện
Field lưu có compute và ghi tay được (ví dụ `sale.order.validity_date`, `compute` phụ thuộc `company_id`, `store`, `readonly=False`), định nghĩa có `reset_field_ids` chứa field đó. Trong CÙNG giao dịch: (1) ghi field nguồn (ví dụ đổi `company_id`) nên field lưu chờ tính lại (tính lười), (2) ghi tay field lưu, chưa flush/đọc ở giữa. Kết quả cũ: hai event `reset`, ba task. Không tái hiện khi chỉ ghi tay một lần, ghi qua Form, ghi cả hai trong một lệnh `write`, hay `reset_action` khác (`cancel`/`complete` đều như nhau).

### Nguyên nhân
Hook `write` đọc giá trị cũ (`record[name]`) TRƯỚC khi ghi. Đọc field lưu đang chờ tính lại ép ORM tính ngay, tức gọi `_compute_field_value` giữa chừng: hook compute đánh giá với `changed={validity_date}` (reset lần 1, trước cả khi lần ghi được áp dụng), rồi sau khi ghi hook `write` đánh giá lại (reset lần 2). Lần ghi tay thay đúng giá trị đó nên tính lại là thừa.

### Cách sửa
`sla_hook.make_write`: với field lưu tính được đang chờ tính lại trên các record sắp ghi, tạm bỏ cờ chờ tính (`env.remove_to_compute`) khi đọc giá trị cũ (đọc giá trị đang lưu, không ép tính), rồi đặt lại cờ (`add_to_compute`) để ORM tự xử lý khi ghi. Dùng API Odoo 15 (`env.records_to_compute`, `remove_to_compute`, `add_to_compute` trong `odoo/api.py`, `env.all.tocompute`), cùng tên với 19.

### Hành vi còn lại (đúng thiết kế)
Hai thay đổi thật vẫn cho hai reset: đổi `company_id` rồi flush (field tính lại đổi giá trị: một reset) rồi ghi tay field đó (reset thứ hai).

### Test
`tests/test_tg35_reset_writable_compute.py` (7 test): `test_rst_005` đã đo đỏ với code cũ, xanh sau khi sửa (ba task, hai reset).
