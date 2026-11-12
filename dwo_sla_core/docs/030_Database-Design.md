# Database Design Document

## Cho module `dwo_sla_core` (SLA generic cho Odoo 19)

Version 0.6 (draft)
Prepared by hieudt
DUO-TEK Software Vietnam
2026-11-12

Liên quan:
- SRS: `010_Software-Requirements-Specification.md` (version 0.7)
- TAD: `020_Technical-Architecture-Document.md` (version 0.6)
- API Design: không có (module không có REST API; giao tiếp qua ORM, server action, cron)

## Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-10-09 | 0.1 | hieudt | Khởi tạo từ SRS 0.2 và TAD 0.1 |
| 2026-10-09 | 0.2 | hieudt | Sửa theo review: tên chỉ mục theo ORM, chính sách gỡ module (task CASCADE, chặn xóa ở ứng dụng), cơ chế không bắn bù mốc (REQ-FUNC-053), predicate chỉ mục, bảng CHECK đầy đủ, chỉ mục khóa ngoại, quy tắc flush khi reset, sửa các mục MINOR (số bảng, ON UPDATE, selection, bảng quan hệ) |
| 2026-10-12 | 0.3 | hieudt | Đối chiếu với code: thêm `sla_escalation.cancel_retry_on_stop`, `sla_task.achieved_rate`, `sla_task.breaching_count`; ghi rõ `business_percent_used`, `is_due_soon` không lưu; sửa quy tắc REQ-FUNC-053 (đổi `percent` hoặc xóa mốc không tính lại riêng, có ví dụ); `next_due_at` chỉ có chỉ mục từng phần; thêm mục 5 phần Quyền truy cập và record rule; làm rõ ràng buộc `percent`; sửa nhãn phiên bản DBML |
| 2026-11-07 | 0.4 | hieudt | D12/D13 (xem `docs/TASKS.md`): xóa bảng `sla_escalation_retry` và mọi tham chiếu (FK, CASCADE, CHECK, index, access, record rule); `sla_escalation` bỏ `retry`/`retry_pattern`/`cancel_retry_on_stop`, thêm `action_type` (`email` mặc định/`server_action`), `email_recipient_type`/`email_field_id`/`email_fixed_address` (REQ-FUNC-064, 065); `sla_event.event` CHECK bỏ giá trị `escalate_retry` (còn 10 giá trị). |
| 2026-11-12 | 0.5 | hieudt | Đợt cải thiện 01 (19.0.1.1.0): thêm bảng `sla_apply_job`; `sla_definition`: `active` mặc định false, `calendar_tz_override` bắt buộc, thêm `due_soon_hours`, `model_name` thành related có lưu, kế thừa `mail.thread`; script nâng cấp `19.0.1.1.0`. Xem mục 3 và mục 8b. |
| 2026-11-12 | 0.6 | hieudt | Đối chiếu toàn bộ với `models/*.py`, `security/`, `data/`: đổi tên theo code (`sla_task.definition_id` thành `sla_id`; `target_hours` thành `duration` ở định nghĩa và `target_duration` ở task; `calendar_source/calendar_id/calendar_path` thành `schedule_source/schedule_id/schedule_path`; `retroactive_start/retroactive_field_id` thành `retroactive/start_field_id`; `start_dt/end_dt/planned_end/business_elapsed/paused_since` thành `start_time/end_time/planned_end_time/business_duration/pause_time`; `pause_duration` (giờ làm việc) thành `business_pause_duration`); thêm cột `sla_definition.retroactive_pause`, `type`, `vendor_id`, `service_commitment`, `target`; `sla_escalation.email_template_id`; `sla_task.original_breach_time`, `duration`, `pause_duration` (giờ đồng hồ); `resource_calendar.sla_tz_override_source_id` kèm unique `(sla_tz_override_source_id, tz)`; `sla_event.event` CHECK còn 12 giá trị (thêm `recalculate`, `reevaluate`); bảng `sla_apply_job` gộp vào mục 3 (bỏ mục 3b); domain `[]` là chưa cấu hình; thêm quyền/record rule của `sla.apply.job`, `sla.apply.wizard`; bổ sung ghi chú chỉ mục và ràng buộc mới. |

---

## 1. Tổng quan

Tài liệu mô tả schema database của `dwo_sla_core`.

**Stores trong scope:** PostgreSQL (phiên bản theo image `odoo:19.0-20260421`), 5 bảng chính (`sla_definition`, `sla_escalation`, `sla_task`, `sla_event`, `sla_apply_job`) cộng 2 bảng quan hệ nhiều-nhiều do module tạo ra, và một cột thêm vào bảng `resource_calendar` của Odoo. Schema được Odoo ORM sinh từ khai báo model; tài liệu này là đặc tả mục tiêu để cài đặt đúng và đã đối chiếu với `models/*.py` của 19.0.1.1.0.

**Ngoài scope:** schema của model gốc được gắn SLA (không bị đổi, REQ-INST-003); cache `ormcache` trong bộ nhớ; vector store (không áp dụng); bảng của `dwo_sla_analysis` (giai đoạn sau).

**Ràng buộc từ framework (quan trọng):** vì schema do Odoo ORM quản lý nên một số quy ước của skill PostgreSQL được điều chỉnh. Mọi chỗ lệch được ghi ở mục 4.

**Ánh xạ model sang bảng:**

| Model Odoo | Bảng | Vai trò | Trace |
|-----------|------|---------|-------|
| `sla.definition` | `sla_definition` | Luật SLA, mỗi dòng áp dụng cho một model | REQ-FUNC-001 đến REQ-FUNC-003, REQ-FUNC-017, REQ-FUNC-019 đến REQ-FUNC-021, REQ-FUNC-066 đến REQ-FUNC-071 |
| `sla.escalation` | `sla_escalation` | Mốc escalation của một định nghĩa (email hoặc server action) | REQ-FUNC-023, REQ-FUNC-064, REQ-FUNC-065 |
| `sla.task` | `sla_task` | Một SLA đang hoặc đã chạy trên một record | REQ-FUNC-006 đến REQ-FUNC-016, REQ-FUNC-018, REQ-FUNC-043, REQ-FUNC-044, REQ-FUNC-022, REQ-FUNC-072 |
| `sla.event` | `sla_event` | Nhật ký sự kiện và lỗi | REQ-FUNC-029, REQ-FUNC-030, REQ-FUNC-040 |
| `sla.apply.job` | `sla_apply_job` | Một lần áp dụng thủ công cho record có sẵn | REQ-FUNC-068 |
| (kế thừa) `resource.calendar` | `resource_calendar` (thêm cột `sla_tz_override_source_id`) | Bản sao lịch theo timezone của SLA | REQ-FUNC-067 |
| (quan hệ) | `sla_definition_reset_field_rel` | Field kích hoạt reset của định nghĩa | REQ-FUNC-013, REQ-FUNC-041 |
| (quan hệ) | `sla_task_escalation_done_rel` | Mốc đã xử lý xong của task | REQ-FUNC-024 |

Tham số cấu hình lưu ở bảng có sẵn `ir_config_parameter` (không tạo bảng mới): `dwo_sla_core.event_retention_days` (mặc định 365, REQ-INT-010), `dwo_sla_core.due_soon_hours` (mặc định 4, REQ-INT-012), `dwo_sla_core.batch_size` (mặc định 50, REQ-REL-002), `dwo_sla_core.show_form_sla_status` (chip trạng thái trên form; chưa có bản ghi nghĩa là bật, REQ-INT-024). Hai model trừu tượng/transient không có bảng: `sla.mixin` (opt-in cho model gốc: `sla_task_count`, `sla_task_active_count`, `sla_task_breach_count`, tính khi đọc), `sla.apply.wizard`; ba model dịch vụ `sla.engine`, `sla.processor`, `sla.time` là `AbstractModel`.

---

## 2. ERD

