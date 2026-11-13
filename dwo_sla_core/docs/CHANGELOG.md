# Changelog `dwo_sla_core`

Ghi tóm tắt cải tiến để AI agent cập nhật lại docs 010-070 sau (docs chưa được sửa theo các mục dưới đây).

## 2026-11-13 - 18.0.1.2.2: màn hình báo cáo R2-R10, màu biểu đồ theo ý nghĩa, trục phần trăm (task 006 C5a-2, task 023)

Port từ 19.0.1.2.0 phần C2 và 19.0.1.2.2 (task 023) sang bản 18. Không đổi model/field/migration (field báo cáo đã có từ 18.0.1.2.1). Chi tiết từng màn hình, bộ lọc, đánh đổi: xem mục 19.0.1.2.0 phần C2 và 19.0.1.2.2 ở changelog bản 19 (cùng nội dung). Dashboard Overview (C5b) chưa port.

### Có trong bản này
- Menu SLA > Reporting với 10 màn hình (`views/sla_report_views.xml`, view `<list>`, graph/pivot như 19); `sla.event` có view graph/pivot; bộ lọc và group-by mới trong search view `sla.task` và `sla.event`; `source_name` chỉ SLA Manager; ja_JP (35 chuỗi); group_sla_user đọc được.
- Patch JS `static/src/graph_colors/sla_graph_colors.js` vá `GraphRenderer`: màu cố định theo giá trị outcome/stage/usage_bucket/event, thứ tự xếp chồng theo selection, pie sắp theo selection. Bundle: `web.assets_backend_lazy`.
- Trục phần trăm của `achieved_rate` ở graph Compliance Trend.

### Test
Mới: `tests/test_tg34_reporting_views.py` (16 test + tour `dwo_sla_reporting_menu`, `dwo_sla_graph_colors`) và `tests/test_tg36_graph_colors.py` (4 test); toàn module 475 test xanh (455 trước). Khác 19: Odoo 18 chưa có `formatted_read_group` nên test dùng helper `_fgroup` trên `_read_group`; tour test dùng `SlaHttpCase` (gỡ patch hook sau test, nếu không `check_attrs` của 18 báo 'unexpected attributes on res.partner'); mỗi màn hình đợi breadcrumb trước khi đọc canvas. Đo thật trên DB 18 có dữ liệu: pie đúng màu và thứ tự, trục tuần 50%.

## 2026-11-12 - 18.0.1.2.1 (nhóm 1.2.0), phần C1: field lưu cho báo cáo (task 006)

Bản 18 (port từ 19, task 006 C5a-1; version 18.0.1.2.1 gồm cả bản sửa reset task 025). Chưa có view/menu (giai đoạn C2). Không đổi hành vi engine.

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
`migrations/18.0.1.2.0/post-migrate.py`: một câu SQL tính lại `outcome`, `final_percent_used`, `usage_bucket`, `overdue_duration`; một câu SQL điền `sla_type`/`sla_target`; `source_name` chỉ điền cho task còn trống, theo lô 2000 qua ORM. Idempotent.

### i18n
`i18n/ja_JP.po`: thêm tên, help và giá trị Selection của 7 field mới (bản 18 chỉ có ja_JP).

### Test
`tests/test_tg33_reporting_fields.py` (tag `tg_33`, 13 test): từng kết quả (đúng hạn, trễ, vi phạm đang mở, đang chạy, tạm dừng, huỷ), biên bucket, target 0, cập nhật khi pause/resume/complete, nhóm theo `outcome` và trung bình, `source_name`/`sla_type`/`sla_target`, migration tính lại trên task đã xoá giá trị (gọi trực tiếp hàm `migrate`, hai lần).

### Khác biệt API so với bản 19
- `_read_group_select(self, aggregate_spec, query)` dùng `self._field_to_sql(self._table, field, query)` (Odoo 20: `table['field']`). `aggregator='avg'` có từ 18. Migration dir giữ tên 18.0.1.2.0 để chạy khi nâng từ 1.1.x.

## 2026-11-13 - 18.0.1.1.1: reset theo field lưu ghi được không bắn hai lần (task 025)

Bản 18 (port từ 19.0.1.2.1, task 025). Sửa lỗi, không đổi field/view/migration.

### Điều kiện tái hiện
Field lưu có compute và ghi tay được (ví dụ `sale.order.validity_date`, `compute` phụ thuộc `company_id`, `store`, `readonly=False`), định nghĩa có `reset_field_ids` chứa field đó. Trong CÙNG giao dịch: (1) ghi field nguồn (ví dụ đổi `company_id`) nên field lưu chờ tính lại (tính lười), (2) ghi tay field lưu, chưa flush/đọc ở giữa. Kết quả cũ: hai event `reset`, ba task. Không tái hiện khi chỉ ghi tay một lần, ghi qua Form, ghi cả hai trong một lệnh `write`, hay `reset_action` khác (`cancel`/`complete` đều như nhau).

### Nguyên nhân
Hook `write` đọc giá trị cũ (`record[name]`) TRƯỚC khi ghi. Đọc field lưu đang chờ tính lại ép ORM tính ngay, tức gọi `_compute_field_value` giữa chừng: hook compute đánh giá với `changed={validity_date}` (reset lần 1, trước cả khi lần ghi được áp dụng), rồi sau khi ghi hook `write` đánh giá lại (reset lần 2). Lần ghi tay thay đúng giá trị đó nên tính lại là thừa.

### Cách sửa
`sla_hook.make_write`: với field lưu tính được đang chờ tính lại trên các record sắp ghi, tạm bỏ cờ chờ tính (`env.remove_to_compute`) khi đọc giá trị cũ (đọc giá trị đang lưu, không ép tính), rồi đặt lại cờ (`add_to_compute`) để ORM tự xử lý khi ghi. Dùng API Odoo 18 (`env.records_to_compute`, `remove_to_compute`, `add_to_compute` trong `odoo/api.py`), cùng tên với 19.

### Hành vi còn lại (đúng thiết kế)
Hai thay đổi thật vẫn cho hai reset: đổi `company_id` rồi flush (field tính lại đổi giá trị: một reset) rồi ghi tay field đó (reset thứ hai).

### Test
`tests/test_tg35_reset_writable_compute.py` (7 test): `test_rst_005` đã đo đỏ với code cũ, xanh sau khi sửa (ba task, hai reset).
