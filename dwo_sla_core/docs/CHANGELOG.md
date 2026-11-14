# Changelog `dwo_sla_core`

Ghi tóm tắt cải tiến để AI agent cập nhật lại docs 010-070 sau (docs chưa được sửa theo các mục dưới đây).

## 2026-11-14 - 14.0.1.2.5: nút Running Tasks mở đúng tập task đang chạy (task 037)

Chỉ đổi `action_view_tasks`; không đổi field, view, dữ liệu hay migration.

### Nguyên nhân
`action_view_tasks` lấy action `action_sla_task` (context mặc định `search_default_in_progress` + `search_default_paused`) rồi GHI ĐÈ `context = {}`, nên bộ lọc mặc định biến mất và danh sách hiện mọi task của định nghĩa (24) trong khi nút ghi `running_task_count` (8). Test cũ `test_action_opens_all_tasks_of_definition` còn khẳng định `context == {}` (thiết kế ban đầu: mở cả lịch sử). Số 8 và 7 khớp nhau: 8 = 7 `in_progress` + 1 `paused`; ảnh chụp chỉ bật thêm bộ lọc In Progress (7), còn Paused 1 task không hiện.

### Quyết định
"Running" của nhãn/đếm gồm `in_progress` và `paused` (như help của field và filter "Open"). Giữ nguyên nhãn và cách đếm; sửa action cho khớp: domain chỉ giới hạn theo định nghĩa, context giữ facet mặc định In Progress + Paused của action gốc (cùng tập với `running_task_count`), nên bỏ facet là thấy cả task đã xong. Không dùng domain cứng để không mất khả năng xem lịch sử. Đổi nhãn thành "Open" không chọn vì đổi chuỗi dịch/ảnh listing. Chưa đổi "Running" thành chỉ in_progress vì form còn dùng số này để cảnh báo khi lưu (cần cả paused).

### Test
`tests/test_tg26_definition_ux.py::TestSmartButton::test_action_opens_definition_tasks_with_running_filter` (thay `test_action_opens_all_tasks_of_definition`): action có facet mặc định, áp các filter đó lên search view cho đúng số task bằng `running_task_count`, domain vẫn gồm cả task đã xong. Đỏ trước khi sửa, xanh sau.

## 2026-11-13 - 14.0.1.2.4: hook không cài hai lớp, reset không bắn hai lần (task 028, port từ 17.0.1.2.4)

Sửa lỗi, không đổi field/view/migration.

### Lỗi và nguyên nhân
Định nghĩa SLA tạo/sửa TRONG LÚC nạp module (data/demo của module cài hoặc nâng cấp): `_register_sla_hook` chạy giữa chừng, rồi bước cuối `load_modules` gọi `_register_hook` MỘT LẦN NỮA mà không gỡ trước. `patch()` (`models/sla_hook.py`) lấy `origin = getattr(model_class, name)` mà không bóc lớp patch của ta, nên `create`, `write`, `_compute_field_value` bị hai lớp hook chồng nhau: một lần `write` field reset ra 2 lần `sla.engine._reset` (3 task thay vì 2). Khởi động lại server thì chỉ một lớp.

### Sửa
Trong `patch()` bóc mọi lớp có `sla_patch` khỏi `origin` trước khi gán (vòng `while`, Python thuần, không phụ thuộc API). Không đổi Engine.

### Test
`tests/test_tg35_reset_writable_compute.py`: `test_rst_008` (mỗi hàm đúng một lớp sau `_register_hook` lần hai), `test_rst_009` (một lần sửa field reset: 1 reset, 2 task). Chạy trước khi sửa: đỏ cả hai; sau khi sửa: xanh.

## 2026-11-13 - 14.0.1.2.2: báo cáo (field lưu C1, 10 màn hình C2, màu và trục % task 023, đường không xếp chồng task 029) (task 006 C5c-1)

Port từ bản 15/16 sang bản 14. Chưa có dashboard Overview và CHƯA port bản sửa hook task 027. Chi tiết field/màn hình/bộ lọc/đánh đổi: xem changelog bản 17, 19 và 16.

