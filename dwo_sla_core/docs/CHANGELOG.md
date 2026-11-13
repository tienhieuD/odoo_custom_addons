# Changelog `dwo_sla_core`

Ghi tóm tắt cải tiến để AI agent cập nhật lại docs 010-070 sau (docs chưa được sửa theo các mục dưới đây).

## 2026-11-13 - 19.0.1.2.1: reset theo field lưu ghi được không bắn hai lần (task 021)

Chỉ bản 19. Sửa lỗi, không đổi field/view/migration.

### Điều kiện tái hiện
Field lưu có compute và ghi tay được (ví dụ `sale.order.validity_date`, `compute` phụ thuộc `company_id`, `store`, `readonly=False`), định nghĩa có `reset_field_ids` chứa field đó. Trong CÙNG giao dịch: (1) ghi field nguồn (ví dụ đổi `company_id`) nên field lưu chờ tính lại (tính lười), (2) ghi tay field lưu, chưa flush/đọc ở giữa. Kết quả cũ: hai event `reset`, ba task. Không tái hiện khi chỉ ghi tay một lần, ghi qua Form, ghi cả hai trong một lệnh `write`, hay `reset_action` khác (`cancel`/`complete` đều như nhau).

### Nguyên nhân
Hook `write` đọc giá trị cũ (`record[name]`) TRƯỚC khi ghi. Đọc field lưu đang chờ tính lại ép ORM tính ngay, tức gọi `_compute_field_value` giữa chừng: hook compute đánh giá với `changed={validity_date}` (reset lần 1, trước cả khi lần ghi được áp dụng), rồi sau khi ghi hook `write` đánh giá lại (reset lần 2). Lần ghi tay thay đúng giá trị đó nên tính lại là thừa.

### Cách sửa
`sla_hook.make_write`: với field lưu tính được đang chờ tính lại trên các record sắp ghi, tạm bỏ cờ chờ tính (`env.remove_to_compute`) khi đọc giá trị cũ (đọc giá trị đang lưu, không ép tính), rồi đặt lại cờ (`add_to_compute`) để ORM tự xử lý khi ghi. Chỉ dùng API Odoo 19; các bản khác khi port cần dùng API tương đương.

### Hành vi còn lại (đúng thiết kế)
Hai thay đổi thật vẫn cho hai reset: đổi `company_id` rồi flush (field tính lại đổi giá trị: một reset) rồi ghi tay field đó (reset thứ hai).

### Test
`tests/test_tg35_reset_writable_compute.py` (7 test): `test_rst_005` đỏ khi bỏ bản sửa (ba task, hai reset). Gợi ý cho demo: tiêu chí S4 (`dwo_sla_demo`) có thể bật lại `reset_field_ids = validity_date` sau khi lên 19.0.1.2.1.

## 2026-11-12 - 19.0.1.2.0 (1.2.0), phần C1: field lưu cho báo cáo (task 006)

Chỉ bản 19. Chưa có view/menu (giai đoạn C2). Không đổi hành vi engine.

### Field mới trên `sla.task` (tất cả là field lưu, tính tự động)
| Field | Kiểu | Ý nghĩa |
|---|---|---|
| `outcome` (index) | Selection | `on_time` (stage achieved), `late` (stage breached, đã kết thúc sau hạn), `breached_open` (in_progress/paused và `has_breached`), `running`, `paused` (chưa vi phạm), `cancelled`. Phụ thuộc `stage`, `has_breached`. |
| `final_percent_used` | Float, aggregator avg | `business_duration / target_duration * 100` (không làm tròn); target 0 thì 100 nếu có thời gian trôi, 0 nếu không; task đã vi phạm không bao giờ dưới 100. Là giá trị LƯU (chốt lúc pause/complete), không cộng đoạn đang chạy. |
| `usage_bucket` | Selection | từ `final_percent_used`: `0_50` (<50), `50_75` (<75), `75_100` (<100), `100_150` (100 đến 150 gồm cả 150), `150_plus` (>150). |
| `overdue_duration` | Float, aggregator avg | giờ làm vượt mục tiêu (`business_duration - target_duration`, tối thiểu 0) khi `has_breached`, ngược lại 0. |
| `source_name` | Char | `display_name` của record nguồn (sudo), tính lúc tạo task; record/model không còn thì `model#id`. KHÔNG tự đổi khi record nguồn đổi tên; `_refresh_source_names()` làm mới, và nút "Apply Current Settings" gọi nó. |
| `sla_type`, `sla_target` (index) | Selection (related stored) | sao chép `type` (SLA/OLA) và `target` (Response/Resolution) của định nghĩa, tự cập nhật khi định nghĩa đổi. |

