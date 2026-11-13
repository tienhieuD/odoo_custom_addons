# Changelog `dwo_sla_core`

Ghi tóm tắt cải tiến để AI agent cập nhật lại docs 010-070 sau (docs chưa được sửa theo các mục dưới đây).

## 2026-11-12 - 20.0.1.2.1 (nhóm 1.2.0), phần C1: field lưu cho báo cáo (task 006)

Bản 20 (port từ 19, task 006 C5a-1; version 20.0.1.2.1 gồm cả bản sửa reset task 025). Chưa có view/menu (giai đoạn C2). Không đổi hành vi engine.

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
`migrations/20.0.1.2.0/post-migrate.py`: một câu SQL tính lại `outcome`, `final_percent_used`, `usage_bucket`, `overdue_duration`; một câu SQL điền `sla_type`/`sla_target`; `source_name` chỉ điền cho task còn trống, theo lô 2000 qua ORM. Idempotent.

### i18n
`i18n/ja_JP.po`: thêm tên, help và giá trị Selection của 7 field mới (bản 20 chỉ có ja_JP).

### Test
`tests/test_tg33_reporting_fields.py` (tag `tg_33`, 13 test): từng kết quả (đúng hạn, trễ, vi phạm đang mở, đang chạy, tạm dừng, huỷ), biên bucket, target 0, cập nhật khi pause/resume/complete, nhóm theo `outcome` và trung bình, `source_name`/`sla_type`/`sla_target`, migration tính lại trên task đã xoá giá trị (gọi trực tiếp hàm `migrate`, hai lần).

### Khác biệt API so với bản 19
- Không có. `_read_group_select(self, table, aggregate_spec)` dùng `table['field']` (Odoo 20). Migration dir giữ tên 20.0.1.2.0 để chạy khi nâng từ 1.1.x.

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