### Có trong bản này
- Field lưu mới trên `sla.task`: `outcome`, `final_percent_used`, `usage_bucket`, `overdue_duration`, `source_name` (chỉ SLA Manager), `sla_type`, `sla_target`; `migrations/14.0.1.2.0/post-migrate.py` (SQL + ORM theo lô, idempotent; `flush()`/`invalidate_cache()`; thư mục giữ tên 14.0.1.2.0 để chạy khi nâng từ 1.1.x). Trung bình `final_percent_used`/`overdue_duration` chỉ tính task đã kết thúc: trong `read_group` ghi đè sẵn có.
- Menu SLA > Reporting 10 màn hình (`views/sla_report_views.xml`), view graph/pivot cho `sla.event`, bộ lọc và group-by mới, ja_JP.
- `static/src/graph_colors/sla_graph_colors.js` (khai báo trong `views/assets.xml`, `odoo.define`): graph 14 là widget legacy (`web.GraphRenderer`); `GraphRenderer.include` ghi đè `_prepareData` (sắp series/lát pie theo thứ tự selection, nhớ màu theo chỉ số), `_getColor(index)` (trả màu cố định theo giá trị outcome/stage/usage_bucket/event) và `_formatValue` (phần trăm cho `achieved_rate`, graph 14 không đọc `widget`). Nhận diện field theo tên + tập khoá selection vì renderer legacy không biết model.

### Khác biệt API
- Nhãn lát pie của graph legacy là mảng (một phần tử mỗi group-by), tour phải `join`. Apps menu 14: `.o_menu_apps a.full`; tour `odoo.define` + `web_tour.tour`, biểu đồ qua `Chart.instances` (Chart.js 2.9).
- Không có `get_views`/`flush_all`/`invalidate_recordset`: test dùng `fields_view_get`, `env['base'].flush()`, `invalidate_cache()`; `_fgroup` dùng `read_group(..., lazy=False)`. Assets qua `views/assets.xml` (test kiểm file này thay vì manifest).

### Test
`tests/test_tg33_reporting_fields.py` (13), `test_tg34_reporting_views.py` (16 + tour `dwo_sla_reporting_menu`, `dwo_sla_graph_colors`), `test_tg36_graph_colors.py` (5). Toàn module 476 test xanh; migration thật `sla_migration_check_120.py 14` PASS 15/15; thử tay Playwright (tz Europe/Brussels, 96 task seed): pie và bar đúng màu và thứ tự, trục 0-100%.

## 2026-11-13 - 14.0.1.1.1: reset theo field lưu ghi được không bắn hai lần (task 025)

Bản 14 (port từ 19.0.1.2.1, task 025). Sửa lỗi, không đổi field/view/migration.

### Điều kiện tái hiện
Field lưu có compute và ghi tay được (ví dụ `sale.order.validity_date`, `compute` phụ thuộc `company_id`, `store`, `readonly=False`), định nghĩa có `reset_field_ids` chứa field đó. Trong CÙNG giao dịch: (1) ghi field nguồn (ví dụ đổi `company_id`) nên field lưu chờ tính lại (tính lười), (2) ghi tay field lưu, chưa flush/đọc ở giữa. Kết quả cũ: hai event `reset`, ba task. Không tái hiện khi chỉ ghi tay một lần, ghi qua Form, ghi cả hai trong một lệnh `write`, hay `reset_action` khác (`cancel`/`complete` đều như nhau).

### Nguyên nhân
Hook `write` đọc giá trị cũ (`record[name]`) TRƯỚC khi ghi. Đọc field lưu đang chờ tính lại ép ORM tính ngay, tức gọi `_compute_field_value` giữa chừng: hook compute đánh giá với `changed={validity_date}` (reset lần 1, trước cả khi lần ghi được áp dụng), rồi sau khi ghi hook `write` đánh giá lại (reset lần 2). Lần ghi tay thay đúng giá trị đó nên tính lại là thừa.

### Cách sửa
`sla_hook.make_write`: với field lưu tính được đang chờ tính lại trên các record sắp ghi, tạm bỏ cờ chờ tính (`env.remove_to_compute`) khi đọc giá trị cũ (đọc giá trị đang lưu, không ép tính), rồi đặt lại cờ (`add_to_compute`) để ORM tự xử lý khi ghi. Dùng API Odoo 14 (`env.records_to_compute`, `remove_to_compute`, `add_to_compute` trong `odoo/api.py`, `env.all.tocompute`), cùng tên với 19.

### Hành vi còn lại (đúng thiết kế)
Hai thay đổi thật vẫn cho hai reset: đổi `company_id` rồi flush (field tính lại đổi giá trị: một reset) rồi ghi tay field đó (reset thứ hai).

### Test
`tests/test_tg35_reset_writable_compute.py` (7 test): `test_rst_005` đã đo đỏ với code cũ, xanh sau khi sửa (ba task, hai reset).
