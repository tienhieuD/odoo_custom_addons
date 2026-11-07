# Software Requirements Specification

## Cho module `dwo_sla_core` (SLA generic cho Odoo 19)

Version 0.2 (draft)
Prepared by hieudt
DUO-TEK Software Vietnam
2026-10-09

## Revision History

| Name | Date | Reason For Changes | Version |
|------|------|--------------------|---------|
| hieudt | 2026-10-09 | Khởi tạo SRS từ bản thiết kế `.claude/plans/010_SLA.md` (đã chốt 10 câu hỏi mở) | 0.1 |
| hieudt | 2026-10-09 | Sửa theo review vòng 1: tách REQ gộp nhiều hành vi, thêm số đo và AC negative, sửa mâu thuẫn (FUNC-005, FUNC-016, INT-005, INT-006), bổ sung REQ còn thiếu (FUNC-038 đến FUNC-062, INT-011 đến INT-023, SEC-006, OBS-002, OBS-003, INST-003, INST-004) | 0.2 |
| hieudt | 2026-10-09 | Đối chiếu 106 REQ với T1–T11 đã cài đặt/kiểm bằng `odoo-bin shell` (xem TASKS.md): đổi 100 REQ từ `draft` sang `active` (đã triển khai, khớp đặc tả). Giữ `draft` 6 REQ: CM-001 (chưa có thay đổi phá vỡ nào để áp dụng quy trình), FUNC-036/062 (tỷ lệ đạt/số đang vi phạm chỉ suy ra thủ công từ pivot, chưa có field riêng), INST-004 (module demo `dwo_sla_demo_ticket` chưa được tạo, ngoài phạm vi T1–T11), MAINT-002 (chưa viết bộ test tự động theo yêu cầu rõ ràng của user), PORT-001 (chưa kiểm trong container deploy thật, mới chỉ chạy trực tiếp bằng `odoo-bin`). Bổ sung help text còn thiếu cho FUNC-042 và SEC-004 trong view, thêm comment giải thích giới hạn field compute không lưu (MAINT-001) vào `sla_hook.py`, cài cơ chế tự phục hồi patch bị mất (`_ensure_hook_registered`, D9/R-01, trước đó chưa code dù đã chốt quyết định) vào `sla_hook.py`/`sla_engine.py`/`sla_processor.py`. | 0.3 |
| hieudt | 2026-10-12 | Đối chiếu SRS với code và bộ test tự động: FUNC-012 AC5 theo FUNC-008; FUNC-012/029 ghi rõ chuỗi event khi reset (`cancel` hoặc `complete`, rồi `reset`); FUNC-014 AC2 viết lại theo cơ chế chỉ mục duy nhất; FUNC-023 làm rõ `percent` là số thực nhưng phải nguyên dương; FUNC-053 thêm AC3 và ví dụ (sửa/xóa mốc có hiệu lực ngay trên task đang chạy); FUNC-055/058 thêm tùy chọn `cancel_retry_on_stop` của mốc (mặc định bật); INT-023 thêm AC cho task đang chạy; INST-002/C-02 ghi `web` (D1); đóng O-01 với ngưỡng 5%; INT-011 nêu nhãn "Has Breached" khác "Currently Breaching"; OBS-003 nêu cơ chế thay giá trị field bằng `<redacted>` (AC2); SEC-001 ghi Settings dành cho quản trị hệ thống (AC5); FUNC-036/062 chuyển `active` (đã có `achieved_rate`, `breaching_count`); mục 4 cập nhật trạng thái. | 0.4 |
| hieudt | 2026-11-07 | D12/D13 (xem `docs/TASKS.md`): gỡ bỏ cơ chế retry escalation (FUNC-027, 028, 056 đến 059 → Removed, số ID giữ nguyên không tái sử dụng; FUNC-026/054/055/029 sửa lại không còn nhắc retry), thêm FUNC-064 (loại hành động escalation: email mặc định/server action) và FUNC-065 (3 cách resolve người nhận email); INT-014 mở rộng với `sla_task_active_count`/`sla_task_breach_count` và quy định nút đỏ khi vi phạm (mixin vẫn opt-in, không kèm bridge module). Đổi theo yêu cầu người dùng "logic escalate có retry hơi thừa thãi... có thể tinh gọn được?" và "tư vấn... nên dùng gì?" cho smart button. | 0.5 |

---

## 1. Introduction

### 1.1 Document Purpose

Tài liệu này đặc tả hệ thống `dwo_sla_core` PHẢI LÀM GÌ, không mô tả làm như thế nào. Người đọc là: product owner, kỹ sư phát triển, QA, vận hành. Cách làm (kiến trúc, hook, engine, cron) nằm ở `020_Technical-Architecture-Document.md`; mô hình dữ liệu nằm ở `030_Database-Design.md`; kiểm thử nằm ở `040_Test-Plan.md`, `050_Test-Design-Specification.md`, `060_Test-Case-Specification.md`; hướng dẫn sử dụng cho người dùng cuối (SLA User/Manager) nằm ở `070_User-Guide.md`, cũng là nguồn cho `static/description/user_guide.html` trên Odoo Apps (các tài liệu 020 đến 070 đã có; SRS này đã được đối chiếu với code và test, xem Revision History).

### 1.2 Product Scope

**Sản phẩm:** `dwo_sla_core`, module Odoo 19 cung cấp SLA dùng chung theo hành vi của ServiceNow. Bất kỳ model nào của Odoo cũng gắn được SLA bằng cấu hình, không cần viết code riêng cho từng model.

**Năng lực chính:** mỗi định nghĩa SLA có 6 điều kiện (start, cancel, pause, resume, stop, reset) được đánh giá mỗi khi record được tạo hoặc sửa; một record chạy nhiều SLA song song; thời gian tính theo giờ làm việc; pause và resume đúng quy tắc; escalation theo mốc phần trăm (email hoặc server action); nhật ký sự kiện; giao diện cấu hình và theo dõi.

**Kết quả mong đợi:** đo đúng và minh bạch thời gian xử lý của các record (ví dụ ticket) so với cam kết, để làm cơ sở cho cảnh báo và báo cáo.

**Trong phạm vi (phiên bản 1):** `dwo_sla_core`, và `dwo_sla_demo_ticket` (module chỉ dùng để test, không đưa lên production; chỉ được nhắc tới khi cần cho kiểm thử).

**Ngoài phạm vi:** sản phẩm helpdesk (portal, email alias, đánh giá khách hàng, knowledge); loại OLA và Underpinning contract; `overrides` giữa các SLA; retroactive pause; relative duration; nguồn múi giờ riêng; workflow hoặc flow designer (thay bằng server action của Odoo); SLO, dashboard SLO và chiều phân tích theo từng model (làm trong module riêng `dwo_sla_analysis` ở giai đoạn sau, xem 2.6).

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|-----------|
| Dấu vi phạm | Cờ của task, bật khi thời gian đã trôi chạm hoặc vượt `planned_end`; không bao giờ tắt lại. Khác với `stage = breached` (task đã kết thúc trong khi dấu vi phạm bật). |
| Event lỗi chưa xử lý / đã xử lý | Trạng thái của event `error` (REQ-FUNC-040). |
| Lô | Nhóm task được xử lý nền cùng lúc (REQ-REL-002). |
| Mốc escalation / mốc bắt đầu | Mốc escalation là phần trăm của thời lượng mục tiêu kích hoạt một server action; mốc bắt đầu là thời điểm `start_dt` của task. Tài liệu này luôn viết đầy đủ để không nhầm. |
| Server action | Hành động cấu hình được của Odoo (`ir.actions.server`): gửi mail, tạo activity, chạy code, đổi field. |
| Thời gian đã trôi | Số giờ làm việc đã dùng của task, cộng dồn qua pause và resume (REQ-FUNC-043). |
| Attach | Gắn một SLA vào record, tạo ra một task SLA ở trạng thái `in_progress` hoặc `paused`. |
| Breach | Vi phạm: thời gian làm việc đã trôi vượt `planned_end` của task SLA. Một khi đã breach thì không bao giờ trở lại trạng thái chưa breach. |
| Business hours | Giờ làm việc, theo lịch `resource.calendar`. |
| Calendar | Bản ghi `resource.calendar` của Odoo mô tả giờ làm việc và ngày nghỉ. |
| Compute field có lưu | Field của Odoo có `compute` và `store=True`: giá trị tự tính và được lưu thành cột trong database. |
| Condition | Một trong 6 điều kiện của định nghĩa SLA, khai báo bằng domain của Odoo. |
| Definition | Định nghĩa SLA (`sla.definition`): model áp dụng, 6 điều kiện, mục tiêu, lịch, escalation. |
| Domain | Biểu thức lọc record của Odoo, ví dụ `[('priority', '=', 'p1')]`. |
| Escalation | Hành động tự động tại một mốc phần trăm của thời lượng mục tiêu, chạy bằng server action. |
| Evaluate | Đánh giá 6 điều kiện của các định nghĩa trên một record và áp dụng chuyển trạng thái tương ứng. |
| Event | Một dòng nhật ký (`sla.event`) ghi lại một thay đổi trạng thái hoặc một lỗi. |
| Milestone | Mốc escalation, tính theo phần trăm của `target_hours`. |
| OLA | Operational Level Agreement. Ngoài phạm vi. |
| Orphan task | Task SLA mà record gốc đã bị xóa. |
| Pause / Resume | Tạm dừng và tiếp tục đồng hồ SLA. Thời gian ở trạng thái paused không tính vào thời gian đã trôi. |
| Planned end | Thời điểm hết hạn dự kiến của task SLA, tính từ thời lượng mục tiêu và lịch. |
| Record gốc | Record của model mà SLA được gắn vào (ví dụ một ticket). |
| Reset | Kết thúc task đang chạy theo `reset_action` rồi gắn task mới nếu start còn khớp. |
| Retroactive start | Lấy mốc bắt đầu SLA từ một field ngày giờ của record thay vì thời điểm hiện tại. |
| SLA | Service Level Agreement: cam kết thời gian xử lý cho từng record. |
| SLI / SLO | Service Level Indicator (số đo thực tế) / Service Level Objective (mục tiêu cho cả kỳ). SLO ngoài phạm vi. |
| Snapshot | Giá trị được sao chép vào task SLA lúc attach để thay đổi cấu hình sau đó không ảnh hưởng task đang chạy. |
| Stage | Trạng thái của task SLA: `in_progress`, `paused`, `achieved`, `breached`, `cancelled`. |
| Target hours | Thời lượng mục tiêu của SLA, tính theo giờ làm việc nếu có lịch. |
| Task SLA | Một SLA đang hoặc đã chạy trên một record (`sla.task`). |

### 1.4 References

| Ref | Tài liệu | Loại | Vị trí |
|-----|---------|------|--------|
| R1 | Thiết kế module SLA generic v3 (bản thiết kế gốc, lịch sử quyết định) | Informative | `.claude/plans/010_SLA.md` |
| R2 | ServiceNow, SLA conditions | Informative | https://www.servicenow.com/docs/r/yokohama/it-service-management/service-level-management/c_SLAConditions.html |
| R3 | ServiceNow, Fluent SLA API | Informative | https://www.servicenow.com/docs/r/application-development/servicenow-sdk/fluent-sla-api.html |
| R4 | Odoo 19 ORM API | Normative cho hành vi ORM | https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html |
| R5 | Odoo 19 source `resource_calendar.py` (`plan_hours`, `get_work_hours_count`) | Normative cho tính giờ | `odoo-19.0.post20260421/addons/resource/models/resource_calendar.py` |
| R6 | Odoo 19 source `base_automation.py` (mẫu hook `write` và `_compute_field_value`) | Informative | `odoo-19.0.post20260421/odoo/addons/base_automation/models/base_automation.py` |
| R7 | `queue_job` `queue_job_function.py` (mẫu kiểm tra `retry_pattern`) | Informative | `3rd-addons/queue_job/models/queue_job_function.py` |
| R8 | CLAUDE.md của repo (quy ước, lint, đa module) | Normative | `CLAUDE.md` |
| R9 | Odoo 19 source `ir_cron.py` (`_commit_progress`, vòng lặp `_run_job`, tham số `cron_end_time`) | Normative cho hành vi cron | `odoo-19.0.post20260421/odoo/addons/base/models/ir_cron.py` |

### 1.5 Document Overview

Mục 2 mô tả bối cảnh, người dùng, ràng buộc, giả định và phân bổ yêu cầu theo giai đoạn. Mục 3 chứa các yêu cầu có thể kiểm chứng, nhóm theo AREA: INT (giao diện), FUNC (chức năng), PERF, SEC, REL, OBS, INST, BUILD, MAINT, REUSE, PORT, CM; các AREA không áp dụng ghi N/A kèm lý do. Mục 4 là ma trận kiểm chứng nối mỗi REQ-ID tới nhóm test. Mục 5 là phụ lục (các mục còn mở). Mỗi yêu cầu có ID bất biến `REQ-[AREA]-[NNN]`; sửa yêu cầu thì tăng hậu tố phiên bản và ghi Revision History. Từ khóa: PHẢI (shall), NÊN (should), CÓ THỂ (may).

---

## 2. Product Overview

### 2.1 Product Perspective

`dwo_sla_core` là module độc lập chạy trong Odoo 19 (image `odoo:19.0-20260421`), thuộc nhóm module first-party `dwo_*` của repo `custom-addons/`. Module không phụ thuộc Helpdesk của Odoo hay module OCA. Nó quan sát record của mọi model qua cơ chế tạo, sửa và tính lại field của Odoo, ghi kết quả vào các bảng riêng, và không thêm field nào vào model nguồn.

Bên ngoài hệ thống, module tương tác với: `resource.calendar` (giờ làm việc, ngày nghỉ), `ir.actions.server` (hành động escalation), `ir.cron` (xử lý theo thời gian), `ir.config_parameter` (cấu hình số ngày lưu nhật ký). Module `dwo_sla_demo_ticket` chỉ là một model nguồn dùng để thử và không được `dwo_sla_core` biết tới. Module `dwo_sla_analysis` (giai đoạn sau) sẽ đọc dữ liệu của `dwo_sla_core`.

### 2.2 Product Functions

- Khai báo định nghĩa SLA cho một model bất kỳ bằng cấu hình (6 điều kiện bằng domain, mục tiêu, lịch).
- Tự động gắn, tạm dừng, tiếp tục, hoàn thành, hủy và reset task SLA khi record thay đổi.
- Tính hạn và thời gian đã trôi theo giờ làm việc; xác định vi phạm.
- Escalation theo mốc phần trăm: email (mặc định) hoặc server action.
- Nhật ký sự kiện đầy đủ cho mọi thay đổi trạng thái và lỗi; cảnh báo và đánh giá lại hàng loạt khi engine lỗi.
- Giao diện cấu hình, theo dõi, báo cáo cơ bản và xem SLA từ record gốc.
- Điểm mở rộng để module khác tùy biến lịch, thời lượng, mốc bắt đầu, điều kiện mà không sửa module này.

### 2.3 Product Constraints

| ID | Ràng buộc | Loại |
|----|----------|------|
| C-01 | Phải chạy trên Odoo 19 (image `odoo:19.0-20260421`) và PostgreSQL; không vendoring core Odoo. | Bắt buộc, nội bộ |
| C-02 | Chỉ phụ thuộc module chuẩn của Odoo (`base`, `resource`, thêm `web` cho view, xem Deviation D1 của REQ-INST-002); không dùng module OCA và không phụ thuộc Helpdesk của Odoo. | Bắt buộc, nội bộ |
| C-03 | Không thêm field nào vào model gốc (REQ-INST-003); liên kết với record gốc chỉ qua tên model và id. | Bắt buộc, nội bộ |
| C-04 | Hành vi 6 điều kiện theo mô tả ServiceNow đã được chốt trong R1 (tham khảo R2, R3), trừ các điểm đã chốt khác. | Bắt buộc, nội bộ |
| C-05 | Giờ làm việc tính bằng `resource.calendar` của Odoo; Datetime lưu UTC. | Bắt buộc, kỹ thuật |
| C-06 | Module đặt trong `custom-addons/`, tiền tố `dwo_`, tuân thủ lint của repo (R8). | Bắt buộc, nội bộ |
| C-07 | Đa công ty được hỗ trợ trong thiết kế dù trước mắt chỉ dùng một công ty. | Bắt buộc, nội bộ |
| C-08 | Server action của escalation chạy trong cron theo quyền của user được gán cho cron. | Bắt buộc, kỹ thuật |

### 2.4 User Characteristics

| Vai trò | Hành vi và mục tiêu | Nhóm quyền |
|---------|---------------------|-----------|
| SLA Manager (người quản trị cấu hình SLA) | Tạo và sửa định nghĩa, escalation; xử lý sự kiện lỗi; bấm đánh giá lại và tính lại; hiểu rõ ba cấu hình dễ sai. Tần suất: thấp, khi đổi chính sách. | `group_sla_manager` |
| SLA User (nhân viên theo dõi) | Xem task SLA, sự kiện, báo cáo; xem SLA trên record gốc. Không sửa cấu hình. | `group_sla_user` |
| Người dùng nghiệp vụ (ví dụ nhân viên xử lý ticket) | Chỉ sửa record gốc như bình thường; không cần quyền với dữ liệu SLA nhưng thao tác của họ kích hoạt SLA. | Không cần nhóm SLA |
| Developer | Mở rộng module qua điểm mở rộng (REQ-INT-007), viết định nghĩa cho model mới. | Theo vai trò kỹ thuật |
| Hệ thống (cron) | Chạy escalation và dọn dẹp theo lịch. | User cố định của cron |

### 2.5 Assumptions and Dependencies

