# Changelog `dwo_sla_core`

Ghi tóm tắt cải tiến để AI agent cập nhật lại docs 010-070 sau (docs chưa được sửa theo các mục dưới đây).

## 2026-11-14 - 13.0.1.2.6: nhãn nút "Running Tasks" đổi thành "Open Tasks" (issue 5)

Chỉ đổi nhãn: số đếm `running_task_count` gồm cả task `in_progress` và `paused` nên "Running" không đúng nghĩa. Giữ nguyên tên kỹ thuật `running_task_count` (tránh migration), cách đếm, action và dữ liệu.
- Đổi `string` của field `running_task_count` ở `models/sla_definition.py` và của field trên smart button ở `views/sla_definition_views.xml` thành "Open Tasks".
- Bản dịch `i18n/ja_JP.po` (bản dịch duy nhất của module): "Open Tasks" -> 未完了のタスク (trước: 実行中のタスク). Không có .pot / ngôn ngữ khác.
- Listing (`static/description/index.html`, `_listings/dwo_sla_core.json`, duotek): sửa chữ "Running Tasks" thành "Open Tasks". Ảnh listing chưa chụp lại (vẫn ghi cũ), chụp ở lần cập nhật listing kế tiếp.
- Test mới: `test_button_label_is_open_tasks` (tg26). Docs 010-070 còn nhắc "Running Tasks" (REQ-INT-025, TC-SBT-003, FT-21...), cập nhật sau.

## 2026-11-14 - 13.0.1.2.5: nút Running Tasks mở đúng tập task đang chạy (task 037)

Chỉ đổi `action_view_tasks`; không đổi field, view, dữ liệu hay migration.

### Nguyên nhân
`action_view_tasks` lấy action `action_sla_task` (context mặc định `search_default_in_progress` + `search_default_paused`) rồi GHI ĐÈ `context = {}`, nên bộ lọc mặc định biến mất và danh sách hiện mọi task của định nghĩa (24) trong khi nút ghi `running_task_count` (8). Test cũ `test_action_opens_all_tasks_of_definition` còn khẳng định `context == {}` (thiết kế ban đầu: mở cả lịch sử). Số 8 và 7 khớp nhau: 8 = 7 `in_progress` + 1 `paused`; ảnh chụp chỉ bật thêm bộ lọc In Progress (7), còn Paused 1 task không hiện.

### Quyết định
"Running" của nhãn/đếm gồm `in_progress` và `paused` (như help của field và filter "Open"). Giữ nguyên nhãn và cách đếm; sửa action cho khớp: domain chỉ giới hạn theo định nghĩa, context giữ facet mặc định In Progress + Paused của action gốc (cùng tập với `running_task_count`), nên bỏ facet là thấy cả task đã xong. Không dùng domain cứng để không mất khả năng xem lịch sử. Đổi nhãn thành "Open" không chọn vì đổi chuỗi dịch/ảnh listing. Chưa đổi "Running" thành chỉ in_progress vì form còn dùng số này để cảnh báo khi lưu (cần cả paused).

### Test
`tests/test_tg26_definition_ux.py::TestSmartButton::test_action_opens_definition_tasks_with_running_filter` (thay `test_action_opens_all_tasks_of_definition`): action có facet mặc định, áp các filter đó lên search view cho đúng số task bằng `running_task_count`, domain vẫn gồm cả task đã xong. Đỏ trước khi sửa, xanh sau.

## 2026-11-13 - 13.0.1.2.4: báo cáo (field lưu C1, 10 màn hình C2, màu và trục % task 023, đường không xếp chồng task 029) (task 006 C5c-2)

Port từ bản 14 sang bản 13. Chưa có dashboard Overview và CHƯA port bản sửa hook task 027. Chi tiết field/màn hình/bộ lọc/đánh đổi: xem changelog bản 19, 17 và 14.

### Có trong bản này
- Field lưu mới trên `sla.task`: `outcome`, `final_percent_used`, `usage_bucket`, `overdue_duration`, `source_name` (chỉ SLA Manager), `sla_type`, `sla_target`; `migrations/13.0.1.2.0/post-migrate.py` (SQL + ORM theo lô, idempotent; thư mục giữ tên 13.0.1.2.0 để chạy khi nâng từ 1.1.x). Trung bình `final_percent_used`/`overdue_duration` chỉ tính task đã kết thúc: trong `read_group` ghi đè sẵn có.
- Menu SLA > Reporting 10 màn hình (`views/sla_report_views.xml`), view graph/pivot cho `sla.event`, bộ lọc và group-by mới, ja_JP.
- `static/src/graph_colors/sla_graph_colors.js` (như bản 14: `GraphRenderer.include` ghi đè `_prepareData`, `_getColor`, `_formatValue`; graph legacy 13 giống 14).

### Khác biệt so với bản 14
- Cột trạng thái của list Backlog không có widget `badge` ở 13: màu theo hàng (`decoration-*` ở thẻ `<tree>`).
- Không có `ir.actions.actions._for_xml_id`: test dùng `browse(id).read()`.
- Tour: mỗi màn hình chờ breadcrumb của chính nó trước khi coi là đã hiển thị (tránh rời trang khi đang tải action).

### Test
`tests/test_tg33_reporting_fields.py`, `test_tg34_reporting_views.py` (+ tour `dwo_sla_reporting_menu`, `dwo_sla_graph_colors`), `test_tg36_graph_colors.py`.

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