Không có `responsible_id` (người dùng đã bỏ).

### Đánh đổi và quyết định kỹ thuật
- `breached_open` thắng `paused`: task tạm dừng đã vi phạm tính là "vi phạm đang mở", khớp `breaching_count`.
- Trung bình `final_percent_used` và `overdue_duration` trong `_read_group_select` chỉ tính task đã kết thúc (achieved/breached), giống `achieved_rate`; task đang chạy/huỷ bị bỏ qua.
- Task đang chạy dùng giá trị lưu cũ (field lưu không biết "bây giờ"); báo cáo cần giá trị tức thời dùng `business_percent_used`/`*_live` (không lưu).
- `source_name` lưu tên record nguồn nên có `groups=group_sla_manager`: SLA User không đọc được (test TC-SEC-017 bắt được lộ tên record liên kết khác công ty). Báo cáo cho user thường nhóm theo `res_model`/định nghĩa.
- Tính `source_name` theo lô cho mỗi model, lỗi đọc tên không chặn tạo task.

### Migration
`migrations/19.0.1.2.0/post-migrate.py`: một câu SQL tính lại `outcome`, `final_percent_used`, `usage_bucket`, `overdue_duration`; một câu SQL điền `sla_type`/`sla_target`; `source_name` chỉ điền cho task còn trống, theo lô 2000 qua ORM. Idempotent.

### i18n
`i18n/ja_JP.po`: thêm tên, help và giá trị Selection của 7 field mới (bản 19 chỉ có ja_JP, không có vi_VN).

### Test
`tests/test_tg33_reporting_fields.py` (tag `tg_33`, 13 test): từng kết quả (đúng hạn, trễ, vi phạm đang mở, đang chạy, tạm dừng, huỷ), biên bucket, target 0, cập nhật khi pause/resume/complete, nhóm theo `outcome` và trung bình, `source_name`/`sla_type`/`sla_target`, migration tính lại trên task đã xoá giá trị (gọi trực tiếp hàm `migrate`, hai lần).

## 2026-11-13 - 19.0.1.2.0 (1.2.0), phần C2: màn hình báo cáo R2-R10 (task 006)

Chỉ bản 19, version giữ 19.0.1.2.0. Không đổi model/field/engine; chỉ view, menu, i18n, test. R1 Overview (OWL) là giai đoạn C3.

### Menu SLA > Reporting (nhóm `group_sla_user` thấy, chỉ đọc)
`menu_sla_reporting` (sequence 15) với 10 mục, mỗi mục là một `ir.actions.act_window` trong `views/sla_report_views.xml` (view riêng gắn qua `ir.actions.act_window.view`):

| Màn hình (action `action_sla_report_<key>`) | Model | View | Group-by / đo | Domain / lọc mặc định |
|---|---|---|---|---|
| R2 Compliance Trend (`trend`) | sla.task | graph line, pivot | `end_time:week` x `sla_id`; `achieved_rate` | task đã xong; lọc Last 30 Days |
| R3 Response Time Distribution (`distribution`) | sla.task | graph bar xếp chồng, pivot | `sla_id` x `usage_bucket`; đếm | task đã xong; lọc Response SLAs mặc định |
| R4 Status Mix (`status`) | sla.task | graph pie, pivot | `outcome` | không |
| R5 Open Backlog & Ageing (`backlog`) | sla.task | pivot, list | hàng `sla_id` > `res_model`, cột `planned_end_time:week`; list theo `planned_end_time` tăng dần, cột `% Used` (progressbar) | stage in_progress/paused |
| R6 Performance by Definition and Source (`performance`) và Performance by Source (`source`) | sla.task | graph bar xếp chồng, pivot | `sla_id` (hoặc `res_model`) x `outcome`; pivot có `overdue_duration`, `final_percent_used` | outcome on_time/late/breached_open |
| R7 Pause Analysis (`pause`) | sla.task | graph bar, pivot | `sla_id`; `business_pause_duration`, `pause_duration` | không |
| R8 Escalation Activity (`escalation`) | sla.event | graph bar xếp chồng, pivot, list | `event_dt:week` x `event`; pivot `event` > `definition_id` x tuần | event breach/escalate/escalate_failed |
| R9 Source Heatmap (`heatmap`) | sla.task | pivot, graph line | hàng `res_model`, cột `start_time:month`; `achieved_rate` + đếm | không |
| R10 Calendar Impact (`calendar`) | sla.task | graph bar, pivot | `sla_id`; pivot đặt cạnh nhau `duration`, `business_duration`, hai loại pause | task đã xong |