| ID | Giả định hoặc phụ thuộc | Tác động nếu sai |
|----|------------------------|------------------|
| A-01 | Patch động `create`, `write` và hàm tính lại field compute có lưu trong `_register_hook`, chỉ trên model có định nghĩa, hoạt động được trên Odoo 19 như `base_automation` (R6), và không bị module khác gỡ mất (xem rủi ro R-01 của TAD). | Phải chuyển sang mixin opt-in cho từng model; chuyển sang phương án thay thế (kế thừa `base` hoặc mixin opt-in cho từng model); ảnh hưởng REQ-FUNC-001, REQ-FUNC-002, REQ-FUNC-004, REQ-FUNC-005, REQ-INT-006, REQ-PERF-001. Kiểm chứng ở spike giai đoạn 0, gồm ca lưu một automation rule rồi kiểm tra SLA vẫn hoạt động. |
| A-02 | `resource.calendar.plan_hours` và `get_work_hours_count` cho kết quả đúng với calendar `fully_fixed` múi giờ `Asia/Ho_Chi_Minh` (R5). | Tính sai hạn; ảnh hưởng REQ-FUNC-018. Kiểm chứng ở spike. |
| A-03 | Thứ tự xử lý stop, cancel, reset, pause của ServiceNow đúng như tài liệu (R2). | Lệch hành vi ở ca biên; ảnh hưởng REQ-FUNC-008. Đối chiếu với instance thực ở spike. |
| A-04 | Chỉ có một công ty đang dùng; các công ty khác có thể thêm sau. | Test đa công ty vẫn phải chạy (REQ-SEC-003). |
| A-05 | Odoo worker cron luôn khả dụng để xử lý nền chạy mỗi phút (REQ-PERF-003). | Escalation và phát hiện vi phạm trễ hơn REQ-PERF-003. |
| A-06 | Domain trong điều kiện chỉ dùng giá trị literal; chưa hỗ trợ biểu thức động như ngày hiện tại. | Người cấu hình phải chấp nhận giới hạn; xem REQ-FUNC-003. |
| A-07 | Ngưỡng overhead của hook (REQ-PERF-001) do bên sở hữu sản phẩm chọn; đã chốt 5% ngày 2026-10-12 (O-01 đã đóng). | Nếu đổi ngưỡng phải sửa REQ-PERF-001 AC1 và TC-PRF-001, TC-PRF-002. |

### 2.6 Apportioning of Requirements

| Thành phần | Yêu cầu |
|-----------|---------|
| `dwo_sla_core` (phiên bản 1) | Toàn bộ REQ trong tài liệu này. |
| `dwo_sla_demo_ticket` (chỉ để test) | Không có REQ riêng; cung cấp model nguồn cho test end-to-end (nhóm TG-10) và demo giao diện. |
| `dwo_sla_analysis` (giai đoạn sau, **defer**) | SLO và mục tiêu theo kỳ; dashboard SLO; chức năng "chốt" dữ liệu phân tích kèm chiều theo model; phát hiện tự động record thiếu SLA bằng cron quét. Ghi chú thiết kế ở R1. |
| Defer khỏi mọi phiên bản hiện tại | Relative duration, nguồn múi giờ riêng, nguồn `target_hours` lấy từ field của record, OLA và Underpinning contract, `overrides`, retroactive pause. |

---

## 3. Requirements

Mặc định cho mọi REQ trong tài liệu này (trừ khi ghi khác): **Status** `draft`, **Owner** `@hieudt`. Priority ghi theo từng REQ.

### 3.1 External Interfaces

#### 3.1.1 User Interfaces

#### REQ-INT-001: Form định nghĩa SLA

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI cung cấp form `Định nghĩa SLA` cho phép SLA Manager chọn model, khai báo 6 điều kiện bằng công cụ chọn domain theo model đã chọn, đặt thời lượng mục tiêu, chọn nguồn lịch, và sửa danh sách escalation ngay trên form.
- **Rationale:** Gắn SLA vào model bất kỳ chỉ bằng cấu hình (1.2).
- **Acceptance Criteria:**
  - AC1 (happy path): Given SLA Manager mở form mới; When chọn model `res.partner`, nhập start `[('is_company', '=', True)]`, mục tiêu 4 giờ rồi lưu; Then mở lại bản ghi thấy model `res.partner`, start đúng chuỗi trên và mục tiêu 4.
  - AC2 (negative): Given người dùng chỉ thuộc `group_sla_user`; When mở form định nghĩa; Then mọi field ở chế độ chỉ đọc và không có nút Lưu.
- **Verification Method:** Test + Demonstration
- **More Information:** Cross-ref REQ-SEC-001.

#### REQ-INT-002: Cảnh báo ba cấu hình dễ sai trên form

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Form định nghĩa PHẢI hiển thị help text nêu ba cấu hình dễ sai: start là tập con của stop; pause là tập con của start; start và pause loại trừ nhau.
- **Rationale:** Ba cấu hình này gây hành vi khó hiểu (R2); người cấu hình cần biết trước.
- **Acceptance Criteria:**
  - AC1: Given mở form định nghĩa; When xem help của điều kiện start, pause và stop; Then văn bản help của start và pause nêu đủ ba cảnh báo trên.
  - AC2 (negative): Given form của model bất kỳ; When xem help của điều kiện cancel hoặc resume; Then không chứa cảnh báo này (tránh nhiễu).
- **Verification Method:** Inspection + Demonstration
- **More Information:** Hành vi tương ứng ở REQ-FUNC-016.

#### REQ-INT-003: Ghi chú lịch dự phòng trên form

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Khi nguồn lịch là `record`, form PHẢI hiển thị một ghi chú (cảnh báo màu vàng, nằm ngay dưới field nguồn lịch) nêu đúng thứ tự dự phòng: không lấy được lịch thì dùng lịch làm việc mặc định của công ty, nếu cũng không dùng được thì SLA chạy 24x7.
- **Rationale:** Tránh hiểu nhầm về lịch thực tế được áp dụng (REQ-FUNC-020).
- **Acceptance Criteria:**
  - AC1: Given nguồn lịch = `record`; When hiển thị form; Then ghi chú xuất hiện với nội dung nêu cả hai bước dự phòng.
  - AC2 (negative): Given nguồn lịch = `none` hoặc `definition`; When hiển thị form; Then ghi chú không xuất hiện.
- **Verification Method:** Test + Demonstration

#### REQ-INT-004: Danh sách và form chỉ đọc cho task SLA

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI cung cấp danh sách task SLA và form xem chi tiết ở chế độ chỉ đọc, hiển thị tối thiểu: record gốc, định nghĩa, stage, `start_dt`, `planned_end`, `end_dt`, thời gian đã trôi, mục tiêu, dấu vi phạm.
- **Rationale:** Người theo dõi cần thấy toàn bộ trạng thái của từng SLA.
- **Acceptance Criteria:**
  - AC1: Given có task `in_progress` của định nghĩa D; When SLA User mở danh sách; Then thấy dòng của task với các trường nêu trên.
  - AC2 (negative): Given SLA Manager mở form task; When tìm nút sửa hoặc xóa; Then không có (xem REQ-SEC-006).
- **Verification Method:** Test + Demonstration

#### REQ-INT-005: Hành động "Tính lại" trên task SLA

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** SLA Manager PHẢI có hành động "Tính lại" trên task `in_progress` hoặc `paused`: hệ thống xác định lại lịch và thời lượng mục tiêu theo cấu hình hiện hành của định nghĩa và record, giữ nguyên thời gian đã trôi, rồi xếp lại `planned_end`. Với task `paused`, `planned_end` được xếp lại khi task resume. Task đã kết thúc KHÔNG có hành động này.
- **Rationale:** Cho phép áp dụng thay đổi lịch hoặc mục tiêu lên task đang chạy theo quyết định có chủ đích (REQ-FUNC-021).
- **Acceptance Criteria:**
  - AC1: Given task `in_progress` đã chạy 3 giờ làm việc, mục tiêu 4 giờ, và lịch của record vừa đổi sang lịch khác; When bấm Tính lại; Then thời gian đã trôi = 3 giờ, `planned_end` = thời điểm hiện tại cộng 1 giờ làm việc theo lịch mới.
  - AC2: Given mục tiêu trên định nghĩa vừa sửa từ 4 thành 8 giờ; When bấm Tính lại; Then mục tiêu của task = 8 và `planned_end` = hiện tại cộng 5 giờ làm việc.
  - AC3 (negative): Given task `achieved`; When mở form; Then không có nút Tính lại.
  - AC4 (negative): Given người dùng thuộc `group_sla_user`; When xem task; Then không có nút Tính lại.
- **Verification Method:** Test

#### REQ-INT-006: Action "SLA" trên record gốc

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Với mỗi model có ít nhất một định nghĩa đang bật hoặc ít nhất một task đang hoạt động, hệ thống PHẢI cung cấp action "SLA" trong menu Action của record, hiển thị các task SLA của chính record đang chọn. Action CHỈ hiển thị cho người thuộc nhóm SLA và PHẢI biến mất khi model không còn định nghĩa đang bật lẫn task đang hoạt động.
- **Rationale:** Xem SLA ngay trên record mà không phải sửa view của từng model.
- **Acceptance Criteria:**
  - AC1: Given có định nghĩa cho `res.partner` và partner P có 2 task; When SLA User mở menu Action của P và chọn SLA; Then thấy đúng 2 task của P và không thấy task của partner khác.
  - AC2: Given định nghĩa cuối của `res.partner` đã archive nhưng còn 1 task đang chạy; Then action SLA vẫn còn.
  - AC3 (negative): Given định nghĩa cuối đã archive và không còn task đang hoạt động; Then action biến mất.
  - AC4 (negative): Given người dùng không thuộc nhóm SLA; Then không thấy action.
- **Verification Method:** Test + Demonstration
- **More Information:** Cách lọc theo record đang chọn cần kiểm chứng ở spike (R1); phương án dự phòng là menu SLA kèm bộ lọc theo record.

#### REQ-INT-011: Bộ lọc trạng thái task SLA

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Danh sách task PHẢI có các bộ lọc: Đang chạy (`stage = in_progress`), Tạm dừng (`stage = paused`), Đã vi phạm (nhãn giao diện "Has Breached": dấu vi phạm bật, bất kể stage hiện tại; khác "Currently Breaching" của REQ-FUNC-062 là số task còn `in_progress` hoặc `paused` đang vi phạm).
- **Rationale:** Người theo dõi cần thu hẹp nhanh danh sách.
- **Acceptance Criteria:**
  - AC1: Given 2 task `in_progress`, 1 `paused`, 1 `breached`, 1 `achieved` có dấu vi phạm bật; When bật lần lượt từng bộ lọc; Then Đang chạy trả 2, Tạm dừng trả 1, Đã vi phạm trả 2.
  - AC2 (negative): Given không có task nào thỏa; When bật bộ lọc; Then danh sách rỗng, không lỗi.
- **Verification Method:** Test

#### REQ-INT-012: Bộ lọc "Sắp đến hạn"

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Danh sách task PHẢI có bộ lọc "Sắp đến hạn": task `in_progress`, chưa vi phạm, và `planned_end` nhỏ hơn hoặc bằng thời điểm hiện tại cộng X giờ. X PHẢI chỉnh được bởi SLA Manager tại màn hình cấu hình SLA (mục Settings của module), giá trị mặc định 4 giờ (đề xuất, xem O-04).
- **Rationale:** Thấy các SLA có nguy cơ vi phạm.
- **Acceptance Criteria:**
  - AC1: Given X = 6 và 3 task `in_progress` chưa vi phạm có `planned_end` sau 1 giờ, 5 giờ, 3 ngày; When bật bộ lọc; Then trả đúng 2 task đầu.
  - AC2 (negative): Given task `paused`, task `achieved`, task đã vi phạm, mỗi task có `planned_end` sau 1 giờ; When bật bộ lọc; Then không trả task nào trong ba task này.
  - AC3: Given SLA Manager đổi X từ 6 thành 1; When bật bộ lọc; Then chỉ trả task có `planned_end` trong 1 giờ.
- **Verification Method:** Test

#### REQ-INT-013: Nhóm, pivot và graph cho task SLA

- **Status:** active
- **Priority:** Low
- **Owner:** @hieudt
- **Statement:** Danh sách task PHẢI cho nhóm theo định nghĩa, model và stage, và PHẢI có hai chế độ xem pivot và graph.
- **Rationale:** Báo cáo cơ bản cho người theo dõi.
- **Acceptance Criteria:**
  - AC1: Given 3 task của định nghĩa D1 và 2 task của D2; When nhóm theo định nghĩa; Then có 2 nhóm với số lượng 3 và 2.
  - AC2: Given dữ liệu như trên; When mở pivot và graph; Then cả hai hiển thị mà không lỗi và tổng số trùng với danh sách.
- **Verification Method:** Test + Demonstration

#### REQ-INT-014: Nút số task SLA trên form của model đã bật

- **Status:** active
- **Priority:** Low
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI cung cấp một thành phần dùng chung (mixin `sla.mixin`) mà model kế thừa để hiển thị trên form record một nút nêu số task SLA của record đó và mở danh sách task khi bấm. Mixin PHẢI cung cấp riêng số task đang hoạt động (`sla_task_active_count`, in_progress + paused) và số đang vi phạm (`sla_task_breach_count`) để view của model kế thừa có thể hiển thị đúng 1 nút `oe_stat_button` đổi sang kiểu nguy hiểm (đỏ) khi có vi phạm, thay vì hiện số dễ gây nhầm cho người dùng. Nút CHỈ hiển thị cho người thuộc nhóm SLA. Mixin là opt-in (model tự kế thừa và tự thêm nút vào view của mình, không có bridge module đi kèm dwo_sla_core — công thức áp dụng nêu trong User Guide, `docs/070_User-Guide.md`).
- **Rationale:** Xem SLA ngay trên form mà không cần vào menu Action; màu đỏ cho tín hiệu ưu tiên tức thì cho agent xử lý ticket/task mà không cần đọc số.
- **Acceptance Criteria:**
  - AC1: Given model đã bật hiển thị và record có 2 task đang hoạt động; When SLA User mở form; Then nút hiện số 2 và bấm vào thấy các task của record đó.
  - AC2 (negative): Given người dùng không thuộc nhóm SLA; Then không thấy nút.
  - AC3: Given record có 1 task đang hoạt động đã vi phạm; Then nút hiển thị ở biến thể đỏ (`sla_task_breach_count > 0`).
- **Verification Method:** Test

#### REQ-INT-020: Hành động "Đánh giá lại" trên task SLA

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** SLA Manager PHẢI có hành động "Đánh giá lại" trên task: hệ thống chạy lại việc đánh giá 6 điều kiện cho record gốc của task theo REQ-FUNC-032.
- **Rationale:** Bù cho giới hạn của REQ-FUNC-042.
- **Acceptance Criteria:**
  - AC1: Given điều kiện stop qua quan hệ đã khớp nhưng task chưa kết thúc (do giới hạn REQ-FUNC-042); When bấm Đánh giá lại; Then task kết thúc đúng.
  - AC2 (negative): Given người dùng thuộc `group_sla_user`; Then không có nút.
  - AC3: Given task đã `achieved`; When bấm Đánh giá lại; Then task không đổi (REQ-FUNC-031 AC3).
- **Verification Method:** Test

#### REQ-INT-021: Danh sách sự kiện SLA

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI cung cấp danh sách event chỉ đọc với bộ lọc theo loại sự kiện và theo trạng thái xử lý của event `error`, nhóm theo định nghĩa và theo loại.
- **Rationale:** Nơi SLA Manager điều tra lỗi và chạy đánh giá lại hàng loạt (REQ-FUNC-031).
- **Acceptance Criteria:**
  - AC1: Given 5 event gồm 2 `error`, 1 `attach`, 2 `escalate`; When lọc loại `error`; Then trả 2 event.
  - AC2 (negative): Given SLA Manager mở danh sách event; When tìm nút sửa hoặc xóa; Then không có (REQ-SEC-006).
- **Verification Method:** Test

#### REQ-INT-022: Cảnh báo event lỗi chưa xử lý

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI hiển thị cho SLA Manager số event `error` chưa xử lý (trạng thái ở REQ-FUNC-040) trên danh sách event và trên menu SLA, và số này PHẢI giảm khi event được xử lý.
- **Rationale:** Bù rủi ro SLA thiếu âm thầm (REQ-FUNC-030).
- **Acceptance Criteria:**
  - AC1: Given 3 event `error` chưa xử lý; When SLA Manager mở menu SLA; Then thấy số 3 gắn với mục event lỗi.
  - AC2: Given đánh dấu 1 event là đã xử lý; Then số hiển thị là 2.
  - AC3 (negative): Given người dùng không thuộc nhóm SLA; Then không thấy số này.
- **Verification Method:** Test + Demonstration

#### REQ-INT-023: Phần trăm thời lượng đã dùng

- **Status:** active
- **Priority:** Low
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI hiển thị phần trăm thời lượng đã dùng của task `in_progress` hoặc `paused`, tính bằng (thời gian đã trôi tính tới thời điểm xem) chia thời lượng mục tiêu, làm tròn xuống số nguyên, và cho phép vượt 100%.
- **Rationale:** Biết SLA đang ở mức nào so với mục tiêu.
- **Acceptance Criteria:**
  - AC1: Given mục tiêu 4 giờ, đã trôi 1 giờ làm việc; Then hiển thị 25%.
  - AC2 (boundary): Given đã trôi 5 giờ làm việc; Then hiển thị 125%.
  - AC3: Given task `paused`; When xem hai lần cách nhau 2 giờ làm việc; Then phần trăm không đổi.
  - AC4 (đang chạy): Given mục tiêu 4 giờ (24x7), task `in_progress` gắn lúc 09:00 và chưa pause lần nào; When xem lúc 10:00 và lúc 14:00; Then hiển thị 25% rồi 125% (giá trị tính tại thời điểm xem, gồm đoạn đang chạy).
