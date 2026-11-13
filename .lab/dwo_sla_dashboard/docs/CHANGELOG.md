# Changelog `dwo_sla_dashboard`

Ghi tóm tắt để AI agent viết docs sau (module chưa có docs 010-070). Module đặt trong `.lab/` (chưa bán). Bản 19 là gốc; port sang 20, 18, 17 ở đầu file này (task 006 C5b).

## 2026-11-13 - 17.0.1.0.0, giai đoạn C5b của task 006: port từ bản 19

- Phụ thuộc `dwo_sla_core` 17.0.1.2.2. Python giữ nguyên (`_read_group(domain, groupby, aggregates)`, `search_fetch` có ở 17).
- `Dropdown` của 17 khác 18/19: nút bật là slot `toggler` (có `togglerClass`, không phải phần tử con mặc định), danh sách là slot `default` (không có `content`), `DropdownItem` dùng `parentClosingMode="'none'"` (thay `closingMode`).
- Tour: `/** @odoo-module **/` ở đầu, bước chỉ chờ phải có `run: () => {}`; test dùng `start_tour('/web', ...)` và `browser_size = "1366,768"`.
- Test: người dùng thử (SLA User/Manager) phải thêm `base.group_user`: `_read_group` theo tuần đọc `res.lang` (`get_lang(env).week_start`) bằng quyền của người dùng; ở 17 người chỉ thuộc nhóm SLA (không phải Internal User) bị AccessError ('Languages'); 18/19/20 không bị. Người dùng backend thật luôn là Internal User nên không ảnh hưởng.
- 16 test (14 Python + 2 tour) xanh. 10.000 task: 0.03 giây, 32 truy vấn.
- Thử tay Playwright (92 task seed, tz admin Asia/Ho_Chi_Minh): màu lát donut/đoạn thanh = rgb(47,158,99) / rgb(240,140,0) / rgb(214,51,74); không lỗi console; menu chọn định nghĩa (toggler), lọc 7 ngày, giao diện hẹp đúng.

## 2026-11-13 - 19.0.1.0.0, giai đoạn C3 của task 006: màn hình SLA Overview

### Thêm mới
- Module riêng `dwo_sla_dashboard`, phụ thuộc `dwo_sla_core` (>= 19.0.1.2.0, dùng `outcome`, `sla_type`, `sla_target`), license OPL-1, chưa có `price`/listing.
- Client action OWL `dwo_sla_dashboard.overview` (xml id `dwo_sla_dashboard.action_sla_overview`) và menu `Overview` đầu tiên của app SLA (sequence 1, nhóm `group_sla_user`). Chỉ đọc; không có model/field mới.
- RPC duy nhất `sla.task.get_dashboard_data(period=30, filters=None)` (thêm bằng `_inherit` trong `models/sla_task.py`), không `sudo`: record rule và đa công ty (theo `allowed_company_ids`) áp dụng như danh sách thường. `period` thuộc {7, 30, 90}, giá trị khác về 30; `filters` = `{sla_type, sla_target, sla_ids}` được làm sạch phía server.

### Số liệu
- Thẻ "stock" (tình trạng hiện tại, không phụ thuộc kỳ): Running (stage in_progress), Due soon (field `is_due_soon` của core, ngưỡng theo định nghĩa), Breached (`outcome = breached_open`).
- Thẻ "flow" theo kỳ, tính trên task KẾT THÚC trong kỳ (`end_time`): Achieved rate (`achieved_rate:avg`, hiển thị %), Late (`outcome = late`).
- Chỉ báo so với kỳ trước: flow = kỳ liền kề cùng độ dài; stock = ảnh chụp XẤP XỈ tại đầu kỳ từ `start_time`/`end_time`/`planned_end_time` (task mở tại thời điểm đó; Breached: hạn `planned_end_time` đã qua; Due soon: hạn nằm trong ngưỡng giờ). Không có lịch sử trạng thái nên pause/resume làm lệch số (đánh đổi). Mũi tên xanh/đỏ theo hướng tốt (tăng là tốt chỉ với Achieved rate).
- Biểu đồ dùng phạm vi "task đang mở + task kết thúc trong kỳ": donut `outcome`, thanh xếp chồng đúng hạn/trễ/vi phạm theo định nghĩa (tối đa 10, nhiều nhất trước), đường % đạt theo tuần (`end_time:week`, tối đa 12 tuần, tuần trống là điểm đứt; nếu PostgreSQL không nhận múi giờ người dùng, vd. `Asia/Saigon` trong Docker, tự lùi về UTC).
- "Needs attention": 10 task mở vi phạm hoặc sắp đến hạn (vi phạm trước, hạn sớm trước). `source_name` CHỈ có trong payload khi người dùng là SLA Manager; user thường chỉ có định nghĩa và tên model. Bấm dòng mở form `sla.task`.
- Drill-down: server trả `domain` cho từng thẻ, `scope_domain` cho biểu đồ (client chỉ nối thêm điều kiện `outcome`/`sla_id`), mở bằng cấu hình action `dwo_sla_core.action_sla_task` (view list/form/pivot/graph, bỏ search_default).
- Bộ lọc nhanh: SLA/OLA, Response/Resolution, nhiều định nghĩa; áp cho mọi thẻ và biểu đồ.

### Giao diện
SVG/CSS thuần OWL (không Chart.js). Màu: xanh đúng hạn, cam trễ, đỏ vi phạm, xám đang chạy/tạm dừng/huỷ. Dùng biến Bootstrap của Odoo (`--bs-body-bg`...) nên tự theo dark mode (Odoo Community 19 không có dark mode, chưa kiểm). Responsive: 5 thẻ, 3, rồi 1 cột. Trạng thái rỗng: chưa có dữ liệu và "không khớp bộ lọc".

### Hiệu năng
10 000 task (6 loại outcome, 2 định nghĩa), kỳ 90 ngày: 0.03 giây, 38 truy vấn (ngưỡng test < 1 giây, < 50 truy vấn). Test `dash_perf`.

### Test (16, tag `dwo_sla_dashboard`)
`tests/test_dashboard_data.py`: thẻ, domain khớp số đếm, kỳ trước, kỳ 7/30/90, bộ lọc (kể cả giá trị rác), biểu đồ, danh sách chú ý và giới hạn 10, quyền SLA User/Manager (không lộ `source_name`), người không thuộc nhóm bị AccessError, đa công ty, rỗng, ngưỡng due soon mặc định, hiệu năng. `tests/test_overview_tour.py`: tour `dwo_sla_overview` (mở app SLA, kiểm giá trị thẻ, bấm thẻ/lát donut/cột và đếm dòng danh sách, lọc OLA, 7 ngày, mở form) và `dwo_sla_overview_empty`; lỗi JS console làm tour đỏ.

### i18n
`i18n/ja_JP.po`: toàn bộ chuỗi giao diện.

### Chưa làm
Ảnh chụp (C4, lưu ở module demo), port sang bản khác (C5), docs, listing.