Mục được bổ sung: `sla.event` có thêm view graph (`view_sla_event_graph`) và pivot (`view_sla_event_pivot`); không dùng `responsible_id`.

### Bộ lọc mới
- `sla.task` (search view): Open, Breached Open, Late, Last 30 Days (theo `start_time`), This Week (theo `start_time`, thứ Hai đến Chủ Nhật), Due This Week (task đang mở có `planned_end_time` trong tuần), Response SLAs, Resolution SLAs, SLA, OLA. Group by: Outcome, Usage Range, Type (SLA/OLA), Target (Response/Resolution), Start/End theo tuần và tháng, Deadline theo ngày và tuần. Các bộ lọc cũ giữ nguyên.
- `sla.event`: thêm lọc Escalation Activity (breach/escalate/escalate_failed), Last 30 Days; group by Model, Week, Month.

### Đánh đổi
- Graph chuẩn của Odoo chỉ có MỘT measure và measure lấy theo aggregator của field (sum hoặc avg đã khai báo): R7 (tổng và trung bình pause) và R10 (so sánh `duration` với `business_duration`) hiển thị tổng trong graph, còn so sánh hai measure cạnh nhau nằm ở pivot. Không có trung bình pause (field có aggregator sum); trung bình = tổng / số task trong pivot.
- R9 không tô nền ô theo ngưỡng (pivot chuẩn không hỗ trợ); chỉ có bảng và biểu đồ đường.
- R3, R2, R10 mặc định chỉ lấy task đã xong (achieved/breached) vì giá trị lưu của task đang chạy chưa chốt.
- `source_name` chỉ xuất hiện trong list backlog (R5) và chỉ SLA Manager thấy (`groups`); các view chung nhóm theo `res_model`/định nghĩa.
- Ngày trong bộ lọc theo ngày của người dùng (`context_today`), so với `Datetime` ở mốc 00:00.

### i18n
`i18n/ja_JP.po`: thêm 35 chuỗi (menu Reporting, tên 10 màn hình, bộ lọc, nhóm theo, help).

### Test
`tests/test_tg34_reporting_views.py` (tag `tg_34`, 16 test): mọi action mở được với SLA User và Manager (`get_views` và `formatted_read_group` đúng groupby/measure suy ra từ arch), đặc tính action, `source_name` chỉ Manager, menu hiển thị đúng nhóm, đếm R4/R3/R6/R2/R5/R7/R9/R10, R8 trên event, từng bộ lọc (đánh giá domain của search view), nhóm theo, bản ghi rỗng, có ja_JP; tour `dwo_sla_reporting_menu` (`static/tests/tours/reporting_tour.js`) mở app SLA và từng màn hình.

### Việc kiểm kèm theo (C1 còn dở)
- Migration chạy thật: `odoo_appstore/_tools/sla_migration_check_120.py 19` dựng DB 1.1.0 (bỏ 7 cột mới, `latest_version` = 19.0.1.1.0), `-u dwo_sla_core`, 15/15 kiểm tra đạt (outcome, bucket, % dùng, trễ, sla_type/target, source_name được tính lại cho task cũ).
- `SLA_PERF=1` tg18: gắn 300 ticket x 30 định nghĩa 2.46s / 725 query (trước C1) so với 2.70s / 905 query (sau); `source_name` thêm khoảng 10% thời gian gắn hàng loạt (tính theo lô mỗi model), chấp nhận được.