- **Verification Method:** Test
- **More Information:** Field `percent_used` không lưu trên DB, được tính lại mỗi lần đọc view; escalation dùng cùng cách tính nên số hiển thị khớp số quyết định bắn mốc.

#### 3.1.2 Hardware Interfaces

N/A — module phần mềm thuần, không giao tiếp thiết bị.

#### 3.1.3 Software Interfaces

#### REQ-INT-007: Điểm mở rộng: nguồn lịch

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI cho module khác thay đổi cách xác định lịch của task (nhận record, trả calendar hoặc không), và cho thêm giá trị mới vào danh sách nguồn lịch, mà không sửa `dwo_sla_core`.
- **Rationale:** Ví dụ lịch theo team (R1).
- **Acceptance Criteria:**
  - AC1: Given module mẫu thêm nguồn lịch `team` và định nghĩa dùng nguồn này; When attach record có team T; Then task dùng calendar của T.
  - AC2 (negative): Given module mẫu trả calendar `flexible`; When attach; Then áp dụng dự phòng của REQ-FUNC-020.
  - AC3: Given gỡ module mẫu; Then định nghĩa dùng nguồn `team` quay về nguồn mặc định `none` và không lỗi.
- **Verification Method:** Test
- **More Information:** Tên phương thức cụ thể thuộc TAD. Cross-ref REQ-REUSE-001.

#### REQ-INT-008: Điểm vào cho server action: ngữ cảnh record

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Khi chạy escalation, hệ thống PHẢI gọi server action với ngữ cảnh chứa model và id của record gốc theo quy ước của Odoo (`active_model`, `active_id`, `active_ids`).
- **Rationale:** Server action cấu hình được phải tác động đúng record.
- **Acceptance Criteria:**
  - AC1: Given escalation trỏ tới server action ghi chú vào chatter; When mốc đến hạn; Then ghi chú xuất hiện trên đúng record gốc.
  - AC2 (negative): Given hai record cùng có mốc đến hạn; Then ghi chú của mỗi record chỉ nằm trên record tương ứng.
- **Verification Method:** Test

#### REQ-INT-009: Tích hợp lịch làm việc

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI chỉ chấp nhận calendar loại `fully_fixed` làm lịch của SLA. Calendar loại khác PHẢI bị từ chối khi chọn cố định trên định nghĩa, và bị coi là không dùng được khi lấy từ record.
- **Rationale:** Calendar `flexible` dựng khoảng giờ giả lập, không đáng tin cho SLA (R5).
- **Acceptance Criteria:**
  - AC1 (negative): Given calendar `flexible`; When chọn làm lịch cố định của định nghĩa và lưu; Then bị từ chối.
  - AC2: Given nguồn `record` trả calendar `flexible`; When attach; Then dùng lịch dự phòng theo REQ-FUNC-020 và event `attach` ghi lý do.
- **Verification Method:** Test

#### REQ-INT-010: Cấu hình thời gian lưu nhật ký

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Số ngày lưu nhật ký sự kiện PHẢI chỉnh được bởi SLA Manager tại màn hình cấu hình SLA (mục Settings của module) và có giá trị mặc định 365 ngày (đề xuất, xem O-03).
- **Rationale:** Nhật ký tăng không giới hạn nếu không dọn (REQ-FUNC-035).
- **Acceptance Criteria:**
  - AC1: Given hệ thống mới cài; Then tham số tồn tại và có giá trị 365.
  - AC2 (negative): Given SLA Manager nhập giá trị 0 hoặc âm; When lưu; Then bị từ chối.
- **Verification Method:** Test
- **More Information:** Hành vi dọn ở REQ-FUNC-035.

#### REQ-INT-015: Điểm mở rộng: thời lượng mục tiêu

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI cho module khác thay đổi cách xác định thời lượng mục tiêu của task (nhận record, trả số giờ), mặc định là thời lượng trên định nghĩa.
- **Rationale:** Ví dụ số giờ khác nhau theo hợp đồng (R1, câu 10).
- **Acceptance Criteria:**
  - AC1: Given module mẫu trả 3 cho record `priority = p1` và định nghĩa ghi 4; When attach record P1; Then `target_hours` của task = 3.
  - AC2 (negative): Given không có module mẫu; When attach; Then `target_hours` = 4.
  - AC3 (negative): Given module mẫu trả giá trị âm; When attach; Then không tạo task và ghi event `error` (giá trị 0 được chấp nhận, REQ-FUNC-018 AC3).
- **Verification Method:** Test

#### REQ-INT-016: Điểm mở rộng: mốc bắt đầu

- **Status:** active
- **Priority:** Low
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI cho module khác thay đổi cách xác định mốc bắt đầu của task (nhận record và thời điểm hiện tại, trả datetime), mặc định là thời điểm hiện tại hoặc field retroactive.
- **Rationale:** Mốc bắt đầu phức tạp hơn một field.
- **Acceptance Criteria:**
  - AC1: Given module mẫu trả mốc cách đây 2 giờ; When attach; Then `start_dt` = mốc đó.
  - AC2 (negative): Given không có module mẫu và không bật retroactive; Then `start_dt` = thời điểm attach.
- **Verification Method:** Test

#### REQ-INT-017: Điểm mở rộng: domain của điều kiện

- **Status:** active
- **Priority:** Low
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI cho module khác thay đổi domain được dùng cho từng điều kiện của định nghĩa, mặc định là chuỗi domain đã lưu.
- **Rationale:** Điều kiện động mà domain literal không biểu diễn được.
- **Acceptance Criteria:**
  - AC1: Given module mẫu trả domain khác cho điều kiện start; When đánh giá; Then kết quả theo domain của module mẫu.
  - AC2 (negative): Given không có module mẫu; Then dùng domain đã lưu.
- **Verification Method:** Test

#### REQ-INT-018: Điểm mở rộng: sau mỗi chuyển trạng thái

- **Status:** active
- **Priority:** Low
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI gọi một điểm mở rộng sau mỗi chuyển trạng thái của task, cung cấp trạng thái cũ, trạng thái mới và loại event; mặc định không làm gì.
- **Rationale:** Module khác thêm logic (ví dụ đồng bộ ra ngoài) mà không sửa engine.
- **Acceptance Criteria:**
  - AC1: Given module mẫu ghi lại tham số nhận được; When task chuyển `in_progress` sang `paused`; Then điểm mở rộng được gọi 1 lần với (`in_progress`, `paused`, `pause`).
  - AC2 (negative): Given đánh giá không đổi trạng thái; Then điểm mở rộng không được gọi.
- **Verification Method:** Test

#### REQ-INT-019: Công ty khi chạy server action

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Khi chạy escalation, hệ thống PHẢI chạy server action trong công ty của record gốc, kể cả khi user cron thuộc công ty khác; user cron PHẢI được cấp quyền truy cập mọi công ty có định nghĩa SLA, và đây là điều kiện triển khai được nêu trong tài liệu cấu hình.
- **Rationale:** Quy tắc đa công ty của Odoo có thể chặn record của công ty khác với user cron.
- **Acceptance Criteria:**
  - AC1: Given record thuộc công ty B, user cron được cấp quyền cả A và B; When escalation chạy; Then action chạy với công ty B và ghi được vào record.
  - AC2 (negative): Given user cron không được cấp quyền công ty B; When escalation chạy; Then có đúng 1 event `escalate_failed` ghi lỗi quyền và action không chạy lại ở chu kỳ sau.
- **Verification Method:** Test
- **More Information:** Hành vi của Odoo với công ty ngoài danh sách của user cần kiểm chứng ở spike (O-02).

### 3.2 Functional

#### 3.2.1 Cấu hình định nghĩa

#### REQ-FUNC-001: Định nghĩa SLA gắn vào model bất kỳ

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI cho phép tạo định nghĩa SLA áp dụng cho một model bất kỳ hợp lệ (REQ-FUNC-002) chỉ bằng cấu hình, không cần viết code riêng cho model đó. Người cấu hình chọn được: model, thời lượng mục tiêu, nguồn lịch, 6 điều kiện, chế độ cancel, chế độ resume, hành động reset, field kích hoạt reset, retroactive start, danh sách escalation, công ty áp dụng, bật hoặc lưu trữ, thứ tự.
- **Rationale:** Mục tiêu cốt lõi của sản phẩm (1.2).
- **Acceptance Criteria:**
  - AC1 (happy path): Given một định nghĩa cho `res.partner` và một định nghĩa cho `demo.ticket` dùng cùng cấu hình điều kiện; When record của mỗi model thỏa start; Then cả hai được gắn SLA đúng, không có code riêng theo model.
  - AC2 (negative): Given định nghĩa thiếu model; When lưu; Then bị từ chối.
  - AC3 (negative): Given thời lượng mục tiêu âm; When lưu; Then bị từ chối (0 được chấp nhận).
- **Verification Method:** Test

#### REQ-FUNC-002: Giới hạn model được gắn SLA

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI từ chối lưu định nghĩa trỏ tới model transient, model abstract, model `_auto = False`, và các model có tên bắt đầu bằng `sla.`, `ir.` hoặc `mail.`; đồng thời PHẢI bỏ qua các model này khi quan sát thay đổi record.
- **Rationale:** Tránh đệ quy (SLA gắn vào chính dữ liệu SLA) và ảnh hưởng hệ thống nền.
- **Acceptance Criteria:**
  - AC1 (negative): Given model `ir.attachment`; When lưu định nghĩa; Then bị từ chối với thông báo nêu lý do.
  - AC2 (negative): Given model `sla.task`; When lưu; Then bị từ chối.
  - AC3 (happy path): Given model `res.partner`; When lưu; Then thành công.
- **Verification Method:** Test

#### REQ-FUNC-003: Điều kiện dạng domain, kiểm tra khi lưu

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Mỗi điều kiện trong 6 điều kiện (start, cancel, pause, resume, stop, reset) PHẢI được khai báo bằng domain. Điều kiện rỗng nghĩa là chưa cấu hình và không bao giờ khớp; domain `[]` khớp mọi record. Khi lưu, hệ thống PHẢI kiểm tra domain hợp lệ với model đã chọn và PHẢI từ chối domain có bất kỳ giá trị nào không phải literal (ví dụ lời gọi hàm như `context_today()`, biến như `uid` hoặc `user`, phép tính ngày).
- **Rationale:** Phân biệt "chưa cấu hình" với "khớp tất cả"; ngăn lỗi cấu hình lọt vào lúc chạy.
- **Acceptance Criteria:**
  - AC1: Given điều kiện stop rỗng; When đánh giá bất kỳ record; Then stop không khớp.
  - AC2: Given điều kiện start = `[]`; When đánh giá; Then start khớp mọi record.
  - AC3 (negative): Given domain `[('x_khong_ton_tai', '=', 1)]`; When lưu; Then bị từ chối với thông báo nêu tên field.
  - AC4 (negative): Given domain `[('create_date', '<', context_today())]`; When lưu; Then bị từ chối với thông báo nêu giới hạn literal.
- **Verification Method:** Test

#### REQ-FUNC-038: Server action của escalation thuộc đúng model

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI từ chối lưu escalation có server action thuộc model khác model của định nghĩa.
- **Rationale:** Server action phải chạy được trên record gốc.
- **Acceptance Criteria:**
  - AC1 (negative): Given định nghĩa cho `res.partner` và server action của `res.users`; When lưu escalation; Then bị từ chối với thông báo nêu hai model.
  - AC2 (happy path): Given server action của `res.partner`; When lưu; Then thành công.
- **Verification Method:** Test

#### REQ-FUNC-039: Từ chối calendar không có giờ làm khi lưu

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Khi nguồn lịch là `definition`, hệ thống PHẢI từ chối lưu nếu calendar không có giờ làm việc nào trong tuần (không thể xếp được hạn).
- **Rationale:** Phát hiện sớm tại cấu hình thay vì lỗi lúc attach (REQ-FUNC-030).
- **Acceptance Criteria:**
  - AC1 (negative): Given calendar không có dòng giờ làm nào; When chọn làm lịch của định nghĩa và lưu; Then bị từ chối.
  - AC2 (happy path): Given calendar `fully_fixed` có giờ làm T2–T6; When lưu; Then thành công.
- **Verification Method:** Test
- **More Information:** Phân biệt: nguồn `record` không từ chối khi lưu mà dự phòng lúc attach (REQ-FUNC-020); calendar bị sửa mất giờ làm sau khi đã lưu gây lỗi lúc attach (REQ-FUNC-030 AC2).

#### REQ-FUNC-041: Kiểm tra field cấu hình thuộc model

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Khi lưu định nghĩa, hệ thống PHẢI từ chối field retroactive không phải kiểu ngày giờ hoặc không thuộc model của định nghĩa, và từ chối field kích hoạt reset không thuộc model của định nghĩa.
- **Rationale:** Cấu hình sai sẽ gây lỗi lúc chạy.
- **Acceptance Criteria:**
  - AC1 (negative): Given field retroactive là `name` (Char); When lưu; Then bị từ chối.
  - AC2 (negative): Given field retroactive hoặc field kích hoạt reset thuộc model khác; When lưu; Then bị từ chối.
  - AC3 (happy path): Given field retroactive kiểu Datetime của đúng model; When lưu; Then thành công.
- **Verification Method:** Test

#### 3.2.2 Kích hoạt đánh giá

#### REQ-FUNC-004: Đánh giá khi record được tạo hoặc sửa

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Mỗi khi record của model có định nghĩa SLA được tạo hoặc sửa, hệ thống PHẢI đánh giá 6 điều kiện của các định nghĩa áp dụng và áp dụng chuyển trạng thái tương ứng. Lần sửa không chạm field nào liên quan đến định nghĩa (field xuất hiện trong điều kiện, field retroactive, field kích hoạt reset) KHÔNG ĐƯỢC làm phát sinh event hay thay đổi task.
- **Rationale:** SLA phản ứng theo thời gian thực mà không bị nhiễu bởi lần sửa không liên quan.
- **Acceptance Criteria:**
  - AC1 (happy path): Given định nghĩa start `[('priority','=','p1')]`; When tạo ticket P1; Then có 1 task `in_progress`.
  - AC2: Given task đang chạy với stop `[('stage','=','resolved')]`; When đổi `stage` sang resolved; Then task chuyển `achieved` hoặc `breached`.
  - AC3 (negative): Given sửa field `description` không nằm trong điều kiện nào; Then số task và số event không đổi.
- **Verification Method:** Test
- **More Information:** Cross-ref REQ-PERF-001.

#### REQ-FUNC-005: Đánh giá khi field compute có lưu đổi giá trị

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Khi một điều kiện dùng field compute có lưu và giá trị field đó đổi do tính lại (không qua lần sửa trực tiếp field đó), hệ thống PHẢI đánh giá record như một lần sửa.
- **Rationale:** Giống `base_automation` của Odoo (R6); tránh bỏ sót khi `stage` đổi làm `is_resolved` đổi.
- **Acceptance Criteria:**
  - AC1 (happy path): Given stop `[('is_resolved','=',True)]` với `is_resolved` là compute có lưu phụ thuộc `stage`; When đổi `stage` sang resolved; Then task kết thúc đúng 1 lần (1 event `complete`).
  - AC2: Given 3 lần ghi cùng record trong một giao dịch; When đánh giá; Then không có event attach hoặc cancel dư thừa (số event = số chuyển trạng thái thực).
  - AC3 (negative): Given field compute có lưu đổi giá trị nhưng không làm thay đổi kết quả điều kiện; Then không có event mới.
- **Verification Method:** Test
- **More Information:** Cross-ref REQ-FUNC-015, REQ-FUNC-042.

#### REQ-FUNC-042: Giới hạn: field không lưu và điều kiện qua quan hệ

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Với field compute không lưu và với điều kiện đi qua quan hệ (ví dụ `partner_id.country_id`) khi chỉ record liên quan đổi, hệ thống CÓ THỂ không đánh giá tự động; hành động "Đánh giá lại" PHẢI cho kết quả đúng với dữ liệu hiện tại, và giới hạn này PHẢI được nêu trong help text của form định nghĩa.
- **Rationale:** Giới hạn đã chấp nhận, giống Odoo (R6); bù bằng đánh giá lại thủ công.
- **Acceptance Criteria:**
  - AC1 (happy path): Given start `[('partner_id.country_id','=',VN)]`, country của partner vừa đổi sang VN, record chưa có task; When SLA Manager bấm Đánh giá lại; Then task được gắn.
  - AC2 (negative): Given điều kiện dùng field compute không lưu; When field gốc đổi và chưa đánh giá lại; Then không có event `error` (việc có tự cập nhật hay không không được yêu cầu).
  - AC3: Given form định nghĩa; When xem help của các điều kiện; Then có câu nêu giới hạn nói trên.
- **Verification Method:** Test + Inspection
- **More Information:** Hành động: REQ-INT-020, REQ-FUNC-032.

#### 3.2.3 Vòng đời task SLA