DBML source nằm inline bên dưới. Render bằng cách import vào [dbdiagram.io](https://dbdiagram.io). Đường nối `sla_task` tới record gốc là **tham chiếu mềm** (không có khóa ngoại), nên không vẽ ở ERD mà ghi chú ở bảng.

```dbml
// ============================================================
// dwo_sla_core — Database Schema
// Version: 19.0.1.1.0  Date: 2026-11-12
// ============================================================

// REQ-FUNC-001..003, 017, 019..021, 066..072: định nghĩa SLA
Table sla_definition {
  id                  int [pk, increment, note: "serial do Odoo sinh"]
  name                varchar [not null]
  active              boolean [not null, default: false, note: "mặc định tắt (bản nháp), nút Enable/Disable; tắt không dừng task đang chạy; REQ-FUNC-066, 033"]
  sequence            int [not null, default: 10]
  company_id          int [null, note: "NULL = áp dụng mọi công ty"]
  model_id            int [not null]
  model_name          varchar [null, note: "related lưu của ir_model.model, dùng thoát sớm của hook; chỉ mục"]
  duration            float8 [not null, default: 0, note: ">= 0; giờ làm việc nếu có lịch"]
  schedule_source     varchar [not null, default: 'none', note: "none | definition | record (+ selection_add của module khác)"]
  schedule_id         int [null, note: "dùng khi schedule_source = definition"]
  schedule_path       varchar [null, note: "đường dẫn Many2one nối bằng dấu chấm, dùng khi schedule_source = record"]
  calendar_tz_override varchar [not null, note: "timezone dùng để đọc giờ làm của lịch; luôn thắng timezone của lịch; REQ-FUNC-067"]
  start_domain        text [default: '[]', note: "rỗng hoặc '[]' = chưa cấu hình, không bao giờ khớp; REQ-FUNC-003"]
  cancel_domain       text [default: '[]']
  pause_domain        text [default: '[]']
  resume_domain       text [default: '[]']
  stop_domain         text [default: '[]']
  reset_domain        text [default: '[]', note: "như các điều kiện khác; muốn khớp mọi record dùng [('id', '!=', 0)]"]
  cancel_mode         varchar [not null, default: 'start_unmatched']
  resume_mode         varchar [not null, default: 'condition']
  reset_action        varchar [not null, default: 'cancel']
  retroactive         boolean [default: false, note: "lấy mốc bắt đầu từ start_field_id (REQ-FUNC-017)"]
  start_field_id      int [null]
  retroactive_pause   boolean [default: true, note: "trừ đoạn pause trong khoảng quá khứ, REQ-FUNC-071"]
  due_soon_hours      float8 [null, note: ">= 0 hoặc NULL; trống hoặc 0 = dùng Settings; REQ-INT-012"]
  type                varchar [default: 'sla', note: "sla | ola; nhãn phân loại, REQ-FUNC-070"]
  vendor_id           int [null, note: "res_partner; nhãn phân loại"]
  service_commitment  boolean [default: false, note: "nhãn phân loại"]
  target              varchar [null, note: "response | resolution; nhãn phân loại"]
  create_uid          int [null]
  create_date         timestamp [null, note: "UTC (kiểu của Odoo)"]
  write_uid           int [null]
  write_date          timestamp [null, note: "UTC"]

  Note: "Luật SLA (kế thừa mail.thread: thay đổi field có tracking vào chatter, không thêm cột). REQ-FUNC-001"
}

// REQ-FUNC-013, 041
Table sla_definition_reset_field_rel {
  definition_id int [not null]
  field_id      int [not null]
  indexes { (definition_id, field_id) [pk] }
  Note: "Field kích hoạt reset (nhiều-nhiều giữa định nghĩa và ir_model_fields)"
}

// REQ-FUNC-023, 064, 065
Table sla_escalation {
  id            int [pk, increment]
  definition_id int [not null]
  sequence      int [not null, default: 10]
  percent       float8 [not null, note: "> 0; trên 100 = quá hạn; FLOAT8 thay cho INT4 gốc (D6, quyết định implement) để từ chối rõ ràng giá trị không nguyên theo REQ-FUNC-023 AC2 thay vì ORM làm tròn âm thầm"]
  action_type   varchar [not null, default: 'email', note: "email | server_action (D12, REQ-FUNC-064)"]
  action_id     int [null, note: "ir_act_server, cùng model với định nghĩa; bắt buộc khi action_type = server_action"]
  email_recipient_type varchar [default: 'responsible', note: "fixed | field | responsible; bắt buộc khi action_type = email (REQ-FUNC-065)"]
  email_field_id int [null, note: "ir_model_fields trên model của định nghĩa; dùng cho field/responsible"]
  email_fixed_address varchar [null, note: "dùng cho recipient_type = fixed"]
  email_template_id int [null, note: "mail_template của model sla.task; rỗng = nội dung mặc định (REQ-FUNC-064 AC3)"]
  create_uid    int [null]
  create_date   timestamp [null]
  write_uid     int [null]
  write_date    timestamp [null]

  Note: "Mốc escalation. REQ-FUNC-023, 064, 065"
}

// REQ-FUNC-006..016, 018, 022, 043, 044, 072
Table sla_task {
  id               int [pk, increment]
  sla_id           int [not null, note: "định nghĩa mà task thuộc về"]
  res_model        varchar [not null, note: "tham chiếu mềm tới record gốc, không có FK"]
  res_id           int [not null, note: "tham chiếu mềm, không có FK"]
  company_id       int [null, note: "lấy từ record gốc lúc attach"]
  target_duration  float8 [not null, note: "snapshot lúc attach; >= 0"]
  schedule_id      int [null, note: "snapshot lúc attach; NULL = 24x7"]
  stage            varchar [not null, default: 'in_progress', note: "in_progress | paused | achieved | breached | cancelled"]
  start_time       timestamp [not null, note: "UTC"]
  planned_end_time timestamp [null, note: "UTC; có thể dời khi resume"]
  original_breach_time timestamp [null, note: "UTC; hạn chót hứa lúc attach, không đổi (REQ-FUNC-072)"]
  end_time         timestamp [null, note: "UTC; có giá trị khi task đã kết thúc"]
  business_duration float8 [default: 0, note: "giờ làm việc đã trôi, được phép vượt target_duration"]
  running_since    timestamp [null, note: "mốc bắt đầu đoạn đang chạy"]
  pause_time       timestamp [null, note: "có giá trị khi stage = paused"]
  business_pause_duration float8 [default: 0, note: "tổng giờ làm việc đã ở paused"]
  duration         float8 [default: 0, note: "giờ đồng hồ đã chạy (không theo lịch)"]
  pause_duration   float8 [default: 0, note: "giờ đồng hồ đã ở paused"]
  has_breached     boolean [default: false, note: "dấu vi phạm, không bao giờ tắt lại"]
  achieved_rate    float8 [default: 0, note: "lưu (compute store): 1.0 khi stage = achieved, ngược lại 0.0; trung bình trên pivot chỉ lọc task achieved/breached nên cancelled hoặc đang chạy không tính 0% (REQ-FUNC-036)"]
  breaching_count  int [default: 0, note: "lưu (compute store): 1 khi đang in_progress/paused và has_breached; phép đo sum trên pivot (REQ-FUNC-062)"]
  next_due_at      timestamp [null, note: "mốc sớm nhất xử lý nền phải xử lý; chỉ có giá trị khi in_progress"]
  create_uid       int [null]
  create_date      timestamp [null]
  write_uid        int [null]
  write_date       timestamp [null]

  Note: "Một SLA đang hoặc đã chạy trên một record. REQ-FUNC-006"
}

// REQ-FUNC-024
Table sla_task_escalation_done_rel {
  task_id       int [not null]
  escalation_id int [not null]
  indexes { (task_id, escalation_id) [pk] }
  Note: "Mốc đã xử lý xong của task (bắn thành công, hoặc lỗi và coi là xong; mốc đã vượt lúc áp dụng cho record có sẵn)"
}

// REQ-FUNC-029, 030, 040
Table sla_event {
  id            int [pk, increment]
  task_id       int [null, note: "NULL với event error không gắn được task"]
  event         varchar [not null, note: "attach | pause | resume | complete | reset | cancel | breach | escalate | escalate_failed | error | recalculate | reevaluate"]
  event_dt      timestamp [not null, note: "UTC"]
  note          text [null]
  res_model     varchar [null, note: "record liên quan, dùng cho event error không có task"]
  res_id        int [null]
  definition_id int [null]
  company_id    int [null]
  is_resolved   boolean [default: false, note: "chỉ có nghĩa với event error; REQ-FUNC-040"]
  create_uid    int [null]
  create_date   timestamp [null]
  write_uid     int [null]
  write_date    timestamp [null]

  Note: "Nhật ký sự kiện SLA. REQ-FUNC-029"
}

// REQ-FUNC-068: mỗi lần "Apply to Existing Records"
Table sla_apply_job {
  id            int [pk, increment]
  definition_id int [not null]
  filter_domain text [null, note: "thu hẹp, không thay Start Condition"]
  state         varchar [not null, default: 'queued', note: "queued | running | done | cancelled | failed"]
  total         int [default: 0]
  processed     int [default: 0]
  attached      int [default: 0]
  error_count   int [default: 0]
  last_id       int [default: 0, note: "con trỏ id đã xử lý, cho phép chạy tiếp sau khi bị ngắt"]
  user_id       int [null]
  start_time    timestamp [null]
  end_time      timestamp [null]
  note          text [null]
  create_uid    int [null]
  create_date   timestamp [null]
  write_uid     int [null]
  write_date    timestamp [null]

  Note: "Lịch sử các lần áp dụng thủ công cho record có sẵn. REQ-FUNC-068"
}

// Cột thêm vào bảng có sẵn của Odoo (REQ-FUNC-067 AC4): bản sao lịch theo timezone
Table resource_calendar {
  sla_tz_override_source_id int [null, note: "trỏ về lịch gốc; unique (sla_tz_override_source_id, tz)"]
  Note: "Chỉ liệt kê cột do dwo_sla_core thêm"
}

// --- Relationships ---
Ref: sla_definition.model_id > ir_model.id [delete: cascade]
Ref: sla_definition.company_id > res_company.id [delete: restrict]
Ref: sla_definition.schedule_id > resource_calendar.id [delete: restrict]
Ref: sla_definition.start_field_id > ir_model_fields.id [delete: set null]
Ref: sla_definition.vendor_id > res_partner.id [delete: set null]
Ref: sla_definition_reset_field_rel.definition_id > sla_definition.id [delete: cascade]
Ref: sla_definition_reset_field_rel.field_id > ir_model_fields.id [delete: cascade]
Ref: sla_escalation.definition_id > sla_definition.id [delete: cascade]
Ref: sla_escalation.action_id > ir_act_server.id [delete: restrict]
Ref: sla_escalation.email_field_id > ir_model_fields.id [delete: set null]
Ref: sla_escalation.email_template_id > mail_template.id [delete: set null]
Ref: sla_task.sla_id > sla_definition.id [delete: cascade]
Ref: sla_task.company_id > res_company.id [delete: restrict]
Ref: sla_task.schedule_id > resource_calendar.id [delete: restrict]
Ref: sla_task_escalation_done_rel.task_id > sla_task.id [delete: cascade]
Ref: sla_task_escalation_done_rel.escalation_id > sla_escalation.id [delete: cascade]
Ref: sla_event.task_id > sla_task.id [delete: cascade]
Ref: sla_event.definition_id > sla_definition.id [delete: set null]
Ref: sla_event.company_id > res_company.id [delete: restrict]
Ref: sla_apply_job.definition_id > sla_definition.id [delete: cascade]
Ref: sla_apply_job.user_id > res_users.id [delete: set null]
Ref: resource_calendar.sla_tz_override_source_id > resource_calendar.id [delete: cascade]

// --- Table Groups ---
TableGroup "Cấu hình" { sla_definition, sla_definition_reset_field_rel, sla_escalation }
TableGroup "Dữ liệu chạy" { sla_task, sla_task_escalation_done_rel, sla_event, sla_apply_job }
```

Bảng ngoài module được tham chiếu (`ir_model`, `ir_model_fields`, `ir_act_server`, `res_company`, `resource_calendar`) do Odoo quản lý; DBML trên chỉ dùng tên bảng đó trong `Ref`, khi import vào dbdiagram.io cần khai báo bảng giả hoặc bỏ các `Ref` ra ngoài.

---

## 3. Data Dictionary

Kiểu dữ liệu là kiểu PostgreSQL mà Odoo ORM sinh ra: `Char` thành `VARCHAR`, `Text` thành `TEXT`, `Integer` và `Many2one` thành `INT4`, `Float` thành `FLOAT8`, `Boolean` thành `BOOL`, `Datetime` thành `TIMESTAMP` không múi giờ (lưu UTC, xem 4). Các cột kiểm toán chuẩn của Odoo (`create_uid`, `create_date`, `write_uid`, `write_date`) có ở mọi bảng nghiệp vụ và không lặp lại ở từng bảng bên dưới.

Cột **Nullable = No** nghĩa là ứng dụng luôn ghi giá trị (field `required=True`, hoặc field Boolean/số có `default` do ORM điền khi tạo); ràng buộc `NOT NULL` ở database chỉ chắc chắn có với field `required=True`. Tên cột đúng theo khai báo trong `models/*.py`.

### Table: sla_definition

**Mô tả:** Luật SLA, mỗi dòng áp dụng cho một model. Kế thừa `mail.thread` (chatter, các field có `tracking` ghi vết thay đổi; không thêm cột).
**Trace:** REQ-FUNC-001, REQ-FUNC-002, REQ-FUNC-003, REQ-FUNC-017, REQ-FUNC-019, REQ-FUNC-020, REQ-FUNC-033, REQ-FUNC-039, REQ-FUNC-041, REQ-FUNC-066 đến REQ-FUNC-072

| Field | Business Meaning | Type | Nullable | Default | Constraint |
|-------|------------------|------|----------|---------|-----------|
| id | Định danh định nghĩa | SERIAL (INT4) | No | sequence | PK |
| name | Tên hiển thị của định nghĩa | VARCHAR | No | — | — |
| active | Bật (true) hay tắt/lưu trữ (false); mặc định tắt (bản nháp) cho tới khi bấm Enable; tắt không dừng task đang chạy | BOOL | No | **false** | — |
| sequence | Thứ tự hiển thị | INT4 | No | 10 | — |
| company_id | Công ty áp dụng; NULL nghĩa là mọi công ty | INT4 | Yes | — | FK → res_company.id, RESTRICT |
| model_id | Model được gắn SLA; không đổi được khi đã có task (ứng dụng) | INT4 | No | — | FK → ir_model.id, CASCADE |
| model_name | Tên kỹ thuật của model: `related='model_id.model'`, lưu, chỉ đọc, để hook tra nhanh | VARCHAR | Yes | — | chỉ mục (mục 6) |
| duration | Thời lượng mục tiêu, giờ làm việc nếu có lịch | FLOAT8 | No | 0 | CHECK ≥ 0 |
| schedule_source | Nguồn lịch: `none` (24x7), `definition`, `record`; module khác thêm giá trị | VARCHAR | No | `none` | CHECK `definition` cần `schedule_id`, `record` cần `schedule_path` |
| schedule_id | Calendar cố định khi nguồn là `definition` | INT4 | Yes | — | FK → resource_calendar.id, RESTRICT |
| schedule_path | Đường dẫn field Many2one tới calendar khi nguồn là `record` | VARCHAR | Yes | — | kiểm tra ở ứng dụng |
| calendar_tz_override | Timezone dùng để đọc giờ làm của lịch; luôn thắng timezone của lịch (REQ-FUNC-067) | VARCHAR (Selection) | No | timezone của người dùng tạo, hoặc `UTC` | NOT NULL (script nâng cấp điền dữ liệu cũ trước, mục 8b) |
| start_domain | Điều kiện start dạng chuỗi domain literal | TEXT | Yes | `[]` | rỗng hoặc `[]` = chưa cấu hình, không bao giờ khớp |
| cancel_domain | Điều kiện cancel | TEXT | Yes | `[]` | như trên |
| pause_domain | Điều kiện pause | TEXT | Yes | `[]` | như trên |
| resume_domain | Điều kiện resume | TEXT | Yes | `[]` | như trên |
| stop_domain | Điều kiện stop | TEXT | Yes | `[]` | như trên |
| reset_domain | Điều kiện reset | TEXT | Yes | `[]` | như trên; muốn khớp mọi record dùng `[('id', '!=', 0)]` |
| cancel_mode | Khi nào hủy: `start_unmatched`, `condition`, `never` | VARCHAR | No | `start_unmatched` | CHECK IN (3 giá trị) |
| resume_mode | Khi nào tiếp tục: `condition`, `pause_unmatched` | VARCHAR | No | `condition` | CHECK IN (2 giá trị) |
| reset_action | Kết thúc task cũ khi reset: `cancel`, `complete` | VARCHAR | No | `cancel` | CHECK IN (2 giá trị) |
| retroactive | Có lấy mốc bắt đầu từ một field ngày giờ của record | BOOL | No | false | — |
| start_field_id | Field ngày giờ làm mốc bắt đầu | INT4 | Yes | — | FK → ir_model_fields.id, SET NULL |
| retroactive_pause | Trừ đoạn pause trong khoảng quá khứ khi backdate (cần model và field pause có tracking) | BOOL | No | true | — |
| due_soon_hours | Số giờ trước hạn để task tính là "Due Soon"; trống hoặc 0 dùng Settings | FLOAT8 | Yes | — | CHECK `IS NULL OR >= 0` |
| type | Nhãn phân loại: `sla`, `ola` | VARCHAR | Yes | `sla` | CHECK IN (2 giá trị); không `required` để INSERT SQL thô không vỡ |
| vendor_id | Nhà cung cấp liên quan (nhãn) | INT4 | Yes | — | FK → res_partner.id, SET NULL |
| service_commitment | Cam kết dịch vụ chính thức (nhãn) | BOOL | No | false | — |
| target | Nhãn phân loại: `response`, `resolution` | VARCHAR | Yes | — | — |

Field không có cột (tính khi đọc): `running_task_count` (số task `in_progress` và `paused`), `apply_retention_days`, `retroactive_pause_warning` (cảnh báo khi `retroactive_pause` không thể có hiệu lực), `apply_job_ids` (One2many tới `sla_apply_job`), `escalation_ids` (One2many tới `sla_escalation`).

### Table: sla_definition_reset_field_rel

**Mô tả:** Field kích hoạt reset của một định nghĩa.
**Trace:** REQ-FUNC-013, REQ-FUNC-041

| Field | Business Meaning | Type | Nullable | Default | Constraint |
|-------|------------------|------|----------|---------|-----------|
| definition_id | Định nghĩa | INT4 | No | — | FK → sla_definition.id, CASCADE; PK (cùng field_id) |
| field_id | Field của model, khi đổi giá trị thì reset | INT4 | No | — | FK → ir_model_fields.id, CASCADE |

### Table: sla_escalation

**Mô tả:** Mốc escalation của một định nghĩa: tại phần trăm nào thì báo cho ai/chạy gì (email mặc định, hoặc server action nâng cao). Không có cơ chế thử lại (D12: gỡ bỏ, xem `docs/TASKS.md`).
**Trace:** REQ-FUNC-023, REQ-FUNC-038, REQ-FUNC-064, REQ-FUNC-065

| Field | Business Meaning | Type | Nullable | Default | Constraint |
|-------|------------------|------|----------|---------|-----------|
| id | Định danh mốc | SERIAL | No | sequence | PK |
| definition_id | Định nghĩa sở hữu mốc | INT4 | No | — | FK → sla_definition.id, CASCADE; chỉ mục |
| sequence | Thứ tự xử lý khi nhiều mốc cùng đến hạn | INT4 | No | 10 | — |
| percent | Phần trăm thời lượng mục tiêu kích hoạt mốc; trên 100 là quá hạn | FLOAT8 *(deviation: gốc INT4, đổi để từ chối số không nguyên theo FUNC-023 AC2, xem D6)* | No | — | CHECK > 0 (ở database); phần "là số nguyên" kiểm ở ứng dụng (VAL_016), không phải CHECK |
| action_type | `email` (mặc định) hoặc `server_action` (REQ-FUNC-064) | VARCHAR | No | `email` | — |
| action_id | Server action chạy tại mốc khi `action_type=server_action`; thuộc cùng model với định nghĩa | INT4 | Yes | — | FK → ir_act_server.id, RESTRICT; bắt buộc + cùng model kiểm ở ứng dụng |
| email_recipient_type | `fixed` / `field` / `responsible` khi `action_type=email` (REQ-FUNC-065) | VARCHAR | Yes | `responsible` | — |
| email_field_id | Field trên model của định nghĩa dùng để resolve người nhận (`field`/`responsible`; `responsible` nhận Many2one, One2many, Many2many tới user hoặc partner) | INT4 | Yes | — | FK → ir_model_fields.id, SET NULL; kiểm đúng model/kiểu ở ứng dụng |
| email_fixed_address | Địa chỉ email cố định khi `email_recipient_type=fixed` | VARCHAR | Yes | — | — |
| email_template_id | Mẫu email (model `sla.task`); rỗng thì dùng nội dung mặc định đơn giản | INT4 | Yes | mẫu `mail_template_escalation_default` | FK → mail_template.id, SET NULL; đúng model kiểm ở ứng dụng |

Field không có cột: `percent_display`, `display_name`.

### Table: sla_task

**Mô tả:** Một SLA đang hoặc đã chạy trên một record. Liên kết tới record gốc bằng `res_model` và `res_id`, không có khóa ngoại.
**Trace:** REQ-FUNC-006 đến REQ-FUNC-016, REQ-FUNC-018, REQ-FUNC-021, REQ-FUNC-022, REQ-FUNC-043, REQ-FUNC-044, REQ-FUNC-046, REQ-FUNC-072

| Field | Business Meaning | Type | Nullable | Default | Constraint |
|-------|------------------|------|----------|---------|-----------|
| id | Định danh task | SERIAL | No | sequence | PK |
| sla_id | Định nghĩa mà task thuộc về | INT4 | No | — | FK → sla_definition.id, CASCADE ở database; xóa định nghĩa còn task bị chặn ở ứng dụng (mục 5); chỉ mục |
| res_model | Tên model của record gốc | VARCHAR | No | — | — |
| res_id | Id record gốc | INT4 | No | — | không FK |
| company_id | Công ty của record gốc lúc attach, dùng cho record rule và escalation | INT4 | Yes | — | FK → res_company.id, RESTRICT; chỉ mục |
| target_duration | Thời lượng mục tiêu đã chốt lúc attach (snapshot của `sla_definition.duration`) | FLOAT8 | No | — | CHECK ≥ 0 |
| schedule_id | Lịch đã chốt lúc attach; NULL là 24x7 | INT4 | Yes | — | FK → resource_calendar.id, RESTRICT; chỉ mục |
| stage | Trạng thái: `in_progress` (đang chạy), `paused` (tạm dừng), `achieved` (đạt), `breached` (kết thúc khi đã vi phạm), `cancelled` (hủy) | VARCHAR | No | `in_progress` | CHECK IN (5 giá trị) |
| start_time | Mốc bắt đầu tính SLA (UTC) | TIMESTAMP | No | — | UTC |
| planned_end_time | Hạn chót dự kiến (UTC); dời khi resume | TIMESTAMP | Yes | — | CHECK ≥ start_time khi không NULL |
| original_breach_time | Hạn chót hứa lúc attach (UTC); đặt một lần, không đổi khi resume hay Apply Current Settings (REQ-FUNC-072) | TIMESTAMP | Yes | — | — |
| end_time | Thời điểm task kết thúc (UTC) | TIMESTAMP | Yes | — | có giá trị khi và chỉ khi stage là `achieved`, `breached`, `cancelled` |
| business_duration | Giờ làm việc đã trôi tính tới lần chốt gần nhất, cộng dồn qua pause và resume, có thể vượt mục tiêu | FLOAT8 | No | 0 | CHECK ≥ 0 |
| running_since | Mốc bắt đầu đoạn đang chạy hiện tại (UTC) | TIMESTAMP | Yes | — | có giá trị khi và chỉ khi stage là `in_progress` |
| pause_time | Mốc bắt đầu lần pause hiện tại (UTC) | TIMESTAMP | Yes | — | có giá trị khi và chỉ khi stage là `paused` |
| business_pause_duration | Tổng giờ làm việc đã ở trạng thái paused | FLOAT8 | No | 0 | CHECK ≥ 0 |
| duration | Thời gian đã chạy theo giờ đồng hồ (không theo lịch) | FLOAT8 | No | 0 | CHECK ≥ 0 |
| pause_duration | Tổng giờ đồng hồ đã ở trạng thái paused | FLOAT8 | No | 0 | CHECK ≥ 0 |
| has_breached | Dấu vi phạm; bật khi đã quá hạn, không bao giờ tắt lại | BOOL | No | false | — |
| next_due_at | Mốc sớm nhất xử lý nền phải xử lý: breach hoặc mốc escalation chưa xong (UTC) | TIMESTAMP | Yes | — | chỉ có giá trị khi stage là `in_progress`; chỉ mục từng phần |
| achieved_rate | Chỉ báo đạt (compute lưu): 1.0 khi `achieved`, ngược lại 0.0. Trung bình trên pivot chỉ lấy task `achieved`, `breached` (task `cancelled` hoặc đang chạy bị loại, không tính 0%) | FLOAT8 | No | 0 | — |
| breaching_count | Compute lưu: 1 khi task còn `in_progress` hoặc `paused` và đã có dấu vi phạm, ngược lại 0; pivot cộng lại ra số đang vi phạm | INT4 | No | 0 | — |

Field tính lại mỗi lần đọc, KHÔNG có cột trong bảng: `business_percent_used` (% thời lượng đã dùng, gồm đoạn đang chạy với task `in_progress`, REQ-INT-023), `business_duration_live` và `duration_live` (giá trị đã chốt cộng đoạn đang chạy, REQ-INT-028), `is_due_soon` (REQ-INT-012, ngưỡng của định nghĩa hoặc Settings), `display_name`. One2many không có cột: `event_ids`, `escalation_event_ids` (chỉ event `escalate` và `escalate_failed`). Quan hệ nhiều-nhiều: `done_escalation_ids` (bảng `sla_task_escalation_done_rel`).

### Table: sla_task_escalation_done_rel

**Mô tả:** Các mốc escalation đã xử lý xong cho một task, để mỗi mốc chỉ xử lý một lần. Gồm mốc bắn thành công, mốc lỗi (coi là xong), và mốc đã vượt sẵn lúc thêm mốc hoặc lúc áp dụng cho record có sẵn (không bắn hồi tố).
**Trace:** REQ-FUNC-024, REQ-FUNC-053, REQ-FUNC-068

| Field | Business Meaning | Type | Nullable | Default | Constraint |
|-------|------------------|------|----------|---------|-----------|
| task_id | Task | INT4 | No | — | FK → sla_task.id, CASCADE; PK (cùng escalation_id) |
| escalation_id | Mốc đã xử lý xong | INT4 | No | — | FK → sla_escalation.id, CASCADE |

### Table: sla_event

**Mô tả:** Nhật ký giải thích vì sao SLA ra kết quả như vậy, và nơi ghi lỗi của engine.
**Trace:** REQ-FUNC-029, REQ-FUNC-030, REQ-FUNC-031, REQ-FUNC-040, REQ-OBS-001, REQ-OBS-003

| Field | Business Meaning | Type | Nullable | Default | Constraint |
|-------|------------------|------|----------|---------|-----------|
| id | Định danh event | SERIAL | No | sequence | PK |
| task_id | Task liên quan; NULL với event `error` không gắn được task | INT4 | Yes | — | FK → sla_task.id, CASCADE |
| event | Loại sự kiện: `attach`, `pause`, `resume`, `complete`, `reset`, `cancel`, `breach`, `escalate`, `escalate_failed`, `error`, `recalculate` (Apply Current Settings), `reevaluate` (Re-check Conditions) | VARCHAR | No | — | CHECK IN (12 giá trị) |
| event_dt | Thời điểm xảy ra (UTC) | TIMESTAMP | No | — | chỉ mục (task_id, event_dt) |
| note | Giải thích: lý do dự phòng lịch, field đã đổi khi reset, thông báo lỗi, người bấm nút; không chứa giá trị field của record | TEXT | Yes | — | — |
| res_model | Model của record liên quan, dùng cho event `error` không có task | VARCHAR | Yes | — | — |
| res_id | Id của record liên quan | INT4 | Yes | — | không FK |
| definition_id | Định nghĩa liên quan | INT4 | Yes | — | FK → sla_definition.id, SET NULL; chỉ mục |
| company_id | Công ty của record liên quan, dùng cho record rule | INT4 | Yes | — | FK → res_company.id, RESTRICT; chỉ mục |
| is_resolved | Event `error` đã được xử lý hay chưa (REQ-FUNC-040) | BOOL | No | false | — |

### Table: sla_apply_job

**Mô tả:** Một lần "Apply to Existing Records": gắn SLA cho các record có sẵn theo lô. Mỗi lần chạy là một dòng, không ghi đè lần trước. Lô đầu chạy ngay trong request của wizard, phần còn lại do cron `SLA: apply to existing records` (5 phút, `ir_cron_sla_apply`) xử lý; cả hai dùng chung hàm lô `_run_batch`. Chỉ hệ thống ghi (mọi ghi qua `sudo()`).
**Trace:** REQ-FUNC-068

| Field | Business Meaning | Type | Nullable | Default | Constraint |
|-------|------------------|------|----------|---------|-----------|
| id | Định danh lần chạy | SERIAL (INT4) | No | sequence | PK |
| definition_id | Định nghĩa được áp dụng | INT4 | No | — | FK → sla_definition.id, CASCADE; chỉ mục |
| filter_domain | Bộ lọc thêm, thu hẹp (không thay) Start Condition; rỗng hoặc `[]` không lọc thêm | TEXT | Yes | — | domain literal, kiểm ở ứng dụng |
| state | `queued`, `running`, `done`, `cancelled`, `failed` | VARCHAR | No | `queued` | chỉ mục |
| total | Số record khớp lúc tạo (chỉ để hiện tiến độ) | INT4 | Yes | 0 | — |
| processed | Số record đã xem | INT4 | Yes | 0 | — |
| attached | Số task đã tạo | INT4 | Yes | 0 | — |
| error_count | Số record lỗi (engine cô lập lỗi theo record) | INT4 | Yes | 0 | — |
| last_id | Con trỏ id đã xử lý (id tăng dần), cho phép chạy tiếp sau khi bị ngắt | INT4 | Yes | 0 | — |
| user_id | Người bấm Apply | INT4 | Yes | — | FK → res_users.id, SET NULL |
| start_time, end_time | Thời điểm bắt đầu và kết thúc | TIMESTAMP | Yes | — | — |
| note | Lỗi không lường trước làm job `failed` | TEXT | Yes | — | — |

Wizard `sla.apply.wizard` là TransientModel (`definition_id`, `model_name` related, `filter_domain` mặc định `[]`, `match_count` tính khi mở), không có bảng đáng kể. Job xong, huỷ hoặc lỗi cũ hơn `event_retention_days` (mặc định 365) bị dọn bởi autovacuum `_gc_old_jobs`; job đang chạy hoặc chờ không bị đụng. Không có cột `active`.

### Cột thêm vào bảng của Odoo: resource_calendar

| Field | Business Meaning | Type | Nullable | Default | Constraint |
|-------|------------------|------|----------|---------|-----------|
| sla_tz_override_source_id | Bản sao lịch theo timezone của SLA trỏ về lịch gốc (REQ-FUNC-067 AC4); lịch thường để trống | INT4 | Yes | — | FK → resource_calendar.id, CASCADE; chỉ mục; UNIQUE `(sla_tz_override_source_id, tz)` tên `resource_calendar_sla_tz_override_uniq` |

Đây là bảng của module `resource`, không phải model được gắn SLA, nên không vi phạm REQ-INST-003 (không thêm cột vào bảng của model gốc được gắn SLA).

### Tham số cấu hình và Settings (`res.config.settings`)

Không có bảng riêng; lưu ở `ir_config_parameter`: `dwo_sla_core.event_retention_days` (365), `dwo_sla_core.due_soon_hours` (4), `dwo_sla_core.batch_size` (50), `dwo_sla_core.show_form_sla_status` (bật khi chưa có bản ghi; tắt lưu chuỗi `False`). Field Settings tương ứng: `sla_event_retention_days`, `sla_due_soon_hours`, `sla_batch_size`, `sla_show_form_status`.

---

## 4. Naming Conventions

Dùng quy ước của Odoo và SRS; chỗ lệch với quy ước chung của skill được nêu rõ.

| Hạng mục | Quy ước dùng | Lệch với quy ước chung? | Lý do |
|----------|--------------|-------------------------|-------|
| Tên bảng | Odoo sinh từ tên model, thay dấu chấm bằng gạch dưới: `sla.task` thành `sla_task` (số ít) | Có: skill dùng số nhiều | ORM của Odoo; tên bảng của cả hệ thống đã theo cách này |
| Khóa chính | `id` kiểu SERIAL (INT4), không phải UUID | Có | ORM của Odoo bắt buộc; id không được expose ra bên ngoài ngoài giao diện Odoo |
| Khóa ngoại | `<field>_id` (Many2one), ví dụ `definition_id` | Không | — |
| Thời điểm | Hậu tố `_time` cho mốc của task và job (`start_time`, `end_time`, `planned_end_time`, `original_breach_time`, `pause_time`), `_dt` cho `sla_event.event_dt`, `_at` cho `next_due_at`; cột kiểm toán `create_date`, `write_date` của Odoo | Một phần | Tên field đã dùng thống nhất trong SRS và TAD |
| Kiểu thời điểm | `TIMESTAMP` (không múi giờ), giá trị luôn là UTC | Có: skill dùng `TIMESTAMPTZ` | Odoo ORM tạo cột `Datetime` là `timestamp without time zone` và lưu UTC; không đổi được nếu không bỏ ORM |
| Boolean | `active`, `retroactive`, `retroactive_pause`, `service_commitment`, `has_breached`, `is_resolved` | Một phần | `active` là tên chuẩn của Odoo cho archive; `has_`, `is_` dùng ở field mới |
| Enum | `VARCHAR` kèm CHECK (không dùng kiểu ENUM của PostgreSQL) | Không | Dễ thêm giá trị; `selection_add` của module khác cần mở rộng được |
| Ràng buộc | Do ORM đặt tên: `<bảng>_<tên thuộc tính khai báo bỏ gạch dưới đầu>` (ví dụ thuộc tính `_target_hours_check` thành `sla_definition_target_hours_check`; tên thuộc tính giữ nguyên dù cột đã đổi thành `duration`, nên tên ràng buộc không đổi) | Có: skill đề xuất `<table>_<column>_check` | Không đặt được tên tùy ý khi khai báo bằng `models.Constraint` |
| Chỉ mục | Do ORM đặt tên: `models.Index`/`models.UniqueIndex` thành `<bảng>_<tên thuộc tính bỏ gạch dưới đầu>`; `index=True` trên field thành `<bảng>__<cột>_index`. Chọn tên thuộc tính kết thúc bằng `_idx` hoặc `_uniq` | Có: skill đề xuất `idx_`, `uq_` | Cú pháp ORM không cho đặt tiền tố riêng (đã đối chiếu `odoo/orm/table_objects.py`); chỉ tạo bằng SQL trong `init()` mới giữ được tên tùy ý, không dùng ở đây |
| Bảng quan hệ | Khai báo tường minh `relation`, `column1`, `column2` (và `ondelete`) trên field Many2many: `sla_definition_reset_field_rel` (`definition_id`, `field_id`), `sla_task_escalation_done_rel` (`task_id`, `escalation_id`) | Một phần | Tên mặc định của Odoo dài và khác tài liệu; Odoo tự tạo chỉ mục `(column2, column1)` nên không cần thêm |
| Tên dài | Tối đa 63 byte với mọi tên bảng, chỉ mục, ràng buộc | Không | PostgreSQL cắt im lặng; kiểm tra khi viết khai báo |

**Không dùng soft delete** kiểu `deleted_at`: định nghĩa dùng `active` (archive); task, event kết thúc được giữ làm lịch sử và dọn theo chính sách (REQ-FUNC-034, REQ-FUNC-035).

---

## 5. Relationships & Referential Integrity

Odoo chỉ sinh mệnh đề `ON DELETE`; `ON UPDATE` là `NO ACTION` mặc định (id không bao giờ đổi nên không ảnh hưởng). Cột On Update được bỏ khỏi bảng.

| FK (child.field) | References | On Delete | Lý do |
|------------------|-----------|-----------|-------|
| sla_definition.model_id | ir_model.id | CASCADE | Gỡ model (gỡ module chứa nó) thì bỏ định nghĩa, kéo theo task, event (dòng dưới) |
| sla_definition.company_id | res_company.id | RESTRICT | Không xóa công ty đang có định nghĩa; SET NULL sẽ biến định nghĩa thành áp dụng cho mọi công ty |
| sla_definition.schedule_id | resource_calendar.id | RESTRICT | Không xóa lịch đang dùng |
| sla_definition.start_field_id | ir_model_fields.id | SET NULL | Field bị gỡ không được chặn việc gỡ module khác; ứng dụng coi cấu hình retroactive thiếu field là lỗi cấu hình và ghi event `error` (vì vậy không có CHECK ràng buộc `retroactive` với field) |
| sla_definition_reset_field_rel.definition_id | sla_definition.id | CASCADE | Quan hệ không có giá trị riêng |
| sla_definition_reset_field_rel.field_id | ir_model_fields.id | CASCADE | Field bị gỡ thì bỏ khỏi danh sách theo dõi |
| sla_escalation.definition_id | sla_definition.id | CASCADE | Mốc không tồn tại độc lập ngoài định nghĩa |
| sla_escalation.action_id | ir_act_server.id | RESTRICT | Không xóa server action đang được mốc dùng; gỡ module sở hữu server action đó làm Odoo ghi cảnh báo và giữ lại bản ghi, người cấu hình phải đổi action |
| sla_definition.vendor_id | res_partner.id | SET NULL | Nhãn phân loại; xóa nhà cung cấp không được chặn |
| sla_escalation.email_template_id | mail_template.id | SET NULL | Mất mẫu thì dùng nội dung mặc định (REQ-FUNC-064 AC3) |
| sla_task.sla_id | sla_definition.id | CASCADE | Xem "Chính sách gỡ module và xóa định nghĩa" bên dưới |
| sla_apply_job.definition_id | sla_definition.id | CASCADE | Lịch sử áp dụng thuộc về định nghĩa |
| sla_apply_job.user_id | res_users.id | SET NULL | Giữ lịch sử khi xóa người dùng |
| resource_calendar.sla_tz_override_source_id | resource_calendar.id | CASCADE | Xóa lịch gốc thì bỏ các bản sao theo timezone |
| sla_task.company_id | res_company.id | RESTRICT | Giữ lịch sử đo; xóa công ty đã có dữ liệu SLA bị chặn với lỗi khóa ngoại chuẩn của Odoo (chấp nhận: hiếm và đúng ý giữ lịch sử) |
| sla_task.schedule_id | resource_calendar.id | RESTRICT | Lịch đã chốt là một phần của snapshot; xóa sẽ biến task thành 24x7 (chặn, lỗi khóa ngoại chuẩn) |
| sla_task_escalation_done_rel.task_id | sla_task.id | CASCADE | Quan hệ phụ thuộc task |
| sla_task_escalation_done_rel.escalation_id | sla_escalation.id | CASCADE | Mốc bị xóa thì bỏ dấu đã xử lý |
| sla_escalation.email_field_id | ir_model_fields.id | SET NULL | Field bị xóa thì mốc còn lại nhưng mất tham chiếu resolve email (cần sửa lại) |
| sla_event.task_id | sla_task.id | CASCADE | Nhật ký của task bị dọn thì bỏ theo; event `error` không có task không bị ảnh hưởng |
| sla_event.definition_id | sla_definition.id | SET NULL | Nhật ký không được chặn việc xóa định nghĩa chưa từng có task |
| sla_event.company_id | res_company.id | RESTRICT | Giữ nhất quán record rule |

### Chính sách gỡ module và xóa định nghĩa

- **Gỡ module sở hữu model có SLA** (ví dụ `sh_all_in_one_helpdesk`): Odoo xóa `ir_model` → `sla_definition` (CASCADE) → `sla_task` (CASCADE) → `sla_event`, `sla_task_escalation_done_rel` (CASCADE). Việc gỡ không bị chặn và dữ liệu SLA của model đó bị xóa cùng. (Phiên bản trước để `sla_task.sla_id` là RESTRICT khiến gỡ module thất bại ngay khi có task.)
- **Người dùng xóa một định nghĩa còn task:** ứng dụng chặn bằng `@api.ondelete(at_uninstall=False)` kèm thông báo gợi ý archive (REQ-FUNC-061). Trong lúc gỡ module (`at_uninstall=True`) việc xóa vẫn được phép và cascade như trên.
- Module demo `dwo_sla_demo_ticket` (chưa được tạo trong 19.0.1.1.0, REQ-INST-004 còn `draft`; mô tả dưới là thiết kế dự kiến): gỡ module làm Odoo xóa model `demo.ticket`, cascade theo chính sách trên; `uninstall_hook` (REQ-INST-004) chỉ còn để dọn dữ liệu mẫu rõ ràng.
- Công ty, calendar: RESTRICT giữ nguyên (xem bảng); server action: RESTRICT.

### Không bắn bù mốc escalation thêm sau (REQ-FUNC-053)

Schema không cần cột mới: dùng `sla_escalation.create_date` (cột kiểm toán có sẵn) và bảng `sla_task_escalation_done_rel`. Quy tắc áp dụng khi **tạo** mốc M trên định nghĩa D (không áp dụng khi sửa hoặc xóa mốc): hệ thống tính lại `next_due_at` cho các task `in_progress` của D; với mỗi task T (`in_progress` hoặc `paused`) mà mức đã dùng (thời gian đã trôi chia thời lượng mục tiêu) đã đạt `M.percent`, chèn `(T, M)` vào `sla_task_escalation_done_rel` **không kèm event** (mốc được coi là đã qua). Mốc có phần trăm chưa tới thì giữ nguyên và bắn đúng lúc. Test: TC của REQ-FUNC-053.

**Sửa `percent` hoặc xóa mốc có sẵn không có xử lý riêng:** mốc là cấu hình dùng chung, mọi task đọc `percent` hiện tại ở mỗi lần xử lý nền; `next_due_at` đã lưu không bị tính lại ngay mà ở lần xử lý nền kế tiếp của task. Xóa mốc kéo theo xóa dòng liên quan ở `sla_task_escalation_done_rel` (CASCADE).

Ví dụ (định nghĩa D mục tiêu 8 giờ, 24x7, mốc R50, R75, R100; lúc 14:00):

| Task | Gắn lúc | Đã dùng | `done_escalation` | `next_due_at` |
|------|---------|---------|-------------------|---------------|
| T1 | 09:00 | 5 giờ (62,5%) | R50 | 15:00 (R75 tại 6 giờ) |
| T2 | 11:00 | 3 giờ (37,5%) | rỗng | 15:00 (R50 tại 4 giờ) |
| T3 | 13:00 | 1 giờ (12,5%) | rỗng | 17:00 (R50 tại 4 giờ) |

| Thao tác lúc 14:00 | Kết quả |
|--------------------|---------|
| Thêm R90 | T1, T2, T3 tính lại `next_due_at`; R90 bắn khi tới 90%; task đã ≥ 90% thì chèn `(T, R90)` vào `done_rel`, không bắn |
| Sửa R75 thành 90 | Không có gì chạy ngay; 15:00 T1 được xử lý nền, 75% chưa tới 90% nên không bắn, `next_due_at` = 16:12 |
| Sửa R75 thành 55 | T1 (62,5% ≥ 55%) chỉ bắn lúc 15:00 vì `next_due_at` chưa được tính lại |
| Xóa R75 | R75 biến mất với mọi task; dòng của R75 trong `done_rel` bị xóa |

### Ràng buộc nhất quán (CHECK, khai báo bằng `models.Constraint`)

| Thuộc tính (tên do ORM sinh) | Biểu thức | Ý nghĩa |
|------------------------------|-----------|---------|
| `sla_definition_target_hours_check` | `duration >= 0` | REQ-FUNC-001 AC3 |
| `sla_definition_cancel_mode_check` | `cancel_mode IN ('start_unmatched','condition','never')` | Tập giá trị đóng |
| `sla_definition_resume_mode_check` | `resume_mode IN ('condition','pause_unmatched')` | Tập giá trị đóng |
| `sla_definition_reset_action_check` | `reset_action IN ('cancel','complete')` | Tập giá trị đóng |
| `sla_definition_calendar_definition_check` | `schedule_source <> 'definition' OR schedule_id IS NOT NULL` | Nguồn `definition` phải có calendar (REQ-FUNC-019, REQ-FUNC-039). `schedule_source` mở rộng được nên chỉ ràng buộc giá trị có sẵn |
| `sla_definition_calendar_record_check` | `schedule_source <> 'record' OR schedule_path IS NOT NULL` | Nguồn `record` phải có đường dẫn |
| `sla_definition_due_soon_hours_check` | `due_soon_hours IS NULL OR due_soon_hours >= 0` | REQ-INT-012 AC5 |
| `sla_definition_type_check` | `type IN ('sla','ola')` | Tập đóng của nhãn phân loại (REQ-FUNC-070) |
| `resource_calendar_sla_tz_override_uniq` | `unique(sla_tz_override_source_id, tz)` | Tối đa một bản sao lịch cho mỗi (lịch gốc, timezone) (REQ-FUNC-067 AC4) |
| `sla_escalation_percent_check` | `percent > 0` | REQ-FUNC-023 — kiểm thêm là số nguyên (float_is_zero(percent - round(percent))) ở constrain Python vì field đổi sang FLOAT8 (D6) |
| `sla_task_stage_check` | `stage IN ('in_progress','paused','achieved','breached','cancelled')` | Tập đóng |
| `sla_task_target_hours_check` | `target_duration >= 0` | Snapshot hợp lệ |
| `sla_task_business_elapsed_check` | `business_duration >= 0` | Thời gian đã trôi (giờ làm việc) không âm |
| `sla_task_pause_duration_check` | `business_pause_duration >= 0` | Không âm |
| `sla_task_duration_check` | `duration >= 0` | Thời gian đã chạy theo giờ đồng hồ không âm (REQ-FUNC-072) |
| `sla_task_pause_duration_clock_check` | `pause_duration >= 0` | Thời gian pause theo giờ đồng hồ không âm |
| `sla_task_end_dt_check` | `(stage IN ('achieved','breached','cancelled')) = (end_time IS NOT NULL)` | `end_time` chỉ có khi đã kết thúc |
| `sla_task_paused_since_check` | `(stage = 'paused') = (pause_time IS NOT NULL)` | `pause_time` chỉ có khi `paused` |
| `sla_task_next_due_at_check` | `next_due_at IS NULL OR stage = 'in_progress'` | Chỉ task đang chạy mới có mốc xử lý nền; mọi chuyển trạng thái phải ghi `stage` và `next_due_at` trong cùng một lệnh `UPDATE` |
| `sla_task_planned_end_check` | `planned_end_time IS NULL OR planned_end_time >= start_time` | Hạn không trước mốc bắt đầu |
| `sla_task_breached_check` | `stage <> 'breached' OR has_breached` | Task `breached` phải có dấu vi phạm (REQ-FUNC-009, REQ-FUNC-046) |
| `sla_task_achieved_check` | `stage <> 'achieved' OR NOT has_breached` | Task `achieved` không có dấu vi phạm |
| `sla_task_running_since_check` | `(stage = 'in_progress') = (running_since IS NOT NULL)` | `running_since` chỉ có khi `in_progress` (khi `paused` hoặc đã kết thúc thì NULL) |
| `sla_event_event_check` | `event IN ('attach','pause','resume','complete','reset','cancel','breach','escalate','escalate_failed','error','recalculate','reevaluate')` | Tập đóng (module khác không mở rộng) |

---

### Quyền truy cập và record rule (đối chiếu `security/`)

| Model | `group_sla_user` | `group_sla_manager` | Ghi chú |
|-------|------------------|---------------------|---------|
| `sla.definition` | đọc | đọc, ghi, tạo, xóa | |
| `sla.escalation` | đọc | đọc, ghi, tạo, xóa | |
| `sla.task` | đọc | đọc | ghi bằng `sudo()` ở điểm ghi hẹp của engine (AD-13) |
| `sla.event` | đọc | đọc | như trên |
| `sla.apply.job` | không có | đọc | ghi bằng `sudo()` của wizard và cron |
| `sla.apply.wizard` | không có | đọc, ghi, tạo, xóa | TransientModel |
| `ir.model`, `ir.model.fields` | không có | đọc | để chọn Model và Field trong form định nghĩa |

- `base.group_system` được kế thừa `group_sla_manager` (implied), nên quản trị hệ thống mặc định có quyền SLA Manager.
- Record rule công ty (miền `['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]`, global rule, không gắn nhóm) có trên `sla.definition` (`rule_sla_definition_company`), `sla.task` (`rule_sla_task_company`), `sla.event` (`rule_sla_event_company`); trên `sla.apply.job` (`rule_sla_apply_job_company`) theo công ty của định nghĩa (`definition_id.company_id`); KHÔNG có trên `sla.escalation` vì bảng này không có `company_id`.
- Tên hiển thị nhóm trong giao diện: "SLA / Viewer" (`group_sla_user`) và "SLA / Configuration Administrator" (`group_sla_manager`).

## 6. Indexing Strategy

PostgreSQL không tự tạo chỉ mục cho khóa ngoại; Odoo cũng không (trừ `index=True` và chỉ mục của bảng quan hệ many2many `(column2, column1)`). Tên chỉ mục do ORM sinh theo mục 4. Cú pháp khai báo đã đối chiếu source Odoo 19: `models.Index("(cột...) WHERE ...")`, `models.UniqueIndex("(cột...) WHERE ...")` (ví dụ `mail_message_reaction.py`).

| Bảng | Khai báo (thuộc tính) | Nội dung | Lý do | Tên do ORM sinh |
|------|----------------------|----------|-------|-----------------|
| sla_task | `_one_active_uniq = models.UniqueIndex` | `(sla_id, res_model, res_id) WHERE stage IN ('in_progress','paused')` | Tối đa một task hoạt động cho mỗi (định nghĩa, record), kể cả khi hai giao dịch đồng thời (REQ-FUNC-014, AD-08) | `sla_task_one_active_uniq` |
| sla_task | `_res_idx = models.Index` | `(res_model, res_id)` | Tìm task của một record (đánh giá, action "SLA", dọn mồ côi) | `sla_task_res_idx` |
| sla_task | `_due_idx = models.Index` | `(next_due_at) WHERE stage = 'in_progress'` | Xử lý nền chỉ lấy task đang chạy đến hạn (REQ-PERF-003, AD-05). Đây là chỉ mục DUY NHẤT trên `next_due_at`; không có chỉ mục đầy đủ vì cột này đổi liên tục (chỉ mục thừa bị xóa khi nâng cấp module) | `sla_task_due_idx` |
| sla_task | `_definition_end_idx = models.Index` | `(sla_id, end_time) WHERE stage IN ('achieved','breached')` | Tỷ lệ đạt theo định nghĩa và kỳ của `end_time` (REQ-FUNC-036) | `sla_task_definition_end_idx` |
| sla_task | `_breached_active_idx = models.Index` | `(has_breached) WHERE stage IN ('in_progress','paused')` | Số SLA đang vi phạm (REQ-FUNC-062) | `sla_task_breached_active_idx` |
| sla_task | `index=True` trên `sla_id` | `(sla_id)` đầy đủ (mọi stage, gồm `cancelled`) | Khóa ngoại: kiểm tra khi xóa định nghĩa (REQ-FUNC-061), nhóm theo định nghĩa (REQ-INT-013) | `sla_task__sla_id_index` |
| sla_task | `index=True` trên `company_id` | `(company_id)` | Khóa ngoại và record rule đa công ty | `sla_task__company_id_index` |
| sla_task | `index=True` trên `schedule_id` | `(schedule_id)` | Khóa ngoại (kiểm tra RESTRICT khi xóa calendar) | `sla_task__schedule_id_index` |
| sla_event | `_task_dt_idx = models.Index` | `(task_id, event_dt)` | Xem nhật ký của một task theo thời gian | `sla_event_task_dt_idx` |
| sla_event | (không có chỉ mục riêng cho `event_dt`) | — | Dọn nhật ký cũ (REQ-FUNC-035) chạy một lần mỗi ngày trong autovacuum, chấp nhận quét tuần tự; thêm `index=True` trên `event_dt` nếu `sla_event` đủ lớn để việc dọn chậm (đã đối chiếu code: chưa khai báo) | — |
| sla_event | `_error_unresolved_idx = models.Index` | `(company_id) WHERE event = 'error' AND is_resolved IS NOT TRUE` | Đếm nhanh event lỗi chưa xử lý (REQ-INT-022). Predicate dùng `IS NOT TRUE` vì ORM sinh `is_resolved IS NOT TRUE` cho điều kiện "bằng False"; PostgreSQL không chứng minh được `NOT is_resolved` từ `IS NOT TRUE` | `sla_event_error_unresolved_idx` |
| sla_event | `index=True` trên `company_id` | `(company_id)` đầy đủ | Khóa ngoại và record rule trên danh sách event (bảng tăng nhanh nhất) | `sla_event__company_id_index` |
| sla_event | `index=True` trên `definition_id` | `(definition_id)` | Khóa ngoại | `sla_event__definition_id_index` |
| sla_escalation | `index=True` trên `definition_id` | `(definition_id)` | Khóa ngoại; lấy mốc của định nghĩa | `sla_escalation__definition_id_index` |
| sla_definition | `_model_name_active_idx = models.Index` | `(model_name) WHERE active IS TRUE` | Hook tra định nghĩa đang bật theo model lúc đăng ký (`_register_hook`) | `sla_definition_model_name_active_idx` |
| sla_definition | `index=True` trên `model_name` | `(model_name)` | Tra định nghĩa archive còn task hoạt động của model (AD-10) | `sla_definition__model_name_index` |
| sla_apply_job | `index=True` trên `definition_id` | `(definition_id)` | Khóa ngoại; lịch sử áp dụng theo định nghĩa, kiểm tra job đang chạy | `sla_apply_job__definition_id_index` |
| sla_apply_job | `index=True` trên `state` | `(state)` | Cron lấy job `queued`/`running`; chặn tạo job trùng | `sla_apply_job__state_index` |
| resource_calendar | `index=True` trên `sla_tz_override_source_id` + unique | `(sla_tz_override_source_id)`; unique `(sla_tz_override_source_id, tz)` | Tìm-hoặc-tạo bản sao lịch theo timezone | `resource_calendar__sla_tz_override_source_id_index`, `resource_calendar_sla_tz_override_uniq` |

Bảng nhỏ (`sla_definition`, `sla_escalation`) không cần thêm chỉ mục cho các khóa ngoại còn lại (`company_id`, `schedule_id`, `action_id`): số dòng thấp, quyết định có chủ ý. Tên mọi chỉ mục và ràng buộc phải không quá 63 byte sau khi ORM ghép tiền tố bảng.

**Truy vấn nóng của xử lý nền:**

```sql
SELECT id FROM sla_task
WHERE stage = 'in_progress' AND next_due_at <= (now() AT TIME ZONE 'UTC')
ORDER BY next_due_at
LIMIT 1;  -- lặp từng task; khóa bằng try_lock_for_update (FOR UPDATE SKIP LOCKED)
```

Dùng `sla_task_due_idx`. Mỗi vòng khóa đúng một task (AD-12); số task còn đến hạn để báo cho `ir.cron._commit_progress` đếm bằng truy vấn tương tự với `count(*)`.

**Quy tắc ghi liên quan chỉ mục duy nhất (reset, attach lại):** trong ORM, `create()` thực thi INSERT ngay còn `write()` chỉ đẩy xuống database khi flush. Vì vậy khi reset kết thúc task cũ rồi tạo task mới (REQ-FUNC-012), hoặc attach lại sau `cancelled` (REQ-FUNC-007), cài đặt PHẢI `write` task cũ rồi flush (`flush_recordset()`) **trước** khi `create` task mới, nếu không INSERT vi phạm `sla_task_one_active_uniq` và reset thất bại thành event `error`. Ca test riêng cho reset và attach lại.

**Kiểm chứng ở spike:** chạy `EXPLAIN` trên SQL thật do ORM sinh cho truy vấn nóng, cho đếm event lỗi chưa xử lý (REQ-INT-022) và cho danh sách theo định nghĩa, để xác nhận các chỉ mục từng phần được dùng.

---

## 7. Non-Relational / Vector Store

N/A — hệ thống không dùng vector store hay kho phi quan hệ. `sla_event.note` là văn bản tự do, không phải JSONB; nếu giai đoạn sau cần dữ liệu có cấu trúc trong event thì đánh giá lại.

---

## 8. Migration & Versioning

- Schema do Odoo ORM sinh và cập nhật khi cài hoặc nâng cấp module (`-i`, `-u dwo_sla_core`). Không sửa schema trực tiếp trên production.
- Thay đổi cấu trúc dữ liệu cần dữ liệu cũ (đổi tên cột, đổi kiểu, thêm cột bắt buộc) viết bằng **script nâng cấp của module** trong `dwo_sla_core/migrations/<phiên bản>/` (`pre-` và `post-`), không dùng Alembic hay golang-migrate vì không phải ứng dụng Python độc lập. Thư mục `migrations/` ở gốc repo chỉ dành cho nâng cấp v17 sang v19 và không dùng cho module này.
- Phiên bản module tăng khi thay đổi schema; thay đổi gây phá vỡ (đổi tên, xóa, đổi kiểu) cần REQ-CM-001: script nâng cấp và ghi vào Revision History của SRS.

| Thay đổi | Loại | Xử lý |
|---------|------|-------|
| Thêm cột nullable | Non-breaking | Deploy trực tiếp qua `-u` |
| Thêm cột NOT NULL không default | Breaking | Hai bước: thêm nullable với `pre-` rồi `post-` backfill, sau đó đặt ràng buộc |
| Xóa hoặc đổi tên cột | Breaking | Deprecate trước, script `pre-`/`post-` chuyển dữ liệu, xóa sau |
| Đổi kiểu | Breaking | Cột mới, chuyển dữ liệu, bỏ cột cũ |
| Thêm giá trị vào Selection `schedule_source` (module khác bằng `selection_add` kèm `ondelete`) | Non-breaking | Không có CHECK trên `schedule_source` nên không cần sửa ràng buộc. `stage` và `event` là **tập đóng** của module (có CHECK); thêm giá trị là thay đổi của `dwo_sla_core`: cập nhật CHECK trong script nâng cấp |

**Gỡ module:** hook là patch động trên `create`, `write`, `_compute_field_value` của từng model có định nghĩa (đăng ký trong `_register_hook`, `models/sla_hook.py`), nên biến mất cùng module sau khi tải lại registry; dữ liệu SLA bị xóa cùng bảng khi gỡ. Không có `uninstall_hook` trong 19.0.1.1.0 (module demo chưa tạo).

**Dung lượng:** bảng tăng nhanh nhất là `sla_event` (nhiều dòng mỗi task); số ngày lưu cấu hình qua tham số (mặc định 365). Với quy mô hiện tại chưa cần phân vùng; nếu `sla_event` vượt hàng chục triệu dòng thì xem xét phân vùng theo `event_dt`.

### 8b. Script nâng cấp 19.0.1.1.0

`migrations/19.0.1.1.0/pre-migrate.py`, chạy trước khi schema áp dụng (hai câu SQL, chạy lại không đổi gì thêm):

1. `calendar_tz_override` còn NULL được điền bằng múi giờ của calendar cố định của định nghĩa, nếu không có thì `UTC` (cột chuyển sang NOT NULL ở bước schema; Odoo không tự điền).
2. `start_domain` đúng bằng `[]` được đổi thành `[('id', '!=', 0)]`, để task đang chạy không bị huỷ hàng loạt khi `[]` đổi nghĩa thành "chưa cấu hình". Năm domain còn lại không cần.

Kiểm chứng (2026-11-12): cài 19.0.1.0.0, tạo hai định nghĩa (Start `[]` và Start có điều kiện) cùng 6 task đang chạy, rồi `-u dwo_sla_core` với bản mới: Start `[]` thành `[('id', '!=', 0)]`, múi giờ được điền, cả 6 task giữ nguyên trạng thái `in_progress`.