#### REQ-FUNC-006: Attach

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Khi record chưa có task đang hoạt động cho một định nghĩa, hệ thống PHẢI gắn SLA (tạo task) nếu và chỉ nếu start khớp, stop không khớp và cancel không khớp. Task mới có `stage = in_progress`, hoặc `paused` nếu pause cũng khớp ngay lúc attach.
- **Rationale:** Quy tắc Attach của ServiceNow (R2).
- **Acceptance Criteria:**
  - AC1: Given start khớp, stop và cancel không khớp; When đánh giá; Then có đúng 1 task `in_progress` và 1 event `attach`.
  - AC2: Given start và pause cùng khớp; When đánh giá; Then task `paused`.
  - AC3 (negative): Given start và stop cùng khớp; When đánh giá; Then không tạo task.
  - AC4 (negative): Given start khớp và cancel khớp; When đánh giá; Then không tạo task.
- **Verification Method:** Test

#### REQ-FUNC-007: Không gắn lại sau khi đã kết thúc

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Khi task gần nhất của (định nghĩa, record) ở `achieved` hoặc `breached`, hệ thống KHÔNG ĐƯỢC gắn task mới và KHÔNG ĐƯỢC reset task đó, kể cả khi start hoặc reset khớp lại; task đã kết thúc theo kết quả này là bất biến. Giới hạn đã chấp nhận ở phiên bản 1: record được mở lại sau khi SLA kết thúc không có SLA mới. Khi task gần nhất ở `cancelled`, hệ thống PHẢI cho gắn lại nếu start khớp và stop, cancel không khớp.
- **Rationale:** Tránh đếm trùng SLA cho cùng một sự việc; task bị hủy chưa phải kết quả đo.
- **Acceptance Criteria:**
  - AC1 (negative): Given task `achieved`, start vẫn khớp; When record sửa thêm; Then không tạo task mới.
  - AC2 (negative): Given task `achieved` và điều kiện reset cùng start khớp; When record sửa thêm; Then task vẫn `achieved` và không có task mới.
  - AC3 (happy path): Given task `cancelled`, start khớp lại; When record sửa; Then tạo task mới `in_progress`.
- **Verification Method:** Test

#### REQ-FUNC-008: Thứ tự ưu tiên khi task đang hoạt động

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Khi record đã có task đang hoạt động, hệ thống PHẢI kiểm tra từ trên xuống và dừng ở mục đầu tiên khớp: (1) stop khớp; (2) cancel khớp (chế độ `condition`) hoặc start không còn khớp (chế độ `start_unmatched`; không áp dụng ở chế độ `never`); (3) điều kiện reset khớp, start khớp, và (không cấu hình field kích hoạt reset hoặc một trong các field đó vừa đổi giá trị); (4) pause khớp khi task `in_progress`; (5) resume theo chế độ resume khi task `paused`.
- **Rationale:** Bám thứ tự của ServiceNow (R2). Cancel đứng trước pause nên cấu hình start và pause loại trừ nhau dẫn tới cancel khi ở chế độ `start_unmatched`.
- **Acceptance Criteria:**
  - AC1: Given stop và pause cùng khớp; Then task kết thúc theo stop, không có event `pause`.
  - AC2: Given chế độ `condition`, cancel và pause cùng khớp; Then task `cancelled`.
  - AC3: Given reset, start và pause cùng khớp; Then reset được áp dụng (REQ-FUNC-012), không có event `pause` trên task cũ.
  - AC4 (negative): Given không điều kiện nào khớp; Then task giữ nguyên và không có event mới.
- **Verification Method:** Test
- **More Information:** Thứ tự cần đối chiếu với instance ServiceNow thực (A-03).

#### REQ-FUNC-009: Hoàn thành (stop)

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Khi stop khớp, hệ thống PHẢI chốt thời gian đã trôi và chuyển task sang `breached` nếu dấu vi phạm đã bật, ngược lại `achieved`. Với task đang `paused`, kết quả chỉ xét dấu vi phạm đã có, không so với `planned_end`. Hệ thống PHẢI ghi `end_dt` và event `complete`.
- **Rationale:** Quy tắc Complete của ServiceNow: stop khớp thì hoàn thành bất kể đã vi phạm hay chưa (R2).
- **Acceptance Criteria:**
  - AC1: Given task `in_progress` chưa quá `planned_end`; When stop khớp; Then `achieved`, `end_dt` = thời điểm stop, 1 event `complete`.
  - AC2: Given task đã quá `planned_end` trong khi record được sửa (chưa tới lượt xử lý nền); When stop khớp; Then `breached`.
  - AC3 (boundary): Given task `paused` 5 ngày làm việc khi mục tiêu còn dư 2 giờ; When stop khớp; Then `achieved`.
  - AC4 (negative): Given task đã `achieved`; When stop khớp lần nữa; Then task và event không đổi.
- **Verification Method:** Test

#### REQ-FUNC-010: Cancel

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI hỗ trợ ba chế độ cancel: `start_unmatched` (mặc định; hủy khi start không còn khớp), `condition` (hủy khi cancel khớp), `never` (không bao giờ hủy). Task bị hủy PHẢI có `stage = cancelled`, `end_dt` được ghi và event `cancel`.
- **Rationale:** Cấu hình "When to cancel" của ServiceNow (R3).
- **Acceptance Criteria:**
  - AC1: Given chế độ `start_unmatched`, start hết khớp; Then `cancelled`.
  - AC2: Given chế độ `condition`, cancel khớp; Then `cancelled`.
  - AC3 (negative): Given chế độ `never`, start hết khớp và cancel khớp; Then task không bị hủy.
- **Verification Method:** Test

#### REQ-FUNC-011: Pause

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Khi pause khớp và task đang `in_progress`, hệ thống PHẢI chuyển task sang `paused`, chốt thời gian đã trôi tới thời điểm đó và ghi event `pause`.
- **Rationale:** Quy tắc Pause của ServiceNow (R2).
- **Acceptance Criteria:**
  - AC1: Given task `in_progress` đã chạy 1 giờ làm việc; When pause khớp; Then `paused`, thời gian đã trôi = 1 giờ, 1 event `pause`.
  - AC2 (negative): Given task đã `paused`; When pause tiếp tục khớp; Then không có event mới.
  - AC3 (negative): Given task `achieved`; When pause khớp; Then task không đổi.
- **Verification Method:** Test

#### REQ-FUNC-037: Resume ở chế độ `condition`

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Với chế độ resume `condition` (mặc định), task `paused` PHẢI chuyển về `in_progress` khi resume khớp và ghi event `resume`; nếu pause hết khớp nhưng resume chưa khớp thì task vẫn `paused`.
- **Rationale:** Cấu hình "When to resume" của ServiceNow (R3).
- **Acceptance Criteria:**
  - AC1: Given chế độ `condition`, task `paused`; When resume khớp; Then `in_progress`, 1 event `resume`.
  - AC2 (negative): Given chế độ `condition`, pause hết khớp nhưng resume chưa khớp; Then vẫn `paused`.
- **Verification Method:** Test

#### REQ-FUNC-048: Resume ở chế độ `pause_unmatched`

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Với chế độ resume `pause_unmatched`, task `paused` PHẢI chuyển về `in_progress` khi pause hết khớp.
- **Rationale:** Cấu hình "When to resume" của ServiceNow (R3).
- **Acceptance Criteria:**
  - AC1: Given chế độ `pause_unmatched`, task `paused`; When pause hết khớp; Then `in_progress`, 1 event `resume`.
  - AC2 (negative): Given chế độ `pause_unmatched`; When pause vẫn khớp; Then vẫn `paused` dù resume khớp.
  - AC3 (end-to-end, cấu hình khuyến nghị): Given start `priority = p1`, pause `stage` thuộc `waiting_customer`, `resolved`, chế độ `pause_unmatched`, stop `stage = closed`; When ticket P1 đi qua `in_progress`, `waiting_customer`, `resolved`, mở lại về `in_progress`, rồi `closed`; Then chỉ có 1 task, đúng 4 event theo thứ tự `attach`, `pause`, `resume`, `complete` (chuyển từ `waiting_customer` sang `resolved` vẫn thuộc điều kiện pause nên không tạo event), và task kết thúc `achieved` hoặc `breached` theo thời gian làm việc đã trôi.
- **Verification Method:** Test

#### REQ-FUNC-012: Reset

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Khi reset và start cùng khớp (và đủ điều kiện ở REQ-FUNC-013 nếu có cấu hình field kích hoạt), hệ thống PHẢI kết thúc task cũ theo hành động reset (`cancel` mặc định: `cancelled`; `complete`: `achieved` hoặc `breached` theo REQ-FUNC-009), gắn task mới theo REQ-FUNC-006 (kể cả vào `paused` nếu pause khớp), và ghi event `reset`; trên task cũ, event theo thứ tự là `cancel` (hành động `cancel`) hoặc `complete` (hành động `complete`) rồi `reset`, task mới có event `attach`. Reset áp dụng cho cả task `in_progress` và `paused`. Reset KHÔNG áp dụng cho task đã `achieved`, `breached` hoặc `cancelled` (REQ-FUNC-007).
- **Rationale:** Cho phép đo lại SLA (ví dụ ticket mở lại) mà vẫn giữ kết quả lần trước (R3).
- **Acceptance Criteria:**
  - AC1: Given hành động reset = `cancel`, task `in_progress`; When reset khớp; Then task cũ `cancelled`, task mới `in_progress`.
  - AC2: Given hành động reset = `complete`, task chưa quá hạn; Then task cũ `achieved`, task mới `in_progress`.
  - AC3: Given reset và pause cùng khớp; Then task mới `paused`.
  - AC4 (negative): Given task gần nhất `achieved`, record không có task hoạt động; When reset và start cùng khớp; Then không có thay đổi nào (REQ-FUNC-007).
  - AC5 (negative): Given reset khớp nhưng start không khớp (nhánh reset chỉ vào khi reset VÀ start cùng khớp, REQ-FUNC-008); Then không áp dụng reset: với `cancel_mode` = `start_unmatched` task cũ bị đóng bởi quy tắc cancel (event `cancel`, không có `reset`), với `cancel_mode` = `never` task cũ giữ nguyên và không có task mới.
  - AC6 (ví dụ chuỗi event): Given ticket T1 `in_progress`, hành động reset = `cancel`; When ticket mở lại, reset và start cùng khớp; Then event của T1: `attach` ... `cancel`, `reset`; task mới T2 `in_progress` với event `attach`.
- **Verification Method:** Test

#### REQ-FUNC-013: Reset chỉ khi field theo dõi đổi giá trị

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Định nghĩa PHẢI có tùy chọn danh sách field kích hoạt reset. Khi tùy chọn này được cấu hình, reset chỉ xảy ra nếu điều kiện reset khớp và giá trị của ít nhất một field trong danh sách vừa thay đổi (giá trị sau khác giá trị trước) trong lần ghi đang xử lý.
- **Rationale:** Điều kiện chỉ mô tả trạng thái; nếu chỉ có domain thì khi điều kiện còn đúng, mỗi lần ghi sẽ reset liên tục (tương đương toán tử "changes" của ServiceNow).
- **Acceptance Criteria:**
  - AC1: Given theo dõi field `assignment_group`, reset `[]`; When đổi `assignment_group` sang giá trị khác; Then reset xảy ra.
  - AC2 (negative): Given field theo dõi giữ nguyên giá trị; Then không reset (chi tiết ở REQ-FUNC-050).
  - AC3: Given field theo dõi là compute có lưu và giá trị đổi do tính lại; Then reset xảy ra.
- **Verification Method:** Test

#### REQ-FUNC-050: Các trường hợp không kích hoạt reset theo field

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Khi có cấu hình field kích hoạt reset, hệ thống KHÔNG ĐƯỢC reset khi: ghi field theo dõi bằng đúng giá trị cũ; chỉ ghi field khác; "Đánh giá lại" thủ công; xử lý nền theo thời gian.
- **Rationale:** Tránh reset ngoài ý muốn và giữ tính lặp lại an toàn (REQ-FUNC-015).
- **Acceptance Criteria:**
  - AC1 (negative): Given như REQ-FUNC-013 AC1; When ghi `assignment_group` bằng đúng giá trị cũ; Then không reset.
  - AC2 (negative): When chỉ ghi field khác; Then không reset.
  - AC3 (negative): When SLA Manager bấm "Đánh giá lại"; Then không reset.
  - AC4 (negative): When xử lý nền chạy; Then không reset.
- **Verification Method:** Test

#### REQ-FUNC-051: Điều kiện reset rỗng và ghi nhận field đã đổi

- **Status:** active
- **Priority:** Low
- **Owner:** @hieudt
- **Statement:** Điều kiện reset rỗng PHẢI nghĩa là chưa cấu hình reset (REQ-FUNC-003), kể cả khi có danh sách field kích hoạt; muốn reset chỉ theo field thì đặt điều kiện reset là `[]`. Event `reset` PHẢI ghi tên các field đã đổi vào ghi chú.
- **Rationale:** Nhất quán với 5 điều kiện còn lại; dễ điều tra.
- **Acceptance Criteria:**
  - AC1 (negative): Given điều kiện reset rỗng và có field theo dõi; When field đổi; Then không reset.
  - AC2: Given điều kiện reset `[]` và field theo dõi `assignment_group`; When reset xảy ra; Then ghi chú của event `reset` chứa `assignment_group`.
- **Verification Method:** Test

#### REQ-FUNC-014: Nhiều SLA song song và tính duy nhất

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Một record PHẢI chạy được nhiều SLA song song, mỗi định nghĩa một task độc lập. Mỗi record PHẢI có tối đa một task đang hoạt động (`in_progress` hoặc `paused`) cho mỗi định nghĩa, kể cả khi hai giao dịch đồng thời cùng cố gắng gắn.
- **Rationale:** Ví dụ SLA phản hồi và SLA xử lý chạy cùng lúc; tránh đo trùng.
- **Acceptance Criteria:**
  - AC1: Given hai định nghĩa response và resolution cùng khớp; Then có 2 task độc lập; stop của resolution không làm đổi task response.
  - AC2 (negative): Given hai giao dịch đồng thời cùng gắn một định nghĩa cho cùng record; Then chỉ 1 task đang hoạt động tồn tại và không bao giờ có task trùng; bên thua không tạo task thứ hai, hoặc ghi event `error` hoặc hoàn tất không tạo trùng. Hệ thống KHÔNG cam kết cả hai giao dịch đều lưu record thành công khi chúng cùng ghi một dòng (cơ sở dữ liệu có thể chặn giao dịch sau trước khi engine chạy).
- **Verification Method:** Test
- **More Information:** Cross-ref REQ-REL-001, REQ-FUNC-030.

#### REQ-FUNC-015: Đánh giá lặp lại không đổi kết quả

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Đánh giá hai lần liên tiếp trên dữ liệu không đổi PHẢI cho cùng kết quả: lần hai không tạo task, không đổi trạng thái và không ghi event nào.
- **Rationale:** An toàn khi chạy lại bằng tay hoặc hàng loạt.
- **Acceptance Criteria:**
  - AC1 (negative: lần hai không thay đổi gì): Given record vừa được đánh giá; When đánh giá lại ngay; Then số task, giá trị task và số event không đổi.
- **Verification Method:** Test

#### REQ-FUNC-016: Xử lý ba cấu hình dễ sai

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI cho kết quả sau với ba cấu hình dễ sai (giả định chế độ cancel `start_unmatched` trừ khi ghi khác): (a) start là tập con của stop: không bao giờ gắn SLA (mọi chế độ cancel); (b) pause là tập con của start: SLA được gắn ở `paused` và khi pause hết khớp thì start cũng hết khớp nên task `cancelled`; (c) start và pause loại trừ nhau: task bị cancel trước khi kịp pause; ở chế độ cancel `never` hoặc `condition` (cancel chưa khớp) task KHÔNG bị cancel mà ở lại `in_progress` hoặc `paused` theo bảng ưu tiên.
- **Rationale:** Hành vi khớp mô tả của ServiceNow (R2); phải có test để người cấu hình hiểu hậu quả.
- **Acceptance Criteria:**
  - AC1: Given start `[('state','in',['new','active'])]`, stop `[('state','in',['new','active','closed'])]`; When record thỏa start; Then không có task.
  - AC2: Given start `[('state','=','hold')]` và pause `[('state','=','hold')]`; When record vào hold rồi đổi sang `closed`; Then task `paused` rồi `cancelled`.
  - AC3: Given start `[('state','in',['new','active'])]`, pause `[('state','=','hold')]`, chế độ `start_unmatched`; When record chuyển sang hold; Then task `cancelled` và không có event `pause`.
  - AC4 (negative): Given như AC3 nhưng chế độ cancel `never`; When record chuyển sang hold; Then task `paused` (không cancel).
- **Verification Method:** Test
- **More Information:** Cross-ref REQ-INT-002.

#### REQ-FUNC-017: Retroactive start

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Khi định nghĩa bật retroactive start, hệ thống PHẢI lấy `start_dt` từ field ngày giờ đã chọn và tính `planned_end` từ mốc đó; nếu mốc đã quá hạn thì task PHẢI breach ngay lúc attach. Nếu field mốc trống, hệ thống PHẢI dùng thời điểm hiện tại và ghi ghi chú vào event `attach`. Thời gian record đã paused trước khi attach KHÔNG được trừ (retroactive pause ngoài phạm vi).
- **Rationale:** Đo SLA từ lúc sự việc xảy ra thay vì lúc hệ thống phát hiện (R3).
- **Acceptance Criteria:**
  - AC1: Given lịch 24x7, mục tiêu 4 giờ, mốc cách đây 1 giờ; When attach; Then `start_dt` = mốc, `planned_end` = mốc + 4 giờ, dấu vi phạm tắt.
  - AC2: Given mục tiêu 4 giờ, mốc cách đây 6 giờ; When attach; Then dấu vi phạm bật ngay và có event `breach`.
  - AC3 (negative): Given field mốc trống; When attach; Then `start_dt` = thời điểm attach và ghi chú của event `attach` nêu việc dùng thời điểm hiện tại.
- **Verification Method:** Test

#### 3.2.4 Thời gian và lịch

#### REQ-FUNC-018: Tính hạn chót theo giờ làm việc

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI tính `planned_end` bằng cách cộng thời lượng mục tiêu tính theo giờ làm việc của lịch được dùng kể từ mốc bắt đầu, có trừ ngày nghỉ (leave) của lịch; khi task không có lịch thì cộng thẳng theo 24x7.
- **Rationale:** Cam kết SLA tính theo giờ làm việc.
- **Acceptance Criteria:**
  - AC1: Given lịch T2–T6 08:00–17:00, mục tiêu 8 giờ, start thứ Sáu 16:00; Then `planned_end` = thứ Hai 15:00 (1 giờ thứ Sáu + 7 giờ thứ Hai).
  - AC2: Given thứ Hai là ngày nghỉ global leave; Then `planned_end` = thứ Ba 15:00.
  - AC3 (boundary): Given mục tiêu 0 giờ; Then `planned_end` = mốc bắt đầu. Given mốc bắt đầu đúng 17:00 thứ Sáu, mục tiêu 1 giờ; Then `planned_end` = thứ Hai 09:00.
  - AC4: Given lịch có múi giờ `Asia/Ho_Chi_Minh`, start 2026-03-02 09:00 giờ địa phương, mục tiêu 2 giờ; Then `planned_end` = 11:00 giờ địa phương (04:00 UTC).
  - AC5: Given không có lịch, mục tiêu 4 giờ; Then `planned_end` = start + 4 giờ.
  - AC6 (negative): Given lịch ngày nghỉ phủ kín 100 cửa sổ 14 ngày liên tiếp (không xếp được hạn); When attach; Then không tạo task và ghi event `error` (REQ-FUNC-030).
- **Verification Method:** Test
- **More Information:** Cross-ref A-02. Giá trị AC được xác nhận ở spike.

#### REQ-FUNC-043: Thời gian đã trôi theo giờ làm việc

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI tính thời gian đã trôi của task theo giờ làm việc giữa các thời điểm, cộng dồn qua các lần pause và resume (thời gian ở `paused` không tính), và cho phép vượt thời lượng mục tiêu.
- **Rationale:** Đo đúng thời gian đã dùng.
- **Acceptance Criteria:**
  - AC1: Given lịch 24x7; chạy 1 giờ, pause 8 giờ, chạy tiếp 2 giờ; Then thời gian đã trôi = 3 giờ.
  - AC2: Given lịch T2–T6 08:00–17:00; chạy từ thứ Sáu 16:00 tới thứ Hai 10:00; Then thời gian đã trôi = 3 giờ (1 + 2).
  - AC3 (negative): Given task `paused` 6 giờ làm việc; Then thời gian đã trôi không tăng trong lúc paused.
  - AC4 (boundary): Given mục tiêu 4 giờ, đã trôi 5 giờ; Then thời gian đã trôi = 5 (không bị cắt ở 4).
- **Verification Method:** Test

#### REQ-FUNC-044: Xếp lại hạn khi resume

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Khi task resume, nếu dấu vi phạm chưa bật thì hệ thống PHẢI xếp lại `planned_end` bằng thời điểm resume cộng phần thời lượng còn lại (mục tiêu trừ thời gian đã trôi, tối thiểu 0); nếu dấu vi phạm đã bật thì `planned_end` giữ nguyên.
- **Rationale:** Thời gian paused không làm dời cam kết ngoài thời gian còn lại.
- **Acceptance Criteria:**
  - AC1: Given lịch 24x7, mục tiêu 4 giờ, đã trôi 1 giờ, pause rồi resume lúc 14:00; Then `planned_end` = 17:00.
  - AC2 (negative): Given dấu vi phạm đã bật, `planned_end` = 13:00; When resume lúc 14:00; Then `planned_end` vẫn = 13:00.
- **Verification Method:** Test

#### REQ-FUNC-019: Ba nguồn lịch

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Mỗi định nghĩa PHẢI chọn một trong ba nguồn lịch: `none` (mặc định, 24x7), `definition` (calendar cố định trên định nghĩa), `record` (field Many2one tới calendar trên chính record, hoặc trên record liên kết qua một chuỗi Many2one nhiều bước, ví dụ `partner_id.parent_id.calendar_id`). Khi lưu, hệ thống PHẢI kiểm tra từng bước của đường dẫn là Many2one trên model của bước trước và bước cuối trỏ tới `resource.calendar`.
- **Rationale:** Tương ứng ba lựa chọn schedule của ServiceNow (R3).
- **Acceptance Criteria:**
  - AC1: Given nguồn `record` với đường dẫn hợp lệ và các bước đều có giá trị; Then task dùng calendar tại cuối đường dẫn.
  - AC2 (negative): Given đường dẫn có bước không phải Many2one hoặc bước cuối không phải `resource.calendar`; When lưu; Then bị từ chối.
  - AC3: Given nguồn `none`; Then task không có lịch (24x7).
- **Verification Method:** Test

#### REQ-FUNC-020: Lịch dự phòng

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Với nguồn `record`, nếu không lấy được lịch (một bước trong đường dẫn trống, calendar cuối trống, hoặc calendar không dùng được: loại `flexible` hoặc không có giờ làm) thì hệ thống PHẢI dùng lịch làm việc mặc định của công ty của record (record không có công ty thì dùng công ty hiện tại); nếu lịch này cũng không dùng được thì task chạy 24x7. Lý do dự phòng PHẢI được ghi vào ghi chú của event `attach`.
- **Rationale:** Không để SLA mất hoặc tính sai vì thiếu dữ liệu lịch, và người vận hành biết lý do.
- **Acceptance Criteria:**
  - AC1: Given khách hàng không có công ty mẹ (đường dẫn trống); When attach; Then task dùng lịch mặc định của công ty và ghi chú event `attach` nêu bước trống.
  - AC2: Given lịch mặc định của công ty cũng không dùng được; When attach; Then task không có lịch (24x7) và ghi chú nêu lý do.
  - AC3 (negative): Given người dùng không có quyền đọc record liên kết; When attach; Then lịch vẫn được tính đúng (REQ-SEC-005).
- **Verification Method:** Test
- **More Information:** Nguồn `definition` không dùng dự phòng: bị từ chối khi lưu (REQ-FUNC-039).

#### REQ-FUNC-021: Snapshot cấu hình lúc attach

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Lúc attach, hệ thống PHẢI sao chép thời lượng mục tiêu và lịch vào task. Sửa thời lượng mục tiêu hoặc lịch trên định nghĩa sau đó KHÔNG ĐƯỢC ảnh hưởng task đang chạy cho tới khi SLA Manager bấm "Tính lại" (REQ-INT-005).
- **Rationale:** Cam kết đã đo không đổi giữa chừng.
- **Acceptance Criteria:**
  - AC1 (negative: task không đổi): Given task đang chạy với mục tiêu 4 giờ; When sửa định nghĩa thành 8 giờ; Then task vẫn mục tiêu 4 giờ và `planned_end` không đổi.
  - AC2: Given task đang chạy với lịch L1; When sửa lịch của định nghĩa thành L2; Then task vẫn dùng L1.
  - AC3: Given record gắn task mới sau khi sửa; Then task mới dùng giá trị mới.
- **Verification Method:** Test

#### REQ-FUNC-052: Snapshot lịch lấy từ record

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Đổi lịch ở record gốc hoặc record liên kết sau khi attach KHÔNG ĐƯỢC ảnh hưởng task đang chạy cho tới khi SLA Manager bấm "Tính lại".
- **Rationale:** Nhất quán với REQ-FUNC-021 cho nguồn `record`.
- **Acceptance Criteria:**
  - AC1 (negative: task không đổi): Given task đang chạy dùng lịch L1 lấy từ công ty mẹ của khách hàng; When đổi lịch của công ty mẹ sang L2; Then task vẫn dùng L1.
  - AC2: Given như trên; When bấm Tính lại; Then task dùng L2.
- **Verification Method:** Test

#### REQ-FUNC-053: Không bắn bù mốc escalation thêm sau

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Mốc escalation thêm vào định nghĩa sau khi task đã đi qua mức phần trăm của mốc đó KHÔNG ĐƯỢC bắn bù; mốc có mức phần trăm chưa tới PHẢI bắn khi tới mức.
- **Rationale:** Tránh bắn hàng loạt khi sửa cấu hình.
- **Acceptance Criteria:**
  - AC1 (negative): Given task đang ở 80%; When thêm mốc 75%; Then mốc 75% không bao giờ bắn cho task này.
  - AC2: Given task đang ở 80%; When thêm mốc 90%; Then mốc 90% bắn khi tới 90%.
  - AC3 (sửa hoặc xóa mốc có sẵn): Given mốc đã tồn tại và task đang chạy; When sửa phần trăm, Server Action hoặc xóa mốc; Then thay đổi có hiệu lực ngay với mọi task đang chạy của định nghĩa (mốc là cấu hình dùng chung, task không giữ bản sao); `next_due_at` chỉ được tính lại ở lần xử lý nền kế tiếp của task.
- **Verification Method:** Test
- **More Information (ví dụ):** Định nghĩa D, mục tiêu 8 giờ, 24x7, mốc R50, R75, R100. Lúc 14:00: T1 gắn 09:00 (5 giờ, 62,5%, đã xử lý R50, `next_due_at` 15:00), T2 gắn 11:00 (37,5%, `next_due_at` 15:00), T3 gắn 13:00 (12,5%, `next_due_at` 17:00). (a) Thêm R90: T1, T2, T3 đều chưa tới 90% nên R90 bắn cho cả ba khi tới mức; task nào đã ≥ 90% thì R90 được đánh dấu đã xử lý, không bắn bù. (b) Sửa R75 thành 90: T1 vẫn được xử lý nền lúc 15:00, thấy 75% chưa tới 90% nên không bắn và tính lại `next_due_at` = 16:12. (c) Sửa R75 thành 55: T1 (62,5%) chỉ bắn lúc 15:00 vì `next_due_at` chưa được tính lại. (d) Xóa R75: mốc biến mất với mọi task, dòng đã xử lý của R75 bị xóa theo.

#### REQ-FUNC-022: Xác định vi phạm

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Khi thời gian đã trôi chạm hoặc vượt `planned_end`, hệ thống PHẢI bật dấu vi phạm của task và ghi event `breach` đúng một lần, bất kể phát hiện lúc record được cập nhật hay lúc xử lý theo thời gian. Task vi phạm vẫn ở `in_progress` cho tới khi stop. Event `breach` PHẢI được ghi trước khi xử lý các mốc escalation từ 100% trở lên.
- **Rationale:** Kết quả `breached` phải nhất quán dù record có được sửa hay không.
- **Acceptance Criteria:**
  - AC1: Given lịch 24x7, start 09:00, mục tiêu 4 giờ, không ai sửa record; When xử lý nền chạy lúc 13:01; Then dấu vi phạm bật và có đúng 1 event `breach`, stage vẫn `in_progress`.
  - AC2: Given như AC1 nhưng người dùng pause record lúc 14:00 trước khi xử lý nền chạy; Then dấu vi phạm bật ngay lúc pause (event `breach` ghi lúc 14:00), rồi task `paused`.
  - AC3: Given mốc 100% đến hạn cùng lúc vi phạm; Then trong nhật ký event `breach` có thời điểm không muộn hơn event `escalate` của mốc 100%.
  - AC4 (negative): Given task chưa tới `planned_end`; Then không có event `breach`.
- **Verification Method:** Test

#### REQ-FUNC-046: Dấu vi phạm không tắt và mức vượt được giữ

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Dấu vi phạm KHÔNG ĐƯỢC tắt lại sau khi bật. Mức vượt mục tiêu PHẢI được giữ qua các lần pause và resume, để mốc escalation trên 100% bắn đúng theo thời gian làm việc đã trôi.
- **Rationale:** Task đã quá hạn rồi pause và resume vẫn tính tiếp mức vượt.
- **Acceptance Criteria:**
  - AC1 (negative): Given dấu vi phạm đã bật; When resume; Then dấu vi phạm vẫn bật.
  - AC2: Given mục tiêu 4 giờ, mốc 120%, task đã trôi 4,4 giờ (110%) rồi pause và resume; Then mốc 120% bắn khi tổng thời gian đã trôi đạt 4,8 giờ.
- **Verification Method:** Test

#### 3.2.5 Escalation

#### REQ-FUNC-023: Escalation theo mốc phần trăm

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Mỗi định nghĩa PHẢI có thể có nhiều mốc escalation, mỗi mốc gồm phần trăm (số nguyên dương, lưu kiểu số thực; giá trị không nguyên bị từ chối khi lưu; trên 100 nghĩa là quá hạn), server action cần chạy và thứ tự. Khi task chạm phần trăm của mốc, hệ thống PHẢI chạy server action trên record gốc, ghi event `escalate`, và đánh dấu mốc đã xử lý.
- **Rationale:** Cảnh báo trước hạn, thông báo vi phạm và xử lý quá hạn cấu hình được.
- **Acceptance Criteria:**
  - AC1: Given mốc 75%, 100%, 120% và task mục tiêu 4 giờ (24x7); When đã trôi 3 giờ, 4 giờ, 4,8 giờ; Then 3 action lần lượt chạy trên record gốc, mỗi mốc 1 event `escalate`.
  - AC2 (negative): Given phần trăm = 0, âm, hoặc không nguyên (75,5); When lưu mốc; Then bị từ chối.
- **Verification Method:** Test

#### REQ-FUNC-024: Mỗi mốc bắn đúng một lần

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Mỗi mốc escalation của một task PHẢI được xử lý đúng một lần, kể cả khi xử lý nền chạy chồng hoặc chạy lại.
- **Rationale:** Gửi mail hay tạo activity trùng gây phiền và sai lệch.
- **Acceptance Criteria:**
  - AC1: Given mốc đã đến hạn; When xử lý nền chạy hai lần liên tiếp; Then action chạy 1 lần và có đúng 1 event `escalate`.
  - AC2 (negative): Given hai tiến trình xử lý nền cùng lúc trên cùng task; Then mốc không bị bắn hai lần.
- **Verification Method:** Test
- **More Information:** Cross-ref REQ-REL-002.

#### REQ-FUNC-025: Escalation không chạy trong thao tác lưu của người dùng

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Escalation PHẢI được xử lý ngoài thao tác lưu record của người dùng (không làm chậm hay thay đổi kết quả lần lưu đó).
- **Rationale:** Hành vi nhất quán, dễ test, không làm chậm người dùng.
- **Acceptance Criteria:**
  - AC1 (negative: chưa chạy trong lần lưu): Given thao tác lưu record làm task chạm mốc 75%; When lưu xong; Then server action chưa chạy và không có event `escalate` cho tới khi xử lý nền chạy.
- **Verification Method:** Test

#### REQ-FUNC-054: Không bắn escalation khi task kết thúc hoặc tạm dừng

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Hệ thống KHÔNG ĐƯỢC chạy escalation cho task đang `paused`, hoặc đã `achieved`, `breached`, `cancelled`.
- **Rationale:** Đồng hồ SLA không chạy thì không có mốc.
- **Acceptance Criteria:**
  - AC1 (negative): Given task `paused` đã qua thời điểm của mốc; When xử lý nền chạy; Then không có event `escalate`.
  - AC2 (negative): Given task `achieved` còn mốc chưa xử lý; When xử lý nền chạy; Then không có event `escalate`.
- **Verification Method:** Test

#### REQ-FUNC-055: Tính lại mốc khi resume

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Khi task resume, hệ thống PHẢI tính lại thời điểm của mọi mốc chưa xử lý xong theo thời gian làm việc còn lại.
- **Rationale:** Mốc phải bắn đúng theo thời gian đã trôi sau khi tạm dừng.
- **Acceptance Criteria:**
  - AC1: Given mục tiêu 4 giờ (24x7), mốc 75%, đã trôi 1 giờ rồi pause 6 giờ; When resume lúc 14:00; Then mốc 75% bắn lúc 16:00 (còn 2 giờ để đủ 3 giờ).
  - AC3 (negative): Given task vẫn `paused`; Then mốc không được tính lại và không bắn.
- **Verification Method:** Test

#### REQ-FUNC-026: Xử lý escalation lỗi

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Khi action của một mốc (email hoặc server action, REQ-FUNC-064) lỗi, hệ thống PHẢI cô lập lỗi (không ảnh hưởng mốc hoặc task khác), ghi event `escalate_failed` kèm thông báo lỗi và đánh dấu mốc đã xử lý ngay để không lặp vô hạn. Không có cơ chế thử lại (xem D12, `docs/TASKS.md`: gỡ bỏ sau khi xác định lỗi action gần như luôn deterministic, thử lại không tự sửa được, và email qua `mail.mail` đã có hàng chờ gửi lại riêng của Odoo).
- **Rationale:** Một action hỏng không được chặn các escalation khác; đơn giản hóa để người dùng phổ thông dễ cấu hình.
- **Acceptance Criteria:**
  - AC1: Given hai task cùng đến hạn, action của task 1 lỗi; Then task 1 có `escalate_failed`, task 2 vẫn có `escalate`.
  - AC2 (negative): Given mốc lỗi; When xử lý nền chạy lần nữa; Then action không chạy lại (mốc đã đánh dấu xử lý xong).
- **Verification Method:** Test

#### REQ-FUNC-027, 028, 056 đến 059: Đã gỡ bỏ (D12)

- **Status:** removed
- **Priority:** N/A
- **Owner:** @hieudt
- **Statement:** (Đã gỡ bỏ) Các REQ này từng đặc tả cơ chế thử lại escalation theo mẫu phút (`retry`, `retry_pattern`, `cancel_retry_on_stop`, event `escalate_retry`, model `sla.escalation.retry`). Toàn bộ cơ chế đã được gỡ bỏ theo quyết định D12 (`docs/TASKS.md`): lỗi action gần như luôn deterministic (bug, thiếu quyền, thiếu field) nên thử lại sau vài phút không tự sửa được; hành vi còn lại (REQ-FUNC-026) là chạy 1 lần, lỗi thì ghi `escalate_failed` ngay. Số REQ-ID giữ nguyên không tái sử dụng, theo quy ước truy vết (xem Revision History).
- **Rationale:** Đơn giản hóa theo yêu cầu người dùng; giảm bề mặt cấu hình cho người dùng phổ thông.
- **Acceptance Criteria:** N/A (removed)
- **Verification Method:** N/A

#### REQ-FUNC-064: Loại hành động escalation — email hoặc server action

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Mỗi mốc escalation PHẢI có `action_type` ∈ {`email`, `server_action`}, mặc định `email`. Với `server_action`, hành vi giữ nguyên như trước (chạy `ir.actions.server` trên record gốc, REQ-FUNC-038). Với `email` (mặc định), hệ thống PHẢI gửi một email qua `mail.mail` tới người nhận resolve theo REQ-FUNC-065, không yêu cầu người dùng tạo Server Action.
- **Rationale:** Tạo Server Action là rào cản kỹ thuật cho người dùng Odoo phổ thông; email là hành động escalation phổ biến nhất nên đưa thành mặc định có sẵn.
- **Acceptance Criteria:**
  - AC1: Given mốc `action_type=email` tới hạn; When xử lý nền chạy; Then 1 `mail.mail` được tạo với `email_to` đúng người nhận resolve được, và mốc đánh dấu xử lý xong.
  - AC2: Given mốc `action_type=server_action`; Then hành vi giống hệt trước khi có REQ này (không regress).
- **Verification Method:** Test

#### REQ-FUNC-065: Resolve người nhận email escalation

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Mốc kiểu `email` PHẢI có `email_recipient_type` ∈ {`fixed`, `field`, `responsible`}. `fixed` dùng địa chỉ cố định (`email_fixed_address`). `field` đọc một field Char trên model của định nghĩa (`email_field_id`) làm địa chỉ email trực tiếp. `responsible` đọc một field Many2one tới `res.users` hoặc `res.partner` trên model của định nghĩa rồi lấy `.email` của record đó. Lưu mốc PHẢI từ chối cấu hình thiếu trường bắt buộc theo loại đã chọn, hoặc field sai model/sai kiểu. Không resolve được người nhận lúc chạy (ví dụ field rỗng) PHẢI ghi `escalate_failed`, không raise lỗi ra ngoài tiến trình nền.
- **Rationale:** 3 cách phủ hầu hết nhu cầu thực tế mà không cần viết code: địa chỉ team cố định, field email có sẵn trên record, hoặc người phụ trách động theo từng record.
- **Acceptance Criteria:**
  - AC1: Given `email_recipient_type=fixed`, `email_fixed_address` rỗng; When lưu; Then bị từ chối.
  - AC2: Given `email_recipient_type=responsible`, `email_field_id` trỏ field không phải Many2one tới res.users/res.partner; When lưu; Then bị từ chối.
  - AC3 (negative): Given `email_recipient_type=field`, field rỗng trên record cụ thể; When xử lý nền chạy; Then ghi `escalate_failed`, không raise ra ngoài.
- **Verification Method:** Test

#### 3.2.6 Nhật ký, lỗi và vận hành

#### REQ-FUNC-029: Nhật ký sự kiện

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI ghi một event cho mỗi thay đổi trạng thái của task và mỗi hành động escalation, gồm thời điểm, task và loại sự kiện thuộc: `attach`, `pause`, `resume`, `complete`, `reset`, `cancel`, `breach`, `escalate`, `escalate_failed`, `error`. Ghi chú PHẢI có với event `attach` khi dùng lịch dự phòng hoặc mốc thay thế (REQ-FUNC-017, REQ-FUNC-020), event `reset` (field đã đổi), và event `escalate_failed`, `error` (thông báo lỗi).
- **Rationale:** Giải thích vì sao SLA ra kết quả như vậy và phát hiện bất thường.
- **Acceptance Criteria:**
  - AC1: Given vòng đời attach, pause, resume, stop; Then có đúng 4 event `attach`, `pause`, `resume`, `complete` theo thứ tự thời gian.
  - AC2 (negative): Given lần ghi record không làm đổi trạng thái; Then không có event mới.
  - AC3: Given event `escalate_failed`; Then ghi chú không rỗng và chứa thông báo lỗi.
  - AC4 (reset): Given reset với hành động `complete`; Then task cũ có event `complete` rồi `reset` (task đổi trạng thái nên có event của trạng thái đó, rồi event `reset` nêu field đã đổi).
- **Verification Method:** Test

#### REQ-FUNC-030: Lỗi của engine không chặn lưu record

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Khi việc đánh giá SLA của một record gặp lỗi (ví dụ domain trỏ tới field đã bị gỡ, lịch không xếp được hạn, vi phạm tính duy nhất khi hai giao dịch cùng gắn), hệ thống PHẢI hoàn tác phần SLA của record đó, ghi event `error` kèm record, định nghĩa liên quan và thông báo lỗi, và PHẢI vẫn lưu thay đổi của người dùng trên record.
- **Rationale:** Ưu tiên không chặn nghiệp vụ; bên compliance đã chấp nhận đánh đổi SLA có thể thiếu (R1, câu 6).
- **Acceptance Criteria:**
  - AC1: Given domain điều kiện trỏ tới field đã bị gỡ; When người dùng lưu record; Then record lưu thành công, không có task mới, có 1 event `error`.
  - AC2: Given calendar của định nghĩa bị sửa mất toàn bộ giờ làm sau khi định nghĩa đã lưu; When attach; Then không có task, có 1 event `error`, record vẫn lưu.
  - AC3 (negative): Given lỗi xảy ra ở record R1 trong lô gồm R1 và R2; Then R2 vẫn được đánh giá bình thường.
- **Verification Method:** Test
- **More Information:** Cross-ref REQ-OBS-001, REQ-FUNC-040, REQ-INT-022.

#### REQ-FUNC-040: Trạng thái xử lý của event lỗi

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Mỗi event `error` PHẢI có trạng thái "chưa xử lý" hoặc "đã xử lý". Event mới là "chưa xử lý". Trạng thái chuyển thành "đã xử lý" khi SLA Manager đánh dấu, hoặc khi việc đánh giá lại record liên quan hoàn tất không lỗi.
- **Rationale:** Cơ sở cho cảnh báo (REQ-INT-022) và đánh giá lại hàng loạt (REQ-FUNC-031).
- **Acceptance Criteria:**
  - AC1: Given event `error` mới; Then trạng thái "chưa xử lý".
  - AC2: Given SLA Manager đánh dấu đã xử lý; Then trạng thái đổi và số cảnh báo giảm 1.
  - AC3: Given đánh giá lại record liên quan thành công; Then event chuyển "đã xử lý".
  - AC4 (negative): Given đánh giá lại vẫn lỗi; Then event cũ vẫn "chưa xử lý" và có event `error` mới.
- **Verification Method:** Test

#### REQ-FUNC-031: Đánh giá lại hàng loạt từ danh sách event lỗi

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI cung cấp hành động "Đánh giá lại" hàng loạt trên danh sách event: với các event đã chọn, đánh giá lại các record liên quan sau khi nguyên nhân đã được sửa. Chạy lại dùng thời điểm hiện tại; muốn tính từ mốc cũ phải bật retroactive start trên định nghĩa; task đã `achieved`, `breached`, `cancelled` KHÔNG ĐƯỢC đổi.
- **Rationale:** Bù đắp rủi ro SLA thiếu âm thầm khi chấp nhận REQ-FUNC-030.
- **Acceptance Criteria:**
  - AC1: Given nguyên nhân đã sửa; When chọn 3 event `error` và bấm "Đánh giá lại"; Then 3 record được đánh giá và các task thiếu được tạo; 3 event chuyển "đã xử lý".
  - AC2 (negative): Given record có task đã `achieved`; When đánh giá lại; Then task không đổi.
  - AC3: Given SLA Manager chọn event không phải `error`; Then hành động bị từ chối hoặc bỏ qua event đó với thông báo.
  - AC4 (negative): Given người dùng `group_sla_user`; Then không có hành động này.
- **Verification Method:** Test

#### REQ-FUNC-032: Đánh giá lại thủ công

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI cho SLA Manager đánh giá lại một task hoặc một lô record theo yêu cầu, áp dụng cùng quy tắc như khi record thay đổi (REQ-FUNC-008), không kích hoạt reset theo field (REQ-FUNC-050), và dùng thời điểm hiện tại.
- **Rationale:** Bù cho REQ-FUNC-042 và cho lỗi cấu hình đã sửa.
- **Acceptance Criteria:**
  - AC1: Given start `[('partner_id.country_id','=',VN)]` và country của partner vừa đổi sang VN; When đánh giá lại; Then task được gắn.
  - AC2 (negative): Given đánh giá lại hai lần liên tiếp; Then lần hai không thay đổi gì (REQ-FUNC-015).
  - AC3 (negative): Given người dùng thuộc `group_sla_user`; Then không thực hiện được.
- **Verification Method:** Test

#### REQ-FUNC-033: Không gắn SLA mới sau khi archive

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Khi một định nghĩa bị lưu trữ (archive), hệ thống KHÔNG ĐƯỢC gắn task mới cho định nghĩa đó. Bỏ archive rồi thì định nghĩa hoạt động lại bình thường và KHÔNG ĐƯỢC sinh task trùng.
- **Rationale:** Ngừng áp dụng cho dữ liệu mới, giống ý nghĩa archive của Odoo.
- **Acceptance Criteria:**
  - AC1 (negative): Given định nghĩa D đã archive; When record mới thỏa start; Then không có task.
  - AC2: Given D đã archive rồi bỏ archive; When record đã có task đang chạy được sửa; Then vẫn đúng 1 task đang hoạt động.
- **Verification Method:** Test

#### REQ-FUNC-060: Task đang chạy tiếp tục sau khi archive định nghĩa

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Sau khi định nghĩa bị archive, các task đang hoạt động của định nghĩa PHẢI tiếp tục nhận stop, cancel, pause, resume, breach và escalation cho tới khi kết thúc, kể cả khi đó là định nghĩa cuối cùng của model.
- **Rationale:** SLA là cam kết với khách; hủy giữa chừng làm số liệu thiếu.
- **Acceptance Criteria:**
  - AC1: Given 30 task `in_progress` của D; When archive D rồi stop khớp trên một record; Then task của record đó kết thúc đúng.
  - AC2: Given D archive, task quá `planned_end`; When xử lý nền chạy; Then có event `breach` và escalation vẫn bắn.
  - AC3 (negative): Given D đã archive; When record mới thỏa start; Then không có task (REQ-FUNC-033).
  - AC4: Given task `in_progress` của D đã archive; When cancel khớp (chế độ `condition`); Then task `cancelled`.
  - AC5: Given task `in_progress` của D đã archive; When pause khớp rồi resume khớp; Then `paused` rồi `in_progress`.
  - AC6 (edge): Given D là định nghĩa cuối của model và đã archive; When stop khớp; Then task kết thúc (không kẹt ở `in_progress`).
- **Verification Method:** Test

#### REQ-FUNC-061: Không xóa định nghĩa còn task

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Hệ thống KHÔNG ĐƯỢC cho xóa định nghĩa còn bất kỳ task nào tham chiếu; người dùng PHẢI dùng archive.
- **Rationale:** Giữ lịch sử đo.
- **Acceptance Criteria:**
  - AC1 (negative): Given D còn 1 task đã `achieved`; When xóa D; Then bị từ chối với thông báo gợi ý archive.
  - AC2: Given D chưa từng có task; When xóa; Then thành công.
- **Verification Method:** Test

#### REQ-FUNC-034: Dọn task mồ côi

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Khi record gốc bị xóa, hệ thống PHẢI dọn các task SLA tương ứng cùng các bản ghi phụ thuộc (event) trong vòng 24 giờ sau khi record bị xóa; việc dọn không bắt buộc đồng bộ với thao tác xóa.
- **Rationale:** Liên kết tới record gốc không có ràng buộc khóa ngoại trong cơ sở dữ liệu; không dọn thì dữ liệu rác tích tụ.
- **Acceptance Criteria:**
  - AC1: Given record có 2 task; When xóa record rồi chạy job dọn; Then 2 task không còn.
  - AC2 (negative): Given record còn tồn tại; When chạy job dọn; Then task không bị xóa.
- **Verification Method:** Test
- **More Information:** Khi có `dwo_sla_analysis`, chỉ dọn task đã được chốt (2.6).

#### REQ-FUNC-035: Dọn nhật ký cũ

- **Status:** active
- **Priority:** Low
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI xóa event có tuổi lớn hơn số ngày cấu hình (REQ-INT-010) trong vòng 24 giờ sau khi quá ngưỡng.
- **Rationale:** Nhật ký tăng không giới hạn.
- **Acceptance Criteria:**
  - AC1: Given ngưỡng 90 ngày, event A cũ 100 ngày, event B cũ 10 ngày; When job dọn chạy; Then A bị xóa, B còn.
  - AC2 (negative, boundary): Given event cũ đúng 90 ngày; Then không bị xóa.
- **Verification Method:** Test

#### REQ-FUNC-036: Tỷ lệ đạt

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI cung cấp tỷ lệ đạt theo định nghĩa và theo kỳ của `end_dt` (trên báo cáo pivot và graph của task), bằng số task `achieved` chia tổng số task `achieved` và `breached`. Task `cancelled` KHÔNG ĐƯỢC tính vào tỷ lệ.
- **Rationale:** Số đo cơ bản (SLI) làm cơ sở cho dashboard SLO ở giai đoạn sau.
- **Acceptance Criteria:**
  - AC1: Given 8 `achieved`, 2 `breached`, 5 `cancelled` trong cùng định nghĩa và kỳ; Then tỷ lệ đạt = 80%.
  - AC2 (negative): Given kỳ không có task kết thúc; Then tỷ lệ hiển thị "không xác định" (không chia cho 0).
  - AC3: Given task kết thúc cuối tháng 9 và task kết thúc đầu tháng 10; Then mỗi task thuộc kỳ của `end_dt`.
- **Verification Method:** Test

#### REQ-FUNC-062: Số SLA đang vi phạm

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI cung cấp, trên bộ lọc "Đã vi phạm" và pivot của danh sách task (REQ-INT-011, REQ-INT-013), số SLA đang vi phạm theo định nghĩa, bằng số task có dấu vi phạm bật và còn `in_progress` hoặc `paused`, theo định nghĩa.
- **Rationale:** Quản lý thấy ngay SLA đang vi phạm cần xử lý.
- **Acceptance Criteria:**
  - AC1: Given 2 task `in_progress` có dấu vi phạm, 1 task `paused` có dấu vi phạm, 1 task `breached`, 1 task `in_progress` chưa vi phạm; Then số đang vi phạm = 3.
  - AC2 (negative): Given không có task nào vi phạm; Then số = 0.
- **Verification Method:** Test

### 3.3 Quality of Service

#### 3.3.1 Performance

#### REQ-PERF-001: Overhead trên model không có định nghĩa

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Với model không có định nghĩa SLA (không bị patch), việc cài `dwo_sla_core` PHẢI làm tăng thời gian ghi hàng loạt không quá 5% (ngưỡng đã chốt ở O-01) so với trước khi cài, đo trên môi trường benchmark được mô tả trong `040_Test-Plan.md`.
- **Rationale:** Mọi model đều chịu ảnh hưởng nên overhead phải nhỏ và đo được.
- **Acceptance Criteria:**
  - AC1: Given database có 1000 `res.partner` và không có định nghĩa cho `res.partner`; When tạo và ghi 1000 record trước và sau khi cài, lặp 10 lần; Then trung vị thời gian sau không quá 105% trung vị thời gian trước.
- **Verification Method:** Test
- **More Information:** Nếu không đạt thì áp dụng phương án thay thế của AD-01 trong `020` (rủi ro R-01 của TAD).

#### REQ-PERF-002: Số truy vấn không tăng theo số record

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Khi đánh giá một lô record cho cùng một định nghĩa, số truy vấn cơ sở dữ liệu giữa lô 100 record và lô 10 record PHẢI chênh nhau không quá 5.
- **Rationale:** Ghi hàng loạt (import, cron) không được làm quá tải.
- **Acceptance Criteria:**
  - AC1: Given lô 10 và lô 100 record của một định nghĩa; When đánh giá; Then |số truy vấn lô 100 − số truy vấn lô 10| ≤ 5.
- **Verification Method:** Test

#### REQ-PERF-003: Độ trễ xử lý theo thời gian

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Xử lý nền PHẢI chạy tối thiểu mỗi 1 phút. Với tối đa 200 mốc đến hạn mỗi chu kỳ, mốc escalation và việc phát hiện vi phạm PHẢI hoàn tất trong 2 phút kể từ thời điểm đến hạn (p95 qua 20 chu kỳ). Thời gian mỗi chu kỳ khi có 10 mốc đến hạn trong 100000 task đang chạy PHẢI không quá 2 lần thời gian khi có 10 mốc đến hạn trong 1000 task đang chạy.
- **Rationale:** Cảnh báo đúng lúc mà không quét toàn bộ.
- **Acceptance Criteria:**
  - AC1: Given 100000 task `in_progress` và 10 mốc đến hạn; When xử lý nền chạy; Then thời gian chu kỳ ≤ 2 × thời gian chu kỳ với 1000 task.
  - AC2: Given 200 mốc đến hạn tại thời điểm T; Then toàn bộ được xử lý trước T + 2 phút (p95 qua 20 lần).
- **Verification Method:** Test
- **More Information:** Cross-ref A-05.

#### 3.3.2 Security

#### REQ-SEC-001: Nhóm quyền

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI có hai nhóm quyền: `group_sla_user` (đọc định nghĩa, escalation, task, event, xem báo cáo) và `group_sla_manager` (thêm: sửa định nghĩa và escalation, bấm đánh giá lại, tính lại, xử lý event lỗi, chỉnh các tham số cấu hình SLA ở REQ-INT-010, REQ-INT-012, REQ-REL-002 qua màn hình Settings chuẩn của Odoo, vốn chỉ cho quản trị hệ thống lưu: người chỉnh được là SLA Manager đồng thời thuộc `base.group_system`; nhóm này mặc định kế thừa `group_sla_manager`). Người dùng không thuộc nhóm nào KHÔNG ĐƯỢC truy cập dữ liệu SLA trực tiếp, kể cả action và nút ở REQ-INT-006 và REQ-INT-014.
- **Rationale:** Tách quyền xem và quyền cấu hình.
- **Acceptance Criteria:**
  - AC1 (negative): Given người dùng không thuộc nhóm; When mở menu SLA; Then không thấy menu.
  - AC2 (negative): Given `group_sla_user`; When sửa định nghĩa; Then bị từ chối.
  - AC3: Given `group_sla_manager`; When sửa định nghĩa; Then thành công.
  - AC4: Given `group_sla_user`; When đọc định nghĩa và task; Then thấy được.
  - AC5: Given người dùng thuộc `base.group_system`; Then mặc định có quyền `group_sla_manager` và lưu được các tham số Settings của SLA; Given SLA Manager không thuộc `base.group_system`; When lưu Settings; Then bị từ chối theo cơ chế chuẩn của Odoo.
- **Verification Method:** Test

#### REQ-SEC-002: Người dùng nghiệp vụ không cần quyền SLA

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Người dùng sửa record gốc mà không thuộc nhóm SLA nào PHẢI vẫn kích hoạt được việc gắn và cập nhật task SLA; việc ghi dữ liệu SLA KHÔNG ĐƯỢC phụ thuộc quyền của người dùng đó.
- **Rationale:** Nhân viên xử lý ticket thường không có quyền với dữ liệu SLA.
- **Acceptance Criteria:**
  - AC1: Given người dùng chỉ có quyền sửa ticket; When đổi ticket thỏa start; Then task được tạo.
  - AC2 (negative): Given cùng người dùng; When cố đọc trực tiếp danh sách task; Then bị từ chối.
- **Verification Method:** Test

#### REQ-SEC-003: Cô lập đa công ty

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Người dùng chỉ thấy task, event và định nghĩa của các công ty mình được phép. Định nghĩa không gán công ty áp dụng cho mọi công ty; nếu model có field công ty thì chỉ định nghĩa trùng công ty của record (hoặc không gán công ty) được áp dụng cho record đó.
- **Rationale:** Hỗ trợ mở rộng đa công ty (C-07).
- **Acceptance Criteria:**
  - AC1 (negative): Given user thuộc công ty A; When xem task của công ty B; Then không thấy.
  - AC2 (negative): Given định nghĩa gán công ty A; When record công ty B thỏa start; Then không gắn.
  - AC3: Given định nghĩa không gán công ty; Then áp dụng cho cả A và B.
- **Verification Method:** Test

#### REQ-SEC-004: Quyền của server action và tài liệu cảnh báo

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Server action của escalation chạy theo quyền của user được gán cho xử lý nền. Form escalation PHẢI nêu điều này để SLA Manager không kỳ vọng action chạy với quyền của người đang sửa record.
- **Rationale:** Tránh cấu hình sai về quyền (C-08).
- **Acceptance Criteria:**
  - AC1: Given server action cần quyền X mà user của xử lý nền không có; When escalation chạy; Then lỗi được ghi `escalate_failed` (REQ-FUNC-026).
  - AC2: Given form escalation; Then có ghi chú nêu quyền của user xử lý nền.
- **Verification Method:** Test + Inspection

#### REQ-SEC-005: Đọc lịch qua record liên kết không phụ thuộc quyền người dùng

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Khi lấy lịch qua đường dẫn nhiều bước, hệ thống PHẢI tính được lịch đúng cho người dùng không có quyền đọc record liên kết, và KHÔNG ĐƯỢC làm lộ dữ liệu record liên kết cho người dùng đó.
- **Rationale:** Ví dụ công ty mẹ của khách hàng mà nhân viên không được xem.
- **Acceptance Criteria:**
  - AC1: Given người dùng không có quyền đọc công ty mẹ; When attach; Then task dùng đúng lịch của công ty mẹ.
  - AC2 (negative): Given cùng người dùng; When xem task; Then không có dữ liệu nào của công ty mẹ ngoài tên calendar áp dụng.
- **Verification Method:** Test

#### REQ-SEC-006: Task và event chỉ do hệ thống ghi

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Task và event SLA CHỈ được tạo, sửa và xóa bởi hệ thống (đánh giá, xử lý nền, dọn dẹp, và các hành động đánh giá lại, tính lại); không người dùng nào, kể cả SLA Manager, được tạo, sửa hoặc xóa trực tiếp. Ngoại lệ duy nhất: SLA Manager được đổi trạng thái xử lý của event `error` (REQ-FUNC-040).
- **Rationale:** Dữ liệu đo phải đáng tin cậy.
- **Acceptance Criteria:**
  - AC1 (negative): Given SLA Manager; When thử tạo, sửa hoặc xóa task, hoặc tạo, xóa event, hoặc sửa field khác ngoài trạng thái xử lý của event, qua giao diện; Then không có thao tác nào khả dụng.
  - AC3: Given SLA Manager; When đánh dấu event `error` là đã xử lý; Then thành công.
  - AC2: Given SLA Manager bấm "Tính lại"; Then task thay đổi (đi qua hành động hợp lệ).
- **Verification Method:** Test

#### 3.3.3 Reliability

#### REQ-REL-001: An toàn khi đồng thời

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Khi hai giao dịch đồng thời tác động lên cùng record hoặc cùng task (ví dụ người dùng stop task đúng lúc xử lý nền đang chạy escalation), hệ thống PHẢI không mất dữ liệu và không tạo trùng; một bên PHẢI được thử lại ở lần xử lý kế tiếp, và lần lưu record của người dùng KHÔNG ĐƯỢC chờ khóa do xử lý nền quá 5 giây (p95).
- **Rationale:** Odoo chạy giao dịch ở mức REPEATABLE READ nên xung đột tuần tự hóa có thể xảy ra.
- **Acceptance Criteria:**
  - AC1: Given xử lý nền đang xử lý task T và người dùng cùng lúc làm stop khớp trên T; Then một bên thành công, bên kia được thử lại; sau đó có đúng 1 trạng thái cuối nhất quán, không event trùng.
  - AC2: Given server action chậm 30 giây trong xử lý nền; When người dùng lưu record có task khác; Then lần lưu chờ khóa không quá 5 giây (p95 qua 20 lần).
- **Verification Method:** Test

#### REQ-REL-002: Xử lý nền khóa và lưu từng task, báo tiến độ, nhường tài nguyên

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Xử lý nền PHẢI xử lý từng task một: khóa đúng task đang xử lý, lưu kết quả và báo tiến độ cho trình chạy cron của Odoo (số task đã xử lý và số task còn đến hạn) ngay sau mỗi task. Mỗi lần được gọi, xử lý nền PHẢI dừng khi hết task đến hạn, khi chạm kích thước lô tối đa (mặc định 50 task, cấu hình được, xem O-05), hoặc khi thời gian còn lại của lần chạy do trình chạy cron cấp bằng 0. Phần còn lại PHẢI được xử lý ở lần gọi kế tiếp (không mất, không lặp). Xử lý nền KHÔNG ĐƯỢC bỏ qua giới hạn thời gian mà trình chạy cron cấp.
- **Rationale:** Giữ khóa chỉ trong thời gian xử lý một task, nhường tài nguyên cho cron và tiến trình khác, an toàn khi bị ngắt. Dùng cơ chế báo tiến độ của `ir.cron` (R9).
- **Acceptance Criteria:**
  - AC1: Given 120 task đến hạn và kích thước lô tối đa 50; When trình chạy cron gọi xử lý nền ba lần liên tiếp; Then lần 1 xử lý 50 task (báo tiến độ 50 lần, số còn lại cuối cùng 70), lần 2 xử lý 50 task (còn lại 20), lần 3 xử lý 20 task (còn lại 0).
  - AC2: Given 3 task đến hạn và tiến trình bị dừng ngay sau khi task thứ nhất đã báo tiến độ; When chạy lại; Then task thứ nhất không bị xử lý lại, hai task còn lại được xử lý.
  - AC3 (negative): Given kích thước lô tối đa cấu hình 0 hoặc âm; When lưu cấu hình; Then bị từ chối.
  - AC4 (negative): Given 100 task đến hạn và thời gian còn lại của lần chạy báo về bằng 0 sau task đầu tiên; When xử lý nền chạy; Then chỉ task đầu tiên được xử lý trong lần gọi này và số còn lại báo là 99.
  - AC5: Given xử lý nền đang xử lý task T1 (server action chạy 30 giây) trong số các task đến hạn gồm T1 và T2; When người dùng stop task T2 trong lúc đó; Then lần lưu không phải chờ T1 xử lý xong (T2 chưa bị khóa).
- **Verification Method:** Test
- **More Information:** Cross-ref REQ-PERF-003, REQ-REL-001. Cơ chế: `ir.cron._commit_progress` của Odoo 19 trả về thời gian còn lại của lần chạy; trình chạy cron gọi lại hàm trong lúc còn task chưa xử lý, ít nhất 10 lần gọi và ít nhất 10 giây rồi mới nhường, nên hàm phải tự dừng khi thời gian còn lại bằng 0 (R9).

#### 3.3.4 Availability

N/A — module chạy bên trong Odoo, tính sẵn sàng do nền tảng Odoo và hạ tầng quyết định; không đặt mục tiêu uptime riêng. Yêu cầu liên quan: REQ-FUNC-030 (lỗi của module không làm Odoo ngừng lưu record).

#### 3.3.5 Observability

#### REQ-OBS-001: Event lỗi có đủ ngữ cảnh

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Mỗi lỗi của engine PHẢI được ghi thành event `error` chứa tên model, id record, tên định nghĩa và thông báo lỗi.
- **Rationale:** Cần điều tra được nguyên nhân (REQ-FUNC-031).
- **Acceptance Criteria:**
  - AC1: Given lỗi engine; Then event `error` có model, id record, tên định nghĩa và thông báo lỗi không rỗng.
- **Verification Method:** Test

#### REQ-OBS-002: Ghi log máy chủ cho lỗi engine

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Mỗi lỗi của engine PHẢI được ghi vào log máy chủ ở mức ERROR kèm tên model, id record và tên định nghĩa.
- **Rationale:** Vận hành tìm lỗi qua log hệ thống.
- **Acceptance Criteria:**
  - AC1: Given lỗi engine; Then log máy chủ có 1 dòng mức ERROR chứa tên model, id record và tên định nghĩa.
- **Verification Method:** Test

#### REQ-OBS-003: Không ghi dữ liệu nhạy cảm trong nhật ký

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Event và log lỗi KHÔNG ĐƯỢC chứa giá trị field của record gốc (chỉ chứa định danh: tên model, id). Thông báo lỗi gốc của ngoại lệ có thể trích nguyên giá trị field, nên trước khi ghi `note` hoặc log, hệ thống PHẢI thay mọi giá trị field chuỗi (`char`, `text`, `html`; từ 3 ký tự trở lên) của record gốc xuất hiện trong thông báo bằng `<redacted>`.
- **Rationale:** Bảo vệ dữ liệu nhạy cảm.
- **Acceptance Criteria:**
  - AC1 (negative): Given record có field chứa chuỗi `SECRET-123` gây lỗi engine; Then chuỗi này không xuất hiện trong ghi chú event hay log.
  - AC2 (negative): Given ngoại lệ gốc có thông báo "cannot plan for SECRET-123" (giá trị field lọt vào thông báo) hoặc server action của escalation báo lỗi trích giá trị field; Then `note` của event `error` hoặc `escalate_failed` và log chỉ chứa "cannot plan for <redacted>" (phần còn lại của thông báo được giữ để điều tra).
- **Verification Method:** Test + Inspection

### 3.4 Compliance

N/A — không có chuẩn hoặc quy định bên ngoài trực tiếp ràng buộc module. Rủi ro SLA thiếu do lỗi đã được bên compliance chấp nhận kèm biện pháp bù (REQ-FUNC-030, REQ-FUNC-031). Nếu hợp đồng khách hàng đặt yêu cầu lưu trữ khác, bổ sung ở đây.

### 3.5 Design and Implementation

#### 3.5.1 Installation

#### REQ-INST-001: Cài, nâng cấp, gỡ sạch

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Hệ thống PHẢI cài đặt, nâng cấp và gỡ `dwo_sla_core` thành công trên database đã có dữ liệu mà không làm hỏng dữ liệu hay hành vi của các model khác; sau khi gỡ, không còn thay đổi hành vi nào lên tạo, sửa record của các model.
- **Rationale:** Module quan sát mọi model nên rủi ro cài và gỡ cao hơn thông thường.
- **Acceptance Criteria:**
  - AC1: Given database có dữ liệu `res.partner`, `sh.helpdesk.ticket`; When cài, nâng cấp rồi gỡ module; Then không lỗi, dữ liệu gốc nguyên vẹn, và sau gỡ không còn event hay task phát sinh khi sửa record.
- **Verification Method:** Test

#### REQ-INST-002: Phụ thuộc tối thiểu

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** `dwo_sla_core` PHẢI chỉ khai báo phụ thuộc vào module chuẩn `base` và `resource`, cộng `web` và `mail` đã được duyệt (Deviation D1, D10 bên dưới); mọi phụ thuộc khác PHẢI được bổ sung vào tài liệu này kèm lý do. Module KHÔNG ĐƯỢC phụ thuộc vào `sh_all_in_one_helpdesk`, `nev_*`, `dwo_*` khác hay module OCA.
- **Rationale:** Dùng được cho model bất kỳ, kể cả ngoài helpdesk (C-02).
- **Acceptance Criteria:**
  - AC1: Given file khai báo module; When kiểm tra danh sách phụ thuộc; Then chỉ gồm `base`, `resource`, `web` và `mail` (D1, D10).
- **Verification Method:** Inspection
- **Deviation (đã duyệt, xem `docs/TASKS.md` D1):** thêm `web` vào `depends` vì các view bắt buộc của module (form domain widget INT-002/003, pivot/graph INT-012/013, settings view) cần asset JS/XML của `web`; `base`/`resource` không đủ để render các view này trong Odoo 19.
- **Deviation (đã duyệt, xem `docs/TASKS.md` D10):** thêm `mail` vào `depends` vì tính năng `retroactive_pause` (031) đọc trực tiếp model `mail.tracking.value` và điều kiện bật tính năng là model đích có mixin `mail.thread`; không có `mail` thì model `mail.tracking.value` không tồn tại và code sập ngay khi dùng tính năng (phát hiện khi chạy lại full test suite trên DB sạch, không phải chỉ mất tính năng).

#### REQ-INST-003: Không thêm cột vào bảng của model gốc

- **Status:** active
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Việc cài `dwo_sla_core` KHÔNG ĐƯỢC thêm field hay cột nào vào model hoặc bảng của model được gắn SLA.
- **Rationale:** Ràng buộc C-03.
- **Acceptance Criteria:**
  - AC1: Given danh sách cột của bảng `res_partner` và `sh_helpdesk_ticket` trước khi cài; When cài module; Then danh sách cột sau khi cài giống hệt.
- **Verification Method:** Test

#### REQ-INST-004: Gỡ module demo dọn dữ liệu của nó

- **Status:** draft
- **Priority:** Low
- **Owner:** @hieudt
- **Statement:** Khi gỡ `dwo_sla_demo_ticket`, hệ thống PHẢI xóa các task của model `demo.ticket` để việc xóa định nghĩa mẫu không bị chặn.
- **Rationale:** Task trỏ tới định nghĩa không cho xóa (REQ-FUNC-061).
- **Acceptance Criteria:**
  - AC1: Given `dwo_sla_demo_ticket` đã cài và có task của `demo.ticket`; When gỡ module demo; Then không lỗi, task của `demo.ticket` không còn, và các định nghĩa mẫu bị xóa.
- **Verification Method:** Test

#### 3.5.2 Build and Delivery

#### REQ-BUILD-001: Tuân thủ lint của repo

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Code Python của `dwo_sla_core` PHẢI đạt pylint theo `.pylintrc` của repo với điểm không dưới 9, và mã JS (nếu có) PHẢI qua eslint và prettier của repo.
- **Rationale:** CI của repo yêu cầu (R8); `dwo_*` thuộc diện bị lint.
- **Acceptance Criteria:**
  - AC1: Given các file Python của module; When chạy pylint với `--fail-under=9`; Then thành công.
- **Verification Method:** Test (CI lint)

#### 3.5.3 Distribution

N/A — module không có yêu cầu triển khai phân tán riêng; triển khai theo quy trình build và deploy của repo (R8).

#### 3.5.4 Maintainability

#### REQ-MAINT-001: Comment lý do tại chỗ cài đặt

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Mã nguồn PHẢI có comment tại chỗ cài đặt giải thích các quyết định không hiển nhiên: vì sao cần quan sát cả lần sửa trực tiếp lẫn việc tính lại field compute có lưu; vì sao engine lỗi không chặn lưu record và đánh đổi kèm biện pháp bù; việc đánh giá lại an toàn nhưng dùng thời điểm hiện tại và không sửa ngược task đã kết thúc; ý nghĩa của nhật ký sự kiện; và giới hạn của field compute không lưu.
- **Rationale:** Người đọc code không phải quay lại tài liệu.
- **Acceptance Criteria:**
  - AC1: Given mã nguồn module; When rà soát (code review); Then mỗi mục nêu trên có comment tương ứng tại vị trí cài đặt.
- **Verification Method:** Inspection

#### REQ-MAINT-002: Bộ test tự động

- **Status:** draft
- **Priority:** High
- **Owner:** @hieudt
- **Statement:** Module PHẢI có bộ test tự động chạy được bằng một lệnh trên database trống, chạy trên model `res.partner` có sẵn của `base` (chứng minh không phụ thuộc model ticket), và một bộ end-to-end trên `demo.ticket`.
- **Rationale:** Cơ sở kiểm chứng toàn bộ REQ.
- **Acceptance Criteria:**
  - AC1: Given database trống; When chạy lệnh test của CI cho module; Then toàn bộ test chạy và báo kết quả đạt hoặc không đạt.
- **Verification Method:** Test (CI)

#### 3.5.5 Reusability

#### REQ-REUSE-001: Không phá vỡ điểm mở rộng trong cùng phiên bản chính

- **Status:** active
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Trong cùng phiên bản chính, `dwo_sla_core` KHÔNG ĐƯỢC đổi tên, đổi tham số hoặc đổi kiểu trả về của các điểm mở rộng ở REQ-INT-007, REQ-INT-015 đến REQ-INT-018.
- **Rationale:** `dwo_sla_analysis` và module theo model phụ thuộc vào chúng.
- **Acceptance Criteria:**
  - AC1: Given module mẫu override toàn bộ điểm mở rộng; When nâng cấp `dwo_sla_core` trong cùng phiên bản chính; Then module mẫu vẫn chạy và bộ test điểm mở rộng vẫn đạt.
  - AC2 (negative): Given thay đổi chữ ký điểm mở rộng trong merge request; Then bộ test điểm mở rộng thất bại.
- **Verification Method:** Test + Inspection
- **More Information:** Thay đổi bắt buộc theo REQ-CM-001.

#### 3.5.6 Portability

#### REQ-PORT-001: Môi trường chạy

- **Status:** draft
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Module PHẢI chạy trên Odoo 19 (image `odoo:19.0-20260421`) với PostgreSQL, trong container theo quy trình deploy của repo, không dùng thư viện Python ngoài những gì image đã có.
- **Rationale:** C-01, C-02.
- **Acceptance Criteria:**
  - AC1: Given image build theo Dockerfile của repo; When cài module; Then thành công mà không cần cài thêm gói.
- **Verification Method:** Test

#### 3.5.7 Cost, 3.5.8 Deadline, 3.5.9 Proof of Concept

N/A — không có ràng buộc ngân sách, hạn chót hay POC riêng cho tài liệu này. Giai đoạn 0 (spike) của kế hoạch triển khai là hoạt động kiểm chứng giả định (2.5), không phải POC độc lập.

#### 3.5.10 Change Management

#### REQ-CM-001: Thay đổi phá vỡ điểm mở rộng và dữ liệu

- **Status:** draft
- **Priority:** Medium
- **Owner:** @hieudt
- **Statement:** Thay đổi làm đổi chữ ký điểm mở rộng hoặc cấu trúc dữ liệu SLA PHẢI được phân loại là thay đổi gây phá vỡ, PHẢI có script nâng cấp (migration) cho dữ liệu hiện có, và PHẢI được ghi vào Revision History của tài liệu này.
- **Rationale:** Module khác và dữ liệu đo đang chạy phụ thuộc.
- **Acceptance Criteria:**
  - AC1: Given thay đổi gây phá vỡ; When tạo merge request; Then có script nâng cấp và dòng ghi Revision History.
- **Verification Method:** Inspection

### 3.6 AI/ML

N/A — module không có thành phần AI/ML.

---

## 4. Verification

Status `Implemented` nghĩa là đã có code và test tự động theo `060` (các ca còn kiểm thủ công hoặc Inspection được liệt kê ở `docs/TASKS.md` T13). Cột Test/Artifact Link trỏ tới nhóm test (TG-xx), đặc tả trong `050_Test-Design-Specification.md` và các ca trong `060_Test-Case-Specification.md`.

**Nhóm test:** TG-01 Gắn và kết thúc · TG-02 Pause và resume · TG-03 Stop quanh hạn · TG-04 Cancel và reset · TG-05 Ba cấu hình dễ sai · TG-06 Giờ làm việc · TG-07 Retroactive · TG-08 Escalation · TG-09 Nhiều SLA · TG-10 Tính generic · TG-11 Đổi cấu hình khi đang chạy · TG-12 Lỗi và đồng thời · TG-13 Field compute có lưu · TG-14 Hạ tầng · TG-15 Nguồn lịch · TG-16 Phân quyền và đa công ty · TG-17 Giao diện và báo cáo · TG-18 Hiệu năng · TG-19 Điểm mở rộng.

| Requirement ID | Verification Method | Test/Artifact Link | Status | Evidence |
|----------------|--------------------|--------------------|--------|----------|
| REQ-INT-001 | Test + Demonstration | TG-17 | Implemented | |
| REQ-INT-002 | Inspection + Demonstration | TG-17 | Implemented | |
| REQ-INT-003 | Test + Demonstration | TG-17 | Implemented | |
| REQ-INT-004 | Test + Demonstration | TG-17 | Implemented | |
| REQ-INT-005 | Test | TG-11, TG-17 | Implemented | |
| REQ-INT-006 | Test + Demonstration | TG-17, TG-11 | Implemented | |
| REQ-INT-011 | Test | TG-17 | Implemented | |
| REQ-INT-012 | Test | TG-17 | Implemented | |
| REQ-INT-013 | Test + Demonstration | TG-17 | Implemented | |
| REQ-INT-014 | Test | TG-17 | Implemented | |
| REQ-INT-020 | Test | TG-17, TG-13 | Implemented | |
| REQ-INT-021 | Test | TG-17, TG-12 | Implemented | |
| REQ-INT-022 | Test + Demonstration | TG-12, TG-17 | Implemented | |
| REQ-INT-023 | Test | TG-03, TG-17 | Implemented | |
| REQ-INT-007 | Test | TG-19, TG-15 | Implemented | |
| REQ-INT-008 | Test | TG-08 | Implemented | |
| REQ-INT-009 | Test | TG-15 | Implemented | |
| REQ-INT-010 | Test | TG-14 | Implemented | |
| REQ-INT-015 | Test | TG-19 | Implemented | |
| REQ-INT-016 | Test | TG-19 | Implemented | |
| REQ-INT-017 | Test | TG-19 | Implemented | |
| REQ-INT-018 | Test | TG-19 | Implemented | |
| REQ-INT-019 | Test | TG-08, TG-16 | Implemented | |
| REQ-FUNC-001 | Test | TG-10 | Implemented | |
| REQ-FUNC-002 | Test | TG-14 | Implemented | |
| REQ-FUNC-003 | Test | TG-01, TG-14 | Implemented | |
| REQ-FUNC-038 | Test | TG-08 | Implemented | |
| REQ-FUNC-039 | Test | TG-15 | Implemented | |
| REQ-FUNC-041 | Test | TG-07, TG-14 | Implemented | |
| REQ-FUNC-004 | Test | TG-01, TG-14 | Implemented | |
| REQ-FUNC-005 | Test | TG-13 | Implemented | |
| REQ-FUNC-042 | Test + Inspection | TG-13, TG-17 | Implemented | |
| REQ-FUNC-006 | Test | TG-01 | Implemented | |
| REQ-FUNC-007 | Test | TG-01, TG-04 | Implemented | |
| REQ-FUNC-008 | Test | TG-04, TG-05 | Implemented | |
| REQ-FUNC-009 | Test | TG-01, TG-03 | Implemented | |
| REQ-FUNC-010 | Test | TG-04 | Implemented | |
| REQ-FUNC-011 | Test | TG-02 | Implemented | |
| REQ-FUNC-037 | Test | TG-02 | Implemented | |
| REQ-FUNC-048 | Test | TG-02 | Implemented | |
| REQ-FUNC-012 | Test | TG-04 | Implemented | |
| REQ-FUNC-013 | Test | TG-04, TG-13 | Implemented | |
| REQ-FUNC-050 | Test | TG-04 | Implemented | |
| REQ-FUNC-051 | Test | TG-04 | Implemented | |
| REQ-FUNC-014 | Test | TG-09, TG-12 | Implemented | |
| REQ-FUNC-015 | Test | TG-01 | Implemented | |
| REQ-FUNC-016 | Test | TG-05 | Implemented | |
| REQ-FUNC-017 | Test | TG-07 | Implemented | |
| REQ-FUNC-018 | Test | TG-06 | Implemented | |
| REQ-FUNC-043 | Test | TG-06, TG-02 | Implemented | |
| REQ-FUNC-044 | Test | TG-02, TG-03 | Implemented | |
| REQ-FUNC-019 | Test | TG-15 | Implemented | |
| REQ-FUNC-020 | Test | TG-15 | Implemented | |
| REQ-FUNC-021 | Test | TG-11 | Implemented | |
| REQ-FUNC-052 | Test | TG-15, TG-11 | Implemented | |
| REQ-FUNC-053 | Test | TG-11, TG-08 | Implemented | |
| REQ-FUNC-022 | Test | TG-03, TG-08 | Implemented | |
| REQ-FUNC-046 | Test | TG-03 | Implemented | |
| REQ-FUNC-023 | Test | TG-08 | Implemented | |
| REQ-FUNC-024 | Test | TG-08 | Implemented | |
| REQ-FUNC-025 | Test | TG-08 | Implemented | |
| REQ-FUNC-054 | Test | TG-08 | Implemented | |
| REQ-FUNC-055 | Test | TG-08, TG-02 | Implemented | |
| REQ-FUNC-026 | Test | TG-08 | Implemented | |
| REQ-FUNC-027 | N/A | N/A | Removed (D12) | |
| REQ-FUNC-056 | N/A | N/A | Removed (D12) | |
| REQ-FUNC-057 | N/A | N/A | Removed (D12) | |
| REQ-FUNC-058 | N/A | N/A | Removed (D12) | |
| REQ-FUNC-059 | N/A | N/A | Removed (D12) | |
| REQ-FUNC-028 | N/A | N/A | Removed (D12) | |
| REQ-FUNC-064 | Test | TG-08 | Implemented | |
| REQ-FUNC-065 | Test | TG-08 | Implemented | |
| REQ-FUNC-029 | Test | TG-01, TG-02, TG-04, TG-08 | Implemented | |
| REQ-FUNC-030 | Test | TG-12 | Implemented | |
| REQ-FUNC-040 | Test | TG-12 | Implemented | |
| REQ-FUNC-031 | Test | TG-12, TG-17 | Implemented | |
| REQ-FUNC-032 | Test | TG-13, TG-01 | Implemented | |
| REQ-FUNC-033 | Test | TG-11 | Implemented | |
| REQ-FUNC-060 | Test | TG-11 | Implemented | |
| REQ-FUNC-061 | Test | TG-11, TG-14 | Implemented | |
| REQ-FUNC-034 | Test | TG-14 | Implemented | |
| REQ-FUNC-035 | Test | TG-14 | Implemented | |
| REQ-FUNC-036 | Test | TG-17 | Implemented | |
| REQ-FUNC-062 | Test | TG-17 | Implemented | |
| REQ-PERF-001 | Test | TG-18 | Implemented | |
| REQ-PERF-002 | Test | TG-18 | Implemented | |
| REQ-PERF-003 | Test | TG-18 | Implemented | |
| REQ-SEC-001 | Test | TG-16 | Implemented | |
| REQ-SEC-002 | Test | TG-16 | Implemented | |
| REQ-SEC-003 | Test | TG-16 | Implemented | |
| REQ-SEC-004 | Test + Inspection | TG-16, TG-08 | Implemented | |
| REQ-SEC-005 | Test | TG-16, TG-15 | Implemented | |
| REQ-SEC-006 | Test | TG-16 | Implemented | |
| REQ-REL-001 | Test | TG-12 | Implemented | |
| REQ-REL-002 | Test | TG-08, TG-12 | Implemented | |
| REQ-OBS-001 | Test | TG-12 | Implemented | |
| REQ-OBS-002 | Test | TG-12 | Implemented | |
| REQ-OBS-003 | Test + Inspection | TG-12 | Implemented | |
| REQ-INST-001 | Test | TG-14 | Implemented | |
| REQ-INST-002 | Inspection | TG-14 | Implemented | |
| REQ-INST-003 | Test | TG-14 | Implemented | |
| REQ-INST-004 | Test | TG-14 | Implemented | |
| REQ-BUILD-001 | Test (CI lint) | CI pipeline | Implemented | |
| REQ-MAINT-001 | Inspection | Code review checklist | Implemented | |
| REQ-MAINT-002 | Test (CI) | CI pipeline | Implemented | |
| REQ-REUSE-001 | Test + Inspection | TG-19 | Implemented | |
| REQ-PORT-001 | Test | TG-14 | Implemented | |
| REQ-CM-001 | Inspection | MR checklist | Implemented | |

---

## 5. Appendixes

### A. Các mục còn mở

| ID | Mục | Việc cần làm |
|----|-----|--------------|
| O-01 | Ngưỡng overhead hook (REQ-PERF-001) | ĐÃ ĐÓNG 2026-10-12: bên sở hữu sản phẩm chốt 5% (trung vị sau khi cài không quá 105% trung vị trước khi cài). |
| O-02 | Spike giai đoạn 0 | Kiểm chứng A-01, A-02, A-03; cú pháp view và domain widget Odoo 19; action `binding_model_id` lọc theo record; chữ ký hàm tính lại field compute có lưu có ổn định giữa các bản Odoo; hành vi của Odoo khi chạy server action trong công ty không nằm trong danh sách công ty của user cron (REQ-INT-019); các giá trị mẫu trong AC của REQ-FUNC-018. |
| O-03 | Giá trị mặc định số ngày lưu nhật ký (REQ-INT-010) | Đề xuất 365 ngày; chốt ở giai đoạn 1. |
| O-04 | Giá trị mặc định khoảng "Sắp đến hạn" X (REQ-INT-012) | Đề xuất 4 giờ; chốt ở giai đoạn 5. |
| O-05 | Kích thước lô của xử lý nền (REQ-REL-002) | Đề xuất 50 task; chốt ở giai đoạn 4. |
| O-06 | Chuyển các REQ từ `draft` sang `active` | O-01 đã chốt; còn `draft`: CM-001, INST-004, MAINT-002, PORT-001 (xem Revision History 0.3). |
| O-07 | Record mở lại sau khi SLA đã kết thúc (REQ-FUNC-007, REQ-FUNC-012) | Đã chốt cho phiên bản 1: task `achieved` hoặc `breached` không bị reset và không gắn lại; ticket đã đóng rồi mới mở lại thì không đo thêm. Cấu hình khuyến nghị cho ca ticket có thể mở lại: pause khi chờ khách và khi đã giải quyết (`resolved`), resume ở chế độ `pause_unmatched`, stop chỉ khi đóng hẳn (`closed`), để một task duy nhất bao trùm cả vòng đời. Muốn đo riêng thời gian xử lý sau khi mở lại: tạo định nghĩa thứ hai (ví dụ "Xử lý sau mở lại") có start khớp khi ticket được mở lại; chỉ đo được lần mở lại đầu tiên, đo nhiều lần mở lại để phiên bản sau cùng `dwo_sla_analysis`. Còn cần đối chiếu ở spike (A-03) xem ServiceNow có gắn SLA mới khi start khớp lại sau khi SLA kết thúc hay không (chỉ có bằng chứng gián tiếp từ cộng đồng). |

### B. Truy vết từ bản thiết kế gốc

Bản thiết kế gốc (R1) đã chốt 10 câu hỏi mở; SRS này phản ánh: hook (câu 1; bản thiết kế gốc nêu hook toàn cục trên `base`, kiến trúc đã chọn patch động chỉ trên model có định nghĩa, xem AD-01 của `020`), không gắn lại sau `achieved` hoặc `breached` (câu 2, REQ-FUNC-007), retry theo mẫu (câu 3; gỡ bỏ sau đó theo D12, xem `docs/TASKS.md`), đa công ty (câu 4, REQ-SEC-003), field compute có lưu (câu 5, REQ-FUNC-005), engine lỗi không chặn lưu (câu 6, REQ-FUNC-030, REQ-FUNC-031, REQ-FUNC-040, REQ-INT-022), reset theo field (câu 7, REQ-FUNC-013, REQ-FUNC-050, REQ-FUNC-051), SLO để giai đoạn sau (câu 8, mục 2.6), đổi cấu hình khi đang chạy (câu 9, REQ-FUNC-021, REQ-FUNC-052, REQ-FUNC-053, REQ-FUNC-033, REQ-FUNC-060, REQ-FUNC-061, REQ-FUNC-017), thời lượng mục tiêu chỉ nguồn cố định cộng điểm mở rộng (câu 10, REQ-INT-015).
