# Test Case Specification

**Document ID:** TCS-SLACORE-001
**Version:** 0.3 | **Date:** 2026-11-12 | **Status:** Draft
**Project:** `dwo_sla_core` 19.0.1.1.0 | **Test Level:** Integration và System (theo ISO/IEC/IEEE 29119-3:2021, mục Test Case Specification)
**Prepared by:** hieudt | **Reviewed by:** chưa có
**Related Test Plan:** TP-SLACORE-001 (`040_Test-Plan.md`)
**Related TDS:** TDS-SLACORE-001 (`050_Test-Design-Specification.md`)

> **Ghi chú 2026-11-12 (19.0.1.1.0):** bản 0.3 mô tả đủ 435 hàm test trong `tests/`, gồm các nhóm TG-21 đến TG-32 (field phân loại, retroactive pause, timezone override, thời lượng đồng hồ, bật/tắt, `[]` là chưa cấu hình, timezone bắt buộc, giao diện định nghĩa, Re-check, Apply Current Settings, Apply to Existing Records, chip trạng thái, Note, Duration live). Các test case mới nằm ở cuối tài liệu (trước Phụ lục A); ánh xạ hàm test sang test case ở Phụ lục C; test case không có hàm test (đã gỡ, manual, ngoài `tests/`) ở Phụ lục D. Mỗi test case mới có các phần tử của ISO/IEC/IEEE 29119-3: ID duy nhất, mục tiêu (tiêu đề), truy vết (REQ-ID, test condition), mức ưu tiên, loại, precondition, bước kèm kết quả mong đợi (đầu vào nằm trong bước), tiêu chí Pass/Fail, và cách tự động hóa (hàm test).

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-10-09 | hieudt | Khởi tạo: 429 test case cho 106 REQ-ID |
| 0.2 | 2026-10-12 | hieudt | Sửa theo review độc lập (099, Phụ lục B và mục 3) và theo code đã hiện thực: đồng bộ tên hàm thật (`process_due()` không nhận `now`, `_process_task(task, now)`, `evaluate`, `action_reevaluate`, `action_reevaluate_batch`, `action_mark_resolved`, `action_recalculate`, điểm mở rộng của `sla.definition`, `sla.mixin`), định nghĩa `process_due`/`_process_task` một lần ở "Ký hiệu chung"; viết lại TC-ERR-005, 026, 027, 029, TC-ESC-053 đến 055, TC-PRF-006 đến 008, TC-CAN-016; loại phụ thuộc giữa 9 TC (F-M5); sửa TC-INF-010 (`sla.escalation.retry`); thay 17 kết quả "Thành công" bằng kết quả đo được; chuyển TC-CHG-014 sang TC-SEC-024; thêm TC-ESC-059 (REL-002 AC5), TC-CHG-028 (INT-005 AC4), TC-ATT-027 (patch hook tự phục hồi), TC-BRE-023 (CHECK chéo), TC-CAN-032 (flush khi reset), TC-INF-035 (gỡ module có model gắn SLA), TC-PRF-010 (patch động); cập nhật Phụ lục A với cột Trạng thái (ĐÃ CHỐT hoặc CÒN MỞ). Cập nhật tiếp cùng ngày theo các quyết định đã chốt và code đã sửa (TASKS T13): đổi mã mục Phụ lục A từ `A-xx` sang `TA-xx` để không trùng `A-xx` của SRS/TAD; TC-INS-001 chấp nhận `web` (D1); TA-03 (reset ghi `cancel`/`complete` rồi `reset`), TA-20 (AC2 FUNC-014 viết lại), TA-22 (`business_percent_used` không lưu, gồm đoạn đang chạy; thêm ví dụ chạy trực tiếp ở TC-BRE-015), TA-24/30/33/34 đã sửa code, TA-26 (AC5 FUNC-012 đang viết lại), TA-32 (sửa số TC Settings), O-01 đóng ở 5%; TA-08: thêm cờ `cancel_retry_on_stop` (TC-ESC-016, 030..032 ghi cờ mặc định True) và thêm TC-ESC-060 (cờ False); TC-PRF-010 đổi tham chiếu sang REQ-FUNC-004/005; TC-INF-013..016 dùng `event_dt`; thêm mục "Ghi chú đối chiếu" ở Phụ lục A. Tổng 437 test case. |
| 0.3 | 2026-11-12 | hieudt | Đợt 1.1.0: thêm 151 test case (TG-21 đến TG-32 và bổ sung TG-03, 08, 12, 13, 14, 16, 18) cho đủ 435 hàm test; đánh dấu 27 test case thử lại là Đã gỡ (D12); đổi tên field theo code (`duration`, `target_duration`, `schedule_source`, `schedule_id`, `start_time`, `end_time`, `planned_end_time`, `business_duration`, `business_percent_used`, `pause_time`) và tên nút (Apply Current Settings, Re-check Conditions); sửa các ca về `[]` (chưa cấu hình, không còn khớp mọi record: TC-ATT-001, 002, 008 đến 010, 016, TC-CAN-020, 029, 030, TC-PAU-007, TC-ESC-024); thêm Phụ lục C (ánh xạ 435 hàm test) và Phụ lục D (test case không có hàm test) |

## Cách đọc tài liệu

- Mỗi coverage item của `050` sinh một test case. Ca độc lập: mỗi ca tự dựng fixture trong Preconditions (fixture `FX-*` định nghĩa ở `040_Test-Plan.md` mục 11.2 và mục "Fixture bổ sung" dưới đây).
- Cột Automation: `Automated` là ca viết bằng test của Odoo (`TransactionCase`); `Manual` là ca Inspection hoặc Demonstration.
- Kết quả thực thi (Actual Result, Status, Executed by, Date, Defect Ref) KHÔNG ghi ở tài liệu này mà ghi vào nhật ký chạy test và Test Summary Report; trạng thái từng REQ cập nhật vào ma trận SRS mục 4.
- Giá trị thời gian tính tay theo lịch FX-CAL-VN (T2–T6 08:00–17:00, 9 giờ mỗi ngày, không nghỉ trưa) và mốc FX-T0 = 2026-03-02 09:00 giờ Asia/Ho_Chi_Minh.
- Các chỗ ghi `[Giả định: ...]` là giả định thật của người viết test mà SRS hoặc TAD chưa nêu; dòng "Phụ thuộc: TA-xx" nghĩa là ca còn phụ thuộc một quyết định chưa chốt (Phụ lục A, cột Trạng thái = CÒN MỞ). Tên hàm và field đã khớp với code module (xem "Ký hiệu chung").
- ID test case không đánh lại số khi có thay đổi: TC-CHG-014 (cũ) đã chuyển thành TC-SEC-024 nên ID TC-CHG-014 để trống; các TC thêm mới lấy ID kế tiếp trong nhóm.
- Ca Smoke (đánh dấu trong cột Requirement Ref): TC-ATT-007, TC-ATT-015 (Smoke mở rộng), TC-ATT-017, TC-ATT-019 (4 ca). Test Plan 6.2 và EC-03 còn ghi "3 ca P1" nên lệch với tài liệu này; Test Plan cần sửa.

## Ký hiệu chung

> **Ký hiệu dùng trong TC-ATT, TC-PAU, TC-BRE.** `T0` = 2026-03-02 09:00 giờ VN (02:00 UTC, thứ Hai); `T0 + 3h` = 12:00 VN; giờ trần (ví dụ 13:01) là 2026-03-02 giờ VN, UTC = VN trừ 7 giờ. Lịch 24x7 nghĩa là nguồn lịch `none`. `evaluate(R, now, changed)` là `Engine.evaluate` (TAD 5.1); "Ghi `ref`=X; `evaluate(...)`" nghĩa là ghi giá trị lên record rồi gọi Engine với `now` đã chỉ định (Hook dùng `fields.Datetime.now()` nên test điều khiển `now` qua Engine hoặc patch `odoo.fields.Datetime.now`). **Xử lý nền tại now=X** = với mỗi task `in_progress` của ca, gọi `env['sla.processor']._process_task(task, X)` (xử lý đúng một task tại thời điểm X: ghi `breach` nếu `X >= planned_end_time`, rồi chạy từng mốc escalation/lượt thử lại đến hạn theo thứ tự `sequence`, rồi tính lại `next_due_at`; không khóa dòng, không báo tiến độ, không dùng `sleep`). **`process_due()`** = `env['sla.processor'].process_due()`, hàm của cron, KHÔNG nhận `now`: mỗi vòng lấy `fields.Datetime.now()`, chọn task `in_progress` có `next_due_at <= now` theo `next_due_at`, khóa đúng một task (`try_lock_for_update(limit=1)`), xử lý trong savepoint bằng `_process_task`, rồi gọi `ir.cron._commit_progress(1, remaining=R)` (R = số task còn đến hạn); dừng khi hết task đến hạn, khi đã xử lý `dwo_sla_core.batch_size` task (mặc định 50, chỉ là trần mỗi lần gọi) hoặc khi `_commit_progress` trả thời gian còn lại <= 0. Ca nào cần điều khiển thời gian qua `process_due()` thì patch `odoo.fields.Datetime.now` (`unittest.mock.patch`) và thay `ir.cron._commit_progress` bằng `fake_progress` (ghi lại tham số, trả thời gian còn lại giả lập). Các barrier đồng bộ trong ca nhiều cursor (ERR-005, ERR-027, ERR-029, ESC-059) chỉ kích hoạt trên đúng cursor đích (điều kiện `self.env.cr is C2`), vì `mock.patch` có hiệu lực toàn tiến trình. Hook (`create`/`write`/`_compute_field_value`) gọi `evaluate(records, now=None, changed)` nên dùng `fields.Datetime.now()`; ca đi qua hook phải patch `odoo.fields.Datetime.now`, ca thuần Engine truyền `now`. Đánh giá lại: `sla.task.action_reevaluate()`, `sla.event.action_reevaluate_batch()`, `sla.event.action_mark_resolved()`; tính lại: `sla.task.action_recalculate()` (cần `group_sla_manager`, ném `AccessError` nếu không). Hàm thời gian: `sla.time.resolve_calendar/plan/settle/next_due_at`. Thông báo `ValidationError`/`note` bằng tiếng Anh từ `constants/message.py`; TC chỉ kiểm từ khóa hoặc loại lỗi. Events luôn sắp theo `id` tăng dần. FX-DEF-STD, FX-DEF-VN, FX-ESC-STD, FX-DEMO, FX-CAL-VN theo Test Plan 11.2.

> Quy ước chung của phần A2: `T0` = FX-T0 = 2026-03-02 09:00 ICT (02:00 UTC, thứ Hai); giờ ghi theo ICT trừ khi nêu UTC. `P-01`, `P-02` là `res.partner`; `ref` là trạng thái theo FX-PARTNER-MARK. FX-DEF-STD viết tắt: start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none (24x7); cancel_mode=start_unmatched; resume_mode=condition; không retroactive; không escalation. Dòng "đổi:" ghi phần khác với FX-DEF-STD.
> G1: để điều khiển `now`, test ghi giá trị field không qua hook (ví dụ ghi bằng SQL/tắt hook của test rồi invalidate cache) rồi gọi `evaluate(records, now, changed)` với `changed` tường minh; không dùng sleep.

## Fixture bổ sung (ngoài Test Plan mục 11.2)

Các nhóm test dùng thêm fixture sau, khai báo đầy đủ trong Preconditions của từng ca. Riêng fixture `D-OTHER` chưa có trong Test Plan mục 11.2 (cần bổ sung ở lần sửa Test Plan kế tiếp).

| Fixture | Mô tả | Nhóm dùng |
|---------|-------|-----------|
| FX-CAL-VN-PM | Calendar `fully_fixed`, `Asia/Ho_Chi_Minh`, T2–T6 13:00–18:00 (để phân biệt với FX-CAL-VN khi đổi lịch) | TG-11, TG-15 |
| FX-CAL-PATH | Field Many2one `x_calendar_id` trên `res.partner` (loại manual) làm đích cho đường dẫn lịch `parent_id.x_calendar_id` | TG-11, TG-15 |
| FX-EXT | Module mẫu chỉ dùng trong test `dwo_sla_test_ext` override các điểm mở rộng | TG-19 |
| FX-CMP | Model kiểm thử `x.sla.cmp.ticket` có field compute có lưu (vì `res.partner` không có field phù hợp) | TG-12, TG-13 |
| FX-RETRO-DT | Field Datetime ghi được làm mốc retroactive (`res.partner` không có field phù hợp) | TG-07 |
| FX-USERS (bổ sung) | `U-CRON` (nhóm `group_sla_user`, không quyền quản trị người dùng), `U-BIZ-S` (`U-BIZ` cộng `group_sla_user`) | TG-08, TG-16 |
| D-OTHER | Định nghĩa thứ hai trên `res.partner` có start không bao giờ khớp | TG-11 |

## Số lượng test case

Bản 0.3 (19.0.1.1.0) mô tả đủ mọi hàm test trong `tests/`. Có hai con số cần phân biệt: **hàm test** (một `def test_` là một đơn vị thực thi) và **test case (ID)** (một mục `TC-xxx-nnn` trong tài liệu này). Một hàm test có thể phủ nhiều test case (ví dụ `test_inf_001_to_006_forbidden_models` phủ TC-INF-001 đến TC-INF-006), nên số test case lớn hơn số hàm test. Quan hệ đầy đủ ở Phụ lục C.

- **Hàm test:** 435, đếm bằng `grep -h "def test_" tests/test_*.py | wc -l` (kết quả 435; 3 hàm trong `test_tg18_performance.py` chỉ chạy khi đặt `SLA_PERF=1`, nên bộ test thường chạy 432 hàm và bỏ qua 3).
- **Test case (ID):** 588 = 437 ID của bản 0.2 + 151 ID mới của 0.3 (TG-21 đến TG-32 và bổ sung cho TG-03, 08, 12, 13, 14, 16, 18).
- **Phân loại 588 ID:** 521 có hàm test tự động; 19 Manual (Inspection hoặc Demonstration); 21 phủ bằng CI hoặc benchmark ngoài `tests/` (hoặc chưa tự động hóa, xem Phụ lục D); 27 đã gỡ ở D12 (cơ chế thử lại) và không còn hiệu lực.
- **Kiểm tra tự động:** Phụ lục C có đúng 435 dòng, mỗi hàm test xuất hiện đúng một lần; mọi ID trong cột "Test case" tồn tại ở tài liệu này; mọi test case còn hiệu lực truy vết được tới ít nhất một REQ-ID còn hiệu lực của `010` (không test case nào trỏ tới REQ-ID đã gỡ), và mọi REQ-ID `active` có ít nhất một test case còn hiệu lực.

| Nhóm | Test case (ID) | Có hàm test tự động | Manual | CI hoặc benchmark ngoài `tests/` | Đã gỡ (D12) |
|---|---|---|---|---|---|
| TG-01 — Gắn, kết thúc, điều kiện, kích hoạt đánh giá | 27 | 27 | 0 | 0 | 0 |
| TG-02 — Pause và resume | 11 | 11 | 0 | 0 | 0 |
| TG-03 — Vi phạm và quanh hạn | 26 | 26 | 0 | 0 | 0 |
| TG-04 — Cancel và reset | 32 | 32 | 0 | 0 | 0 |
| TG-05 — Ba cấu hình dễ sai | 8 | 8 | 0 | 0 | 0 |
| TG-06 — Giờ làm việc | 11 | 11 | 0 | 0 | 0 |
| TG-07 — Retroactive start | 12 | 12 | 0 | 0 | 0 |
| TG-08 — Escalation (email, server action), xử lý nền | 70 | 44 | 0 | 0 | 26 |
| TG-09 — Nhiều SLA song song | 8 | 8 | 0 | 0 | 0 |
| TG-10 — Tính generic | 5 | 5 | 0 | 0 | 0 |
| TG-11 — Đổi cấu hình khi đang chạy và archive | 27 | 27 | 0 | 0 | 0 |
| TG-12 — Lỗi engine và đồng thời | 30 | 27 | 2 | 1 | 0 |
| TG-13 — Field compute có lưu | 17 | 17 | 0 | 0 | 0 |
| TG-14 — Hạ tầng | 37 | 26 | 0 | 11 | 0 |
| TG-15 — Nguồn lịch | 15 | 15 | 0 | 0 | 0 |
| TG-16 — Phân quyền và đa công ty | 25 | 24 | 0 | 0 | 1 |
| TG-17 — Giao diện và báo cáo | 44 | 34 | 8 | 2 | 0 |
| TG-18 — Hiệu năng | 13 | 11 | 0 | 2 | 0 |
| TG-19 — Điểm mở rộng | 23 | 21 | 1 | 1 | 0 |
| TG-21 — Field phân loại | 10 | 10 | 0 | 0 | 0 |
| TG-22 — Retroactive pause | 9 | 9 | 0 | 0 | 0 |
| TG-23 — Timezone override | 5 | 5 | 0 | 0 | 0 |
| TG-24 — Hạn chót ban đầu và thời lượng đồng hồ | 4 | 4 | 0 | 0 | 0 |
| TG-25 — Bật/tắt, `[]` chưa cấu hình, timezone bắt buộc | 23 | 23 | 0 | 0 | 0 |
| TG-26 — Giao diện định nghĩa và task | 27 | 27 | 0 | 0 | 0 |
| TG-27 — Re-check Conditions | 6 | 6 | 0 | 0 | 0 |
| TG-28 — Apply Current Settings | 6 | 6 | 0 | 0 | 0 |
| TG-29 — Apply to Existing Records | 12 | 12 | 0 | 0 | 0 |
| TG-30 — Chip trạng thái | 20 | 20 | 0 | 0 | 0 |
| TG-31 — Tab Note, chuỗi | 4 | 4 | 0 | 0 | 0 |
| TG-32 — Duration (live) | 4 | 4 | 0 | 0 | 0 |
| INS — Inspection và kiểm tra CI | 17 | 5 | 8 | 4 | 0 |
| **Tổng** | **588** | **521** | **19** | **21** | **27** |

Nhóm TG-20 (đồng thời, hai cursor) không có ID riêng: các ca của nó là TC-ESC-009, TC-ESC-059, TC-ERR-005, 026, 027, 029 và TC-MUL-007, đã tính ở TG-08, TG-09 và TG-12.

## Traceability

Trạng thái ban đầu của mọi dòng là `Planned`. Cập nhật khi chạy test.

| REQ-ID | Test Condition | Coverage Item | Test Case | Status |
|---|---|---|---|---|
| REQ-INT-001 | TCOND-17-01 | CI-1 | TC-UIX-001 | Planned |
| REQ-INT-001 | TCOND-17-01 | CI-2 | TC-UIX-002 | Planned |
| REQ-INT-001 | TCOND-17-01 | CI-3 | TC-UIX-003 | Planned |
| REQ-INT-002 | TCOND-17-02 | CI-1 | TC-UIX-004 | Planned |
| REQ-INT-002 | TCOND-17-02 | CI-2 | TC-UIX-005 | Planned |
| REQ-INT-002 | TCOND-17-02 | CI-3 | TC-UIX-006 | Planned |
| REQ-INT-003 | TCOND-17-03 | CI-1 | TC-UIX-007 | Planned |
| REQ-INT-003 | TCOND-17-03 | CI-2 | TC-UIX-008 | Planned |
| REQ-INT-003 | TCOND-17-03 | CI-3 | TC-UIX-009 | Planned |
| REQ-INT-004 | TCOND-17-04 | CI-1 | TC-UIX-010 | Planned |
| REQ-INT-004 | TCOND-17-04 | CI-2 | TC-UIX-011 | Planned |
| REQ-INT-004 | TCOND-17-04 | CI-3 | TC-UIX-012 | Planned |
| REQ-INT-005 | TCOND-11-03 | CI-1 | TC-CHG-006 | Planned |
| REQ-INT-005 | TCOND-11-03 | CI-2 | TC-CHG-007 | Planned |
| REQ-INT-005 | TCOND-11-03 | CI-3 | TC-CHG-008 | Planned |
| REQ-INT-005 | TCOND-11-03 | CI-4 | TC-CHG-009 | Planned |
| REQ-INT-005 | TCOND-11-03 | CI-5 | TC-CHG-010 | Planned |
| REQ-INT-005 | TCOND-11-03 | CI-6 | TC-CHG-011 | Planned |
| REQ-INT-005 | TCOND-11-03 | CI-7 | TC-CHG-028 | Planned |
| REQ-INT-006 | TCOND-17-05 | CI-1 | TC-UIX-013 | Planned |
| REQ-INT-006 | TCOND-17-05 | CI-2 | TC-UIX-014 | Planned |
| REQ-INT-006 | TCOND-17-05 | CI-3 | TC-UIX-015 | Planned |
| REQ-INT-006 | TCOND-17-05 | CI-4 | TC-UIX-016 | Planned |
| REQ-INT-006 | TCOND-17-05 | CI-5 | TC-UIX-017 | Planned |
| REQ-INT-011 | TCOND-17-06 | CI-1 | TC-UIX-018 | Planned |
| REQ-INT-011 | TCOND-17-06 | CI-2 | TC-UIX-019 | Planned |
| REQ-INT-012 | TCOND-17-07 | CI-1 | TC-UIX-020 | Planned |
| REQ-INT-012 | TCOND-17-07 | CI-2 | TC-UIX-021 | Planned |
| REQ-INT-012 | TCOND-17-07 | CI-3 | TC-UIX-022 | Planned |
| REQ-INT-012 | TCOND-17-07 | CI-4 | TC-UIX-023 | Planned |
| REQ-INT-012 | TCOND-17-07 | CI-5 | TC-UIX-024 | Planned |
| REQ-INT-012 | TCOND-17-07 | CI-6 | TC-UIX-025 | Planned |
| REQ-INT-013 | TCOND-17-08 | CI-1 | TC-UIX-026 | Planned |
| REQ-INT-013 | TCOND-17-08 | CI-2 | TC-UIX-027 | Planned |
| REQ-INT-013 | TCOND-17-08 | CI-3 | TC-UIX-028 | Planned |
| REQ-INT-014 | TCOND-17-09 | CI-1 | TC-UIX-029 | Planned |
| REQ-INT-014 | TCOND-17-09 | CI-2 | TC-UIX-030 | Planned |
| REQ-INT-014 | TCOND-17-09 | CI-3 | TC-UIX-031 | Planned |
| REQ-INT-020 | TCOND-17-10 | CI-1 | TC-UIX-032 | Planned |
| REQ-INT-020 | TCOND-17-10 | CI-2 | TC-UIX-033 | Planned |
| REQ-INT-020 | TCOND-17-10 | CI-3 | TC-UIX-034 | Planned |
| REQ-INT-021 | TCOND-17-11 | CI-1 | TC-UIX-035 | Planned |
| REQ-INT-021 | TCOND-17-11 | CI-2 | TC-UIX-036 | Planned |
| REQ-INT-021 | TCOND-17-11 | CI-3 | TC-UIX-037 | Planned |
| REQ-INT-021 | TCOND-17-11 | CI-4 | TC-UIX-038 | Planned |
| REQ-INT-022 | TCOND-12-07 | CI-1 | TC-ERR-022 | Planned |
| REQ-INT-022 | TCOND-12-07 | CI-2 | TC-ERR-023 | Planned |
| REQ-INT-022 | TCOND-12-07 | CI-3 | TC-ERR-024 | Planned |
| REQ-INT-022 | TCOND-12-07 | CI-4 | TC-ERR-025 | Planned |
| REQ-INT-023 | TCOND-03-06 | CI-1 | TC-BRE-015 | Planned |
| REQ-INT-023 | TCOND-03-06 | CI-2 | TC-BRE-016 | Planned |
| REQ-INT-023 | TCOND-03-06 | CI-3 | TC-BRE-017 | Planned |
| REQ-INT-023 | TCOND-03-06 | CI-4 | TC-BRE-018 | Planned |
| REQ-INT-023 | TCOND-03-06 | CI-5 | TC-BRE-019 | Planned |
| REQ-INT-023 | TCOND-03-06 | CI-6 | TC-BRE-020 | Planned |
| REQ-INT-023 | TCOND-03-06 | CI-7 | TC-BRE-021 | Planned |
| REQ-INT-007 | TCOND-19-01 | CI-1 | TC-EXT-001 | Planned |
| REQ-INT-007 | TCOND-19-01 | CI-2 | TC-EXT-002 | Planned |
| REQ-INT-007 | TCOND-19-01 | CI-3 | TC-EXT-003 | Planned |
| REQ-INT-007 | TCOND-19-01 | CI-4 | TC-EXT-004 | Planned |
| REQ-INT-007 | TCOND-19-01 | CI-5 | TC-EXT-005 | Planned |
| REQ-INT-008 | TCOND-08-16 | CI-1 | TC-ESC-048 | Planned |
| REQ-INT-008 | TCOND-08-16 | CI-2 | TC-ESC-049 | Planned |
| REQ-INT-009 | TCOND-15-02 | CI-1 | TC-CAL-003 | Planned |
| REQ-INT-009 | TCOND-15-02 | CI-2 | TC-CAL-004 | Planned |
| REQ-INT-010 | TCOND-14-06 | CI-1 | TC-INF-017 | Planned |
| REQ-INT-010 | TCOND-14-06 | CI-2 | TC-INF-018 | Planned |
| REQ-INT-010 | TCOND-14-06 | CI-3 | TC-INF-019 | Planned |
| REQ-INT-010 | TCOND-14-06 | CI-4 | TC-INF-020 | Planned |
| REQ-INT-010 | TCOND-14-06 | CI-5 | TC-INF-021 | Planned |
| REQ-INT-010 | TCOND-14-06 | CI-6 | TC-INF-022 | Planned |
| REQ-INT-015 | TCOND-19-02 | CI-1 | TC-EXT-006 | Planned |
| REQ-INT-015 | TCOND-19-02 | CI-2 | TC-EXT-007 | Planned |
| REQ-INT-015 | TCOND-19-02 | CI-3 | TC-EXT-008 | Planned |
| REQ-INT-015 | TCOND-19-02 | CI-4 | TC-EXT-009 | Planned |
| REQ-INT-015 | TCOND-19-02 | CI-5 | TC-EXT-010 | Planned |
| REQ-INT-016 | TCOND-19-03 | CI-1 | TC-EXT-011 | Planned |
| REQ-INT-016 | TCOND-19-03 | CI-2 | TC-EXT-012 | Planned |
| REQ-INT-016 | TCOND-19-03 | CI-3 | TC-EXT-013 | Planned |
| REQ-INT-017 | TCOND-19-04 | CI-1 | TC-EXT-014 | Planned |
| REQ-INT-017 | TCOND-19-04 | CI-2 | TC-EXT-015 | Planned |
| REQ-INT-017 | TCOND-19-04 | CI-3 | TC-EXT-016 | Planned |
| REQ-INT-018 | TCOND-19-05 | CI-1 | TC-EXT-017 | Planned |
| REQ-INT-018 | TCOND-19-05 | CI-2 | TC-EXT-018 | Planned |
| REQ-INT-018 | TCOND-19-05 | CI-3 | TC-EXT-019 | Planned |
| REQ-INT-018 | TCOND-19-05 | CI-4 | TC-EXT-020 | Planned |
| REQ-INT-019 | TCOND-08-17 | CI-1 | TC-ESC-050 | Planned |
| REQ-INT-019 | TCOND-08-17 | CI-2 | TC-ESC-051 | Planned |
| REQ-INT-019 | TCOND-08-17 | CI-3 | TC-ESC-052 | Removed (D12) |
| REQ-FUNC-001 | TCOND-10-01 | CI-1 | TC-GEN-001 | Planned |
| REQ-FUNC-001 | TCOND-10-02 | CI-1 | TC-GEN-002 | Planned |
| REQ-FUNC-001 | TCOND-10-03 | CI-1 | TC-GEN-003 | Planned |
| REQ-FUNC-001 | TCOND-10-03 | CI-2 | TC-GEN-004 | Planned |
| REQ-FUNC-001 | TCOND-10-03 | CI-3 | TC-GEN-005 | Planned |
| REQ-FUNC-002 | TCOND-14-01 | CI-1 | TC-INF-001 | Planned |
| REQ-FUNC-002 | TCOND-14-01 | CI-2 | TC-INF-002 | Planned |
| REQ-FUNC-002 | TCOND-14-01 | CI-3 | TC-INF-003 | Planned |
| REQ-FUNC-002 | TCOND-14-01 | CI-4 | TC-INF-004 | Planned |
| REQ-FUNC-002 | TCOND-14-01 | CI-5 | TC-INF-005 | Planned |
| REQ-FUNC-002 | TCOND-14-01 | CI-6 | TC-INF-006 | Planned |
| REQ-FUNC-002 | TCOND-14-02 | CI-1 | TC-INF-007 | Planned |
| REQ-FUNC-002 | TCOND-14-02 | CI-2 | TC-INF-008 | Planned |
| REQ-FUNC-002 | TCOND-14-03 | CI-1 | TC-INF-009 | Planned |
| REQ-FUNC-003 | TCOND-01-01 | CI-1 | TC-ATT-001 | Planned |
| REQ-FUNC-003 | TCOND-01-01 | CI-2 | TC-ATT-002 | Planned |
| REQ-FUNC-003 | TCOND-01-02 | CI-1 | TC-ATT-003 | Planned |
| REQ-FUNC-003 | TCOND-01-02 | CI-2 | TC-ATT-004 | Planned |
| REQ-FUNC-003 | TCOND-01-02 | CI-3 | TC-ATT-005 | Planned |
| REQ-FUNC-003 | TCOND-01-02 | CI-4 | TC-ATT-006 | Planned |
| REQ-FUNC-038 | TCOND-08-14 | CI-1 | TC-ESC-044 | Planned |
| REQ-FUNC-038 | TCOND-08-14 | CI-2 | TC-ESC-045 | Planned |
| REQ-FUNC-039 | TCOND-15-01 | CI-1 | TC-CAL-001 | Planned |
| REQ-FUNC-039 | TCOND-15-01 | CI-2 | TC-CAL-002 | Planned |
| REQ-FUNC-041 | TCOND-07-02 | CI-1 | TC-RET-008 | Planned |
| REQ-FUNC-041 | TCOND-07-02 | CI-2 | TC-RET-009 | Planned |
| REQ-FUNC-041 | TCOND-07-02 | CI-3 | TC-RET-010 | Planned |
| REQ-FUNC-041 | TCOND-07-02 | CI-4 | TC-RET-011 | Planned |
| REQ-FUNC-041 | TCOND-07-02 | CI-5 | TC-RET-012 | Planned |
| REQ-FUNC-004 | TCOND-01-06 | CI-1 | TC-ATT-019 | Planned |
| REQ-FUNC-004 | TCOND-01-06 | CI-2 | TC-ATT-020 | Planned |
| REQ-FUNC-004 | TCOND-01-06 | CI-3 | TC-ATT-021 | Planned |
| REQ-FUNC-004 | TCOND-01-06 | CI-4 | TC-ATT-022 | Planned |
| REQ-FUNC-004 | TCOND-01-06 | CI-5 | TC-ATT-027 | Planned |
| REQ-FUNC-005 | TCOND-13-01 | CI-1 | TC-CMP-001 | Planned |
| REQ-FUNC-005 | TCOND-13-01 | CI-2 | TC-CMP-002 | Planned |
| REQ-FUNC-005 | TCOND-13-01 | CI-3 | TC-CMP-003 | Planned |
| REQ-FUNC-005 | TCOND-13-01 | CI-4 | TC-CMP-004 | Planned |
| REQ-FUNC-005 | TCOND-13-01 | CI-5 | TC-CMP-005 | Planned |
| REQ-FUNC-042 | TCOND-13-02 | CI-1 | TC-CMP-006 | Planned |
| REQ-FUNC-042 | TCOND-13-02 | CI-2 | TC-CMP-007 | Planned |
| REQ-FUNC-042 | TCOND-13-02 | CI-3 | TC-CMP-008 | Planned |
| REQ-FUNC-042 | TCOND-13-02 | CI-4 | TC-CMP-009 | Planned |
| REQ-FUNC-006 | TCOND-01-03 | CI-1 | TC-ATT-007 | Planned |
| REQ-FUNC-006 | TCOND-01-03 | CI-2 | TC-ATT-008 | Planned |
| REQ-FUNC-006 | TCOND-01-03 | CI-3 | TC-ATT-009 | Planned |
| REQ-FUNC-006 | TCOND-01-03 | CI-4 | TC-ATT-010 | Planned |
| REQ-FUNC-006 | TCOND-01-03 | CI-5 | TC-ATT-011 | Planned |
| REQ-FUNC-007 | TCOND-01-04 | CI-1 | TC-ATT-012 | Planned |
| REQ-FUNC-007 | TCOND-01-04 | CI-2 | TC-ATT-013 | Planned |
| REQ-FUNC-007 | TCOND-01-04 | CI-3 | TC-ATT-014 | Planned |
| REQ-FUNC-007 | TCOND-01-04 | CI-4 | TC-ATT-015 | Planned |
| REQ-FUNC-007 | TCOND-01-04 | CI-5 | TC-ATT-016 | Planned |
| REQ-FUNC-008 | TCOND-04-01 | CI-1 | TC-CAN-001 | Planned |
| REQ-FUNC-008 | TCOND-04-01 | CI-2 | TC-CAN-002 | Planned |
| REQ-FUNC-008 | TCOND-04-01 | CI-3 | TC-CAN-003 | Planned |
| REQ-FUNC-008 | TCOND-04-01 | CI-4 | TC-CAN-004 | Planned |
| REQ-FUNC-008 | TCOND-04-01 | CI-5 | TC-CAN-005 | Planned |
| REQ-FUNC-008 | TCOND-04-01 | CI-6 | TC-CAN-006 | Planned |
| REQ-FUNC-008 | TCOND-05-03 | CI-1 | TC-MIS-006 | Planned |
| REQ-FUNC-009 | TCOND-01-05 | CI-1 | TC-ATT-017 | Planned |
| REQ-FUNC-009 | TCOND-01-05 | CI-2 | TC-ATT-018 | Planned |
| REQ-FUNC-009 | TCOND-03-04 | CI-1 | TC-BRE-009 | Planned |
| REQ-FUNC-009 | TCOND-03-04 | CI-2 | TC-BRE-010 | Planned |
| REQ-FUNC-009 | TCOND-03-04 | CI-3 | TC-BRE-011 | Planned |
| REQ-FUNC-009 | TCOND-03-04 | CI-4 | TC-BRE-012 | Planned |
| REQ-FUNC-010 | TCOND-04-02 | CI-1 | TC-CAN-007 | Planned |
| REQ-FUNC-010 | TCOND-04-02 | CI-2 | TC-CAN-008 | Planned |
| REQ-FUNC-010 | TCOND-04-02 | CI-3 | TC-CAN-009 | Planned |
| REQ-FUNC-010 | TCOND-04-02 | CI-4 | TC-CAN-010 | Planned |
| REQ-FUNC-010 | TCOND-04-02 | CI-5 | TC-CAN-011 | Planned |
| REQ-FUNC-011 | TCOND-02-01 | CI-1 | TC-PAU-001 | Planned |
| REQ-FUNC-011 | TCOND-02-01 | CI-2 | TC-PAU-002 | Planned |
| REQ-FUNC-011 | TCOND-02-01 | CI-3 | TC-PAU-003 | Planned |
| REQ-FUNC-037 | TCOND-02-02 | CI-1 | TC-PAU-004 | Planned |
| REQ-FUNC-037 | TCOND-02-02 | CI-2 | TC-PAU-005 | Planned |
| REQ-FUNC-048 | TCOND-02-03 | CI-1 | TC-PAU-006 | Planned |
| REQ-FUNC-048 | TCOND-02-03 | CI-2 | TC-PAU-007 | Planned |
| REQ-FUNC-048 | TCOND-02-03 | CI-3 | TC-PAU-008 | Planned |
| REQ-FUNC-012 | TCOND-04-03 | CI-1 | TC-CAN-012 | Planned |
| REQ-FUNC-012 | TCOND-04-03 | CI-2 | TC-CAN-013 | Planned |
| REQ-FUNC-012 | TCOND-04-03 | CI-3 | TC-CAN-014 | Planned |
| REQ-FUNC-012 | TCOND-04-03 | CI-4 | TC-CAN-015 | Planned |
| REQ-FUNC-012 | TCOND-04-03 | CI-5 | TC-CAN-016 | Planned |
| REQ-FUNC-012 | TCOND-04-03 | CI-6 | TC-CAN-017 | Planned |
| REQ-FUNC-012 | TCOND-04-03 | CI-7 | TC-CAN-018 | Planned |
| REQ-FUNC-012 | TCOND-04-03 | CI-8 | TC-CAN-019 | Planned |
| REQ-FUNC-012 | TCOND-04-03 | CI-9 | TC-CAN-032 | Planned |
| REQ-FUNC-013 | TCOND-04-04 | CI-1 | TC-CAN-020 | Planned |
| REQ-FUNC-013 | TCOND-04-04 | CI-2 | TC-CAN-021 | Planned |
| REQ-FUNC-013 | TCOND-04-04 | CI-3 | TC-CAN-022 | Planned |
| REQ-FUNC-013 | TCOND-04-04 | CI-4 | TC-CAN-023 | Planned |
| REQ-FUNC-013 | TCOND-04-04 | CI-5 | TC-CAN-024 | Planned |
| REQ-FUNC-050 | TCOND-04-05 | CI-1 | TC-CAN-025 | Planned |
| REQ-FUNC-050 | TCOND-04-05 | CI-2 | TC-CAN-026 | Planned |
| REQ-FUNC-050 | TCOND-04-05 | CI-3 | TC-CAN-027 | Planned |
| REQ-FUNC-050 | TCOND-04-05 | CI-4 | TC-CAN-028 | Planned |
| REQ-FUNC-051 | TCOND-04-06 | CI-1 | TC-CAN-029 | Planned |
| REQ-FUNC-051 | TCOND-04-06 | CI-2 | TC-CAN-030 | Planned |
| REQ-FUNC-051 | TCOND-04-06 | CI-3 | TC-CAN-031 | Planned |
| REQ-FUNC-014 | TCOND-09-01 | CI-1 | TC-MUL-001 | Planned |
| REQ-FUNC-014 | TCOND-09-01 | CI-2 | TC-MUL-002 | Planned |
| REQ-FUNC-014 | TCOND-09-01 | CI-3 | TC-MUL-003 | Planned |
| REQ-FUNC-014 | TCOND-09-01 | CI-4 | TC-MUL-004 | Planned |
| REQ-FUNC-014 | TCOND-09-01 | CI-5 | TC-MUL-005 | Planned |
| REQ-FUNC-014 | TCOND-09-02 | CI-1 | TC-MUL-006 | Planned |
| REQ-FUNC-014 | TCOND-09-02 | CI-2 | TC-MUL-007 | Planned |
| REQ-FUNC-014 | TCOND-09-02 | CI-3 | TC-MUL-008 | Planned |
| REQ-FUNC-015 | TCOND-01-07 | CI-1 | TC-ATT-023 | Planned |
| REQ-FUNC-015 | TCOND-01-07 | CI-2 | TC-ATT-024 | Planned |
| REQ-FUNC-016 | TCOND-05-01 | CI-1 | TC-MIS-001 | Planned |
| REQ-FUNC-016 | TCOND-05-01 | CI-2 | TC-MIS-002 | Planned |
| REQ-FUNC-016 | TCOND-05-01 | CI-3 | TC-MIS-003 | Planned |
| REQ-FUNC-016 | TCOND-05-02 | CI-1 | TC-MIS-004 | Planned |
| REQ-FUNC-016 | TCOND-05-02 | CI-2 | TC-MIS-005 | Planned |
| REQ-FUNC-016 | TCOND-05-03 | CI-1 | TC-MIS-006 | Planned |
| REQ-FUNC-016 | TCOND-05-03 | CI-2 | TC-MIS-007 | Planned |
| REQ-FUNC-016 | TCOND-05-03 | CI-3 | TC-MIS-008 | Planned |
| REQ-FUNC-017 | TCOND-07-01 | CI-1 | TC-RET-001 | Planned |
| REQ-FUNC-017 | TCOND-07-01 | CI-2 | TC-RET-002 | Planned |
| REQ-FUNC-017 | TCOND-07-01 | CI-3 | TC-RET-003 | Planned |
| REQ-FUNC-017 | TCOND-07-01 | CI-4 | TC-RET-004 | Planned |
| REQ-FUNC-017 | TCOND-07-01 | CI-5 | TC-RET-005 | Planned |
| REQ-FUNC-017 | TCOND-07-01 | CI-6 | TC-RET-006 | Planned |
| REQ-FUNC-017 | TCOND-07-01 | CI-7 | TC-RET-007 | Planned |
| REQ-FUNC-018 | TCOND-06-01 | CI-1 | TC-TIM-001 | Planned |
| REQ-FUNC-018 | TCOND-06-01 | CI-2 | TC-TIM-002 | Planned |
| REQ-FUNC-018 | TCOND-06-02 | CI-1 | TC-TIM-003 | Planned |
| REQ-FUNC-018 | TCOND-06-02 | CI-2 | TC-TIM-004 | Planned |
| REQ-FUNC-018 | TCOND-06-03 | CI-1 | TC-TIM-005 | Planned |
| REQ-FUNC-018 | TCOND-06-04 | CI-1 | TC-TIM-006 | Planned |
| REQ-FUNC-018 | TCOND-06-05 | CI-1 | TC-TIM-007 | Planned |
| REQ-FUNC-043 | TCOND-06-06 | CI-1 | TC-TIM-008 | Planned |
| REQ-FUNC-043 | TCOND-06-06 | CI-2 | TC-TIM-009 | Planned |
| REQ-FUNC-043 | TCOND-06-06 | CI-3 | TC-TIM-010 | Planned |
| REQ-FUNC-043 | TCOND-06-06 | CI-4 | TC-TIM-011 | Planned |
| REQ-FUNC-044 | TCOND-02-04 | CI-1 | TC-PAU-009 | Planned |
| REQ-FUNC-044 | TCOND-02-04 | CI-2 | TC-PAU-010 | Planned |
| REQ-FUNC-019 | TCOND-15-03 | CI-1 | TC-CAL-005 | Planned |
| REQ-FUNC-019 | TCOND-15-03 | CI-2 | TC-CAL-006 | Planned |
| REQ-FUNC-019 | TCOND-15-03 | CI-3 | TC-CAL-007 | Planned |
| REQ-FUNC-019 | TCOND-15-03 | CI-4 | TC-CAL-008 | Planned |
| REQ-FUNC-019 | TCOND-15-03 | CI-5 | TC-CAL-009 | Planned |
| REQ-FUNC-020 | TCOND-15-04 | CI-1 | TC-CAL-010 | Planned |
| REQ-FUNC-020 | TCOND-15-04 | CI-2 | TC-CAL-011 | Planned |
| REQ-FUNC-020 | TCOND-15-04 | CI-3 | TC-CAL-012 | Planned |
| REQ-FUNC-020 | TCOND-15-04 | CI-4 | TC-CAL-013 | Planned |
| REQ-FUNC-020 | TCOND-15-04 | CI-5 | TC-CAL-014 | Planned |
| REQ-FUNC-020 | TCOND-15-04 | CI-6 | TC-CAL-015 | Planned |
| REQ-FUNC-021 | TCOND-11-01 | CI-1 | TC-CHG-001 | Planned |
| REQ-FUNC-021 | TCOND-11-01 | CI-2 | TC-CHG-002 | Planned |
| REQ-FUNC-021 | TCOND-11-01 | CI-3 | TC-CHG-003 | Planned |
| REQ-FUNC-052 | TCOND-11-02 | CI-1 | TC-CHG-004 | Planned |
| REQ-FUNC-052 | TCOND-11-02 | CI-2 | TC-CHG-005 | Planned |
| REQ-FUNC-053 | TCOND-08-15 | CI-1 | TC-ESC-046 | Planned |
| REQ-FUNC-053 | TCOND-08-15 | CI-2 | TC-ESC-047 | Planned |
| REQ-FUNC-053 | TCOND-11-04 | CI-1 | TC-CHG-012 | Planned |
| REQ-FUNC-053 | TCOND-11-04 | CI-2 | TC-CHG-013 | Planned |
| REQ-FUNC-022 | TCOND-03-01 | CI-1 | TC-BRE-001 | Planned |
| REQ-FUNC-022 | TCOND-03-01 | CI-2 | TC-BRE-002 | Planned |
| REQ-FUNC-022 | TCOND-03-01 | CI-3 | TC-BRE-003 | Planned |
| REQ-FUNC-022 | TCOND-03-01 | CI-4 | TC-BRE-004 | Planned |
| REQ-FUNC-022 | TCOND-03-02 | CI-1 | TC-BRE-005 | Planned |
| REQ-FUNC-022 | TCOND-03-02 | CI-2 | TC-BRE-006 | Planned |
| REQ-FUNC-022 | TCOND-03-03 | CI-1 | TC-BRE-007 | Planned |
| REQ-FUNC-022 | TCOND-03-03 | CI-2 | TC-BRE-008 | Planned |
| REQ-FUNC-046 | TCOND-03-05 | CI-1 | TC-BRE-013 | Planned |
| REQ-FUNC-046 | TCOND-03-05 | CI-2 | TC-BRE-014 | Planned |
| REQ-FUNC-046 | TCOND-03-05 | CI-3 | TC-BRE-023 | Planned |
| REQ-FUNC-023 | TCOND-08-01 | CI-1 | TC-ESC-001 | Planned |
| REQ-FUNC-023 | TCOND-08-01 | CI-2 | TC-ESC-002 | Planned |
| REQ-FUNC-023 | TCOND-08-01 | CI-3 | TC-ESC-003 | Planned |
| REQ-FUNC-023 | TCOND-08-01 | CI-4 | TC-ESC-004 | Planned |
| REQ-FUNC-023 | TCOND-08-01 | CI-5 | TC-ESC-005 | Planned |
| REQ-FUNC-023 | TCOND-08-02 | CI-1 | TC-ESC-006 | Planned |
| REQ-FUNC-023 | TCOND-08-02 | CI-2 | TC-ESC-007 | Planned |
| REQ-FUNC-024 | TCOND-08-03 | CI-1 | TC-ESC-008 | Planned |
| REQ-FUNC-024 | TCOND-08-03 | CI-2 | TC-ESC-009 | Planned |
| REQ-FUNC-025 | TCOND-08-04 | CI-1 | TC-ESC-010 | Planned |
| REQ-FUNC-054 | TCOND-08-05 | CI-1 | TC-ESC-011 | Planned |
| REQ-FUNC-054 | TCOND-08-05 | CI-2 | TC-ESC-012 | Planned |
| REQ-FUNC-054 | TCOND-08-05 | CI-3 | TC-ESC-013 | Planned |
| REQ-FUNC-054 | TCOND-08-05 | CI-4 | TC-ESC-014 | Planned |
| REQ-FUNC-055 | TCOND-08-06 | CI-1 | TC-ESC-015 | Planned |
| REQ-FUNC-055 | TCOND-08-06 | CI-2 | TC-ESC-016 | Removed (D12) |
| REQ-FUNC-055 | TCOND-08-06 | CI-3 | TC-ESC-017 | Planned |
| REQ-FUNC-026 | TCOND-08-07 | CI-1 | TC-ESC-018 | Planned |
| REQ-FUNC-026 | TCOND-08-07 | CI-2 | TC-ESC-019 | Planned |
| REQ-FUNC-027 | TCOND-08-08 | CI-1 | TC-ESC-020 | Removed (D12) |
| REQ-FUNC-027 | TCOND-08-08 | CI-2 | TC-ESC-021 | Removed (D12) |
| REQ-FUNC-027 | TCOND-08-08 | CI-3 | TC-ESC-022 | Removed (D12) |
| REQ-FUNC-027 | TCOND-08-08 | CI-4 | TC-ESC-023 | Removed (D12) |
| REQ-FUNC-026 | TCOND-08-07 | CI-3 | TC-ESC-024 | Planned |
| REQ-FUNC-056 | TCOND-08-09 | CI-1 | TC-ESC-025 | Removed (D12) |
| REQ-FUNC-056 | TCOND-08-09 | CI-2 | TC-ESC-026 | Removed (D12) |
| REQ-FUNC-057 | TCOND-08-10 | CI-1 | TC-ESC-027 | Removed (D12) |
| REQ-FUNC-057 | TCOND-08-10 | CI-2 | TC-ESC-028 | Removed (D12) |
| REQ-FUNC-057 | TCOND-08-10 | CI-3 | TC-ESC-029 | Removed (D12) |
| REQ-FUNC-058 | TCOND-08-11 | CI-1 | TC-ESC-030 | Removed (D12) |
| REQ-FUNC-058 | TCOND-08-11 | CI-2 | TC-ESC-031 | Removed (D12) |
| REQ-FUNC-058 | TCOND-08-11 | CI-3 | TC-ESC-032 | Removed (D12) |
| REQ-FUNC-058 | TCOND-08-11 | CI-4 | TC-ESC-060 | Removed (D12) |
| REQ-FUNC-059 | TCOND-08-12 | CI-1 | TC-ESC-033 | Removed (D12) |
| REQ-FUNC-059 | TCOND-08-12 | CI-2 | TC-ESC-034 | Removed (D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-1 | TC-ESC-035 | Removed (D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-2 | TC-ESC-036 | Removed (D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-3 | TC-ESC-037 | Removed (D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-4 | TC-ESC-038 | Removed (D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-5 | TC-ESC-039 | Removed (D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-6 | TC-ESC-040 | Removed (D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-7 | TC-ESC-041 | Removed (D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-8 | TC-ESC-042 | Removed (D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-9 | TC-ESC-043 | Removed (D12) |
| REQ-FUNC-029 | TCOND-01-08 | CI-1 | TC-ATT-025 | Planned |
| REQ-FUNC-029 | TCOND-01-08 | CI-2 | TC-ATT-026 | Planned |
| REQ-FUNC-029 | TCOND-02-05 | CI-1 | TC-PAU-011 | Planned |
| REQ-FUNC-029 | TCOND-03-07 | CI-1 | TC-BRE-022 | Planned |
| REQ-FUNC-030 | TCOND-12-01 | CI-1 | TC-ERR-001 | Planned |
| REQ-FUNC-030 | TCOND-12-01 | CI-2 | TC-ERR-002 | Planned |
| REQ-FUNC-030 | TCOND-12-01 | CI-3 | TC-ERR-003 | Planned |
| REQ-FUNC-030 | TCOND-12-01 | CI-4 | TC-ERR-004 | Planned |
| REQ-FUNC-030 | TCOND-12-01 | CI-5 | TC-ERR-005 | Planned |
| REQ-FUNC-040 | TCOND-12-05 | CI-1 | TC-ERR-012 | Planned |
| REQ-FUNC-040 | TCOND-12-05 | CI-2 | TC-ERR-013 | Planned |
| REQ-FUNC-040 | TCOND-12-05 | CI-3 | TC-ERR-014 | Planned |
| REQ-FUNC-040 | TCOND-12-05 | CI-4 | TC-ERR-015 | Planned |
| REQ-FUNC-031 | TCOND-12-06 | CI-1 | TC-ERR-016 | Planned |
| REQ-FUNC-031 | TCOND-12-06 | CI-2 | TC-ERR-017 | Planned |
| REQ-FUNC-031 | TCOND-12-06 | CI-3 | TC-ERR-018 | Planned |
| REQ-FUNC-031 | TCOND-12-06 | CI-4 | TC-ERR-019 | Planned |
| REQ-FUNC-031 | TCOND-12-06 | CI-5 | TC-ERR-020 | Planned |
| REQ-FUNC-031 | TCOND-12-06 | CI-6 | TC-ERR-021 | Planned |
| REQ-FUNC-032 | TCOND-13-03 | CI-1 | TC-CMP-010 | Planned |
| REQ-FUNC-032 | TCOND-13-03 | CI-2 | TC-CMP-011 | Planned |
| REQ-FUNC-032 | TCOND-13-03 | CI-3 | TC-CMP-012 | Planned |
| REQ-FUNC-032 | TCOND-13-03 | CI-4 | TC-CMP-013 | Planned |
| REQ-FUNC-032 | TCOND-13-03 | CI-5 | TC-CMP-014 | Planned |
| REQ-FUNC-032 | TCOND-13-03 | CI-6 | TC-CMP-015 | Planned |
| REQ-FUNC-032 | TCOND-13-03 | CI-7 | TC-CMP-016 | Planned |
| REQ-FUNC-033 | TCOND-11-05 | CI-1 | TC-CHG-015 | Planned |
| REQ-FUNC-033 | TCOND-11-05 | CI-2 | TC-CHG-016 | Planned |
| REQ-FUNC-033 | TCOND-11-05 | CI-3 | TC-CHG-017 | Planned |
| REQ-FUNC-060 | TCOND-11-06 | CI-1 | TC-CHG-018 | Planned |
| REQ-FUNC-060 | TCOND-11-06 | CI-2 | TC-CHG-019 | Planned |
| REQ-FUNC-060 | TCOND-11-06 | CI-3 | TC-CHG-020 | Planned |
| REQ-FUNC-060 | TCOND-11-06 | CI-4 | TC-CHG-021 | Planned |
| REQ-FUNC-060 | TCOND-11-06 | CI-5 | TC-CHG-022 | Planned |
| REQ-FUNC-060 | TCOND-11-06 | CI-6 | TC-CHG-023 | Planned |
| REQ-FUNC-061 | TCOND-11-07 | CI-1 | TC-CHG-024 | Planned |
| REQ-FUNC-061 | TCOND-11-07 | CI-2 | TC-CHG-025 | Planned |
| REQ-FUNC-061 | TCOND-11-07 | CI-3 | TC-CHG-026 | Planned |
| REQ-FUNC-061 | TCOND-11-07 | CI-4 | TC-CHG-027 | Planned |
| REQ-FUNC-034 | TCOND-14-04 | CI-1 | TC-INF-010 | Planned |
| REQ-FUNC-034 | TCOND-14-04 | CI-2 | TC-INF-011 | Planned |
| REQ-FUNC-034 | TCOND-14-04 | CI-3 | TC-INF-012 | Planned |
| REQ-FUNC-035 | TCOND-14-05 | CI-1 | TC-INF-013 | Planned |
| REQ-FUNC-035 | TCOND-14-05 | CI-2 | TC-INF-014 | Planned |
| REQ-FUNC-035 | TCOND-14-05 | CI-3 | TC-INF-015 | Planned |
| REQ-FUNC-035 | TCOND-14-05 | CI-4 | TC-INF-016 | Planned |
| REQ-FUNC-036 | TCOND-17-12 | CI-1 | TC-UIX-039 | Planned |
| REQ-FUNC-036 | TCOND-17-12 | CI-2 | TC-UIX-040 | Planned |
| REQ-FUNC-036 | TCOND-17-12 | CI-3 | TC-UIX-041 | Planned |
| REQ-FUNC-062 | TCOND-17-13 | CI-1 | TC-UIX-042 | Planned |
| REQ-FUNC-062 | TCOND-17-13 | CI-2 | TC-UIX-043 | Planned |
| REQ-FUNC-062 | TCOND-17-13 | CI-3 | TC-UIX-044 | Planned |
| REQ-PERF-001 | TCOND-18-01 | CI-1 | TC-PRF-001 | Planned |
| REQ-PERF-001 | TCOND-18-01 | CI-2 | TC-PRF-002 | Planned |
| REQ-FUNC-004 | TCOND-18-01 | CI-3 | TC-PRF-010 | Planned |
| REQ-FUNC-005 | TCOND-18-01 | CI-3 | TC-PRF-010 | Planned |
| REQ-PERF-002 | TCOND-18-02 | CI-1 | TC-PRF-003 | Planned |
| REQ-PERF-002 | TCOND-18-02 | CI-2 | TC-PRF-004 | Planned |
| REQ-PERF-002 | TCOND-18-02 | CI-3 | TC-PRF-005 | Planned |
| REQ-PERF-003 | TCOND-18-03 | CI-1 | TC-PRF-006 | Planned |
| REQ-PERF-003 | TCOND-18-03 | CI-2 | TC-PRF-007 | Planned |
| REQ-PERF-003 | TCOND-18-03 | CI-3 | TC-PRF-008 | Planned |
| REQ-PERF-003 | TCOND-18-03 | CI-4 | TC-PRF-009 | Planned |
| REQ-SEC-001 | TCOND-16-01 | CI-1 | TC-SEC-001 | Planned |
| REQ-SEC-001 | TCOND-16-01 | CI-2 | TC-SEC-002 | Planned |
| REQ-SEC-001 | TCOND-16-01 | CI-3 | TC-SEC-003 | Planned |
| REQ-SEC-001 | TCOND-16-01 | CI-4 | TC-SEC-004 | Planned |
| REQ-SEC-001 | TCOND-16-01 | CI-5 | TC-SEC-005 | Planned |
| REQ-SEC-001 | TCOND-16-01 | CI-6 | TC-SEC-024 | Planned |
| REQ-SEC-002 | TCOND-16-02 | CI-1 | TC-SEC-006 | Planned |
| REQ-SEC-002 | TCOND-16-02 | CI-2 | TC-SEC-007 | Planned |
| REQ-SEC-003 | TCOND-16-03 | CI-1 | TC-SEC-008 | Planned |
| REQ-SEC-003 | TCOND-16-03 | CI-2 | TC-SEC-009 | Planned |
| REQ-SEC-003 | TCOND-16-03 | CI-3 | TC-SEC-010 | Planned |
| REQ-SEC-003 | TCOND-16-03 | CI-4 | TC-SEC-011 | Planned |
| REQ-SEC-003 | TCOND-16-03 | CI-5 | TC-SEC-012 | Planned |
| REQ-SEC-004 | TCOND-16-04 | CI-1 | TC-SEC-013 | Planned |
| REQ-SEC-004 | TCOND-16-04 | CI-2 | TC-SEC-014 | Removed (D12) |
| REQ-SEC-004 | TCOND-16-04 | CI-3 | TC-SEC-015 | Planned |
| REQ-SEC-005 | TCOND-16-05 | CI-1 | TC-SEC-016 | Planned |
| REQ-SEC-005 | TCOND-16-05 | CI-2 | TC-SEC-017 | Planned |
| REQ-SEC-006 | TCOND-16-06 | CI-1 | TC-SEC-018 | Planned |
| REQ-SEC-006 | TCOND-16-06 | CI-2 | TC-SEC-019 | Planned |
| REQ-SEC-006 | TCOND-16-06 | CI-3 | TC-SEC-020 | Planned |
| REQ-SEC-006 | TCOND-16-06 | CI-4 | TC-SEC-021 | Planned |
| REQ-SEC-006 | TCOND-16-06 | CI-5 | TC-SEC-022 | Planned |
| REQ-SEC-006 | TCOND-16-06 | CI-6 | TC-SEC-023 | Planned |
| REQ-REL-001 | TCOND-12-01 | CI-5 | TC-ERR-005 | Planned |
| REQ-REL-001 | TCOND-12-08 | CI-1 | TC-ERR-026 | Planned |
| REQ-REL-001 | TCOND-12-08 | CI-2 | TC-ERR-027 | Planned |
| REQ-REL-001 | TCOND-12-08 | CI-3 | TC-ERR-028 | Planned |
| REQ-REL-002 | TCOND-08-18 | CI-1 | TC-ESC-053 | Planned |
| REQ-REL-002 | TCOND-08-18 | CI-2 | TC-ESC-054 | Planned |
| REQ-REL-002 | TCOND-08-18 | CI-3 | TC-ESC-055 | Planned |
| REQ-REL-002 | TCOND-08-18 | CI-4 | TC-ESC-056 | Planned |
| REQ-REL-002 | TCOND-08-18 | CI-5 | TC-ESC-057 | Planned |
| REQ-REL-002 | TCOND-08-18 | CI-6 | TC-ESC-058 | Planned |
| REQ-REL-002 | TCOND-08-18 | CI-7 | TC-ESC-059 | Planned |
| REQ-REL-002 | TCOND-12-09 | CI-1 | TC-ERR-029 | Planned |
| REQ-OBS-001 | TCOND-12-02 | CI-1 | TC-ERR-006 | Planned |
| REQ-OBS-001 | TCOND-12-02 | CI-2 | TC-ERR-007 | Planned |
| REQ-OBS-002 | TCOND-12-03 | CI-1 | TC-ERR-008 | Planned |
| REQ-OBS-003 | TCOND-12-04 | CI-1 | TC-ERR-009 | Planned |
| REQ-OBS-003 | TCOND-12-04 | CI-2 | TC-ERR-010 | Planned |
| REQ-OBS-003 | TCOND-12-04 | CI-3 | TC-ERR-011 | Planned |
| REQ-INST-001 | TCOND-14-07 | CI-1 | TC-INF-023 | Planned |
| REQ-INST-001 | TCOND-14-07 | CI-2 | TC-INF-024 | Planned |
| REQ-INST-001 | TCOND-14-07 | CI-3 | TC-INF-025 | Planned |
| REQ-INST-001 | TCOND-14-07 | CI-4 | TC-INF-026 | Planned |
| REQ-INST-001 | TCOND-14-07 | CI-5 | TC-INF-035 | Planned |
| REQ-INST-002 | TCOND-INS-01 | CI-1 | TC-INS-001 | Planned |
| REQ-INST-002 | TCOND-INS-01 | CI-2 | TC-INS-002 | Planned |
| REQ-INST-003 | TCOND-14-08 | CI-1 | TC-INF-027 | Planned |
| REQ-INST-003 | TCOND-14-08 | CI-2 | TC-INF-028 | Planned |
| REQ-INST-003 | TCOND-14-08 | CI-3 | TC-INF-029 | Planned |
| REQ-INST-004 | TCOND-14-09 | CI-1 | TC-INF-030 | Planned |
| REQ-INST-004 | TCOND-14-09 | CI-2 | TC-INF-031 | Planned |
| REQ-INST-004 | TCOND-14-09 | CI-3 | TC-INF-032 | Planned |
| REQ-BUILD-001 | TCOND-INS-02 | CI-1 | TC-INS-003 | Planned |
| REQ-BUILD-001 | TCOND-INS-02 | CI-2 | TC-INS-004 | Planned |
| REQ-BUILD-001 | TCOND-INS-02 | CI-3 | TC-INS-005 | Planned |
| REQ-MAINT-001 | TCOND-INS-03 | CI-1 | TC-INS-006 | Planned |
| REQ-MAINT-001 | TCOND-INS-03 | CI-2 | TC-INS-007 | Planned |
| REQ-MAINT-001 | TCOND-INS-03 | CI-3 | TC-INS-008 | Planned |
| REQ-MAINT-001 | TCOND-INS-03 | CI-4 | TC-INS-009 | Planned |
| REQ-MAINT-001 | TCOND-INS-03 | CI-5 | TC-INS-010 | Planned |
| REQ-MAINT-002 | TCOND-INS-04 | CI-1 | TC-INS-011 | Planned |
| REQ-MAINT-002 | TCOND-INS-04 | CI-2 | TC-INS-012 | Planned |
| REQ-MAINT-002 | TCOND-INS-04 | CI-3 | TC-INS-013 | Planned |
| REQ-MAINT-002 | TCOND-INS-04 | CI-4 | TC-INS-014 | Planned |
| REQ-REUSE-001 | TCOND-19-06 | CI-1 | TC-EXT-021 | Planned |
| REQ-REUSE-001 | TCOND-19-06 | CI-2 | TC-EXT-022 | Planned |
| REQ-REUSE-001 | TCOND-19-06 | CI-3 | TC-EXT-023 | Planned |
| REQ-PORT-001 | TCOND-14-10 | CI-1 | TC-INF-033 | Planned |
| REQ-PORT-001 | TCOND-14-10 | CI-2 | TC-INF-034 | Planned |
| REQ-CM-001 | TCOND-INS-05 | CI-1 | TC-INS-015 | Planned |
| REQ-CM-001 | TCOND-INS-05 | CI-2 | TC-INS-016 | Planned |
| REQ-CM-001 | TCOND-INS-05 | CI-3 | TC-INS-017 | Planned |


---

### Traceability bổ sung 19.0.1.1.0

Các dòng dưới đây nối tiếp bảng trên cho 151 test case mới (ID mới của TG-21 đến TG-32 và bổ sung). Test condition và coverage item định nghĩa ở `050` mục 7.

| REQ-ID | Test Condition | Coverage Item | Test Case | Status |
|---|---|---|---|---|
| REQ-FUNC-001 | TCOND-14-36 | CI-1 | TC-INF-036 | Planned |
| REQ-FUNC-001 | TCOND-20-02 | CI-1 | TC-ENB-002 | Planned |
| REQ-FUNC-003 | TCOND-20-06 | CI-1 | TC-CND-001 | Planned |
| REQ-FUNC-003 | TCOND-20-06 | CI-2 | TC-CND-002 | Planned |
| REQ-FUNC-003 | TCOND-20-06 | CI-3 | TC-CND-003 | Planned |
| REQ-FUNC-003 | TCOND-20-06 | CI-4 | TC-CND-004 | Planned |
| REQ-FUNC-003 | TCOND-20-07 | CI-1 | TC-CND-005 | Planned |
| REQ-FUNC-003 | TCOND-24-03 | CI-1 | TC-APX-004 | Planned |
| REQ-FUNC-003 | TCOND-26-01 | CI-2 | TC-NOT-002 | Planned |
| REQ-FUNC-005 | TCOND-13-17 | CI-1 | TC-CMP-017 | Planned |
| REQ-FUNC-013 | TCOND-20-07 | CI-2 | TC-CND-006 | Planned |
| REQ-FUNC-021 | TCOND-20-12 | CI-1 | TC-TZR-009 | Planned |
| REQ-FUNC-022 | TCOND-03-24 | CI-1 | TC-BRE-024 | Planned |
| REQ-FUNC-022 | TCOND-08-70 | CI-1 | TC-PRC-001 | Planned |
| REQ-FUNC-022 | TCOND-08-70 | CI-2 | TC-PRC-002 | Planned |
| REQ-FUNC-026 | TCOND-08-73 | CI-1 | TC-EML-005 | Planned |
| REQ-FUNC-026 | TCOND-12-30 | CI-1 | TC-ERR-030 | Planned |
| REQ-FUNC-032 | TCOND-22-01 | CI-1 | TC-RCK-001 | Planned |
| REQ-FUNC-032 | TCOND-22-04 | CI-1 | TC-RCK-005 | Planned |
| REQ-FUNC-032 | TCOND-22-05 | CI-1 | TC-RCK-006 | Planned |
| REQ-FUNC-042 | TCOND-13-17 | CI-1 | TC-CMP-017 | Planned |
| REQ-FUNC-051 | TCOND-20-07 | CI-2 | TC-CND-006 | Planned |
| REQ-FUNC-053 | TCOND-24-07 | CI-1 | TC-APX-011 | Planned |
| REQ-FUNC-060 | TCOND-20-05 | CI-3 | TC-ENB-008 | Planned |
| REQ-FUNC-064 | TCOND-08-72 | CI-1 | TC-EML-001 | Planned |
| REQ-FUNC-064 | TCOND-08-74 | CI-1 | TC-EML-006 | Planned |
| REQ-FUNC-064 | TCOND-08-74 | CI-2 | TC-EML-007 | Planned |
| REQ-FUNC-065 | TCOND-08-72 | CI-2 | TC-EML-002 | Planned |
| REQ-FUNC-065 | TCOND-08-72 | CI-3 | TC-EML-003 | Planned |
| REQ-FUNC-065 | TCOND-08-72 | CI-4 | TC-EML-004 | Planned |
| REQ-FUNC-065 | TCOND-08-73 | CI-1 | TC-EML-005 | Planned |
| REQ-FUNC-066 | TCOND-20-01 | CI-1 | TC-ENB-001 | Planned |
| REQ-FUNC-066 | TCOND-20-03 | CI-1 | TC-ENB-003 | Planned |
| REQ-FUNC-066 | TCOND-20-03 | CI-2 | TC-ENB-004 | Planned |
| REQ-FUNC-066 | TCOND-20-04 | CI-1 | TC-ENB-005 | Planned |
| REQ-FUNC-066 | TCOND-20-05 | CI-1 | TC-ENB-006 | Planned |
| REQ-FUNC-066 | TCOND-20-05 | CI-2 | TC-ENB-007 | Planned |
| REQ-FUNC-066 | TCOND-20-05 | CI-3 | TC-ENB-008 | Planned |
| REQ-FUNC-066 | TCOND-21-08 | CI-1 | TC-DLV-001 | Planned |
| REQ-FUNC-066 | TCOND-21-08 | CI-2 | TC-DLV-002 | Planned |
| REQ-FUNC-067 | TCOND-20-08 | CI-1 | TC-TZR-001 | Planned |
| REQ-FUNC-067 | TCOND-20-08 | CI-2 | TC-TZR-002 | Planned |
| REQ-FUNC-067 | TCOND-20-08 | CI-3 | TC-TZR-003 | Planned |
| REQ-FUNC-067 | TCOND-20-09 | CI-1 | TC-TZR-004 | Planned |
| REQ-FUNC-067 | TCOND-20-09 | CI-2 | TC-TZR-005 | Planned |
| REQ-FUNC-067 | TCOND-20-09 | CI-3 | TC-TZR-006 | Planned |
| REQ-FUNC-067 | TCOND-20-10 | CI-1 | TC-TZR-007 | Planned |
| REQ-FUNC-067 | TCOND-20-11 | CI-1 | TC-TZR-008 | Planned |
| REQ-FUNC-067 | TCOND-20-12 | CI-1 | TC-TZR-009 | Planned |
| REQ-FUNC-067 | TCOND-26-01 | CI-2 | TC-NOT-002 | Planned |
| REQ-FUNC-067 | TCOND-30-01 | CI-1 | TC-TZO-001 | Planned |
| REQ-FUNC-067 | TCOND-30-02 | CI-1 | TC-TZO-002 | Planned |
| REQ-FUNC-067 | TCOND-30-02 | CI-2 | TC-TZO-003 | Planned |
| REQ-FUNC-067 | TCOND-30-02 | CI-3 | TC-TZO-004 | Planned |
| REQ-FUNC-067 | TCOND-30-03 | CI-1 | TC-TZO-005 | Planned |
| REQ-FUNC-068 | TCOND-24-01 | CI-1 | TC-APX-001 | Planned |
| REQ-FUNC-068 | TCOND-24-02 | CI-1 | TC-APX-002 | Planned |
| REQ-FUNC-068 | TCOND-24-02 | CI-2 | TC-APX-003 | Planned |
| REQ-FUNC-068 | TCOND-24-03 | CI-1 | TC-APX-004 | Planned |
| REQ-FUNC-068 | TCOND-24-03 | CI-2 | TC-APX-005 | Planned |
| REQ-FUNC-068 | TCOND-24-04 | CI-1 | TC-APX-006 | Planned |
| REQ-FUNC-068 | TCOND-24-04 | CI-2 | TC-APX-007 | Planned |
| REQ-FUNC-068 | TCOND-24-05 | CI-1 | TC-APX-008 | Planned |
| REQ-FUNC-068 | TCOND-24-05 | CI-2 | TC-APX-009 | Planned |
| REQ-FUNC-068 | TCOND-24-06 | CI-1 | TC-APX-010 | Planned |
| REQ-FUNC-068 | TCOND-24-07 | CI-1 | TC-APX-011 | Planned |
| REQ-FUNC-068 | TCOND-24-08 | CI-1 | TC-APX-012 | Planned |
| REQ-FUNC-069 | TCOND-21-04 | CI-1 | TC-LCK-001 | Planned |
| REQ-FUNC-069 | TCOND-21-04 | CI-2 | TC-LCK-002 | Planned |
| REQ-FUNC-069 | TCOND-21-04 | CI-3 | TC-LCK-003 | Planned |
| REQ-FUNC-069 | TCOND-21-05 | CI-1 | TC-AUD-001 | Planned |
| REQ-FUNC-069 | TCOND-21-05 | CI-2 | TC-AUD-002 | Planned |
| REQ-FUNC-069 | TCOND-21-05 | CI-3 | TC-AUD-003 | Planned |
| REQ-FUNC-069 | TCOND-21-07 | CI-2 | TC-SBT-004 | Planned |
| REQ-FUNC-069 | TCOND-21-13 | CI-1 | TC-TOUR-001 | Planned |
| REQ-FUNC-070 | TCOND-28-01 | CI-1 | TC-MDF-001 | Planned |
| REQ-FUNC-070 | TCOND-28-01 | CI-2 | TC-MDF-002 | Planned |
| REQ-FUNC-070 | TCOND-28-02 | CI-1 | TC-MDF-003 | Planned |
| REQ-FUNC-070 | TCOND-28-02 | CI-2 | TC-MDF-004 | Planned |
| REQ-FUNC-070 | TCOND-28-03 | CI-1 | TC-MDF-005 | Planned |
| REQ-FUNC-070 | TCOND-28-03 | CI-2 | TC-MDF-006 | Planned |
| REQ-FUNC-070 | TCOND-28-04 | CI-1 | TC-MDF-007 | Planned |
| REQ-FUNC-070 | TCOND-28-04 | CI-2 | TC-MDF-008 | Planned |
| REQ-FUNC-070 | TCOND-28-04 | CI-3 | TC-MDF-009 | Planned |
| REQ-FUNC-070 | TCOND-28-05 | CI-1 | TC-MDF-010 | Planned |
| REQ-FUNC-071 | TCOND-29-01 | CI-1 | TC-RPS-001 | Planned |
| REQ-FUNC-071 | TCOND-29-01 | CI-2 | TC-RPS-002 | Planned |
| REQ-FUNC-071 | TCOND-29-01 | CI-3 | TC-RPS-003 | Planned |
| REQ-FUNC-071 | TCOND-29-01 | CI-4 | TC-RPS-004 | Planned |
| REQ-FUNC-071 | TCOND-29-01 | CI-5 | TC-RPS-005 | Planned |
| REQ-FUNC-071 | TCOND-29-02 | CI-1 | TC-RPS-006 | Planned |
| REQ-FUNC-071 | TCOND-29-03 | CI-1 | TC-RPS-007 | Planned |
| REQ-FUNC-071 | TCOND-29-03 | CI-2 | TC-RPS-008 | Planned |
| REQ-FUNC-071 | TCOND-29-04 | CI-1 | TC-RPS-009 | Planned |
| REQ-FUNC-072 | TCOND-31-01 | CI-1 | TC-CLK-001 | Planned |
| REQ-FUNC-072 | TCOND-31-01 | CI-2 | TC-CLK-002 | Planned |
| REQ-FUNC-072 | TCOND-31-02 | CI-1 | TC-CLK-003 | Planned |
| REQ-FUNC-072 | TCOND-31-02 | CI-2 | TC-CLK-004 | Planned |
| REQ-INT-001 | TCOND-20-02 | CI-1 | TC-ENB-002 | Planned |
| REQ-INT-005 | TCOND-23-01 | CI-1 | TC-APS-001 | Planned |
| REQ-INT-005 | TCOND-23-02 | CI-1 | TC-APS-002 | Planned |
| REQ-INT-005 | TCOND-23-03 | CI-1 | TC-APS-003 | Planned |
| REQ-INT-005 | TCOND-23-04 | CI-1 | TC-APS-004 | Planned |
| REQ-INT-005 | TCOND-23-05 | CI-1 | TC-APS-005 | Planned |
| REQ-INT-005 | TCOND-23-06 | CI-1 | TC-APS-006 | Planned |
| REQ-INT-005 | TCOND-26-03 | CI-1 | TC-NOT-004 | Planned |
| REQ-INT-010 | TCOND-24-06 | CI-1 | TC-APX-010 | Planned |
| REQ-INT-012 | TCOND-21-01 | CI-1 | TC-DUE-001 | Planned |
| REQ-INT-012 | TCOND-21-01 | CI-2 | TC-DUE-002 | Planned |
| REQ-INT-012 | TCOND-21-02 | CI-1 | TC-DUE-003 | Planned |
| REQ-INT-012 | TCOND-21-02 | CI-2 | TC-DUE-004 | Planned |
| REQ-INT-012 | TCOND-21-03 | CI-1 | TC-DUE-005 | Planned |
| REQ-INT-012 | TCOND-25-02 | CI-2 | TC-FST-004 | Planned |
| REQ-INT-020 | TCOND-22-01 | CI-1 | TC-RCK-001 | Planned |
| REQ-INT-020 | TCOND-22-02 | CI-1 | TC-RCK-002 | Planned |
| REQ-INT-020 | TCOND-22-02 | CI-2 | TC-RCK-003 | Planned |
| REQ-INT-020 | TCOND-22-03 | CI-1 | TC-RCK-004 | Planned |
| REQ-INT-020 | TCOND-22-04 | CI-1 | TC-RCK-005 | Planned |
| REQ-INT-020 | TCOND-26-03 | CI-1 | TC-NOT-004 | Planned |
| REQ-INT-023 | TCOND-03-25 | CI-1 | TC-BRE-025 | Planned |
| REQ-INT-023 | TCOND-03-26 | CI-1 | TC-BRE-026 | Planned |
| REQ-INT-023 | TCOND-18-12 | CI-1 | TC-PRF-012 | Planned |
| REQ-INT-023 | TCOND-18-12 | CI-2 | TC-PRF-013 | Planned |
| REQ-INT-024 | TCOND-21-12 | CI-1 | TC-LGT-001 | Planned |
| REQ-INT-024 | TCOND-25-01 | CI-1 | TC-FST-001 | Planned |
| REQ-INT-024 | TCOND-25-01 | CI-2 | TC-FST-002 | Planned |
| REQ-INT-024 | TCOND-25-01 | CI-3 | TC-FST-009 | Planned |
| REQ-INT-024 | TCOND-25-02 | CI-1 | TC-FST-003 | Planned |
| REQ-INT-024 | TCOND-25-02 | CI-2 | TC-FST-004 | Planned |
| REQ-INT-024 | TCOND-25-02 | CI-3 | TC-FST-005 | Planned |
| REQ-INT-024 | TCOND-25-02 | CI-4 | TC-FST-007 | Planned |
| REQ-INT-024 | TCOND-25-02 | CI-5 | TC-FST-008 | Planned |
| REQ-INT-024 | TCOND-25-03 | CI-1 | TC-FST-006 | Planned |
| REQ-INT-024 | TCOND-25-04 | CI-1 | TC-FST-010 | Planned |
| REQ-INT-024 | TCOND-25-04 | CI-2 | TC-FST-011 | Planned |
| REQ-INT-024 | TCOND-25-05 | CI-1 | TC-FST-012 | Planned |
| REQ-INT-024 | TCOND-25-05 | CI-2 | TC-FST-013 | Planned |
| REQ-INT-024 | TCOND-25-06 | CI-1 | TC-FST-014 | Planned |
| REQ-INT-024 | TCOND-25-06 | CI-2 | TC-FST-015 | Planned |
| REQ-INT-024 | TCOND-25-07 | CI-1 | TC-FST-016 | Planned |
| REQ-INT-024 | TCOND-25-07 | CI-2 | TC-FST-017 | Planned |
| REQ-INT-024 | TCOND-25-07 | CI-3 | TC-FST-018 | Planned |
| REQ-INT-024 | TCOND-25-08 | CI-1 | TC-FST-019 | Planned |
| REQ-INT-024 | TCOND-25-08 | CI-2 | TC-FST-020 | Planned |
| REQ-INT-024 | TCOND-26-01 | CI-2 | TC-NOT-002 | Planned |
| REQ-INT-025 | TCOND-21-06 | CI-1 | TC-SBT-001 | Planned |
| REQ-INT-025 | TCOND-21-06 | CI-2 | TC-SBT-002 | Planned |
| REQ-INT-025 | TCOND-21-07 | CI-1 | TC-SBT-003 | Planned |
| REQ-INT-025 | TCOND-21-07 | CI-2 | TC-SBT-004 | Planned |
| REQ-INT-026 | TCOND-21-09 | CI-1 | TC-EHS-001 | Planned |
| REQ-INT-026 | TCOND-21-09 | CI-2 | TC-EHS-002 | Planned |
| REQ-INT-026 | TCOND-21-09 | CI-3 | TC-EHS-003 | Planned |
| REQ-INT-026 | TCOND-21-10 | CI-1 | TC-OSR-001 | Planned |
| REQ-INT-026 | TCOND-21-10 | CI-2 | TC-OSR-002 | Planned |
| REQ-INT-026 | TCOND-21-10 | CI-3 | TC-OSR-003 | Planned |
| REQ-INT-026 | TCOND-21-10 | CI-4 | TC-OSR-004 | Planned |
| REQ-INT-027 | TCOND-21-11 | CI-1 | TC-TLV-001 | Planned |
| REQ-INT-028 | TCOND-27-01 | CI-1 | TC-DUR-001 | Planned |
| REQ-INT-028 | TCOND-27-02 | CI-1 | TC-DUR-002 | Planned |
| REQ-INT-028 | TCOND-27-03 | CI-1 | TC-DUR-003 | Planned |
| REQ-INT-028 | TCOND-27-04 | CI-1 | TC-DUR-004 | Planned |
| REQ-INT-029 | TCOND-26-01 | CI-1 | TC-NOT-001 | Planned |
| REQ-INT-029 | TCOND-26-01 | CI-2 | TC-NOT-002 | Planned |
| REQ-INT-029 | TCOND-26-02 | CI-1 | TC-NOT-003 | Planned |
| REQ-INT-029 | TCOND-26-03 | CI-1 | TC-NOT-004 | Planned |
| REQ-OBS-003 | TCOND-12-30 | CI-1 | TC-ERR-030 | Planned |
| REQ-PERF-001 | TCOND-18-11 | CI-1 | TC-PRF-011 | Planned |
| REQ-PERF-001 | TCOND-20-05 | CI-2 | TC-ENB-007 | Planned |
| REQ-PERF-001 | TCOND-20-07 | CI-1 | TC-CND-005 | Planned |
| REQ-PERF-002 | TCOND-03-26 | CI-1 | TC-BRE-026 | Planned |
| REQ-PERF-002 | TCOND-18-11 | CI-1 | TC-PRF-011 | Planned |
| REQ-PERF-002 | TCOND-18-12 | CI-1 | TC-PRF-012 | Planned |
| REQ-PERF-002 | TCOND-18-12 | CI-2 | TC-PRF-013 | Planned |
| REQ-PERF-003 | TCOND-14-37 | CI-1 | TC-INF-037 | Planned |
| REQ-REL-002 | TCOND-08-70 | CI-1 | TC-PRC-001 | Planned |
| REQ-REL-002 | TCOND-08-70 | CI-2 | TC-PRC-002 | Planned |
| REQ-REL-002 | TCOND-08-71 | CI-1 | TC-PRC-003 | Planned |
| REQ-REL-002 | TCOND-18-11 | CI-1 | TC-PRF-011 | Planned |
| REQ-REL-002 | TCOND-24-04 | CI-1 | TC-APX-006 | Planned |
| REQ-SEC-001 | TCOND-16-25 | CI-1 | TC-SEC-025 | Planned |
| REQ-SEC-001 | TCOND-24-08 | CI-1 | TC-APX-012 | Planned |
| REQ-SEC-002 | TCOND-25-05 | CI-1 | TC-FST-012 | Planned |

---

## TG-01 — Gắn, kết thúc, điều kiện, kích hoạt đánh giá

### TC-ATT-001: Đánh giá record khi stop để rỗng: stop không khớp dù `ref`=DONE, task vẫn `in_progress`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-01 |
| Coverage Item | CI-1 (Lớp: stop rỗng (chưa cấu hình)) |
| Requirement Ref | REQ-FUNC-003 (AC1) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation). Biến thể: `stop_domain` rỗng (chưa cấu hình), `start_domain` = `[('id', '!=', 0)]` (khớp mọi record).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='DONE' | Giá trị trùng stop thông thường |
| now lần 1 | T0 | 09:00 VN |
| now lần 2 | T0 + 1h | 10:00 VN |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo partner P với `ref`='DONE'; gọi Engine `evaluate(P, now=T0, changed=None)`. | Có đúng 1 task `in_progress` (start `[('id', '!=', 0)]` khớp, stop rỗng không khớp, cancel không khớp); 1 event `attach`. |
| 2 | Gọi `evaluate(P, now=T0 + 1h, changed={'ref'})`. | Task vẫn `in_progress`; số event `complete` = 0; tổng event = 1. |

**Pass/Fail Criteria:** ✅ Pass: Task `in_progress`, không có event `complete`. ❌ Fail: Task `achieved` hoặc có event `complete`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-002: Đánh giá ba record có giá trị khác nhau khi start=`[('id', '!=', 0)]`: start khớp mọi record

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-01 |
| Coverage Item | CI-2 (Lớp: start = `[('id', '!=', 0)]`) |
| Requirement Ref | REQ-FUNC-003 (AC2) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation). Biến thể: `start_domain` = `[('id', '!=', 0)]` (khớp mọi record).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| P-A | `ref`='NEW' |  |
| P-B | `ref`='ZZZ' | Giá trị ngoài mọi tập |
| P-C | `ref` rỗng | Không có giá trị |
| now | T0 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P-A, P-B, P-C; gọi `evaluate([P-A, P-B, P-C], now=T0, changed=None)`. | Mỗi partner có đúng 1 task `in_progress`: tổng 3 task, mỗi partner 1 event `attach`. |

**Pass/Fail Criteria:** ✅ Pass: 3 task `in_progress`, 3 event `attach`. ❌ Fail: Thiếu task ở bất kỳ partner nào.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-003: Lưu domain có field không tồn tại: bị từ chối, thông báo nêu tên field

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-02 |
| Coverage Item | CI-1 (Lớp không hợp lệ: field không tồn tại) |
| Requirement Ref | REQ-FUNC-003 (AC3) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; model `res.partner` được phép gắn SLA.
2. Định nghĩa mới chưa lưu (số bản ghi `sla.definition` = n0 đã đọc).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| model | `res.partner` |  |
| start_domain | `[('x_khong_ton_tai','=',1)]` | Field không tồn tại |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` với `start_domain` như trên (`duration`=4). | Ném lỗi kiểm tra (`ValidationError`); thông báo chứa chuỗi `x_khong_ton_tai`. |
| 2 | Đếm lại `sla.definition`. | Số bản ghi = n0 (không lưu). |

**Pass/Fail Criteria:** ✅ Pass: Có lỗi, thông báo chứa tên field, không có bản ghi mới. ❌ Fail: Lưu thành công hoặc thông báo không nêu tên field.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-004: Lưu domain dùng `context_today()`: bị từ chối, thông báo nêu giới hạn literal

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-02 |
| Coverage Item | CI-2 (Lớp không hợp lệ: lời gọi hàm `context_today()`) |
| Requirement Ref | REQ-FUNC-003 (AC4) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; model `res.partner` được phép gắn SLA.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| model | `res.partner` |  |
| start_domain | `[('create_date','<',context_today())]` | Lời gọi hàm |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` với `start_domain` như trên. | Ném `ValidationError`; thông báo chứa từ `literal` (từ khóa theo `constants/message.py`: "is not a valid domain literal"). |

**Pass/Fail Criteria:** ✅ Pass: Bị từ chối, thông báo nêu giới hạn literal. ❌ Fail: Lưu thành công hoặc thông báo không nêu giới hạn.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-005: Lưu domain dùng biến `uid`: bị từ chối, thông báo nêu giới hạn literal

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-02 |
| Coverage Item | CI-3 (Lớp không hợp lệ: biến `uid`) |
| Requirement Ref | REQ-FUNC-003 (Statement (biến uid)) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; model `res.partner` được phép gắn SLA.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| model | `res.partner` |  |
| stop_domain | `[('user_id','=',uid)]` | Biến không phải literal |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` với `stop_domain` như trên. | Ném `ValidationError`; thông báo nêu giới hạn literal. |

**Pass/Fail Criteria:** ✅ Pass: Bị từ chối. ❌ Fail: Lưu thành công.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-006: Lưu domain literal hợp lệ (gồm ngày giờ literal) trên hai điều kiện: lưu thành công

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-02 |
| Coverage Item | CI-4 (Lớp hợp lệ: domain literal (gồm ngày giờ literal)) |
| Requirement Ref | REQ-FUNC-003 (Statement (literal hợp lệ)) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; model `res.partner` được phép gắn SLA.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| start_domain | `[('ref','=','NEW')]` |  |
| stop_domain | `[('create_date','<','2026-01-01 00:00:00')]` | Ngày giờ literal |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` (`duration`=4) với hai domain trên. | Lưu thành công, không lỗi. |
| 2 | Đọc lại `start_domain` và `stop_domain`. | Chuỗi domain đọc lại tương đương giá trị đã nhập. |

**Pass/Fail Criteria:** ✅ Pass: Lưu thành công, giá trị được giữ. ❌ Fail: Bị từ chối hoặc giá trị bị đổi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-007: Attach khi start khớp, stop và cancel không khớp: 1 task `in_progress`, 1 event `attach`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-03 |
| Coverage Item | CI-1 (R1) |
| Requirement Ref | REQ-FUNC-006 (AC1; Smoke) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='NEW' | start khớp, stop và cancel không khớp |
| now | T0 | 09:00 VN |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo partner P `ref`='NEW'; gọi `evaluate(P, now=T0, changed=None)`. | Có đúng 1 `sla.task`: `stage`='in_progress', `start_time`=2026-03-02 02:00 UTC, `planned_end_time`=2026-03-02 06:00 UTC (13:00 VN), `target_duration`=4, `business_duration`=0, `has_breached`=False, `end_time` rỗng. |
| 2 | Đọc `sla.event` của task. | Đúng 1 event, `event`='attach', `event_dt`=T0. |

**Pass/Fail Criteria:** ✅ Pass: Giá trị khớp từng field nêu ở các bước. ❌ Fail: Số task khác 1, stage khác `in_progress` hoặc số event khác 1.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-008: Attach khi start và pause cùng khớp: task `paused`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-03 |
| Coverage Item | CI-2 (R2) |
| Requirement Ref | REQ-FUNC-006 (AC2) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='HOLD' | start và pause cùng khớp |
| now | T0 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo partner P `ref`='HOLD'; gọi `evaluate(P, now=T0, changed=None)`. | Có đúng 1 task, `stage`='paused', `pause_time`=T0, `next_due_at` rỗng, `business_duration`=0. |
| 2 | Đếm event `attach` của task. | Đúng 1 event `attach` và 0 event `pause` (D2/TA-04: attach thẳng vào `paused` chỉ ghi đúng 1 event `attach`). |

**Pass/Fail Criteria:** ✅ Pass: Task `paused`, đúng 1 event `attach`, 0 event `pause`. ❌ Fail: Task `in_progress` hoặc không có task.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-009: Không attach khi start và stop cùng khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-03 |
| Coverage Item | CI-3 (R3 (negative)) |
| Requirement Ref | REQ-FUNC-006 (AC3) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation). Biến thể: `start_domain` = `[('id', '!=', 0)]` (khớp mọi record).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='DONE' | start (`[('id', '!=', 0)]`) và stop cùng khớp |
| now | T0 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo partner P `ref`='DONE'; gọi `evaluate(P, now=T0, changed=None)`. | Không có `sla.task` cho P; không có `sla.event` nào. |

**Pass/Fail Criteria:** ✅ Pass: 0 task, 0 event. ❌ Fail: Có task được tạo.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-010: Không attach khi start và cancel cùng khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-03 |
| Coverage Item | CI-4 (R4 (negative)) |
| Requirement Ref | REQ-FUNC-006 (AC4) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation). Biến thể: `start_domain` = `[('id', '!=', 0)]`, cancel_mode `condition`.
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='CANCEL' | start (`[('id', '!=', 0)]`) và cancel cùng khớp |
| now | T0 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo partner P `ref`='CANCEL'; gọi `evaluate(P, now=T0, changed=None)`. | Không có `sla.task` cho P; không có event. |

**Ghi chú:** Theo code (`sla_engine._maybe_attach`), điều kiện cancel khớp luôn chặn attach, không phụ thuộc `cancel_mode` (TA-18 đã chốt theo code; AC4 của SRS không nêu chế độ cancel).

**Pass/Fail Criteria:** ✅ Pass: 0 task, 0 event. ❌ Fail: Có task được tạo.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-011: Không attach khi start không khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-03 |
| Coverage Item | CI-5 (R5 (negative)) |
| Requirement Ref | REQ-FUNC-006 (Statement (start không khớp)) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='OTHER' | Ngoài tập start |
| now | T0 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo partner P `ref`='OTHER'; gọi `evaluate(P, now=T0, changed=None)`. | Không có task, không có event. |

**Pass/Fail Criteria:** ✅ Pass: 0 task, 0 event. ❌ Fail: Có task được tạo.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-012: Task `achieved` và start khớp lại khi sửa record: không tạo task mới

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-04 |
| Coverage Item | CI-1 (achieved + start khớp lại) |
| Requirement Ref | REQ-FUNC-007 (AC1) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` NEW → DONE → WORK |  |
| Mốc | T0; T0 + 1h; T0 + 2h |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='NEW'; `evaluate(P, T0, None)`. Ghi `ref`='DONE'; `evaluate(P, T0 + 1h, {'ref'})`. | Task A `achieved`, events [attach, complete]. |
| 2 | Ghi `ref`='WORK' (start khớp lại); `evaluate(P, T0 + 2h, {'ref'})`. | Vẫn đúng 1 task (A), `stage`='achieved'; tổng event = 2. |

**Pass/Fail Criteria:** ✅ Pass: Không có task thứ hai, A vẫn `achieved`. ❌ Fail: Có task mới hoặc A đổi stage.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-013: Task `breached` và start khớp lại khi sửa record: không tạo task mới

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-04 |
| Coverage Item | CI-2 (breached + start khớp lại) |
| Requirement Ref | REQ-FUNC-007 (Statement (breached)) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` NEW → DONE → NEW |  |
| Mốc | T0; T0 + 5h (14:00); T0 + 6h | Stop sau planned_end_time 13:00 |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='NEW'; `evaluate(P, T0, None)`. Ghi `ref`='DONE'; `evaluate(P, T0 + 5h, {'ref'})`. | Task A `breached` (`has_breached`=True). |
| 2 | Ghi `ref`='NEW'; `evaluate(P, T0 + 6h, {'ref'})`. | Vẫn 1 task, `stage`='breached'; số event không đổi so với sau bước 1. |

**Pass/Fail Criteria:** ✅ Pass: Không có task thứ hai, A vẫn `breached`. ❌ Fail: Có task mới hoặc A đổi stage.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-014: Task `achieved`, reset và start cùng khớp: không reset, không task mới

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-04 |
| Coverage Item | CI-3 (achieved + reset và start cùng khớp) |
| Requirement Ref | REQ-FUNC-007 (AC2) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD biến thể: `start_domain` = `[('id', '!=', 0)]`, `reset_domain` = `[('ref','=','RESET')]`, reset_action `cancel`.
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` NEW → DONE → RESET |  |
| Mốc | T0; T0 + 1h; T0 + 2h |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='NEW'; `evaluate(P, T0, None)`. Ghi `ref`='DONE'; `evaluate(P, T0 + 1h, {'ref'})`. | Task A `achieved`; events [attach, complete]. |
| 2 | Ghi `ref`='RESET' (reset khớp, start khớp); `evaluate(P, T0 + 2h, {'ref'})`. | A vẫn `achieved`; không task mới; số event `reset` = 0; tổng event = 2. |

**Pass/Fail Criteria:** ✅ Pass: A `achieved`, 1 task, 0 event `reset`. ❌ Fail: A đổi stage, có task mới hoặc có event `reset`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-015: Task `cancelled` và start khớp lại: tạo task mới `in_progress`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-04 |
| Coverage Item | CI-4 (cancelled + start khớp lại) |
| Requirement Ref | REQ-FUNC-007 (AC3; Smoke mở rộng) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` NEW → CANCEL → NEW |  |
| Mốc | T0; T0 + 1h; T0 + 2h |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='NEW'; `evaluate(P, T0, None)`. Ghi `ref`='CANCEL'; `evaluate(P, T0 + 1h, {'ref'})`. | Task A `cancelled` (start không còn khớp), events [attach, cancel]. |
| 2 | Ghi `ref`='NEW'; `evaluate(P, T0 + 2h, {'ref'})`. | Tổng 2 task: A vẫn `cancelled`; task B `in_progress`, `start_time`=T0 + 2h (04:00 UTC), `planned_end_time`=15:00 VN (08:00 UTC); thêm 1 event `attach` cho B. |

**Pass/Fail Criteria:** ✅ Pass: Task B `in_progress` với giá trị nêu trên. ❌ Fail: Không có task B hoặc A đổi stage.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-016: Task `cancelled`, start khớp nhưng stop khớp: không tạo task mới

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-04 |
| Coverage Item | CI-5 (cancelled + start khớp nhưng stop khớp (negative)) |
| Requirement Ref | REQ-FUNC-007 (Statement (cancelled, stop khớp)) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD biến thể: `start_domain` = `[('id', '!=', 0)]`, cancel_mode `condition`.
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` NEW → CANCEL → DONE |  |
| Mốc | T0; T0 + 1h; T0 + 2h |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='NEW'; `evaluate(P, T0, None)`. Ghi `ref`='CANCEL'; `evaluate(P, T0 + 1h, {'ref'})`. | Task A `cancelled`. |
| 2 | Ghi `ref`='DONE' (start `[('id', '!=', 0)]` khớp, stop khớp); `evaluate(P, T0 + 2h, {'ref'})`. | Vẫn 1 task (A `cancelled`); không event mới. |

**Pass/Fail Criteria:** ✅ Pass: 1 task `cancelled`, không event mới. ❌ Fail: Có task mới.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-017: Stop khớp khi task chưa quá hạn: `achieved`, `end_time` = thời điểm stop, 1 event `complete`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-05 |
| Coverage Item | CI-1 (in_progress chưa vi phạm → stop) |
| Requirement Ref | REQ-FUNC-009 (AC1; Smoke) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` NEW → DONE |  |
| Mốc | T0; T0 + 1h (10:00 VN) | planned_end_time = 13:00 VN |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='NEW'; `evaluate(P, T0, None)`. | Task `in_progress`. |
| 2 | Ghi `ref`='DONE'; `evaluate(P, T0 + 1h, {'ref'})`. | `stage`='achieved'; `end_time`=2026-03-02 03:00 UTC (10:00 VN); `business_duration`=1.0; `has_breached`=False; đúng 1 event `complete` (`event_dt`=03:00 UTC); events [attach, complete]. |

**Pass/Fail Criteria:** ✅ Pass: `achieved`, `end_time` 03:00 UTC, 1 `complete`. ❌ Fail: Stage khác `achieved`, `end_time` lệch, hoặc số `complete` ≠ 1.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-018: Stop khớp lần nữa trên task đã `achieved`: task và event không đổi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-05 |
| Coverage Item | CI-2 (achieved → stop khớp lần nữa (negative)) |
| Requirement Ref | REQ-FUNC-009 (AC4) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` NEW → DONE → DONE |  |
| Mốc | T0; T0 + 1h; T0 + 2h |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='NEW', attach tại T0; ghi `ref`='DONE', `evaluate(P, T0 + 1h, {'ref'})`. | Task `achieved`, `end_time`=03:00 UTC; 2 event. |
| 2 | Ghi lại `ref`='DONE' (stop vẫn khớp); `evaluate(P, T0 + 2h, {'ref'})`. | Task vẫn `achieved`, `end_time`=03:00 UTC (không đổi), `business_duration`=1.0; tổng event = 2; số task = 1. |

**Pass/Fail Criteria:** ✅ Pass: Không đổi gì ở bước 2. ❌ Fail: `end_time` đổi hoặc có event mới.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-019: Tạo record khớp start: có 1 task `in_progress`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-06 |
| Coverage Item | CI-1 (Tạo record khớp start) |
| Requirement Ref | REQ-FUNC-004 (AC1; Smoke) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='WORK' | Giá trị khớp start |
| now | T0 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo partner P `ref`='WORK' và gọi `evaluate(P, now=T0, changed=None)` (đường create của Hook). | Có đúng 1 task `in_progress` cho (FX-DEF-STD, P). |

**Pass/Fail Criteria:** ✅ Pass: 1 task `in_progress`. ❌ Fail: 0 hoặc >1 task.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-020: Tạo record không khớp start: không có task

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-06 |
| Coverage Item | CI-2 (Tạo record không khớp start) |
| Requirement Ref | REQ-FUNC-004 (EP (không khớp)) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='OTHER' |  |
| now | T0 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo partner P `ref`='OTHER' và gọi `evaluate(P, T0, None)`. | Không có task, không có event. |

**Pass/Fail Criteria:** ✅ Pass: 0 task. ❌ Fail: Có task.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-021: Sửa field stop khi task đang chạy: task chuyển `achieved`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-06 |
| Coverage Item | CI-3 (Sửa field nằm trong điều kiện stop) |
| Requirement Ref | REQ-FUNC-004 (AC2) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` WORK → DONE |  |
| Mốc | T0; T0 + 30m (09:30) |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='WORK'; `evaluate(P, T0, None)`. | Task `in_progress`. |
| 2 | Ghi `ref`='DONE'; `evaluate(P, T0 + 30m, {'ref'})`. | Task `achieved`, `end_time`=02:30 UTC, `business_duration`=0.5. |

**Pass/Fail Criteria:** ✅ Pass: Task `achieved` sau bước 2. ❌ Fail: Task còn `in_progress`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-022: Sửa field không thuộc điều kiện nào: số task và số event không đổi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-06 |
| Coverage Item | CI-4 (Sửa field không thuộc điều kiện nào (negative)) |
| Requirement Ref | REQ-FUNC-004 (AC3) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='WORK' |  |
| Field sửa | `comment`='ghi chú nội bộ' | Không thuộc điều kiện/field retroactive/reset |
| Mốc | T0; T0 + 30m |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='WORK'; `evaluate(P, T0, None)`. Ghi nhận ảnh chụp task (stage, planned_end_time, business_duration, running_since, next_due_at) và số event. | 1 task `in_progress`, 1 event `attach`. |
| 2 | Ghi `comment`='ghi chú nội bộ'; `evaluate(P, T0 + 30m, {'comment'})`. | Vẫn 1 task, 1 event; ảnh chụp task không đổi. |

**Pass/Fail Criteria:** ✅ Pass: Số task, số event và ảnh chụp task không đổi. ❌ Fail: Bất kỳ giá trị nào đổi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-023: Đánh giá lại ngay sau attach: không tạo task, không đổi giá trị, không event

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-07 |
| Coverage Item | CI-1 (Lặp lại ngay sau attach (`in_progress`)) |
| Requirement Ref | REQ-FUNC-015 (AC1) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='NEW' |  |
| now | T0 cho cả hai lần |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; `evaluate(P, T0, None)`. Ghi ảnh chụp task và số event. | 1 task `in_progress`, 1 event `attach`. |
| 2 | Gọi lại `evaluate(P, T0, None)` với dữ liệu không đổi. | Số task = 1, số event = 1, ảnh chụp task giống hệt bước 1. |

**Pass/Fail Criteria:** ✅ Pass: Lần hai không thay đổi gì. ❌ Fail: Có task hoặc event mới, hoặc giá trị đổi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-024: Đánh giá lại khi task `paused` và dữ liệu không đổi: không event, không đổi giá trị

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-07 |
| Coverage Item | CI-2 (Lặp lại khi task `paused` (negative)) |
| Requirement Ref | REQ-FUNC-015 (AC1 (mở rộng sang `paused`)) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='HOLD' | Attach ở `paused` |
| Mốc | T0; T0 + 1h |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='HOLD'; `evaluate(P, T0, None)`. Ghi ảnh chụp task và số event. | 1 task `paused`, 1 event. |
| 2 | Gọi `evaluate(P, T0 + 1h, None)` với dữ liệu không đổi. | Số task, số event và ảnh chụp task không đổi (`pause_time`=T0). |

**Pass/Fail Criteria:** ✅ Pass: Không đổi gì. ❌ Fail: Có event mới hoặc giá trị đổi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-025: Đổi `ref` giữa hai giá trị đều khớp start (NEW → WORK): không có event mới

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-08 |
| Coverage Item | CI-1 (Đổi giá trị field điều kiện nhưng kết quả đánh giá không đổi) |
| Requirement Ref | REQ-FUNC-029 (AC2) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` NEW → WORK | Cả hai chỉ khớp start |
| Mốc | T0; T0 + 1h |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='NEW'; `evaluate(P, T0, None)`. | 1 task `in_progress`, 1 event `attach`. |
| 2 | Ghi `ref`='WORK'; `evaluate(P, T0 + 1h, {'ref'})`. | Task vẫn `in_progress`; `business_duration` và `planned_end_time` (06:00 UTC) không đổi; tổng event = 1. |

**Pass/Fail Criteria:** ✅ Pass: Không event mới. ❌ Fail: Có event mới.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-026: Ghi lại đúng giá trị `ref` cũ: không có event mới

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-08 |
| Coverage Item | CI-2 (Ghi lại đúng giá trị cũ) |
| Requirement Ref | REQ-FUNC-029 (AC2) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='NEW' ghi lại 'NEW' |  |
| Mốc | T0; T0 + 1h |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='NEW'; `evaluate(P, T0, None)`. | 1 task, 1 event. |
| 2 | Ghi `ref`='NEW' (không đổi giá trị); `evaluate(P, T0 + 1h, {'ref'})`. | Số event = 1, ảnh chụp task không đổi. |

**Pass/Fail Criteria:** ✅ Pass: Không event mới. ❌ Fail: Có event mới.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ATT-027: Patch hook bị xóa (mô phỏng lưu một automation rule): xử lý tiếp theo tự đăng ký lại và tạo record khớp start vẫn có task

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-01-06 |
| Coverage Item | CI-5 (Patch động bị mất rồi tự phục hồi, AD-01/D9) |
| Requirement Ref | REQ-FUNC-004 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; mục tiêu 4 giờ; 24x7); hook đã đăng ký (hàm `create`, `write`, `_compute_field_value` của `res.partner` có `sla_patch`).
2. Chưa có `sla.task` nào của partner thử; `odoo.fields.Datetime.now` được patch trả FX-T0.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Mô phỏng mất patch | `delattr(type(env['res.partner']), name)` cho 3 tên hàm | giống `base_automation._unregister_hook` khi lưu automation rule |
| ref | NEW |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Xóa 3 hàm đã patch trên `res.partner` bằng `delattr`; đọc `sla_patch` của `create` | Không còn dấu `sla_patch` |
| 2 | Tạo partner P-1 `ref`='NEW' (hook mất nên chưa có task) | 0 task cho P-1 |
| 3 | Gọi `sla.processor.process_due()` (đầu hàm gọi `_ensure_hook_registered`) | Có log cảnh báo mức WARNING nêu `res.partner` bị mất patch; `create` của `res.partner` có lại `sla_patch` |
| 4 | Tạo partner P-2 `ref`='NEW' | P-2 có đúng 1 task `in_progress` và 1 event `attach` (hook hoạt động lại) |
| 5 | Gọi `sla.engine.evaluate(P-1, now = FX-T0)` (tương đương đánh giá lại thủ công qua engine, REQ-FUNC-032) | P-1 có đúng 1 task `in_progress` (bù cho lần mất patch) |

**Pass/Fail Criteria:** ✅ Pass: patch được đăng ký lại tự động và record tạo sau đó có task; ❌ Fail: patch không phục hồi, hoặc P-2 không có task

**Ghi chú:** Ca spike QS-12 / rủi ro R-01 (TAD AD-01 patch động, D9). Log cảnh báo của `_ensure_hook_registered` là text log nội bộ (tiếng Việt, không thuộc `constants/message.py`): kiểm bằng từ khóa `res.partner`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase); khôi phục patch bằng `_register_sla_hook()` trong `tearDown`.

## TG-02 — Pause và resume

### TC-PAU-001: Pause task `in_progress` đã chạy 1 giờ: `paused`, đã trôi 1 giờ, 1 event `pause`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-02-01 |
| Coverage Item | CI-1 (`in_progress` → pause) |
| Requirement Ref | REQ-FUNC-011 (AC1) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` WORK → HOLD |  |
| Mốc | T0; T0 + 1h (10:00 VN) |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='WORK'; `evaluate(P, T0, None)`. | Task `in_progress`. |
| 2 | Ghi `ref`='HOLD'; `evaluate(P, T0 + 1h, {'ref'})`. | `stage`='paused'; `business_duration`=1.0; `pause_time`=03:00 UTC; `next_due_at` rỗng; `has_breached`=False; đúng 1 event `pause` (`event_dt`=03:00 UTC); events [attach, pause]. |

**Pass/Fail Criteria:** ✅ Pass: Các giá trị nêu ở bước 2 đúng. ❌ Fail: Stage khác `paused`, elapsed ≠ 1.0 hoặc số `pause` ≠ 1.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-PAU-002: Task `paused`, pause tiếp tục khớp: không có event mới

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-02-01 |
| Coverage Item | CI-2 (`paused` + pause vẫn khớp (negative)) |
| Requirement Ref | REQ-FUNC-011 (AC2) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` WORK → HOLD → HOLD |  |
| Mốc | T0; T0 + 1h; T0 + 2h |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='WORK', attach; ghi `ref`='HOLD', `evaluate(P, T0 + 1h, {'ref'})`. | Task `paused`; 2 event. |
| 2 | Ghi lại `ref`='HOLD'; `evaluate(P, T0 + 2h, {'ref'})`. | Vẫn `paused`; `pause_time`=03:00 UTC; `business_duration`=1.0; tổng event = 2. |

**Pass/Fail Criteria:** ✅ Pass: Không event mới, không đổi giá trị. ❌ Fail: Có event mới hoặc `pause_time` đổi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-PAU-003: Task `achieved`, pause khớp: task không đổi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-02-01 |
| Coverage Item | CI-3 (`achieved` + pause khớp (negative)) |
| Requirement Ref | REQ-FUNC-011 (AC3) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` NEW → DONE → HOLD |  |
| Mốc | T0; T0 + 1h; T0 + 2h |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='NEW', attach; ghi `ref`='DONE'; `evaluate(P, T0 + 1h, {'ref'})`. | Task `achieved`, `end_time`=03:00 UTC; 2 event. |
| 2 | Ghi `ref`='HOLD' (pause và start khớp); `evaluate(P, T0 + 2h, {'ref'})`. | Task vẫn `achieved`, `end_time`=03:00 UTC; số task = 1; tổng event = 2. |

**Pass/Fail Criteria:** ✅ Pass: Task không đổi. ❌ Fail: Task đổi stage hoặc có event `pause`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-PAU-004: Resume khớp ở chế độ `condition`: task `paused` về `in_progress`, 1 event `resume`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-02-02 |
| Coverage Item | CI-1 (R1: resume khớp) |
| Requirement Ref | REQ-FUNC-037 (AC1) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation). resume_mode `condition`.
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` WORK → HOLD → WORK |  |
| Mốc | T0; T0 + 1h (10:00); T0 + 3h (12:00) |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='WORK', attach; ghi `ref`='HOLD', `evaluate(P, T0 + 1h, {'ref'})`. | Task `paused`. |
| 2 | Ghi `ref`='WORK' (resume khớp); `evaluate(P, T0 + 3h, {'ref'})`. | `stage`='in_progress'; `pause_time` rỗng; `running_since`=05:00 UTC; `business_duration`=1.0; đúng 1 event `resume` (`event_dt`=05:00 UTC). |

**Pass/Fail Criteria:** ✅ Pass: `in_progress`, 1 event `resume`. ❌ Fail: Còn `paused` hoặc số `resume` ≠ 1.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-PAU-005: Chế độ `condition`: pause hết khớp nhưng resume chưa khớp: vẫn `paused`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-02-02 |
| Coverage Item | CI-2 (R2: pause hết khớp, resume chưa khớp (negative)) |
| Requirement Ref | REQ-FUNC-037 (AC2) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation). resume_mode `condition`.
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` WORK → HOLD → NEW | NEW: pause N, resume N |
| Mốc | T0; T0 + 1h; T0 + 2h |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='WORK', attach; ghi `ref`='HOLD', `evaluate(P, T0 + 1h, {'ref'})`. | Task `paused`; 2 event. |
| 2 | Ghi `ref`='NEW' (pause hết khớp, resume không khớp); `evaluate(P, T0 + 2h, {'ref'})`. | Task vẫn `paused`; số event `resume` = 0; tổng event = 2. |

**Pass/Fail Criteria:** ✅ Pass: Vẫn `paused`, không `resume`. ❌ Fail: Task về `in_progress`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-PAU-006: Chế độ `pause_unmatched`: pause hết khớp thì resume (resume không khớp)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-02-03 |
| Coverage Item | CI-1 (R1: pause hết khớp) |
| Requirement Ref | REQ-FUNC-048 (AC1) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation). Biến thể: resume_mode `pause_unmatched`.
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` WORK → HOLD → NEW | NEW: pause N, resume N |
| Mốc | T0; T0 + 1h; T0 + 2h |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='WORK', attach; ghi `ref`='HOLD', `evaluate(P, T0 + 1h, {'ref'})`. | Task `paused`. |
| 2 | Ghi `ref`='NEW'; `evaluate(P, T0 + 2h, {'ref'})`. | `stage`='in_progress'; đúng 1 event `resume` (`event_dt`=04:00 UTC); events [attach, pause, resume]. |

**Pass/Fail Criteria:** ✅ Pass: `in_progress`, 1 `resume`. ❌ Fail: Còn `paused`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-PAU-007: Chế độ `pause_unmatched`: pause vẫn khớp dù resume khớp: vẫn `paused`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-02-03 |
| Coverage Item | CI-2 (R2: pause vẫn khớp, resume khớp (negative)) |
| Requirement Ref | REQ-FUNC-048 (AC2) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation). Biến thể: resume_mode `pause_unmatched`, `resume_domain` = `[]` (luôn khớp).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` WORK → HOLD → HOLD |  |
| Mốc | T0; T0 + 1h; T0 + 2h |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='WORK', attach; ghi `ref`='HOLD', `evaluate(P, T0 + 1h, {'ref'})`. | Task `paused`. |
| 2 | Ghi lại `ref`='HOLD' (pause khớp, resume `[('id', '!=', 0)]` khớp); `evaluate(P, T0 + 2h, {'ref'})`. | Task vẫn `paused`; số event `resume` = 0; tổng event = 2. |

**Pass/Fail Criteria:** ✅ Pass: Vẫn `paused`. ❌ Fail: Task về `in_progress`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-PAU-008: Cấu hình khuyến nghị trên ticket P1: 1 task, đúng 4 event [attach, pause, resume, complete], `achieved`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-02-03 |
| Coverage Item | CI-3 (Đầu cuối: in_progress → waiting_customer → resolved → in_progress → closed) |
| Requirement Ref | REQ-FUNC-048 (AC3) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` và `dwo_sla_demo_ticket` đã cài (FX-DEMO).
2. Định nghĩa trên `demo.ticket`: start `[('priority','=','p1')]`; pause `[('stage','in',['waiting_customer','resolved'])]`; resume_mode `pause_unmatched`; stop `[('stage','=','closed')]`; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`. (Phụ thuộc: TA-15, module demo `dwo_sla_demo_ticket` chưa hiện thực: `demo.ticket` phải có `priority` chứa `p1` và `stage` chứa các giá trị trên theo AC của SRS)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Ticket | `priority`='p1', `stage` in_progress → waiting_customer → resolved → in_progress → closed |  |
| Mốc | T0, T0 + 1h, T0 + 2h, T0 + 3h, T0 + 3.5h | 09:00, 10:00, 11:00, 12:00, 12:30 VN |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo ticket K `priority`='p1', `stage`='in_progress'; `evaluate(K, T0, None)`. | 1 task `in_progress`; events [attach]. |
| 2 | Ghi `stage`='waiting_customer'; `evaluate(K, T0 + 1h, {'stage'})`. | Task `paused`; events [attach, pause]. |
| 3 | Ghi `stage`='resolved'; `evaluate(K, T0 + 2h, {'stage'})`. | Vẫn `paused`; số event vẫn 2 (pause vẫn khớp). |
| 4 | Ghi `stage`='in_progress'; `evaluate(K, T0 + 3h, {'stage'})`. | Task `in_progress`; 3 event, event cuối `resume`. |
| 5 | Ghi `stage`='closed'; `evaluate(K, T0 + 3.5h, {'stage'})`. | Task `achieved`, `end_time`=05:30 UTC (12:30 VN), `business_duration`=1.5; tổng 1 task; đúng 4 event theo thứ tự [attach, pause, resume, complete]. |

**Pass/Fail Criteria:** ✅ Pass: 1 task, đúng 4 event đúng thứ tự, `achieved`. ❌ Fail: Số event ≠ 4, sai thứ tự hoặc có task thứ hai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-PAU-009: Resume khi chưa vi phạm: `planned_end_time` = thời điểm resume + phần còn lại (17:00)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-02-04 |
| Coverage Item | CI-1 (Dấu vi phạm chưa bật) |
| Requirement Ref | REQ-FUNC-044 (AC1) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation). `duration`=4, lịch 24x7.
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` WORK → HOLD → WORK |  |
| Mốc | T0; T0 + 1h (pause); T0 + 5h (14:00, resume) |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='WORK'; `evaluate(P, T0, None)`. | `planned_end_time`=06:00 UTC (13:00 VN). |
| 2 | Ghi `ref`='HOLD'; `evaluate(P, T0 + 1h, {'ref'})`. | `paused`, `business_duration`=1.0, `has_breached`=False. |
| 3 | Ghi `ref`='WORK'; `evaluate(P, T0 + 5h, {'ref'})`. | `in_progress`; `planned_end_time`=2026-03-02 10:00 UTC (17:00 VN = 14:00 + 3h); `has_breached`=False. |

**Pass/Fail Criteria:** ✅ Pass: `planned_end_time` = 10:00 UTC. ❌ Fail: `planned_end_time` ≠ 10:00 UTC.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-PAU-010: Resume khi dấu vi phạm đã bật: `planned_end_time` giữ nguyên 13:00

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-02-04 |
| Coverage Item | CI-2 (Dấu vi phạm đã bật (negative)) |
| Requirement Ref | REQ-FUNC-044 (AC2) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation). `duration`=4, lịch 24x7.
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` WORK → HOLD → WORK |  |
| Mốc | T0; BG 13:01; pause 13:30; resume 14:00 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='WORK'; `evaluate(P, T0, None)`. Xử lý nền tại now=T0 + 4h01m (13:01). | `has_breached`=True; `planned_end_time`=06:00 UTC (13:00 VN). |
| 2 | Ghi `ref`='HOLD'; `evaluate(P, T0 + 4.5h, {'ref'})`. | `paused`; `business_duration`=4.5. |
| 3 | Ghi `ref`='WORK'; `evaluate(P, T0 + 5h, {'ref'})`. | `in_progress`; `planned_end_time` vẫn 06:00 UTC (13:00 VN); `has_breached`=True. |

**Pass/Fail Criteria:** ✅ Pass: `planned_end_time` không đổi. ❌ Fail: `planned_end_time` bị dời.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-PAU-011: Vòng đời attach, pause, resume, stop: đúng 4 event theo thứ tự thời gian

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-02-05 |
| Coverage Item | CI-1 (Vòng đời đầy đủ) |
| Requirement Ref | REQ-FUNC-029 (AC1) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` NEW → HOLD → WORK → DONE |  |
| Mốc | T0; T0 + 1h; T0 + 2h; T0 + 3h | 09:00, 10:00, 11:00, 12:00 |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='NEW'; `evaluate(P, T0, None)`. | Event: attach. |
| 2 | Ghi `ref`='HOLD'; `evaluate(P, T0 + 1h, {'ref'})`. | Thêm: pause. |
| 3 | Ghi `ref`='WORK'; `evaluate(P, T0 + 2h, {'ref'})`. | Thêm: resume. |
| 4 | Ghi `ref`='DONE'; `evaluate(P, T0 + 3h, {'ref'})`. | Thêm: complete; task `achieved`, `business_duration`=2.0. |
| 5 | Đọc `sla.event` của task sắp theo `event_dt`, `id`. | Đúng 4 event [attach 02:00, pause 03:00, resume 04:00, complete 05:00 UTC]. |

**Pass/Fail Criteria:** ✅ Pass: Danh sách event đúng 4 phần tử đúng thứ tự. ❌ Fail: Thiếu, thừa hoặc sai thứ tự event.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

## TG-03 — Vi phạm và quanh hạn

### TC-BRE-001: Xử lý nền tại 12:59 (trước `planned_end_time` 13:00): không vi phạm

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-01 |
| Coverage Item | CI-1 (Trước biên: now = 12:59 (negative)) |
| Requirement Ref | REQ-FUNC-022 (AC4) |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='WORK' |  |
| now attach | T0 | planned_end_time = 13:00 VN (06:00 UTC) |
| now xử lý nền | T0 + 3h59m (12:59) |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; `evaluate(P, T0, None)`. Gọi xử lý nền với now=12:59. | `has_breached`=False; số event `breach` = 0; `stage`='in_progress'. |

**Pass/Fail Criteria:** ✅ Pass: Không dấu vi phạm, không `breach`. ❌ Fail: Có `breach` hoặc dấu bật.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-002: Xử lý nền đúng 13:00 (chạm `planned_end_time`): bật dấu vi phạm, 1 event `breach`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-01 |
| Coverage Item | CI-2 (Tại biên: now = 13:00) |
| Requirement Ref | REQ-FUNC-022 (AC1 (biên)) |
| Priority | P1-Critical |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='WORK' |  |
| now xử lý nền | T0 + 4h (13:00) | đã trôi = mục tiêu |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; `evaluate(P, T0, None)`. Gọi xử lý nền với now=13:00. | `has_breached`=True; đúng 1 event `breach` (`event_dt`=06:00 UTC); `stage`='in_progress'. |

**Pass/Fail Criteria:** ✅ Pass: Dấu bật, 1 `breach`. ❌ Fail: Dấu không bật hoặc số `breach` ≠ 1.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-003: Xử lý nền lúc 13:01 khi không ai sửa record: dấu vi phạm bật, đúng 1 event `breach`, vẫn `in_progress`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-01 |
| Coverage Item | CI-3 (Sau biên: now = 13:01) |
| Requirement Ref | REQ-FUNC-022 (AC1) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='WORK' |  |
| now xử lý nền | T0 + 4h01m (13:01) |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; `evaluate(P, T0, None)`. Gọi xử lý nền với now=13:01. | `has_breached`=True; đúng 1 event `breach` với `event_dt` = 06:01 UTC (= `now` lúc xử lý, D3/TA-05 đã chốt); `stage`='in_progress'; `end_time` rỗng. |

**Pass/Fail Criteria:** ✅ Pass: Như bước 1. ❌ Fail: Sai bất kỳ giá trị.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-004: Xử lý nền chạy lần hai sau khi vi phạm: vẫn đúng 1 event `breach`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-01 |
| Coverage Item | CI-4 (Xử lý nền chạy lần hai sau khi đã vi phạm (negative)) |
| Requirement Ref | REQ-FUNC-022 (Statement (đúng một lần)) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='WORK' |  |
| now xử lý nền | 13:01 rồi 13:02 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; attach tại T0; xử lý nền now=13:01. | 1 event `breach`. |
| 2 | Xử lý nền lần hai với now=13:02. | Số event `breach` vẫn = 1; tổng event = 2 (attach, breach); `has_breached`=True. |

**Pass/Fail Criteria:** ✅ Pass: Đúng 1 `breach`. ❌ Fail: Có `breach` thứ hai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-005: Pause lúc 14:00 trước khi xử lý nền: breach ghi lúc 14:00 rồi task `paused`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-02 |
| Coverage Item | CI-1 (Pause sau `planned_end_time` (14:00), chưa có xử lý nền) |
| Requirement Ref | REQ-FUNC-022 (AC2) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` WORK → HOLD |  |
| Mốc | T0; T0 + 5h (14:00) | planned_end_time 13:00, chưa chạy xử lý nền |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; `evaluate(P, T0, None)`. Không chạy xử lý nền. | Task `in_progress`, `has_breached`=False. |
| 2 | Ghi `ref`='HOLD'; `evaluate(P, T0 + 5h, {'ref'})`. | `has_breached`=True; `stage`='paused'; `business_duration`=5.0; events theo `id`: [attach, breach (`event_dt`=07:00 UTC), pause (`event_dt`=07:00 UTC)]. |

**Pass/Fail Criteria:** ✅ Pass: Có `breach` trước `pause`, cả hai lúc 07:00 UTC. ❌ Fail: Không có `breach` hoặc sai thứ tự.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-006: Pause đúng 13:00 (đã trôi = mục tiêu): dấu vi phạm bật, breach rồi pause

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-02 |
| Coverage Item | CI-2 (Pause đúng `planned_end_time` (13:00), đã trôi = mục tiêu) |
| Requirement Ref | REQ-FUNC-022 (AC2 (biên)) |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` WORK → HOLD |  |
| Mốc | T0; T0 + 4h (13:00) |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; `evaluate(P, T0, None)`. Ghi `ref`='HOLD'; `evaluate(P, T0 + 4h, {'ref'})`. | `has_breached`=True; `stage`='paused'; `business_duration`=4.0; events [attach, breach, pause], `breach.id` < `pause.id`. |

**Pass/Fail Criteria:** ✅ Pass: Dấu bật, đúng thứ tự. ❌ Fail: Dấu không bật.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-007: Mốc 100% đến hạn cùng lúc vi phạm: `breach` ghi trước `escalate` của mốc 100%

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-03 |
| Coverage Item | CI-1 (Mốc 100% cùng đến hạn với vi phạm) |
| Requirement Ref | REQ-FUNC-022 (AC3) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation). FX-ESC-STD biến thể: chỉ một mốc `percent`=100, server action ghi chú vào chatter của partner.
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='WORK' |  |
| now xử lý nền | T0 + 4h01m (13:01) |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; `evaluate(P, T0, None)`. Xử lý nền now=13:01. | Có đúng 1 event `breach` và đúng 1 event `escalate`. |
| 2 | So sánh `breach` với `escalate`. | `breach.id` < `escalate.id` và `breach.event_dt` ≤ `escalate.event_dt`. |

**Pass/Fail Criteria:** ✅ Pass: Thứ tự đúng. ❌ Fail: `breach` ghi sau `escalate`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-008: Mốc 120% đến hạn cùng lần xử lý với vi phạm: `breach` ghi trước `escalate`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-03 |
| Coverage Item | CI-2 (Mốc 120% đến hạn trong cùng lần xử lý với vi phạm) |
| Requirement Ref | REQ-FUNC-022 (AC3 (mốc trên 100%)) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation). Biến thể: một mốc `percent`=120 (đến hạn 13:48), server action ghi chú vào chatter.
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='WORK' |  |
| now xử lý nền | T0 + 4h50m (13:50) | Cả `planned_end_time` (13:00) và mốc 120% (13:48) đã đến hạn |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; `evaluate(P, T0, None)`. Xử lý nền lần đầu với now=13:50. | Đúng 1 `breach` và 1 `escalate`; `breach.id` < `escalate.id`. |

**Pass/Fail Criteria:** ✅ Pass: `breach` trước `escalate`. ❌ Fail: Sai thứ tự.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-009: Stop khi đã quá `planned_end_time` nhưng xử lý nền chưa chạy: `breached`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-04 |
| Coverage Item | CI-1 (R2) |
| Requirement Ref | REQ-FUNC-009 (AC2) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` NEW → DONE |  |
| Mốc | T0; T0 + 4.5h (13:30) | planned_end_time 13:00, không chạy xử lý nền |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; `evaluate(P, T0, None)`. | Task `in_progress`. |
| 2 | Ghi `ref`='DONE'; `evaluate(P, T0 + 4.5h, {'ref'})`. | `stage`='breached'; `end_time`=06:30 UTC; `has_breached`=True; `business_duration`=4.5; events theo `id`: [attach, breach, complete]. |

**Pass/Fail Criteria:** ✅ Pass: `breached`, đủ 3 event. ❌ Fail: `achieved`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-010: Task `paused` 5 ngày làm việc khi còn dư 2 giờ, rồi stop: `achieved`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-04 |
| Coverage Item | CI-2 (R3 (boundary: paused 5 ngày làm việc, còn dư 2 giờ)) |
| Requirement Ref | REQ-FUNC-009 (AC3) |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-VN (FX-DEF-STD với lịch FX-CAL-VN, `duration`=4).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` WORK → HOLD → DONE |  |
| Mốc | T0 (Thứ Hai 03-02 09:00); pause 11:00; stop Thứ Hai 2026-03-09 11:00 | 5 ngày làm việc (Tue–Fri + Mon) |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P `ref`='WORK'; `evaluate(P, T0, None)`. | `planned_end_time`=2026-03-02 06:00 UTC (13:00 VN). |
| 2 | Ghi `ref`='HOLD'; `evaluate(P, 2026-03-02 11:00 VN, {'ref'})`. | `paused`; `business_duration`=2.0; `has_breached`=False. |
| 3 | Ghi `ref`='DONE'; `evaluate(P, 2026-03-09 11:00 VN, {'ref'})`. | `stage`='achieved'; `has_breached`=False; `business_duration`=2.0 (không tăng khi paused); `end_time`=2026-03-09 04:00 UTC; đúng 1 event `complete`. |

**Pass/Fail Criteria:** ✅ Pass: `achieved`, elapsed 2.0. ❌ Fail: `breached` hoặc elapsed tăng.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-011: Stop task `paused` khi dấu vi phạm đã bật: `breached`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-04 |
| Coverage Item | CI-3 (R4) |
| Requirement Ref | REQ-FUNC-009 (Statement (paused + cờ bật)) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` WORK → HOLD → DONE |  |
| Mốc | T0; BG 13:01; pause 13:30; stop 15:00 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; `evaluate(P, T0, None)`; xử lý nền now=13:01. | `has_breached`=True. |
| 2 | Ghi `ref`='HOLD'; `evaluate(P, T0 + 4.5h, {'ref'})`. | `paused`; `business_duration`=4.5. |
| 3 | Ghi `ref`='DONE'; `evaluate(P, T0 + 6h, {'ref'})`. | `stage`='breached'; `end_time`=08:00 UTC; `business_duration`=4.5; 1 event `complete`. |

**Pass/Fail Criteria:** ✅ Pass: `breached`. ❌ Fail: `achieved`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-012: Stop sau khi xử lý nền đã ghi vi phạm: `breached`, không ghi trùng `breach`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-04 |
| Coverage Item | CI-4 (R5) |
| Requirement Ref | REQ-FUNC-009 (Statement (cờ bật, in_progress)) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` WORK → DONE |  |
| Mốc | T0; BG 13:01; stop 13:30 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; `evaluate(P, T0, None)`; xử lý nền now=13:01. | 1 event `breach`. |
| 2 | Ghi `ref`='DONE'; `evaluate(P, T0 + 4.5h, {'ref'})`. | `stage`='breached'; `end_time`=06:30 UTC; số `breach` = 1; số `complete` = 1; tổng event = 3. |

**Pass/Fail Criteria:** ✅ Pass: `breached`, 1 `breach`, 1 `complete`. ❌ Fail: Số `breach` > 1.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-013: Task đã vi phạm rồi pause và resume: dấu vi phạm vẫn bật

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-05 |
| Coverage Item | CI-1 (Cờ bật → resume (negative: cờ không tắt)) |
| Requirement Ref | REQ-FUNC-046 (AC1) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` WORK → HOLD → WORK |  |
| Mốc | T0; BG 13:01; pause 13:30; resume 14:00 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; attach T0; xử lý nền now=13:01. | `has_breached`=True. |
| 2 | Pause tại 13:30 (`ref`='HOLD'); resume tại 14:00 (`ref`='WORK') bằng `evaluate`. | `stage`='in_progress'; `has_breached`=True. |

**Pass/Fail Criteria:** ✅ Pass: `has_breached`=True sau resume. ❌ Fail: Dấu bị tắt.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-014: Đã trôi 4,4 giờ (110%) rồi pause và resume: mốc 120% bắn khi tổng đã trôi đạt 4,8 giờ

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-05 |
| Coverage Item | CI-2 (Đã trôi 4,4 giờ (110%) → pause → resume → mốc 120%) |
| Requirement Ref | REQ-FUNC-046 (AC2) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation). Biến thể: một mốc `percent`=120, server action ghi chú vào chatter.
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` WORK → HOLD → WORK |  |
| Mốc | T0; pause 13:24 (đã trôi 4,4h); resume 15:00 | Chờ 1,6 giờ |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; `evaluate(P, T0, None)`. Ghi `ref`='HOLD'; `evaluate(P, T0 + 4h24m, {'ref'})`. | `paused`; `business_duration`=4.4; `has_breached`=True; 0 event `escalate`. |
| 2 | Ghi `ref`='WORK'; `evaluate(P, T0 + 6h, {'ref'})` (15:00). | `in_progress`; `next_due_at`=2026-03-02 08:24 UTC (15:24 VN). |
| 3 | Xử lý nền với now=15:23. | Số event `escalate` = 0. |
| 4 | Xử lý nền với now=15:24. | Số event `escalate` = 1 (tổng đã trôi 4,4 + 0,4 = 4,8 giờ). |

**Pass/Fail Criteria:** ✅ Pass: Mốc 120% bắn đúng tại 15:24, không sớm hơn. ❌ Fail: Bắn trước 15:24 hoặc không bắn.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-015: Xem phần trăm đã dùng khi đã trôi 1 giờ trên mục tiêu 4 giờ: 25%

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-06 |
| Coverage Item | CI-1 (1 giờ trên 4 giờ) |
| Requirement Ref | REQ-INT-023 (AC1) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='WORK' |  |
| now attach / chốt | T0 / T0 + 1h |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; `evaluate(P, T0, None)`. | Task `in_progress`. |
| 2 | Ghi `ref`='HOLD'; `evaluate(P, T0 + 1h, {'ref'})` để chốt đã trôi; đọc `business_percent_used` của task. | `stage`='paused'; `business_duration`=1.0; `business_percent_used` = 25. |
| 3 | Ví dụ chạy trực tiếp (không pause): partner P2 mới (`ref`='WORK'), `evaluate(P2, T0, None)`; patch `odoo.fields.Datetime.now` lần lượt T0 + 1h rồi T0 + 5h, invalidate cache và đọc `business_percent_used`, `business_duration` của task. | Task `in_progress`; `business_percent_used` = 25 tại T0 + 1h và = 125 tại T0 + 5h (gồm đoạn đang chạy từ `running_since`); `business_duration` vẫn = 0.0 (chưa chốt). Khớp `tests/test_tg03_more.py::test_bre_017b_running_percent_live`. |

**Ghi chú:** `business_percent_used` KHÔNG lưu: giá trị tính khi đọc từ `business_duration` và `target_duration`, và với task `in_progress` còn cộng đoạn đang chạy từ `running_since` tới thời điểm xem (TA-22 ĐÃ CHỐT; code đổi 2026-10-12, `sla.time.settle_batch`). Ca vẫn pause trước để có số cố định, vì đoạn đang chạy phụ thuộc đồng hồ lúc đọc.

**Pass/Fail Criteria:** ✅ Pass: Giá trị = 25. ❌ Fail: Giá trị khác 25.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-016: Xem phần trăm khi đã trôi 5 giờ trên mục tiêu 4 giờ: 125% (cho phép vượt 100%)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-06 |
| Coverage Item | CI-2 (Vượt mục tiêu (5 giờ trên 4 giờ) (boundary)) |
| Requirement Ref | REQ-INT-023 (AC2) |
| Priority | P3-Medium |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='WORK' |  |
| now xem | T0 + 5h (14:00) | Không chạy xử lý nền |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; `evaluate(P, T0, None)`. Ghi `ref`='HOLD'; `evaluate(P, T0 + 5h, {'ref'})`; đọc `business_percent_used`. | `business_duration`=5.0; `business_percent_used` = 125 (không bị cắt ở 100). |

**Ghi chú:** `business_percent_used` KHÔNG lưu: giá trị tính khi đọc từ `business_duration` và `target_duration`, và với task `in_progress` còn cộng đoạn đang chạy từ `running_since` tới thời điểm xem (TA-22 ĐÃ CHỐT; code đổi 2026-10-12, `sla.time.settle_batch`). Ca vẫn pause trước để có số cố định, vì đoạn đang chạy phụ thuộc đồng hồ lúc đọc.

**Pass/Fail Criteria:** ✅ Pass: `business_percent_used` = 125. ❌ Fail: `business_percent_used` ≠ 125.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-017: Task `paused` xem hai lần cách nhau 2 giờ làm việc: phần trăm không đổi (25%)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-06 |
| Coverage Item | CI-3 (Task `paused`, xem hai lần cách nhau 2 giờ làm việc (negative)) |
| Requirement Ref | REQ-INT-023 (AC3) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-VN (FX-DEF-STD với lịch FX-CAL-VN, `duration`=4).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref` WORK → HOLD |  |
| Mốc | T0; pause 10:00; xem 11:00 và 13:00 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; attach T0; ghi `ref`='HOLD'; `evaluate(P, T0 + 1h, {'ref'})`. | `paused`; `business_duration`=1.0. |
| 2 | Với patch `odoo.fields.Datetime.now` trả 11:00: `invalidate_recordset()` rồi đọc `business_percent_used`. | 25. |
| 3 | Patch `odoo.fields.Datetime.now` trả 13:00 (cách 2 giờ làm việc); `invalidate_recordset()` rồi đọc `business_percent_used` và `business_duration`. | `business_percent_used` = 25 (không đổi); `business_duration` = 1.0. |

**Pass/Fail Criteria:** ✅ Pass: hai lần đọc đều `business_percent_used` = 25 và `business_duration` = 1.0. ❌ Fail: giá trị lần hai ≠ 25.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-018: Làm tròn xuống: đã trôi 1h59m trên 4 giờ (49,58%) hiển thị 49%

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-06 |
| Coverage Item | CI-4 (Làm tròn xuống: 1h59m trên 4 giờ (49,58%)) |
| Requirement Ref | REQ-INT-023 (Statement (làm tròn xuống)) |
| Priority | P3-Medium |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='WORK' |  |
| now xem | T0 + 1h59m (10:59) |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; attach T0. Ghi `ref`='HOLD'; `evaluate(P, now=10:59, {'ref'})`; đọc `business_percent_used`. | `stage`='paused'; `business_percent_used` = 49. |

**Ghi chú:** `business_percent_used` KHÔNG lưu: giá trị tính khi đọc từ `business_duration` và `target_duration`, và với task `in_progress` còn cộng đoạn đang chạy từ `running_since` tới thời điểm xem (TA-22 ĐÃ CHỐT; code đổi 2026-10-12, `sla.time.settle_batch`). Ca vẫn pause trước để có số cố định, vì đoạn đang chạy phụ thuộc đồng hồ lúc đọc.

**Pass/Fail Criteria:** ✅ Pass: `business_percent_used` = 49. ❌ Fail: `business_percent_used` = 50.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-019: Ngay dưới biên 100%: đã trôi 3h59m trên 4 giờ hiển thị 99%

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-06 |
| Coverage Item | CI-5 (Ngay dưới biên: 3h59m (99,58%)) |
| Requirement Ref | REQ-INT-023 (BVA 99%) |
| Priority | P3-Medium |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='WORK' |  |
| now xem | T0 + 3h59m (12:59) |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; attach T0. Ghi `ref`='HOLD'; `evaluate(P, now=12:59, {'ref'})`; đọc `business_percent_used`. | `stage`='paused'; `business_percent_used` = 99. |

**Ghi chú:** `business_percent_used` KHÔNG lưu: giá trị tính khi đọc từ `business_duration` và `target_duration`, và với task `in_progress` còn cộng đoạn đang chạy từ `running_since` tới thời điểm xem (TA-22 ĐÃ CHỐT; code đổi 2026-10-12, `sla.time.settle_batch`). Ca vẫn pause trước để có số cố định, vì đoạn đang chạy phụ thuộc đồng hồ lúc đọc.

**Pass/Fail Criteria:** ✅ Pass: `business_percent_used` = 99. ❌ Fail: `business_percent_used` ≠ 99.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-020: Đúng biên: đã trôi 4 giờ trên 4 giờ hiển thị 100%

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-06 |
| Coverage Item | CI-6 (Đúng biên: 4h) |
| Requirement Ref | REQ-INT-023 (BVA 100%) |
| Priority | P3-Medium |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='WORK' |  |
| now xem | T0 + 4h (13:00) |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; attach T0. Ghi `ref`='HOLD'; `evaluate(P, now=13:00, {'ref'})`; đọc `business_percent_used`. | `stage`='paused'; `business_percent_used` = 100. |

**Ghi chú:** `business_percent_used` KHÔNG lưu: giá trị tính khi đọc từ `business_duration` và `target_duration`, và với task `in_progress` còn cộng đoạn đang chạy từ `running_since` tới thời điểm xem (TA-22 ĐÃ CHỐT; code đổi 2026-10-12, `sla.time.settle_batch`). Ca vẫn pause trước để có số cố định, vì đoạn đang chạy phụ thuộc đồng hồ lúc đọc.

**Pass/Fail Criteria:** ✅ Pass: `business_percent_used` = 100. ❌ Fail: `business_percent_used` ≠ 100.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-021: Vừa attach (đã trôi 0 giờ): phần trăm = 0%

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-06 |
| Coverage Item | CI-7 (Biên dưới: vừa attach (0h)) |
| Requirement Ref | REQ-INT-023 (BVA 0%) |
| Priority | P4-Low |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation).
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='WORK' |  |
| now xem | T0 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; attach T0. Đọc `business_percent_used` ngay sau attach (task `in_progress`, `business_duration`=0). | `business_percent_used` = 0. |

**Pass/Fail Criteria:** ✅ Pass: `business_percent_used` = 0. ❌ Fail: `business_percent_used` ≠ 0.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-022: Server action của mốc 100% ném lỗi, retry tắt: event `escalate_failed` có ghi chú chứa thông báo lỗi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-07 |
| Coverage Item | CI-1 (Server action lỗi, retry tắt) |
| Requirement Ref | REQ-FUNC-029 (AC3 (cross-ref TG-08)) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (start `ref`∈{NEW,WORK,HOLD}; pause `ref`=HOLD; resume `ref`=WORK; stop `ref`=DONE; cancel `ref`=CANCEL; reset rỗng; `duration`=4; lịch 24x7; cancel_mode `start_unmatched`; resume_mode `condition`; không escalation). Một mốc `percent`=100, `retry`=False, server action chạy `raise UserError('boom: gateway down')`.
2. Chưa có `sla.task` và `sla.event` nào cho partner thử (partner tạo mới trong ca).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner | `ref`='WORK' |  |
| now xử lý nền | T0 + 4h01m (13:01) |  |
| Thông báo lỗi | boom: gateway down |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P; `evaluate(P, T0, None)`. Xử lý nền now=13:01. | Có 1 event `breach`; 1 event `escalate_failed`; 0 event `escalate`. |
| 2 | Đọc `note` của event `escalate_failed`. | `note` không rỗng và chứa chuỗi `boom: gateway down`. |

**Pass/Fail Criteria:** ✅ Pass: `note` chứa thông báo lỗi. ❌ Fail: `note` rỗng hoặc thiếu thông báo.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-BRE-023: Ràng buộc CSDL chéo trên task: `breached` kéo theo dấu vi phạm, `achieved` không có dấu vi phạm, `end_time` và `next_due_at` theo stage

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-03-05 |
| Coverage Item | CI-3 (CHECK chéo của `sla_task`: dấu vi phạm và stage nhất quán, 030 mục 5) |
| Requirement Ref | REQ-FUNC-046 (Statement: dấu vi phạm không tắt; nhất quán với REQ-FUNC-009) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; FX-DEF-STD đang active trên `res.partner` (4 giờ, 24x7).
2. Partner P (`ref`='NEW') với task T1 `in_progress` (`has_breached` = False) tạo bằng `evaluate(P, now = T0)`; partner Q (`ref`='NEW') với task T2 `paused` (`ref`='HOLD', `has_breached` = False); mỗi bước ghi SQL chạy trong savepoint riêng và được rollback.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| T1 | `in_progress`, `has_breached` = False |  |
| T2 | `paused` |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Savepoint: `UPDATE sla_task SET stage='breached', end_time=now(), running_since=NULL, next_due_at=NULL WHERE id = T1` (không bật `has_breached`) | Bị từ chối bởi `sla_task_breached_check` (CheckViolation/IntegrityError) |
| 2 | Savepoint: `UPDATE sla_task SET stage='achieved', has_breached=true, end_time=now(), running_since=NULL, next_due_at=NULL WHERE id = T1` | Bị từ chối bởi `sla_task_achieved_check` |
| 3 | Savepoint: `UPDATE sla_task SET stage='cancelled', running_since=NULL, next_due_at=NULL WHERE id = T1` (thiếu `end_time`) | Bị từ chối bởi `sla_task_end_dt_check` |
| 4 | Savepoint: `UPDATE sla_task SET next_due_at=now() WHERE id = T2` (task `paused` có mốc xử lý nền) | Bị từ chối bởi `sla_task_next_due_at_check` |
| 5 | Đọc lại T1 và T2 sau các bước | T1 `in_progress`, `has_breached` = False; T2 `paused`; không đổi |

**Pass/Fail Criteria:** ✅ Pass: cả 4 lệnh ghi sai bị CSDL từ chối đúng ràng buộc và task không đổi; ❌ Fail: có lệnh được chấp nhận hoặc bị từ chối bởi ràng buộc khác

**Ghi chú:** Ca thêm theo 099 mục 3 (bảng CHECK mới của Database Design 0.2, mục 5). Chỉ kiểm bốn ràng buộc chéo tiêu biểu liên quan REQ-FUNC-046/009; các CHECK đơn giản còn lại (`stage`, giá trị không âm) không có ca riêng.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

## TG-04 — Cancel và reset (kể cả reset theo field)

### TC-CAN-001: Kết thúc task theo stop khi stop và pause cùng khớp, không ghi event pause

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-01 |
| Coverage Item | CI-1 (stop khớp + pause khớp -> kết thúc theo stop) |
| Requirement Ref | REQ-FUNC-008 (AC1) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: pause = `[('ref','in',['HOLD','DONE'])]`; start = `ref ∈ {NEW,WORK,HOLD,DONE}`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào; task `in_progress` được gắn bằng bước 1

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | DONE | stop và pause cùng khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress`, `start_time`=09:00, 1 event `attach` |
| 2 | Đặt `ref`='DONE' (không qua hook, G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Task `stage`='achieved', `end_time`=2026-03-02 10:00 ICT |
| 3 | Đếm event của task theo loại | `complete`=1, `pause`=0, tổng event = 2 (`attach`,`complete`) |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Task `achieved` và không có event `pause`. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-002: Kết thúc task theo stop khi stop và cancel (chế độ condition) cùng khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-01 |
| Coverage Item | CI-2 (stop khớp + cancel khớp -> stop thắng) |
| Requirement Ref | REQ-FUNC-008 (mục 1 trước mục 2) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: cancel_mode=`condition`; cancel = `[('ref','in',['CANCEL','DONE'])]`; start = `ref ∈ {NEW,WORK,HOLD,DONE}`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | DONE | stop và cancel cùng khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Đặt `ref`='DONE' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Task `stage`='achieved' |
| 3 | Đếm event theo loại | `complete`=1, `cancel`=0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Task `achieved`, không có event `cancel`. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-003: Hủy task khi chế độ condition, cancel và pause cùng khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-01 |
| Coverage Item | CI-3 (cancel (condition) khớp + pause khớp -> cancelled) |
| Requirement Ref | REQ-FUNC-008 (AC2) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: cancel_mode=`condition`; cancel = `[('ref','=','HOLD')]` (cùng giá trị với pause)
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | HOLD | cancel và pause cùng khớp, start vẫn khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Đặt `ref`='HOLD' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Task `stage`='cancelled', `end_time`=10:00 |
| 3 | Đếm event theo loại | `cancel`=1, `pause`=0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Task `cancelled`, không có event `pause`. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-004: Áp dụng reset khi reset, start và pause cùng khớp; task cũ không có event pause

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-01 |
| Coverage Item | CI-4 (reset + start + pause cùng khớp -> reset thắng pause) |
| Requirement Ref | REQ-FUNC-008 (AC3) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; pause = `ref ∈ {HOLD,RESET}`; reset = `[('ref','=','RESET')]`; reset_action=`cancel`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | RESET | reset, start, pause cùng khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (T-old) |
| 2 | Đặt `ref`='RESET' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | T-old `stage`='cancelled'; có task mới T-new |
| 3 | Đếm event của T-old theo loại | `reset`=1, `cancel`=1 (thứ tự id: `cancel` rồi `reset`; TA-03 ĐÃ CHỐT), `pause`=0 |
| 4 | Đọc `stage` của T-new | 'paused' (reset/start/pause cùng khớp, REQ-FUNC-012 AC3) |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; T-old không có event `pause`, có event `reset`; T-new tồn tại. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-005: Giữ nguyên task và không ghi event mới khi không điều kiện nào khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-01 |
| Coverage Item | CI-5 (không điều kiện nào khớp -> không đổi) |
| Requirement Ref | REQ-FUNC-008 (AC4) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition) (không đổi)
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| field ghi bước 2 | `comment`='ghi chú' (field không liên quan) | stop, cancel, pause, reset, resume đều không khớp; start vẫn khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (ghi `id`=T1), 1 event `attach` |
| 2 | Ghi `comment` (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {comment} (`evaluate(records, now, changed)`, TAD 5.1) | Không ngoại lệ |
| 3 | Đọc lại task T1 và đếm event | T1 `stage`='in_progress', số task = 1, tổng event = 1 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Không có task hoặc event mới, `stage` không đổi. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-006: Hủy task thay vì reset khi cancel (condition), reset và start cùng khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-01 |
| Coverage Item | CI-6 (cancel (condition) khớp + reset khớp -> cancel thắng reset) |
| Requirement Ref | REQ-FUNC-008 (mục 2 trước mục 3) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: cancel_mode=`condition`; cancel = `[('ref','=','RESET')]`; reset = `[('ref','=','RESET')]`; start = `ref ∈ {NEW,WORK,HOLD,RESET}`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | RESET | cancel, reset, start cùng khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Đặt `ref`='RESET' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Task `stage`='cancelled' |
| 3 | Đếm task và event theo loại | Tổng số task = 1 (không có task mới), `cancel`=1, `reset`=0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Task `cancelled`, không có task mới, không có event `reset`. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-007: Hủy task khi chế độ start_unmatched và start hết khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-02 |
| Coverage Item | CI-1 (start_unmatched: start hết khớp -> cancelled) |
| Requirement Ref | REQ-FUNC-010 (AC1) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition) (cancel_mode=`start_unmatched`)
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | OTHER | start không còn khớp; cancel không khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Đặt `ref`='OTHER' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Task `stage`='cancelled' |
| 3 | Đọc `end_time` và đếm event `cancel` | `end_time`=2026-03-02 10:00 ICT (03:00 UTC), `cancel`=1 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Task `cancelled`, `end_time` có giá trị, đúng 1 event `cancel`. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-008: Hủy task khi chế độ condition và cancel khớp trong lúc start vẫn khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-02 |
| Coverage Item | CI-2 (condition: cancel khớp -> cancelled) |
| Requirement Ref | REQ-FUNC-010 (AC2) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: cancel_mode=`condition`; cancel = `[('ref','=','WORK')]`; pause = `[('ref','=','HOLD')]`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | WORK | cancel khớp, start vẫn khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Đặt `ref`='WORK' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Task `stage`='cancelled', `end_time`=10:00 |
| 3 | Đếm event `cancel` | 1 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Task `cancelled` dù start vẫn khớp. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-009: Không hủy task khi chế độ never, start hết khớp và cancel khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-02 |
| Coverage Item | CI-3 (never: start hết khớp và cancel khớp -> không hủy) |
| Requirement Ref | REQ-FUNC-010 (AC3) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: cancel_mode=`never`; cancel = `[('ref','=','CANCEL')]`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | CANCEL | start hết khớp và cancel khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Đặt `ref`='CANCEL' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Task `stage`='in_progress' |
| 3 | Đọc `end_time` và đếm event `cancel` | `end_time` rỗng, `cancel`=0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Task vẫn `in_progress`, không event `cancel`. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-010: Không hủy task khi chế độ condition, start hết khớp nhưng cancel không khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-02 |
| Coverage Item | CI-4 (condition: start hết khớp nhưng cancel chưa khớp -> không hủy) |
| Requirement Ref | REQ-FUNC-010 (EP: condition, cancel không khớp) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: cancel_mode=`condition`; cancel = `[('ref','=','CANCEL')]`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | OTHER | start hết khớp; cancel không khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Đặt `ref`='OTHER' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Task `stage`='in_progress' |
| 3 | Đếm event `cancel` | 0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Task không bị hủy vì chế độ condition chỉ xét cancel. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-011: Không hủy task khi chế độ start_unmatched, cancel khớp nhưng start vẫn khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-02 |
| Coverage Item | CI-5 (start_unmatched: cancel khớp nhưng start vẫn khớp -> không hủy) |
| Requirement Ref | REQ-FUNC-010 (EP: start_unmatched bỏ qua domain cancel) (theo code `sla_engine._cancel_matches`) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: cancel = `[('ref','=','WORK')]` (start vẫn gồm WORK); cancel_mode=`start_unmatched`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | WORK | cancel khớp, start khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Đặt `ref`='WORK' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Task `stage`='in_progress' |
| 3 | Đếm event `cancel` | 0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Task không bị hủy; domain cancel không có tác dụng ở chế độ start_unmatched. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-012: Reset hủy task cũ và gắn task mới in_progress khi reset_action là cancel

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-03 |
| Coverage Item | CI-1 (reset_action=cancel, task in_progress) |
| Requirement Ref | REQ-FUNC-012 (AC1) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[('ref','=','RESET')]`; reset_action=`cancel`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | RESET | reset và start cùng khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (T-old), `planned_end_time`=13:00 |
| 2 | Đặt `ref`='RESET' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | T-old `stage`='cancelled', `end_time`=10:00 |
| 3 | Đọc task mới T-new | `stage`='in_progress', `start_time`=10:00, `planned_end_time`=14:00 |
| 4 | Đọc event của T-old theo thứ tự id | Đúng 1 event `reset`, đứng sau event `cancel` (code ghi `cancel` rồi `reset`; TA-03 ĐÃ CHỐT); T-old không có event `pause` |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; T-old `cancelled`, T-new `in_progress`, 1 event `reset`. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-013: Reset kết thúc task cũ achieved khi reset_action là complete và chưa quá hạn

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-03 |
| Coverage Item | CI-2 (reset_action=complete, chưa quá hạn -> achieved) |
| Requirement Ref | REQ-FUNC-012 (AC2) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[('ref','=','RESET')]`; reset_action=`complete`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | RESET |  |
| now bước 2 | T0+1h = 10:00 (trước `planned_end_time`=13:00) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (T-old) |
| 2 | Đặt `ref`='RESET' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | T-old `stage`='achieved', `end_time`=10:00; event của T-old theo thứ tự id có `complete` rồi `reset` (TA-03 ĐÃ CHỐT) |
| 3 | Đọc task mới | `stage`='in_progress', `start_time`=10:00 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; T-old `achieved`, task mới `in_progress`. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-014: Gắn task mới ở trạng thái paused khi reset và pause cùng khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-03 |
| Coverage Item | CI-3 (reset + pause cùng khớp -> task mới paused) |
| Requirement Ref | REQ-FUNC-012 (AC3) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[('ref','=','RESET')]`; pause = `ref ∈ {HOLD,RESET}`; reset_action=`complete`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | RESET | reset, start, pause cùng khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (T-old) |
| 2 | Đặt `ref`='RESET' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | T-old `stage`='achieved' |
| 3 | Đọc task mới | `stage`='paused' |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Task mới `paused`. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-015: Không đổi gì khi task gần nhất đã achieved dù reset và start cùng khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-03 |
| Coverage Item | CI-4 (task gần nhất achieved -> reset không áp dụng) |
| Requirement Ref | REQ-FUNC-012 (AC4); REQ-FUNC-007 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[('ref','=','RESET')]`; reset_action=`cancel`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào; sau bước 1 task `in_progress` rồi kết thúc `achieved` ở bước 2

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref bước 2 | DONE | stop khớp |
| ref bước 3 | RESET | reset và start khớp, stop không khớp |
| now bước 3 | T0+2h = 11:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Đặt `ref`='DONE' (G1) (start gồm DONE do stop thắng ở mục 1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Task `achieved`, `end_time`=10:00; 2 event (`attach`,`complete`) |
| 3 | Đặt `ref`='RESET' (G1); Gọi Engine đánh giá `P-01` với now = T0+2h (11:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Không ngoại lệ |
| 4 | Đọc tất cả task và event của `P-01` | Số task = 1, `stage`='achieved', số event vẫn = 2, `reset`=0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Không có task mới, task `achieved` bất biến, không event mới. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-016: Reset khớp nhưng start không khớp (cancel_mode never): nhánh reset không vào, task cũ giữ nguyên và không có task mới

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-03 |
| Coverage Item | CI-5 (reset khớp nhưng start không khớp: nhánh reset chỉ vào khi reset VÀ start cùng khớp, FUNC-008) |
| Requirement Ref | REQ-FUNC-012 (AC5, đang được SRS viết lại cho khớp FUNC-008), REQ-FUNC-008 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` đổi: reset = `[('ref','=','RESET')]` (start KHÔNG gồm RESET); reset_action=`cancel`; cancel_mode=`never` (để cô lập nhánh reset, không để quy tắc cancel `start_unmatched` đóng task).
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | RESET | reset khớp, start không khớp, pause không khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`) | 1 task `in_progress` (T-old), 1 event `attach` |
| 2 | Đặt `ref`='RESET' (G1); gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} | Không ném lỗi; T-old vẫn `stage`='in_progress', `end_time` rỗng |
| 3 | Đếm task và event của `P-01` | Tổng số task = 1; số event vẫn = 1 (`attach`); `reset`=0, `cancel`=0 |

**Pass/Fail Criteria:** ✅ Pass: T-old giữ `in_progress`, không có task mới, không có event `reset` hay `cancel`; ❌ Fail: T-old bị đóng hoặc có task mới

**Ghi chú:** Quyết định đã chốt (giữ code theo FUNC-008): AC5 của REQ-FUNC-012 ("reset khớp mà start không khớp thì kết thúc task cũ theo reset_action, không gắn task mới") mâu thuẫn với bảng ưu tiên FUNC-008 (nhánh reset chỉ vào khi reset VÀ start cùng khớp). Code theo FUNC-008; SRS REQ-FUNC-012 AC5 đang được viết lại cho khớp FUNC-008 (TA-26 ĐÃ CHỐT); TC này là ca chuẩn cho AC5 mới. Với cancel_mode=`start_unmatched` (mặc định) task cũ bị đóng bởi quy tắc cancel (event `cancel`, không có `reset`), xem TC-CAN-007.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CAN-017: Reset task đang paused: hủy task cũ và gắn task mới in_progress

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-03 |
| Coverage Item | CI-6 (reset áp dụng cho task paused) |
| Requirement Ref | REQ-FUNC-012 (Statement: cả in_progress và paused) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[('ref','=','RESET')]`; reset_action=`cancel`
2. Partner `P-01` tạo với `ref`='HOLD' tại FX-T0 (task đầu gắn ở `paused`)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | RESET | reset, start khớp; pause (ref=HOLD) không khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `paused` (T-old) |
| 2 | Đặt `ref`='RESET' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | T-old `stage`='cancelled' |
| 3 | Đọc task mới | `stage`='in_progress', `start_time`=10:00 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Reset hoạt động trên task `paused`. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-018: Reset kết thúc task cũ breached khi reset_action là complete và đã quá planned_end_time

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-03 |
| Coverage Item | CI-7 (reset_action=complete, quá hạn -> breached) |
| Requirement Ref | REQ-FUNC-012 (AC2); REQ-FUNC-009 |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[('ref','=','RESET')]`; reset_action=`complete`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào (task gắn ở T0, `planned_end_time`=13:00)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | RESET |  |
| now bước 2 | T0+5h = 14:00 (quá `planned_end_time` 1 giờ, chưa có xử lý nền) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress`, `planned_end_time`=13:00 |
| 2 | Đặt `ref`='RESET' (G1); Gọi Engine đánh giá `P-01` với now = T0+5h (14:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | T-old `stage`='breached', `end_time`=14:00; event của T-old theo thứ tự id có `complete` rồi `reset` (TA-03 ĐÃ CHỐT) |
| 3 | Đọc task mới | `stage`='in_progress', `start_time`=14:00, `planned_end_time`=18:00 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; T-old `breached`, task mới `in_progress`. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-019: Gắn task mới qua attach (không reset) khi task gần nhất cancelled và reset, start cùng khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-03 |
| Coverage Item | CI-8 (task gần nhất cancelled: reset không áp dụng, gắn lại theo attach) |
| Requirement Ref | REQ-FUNC-012 (Statement: không áp dụng cho cancelled); REQ-FUNC-007 (AC3) (task gắn lại sau `cancelled` ghi event `attach`) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[('ref','=','RESET')]`; cancel_mode=`condition`; cancel = `[('ref','=','CANCEL')]`; start gồm cả CANCEL; reset_action=`cancel`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref bước 2 | CANCEL | cancel khớp |
| ref bước 3 | RESET | reset và start khớp, cancel không khớp |
| now bước 3 | T0+2h = 11:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (T1) |
| 2 | Đặt `ref`='CANCEL' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | T1 `stage`='cancelled' |
| 3 | Đặt `ref`='RESET' (G1); Gọi Engine đánh giá `P-01` với now = T0+2h (11:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Có task mới T2 `in_progress`, `start_time`=11:00 |
| 4 | Đếm event theo loại trên cả hai task | `reset`=0; `attach`=2 (1 cho mỗi task) |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; T2 được gắn bằng attach; không có event `reset`. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-020: Reset khi field theo dõi user_id đổi sang giá trị khác và reset là domain luôn đúng `[('id', '!=', 0)]`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-04 |
| Coverage Item | CI-1 (field theo dõi đổi giá trị -> reset) |
| Requirement Ref | REQ-FUNC-013 (AC1) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[]`; reset_field_ids = {user_id}; reset_action=`cancel`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào với `user_id`=`U-USR` (field giá trị ban đầu khác rỗng)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| user_id (bước 2) | `U-USR` -> `U-MGR` |  |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (T-old) |
| 2 | Ghi `user_id`=`U-MGR` (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {user_id} (`evaluate(records, now, changed)`, TAD 5.1) | T-old `stage`='cancelled'; task mới `in_progress`, `start_time`=10:00 |
| 3 | Đếm event `reset` của T-old | 1 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Có reset đúng 1 lần. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-021: Không reset khi hai field theo dõi giữ nguyên giá trị sau lần ghi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-04 |
| Coverage Item | CI-2 (field theo dõi giữ nguyên giá trị -> không reset) |
| Requirement Ref | REQ-FUNC-013 (AC2) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[]`; reset_field_ids = {user_id, comment}; reset_action=`cancel`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào với `user_id`=`U-USR` (field giá trị ban đầu khác rỗng) và `comment`='A'

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ghi bước 2 | `user_id`=`U-USR`, `comment`='A' (giữ nguyên) |  |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (T1) |
| 2 | Ghi lại đúng giá trị cũ (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = ∅ (hook không tính field nào đổi) (`evaluate(records, now, changed)`, TAD 5.1) | Không ngoại lệ |
| 3 | Đọc task và event | Số task = 1, T1 `in_progress`, `reset`=0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Không reset. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-022: Reset khi field theo dõi là compute có lưu và giá trị đổi do tính lại

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-04 |
| Coverage Item | CI-3 (field compute có lưu đổi do tính lại -> reset) |
| Requirement Ref | REQ-FUNC-013 (AC3) [G5] |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[]`; reset_field_ids = {complete_name}; reset_action=`cancel`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào với `user_id`=`U-USR` (field giá trị ban đầu khác rỗng); `complete_name`='P-01' (compute có lưu phụ thuộc `name`)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ghi bước 2 | `name`='P-01-X' -> `complete_name`='P-01-X' do tính lại |  |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (T-old) |
| 2 | Ghi `name`='P-01-X' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {complete_name} (`evaluate(records, now, changed)`, TAD 5.1) | T-old `stage`='cancelled'; task mới `in_progress` |
| 3 | Đếm event `reset` | 1 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Reset xảy ra khi giá trị compute có lưu đổi. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-023: Không reset khi field theo dõi đổi nhưng điều kiện reset không khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-04 |
| Coverage Item | CI-4 (field theo dõi đổi nhưng điều kiện reset không khớp -> không reset) |
| Requirement Ref | REQ-FUNC-013 (Statement: điều kiện reset khớp VÀ field đổi) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: reset = `[('ref','=','RESET')]`; reset_field_ids = {user_id}; reset_action=`cancel`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào với `user_id`=`U-USR` (field giá trị ban đầu khác rỗng)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| user_id (bước 2) | `U-USR` -> `U-MGR` | `ref` vẫn 'NEW' nên reset domain không khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (T1) |
| 2 | Ghi `user_id`=`U-MGR` (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {user_id} (`evaluate(records, now, changed)`, TAD 5.1) | Không ngoại lệ |
| 3 | Đọc task và event | Số task = 1, T1 `in_progress`, `reset`=0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Không reset vì điều kiện reset không khớp. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-024: Reset khi chỉ một trong hai field theo dõi đổi giá trị

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-04 |
| Coverage Item | CI-5 (danh sách nhiều field, chỉ một field đổi -> reset) |
| Requirement Ref | REQ-FUNC-013 (Statement: ít nhất một field) |
| Priority | P3-Medium |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[]`; reset_field_ids = {user_id, comment}; reset_action=`cancel`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào với `user_id`=`U-USR` (field giá trị ban đầu khác rỗng) và `comment`='A'

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ghi bước 2 | `user_id`=`U-USR` (giữ), `comment`='B' (đổi) |  |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (T-old) |
| 2 | Ghi `comment`='B' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {comment} (`evaluate(records, now, changed)`, TAD 5.1) | T-old `stage`='cancelled'; task mới `in_progress` |
| 3 | Đếm event `reset` | 1 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Reset xảy ra dù chỉ một field đổi. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-025: Không reset khi ghi field theo dõi bằng đúng giá trị cũ

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-05 |
| Coverage Item | CI-1 (ghi field theo dõi bằng đúng giá trị cũ -> không reset) |
| Requirement Ref | REQ-FUNC-050 (AC1) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[]`; reset_field_ids = {user_id}; reset_action=`cancel`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào với `user_id` rỗng (giá trị cũ = rỗng)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ghi bước 2 | `user_id`=False (giữ rỗng) |  |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (T1) |
| 2 | Ghi `user_id`=False (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = ∅ (`evaluate(records, now, changed)`, TAD 5.1) | Không ngoại lệ |
| 3 | Đọc task và event | Số task = 1, T1 `in_progress`, `reset`=0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Không reset. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-026: Không reset khi chỉ ghi field không nằm trong danh sách theo dõi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-05 |
| Coverage Item | CI-2 (chỉ ghi field khác -> không reset) |
| Requirement Ref | REQ-FUNC-050 (AC2) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[]`; reset_field_ids = {user_id}; reset_action=`cancel`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào với `user_id`=`U-USR` (field giá trị ban đầu khác rỗng)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ghi bước 2 | `phone`='0901234567' (field khác) |  |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (T1) |
| 2 | Ghi `phone` (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {phone} (`evaluate(records, now, changed)`, TAD 5.1) | Không ngoại lệ |
| 3 | Đọc task và event | Số task = 1, T1 `in_progress`, `reset`=0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Không reset. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-027: Không reset khi SLA Manager đánh giá lại thủ công

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-05 |
| Coverage Item | CI-3 (Đánh giá lại thủ công -> không reset) |
| Requirement Ref | REQ-FUNC-050 (AC3) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[]`; reset_field_ids = {user_id}; reset_action=`cancel`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào với `user_id`=`U-USR` (field giá trị ban đầu khác rỗng); người thực hiện `U-MGR`

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| now | T0+1h = 10:00 | đánh giá lại thủ công qua engine dùng changed rỗng (TAD: changed rỗng) |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (T1) |
| 2 | Với quyền `U-MGR`, thực hiện đánh giá lại thủ công (hàm `Engine.evaluate`, không phải nút trên task vì `P-01` chưa có task) trên `P-01` (đường gọi: Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = ∅ (`evaluate(records, now, changed)`, TAD 5.1)) | Không ngoại lệ |
| 3 | Đọc task và event | Số task = 1, T1 `in_progress` (cùng `id`), `reset`=0, tổng event = 1 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Không reset. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-028: Không reset khi xử lý nền chạy

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-05 |
| Coverage Item | CI-4 (xử lý nền theo thời gian -> không reset) |
| Requirement Ref | REQ-FUNC-050 (AC4) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[]`; reset_field_ids = {user_id}; reset_action=`cancel`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào với `user_id`=`U-USR` (field giá trị ban đầu khác rỗng)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| now | T0+2h = 11:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (T1) |
| 2 | Xử lý nền tại now = T0+2h (11:00) (`_process_task`; không dùng `sleep`) | Không ngoại lệ |
| 3 | Đọc task và event | Số task = 1, T1 `in_progress` (cùng `id`), `reset`=0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Không reset. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-029: Không reset khi điều kiện reset rỗng dù field theo dõi đổi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-06 |
| Coverage Item | CI-1 (điều kiện reset rỗng + có field theo dõi -> không reset) |
| Requirement Ref | REQ-FUNC-051 (AC1) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: reset_domain rỗng (chưa cấu hình); reset_field_ids = {user_id}
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào với `user_id`=`U-USR` (field giá trị ban đầu khác rỗng)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| user_id (bước 2) | `U-USR` -> `U-MGR` |  |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (T1) |
| 2 | Ghi `user_id`=`U-MGR` (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {user_id} (`evaluate(records, now, changed)`, TAD 5.1) | Không ngoại lệ |
| 3 | Đọc task và event | Số task = 1, T1 `in_progress`, `reset`=0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Không reset. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-030: Ghi tên field user_id vào ghi chú event reset

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-06 |
| Coverage Item | CI-2 (reset domain luôn đúng + field theo dõi đổi -> ghi chú event reset chứa tên field) |
| Requirement Ref | REQ-FUNC-051 (AC2) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[]`; reset_field_ids = {user_id}; reset_action=`cancel`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào với `user_id`=`U-USR` (field giá trị ban đầu khác rỗng)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| user_id (bước 2) | `U-USR` -> `U-MGR` |  |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (T-old) |
| 2 | Ghi `user_id`=`U-MGR` (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {user_id} (`evaluate(records, now, changed)`, TAD 5.1) | Reset xảy ra |
| 3 | Đọc `note` của event `reset` | Chứa chuỗi `user_id` |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; `note` của event `reset` chứa `user_id`. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-031: Ghi tên cả hai field user_id và comment vào ghi chú event reset

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-06 |
| Coverage Item | CI-3 (hai field đổi -> ghi chú chứa cả hai tên) |
| Requirement Ref | REQ-FUNC-051 (Statement: tên các field đã đổi) |
| Priority | P4-Low |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[]`; reset_field_ids = {user_id, comment}; reset_action=`cancel`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào với `user_id`=`U-USR` (field giá trị ban đầu khác rỗng) và `comment`='A'

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ghi bước 2 | `user_id`=`U-MGR`, `comment`='B' trong cùng một lần ghi |  |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Ghi hai field (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {user_id, comment} (`evaluate(records, now, changed)`, TAD 5.1) | Reset xảy ra |
| 3 | Đọc `note` của event `reset` | Chứa cả `user_id` và `comment` |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; `note` chứa đủ cả hai tên field. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-CAN-032: Reset và attach lại sau cancelled: ghi task cũ rồi mới tạo task mới, không vi phạm chỉ mục duy nhất và không có event `error`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-04-03 |
| Coverage Item | CI-9 (flush task cũ trước khi create task mới: không vi phạm `sla_task_one_active_uniq`) |
| Requirement Ref | REQ-FUNC-012 (AC1; gắn lại sau cancelled theo REQ-FUNC-007) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` đổi: start = `ref ∈ {NEW,WORK,HOLD,RESET}`; reset = `[('ref','=','RESET')]`; reset_action=`cancel`; cancel_mode=`start_unmatched` (mục tiêu 4 giờ, 24x7).
2. Partner `P-01` tạo mới với `ref`='NEW', chưa có task nào; không có `sla.event` nào của `P-01`.
3. Quy tắc 030 mục 6: `write` task cũ rồi flush TRƯỚC `create` task mới, nếu không INSERT vi phạm `sla_task_one_active_uniq` và reset thất bại thành event `error`.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| now | T0, T0+1h, T0+2h, T0+3h |  |
| ref | NEW, RESET, CANCEL, RESET |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0, changed = {ref} | 1 task `in_progress` (T1) |
| 2 | Đặt `ref`='RESET' (G1); gọi Engine đánh giá `P-01` với now = T0+1h, changed = {ref} | T1 `cancelled`; có task mới T2 `in_progress`; đúng 1 task hoạt động; 0 event `error` của `P-01` |
| 3 | Đặt `ref`='CANCEL' (G1); gọi Engine với now = T0+2h, changed = {ref} | T2 `cancelled` (start không khớp, cancel_mode `start_unmatched`) |
| 4 | Đặt `ref`='RESET' (G1); gọi Engine với now = T0+3h, changed = {ref} (start khớp lại, task gần nhất `cancelled`: gắn lại bằng attach) | Có task mới T3 `in_progress` (attach); không vi phạm `sla_task_one_active_uniq`; tổng 3 task, đúng 1 task hoạt động; 0 event `error` của `P-01` |
| 5 | Gọi `flush_all()` rồi đọc `sla_task` bằng SQL trực tiếp theo (definition, `res.partner`, P-01) | Đúng 1 dòng có `stage` IN ('in_progress','paused'); không có lỗi chỉ mục duy nhất |

**Pass/Fail Criteria:** ✅ Pass: reset và attach lại thành công, mỗi thời điểm chỉ 1 task hoạt động, 0 event `error`; ❌ Fail: có event `error` do vi phạm chỉ mục duy nhất, thiếu task mới, hoặc 2 task hoạt động

**Ghi chú:** Ca bổ sung theo 030 mục 6 (quy tắc flush). Khi đối chiếu code ngày 2026-10-12, `sla_engine._reset/_cancel/_attach` chưa gọi `flush_recordset()` tường minh (TA-27): ca này kiểm kết quả quan sát được, không kiểm lời gọi flush.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

## TG-05 — Ba cấu hình dễ sai

### TC-MIS-001: Không gắn SLA khi start là tập con của stop ở chế độ cancel start_unmatched

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-05-01 |
| Coverage Item | CI-1 ((a) start ⊂ stop, cancel_mode=start_unmatched -> không gắn) |
| Requirement Ref | REQ-FUNC-016 (AC1) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `[('ref','in',['NEW','WORK'])]`; stop = `[('ref','in',['NEW','WORK','DONE'])]` (start là tập con của stop); cancel_mode=`start_unmatched`
2. Partner `P-01` tạo với `ref`='NEW' tại FX-T0, chưa có task

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref | NEW | thỏa start và đồng thời thỏa stop |
| now | T0 (09:00) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Không ngoại lệ |
| 2 | Đếm task và event của `P-01` | Số task = 0, số event `attach` = 0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Không có task nào được gắn. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-MIS-002: Không gắn SLA khi start là tập con của stop ở chế độ cancel condition

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-05-01 |
| Coverage Item | CI-2 ((a) start ⊂ stop, cancel_mode=condition -> không gắn) |
| Requirement Ref | REQ-FUNC-016 (AC1) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `[('ref','in',['NEW','WORK'])]`; stop = `[('ref','in',['NEW','WORK','DONE'])]` (start là tập con của stop); cancel_mode=`condition`; cancel = `[('ref','=','CANCEL')]`
2. Partner `P-01` tạo với `ref`='NEW' tại FX-T0, chưa có task

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref | NEW | thỏa start và đồng thời thỏa stop |
| now | T0 (09:00) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Không ngoại lệ |
| 2 | Đếm task và event của `P-01` | Số task = 0, số event `attach` = 0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Không có task nào được gắn. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-MIS-003: Không gắn SLA khi start là tập con của stop ở chế độ cancel never

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-05-01 |
| Coverage Item | CI-3 ((a) start ⊂ stop, cancel_mode=never -> không gắn) |
| Requirement Ref | REQ-FUNC-016 (AC1) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `[('ref','in',['NEW','WORK'])]`; stop = `[('ref','in',['NEW','WORK','DONE'])]` (start là tập con của stop); cancel_mode=`never`
2. Partner `P-01` tạo với `ref`='NEW' tại FX-T0, chưa có task

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref | NEW | thỏa start và đồng thời thỏa stop |
| now | T0 (09:00) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Không ngoại lệ |
| 2 | Đếm task và event của `P-01` | Số task = 0, số event `attach` = 0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Không có task nào được gắn. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-MIS-004: Gắn task ở trạng thái paused khi record vào hold và pause là tập con của start

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-05-02 |
| Coverage Item | CI-1 ((b) pause ⊂ start: gắn ở paused) |
| Requirement Ref | REQ-FUNC-016 (AC2, nửa đầu) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `[('ref','=','HOLD')]`; pause = `[('ref','=','HOLD')]` (pause ⊂ start); cancel_mode=`start_unmatched`
2. Partner `P-01` tạo với `ref`='HOLD' tại FX-T0, chưa có task

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref | HOLD | thỏa start và pause |
| now | T0 (09:00) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task, `stage`='paused' |
| 2 | Đếm event `attach` | Đúng 1 event `attach` và 0 event `pause` (D2/TA-04: attach thẳng vào `paused` chỉ ghi event `attach`) |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Task `paused` được gắn. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-MIS-005: Hủy task paused khi record rời hold vì pause hết khớp kéo theo start hết khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-05-02 |
| Coverage Item | CI-2 ((b) pause ⊂ start: hết hold -> cancelled) |
| Requirement Ref | REQ-FUNC-016 (AC2, nửa sau) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `[('ref','=','HOLD')]`; pause = `[('ref','=','HOLD')]` (pause ⊂ start); cancel_mode=`start_unmatched`
2. Partner `P-01` tạo với `ref`='HOLD' tại FX-T0; task `paused` được gắn ở bước 1

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | CLOSED | start và pause cùng hết khớp; stop (ref=DONE) không khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `paused` |
| 2 | Đặt `ref`='CLOSED' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Task `stage`='cancelled', `end_time`=10:00 |
| 3 | Đếm event `cancel` | 1 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Task chuyển `paused` -> `cancelled`. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-MIS-006: Hủy task, không ghi event pause, khi start và pause loại trừ nhau ở chế độ start_unmatched

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-05-03 |
| Coverage Item | CI-1 ((c) start_unmatched: cancel trước khi kịp pause) |
| Requirement Ref | REQ-FUNC-016 (AC3); REQ-FUNC-008 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `[('ref','in',['NEW','WORK'])]`; pause = `[('ref','=','HOLD')]` (start và pause loại trừ nhau); cancel_mode=`start_unmatched`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | HOLD | pause khớp, start hết khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Đặt `ref`='HOLD' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Task `stage`='cancelled' |
| 3 | Đếm event `pause` | 0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Task `cancelled` và không có event `pause`. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-MIS-007: Giữ task và chuyển paused khi start và pause loại trừ nhau ở chế độ cancel never

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-05-03 |
| Coverage Item | CI-2 ((c) never: ở lại và pause) |
| Requirement Ref | REQ-FUNC-016 (AC4) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `[('ref','in',['NEW','WORK'])]`; pause = `[('ref','=','HOLD')]` (start và pause loại trừ nhau); cancel_mode=`never`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | HOLD |  |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Đặt `ref`='HOLD' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Task `stage`='paused' (không bị hủy) |
| 3 | Đếm event `cancel` và `pause` | `cancel`=0, `pause`=1 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Task `paused`, không event `cancel`. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-MIS-008: Giữ task và chuyển paused khi start, pause loại trừ nhau, chế độ condition và cancel chưa khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-05-03 |
| Coverage Item | CI-3 ((c) condition, cancel chưa khớp: ở lại và pause) |
| Requirement Ref | REQ-FUNC-016 (Statement: condition, cancel chưa khớp) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: start = `[('ref','in',['NEW','WORK'])]`; pause = `[('ref','=','HOLD')]` (start và pause loại trừ nhau); cancel_mode=`condition`; cancel = `[('ref','=','CANCEL')]`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | HOLD | cancel không khớp |
| now bước 2 | T0+1h = 10:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Đặt `ref`='HOLD' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Task `stage`='paused' |
| 3 | Đếm event `cancel` và `pause` | `cancel`=0, `pause`=1 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Task `paused`, không bị hủy. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

## TG-06 — Giờ làm việc

### TC-TIM-001: Tính planned_end_time khi mục tiêu 8 giờ bắt đầu thứ Sáu 16:00 trên lịch T2-T6 (qua cuối tuần)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-06-01 |
| Coverage Item | CI-1 (Lớp a: cộng 8 giờ từ thứ Sáu 16:00, lịch T2-T6 08:00-17:00) |
| Requirement Ref | REQ-FUNC-018 (AC1) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. FX-CAL-VN: `fully_fixed`, `Asia/Ho_Chi_Minh`, T2-T6 08:00-17:00, 9 giờ/ngày, không nghỉ trưa.
3. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
4. Định nghĩa FX-DEF-VN trên `res.partner` với `duration` = 8, `schedule_source` = `definition`, `schedule_id` = FX-CAL-VN; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| P.ref | `NEW` | khớp start |
| duration | 8 | giờ |
| now (start) | 2026-03-06 16:00 giờ địa phương (09:00 UTC) | start_time = now vì không retroactive |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = 2026-03-06 16:00 giờ địa phương (09:00 UTC))` | Có đúng 1 task của (định nghĩa, P); `stage` = `in_progress`; `start_time` = 2026-03-06 09:00 UTC |
| 2 | Đọc `planned_end_time` của task | `planned_end_time` = thứ Hai 2026-03-09 15:00 giờ địa phương = 2026-03-09 08:00 UTC |

**Pass/Fail Criteria:** ✅ Pass: `planned_end_time` đúng bằng 2026-03-09 08:00 UTC; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-TIM-002: Tính planned_end_time khi thứ Hai là global leave của lịch (dời sang thứ Ba)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-06-01 |
| Coverage Item | CI-2 (Lớp b: như trên, thứ Hai là global leave) |
| Requirement Ref | REQ-FUNC-018 (AC2) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. FX-CAL-VN: `fully_fixed`, `Asia/Ho_Chi_Minh`, T2-T6 08:00-17:00, 9 giờ/ngày, không nghỉ trưa.
3. Global leave của FX-CAL-VN (`resource.calendar.leaves`, không gắn `resource_id`): từ 2026-03-09 00:00 đến 23:59 giờ địa phương (2026-03-08 17:00 UTC đến 2026-03-09 16:59 UTC).
4. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
5. Định nghĩa FX-DEF-VN trên `res.partner` với `duration` = 8, `schedule_source` = `definition`, `schedule_id` = FX-CAL-VN; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| P.ref | `NEW` | khớp start |
| duration | 8 | giờ |
| now (start) | 2026-03-06 16:00 giờ địa phương (09:00 UTC) | start_time = now vì không retroactive |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = 2026-03-06 16:00 giờ địa phương (09:00 UTC))` | Có đúng 1 task của (định nghĩa, P); `stage` = `in_progress`; `start_time` = 2026-03-06 09:00 UTC |
| 2 | Đọc `planned_end_time` của task | `planned_end_time` = thứ Ba 2026-03-10 15:00 giờ địa phương = 2026-03-10 08:00 UTC |

**Pass/Fail Criteria:** ✅ Pass: `planned_end_time` đúng bằng 2026-03-10 08:00 UTC; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-TIM-003: Tính planned_end_time bằng mốc bắt đầu khi mục tiêu bằng 0 giờ

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-06-02 |
| Coverage Item | CI-1 (Biên mục tiêu = 0 giờ) |
| Requirement Ref | REQ-FUNC-018 (AC3) |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. FX-CAL-VN: `fully_fixed`, `Asia/Ho_Chi_Minh`, T2-T6 08:00-17:00, 9 giờ/ngày, không nghỉ trưa.
3. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
4. Định nghĩa FX-DEF-VN trên `res.partner` với `duration` = 0, `schedule_source` = `definition`, `schedule_id` = FX-CAL-VN; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| P.ref | `NEW` | khớp start |
| duration | 0 | giờ |
| now (start) | T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC) | start_time = now vì không retroactive |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Có đúng 1 task của (định nghĩa, P); `stage` = `in_progress`; `start_time` = 2026-03-02 02:00 UTC |
| 2 | Đọc `planned_end_time` của task | `planned_end_time` = 2026-03-02 09:00 giờ địa phương = 2026-03-02 02:00 UTC |

**Pass/Fail Criteria:** ✅ Pass: `planned_end_time` đúng bằng 2026-03-02 02:00 UTC; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-TIM-004: Tính planned_end_time sang thứ Hai 09:00 khi mốc bắt đầu đúng 17:00 thứ Sáu và mục tiêu 1 giờ

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-06-02 |
| Coverage Item | CI-2 (Biên mốc đúng 17:00 thứ Sáu, mục tiêu 1 giờ) |
| Requirement Ref | REQ-FUNC-018 (AC3) |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. FX-CAL-VN: `fully_fixed`, `Asia/Ho_Chi_Minh`, T2-T6 08:00-17:00, 9 giờ/ngày, không nghỉ trưa.
3. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
4. Định nghĩa FX-DEF-VN trên `res.partner` với `duration` = 1, `schedule_source` = `definition`, `schedule_id` = FX-CAL-VN; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| P.ref | `NEW` | khớp start |
| duration | 1 | giờ |
| now (start) | 2026-03-06 17:00 giờ địa phương (10:00 UTC) | start_time = now vì không retroactive |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = 2026-03-06 17:00 giờ địa phương (10:00 UTC))` | Có đúng 1 task của (định nghĩa, P); `stage` = `in_progress`; `start_time` = 2026-03-06 10:00 UTC |
| 2 | Đọc `planned_end_time` của task | `planned_end_time` = thứ Hai 2026-03-09 09:00 giờ địa phương = 2026-03-09 02:00 UTC |

**Pass/Fail Criteria:** ✅ Pass: `planned_end_time` đúng bằng 2026-03-09 02:00 UTC; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Ghi chú:** Mốc bắt đầu trùng đúng giờ đóng cửa: không có giờ làm nào còn lại trong ngày Thứ Sáu nên cả 1 giờ nằm ở thứ Hai (08:00-09:00).

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-TIM-005: Tính planned_end_time 11:00 giờ địa phương (04:00 UTC) với lịch múi giờ Asia/Ho_Chi_Minh

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-06-03 |
| Coverage Item | CI-1 (Mốc 09:00 giờ địa phương, mục tiêu 2 giờ) |
| Requirement Ref | REQ-FUNC-018 (AC4) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. FX-CAL-VN: `fully_fixed`, `Asia/Ho_Chi_Minh`, T2-T6 08:00-17:00, 9 giờ/ngày, không nghỉ trưa.
3. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
4. Định nghĩa FX-DEF-VN trên `res.partner` với `duration` = 2, `schedule_source` = `definition`, `schedule_id` = FX-CAL-VN; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| P.ref | `NEW` | khớp start |
| duration | 2 | giờ |
| now (start) | T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC) | start_time = now vì không retroactive |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Có đúng 1 task của (định nghĩa, P); `stage` = `in_progress`; `start_time` = 2026-03-02 02:00 UTC |
| 2 | Đọc `planned_end_time` của task | `planned_end_time` = 2026-03-02 11:00 giờ địa phương = 2026-03-02 04:00 UTC |

**Pass/Fail Criteria:** ✅ Pass: `planned_end_time` đúng bằng 2026-03-02 04:00 UTC; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-TIM-006: Tính planned_end_time bằng start cộng thẳng 4 giờ khi task không có lịch (24x7)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-06-04 |
| Coverage Item | CI-1 (Không lịch, mục tiêu 4 giờ) |
| Requirement Ref | REQ-FUNC-018 (AC5) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| P.ref | `NEW` | khớp start |
| duration | 4 | giờ |
| now | T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Có 1 task `in_progress`; `schedule_id` rỗng; `start_time` = 2026-03-02 02:00 UTC |
| 2 | Đọc `planned_end_time` | `planned_end_time` = 2026-03-02 06:00 UTC (13:00 giờ địa phương) |

**Pass/Fail Criteria:** ✅ Pass: `planned_end_time` = 2026-03-02 06:00 UTC và `schedule_id` rỗng; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-TIM-007: Không tạo task và ghi event error khi lịch có ngày nghỉ phủ kín không xếp được hạn

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-06-05 |
| Coverage Item | CI-1 (Ngày nghỉ phủ kín > 100 cửa sổ 14 ngày) |
| Requirement Ref | REQ-FUNC-018 (AC6) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. FX-CAL-VN có global leave liên tục từ 2026-03-02 00:00 đến 2030-12-31 23:59 giờ địa phương (dài hơn 1400 ngày, tức hơn 100 cửa sổ 14 ngày liên tiếp).
3. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
4. Định nghĩa FX-DEF-VN trên `res.partner` với `duration` = 4, `schedule_source` = `definition`, `schedule_id` = FX-CAL-VN; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| P.ref | `NEW` | khớp start |
| duration | 4 |  |
| now | T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Engine không ném ngoại lệ ra ngoài (lỗi không chặn lưu record) |
| 2 | Đếm `sla.task` của (định nghĩa, P) | 0 task |
| 3 | Đọc `sla.event` có `event` = `error` với `res_model` = `res.partner`, `res_id` = P.id | Có đúng 1 event `error`, `task_id` rỗng, `note` không rỗng, `is_resolved` = False |

**Pass/Fail Criteria:** ✅ Pass: 0 task và đúng 1 event `error` chưa xử lý cho P; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Ghi chú:** event `error` không gắn task nên tra theo `res_model`/`res_id` (030 bảng `sla_event`; `sla.event._log_error` ghi hai field này); nội dung `note` lấy từ `constants/message.py` nên chỉ kiểm không rỗng.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-TIM-008: Cộng dồn thời gian đã trôi 1 giờ + 2 giờ = 3 giờ qua một lần pause 8 giờ trên lịch 24x7

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-06-06 |
| Coverage Item | CI-1 (Lịch 24x7: 1h chạy, 8h pause, 2h chạy) |
| Requirement Ref | REQ-FUNC-043 (AC1) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); pause khi `ref` = `HOLD`, resume khi `ref` = `WORK`, stop khi `ref` = `DONE`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| P.ref theo thứ tự | `NEW`, `HOLD`, `WORK`, `DONE` | FX-PARTNER-MARK |
| Mốc | T0, T0+1h, T0+9h, T0+11h | 10:00, 18:00, 20:00 giờ địa phương |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress`, `business_duration` = 0 |
| 2 | Ghi `ref` = `HOLD` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = T0 + 1h (10:00 giờ địa phương), changed = {ref})` | `stage` = `paused`; `business_duration` = 1.0 |
| 3 | Ghi `ref` = `WORK` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = T0 + 9h (18:00 giờ địa phương), changed = {ref})` | `stage` = `in_progress`; `business_duration` = 1.0 (8 giờ pause không tính) |
| 4 | Ghi `ref` = `DONE` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = T0 + 11h (20:00 giờ địa phương), changed = {ref})` | `stage` = `achieved`; `business_duration` = 3.0 (1 + 2) |

**Pass/Fail Criteria:** ✅ Pass: `business_duration` = 3.0 ở bước 4 (sai số tuyệt đối <= 0.001); ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Ghi chú:** Cần quy ước ghi `ref` bằng `_write` để tránh hook chạy với giờ thật; xem Vấn đề SRS 3.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-TIM-009: Cộng giờ làm việc từ thứ Sáu 16:00 đến thứ Hai 10:00 ra 3 giờ (1 + 2)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-06-06 |
| Coverage Item | CI-2 (Lịch T2-T6: thứ Sáu 16:00 đến thứ Hai 10:00) |
| Requirement Ref | REQ-FUNC-043 (AC2) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-VN trên `res.partner` với `duration` = 4, `schedule_source` = `definition`, `schedule_id` = FX-CAL-VN; stop khi `ref` = `DONE`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| P.ref | `NEW` rồi `DONE` |  |
| Mốc | 2026-03-06 16:00 và 2026-03-09 10:00 giờ địa phương | 09:00 UTC và 03:00 UTC |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = 2026-03-06 16:00 giờ địa phương (09:00 UTC))` | Task `in_progress`; `planned_end_time` = 2026-03-09 04:00 UTC (thứ Hai 11:00 giờ địa phương) |
| 2 | Ghi `ref` = `DONE` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = 2026-03-09 10:00 giờ địa phương (03:00 UTC), changed = {ref})` | `stage` = `achieved`; `business_duration` = 3.0 (1 giờ thứ Sáu + 2 giờ thứ Hai, 63 giờ ngoài giờ làm việc không được tính) |

**Pass/Fail Criteria:** ✅ Pass: `business_duration` = 3.0 và `stage` = `achieved`; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-TIM-010: Không tăng thời gian đã trôi khi task paused qua 6 giờ làm việc

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-06-06 |
| Coverage Item | CI-3 (Negative: task paused 6 giờ làm việc) |
| Requirement Ref | REQ-FUNC-043 (AC3) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-VN trên `res.partner` với `duration` = 8, `schedule_source` = `definition`, `schedule_id` = FX-CAL-VN; pause khi `ref` = `HOLD`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| P.ref | `NEW` rồi `HOLD` |  |
| Mốc | T0, T0+1h (10:00), T0+7h (16:00) | giờ địa phương |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress` |
| 2 | Ghi `ref` = `HOLD` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = T0 + 1h (10:00 giờ địa phương), changed = {ref})` | `stage` = `paused`; `business_duration` = 1.0 |
| 3 | Gọi Engine `evaluate(P, now = T0 + 7h (16:00 giờ địa phương; 6 giờ làm việc sau lúc pause))` | `stage` vẫn `paused`; `business_duration` vẫn = 1.0 |

**Pass/Fail Criteria:** ✅ Pass: `business_duration` = 1.0 ở bước 3 như ở bước 2; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-TIM-011: Giữ thời gian đã trôi 5 giờ không bị cắt ở mục tiêu 4 giờ

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-06-06 |
| Coverage Item | CI-4 (Biên: mục tiêu 4 giờ, đã trôi 5 giờ) |
| Requirement Ref | REQ-FUNC-043 (AC4) |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); stop khi `ref` = `DONE`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| duration | 4 |  |
| Mốc stop | T0 + 5h (14:00 giờ địa phương) | Xử lý nền chưa chạy |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress`; `planned_end_time` = 2026-03-02 06:00 UTC |
| 2 | Ghi `ref` = `DONE` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = T0 + 5h (14:00 giờ địa phương), changed = {ref})` | `stage` = `breached` (REQ-FUNC-009 AC2); `business_duration` = 5.0; `duration` = 4.0 |

**Pass/Fail Criteria:** ✅ Pass: `business_duration` = 5.0 (không phải 4.0); ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

## TG-07 — Retroactive start

### TC-RET-001: Lấy start_time từ mốc retroactive và tính planned_end_time = mốc + 4 giờ, chưa vi phạm

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-07-01 |
| Coverage Item | CI-1 (mốc cách 1h, mục tiêu 4h, lịch 24x7) |
| Requirement Ref | REQ-FUNC-017 (AC1) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: retroactive_start=true; retroactive_field_id = `RETRO-DT` (field Datetime ghi được của `res.partner`, G9)
2. Partner `P-01` tạo với `ref`='NEW' và `RETRO-DT`=2026-03-02 08:00 ICT (T0-1h)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| RETRO-DT | 2026-03-02 08:00 ICT (01:00 UTC) | T0-1h |
| now | T0 (09:00) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Đọc `start_time`, `planned_end_time`, `has_breached` | `start_time`=08:00; `planned_end_time`=12:00; `has_breached`=false |
| 3 | Đếm event `breach` | 0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Giá trị đúng như bước 2. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-RET-002: Bật dấu vi phạm và ghi event breach ngay lúc attach khi mốc đã quá hạn

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-07-01 |
| Coverage Item | CI-2 (mốc cách 6h -> breach ngay lúc attach) |
| Requirement Ref | REQ-FUNC-017 (AC2) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: retroactive_start=true; retroactive_field_id = `RETRO-DT` (field Datetime ghi được của `res.partner`, G9)
2. Partner `P-01` tạo với `ref`='NEW' và `RETRO-DT`=2026-03-02 03:00 ICT (T0-6h)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| RETRO-DT | 2026-03-02 03:00 ICT (2026-03-01 20:00 UTC) | T0-6h |
| now | T0 (09:00) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task được gắn |
| 2 | Đọc `start_time`, `planned_end_time`, `has_breached` | `start_time`=03:00; `planned_end_time`=07:00; `has_breached`=true |
| 3 | Đếm event `breach` | 1 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; `has_breached`=true và đúng 1 event `breach`. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-RET-003: Dùng thời điểm hiện tại làm start_time và ghi chú vào event attach khi field mốc trống

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-07-01 |
| Coverage Item | CI-3 (mốc trống -> dùng thời điểm attach + ghi chú) |
| Requirement Ref | REQ-FUNC-017 (AC3) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: retroactive_start=true; retroactive_field_id = `RETRO-DT` (field Datetime ghi được của `res.partner`, G9)
2. Partner `P-01` tạo với `ref`='NEW' và `RETRO-DT` rỗng

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| RETRO-DT | rỗng |  |
| now | T0 (09:00) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Đọc `start_time` và `planned_end_time` | `start_time`=09:00; `planned_end_time`=13:00 |
| 3 | Đọc `note` của event `attach` | Không rỗng, nêu việc dùng thời điểm hiện tại do mốc trống (G10: từ khóa cụ thể do SRS chưa quy định) |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; `start_time`=now và `note` của `attach` giải thích. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-RET-004: Bật dấu vi phạm khi planned_end_time bằng đúng thời điểm attach

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-07-01 |
| Coverage Item | CI-4 (biên: mốc đúng 4h trước (planned_end_time = now) -> breach) |
| Requirement Ref | REQ-FUNC-017 (Statement: quá hạn); thuật ngữ Dấu vi phạm: chạm hoặc vượt [G11] |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: retroactive_start=true; retroactive_field_id = `RETRO-DT` (field Datetime ghi được của `res.partner`, G9)
2. Partner `P-01` tạo với `ref`='NEW' và `RETRO-DT`=2026-03-02 05:00 ICT (T0-4h)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| RETRO-DT | 2026-03-02 05:00 ICT | planned_end_time = 09:00 = now |
| now | T0 (09:00) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task được gắn |
| 2 | Đọc `planned_end_time` và `has_breached` | `planned_end_time`=09:00; `has_breached`=true |
| 3 | Đếm event `breach` | 1 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Chạm đúng hạn thì breach (theo định nghĩa Dấu vi phạm). ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-RET-005: Không bật dấu vi phạm khi planned_end_time còn 1 phút so với thời điểm attach

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-07-01 |
| Coverage Item | CI-5 (biên: mốc cách 3h59m -> chưa breach) |
| Requirement Ref | REQ-FUNC-017 (BVA dưới hạn) |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: retroactive_start=true; retroactive_field_id = `RETRO-DT` (field Datetime ghi được của `res.partner`, G9)
2. Partner `P-01` tạo với `ref`='NEW' và `RETRO-DT`=2026-03-02 05:01 ICT (T0-3h59m)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| RETRO-DT | 2026-03-02 05:01 ICT | planned_end_time = 09:01 |
| now | T0 (09:00) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Đọc `planned_end_time` và `has_breached` | `planned_end_time`=09:01; `has_breached`=false |
| 3 | Đếm event `breach` | 0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Chưa breach. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-RET-006: Không trừ thời gian đã paused trước attach khi tính planned_end_time retroactive

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-07-01 |
| Coverage Item | CI-6 (thời gian paused trước attach không được trừ) |
| Requirement Ref | REQ-FUNC-017 (Statement: không trừ thời gian paused) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: retroactive_start=true; retroactive_field_id = `RETRO-DT` (field Datetime ghi được của `res.partner`, G9); pause = `[('ref','=','HOLD')]` (đã sẵn trong FX-DEF-STD)
2. Partner `P-01` tạo với `ref`='HOLD' và `RETRO-DT`=2026-03-02 06:00 ICT (T0-3h); record đã ở HOLD từ trước mốc (không có dữ liệu pause quá khứ được dùng)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| RETRO-DT | 2026-03-02 06:00 ICT | T0-3h |
| now | T0 (09:00) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `stage`='paused' (pause khớp lúc attach) |
| 2 | Đọc `start_time` và `planned_end_time` | `start_time`=06:00; `planned_end_time`=10:00 (= mốc + 4h, không cộng thêm thời gian paused trước đó) |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; `planned_end_time` đúng bằng mốc + mục tiêu. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-RET-007: Tính planned_end_time theo lịch FX-CAL-VN từ mốc retroactive trước cuối tuần

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-07-01 |
| Coverage Item | CI-7 (retroactive với lịch giờ làm việc) |
| Requirement Ref | REQ-FUNC-017 (Statement: tính planned_end_time từ mốc); REQ-FUNC-018 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition); đổi: schedule_source=`definition`, schedule_id=FX-CAL-VN (T2–T6 08:00–17:00); retroactive_start=true; retroactive_field_id=`RETRO-DT`
2. Partner `P-01` tạo với `ref`='NEW' và `RETRO-DT`=2026-02-27 16:00 ICT (thứ Sáu)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| RETRO-DT | 2026-02-27 16:00 ICT (09:00 UTC) | thứ Sáu |
| now | T0 (2026-03-02 09:00) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Đọc `start_time` và `planned_end_time` | `start_time`=2026-02-27 16:00; `planned_end_time`=2026-03-02 11:00 (1 giờ thứ Sáu + 3 giờ thứ Hai) |
| 3 | Đọc `has_breached` | false (đã trôi 1h thứ Sáu + 1h thứ Hai = 2h < 4h) |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; `planned_end_time`=2026-03-02 11:00 ICT, chưa breach. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-RET-008: Từ chối lưu định nghĩa khi field retroactive là `name` (Char)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-07-02 |
| Coverage Item | CI-1 (field retroactive là Char -> từ chối) |
| Requirement Ref | REQ-FUNC-041 (AC1) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Định nghĩa `D-1` trên model `res.partner`, duration=4, chưa lưu

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| retroactive_start | true |  |
| retroactive_field_id | `res.partner.name` (Char) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gán retroactive_field_id=`name` và lưu `D-1` | Lưu bị từ chối với lỗi validation (ValidationError) |
| 2 | Đếm bản ghi `sla.definition` tên `D-1` | 0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Định nghĩa không được lưu. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-RET-009: Từ chối lưu định nghĩa khi field retroactive thuộc model khác

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-07-02 |
| Coverage Item | CI-2 (field retroactive thuộc model khác -> từ chối) |
| Requirement Ref | REQ-FUNC-041 (AC2) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Định nghĩa `D-1` trên model `res.partner`, duration=4, chưa lưu
2. Có field Datetime `res.users.login_date` (model `res.users`)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| retroactive_field_id | `res.users.login_date` (Datetime, model khác) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gán retroactive_field_id=`login_date` của `res.users` và lưu `D-1` | Lưu bị từ chối |
| 2 | Đếm bản ghi `D-1` | 0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Định nghĩa không được lưu. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-RET-010: Từ chối lưu định nghĩa khi field kích hoạt reset thuộc model khác

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-07-02 |
| Coverage Item | CI-3 (field kích hoạt reset thuộc model khác -> từ chối) |
| Requirement Ref | REQ-FUNC-041 (AC2) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Định nghĩa `D-1` trên model `res.partner`, duration=4, chưa lưu; reset = `[]`

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| reset_field_ids | {`res.users.login`} (model khác) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gán reset_field_ids = {`login` của `res.users`} và lưu `D-1` | Lưu bị từ chối |
| 2 | Đếm bản ghi `D-1` | 0 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Định nghĩa không được lưu. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-RET-011: Lưu thành công định nghĩa khi field retroactive là Datetime của đúng model

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-07-02 |
| Coverage Item | CI-4 (field retroactive Datetime đúng model -> lưu được) |
| Requirement Ref | REQ-FUNC-041 (AC3) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Định nghĩa `D-1` trên model `res.partner`, duration=4, chưa lưu

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| retroactive_field_id | `RETRO-DT` (Datetime, `res.partner`) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gán retroactive_start=true, retroactive_field_id=`RETRO-DT` và lưu `D-1` | Lưu thành công |
| 2 | Đọc lại `retroactive_field_id` | = `RETRO-DT` |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Định nghĩa được lưu. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-RET-012: Lưu thành công định nghĩa khi field kích hoạt reset thuộc đúng model

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-07-02 |
| Coverage Item | CI-5 (field kích hoạt reset thuộc đúng model -> lưu được) |
| Requirement Ref | REQ-FUNC-041 (Statement, phía chấp nhận) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Định nghĩa `D-1` trên model `res.partner`, duration=4, chưa lưu; reset = `[]`

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| reset_field_ids | {`res.partner.user_id`} |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gán reset_field_ids = {`user_id`} và lưu `D-1` | Lưu thành công |
| 2 | Đọc lại reset_field_ids | = {`user_id`} |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Định nghĩa được lưu. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

## TG-08 — Escalation, thử lại, xử lý nền

### TC-ESC-001: Bắn lần lượt ba mốc 75%, 100%, 120% khi đã trôi 3 giờ, 4 giờ, 4,8 giờ

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-01 |
| Coverage Item | CI-1 (AC1: ba mốc 75/100/120% bắn lần lượt tại 3h, 4h, 4,8h) |
| Requirement Ref | REQ-FUNC-023 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Ba mốc: Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false). Mốc escalation 100% (`percent` = 100, `action_id` = SA-N100, `retry` = false). Mốc escalation 120% (`percent` = 120, `action_id` = SA-N120, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`. Server action SA-N100 (model `res.partner`): code `record.message_post(body='N100')`. Server action SA-N120 (model `res.partner`): code `record.message_post(body='N120')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Mục tiêu | 4 giờ, 24x7 | 75% = 3h, 100% = 4h, 120% = 4h48 |
| Record gốc | P-1 | `ref` = 'NEW' |
| Thời điểm attach | 2026-03-02 09:00 | FX-T0 |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = FX-T0, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress`, `start_time` = 09:00, `planned_end_time` = 13:00; chưa có event `escalate` |
| 2 | Xử lý nền tại now = FX-T0 + 3h (12:00) | `call_count` SA-N75 = 1, SA-N100 = 0, SA-N120 = 0; số event `escalate` của task = 1; chatter của P-1 có 1 ghi chú 'N75' |
| 3 | Xử lý nền tại now = FX-T0 + 4h (13:00) | `call_count` SA-N100 = 1; số event `escalate` = 2; chatter có thêm ghi chú 'N100' (event `breach` nếu có không tính vào số này) |
| 4 | Xử lý nền tại now = FX-T0 + 4h48 (13:48) | `call_count` SA-N120 = 1; số event `escalate` = 3; chatter có thêm ghi chú 'N120' |
| 5 | Đọc `done` (mốc đã xử lý) của task | Cả 3 mốc nằm trong tập mốc đã xử lý |

**Pass/Fail Criteria:** ✅ Pass: đúng 3 event `escalate`, mỗi action đúng 1 lần, đúng thứ tự 75, 100, 120 và đúng thời điểm; ❌ Fail: thiếu hoặc thừa event `escalate`, sai thứ tự, action chạy trên record khác, hoặc mốc bắn trước thời điểm

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-002: Từ chối lưu mốc có phần trăm = 0

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-01 |
| Coverage Item | CI-2 (AC2: percent = 0 (biên dưới) bị từ chối) |
| Requirement Ref | REQ-FUNC-023 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
4. Chưa có mốc escalation nào trên FX-DEF-STD

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| percent | 0 | Giá trị không hợp lệ |
| action_id | SA-N75 | cùng model `res.partner` |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 0, action_id: SA-N75, retry: false} | Bị từ chối bởi ràng buộc CSDL `sla_escalation_percent_check` (`IntegrityError`, thông báo ràng buộc "Percent must be greater than 0.") |
| 2 | Đếm `sla.escalation` của FX-DEF-STD | = 0 (không có mốc nào được lưu) |

**Pass/Fail Criteria:** ✅ Pass: ngoại lệ được ném và không có bản ghi mốc nào được tạo; ❌ Fail: mốc được lưu thành công hoặc bị làm tròn/ép kiểu im lặng thành số khác

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-003: Từ chối lưu mốc có phần trăm âm

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-01 |
| Coverage Item | CI-3 (AC2: percent âm (-10) bị từ chối) |
| Requirement Ref | REQ-FUNC-023 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
4. Chưa có mốc escalation nào trên FX-DEF-STD

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| percent | -10 | Giá trị không hợp lệ |
| action_id | SA-N75 | cùng model `res.partner` |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: -10, action_id: SA-N75, retry: false} | Bị từ chối bởi ràng buộc CSDL `sla_escalation_percent_check` (`IntegrityError`, thông báo ràng buộc "Percent must be greater than 0."); giá trị 0 cũng bị từ chối cùng ràng buộc |
| 2 | Đếm `sla.escalation` của FX-DEF-STD | = 0 (không có mốc nào được lưu) |

**Pass/Fail Criteria:** ✅ Pass: ngoại lệ được ném và không có bản ghi mốc nào được tạo; ❌ Fail: mốc được lưu thành công hoặc bị làm tròn/ép kiểu im lặng thành số khác

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-004: Từ chối lưu mốc có phần trăm không nguyên 75,5

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-01 |
| Coverage Item | CI-4 (AC2: percent không nguyên (75,5) bị từ chối) |
| Requirement Ref | REQ-FUNC-023 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
4. Chưa có mốc escalation nào trên FX-DEF-STD

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| percent | 75.5 | `percent` là FLOAT8 (D6/TA-06 đã chốt): không bị ép thành 75 im lặng; `_check_percent` từ chối số không nguyên |
| action_id | SA-N75 | cùng model `res.partner` |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 75.5, action_id: SA-N75, retry: false} | Bị từ chối bằng `ValidationError`; thông báo chứa "is not an integer" (VAL_016: "Percent '75.5' is not an integer. Enter a positive integer, e.g. 75 or 100.") |
| 2 | Đếm `sla.escalation` của FX-DEF-STD | = 0 (không có mốc nào được lưu) |

**Pass/Fail Criteria:** ✅ Pass: ngoại lệ được ném và không có bản ghi mốc nào được tạo; ❌ Fail: mốc được lưu thành công hoặc bị làm tròn/ép kiểu im lặng thành số khác

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-005: Chấp nhận lưu mốc có phần trăm = 1 (biên hợp lệ nhỏ nhất)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-01 |
| Coverage Item | CI-5 (Biên hợp lệ: percent = 1 được chấp nhận) |
| Requirement Ref | REQ-FUNC-023 AC2 |
| Priority | P3-Medium |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
4. Chưa có mốc escalation nào trên FX-DEF-STD

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| percent | 1 | biên hợp lệ nhỏ nhất |
| action_id | SA-N75 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 1, action_id: SA-N75} | Tạo thành công, không có lỗi |
| 2 | Đọc lại bản ghi | `percent` = 1; số mốc của FX-DEF-STD = 1 |

**Pass/Fail Criteria:** ✅ Pass: bản ghi tồn tại với `percent` = 1; ❌ Fail: bị từ chối hoặc lưu giá trị khác 1

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-006: Không bắn mốc 75% khi mới trôi 2 giờ 59 phút

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-02 |
| Coverage Item | CI-1 (Biên: đã trôi 2h59 (ngay dưới 75%)) |
| Requirement Ref | REQ-FUNC-023 AC1 |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Mục tiêu | 4 giờ, 24x7 |  |
| now xử lý nền | 2026-03-02 11:59 | FX-T0 + 2h59 |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = FX-T0, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress`; `next_due_at` = 12:00 (05:00 UTC) |
| 2 | Xử lý nền tại now = FX-T0 + 2h59 (11:59) | `call_count` SA-N75 = 0; số event `escalate` = 0; `next_due_at` vẫn 12:00 |

**Pass/Fail Criteria:** ✅ Pass: không có action và không có event `escalate`; ❌ Fail: mốc bắn sớm hơn 3 giờ đã trôi

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-007: Bắn mốc 75% khi đã trôi đúng 3 giờ

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-02 |
| Coverage Item | CI-2 (Biên: đã trôi đúng 3h00 (đúng 75%)) |
| Requirement Ref | REQ-FUNC-023 AC1 |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Mục tiêu | 4 giờ, 24x7 |  |
| now xử lý nền | 2026-03-02 12:00 | FX-T0 + 3h |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = FX-T0, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress`; `next_due_at` = 12:00 |
| 2 | Xử lý nền tại now = FX-T0 + 3h (12:00) | `call_count` SA-N75 = 1; số event `escalate` = 1 |

**Pass/Fail Criteria:** ✅ Pass: đúng 1 action và 1 event `escalate` tại biên 3 giờ; ❌ Fail: không bắn tại đúng biên hoặc bắn nhiều hơn 1 lần

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-008: Không bắn lại mốc đã xử lý khi xử lý nền chạy hai lần liên tiếp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-03 |
| Coverage Item | CI-1 (AC1: xử lý nền chạy hai lần liên tiếp) |
| Requirement Ref | REQ-FUNC-024 AC1 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| now lần 1 | 2026-03-02 12:00 | mốc đến hạn |
| now lần 2 | 2026-03-02 12:01 | chạy lại sau 1 phút |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = FX-T0, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 12:00 | `call_count` SA-N75 = 1; 1 event `escalate` |
| 3 | Xử lý nền tại now = 12:01 | `call_count` SA-N75 vẫn = 1; số event `escalate` vẫn = 1 |

**Pass/Fail Criteria:** ✅ Pass: tổng đúng 1 lần chạy action và 1 event `escalate`; ❌ Fail: action chạy lần hai hoặc có event `escalate` thứ hai

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-009: Không bắn hai lần khi hai tiến trình xử lý nền cùng chạy trên một task

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-03 |
| Coverage Item | CI-2 (AC2: hai tiến trình xử lý nền đồng thời trên cùng task) |
| Requirement Ref | REQ-FUNC-024 AC2 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
7. Hai cursor độc lập C1 và C2 (hai giao dịch) tới cùng database; task của P-1 đã attach và commit lúc FX-T0

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| now | 2026-03-02 12:00 | mốc 75% đến hạn |
| Thứ tự | C1 chọn và giữ khóa trước, C2 chạy khi C1 chưa commit | điều khiển bằng mã, không dùng sleep |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | C1: `process_due()` (patch `odoo.fields.Datetime.now` trả 12:00 giờ VN) tạm dừng sau khi chạy action và ghi event nhưng CHƯA commit (giữ khóa dòng task) | C1 đã gọi SA-N75 1 lần |
| 2 | C2: `process_due()` (patch `odoo.fields.Datetime.now` trả 12:00 giờ VN) chạy trọn vẹn khi C1 đang giữ khóa | C2 bỏ qua task (SKIP LOCKED): `call_count` SA-N75 vẫn = 1; C2 không ghi event |
| 3 | C1 commit; sau đó C3 (cursor mới): `process_due()` (patch `odoo.fields.Datetime.now` trả 12:00 giờ VN) | `call_count` SA-N75 vẫn = 1 (mốc đã trong tập đã xử lý) |
| 4 | Đếm event `escalate` của task bằng cursor mới | = 1 |

**Pass/Fail Criteria:** ✅ Pass: đúng 1 lần chạy action và đúng 1 event `escalate` sau cả ba lần xử lý; ❌ Fail: action chạy từ 2 lần trở lên hoặc có 2 event `escalate`

**Postconditions:** Dữ liệu đã commit bởi C1: dọn bằng xóa các bản ghi test sau ca (ca đồng thời dùng `TransactionCase` kèm cursor riêng, cần `tearDown` dọn thủ công).

### TC-ESC-010: Không chạy server action trong lần lưu record dù task đã chạm mốc 75%

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-04 |
| Coverage Item | CI-1 (AC1: lưu record khi task chạm 75% chưa chạy action) |
| Requirement Ref | REQ-FUNC-025 AC1 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
7. Task của P-1 đã attach lúc FX-T0 (09:00)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Thao tác lưu | ghi `ref` = 'WORK' tại now = 12:00 | task đã trôi 3 giờ = 75% |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Ghi `P-1.ref` = 'WORK' rồi gọi Engine `evaluate(P-1, now = 12:00, changed = {ref})` | Lệnh hoàn tất không lỗi; `P-1.ref` = 'WORK'; task vẫn `in_progress` |
| 2 | Đọc `call_count` SA-N75 và event `escalate` | `call_count` = 0; số event `escalate` = 0; chatter không có 'N75' |
| 3 | Xử lý nền tại now = 12:00 | `call_count` SA-N75 = 1; số event `escalate` = 1 |

**Pass/Fail Criteria:** ✅ Pass: action chỉ chạy sau bước xử lý nền, không chạy trong bước lưu; ❌ Fail: action chạy hoặc có event `escalate` ngay sau lần lưu

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-011: Không bắn escalation cho task paused dù đã qua thời điểm mốc

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-05 |
| Coverage Item | CI-1 (AC1: task paused đã qua thời điểm của mốc) |
| Requirement Ref | REQ-FUNC-054 AC1 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false). Mốc escalation 100% (`percent` = 100, `action_id` = SA-N100, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`. Server action SA-N100 (model `res.partner`): code `record.message_post(body='N100')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Mục tiêu | 4 giờ, 24x7 | mốc 75% và 100% |
| now xử lý nền | 19:00 (10 giờ sau FX-T0) | quá thời điểm của mọi mốc theo đồng hồ |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = FX-T0, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Ghi `ref` = 'HOLD' và gọi `evaluate(P-1, now = 10:00, changed = {ref})` | `stage` = `paused`; `business_duration` = 1h |
| 3 | Xử lý nền tại now = 19:00 (10 giờ sau FX-T0) | `call_count` SA-N75 = 0 và SA-N100 = 0; số event `escalate` = 0; `next_due_at` = NULL (không còn mốc cho xử lý nền) |

**Pass/Fail Criteria:** ✅ Pass: không có event `escalate` nào cho task ở stage `paused`; ❌ Fail: có action chạy hoặc có event `escalate`

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-012: Không bắn escalation cho task achieved còn mốc chưa xử lý

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-05 |
| Coverage Item | CI-2 (AC2: task achieved còn mốc chưa xử lý) |
| Requirement Ref | REQ-FUNC-054 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false). Mốc escalation 100% (`percent` = 100, `action_id` = SA-N100, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`. Server action SA-N100 (model `res.partner`): code `record.message_post(body='N100')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Mục tiêu | 4 giờ, 24x7 | mốc 75% và 100% |
| now xử lý nền | 13:00 | quá thời điểm của mọi mốc theo đồng hồ |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = FX-T0, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Ghi `ref` = 'DONE' và gọi `evaluate(P-1, now = 10:00, changed = {ref})` | `stage` = `achieved`; 1 event `complete`; không mốc nào trong tập đã xử lý |
| 3 | Xử lý nền tại now = 13:00 | `call_count` SA-N75 = 0 và SA-N100 = 0; số event `escalate` = 0; `next_due_at` = NULL (không còn mốc cho xử lý nền) |

**Pass/Fail Criteria:** ✅ Pass: không có event `escalate` nào cho task ở stage `achieved`; ❌ Fail: có action chạy hoặc có event `escalate`

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-013: Không bắn escalation cho task breached

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-05 |
| Coverage Item | CI-3 (Statement: task breached) |
| Requirement Ref | REQ-FUNC-054 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false). Mốc escalation 100% (`percent` = 100, `action_id` = SA-N100, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`. Server action SA-N100 (model `res.partner`): code `record.message_post(body='N100')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Mục tiêu | 4 giờ, 24x7 | mốc 75% và 100% |
| now xử lý nền | 14:30 | quá thời điểm của mọi mốc theo đồng hồ |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = FX-T0, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress`, `planned_end_time` = 13:00 |
| 2 | Ghi `ref` = 'DONE' và gọi `evaluate(P-1, now = 14:00, changed = {ref})` (đã quá `planned_end_time`) | `stage` = `breached`; `has_breached` = true |
| 3 | Xử lý nền tại now = 14:30 | `call_count` SA-N75 = 0 và SA-N100 = 0; số event `escalate` = 0; `next_due_at` = NULL (không còn mốc cho xử lý nền) |

**Pass/Fail Criteria:** ✅ Pass: không có event `escalate` nào cho task ở stage `breached`; ❌ Fail: có action chạy hoặc có event `escalate`

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-014: Không bắn escalation cho task cancelled

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-05 |
| Coverage Item | CI-4 (Statement: task cancelled) |
| Requirement Ref | REQ-FUNC-054 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false). Mốc escalation 100% (`percent` = 100, `action_id` = SA-N100, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`. Server action SA-N100 (model `res.partner`): code `record.message_post(body='N100')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Mục tiêu | 4 giờ, 24x7 | mốc 75% và 100% |
| now xử lý nền | 13:00 | quá thời điểm của mọi mốc theo đồng hồ |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = FX-T0, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Ghi `ref` = 'CANCEL' và gọi `evaluate(P-1, now = 10:00, changed = {ref})` | `stage` = `cancelled`; 1 event `cancel` |
| 3 | Xử lý nền tại now = 13:00 | `call_count` SA-N75 = 0 và SA-N100 = 0; số event `escalate` = 0; `next_due_at` = NULL (không còn mốc cho xử lý nền) |

**Pass/Fail Criteria:** ✅ Pass: không có event `escalate` nào cho task ở stage `cancelled`; ❌ Fail: có action chạy hoặc có event `escalate`

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-015: Tính lại mốc 75% bắn lúc 16:00 khi resume lúc 14:00 sau khi đã trôi 1 giờ

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-06 |
| Coverage Item | CI-1 (AC1: resume tính lại mốc 75% theo giờ còn lại) |
| Requirement Ref | REQ-FUNC-055 AC1 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Attach | 07:00 | FX-T0 − 2h |
| Pause | 08:00 (đã trôi 1h) |  |
| Resume | 14:00 (pause 6h) |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = 07:00, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress`, `start_time` = 07:00 |
| 2 | Ghi `ref` = 'HOLD', `evaluate(P-1, now = 08:00, changed = {ref})` | `stage` = `paused`; `business_duration` = 1.0 |
| 3 | Ghi `ref` = 'WORK', `evaluate(P-1, now = 14:00, changed = {ref})` | `stage` = `in_progress`; `next_due_at` = 16:00 (còn 2 giờ để đủ 3 giờ) |
| 4 | Xử lý nền tại now = 15:59 | `call_count` SA-N75 = 0; không event `escalate` |
| 5 | Xử lý nền tại now = 16:00 | `call_count` SA-N75 = 1; 1 event `escalate` |

**Pass/Fail Criteria:** ✅ Pass: mốc 75% bắn đúng 16:00 và không bắn trước; ❌ Fail: mốc bắn lúc 12:00 hoặc thời điểm khác 16:00

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-016: Tính lại mốc đang chờ thử lại như mốc chưa xử lý khi resume [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-06 |
| Coverage Item | CI-2 (AC2: mốc đang chờ thử lại khi pause rồi resume) |
| Requirement Ref | REQ-FUNC-055 AC2 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-F1, `retry` = true, `retry_pattern` = '[10]').
4. Server action SA-FLAKY(1) tên SA-F1: lần gọi đầu ném `UserError('SA-FAIL: boom')`, các lần sau thành công (đếm bằng `call_count`).
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Attach | 07:00 |  |
| Mốc 75% đến hạn | 10:00 | 3h sau attach |
| Pause | 10:05 |  |
| Resume | 11:00 |  |
| retry_pattern | [10] |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = 07:00, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 10:00 | Lần gọi 1 lỗi: 1 event `escalate_retry`; 1 dòng `sla.escalation.retry` với `retry_at` = 10:10 |
| 3 | Ghi `ref` = 'HOLD', `evaluate(P-1, now = 10:05, changed = {ref})` | `stage` = `paused`; số dòng `sla.escalation.retry` = 0 (cờ `cancel_retry_on_stop` mặc định True nên dòng retry bị xóa lúc pause) |
| 4 | Ghi `ref` = 'WORK', `evaluate(P-1, now = 11:00, changed = {ref})` | `stage` = `in_progress`; số dòng retry = 0; mốc 75% chưa nằm trong tập đã xử lý; `next_due_at` = 11:00 (đã trôi 3h05 > 3h nên mốc 75% đến hạn ngay; TA-08: cờ `cancel_retry_on_stop` mặc định True nên dòng retry đã bị xóa từ lúc pause ở bước 3 (`_cancel_pending_retries`); resume không còn xóa lượt thử, chỉ tính lại mốc từ đầu) |
| 5 | Xử lý nền tại now = 11:00 | `call_count` SA-F1 = 2; 1 event `escalate`; tổng `escalate_retry` vẫn = 1; số dòng retry = 0 |

**Pass/Fail Criteria:** ✅ Pass: sau resume mốc được xử lý như chưa xử lý: không còn lượt thử cũ, action chạy lại và ghi `escalate`; ❌ Fail: lượt thử cũ còn tồn tại, hoặc không chạy lại action, hoặc ghi thêm `escalate_retry`

**Ghi chú:** Với cờ `cancel_retry_on_stop` = False dòng retry sống qua pause và vẫn chạy ở nền (TC-ESC-060); resume không xóa lượt thử trong cả hai trường hợp.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-017: Không tính lại và không bắn mốc khi task vẫn paused

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-06 |
| Coverage Item | CI-3 (AC3: task vẫn paused thì không tính lại, không bắn) |
| Requirement Ref | REQ-FUNC-055 AC3 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Attach | 07:00 |  |
| Pause | 08:00 |  |
| now xử lý nền | 2026-03-03 09:00 | 25 giờ sau |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = 07:00, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Ghi `ref` = 'HOLD', `evaluate(P-1, now = 08:00, changed = {ref})` | `stage` = `paused`; `next_due_at` = NULL |
| 3 | Xử lý nền tại now = 2026-03-03 09:00 | `call_count` SA-N75 = 0; số event `escalate` = 0; `next_due_at` vẫn NULL; mốc 75% chưa nằm trong tập đã xử lý |

**Pass/Fail Criteria:** ✅ Pass: paused: không event `escalate`, `next_due_at` vẫn NULL; ❌ Fail: mốc bắn hoặc `next_due_at` có giá trị

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-018: Cô lập lỗi: task 1 ghi escalate_failed còn task 2 vẫn ghi escalate

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-07 |
| Coverage Item | CI-1 (AC1: action task 1 lỗi, task 2 vẫn bắn) |
| Requirement Ref | REQ-FUNC-026 AC1 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
5. Wrapper `ir.actions.server.run` ném `UserError('SA-FAIL: boom')` khi record là P-A, gọi bình thường với P-B; Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-A (`ref` = 'NEW') tạo xong, chưa có task SLA.
7. Partner P-B (`ref` = 'NEW') tạo xong, chưa có task SLA.
8. Cả hai attach lúc FX-T0 (có 2 task)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Record lỗi | P-A |  |
| Record bình thường | P-B |  |
| now | 12:00 | cả hai mốc 75% đến hạn |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Xử lý nền tại now = 12:00 | Lệnh hoàn tất, không ném ngoại lệ ra ngoài |
| 2 | Đọc event của task P-A | 1 event `escalate_failed` có `note` chứa 'SA-FAIL: boom'; 0 event `escalate` |
| 3 | Đọc event của task P-B | 1 event `escalate`; 0 event `escalate_failed`; chatter P-B có ghi chú 'N75' |
| 4 | Đọc tập mốc đã xử lý của hai task | Mốc 75% nằm trong tập của cả P-A và P-B |

**Pass/Fail Criteria:** ✅ Pass: lỗi chỉ ảnh hưởng task P-A; P-B có `escalate`; ❌ Fail: P-B không bắn, hoặc P-A không có `escalate_failed`, hoặc ngoại lệ lan ra ngoài

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-019: Không chạy lại action lỗi của mốc không bật thử lại ở các lần xử lý nền sau

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-07 |
| Coverage Item | CI-2 (AC2: chạy nền lần nữa không chạy lại action lỗi) |
| Requirement Ref | REQ-FUNC-026 AC2 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-FAIL, `retry` = false).
4. Server action SA-FAIL (model `res.partner`): luôn ném `UserError('SA-FAIL: boom')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| now lần 1 | 12:00 |  |
| now lần 2 và 3 | 12:01 và 13:00 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = FX-T0, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 12:00 | `call_count` SA-FAIL = 1; 1 event `escalate_failed` |
| 3 | Xử lý nền tại now = 12:01 | `call_count` vẫn = 1; số event `escalate_failed` vẫn = 1 |
| 4 | Xử lý nền tại now = 13:00 | `call_count` vẫn = 1; không có event `escalate` hay `escalate_retry` |

**Pass/Fail Criteria:** ✅ Pass: action lỗi chỉ được gọi đúng 1 lần; ❌ Fail: action lỗi được gọi lại ở lần xử lý sau

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-020: Ghi escalate_retry nêu giờ thử kế tiếp 10:01 khi action lỗi lúc 10:00 [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-08 |
| Coverage Item | CI-1 (AC1: lỗi lúc 10:00 ghi 1 escalate_retry với giờ 10:01) |
| Requirement Ref | REQ-FUNC-027 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc 75% với `retry` = true, `retry_pattern` = '[1, 10]', action SA-FAIL (luôn lỗi); Server action SA-FAIL (model `res.partner`): luôn ném `UserError('SA-FAIL: boom')`.
4. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
5. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
6. Task attach lúc 07:00 (FX-T0 − 2h) nên mốc 75% đến hạn 10:00

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| retry_pattern | [1, 10] |  |
| Lỗi lúc | 10:00 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = 07:00, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 10:00 | `call_count` SA-FAIL = 1 |
| 3 | Đọc event của task | Đúng 1 event `escalate_retry`, `note` chứa 'SA-FAIL: boom' và giờ thử kế tiếp dạng chuỗi của datetime UTC '2026-03-02 03:01:00' (định dạng "Error: %s. Will retry at %s."; múi giờ UTC, TA-23); 0 event `escalate_failed`; 0 event `escalate` |
| 4 | Đọc `sla.escalation.retry` của (task, mốc) | Đúng 1 dòng, `retry_at` = 10:01:00 (03:01 UTC) |
| 5 | Đọc tập mốc đã xử lý | Mốc 75% chưa nằm trong tập |

**Pass/Fail Criteria:** ✅ Pass: 1 `escalate_retry` có giờ thử 03:01:00 UTC (= 10:01 VN), mốc chưa xử lý xong; ❌ Fail: thiếu `escalate_retry`, sai giờ, hoặc mốc bị đánh dấu xong

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-021: Không thử lại sớm hơn giờ thử kế tiếp (10:00:59 < 10:01:00) [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-08 |
| Coverage Item | CI-2 (Biên dưới: chạy lúc 10:00:59 (ngay trước retry_at)) |
| Requirement Ref | REQ-FUNC-027 AC1 |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc 75% với `retry` = true, `retry_pattern` = '[1, 10]', action SA-FAIL (luôn lỗi); Server action SA-FAIL (model `res.partner`): luôn ném `UserError('SA-FAIL: boom')`.
4. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
5. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
6. Task attach lúc 07:00 (FX-T0 − 2h) nên mốc 75% đến hạn 10:00

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| retry_at | 10:01:00 |  |
| now kiểm tra | 10:00:59 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = 07:00, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 10:00:00 | `call_count` = 1; 1 dòng retry `retry_at` = 10:01:00 |
| 3 | Xử lý nền tại now = 10:00:59 | `call_count` vẫn = 1; số event `escalate_retry` vẫn = 1; `retry_at` vẫn 10:01:00 |

**Pass/Fail Criteria:** ✅ Pass: không có lần chạy action nào trước 10:01:00; ❌ Fail: action chạy lúc 10:00:59

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-022: Thử lại chạy khi now đúng bằng giờ thử kế tiếp 10:01:00 [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-08 |
| Coverage Item | CI-3 (Biên: chạy đúng retry_at (10:01:00)) |
| Requirement Ref | REQ-FUNC-027 AC1 |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc 75% với `retry` = true, `retry_pattern` = '[1, 10]', action SA-FAIL (luôn lỗi); Server action SA-FAIL (model `res.partner`): luôn ném `UserError('SA-FAIL: boom')`.
4. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
5. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
6. Task attach lúc 07:00 (FX-T0 − 2h) nên mốc 75% đến hạn 10:00

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| retry_at | 10:01:00 |  |
| now kiểm tra | 10:01:00 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = 07:00, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 10:00:00 | `call_count` = 1 |
| 3 | Xử lý nền tại now = 10:01:00 | `call_count` = 2 (action lỗi lần nữa); số event `escalate_retry` = 2; dòng retry mới có `retry_at` = 10:11:00 (10:01 + 10 phút) |

**Pass/Fail Criteria:** ✅ Pass: lần thử lại chạy tại đúng biên 10:01:00; ❌ Fail: không chạy tại 10:01:00

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-023: Lần thử lại chạy trong khoảng 10:01 đến 10:03 với tick cron lệch 30 giây [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-08 |
| Coverage Item | CI-4 (Trễ tick cron: lần thử chạy trong [10:01, 10:03]) |
| Requirement Ref | REQ-FUNC-027 AC1 |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc 75% với `retry` = true, `retry_pattern` = '[1, 10]', action SA-FAIL (luôn lỗi); Server action SA-FAIL (model `res.partner`): luôn ném `UserError('SA-FAIL: boom')`.
4. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
5. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
6. Task attach lúc 07:00 (FX-T0 − 2h) nên mốc 75% đến hạn 10:00

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Chuỗi tick cron | 10:00:00, 10:00:50, 10:01:30, 10:02:30 | mô phỏng bằng 4 lần xử lý nền tại now tương ứng |
| Cửa sổ cho phép | [10:01:00, 10:03:00] | retry_at + 2 phút |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = 07:00, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 10:00:00 rồi Xử lý nền tại now = 10:00:50 | `call_count` = 1 sau tick 10:00:50 (chưa tới giờ) |
| 3 | Xử lý nền tại now = 10:01:30 | `call_count` = 2: lần thử chạy ở tick đầu tiên có now ≥ 10:01:00 và now ≤ 10:03:00 |
| 4 | Đối chiếu now của lần chạy action thứ hai | 10:01:00 ≤ 10:01:30 ≤ 10:03:00 |

**Pass/Fail Criteria:** ✅ Pass: lần thử lại xảy ra ở tick đầu tiên sau 10:01:00 và không muộn quá 10:03:00; ❌ Fail: chạy trước 10:01:00 hoặc sau 10:03:00 khi các tick vẫn đều

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-024: Action của mốc lỗi: ghi escalate_failed một lần, mốc coi là đã xong, không thử lại (D12)

> **Cập nhật 19.0.1.1.0:** sau D12 không còn cơ chế thử lại; ca này kiểm hành vi duy nhất còn lại khi action lỗi (hàm test `test_esc_024_failed_action_marks_done_no_retry`). Các bước dưới đây giữ nguyên từ bản trước; chỗ nhắc `retry`, `retry_pattern` và dòng retry chỉ để đối chiếu và luôn bằng "không có".

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-07 |
| Coverage Item | CI-1 (action lỗi: một `escalate_failed`, không thử lại) |
| Requirement Ref | REQ-FUNC-026 (AC1) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc 75% với `retry` = false, `retry_pattern` rỗng, action SA-FAIL. Server action SA-FAIL (model `res.partner`): luôn ném `UserError('SA-FAIL: boom')`.
4. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
5. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| retry | false |  |
| Lỗi lúc | 12:00 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = FX-T0, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 12:00 | `call_count` = 1 |
| 3 | Đếm event theo loại và dòng `sla.escalation.retry` | `escalate_retry` = 0; `escalate_failed` = 1; số dòng retry = 0 |

**Pass/Fail Criteria:** ✅ Pass: không có `escalate_retry` và không có dòng retry; ❌ Fail: xuất hiện `escalate_retry` hoặc dòng retry

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-025: Ghi escalate_retry rồi escalate khi action lỗi một lần rồi thành công [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-09 |
| Coverage Item | CI-1 (AC1: lỗi một lần rồi thành công) |
| Requirement Ref | REQ-FUNC-056 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc 75% `retry` = true, `retry_pattern` = '[1, 10]', action SA-FLAKY(1)
4. Server action SA-FLAKY(k) (model `res.partner`): k lần gọi đầu ném `UserError('SA-FAIL: boom')`, sau đó gọi `record.message_post(body='OK')` (đếm bằng `call_count`).
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
7. Task attach lúc 07:00; mốc 75% đến hạn 10:00

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| retry_pattern | [1, 10] |  |
| Lần 1 lỗi | 10:00 |  |
| Lần 2 thành công | 10:01 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = 07:00, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 10:00 | 1 event `escalate_retry`; `call_count` = 1 |
| 3 | Xử lý nền tại now = 10:01 | `call_count` = 2; 1 event `escalate` sau event `escalate_retry` (theo `event_dt`/id) |
| 4 | Đếm event và đọc tập mốc đã xử lý, dòng retry | `escalate_retry` = 1, `escalate` = 1, `escalate_failed` = 0; mốc 75% nằm trong tập đã xử lý; số dòng retry = 0 |

**Pass/Fail Criteria:** ✅ Pass: đúng 1 `escalate_retry` rồi 1 `escalate`, mốc đã xử lý; ❌ Fail: thiếu `escalate`, có `escalate_failed`, hoặc mốc chưa xử lý

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-026: Không chạy lại action sau khi thử lại đã thành công [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-09 |
| Coverage Item | CI-2 (AC2: sau khi thành công, chạy nền thêm) |
| Requirement Ref | REQ-FUNC-056 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc 75% `retry` = true, `retry_pattern` = '[1, 10]', action SA-FLAKY(1)
4. Server action SA-FLAKY(k) (model `res.partner`): k lần gọi đầu ném `UserError('SA-FAIL: boom')`, sau đó gọi `record.message_post(body='OK')` (đếm bằng `call_count`).
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
7. Task attach 07:00

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| now bổ sung | 10:02, 10:30, 11:00 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = 07:00, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 10:00; Xử lý nền tại now = 10:01 | `call_count` = 2; `escalate` = 1 |
| 3 | Xử lý nền tại now = 10:02; Xử lý nền tại now = 10:30; Xử lý nền tại now = 11:00 | `call_count` vẫn = 2; `escalate` vẫn = 1; `escalate_retry` vẫn = 1 |

**Pass/Fail Criteria:** ✅ Pass: không có lần gọi action nào sau lần thành công; ❌ Fail: action được gọi lại

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-027: Ghi 2 escalate_retry rồi escalate_failed khi mẫu [1, 10] và action luôn lỗi [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-10 |
| Coverage Item | CI-1 (AC1: mẫu [1,10], action luôn lỗi) |
| Requirement Ref | REQ-FUNC-057 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
4. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
5. Task attach lúc 07:00; mốc 75% đến hạn 10:00
6. Mốc 75% `retry` = true, `retry_pattern` = '[1, 10]', action SA-FAIL. Server action SA-FAIL (model `res.partner`): luôn ném `UserError('SA-FAIL: boom')`.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| retry_pattern | [1, 10] |  |
| Thời điểm các lần gọi | 10:00, 10:01, 10:11 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = 07:00, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 10:00 | `call_count` = 1; `escalate_retry` = 1; `retry_at` = 10:01 |
| 3 | Xử lý nền tại now = 10:01 | `call_count` = 2; `escalate_retry` = 2; `retry_at` = 10:11 |
| 4 | Xử lý nền tại now = 10:11 | `call_count` = 3; `escalate_failed` = 1 với `note` chứa 'SA-FAIL: boom'; số dòng retry = 0; mốc nằm trong tập đã xử lý |
| 5 | Xử lý nền tại now = 11:00; Xử lý nền tại now = 12:00 | `call_count` vẫn = 3; tổng `escalate_retry` = 2, `escalate_failed` = 1, `escalate` = 0 |

**Pass/Fail Criteria:** ✅ Pass: đúng 2 `escalate_retry`, 1 `escalate_failed`, 3 lần gọi action; ❌ Fail: số lần thử khác 2, thiếu `escalate_failed`, hoặc còn thử thêm

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-028: Chỉ thử lại đúng 1 lần với mẫu một phần tử [5] [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-10 |
| Coverage Item | CI-2 (AC2 biên: mẫu [5] → đúng 1 lần thử lại) |
| Requirement Ref | REQ-FUNC-057 AC2 |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
4. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
5. Task attach lúc 07:00; mốc 75% đến hạn 10:00
6. Mốc 75% `retry` = true, `retry_pattern` = '[5]', action SA-FAIL. Server action SA-FAIL (model `res.partner`): luôn ném `UserError('SA-FAIL: boom')`.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| retry_pattern | [5] | biên 1 phần tử |
| Thời điểm | 10:00, 10:05 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = 07:00, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 10:00 | `call_count` = 1; `escalate_retry` = 1; `retry_at` = 10:05 |
| 3 | Xử lý nền tại now = 10:05 | `call_count` = 2; `escalate_failed` = 1; số dòng retry = 0 |
| 4 | Xử lý nền tại now = 11:00 | `call_count` vẫn = 2; `escalate_retry` vẫn = 1 |

**Pass/Fail Criteria:** ✅ Pass: đúng 1 lần thử lại (tổng 2 lần gọi); ❌ Fail: thử lại 0 hoặc từ 2 lần trở lên

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-029: Không ghi escalate_failed khi lần thử lại cuối cùng thành công [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-10 |
| Coverage Item | CI-3 (AC3: lần thử cuối thành công) |
| Requirement Ref | REQ-FUNC-057 AC3 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
4. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
5. Task attach lúc 07:00; mốc 75% đến hạn 10:00
6. Mốc 75% `retry` = true, `retry_pattern` = '[1, 10]', action SA-FLAKY(2). Server action SA-FLAKY(k) (model `res.partner`): k lần gọi đầu ném `UserError('SA-FAIL: boom')`, sau đó gọi `record.message_post(body='OK')` (đếm bằng `call_count`).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| retry_pattern | [1, 10] |  |
| Thời điểm | 10:00 lỗi, 10:01 lỗi, 10:11 thành công |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = 07:00, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 10:00; Xử lý nền tại now = 10:01 | `call_count` = 2; `escalate_retry` = 2 |
| 3 | Xử lý nền tại now = 10:11 | `call_count` = 3; `escalate` = 1; `escalate_failed` = 0; mốc nằm trong tập đã xử lý; số dòng retry = 0 |

**Pass/Fail Criteria:** ✅ Pass: lần thử cuối (thứ 2) thành công → `escalate` = 1 và `escalate_failed` = 0; ❌ Fail: có `escalate_failed`

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-030: Hủy lượt thử lại đang chờ khi task bị stop [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-11 |
| Coverage Item | CI-1 (AC1: task bị stop khi đang chờ thử lại) |
| Requirement Ref | REQ-FUNC-058 AC1 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc 75% `retry` = true, `retry_pattern` = '[1, 10]', action SA-FAIL. Server action SA-FAIL (model `res.partner`): luôn ném `UserError('SA-FAIL: boom')`.
4. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
5. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
6. Task attach 07:00; mốc 75% lỗi lúc 10:00 nên đang chờ thử lại (`retry_at` = 10:01)
7. Cờ `cancel_retry_on_stop` của mốc ('Cancel Retries When Task Stops') giữ giá trị mặc định True (TA-08).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Tác động | ghi `ref` = 'DONE' lúc 10:00:30 | dẫn tới stage `achieved` |
| now kiểm tra | 10:05 | sau retry_at |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = 07:00, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 10:00 | `call_count` = 1; 1 dòng retry `retry_at` = 10:01 |
| 3 | Ghi `ref` = 'DONE', `evaluate(P-1, now = 10:00:30, changed = {ref})` | `stage` = `achieved`; 1 event `complete`; số dòng `sla.escalation.retry` = 0 |
| 4 | Xử lý nền tại now = 10:05 | `call_count` vẫn = 1; không có event `escalate`, `escalate_retry` hay `escalate_failed` mới |

**Pass/Fail Criteria:** ✅ Pass: lượt thử bị hủy và action không chạy lần hai; ❌ Fail: action chạy lần hai hoặc dòng retry còn tồn tại

**Ghi chú:** Ca này kiểm hành vi mặc định (cờ `cancel_retry_on_stop` = True: một cờ chung cho pause, stop, cancel, reset). Hành vi khi cờ = False (dòng retry được giữ và vẫn chạy) kiểm ở TC-ESC-060.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-031: Hủy lượt thử lại đang chờ khi task bị cancel [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-11 |
| Coverage Item | CI-2 (AC2: task bị cancel khi đang chờ thử lại) |
| Requirement Ref | REQ-FUNC-058 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc 75% `retry` = true, `retry_pattern` = '[1, 10]', action SA-FAIL. Server action SA-FAIL (model `res.partner`): luôn ném `UserError('SA-FAIL: boom')`.
4. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
5. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
6. Task attach 07:00; mốc 75% lỗi lúc 10:00 nên đang chờ thử lại (`retry_at` = 10:01)
7. Cờ `cancel_retry_on_stop` của mốc ('Cancel Retries When Task Stops') giữ giá trị mặc định True (TA-08).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Tác động | ghi `ref` = 'CANCEL' lúc 10:00:30 | dẫn tới stage `cancelled` |
| now kiểm tra | 10:05 | sau retry_at |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = 07:00, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 10:00 | `call_count` = 1; 1 dòng retry `retry_at` = 10:01 |
| 3 | Ghi `ref` = 'CANCEL', `evaluate(P-1, now = 10:00:30, changed = {ref})` | `stage` = `cancelled`; 1 event `cancel`; số dòng `sla.escalation.retry` = 0 |
| 4 | Xử lý nền tại now = 10:05 | `call_count` vẫn = 1; không có event `escalate`, `escalate_retry` hay `escalate_failed` mới |

**Pass/Fail Criteria:** ✅ Pass: lượt thử bị hủy và action không chạy lần hai; ❌ Fail: action chạy lần hai hoặc dòng retry còn tồn tại

**Ghi chú:** Ca này kiểm hành vi mặc định (cờ `cancel_retry_on_stop` = True: một cờ chung cho pause, stop, cancel, reset). Hành vi khi cờ = False (dòng retry được giữ và vẫn chạy) kiểm ở TC-ESC-060.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-032: Hủy lượt thử lại đang chờ khi task chuyển paused [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-11 |
| Coverage Item | CI-3 (AC3: task chuyển paused khi đang chờ thử lại) |
| Requirement Ref | REQ-FUNC-058 AC3 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc 75% `retry` = true, `retry_pattern` = '[1, 10]', action SA-FAIL. Server action SA-FAIL (model `res.partner`): luôn ném `UserError('SA-FAIL: boom')`.
4. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
5. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
6. Task attach 07:00; mốc 75% lỗi lúc 10:00 nên đang chờ thử lại (`retry_at` = 10:01)
7. Cờ `cancel_retry_on_stop` của mốc ('Cancel Retries When Task Stops') giữ giá trị mặc định True (TA-08).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Tác động | ghi `ref` = 'HOLD' lúc 10:00:30 | dẫn tới stage `paused` |
| now kiểm tra | 10:05 | sau retry_at |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = 07:00, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 10:00 | `call_count` = 1; 1 dòng retry `retry_at` = 10:01 |
| 3 | Ghi `ref` = 'HOLD', `evaluate(P-1, now = 10:00:30, changed = {ref})` | `stage` = `paused`; 1 event `pause`; số dòng `sla.escalation.retry` = 0 |
| 4 | Xử lý nền tại now = 10:05 | `call_count` vẫn = 1; không có event `escalate`, `escalate_retry` hay `escalate_failed` mới |

**Pass/Fail Criteria:** ✅ Pass: lượt thử bị hủy và action không chạy lần hai; ❌ Fail: action chạy lần hai hoặc dòng retry còn tồn tại

**Ghi chú:** Ca này kiểm hành vi mặc định (cờ `cancel_retry_on_stop` = True: một cờ chung cho pause, stop, cancel, reset). Hành vi khi cờ = False (dòng retry được giữ và vẫn chạy) kiểm ở TC-ESC-060.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-033: Giữ nguyên giờ thử 10:01 của lượt chờ khi sửa mẫu sang [1, 30] [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-12 |
| Coverage Item | CI-1 (AC1: giờ lượt chờ không đổi sau khi sửa mẫu) |
| Requirement Ref | REQ-FUNC-059 AC1 |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc 75% `retry` = true, `retry_pattern` = '[1, 10]', action SA-FAIL. Server action SA-FAIL (model `res.partner`): luôn ném `UserError('SA-FAIL: boom')`.
4. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
5. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
6. Task attach 07:00; lỗi lúc 10:00 nên có lượt chờ `retry_at` = 10:01

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Mẫu cũ | [1, 10] |  |
| Mẫu mới | [1, 30] | sửa lúc 10:00:30 |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = 07:00, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 10:00 | 1 dòng retry, `retry_at` = 10:01:00 |
| 3 | Ghi `retry_pattern` = '[1, 30]' trên mốc 75% (hệ thống coi now = 10:00:30) | Lưu thành công |
| 4 | Đọc dòng retry của (task, mốc) | Vẫn 1 dòng với `retry_at` = 10:01:00 |

**Pass/Fail Criteria:** ✅ Pass: `retry_at` giữ nguyên 10:01:00; ❌ Fail: `retry_at` đổi (ví dụ 10:00:30 + 1 phút hoặc 10:30)

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-034: Tính giờ thử kế tiếp 10:31 theo mẫu mới [1, 30] khi lần thử 10:01 lại lỗi [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-12 |
| Coverage Item | CI-2 (AC2: lần thử kế tiếp theo mẫu mới) |
| Requirement Ref | REQ-FUNC-059 AC2 |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc 75% `retry` = true, `retry_pattern` = '[1, 10]', action SA-FAIL. Server action SA-FAIL (model `res.partner`): luôn ném `UserError('SA-FAIL: boom')`.
4. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
5. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
6. Task attach 07:00; lỗi lúc 10:00 nên có lượt chờ `retry_at` = 10:01

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Mẫu mới | [1, 30] | số phút thứ hai = 30 |
| Lần thử | 10:01 | lỗi lại |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = 07:00, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 10:00 | 1 dòng retry, `retry_at` = 10:01:00 |
| 3 | Ghi `retry_pattern` = '[1, 30]' (now = 10:00:30) | Lưu thành công |
| 4 | Xử lý nền tại now = 10:01 | `call_count` = 2 (lỗi); `escalate_retry` = 2; dòng retry mới có `retry_at` = 10:31:00 |

**Pass/Fail Criteria:** ✅ Pass: `retry_at` = 10:31:00 (10:01 + 30 phút); ❌ Fail: `retry_at` = 10:11:00 (theo mẫu cũ) hoặc giá trị khác 10:31:00

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-035: Từ chối mẫu thử lại rỗng khi bật thử lại [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-13 |
| Coverage Item | CI-1 (AC1: mẫu rỗng) |
| Requirement Ref | REQ-FUNC-028 AC1 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
4. Chưa có mốc escalation nào trên FX-DEF-STD

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| retry | true |  |
| retry_pattern | '' / False / '[]' |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 75, action_id: SA-N75, retry: true, retry_pattern: '' (chuỗi rỗng)} | Bị từ chối bằng `ValidationError`; thông báo chứa "Valid example: [1, 10, 20, 60]." |
| 2 | Tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 75, action_id: SA-N75, retry: true, retry_pattern: False (không có giá trị)} trong savepoint | Bị từ chối bởi ràng buộc CSDL `sla_escalation_retry_check` (`IntegrityError`; thông báo ràng buộc "A retry pattern must be configured when Retry On Failure is enabled."); không có ví dụ mẫu vì lỗi xảy ra ở lớp CSDL |
| 3 | Tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 75, action_id: SA-N75, retry: true, retry_pattern: '[]'} | Bị từ chối bằng `ValidationError`; thông báo chứa "Valid example: [1, 10, 20, 60]." |
| 4 | Đếm `sla.escalation` của FX-DEF-STD | = 0 |

**Pass/Fail Criteria:** ✅ Pass: cả ba giá trị bị từ chối (bước 1 và 3 kèm ví dụ hợp lệ) và không bản ghi nào được lưu; ❌ Fail: có giá trị được lưu hoặc `ValidationError` ở bước 1 hoặc 3 thiếu ví dụ hợp lệ

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-036: Từ chối mẫu thử lại chứa số 0 [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-13 |
| Coverage Item | CI-2 (AC1: mẫu chứa 0) |
| Requirement Ref | REQ-FUNC-028 AC1 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
4. Chưa có mốc escalation nào trên FX-DEF-STD

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| retry | true |  |
| retry_pattern | '[0, 5]' |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 75, action_id: SA-N75, retry: true, retry_pattern: '[0, 5]'} | Bị từ chối bằng `ValidationError`; thông báo chứa "Valid example: [1, 10, 20, 60]." |
| 2 | Đếm `sla.escalation` của FX-DEF-STD | = 0 |

**Pass/Fail Criteria:** ✅ Pass: mọi giá trị bị từ chối kèm ví dụ hợp lệ và không bản ghi nào được lưu; ❌ Fail: có giá trị được lưu hoặc thông báo thiếu ví dụ hợp lệ

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-037: Từ chối mẫu thử lại có số âm [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-13 |
| Coverage Item | CI-3 (AC1: mẫu có số âm) |
| Requirement Ref | REQ-FUNC-028 AC1 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
4. Chưa có mốc escalation nào trên FX-DEF-STD

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| retry | true |  |
| retry_pattern | '[-1]' |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 75, action_id: SA-N75, retry: true, retry_pattern: '[-1]'} | Bị từ chối bằng `ValidationError`; thông báo chứa "Valid example: [1, 10, 20, 60]." |
| 2 | Đếm `sla.escalation` của FX-DEF-STD | = 0 |

**Pass/Fail Criteria:** ✅ Pass: mọi giá trị bị từ chối kèm ví dụ hợp lệ và không bản ghi nào được lưu; ❌ Fail: có giá trị được lưu hoặc thông báo thiếu ví dụ hợp lệ

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-038: Từ chối mẫu thử lại có số không nguyên [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-13 |
| Coverage Item | CI-4 (AC1: mẫu có số không nguyên) |
| Requirement Ref | REQ-FUNC-028 AC1 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
4. Chưa có mốc escalation nào trên FX-DEF-STD

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| retry | true |  |
| retry_pattern | '[1.5]' |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 75, action_id: SA-N75, retry: true, retry_pattern: '[1.5]'} | Bị từ chối bằng `ValidationError`; thông báo chứa "Valid example: [1, 10, 20, 60]." |
| 2 | Đếm `sla.escalation` của FX-DEF-STD | = 0 |

**Pass/Fail Criteria:** ✅ Pass: mọi giá trị bị từ chối kèm ví dụ hợp lệ và không bản ghi nào được lưu; ❌ Fail: có giá trị được lưu hoặc thông báo thiếu ví dụ hợp lệ

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-039: Từ chối mẫu thử lại không phải danh sách ('abc') [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-13 |
| Coverage Item | CI-5 (AC1: mẫu không phải danh sách) |
| Requirement Ref | REQ-FUNC-028 AC1 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
4. Chưa có mốc escalation nào trên FX-DEF-STD

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| retry | true |  |
| retry_pattern | 'abc' |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 75, action_id: SA-N75, retry: true, retry_pattern: 'abc'} | Bị từ chối bằng `ValidationError`; thông báo chứa "Valid example: [1, 10, 20, 60]." |
| 2 | Đếm `sla.escalation` của FX-DEF-STD | = 0 |

**Pass/Fail Criteria:** ✅ Pass: mọi giá trị bị từ chối kèm ví dụ hợp lệ và không bản ghi nào được lưu; ❌ Fail: có giá trị được lưu hoặc thông báo thiếu ví dụ hợp lệ

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-040: Từ chối mẫu thử lại 11 phần tử (vượt biên trên 10) [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-13 |
| Coverage Item | CI-6 (AC1 biên: 11 phần tử) |
| Requirement Ref | REQ-FUNC-028 AC1 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
4. Chưa có mốc escalation nào trên FX-DEF-STD

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| retry | true |  |
| retry_pattern | '[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]' |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 75, action_id: SA-N75, retry: true, retry_pattern: '[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]'} | Bị từ chối bằng `ValidationError`; thông báo chứa "Valid example: [1, 10, 20, 60]." |
| 2 | Đếm `sla.escalation` của FX-DEF-STD | = 0 |

**Pass/Fail Criteria:** ✅ Pass: mọi giá trị bị từ chối kèm ví dụ hợp lệ và không bản ghi nào được lưu; ❌ Fail: có giá trị được lưu hoặc thông báo thiếu ví dụ hợp lệ

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-041: Chấp nhận mẫu thử lại hợp lệ [1, 10, 20, 60] [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-13 |
| Coverage Item | CI-7 (AC2: mẫu hợp lệ [1, 10, 20, 60]) |
| Requirement Ref | REQ-FUNC-028 AC2 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
4. Chưa có mốc escalation nào trên FX-DEF-STD

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| retry | true |  |
| retry_pattern | '[1, 10, 20, 60]' |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 75, action_id: SA-N75, retry: true, retry_pattern: '[1, 10, 20, 60]'} | Tạo thành công, không lỗi |
| 2 | Đọc lại bản ghi | `retry_pattern` = '[1, 10, 20, 60]'; số mốc của FX-DEF-STD = 1 |

**Pass/Fail Criteria:** ✅ Pass: bản ghi được lưu với đúng mẫu; ❌ Fail: bị từ chối hoặc mẫu bị đổi

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-042: Chấp nhận mẫu thử lại 10 phần tử (biên trên) [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-13 |
| Coverage Item | CI-8 (AC2 biên: 10 phần tử) |
| Requirement Ref | REQ-FUNC-028 AC2 |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
4. Chưa có mốc escalation nào trên FX-DEF-STD

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| retry | true |  |
| retry_pattern | '[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]' |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 75, action_id: SA-N75, retry: true, retry_pattern: '[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]'} | Tạo thành công, không lỗi |
| 2 | Đọc lại bản ghi | `retry_pattern` = '[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]'; số mốc của FX-DEF-STD = 1 |

**Pass/Fail Criteria:** ✅ Pass: bản ghi được lưu với đúng mẫu; ❌ Fail: bị từ chối hoặc mẫu bị đổi

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-043: Không kiểm tra mẫu khi tắt thử lại (retry = false) [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-13 |
| Coverage Item | CI-9 (Statement: retry = false không kiểm tra mẫu) |
| Requirement Ref | REQ-FUNC-028 |
| Priority | P4-Low |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
4. Chưa có mốc escalation nào trên FX-DEF-STD

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| retry | false |  |
| retry_pattern | 'abc' | D5/TA-10 đã chốt: không kiểm `retry_pattern` khi `retry` = false |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 75, action_id: SA-N75, retry: false, retry_pattern: 'abc'} | Tạo thành công, không lỗi |
| 2 | Đọc lại bản ghi | `retry_pattern` = 'abc'; số mốc của FX-DEF-STD = 1 |

**Pass/Fail Criteria:** ✅ Pass: bản ghi được lưu với đúng mẫu; ❌ Fail: bị từ chối hoặc mẫu bị đổi

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-044: Từ chối lưu mốc có server action thuộc model res.users trên định nghĩa res.partner

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-14 |
| Coverage Item | CI-1 (AC1: server action của res.users trên định nghĩa res.partner) |
| Requirement Ref | REQ-FUNC-038 AC1 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Server action SA-USER thuộc model `res.users` (code: `pass`)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| definition_id | FX-DEF-STD (res.partner) |  |
| action_id | SA-USER (res.users) |  |
| percent | 75 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 75, action_id: SA-USER} | Bị từ chối (`ValidationError`); thông báo chứa cả 'res.partner' và 'res.users' |
| 2 | Đếm `sla.escalation` của FX-DEF-STD | = 0 |

**Pass/Fail Criteria:** ✅ Pass: bị từ chối và thông báo chứa đủ hai tên model; ❌ Fail: lưu thành công hoặc thông báo thiếu một trong hai model

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-045: Chấp nhận lưu mốc có server action thuộc model res.partner

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-14 |
| Coverage Item | CI-2 (AC2: server action của res.partner) |
| Requirement Ref | REQ-FUNC-038 AC2 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| definition_id | FX-DEF-STD (res.partner) |  |
| action_id | SA-N75 (res.partner) |  |
| percent | 75 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 75, action_id: SA-N75} | Tạo thành công |
| 2 | Đếm `sla.escalation` của FX-DEF-STD | = 1 |

**Pass/Fail Criteria:** ✅ Pass: mốc được lưu; ❌ Fail: bị từ chối

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-046: Không bắn bù mốc 75% thêm vào khi task đã ở 80%

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-15 |
| Coverage Item | CI-1 (AC1: thêm mốc 75% khi task đang ở 80%) |
| Requirement Ref | REQ-FUNC-053 AC1 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc ban đầu duy nhất: Mốc escalation 100% (`percent` = 100, `action_id` = SA-N100, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`. Server action SA-N90 (model `res.partner`): code `record.message_post(body='N90')`. Server action SA-N100 (model `res.partner`): code `record.message_post(body='N100')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
7. Task attach lúc FX-T0; tại 12:12 task đã trôi 3,2 giờ (80%)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Thời điểm thêm mốc | 12:12 | 80% của 4 giờ |
| Mốc thêm | 75%, SA-N75 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = FX-T0, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Với patch `odoo.fields.Datetime.now` trả 12:12 giờ VN: tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 75, action_id: SA-N75} | Lưu thành công; mốc 75% nằm trong `done_escalation_ids` của task và không có event nào được ghi (D4: mốc đã vượt chèn vào tập đã xử lý) |
| 3 | Xử lý nền tại now = 12:12 | `call_count` SA-N75 = 0; 0 event `escalate` |
| 4 | Xử lý nền tại now = 13:00 | `call_count` SA-N100 = 1; `call_count` SA-N75 = 0 |
| 5 | Xử lý nền tại now = 14:00 | `call_count` SA-N75 vẫn = 0; không có event `escalate` nào ứng với mốc 75% |

**Pass/Fail Criteria:** ✅ Pass: mốc 75% không bắn ở bất kỳ lần xử lý nào; ❌ Fail: SA-N75 được gọi

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-047: Bắn mốc 90% thêm vào khi task tới 90% (12:36)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-15 |
| Coverage Item | CI-2 (AC2: thêm mốc 90% khi task đang ở 80%) |
| Requirement Ref | REQ-FUNC-053 AC2 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc ban đầu duy nhất: Mốc escalation 100% (`percent` = 100, `action_id` = SA-N100, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`. Server action SA-N90 (model `res.partner`): code `record.message_post(body='N90')`. Server action SA-N100 (model `res.partner`): code `record.message_post(body='N100')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
7. Task attach lúc FX-T0; tại 12:12 task đã trôi 3,2 giờ (80%)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Thời điểm thêm mốc | 12:12 | 80% |
| Mốc thêm | 90%, SA-N90 | đến hạn 12:36 |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = FX-T0, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Với patch `odoo.fields.Datetime.now` trả 12:12 giờ VN (`sla.escalation.create` đọc đồng hồ qua hàm này): tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 90, action_id: SA-N90} | Lưu thành công; mốc 90% KHÔNG nằm trong `done_escalation_ids` của task (chưa tới mức); `next_due_at` của task = 12:36 (D4/TA-07 đã chốt: thêm mốc thì tính lại `next_due_at`) |
| 3 | Xử lý nền tại now = 12:35 (`_process_task` không bắn vì phần trăm 87,5% < 90%) | `call_count` SA-N90 = 0 |
| 4 | Xử lý nền tại now = 12:36 | `call_count` SA-N90 = 1; 1 event `escalate`; chatter có ghi chú 'N90' |

**Ghi chú:** Khi đối chiếu code ngày 2026-10-12, `sla_escalation.create` chỉ chèn mốc đã vượt vào `done_escalation_ids` và chưa gọi tính lại `next_due_at` cho mốc chưa tới; code đã sửa (TASKS T13): `create` tính lại `next_due_at` cho mốc chưa tới nên bước 2 kỳ vọng `next_due_at` = 12:36 (TA-24 ĐÃ SỬA).

**Pass/Fail Criteria:** ✅ Pass: mốc 90% bắn đúng 12:36; ❌ Fail: không bắn hoặc bắn sai thời điểm

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-048: Truyền đúng active_model, active_id, active_ids và ghi chú nằm trên record gốc

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-16 |
| Coverage Item | CI-1 (AC1: ghi chú xuất hiện trên đúng record gốc) |
| Requirement Ref | REQ-INT-008 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-CTX, `retry` = false).
4. Server action SA-CTX (model `res.partner`): code lưu `(env.context.get('active_model'), env.context.get('active_id'), env.context.get('active_ids'))` vào danh sách `ctx_log` rồi `env[env.context['active_model']].browse(env.context['active_id']).message_post(body='ESC-%s' % env.context['active_id'])`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Record gốc | P-1 | id = P-1.id |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P-1, now = FX-T0, changed = ∅)` với `P-1.ref` = 'NEW' (hàm `evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` |
| 2 | Xử lý nền tại now = 12:00 | `ctx_log` có đúng 1 phần tử |
| 3 | Đối chiếu `ctx_log[0]` | = ('res.partner', P-1.id, [P-1.id]) |
| 4 | Đọc chatter của P-1 | Có đúng 1 ghi chú 'ESC-<P-1.id>' |

**Pass/Fail Criteria:** ✅ Pass: ngữ cảnh và vị trí ghi chú đều đúng; ❌ Fail: thiếu khóa ngữ cảnh, sai id, hoặc ghi chú nằm trên record khác

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-049: Không lẫn ghi chú giữa hai record cùng đến hạn

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-16 |
| Coverage Item | CI-2 (AC2: hai record cùng đến hạn, ghi chú không lẫn) |
| Requirement Ref | REQ-INT-008 AC2 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-CTX, `retry` = false).
4. Server action SA-CTX (model `res.partner`): code lưu `(env.context.get('active_model'), env.context.get('active_id'), env.context.get('active_ids'))` vào danh sách `ctx_log` rồi `env[env.context['active_model']].browse(env.context['active_id']).message_post(body='ESC-%s' % env.context['active_id'])`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') tạo xong, chưa có task SLA.
7. Partner P-2 (`ref` = 'NEW') tạo xong, chưa có task SLA.
8. Cả hai task attach lúc FX-T0

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Record | P-1 và P-2 | cùng mốc 75% đến hạn 12:00 |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Xử lý nền tại now = 12:00 | `ctx_log` có 2 phần tử, mỗi phần tử `active_ids` có đúng 1 id |
| 2 | Đọc chatter của P-1 | Đúng 1 ghi chú 'ESC-<P-1.id>'; không có 'ESC-<P-2.id>' |
| 3 | Đọc chatter của P-2 | Đúng 1 ghi chú 'ESC-<P-2.id>'; không có 'ESC-<P-1.id>' |

**Pass/Fail Criteria:** ✅ Pass: mỗi record chỉ có ghi chú của chính nó; ❌ Fail: ghi chú nằm sai record hoặc `active_ids` chứa nhiều id

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-050: Chạy action trong công ty của record (CO-B) khi user cron được cấp cả CO-A và CO-B

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-17 |
| Coverage Item | CI-1 (AC1: U-CRON có quyền A và B) |
| Requirement Ref | REQ-INT-019 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7). `company_id` của định nghĩa = NULL (mọi công ty).
3. FX-CO: công ty CO-A và CO-B
4. Partner P-B (`ref` = 'NEW') tạo xong, chưa có task SLA. thuộc CO-B (`company_id` = CO-B).
5. Task của P-B attach lúc FX-T0, `company_id` của task = CO-B
6. Mốc escalation 75% (`percent` = 75, `action_id` = SA-CO, `retry` = false).
7. Server action SA-CO (model `res.partner`): code `record.write({'comment': 'CO=%s' % env.company.id})`
8. U-CRON có `company_ids` = {CO-A, CO-B}, công ty mặc định CO-A; xử lý nền chạy bằng U-CRON

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| U-CRON.company_ids | CO-A, CO-B | FX-CO |
| Công ty của P-B | CO-B |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi `env['sla.processor'].with_user(U-CRON).process_due()` (đường chạy thật của cron) với patch `odoo.fields.Datetime.now` trả 12:00 giờ VN và `fake_progress` | Không có ngoại lệ |
| 2 | Đọc `P-B.comment` | = 'CO=<CO-B.id>' (action chạy với `env.company` = CO-B) |
| 3 | Đếm event của task | `escalate` = 1; `escalate_failed` = 0 |

**Pass/Fail Criteria:** ✅ Pass: action chạy trong CO-B và ghi được vào P-B; ❌ Fail: action chạy với CO-A, bị từ chối quyền, hoặc không ghi được

**Ghi chú:** (TA-33) trước đây `process_due()` đọc task bằng `sudo()` nên server action chạy với quyền superuser thay vì quyền user cron/công ty; ca viết theo kết quả SRS (REQ-SEC-004, REQ-INT-019); code đã sửa (TASKS T13): server action của escalation chạy theo quyền user nền và công ty của record (TA-33 ĐÃ SỬA).

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-051: Ghi đúng 1 escalate_failed lỗi quyền khi user cron không có quyền công ty của record

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-17 |
| Coverage Item | CI-2 (AC2: U-CRON chỉ có CO-A, mốc không bật thử lại) |
| Requirement Ref | REQ-INT-019 AC2 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7). `company_id` của định nghĩa = NULL (mọi công ty).
3. FX-CO: công ty CO-A và CO-B
4. Partner P-B (`ref` = 'NEW') tạo xong, chưa có task SLA. thuộc CO-B (`company_id` = CO-B).
5. Task của P-B attach lúc FX-T0, `company_id` của task = CO-B
6. Mốc escalation 75% (`percent` = 75, `action_id` = SA-CO, `retry` = false).
7. Server action SA-CO (model `res.partner`): code `record.write({'comment': 'SA-CO'})`
8. U-CRON-A có `company_ids` = {CO-A} (không có CO-B); xử lý nền chạy bằng U-CRON-A
9. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| U-CRON-A.company_ids | CO-A | không có CO-B |
| retry | false |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi `env['sla.processor'].with_user(U-CRON-A).process_due()` (đường chạy thật của cron) với patch `odoo.fields.Datetime.now` trả 12:00 giờ VN và `fake_progress` | Không ném ngoại lệ ra ngoài |
| 2 | Đọc event của task | Đúng 1 event `escalate_failed` có `note` không rỗng nêu lỗi quyền truy cập: `note` chứa 'access' (không phân biệt hoa thường; code lưu `str(exc)` của lỗi gốc Odoo, không thuộc `constants/message.py`); 0 event `escalate` |
| 3 | Đọc `P-B.comment` | Không đổi (rỗng): action không thực thi được |
| 4 | Gọi `process_due()` như bước 1 với patch now = 12:01 rồi lại với now = 13:00 | Số event `escalate_failed` vẫn = 1; `P-B.comment` vẫn rỗng; không event mới |

**Pass/Fail Criteria:** ✅ Pass: đúng 1 `escalate_failed` lỗi quyền và không chạy lại ở chu kỳ sau; ❌ Fail: 0 hoặc ≥ 2 event `escalate_failed`, hoặc action chạy lại

**Ghi chú:** (TA-33) trước đây `process_due()` đọc task bằng `sudo()` nên server action chạy với quyền superuser thay vì quyền user cron/công ty; ca viết theo kết quả SRS (REQ-SEC-004, REQ-INT-019); code đã sửa (TASKS T13): server action của escalation chạy theo quyền user nền và công ty của record (TA-33 ĐÃ SỬA).

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-052: Ghi escalate_retry thay cho escalate_failed ở lần lỗi quyền đầu tiên khi mốc bật thử lại [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-17 |
| Coverage Item | CI-3 (AC2 nhánh retry: U-CRON chỉ có CO-A, mốc bật thử lại) |
| Requirement Ref | REQ-INT-019 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7). `company_id` của định nghĩa = NULL (mọi công ty).
3. FX-CO: công ty CO-A và CO-B
4. Partner P-B (`ref` = 'NEW') tạo xong, chưa có task SLA. thuộc CO-B (`company_id` = CO-B).
5. Task của P-B attach lúc FX-T0, `company_id` của task = CO-B
6. Mốc escalation 75% (`percent` = 75, `action_id` = SA-CO, `retry` = true, `retry_pattern` = '[1]').
7. Server action SA-CO (model `res.partner`): code `record.write({'comment': 'SA-CO'})`
8. U-CRON-A có `company_ids` = {CO-A}; xử lý nền chạy bằng U-CRON-A

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| U-CRON-A.company_ids | CO-A |  |
| retry_pattern | [1] |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi `env['sla.processor'].with_user(U-CRON-A).process_due()` (đường chạy thật của cron) với patch `odoo.fields.Datetime.now` trả 12:00 giờ VN và `fake_progress` | Không ném ngoại lệ ra ngoài |
| 2 | Đếm event của task | `escalate_retry` = 1 (note nêu lỗi quyền); `escalate_failed` = 0 |

**Pass/Fail Criteria:** ✅ Pass: lần lỗi đầu ghi `escalate_retry` và không ghi `escalate_failed`; ❌ Fail: ghi `escalate_failed` ngay lần đầu

**Ghi chú:** (TA-33) trước đây `process_due()` đọc task bằng `sudo()` nên server action chạy với quyền superuser thay vì quyền user cron/công ty; ca viết theo kết quả SRS (REQ-SEC-004, REQ-INT-019); code đã sửa (TASKS T13): server action của escalation chạy theo quyền user nền và công ty của record (TA-33 ĐÃ SỬA).

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-053: Báo tiến độ từng task qua ba lần gọi `process_due()` với 120 task đến hạn và lô 50: số còn lại cuối mỗi lần gọi là 70, 20, 0

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-18 |
| Coverage Item | CI-1 (AC1: 120 task, lô 50, ba lần gọi, số còn lại cuối mỗi lần gọi 70, 20, 0) |
| Requirement Ref | REQ-REL-002 AC1 |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. `fake_progress` thay `ir.cron._commit_progress`: ghi lại mỗi lần gọi dưới dạng (processed, remaining) và trả về thời gian còn lại giả lập (mặc định 100 giây).
7. Tham số `dwo_sla_core.batch_size` không đặt (mặc định 50).
8. 120 partner, mỗi partner có 1 task attach lúc FX-T0 (mốc 75% đến hạn 12:00, `next_due_at` = 12:00 giờ VN).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Số task đến hạn | 120 |  |
| batch_size | 50 (mặc định) | trần mỗi lần gọi |
| Thời điểm | 12:00 giờ VN | patch `odoo.fields.Datetime.now` trả FX-T0 + 3h (12:00 giờ VN = 05:00 UTC) |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với patch `odoo.fields.Datetime.now` trả FX-T0 + 3h (12:00 giờ VN = 05:00 UTC): gọi `process_due()` lần 1 | `fake_progress` được gọi đúng 50 lần, mỗi lần có processed = 1; giá trị remaining giảm dần 119, 118, ..., 70 (lần gọi thứ 50 báo remaining = 70); đúng 50 task có 1 event `escalate` |
| 2 | Gọi `process_due()` lần 2 | `fake_progress` ghi thêm 50 lần, remaining 69, ..., 20; tổng 100 task có 1 event `escalate`; `call_count` của 50 task ở lần 1 vẫn = 1 |
| 3 | Gọi `process_due()` lần 3 | `fake_progress` ghi thêm 20 lần, remaining 19, ..., 0 (lần gọi cuối báo remaining = 0); tổng 120 task có đúng 1 event `escalate` |
| 4 | Đọc danh sách tham số của `fake_progress` | Tổng 120 lần gọi; mọi lần processed = 1; dãy remaining = [119, 118, ..., 0] giảm đúng 1 mỗi lần |

**Pass/Fail Criteria:** ✅ Pass: số lần báo tiến độ mỗi lần gọi là 50, 50, 20 với remaining cuối là 70, 20, 0 và mỗi task bắn đúng 1 lần; ❌ Fail: một lần gọi xử lý nhiều hơn 50 task, dãy remaining lệch, hoặc task bị bắn lặp hay sót

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-054: Chạy lại sau khi bị dừng ngay sau task thứ nhất: task đó không bị xử lý lại, hai task còn lại được xử lý

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-18 |
| Coverage Item | CI-2 (AC2: dừng sau task thứ nhất rồi chạy lại) |
| Requirement Ref | REQ-REL-002 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. `fake_progress` lần gọi đầu ném `InterruptedError` ngay sau khi ghi tham số (mô phỏng tiến trình bị dừng sau khi task thứ nhất đã báo tiến độ); các lần gọi sau không ném.
7. Tham số `dwo_sla_core.batch_size` = 50 (mặc định).
8. 3 partner P-1..P-3, mỗi partner có 1 task attach lúc FX-T0 (mốc 75% cùng đến hạn 12:00).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Số task đến hạn | 3 |  |
| Thời điểm | 12:00 giờ VN | patch `odoo.fields.Datetime.now` trả FX-T0 + 3h (12:00 giờ VN = 05:00 UTC) |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với patch `odoo.fields.Datetime.now` trả FX-T0 + 3h (12:00 giờ VN = 05:00 UTC): gọi `process_due()` lần 1 | Ném `InterruptedError` ở lần báo tiến độ đầu tiên; `fake_progress` ghi [(1, 2)] |
| 2 | Bắt `InterruptedError` (giao dịch của test không bị rollback, mô phỏng kết quả task thứ nhất đã lưu); đọc event `escalate` của P-1..P-3 sau `invalidate_all()` | Đúng 1 task (gọi là T-a) có 1 event `escalate`; hai task còn lại có 0 event; không khẳng định task nào được xử lý trước (thứ tự khi cùng `next_due_at` không xác định) |
| 3 | Bỏ ngắt giả lập; gọi `process_due()` lần 2 | `fake_progress` ghi thêm (1, 1) rồi (1, 0); `call_count` của T-a vẫn = 1 |
| 4 | Đọc event `escalate` của P-1..P-3 | Mỗi task đúng 1 event `escalate`; mỗi record `call_count` = 1 |

**Pass/Fail Criteria:** ✅ Pass: task thứ nhất giữ kết quả và không bị xử lý lại, hai task còn lại được xử lý ở lần chạy sau, không bắn lặp; ❌ Fail: task thứ nhất bị xử lý lại, hoặc task còn lại bị bỏ sót

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-055: Thời gian còn lại của lần chạy bằng 0 sau task đầu tiên: chỉ 1 task được xử lý trong lần gọi và số còn lại báo 99

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-18 |
| Coverage Item | CI-3 (AC4: hết thời gian còn lại thì dừng, remaining = 99) |
| Requirement Ref | REQ-REL-002 AC4 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. `fake_progress` trả về thời gian còn lại = 0 ở mọi lần gọi (ngân sách thời gian của lần chạy đã hết).
7. Tham số `dwo_sla_core.batch_size` = 50 (mặc định).
8. 100 partner, mỗi partner có 1 task attach lúc FX-T0 (mốc 75% đến hạn 12:00).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Số task đến hạn | 100 |  |
| Thời gian còn lại giả lập | 0 |  |
| Thời điểm | 12:00 giờ VN | patch `odoo.fields.Datetime.now` trả FX-T0 + 3h (12:00 giờ VN = 05:00 UTC) |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với patch `odoo.fields.Datetime.now` trả FX-T0 + 3h (12:00 giờ VN = 05:00 UTC): gọi `process_due()` một lần | Hoàn tất, không ném lỗi |
| 2 | Đọc tham số `fake_progress` | Gọi đúng 1 lần với (processed = 1, remaining = 99) |
| 3 | Đếm task có event `escalate` và task `in_progress` còn `next_due_at <= 12:00` | Đúng 1 task có event `escalate`; 99 task còn lại có 0 event `escalate` và vẫn đến hạn |

**Pass/Fail Criteria:** ✅ Pass: chỉ 1 task được xử lý và báo remaining = 99; ❌ Fail: xử lý từ 2 task trở lên trong lần gọi, hoặc remaining khác 99

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-056: Từ chối kích thước lô bằng 0

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-18 |
| Coverage Item | CI-4 (AC3: batch_size = 0) |
| Requirement Ref | REQ-REL-002 AC3 |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Tham số `dwo_sla_core.batch_size` = 50 (đang lưu)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| batch_size mới | 0 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | SLA Manager lưu `dwo_sla_core.batch_size` = 0 qua màn hình Settings của module (`res.config.settings`, field `sla_batch_size`) | Bị từ chối bằng `ValidationError` có nội dung chứa "batch size" |
| 2 | Đọc `ir.config_parameter` `dwo_sla_core.batch_size` | Vẫn = '50' |

**Pass/Fail Criteria:** ✅ Pass: bị từ chối và giá trị cũ giữ nguyên; ❌ Fail: giá trị được lưu

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-057: Từ chối kích thước lô âm

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-18 |
| Coverage Item | CI-5 (AC3: batch_size âm (-5)) |
| Requirement Ref | REQ-REL-002 AC3 |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Tham số `dwo_sla_core.batch_size` = 50 (đang lưu)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| batch_size mới | -5 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | SLA Manager lưu `dwo_sla_core.batch_size` = -5 qua màn hình Settings của module (`res.config.settings`, field `sla_batch_size`) | Bị từ chối bằng `ValidationError` có nội dung chứa "batch size" |
| 2 | Đọc `ir.config_parameter` `dwo_sla_core.batch_size` | Vẫn = '50' |

**Pass/Fail Criteria:** ✅ Pass: bị từ chối và giá trị cũ giữ nguyên; ❌ Fail: giá trị được lưu

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-058: Chấp nhận kích thước lô bằng 1 (biên hợp lệ nhỏ nhất)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-18 |
| Coverage Item | CI-6 (Biên hợp lệ: batch_size = 1) |
| Requirement Ref | REQ-REL-002 AC3 |
| Priority | P3-Medium |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Tham số `dwo_sla_core.batch_size` = 50 (đang lưu)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| batch_size mới | 1 | biên hợp lệ nhỏ nhất |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | SLA Manager lưu `dwo_sla_core.batch_size` = 1 qua màn hình Settings của module (`res.config.settings`, field `sla_batch_size`) | Không ném lỗi |
| 2 | Đọc `ir.config_parameter` `dwo_sla_core.batch_size` | = '1' (chuỗi) |

**Pass/Fail Criteria:** ✅ Pass: giá trị 1 được lưu; ❌ Fail: bị từ chối

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ESC-059: Stop task T2 trong lúc xử lý nền đang chạy server action chậm trên task T1: lần lưu không phải chờ T1

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-18 |
| Coverage Item | CI-7 (AC5: stop task khác không phải chờ task đang xử lý) |
| Requirement Ref | REQ-REL-002 AC5 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (hai cursor, không dùng TransactionCase đơn) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-SLOW, `retry` = false); stop khi `ref` = 'DONE'.
4. Server action SA-SLOW: khi được gọi thì chặn lại tại điểm đồng bộ của test (giữ giao dịch của C1 mở, mô phỏng chạy 30 giây) mà không dùng `sleep`.
5. Hai partner P-1, P-2 (`ref` = 'NEW') đã commit, mỗi partner có 1 task (T1, T2) attach lúc FX-T0; `next_due_at` của T1 sớm hơn của T2 (T1 đến hạn 12:00, T2 đến hạn 12:01) để C1 xử lý T1 trước.
6. Cursor C1 (xử lý nền, `process_due()`), C2 (U-BIZ ghi record) và C3 (chỉ dò khóa), mỗi cursor một giao dịch riêng; `odoo.fields.Datetime.now` được patch trả 12:01 giờ VN ở cả ba.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Task đang xử lý (bị khóa) | T1 |  |
| Task bị stop | T2 | chưa bị khóa |
| Ngưỡng chờ | 5 giây | đo bằng `time.monotonic()` |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | C1: gọi `process_due()` tới khi SA-SLOW chặn (C1 giữ khóa dòng T1, chưa commit) | C1 đang giữ giao dịch mở; `call_count` SA-SLOW của P-1 = 1 |
| 2 | C3 (trước khi C2 ghi gì): `SELECT id FROM sla_task WHERE id = T2 FOR UPDATE NOWAIT`, rồi rollback C3; sau đó cùng truy vấn với T1 trong giao dịch mới của C3 | Với T2: thành công, không lỗi khóa (T2 chưa bị C1 khóa); với T1: lỗi khóa (`LockNotAvailable`) |
| 3 | C2: ghi P-2 {ref: 'DONE'} (hook gọi `evaluate`) rồi commit, đo thời gian của lệnh ghi và commit | Hoàn tất trong dưới 5 giây khi C1 vẫn chưa commit; T2 `stage` = `achieved`, 1 event `complete` |
| 4 | Giải phóng SA-SLOW, C1 commit; đọc trạng thái cuối bằng cursor mới | T1 có đúng 1 event `escalate`; T2 `achieved` với đúng 1 event `complete` và 0 event `escalate` |

**Pass/Fail Criteria:** ✅ Pass: lệnh stop T2 hoàn tất và commit trước khi C1 commit, T2 không bị khóa; ❌ Fail: lệnh stop T2 phải chờ C1 (>= 5 giây hoặc chặn tới khi C1 kết thúc)

**Postconditions:** Dữ liệu đã commit bởi các cursor: dọn trong `tearDown`.

### TC-ESC-060: Giữ lượt thử lại đang chờ và vẫn chạy khi cờ `cancel_retry_on_stop` = False (pause, stop, cancel, reset) [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-08-11 |
| Coverage Item | CI-4 (cờ `cancel_retry_on_stop` = False: pause, stop, cancel, reset đều giữ lượt thử) |
| Requirement Ref | REQ-FUNC-058 (mở rộng theo TA-08), REQ-FUNC-054 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7). Với biến thể reset: `start` gồm `ref` in ('NEW', 'RESET') và `reset` là `ref` = 'RESET' (reset_action mặc định `cancel`).
3. Mốc 75% `retry` = true, `retry_pattern` = '[1, 10]', `cancel_retry_on_stop` = False, action SA-FAIL. Server action SA-FAIL (model `res.partner`): luôn ném `UserError('SA-FAIL: boom')`.
4. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`.
5. Với mỗi biến thể dưới đây dựng lại partner P-1 (`ref` = 'NEW') và task mới, task attach 07:00; mốc 75% lỗi lúc 10:00 nên đang chờ thử lại (`retry_at` = 10:01).

**Test Data:**
| Biến thể | Ghi `ref` lúc 10:00:30 | `stage` của task cũ sau đó |
|---|---|---|
| stop | 'DONE' | `achieved` |
| cancel | 'CANCEL' | `cancelled` |
| pause | 'HOLD' | `paused` |
| reset | 'RESET' | `cancelled` (task mới được gắn) |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Xử lý nền tại now = 10:00 | `call_count` = 1; đúng 1 dòng retry của task, `retry_at` = 10:01 |
| 2 | Ghi `ref` theo biến thể, `evaluate(P-1, now = 10:00:30, changed = {ref})` | `stage` của task cũ theo bảng trên; số dòng `sla.escalation.retry` của task cũ vẫn = 1 (không bị xóa) |
| 3 | Xử lý nền tại now = 10:05 | Lượt thử chạy dù task không còn `in_progress`: `call_count` = 2; tổng event `escalate_retry` = 2; còn 1 dòng retry (mẫu [1, 10] đặt `retry_at` kế tiếp = 10:15) |
| 4 | Xử lý nền tại now = 10:20 | `call_count` = 3; đúng 1 event `escalate_failed`, 0 event `escalate`; số dòng retry = 0 |

**Pass/Fail Criteria:** ✅ Pass: cả bốn biến thể giữ dòng retry sau thao tác và lượt thử chạy tiếp tới `escalate_failed` với đúng 3 lần gọi action; ❌ Fail: dòng retry bị xóa, action không chạy lại, hoặc số lần gọi khác 3

**Ghi chú:** Quyết định đã chốt (TA-08): cờ `cancel_retry_on_stop` (mặc định True) là một cờ chung cho pause, stop, cancel, reset; với False, tiến trình nền vẫn chạy lượt thử cho task không còn `in_progress`, nhưng KHÔNG bắn mốc mới trên task không `in_progress` (REQ-FUNC-054 không đổi). Khớp `tests/test_tg08_more.py::test_esc_030b_flag_off_keeps_retries`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

## TG-09 — Nhiều SLA song song

### TC-MUL-001: Gắn hai task độc lập khi hai định nghĩa cùng khớp một record

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-09-01 |
| Coverage Item | CI-1 (hai định nghĩa cùng khớp -> 2 task độc lập) |
| Requirement Ref | REQ-FUNC-014 (AC1, nửa đầu) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Hai định nghĩa trên `res.partner`: `D-RESP` (mục tiêu 1 giờ; start `ref ∈ {NEW,WORK,HOLD,DONE}`; stop `ref='RESPONDED'`) và `D-RES` (mục tiêu 4 giờ; start `ref ∈ {NEW,WORK,HOLD,DONE}`; stop `ref='DONE'`); cả hai schedule_source=none, cancel_mode=`start_unmatched`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref | NEW |  |
| now | T0 (09:00) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Không ngoại lệ |
| 2 | Đọc task của `P-01` theo định nghĩa | 2 task: `D-RESP` `in_progress` (`planned_end_time`=10:00) và `D-RES` `in_progress` (`planned_end_time`=13:00) |
| 3 | Đếm event `attach` theo task | Mỗi task đúng 1 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Hai task độc lập, mỗi định nghĩa đúng một. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-MUL-002: Giữ nguyên task response khi stop của resolution khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-09-01 |
| Coverage Item | CI-2 (stop của D-RES không đổi task D-RESP) |
| Requirement Ref | REQ-FUNC-014 (AC1, nửa sau) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Hai định nghĩa trên `res.partner`: `D-RESP` (mục tiêu 1 giờ; start `ref ∈ {NEW,WORK,HOLD,DONE}`; stop `ref='RESPONDED'`) và `D-RES` (mục tiêu 4 giờ; start `ref ∈ {NEW,WORK,HOLD,DONE}`; stop `ref='DONE'`); cả hai schedule_source=none, cancel_mode=`start_unmatched`
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref (bước 2) | DONE | chỉ stop của `D-RES` khớp |
| now bước 2 | T0+30m = 09:30 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 2 task `in_progress`; ghi lại số event của task `D-RESP` (=1) và `write_date` |
| 2 | Đặt `ref`='DONE' (G1); Gọi Engine đánh giá `P-01` với now = T0+30m (09:30), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Không ngoại lệ |
| 3 | Đọc task `D-RES` | `stage`='achieved', `end_time`=09:30 |
| 4 | Đọc task `D-RESP` | `stage`='in_progress', `end_time` rỗng, số event vẫn = 1 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; `D-RES` achieved; `D-RESP` không đổi. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-MUL-003: Gắn mỗi record một task riêng và độc lập khi cùng một định nghĩa

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-09-01 |
| Coverage Item | CI-3 (cùng định nghĩa, hai record khác nhau) |
| Requirement Ref | REQ-FUNC-014 (EP: tính duy nhất theo từng record) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition) (không đổi)
2. Hai partner `P-01`, `P-02` tạo với `ref`='NEW' tại FX-T0

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ref | NEW (cả hai) |  |
| now | T0 (09:00) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá {`P-01`,`P-02`} với now = T0, changed = {ref} | Không ngoại lệ |
| 2 | Đếm task đang hoạt động theo record | `P-01`: 1, `P-02`: 1 |
| 3 | Đặt `P-01.ref`='DONE' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | Task `P-01` `achieved`; task `P-02` vẫn `in_progress` |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Mỗi record một task; kết quả của record này không ảnh hưởng record kia. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-MUL-004: Từ chối tạo task hoạt động thứ hai khi record đã có task paused cho cùng định nghĩa

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-09-01 |
| Coverage Item | CI-4 (ràng buộc duy nhất: task paused vẫn là hoạt động) |
| Requirement Ref | REQ-FUNC-014 (Statement: tối đa một task hoạt động; `paused` tính là hoạt động) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition) (không đổi)
2. Partner `P-01` `ref`='HOLD' đã được gắn task `paused` (T-1) bằng bước 1

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| task thứ hai | `sla.task` create: definition=FX-DEF-STD, res_model=`res.partner`, res_id=`P-01`, stage=`in_progress`, start_time=T0 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | T-1 `stage`='paused' |
| 2 | Trong savepoint, tạo trực tiếp task thứ hai như Test Data bằng ORM | Ném lỗi vi phạm ràng buộc duy nhất `sla_task_one_active_uniq` (IntegrityError) |
| 3 | Sau rollback savepoint, đếm task của (định nghĩa, `P-01`) | = 1, chính là T-1 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Chỉ mục duy nhất chặn task hoạt động thứ hai. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-MUL-005: Cho phép task hoạt động mới khi task trước của cùng định nghĩa và record đã cancelled

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-09-01 |
| Coverage Item | CI-5 (ràng buộc duy nhất chỉ áp cho task hoạt động: được có task mới sau khi cancelled) |
| Requirement Ref | REQ-FUNC-014; REQ-FUNC-007 (AC3) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition) (không đổi)
2. Partner `P-01` tạo mới với `ref`='NEW' tại FX-T0, chưa có task nào

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| task thứ hai | `sla.task` create với stage=`in_progress` cho cùng (định nghĩa, `P-01`) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá `P-01` với now = T0 (2026-03-02 09:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | 1 task `in_progress` (T-1) |
| 2 | Đặt `ref`='OTHER' (G1); Gọi Engine đánh giá `P-01` với now = T0+1h (10:00), changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1) | T-1 `cancelled` |
| 3 | Tạo trực tiếp task thứ hai `in_progress` cho cùng (định nghĩa, `P-01`) bằng ORM | Không ném lỗi (chỉ mục `sla_task_one_active_uniq` không chặn vì T-1 đã `cancelled`); bản ghi mới có `stage` = 'in_progress' |
| 4 | Đếm tổng số task và số task hoạt động | Tổng = 2, hoạt động = 1 |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Ràng buộc chỉ giới hạn task hoạt động. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

---

### TC-MUL-006: Chỉ tồn tại một task hoạt động khi hai giao dịch đồng thời cùng gắn một định nghĩa

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-09-02 |
| Coverage Item | CI-1 (hai giao dịch cùng gắn -> chỉ 1 task hoạt động) |
| Requirement Ref | REQ-FUNC-014 (AC2: chỉ 1 task hoạt động) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase + hai cursor riêng, tự dọn dữ liệu) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition) (không đổi)
2. Dữ liệu nền được commit bằng cursor riêng: partner `P-01` với `ref`='NEW' tạo TRƯỚC khi định nghĩa FX-DEF-STD tồn tại (nên chưa có task); hai cursor `cr-A`, `cr-B` mở trên cùng registry, mức REPEATABLE READ (G6)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| cr-A / cr-B | hai cursor độc lập trên cùng database | mô phỏng hai giao dịch; thứ tự điều khiển bằng mã, không dùng thời gian thật |
| now | T0 (09:00) cho cả hai |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | `cr-B`: đọc số task hoạt động của (định nghĩa, `P-01`) để cố định snapshot | 0 |
| 2 | `cr-A`: Gọi Engine đánh giá `P-01` với now = T0, changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1); flush; COMMIT | Thành công; `cr-A` có 1 task `in_progress` |
| 3 | `cr-B` (snapshot cũ, vẫn thấy 0 task): Gọi Engine đánh giá `P-01` với now = T0, changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1); flush; COMMIT | Không ném ngoại lệ ra ngoài Engine |
| 4 | Cursor thứ ba: đếm task `in_progress`/`paused` của (định nghĩa, `P-01`) | Đúng 1 (do `cr-A` tạo), có đúng 1 event `attach` |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Đúng 1 task hoạt động. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Xóa dữ liệu đã commit (task, event, định nghĩa, partner `P-01`) trong tearDown vì ca dùng cursor đã commit.

---

### TC-MUL-007: Cả hai giao dịch commit thành công và không có lỗi nào đến người dùng khi xung đột gắn

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-09-02 |
| Coverage Item | CI-2 (cả hai giao dịch commit thành công, người dùng không thấy lỗi) |
| Requirement Ref | REQ-FUNC-014 (AC2 viết lại, TA-20: không lỗi nào tới người dùng; không yêu cầu cả hai giao dịch lưu record) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase + hai cursor riêng, tự dọn dữ liệu) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition) (không đổi)
2. Dữ liệu nền được commit bằng cursor riêng: partner `P-01` với `ref`='NEW' tạo TRƯỚC khi định nghĩa FX-DEF-STD tồn tại (nên chưa có task); hai cursor `cr-A`, `cr-B` mở trên cùng registry, mức REPEATABLE READ (G6)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| cr-A / cr-B | hai cursor độc lập trên cùng database | mô phỏng hai giao dịch; thứ tự điều khiển bằng mã, không dùng thời gian thật |
| now | T0 (09:00) cho cả hai |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | `cr-B`: đọc số task hoạt động của (định nghĩa, `P-01`) để cố định snapshot | 0 |
| 2 | `cr-A`: Gọi Engine đánh giá `P-01` với now = T0, changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1); flush; COMMIT | Thành công; `cr-A` có 1 task `in_progress` |
| 3 | `cr-B` (snapshot cũ, vẫn thấy 0 task): Gọi Engine đánh giá `P-01` với now = T0, changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1); flush; COMMIT | Không ném ngoại lệ ra ngoài Engine |
| 4 | Kiểm tra COMMIT của `cr-A` và `cr-B` ở bước 2, 3 | Cả hai COMMIT không ném ngoại lệ; không có exception nào thoát khỏi lời gọi evaluate ở `cr-B` |
| 5 | Cursor thứ ba: đọc `P-01.ref` | = 'NEW' (record giữ nguyên, không bị rollback) |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Hai COMMIT đều thành công; không lỗi nổi lên người dùng. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Xóa dữ liệu đã commit (task, event, định nghĩa, partner `P-01`) trong tearDown vì ca dùng cursor đã commit.

---

### TC-MUL-008: Ghi event error cho giao dịch gặp xung đột khi gắn trùng

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-09-02 |
| Coverage Item | CI-3 (bên gặp xung đột có event error) |
| Requirement Ref | REQ-FUNC-014 (AC2 viết lại, TA-20: bên thua ghi event `error` hoặc kết thúc không tạo task trùng); REQ-FUNC-030 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase + hai cursor riêng, tự dọn dữ liệu) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (start ref∈{NEW,WORK,HOLD}; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; reset rỗng; mục tiêu 4 giờ; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition) (không đổi)
2. Dữ liệu nền được commit bằng cursor riêng: partner `P-01` với `ref`='NEW' tạo TRƯỚC khi định nghĩa FX-DEF-STD tồn tại (nên chưa có task); hai cursor `cr-A`, `cr-B` mở trên cùng registry, mức REPEATABLE READ (G6)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| cr-A / cr-B | hai cursor độc lập trên cùng database | mô phỏng hai giao dịch; thứ tự điều khiển bằng mã, không dùng thời gian thật |
| now | T0 (09:00) cho cả hai |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | `cr-B`: đọc số task hoạt động của (định nghĩa, `P-01`) để cố định snapshot | 0 |
| 2 | `cr-A`: Gọi Engine đánh giá `P-01` với now = T0, changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1); flush; COMMIT | Thành công; `cr-A` có 1 task `in_progress` |
| 3 | `cr-B` (snapshot cũ, vẫn thấy 0 task): Gọi Engine đánh giá `P-01` với now = T0, changed = {ref} (`evaluate(records, now, changed)`, TAD 5.1); flush; COMMIT | Không ném ngoại lệ ra ngoài Engine |
| 4 | Cursor thứ ba: đếm event `error` của định nghĩa/`P-01` | Đúng 1 event `error`, do giao dịch `cr-B` ghi, `note` không rỗng (G12) |
| 5 | Đếm event `attach` | 1 (chỉ của `cr-A`) |

**Pass/Fail Criteria:** ✅ Pass: mọi Expected Result đúng; Có đúng 1 event `error` từ bên thua xung đột. ❌ Fail: bất kỳ Expected Result nào sai.

**Postconditions:** Xóa dữ liệu đã commit (task, event, định nghĩa, partner `P-01`) trong tearDown vì ca dùng cursor đã commit.

---

## TG-10 — Tính generic

### TC-GEN-001: Gắn SLA đúng cho record của hai model khác nhau chỉ bằng cấu hình

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-10-01 |
| Coverage Item | CI-1 (Hai model (`res.partner`, `demo.ticket`) cùng cấu hình) |
| Requirement Ref | REQ-FUNC-001 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-DEF-STD trên `res.partner` (start `[('ref','in',['NEW','WORK','HOLD'])]`, 4 giờ, nguồn lịch `none`).
2. Dựng định nghĩa D2 trên `demo.ticket` (FX-DEMO) cùng cấu trúc: start `[('priority','=','p1')]`, 4 giờ, nguồn lịch `none`, cancel `start_unmatched`, resume `condition`. (Phụ thuộc: TA-15, module demo `dwo_sla_demo_ticket` chưa hiện thực: `demo.ticket` có field `priority` với giá trị `p1`.)
3. Chưa có task nào (đếm `sla.task` = 0).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Partner P | ref = `NEW` | Thỏa start của FX-DEF-STD |
| Ticket K | priority = `p1` | Thỏa start của D2 |
| now | T0 = 2026-03-02 09:00 (UTC+7) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo P và K, gọi Engine đánh giá {P, K} với now = T0 (`evaluate(records, now, changed)`). | Không lỗi. |
| 2 | Đọc `sla.task` theo (`res_model`,`res_id`). | P có đúng 1 task của FX-DEF-STD; K có đúng 1 task của D2; cả hai `stage` = `in_progress`, `start_time` = T0, `target_duration` = 4, `planned_end_time` = 2026-03-02 13:00 (UTC+7). |
| 3 | Đếm event `attach`. | Có 2 event `attach` (mỗi task 1). |

**Pass/Fail Criteria:** ✅ Pass: Cả hai record có task `in_progress` đúng giá trị; không cần code riêng theo model. ❌ Fail: Thiếu task ở một model, hoặc giá trị sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-GEN-002: Lưu định nghĩa với đủ mọi tùy chọn cấu hình và đọc lại đúng giá trị

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-10-02 |
| Coverage Item | CI-1 (Lưu định nghĩa đặt đủ mọi tùy chọn) |
| Requirement Ref | REQ-FUNC-001 Statement |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-CAL-VN, FX-CO (CO-A), FX-ESC-STD có sẵn; một server action S bất kỳ.
2. Chưa có định nghĩa nào trên `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| model | `res.partner` |  |
| duration | 6 |  |
| schedule_source / schedule_id | `definition` / FX-CAL-VN |  |
| 6 domain | start `[('ref','=','NEW')]`, cancel `[('ref','=','CANCEL')]`, pause `[('ref','=','HOLD')]`, resume `[('ref','=','WORK')]`, stop `[('ref','=','DONE')]`, reset `[('ref','=','RESET')]` |  |
| cancel_mode / resume_mode / reset_action | `start_unmatched` / `condition` / `cancel` | `reset_action` có hai giá trị `cancel`, `complete` (030 bảng `sla_definition`) |
| reset_field_ids | field `ref` |  |
| retroactive_start / retroactive_field_id | bật / `create_date` |  |
| escalation | mốc 75% và 100% (FX-ESC-STD) |  |
| company_id / active / sequence | CO-A / True / 5 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` với toàn bộ Test Data, lưu. | Lưu thành công, không lỗi. |
| 2 | Đọc lại bản ghi (invalidate cache). | Từng field bằng đúng giá trị ở Test Data; có 2 escalation 75 và 100; `sequence` = 5; `active` = True. |

**Pass/Fail Criteria:** ✅ Pass: Mọi tùy chọn lưu và đọc lại đúng. ❌ Fail: Có tùy chọn không chọn được hoặc giá trị lưu sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-GEN-003: Từ chối lưu định nghĩa khi thiếu model

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-10-03 |
| Coverage Item | CI-1 (Thiếu model) |
| Requirement Ref | REQ-FUNC-001 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Chưa có định nghĩa nào.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| model | (rỗng) |  |
| duration | 4 |  |
| start | `[('ref','=','NEW')]` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` không có model, lưu. | Bị từ chối (ValidationError hoặc lỗi ràng buộc not-null) kèm thông báo. |
| 2 | Đếm `sla.definition`. | Số bản ghi vẫn = 0. |

**Pass/Fail Criteria:** ✅ Pass: Lưu bị từ chối, không có bản ghi mới. ❌ Fail: Lưu thành công.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-GEN-004: Từ chối lưu định nghĩa có thời lượng mục tiêu âm

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-10-03 |
| Coverage Item | CI-2 (`duration` = -1 (âm)) |
| Requirement Ref | REQ-FUNC-001 AC3 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Chưa có định nghĩa nào trên `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| model | `res.partner` |  |
| duration | -1 | Giá trị âm gần biên nhất |
| start | `[('ref','=','NEW')]` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo định nghĩa với `duration` = -1, lưu. | Bị từ chối kèm thông báo nêu thời lượng không được âm. |
| 2 | Đếm `sla.definition` của `res.partner`. | = 0. |

**Pass/Fail Criteria:** ✅ Pass: Từ chối, không có bản ghi. ❌ Fail: Lưu thành công.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-GEN-005: Chấp nhận lưu định nghĩa có thời lượng mục tiêu 0

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-10-03 |
| Coverage Item | CI-3 (`duration` = 0 (biên hợp lệ)) |
| Requirement Ref | REQ-FUNC-001 AC3 (boundary) |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Chưa có định nghĩa nào trên `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| model | `res.partner` |  |
| duration | 0 | Biên: 0 được chấp nhận |
| start | `[('ref','=','NEW')]` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo định nghĩa với `duration` = 0, lưu. | Lưu thành công. |
| 2 | Đọc lại `duration`. | = 0. |

**Pass/Fail Criteria:** ✅ Pass: Lưu thành công, `duration` = 0. ❌ Fail: Bị từ chối.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

## TG-11 — Đổi cấu hình khi đang chạy và archive

### TC-CHG-001: Giữ nguyên mục tiêu 4 giờ và planned_end_time của task đang chạy khi định nghĩa sửa thành 8 giờ

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-01 |
| Coverage Item | CI-1 (Task đang chạy, mục tiêu định nghĩa 4 -> 8) |
| Requirement Ref | REQ-FUNC-021 (AC1) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| duration ban đầu | 4 |  |
| duration sau khi sửa | 8 | sửa trên định nghĩa |
| now | T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress`; `target_duration` = 4.0; `planned_end_time` = 2026-03-02 06:00 UTC |
| 2 | U-MGR sửa `duration` của định nghĩa thành 8 | Lưu thành công |
| 3 | Gọi Engine `evaluate(P, now = T0 + 1h (10:00 giờ địa phương))` | Task vẫn `in_progress`; `target_duration` = 4.0; `planned_end_time` = 2026-03-02 06:00 UTC (không đổi) |

**Pass/Fail Criteria:** ✅ Pass: `target_duration` = 4.0 và `planned_end_time` = 06:00 UTC sau khi sửa; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-002: Giữ nguyên lịch L1 của task đang chạy khi định nghĩa đổi sang lịch L2

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-01 |
| Coverage Item | CI-2 (Task đang chạy, lịch định nghĩa L1 -> L2) |
| Requirement Ref | REQ-FUNC-021 (AC2) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-VN trên `res.partner` với `duration` = 4, `schedule_source` = `definition`, `schedule_id` = FX-CAL-VN; là định nghĩa duy nhất đang bật của `res.partner`.
4. FX-CAL-VN-PM (fixture bổ sung): `fully_fixed`, `Asia/Ho_Chi_Minh`, T2-T6 13:00-18:00 (5 giờ/ngày).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Lịch L1 | FX-CAL-VN |  |
| Lịch L2 | FX-CAL-VN-PM | đổi trên định nghĩa |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress`; `schedule_id` = FX-CAL-VN; `planned_end_time` = 2026-03-02 06:00 UTC (13:00 giờ địa phương) |
| 2 | U-MGR đổi `schedule_id` của định nghĩa thành FX-CAL-VN-PM | Lưu thành công |
| 3 | Gọi Engine `evaluate(P, now = T0 + 1h (10:00 giờ địa phương))` | `schedule_id` của task vẫn = FX-CAL-VN; `planned_end_time` = 2026-03-02 06:00 UTC |

**Pass/Fail Criteria:** ✅ Pass: `schedule_id` của task = FX-CAL-VN và `planned_end_time` không đổi; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-003: Task gắn mới sau khi sửa định nghĩa dùng mục tiêu 8 giờ và lịch mới

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-01 |
| Coverage Item | CI-3 (Record attach sau khi sửa) |
| Requirement Ref | REQ-FUNC-021 (AC3) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. FX-CAL-VN-PM (fixture bổ sung): `fully_fixed`, `Asia/Ho_Chi_Minh`, T2-T6 13:00-18:00 (5 giờ/ngày).
3. Partner P2 có `ref` = `NEW`, tạo TRƯỚC định nghĩa; chưa có task nào.
4. Định nghĩa FX-DEF-VN trên `res.partner` với `duration` = 4, `schedule_source` = `definition`, `schedule_id` = FX-CAL-VN; là định nghĩa duy nhất đang bật của `res.partner`.
5. U-MGR sửa định nghĩa: `duration` = 8, `schedule_id` = FX-CAL-VN-PM (trước khi attach P2).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| duration | 8 |  |
| Lịch | FX-CAL-VN-PM |  |
| now | T0 + 1h (10:00 giờ địa phương = 03:00 UTC) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P2, now = T0 + 1h)` | Task mới `in_progress`; `target_duration` = 8.0; `schedule_id` = FX-CAL-VN-PM |
| 2 | Đọc `planned_end_time` | = 2026-03-03 09:00 UTC (thứ Ba 16:00 giờ địa phương: 5 giờ thứ Hai 13:00-18:00 + 3 giờ thứ Ba 13:00-16:00) |

**Pass/Fail Criteria:** ✅ Pass: `target_duration` = 8.0, `schedule_id` = FX-CAL-VN-PM, `planned_end_time` = 2026-03-03 09:00 UTC; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-004: Giữ lịch L1 của task khi lịch lấy từ công ty mẹ của record đổi sang L2

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-02 |
| Coverage Item | CI-1 (Đổi lịch ở công ty mẹ sau khi attach) |
| Requirement Ref | REQ-FUNC-052 (AC1) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Field Many2one `x_calendar_id` -> `resource.calendar` trên `res.partner` do ca tự tạo (`ir.model.fields` loại manual) để làm đích của đường dẫn lịch.
3. FX-CAL-VN-PM (fixture bổ sung): `fully_fixed`, `Asia/Ho_Chi_Minh`, T2-T6 13:00-18:00 (5 giờ/ngày).
4. Partner Q (công ty mẹ) có `x_calendar_id` = FX-CAL-VN; partner P có `parent_id` = Q, `ref` = `NEW`, tạo TRƯỚC định nghĩa.
5. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4, `schedule_source` = `record`, `schedule_path` = `parent_id.x_calendar_id`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Lịch L1 (Q) | FX-CAL-VN |  |
| Lịch L2 (Q sau khi đổi) | FX-CAL-VN-PM |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress`; `schedule_id` = FX-CAL-VN; `planned_end_time` = 2026-03-02 06:00 UTC |
| 2 | Đặt `Q.x_calendar_id` = FX-CAL-VN-PM | Ghi thành công |
| 3 | Gọi Engine `evaluate(P, now = T0 + 1h (10:00 giờ địa phương))` | `schedule_id` của task vẫn = FX-CAL-VN; `planned_end_time` = 2026-03-02 06:00 UTC |

**Pass/Fail Criteria:** ✅ Pass: `schedule_id` = FX-CAL-VN và `planned_end_time` không đổi; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-005: Dùng lịch L2 sau khi SLA Manager bấm Apply Current Settings, khi lịch công ty mẹ đã đổi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-02 |
| Coverage Item | CI-2 (Bấm Apply Current Settings sau khi đổi) |
| Requirement Ref | REQ-FUNC-052 (AC2) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Field Many2one `x_calendar_id` -> `resource.calendar` trên `res.partner` do ca tự tạo (`ir.model.fields` loại manual) để làm đích của đường dẫn lịch.
3. FX-CAL-VN-PM (fixture bổ sung): `fully_fixed`, `Asia/Ho_Chi_Minh`, T2-T6 13:00-18:00 (5 giờ/ngày).
4. Partner Q (công ty mẹ) có `x_calendar_id` = FX-CAL-VN; partner P có `parent_id` = Q, `ref` = `NEW`, tạo TRƯỚC định nghĩa.
5. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4, `schedule_source` = `record`, `schedule_path` = `parent_id.x_calendar_id`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Lịch L1 -> L2 | FX-CAL-VN -> FX-CAL-VN-PM | đổi ở Q |
| Mốc Apply Current Settings | T0 + 1h (10:00 giờ địa phương) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress`; `schedule_id` = FX-CAL-VN |
| 2 | Đặt `Q.x_calendar_id` = FX-CAL-VN-PM | Ghi thành công |
| 3 | U-MGR thực hiện hành động Apply Current Settings trên task của P với now = T0 + 1h (10:00 giờ địa phương) | `schedule_id` của task = FX-CAL-VN-PM; `business_duration` = 1.0; `planned_end_time` = 2026-03-02 09:00 UTC (16:00 giờ địa phương: còn 3 giờ tính từ 13:00 theo lịch mới) |

**Pass/Fail Criteria:** ✅ Pass: `schedule_id` = FX-CAL-VN-PM và `planned_end_time` = 09:00 UTC; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-006: Apply Current Settings giữ 3 giờ đã trôi và xếp planned_end_time = hiện tại + 1 giờ làm việc theo lịch mới

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-03 |
| Coverage Item | CI-1 (Transition in_progress: lịch record đổi, đã trôi 3 giờ, mục tiêu 4) |
| Requirement Ref | REQ-INT-005 (AC1) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Field Many2one `x_calendar_id` -> `resource.calendar` trên `res.partner` do ca tự tạo (`ir.model.fields` loại manual) để làm đích của đường dẫn lịch.
3. FX-CAL-VN-PM (fixture bổ sung): `fully_fixed`, `Asia/Ho_Chi_Minh`, T2-T6 13:00-18:00 (5 giờ/ngày).
4. Partner Q (công ty mẹ) có `x_calendar_id` = FX-CAL-VN; partner P có `parent_id` = Q, `ref` = `NEW`, tạo TRƯỚC định nghĩa.
5. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4, `schedule_source` = `record`, `schedule_path` = `parent_id.x_calendar_id`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Mục tiêu | 4 |  |
| Lịch mới | FX-CAL-VN-PM | đổi ở Q sau khi attach |
| Mốc Apply Current Settings | T0 + 3h (12:00 giờ địa phương = 05:00 UTC) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress`; `schedule_id` = FX-CAL-VN; `planned_end_time` = 2026-03-02 06:00 UTC |
| 2 | Đặt `Q.x_calendar_id` = FX-CAL-VN-PM | Ghi thành công |
| 3 | U-MGR thực hiện hành động Apply Current Settings trên task của P với now = T0 + 3h | `business_duration` = 3.0; `schedule_id` = FX-CAL-VN-PM; `target_duration` = 4.0; `planned_end_time` = 2026-03-02 07:00 UTC (14:00 giờ địa phương: 12:00 ngoài giờ làm của lịch mới nên giờ thứ 1 bắt đầu 13:00) |
| 4 | Đếm task của (định nghĩa, P) | 1 task, vẫn `in_progress` |

**Pass/Fail Criteria:** ✅ Pass: `business_duration` = 3.0 và `planned_end_time` = 07:00 UTC; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Ghi chú:** `planned_end_time` = `sla.time.plan(lịch mới, now, mục tiêu - business_duration)`, tức `resource.calendar.plan_hours` từ `now`; 12:00 nằm ngoài giờ làm của lịch mới nên giờ thứ nhất bắt đầu 13:00.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-007: Apply Current Settings áp mục tiêu 8 giờ mới và xếp planned_end_time = hiện tại + 5 giờ làm việc

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-03 |
| Coverage Item | CI-2 (Transition in_progress: mục tiêu 4 -> 8) |
| Requirement Ref | REQ-INT-005 (AC2) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Mục tiêu | 4 -> 8 | sửa trên định nghĩa |
| Mốc Apply Current Settings | T0 + 3h (12:00 giờ địa phương) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress`; `target_duration` = 4.0 |
| 2 | U-MGR sửa `duration` của định nghĩa thành 8 | Task vẫn `target_duration` = 4.0 |
| 3 | U-MGR thực hiện hành động Apply Current Settings trên task của P với now = T0 + 3h | `target_duration` = 8.0; `business_duration` = 3.0; `planned_end_time` = 2026-03-02 10:00 UTC (17:00 giờ địa phương = 12:00 + 5 giờ, 24x7) |

**Pass/Fail Criteria:** ✅ Pass: `target_duration` = 8.0 và `planned_end_time` = 10:00 UTC; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Ghi chú:** Thời gian đã trôi 3 giờ lấy như AC1 vì AC2 không nêu.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-008: Apply Current Settings không khả dụng trên task đã achieved: nút bị ẩn theo stage và gọi hàm không đổi task

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-03 |
| Coverage Item | CI-3 (Negative: task achieved) |
| Requirement Ref | REQ-INT-005 (AC3) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); stop khi `ref` = `DONE`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Stage kết thúc | `achieved` | stop khớp khi chưa quá hạn |
| Mốc | T0 + 1h (10:00 giờ địa phương) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress`; `planned_end_time` = 2026-03-02 06:00 UTC |
| 2 | Ghi `ref` = `DONE` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = T0 + 1h (10:00 giờ địa phương), changed = {ref})` | `stage` = `achieved` |
| 3 | Đọc arch của view form/list `sla.task` (`views/sla_task_views.xml`) bằng `get_view` | Nút `action_recalculate` có `groups="dwo_sla_core.group_sla_manager"` và `invisible="stage not in ('in_progress', 'paused')"`, nên không hiển thị cho stage `achieved` |
| 4 | U-MGR gọi trực tiếp `action_recalculate()` trên task của P | Không ném lỗi và không đổi task (hàm chỉ áp dụng cho task `in_progress` hoặc `paused`) |
| 5 | Đọc lại task | `stage` = `achieved`; `planned_end_time` = 2026-03-02 06:00 UTC; `business_duration` không đổi so với bước trước |

**Pass/Fail Criteria:** ✅ Pass: nút bị ẩn ở stage này theo arch view, gọi trực tiếp không làm đổi task; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.


**Ghi chú:** Mức kiểm AC3 (REQ-INT-005): kiểm cấu hình view (`invisible` theo stage) VÀ hành vi hàm (không đổi task); việc nút thực sự không hiển thị trên trình duyệt kiểm bằng Demonstration ở TG-17. Gọi trực tiếp không ném lỗi (khác giả định cũ về `UserError`; TA-25).

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-009: Apply Current Settings không khả dụng trên task đã breached: nút bị ẩn theo stage và gọi hàm không đổi task

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-03 |
| Coverage Item | CI-4 (Negative: task breached) |
| Requirement Ref | REQ-INT-005 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); stop khi `ref` = `DONE`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Stage kết thúc | `breached` | stop khớp khi đã quá hạn |
| Mốc | T0 + 5h (14:00 giờ địa phương) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress`; `planned_end_time` = 2026-03-02 06:00 UTC |
| 2 | Ghi `ref` = `DONE` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = T0 + 5h (14:00 giờ địa phương), changed = {ref})` | `stage` = `breached` |
| 3 | Đọc arch của view form/list `sla.task` (`views/sla_task_views.xml`) bằng `get_view` | Nút `action_recalculate` có `groups="dwo_sla_core.group_sla_manager"` và `invisible="stage not in ('in_progress', 'paused')"`, nên không hiển thị cho stage `breached` |
| 4 | U-MGR gọi trực tiếp `action_recalculate()` trên task của P | Không ném lỗi và không đổi task (hàm chỉ áp dụng cho task `in_progress` hoặc `paused`) |
| 5 | Đọc lại task | `stage` = `breached`; `planned_end_time` = 2026-03-02 06:00 UTC; `business_duration` không đổi so với bước trước |

**Pass/Fail Criteria:** ✅ Pass: nút bị ẩn ở stage này theo arch view, gọi trực tiếp không làm đổi task; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.


**Ghi chú:** Mức kiểm AC3 (REQ-INT-005): kiểm cấu hình view (`invisible` theo stage) VÀ hành vi hàm (không đổi task); việc nút thực sự không hiển thị trên trình duyệt kiểm bằng Demonstration ở TG-17. Gọi trực tiếp không ném lỗi (khác giả định cũ về `UserError`; TA-25).

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-010: Apply Current Settings không khả dụng trên task đã cancelled: nút bị ẩn theo stage và gọi hàm không đổi task

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-03 |
| Coverage Item | CI-5 (Negative: task cancelled) |
| Requirement Ref | REQ-INT-005 |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Stage | `cancelled` | ref `CANCEL` làm start không khớp |
| Mốc | T0 + 1h (10:00 giờ địa phương) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress` |
| 2 | Ghi `ref` = `CANCEL` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = T0 + 1h (10:00 giờ địa phương), changed = {ref})` | `stage` = `cancelled` |
| 3 | Đọc arch của view form/list `sla.task` (`views/sla_task_views.xml`) bằng `get_view` | Nút `action_recalculate` có `groups="dwo_sla_core.group_sla_manager"` và `invisible="stage not in ('in_progress', 'paused')"`, nên không hiển thị cho stage `cancelled` |
| 4 | U-MGR gọi trực tiếp `action_recalculate()` trên task của P | Không ném lỗi và không đổi task (hàm chỉ áp dụng cho task `in_progress` hoặc `paused`) |
| 5 | Đọc lại task | `stage` = `cancelled`; `planned_end_time` = 2026-03-02 06:00 UTC |

**Pass/Fail Criteria:** ✅ Pass: nút bị ẩn ở stage này theo arch view, gọi trực tiếp không làm đổi task; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.


**Ghi chú:** Mức kiểm AC3 (REQ-INT-005): kiểm cấu hình view (`invisible` theo stage) VÀ hành vi hàm (không đổi task); việc nút thực sự không hiển thị trên trình duyệt kiểm bằng Demonstration ở TG-17. Gọi trực tiếp không ném lỗi (khác giả định cũ về `UserError`; TA-25).

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-011: Apply Current Settings task paused: đổi mục tiêu ngay, xếp lại planned_end_time khi resume

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-03 |
| Coverage Item | CI-6 (Transition paused) |
| Requirement Ref | REQ-INT-005 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); pause khi `ref` = `HOLD`, resume khi `ref` = `WORK`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Mục tiêu | 4 -> 8 |  |
| Mốc | pause T0+1h, Apply Current Settings T0+2h, resume T0+3h | 10:00, 11:00, 12:00 giờ địa phương |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress`; `planned_end_time` = 2026-03-02 06:00 UTC |
| 2 | Ghi `ref` = `HOLD` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = T0 + 1h, changed = {ref})` | `stage` = `paused`; `business_duration` = 1.0 |
| 3 | U-MGR sửa `duration` của định nghĩa thành 8 | Lưu thành công |
| 4 | U-MGR thực hiện hành động Apply Current Settings trên task của P với now = T0 + 2h | `stage` vẫn `paused`; `target_duration` = 8.0; `business_duration` = 1.0; `planned_end_time` = 2026-03-02 06:00 UTC (chưa xếp lại) |
| 5 | Ghi `ref` = `WORK` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = T0 + 3h (12:00 giờ địa phương), changed = {ref})` | `stage` = `in_progress`; `planned_end_time` = 2026-03-02 12:00 UTC (19:00 giờ địa phương = 12:00 + (8 - 1) giờ) |

**Pass/Fail Criteria:** ✅ Pass: `planned_end_time` = 12:00 UTC chỉ sau khi resume; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Ghi chú:** Theo code (`sla_task.action_recalculate`) và Statement REQ-INT-005, `planned_end_time` của task `paused` giữ giá trị cũ cho tới khi resume.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-012: Không bắn bù mốc 75% thêm sau khi task đã ở 80%

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-04 |
| Coverage Item | CI-1 (Mốc 75% thêm khi task ở 80%) |
| Requirement Ref | REQ-FUNC-053 (AC1) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); một mốc escalation 100% với server action ghi ghi chú `SLA-100` vào chatter của partner; là định nghĩa duy nhất đang bật của `res.partner`.
4. Mốc 100% là mốc duy nhất lúc đầu (FX-ESC-STD rút gọn).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Mốc thêm sau | 75% | thêm khi task đã ở 80% |
| Thời điểm 80% | T0 + 3.2h (12:12 giờ địa phương = 05:12 UTC) | 3.2 / 4 giờ |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress`; `business_duration` = 0 |
| 2 | Xử lý nền tại now = T0 + 3.2h (12:12 giờ địa phương) | 0 event `escalate`; chatter của P không có ghi chú `SLA-100` |
| 3 | Với patch `odoo.fields.Datetime.now` trả T0 + 3.2h (12:12 giờ VN): U-MGR thêm mốc 75% (server action ghi `SLA-75`) vào định nghĩa | Lưu thành công; mốc 75% nằm trong `done_escalation_ids` của task và KHÔNG có event nào được ghi (D4/FUNC-053: mốc đã vượt chèn vào tập đã xử lý, không bắn bù) |
| 4 | Xử lý nền tại now = T0 + 3.2h (12:12 giờ địa phương) | 0 event `escalate`; chatter không có `SLA-75` |
| 5 | Xử lý nền tại now = T0 + 4h (13:00 giờ địa phương) | Đúng 1 event `escalate` (mốc 100%); chatter có đúng 1 ghi chú `SLA-100` và 0 ghi chú `SLA-75` |

**Pass/Fail Criteria:** ✅ Pass: Mốc 75% không bao giờ bắn: 0 ghi chú `SLA-75` ở bước 4 và 5; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-013: Bắn mốc 90% thêm sau khi tới 90% của task đang ở 80%

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-04 |
| Coverage Item | CI-2 (Mốc 90% thêm khi task ở 80%) |
| Requirement Ref | REQ-FUNC-053 (AC2) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); một mốc escalation 100% với server action ghi ghi chú `SLA-100` vào chatter của partner; là định nghĩa duy nhất đang bật của `res.partner`.
4. Mốc 100% là mốc duy nhất lúc đầu (FX-ESC-STD rút gọn).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Mốc thêm sau | 90% | thêm khi task đã ở 80% |
| Thời điểm 80% | T0 + 3.2h (12:12 giờ địa phương = 05:12 UTC) | 3.2 / 4 giờ |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress` |
| 2 | Xử lý nền tại now = T0 + 3.2h (12:12 giờ địa phương) | 0 event `escalate` |
| 3 | Với patch `odoo.fields.Datetime.now` trả T0 + 3.2h (12:12 giờ VN): U-MGR thêm mốc 90% (server action ghi `SLA-90`) vào định nghĩa | Lưu thành công; mốc 90% KHÔNG nằm trong `done_escalation_ids`; `next_due_at` của task = T0 + 3.6h (12:36 giờ VN = 05:36 UTC) (D4/TA-07 đã chốt) |
| 4 | Xử lý nền tại now = T0 + 3.55h (12:33 giờ địa phương, 88.75%) | 0 event `escalate`; 0 ghi chú `SLA-90` |
| 5 | Xử lý nền tại now = T0 + 3.6h (12:36 giờ địa phương, đúng 90%) | Đúng 1 event `escalate`; chatter có đúng 1 ghi chú `SLA-90`, 0 ghi chú `SLA-100` |

**Pass/Fail Criteria:** ✅ Pass: Mốc 90% bắn đúng 1 lần ở now = 12:36 và không bắn ở 12:33; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Ghi chú:** D4/TA-07 đã chốt: thêm mốc làm tính lại `next_due_at`. Code `sla_escalation.create` đã tính lại `next_due_at` cho mốc chưa tới (TA-24 ĐÃ SỬA, TASKS T13), nên xử lý nền theo `process_due()` chọn task đúng lúc 12:36 ở bước 5.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-015: Không gắn task cho record mới thỏa start khi định nghĩa đã archive

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-05 |
| Coverage Item | CI-1 (Archive: record mới thỏa start) |
| Requirement Ref | REQ-FUNC-033 (AC1) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); đã archive (`active` = False); là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Định nghĩa | FX-DEF-STD, `active` = False |  |
| P.ref | `NEW` | khớp start |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo partner P (`ref` = `NEW`) qua `create` rồi gọi `evaluate(P, now = T0)` | Không lỗi |
| 2 | Đếm `sla.task` của P | 0 |
| 3 | Đếm event `error` của P | 0 |

**Pass/Fail Criteria:** ✅ Pass: 0 task và 0 event `error` cho P; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-016: Giữ đúng 1 task đang hoạt động khi bỏ archive rồi sửa record đã có task

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-05 |
| Coverage Item | CI-2 (Archive rồi bỏ archive, sửa record đã có task) |
| Requirement Ref | REQ-FUNC-033 (AC2) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); pause khi `ref` = `HOLD`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Chuỗi | attach, archive, bỏ archive, sửa record |  |
| P.ref | `NEW` rồi `HOLD` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | 1 task `in_progress` |
| 2 | U-MGR archive định nghĩa rồi bỏ archive | `active` = True |
| 3 | Ghi `ref` = `HOLD` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = T0 + 1h (10:00 giờ địa phương), changed = {ref})` | Task chuyển `paused` |
| 4 | Đếm task của (định nghĩa, P) và task có `stage` thuộc `in_progress`, `paused` | Tổng 1 task; 1 task đang hoạt động (không sinh task trùng) |

**Pass/Fail Criteria:** ✅ Pass: Đúng 1 task, `stage` = `paused`; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-017: Gắn task cho record mới sau khi bỏ archive định nghĩa

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-05 |
| Coverage Item | CI-3 (Bỏ archive: record mới thỏa start) |
| Requirement Ref | REQ-FUNC-033 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); đã archive rồi bỏ archive; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Định nghĩa | `active` False -> True |  |
| P.ref | `NEW` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo partner P (`ref` = `NEW`), gọi `evaluate(P, now = T0)` | Có đúng 1 task `in_progress` của P |

**Pass/Fail Criteria:** ✅ Pass: Đúng 1 task `in_progress`; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-018: Kết thúc đúng task của record được stop trong 30 task đang chạy khi định nghĩa đã archive

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-06 |
| Coverage Item | CI-1 (Archive D có 30 task, stop một record) |
| Requirement Ref | REQ-FUNC-060 (AC1) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. 30 partner P01..P30 có `ref` = `NEW`, tạo TRƯỚC định nghĩa.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); stop khi `ref` = `DONE`; là một trong hai định nghĩa đang bật của `res.partner`.
4. Định nghĩa D-OTHER thứ hai trên `res.partner` với start `[('ref', '=', 'ZZZ')]` (không bao giờ khớp), đang bật.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Số task | 30 `in_progress` |  |
| Record stop | P01 (`ref` = `DONE`) | mốc T0 + 1h |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi `evaluate(P01..P30, now = T0)` | 30 task `in_progress` |
| 2 | U-MGR archive FX-DEF-STD | `active` = False; vẫn 30 task `in_progress` |
| 3 | Ghi `ref` = `DONE` trên P01 (qua `_write`) rồi `evaluate(P01, now = T0 + 1h, changed = {ref})` | Task của P01 `stage` = `achieved`, `end_time` = 2026-03-02 03:00 UTC; có 1 event `complete` |
| 4 | Đếm task còn `in_progress` | 29 |

**Pass/Fail Criteria:** ✅ Pass: Task P01 `achieved` và 29 task còn lại `in_progress`; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-019: Ghi event breach và bắn escalation cho task quá planned_end_time của định nghĩa đã archive

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-06 |
| Coverage Item | CI-2 (Task quá `planned_end_time`, xử lý nền chạy) |
| Requirement Ref | REQ-FUNC-060 (AC2) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); mốc 75% (ghi `SLA-75`) và 100% (ghi `SLA-100`); là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Mốc xử lý nền | T0 + 5h (14:00 giờ địa phương) | quá `planned_end_time` 13:00 |
| Escalation | 75% và 100% |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress`; `planned_end_time` = 2026-03-02 06:00 UTC |
| 2 | U-MGR archive định nghĩa | `active` = False |
| 3 | Xử lý nền tại now = T0 + 5h | `has_breached` = True; đúng 1 event `breach`; đúng 2 event `escalate`; chatter của P có `SLA-75` và `SLA-100` mỗi loại 1 ghi chú |

**Pass/Fail Criteria:** ✅ Pass: 1 event `breach` và 2 event `escalate`; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-020: Không gắn task mới cho record thỏa start khi định nghĩa đã archive (nhìn từ task đang chạy)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-06 |
| Coverage Item | CI-3 (Negative: record mới thỏa start) |
| Requirement Ref | REQ-FUNC-060 (AC3) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P01 có `ref` = `NEW`, tạo TRƯỚC định nghĩa.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); archive sau khi P01 có task; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| P01 | có 1 task `in_progress` |  |
| P02.ref | `NEW` | record mới |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P01, now = T0)` | P01 có 1 task `in_progress` |
| 2 | U-MGR archive định nghĩa | `active` = False |
| 3 | Tạo partner P02 (`ref` = `NEW`) rồi `evaluate(P02, now = T0 + 1h)` | 0 task cho P02; P01 vẫn 1 task `in_progress` |

**Pass/Fail Criteria:** ✅ Pass: P02 không có task; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-021: Chuyển task sang cancelled khi cancel khớp (chế độ condition) trên định nghĩa đã archive

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-06 |
| Coverage Item | CI-4 (Cancel khớp, chế độ `condition`) |
| Requirement Ref | REQ-FUNC-060 (AC4) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); `cancel_mode` = `condition`, cancel domain `[('ref', '=', 'CANCEL')]`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| cancel_mode | `condition` |  |
| P.ref | `CANCEL` | mốc T0 + 1h |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress` |
| 2 | U-MGR archive định nghĩa | `active` = False |
| 3 | Ghi `ref` = `CANCEL` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = T0 + 1h (10:00 giờ địa phương), changed = {ref})` | `stage` = `cancelled`; `end_time` = 2026-03-02 03:00 UTC; 1 event `cancel` |

**Pass/Fail Criteria:** ✅ Pass: `stage` = `cancelled`; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-022: Pause rồi resume task thuộc định nghĩa đã archive

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-06 |
| Coverage Item | CI-5 (Pause khớp rồi resume khớp) |
| Requirement Ref | REQ-FUNC-060 (AC5) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); pause khi `ref` = `HOLD`, resume khi `ref` = `WORK`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Chuỗi ref | `NEW`, `HOLD`, `WORK` |  |
| Mốc | T0, T0+1h, T0+2h |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress` |
| 2 | U-MGR archive định nghĩa | `active` = False |
| 3 | Ghi `ref` = `HOLD` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = T0 + 1h (10:00 giờ địa phương), changed = {ref})` | `stage` = `paused`; 1 event `pause` |
| 4 | Ghi `ref` = `WORK` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = T0 + 2h (11:00 giờ địa phương), changed = {ref})` | `stage` = `in_progress`; 1 event `resume` |

**Pass/Fail Criteria:** ✅ Pass: `paused` rồi `in_progress`; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-023: Kết thúc task khi stop khớp và định nghĩa archive là định nghĩa cuối cùng của model

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-06 |
| Coverage Item | CI-6 (Edge: D là định nghĩa cuối của model, stop khớp) |
| Requirement Ref | REQ-FUNC-060 (AC6) |
| Priority | P1-Critical |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); stop khi `ref` = `DONE`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Số định nghĩa đang bật của `res.partner` sau archive | 0 | D là định nghĩa cuối |
| Mốc stop | T0 + 1h |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress` |
| 2 | U-MGR archive định nghĩa; xác nhận không còn định nghĩa `active` nào của `res.partner` | 0 định nghĩa đang bật |
| 3 | Ghi `ref` = `DONE` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = T0 + 1h (10:00 giờ địa phương), changed = {ref})` | `stage` = `achieved`; `end_time` = 2026-03-02 03:00 UTC |
| 4 | Đếm task `in_progress` hoặc `paused` của P | 0 (không kẹt) |

**Pass/Fail Criteria:** ✅ Pass: Task `achieved`, không còn task hoạt động; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Ghi chú:** Phân biệt với CI-1: ở đây không còn định nghĩa nào đang bật, hook không được thoát sớm theo model (TAD AD-01: hook thoát sớm hai lớp, lớp 1 là tập model có định nghĩa đang bật).

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-024: Từ chối xóa định nghĩa còn 1 task achieved và gợi ý archive

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-07 |
| Coverage Item | CI-1 (Còn 1 task `achieved`) |
| Requirement Ref | REQ-FUNC-061 (AC1) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); stop khi `ref` = `DONE`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-MGR |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress` |
| 2 | Ghi `ref` = `DONE` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = T0 + 1h, changed = {ref})` | Task `achieved` |
| 3 | U-MGR xóa (`unlink`) định nghĩa | Ném `ValidationError`; thông báo chứa từ `archive` (VAL_004: "... Archive it instead of deleting.") |
| 4 | Đọc lại định nghĩa và task | Định nghĩa còn tồn tại (`exists()`); task `achieved` còn nguyên |

**Pass/Fail Criteria:** ✅ Pass: Xóa bị từ chối, thông báo gợi ý archive; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-025: Xóa thành công định nghĩa chưa từng có task

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-07 |
| Coverage Item | CI-2 (Chưa từng có task) |
| Requirement Ref | REQ-FUNC-061 (AC2) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-MGR |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đếm `sla.task` của định nghĩa | 0 |
| 2 | U-MGR gọi `unlink()` trên định nghĩa | Không ném lỗi (trả True) |
| 3 | Kiểm tra `exists()` | Định nghĩa không còn |

**Pass/Fail Criteria:** ✅ Pass: Định nghĩa bị xóa; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-026: Từ chối xóa định nghĩa còn task in_progress

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-07 |
| Coverage Item | CI-3 (Còn task `in_progress` (lớp stage hoạt động)) |
| Requirement Ref | REQ-FUNC-061 |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-MGR |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress` |
| 2 | U-MGR xóa định nghĩa | Ném `ValidationError` (VAL_004) |
| 3 | Kiểm tra `exists()` và stage task | Định nghĩa còn; task `in_progress` |

**Pass/Fail Criteria:** ✅ Pass: Xóa bị từ chối; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-027: Từ chối xóa định nghĩa đã archive còn task cancelled

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-07 |
| Coverage Item | CI-4 (Đã archive, còn task `cancelled`) |
| Requirement Ref | REQ-FUNC-061 |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P được tạo TRƯỚC định nghĩa với `ref` = `NEW` (nên chưa có task nào); ca dựng record trước, định nghĩa sau.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-MGR |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Task `in_progress` |
| 2 | Ghi `ref` = `CANCEL` trên P (qua `_write`, bỏ qua hook) rồi gọi Engine `evaluate(P, now = T0 + 1h, changed = {ref})` | Task `cancelled` |
| 3 | U-MGR archive định nghĩa | `active` = False |
| 4 | U-MGR xóa định nghĩa | Ném `ValidationError` (VAL_004) |
| 5 | Kiểm tra `exists()` | Định nghĩa còn |

**Pass/Fail Criteria:** ✅ Pass: Xóa bị từ chối; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CHG-028: Người dùng chỉ thuộc `group_sla_user` không có nút Apply Current Settings trên task và không gọi được hành động Apply Current Settings

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-11-03 |
| Coverage Item | CI-7 (AC4 negative: SLA User không có nút Apply Current Settings) |
| Requirement Ref | REQ-INT-005 (AC4) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-USERS: U-MGR (`group_sla_manager`), U-USR (chỉ `group_sla_user`), U-BIZ (chỉ quyền sửa `res.partner`), U-NONE (không quyền SLA); công ty hiện tại CO-A.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, nguồn lịch `none`); partner P (`ref` = `NEW`) tạo trước định nghĩa.
3. Task T của P attach lúc T0 (2026-03-02 09:00 giờ VN) bằng `evaluate(P, now = T0)`; T `in_progress`, `planned_end_time` = 06:00 UTC.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng kiểm | U-USR (chỉ `group_sla_user`) | đối chứng bằng U-MGR |
| Hành động | `action_recalculate` trên T |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env U-USR, `sla.task.get_view(view_type='form')` và `'list'` rồi tìm nút `action_recalculate` trong arch | Không có nút `action_recalculate` trong arch của cả hai view (nút khai báo `groups="dwo_sla_core.group_sla_manager"`) |
| 2 | Với env U-MGR, cùng thao tác bước 1 | Arch có nút `action_recalculate` (đối chứng, bảo đảm bước 1 không đạt vì lý do khác) |
| 3 | Với env U-USR, gọi trực tiếp `T.action_recalculate()` | Ném `AccessError` có nội dung chứa "SLA Manager" (ACC_001); T không đổi |
| 4 | Đọc lại T (sudo) | `planned_end_time` = 06:00 UTC; `target_duration` = 4.0; `stage` = `in_progress` |

**Pass/Fail Criteria:** ✅ Pass: U-USR không thấy nút ở cả hai view và bị `AccessError` khi gọi hàm, U-MGR thấy nút; ❌ Fail: U-USR thấy nút hoặc gọi hàm được

**Ghi chú:** Mức kiểm: cấu hình view (`groups`) và hàm (kiểm quyền cứng); không kiểm hiển thị trên trình duyệt.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

## TG-12 — Lỗi engine và đồng thời

### TC-ERR-001: Lưu record thành công, không có task, có 1 event error khi domain trỏ field đã bị gỡ

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-01 |
| Coverage Item | CI-1 (AC1: domain trỏ field đã bị gỡ (đường write)) |
| Requirement Ref | REQ-FUNC-030 AC1 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD (tên 'FX-DEF-STD') có `start_domain` bị ghi trực tiếp bằng SQL thành `[('x_removed_field', '=', 1)]` để mô phỏng field đã bị gỡ sau khi lưu (bỏ qua kiểm tra lúc lưu của REQ-FUNC-003).
4. U-BIZ (chỉ quyền sửa `res.partner`) làm người dùng lưu
5. Partner P-1 (`ref` = 'OLD', `comment` = 'C0') đã tồn tại

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Giá trị lưu | `ref` = 'NEW', `comment` = 'C1' | thay đổi của người dùng |
| Định nghĩa | FX-DEF-STD | domain lỗi |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | U-BIZ ghi P-1 {ref: 'NEW', comment: 'C1'} | Lệnh `write` hoàn tất, không ném ngoại lệ |
| 2 | Đọc P-1 bằng cursor mới | `ref` = 'NEW' và `comment` = 'C1' (thay đổi của người dùng được lưu) |
| 3 | Đếm `sla.task` có `res_model` = 'res.partner', `res_id` = P-1.id | = 0 |
| 4 | Đọc event `error` | Đúng 1 event `error` (task_id rỗng, `res_model` = 'res.partner', `res_id` = P-1.id, `definition_id` = FX-DEF-STD, `note` không rỗng) |

**Pass/Fail Criteria:** ✅ Pass: record lưu đủ hai giá trị, 0 task, đúng 1 event `error`; ❌ Fail: `write` ném lỗi, mất thay đổi, có task, hoặc số event `error` ≠ 1

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-002: Tạo record thành công và ghi event error khi domain điều kiện trỏ field đã bị gỡ

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-01 |
| Coverage Item | CI-2 (AC1 (đường create): domain lỗi khi tạo record) |
| Requirement Ref | REQ-FUNC-030 AC1 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD (tên 'FX-DEF-STD') có `start_domain` bị ghi trực tiếp bằng SQL thành `[('x_removed_field', '=', 1)]` để mô phỏng field đã bị gỡ sau khi lưu (bỏ qua kiểm tra lúc lưu của REQ-FUNC-003).
4. U-BIZ làm người dùng tạo

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Giá trị tạo | `name` = 'P-NEW', `ref` = 'NEW' |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | U-BIZ tạo `res.partner` {name: 'P-NEW', ref: 'NEW'} | Tạo thành công, trả record P-NEW |
| 2 | Đếm `sla.task` của P-NEW | = 0 |
| 3 | Đọc event `error` | Đúng 1 event `error` (task_id rỗng, `res_model` = 'res.partner', `res_id` = P-NEW.id, `definition_id` = FX-DEF-STD, `note` không rỗng) |

**Pass/Fail Criteria:** ✅ Pass: record tồn tại, 0 task, đúng 1 event `error`; ❌ Fail: tạo thất bại hoặc không có event `error`

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-003: Không gắn task, ghi 1 event error khi calendar của định nghĩa bị xóa hết giờ làm

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-01 |
| Coverage Item | CI-3 (AC2: calendar mất toàn bộ giờ làm sau khi định nghĩa đã lưu) |
| Requirement Ref | REQ-FUNC-030 AC2 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-VN (nguồn lịch `definition` = FX-CAL-VN, mục tiêu 4 giờ) đã lưu thành công
4. Sau đó xóa toàn bộ `attendance_ids` của FX-CAL-VN (calendar không còn giờ làm; `plan_hours` trả False)
5. Partner P-1 (`ref` = 'OLD') đã tồn tại; U-BIZ làm người dùng lưu

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Giá trị lưu | `ref` = 'NEW' | khớp start của FX-DEF-VN |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | U-BIZ ghi P-1 {ref: 'NEW'} | Không ném ngoại lệ |
| 2 | Đọc P-1 bằng cursor mới | `ref` = 'NEW' |
| 3 | Đếm `sla.task` của P-1 | = 0 |
| 4 | Đọc event `error` | Đúng 1 event `error` (task_id rỗng, `res_model` = 'res.partner', `res_id` = P-1.id, `definition_id` = FX-DEF-VN, `note` không rỗng) |

**Pass/Fail Criteria:** ✅ Pass: record lưu, 0 task, đúng 1 event `error`; ❌ Fail: lỗi lan ra người dùng, có task, hoặc không có event `error`

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-004: Cô lập lỗi theo record: lỗi ở R1 không ngăn R2 được attach trong cùng lô

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-01 |
| Coverage Item | CI-4 (AC3: lỗi ở R1 trong lô R1 và R2, R2 vẫn bình thường) |
| Requirement Ref | REQ-FUNC-030 AC3 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Hai partner R1, R2 có `ref` = 'NEW', chưa có task
4. Mock Time Service `plan` ném `ValueError('plan failed')` khi xử lý R1 và hoạt động bình thường với R2 (mock `sla.time.plan` kiểm theo record đang xử lý nên chỉ R1 lỗi)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Lô | R1, R2 | cùng một lần gọi |
| now | FX-T0 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(R1 \| R2, now = FX-T0, changed = ∅)` | Không ném ngoại lệ ra ngoài |
| 2 | Đọc task và event của R1 | 0 task; 1 event `error` của R1; 0 event `attach` của R1 |
| 3 | Đọc task và event của R2 | 1 task `in_progress` (`start_time` = 09:00, `planned_end_time` = 13:00); 1 event `attach`; 0 event `error` |

**Pass/Fail Criteria:** ✅ Pass: R1 có event `error` và không có task; R2 có task và event `attach`; ❌ Fail: R2 không được xử lý hoặc R1 để lại dữ liệu dở dang

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-005: Hai cursor cùng attach một record qua `evaluate`: chỉ 1 task hoạt động, bên thua ghi 1 event `error` và không ném lỗi ra ngoài

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-01 |
| Coverage Item | CI-5 (Vi phạm tính duy nhất khi hai giao dịch cùng attach) |
| Requirement Ref | REQ-FUNC-030, REQ-REL-001 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (hai cursor, không dùng TransactionCase đơn) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Partner P-1 (`ref` = 'NEW', khớp start) đã commit, chưa có task. Hai cursor C1 và C2 độc lập (REPEATABLE READ); C1 và C2 KHÔNG ghi P-1, chỉ gọi `sla.engine.evaluate(P-1, now)`, nên không có tranh chấp khóa dòng P-1.
4. Thứ tự điều khiển bằng mã test: `sla.engine._attach` trong C2 được bọc để dừng tại `threading.Event` ngay trước lệnh tạo task (sau khi đã đọc 'chưa có task hoạt động').

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Record | P-1 |  |
| now | FX-T0 |  |
| Chỉ mục duy nhất | `sla_task_one_active_uniq` | duy nhất cho (definition_id, res_model, res_id) khi task `in_progress` hoặc `paused` (030 mục 6) |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | C2: bắt đầu giao dịch, gọi `evaluate(P-1, now = FX-T0)` tới khi dừng tại barrier trước lệnh tạo task | C2 đã đọc 0 task hoạt động của (FX-DEF-STD, P-1); chưa có dòng nào được chèn bởi C2 |
| 2 | C1: `evaluate(P-1, now = FX-T0)` rồi commit | C1 tạo 1 task `in_progress` và 1 event `attach` |
| 3 | Mở barrier: C2 tiếp tục tạo task (vi phạm `sla_task_one_active_uniq`) rồi commit | `evaluate` của C2 không ném ngoại lệ ra ngoài; savepoint của record bị hoàn tác; giao dịch C2 commit được |
| 4 | Đọc bằng cursor mới | Đúng 1 task hoạt động cho (FX-DEF-STD, P-1), không có task trùng; đúng 1 event `attach`; bên thua ghi đúng 1 event `error` có `res_model` = 'res.partner', `res_id` = P-1 và `note` không rỗng (hành vi hiện tại của code; AC2 của REQ-FUNC-014 cũng chấp nhận bên thua kết thúc mà không tạo task trùng) |

**Pass/Fail Criteria:** ✅ Pass: đúng 1 task hoạt động, không có task trùng, bên thua ghi event `error` (hoặc kết thúc không tạo task trùng) và không có lỗi ném ra ngoài; ❌ Fail: có 2 task hoạt động, hoặc `evaluate` của C2 ném lỗi

**Ghi chú:** TA-20 ĐÃ CHỐT: AC2 của REQ-FUNC-014 được SRS viết lại thành "chỉ một task hoạt động tồn tại, không có task trùng, bên thua ghi event `error` hoặc kết thúc mà không tạo task trùng"; không yêu cầu cả hai giao dịch cùng lưu record (C1 và C2 ở ca này không ghi P-1).

**Postconditions:** Dữ liệu đã commit bởi các cursor: dọn bằng xóa bản ghi test trong `tearDown`.

### TC-ERR-006: Ghi đủ model, id, tên định nghĩa và thông báo vào event error (lỗi domain)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-02 |
| Coverage Item | CI-1 (AC1: lỗi do domain trỏ field bị gỡ) |
| Requirement Ref | REQ-OBS-001 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD (tên 'FX-DEF-STD') có `start_domain` bị ghi trực tiếp bằng SQL thành `[('x_removed_field', '=', 1)]` để mô phỏng field đã bị gỡ sau khi lưu (bỏ qua kiểm tra lúc lưu của REQ-FUNC-003).
4. Partner P-1 (`ref` = 'OLD') đã tồn tại; U-BIZ làm người dùng lưu

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Giá trị lưu | `ref` = 'NEW' |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | U-BIZ ghi P-1 {ref: 'NEW'} | Không ném ngoại lệ |
| 2 | Đọc event `error` duy nhất | `res_model` = 'res.partner'; `res_id` = P-1.id; `definition_id.name` = 'FX-DEF-STD'; `note` không rỗng (độ dài > 0) |
| 3 | Đọc `company_id` của event | = công ty của P-1 |

**Pass/Fail Criteria:** ✅ Pass: cả bốn thông tin đều có và đúng; ❌ Fail: thiếu bất kỳ thông tin nào hoặc `note` rỗng

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-007: Ghi đủ model, id, tên định nghĩa và thông báo vào event error (lỗi lịch)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-02 |
| Coverage Item | CI-2 (AC1: lỗi do calendar không xếp được hạn) |
| Requirement Ref | REQ-OBS-001 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-VN (nguồn lịch `definition` = FX-CAL-VN); sau khi lưu xóa toàn bộ `attendance_ids` của FX-CAL-VN
4. Partner P-1 (`ref` = 'OLD') đã tồn tại; U-BIZ làm người dùng lưu

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Giá trị lưu | `ref` = 'NEW' |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | U-BIZ ghi P-1 {ref: 'NEW'} | Không ném ngoại lệ |
| 2 | Đọc event `error` duy nhất | `res_model` = 'res.partner'; `res_id` = P-1.id; `definition_id.name` = 'FX-DEF-VN'; `note` không rỗng (độ dài > 0) |
| 3 | Đọc `company_id` của event | = công ty của P-1 |

**Pass/Fail Criteria:** ✅ Pass: cả bốn thông tin đều có và đúng; ❌ Fail: thiếu bất kỳ thông tin nào hoặc `note` rỗng

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-008: Ghi đúng 1 dòng log ERROR chứa model, id record và tên định nghĩa khi engine lỗi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-03 |
| Coverage Item | CI-1 (AC1: lỗi engine ghi 1 dòng ERROR có model, id, tên định nghĩa) |
| Requirement Ref | REQ-OBS-002 AC1 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD (tên 'FX-DEF-STD') có `start_domain` bị ghi trực tiếp bằng SQL thành `[('x_removed_field', '=', 1)]` để mô phỏng field đã bị gỡ sau khi lưu (bỏ qua kiểm tra lúc lưu của REQ-FUNC-003).
4. Bắt log bằng `assertLogs(level='ERROR')` trên logger của module (logger `odoo.addons.dwo_sla_core.models.sla_event`, định dạng "SLA engine error: model=%s id=%s definition=%s message=%s").
5. Partner P-1 (`ref` = 'OLD') đã tồn tại

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Giá trị lưu | `ref` = 'NEW' |  |
| Chuỗi cần có trong dòng log | 'res.partner', str(P-1.id), 'FX-DEF-STD' |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Trong `assertLogs`, ghi P-1 {ref: 'NEW'} | Không ném ngoại lệ |
| 2 | Lọc các bản ghi log mức ERROR liên quan tới lỗi SLA của P-1 | Có đúng 1 dòng |
| 3 | Kiểm tra nội dung dòng đó | Chứa đồng thời 'res.partner', số id của P-1 và 'FX-DEF-STD' |

**Pass/Fail Criteria:** ✅ Pass: đúng 1 dòng ERROR đủ ba chuỗi; ❌ Fail: 0 hoặc ≥ 2 dòng, mức khác ERROR, hoặc thiếu chuỗi

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-009: Không để chuỗi SECRET-123 xuất hiện trong event và log khi engine lỗi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-04 |
| Coverage Item | CI-1 (AC1: record có SECRET-123 gây lỗi engine) |
| Requirement Ref | REQ-OBS-003 AC1 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD (tên 'FX-DEF-STD') có `start_domain` bị ghi trực tiếp bằng SQL thành `[('x_removed_field', '=', 1)]` để mô phỏng field đã bị gỡ sau khi lưu (bỏ qua kiểm tra lúc lưu của REQ-FUNC-003).
4. Bắt log bằng `assertLogs(level='ERROR')` trên logger của module (logger `odoo.addons.dwo_sla_core.models.sla_event`, định dạng "SLA engine error: model=%s id=%s definition=%s message=%s").
5. Partner P-1 với `name` = 'SECRET-123' và `comment` = 'SECRET-123'

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Chuỗi nhạy cảm | SECRET-123 | trong `name` và `comment` của P-1 |
| Giá trị lưu | `ref` = 'NEW' |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Trong `assertLogs`, ghi P-1 {ref: 'NEW'} | Không ném ngoại lệ; có 1 event `error` |
| 2 | Duyệt mọi cột chuỗi (`note`, `res_model`, ...) của các event `error` | Không cột nào chứa 'SECRET-123' |
| 3 | Duyệt toàn bộ dòng log đã bắt | Không dòng nào chứa 'SECRET-123' |

**Pass/Fail Criteria:** ✅ Pass: không có 'SECRET-123' ở event nào hoặc dòng log nào; ❌ Fail: 'SECRET-123' xuất hiện ở bất kỳ đâu

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-010: Kiểm tra mã nguồn: đường ghi event error và log chỉ dùng tên model, id và tên định nghĩa

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-04 |
| Coverage Item | CI-2 (AC1 (Inspection): mã nguồn đường ghi lỗi chỉ dùng định danh) |
| Requirement Ref | REQ-OBS-003 |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Có mã nguồn `custom-addons/dwo_sla_core/` ở commit cần kiểm tra

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Phạm vi | Hàm ghi event `error` của Engine và mọi lời gọi `_logger.error/exception` trong module |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Liệt kê mọi nơi ghi `sla.event` với `event = 'error'` (grep `'error'` trong `models/`) | Mỗi nơi chỉ dùng `res_model`, `res_id`, `definition_id`, thông báo lỗi |
| 2 | Với mỗi lời gọi `_logger.error`/`_logger.exception` của module | Chuỗi định dạng chỉ nhận `record._name`, `record.id`, `definition.name`; không nhận `record.<field>`, `record.read()`, `record.display_name`, `vals` |
| 3 | Kiểm tra thông báo lỗi gốc được đưa vào `note` | Có bước loại bỏ/không đưa giá trị field của record, hoặc chỉ dùng tên lớp ngoại lệ (TA-28 CÒN MỞ: code `sla_engine._evaluate_definition` lưu `str(exc)` thô vào `note`; cơ chế lọc theo OBS-003 chưa quy định) |
| 4 | Ghi kết quả vào biên bản kiểm tra | Mỗi mục có kết luận Đạt/Không đạt kèm tên file và số dòng |

**Pass/Fail Criteria:** ✅ Pass: cả 3 mục kiểm tra Đạt; ❌ Fail: có nơi nào đưa giá trị field của record vào event hoặc log

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-011: Không đưa giá trị field của record vào event khi thông báo lỗi gốc chứa giá trị đó

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-04 |
| Coverage Item | CI-3 (Thông báo lỗi gốc chứa giá trị field) |
| Requirement Ref | REQ-OBS-003 |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
4. Bắt log bằng `assertLogs(level='ERROR')` trên logger của module (logger `odoo.addons.dwo_sla_core.models.sla_event`, định dạng "SLA engine error: model=%s id=%s definition=%s message=%s").
5. Partner P-1 với `ref` = 'SECRET-123'
6. Mock Time Service `plan` ném `ValueError('cannot plan for SECRET-123')` (giá trị field lọt vào thông báo gốc)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Chuỗi nhạy cảm | SECRET-123 | nằm trong thông báo ngoại lệ gốc |
| Giá trị lưu | `comment` = 'x' rồi `ref` = 'NEW' |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Ghi P-1 {ref: 'NEW'} (start của FX-DEF-STD khớp) trong `assertLogs` | Không ném ngoại lệ; có 1 event `error` |
| 2 | Kiểm tra `note` và log | Không chứa 'SECRET-123' (Phụ thuộc: TA-28 CÒN MỞ: cơ chế lọc thông báo gốc chưa quy định; code hiện lưu `str(exc)` thô nên bước này dự kiến phát hiện lệch) |
| 3 | Kiểm tra `note` còn thông tin chẩn đoán | `note` không rỗng (ví dụ chứa 'ValueError') |

**Pass/Fail Criteria:** ✅ Pass: 'SECRET-123' không xuất hiện trong `note` và log, `note` vẫn không rỗng; ❌ Fail: 'SECRET-123' xuất hiện

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-012: Đặt event error mới ở trạng thái chưa xử lý

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-05 |
| Coverage Item | CI-1 (AC1: event error mới ở trạng thái chưa xử lý) |
| Requirement Ref | REQ-FUNC-040 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD (tên 'FX-DEF-STD') có `start_domain` bị ghi trực tiếp bằng SQL thành `[('x_removed_field', '=', 1)]` để mô phỏng field đã bị gỡ sau khi lưu (bỏ qua kiểm tra lúc lưu của REQ-FUNC-003).
4. Partner P-1 (`ref` = 'OLD') đã tồn tại; U-BIZ ghi P-1 {ref: 'NEW'} để sinh 1 event `error` (E1)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Event | E1 | event `error` vừa sinh |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Đọc E1 | `event` = 'error'; `is_resolved` = false |
| 2 | Đếm event `error` chưa xử lý | = 1 |

**Pass/Fail Criteria:** ✅ Pass: `is_resolved` = false; ❌ Fail: `is_resolved` = true

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-013: Đánh dấu đã xử lý làm đổi trạng thái và giảm số cảnh báo đúng 1

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-05 |
| Coverage Item | CI-2 (AC2: SLA Manager đánh dấu đã xử lý) |
| Requirement Ref | REQ-FUNC-040 AC2 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD (tên 'FX-DEF-STD') có `start_domain` bị ghi trực tiếp bằng SQL thành `[('x_removed_field', '=', 1)]` để mô phỏng field đã bị gỡ sau khi lưu (bỏ qua kiểm tra lúc lưu của REQ-FUNC-003).
4. 3 partner P-1, P-2, P-3 (`ref` = 'OLD'); U-BIZ ghi từng partner {ref: 'NEW'} để sinh 3 event `error` E1, E2, E3 (đều chưa xử lý)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Event được đánh dấu | E2 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | U-MGR đếm event `error` chưa xử lý | = 3 |
| 2 | U-MGR gọi `E2.action_mark_resolved()` (thao tác 'Đánh dấu đã xử lý') | Không ném lỗi; đọc lại bằng sudo `E2.is_resolved` = True |
| 3 | Đọc E1, E2, E3 | `is_resolved`: E1 = false, E2 = true, E3 = false |
| 4 | U-MGR đếm lại event `error` chưa xử lý | = 2 |

**Pass/Fail Criteria:** ✅ Pass: E2 đã xử lý và số cảnh báo giảm từ 3 xuống 2; ❌ Fail: số không giảm hoặc giảm sai event

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-014: Chuyển event sang đã xử lý khi đánh giá lại record liên quan hoàn tất không lỗi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-05 |
| Coverage Item | CI-3 (AC3: đánh giá lại record liên quan thành công) |
| Requirement Ref | REQ-FUNC-040 AC3 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD (tên 'FX-DEF-STD') có `start_domain` bị ghi trực tiếp bằng SQL thành `[('x_removed_field', '=', 1)]` để mô phỏng field đã bị gỡ sau khi lưu (bỏ qua kiểm tra lúc lưu của REQ-FUNC-003).
4. Partner P-1 (`ref` = 'OLD') đã tồn tại; U-BIZ ghi P-1 {ref: 'NEW'} để sinh 1 event `error` (E1)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Cách sửa nguyên nhân | đặt lại `start_domain` = `[('ref', 'in', ['NEW', 'WORK', 'HOLD'])]` |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Sửa nguyên nhân: ghi `start_domain` hợp lệ của FX-DEF-STD | Lưu thành công |
| 2 | Với patch `odoo.fields.Datetime.now` trả FX-T0 + 1h, U-MGR gọi `E1.action_reevaluate_batch()` | Không ném lỗi; P-1 có đúng 1 task `in_progress` với `start_time` = FX-T0 + 1h (10:00) |
| 3 | Đọc E1 | `is_resolved` = true |
| 4 | Đếm event `error` chưa xử lý | = 0 |

**Pass/Fail Criteria:** ✅ Pass: E1 đã xử lý và task đã được gắn; ❌ Fail: E1 vẫn chưa xử lý

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-015: Giữ event cũ chưa xử lý và ghi event error mới khi đánh giá lại vẫn lỗi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-05 |
| Coverage Item | CI-4 (AC4: đánh giá lại vẫn lỗi) |
| Requirement Ref | REQ-FUNC-040 AC4 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD (tên 'FX-DEF-STD') có `start_domain` bị ghi trực tiếp bằng SQL thành `[('x_removed_field', '=', 1)]` để mô phỏng field đã bị gỡ sau khi lưu (bỏ qua kiểm tra lúc lưu của REQ-FUNC-003).
4. Partner P-1 (`ref` = 'OLD') đã tồn tại; U-BIZ ghi P-1 {ref: 'NEW'} để sinh 1 event `error` (E1)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Nguyên nhân | chưa sửa | domain vẫn trỏ field đã bị gỡ |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với patch `odoo.fields.Datetime.now` trả FX-T0 + 1h, U-MGR gọi `E1.action_reevaluate_batch()` | Không ném ngoại lệ |
| 2 | Đọc E1 | `is_resolved` = false |
| 3 | Đếm event `error` của P-1 | = 2 (E1 và event mới), cả hai `is_resolved` = false |

**Pass/Fail Criteria:** ✅ Pass: E1 chưa xử lý và có thêm 1 event `error` mới; ❌ Fail: E1 bị đánh dấu đã xử lý hoặc không có event mới

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-016: Đánh giá lại 3 event error đã chọn: tạo 3 task thiếu và chuyển 3 event sang đã xử lý

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-06 |
| Coverage Item | CI-1 (AC1: chọn 3 event error sau khi sửa nguyên nhân) |
| Requirement Ref | REQ-FUNC-031 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD (tên 'FX-DEF-STD') có `start_domain` bị ghi trực tiếp bằng SQL thành `[('x_removed_field', '=', 1)]` để mô phỏng field đã bị gỡ sau khi lưu (bỏ qua kiểm tra lúc lưu của REQ-FUNC-003).
4. 3 partner P-1, P-2, P-3 (`ref` = 'OLD'); U-BIZ ghi từng partner {ref: 'NEW'} → 3 event `error` E1, E2, E3
5. Nguyên nhân đã sửa: `start_domain` đặt lại = `[('ref', 'in', ['NEW', 'WORK', 'HOLD'])]`

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Event chọn | E1, E2, E3 |  |
| now | FX-T0 + 1h (10:00) | đồng hồ patch |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với patch `odoo.fields.Datetime.now` trả FX-T0 + 1h, U-MGR gọi `action_reevaluate_batch()` trên recordset {E1, E2, E3} | Không ném lỗi; không có event `error` mới |
| 2 | Đếm `sla.task` `in_progress` của P-1, P-2, P-3 | Mỗi partner 1 task (tổng 3), `start_time` = 10:00 |
| 3 | Đọc E1, E2, E3 | Cả ba `is_resolved` = true |

**Pass/Fail Criteria:** ✅ Pass: 3 task được tạo và 3 event đã xử lý; ❌ Fail: thiếu task, event còn chưa xử lý, hoặc record khác bị đánh giá

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-017: Giữ nguyên task achieved khi đánh giá lại hàng loạt

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-06 |
| Coverage Item | CI-2 (AC2: record có task achieved không đổi) |
| Requirement Ref | REQ-FUNC-031 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7). (domain hợp lệ)
4. Partner P-1: attach lúc FX-T0 rồi stop lúc 10:00 (ref 'DONE') → 1 task `achieved`, `end_time` = 10:00
5. Event `error` E1 cho (FX-DEF-STD, P-1) tạo qua ORM bằng quyền hệ thống (mô phỏng lỗi cũ chưa xử lý)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Task | achieved, end_time 10:00 |  |
| now | FX-T0 + 2h (11:00) |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Chụp trạng thái task (id, stage, start_time, end_time, business_duration) và số event của task | stage = `achieved` |
| 2 | Với patch `odoo.fields.Datetime.now` trả 11:00, U-MGR gọi `E1.action_reevaluate_batch()` | Không ném lỗi |
| 3 | So sánh trạng thái task và số event | Giống hệt ảnh chụp; không có task mới cho P-1 (tổng 1 task) |
| 4 | Đọc E1 | `is_resolved` = true (đánh giá lại hoàn tất không lỗi) |

**Pass/Fail Criteria:** ✅ Pass: task achieved giữ nguyên mọi giá trị và không có task mới; ❌ Fail: task đổi stage/giá trị, hoặc có task mới

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-018: Bỏ qua lặng lẽ event không phải error khi đánh giá lại hàng loạt (chỉ E1 được đánh giá lại)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-06 |
| Coverage Item | CI-3 (AC3: chọn event không phải error) |
| Requirement Ref | REQ-FUNC-031 AC3 |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7). (domain hợp lệ)
4. Partner P-1 đã attach → event `attach` EV-A; Partner P-2 có event `error` E1 chưa xử lý (tạo qua ORM hệ thống)
5. Spy bọc Engine `evaluate` ghi lại các record được đánh giá

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Event chọn | EV-A (attach) và E1 (error) |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | U-MGR gọi `action_reevaluate_batch()` trên recordset {EV-A, E1} | Không ném lỗi; EV-A bị bỏ qua lặng lẽ (D5/TA-09 đã chốt: event không phải `error` bị bỏ qua), `EV-A.is_resolved` vẫn False |
| 2 | Kiểm tra spy | Đúng 1 lần đánh giá, cho record của E1 (P-2); không có lần đánh giá nào cho record của EV-A (P-1) |

**Pass/Fail Criteria:** ✅ Pass: event `attach` bị bỏ qua (không ném lỗi, không đổi `is_resolved`, không đánh giá lại record của nó) và E1 được đánh giá lại; ❌ Fail: record của event `attach` bị đánh giá lại, hoặc ném lỗi

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-019: Từ chối hành động đánh giá lại hàng loạt đối với người dùng group_sla_user

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-06 |
| Coverage Item | CI-4 (AC4: người dùng group_sla_user) |
| Requirement Ref | REQ-FUNC-031 AC4 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD (tên 'FX-DEF-STD') có `start_domain` bị ghi trực tiếp bằng SQL thành `[('x_removed_field', '=', 1)]` để mô phỏng field đã bị gỡ sau khi lưu (bỏ qua kiểm tra lúc lưu của REQ-FUNC-003).
4. Partner P-1 → event `error` E1; U-USR thuộc `group_sla_user`

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-USR |  |
| Event | E1 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | U-USR gọi `E1.with_user(U-USR).action_reevaluate_batch()` | Ném `AccessError` chứa "SLA Manager" (ACC_002) |
| 2 | Đọc E1 và đếm task của P-1 | `is_resolved` = false; 0 task |
| 3 | Kiểm tra định nghĩa action/nút trong view danh sách event với U-USR | Hành động không hiển thị cho U-USR (`groups` = `group_sla_manager`) |

**Pass/Fail Criteria:** ✅ Pass: hành động bị từ chối và không có thay đổi dữ liệu; ❌ Fail: U-USR đánh giá lại được

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-020: Dùng thời điểm hiện tại làm mốc bắt đầu khi đánh giá lại hàng loạt (không bật retroactive)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-06 |
| Coverage Item | CI-5 (Thời điểm hiện tại, không retroactive) |
| Requirement Ref | REQ-FUNC-031 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD (tên 'FX-DEF-STD') có `start_domain` bị ghi trực tiếp bằng SQL thành `[('x_removed_field', '=', 1)]` để mô phỏng field đã bị gỡ sau khi lưu (bỏ qua kiểm tra lúc lưu của REQ-FUNC-003).
4. Partner P-1 tạo lúc FX-T0 → event `error` E1; nguyên nhân sửa: `start_domain` hợp lệ; `retroactive_start` = false

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Thời điểm lỗi | 09:00 |  |
| Thời điểm đánh giá lại | 14:00 (FX-T0 + 5h) |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Patch `odoo.fields.Datetime.now` trả 14:00; U-MGR gọi `E1.action_reevaluate_batch()` | Không ném lỗi; `E1.is_resolved` = True |
| 2 | Đọc task của P-1 | 1 task `in_progress`; `start_time` = 14:00 (không phải 09:00); `planned_end_time` = 18:00 |

**Pass/Fail Criteria:** ✅ Pass: `start_time` = 14:00 và `planned_end_time` = 18:00; ❌ Fail: `start_time` = 09:00 hoặc giá trị khác

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-021: Lấy mốc bắt đầu từ field ngày giờ khi đánh giá lại hàng loạt có bật retroactive start

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-06 |
| Coverage Item | CI-6 (Retroactive start bật: lấy mốc từ field của record) |
| Requirement Ref | REQ-FUNC-031 |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD (tên 'FX-DEF-STD') có `start_domain` bị ghi trực tiếp bằng SQL thành `[('x_removed_field', '=', 1)]` để mô phỏng field đã bị gỡ sau khi lưu (bỏ qua kiểm tra lúc lưu của REQ-FUNC-003).
4. `retroactive_start` = true, `retroactive_field_id` = `res.partner.create_date`
5. Partner P-1 có `create_date` đặt bằng SQL = 09:00 (02:00 UTC) → event `error` E1; nguyên nhân sửa: `start_domain` hợp lệ

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| create_date của P-1 | 2026-03-02 09:00 |  |
| Thời điểm đánh giá lại | 10:00 (FX-T0 + 1h) |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Patch `odoo.fields.Datetime.now` trả 10:00; U-MGR gọi `E1.action_reevaluate_batch()` | Không ném lỗi; `E1.is_resolved` = True |
| 2 | Đọc task của P-1 | 1 task `in_progress`; `start_time` = 09:00 (từ `create_date`); `planned_end_time` = 13:00 |

**Pass/Fail Criteria:** ✅ Pass: `start_time` = 09:00 theo field retroactive; ❌ Fail: `start_time` = 10:00

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-022: Hiển thị số 3 cho SLA Manager khi có 3 event error chưa xử lý

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-07 |
| Coverage Item | CI-1 (AC1: 3 event chưa xử lý, SLA Manager thấy số 3) |
| Requirement Ref | REQ-INT-022 AC1 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD (tên 'FX-DEF-STD') có `start_domain` bị ghi trực tiếp bằng SQL thành `[('x_removed_field', '=', 1)]` để mô phỏng field đã bị gỡ sau khi lưu (bỏ qua kiểm tra lúc lưu của REQ-FUNC-003).
4. 3 partner P-1, P-2, P-3; U-BIZ ghi từng partner {ref: 'NEW'} → 3 event `error` E1, E2, E3 chưa xử lý

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-MGR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | U-MGR gọi nguồn dữ liệu của nhãn số (`search_count([('event', '=', 'error'), ('is_resolved', '=', False)])` trên `sla.event` bằng U-MGR) (nhãn số của menu 'Unresolved Error Events' dùng cùng điều kiện đếm này) | = 3 |

**Pass/Fail Criteria:** ✅ Pass: số đếm = 3; ❌ Fail: số đếm khác 3

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-023: Giảm số hiển thị xuống 2 sau khi đánh dấu 1 event đã xử lý

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-07 |
| Coverage Item | CI-2 (AC2: đánh dấu 1 event đã xử lý) |
| Requirement Ref | REQ-INT-022 AC2 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD (tên 'FX-DEF-STD') có `start_domain` bị ghi trực tiếp bằng SQL thành `[('x_removed_field', '=', 1)]` để mô phỏng field đã bị gỡ sau khi lưu (bỏ qua kiểm tra lúc lưu của REQ-FUNC-003).
4. 3 partner P-1, P-2, P-3; U-BIZ ghi từng partner {ref: 'NEW'} → 3 event `error` E1, E2, E3 chưa xử lý

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Event được đánh dấu | E3 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | U-MGR gọi `E3.action_mark_resolved()` | Không ném lỗi; `E3.is_resolved` = True (đọc bằng sudo) |
| 2 | U-MGR đếm event `error` chưa xử lý | = 2 |

**Pass/Fail Criteria:** ✅ Pass: số đếm = 2; ❌ Fail: số đếm vẫn 3 hoặc khác 2

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-024: Không hiển thị số event lỗi cho người dùng không thuộc nhóm SLA

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-07 |
| Coverage Item | CI-3 (AC3: người dùng không thuộc nhóm SLA) |
| Requirement Ref | REQ-INT-022 AC3 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` trả FX-T0 (2026-03-02 09:00) cho đường hook (hook gọi `evaluate(now=None)` nên dùng `fields.Datetime.now()`; TA-01 đã chốt).
3. Định nghĩa FX-DEF-STD (tên 'FX-DEF-STD') có `start_domain` bị ghi trực tiếp bằng SQL thành `[('x_removed_field', '=', 1)]` để mô phỏng field đã bị gỡ sau khi lưu (bỏ qua kiểm tra lúc lưu của REQ-FUNC-003).
4. 3 partner P-1, P-2, P-3; U-BIZ ghi từng partner {ref: 'NEW'} → 3 event `error` E1, E2, E3 chưa xử lý
5. U-NONE (không có nhóm SLA) có quyền đọc menu gốc của Odoo

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-NONE |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | U-NONE gọi `sla.event.search_count([('event', '=', 'error'), ('is_resolved', '=', False)])` | Ném `AccessError` (không có quyền đọc `sla.event`) |
| 2 | Lấy danh sách menu U-NONE thấy được (`ir.ui.menu._visible_menu_ids`) | Menu 'SLA' (`dwo_sla_core.menu_sla_root`) và mục 'Unresolved Error Events' (`dwo_sla_core.menu_sla_event_error_unresolved`) không nằm trong danh sách |

**Pass/Fail Criteria:** ✅ Pass: không đếm được và không thấy menu SLA; ❌ Fail: U-NONE đọc được số hoặc thấy menu

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-025: Trình diễn nhãn số event lỗi chưa xử lý trên menu SLA cho Manager và ẩn với người không thuộc nhóm SLA

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-07 |
| Coverage Item | CI-4 (Demonstration: nhãn số trên menu và danh sách event) |
| Requirement Ref | REQ-INT-022 |
| Priority | P3-Medium |
| Test Type | Demonstration |
| Automation | Manual |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Database demo có đúng 3 event `error` chưa xử lý, tạo trong Preconditions của ca này: định nghĩa FX-DEF-STD có `start_domain` ghi bằng SQL thành `[('x_removed_field', '=', 1)]`; 3 partner P-1..P-3; U-BIZ ghi từng partner {ref: 'NEW'}
3. Trình duyệt, hai phiên đăng nhập: U-MGR và U-NONE

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Dữ liệu | 3 event `error` chưa xử lý |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Đăng nhập U-MGR, mở menu SLA | Mục 'Event lỗi' có nhãn số '3'; danh sách event hiển thị cảnh báo số chưa xử lý |
| 2 | Đánh dấu 1 event đã xử lý rồi tải lại trang | Nhãn số đổi thành '2' |
| 3 | Đăng nhập U-NONE | Không có menu SLA, không thấy nhãn số |
| 4 | Ghi biên bản Demonstration kèm ảnh chụp màn hình | Cả 3 mục đạt |

**Pass/Fail Criteria:** ✅ Pass: 3/3 mục quan sát đạt; ❌ Fail: nhãn số sai, hoặc hiện với U-NONE

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-ERR-026: Stop của người dùng xung đột với xử lý nền đã commit trước (thứ tự A): thao tác stop không để lại dữ liệu dở dang và, khi lặp lại ở giao dịch mới, cho trạng thái cuối nhất quán

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-08 |
| Coverage Item | CI-1 (AC1 thứ tự A: xử lý nền commit trước, user stop gặp xung đột và thử lại) |
| Requirement Ref | REQ-REL-001 AC1 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (hai cursor, không dùng TransactionCase đơn) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') đã commit; task T của P-1 attach lúc FX-T0 đã commit; mốc 75% đến hạn 12:00.
7. Hai cursor C1 (xử lý nền) và C2 (U-BIZ), cả hai REPEATABLE READ; `odoo.fields.Datetime.now` được patch trả 12:00 giờ VN ở cả hai.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Thứ tự | C2 đọc T, C1 chạy và commit, C2 ghi |  |
| Thời điểm | 12:00 giờ VN | stop lúc đã trôi 3 giờ, nhỏ hơn 4 giờ |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | C2: bắt đầu giao dịch, đọc T (snapshot) | T `in_progress` |
| 2 | C1: gọi `process_due()` rồi commit | T có 1 event `escalate`; `call_count` SA-N75 = 1 |
| 3 | C2: ghi P-1 {ref: 'DONE'} (hook gọi `evaluate`) trong giao dịch cũ | Không có thay đổi nào của C2 trên T được lưu: T chưa `achieved`, không có event `complete` do C2 |
| 4 | C2: mở giao dịch mới và lặp lại đúng thao tác ghi P-1 {ref: 'DONE'} (không dùng cơ chế retry của Odoo) | Thành công, không ném lỗi |
| 5 | Đọc trạng thái cuối bằng cursor mới | T `stage` = `achieved`; đúng 1 event `complete`; đúng 1 event `escalate`; P-1 `ref` = 'DONE'; không event trùng |

**Pass/Fail Criteria:** ✅ Pass: bước 3 không để lại thay đổi của C2 và trạng thái cuối ở bước 5 đúng; ❌ Fail: mất stop, mất `escalate`, hoặc có event trùng

**Ghi chú:** Kết quả quan sát ở bước 3 không phụ thuộc việc xung đột tuần tự hóa được ném ra hay được Engine bắt trong savepoint theo record (TA-19, TA-20).

**Postconditions:** Dữ liệu đã commit bởi các cursor: dọn bằng xóa bản ghi test trong `tearDown`.

### TC-ERR-027: Người dùng stop task commit trước xử lý nền (thứ tự B): xử lý nền không lưu event `escalate` cho task đã dừng

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-08 |
| Coverage Item | CI-2 (AC1 thứ tự B: user stop commit trước, xử lý nền không lưu kết quả cho task đã dừng) |
| Requirement Ref | REQ-REL-001 AC1 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (hai cursor, không dùng TransactionCase đơn) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Partner P-1 (`ref` = 'NEW') đã commit; task T của P-1 attach lúc FX-T0 đã commit; mốc 75% đến hạn 12:00.
7. Hai cursor C1 (xử lý nền) và C2 (U-BIZ), cả hai REPEATABLE READ; `odoo.fields.Datetime.now` được patch trả 12:00 giờ VN ở cả hai.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Thứ tự | C1 đọc danh sách task đến hạn, C2 stop và commit, C1 tiếp tục |  |
| Thời điểm | 12:00 giờ VN |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | C1: bắt đầu giao dịch, chạy `process_due()` tới ngay sau lệnh tìm task đến hạn và trước lệnh khóa (dừng bằng barrier) | T nằm trong danh sách ứng viên của C1 |
| 2 | C2: ghi P-1 {ref: 'DONE'} (hook gọi `evaluate`) rồi commit | T `stage` = `achieved`; 1 event `complete` |
| 3 | Mở barrier: C1 tiếp tục (khóa và xử lý T) | C1 không lưu event `escalate` nào cho T; `call_count` SA-N75 = 0 |
| 4 | Chạy lại `process_due()` trong giao dịch mới | Không chọn T (đã `achieved`); `call_count` SA-N75 vẫn = 0 |
| 5 | Đọc trạng thái cuối bằng cursor mới | T `achieved`; số event `complete` = 1; số event `escalate` = 0 |

**Pass/Fail Criteria:** ✅ Pass: stop của người dùng được giữ và không có event `escalate` cho task đã dừng; ❌ Fail: có event `escalate` cho T hoặc mất stop

**Ghi chú:** Quan sát bước 3 là trạng thái đã lưu của C1 (C1 có thể kết thúc bằng lỗi tuần tự hóa hoặc bỏ qua T; cả hai cho cùng kết quả đã lưu).

**Postconditions:** Dữ liệu đã commit bởi các cursor: dọn bằng xóa bản ghi test trong `tearDown`.

### TC-ERR-028: Đo thời gian chờ khóa của lần lưu record khác khi action nền đang chậm (p95 qua 20 lần ≤ 5 giây)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-08 |
| Coverage Item | CI-3 (AC2: action chậm không làm user chờ khóa quá 5 giây (p95/20)) |
| Requirement Ref | REQ-REL-001 AC2 |
| Priority | P2-High |
| Test Type | Performance |
| Automation | Automated (hai cursor, không dùng TransactionCase đơn) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-SLOW, `retry` = false).
4. Server action SA-SLOW: khi được gọi thì chặn lại tại điểm đồng bộ của test (giữ giao dịch C1 mở, mô phỏng 30 giây) mà không `sleep`
5. Hai partner P-SLOW (task đến hạn 12:00) và P-OTHER (task attach FX-T0, chưa đến hạn); cả hai đã commit
6. Cursor C1 (nền) và C2 (U-BIZ)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Số lần lặp | 20 | mỗi lần dựng lại trạng thái |
| Đo | `time.monotonic()` quanh lệnh ghi của C2 |  |
| Thống kê | p95 (hạng thứ 19 của 20 giá trị sắp xếp tăng) và max | ngưỡng p95 ≤ 5,0 giây |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Lặp 20 lần: với patch `odoo.fields.Datetime.now` trả 12:00 giờ VN, C1 chạy `process_due()` tới khi SA-SLOW chặn (C1 giữ khóa dòng task của P-SLOW, chưa commit) | C1 đang giữ giao dịch mở |
| 2 | C2: ghi P-OTHER {comment: 'n'} (kích hoạt hook và `evaluate` của P-OTHER), đo thời gian | Lệnh ghi hoàn tất, không chờ khóa của C1 |
| 3 | Giải phóng SA-SLOW và rollback/commit C1; ghi lại thời gian mẫu | Có 20 mẫu |
| 4 | Tính p95 của 20 mẫu | p95 ≤ 5,0 giây |

**Pass/Fail Criteria:** ✅ Pass: p95 của 20 mẫu ≤ 5,0 giây và không mẫu nào bị timeout; ❌ Fail: p95 > 5,0 giây hoặc C2 bị chặn tới khi C1 kết thúc

**Postconditions:** Rollback C1 và dọn dữ liệu đã commit trong `tearDown`.

### TC-ERR-029: Task đến hạn bị người dùng stop trước khi xử lý nền khóa: không lưu kết quả xung đột, lần chạy sau chỉ xử lý task còn lại và không bắn lặp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-12-09 |
| Coverage Item | CI-1 (Lô chứa task bị user stop đồng thời) |
| Requirement Ref | REQ-REL-002 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (hai cursor, không dùng TransactionCase đơn) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none` tức 24x7).
3. Mốc escalation 75% (`percent` = 75, `action_id` = SA-N75, `retry` = false).
4. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.
5. Wrapper đếm lời gọi `ir.actions.server.run` theo (server action, record id) gọi là `call_count`; server action thành công mặc định chỉ gọi `record.message_post`.
6. Tham số `dwo_sla_core.batch_size` = 2 (trần mỗi lần gọi).
7. Partner T1-rec và T2-rec (`ref` = 'NEW') đã commit; hai task attach FX-T0 đã commit, mốc 75% cùng đến hạn 12:00; `next_due_at` của T1 sớm hơn T2 để C1 khóa T1 trước. Cursor C1 (xử lý nền), C2 (U-BIZ); `odoo.fields.Datetime.now` patch trả 12:00 giờ VN.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Task đến hạn | T1, T2 | batch_size = 2 chỉ là trần mỗi lần gọi |
| Thời điểm | 12:00 giờ VN |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | C1: bắt đầu `process_due()`, dừng bằng barrier sau lệnh tìm task đến hạn và trước lệnh khóa | Cả hai task nằm trong danh sách ứng viên |
| 2 | C2: stop T1-rec (ghi `ref` = 'DONE', hook gọi `evaluate`) rồi commit | T1 `achieved` |
| 3 | Mở barrier: C1 tiếp tục | Sau khi C1 kết thúc (lỗi hay hoàn tất), dữ liệu đã lưu của C1 không có event `escalate` nào cho T1; T1 vẫn `achieved` |
| 4 | Chạy lại `process_due()` trong giao dịch mới | T2 có đúng 1 event `escalate`; T1 có 0 event `escalate` |
| 5 | Chạy `process_due()` thêm một lần | `call_count` của T2-rec vẫn = 1 (không bắn lặp) |

**Pass/Fail Criteria:** ✅ Pass: T1 không có `escalate`, T2 bắn đúng 1 lần ở lần chạy sau; ❌ Fail: T1 bắn dù đã stop, T2 bắn 2 lần hoặc bị bỏ sót

**Postconditions:** Dữ liệu đã commit bởi các cursor: dọn bằng xóa bản ghi test trong `tearDown`.

## TG-13 — Field compute có lưu

### TC-CMP-001: Kết thúc task đúng 1 lần khi đổi stage làm field compute có lưu is_resolved đổi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-13-01 |
| Coverage Item | CI-1 (AC1: stage đổi sang resolved làm is_resolved đổi → stop) |
| Requirement Ref | REQ-FUNC-005 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` theo từng bước (đường hook dùng `fields.Datetime.now()`, TA-01).
3. FX-CMP (model kiểm thử `x.sla.cmp.ticket`, khai báo trong module test): `name` Char; `stage` Selection (`new`, `work`, `resolved`); `is_resolved` Boolean compute `store=True` phụ thuộc `stage` (true khi `stage` = 'resolved'); `weight` Integer; `lvl` Integer compute `store=True` phụ thuộc `weight` (= weight // 10); `is_big` Boolean compute KHÔNG lưu phụ thuộc `weight` (true khi weight ≥ 100); `partner_id` Many2one `res.partner`; `parent_id` Many2one cùng model, `child_ids` One2many; `children_done` Boolean compute `store=True` phụ thuộc `child_ids.stage` (true khi có con và mọi con `resolved`). (ghi chú fixture: dựng model kiểm thử vì `res.partner` không có field compute có lưu phù hợp)
4. Định nghĩa DEF-CMP trên `x.sla.cmp.ticket`: mục tiêu 4 giờ, nguồn lịch `none` (24x7), start `[('stage', 'in', ['new', 'work'])]`, stop `[('is_resolved', '=', True)]`, cancel/pause/resume/reset rỗng.
5. Ticket K (`stage` = 'new') tạo lúc FX-T0 → 1 task `in_progress`, 1 event `attach`

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Ghi | `stage` = 'resolved' | chỉ ghi `stage`, không ghi `is_resolved` |
| Thời điểm | 10:00 | FX-T0 + 1h |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo K {stage: 'new'} lúc 09:00 | 1 task `in_progress`; `is_resolved` = false |
| 2 | Đặt đồng hồ 10:00; ghi K {stage: 'resolved'} | `is_resolved` = true (đã lưu) |
| 3 | Đọc task và event của K | Task `stage` = `achieved`, `end_time` = 10:00; đúng 1 event `complete`; tổng event = 2 (`attach`, `complete`) |

**Pass/Fail Criteria:** ✅ Pass: đúng 1 event `complete` và task `achieved`; ❌ Fail: 0 event `complete` (bỏ sót) hoặc ≥ 2 event `complete`

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CMP-002: Không sinh event attach hoặc cancel dư thừa khi ghi 3 lần trong một giao dịch

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-13-01 |
| Coverage Item | CI-2 (AC2: 3 lần ghi trong một giao dịch) |
| Requirement Ref | REQ-FUNC-005 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` theo từng bước (đường hook dùng `fields.Datetime.now()`, TA-01).
3. FX-CMP (model kiểm thử `x.sla.cmp.ticket`, khai báo trong module test): `name` Char; `stage` Selection (`new`, `work`, `resolved`); `is_resolved` Boolean compute `store=True` phụ thuộc `stage` (true khi `stage` = 'resolved'); `weight` Integer; `lvl` Integer compute `store=True` phụ thuộc `weight` (= weight // 10); `is_big` Boolean compute KHÔNG lưu phụ thuộc `weight` (true khi weight ≥ 100); `partner_id` Many2one `res.partner`; `parent_id` Many2one cùng model, `child_ids` One2many; `children_done` Boolean compute `store=True` phụ thuộc `child_ids.stage` (true khi có con và mọi con `resolved`). (ghi chú fixture: dựng model kiểm thử vì `res.partner` không có field compute có lưu phù hợp)
4. Định nghĩa DEF-CMP trên `x.sla.cmp.ticket`: mục tiêu 4 giờ, nguồn lịch `none` (24x7), start `[('stage', 'in', ['new', 'work'])]`, stop `[('is_resolved', '=', True)]`, cancel/pause/resume/reset rỗng.
5. Định nghĩa DEF-CMP có `cancel_mode` = `start_unmatched`
6. Ticket K (`stage` = 'new') tạo lúc FX-T0 → 1 task `in_progress`, 1 event `attach`

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Ba lần ghi | `stage` = 'work'; `stage` = 'new'; `stage` = 'work' | trong cùng 1 giao dịch, start vẫn khớp ở mọi lần |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Trong một giao dịch, ghi K {stage: 'work'}, rồi {stage: 'new'}, rồi {stage: 'work'} | Không lỗi |
| 2 | Đọc task của K | Đúng 1 task, `stage` = `in_progress`, cùng id với task ban đầu |
| 3 | Đếm event của K theo loại | `attach` = 1; `cancel` = 0; `resume` = 0; `pause` = 0; tổng = 1 |

**Pass/Fail Criteria:** ✅ Pass: tổng event vẫn = 1 và không có task mới; ❌ Fail: xuất hiện `attach`/`cancel` thêm hoặc task mới

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CMP-003: Không sinh event khi field compute có lưu đổi giá trị nhưng kết quả điều kiện không đổi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-13-01 |
| Coverage Item | CI-3 (AC3: field compute đổi nhưng kết quả điều kiện không đổi) |
| Requirement Ref | REQ-FUNC-005 AC3 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` theo từng bước (đường hook dùng `fields.Datetime.now()`, TA-01).
3. FX-CMP (model kiểm thử `x.sla.cmp.ticket`, khai báo trong module test): `name` Char; `stage` Selection (`new`, `work`, `resolved`); `is_resolved` Boolean compute `store=True` phụ thuộc `stage` (true khi `stage` = 'resolved'); `weight` Integer; `lvl` Integer compute `store=True` phụ thuộc `weight` (= weight // 10); `is_big` Boolean compute KHÔNG lưu phụ thuộc `weight` (true khi weight ≥ 100); `partner_id` Many2one `res.partner`; `parent_id` Many2one cùng model, `child_ids` One2many; `children_done` Boolean compute `store=True` phụ thuộc `child_ids.stage` (true khi có con và mọi con `resolved`). (ghi chú fixture: dựng model kiểm thử vì `res.partner` không có field compute có lưu phù hợp)
4. Định nghĩa DEF-CMP2 trên `x.sla.cmp.ticket`: mục tiêu 4 giờ, 24x7, start `[('lvl', '>=', 1)]`, các điều kiện khác rỗng
5. Ticket K (`weight` = 10 → `lvl` = 1) tạo lúc FX-T0 → 1 task `in_progress`, 1 event `attach`

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Ghi | `weight` = 20 | `lvl` đổi 1 → 2 nhưng vẫn thỏa `lvl >= 1` |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Chụp số task và số event của K | task = 1; event = 1 |
| 2 | Ghi K {weight: 20} lúc 10:00 | `lvl` = 2 (đã lưu) |
| 3 | Đếm lại task và event của K | task = 1 (không đổi); event = 1 (không có event mới) |

**Pass/Fail Criteria:** ✅ Pass: số task và số event không đổi; ❌ Fail: xuất hiện event mới hoặc task mới

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CMP-004: Kết thúc task của record cha khi field compute có lưu children_done đổi do record con đổi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-13-01 |
| Coverage Item | CI-4 (Recompute qua quan hệ con làm field cha đổi) |
| Requirement Ref | REQ-FUNC-005 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` theo từng bước (đường hook dùng `fields.Datetime.now()`, TA-01).
3. FX-CMP (model kiểm thử `x.sla.cmp.ticket`, khai báo trong module test): `name` Char; `stage` Selection (`new`, `work`, `resolved`); `is_resolved` Boolean compute `store=True` phụ thuộc `stage` (true khi `stage` = 'resolved'); `weight` Integer; `lvl` Integer compute `store=True` phụ thuộc `weight` (= weight // 10); `is_big` Boolean compute KHÔNG lưu phụ thuộc `weight` (true khi weight ≥ 100); `partner_id` Many2one `res.partner`; `parent_id` Many2one cùng model, `child_ids` One2many; `children_done` Boolean compute `store=True` phụ thuộc `child_ids.stage` (true khi có con và mọi con `resolved`). (ghi chú fixture: dựng model kiểm thử vì `res.partner` không có field compute có lưu phù hợp)
4. Định nghĩa DEF-CMP3 trên `x.sla.cmp.ticket`: mục tiêu 4 giờ, 24x7, start `[('stage', '=', 'new')]`, stop `[('children_done', '=', True)]`
5. Ticket cha K (`stage` = 'new') và 1 ticket con C (`parent_id` = K, `stage` = 'new'); K có 1 task `in_progress`

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Thay đổi | C.stage = 'resolved' | chỉ ghi record con C, không ghi K |
| Thời điểm | 10:00 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Đặt đồng hồ 10:00; ghi C {stage: 'resolved'} | `K.children_done` = true (tính lại, đã lưu) |
| 2 | Đọc task và event của K | Task `stage` = `achieved`; đúng 1 event `complete` |

**Pass/Fail Criteria:** ✅ Pass: task của K kết thúc đúng 1 lần dù chỉ ghi record con; ❌ Fail: task của K không kết thúc hoặc có 2 event `complete`

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CMP-005: Bỏ qua recompute của field có lưu không nằm trong domain của định nghĩa nào

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-13-01 |
| Coverage Item | CI-5 (Field compute có lưu không nằm trong domain của định nghĩa nào) |
| Requirement Ref | REQ-FUNC-005 |
| Priority | P4-Low |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` theo từng bước (đường hook dùng `fields.Datetime.now()`, TA-01).
3. FX-CMP (model kiểm thử `x.sla.cmp.ticket`, khai báo trong module test): `name` Char; `stage` Selection (`new`, `work`, `resolved`); `is_resolved` Boolean compute `store=True` phụ thuộc `stage` (true khi `stage` = 'resolved'); `weight` Integer; `lvl` Integer compute `store=True` phụ thuộc `weight` (= weight // 10); `is_big` Boolean compute KHÔNG lưu phụ thuộc `weight` (true khi weight ≥ 100); `partner_id` Many2one `res.partner`; `parent_id` Many2one cùng model, `child_ids` One2many; `children_done` Boolean compute `store=True` phụ thuộc `child_ids.stage` (true khi có con và mọi con `resolved`). (ghi chú fixture: dựng model kiểm thử vì `res.partner` không có field compute có lưu phù hợp)
4. Định nghĩa DEF-CMP trên `x.sla.cmp.ticket`: mục tiêu 4 giờ, nguồn lịch `none` (24x7), start `[('stage', 'in', ['new', 'work'])]`, stop `[('is_resolved', '=', True)]`, cancel/pause/resume/reset rỗng.
5. Ticket K (`stage` = 'new', `weight` = 10) tạo lúc FX-T0 → 1 task, 1 event `attach`
6. Spy bọc Engine `evaluate` đếm số lần gọi, đặt sau khi tạo K

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Ghi | `weight` = 50 | `lvl` tính lại nhưng `lvl` không có trong domain nào của DEF-CMP; `weight` cũng không |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Ghi K {weight: 50} lúc 10:00 | `lvl` = 5 (đã lưu); không lỗi |
| 2 | Đọc spy `evaluate` và số event | Số lần gọi `evaluate` = 0; số event vẫn = 1; 0 event `error` |

**Pass/Fail Criteria:** ✅ Pass: `evaluate` không được gọi và không có event mới; ❌ Fail: `evaluate` được gọi hoặc có event `error`

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CMP-006: Gắn task khi đánh giá lại thủ công qua engine sau khi country của partner liên quan đổi sang VN

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-13-02 |
| Coverage Item | CI-1 (AC1: điều kiện qua quan hệ, partner đổi country sang VN rồi Đánh giá lại) |
| Requirement Ref | REQ-FUNC-042 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` theo từng bước (đường hook dùng `fields.Datetime.now()`, TA-01).
3. FX-CMP (model kiểm thử `x.sla.cmp.ticket`, khai báo trong module test): `name` Char; `stage` Selection (`new`, `work`, `resolved`); `is_resolved` Boolean compute `store=True` phụ thuộc `stage` (true khi `stage` = 'resolved'); `weight` Integer; `lvl` Integer compute `store=True` phụ thuộc `weight` (= weight // 10); `is_big` Boolean compute KHÔNG lưu phụ thuộc `weight` (true khi weight ≥ 100); `partner_id` Many2one `res.partner`; `parent_id` Many2one cùng model, `child_ids` One2many; `children_done` Boolean compute `store=True` phụ thuộc `child_ids.stage` (true khi có con và mọi con `resolved`). (ghi chú fixture: dựng model kiểm thử vì `res.partner` không có field compute có lưu phù hợp)
4. Định nghĩa DEF-REL trên `x.sla.cmp.ticket`: mục tiêu 4 giờ, 24x7, start `[('partner_id.country_id', '=', VN)]` (VN = `base.vn`), các điều kiện khác rỗng
5. Partner PX (country = Pháp) và ticket K (`partner_id` = PX); K chưa có task

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Thay đổi | PX.country_id = VN (`base.vn`) | chỉ ghi partner, không ghi K |
| now Đánh giá lại | 10:00 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Ghi PX {country_id: VN} | Lưu thành công; K vẫn có thể chưa có task (không yêu cầu tự đánh giá) |
| 2 | U-MGR: Gọi `sla.engine.evaluate(K, now=None, changed=set())` với patch `odoo.fields.Datetime.now` trả 10:00 (lõi của hành động đánh giá lại thủ công: `action_reevaluate` gom record gốc rồi gọi hàm này) | Không ném lỗi; 0 event `error` của K |
| 3 | Đọc task và event của K | 1 task `in_progress`, `start_time` = 10:00; 1 event `attach` |

**Pass/Fail Criteria:** ✅ Pass: sau đánh giá lại thủ công qua engine có đúng 1 task `in_progress` cho K; ❌ Fail: không có task hoặc có task trùng

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CMP-007: Không ghi event error khi điều kiện dùng field compute không lưu và field gốc đổi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-13-02 |
| Coverage Item | CI-2 (AC2: field compute không lưu, field gốc đổi, chưa đánh giá lại) |
| Requirement Ref | REQ-FUNC-042 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` theo từng bước (đường hook dùng `fields.Datetime.now()`, TA-01).
3. FX-CMP (model kiểm thử `x.sla.cmp.ticket`, khai báo trong module test): `name` Char; `stage` Selection (`new`, `work`, `resolved`); `is_resolved` Boolean compute `store=True` phụ thuộc `stage` (true khi `stage` = 'resolved'); `weight` Integer; `lvl` Integer compute `store=True` phụ thuộc `weight` (= weight // 10); `is_big` Boolean compute KHÔNG lưu phụ thuộc `weight` (true khi weight ≥ 100); `partner_id` Many2one `res.partner`; `parent_id` Many2one cùng model, `child_ids` One2many; `children_done` Boolean compute `store=True` phụ thuộc `child_ids.stage` (true khi có con và mọi con `resolved`). (ghi chú fixture: dựng model kiểm thử vì `res.partner` không có field compute có lưu phù hợp)
4. Định nghĩa DEF-NS trên `x.sla.cmp.ticket`: mục tiêu 4 giờ, 24x7, start `[('is_big', '=', True)]` (`is_big` compute không lưu), các điều kiện khác rỗng
5. Ticket K (`weight` = 50) tạo lúc FX-T0; K chưa có task

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Thay đổi | K.weight = 500 | `is_big` đổi false → true (không lưu) |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Ghi K {weight: 500} lúc 10:00 | Lưu thành công, không ngoại lệ |
| 2 | Đếm event `error` của K và của định nghĩa DEF-NS | = 0 |
| 3 | Đếm task của K | Không kiểm (SRS không yêu cầu tự cập nhật): chấp nhận 0 hoặc 1 |

**Pass/Fail Criteria:** ✅ Pass: 0 event `error`; ❌ Fail: có event `error`

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CMP-008: Gắn task theo dữ liệu hiện tại khi đánh giá lại thủ công qua engine với điều kiện dùng field compute không lưu

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-13-02 |
| Coverage Item | CI-3 (Đánh giá lại cho kết quả đúng với dữ liệu hiện tại (field không lưu)) |
| Requirement Ref | REQ-FUNC-042 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` theo từng bước (đường hook dùng `fields.Datetime.now()`, TA-01).
3. FX-CMP (model kiểm thử `x.sla.cmp.ticket`, khai báo trong module test): `name` Char; `stage` Selection (`new`, `work`, `resolved`); `is_resolved` Boolean compute `store=True` phụ thuộc `stage` (true khi `stage` = 'resolved'); `weight` Integer; `lvl` Integer compute `store=True` phụ thuộc `weight` (= weight // 10); `is_big` Boolean compute KHÔNG lưu phụ thuộc `weight` (true khi weight ≥ 100); `partner_id` Many2one `res.partner`; `parent_id` Many2one cùng model, `child_ids` One2many; `children_done` Boolean compute `store=True` phụ thuộc `child_ids.stage` (true khi có con và mọi con `resolved`). (ghi chú fixture: dựng model kiểm thử vì `res.partner` không có field compute có lưu phù hợp)
4. Định nghĩa DEF-NS trên `x.sla.cmp.ticket`: mục tiêu 4 giờ, 24x7, start `[('is_big', '=', True)]` (điều kiện dùng field compute không lưu), các điều kiện khác rỗng
5. Ticket K (`weight` = 50) tạo rồi ghi {weight: 500}; K chưa có task (field compute không lưu không đi qua hook nên hệ thống không tự gắn; nếu đã có 1 task thì bước 2 không được tạo task thứ hai)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| weight | 500 | is_big = true |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | U-MGR: Gọi `sla.engine.evaluate(K, now=None, changed=set())` với patch `odoo.fields.Datetime.now` trả 10:00 (lõi của hành động đánh giá lại thủ công: `action_reevaluate` gom record gốc rồi gọi hàm này) | Không ném lỗi; 0 event `error` của K |
| 2 | Đọc task của K | Đúng 1 task `in_progress` (không trùng dù hệ thống đã tự gắn trước đó) |
| 3 | U-MGR: gọi lại đúng lệnh bước 1 lần nữa | Không ném lỗi; số task và số event của K không đổi so với sau bước 1 |

**Pass/Fail Criteria:** ✅ Pass: đúng 1 task sau đánh giá lại thủ công qua engine và lần hai không đổi; ❌ Fail: không có task hoặc có 2 task

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CMP-009: Kiểm tra help text của các điều kiện trên form định nghĩa có nêu giới hạn field không lưu và điều kiện qua quan hệ

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-13-02 |
| Coverage Item | CI-4 (AC3 (Inspection): help text nêu giới hạn) |
| Requirement Ref | REQ-FUNC-042 AC3 |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Giao diện Odoo mở được, đăng nhập U-MGR
3. Có form định nghĩa SLA (REQ-INT-001) với các field điều kiện: `start_domain`, `cancel_domain`, `pause_domain`, `resume_domain`, `stop_domain`, `reset_domain`

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Số điều kiện cần kiểm | 6 | start, cancel, pause, resume, stop, reset |
| Nội dung phải có | Nêu field compute không lưu và điều kiện qua quan hệ có thể không tự đánh giá; dùng 'Re-check Conditions' (hoặc đánh giá lại thủ công qua engine) để bù |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Mở Cấu hình SLA > Định nghĩa > Tạo mới, chọn model `res.partner` | Form hiển thị 6 field điều kiện |
| 2 | Di chuột lên dấu '?' (hoặc đọc thuộc tính `help` của field qua `fields_get`) của từng điều kiện trong 6 điều kiện | Mỗi help có ít nhất 1 câu nêu giới hạn nói trên |
| 3 | Ghi biên bản: tên field, trích câu giới hạn, Đạt/Không đạt | 6/6 dòng Đạt |

**Pass/Fail Criteria:** ✅ Pass: 6/6 điều kiện có câu nêu giới hạn; ❌ Fail: thiếu help hoặc help không nêu giới hạn ở ≥ 1 điều kiện

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CMP-010: Gắn task khi đánh giá lại một record sau khi country của partner đổi sang VN

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-13-03 |
| Coverage Item | CI-1 (AC1: partner đổi country sang VN rồi đánh giá lại (một record)) |
| Requirement Ref | REQ-FUNC-032 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` theo từng bước (đường hook dùng `fields.Datetime.now()`, TA-01).
3. FX-CMP (model kiểm thử `x.sla.cmp.ticket`, khai báo trong module test): `name` Char; `stage` Selection (`new`, `work`, `resolved`); `is_resolved` Boolean compute `store=True` phụ thuộc `stage` (true khi `stage` = 'resolved'); `weight` Integer; `lvl` Integer compute `store=True` phụ thuộc `weight` (= weight // 10); `is_big` Boolean compute KHÔNG lưu phụ thuộc `weight` (true khi weight ≥ 100); `partner_id` Many2one `res.partner`; `parent_id` Many2one cùng model, `child_ids` One2many; `children_done` Boolean compute `store=True` phụ thuộc `child_ids.stage` (true khi có con và mọi con `resolved`). (ghi chú fixture: dựng model kiểm thử vì `res.partner` không có field compute có lưu phù hợp)
4. Định nghĩa DEF-REL trên `x.sla.cmp.ticket`: mục tiêu 4 giờ, 24x7, start `[('partner_id.country_id', '=', VN)]` (VN = `base.vn`).
5. Partner PX (country = Pháp), ticket K (`partner_id` = PX), chưa có task; sau đó ghi PX {country_id: VN}

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| now | 10:00 |  |
| Người dùng | U-MGR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | U-MGR: Gọi `sla.engine.evaluate(K, now=None, changed=set())` với patch `odoo.fields.Datetime.now` trả 10:00 (lõi của hành động đánh giá lại thủ công: `action_reevaluate` gom record gốc rồi gọi hàm này) | Không ném lỗi; 0 event `error` của K |
| 2 | Đọc task và event của K | 1 task `in_progress`; `start_time` = 10:00; 1 event `attach` |

**Pass/Fail Criteria:** ✅ Pass: đúng 1 task `in_progress`; ❌ Fail: không có task

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CMP-011: Đánh giá lại một lô 2 record và chỉ gắn task cho record có điều kiện start khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-13-03 |
| Coverage Item | CI-2 (Lô 2 record, chỉ 1 record khớp) |
| Requirement Ref | REQ-FUNC-032 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` theo từng bước (đường hook dùng `fields.Datetime.now()`, TA-01).
3. FX-CMP (model kiểm thử `x.sla.cmp.ticket`, khai báo trong module test): `name` Char; `stage` Selection (`new`, `work`, `resolved`); `is_resolved` Boolean compute `store=True` phụ thuộc `stage` (true khi `stage` = 'resolved'); `weight` Integer; `lvl` Integer compute `store=True` phụ thuộc `weight` (= weight // 10); `is_big` Boolean compute KHÔNG lưu phụ thuộc `weight` (true khi weight ≥ 100); `partner_id` Many2one `res.partner`; `parent_id` Many2one cùng model, `child_ids` One2many; `children_done` Boolean compute `store=True` phụ thuộc `child_ids.stage` (true khi có con và mọi con `resolved`). (ghi chú fixture: dựng model kiểm thử vì `res.partner` không có field compute có lưu phù hợp)
4. Định nghĩa DEF-REL trên `x.sla.cmp.ticket`: mục tiêu 4 giờ, 24x7, start `[('partner_id.country_id', '=', VN)]` (VN = `base.vn`).
5. Ticket K1 (partner country = VN) và K2 (partner country = Pháp), chưa có task

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Lô | K1, K2 |  |
| now | 10:00 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với patch `odoo.fields.Datetime.now` trả 10:00, U-MGR gọi `sla.engine.evaluate(K1 \| K2, now=None, changed=set())` (lõi của đánh giá lại hàng loạt) | Không ném lỗi; 0 event `error` của K1 và K2 |
| 2 | Đếm task của K1 và K2 | K1: 1 task `in_progress`; K2: 0 task |
| 3 | Đếm event | K1: 1 `attach`; K2: 0 event |

**Pass/Fail Criteria:** ✅ Pass: chỉ K1 có task; ❌ Fail: K2 có task hoặc K1 không có

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CMP-012: Không đổi task và event ở lần đánh giá lại thứ hai liền sau

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-13-03 |
| Coverage Item | CI-3 (AC2: đánh giá lại hai lần liên tiếp) |
| Requirement Ref | REQ-FUNC-032 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` theo từng bước (đường hook dùng `fields.Datetime.now()`, TA-01).
3. FX-CMP (model kiểm thử `x.sla.cmp.ticket`, khai báo trong module test): `name` Char; `stage` Selection (`new`, `work`, `resolved`); `is_resolved` Boolean compute `store=True` phụ thuộc `stage` (true khi `stage` = 'resolved'); `weight` Integer; `lvl` Integer compute `store=True` phụ thuộc `weight` (= weight // 10); `is_big` Boolean compute KHÔNG lưu phụ thuộc `weight` (true khi weight ≥ 100); `partner_id` Many2one `res.partner`; `parent_id` Many2one cùng model, `child_ids` One2many; `children_done` Boolean compute `store=True` phụ thuộc `child_ids.stage` (true khi có con và mọi con `resolved`). (ghi chú fixture: dựng model kiểm thử vì `res.partner` không có field compute có lưu phù hợp)
4. Định nghĩa DEF-REL trên `x.sla.cmp.ticket`: mục tiêu 4 giờ, 24x7, start `[('partner_id.country_id', '=', VN)]` (VN = `base.vn`).
5. Ticket K (partner country = VN), chưa có task

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| now | 10:00 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Đặt đồng hồ 10:00; U-MGR đánh giá lại K lần 1 | 1 task `in_progress`; 1 event `attach` |
| 2 | Chụp (id, stage, start_time, planned_end_time, business_duration) của task và số event |  |
| 3 | U-MGR đánh giá lại K lần 2 (now = 10:00) | Không lỗi |
| 4 | So sánh với ảnh chụp | Giống hệt; số task = 1; số event = 1 |

**Pass/Fail Criteria:** ✅ Pass: không có thay đổi nào ở lần hai; ❌ Fail: task mới, giá trị đổi, hoặc event mới

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CMP-013: Từ chối đánh giá lại thủ công đối với người dùng group_sla_user

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-13-03 |
| Coverage Item | CI-4 (AC3: người dùng group_sla_user) |
| Requirement Ref | REQ-FUNC-032 AC3 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` theo từng bước (đường hook dùng `fields.Datetime.now()`, TA-01).
3. FX-CMP (model kiểm thử `x.sla.cmp.ticket`, khai báo trong module test): `name` Char; `stage` Selection (`new`, `work`, `resolved`); `is_resolved` Boolean compute `store=True` phụ thuộc `stage` (true khi `stage` = 'resolved'); `weight` Integer; `lvl` Integer compute `store=True` phụ thuộc `weight` (= weight // 10); `is_big` Boolean compute KHÔNG lưu phụ thuộc `weight` (true khi weight ≥ 100); `partner_id` Many2one `res.partner`; `parent_id` Many2one cùng model, `child_ids` One2many; `children_done` Boolean compute `store=True` phụ thuộc `child_ids.stage` (true khi có con và mọi con `resolved`). (ghi chú fixture: dựng model kiểm thử vì `res.partner` không có field compute có lưu phù hợp)
4. Định nghĩa DEF-REL trên `x.sla.cmp.ticket`: mục tiêu 4 giờ, 24x7, start `[('partner_id.country_id', '=', VN)]` (VN = `base.vn`).
5. Ticket K (partner country = VN), chưa có task; U-USR thuộc `group_sla_user`
6. Event `error` E1 của K tạo bằng sudo (`res_model` = 'x.sla.cmp.ticket', `res_id` = K.id, `note` = 'boom') để có đối tượng cho hành động đánh giá lại.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-USR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | U-USR gọi `E1.with_user(U-USR).action_reevaluate_batch()` (đường đánh giá lại cho record chưa có task) | Ném `AccessError` chứa "SLA Manager" (ACC_002) |
| 2 | Đếm task và event của K | 0 task; đúng 1 event (E1, không có event mới) |

**Pass/Fail Criteria:** ✅ Pass: hành động bị từ chối và không có dữ liệu mới; ❌ Fail: U-USR đánh giá lại được

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CMP-014: Không reset task khi đánh giá lại thủ công dù field theo dõi đã khác giá trị trước

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-13-03 |
| Coverage Item | CI-5 (Statement: không kích hoạt reset theo field) |
| Requirement Ref | REQ-FUNC-032 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` theo từng bước (đường hook dùng `fields.Datetime.now()`, TA-01).
3. FX-CMP (model kiểm thử `x.sla.cmp.ticket`, khai báo trong module test): `name` Char; `stage` Selection (`new`, `work`, `resolved`); `is_resolved` Boolean compute `store=True` phụ thuộc `stage` (true khi `stage` = 'resolved'); `weight` Integer; `lvl` Integer compute `store=True` phụ thuộc `weight` (= weight // 10); `is_big` Boolean compute KHÔNG lưu phụ thuộc `weight` (true khi weight ≥ 100); `partner_id` Many2one `res.partner`; `parent_id` Many2one cùng model, `child_ids` One2many; `children_done` Boolean compute `store=True` phụ thuộc `child_ids.stage` (true khi có con và mọi con `resolved`). (ghi chú fixture: dựng model kiểm thử vì `res.partner` không có field compute có lưu phù hợp)
4. Định nghĩa DEF-RST trên `x.sla.cmp.ticket`: mục tiêu 4 giờ, 24x7, start `[('stage', 'in', ['new', 'work'])]`, `reset_domain` = `[('id', '!=', 0)]` (khớp mọi record), `reset_field_ids` = {`weight`}, `reset_action` = `cancel`
5. Ticket K (`weight` = 10, `stage` = 'new') tạo lúc FX-T0 → task T1 `in_progress`
6. Đổi `weight` thành 99 bằng SQL trực tiếp (bỏ qua hook) để hệ thống không thấy thay đổi

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Field theo dõi | weight 10 → 99 | không qua hook |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Đặt đồng hồ 10:00; U-MGR đánh giá lại K | Không lỗi |
| 2 | Đọc task của K | Vẫn đúng task T1 (cùng id), `stage` = `in_progress`; số task = 1 |
| 3 | Đếm event `reset` và `cancel` | = 0 |

**Pass/Fail Criteria:** ✅ Pass: không có event `reset`, T1 giữ nguyên; ❌ Fail: xuất hiện `reset` hoặc task mới

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CMP-015: Dùng thời điểm hiện tại làm mốc bắt đầu khi đánh giá lại thủ công

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-13-03 |
| Coverage Item | CI-6 (Statement: dùng thời điểm hiện tại, không retroactive) |
| Requirement Ref | REQ-FUNC-032 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` theo từng bước (đường hook dùng `fields.Datetime.now()`, TA-01).
3. FX-CMP (model kiểm thử `x.sla.cmp.ticket`, khai báo trong module test): `name` Char; `stage` Selection (`new`, `work`, `resolved`); `is_resolved` Boolean compute `store=True` phụ thuộc `stage` (true khi `stage` = 'resolved'); `weight` Integer; `lvl` Integer compute `store=True` phụ thuộc `weight` (= weight // 10); `is_big` Boolean compute KHÔNG lưu phụ thuộc `weight` (true khi weight ≥ 100); `partner_id` Many2one `res.partner`; `parent_id` Many2one cùng model, `child_ids` One2many; `children_done` Boolean compute `store=True` phụ thuộc `child_ids.stage` (true khi có con và mọi con `resolved`). (ghi chú fixture: dựng model kiểm thử vì `res.partner` không có field compute có lưu phù hợp)
4. Định nghĩa DEF-REL trên `x.sla.cmp.ticket`: mục tiêu 4 giờ, 24x7, start `[('partner_id.country_id', '=', VN)]` (VN = `base.vn`).
5. `retroactive_start` = false
6. Ticket K (partner country = VN) tạo lúc 09:00 nhưng chưa có task (start khớp chỉ sau khi dữ liệu partner đổi lúc 09:00)

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Thời điểm dữ liệu đổi | 09:00 |  |
| now đánh giá lại | 14:00 | FX-T0 + 5h |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | U-MGR: Gọi `sla.engine.evaluate(K, now=None, changed=set())` với patch `odoo.fields.Datetime.now` trả 14:00 (lõi của hành động đánh giá lại thủ công: `action_reevaluate` gom record gốc rồi gọi hàm này) | Không ném lỗi; 0 event `error` của K |
| 2 | Đọc task của K | `start_time` = 14:00 (không phải 09:00); `planned_end_time` = 18:00 |

**Pass/Fail Criteria:** ✅ Pass: `start_time` = 14:00 và `planned_end_time` = 18:00; ❌ Fail: `start_time` = 09:00

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CMP-016: Áp dụng ưu tiên stop trước cancel khi đánh giá lại record khớp cả hai điều kiện

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-13-03 |
| Coverage Item | CI-7 (Statement: áp dụng cùng quy tắc ưu tiên (stop thắng cancel)) |
| Requirement Ref | REQ-FUNC-032 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database `sla_test` đã cài `dwo_sla_core`; ca chạy với user U-MGR (FX-USERS) trừ khi ghi khác; giờ ghi theo Asia/Ho_Chi_Minh (UTC+7), FX-T0 = 2026-03-02 09:00.
2. Đồng hồ cố định: patch `odoo.fields.Datetime.now` theo từng bước (đường hook dùng `fields.Datetime.now()`, TA-01).
3. FX-CMP (model kiểm thử `x.sla.cmp.ticket`, khai báo trong module test): `name` Char; `stage` Selection (`new`, `work`, `resolved`); `is_resolved` Boolean compute `store=True` phụ thuộc `stage` (true khi `stage` = 'resolved'); `weight` Integer; `lvl` Integer compute `store=True` phụ thuộc `weight` (= weight // 10); `is_big` Boolean compute KHÔNG lưu phụ thuộc `weight` (true khi weight ≥ 100); `partner_id` Many2one `res.partner`; `parent_id` Many2one cùng model, `child_ids` One2many; `children_done` Boolean compute `store=True` phụ thuộc `child_ids.stage` (true khi có con và mọi con `resolved`). (ghi chú fixture: dựng model kiểm thử vì `res.partner` không có field compute có lưu phù hợp)
4. Định nghĩa DEF-PRI trên `x.sla.cmp.ticket`: mục tiêu 4 giờ, 24x7, start `[('stage', 'in', ['new', 'work'])]`, stop `[('weight', '>=', 50)]`, cancel `[('weight', '>=', 50)]`, `cancel_mode` = `condition`
5. Ticket K (`stage` = 'new', `weight` = 10) tạo lúc FX-T0 → task `in_progress`; sau đó đổi `weight` = 60 bằng SQL (bỏ qua hook): K khớp cả stop và cancel

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Điều kiện | stop và cancel cùng khớp | ưu tiên REQ-FUNC-008: stop > cancel |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với patch `odoo.fields.Datetime.now` trả 10:00, U-MGR gọi `action_reevaluate()` trên task của K | Không ném lỗi; 0 event `error` của K |
| 2 | Đọc task của K và event | Task `stage` = `achieved`, `end_time` = 10:00; 1 event `complete`; 0 event `cancel` |

**Pass/Fail Criteria:** ✅ Pass: task `achieved` với 1 event `complete`, không `cancel`; ❌ Fail: task `cancelled` hoặc có cả hai event

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

## TG-14 — Hạ tầng: cài, nâng cấp, gỡ, dọn dẹp, tham số

### TC-INF-001: Từ chối lưu định nghĩa trỏ tới model tiền tố `ir.` (`ir.attachment`)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-01 |
| Coverage Item | CI-1 (model tiền tố `ir.` (`ir.attachment`)) |
| Requirement Ref | REQ-FUNC-002 AC1 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Chưa có định nghĩa nào trên model `ir.attachment`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| model | ir.attachment |  |
| duration | 4 |  |
| start | `[]` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` với model = `ir.attachment`, lưu. | Bị từ chối (ValidationError). |
| 2 | Đọc thông báo lỗi. | Thông báo nêu lý do (loại model hoặc tiền tố bị cấm). |
| 3 | Đếm `sla.definition` của model này. | = 0. |

**Pass/Fail Criteria:** ✅ Pass: Từ chối, có thông báo lý do, không có bản ghi. ❌ Fail: Lưu thành công hoặc thông báo không nêu lý do.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-002: Từ chối lưu định nghĩa trỏ tới model tiền tố `sla.` (`sla.task`)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-01 |
| Coverage Item | CI-2 (model tiền tố `sla.` (`sla.task`)) |
| Requirement Ref | REQ-FUNC-002 AC2 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Chưa có định nghĩa nào trên model `sla.task`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| model | sla.task |  |
| duration | 4 |  |
| start | `[]` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` với model = `sla.task`, lưu. | Bị từ chối (ValidationError). |
| 2 | Đọc thông báo lỗi. | Thông báo nêu lý do (loại model hoặc tiền tố bị cấm). |
| 3 | Đếm `sla.definition` của model này. | = 0. |

**Pass/Fail Criteria:** ✅ Pass: Từ chối, có thông báo lý do, không có bản ghi. ❌ Fail: Lưu thành công hoặc thông báo không nêu lý do.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-003: Từ chối lưu định nghĩa trỏ tới model transient (`base.language.install`)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-01 |
| Coverage Item | CI-3 (model transient (`base.language.install`)) |
| Requirement Ref | REQ-FUNC-002 Statement |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Chưa có định nghĩa nào trên model `base.language.install`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| model | base.language.install |  |
| duration | 4 |  |
| start | `[]` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` với model = `base.language.install`, lưu. | Bị từ chối (ValidationError). |
| 2 | Đọc thông báo lỗi. | Thông báo nêu lý do (loại model hoặc tiền tố bị cấm). |
| 3 | Đếm `sla.definition` của model này. | = 0. |

**Pass/Fail Criteria:** ✅ Pass: Từ chối, có thông báo lý do, không có bản ghi. ❌ Fail: Lưu thành công hoặc thông báo không nêu lý do.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-004: Từ chối lưu định nghĩa trỏ tới model abstract (`image.mixin`)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-01 |
| Coverage Item | CI-4 (model abstract (`image.mixin`)) |
| Requirement Ref | REQ-FUNC-002 Statement |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Chưa có định nghĩa nào trên model `image.mixin`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| model | image.mixin |  |
| duration | 4 |  |
| start | `[]` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` với model = `image.mixin`, lưu. | Bị từ chối (ValidationError). |
| 2 | Đọc thông báo lỗi. | Thông báo nêu lý do (loại model hoặc tiền tố bị cấm). |
| 3 | Đếm `sla.definition` của model này. | = 0. |

**Pass/Fail Criteria:** ✅ Pass: Từ chối, có thông báo lý do, không có bản ghi. ❌ Fail: Lưu thành công hoặc thông báo không nêu lý do.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-005: Từ chối lưu định nghĩa trỏ tới model `_auto = False` (model chỉ dành cho test `x_test.sqlview` khai báo `_auto = False`)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-01 |
| Coverage Item | CI-5 (model `_auto = False` (model chỉ dành cho test `x_test.sqlview` khai báo `_auto = False`)) |
| Requirement Ref | REQ-FUNC-002 Statement |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Đăng ký model test `x_test.sqlview` với `_auto = False` trong registry test.
2. Chưa có định nghĩa nào trên model `x_test.sqlview`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| model | x_test.sqlview |  |
| duration | 4 |  |
| start | `[]` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` với model = `x_test.sqlview`, lưu. | Bị từ chối (ValidationError). |
| 2 | Đọc thông báo lỗi. | Thông báo nêu lý do (loại model hoặc tiền tố bị cấm). |
| 3 | Đếm `sla.definition` của model này. | = 0. |

**Pass/Fail Criteria:** ✅ Pass: Từ chối, có thông báo lý do, không có bản ghi. ❌ Fail: Lưu thành công hoặc thông báo không nêu lý do.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-006: Từ chối lưu định nghĩa trỏ tới model tiền tố `mail.` (`mail.message`)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-01 |
| Coverage Item | CI-6 (model tiền tố `mail.` (`mail.message`)) |
| Requirement Ref | REQ-FUNC-002 Statement |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Chưa có định nghĩa nào trên model `mail.message`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| model | mail.message |  |
| duration | 4 |  |
| start | `[]` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` với model = `mail.message`, lưu. | Bị từ chối (ValidationError). |
| 2 | Đọc thông báo lỗi. | Thông báo nêu lý do (loại model hoặc tiền tố bị cấm). |
| 3 | Đếm `sla.definition` của model này. | = 0. |

**Pass/Fail Criteria:** ✅ Pass: Từ chối, có thông báo lý do, không có bản ghi. ❌ Fail: Lưu thành công hoặc thông báo không nêu lý do.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-007: Chấp nhận lưu định nghĩa trỏ tới `res.partner`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-02 |
| Coverage Item | CI-1 (`res.partner`) |
| Requirement Ref | REQ-FUNC-002 AC3 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Chưa có định nghĩa nào trên `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| model | `res.partner` |  |
| duration | 4 |  |
| start | `[('ref','=','NEW')]` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` model `res.partner`, lưu. | Không ném lỗi; bản ghi được tạo (id > 0) với `model_name` = 'res.partner'. |
| 2 | Đếm `sla.definition` của `res.partner`. | = 1. |

**Pass/Fail Criteria:** ✅ Pass: Lưu thành công. ❌ Fail: Bị từ chối.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-008: Chấp nhận lưu định nghĩa trỏ tới model `demo.ticket`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-02 |
| Coverage Item | CI-2 (`demo.ticket` (model ngoài base)) |
| Requirement Ref | REQ-FUNC-002 AC3 (mở rộng) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEMO đã cài (model `demo.ticket`).
2. Chưa có định nghĩa mới nào trên `demo.ticket` ngoài 4 định nghĩa mẫu.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| model | `demo.ticket` |  |
| duration | 4 |  |
| start | `[('priority','=','p1')]` | `demo.ticket` có field `priority` (phụ thuộc module demo, TA-15) |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` {name: 'D-DEMO', model_id: `demo.ticket`, duration: 4, start_domain: `[('priority','=','p1')]`, schedule_source: 'none', cancel_mode: 'start_unmatched', resume_mode: 'condition'; stop, pause, resume, cancel, reset để rỗng}, lưu. | Không ném lỗi; bản ghi được tạo (id > 0) với `model_name` = 'demo.ticket' và `active` = True. |

**Pass/Fail Criteria:** ✅ Pass: bản ghi được tạo với `model_name` = 'demo.ticket'. ❌ Fail: bị từ chối.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-009: Bỏ qua model `ir.attachment` khi quan sát tạo record dù có định nghĩa lọt qua

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-03 |
| Coverage Item | CI-1 (Định nghĩa trỏ `ir.attachment` lọt qua bằng SQL) |
| Requirement Ref | REQ-FUNC-002 Statement (vế bỏ qua) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Chèn bằng SQL một `sla_definition` (model `ir.attachment`, start `[]`, 4 giờ, active) để vượt qua kiểm tra khi lưu. (đường tắt SQL là chủ ý của ca vì ORM từ chối model `ir.*`, REQ-FUNC-002.)
2. Đếm trước: `sla.task` = 0, `sla.event` = 0.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| attachment | name = `a.txt`, res_model = `res.partner` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo một `ir.attachment` (qua ORM). | Tạo thành công, không lỗi. |
| 2 | Đếm `sla.task` và `sla.event`. | Cả hai vẫn = 0 (hook bỏ qua model `ir.`). |

**Pass/Fail Criteria:** ✅ Pass: Không có task và event. ❌ Fail: Có task hoặc event, hoặc lỗi khi tạo attachment.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-010: Dọn 2 task, 1 lượt thử lại và event của record đã bị xóa sau khi chạy job dọn

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-04 |
| Coverage Item | CI-1 (Record bị xóa, có 2 task và 1 lượt thử lại) |
| Requirement Ref | REQ-FUNC-034 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD (D1) và định nghĩa D2 cùng trên `res.partner` (D2: như D1, đặt tên khác); FX-ESC-STD trên D1.
2. Partner P `ref` = `NEW` có 2 task `in_progress` (D1, D2) tạo bằng Engine với now = T0.
3. Tạo 1 dòng `sla.escalation.retry` {task_id: task D1, escalation_id: mốc của FX-ESC-STD trên D1, attempt: 1, retry_at: T0 + 10 phút} (bảng `sla_escalation_retry` theo 030).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| P.id | id của P | Ghi lại trước khi xóa |
| now | T0 + 1 ngày |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Xóa P bằng `unlink`. | Thành công; task vẫn còn (dọn không đồng bộ). |
| 2 | Gọi `sla.task._gc_orphan_tasks()` (job autovacuum hằng ngày, TAD AD-09; hàm không nhận `now`). | Không ném lỗi. |
| 3 | Đếm `sla.task` có `res_model`=`res.partner`, `res_id`=P.id; đếm `sla.escalation.retry` liên quan; đếm `sla.event` có `res_id` = P.id. | Cả ba = 0. |

**Pass/Fail Criteria:** ✅ Pass: Task, lượt thử lại và event của P đều không còn. ❌ Fail: Còn bất kỳ bản ghi nào.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-011: Giữ nguyên task khi record gốc còn tồn tại sau khi chạy job dọn

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-04 |
| Coverage Item | CI-2 (Record còn tồn tại) |
| Requirement Ref | REQ-FUNC-034 AC2 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD; partner P `ref` = `NEW` có 1 task `in_progress` (start T0).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| now | T0 + 1 ngày |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi job dọn task mồ côi với now = T0 + 1 ngày. | Không lỗi. |
| 2 | Đọc task của P. | Còn đúng 1 task, `stage` = `in_progress`, các event `attach` vẫn còn (1). |

**Pass/Fail Criteria:** ✅ Pass: Task và event giữ nguyên. ❌ Fail: Task bị xóa.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-012: Chỉ dọn task của record đã xóa khi lô có cả record còn tồn tại

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-04 |
| Coverage Item | CI-3 (Lô hỗn hợp (1 record xóa, 1 record còn)) |
| Requirement Ref | REQ-FUNC-034 AC1/AC2 (kết hợp) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD; partner P1 và P2 `ref` = `NEW`, mỗi record có 1 task `in_progress`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| now | T0 + 1 ngày |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Xóa P1 bằng `unlink`; gọi job dọn với now = T0 + 1 ngày. | Không lỗi. |
| 2 | Đếm task theo record. | Task của P1 = 0; task của P2 = 1 (`in_progress`). |

**Pass/Fail Criteria:** ✅ Pass: Chỉ task của P1 bị dọn. ❌ Fail: Task của P2 bị xóa hoặc task của P1 còn.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-013: Xóa event cũ hơn ngưỡng 90 ngày và giữ event mới hơn

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-05 |
| Coverage Item | CI-1 (Event 100 ngày (A) và 10 ngày (B), ngưỡng 90) |
| Requirement Ref | REQ-FUNC-035 AC1 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Tham số `dwo_sla_core.event_retention_days` = 90.
2. Hai event A (`event_dt` = now - 100 ngày) và B (`event_dt` = now - 10 ngày); test đặt thêm `create_date` bằng cùng giá trị (code dọn theo `event_dt`; sai lệch đã ghi ở TASKS T13), với now = T0 + 200 ngày.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ngưỡng | 90 ngày |  |
| tuổi A / B | 100 ngày / 10 ngày |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi job dọn nhật ký với now = T0 + 200 ngày. | Không lỗi. |
| 2 | Đọc A và B. | A không còn; B còn. |

**Pass/Fail Criteria:** ✅ Pass: A bị xóa, B còn. ❌ Fail: A còn hoặc B bị xóa.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-014: Giữ event có tuổi đúng bằng ngưỡng 90 ngày

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-05 |
| Coverage Item | CI-2 (Event đúng 90 ngày (biên)) |
| Requirement Ref | REQ-FUNC-035 AC2 |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Tham số `dwo_sla_core.event_retention_days` = 90.
2. Event E được chèn với `event_dt` = now - 90 ngày 00:00:00 (đồng thời đặt `create_date` bằng cùng giá trị; code dọn theo `event_dt`, TASKS T13) (now = T0 + 200 ngày = 2026-09-18 09:00 UTC+7), thuộc task bất kỳ hoặc không có task.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ngưỡng | 90 ngày |  |
| tuổi E | 90 ngày 00:00:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi job dọn nhật ký với now = T0 + 200 ngày. | Không lỗi. |
| 2 | Đọc E theo id. | Event còn tồn tại. |

**Pass/Fail Criteria:** ✅ Pass: Event còn (không bị xóa). ❌ Fail: Kết quả ngược lại.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-015: Xóa event có tuổi vượt ngưỡng 90 ngày 1 phút

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-05 |
| Coverage Item | CI-3 (Event 90 ngày + 1 phút (ngay trên biên)) |
| Requirement Ref | REQ-FUNC-035 AC1 (biên) |
| Priority | P3-Medium |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Tham số `dwo_sla_core.event_retention_days` = 90.
2. Event E được chèn với `event_dt` = now - 90 ngày 00:01:00 (đồng thời đặt `create_date` bằng cùng giá trị; code dọn theo `event_dt`, TASKS T13) (now = T0 + 200 ngày = 2026-09-18 09:00 UTC+7), thuộc task bất kỳ hoặc không có task.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ngưỡng | 90 ngày |  |
| tuổi E | 90 ngày 00:01:00 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi job dọn nhật ký với now = T0 + 200 ngày. | Không lỗi. |
| 2 | Đọc E theo id. | Event không còn. |

**Pass/Fail Criteria:** ✅ Pass: Event bị xóa. ❌ Fail: Kết quả ngược lại.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-016: Áp dụng ngưỡng đã chỉnh 30 ngày khi dọn event 40 ngày

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-05 |
| Coverage Item | CI-4 (Ngưỡng đổi thành 30, event 40 ngày) |
| Requirement Ref | REQ-FUNC-035 INT-010 (liên kết) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Tham số `dwo_sla_core.event_retention_days` = 30.
2. Event E được chèn với `event_dt` = now - 40 ngày (đồng thời đặt `create_date` bằng cùng giá trị; code dọn theo `event_dt`, TASKS T13) (now = T0 + 200 ngày = 2026-09-18 09:00 UTC+7), thuộc task bất kỳ hoặc không có task.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ngưỡng | 30 ngày |  |
| tuổi E | 40 ngày |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi job dọn nhật ký với now = T0 + 200 ngày. | Không lỗi. |
| 2 | Đọc E theo id. | Event không còn. |

**Pass/Fail Criteria:** ✅ Pass: Event bị xóa theo ngưỡng mới. ❌ Fail: Kết quả ngược lại.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-017: Tham số số ngày lưu nhật ký có giá trị mặc định 365 sau khi cài mới

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-06 |
| Coverage Item | CI-1 (Hệ thống mới cài) |
| Requirement Ref | REQ-INT-010 AC1 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Database trống `sla_test`, cài `dwo_sla_core` (chưa chỉnh cấu hình).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| key | dwo_sla_core.event_retention_days |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đọc `ir.config_parameter` theo key. | Bản ghi tồn tại. |
| 2 | Đọc giá trị. | = `365`. |

**Pass/Fail Criteria:** ✅ Pass: Tham số tồn tại và = 365. ❌ Fail: Không tồn tại hoặc khác 365.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-018: Từ chối lưu số ngày lưu nhật ký = 0

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-06 |
| Coverage Item | CI-2 (Giá trị 0 (biên không hợp lệ)) |
| Requirement Ref | REQ-INT-010 AC2 |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. U-MGR (FX-USERS) thuộc `group_sla_manager`.
2. Tham số hiện = 365.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| user | U-MGR |  |
| giá trị nhập | 0 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Với quyền U-MGR, mở `res.config.settings`, đặt số ngày lưu nhật ký = 0, thực thi lưu. | Bị từ chối bằng `ValidationError` chứa "greater than 0" (VAL_001). |
| 2 | Đọc `ir.config_parameter` theo key. | Vẫn = `365`. |

**Pass/Fail Criteria:** ✅ Pass: Giá trị bị từ chối và tham số giữ nguyên = 365. ❌ Fail: Kết quả ngược lại.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-019: Từ chối lưu số ngày lưu nhật ký âm (-1)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-06 |
| Coverage Item | CI-3 (Giá trị -1 (âm)) |
| Requirement Ref | REQ-INT-010 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. U-MGR (FX-USERS) thuộc `group_sla_manager`.
2. Tham số hiện = 365.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| user | U-MGR |  |
| giá trị nhập | -1 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Với quyền U-MGR, mở `res.config.settings`, đặt số ngày lưu nhật ký = -1, thực thi lưu. | Bị từ chối bằng `ValidationError` chứa "greater than 0" (VAL_001). |
| 2 | Đọc `ir.config_parameter` theo key. | Vẫn = `365`. |

**Pass/Fail Criteria:** ✅ Pass: Giá trị bị từ chối và tham số giữ nguyên = 365. ❌ Fail: Kết quả ngược lại.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-020: Chấp nhận số ngày lưu nhật ký = 1

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-06 |
| Coverage Item | CI-4 (Giá trị 1 (biên hợp lệ thấp nhất)) |
| Requirement Ref | REQ-INT-010 AC2 (biên) |
| Priority | P3-Medium |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. U-MGR (FX-USERS) thuộc `group_sla_manager`.
2. Tham số hiện = 365.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| user | U-MGR |  |
| giá trị nhập | 1 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Với quyền U-MGR, mở `res.config.settings`, đặt số ngày lưu nhật ký = 1, thực thi lưu. | Lưu thành công. |
| 2 | Đọc `ir.config_parameter` theo key. | = `1`. |

**Pass/Fail Criteria:** ✅ Pass: Giá trị được lưu. ❌ Fail: Kết quả ngược lại.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-021: SLA Manager chỉnh số ngày lưu nhật ký thành 180 tại Settings

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-06 |
| Coverage Item | CI-5 (SLA Manager chỉnh 180) |
| Requirement Ref | REQ-INT-010 Statement |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. U-MGR (FX-USERS) thuộc `group_sla_manager`.
2. Tham số hiện = 365.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| user | U-MGR |  |
| giá trị nhập | 180 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Với quyền U-MGR, mở `res.config.settings`, đặt số ngày lưu nhật ký = 180, thực thi lưu. | Lưu thành công. |
| 2 | Đọc `ir.config_parameter` theo key. | = `180`. |

**Pass/Fail Criteria:** ✅ Pass: Giá trị được lưu. ❌ Fail: Kết quả ngược lại.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-022: Từ chối khi SLA User thay đổi số ngày lưu nhật ký

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-06 |
| Coverage Item | CI-6 (SLA User (không phải Manager)) |
| Requirement Ref | REQ-INT-010 Statement |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. U-USR (FX-USERS) chỉ thuộc `group_sla_user`.
2. Tham số `dwo_sla_core.event_retention_days` = 365 (theo REQ-SEC-001 chỉ `group_sla_manager` chỉnh tham số).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| user | U-USR |  |
| giá trị nhập | 180 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Với quyền U-USR, thực thi lưu `res.config.settings` đặt 180. | Bị từ chối (AccessError). |
| 2 | Đọc tham số. | Vẫn = `365`. |

**Pass/Fail Criteria:** ✅ Pass: Bị từ chối, tham số giữ nguyên. ❌ Fail: Tham số bị đổi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-023: Cài `dwo_sla_core` trên database có dữ liệu không lỗi và không làm đổi dữ liệu

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-07 |
| Coverage Item | CI-1 (Cài mới) |
| Requirement Ref | REQ-INST-001 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (lệnh cài/gỡ trong CI) |

**Preconditions:**
1. Database `sla_inst` có sẵn `base`, `sh_all_in_one_helpdesk`, 1000 `res.partner`, 200 `sh.helpdesk.ticket`; ghi checksum bảng `res_partner` và `sh_helpdesk_ticket` (CK0).
2. Module `dwo_sla_core` chưa cài.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| DB | `sla_inst` (bản sao có dữ liệu) |  |
| Dữ liệu mẫu | 1000 `res.partner`, 200 `sh.helpdesk.ticket` | Checksum = md5 của `id,name,write_date` sắp theo id |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Chạy `odoo -d sla_inst -i dwo_sla_core --stop-after-init`. | Mã thoát 0; log không có `ERROR`/`CRITICAL`. |
| 2 | Tính checksum `res_partner`, `sh_helpdesk_ticket` (CK1); thử tạo và sửa 1 partner. | CK1 = CK0 (không có dòng bị đổi do cài); thao tác tạo/sửa partner thành công. |

**Pass/Fail Criteria:** ✅ Pass: Cài thành công, dữ liệu nguyên vẹn. ❌ Fail: Lỗi khi cài hoặc checksum đổi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-024: Nâng cấp `dwo_sla_core` đã cài không lỗi và không làm đổi dữ liệu

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-07 |
| Coverage Item | CI-2 (Nâng cấp) |
| Requirement Ref | REQ-INST-001 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (lệnh cài/gỡ trong CI) |

**Preconditions:**
1. Database `sla_inst` có sẵn `base`, `sh_all_in_one_helpdesk`, 1000 `res.partner`, 200 `sh.helpdesk.ticket`; ghi checksum bảng `res_partner` và `sh_helpdesk_ticket` (CK0).
2. `dwo_sla_core` đã cài; có 5 task SLA mẫu (CK-SLA = số task và checksum `sla_task`).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| DB | `sla_inst` (bản sao có dữ liệu) |  |
| Dữ liệu mẫu | 1000 `res.partner`, 200 `sh.helpdesk.ticket` | Checksum = md5 của `id,name,write_date` sắp theo id |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Chạy `odoo -d sla_inst -u dwo_sla_core --stop-after-init`. | Mã thoát 0; log không có `ERROR`. |
| 2 | Tính checksum `res_partner`, `sh_helpdesk_ticket` và đếm/ checksum `sla_task`. | Bằng giá trị trước khi nâng cấp; 5 task còn nguyên. |

**Pass/Fail Criteria:** ✅ Pass: Nâng cấp thành công, dữ liệu nguyên vẹn. ❌ Fail: Lỗi hoặc dữ liệu đổi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-025: Gỡ `dwo_sla_core` không lỗi và dữ liệu `res.partner`, `sh.helpdesk.ticket` nguyên vẹn

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-07 |
| Coverage Item | CI-3 (Gỡ) |
| Requirement Ref | REQ-INST-001 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (lệnh cài/gỡ trong CI) |

**Preconditions:**
1. Database `sla_inst` có sẵn `base`, `sh_all_in_one_helpdesk`, 1000 `res.partner`, 200 `sh.helpdesk.ticket`; ghi checksum bảng `res_partner` và `sh_helpdesk_ticket` (CK0).
2. `dwo_sla_core` đã cài.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| DB | `sla_inst` (bản sao có dữ liệu) |  |
| Dữ liệu mẫu | 1000 `res.partner`, 200 `sh.helpdesk.ticket` | Checksum = md5 của `id,name,write_date` sắp theo id |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gỡ module bằng `button_immediate_uninstall` (hoặc `odoo shell`). | Không lỗi. |
| 2 | Kiểm tra bảng `sla_task`, `sla_event`, `sla_definition`. | Các bảng không còn; không còn cron, group của module. |
| 3 | Tính checksum `res_partner`, `sh_helpdesk_ticket`. | Bằng CK0. |

**Pass/Fail Criteria:** ✅ Pass: Gỡ sạch, dữ liệu gốc nguyên vẹn. ❌ Fail: Lỗi gỡ, bảng/cron còn sót hoặc dữ liệu gốc đổi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-026: Sau khi gỡ, sửa record không phát sinh event hay task

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-07 |
| Coverage Item | CI-4 (Sau gỡ) |
| Requirement Ref | REQ-INST-001 AC1 (phần sau gỡ) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (lệnh cài/gỡ trong CI) |

**Preconditions:**
1. Database `sla_inst` có sẵn `base`, `sh_all_in_one_helpdesk`, 1000 `res.partner`, 200 `sh.helpdesk.ticket`; ghi checksum bảng `res_partner` và `sh_helpdesk_ticket` (CK0).
2. Ca tự dựng trạng thái "sau gỡ": cài `dwo_sla_core` trên `sla_inst`, rồi gỡ bằng `button_immediate_uninstall` và xác nhận bảng `sla_task` không còn (không dựa vào kết quả của ca khác).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| DB | `sla_inst` (bản sao có dữ liệu) |  |
| Dữ liệu mẫu | 1000 `res.partner`, 200 `sh.helpdesk.ticket` | Checksum = md5 của `id,name,write_date` sắp theo id |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo mới 1 `res.partner` (ref = `NEW`) và sửa 1 `sh.helpdesk.ticket` có sẵn. | Cả hai thành công, không lỗi, không cảnh báo về bảng `sla_*`. |
| 2 | Kiểm tra sự tồn tại bảng `sla_task`, `sla_event` và log của server. | Bảng không tồn tại; log không có đề cập `sla.`/hook. |

**Pass/Fail Criteria:** ✅ Pass: Hành vi tạo/sửa như khi chưa cài. ❌ Fail: Có lỗi, hoặc có dấu vết SLA.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-027: Bảng `res_partner` không đổi cột sau khi cài module

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-08 |
| Coverage Item | CI-1 (Bảng `res_partner`) |
| Requirement Ref | REQ-INST-003 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (lệnh cài/gỡ trong CI) |

**Preconditions:**
1. Database `sla_inst` chưa cài `dwo_sla_core`.
2. Chụp danh sách cột bảng `res_partner` từ `information_schema.columns` (column_name, data_type, is_nullable, column_default) sắp theo tên: CL0.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| bảng | res_partner |  |
| model | res.partner |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Cài `dwo_sla_core`. | Cài thành công. |
| 2 | Chụp lại danh sách cột bảng `res_partner`: CL1. | CL1 giống hệt CL0 (số cột bằng nhau, từng thuộc tính bằng nhau). |
| 3 | Đọc `ir.model.fields` của model `res.partner` có `modules` chứa `dwo_sla_core`. | Không có dòng nào. |

**Pass/Fail Criteria:** ✅ Pass: CL1 = CL0 và không có field do module thêm. ❌ Fail: Có cột/field mới.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-028: Bảng `sh_helpdesk_ticket` không đổi cột sau khi cài module

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-08 |
| Coverage Item | CI-2 (Bảng `sh_helpdesk_ticket`) |
| Requirement Ref | REQ-INST-003 AC1 |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (lệnh cài/gỡ trong CI) |

**Preconditions:**
1. Database `sla_inst` chưa cài `dwo_sla_core`.
2. Chụp danh sách cột bảng `sh_helpdesk_ticket` từ `information_schema.columns` (column_name, data_type, is_nullable, column_default) sắp theo tên: CL0.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| bảng | sh_helpdesk_ticket |  |
| model | sh.helpdesk.ticket |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Cài `dwo_sla_core`. | Cài thành công. |
| 2 | Chụp lại danh sách cột bảng `sh_helpdesk_ticket`: CL1. | CL1 giống hệt CL0 (số cột bằng nhau, từng thuộc tính bằng nhau). |
| 3 | Đọc `ir.model.fields` của model `sh.helpdesk.ticket` có `modules` chứa `dwo_sla_core`. | Không có dòng nào. |

**Pass/Fail Criteria:** ✅ Pass: CL1 = CL0 và không có field do module thêm. ❌ Fail: Có cột/field mới.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-029: Tạo định nghĩa và task SLA không thêm cột vào bảng `res_partner`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-08 |
| Coverage Item | CI-3 (Mọi model có định nghĩa SLA (kể cả sau khi tạo định nghĩa)) |
| Requirement Ref | REQ-INST-003 C-03 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Chụp cột bảng `res_partner` (CL0).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| định nghĩa | FX-DEF-STD |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo FX-DEF-STD, tạo partner `ref` = `NEW`, đánh giá now = T0 (1 task `in_progress`). | 1 task. |
| 2 | Chụp lại cột bảng `res_partner` (CL1). | CL1 = CL0. |

**Pass/Fail Criteria:** ✅ Pass: Không có cột mới. ❌ Fail: Có cột mới.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-030: Gỡ `dwo_sla_demo_ticket` xóa hết task của `demo.ticket` và không lỗi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-09 |
| Coverage Item | CI-1 (Task `demo.ticket` khi gỡ demo) |
| Requirement Ref | REQ-INST-004 AC1 |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (lệnh cài/gỡ trong CI) |

**Preconditions:**
1. Cài `dwo_sla_demo_ticket` (FX-DEMO: 4 định nghĩa mẫu).
2. Tạo 3 `demo.ticket` priority `p1`, đánh giá now = T0 → mỗi ticket ≥ 1 task `in_progress` (đếm DT = số task của `demo.ticket`, DT >= 3).
3. Tạo `res.partner` P (ref=`NEW`) với FX-DEF-STD, 1 task (đếm PT = 1).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| module | `dwo_sla_demo_ticket` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gỡ module `dwo_sla_demo_ticket`. | Không lỗi, không bị chặn bởi quy tắc REQ-FUNC-061. |
| 2 | Đếm `sla.task` có `res_model` = `demo.ticket`. | = 0. |

**Pass/Fail Criteria:** ✅ Pass: Không lỗi và 0 task `demo.ticket`. ❌ Fail: Lỗi gỡ hoặc còn task.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-031: Gỡ `dwo_sla_demo_ticket` xóa 4 định nghĩa mẫu

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-09 |
| Coverage Item | CI-2 (Định nghĩa mẫu khi gỡ demo) |
| Requirement Ref | REQ-INST-004 AC1 |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (lệnh cài/gỡ trong CI) |

**Preconditions:**
1. Cài `dwo_sla_demo_ticket` (FX-DEMO: 4 định nghĩa mẫu).
2. Tạo 3 `demo.ticket` priority `p1`, đánh giá now = T0 → mỗi ticket ≥ 1 task `in_progress` (đếm DT = số task của `demo.ticket`, DT >= 3).
3. Tạo `res.partner` P (ref=`NEW`) với FX-DEF-STD, 1 task (đếm PT = 1).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| module | `dwo_sla_demo_ticket` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gỡ module `dwo_sla_demo_ticket` bằng `button_immediate_uninstall`. | Không ném lỗi; `ir.module.module` của `dwo_sla_demo_ticket` có `state` = `uninstalled`. |
| 2 | Đếm `sla.definition` có `model_id.model` = `demo.ticket` (kể cả archive). | = 0 (trước khi gỡ = 4). |

**Pass/Fail Criteria:** ✅ Pass: Định nghĩa mẫu không còn. ❌ Fail: Còn định nghĩa mẫu.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-032: Gỡ `dwo_sla_demo_ticket` không xóa task của `res.partner`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-09 |
| Coverage Item | CI-3 (Dữ liệu SLA của model khác khi gỡ demo) |
| Requirement Ref | REQ-INST-004 AC1 (negative bổ sung) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (lệnh cài/gỡ trong CI) |

**Preconditions:**
1. Cài `dwo_sla_demo_ticket` (FX-DEMO: 4 định nghĩa mẫu).
2. Tạo 3 `demo.ticket` priority `p1`, đánh giá now = T0 → mỗi ticket ≥ 1 task `in_progress` (đếm DT = số task của `demo.ticket`, DT >= 3).
3. Tạo `res.partner` P (ref=`NEW`) với FX-DEF-STD, 1 task (đếm PT = 1).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| module | `dwo_sla_demo_ticket` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gỡ module `dwo_sla_demo_ticket` bằng `button_immediate_uninstall`. | Không ném lỗi; `ir.module.module` của `dwo_sla_demo_ticket` có `state` = `uninstalled`. |
| 2 | Đếm task của FX-DEF-STD trên P. | = 1 (PT), `stage` = `in_progress`; FX-DEF-STD còn. |

**Pass/Fail Criteria:** ✅ Pass: Task `res.partner` giữ nguyên. ❌ Fail: Task hoặc định nghĩa của `res.partner` bị xóa.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-033: Cài module trên image dựng từ Dockerfile của repo không cần thêm gói Python

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-10 |
| Coverage Item | CI-1 (Image từ Dockerfile của repo) |
| Requirement Ref | REQ-PORT-001 AC1 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (lệnh cài/gỡ trong CI) |

**Preconditions:**
1. Build image: `docker build -t itsmforis-app:latest .` từ repo (base `odoo:19.0-20260421`).
2. Chạy container với PostgreSQL theo docker-compose; ghi `pip freeze` trong container (PF0).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| lệnh | `odoo -d sla_test -i dwo_sla_core --stop-after-init` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Chạy lệnh cài. | Mã thoát 0; log không có `ERROR` và không có `ModuleNotFoundError`/`ImportError`. |
| 2 | Ghi lại `pip freeze` (PF1). | PF1 = PF0 (không cài thêm gói). |

**Pass/Fail Criteria:** ✅ Pass: Cài thành công mà không cần thêm gói. ❌ Fail: Lỗi cài hoặc phải cài thêm gói.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-034: Mã nguồn module chỉ import thư viện chuẩn và `odoo`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-10 |
| Coverage Item | CI-2 (Import trong mã nguồn) |
| Requirement Ref | REQ-PORT-001 Statement |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Mã nguồn `custom-addons/dwo_sla_core/` ở build đang test; `__manifest__.py` đọc được.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| phạm vi | Mọi file `*.py` trừ `tests/` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Phân tích AST mọi file `*.py`, liệt kê mọi top-level package được import. | Mọi package thuộc `sys.stdlib_module_names` hoặc là `odoo`. |
| 2 | Đọc `external_dependencies` trong manifest. | Rỗng hoặc không khai báo. |

**Pass/Fail Criteria:** ✅ Pass: Không có import ngoài stdlib/`odoo`. ❌ Fail: Có import thư viện ngoài.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-INF-035: Gỡ module chứa model có định nghĩa SLA: CASCADE xóa định nghĩa, task, event, lượt thử lại và dấu mốc đã xử lý, không lỗi và `dwo_sla_core` vẫn hoạt động

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-14-07 |
| Coverage Item | CI-5 (Gỡ module sở hữu model gắn SLA: CASCADE ở CSDL, 030 mục 5) |
| Requirement Ref | REQ-INST-001 (mở rộng: gỡ module có model gắn SLA) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (CI trên database riêng) |

**Preconditions:**
1. Database riêng `sla_inst2` có `base` và `dwo_sla_core`; ca tự cài thêm module mẫu `x_sla_victim` (chỉ dùng trong test) định nghĩa model `x.sla.victim` (field `name`, `ref` Char); trong database có 1000 `res.partner`; ghi checksum bảng `res_partner` (CK0).
2. Định nghĩa DV trên `x.sla.victim` (mục tiêu 4 giờ, start `[('ref','=','NEW')]`) có 1 mốc escalation 75% (server action ghi chatter); định nghĩa DP trên `res.partner` (FX-DEF-STD) có 1 task.
3. Record V (`ref` = 'NEW') của `x.sla.victim` có 1 task TV `in_progress` (kèm event `attach`, 1 dòng `sla.escalation.retry` và 1 dòng `sla_task_escalation_done_rel`); record `res.partner` P (`ref`='NEW') có 1 task TP của DP.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Module bị gỡ | `x_sla_victim` |  |
| Số bản ghi trước gỡ | DV=1, TV=1, event của TV>=1, retry=1, done_rel=1 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gỡ module `x_sla_victim` bằng `button_immediate_uninstall` | Không ném lỗi (xóa `ir_model` kéo CASCADE xuống `sla_definition` rồi `sla_task` và các bảng con) |
| 2 | Đếm bản ghi theo SQL: `sla_definition` có `model_name` = 'x.sla.victim'; `sla_task` có `res_model` = 'x.sla.victim'; `sla_event`, `sla_escalation_retry`, `sla_task_escalation_done_rel` của TV | Tất cả = 0 |
| 3 | Đọc DP, TP và event của TP; tính checksum `res_partner` | DP còn; TP còn `in_progress`; checksum = CK0; `dwo_sla_core` vẫn `installed` |
| 4 | Tạo `res.partner` mới `ref`='NEW' | Có 1 task `in_progress` (hook vẫn hoạt động, không lỗi do patch của model đã gỡ) |

**Pass/Fail Criteria:** ✅ Pass: bản ghi SLA của model đã gỡ bị CASCADE sạch, dữ liệu SLA của `res.partner` nguyên vẹn và hook còn hoạt động; ❌ Fail: lỗi khi gỡ, còn bản ghi SLA mồ côi, hoặc task của `res.partner` bị xóa

**Ghi chú:** Bổ sung theo Database Design 0.2 (task CASCADE ở CSDL; xóa định nghĩa còn task bị chặn ở ứng dụng bằng `@api.ondelete(at_uninstall=False)`, trong lúc gỡ module thì được phép) và REQ-INST-001. Việc chặn xóa định nghĩa còn task ở ứng dụng đã có ở TC-CHG-026, TC-CHG-027 (REQ-FUNC-061).

**Postconditions:** Hủy database `sla_inst2`.

## TG-15 — Nguồn lịch

### TC-CAL-001: Từ chối lưu định nghĩa nguồn definition khi calendar không có dòng giờ làm nào

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-15-01 |
| Coverage Item | CI-1 (Calendar không có dòng giờ làm) |
| Requirement Ref | REQ-FUNC-039 (AC1) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. FX-CAL-EMPTY: calendar `fully_fixed`, không có dòng giờ làm (`attendance_ids` rỗng).
3. Chưa có định nghĩa nào tên `CAL-001` trên `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| schedule_source | `definition` |  |
| schedule_id | FX-CAL-EMPTY |  |
| model | `res.partner` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` tên `CAL-001` (model `res.partner`, `schedule_source` = `definition`, `schedule_id` = FX-CAL-EMPTY, `duration` = 4) bằng U-MGR | Ném `ValidationError`; thông báo nêu calendar không có giờ làm việc |
| 2 | Tìm `sla.definition` tên `CAL-001` (kể cả archive) | Không có bản ghi nào |

**Pass/Fail Criteria:** ✅ Pass: Lưu bị từ chối và không có bản ghi `CAL-001`; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CAL-002: Lưu thành công định nghĩa nguồn definition với calendar fully_fixed có giờ làm T2-T6

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-15-01 |
| Coverage Item | CI-2 (Calendar fully_fixed có giờ T2-T6 (happy path)) |
| Requirement Ref | REQ-FUNC-039 (AC2) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. FX-CAL-VN: `fully_fixed`, `Asia/Ho_Chi_Minh`, T2-T6 08:00-17:00.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| schedule_source | `definition` |  |
| schedule_id | FX-CAL-VN |  |
| duration | 4 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` tên `CAL-002` (model `res.partner`, `schedule_source` = `definition`, `schedule_id` = FX-CAL-VN, `duration` = 4) bằng U-MGR | Lưu thành công, không có lỗi |
| 2 | Đọc lại `schedule_id` của `CAL-002` | = FX-CAL-VN |

**Pass/Fail Criteria:** ✅ Pass: Bản ghi được tạo với `schedule_id` = FX-CAL-VN; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CAL-003: Từ chối chọn calendar flexible làm lịch cố định của định nghĩa

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-15-02 |
| Coverage Item | CI-1 (Nguồn definition chọn calendar flexible) |
| Requirement Ref | REQ-INT-009 (AC1) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. FX-CAL-FLEX: calendar loại `flexible` (`flexible_hours` = True).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| schedule_source | `definition` |  |
| schedule_id | FX-CAL-FLEX |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` tên `CAL-003` (model `res.partner`, `schedule_source` = `definition`, `schedule_id` = FX-CAL-FLEX, `duration` = 4) bằng U-MGR | Ném `ValidationError`; thông báo nêu calendar không phải `fully_fixed` |
| 2 | Tìm `sla.definition` tên `CAL-003` | Không có bản ghi nào |

**Pass/Fail Criteria:** ✅ Pass: Lưu bị từ chối; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CAL-004: Dùng lịch dự phòng của công ty và ghi lý do vào event attach khi record trả calendar flexible

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-15-02 |
| Coverage Item | CI-2 (Nguồn record trả calendar flexible) |
| Requirement Ref | REQ-INT-009 (AC2) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Công ty CO-A có `resource_calendar_id` = FX-CAL-VN; công ty CO-B có `resource_calendar_id` = FX-CAL-VN-PM; cả hai thuộc FX-CO.
3. Field Many2one `x_calendar_id` -> `resource.calendar` trên `res.partner` do ca tự tạo (`ir.model.fields` loại manual) để làm đích của đường dẫn lịch.
4. Partner Q có `x_calendar_id` = FX-CAL-FLEX (`flexible`); partner P có `parent_id` = Q, `company_id` = CO-A, `ref` = `NEW`, tạo TRƯỚC định nghĩa.
5. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4, `schedule_source` = `record`, `schedule_path` = `parent_id.x_calendar_id`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| schedule_path | `parent_id.x_calendar_id` |  |
| Calendar tại cuối đường dẫn | FX-CAL-FLEX | không dùng được |
| Lịch mặc định CO-A | FX-CAL-VN | dùng được |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Có 1 task `in_progress`; `schedule_id` = FX-CAL-VN |
| 2 | Đọc `note` của event `attach` của task | `note` không rỗng, nêu calendar FX-CAL-FLEX không dùng được vì loại `flexible` |

**Pass/Fail Criteria:** ✅ Pass: `schedule_id` = FX-CAL-VN và `note` của event `attach` nêu lý do dự phòng; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Ghi chú:** nội dung `note` không được SRS quy định; kiểm bằng việc chứa tên calendar và từ `flexible` (NOTE_002 trong `constants/message.py`: "Calendar '%s' cannot be used (flexible type or no working hours).").

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CAL-005: Dùng calendar tại cuối đường dẫn parent_id.x_calendar_id khi các bước đều có giá trị

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-15-03 |
| Coverage Item | CI-1 (Đường dẫn hợp lệ 2 bước, các bước đều có giá trị) |
| Requirement Ref | REQ-FUNC-019 (AC1) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Công ty CO-A có `resource_calendar_id` = FX-CAL-VN; công ty CO-B có `resource_calendar_id` = FX-CAL-VN-PM; cả hai thuộc FX-CO.
3. Field Many2one `x_calendar_id` -> `resource.calendar` trên `res.partner` do ca tự tạo (`ir.model.fields` loại manual) để làm đích của đường dẫn lịch.
4. FX-CAL-VN-PM (fixture bổ sung): `fully_fixed`, `Asia/Ho_Chi_Minh`, T2-T6 13:00-18:00 (5 giờ/ngày).
5. Partner Q có `x_calendar_id` = FX-CAL-VN-PM; partner P có `parent_id` = Q, `company_id` = CO-A, `ref` = `NEW`, tạo TRƯỚC định nghĩa.
6. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 2, `schedule_source` = `record`, `schedule_path` = `parent_id.x_calendar_id`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| schedule_path | `parent_id.x_calendar_id` | 2 bước |
| duration | 2 |  |
| now | T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Có 1 task `in_progress`; `schedule_id` = FX-CAL-VN-PM (không phải lịch công ty FX-CAL-VN) |
| 2 | Đọc `planned_end_time` | = 2026-03-02 08:00 UTC (15:00 giờ địa phương: giờ làm bắt đầu 13:00, cộng 2 giờ) |
| 3 | Đếm event `attach` của task | 1 event |

**Pass/Fail Criteria:** ✅ Pass: `schedule_id` = FX-CAL-VN-PM và `planned_end_time` = 08:00 UTC; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CAL-006: Từ chối lưu đường dẫn có bước giữa là One2many

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-15-03 |
| Coverage Item | CI-2 (Bước giữa không phải Many2one (One2many)) |
| Requirement Ref | REQ-FUNC-019 (AC2) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Field Many2one `x_calendar_id` -> `resource.calendar` trên `res.partner` do ca tự tạo (`ir.model.fields` loại manual) để làm đích của đường dẫn lịch.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| schedule_source | `record` |  |
| schedule_path | `child_ids.x_calendar_id` | `child_ids` là One2many |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` tên `CAL-004` (model `res.partner`, `schedule_source` = `record`, `schedule_path` = `child_ids.x_calendar_id`) bằng U-MGR | Ném `ValidationError`; thông báo nêu bước `child_ids` không phải Many2one |
| 2 | Tìm `sla.definition` tên `CAL-004` | Không có bản ghi nào |

**Pass/Fail Criteria:** ✅ Pass: Lưu bị từ chối; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CAL-007: Từ chối lưu đường dẫn có bước cuối trỏ tới res.company thay vì resource.calendar

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-15-03 |
| Coverage Item | CI-3 (Bước cuối không phải `resource.calendar`) |
| Requirement Ref | REQ-FUNC-019 (AC2) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| schedule_source | `record` |  |
| schedule_path | `parent_id.company_id` | bước cuối là Many2one tới `res.company` |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Tạo `sla.definition` tên `CAL-005` (model `res.partner`, `schedule_source` = `record`, `schedule_path` = `parent_id.company_id`) bằng U-MGR | Ném `ValidationError`; thông báo nêu bước cuối phải trỏ tới `resource.calendar` |
| 2 | Tìm `sla.definition` tên `CAL-005` | Không có bản ghi nào |

**Pass/Fail Criteria:** ✅ Pass: Lưu bị từ chối; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CAL-008: Task không có lịch (24x7) khi nguồn lịch là none

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-15-03 |
| Coverage Item | CI-4 (Nguồn `none`) |
| Requirement Ref | REQ-FUNC-019 (AC3) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Partner P có `ref` = `NEW`, tạo TRƯỚC định nghĩa.
3. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4 (nguồn lịch `none`); là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| schedule_source | `none` (mặc định) |  |
| duration | 4 |  |
| now | T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Có 1 task `in_progress`; `schedule_id` rỗng |
| 2 | Đọc `planned_end_time` | = 2026-03-02 06:00 UTC (start + 4 giờ, 24x7) |

**Pass/Fail Criteria:** ✅ Pass: `schedule_id` rỗng và `planned_end_time` = 06:00 UTC; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CAL-009: Dùng calendar trên chính record khi đường dẫn chỉ có một bước x_calendar_id

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-15-03 |
| Coverage Item | CI-5 (Biên: đường dẫn 1 bước (field trên chính record)) |
| Requirement Ref | REQ-FUNC-019 (AC1) |
| Priority | P3-Medium |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Công ty CO-A có `resource_calendar_id` = FX-CAL-VN; công ty CO-B có `resource_calendar_id` = FX-CAL-VN-PM; cả hai thuộc FX-CO.
3. Field Many2one `x_calendar_id` -> `resource.calendar` trên `res.partner` do ca tự tạo (`ir.model.fields` loại manual) để làm đích của đường dẫn lịch.
4. FX-CAL-VN-PM (fixture bổ sung): `fully_fixed`, `Asia/Ho_Chi_Minh`, T2-T6 13:00-18:00 (5 giờ/ngày).
5. Partner P có `x_calendar_id` = FX-CAL-VN-PM, `company_id` = CO-A, `ref` = `NEW`, tạo TRƯỚC định nghĩa.
6. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4, `schedule_source` = `record`, `schedule_path` = `x_calendar_id`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| schedule_path | `x_calendar_id` | 1 bước, biên độ dài đường dẫn |
| now | T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Có 1 task `in_progress`; `schedule_id` = FX-CAL-VN-PM |

**Pass/Fail Criteria:** ✅ Pass: `schedule_id` = FX-CAL-VN-PM; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CAL-010: Dùng lịch mặc định của công ty của record và ghi bước trống vào event attach khi record không có công ty mẹ

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-15-04 |
| Coverage Item | CI-1 (Bước đường dẫn trống (khách hàng không có công ty mẹ)) |
| Requirement Ref | REQ-FUNC-020 (AC1) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Công ty CO-A có `resource_calendar_id` = FX-CAL-VN; công ty CO-B có `resource_calendar_id` = FX-CAL-VN-PM; cả hai thuộc FX-CO.
3. Field Many2one `x_calendar_id` -> `resource.calendar` trên `res.partner` do ca tự tạo (`ir.model.fields` loại manual) để làm đích của đường dẫn lịch.
4. Partner P có `parent_id` rỗng, `company_id` = CO-A, `ref` = `NEW`, tạo TRƯỚC định nghĩa; công ty hiện tại của env là CO-B (để phân biệt công ty của record với công ty hiện tại).
5. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4, `schedule_source` = `record`, `schedule_path` = `parent_id.x_calendar_id`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Bước trống | `parent_id` |  |
| Lịch mặc định CO-A | FX-CAL-VN | công ty của record |
| Lịch mặc định CO-B | FX-CAL-VN-PM | công ty hiện tại |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Có 1 task `in_progress`; `schedule_id` = FX-CAL-VN |
| 2 | Đọc `note` của event `attach` | `note` không rỗng và chứa `parent_id` (bước trống) |

**Pass/Fail Criteria:** ✅ Pass: `schedule_id` = FX-CAL-VN và `note` nêu bước trống `parent_id`; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Ghi chú:** code ghi NOTE_001 chứa toàn bộ đường dẫn (`parent_id.x_calendar_id`), không tách riêng bước trống; ca kiểm `note` chứa `parent_id`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CAL-011: Dùng lịch mặc định của công ty khi calendar cuối đường dẫn trống

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-15-04 |
| Coverage Item | CI-2 (Calendar cuối đường dẫn trống) |
| Requirement Ref | REQ-FUNC-020 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Công ty CO-A có `resource_calendar_id` = FX-CAL-VN; công ty CO-B có `resource_calendar_id` = FX-CAL-VN-PM; cả hai thuộc FX-CO.
3. Field Many2one `x_calendar_id` -> `resource.calendar` trên `res.partner` do ca tự tạo (`ir.model.fields` loại manual) để làm đích của đường dẫn lịch.
4. Partner Q có `x_calendar_id` rỗng; partner P có `parent_id` = Q, `company_id` = CO-A, `ref` = `NEW`, tạo TRƯỚC định nghĩa.
5. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4, `schedule_source` = `record`, `schedule_path` = `parent_id.x_calendar_id`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Calendar cuối | rỗng |  |
| Lịch mặc định CO-A | FX-CAL-VN |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Có 1 task; `schedule_id` = FX-CAL-VN |
| 2 | Đọc `note` của event `attach` | `note` không rỗng và chứa `x_calendar_id` |

**Pass/Fail Criteria:** ✅ Pass: `schedule_id` = FX-CAL-VN và `note` nêu lý do; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CAL-012: Dùng lịch mặc định của công ty khi calendar của record không có giờ làm

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-15-04 |
| Coverage Item | CI-3 (Calendar cuối không có giờ làm) |
| Requirement Ref | REQ-FUNC-020 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Công ty CO-A có `resource_calendar_id` = FX-CAL-VN; công ty CO-B có `resource_calendar_id` = FX-CAL-VN-PM; cả hai thuộc FX-CO.
3. Field Many2one `x_calendar_id` -> `resource.calendar` trên `res.partner` do ca tự tạo (`ir.model.fields` loại manual) để làm đích của đường dẫn lịch.
4. Partner Q có `x_calendar_id` = FX-CAL-EMPTY (fully_fixed, không có dòng giờ làm); partner P có `parent_id` = Q, `company_id` = CO-A, `ref` = `NEW`, tạo TRƯỚC định nghĩa.
5. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4, `schedule_source` = `record`, `schedule_path` = `parent_id.x_calendar_id`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Calendar cuối | FX-CAL-EMPTY | không có giờ làm |
| Lịch mặc định CO-A | FX-CAL-VN |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Có 1 task; `schedule_id` = FX-CAL-VN |
| 2 | Đọc `note` của event `attach` | `note` không rỗng và chứa tên calendar 'FX-CAL-EMPTY' (NOTE_002) |

**Pass/Fail Criteria:** ✅ Pass: `schedule_id` = FX-CAL-VN và `note` nêu lý do; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Ghi chú:** nguồn `record` không từ chối calendar rỗng khi lưu (REQ-FUNC-039 More Information); ghi chú nêu calendar không dùng được.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CAL-013: Task chạy 24x7 và ghi lý do khi lịch mặc định của công ty cũng không dùng được

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-15-04 |
| Coverage Item | CI-4 (Lịch mặc định của công ty cũng không dùng được) |
| Requirement Ref | REQ-FUNC-020 (AC2) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Công ty CO-A có `resource_calendar_id` = FX-CAL-VN; công ty CO-B có `resource_calendar_id` = FX-CAL-VN-PM; cả hai thuộc FX-CO.
3. Field Many2one `x_calendar_id` -> `resource.calendar` trên `res.partner` do ca tự tạo (`ir.model.fields` loại manual) để làm đích của đường dẫn lịch.
4. Đặt `resource_calendar_id` của CO-A = FX-CAL-FLEX (không dùng được). Partner P có `parent_id` rỗng, `company_id` = CO-A, `ref` = `NEW`, tạo TRƯỚC định nghĩa.
5. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4, `schedule_source` = `record`, `schedule_path` = `parent_id.x_calendar_id`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Lịch mặc định CO-A | FX-CAL-FLEX | không dùng được |
| duration | 4 |  |
| now | T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Có 1 task `in_progress`; `schedule_id` rỗng |
| 2 | Đọc `planned_end_time` | = 2026-03-02 06:00 UTC (24x7) |
| 3 | Đọc `note` của event `attach` | `note` không rỗng, nêu lịch công ty không dùng được và việc chạy 24x7 |

**Pass/Fail Criteria:** ✅ Pass: `schedule_id` rỗng, `planned_end_time` = 06:00 UTC và `note` nêu lý do; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CAL-014: Dùng lịch mặc định của công ty hiện tại khi record không có công ty

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-15-04 |
| Coverage Item | CI-5 (Biên: record không có công ty) |
| Requirement Ref | REQ-FUNC-020 |
| Priority | P2-High |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Công ty CO-A có `resource_calendar_id` = FX-CAL-VN; công ty CO-B có `resource_calendar_id` = FX-CAL-VN-PM; cả hai thuộc FX-CO.
3. Field Many2one `x_calendar_id` -> `resource.calendar` trên `res.partner` do ca tự tạo (`ir.model.fields` loại manual) để làm đích của đường dẫn lịch.
4. Partner P có `parent_id` rỗng, `company_id` rỗng, `ref` = `NEW`, tạo TRƯỚC định nghĩa; công ty hiện tại của env là CO-B.
5. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4, `schedule_source` = `record`, `schedule_path` = `parent_id.x_calendar_id`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Công ty của record | rỗng |  |
| Công ty hiện tại | CO-B | lịch FX-CAL-VN-PM |
| Lịch mặc định CO-A | FX-CAL-VN | không được dùng |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0 (2026-03-02 09:00 giờ địa phương = 02:00 UTC))` | Có 1 task; `schedule_id` = FX-CAL-VN-PM |

**Pass/Fail Criteria:** ✅ Pass: `schedule_id` = FX-CAL-VN-PM; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-CAL-015: Tính lịch đúng khi người dùng sửa record không có quyền đọc record liên kết

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-15-04 |
| Coverage Item | CI-6 (Negative: người dùng không có quyền đọc record liên kết) |
| Requirement Ref | REQ-FUNC-020 (AC3) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. CSDL `sla_test` đã cài `dwo_sla_core`; công ty hiện tại là CO-A; thao tác cấu hình do user U-MGR (FX-USERS) thực hiện.
2. Công ty CO-A có `resource_calendar_id` = FX-CAL-VN; công ty CO-B có `resource_calendar_id` = FX-CAL-VN-PM; cả hai thuộc FX-CO.
3. Field Many2one `x_calendar_id` -> `resource.calendar` trên `res.partner` do ca tự tạo (`ir.model.fields` loại manual) để làm đích của đường dẫn lịch.
4. Partner Q (parent) có `x_calendar_id` = FX-CAL-VN-PM; partner P có `parent_id` = Q, `company_id` = CO-A, `ref` = `NEW`, tạo TRƯỚC định nghĩa.
5. Record rule bổ sung loại Q khỏi phạm vi đọc của U-BIZ (`[('id', '!=', Q.id)]`); xác nhận `Q.with_user(U-BIZ).read(['name'])` ném `AccessError`.
6. Định nghĩa FX-DEF-STD trên `res.partner` với `duration` = 4, `schedule_source` = `record`, `schedule_path` = `parent_id.x_calendar_id`; là định nghĩa duy nhất đang bật của `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-BIZ | chỉ sửa `res.partner`, không đọc được Q |
| schedule_path | `parent_id.x_calendar_id` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine `evaluate(P, now = T0)` với môi trường của U-BIZ (`env = env(user=U-BIZ)`) | Không ném `AccessError`; có 1 task; `schedule_id` = FX-CAL-VN-PM |
| 2 | Đếm event `error` của P | 0 event |

**Pass/Fail Criteria:** ✅ Pass: `schedule_id` = FX-CAL-VN-PM và không có event `error`; ❌ Fail: Một giá trị bất kỳ ở cột Expected Result khác kết quả mong đợi, hoặc engine ném lỗi không dự kiến.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

## TG-16 — Phân quyền và đa công ty

### TC-SEC-001: Ẩn menu SLA với người dùng không thuộc nhóm SLA

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-01 |
| Coverage Item | CI-1 (U-NONE không thấy menu SLA) |
| Requirement Ref | REQ-SEC-001 (AC1) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Module dwo_sla_core đã cài; menu gốc SLA (`menu_sla_root`) tồn tại.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-NONE | Không thuộc group_sla_user hay group_sla_manager |
| Menu | `dwo_sla_core.menu_sla_root` | menu gốc 'SLA' trong `views/sla_menus.xml` |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Lấy tập menu hiển thị của U-NONE (`ir.ui.menu._visible_menu_ids()` với env của U-NONE) | Tập kết quả KHÔNG chứa id của `menu_sla_root` và không chứa menu con nào của module (đếm = 0) |
| 2 | Lặp với U-USR | Tập kết quả chứa id của `menu_sla_root` (đối chứng) |

**Pass/Fail Criteria:** ✅ Pass: Bước 1 và 2 đúng như cột Expected. ❌ Fail: Có bất kỳ menu SLA nào xuất hiện cho U-NONE, hoặc U-USR không thấy menu.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-002: Từ chối sửa định nghĩa với group_sla_user

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-01 |
| Coverage Item | CI-2 (U-USR sửa định nghĩa bị từ chối) |
| Requirement Ref | REQ-SEC-001 (AC2) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng). Gọi là D1 với name='D1'.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-USR |  |
| Field sửa | name | 'D1' đổi thành 'D1-edit' |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-USR, gọi `D1.write({'name': 'D1-edit'})` | Ném AccessError |
| 2 | Đọc lại `D1.name` bằng quyền hệ thống | Giá trị vẫn là 'D1' |

**Pass/Fail Criteria:** ✅ Pass: Bước 1 ném AccessError và bước 2 giá trị không đổi. ❌ Fail: write thành công hoặc tên bị đổi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-003: Cho phép group_sla_manager sửa định nghĩa

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-01 |
| Coverage Item | CI-3 (U-MGR sửa định nghĩa thành công) |
| Requirement Ref | REQ-SEC-001 (AC3) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng). Gọi là D1 với name='D1'.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-MGR |  |
| Field sửa | name | 'D1' đổi thành 'D1-edit' |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-MGR, gọi `D1.write({'name': 'D1-edit'})` | Không ném lỗi, trả True |
| 2 | Đọc lại `D1.name` | Giá trị = 'D1-edit' |

**Pass/Fail Criteria:** ✅ Pass: Hai bước đúng Expected. ❌ Fail: Bị từ chối hoặc giá trị không đổi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-004: Cho phép group_sla_user đọc định nghĩa và task

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-01 |
| Coverage Item | CI-4 (U-USR đọc định nghĩa và task) |
| Requirement Ref | REQ-SEC-001 (AC4) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng). Gọi là D1.
3. Partner P (ref='NEW'). Tạo bằng sudo task K1: definition_id=FX-DEF-STD, res_model='res.partner', res_id của partner tương ứng, stage='in_progress', start_time=FX-T0 (2026-03-02 02:00 UTC), duration=4.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-USR |  |
| Định nghĩa | D1 | 1 bản ghi |
| Task | K1 | 1 bản ghi |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-USR: `sla.definition.search([('id','=',D1.id)])` rồi đọc `name` | Trả đúng 1 bản ghi, `name` đọc được |
| 2 | Với env của U-USR: `sla.task.search([('id','=',K1.id)])` rồi đọc `stage` | Trả đúng 1 bản ghi, `stage` = 'in_progress' |

**Pass/Fail Criteria:** ✅ Pass: Cả hai bước trả đúng 1 bản ghi, không lỗi quyền. ❌ Fail: AccessError hoặc kết quả rỗng.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-005: Từ chối đọc trực tiếp mọi model SLA với người dùng không thuộc nhóm

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-01 |
| Coverage Item | CI-5 (U-NONE đọc trực tiếp dữ liệu SLA) |
| Requirement Ref | REQ-SEC-001 (AC (Statement: không nhóm KHÔNG truy cập dữ liệu trực tiếp)) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng). Tạo thêm một mốc FX-ESC-STD và một event bằng sudo (event='attach').

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-NONE |  |
| Model | sla.definition, sla.escalation, sla.task, sla.event | 4 model |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-NONE, gọi `search([])` lần lượt trên từng model trong 4 model | Cả 4 lần ném AccessError (đếm lỗi = 4) |

**Pass/Fail Criteria:** ✅ Pass: Đếm AccessError = 4. ❌ Fail: Có model nào trả kết quả cho U-NONE.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-006: Tạo task SLA khi người dùng chỉ có quyền sửa record gốc

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-02 |
| Coverage Item | CI-1 (U-BIZ đổi partner thỏa start, task được tạo) |
| Requirement Ref | REQ-SEC-002 (AC1) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Partner P (ref='' ) tạo bằng quyền hệ thống; chưa có task.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-BIZ | Chỉ sửa res.partner |
| Thay đổi | ref: '' -> 'NEW' | Thỏa start |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-BIZ, gọi `P.write({'ref': 'NEW'})` | Ghi thành công, không AccessError |
| 2 | Bằng quyền hệ thống, đếm `sla.task` có res_model='res.partner', res_id=P.id, definition_id=FX-DEF-STD | Đếm = 1, stage = 'in_progress' |
| 3 | Đếm `sla.event` event='attach' của task đó | Đếm = 1 |

**Pass/Fail Criteria:** ✅ Pass: Cả 3 bước đạt. ❌ Fail: Ghi bị chặn do quyền SLA hoặc không có task.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-007: Từ chối đọc trực tiếp danh sách task với người dùng nghiệp vụ

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-02 |
| Coverage Item | CI-2 (U-BIZ đọc task bị từ chối) |
| Requirement Ref | REQ-SEC-002 (AC2) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Partner P ref='NEW'; tạo bằng sudo task in_progress của P (start_time=FX-T0, duration=4).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-BIZ | Cùng người dùng với TC-SEC-006 |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-BIZ, gọi `sla.task.search([])` | Ném AccessError |
| 2 | Với env của U-BIZ, gọi `sla.task.browse(K1.id).read(['stage'])` | Ném AccessError |

**Pass/Fail Criteria:** ✅ Pass: Cả 2 bước ném AccessError. ❌ Fail: Có dữ liệu task trả về cho U-BIZ.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-008: Ẩn task của công ty khác với người dùng chỉ thuộc công ty A

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-03 |
| Coverage Item | CI-1 (U-A không thấy task CO-B) |
| Requirement Ref | REQ-SEC-003 (AC1) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS và FX-CO; U-A: group_sla_user, chỉ được phép CO-A; U-MGR có cả CO-A và CO-B.
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Hai partner PA (company_id=CO-A) và PB (company_id=CO-B); tạo bằng sudo task KA (company_id=CO-A, res_id=PA) và KB (company_id=CO-B, res_id=PB), stage='in_progress', start_time=FX-T0, duration=4.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-A | allowed_company_ids=[CO-A] |
| Task | KA, KB |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-A (allowed_company_ids=[CO-A]), `sla.task.search([])` | Kết quả = {KA}, KB không có (đếm = 1) |
| 2 | Với env của U-A, đọc `KB.read(['stage'])` | Ném AccessError |

**Pass/Fail Criteria:** ✅ Pass: Bước 1 chỉ có KA; bước 2 AccessError. ❌ Fail: U-A thấy KB.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-009: Ẩn event của công ty khác với người dùng chỉ thuộc công ty A

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-03 |
| Coverage Item | CI-2 (U-A không thấy event CO-B) |
| Requirement Ref | REQ-SEC-003 (AC (Statement: event)) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS và FX-CO; U-A: group_sla_user, chỉ được phép CO-A; U-MGR có cả CO-A và CO-B.
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Tạo bằng sudo hai event: EA (company_id=CO-A, event='error') và EB (company_id=CO-B, event='error').

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-A | allowed_company_ids=[CO-A] |
| Event | EA, EB |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-A, `sla.event.search([])` | Kết quả = {EA} (đếm = 1), EB không có |

**Pass/Fail Criteria:** ✅ Pass: Chỉ EA trả về. ❌ Fail: EB xuất hiện.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-010: Giới hạn tầm nhìn định nghĩa theo công ty

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-03 |
| Coverage Item | CI-3 (U-A thấy định nghĩa CO-A và không gán, không thấy CO-B) |
| Requirement Ref | REQ-SEC-003 (AC (Statement: định nghĩa)) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS và FX-CO; U-A: group_sla_user, chỉ được phép CO-A; U-MGR có cả CO-A và CO-B.
2. Tạo bằng sudo 3 định nghĩa trên res.partner (cấu hình như FX-DEF-STD): DA (company_id=CO-A), DB (company_id=CO-B), DN (company_id rỗng).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-A | allowed_company_ids=[CO-A] |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-A, `sla.definition.search([('id','in',[DA,DB,DN])])` | Kết quả = {DA, DN} (đếm = 2); DB không có |

**Pass/Fail Criteria:** ✅ Pass: Kết quả đúng {DA, DN}. ❌ Fail: DB xuất hiện hoặc DN bị ẩn.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-011: Không gắn task khi định nghĩa gán công ty A và record thuộc công ty B

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-03 |
| Coverage Item | CI-4 (Định nghĩa CO-A không gắn record CO-B) |
| Requirement Ref | REQ-SEC-003 (AC2) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS và FX-CO; U-A: group_sla_user, chỉ được phép CO-A; U-MGR có cả CO-A và CO-B.
2. Không cần lịch (schedule_source=none).
3. Dựng FX-DEF-STD nhưng company_id=CO-A.
4. PA (company_id=CO-A, ref='NEW'), PB (company_id=CO-B, ref='NEW') tạo trước khi bật định nghĩa.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| now | FX-T0 = 2026-03-02 09:00 giờ địa phương |  |
| Records | PA, PB |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá PA với now = T0 (`evaluate(PA, now, changed)`, TAD 5.1) | Có đúng 1 task in_progress của PA (đối chứng) |
| 2 | Gọi Engine đánh giá PB với now = T0 | Số task của PB = 0; số event 'attach' của PB = 0 |

**Pass/Fail Criteria:** ✅ Pass: PA có 1 task; PB có 0 task, 0 event attach. ❌ Fail: PB có task.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-012: Áp dụng định nghĩa không gán công ty cho mọi công ty

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-03 |
| Coverage Item | CI-5 (Định nghĩa company_id rỗng gắn cả A và B) |
| Requirement Ref | REQ-SEC-003 (AC3) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS và FX-CO; U-A: group_sla_user, chỉ được phép CO-A; U-MGR có cả CO-A và CO-B.
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng). (company_id rỗng).
3. PA (company_id=CO-A, ref='NEW'), PB (company_id=CO-B, ref='NEW').

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| now | FX-T0 |  |
| Records | PA, PB |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá PA với now = T0 | Có 1 task in_progress của PA, task.company_id = CO-A |
| 2 | Gọi Engine đánh giá PB với now = T0 | Có 1 task in_progress của PB, task.company_id = CO-B |

**Pass/Fail Criteria:** ✅ Pass: Mỗi partner có đúng 1 task với company_id đúng. ❌ Fail: Thiếu task ở một trong hai công ty.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-013: Ghi escalate_failed khi action vượt quyền U-CRON và mốc không bật retry

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-04 |
| Coverage Item | CI-1 (Action lỗi quyền, retry=false) |
| Requirement Ref | REQ-SEC-004 (AC1 (nhánh không retry)) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS và FX-CO; U-CRON thuộc group_sla_user, được cấp CO-A và CO-B, không có quyền quản trị người dùng.
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Server action SA-DENY loại code, model res.partner, nội dung `env['res.users'].create({'name': 'x', 'login': 'x@sla.test'})` (cần quyền quản trị người dùng mà U-CRON không có).
4. Escalation ES1 trên FX-DEF-STD: percent=75, action_id=SA-DENY, retry=False. Partner P ref='NEW', task in_progress start_time=T0 (02:00 UTC), duration=4, next_due_at=T0+3h.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| now xử lý nền | T0 + 3h = 2026-03-02 12:00 giờ địa phương | đúng mốc 75% |
| User chạy | U-CRON |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi `env['sla.processor'].with_user(U-CRON).process_due()` (đường chạy thật của cron) với patch `odoo.fields.Datetime.now` trả T0 + 3h (12:00 giờ VN) và `fake_progress` | Không ném lỗi ra ngoài |
| 2 | Đếm event của task theo loại | escalate_failed = 1 (note không rỗng), escalate_retry = 0, escalate = 0 |
| 3 | Đọc quan hệ mốc đã xử lý của task | ES1 thuộc danh sách mốc đã xong |

**Pass/Fail Criteria:** ✅ Pass: Ba kết quả đúng. ❌ Fail: Có escalate hoặc escalate_retry, hoặc xử lý nền ném lỗi.

**Ghi chú:** (TA-33) trước đây `process_due()` đọc task bằng `sudo()` nên server action chạy với quyền superuser thay vì quyền user cron/công ty; ca viết theo kết quả SRS (REQ-SEC-004, REQ-INT-019); code đã sửa (TASKS T13): server action của escalation chạy theo quyền user nền và công ty của record (TA-33 ĐÃ SỬA).

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-014: Ghi escalate_retry khi action vượt quyền U-CRON và mốc bật retry [Đã gỡ D12]

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-04 |
| Coverage Item | CI-2 (Action lỗi quyền, retry=true) |
| Requirement Ref | REQ-SEC-004 (AC1 (nhánh retry)) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS và FX-CO; U-CRON thuộc `group_sla_user`, được cấp CO-A và CO-B, không có quyền quản trị người dùng.
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Server action SA-DENY loại code, model res.partner, nội dung `env['res.users'].create({'name': 'x', 'login': 'x@sla.test'})` (cần quyền quản trị người dùng mà U-CRON không có).
4. Escalation ES1: percent=75, action_id=SA-DENY, retry=True, retry_pattern='[1, 10]'. Partner P ref='NEW', task in_progress start_time=T0, duration=4.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| now xử lý nền | T0 + 3h = 12:00 giờ địa phương |  |
| User chạy | U-CRON |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi `env['sla.processor'].with_user(U-CRON).process_due()` (đường chạy thật của cron) với patch `odoo.fields.Datetime.now` trả T0 + 3h (12:00 giờ VN) và `fake_progress` | Không ném lỗi ra ngoài |
| 2 | Đếm event của task theo loại | escalate_retry = 1, escalate_failed = 0, escalate = 0 |
| 3 | Đọc sla.escalation.retry của (task, ES1) | 1 dòng, attempt = 1, retry_at = 2026-03-02 12:01 giờ địa phương (05:01 UTC) |
| 4 | Đọc quan hệ mốc đã xử lý | ES1 CHƯA thuộc danh sách mốc đã xong |

**Pass/Fail Criteria:** ✅ Pass: Bốn kết quả đúng. ❌ Fail: Có escalate_failed ngay, hoặc retry_at khác 12:01.

**Ghi chú:** (TA-33) trước đây `process_due()` đọc task bằng `sudo()` nên server action chạy với quyền superuser thay vì quyền user cron/công ty; ca viết theo kết quả SRS (REQ-SEC-004, REQ-INT-019); code đã sửa (TASKS T13): server action của escalation chạy theo quyền user nền và công ty của record (TA-33 ĐÃ SỬA).

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-015: Kiểm ghi chú quyền user xử lý nền trên form escalation

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-04 |
| Coverage Item | CI-3 (Form escalation có ghi chú quyền) |
| Requirement Ref | REQ-SEC-004 (AC2) |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. Môi trường: database sla_test đã cài dwo_sla_core và dwo_sla_demo_ticket (FX-DEMO), trình duyệt đăng nhập được bằng tài khoản của FX-USERS.
2. Đăng nhập U-MGR; có 1 định nghĩa với ít nhất 1 mốc escalation.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Màn hình | Form sla.escalation (hoặc dòng escalation trên form định nghĩa) |  |
| Người kiểm | QA |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Mở form escalation của định nghĩa | Hiển thị form, không lỗi |
| 2 | Tìm ghi chú gần field Server Action | Có ghi chú văn bản (không phải chỉ tooltip trống) |
| 3 | Đọc nội dung ghi chú | Nêu rõ: server action chạy theo quyền của user được gán cho xử lý nền (cron) |
| 4 | Đọc nội dung ghi chú, tìm ý ngược | Không nêu action chạy với quyền của người đang sửa record |

**Pass/Fail Criteria:** ✅ Pass: Cả 4 mục đạt; ghi biên bản kèm ảnh chụp. ❌ Fail: Không có ghi chú hoặc nội dung sai ý.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-016: Tính đúng lịch của công ty mẹ khi người dùng không có quyền đọc

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-05 |
| Coverage Item | CI-1 (Attach dùng lịch FX-CAL-VN dù U-BIZ-S không đọc PM) |
| Requirement Ref | REQ-SEC-005 (AC1) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS và FX-CO; U-BIZ-S = U-BIZ cộng group_sla_user, allowed_company_ids=[CO-A] (không đọc được record của CO-B).
2. Dựng FX-CAL-VN (fully_fixed, Asia/Ho_Chi_Minh, T2-T6 08:00-17:00, 9 giờ/ngày, không nghỉ trưa).
3. CO-B.resource_calendar_id = FX-CAL-VN. Partner mẹ PM (name='PM-Secret', company_id=CO-B); partner con PC (company_id=CO-A, parent_id=PM, ref='NEW') [Giả định: res.partner cho phép con khác công ty với mẹ].
4. Dựng định nghĩa như FX-DEF-STD nhưng schedule_source='record', schedule_path='parent_id.company_id.resource_calendar_id'.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| now | FX-T0 |  |
| User | U-BIZ-S |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-BIZ-S, xác nhận `PM.read(['name'])` ném AccessError | Ném AccessError (xác nhận điều kiện tiền đề) |
| 2 | Gọi Engine đánh giá PC với now = T0, thực thi trong ngữ cảnh U-BIZ-S | Có 1 task in_progress của PC |
| 3 | Đọc task bằng quyền hệ thống | schedule_id = FX-CAL-VN; start_time = 2026-03-02 09:00 giờ địa phương; planned_end_time = 2026-03-02 13:00 giờ địa phương (4 giờ làm việc) |
| 4 | Đọc note của event 'attach' | Không chứa chuỗi 'fallback' hay 'dự phòng' (lịch lấy được, không rơi về mặc định) |

**Pass/Fail Criteria:** ✅ Pass: 4 bước đúng. ❌ Fail: Task rơi về lịch mặc định hoặc 24x7 (planned_end_time khác 13:00), hoặc lỗi quyền.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-017: Không lộ dữ liệu record liên kết khi xem task

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-05 |
| Coverage Item | CI-2 (Task và event không chứa dữ liệu PM ngoài tên calendar) |
| Requirement Ref | REQ-SEC-005 (AC2) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS và FX-CO; U-BIZ-S = U-BIZ cộng group_sla_user, allowed_company_ids=[CO-A] (không đọc được record của CO-B).
2. Dựng FX-CAL-VN (fully_fixed, Asia/Ho_Chi_Minh, T2-T6 08:00-17:00, 9 giờ/ngày, không nghỉ trưa).
3. CO-B.resource_calendar_id = FX-CAL-VN. Partner mẹ PM (name='PM-Secret', company_id=CO-B); partner con PC (company_id=CO-A, parent_id=PM, ref='NEW') [Giả định: res.partner cho phép con khác công ty với mẹ].
4. Dựng định nghĩa như FX-DEF-STD nhưng schedule_source='record', schedule_path='parent_id.company_id.resource_calendar_id'.
5. Task K của PC được tạo trong Preconditions của ca này bằng `evaluate(PC, now = T0)` với env hệ thống (lịch FX-CAL-VN lấy qua `parent_id.company_id.resource_calendar_id`); K `in_progress`.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| User | U-BIZ-S | có group_sla_user |
| Chuỗi cấm | 'PM-Secret', tên CO-B |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-BIZ-S, đọc K với mọi field lưu trữ (`read()` không đối số) | Đọc được; schedule_id hiển thị tên 'FX-CAL-VN' |
| 2 | Duyệt giá trị chuỗi của mọi field trên K | Không giá trị nào chứa 'PM-Secret' hoặc tên của CO-B |
| 3 | Đọc mọi event của K (field note, res_model, res_id) | Không note nào chứa 'PM-Secret' hoặc tên CO-B |
| 4 | Với env của U-BIZ-S, đọc `PM.read(['name'])` | Vẫn ném AccessError |

**Pass/Fail Criteria:** ✅ Pass: Bước 1 đọc được, bước 2 và 3 không chứa chuỗi cấm, bước 4 AccessError. ❌ Fail: Có chuỗi cấm trong dữ liệu hiển thị.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-018: Từ chối tạo, sửa, xóa task trực tiếp với SLA Manager

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-06 |
| Coverage Item | CI-1 (U-MGR không ghi trực tiếp task) |
| Requirement Ref | REQ-SEC-006 (AC1 (task)) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Partner P ref='NEW'; task K (sudo) in_progress start_time=T0, duration=4.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-MGR |  |
| Thao tác | create/write/unlink | 3 thao tác |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-MGR, `sla.task.create({definition_id: FX-DEF-STD, res_model: 'res.partner', res_id: P.id, start_time: T0, duration: 4})` | Ném AccessError |
| 2 | Với env của U-MGR, `K.write({'duration': 8})` | Ném AccessError |
| 3 | Với env của U-MGR, `K.unlink()` | Ném AccessError |
| 4 | Đọc K bằng quyền hệ thống | K còn tồn tại, duration = 4 |

**Pass/Fail Criteria:** ✅ Pass: 3 AccessError, K không đổi. ❌ Fail: Một thao tác thành công.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-019: Từ chối tạo, xóa event và sửa field khác is_resolved với SLA Manager

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-06 |
| Coverage Item | CI-2 (U-MGR không ghi event ngoài ngoại lệ) |
| Requirement Ref | REQ-SEC-006 (AC1 (event)) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Event E (sudo): event='error', note='boom', is_resolved=False, res_model='res.partner', res_id=1.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-MGR |  |
| Field sửa | note | 'boom' -> 'edited' |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-MGR, `sla.event.create({'event': 'attach', 'event_dt': T0})` | Ném `AccessError` (ACL `sla.event` không cấp quyền ghi cho nhóm SLA) |
| 2 | Với env của U-MGR, `E.write({'note': 'edited'})` | Ném `AccessError` (ACL `sla.event` không cấp quyền ghi cho nhóm SLA) |
| 3 | Với env của U-MGR, `E.unlink()` | Ném `AccessError` (ACL `sla.event` không cấp quyền ghi cho nhóm SLA) |
| 4 | Đọc E bằng quyền hệ thống | E còn tồn tại, note = 'boom', is_resolved = False |

**Pass/Fail Criteria:** ✅ Pass: 3 thao tác bị từ chối, E không đổi. ❌ Fail: Một thao tác thành công.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-020: Cho phép SLA Manager đánh dấu event error đã xử lý

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-06 |
| Coverage Item | CI-3 (U-MGR sửa is_resolved thành công) |
| Requirement Ref | REQ-SEC-006 (AC3) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Event E (sudo): event='error', note='boom', is_resolved=False.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-MGR |  |
| Field | is_resolved | False -> True |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-MGR, gọi `E.action_mark_resolved()` (đường ghi hợp lệ duy nhất cho `is_resolved`; ACL `sla.event` của Manager chỉ đọc nên `E.write` trực tiếp bị từ chối) | Không ném lỗi; đọc lại bằng sudo `E.is_resolved` = True |
| 2 | Đọc E | is_resolved = True; note vẫn 'boom' |

**Pass/Fail Criteria:** ✅ Pass: `is_resolved` = True và `note` vẫn 'boom'. ❌ Fail: bị từ chối hoặc `note` bị đổi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-021: Thay đổi task qua hành động Apply Current Settings của SLA Manager

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-06 |
| Coverage Item | CI-4 (Apply Current Settings là đường ghi hợp lệ) |
| Requirement Ref | REQ-SEC-006 (AC2) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-VN (như FX-DEF-STD nhưng schedule_source=definition, schedule_id=FX-CAL-VN).
3. Dựng FX-CAL-VN (fully_fixed, Asia/Ho_Chi_Minh, T2-T6 08:00-17:00, 9 giờ/ngày, không nghỉ trưa).
4. Partner P ref='NEW'. Gọi Engine đánh giá P với now = T0 để có task K (planned_end_time = 2026-03-02 13:00 giờ địa phương). Sau đó đổi duration của FX-DEF-VN từ 4 thành 8.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| now | T0 (chạy ngay lúc 09:00, elapsed = 0) |  |
| User | U-MGR |  |
| Target mới | 8 giờ |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-MGR, gọi hành động Apply Current Settings trên K (hàm hành động, now = T0) | Thành công, không AccessError |
| 2 | Đọc K | duration = 8; business_duration = 0; planned_end_time = 2026-03-02 17:00 giờ địa phương (8 giờ làm việc tính từ 09:00 ngày T2, vừa tới hết ca 17:00) |

**Pass/Fail Criteria:** ✅ Pass: duration = 8 và planned_end_time = 17:00 ngày 2026-03-02. ❌ Fail: Hành động bị từ chối hoặc planned_end_time khác 17:00.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-022: Từ chối group_sla_user đánh dấu event đã xử lý

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-06 |
| Coverage Item | CI-5 (U-USR không có ngoại lệ is_resolved) |
| Requirement Ref | REQ-SEC-006 (Statement: ngoại lệ chỉ cho SLA Manager) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Event E (sudo): event='error', is_resolved=False.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-USR |  |
| Field | is_resolved | False -> True |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-USR, gọi `E.with_user(U-USR).action_mark_resolved()` (đường ghi `is_resolved` duy nhất; gọi `E.write` trực tiếp luôn bị ACL từ chối nên không đủ để chứng minh quy tắc) | Ném `AccessError`; `E.is_resolved` vẫn False (đọc bằng sudo) |
| 2 | Đọc E | is_resolved = False |

**Pass/Fail Criteria:** ✅ Pass: Bị từ chối, giá trị không đổi. ❌ Fail: Ghi thành công.

**Ghi chú:** (TA-34) trước đây `sla.event.action_mark_resolved` ghi bằng `sudo()` và chưa kiểm tra nhóm `group_sla_manager` như `action_reevaluate_batch`; ca viết theo SRS (REQ-SEC-006: U-USR không có ngoại lệ); code đã sửa thêm kiểm quyền (TASKS T13, TA-34 ĐÃ SỬA). Nút trên view đã giới hạn `groups="dwo_sla_core.group_sla_manager"`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-023: Không có thao tác tạo, sửa, xóa trên view của task và event

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-06 |
| Coverage Item | CI-6 (View task và event không có create/edit/delete) |
| Requirement Ref | REQ-SEC-006 (AC1 (qua giao diện)) |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Module đã cài.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-MGR |  |
| View | list và form của sla.task, sla.event | 4 view |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-MGR, `sla.task.get_view(view_type='list')` và `'form'`, phân tích arch | Thuộc tính create, edit, delete đều = '0' (hoặc 'false') trên cả 2 view; không có nút Xóa, không có nút Lưu |
| 2 | Với env của U-MGR, `sla.event.get_view(view_type='list')` và `'form'`, phân tích arch | create và delete = '0'; trường duy nhất sửa được là is_resolved; các field khác readonly |
| 3 | Đọc `ir.model.access` của `sla.task` cho nhóm `group_sla_manager` | `perm_create` = 0, `perm_write` = 0, `perm_unlink` = 0 (chỉ đọc; thay đổi qua các hành động Apply Current Settings, Re-check Conditions) |

**Pass/Fail Criteria:** ✅ Pass: 3 bước đạt. ❌ Fail: Có create/edit/delete khả dụng trên view.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-SEC-024: Người dùng chỉ thuộc `group_sla_user` không tạo được mốc escalation: `AccessError` và không có mốc mới

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-16-01 |
| Coverage Item | CI-6 (U-USR thêm mốc escalation bị từ chối) |
| Requirement Ref | REQ-SEC-001 (AC2, Statement: chỉ Manager sửa escalation) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-USERS: U-MGR (`group_sla_manager`), U-USR (chỉ `group_sla_user`), U-BIZ (chỉ quyền sửa `res.partner`), U-NONE (không quyền SLA); công ty hiện tại CO-A.
2. Module `dwo_sla_core` đã cài; định nghĩa FX-DEF-STD trên `res.partner` (mục tiêu `duration` = 4, `schedule_source` = `none`); chưa có mốc escalation nào.
3. Server action SA-N75 (model `res.partner`): code `record.message_post(body='N75')`.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-USR | `group_sla_user` |
| percent | 90 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Đếm `sla.escalation` của FX-DEF-STD (sudo) | N = 0 |
| 2 | Với env của U-USR, tạo `sla.escalation` {definition_id: FX-DEF-STD, percent: 90, action_id: SA-N75} | Ném `AccessError` (ACL `access_sla_escalation_user` chỉ có quyền đọc) |
| 3 | Đếm `sla.escalation` của FX-DEF-STD (sudo) | = N (không tăng) |

**Pass/Fail Criteria:** ✅ Pass: `AccessError` và số mốc không đổi; ❌ Fail: mốc được tạo hoặc không ném `AccessError`

**Ghi chú:** Ca này trước đây là TC-CHG-014 (TG-11, trace sai sang REQ-FUNC-053 AC3 không tồn tại); chuyển sang TG-16 theo F-M3.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

## TG-17 — Giao diện và báo cáo

### TC-UIX-001: Lưu định nghĩa res.partner với start domain và mục tiêu 4 giờ rồi đọc lại

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-01 |
| Coverage Item | CI-1 (Lưu và mở lại giữ đúng model, start, target) |
| Requirement Ref | REQ-INT-001 (AC1) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS (U-MGR).
2. Không có định nghĩa nào tên 'UI-DEF-1'.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| name | UI-DEF-1 |  |
| model | res.partner |  |
| start_domain | [('is_company', '=', True)] | chuỗi chính xác |
| duration | 4 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với U-MGR, mô phỏng form mới (`odoo.tests.Form`): chọn model res.partner, nhập name, start_domain, duration rồi lưu | Lưu thành công, tạo 1 bản ghi |
| 2 | Đọc lại bản ghi từ database (invalidate cache) | model_name = 'res.partner'; start_domain = "[('is_company', '=', True)]"; duration = 4.0 |

**Pass/Fail Criteria:** ✅ Pass: Ba giá trị đọc lại đúng. ❌ Fail: Giá trị đọc lại khác hoặc lưu lỗi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-002: Form định nghĩa chỉ đọc với group_sla_user

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-01 |
| Coverage Item | CI-2 (U-USR không sửa được form) |
| Requirement Ref | REQ-INT-001 (AC2) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS (U-USR).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-USR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env của U-USR kiểm `sla.definition.has_access('write')` | False |
| 2 | Với env của U-USR, `get_view(view_type='form')` của sla.definition, kiểm quyền hiệu lực (`access_rights` hoặc kết quả `check_access`) | Mọi field sửa được bị chặn bởi quyền ghi False; không có quyền create nên không có nút Lưu mới |
| 3 | Mở bản ghi form qua `Form` bởi U-USR rồi thử đặt `name` | Ném lỗi (field readonly hoặc AccessError) |

**Pass/Fail Criteria:** ✅ Pass: 3 bước đạt. ❌ Fail: has_access('write') = True hoặc đặt được name.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-003: Trình diễn bố cục form định nghĩa SLA

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-01 |
| Coverage Item | CI-3 (Form đủ thành phần cấu hình) |
| Requirement Ref | REQ-INT-001 (Statement) |
| Priority | P2-High |
| Test Type | Demonstration |
| Automation | Manual |

**Preconditions:**
1. Môi trường: database sla_test đã cài dwo_sla_core và dwo_sla_demo_ticket (FX-DEMO), trình duyệt đăng nhập được bằng tài khoản của FX-USERS.
2. Đăng nhập U-MGR.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Màn hình | Menu SLA > Định nghĩa > Tạo mới |  |
| Người kiểm | QA |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Mở form mới, chọn model `res.partner` | Field chọn model có; thay đổi model không báo lỗi |
| 2 | Mở 6 điều kiện start, cancel, pause, resume, stop, reset | Mỗi điều kiện có công cụ chọn domain, field gợi ý thuộc res.partner |
| 3 | Nhập mục tiêu 4 | Field thời lượng mục tiêu nhận số |
| 4 | Mở field nguồn lịch | Có 3 giá trị none, definition, record |
| 5 | Tìm danh sách escalation trên form | Có danh sách nội tuyến, thêm dòng ngay trên form |
| 6 | Lưu form | Lưu được, không lỗi |

**Pass/Fail Criteria:** ✅ Pass: 6 mục đạt, QA ký biên bản Demonstration. ❌ Fail: Thiếu thành phần hoặc lỗi hiển thị.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-004: Kiểm help của điều kiện start và pause nêu đủ ba cảnh báo

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-02 |
| Coverage Item | CI-1 (Help start và pause có 3 cảnh báo) |
| Requirement Ref | REQ-INT-002 (AC1) |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. Môi trường: database sla_test đã cài dwo_sla_core và dwo_sla_demo_ticket (FX-DEMO), trình duyệt đăng nhập được bằng tài khoản của FX-USERS.
2. Đăng nhập U-MGR; mở form định nghĩa (bất kỳ model, ví dụ res.partner).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Field kiểm | start_domain, pause_domain |  |
| Ba cảnh báo | (1) start là tập con của stop; (2) pause là tập con của start; (3) start và pause loại trừ nhau |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Rê chuột vào dấu ? của điều kiện start, đọc help | Có ý (1) start là tập con của stop |
| 2 | Tiếp tục đọc help start | Có ý (2) pause là tập con của start và ý (3) start và pause loại trừ nhau |
| 3 | Rê chuột vào dấu ? của điều kiện pause | Có đủ ý (1), (2), (3) |
| 4 | Đối chiếu với `fields_get` help của 2 field (nếu có shell) | Văn bản khớp giao diện |

**Pass/Fail Criteria:** ✅ Pass: Hai help đều chứa đủ 3 ý. ❌ Fail: Thiếu ít nhất 1 ý ở một help.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-005: Kiểm help của điều kiện cancel và resume không chứa cảnh báo

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-02 |
| Coverage Item | CI-2 (Help cancel và resume sạch) |
| Requirement Ref | REQ-INT-002 (AC2) |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. Môi trường: database sla_test đã cài dwo_sla_core và dwo_sla_demo_ticket (FX-DEMO), trình duyệt đăng nhập được bằng tài khoản của FX-USERS.
2. Đăng nhập U-MGR; mở form định nghĩa (bất kỳ model, ví dụ res.partner).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Field kiểm | cancel_domain, resume_domain |  |
| Từ khóa cấm | 'tập con', 'loại trừ' |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Rê chuột vào dấu ? của điều kiện cancel, đọc help | Không có ý 'tập con' hay 'loại trừ' |
| 2 | Rê chuột vào dấu ? của điều kiện resume, đọc help | Không có ý 'tập con' hay 'loại trừ' |
| 3 | Lặp với form của một model khác (ví dụ demo.ticket) | Kết quả giống |

**Pass/Fail Criteria:** ✅ Pass: Cả 2 help không chứa cảnh báo ở cả 2 model. ❌ Fail: Có cảnh báo nhiễu.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-006: Trình diễn hiển thị help của start và pause trên giao diện

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-02 |
| Coverage Item | CI-3 (Help hiện ra trên giao diện) |
| Requirement Ref | REQ-INT-002 (AC1 (hiển thị)) |
| Priority | P3-Medium |
| Test Type | Demonstration |
| Automation | Manual |

**Preconditions:**
1. Môi trường: database sla_test đã cài dwo_sla_core và dwo_sla_demo_ticket (FX-DEMO), trình duyệt đăng nhập được bằng tài khoản của FX-USERS.
2. Đăng nhập U-MGR; mở form định nghĩa (bất kỳ model, ví dụ res.partner).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Trình duyệt | Chrome bản hiện hành, độ rộng 1366 px |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Rê chuột vào dấu ? của start | Tooltip hiện trong 1 giây, không bị cắt chữ |
| 2 | Rê chuột vào dấu ? của pause | Tooltip hiện, không bị cắt chữ |
| 3 | Chuyển ngôn ngữ giao diện sang ja_JP nếu có bản dịch | Văn bản vẫn hiện (không rỗng) |

**Pass/Fail Criteria:** ✅ Pass: 3 mục đạt. ❌ Fail: Tooltip không hiện hoặc bị cắt.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-007: Trình diễn ghi chú lịch dự phòng khi nguồn lịch là record

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-03 |
| Coverage Item | CI-1 (Ghi chú hiện khi source=record) |
| Requirement Ref | REQ-INT-003 (AC1) |
| Priority | P3-Medium |
| Test Type | Demonstration |
| Automation | Manual |

**Preconditions:**
1. Môi trường: database sla_test đã cài dwo_sla_core và dwo_sla_demo_ticket (FX-DEMO), trình duyệt đăng nhập được bằng tài khoản của FX-USERS.
2. Đăng nhập U-MGR; form định nghĩa mới.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| schedule_source | record |  |
| Nội dung cần có | (1) không lấy được lịch thì dùng lịch làm việc mặc định của công ty; (2) nếu cũng không dùng được thì chạy 24x7 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Chọn nguồn lịch = record | Ghi chú xuất hiện ngay (không cần lưu) |
| 2 | Kiểm màu và vị trí | Nền cảnh báo màu vàng; nằm ngay dưới field nguồn lịch, trên field đường dẫn lịch |
| 3 | Đọc nội dung | Nêu (1) rồi (2) đúng thứ tự |

**Pass/Fail Criteria:** ✅ Pass: 3 mục đạt. ❌ Fail: Không hiện, sai màu, sai vị trí hoặc thiếu một bước.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-008: Trình diễn ghi chú ẩn khi nguồn lịch là none hoặc definition

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-03 |
| Coverage Item | CI-2 (Ghi chú ẩn khi source khác record) |
| Requirement Ref | REQ-INT-003 (AC2) |
| Priority | P3-Medium |
| Test Type | Demonstration |
| Automation | Manual |

**Preconditions:**
1. Môi trường: database sla_test đã cài dwo_sla_core và dwo_sla_demo_ticket (FX-DEMO), trình duyệt đăng nhập được bằng tài khoản của FX-USERS.
2. Đăng nhập U-MGR; form định nghĩa mới.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| schedule_source | none rồi definition |  |
| Chuyển lại | record rồi none |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Chọn nguồn lịch = none | Không có ghi chú |
| 2 | Chọn nguồn lịch = definition | Không có ghi chú |
| 3 | Chọn lại record rồi none | Ghi chú hiện ở record, ẩn lại ở none |

**Pass/Fail Criteria:** ✅ Pass: 3 mục đạt. ❌ Fail: Ghi chú hiện ở none hoặc definition.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-009: Kiểm arch form: ghi chú chỉ hiện khi schedule_source là record

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-03 |
| Coverage Item | CI-3 (Arch có ghi chú điều kiện theo schedule_source) |
| Requirement Ref | REQ-INT-003 (AC1, AC2) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS (U-MGR).
2. Module đã cài.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| View | form sla.definition | get_view bởi U-MGR |
| Từ khóa | 'mặc định', '24x7' |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env U-MGR, lấy arch `sla.definition.get_view(view_type='form')` và tìm phần tử có class alert-warning cạnh field schedule_source (view `sla_definition_views.xml` dùng `<div class="alert alert-warning" invisible="schedule_source != 'record'">`) | Có đúng 1 phần tử |
| 2 | Đọc điều kiện ẩn của phần tử | Ẩn khi schedule_source khác 'record' (biểu thức tham chiếu schedule_source) |
| 3 | Đọc nội dung văn bản | Chứa cả 'mặc định' (lịch làm việc mặc định của công ty) và '24x7' |

**Pass/Fail Criteria:** ✅ Pass: 3 mục đạt. ❌ Fail: Không có phần tử, điều kiện sai hoặc thiếu nội dung.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-010: Hiển thị danh sách task với các trường tối thiểu cho SLA User

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-04 |
| Coverage Item | CI-1 (List task có đủ cột và dòng của task) |
| Requirement Ref | REQ-INT-004 (AC1) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS (U-USR).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Partner P ref='NEW'; task K (sudo) stage='in_progress', start_time=T0, planned_end_time=T0+4h (13:00 giờ địa phương), business_duration=0, duration=4, has_breached=False.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-USR |  |
| Field bắt buộc trên list | res_id/record gốc, definition_id, stage, start_time, planned_end_time, end_time, business_duration, duration, has_breached | 9 mục |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env U-USR, `sla.task.get_view(view_type='list')`, đếm trong arch 9 field bắt buộc | Cả 9 field có trong arch (đếm = 9) |
| 2 | Với env U-USR, `search_read([('id','=',K.id)], 9 field)` | Trả 1 dòng: stage='in_progress', duration=4.0, planned_end_time = 2026-03-02 13:00 giờ địa phương, business_duration=0.0, has_breached=False, definition_id=FX-DEF-STD |

**Pass/Fail Criteria:** ✅ Pass: Arch đủ 9 field và dòng đọc đúng. ❌ Fail: Thiếu field hoặc giá trị sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-011: Không có thao tác sửa hoặc xóa trên form task với SLA Manager

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-04 |
| Coverage Item | CI-2 (Form task chỉ đọc cho U-MGR) |
| Requirement Ref | REQ-INT-004 (AC2) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS (U-MGR).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Task K (sudo) in_progress cho partner P.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-MGR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env U-MGR, `sla.task.get_view(view_type='form')`, đọc thuộc tính edit, create, delete của phần tử form | edit='0', create='0', delete='0' |
| 2 | Tìm nút Xóa, Lưu trong arch | Không có |
| 3 | Với env U-MGR kiểm `has_access('write')`, `has_access('create')`, `has_access('unlink')` trên sla.task | Cả 3 = False |

**Pass/Fail Criteria:** ✅ Pass: 3 bước đạt. ❌ Fail: Có thao tác sửa hoặc xóa khả dụng.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-012: Trình diễn danh sách và form chi tiết task SLA ở chế độ chỉ đọc

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-04 |
| Coverage Item | CI-3 (List và form task hiển thị đủ, chỉ đọc) |
| Requirement Ref | REQ-INT-004 (AC1, AC2) |
| Priority | P2-High |
| Test Type | Demonstration |
| Automation | Manual |

**Preconditions:**
1. Môi trường: database sla_test đã cài dwo_sla_core và dwo_sla_demo_ticket (FX-DEMO), trình duyệt đăng nhập được bằng tài khoản của FX-USERS.
2. Có ít nhất 1 task in_progress của FX-DEMO; đăng nhập U-USR rồi U-MGR.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Màn hình | Menu SLA > Task SLA |  |
| Cột tối thiểu | Record gốc, Định nghĩa, Stage, start_time, planned_end_time, end_time, Thời gian đã trôi, Mục tiêu, Dấu vi phạm | 9 cột |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | U-USR mở danh sách task | Thấy dòng task với đủ 9 cột, thời gian hiển thị theo múi giờ người dùng |
| 2 | Mở form chi tiết một task | Mọi field ở chế độ chỉ đọc |
| 3 | Đăng nhập U-MGR, mở form task | Không có nút Sửa, Xóa, Lưu; có nút Apply Current Settings và Re-check Conditions |
| 4 | Chọn nhiều dòng trên danh sách (U-MGR) | Không có hành động Xóa trong menu Action |

**Pass/Fail Criteria:** ✅ Pass: 4 mục đạt. ❌ Fail: Thiếu cột hoặc có nút sửa/xóa.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-013: Action SLA trên partner chỉ hiện task của chính partner đang chọn

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-05 |
| Coverage Item | CI-1 (Action SLA lọc theo record) |
| Requirement Ref | REQ-INT-006 (AC1) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Module dwo_sla_core đã cài; action 'SLA' là `ir.actions.act_window` có `binding_model_id` trỏ tới model của định nghĩa, domain `[('res_model','=','<model>'),('res_id','=',active_id)]`, `group_ids` = `group_sla_user`, do `sla.definition._register_sla_action_binding` tạo/xóa theo tập định nghĩa.
3. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
4. Partner P và Q (ref='NEW'). Hai định nghĩa D1 (FX-DEF-STD) và D2 (như D1, name='D2'); task của P: K1 (D1) và K2 (D2), stage='in_progress'; task của Q: K3 (D1).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-USR |  |
| active_id | P.id |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env U-USR, lấy danh sách action gắn vào res.partner (`ir.actions.actions.get_bindings('res.partner')`) | Có action tên 'SLA' |
| 2 | Chạy action với context active_model='res.partner', active_id=P.id, rồi `search` theo domain trả về | Kết quả = {K1, K2} (đếm = 2); K3 không có |

**Pass/Fail Criteria:** ✅ Pass: Đếm = 2 và đúng id. ❌ Fail: Thấy K3 hoặc thiếu action.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-014: Giữ action SLA khi định nghĩa cuối đã archive nhưng còn task đang chạy

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-05 |
| Coverage Item | CI-2 (Action còn khi còn task đang hoạt động) |
| Requirement Ref | REQ-INT-006 (AC2) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Module dwo_sla_core đã cài; action 'SLA' là `ir.actions.act_window` có `binding_model_id` trỏ tới model của định nghĩa, domain `[('res_model','=','<model>'),('res_id','=',active_id)]`, `group_ids` = `group_sla_user`, do `sla.definition._register_sla_action_binding` tạo/xóa theo tập định nghĩa.
3. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng). Là định nghĩa duy nhất của res.partner.
4. Partner P có 1 task in_progress.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Thao tác | D.active = False | archive định nghĩa cuối |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Archive định nghĩa (D.write({'active': False})) bằng U-MGR | Không ném lỗi; `D.active` = False; số task hoạt động của P vẫn = 1 |
| 2 | Với env U-USR, `get_bindings('res.partner')` | Vẫn có action 'SLA' |

**Pass/Fail Criteria:** ✅ Pass: Action còn. ❌ Fail: Action biến mất khi còn task đang chạy.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-015: Gỡ action SLA khi không còn định nghĩa bật và không còn task hoạt động

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-05 |
| Coverage Item | CI-3 (Action biến mất khi hết cả hai) |
| Requirement Ref | REQ-INT-006 (AC3) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Module dwo_sla_core đã cài; action 'SLA' là `ir.actions.act_window` có `binding_model_id` trỏ tới model của định nghĩa, domain `[('res_model','=','<model>'),('res_id','=',active_id)]`, `group_ids` = `group_sla_user`, do `sla.definition._register_sla_action_binding` tạo/xóa theo tập định nghĩa.
3. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng). Là định nghĩa duy nhất của res.partner.
4. Partner P có 1 task stage='achieved' (không hoạt động); không có task in_progress hay paused.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Thao tác | D.active = False |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Archive định nghĩa bằng U-MGR | Không ném lỗi; `D.active` = False; P không có task `in_progress` hay `paused` |
| 2 | Với env U-USR, `get_bindings('res.partner')` | Không còn action tên 'SLA' |
| 3 | Bật lại D.active = True, lấy lại bindings (đối chứng) | Action 'SLA' xuất hiện lại |

**Pass/Fail Criteria:** ✅ Pass: Bước 2 và 3 đúng. ❌ Fail: Action còn sau khi archive.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-016: Ẩn action SLA với người dùng không thuộc nhóm SLA

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-05 |
| Coverage Item | CI-4 (U-NONE không thấy action) |
| Requirement Ref | REQ-INT-006 (AC4) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Module dwo_sla_core đã cài; action 'SLA' là `ir.actions.act_window` có `binding_model_id` trỏ tới model của định nghĩa, domain `[('res_model','=','<model>'),('res_id','=',active_id)]`, `group_ids` = `group_sla_user`, do `sla.definition._register_sla_action_binding` tạo/xóa theo tập định nghĩa.
3. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
4. Partner P có 1 task in_progress.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-NONE |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env U-NONE, `get_bindings('res.partner')` | Không có action 'SLA' |
| 2 | Với env U-USR, `get_bindings('res.partner')` | Có action 'SLA' (đối chứng) |

**Pass/Fail Criteria:** ✅ Pass: Hai bước đạt. ❌ Fail: U-NONE thấy action.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-017: Trình diễn action SLA trong menu Action của form partner

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-05 |
| Coverage Item | CI-5 (Action SLA trên giao diện) |
| Requirement Ref | REQ-INT-006 (AC1, AC4 (hiển thị)) |
| Priority | P3-Medium |
| Test Type | Demonstration |
| Automation | Manual |

**Preconditions:**
1. Môi trường: database sla_test đã cài dwo_sla_core và dwo_sla_demo_ticket (FX-DEMO), trình duyệt đăng nhập được bằng tài khoản của FX-USERS.
2. Dữ liệu dựng trong ca: partner P và Q (`ref` = 'NEW'); hai định nghĩa D1 (FX-DEF-STD) và D2 (như D1, name = 'D2'); task `in_progress` của P: K1 (D1) và K2 (D2); task của Q: K3 (D1).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-USR rồi U-NONE |  |
| Màn hình | Form res.partner của P |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | U-USR mở form P, bấm menu Action (biểu tượng bánh răng) | Có mục 'SLA' |
| 2 | Chọn 'SLA' | Danh sách hiển thị đúng 2 task của P |
| 3 | U-NONE mở form P, bấm menu Action | Không có mục 'SLA' |
| 4 | Nếu cơ chế lọc theo record không khả dụng (spike) | Ghi nhận phương án dự phòng: menu SLA kèm bộ lọc theo record, chạy lại bước 2 |

**Pass/Fail Criteria:** ✅ Pass: Bước 1 đến 3 đạt (bước 4 chỉ khi dùng phương án dự phòng). ❌ Fail: Thiếu action hoặc lọc sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-018: Lọc trạng thái trả đúng 2, 1, 2 trên bộ dữ liệu hỗn hợp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-06 |
| Coverage Item | CI-1 (Ba bộ lọc trả đúng số task) |
| Requirement Ref | REQ-INT-011 (AC1) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Mỗi task do sudo tạo trên partner riêng (chỉ mục duy nhất chỉ cho 1 task hoạt động mỗi (định nghĩa, record)), definition_id=FX-DEF-STD, res_model='res.partner', start_time=FX-T0, duration=4.
4. Tạo 5 task: A1 và A2 stage='in_progress' (has_breached=False); B stage='paused' (has_breached=False, pause_time=T0+1h); C stage='breached' (has_breached=True, end_time=T0+5h); D stage='achieved' (has_breached=True, end_time=T0+3h).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-USR |  |
| Bộ lọc | Đang chạy; Tạm dừng; Đã vi phạm | lấy domain từ search view sla.task |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env U-USR, áp domain bộ lọc 'Đang chạy' (`search_count`) | = 2 (A1, A2) |
| 2 | Áp bộ lọc 'Tạm dừng' | = 1 (B) |
| 3 | Áp bộ lọc 'Đã vi phạm' | = 2 (C, D; bất kể stage) |

**Pass/Fail Criteria:** ✅ Pass: Ba số đếm 2, 1, 2. ❌ Fail: Số đếm sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-019: Bộ lọc rỗng không gây lỗi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-06 |
| Coverage Item | CI-2 (Bộ lọc không có kết quả trả rỗng) |
| Requirement Ref | REQ-INT-011 (AC2) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Chỉ có 1 task stage='achieved', has_breached=False (không thỏa cả 3 bộ lọc).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-USR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Áp lần lượt 3 bộ lọc Đang chạy, Tạm dừng, Đã vi phạm bằng `search` | Mỗi lần trả recordset rỗng (đếm = 0), không ném lỗi |

**Pass/Fail Criteria:** ✅ Pass: Ba lần trả 0. ❌ Fail: Ném lỗi hoặc trả dòng.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-020: Lọc Sắp đến hạn với X = 6 trả 2 trong 3 task

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-07 |
| Coverage Item | CI-1 (Bộ lọc theo X) |
| Requirement Ref | REQ-INT-012 (AC1) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Mỗi task do sudo tạo trên partner riêng (chỉ mục duy nhất chỉ cho 1 task hoạt động mỗi (định nghĩa, record)), definition_id=FX-DEF-STD, res_model='res.partner', start_time=FX-T0, duration=4.
4. Tham số X (`dwo_sla_core.due_soon_hours`) = 6.
5. now_real = thời điểm thật lấy một lần ở đầu ca (`fields.Datetime.now()`); các mốc tạo dữ liệu tính tương đối so với now_real; bộ lọc đánh giá theo đồng hồ thật nên mọi mốc cách biên tối thiểu 1 phút.
6. 3 task in_progress, has_breached=False: T1 planned_end_time=now_real+1h; T2 planned_end_time=now_real+5h; T3 planned_end_time=now_real+3 ngày.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| X | 6 | giờ |
| Người dùng | U-USR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Áp bộ lọc 'Sắp đến hạn' bởi U-USR | Kết quả = {T1, T2} (đếm = 2); T3 không có |

**Pass/Fail Criteria:** ✅ Pass: Đúng {T1, T2}. ❌ Fail: Sai tập kết quả.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-021: Kiểm biên X = 6 giờ của bộ lọc Sắp đến hạn: planned_end_time đúng now + 6h có mặt, now + 6h + 1 giây vắng mặt

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-07 |
| Coverage Item | CI-2 (Biên planned_end_time quanh now + X) |
| Requirement Ref | REQ-INT-012 (AC1 (biên)) |
| Priority | P3-Medium |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Mỗi task do sudo tạo trên partner riêng (chỉ mục duy nhất chỉ cho 1 task hoạt động mỗi (định nghĩa, record)), definition_id=FX-DEF-STD, res_model='res.partner', start_time=FX-T0, duration=4.
4. Tham số X (`dwo_sla_core.due_soon_hours`) = 6.
5. `odoo.fields.Datetime.now` được patch trả NOW = 2026-03-02 10:00:00 UTC cố định; bộ lọc 'Sắp đến hạn' (`sla.task._search_is_due_soon`) đọc đồng hồ qua hàm này nên biên được kiểm chính xác đến giây.
6. 3 task in_progress, has_breached=False: E1 planned_end_time = NOW - 10 phút (đã quá hạn nhưng chưa bật cờ: thuộc kết quả vì bộ lọc không có chặn dưới, theo Statement và `_search_is_due_soon`); E2 planned_end_time = NOW + 6h (đúng biên, so sánh `<=`); E3 planned_end_time = NOW + 6h + 1 giây.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| X | 6 |  |
| Biên | NOW + 6h, so sánh `<=` (bao gồm) |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Áp bộ lọc 'Sắp đến hạn' bởi U-USR | Kết quả = {E1, E2}; E3 không có |

**Pass/Fail Criteria:** ✅ Pass: Đúng {E1, E2}. ❌ Fail: E3 có mặt hoặc E2 (đúng biên) vắng mặt.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-022: Loại paused, achieved, đã vi phạm khỏi bộ lọc Sắp đến hạn

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-07 |
| Coverage Item | CI-3 (Task ngoài lớp không xuất hiện) |
| Requirement Ref | REQ-INT-012 (AC2) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Mỗi task do sudo tạo trên partner riêng (chỉ mục duy nhất chỉ cho 1 task hoạt động mỗi (định nghĩa, record)), definition_id=FX-DEF-STD, res_model='res.partner', start_time=FX-T0, duration=4.
4. Tham số X (`dwo_sla_core.due_soon_hours`) = 6.
5. now_real = thời điểm thật lấy một lần ở đầu ca (`fields.Datetime.now()`); các mốc tạo dữ liệu tính tương đối so với now_real; bộ lọc đánh giá theo đồng hồ thật nên mọi mốc cách biên tối thiểu 1 phút.
6. 3 task, cùng planned_end_time=now_real+1h: N1 stage='paused'; N2 stage='achieved', end_time=now_real-1h; N3 stage='in_progress' có has_breached=True.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| X | 6 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Áp bộ lọc 'Sắp đến hạn' bởi U-USR | Kết quả rỗng (đếm = 0) |

**Pass/Fail Criteria:** ✅ Pass: Đếm = 0. ❌ Fail: Một trong N1, N2, N3 xuất hiện.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-023: Đổi X từ 6 xuống 1 thu hẹp kết quả bộ lọc

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-07 |
| Coverage Item | CI-4 (SLA Manager đổi X) |
| Requirement Ref | REQ-INT-012 (AC3) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Mỗi task do sudo tạo trên partner riêng (chỉ mục duy nhất chỉ cho 1 task hoạt động mỗi (định nghĩa, record)), definition_id=FX-DEF-STD, res_model='res.partner', start_time=FX-T0, duration=4.
4. Tham số X (`dwo_sla_core.due_soon_hours`) = 6.
5. now_real = thời điểm thật lấy một lần ở đầu ca (`fields.Datetime.now()`); các mốc tạo dữ liệu tính tương đối so với now_real; bộ lọc đánh giá theo đồng hồ thật nên mọi mốc cách biên tối thiểu 1 phút.
6. 2 task in_progress, has_breached=False: F1 planned_end_time=now_real+30 phút; F2 planned_end_time=now_real+5h.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| X cũ | 6 |  |
| X mới | 1 | do U-MGR đặt |
| Người dùng | U-MGR rồi U-USR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Áp bộ lọc ở X = 6 | Kết quả = {F1, F2} |
| 2 | U-MGR đặt X = 1 qua màn hình cấu hình SLA (`res.config.settings`, field `sla_due_soon_hours`) và Lưu | Tham số `dwo_sla_core.due_soon_hours` = '1' |
| 3 | Áp lại bộ lọc bởi U-USR | Kết quả = {F1}; F2 không có |

**Pass/Fail Criteria:** ✅ Pass: Ba bước đạt. ❌ Fail: Kết quả không đổi sau khi đổi X.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-024: Giá trị mặc định của X là 4 giờ

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-07 |
| Coverage Item | CI-5 (Mặc định 4) |
| Requirement Ref | REQ-INT-012 (Statement (mặc định 4, O-04)) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Mỗi task do sudo tạo trên partner riêng (chỉ mục duy nhất chỉ cho 1 task hoạt động mỗi (định nghĩa, record)), definition_id=FX-DEF-STD, res_model='res.partner', start_time=FX-T0, duration=4.
4. Xóa tham số `dwo_sla_core.due_soon_hours` khỏi ir.config_parameter nếu có (module mới cài, chưa chỉnh). now_real = thời điểm thật lấy một lần ở đầu ca (`fields.Datetime.now()`); các mốc tạo dữ liệu tính tương đối so với now_real; bộ lọc đánh giá theo đồng hồ thật nên mọi mốc cách biên tối thiểu 1 phút.
5. 2 task in_progress, has_breached=False: G1 planned_end_time=now_real+3h; G2 planned_end_time=now_real+5h.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| X | mặc định 4 | đề xuất O-04 |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Đọc giá trị X hiệu lực (màn hình cấu hình hoặc get_param với default của module) | = 4 |
| 2 | Áp bộ lọc 'Sắp đến hạn' bởi U-USR | Kết quả = {G1}; G2 không có |

**Pass/Fail Criteria:** ✅ Pass: X = 4 và kết quả {G1}. ❌ Fail: X khác 4.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-025: Từ chối group_sla_user chỉnh X

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-07 |
| Coverage Item | CI-6 (U-USR không đổi được X) |
| Requirement Ref | REQ-INT-012 (Statement (chỉ SLA Manager)) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. X = 4.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-USR |  |
| X thử đặt | 1 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env U-USR, ghi X qua màn hình cấu hình (`res.config.settings` field `sla_due_soon_hours` = 1, `execute()`) | Ném AccessError |
| 2 | Đọc tham số X | Vẫn 4 |

**Pass/Fail Criteria:** ✅ Pass: Bị từ chối và X vẫn 4. ❌ Fail: X bị đổi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-026: Nhóm task theo định nghĩa cho 2 nhóm số lượng 3 và 2

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-08 |
| Coverage Item | CI-1 (Nhóm theo definition_id) |
| Requirement Ref | REQ-INT-013 (AC1) |
| Priority | P4-Low |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng). Là D1. Thêm D2 (cùng cấu hình, name='D2').
3. 5 partner P1..P5 (ref='NEW'); task in_progress: 3 của D1 (P1, P2, P3), 2 của D2 (P4, P5).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-USR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env U-USR, `sla.task.read_group([], ['definition_id'], ['definition_id'])` (hoặc `_read_group`) | Có 2 nhóm: D1 với count = 3, D2 với count = 2 |

**Pass/Fail Criteria:** ✅ Pass: Hai nhóm 3 và 2. ❌ Fail: Số nhóm hoặc số lượng sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-027: Nhóm task theo model và theo stage

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-08 |
| Coverage Item | CI-2 (Nhóm theo res_model và stage) |
| Requirement Ref | REQ-INT-013 (Statement (nhóm model, stage)) |
| Priority | P4-Low |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Dữ liệu dựng trong ca: D1 (FX-DEF-STD) và D2 (như D1, name = 'D2'); 5 partner P1..P5 (`ref` = 'NEW'); task `in_progress`: 3 của D1 (P1, P2, P3), 2 của D2 (P4, P5); thêm partner P6 có 1 task `paused` (D1) và 1 task thuộc `res_model` = 'demo.ticket' của FX-DEMO (`in_progress`).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-USR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Nhóm theo res_model | 2 nhóm: res.partner = 6, demo.ticket = 1 |
| 2 | Nhóm theo stage | 2 nhóm: in_progress = 6, paused = 1 |

**Pass/Fail Criteria:** ✅ Pass: Cả 2 phép nhóm đúng. ❌ Fail: Sai số nhóm hoặc số lượng.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-028: Trình diễn chế độ xem pivot và graph của task SLA

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-08 |
| Coverage Item | CI-3 (Pivot và graph mở được, tổng khớp danh sách) |
| Requirement Ref | REQ-INT-013 (AC2) |
| Priority | P4-Low |
| Test Type | Demonstration |
| Automation | Manual |

**Preconditions:**
1. Môi trường: database sla_test đã cài dwo_sla_core và dwo_sla_demo_ticket (FX-DEMO), trình duyệt đăng nhập được bằng tài khoản của FX-USERS.
2. Dữ liệu dựng trong ca: D1 (FX-DEF-STD) và D2 (như D1, name = 'D2'); 5 partner P1..P5 (`ref` = 'NEW'); task `in_progress`: 3 của D1 (P1..P3), 2 của D2 (P4, P5); đăng nhập U-USR.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Màn hình | Menu SLA > Task SLA |  |
| Tổng kỳ vọng | 5 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Nhóm theo Định nghĩa trên danh sách | 2 nhóm, số 3 và 2 |
| 2 | Chuyển sang chế độ Pivot | Hiển thị, không lỗi; tổng cột = 5 |
| 3 | Chuyển sang chế độ Graph | Hiển thị biểu đồ, không lỗi; tổng các cột = 5 |
| 4 | Nhóm theo Model rồi theo Stage ở danh sách | Có tùy chọn nhóm, hiển thị đúng |
| 5 | Mở console trình duyệt | Không có lỗi JavaScript |

**Pass/Fail Criteria:** ✅ Pass: 5 mục đạt. ❌ Fail: Có lỗi hoặc tổng khác 5.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-029: Đếm task của record và mở danh sách task qua nút

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-09 |
| Coverage Item | CI-1 (Số và action của nút đúng) |
| Requirement Ref | REQ-INT-014 (AC1) |
| Priority | P4-Low |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. FX-DEMO (phụ thuộc module demo, TA-15): model demo.ticket kế thừa sla.mixin. Ticket TK1 có 2 task (sudo, stage='in_progress' và 'achieved'); ticket TK2 có 1 task.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-USR |  |
| Field đếm | `sla_task_count` | field của `sla.mixin` |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env U-USR, đọc `TK1.sla_task_count` | = 2 |
| 2 | Gọi hàm của nút (`TK1.action_view_sla_tasks()` của `sla.mixin`) rồi search theo domain action | Đúng 2 task của TK1 (đếm = 2) |
| 3 | Đọc `TK2.sla_task_count` | = 1 |

**Pass/Fail Criteria:** ✅ Pass: Ba bước đúng. ❌ Fail: Đếm hoặc tập task sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-030: Trình diễn nút số task SLA trên form record

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-09 |
| Coverage Item | CI-2 (Nút hiện số 2 và mở danh sách) |
| Requirement Ref | REQ-INT-014 (AC1) |
| Priority | P4-Low |
| Test Type | Demonstration |
| Automation | Manual |

**Preconditions:**
1. Môi trường: database sla_test đã cài dwo_sla_core và dwo_sla_demo_ticket (FX-DEMO), trình duyệt đăng nhập được bằng tài khoản của FX-USERS.
2. Dữ liệu dựng trong ca: `demo.ticket` kế thừa `sla.mixin`; ticket TK1 có 2 task (stage `in_progress` và `achieved`), TK2 có 1 task; đăng nhập U-USR.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Màn hình | Form demo.ticket TK1 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Mở form TK1 | Có nút thông minh (stat button) nhãn SLA hiển thị số 2 |
| 2 | Kiểm vị trí | Nằm trong khu nút thông minh trên đầu form, cùng hàng với các nút khác |
| 3 | Bấm nút | Mở danh sách 2 task của TK1 |
| 4 | Mở form TK2 (1 task) | Nút hiện số 1 |

**Pass/Fail Criteria:** ✅ Pass: 4 mục đạt. ❌ Fail: Nút không hiện hoặc số sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-031: Ẩn nút số task SLA với người dùng không thuộc nhóm SLA

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-09 |
| Coverage Item | CI-3 (Nút ẩn với U-NONE) |
| Requirement Ref | REQ-INT-014 (AC2) |
| Priority | P4-Low |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. FX-DEMO: demo.ticket với sla.mixin; U-NONE và U-USR đều có quyền đọc demo.ticket.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-NONE và U-USR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env U-NONE, `demo.ticket.get_view(view_type='form')`, tìm nút/stat button SLA trong arch | Không có (đếm = 0) |
| 2 | Với env U-USR, cùng lệnh | Có đúng 1 nút SLA |

**Pass/Fail Criteria:** ✅ Pass: Hai bước đạt. ❌ Fail: U-NONE có nút.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-032: Đánh giá lại kết thúc task khi điều kiện stop qua quan hệ đã khớp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-10 |
| Coverage Item | CI-1 (Đánh giá lại kéo task về achieved) |
| Requirement Ref | REQ-INT-020 (AC1) |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng định nghĩa FX-DEF-STD nhưng stop_domain=[('parent_id.ref','=','DONE')] (điều kiện qua quan hệ, giới hạn REQ-FUNC-042). start ref in NEW/WORK.
3. Partner mẹ PM (ref='NEW'); partner con PC (parent_id=PM, ref='WORK'); Engine đã gắn task K in_progress cho PC (start_time=T0).
4. Đổi PM.ref='DONE' bằng quyền hệ thống: task K vẫn in_progress (giới hạn REQ-FUNC-042, xác nhận ở bước 1).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| now | T0 + 2h = 11:00 giờ địa phương |  |
| Người dùng | U-MGR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Đọc K.stage | 'in_progress' (tiền đề) |
| 2 | Với patch `odoo.fields.Datetime.now` trả T0 + 2h, U-MGR gọi `action_reevaluate()` (nút 'Re-evaluate') trên task của K | Không ném lỗi |
| 3 | Đọc K | stage = 'achieved'; end_time = 2026-03-02 11:00 giờ địa phương; business_duration = 2.0 |
| 4 | Đếm event 'complete' của K | = 1 |

**Pass/Fail Criteria:** ✅ Pass: Bốn bước đạt. ❌ Fail: K không kết thúc hoặc end_time sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-033: Từ chối group_sla_user dùng Re-check Conditions

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-10 |
| Coverage Item | CI-2 (U-USR không có nút Re-check Conditions) |
| Requirement Ref | REQ-INT-020 (AC2) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Task K in_progress cho partner P.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-USR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env U-USR, `get_view(view_type='form')` của sla.task, tìm nút 'Re-check Conditions' | Không có (đếm = 0) |
| 2 | Với env U-USR, gọi hàm hành động Re-check Conditions trên K | Ném AccessError |
| 3 | Với env U-MGR, arch cùng view (đối chứng) | Có nút 'Re-check Conditions' |

**Pass/Fail Criteria:** ✅ Pass: Ba bước đạt. ❌ Fail: U-USR thấy hoặc gọi được.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-034: Đánh giá lại task đã achieved không làm đổi task

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-10 |
| Coverage Item | CI-3 (Task kết thúc bất biến) |
| Requirement Ref | REQ-INT-020 (AC3) |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. Partner P ref='DONE'; task K stage='achieved', end_time=T0+1h (10:00 giờ địa phương), business_duration=1.0 (sudo); 2 event của K (attach, complete).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| now | T0 + 5h |  |
| Người dùng | U-MGR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Ghi lại stage, end_time, business_duration và số event của K | stage='achieved', end_time=10:00, elapsed=1.0, event = 2 |
| 2 | U-MGR bấm Re-check Conditions trên K với now = T0 + 5h | Không ném lỗi nghiêm trọng (hoặc từ chối rõ ràng), không đổi dữ liệu |
| 3 | Đọc lại K và số event | Giá trị y hệt bước 1: stage='achieved', end_time=10:00, elapsed=1.0, event = 2 |

**Pass/Fail Criteria:** ✅ Pass: Dữ liệu K không đổi. ❌ Fail: Bất kỳ giá trị nào đổi hoặc có event mới.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-035: Lọc event theo loại error trả 2

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-11 |
| Coverage Item | CI-1 (Bộ lọc loại sự kiện) |
| Requirement Ref | REQ-INT-021 (AC1) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. 5 event (sudo): 2 event='error' (E1 is_resolved=False, E2 is_resolved=True), 1 'attach', 2 'escalate'; E1, E2, 1 attach thuộc FX-DEF-STD, 2 escalate thuộc D2 (định nghĩa thứ hai cùng cấu hình).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-MGR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env U-MGR, áp bộ lọc loại 'error' của danh sách event (`search_count`) | = 2 (E1, E2) |

**Pass/Fail Criteria:** ✅ Pass: Đếm = 2. ❌ Fail: Số đếm khác 2.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-036: Lọc event error theo trạng thái xử lý

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-11 |
| Coverage Item | CI-2 (Bộ lọc chưa xử lý và đã xử lý) |
| Requirement Ref | REQ-INT-021 (Statement (lọc theo trạng thái xử lý)) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. 5 event (sudo): 2 event='error' (E1 is_resolved=False, E2 is_resolved=True), 1 'attach', 2 'escalate'; E1, E2, 1 attach thuộc FX-DEF-STD, 2 escalate thuộc D2 (định nghĩa thứ hai cùng cấu hình).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-MGR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Áp bộ lọc 'Lỗi chưa xử lý' | Kết quả = {E1} (đếm = 1) |
| 2 | Áp bộ lọc 'Lỗi đã xử lý' | Kết quả = {E2} (đếm = 1) |

**Pass/Fail Criteria:** ✅ Pass: Hai bước đúng. ❌ Fail: Bộ lọc lẫn event loại khác.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-037: Nhóm event theo định nghĩa và theo loại

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-11 |
| Coverage Item | CI-3 (Nhóm theo definition_id và event) |
| Requirement Ref | REQ-INT-021 (Statement (nhóm)) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. 5 event (sudo): 2 event='error' (E1 is_resolved=False, E2 is_resolved=True), 1 'attach', 2 'escalate'; E1, E2, 1 attach thuộc FX-DEF-STD, 2 escalate thuộc D2 (định nghĩa thứ hai cùng cấu hình).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-MGR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Nhóm theo definition_id | 2 nhóm: FX-DEF-STD = 3, D2 = 2 |
| 2 | Nhóm theo event | 3 nhóm: error = 2, attach = 1, escalate = 2 |

**Pass/Fail Criteria:** ✅ Pass: Cả 2 phép nhóm đúng. ❌ Fail: Sai nhóm.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-038: Danh sách event không có nút tạo, sửa, xóa với SLA Manager

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-11 |
| Coverage Item | CI-4 (Danh sách event chỉ đọc) |
| Requirement Ref | REQ-INT-021 (AC2) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng).
3. 5 event (sudo): 2 event='error' (E1 is_resolved=False, E2 is_resolved=True), 1 'attach', 2 'escalate'; E1, E2, 1 attach thuộc FX-DEF-STD, 2 escalate thuộc D2 (định nghĩa thứ hai cùng cấu hình).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Người dùng | U-MGR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env U-MGR, `sla.event.get_view(view_type='list')`, đọc thuộc tính create, delete, edit | Đều = '0' |
| 2 | Kiểm `has_access('create')` và `has_access('unlink')` trên sla.event | Cả 2 = False |

**Pass/Fail Criteria:** ✅ Pass: Cả 2 bước đạt. ❌ Fail: Có thao tác tạo/xóa khả dụng.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-039: Tính tỷ lệ đạt 80% và loại task cancelled

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-12 |
| Coverage Item | CI-1 (8 achieved, 2 breached, 5 cancelled cho 80%) |
| Requirement Ref | REQ-FUNC-036 (AC1) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng). Là D1.
3. (TA-30 ĐÃ SỬA) báo cáo pivot/graph của sla.task có measure 'Tỷ lệ đạt' (field `achieved_rate`, cột lưu của `sla.task`), đọc qua `read_group`; tỷ lệ rỗng/False khi mẫu số = 0 (REQ-FUNC-036, 062).
4. 15 task của D1 có end_time trong tháng 03/2026: 8 stage='achieved' (end_time=2026-03-10 08:00 UTC), 2 stage='breached' (end_time=2026-03-10 08:00 UTC), 5 stage='cancelled' (end_time=2026-03-10 08:00 UTC); mỗi task trên partner riêng.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Nhóm | definition_id=D1, end_time:month=2026-03 |  |
| Người dùng | U-USR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env U-USR, `read_group` theo definition_id và end_time:month, lấy measure tỷ lệ đạt | 1 nhóm D1/2026-03 với tỷ lệ = 80% (0.8) |
| 2 | Kiểm số task cancelled trong nhóm | Có 5 task cancelled nhưng không đổi tỷ lệ (nếu tính cả cancelled sẽ là 8/15 = 53.3%) |

**Pass/Fail Criteria:** ✅ Pass: Tỷ lệ = 80%. ❌ Fail: Tỷ lệ khác 80% (ví dụ 53.3%).

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-040: Hiển thị không xác định khi kỳ không có task kết thúc

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-12 |
| Coverage Item | CI-2 (Mẫu số 0 không chia cho 0) |
| Requirement Ref | REQ-FUNC-036 (AC2) |
| Priority | P3-Medium |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng). Là D1.
3. (TA-30 ĐÃ SỬA) báo cáo pivot/graph của sla.task có measure 'Tỷ lệ đạt' (field `achieved_rate`, cột lưu của `sla.task`), đọc qua `read_group`; tỷ lệ rỗng/False khi mẫu số = 0 (REQ-FUNC-036, 062).
4. Kỳ 2026-04: chỉ có 2 task D1 stage='cancelled' (end_time=2026-04-10 08:00 UTC) và 1 task stage='in_progress'; không có achieved hay breached.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Nhóm | D1 / 2026-04 |  |
| Người dùng | U-USR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | `read_group` theo definition_id và end_time:month, đọc tỷ lệ của nhóm D1/2026-04 | Không ném ZeroDivisionError; giá trị rỗng/False tương ứng 'không xác định' (không phải 0%) |
| 2 | Kiểm chuỗi hiển thị của pivot cho ô này (TA-30 ĐÃ SỬA: `achieved_rate` là cột lưu) | Hiển thị 'không xác định' |

**Pass/Fail Criteria:** ✅ Pass: Không lỗi chia 0 và giá trị không phải 0%. ❌ Fail: Ném lỗi hoặc hiển thị 0%.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-041: Gán task kết thúc cuối tháng 9 và đầu tháng 10 vào hai kỳ khác nhau

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-12 |
| Coverage Item | CI-3 (Kỳ theo end_time) |
| Requirement Ref | REQ-FUNC-036 (AC3) |
| Priority | P3-Medium |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng). Là D1.
3. (TA-30 ĐÃ SỬA) báo cáo pivot/graph của sla.task có measure 'Tỷ lệ đạt' (field `achieved_rate`, cột lưu của `sla.task`), đọc qua `read_group`; tỷ lệ rỗng/False khi mẫu số = 0 (REQ-FUNC-036, 062).
4. Task X1 stage='achieved', end_time=2026-09-30 08:00 UTC (15:00 giờ địa phương); task X2 stage='achieved', end_time=2026-10-01 08:00 UTC (15:00 giờ địa phương); cả hai thuộc D1.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Nhóm | end_time:month |  |
| Người dùng | U-USR | timezone Asia/Ho_Chi_Minh |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | `read_group` theo definition_id và end_time:month | 2 nhóm: tháng 9/2026 chứa X1 (count=1, tỷ lệ 100%) và tháng 10/2026 chứa X2 (count=1, tỷ lệ 100%) |
| 2 | Kiểm X1 không có trong nhóm tháng 10 và X2 không có trong nhóm tháng 9 | Đúng |

**Pass/Fail Criteria:** ✅ Pass: Hai nhóm tách đúng. ❌ Fail: X1 và X2 cùng một nhóm.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-042: Đếm số SLA đang vi phạm trên bộ dữ liệu hỗn hợp

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-13 |
| Coverage Item | CI-1 (Số đang vi phạm = 3) |
| Requirement Ref | REQ-FUNC-062 (AC1) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng). Là D1.
3. (TA-11 CÒN MỞ; TA-30 ĐÃ SỬA: `breaching_count` là cột lưu) measure/đếm 'Đang vi phạm' trong pivot = count của task has_breached=True và stage in (in_progress, paused)
4. 5 task của D1: V1, V2 stage='in_progress' has_breached=True; V3 stage='paused' has_breached=True; V4 stage='breached' has_breached=True (end_time=T0+5h); V5 stage='in_progress' has_breached=False.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Nhóm | definition_id=D1 |  |
| Người dùng | U-USR |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Với env U-USR, `read_group` theo definition_id lấy measure số đang vi phạm | D1 = 3 (V1, V2, V3) |
| 2 | Đối chiếu bộ lọc 'Đã vi phạm' | Bộ lọc trả 4 (V1..V4), nghĩa là số đang vi phạm (3) khác số của bộ lọc; V4 bị loại khỏi số đang vi phạm vì stage='breached' |

**Pass/Fail Criteria:** ✅ Pass: Số đang vi phạm = 3. ❌ Fail: Số khác 3.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-043: Số đang vi phạm bằng 0 khi không có task vi phạm

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-13 |
| Coverage Item | CI-2 (Không vi phạm cho 0) |
| Requirement Ref | REQ-FUNC-062 (AC2) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng). Là D1.
3. 2 task D1 stage='in_progress' has_breached=False và 1 task stage='achieved' has_breached=False.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Nhóm | D1 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | `read_group` theo definition_id lấy số đang vi phạm | D1 = 0 (hoặc nhóm không xuất hiện), không lỗi |
| 2 | Áp bộ lọc 'Đã vi phạm' (`search_count`) | = 0 |

**Pass/Fail Criteria:** ✅ Pass: Số = 0. ❌ Fail: Số khác 0 hoặc lỗi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-UIX-044: Tách số đang vi phạm theo từng định nghĩa

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-17-13 |
| Coverage Item | CI-3 (Theo định nghĩa) |
| Requirement Ref | REQ-FUNC-062 (Statement (theo định nghĩa)) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Dựng FX-USERS: U-MGR (group_sla_manager), U-USR (group_sla_user), U-BIZ (chỉ quyền sửa res.partner và demo.ticket), U-NONE (không quyền SLA, không sửa partner).
2. Dựng FX-DEF-STD trên res.partner (start ref in NEW/WORK/HOLD; pause ref=HOLD; resume ref=WORK; stop ref=DONE; cancel ref=CANCEL; duration=4; schedule_source=none; cancel_mode=start_unmatched; resume_mode=condition; active=True; company_id rỗng). Là D1; thêm D2 (cùng cấu hình, name='D2').
3. Task: D1 có 2 task in_progress has_breached=True; D2 có 1 task paused has_breached=True và 1 task in_progress has_breached=False.

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Nhóm | definition_id |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | `read_group` theo definition_id lấy số đang vi phạm | D1 = 2, D2 = 1 |

**Pass/Fail Criteria:** ✅ Pass: D1 = 2 và D2 = 1. ❌ Fail: Số bị gộp hoặc sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

## TG-18 — Hiệu năng

### TC-PRF-001: Đo overhead ghi hàng loạt 1000 `res.partner` trước và sau khi cài module (10 lần lặp)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-18-01 |
| Coverage Item | CI-1 (Mô hình không có định nghĩa, hai DB (trước/sau cài)) |
| Requirement Ref | REQ-PERF-001 AC1 |
| Priority | P1-Critical |
| Test Type | Performance |
| Automation | Automated (script benchmark, odoo shell) |

**Preconditions:**
1. Môi trường benchmark (Test Plan 11.1): cùng cấu hình container, 1 worker HTTP + 1 worker cron, không chạy tác vụ khác; ghi CPU/RAM vào biên bản.
2. Không có định nghĩa SLA nào trên `res.partner`.
3. DB-A: `base` (chưa cài `dwo_sla_core`); DB-B: bản sao DB-A đã cài `dwo_sla_core`. Hai database riêng vì "trước khi cài" cần module vắng mặt (TA-13; ngưỡng 5% đã chốt, O-01 đã đóng).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| quy mô | 1000 `res.partner`/lần |  |
| lặp | 10 lần mỗi DB | Bỏ lần chạy khởi động nguội (warm-up 1 lần) |
| thống kê | Trung vị (median) | Ghi thêm p95 và min/max |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Trên DB-A: lặp 10 lần: tạo 1000 partner bằng `create` (1 lô), rồi `write({'comment':'x'})` toàn bộ 1000; đo tổng thời gian bằng `time.perf_counter`; rollback sau mỗi lần. | Có 10 số đo T_A[1..10]; median_A tính được. |
| 2 | Lặp y hệt trên DB-B: T_B[1..10]. | median_B tính được. |
| 3 | Tính R = median_B / median_A. | R <= 1.05. |

**Pass/Fail Criteria:** ✅ Pass: R <= 1.05 (trung vị sau không quá 105% trước). ❌ Fail: R > 1.05.

**Postconditions:** Hủy hai DB benchmark; lưu bảng số đo vào biên bản.

### TC-PRF-002: Đo overhead trên `res.partner` khi `demo.ticket` có 4 định nghĩa mẫu (10 lần lặp)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-18-01 |
| Coverage Item | CI-2 (Model không có định nghĩa khi model khác có 4 định nghĩa mẫu) |
| Requirement Ref | REQ-PERF-001 AC1 (biến thể) |
| Priority | P2-High |
| Test Type | Performance |
| Automation | Automated (script benchmark, odoo shell) |

**Preconditions:**
1. Môi trường benchmark (Test Plan 11.1): cùng cấu hình container, 1 worker HTTP + 1 worker cron, không chạy tác vụ khác; ghi CPU/RAM vào biên bản.
2. Không có định nghĩa SLA nào trên `res.partner`. 
3. DB-B: cài thêm `dwo_sla_demo_ticket` (FX-DEMO: 4 định nghĩa trên `demo.ticket`, không có định nghĩa trên `res.partner`).
4. DB-A: `base` chưa cài module.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| quy mô | 1000 `res.partner`/lần |  |
| lặp | 10 lần | warm-up 1 lần |
| thống kê | Trung vị |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Trên DB-A: tạo 1000 partner bằng `create` (1 lô), rồi `write({'comment':'x'})` toàn bộ 1000; đo tổng thời gian bằng `time.perf_counter`; rollback sau mỗi lần; lặp 10 lần sau 1 lần warm-up, lấy trung vị. | Có median_A. |
| 2 | Đo trên DB-B (có định nghĩa demo): median_B. | Có median_B. |
| 3 | R = median_B / median_A. | R <= 1.05. |

**Pass/Fail Criteria:** ✅ Pass: R <= 1.05. ❌ Fail: R > 1.05.

**Postconditions:** Hủy DB benchmark.

### TC-PRF-003: Đếm truy vấn khi đánh giá lô khớp start 10 và 100 record

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-18-02 |
| Coverage Item | CI-1 (Lô khớp start (attach hàng loạt)) |
| Requirement Ref | REQ-PERF-002 AC1 |
| Priority | P1-Critical |
| Test Type | Performance |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (không escalation); now = T0.
2. Mọi partner trong lô có `ref` = `NEW` (khớp start), chưa có task.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| lô nhỏ | 10 partner |  |
| lô lớn | 100 partner | Cùng định nghĩa |
| đếm truy vấn | `self.assertQueryCount`/đếm `cr.sql_log` quanh lời gọi Engine | Warm-up 1 lần để nạp cache registry; chỉ đếm lần gọi thứ hai |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Chuẩn bị lô 10 partner; gọi Engine đánh giá lô (`evaluate(records, T0, changed)`) và đếm số truy vấn Q10. | Q10 đo được (số nguyên). |
| 2 | Rollback về savepoint; chuẩn bị lô 100 partner cùng dạng; đánh giá và đếm Q100. | Q100 đo được. |
| 3 | Tính |Q100 - Q10|. | |Q100 - Q10| <= 5; ngoài ra mỗi lô tạo đủ task (10 và 100). |

**Pass/Fail Criteria:** ✅ Pass: |Q100 - Q10| <= 5. ❌ Fail: |Q100 - Q10| > 5.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-PRF-004: Đếm truy vấn khi đánh giá lô không khớp điều kiện 10 và 100 record

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-18-02 |
| Coverage Item | CI-2 (Lô không khớp điều kiện nào) |
| Requirement Ref | REQ-PERF-002 AC1 |
| Priority | P2-High |
| Test Type | Performance |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (không escalation); now = T0.
2. Mọi partner trong lô có `ref` = `ZZZ` (không khớp điều kiện nào).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| lô nhỏ | 10 partner |  |
| lô lớn | 100 partner | Cùng định nghĩa |
| đếm truy vấn | `self.assertQueryCount`/đếm `cr.sql_log` quanh lời gọi Engine | Warm-up 1 lần để nạp cache registry; chỉ đếm lần gọi thứ hai |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Chuẩn bị lô 10 partner; gọi Engine đánh giá lô (`evaluate(records, T0, changed)`) và đếm số truy vấn Q10. | Q10 đo được (số nguyên). |
| 2 | Rollback về savepoint; chuẩn bị lô 100 partner cùng dạng; đánh giá và đếm Q100. | Q100 đo được. |
| 3 | Tính |Q100 - Q10|. | |Q100 - Q10| <= 5; không có task nào được tạo. |

**Pass/Fail Criteria:** ✅ Pass: |Q100 - Q10| <= 5. ❌ Fail: |Q100 - Q10| > 5.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-PRF-005: Đếm truy vấn khi kết thúc hàng loạt lô 10 và 100 record

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-18-02 |
| Coverage Item | CI-3 (Lô có task, khớp stop) |
| Requirement Ref | REQ-PERF-002 AC1 |
| Priority | P1-Critical |
| Test Type | Performance |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. FX-DEF-STD trên `res.partner` (không escalation); now = T0.
2. Mỗi partner có 1 task `in_progress` (tạo ở now = T0), rồi đặt `ref` = `DONE` (khớp stop); đánh giá now = T0 + 1h.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| lô nhỏ | 10 partner |  |
| lô lớn | 100 partner | Cùng định nghĩa |
| đếm truy vấn | `self.assertQueryCount`/đếm `cr.sql_log` quanh lời gọi Engine | Warm-up 1 lần để nạp cache registry; chỉ đếm lần gọi thứ hai |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Chuẩn bị lô 10 partner; gọi Engine đánh giá lô (`evaluate(records, T0, changed)`) và đếm số truy vấn Q10. | Q10 đo được (số nguyên). |
| 2 | Rollback về savepoint; chuẩn bị lô 100 partner cùng dạng; đánh giá và đếm Q100. | Q100 đo được. |
| 3 | Tính |Q100 - Q10|. | |Q100 - Q10| <= 5; mọi task `achieved`. |

**Pass/Fail Criteria:** ✅ Pass: |Q100 - Q10| <= 5. ❌ Fail: |Q100 - Q10| > 5.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-PRF-006: Đo thời gian chu kỳ xử lý nền với 100000 task so với 1000 task (10 mốc đến hạn)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-18-03 |
| Coverage Item | CI-1 (100000 vs 1000 task đang chạy, 10 mốc đến hạn) |
| Requirement Ref | REQ-PERF-003 AC1 |
| Priority | P2-High |
| Test Type | Performance |
| Automation | Automated (script benchmark, odoo shell) |

**Preconditions:**
1. Môi trường benchmark (Test Plan 11.1): cùng cấu hình container, 1 worker HTTP + 1 worker cron, không chạy tác vụ khác; ghi CPU/RAM vào biên bản. FX-DEF-STD + FX-ESC-STD (mốc 75%, 100%); `dwo_sla_core.batch_size` = 50 (mặc định); `ir.cron._commit_progress` thay bằng `fake_progress` trả 100 giây.
2. Dataset-S: 1000 task `in_progress` chèn bằng SQL, `next_due_at` cách đều, 10 task có `next_due_at` <= now; Dataset-L: 100000 task như trên (cũng 10 mốc đến hạn).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| now | T0 + 3h |  |
| lặp | 20 chu kỳ mỗi dataset | Dựng lại 10 mốc đến hạn trước mỗi chu kỳ |
| thống kê | Trung vị thời gian chu kỳ; ghi p95 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Với Dataset-S: với patch `odoo.fields.Datetime.now` trả T0 + 3h (12:00 giờ VN), gọi `process_due()` một lần (10 task đến hạn nhỏ hơn batch_size 50 nên một lần gọi xử lý hết), đo thời gian; lặp 20 lần (dựng lại 10 mốc đến hạn mỗi lần). | median_S; mỗi lần có đúng 10 task được xử lý. |
| 2 | Với Dataset-L: cùng thao tác và cùng số lần lặp như bước 1. | median_L; mỗi lần có đúng 10 task được xử lý. |
| 3 | Tính R = median_L / median_S. | R <= 2. |

**Pass/Fail Criteria:** ✅ Pass: R <= 2. ❌ Fail: R > 2.

**Postconditions:** Xóa dataset SQL.

### TC-PRF-007: Đo thời gian hoàn tất 200 mốc escalation đến hạn khi mô phỏng vòng lặp cron (p95 qua 20 chu kỳ)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-18-03 |
| Coverage Item | CI-2 (200 mốc escalation đến hạn tại T) |
| Requirement Ref | REQ-PERF-003 AC2 |
| Priority | P2-High |
| Test Type | Performance |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Môi trường benchmark (Test Plan 11.1): cùng cấu hình container, 1 worker cron, không chạy tác vụ khác; FX-DEF-STD + mốc 75% (SA-N75); `dwo_sla_core.batch_size` = 50 (mặc định).
2. Mỗi chu kỳ dựng 200 task `in_progress`, mỗi task có mốc 75% đến hạn tại T = T0 + 3h (`next_due_at` = T).
3. `ir.cron._commit_progress` thay bằng `fake_progress` trả 100 giây (không hết ngân sách); `odoo.fields.Datetime.now` được patch trả T + 60 giây (trường hợp xấu nhất cron khởi chạy sau T một chu kỳ 1 phút).
4. Định nghĩa độ trễ: L_k = 60 giây (độ trễ lịch tối đa do chu kỳ cron 1 phút, REQ-PERF-003 Statement) + D_k, trong đó D_k là tổng thời gian đo được của các lần gọi `process_due()` liên tiếp tới khi hết task đến hạn của chu kỳ k (TA-13).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| T | T0 + 3h |  |
| Vòng lặp mô phỏng cron | gọi `process_due()` lặp tới khi `search_count([stage=in_progress, next_due_at<=now])` = 0 | tối đa 10 lần gọi; 200 mốc với batch_size 50 cần đúng 4 lần gọi |
| Lặp | 20 chu kỳ |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Mỗi chu kỳ: dựng 200 task; chạy vòng lặp mô phỏng cron; đo D_k bằng `time.perf_counter` quanh toàn bộ vòng lặp | Vòng lặp gọi `process_due()` đúng 4 lần; 20 giá trị D_k |
| 2 | Sau mỗi chu kỳ đếm event `escalate` | Đúng 200 event `escalate` (mỗi task 1 event) |
| 3 | Tính L_k = 60 + D_k; lấy p95 của 20 giá trị L_k | p95(L) <= 120 giây (tương đương p95(D) <= 60 giây) |

**Pass/Fail Criteria:** ✅ Pass: mỗi chu kỳ có đủ 200 event `escalate` sau đúng 4 lần gọi và p95(L) <= 120 giây; ❌ Fail: thiếu mốc, số lần gọi khác 4, hoặc p95(L) > 120 giây

**Postconditions:** Xóa dữ liệu benchmark.

### TC-PRF-008: Đo thời gian bật dấu vi phạm cho 200 task đến hạn khi mô phỏng vòng lặp cron (p95 qua 20 chu kỳ)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-18-03 |
| Coverage Item | CI-3 (200 task vượt `planned_end_time` tại T) |
| Requirement Ref | REQ-PERF-003 AC2 |
| Priority | P2-High |
| Test Type | Performance |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Môi trường benchmark (Test Plan 11.1): cùng cấu hình container, 1 worker cron, không chạy tác vụ khác; FX-DEF-STD không escalation, 4 giờ, start T0; `dwo_sla_core.batch_size` = 50 (mặc định).
2. Mỗi chu kỳ dựng 200 task `in_progress` có `planned_end_time` = T0 + 4h = T, `next_due_at` = T, `has_breached` = False.
3. `ir.cron._commit_progress` thay bằng `fake_progress` trả 100 giây; `odoo.fields.Datetime.now` được patch trả T + 60 giây.
4. Định nghĩa độ trễ: L_k = 60 giây (độ trễ lịch tối đa do chu kỳ cron 1 phút, REQ-PERF-003 Statement) + D_k, trong đó D_k là tổng thời gian đo được của các lần gọi `process_due()` liên tiếp tới khi hết task đến hạn của chu kỳ k (TA-13).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| now (patch) | T + 60 giây |  |
| Lặp | 20 chu kỳ |  |
| Thống kê | p95 |  |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Mỗi chu kỳ: dựng 200 task; chạy vòng lặp mô phỏng cron (gọi `process_due()` tới khi hết task đến hạn); đo D_k | Vòng lặp gọi `process_due()` đúng 4 lần; 20 giá trị D_k |
| 2 | Đếm task có `has_breached` = True và event `breach` | 200 task và 200 event `breach` mỗi chu kỳ |
| 3 | Tính p95 của L_k = 60 + D_k | p95(L) <= 120 giây |

**Pass/Fail Criteria:** ✅ Pass: 200 task có dấu vi phạm sau đúng 4 lần gọi và p95(L) <= 120 giây; ❌ Fail: thiếu task, số lần gọi khác 4, hoặc p95(L) > 120 giây

**Postconditions:** Xóa dữ liệu benchmark.

### TC-PRF-009: Cron xử lý nền được khai báo chạy mỗi 1 phút và đang bật

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-18-03 |
| Coverage Item | CI-4 (Chu kỳ cron) |
| Requirement Ref | REQ-PERF-003 Statement |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. `dwo_sla_core` đã cài trên `sla_test`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| cron | `ir.cron` gọi `sla.processor.process_due()` (khai báo trong `data/ir_cron.xml`) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đọc `ir.cron` xử lý nền. | `active` = True; `interval_number` = 1; `interval_type` = `minutes`. |
| 2 | Quy đổi chu kỳ. | <= 1 phút. |

**Pass/Fail Criteria:** ✅ Pass: Cron active, chu kỳ <= 1 phút. ❌ Fail: Cron không có, tắt, hoặc chu kỳ > 1 phút.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-PRF-010: Model không có định nghĩa SLA không bị patch `create`/`write`/`_compute_field_value`; model có định nghĩa thì bị patch, và hết định nghĩa thì gỡ patch

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-18-01 |
| Coverage Item | CI-3 (So sánh model có và không có định nghĩa: patch động theo AD-01) |
| Requirement Ref | REQ-FUNC-004, REQ-FUNC-005 (patch động theo AD-01; liên quan REQ-PERF-001) |
| Priority | P1-Critical |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Module `dwo_sla_core` đã cài; chưa có định nghĩa SLA nào đang bật trên `res.partner` và `res.country` (model đối chứng không có định nghĩa); không có định nghĩa archive còn task hoạt động trên hai model này.
2. Mô phỏng "lưu một automation rule" không thuộc ca này (xem TC-ERR-030 về tự phục hồi patch).

**Test Data:**
| Field | Giá trị | Ghi chú |
|---|---|---|
| Model có định nghĩa | `res.partner` | tạo ở bước 2 |
| Model đối chứng | `res.country` | không có định nghĩa |
| Dấu patch | thuộc tính `sla_patch` trên hàm `create`, `write`, `_compute_field_value` của lớp model | đặt bởi `sla.definition._register_hook` |

**Steps & Expected Results:**
| Step | Action | Expected Result |
|---|---|---|
| 1 | Đọc thuộc tính `sla_patch` của `type(env['res.partner']).create`, `.write`, `._compute_field_value` và của `res.country` | Cả 6 hàm không có dấu `sla_patch` (không bị patch) |
| 2 | Tạo định nghĩa FX-DEF-STD (bật) trên `res.partner`, đọc lại thuộc tính ở bước 1 | Ba hàm của `res.partner` có `sla_patch` = True; ba hàm của `res.country` vẫn không có dấu |
| 3 | Archive định nghĩa (không còn task hoạt động), đọc lại | Ba hàm của `res.partner` không còn dấu `sla_patch` |

**Pass/Fail Criteria:** ✅ Pass: chỉ model có định nghĩa (hoặc archive còn task hoạt động) bị patch, model không có định nghĩa không bị patch ở mọi bước; ❌ Fail: `res.country` bị patch hoặc `res.partner` không được patch/gỡ patch đúng lúc

**Ghi chú:** Ca cấu trúc bổ sung cho PRF-001/002 (đo thời gian) theo AD-01 đổi sang patch động (099 mục 3). Ca kiểm dấu patch của hook (cơ chế để REQ-FUNC-004/005 chỉ chạy trên model có định nghĩa), không kiểm ngưỡng 5% của REQ-PERF-001 AC1; ngưỡng đó do TC-PRF-001, 002 đo.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

## TG-19 — Điểm mở rộng

### TC-EXT-001: Task dùng calendar của team khi định nghĩa chọn nguồn `team`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-01 |
| Coverage Item | CI-1 (Module mẫu thêm nguồn `team`, record có team T) |
| Requirement Ref | REQ-INT-007 AC1 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Cài FX-EXT: `selection_add` giá trị `team` cho `schedule_source`; điểm mở rộng nguồn lịch trả `record.team_id.calendar_id`. (override `sla.definition._get_calendar(record)`)
2. Calendar CAL-T = FX-CAL-VN gán cho team T; calendar mặc định của công ty là lịch khác (T2–T6 09:00–18:00).
3. Định nghĩa D: FX-DEF-STD, mục tiêu 4 giờ, `schedule_source` = `team`, trên model có team (`demo.ticket` có `team_id`; phụ thuộc module demo, TA-15).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| record | ticket K, priority `p1`, team = T |  |
| now | T0 |  |
| mục tiêu | 4 giờ |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gọi Engine đánh giá K với now = T0. | Tạo 1 task `in_progress`. |
| 2 | Đọc `schedule_id` của task và `planned_end_time`. | `schedule_id` = CAL-T; `planned_end_time` = 2026-03-02 13:00 (UTC+7). |

**Pass/Fail Criteria:** ✅ Pass: Task dùng CAL-T. ❌ Fail: Task dùng lịch khác hoặc lỗi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-002: Dùng lịch dự phòng khi điểm mở rộng nguồn lịch trả calendar `flexible`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-01 |
| Coverage Item | CI-2 (Module mẫu trả calendar `flexible`) |
| Requirement Ref | REQ-INT-007 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Cài FX-EXT: `sla.definition._get_calendar(record)` trả `record.team_id.calendar_id`, với lịch của team là FX-CAL-FLEX (calendar `flexible`).
2. Lịch mặc định của công ty = FX-CAL-VN; D `schedule_source` = `team`, 4 giờ.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| record | ticket K, priority `p1`, team T |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đánh giá K với now = T0. | Tạo 1 task. |
| 2 | Đọc `schedule_id` task và event `attach`. | `schedule_id` = FX-CAL-VN (lịch công ty); `note` của event `attach` nêu lý do dự phòng (calendar `flexible`). |
| 3 | Kiểm tra `planned_end_time`. | = 2026-03-02 13:00 (UTC+7). |

**Pass/Fail Criteria:** ✅ Pass: Dùng lịch công ty và ghi lý do vào event `attach`. ❌ Fail: Dùng FX-CAL-FLEX hoặc không ghi lý do.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-003: Gỡ module mẫu đưa định nghĩa nguồn `team` về nguồn `none` không lỗi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-01 |
| Coverage Item | CI-3 (Gỡ module mẫu) |
| Requirement Ref | REQ-INT-007 AC3 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (lệnh cài/gỡ trong CI) |

**Preconditions:**
1. Cài FX-EXT; định nghĩa D `schedule_source` = `team` đã lưu.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| module | `dwo_sla_test_ext` |  |
| D | `schedule_source` = `team` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Gỡ module mẫu. | Không lỗi. |
| 2 | Đọc `schedule_source` của D. | = `none`. |
| 3 | Đánh giá 1 record thỏa start với now = T0. | Task tạo, `schedule_id` rỗng, `planned_end_time` = T0 + 4h = 2026-03-02 13:00 (UTC+7). |

**Pass/Fail Criteria:** ✅ Pass: D về `none`, không lỗi. ❌ Fail: Lỗi gỡ hoặc D còn `team`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-004: Danh sách nguồn lịch mặc định không chứa `team` khi chưa cài module mẫu

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-01 |
| Coverage Item | CI-4 (Không có module mẫu: các giá trị mặc định) |
| Requirement Ref | REQ-INT-007 AC1/AC3 (đối chứng) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Không cài FX-EXT.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| field | `sla.definition.schedule_source` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đọc danh sách giá trị selection của `schedule_source`. | Đúng 3 giá trị: `none`, `definition`, `record`. |

**Pass/Fail Criteria:** ✅ Pass: Đúng 3 giá trị mặc định. ❌ Fail: Có giá trị lạ hoặc thiếu.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-005: Dùng lịch dự phòng khi điểm mở rộng nguồn lịch trả rỗng

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-01 |
| Coverage Item | CI-5 (Module mẫu trả rỗng (không có calendar)) |
| Requirement Ref | REQ-INT-007 Statement (trả 'không') |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Cài FX-EXT với điểm mở rộng trả rỗng (`False`).
2. Lịch công ty = FX-CAL-VN; D `schedule_source` = `team`, 4 giờ. (Statement REQ-INT-007 cho phép 'trả calendar hoặc không'; `sla.time.resolve_calendar` áp dụng dự phòng REQ-FUNC-020 cho mọi nguồn khác `none` và `definition`.)

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| record | ticket K, priority `p1`, team rỗng |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đánh giá K với now = T0. | Tạo 1 task. |
| 2 | Đọc `schedule_id` và event `attach`. | `schedule_id` = FX-CAL-VN; `note` nêu lý do dự phòng. |

**Pass/Fail Criteria:** ✅ Pass: Dùng lịch công ty và ghi lý do. ❌ Fail: Task không có lịch mà không ghi lý do, hoặc lỗi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-006: Task P1 có `target_duration` = 3 khi module mẫu trả 3 (định nghĩa ghi 4)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-02 |
| Coverage Item | CI-1 (Module mẫu trả 3 cho `priority = p1`) |
| Requirement Ref | REQ-INT-015 AC1 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Cài FX-EXT: điểm mở rộng thời lượng trả 3 nếu `priority = p1`, ngược lại trả mặc định. (override `sla.definition._get_target_hours(record)`)
2. Định nghĩa FX-DEF-STD trên `demo.ticket`: start `[('priority','in',['p1','p2'])]`, mục tiêu 4 giờ, nguồn lịch `none`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ticket | K1 priority `p1` |  |
| now | T0 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đánh giá K1 với now = T0. | 1 task `in_progress`. |
| 2 | Đọc `target_duration` và `planned_end_time`. | `target_duration` = 3; `planned_end_time` = 2026-03-02 12:00 (UTC+7). |

**Pass/Fail Criteria:** ✅ Pass: `target_duration` = 3. ❌ Fail: `target_duration` = 4 hoặc khác.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-007: Task có `target_duration` = 4 (theo định nghĩa) khi không có module mẫu

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-02 |
| Coverage Item | CI-2 (Không có module mẫu) |
| Requirement Ref | REQ-INT-015 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Không cài FX-EXT.
2. Định nghĩa FX-DEF-STD trên `demo.ticket`: start `[('priority','in',['p1','p2'])]`, mục tiêu 4 giờ, nguồn lịch `none`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ticket | K1 priority `p1` |  |
| now | T0 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đánh giá K1 với now = T0. | 1 task. |
| 2 | Đọc `target_duration`, `planned_end_time`. | `target_duration` = 4; `planned_end_time` = 2026-03-02 13:00 (UTC+7). |

**Pass/Fail Criteria:** ✅ Pass: `target_duration` = 4. ❌ Fail: Khác 4.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-008: Không tạo task và ghi event `error` khi điểm mở rộng trả thời lượng âm

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-02 |
| Coverage Item | CI-3 (Module mẫu trả -1) |
| Requirement Ref | REQ-INT-015 AC3 |
| Priority | P1-Critical |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Cài FX-EXT: trả -1 nếu `priority = p1`.
2. Định nghĩa FX-DEF-STD trên `demo.ticket`: start `[('priority','in',['p1','p2'])]`, mục tiêu 4 giờ, nguồn lịch `none`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ticket | K1 priority `p1` |  |
| now | T0 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đánh giá K1 với now = T0. | Engine không ném lỗi ra ngoài (không chặn lưu record). |
| 2 | Đếm task của K1 và event `error`. | Task = 0; có đúng 1 event `error`. |

**Pass/Fail Criteria:** ✅ Pass: 0 task, 1 event `error`. ❌ Fail: Có task hoặc không có event `error`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-009: Chấp nhận thời lượng 0 từ điểm mở rộng và tạo task có `planned_end_time` = mốc bắt đầu

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-02 |
| Coverage Item | CI-4 (Module mẫu trả 0 (biên hợp lệ)) |
| Requirement Ref | REQ-INT-015 AC3 (ghi chú: 0 chấp nhận) |
| Priority | P3-Medium |
| Test Type | Boundary |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Cài FX-EXT: trả 0 nếu `priority = p1`.
2. Định nghĩa FX-DEF-STD trên `demo.ticket`: start `[('priority','in',['p1','p2'])]`, mục tiêu 4 giờ, nguồn lịch `none`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ticket | K1 priority `p1` |  |
| now | T0 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đánh giá K1 với now = T0. | 1 task `in_progress`. |
| 2 | Đọc `target_duration`, `planned_end_time`. | `target_duration` = 0; `planned_end_time` = `start_time` = 2026-03-02 09:00 (UTC+7). |

**Pass/Fail Criteria:** ✅ Pass: Task tạo với 0 giờ. ❌ Fail: Không tạo task hoặc có event `error`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-010: Record P2 vẫn nhận thời lượng 4 từ định nghĩa khi module mẫu chỉ override P1

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-02 |
| Coverage Item | CI-5 (Record không thuộc quy tắc override (`p2`)) |
| Requirement Ref | REQ-INT-015 AC1/AC2 (EP) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Cài FX-EXT: trả 3 nếu `priority = p1`, ngược lại trả giá trị mặc định.
2. Định nghĩa FX-DEF-STD trên `demo.ticket`: start `[('priority','in',['p1','p2'])]`, mục tiêu 4 giờ, nguồn lịch `none`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| ticket | K2 priority `p2` |  |
| now | T0 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đánh giá K2 với now = T0. | 1 task. |
| 2 | Đọc `target_duration`. | = 4. |

**Pass/Fail Criteria:** ✅ Pass: `target_duration` = 4. ❌ Fail: Khác 4.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-011: `start_time` bằng mốc do module mẫu trả (cách đây 2 giờ)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-03 |
| Coverage Item | CI-1 (Module mẫu trả mốc T0 - 2h) |
| Requirement Ref | REQ-INT-016 AC1 |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Cài FX-EXT: điểm mở rộng mốc bắt đầu trả `now - 2 giờ`. (override `sla.definition._get_start_dt(record, now)`)
2. FX-DEF-STD trên `res.partner` (retroactive_start tắt).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| partner | P `ref` = `NEW` |  |
| now | T0 |  |
| mục tiêu | 4 giờ |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đánh giá P với now = T0. | 1 task. |
| 2 | Đọc `start_time`, `planned_end_time`. | `start_time` = 2026-03-02 07:00 (UTC+7); `planned_end_time` = 2026-03-02 11:00 (UTC+7) (24x7). |

**Pass/Fail Criteria:** ✅ Pass: `start_time` = T0 - 2h. ❌ Fail: Khác.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-012: `start_time` bằng thời điểm attach khi không có module mẫu và không bật retroactive

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-03 |
| Coverage Item | CI-2 (Không có module mẫu, không retroactive) |
| Requirement Ref | REQ-INT-016 AC2 |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Không cài FX-EXT.
2. FX-DEF-STD trên `res.partner`, retroactive_start tắt.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| partner | P `ref` = `NEW` |  |
| now | T0 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đánh giá P với now = T0. | 1 task. |
| 2 | Đọc `start_time`. | = 2026-03-02 09:00 (UTC+7). |

**Pass/Fail Criteria:** ✅ Pass: `start_time` = T0. ❌ Fail: Khác T0.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-013: `start_time` theo field retroactive khi không có module mẫu

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-03 |
| Coverage Item | CI-3 (Không có module mẫu, bật retroactive) |
| Requirement Ref | REQ-INT-016 Statement (mặc định: field retroactive) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Không cài FX-EXT.
2. FX-DEF-STD, `retroactive_start` = True, `retroactive_field_id` = `create_date` của `res.partner`.
3. Partner P tạo với `create_date` = T0 - 1h (đặt bằng SQL).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| partner | P `ref` = `NEW` |  |
| now | T0 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đánh giá P với now = T0. | 1 task. |
| 2 | Đọc `start_time`. | = 2026-03-02 08:00 (UTC+7). |

**Pass/Fail Criteria:** ✅ Pass: `start_time` = T0 - 1h. ❌ Fail: Khác.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-014: Kết quả điều kiện start theo domain do module mẫu trả thay cho domain đã lưu

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-04 |
| Coverage Item | CI-1 (Module mẫu trả domain khác cho start) |
| Requirement Ref | REQ-INT-017 AC1 |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Cài FX-EXT: điểm mở rộng domain trả `[('ref','=','WORK')]` cho điều kiện `start`. (override `sla.definition._get_domain(cond)`)
2. FX-DEF-STD trên `res.partner` (start đã lưu `[('ref','in',['NEW','WORK','HOLD'])]`).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| P1 | `ref` = `NEW` | Khớp domain lưu, không khớp domain module mẫu |
| P2 | `ref` = `WORK` | Khớp cả hai |
| now | T0 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đánh giá {P1, P2} với now = T0. | Không lỗi. |
| 2 | Đếm task theo record. | P1 = 0 task; P2 = 1 task `in_progress`. |

**Pass/Fail Criteria:** ✅ Pass: Chỉ P2 có task. ❌ Fail: P1 có task hoặc P2 không có.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-015: Dùng domain đã lưu của điều kiện start khi không có module mẫu

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-04 |
| Coverage Item | CI-2 (Không có module mẫu) |
| Requirement Ref | REQ-INT-017 AC2 |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Không cài FX-EXT.
2. FX-DEF-STD trên `res.partner`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| P1 | `ref` = `NEW` |  |
| P2 | `ref` = `WORK` |  |
| now | T0 |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đánh giá {P1, P2} với now = T0. | Không lỗi. |
| 2 | Đếm task. | P1 = 1; P2 = 1 (cả hai khớp domain đã lưu). |

**Pass/Fail Criteria:** ✅ Pass: Cả hai có task. ❌ Fail: Thiếu task.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-016: Điều kiện `stop` dùng domain đã lưu khi module mẫu chỉ thay domain của `start`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-04 |
| Coverage Item | CI-3 (Module mẫu chỉ đổi `start`, điều kiện `stop` dùng domain lưu) |
| Requirement Ref | REQ-INT-017 Statement (cho từng điều kiện) |
| Priority | P4-Low |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Cài FX-EXT: chỉ thay domain `start` thành `[('ref','=','WORK')]`.
2. FX-DEF-STD; partner P `ref` = `WORK` có task `in_progress` (start T0).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| hành động | đặt `ref` = `DONE` | Khớp stop đã lưu |
| now | T0 + 1h |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Sửa `ref` = `DONE`; đánh giá P với now = T0 + 1h, changed = {ref}. | Không lỗi. |
| 2 | Đọc `stage` của task. | = `achieved`; `end_time` = 2026-03-02 10:00 (UTC+7). |

**Pass/Fail Criteria:** ✅ Pass: Task `achieved` theo stop đã lưu. ❌ Fail: Task còn `in_progress`.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-017: Điểm mở rộng được gọi 1 lần với (`in_progress`,`paused`,`pause`) khi task pause

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-05 |
| Coverage Item | CI-1 (`in_progress` → `paused`) |
| Requirement Ref | REQ-INT-018 AC1 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Cài FX-EXT: điểm mở rộng sau chuyển trạng thái ghi lại danh sách tham số (cũ, mới, loại event) mỗi lần được gọi. (override `sla.definition._after_transition(task, old_stage, new_stage, event)`)
2. FX-DEF-STD; partner P `ref` = `NEW` có task `in_progress` (start T0); xóa nhật ký gọi của module mẫu.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| hành động | đặt `ref` = `HOLD` | Khớp pause |
| now | T0 + 1h |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Sửa `ref` = `HOLD`; đánh giá P với now = T0 + 1h, changed = {ref}. | Task `paused`. |
| 2 | Đọc nhật ký gọi hook. | Đúng 1 lần gọi: (`in_progress`, `paused`, `pause`). |

**Pass/Fail Criteria:** ✅ Pass: 1 lần gọi với đúng tham số. ❌ Fail: 0 hoặc >1 lần gọi, hoặc tham số sai.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-018: Không gọi điểm mở rộng khi đánh giá không đổi trạng thái

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-05 |
| Coverage Item | CI-2 (Đánh giá không đổi trạng thái) |
| Requirement Ref | REQ-INT-018 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Cài FX-EXT: điểm mở rộng sau chuyển trạng thái ghi lại danh sách tham số (cũ, mới, loại event) mỗi lần được gọi. (override `sla.definition._after_transition(task, old_stage, new_stage, event)`)
2. FX-DEF-STD; partner P `ref` = `NEW` có task `in_progress`; xóa nhật ký gọi.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| now | T0 + 1h |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đánh giá P với now = T0 + 1h, changed = {ref} (giá trị `ref` không đổi, vẫn `NEW`). | Task vẫn `in_progress`, không có event mới. |
| 2 | Đọc nhật ký gọi hook. | 0 lần gọi. |

**Pass/Fail Criteria:** ✅ Pass: Hook không được gọi. ❌ Fail: Hook được gọi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-019: Điểm mở rộng được gọi 1 lần khi task hoàn thành

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-05 |
| Coverage Item | CI-3 (`in_progress` → `achieved`) |
| Requirement Ref | REQ-INT-018 Statement (mọi chuyển trạng thái) |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Cài FX-EXT: điểm mở rộng sau chuyển trạng thái ghi lại danh sách tham số (cũ, mới, loại event) mỗi lần được gọi. (override `sla.definition._after_transition(task, old_stage, new_stage, event)`)
2. FX-DEF-STD; partner P `ref` = `NEW` có task `in_progress` (start T0); xóa nhật ký gọi.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| hành động | đặt `ref` = `DONE` |  |
| now | T0 + 1h |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Sửa `ref` = `DONE`; đánh giá P với now = T0 + 1h. | Task `achieved`. |
| 2 | Đọc nhật ký gọi hook. | Đúng 1 lần: (`in_progress`, `achieved`, `complete`). |

**Pass/Fail Criteria:** ✅ Pass: 1 lần gọi đúng tham số. ❌ Fail: Sai số lần hoặc tham số.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-020: Mặc định không làm gì khi không có module override điểm mở rộng sau chuyển trạng thái

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-05 |
| Coverage Item | CI-4 (Không có module mẫu (mặc định)) |
| Requirement Ref | REQ-INT-018 Statement (mặc định) |
| Priority | P3-Medium |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Không cài FX-EXT.
2. FX-DEF-STD; partner P `ref` = `NEW` có task `in_progress`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| hành động | đặt `ref` = `HOLD` |  |
| now | T0 + 1h |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Sửa `ref` = `HOLD`; đánh giá P với now = T0 + 1h. | Không lỗi; task `paused`. |
| 2 | Đếm event của task. | Đúng 2 event: `attach`, `pause` (không có event phụ do hook). |

**Pass/Fail Criteria:** ✅ Pass: Chuyển trạng thái đúng, không có tác dụng phụ. ❌ Fail: Lỗi hoặc event thừa.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-021: Module mẫu override đủ 5 điểm mở rộng vẫn chạy sau khi nâng cấp `dwo_sla_core`

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-06 |
| Coverage Item | CI-1 (Module mẫu override đủ 5 điểm sau nâng cấp) |
| Requirement Ref | REQ-REUSE-001 AC1 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (lệnh cài/gỡ trong CI) |

**Preconditions:**
1. Cài FX-EXT override cả 5 điểm trên `sla.definition`: `_get_calendar(record)` (nguồn lịch `team`), `_get_target_hours(record)` (3 cho `p1`), `_get_start_dt(record, now)` (now - 2h), `_get_domain(cond)` (điều kiện `start` = `[('ref','=','WORK')]`), `_after_transition(task, old_stage, new_stage, event)` (ghi lại tham số).
2. Baseline nằm trong Steps của ca này (bước 1), không dựa vào ca khác. Dữ liệu: model có team (`demo.ticket` có `team_id`, `priority`), định nghĩa D (FX-DEF-STD, `schedule_source` = `team`), lịch của team = FX-CAL-VN.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| lệnh nâng cấp | `odoo -d sla_test -u dwo_sla_core --stop-after-init` | cú pháp tag Odoo: `--test-tags tg_19` chọn theo tag, không dùng `dwo_sla_core:tg_19` |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Trước nâng cấp: với record có `priority` = `p1` gọi 5 điểm mở rộng của D | `_get_calendar` trả lịch của team (FX-CAL-VN); `_get_target_hours` = 3; `_get_start_dt(record, now)` = now - 2h; `_get_domain('start')` = `[('ref','=','WORK')]`; `_after_transition` đã ghi lại một lần gọi với (task, False, `in_progress`, `attach`) khi attach |
| 2 | Nâng cấp `dwo_sla_core` (cùng phiên bản chính) bằng lệnh ở Test Data | Nâng cấp không lỗi |
| 3 | Gọi lại đúng 5 điểm mở rộng như bước 1 | Cùng 5 kết quả như bước 1; không có lỗi `TypeError` về chữ ký |

**Pass/Fail Criteria:** ✅ Pass: Module mẫu chạy, bộ test đạt. ❌ Fail: Có ca thất bại hoặc lỗi chữ ký.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-022: Test hợp đồng thất bại khi chữ ký một điểm mở rộng bị đổi

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-06 |
| Coverage Item | CI-2 (Thay đổi chữ ký điểm mở rộng) |
| Requirement Ref | REQ-REUSE-001 AC2 |
| Priority | P2-High |
| Test Type | Negative |
| Automation | Automated (Odoo TransactionCase) |

**Preconditions:**
1. Test hợp đồng lưu 'ảnh chụp chữ ký' (tên, tham số, kiểu trả về theo `inspect.signature`) của 5 điểm mở rộng.
2. Trong test dùng `unittest.mock.patch` để thay một điểm mở rộng bằng phương thức có thêm 1 tham số bắt buộc (mô phỏng thay đổi trong MR).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| điểm bị đổi | điểm mở rộng thời lượng mục tiêu (thêm tham số `extra`) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Chạy test hợp đồng với patch thay đổi chữ ký. | Test hợp đồng thất bại (AssertionError nêu tên điểm bị đổi). |
| 2 | Chạy test hợp đồng không patch. | Đạt. |

**Pass/Fail Criteria:** ✅ Pass: Phát hiện đúng thay đổi chữ ký (fail khi đổi, pass khi không). ❌ Fail: Không phát hiện thay đổi.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

### TC-EXT-023: Rà soát MR đổi chữ ký điểm mở rộng có tuân thủ REQ-CM-001

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-19-06 |
| Coverage Item | CI-3 (MR đổi chữ ký điểm mở rộng (Inspection)) |
| Requirement Ref | REQ-REUSE-001 AC2 |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. Có MR giả định thay đổi tên/tham số/kiểu trả về của một điểm mở rộng, hoặc MR hợp lệ không đổi chữ ký để đối chứng.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| checklist | Danh sách kiểm tra MR (Test Plan mục 9) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Mở diff của MR; liệt kê mọi `def` điểm mở rộng có thay đổi tên/tham số/kiểu trả về. | Danh sách rõ ràng (trống hoặc có mục). |
| 2 | Nếu danh sách không trống: kiểm tra có script nâng cấp trong `migrations/` và dòng Revision History trong SRS. | Có cả hai; MR được phân loại 'gây phá vỡ'. |
| 3 | Kiểm tra bộ test điểm mở rộng đã được cập nhật theo. | Có cập nhật. |

**Pass/Fail Criteria:** ✅ Pass: Mọi mục đạt (hoặc MR không đổi chữ ký). ❌ Fail: Đổi chữ ký mà thiếu script/Revision History/phân loại.

**Postconditions:** Không: dữ liệu bị rollback cuối ca (TransactionCase).

## INS — Inspection và kiểm tra CI (BUILD, MAINT, CM, INST-002)

### TC-INS-001: Kiểm tra manifest chỉ khai báo phụ thuộc `base`, `resource` và `web` (D1)

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-INS-01 |
| Coverage Item | CI-1 (`depends` của manifest) |
| Requirement Ref | REQ-INST-002 AC1 |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. Mã nguồn `custom-addons/dwo_sla_core/` ở commit đang test (ghi vào biên bản).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| file | `custom-addons/dwo_sla_core/__manifest__.py` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Mở manifest, đọc khóa `depends`. | Tập giá trị = {`base`, `resource`, `web`} (không thừa, không thiếu). `web` là sai lệch đã được duyệt D1 (SRS REQ-INST-002): module cần `web` cho view, report và asset của giao diện. |
| 2 | Nếu có phụ thuộc ngoài {`base`, `resource`, `web`}: tìm mục tương ứng trong SRS (kèm lý do). | Không có phụ thuộc nào khác ngoài ba module trên (phụ thuộc thứ tư chỉ hợp lệ khi SRS ghi lý do; với AC1 kết quả mong đợi là không có). |

**Pass/Fail Criteria:** ✅ Pass: `depends` đúng bằng {`base`, `resource`, `web`}. ❌ Fail: Thiếu một trong ba, hoặc có phụ thuộc khác (kể cả helpdesk, `nev_*`, `dwo_*` khác).

**Postconditions:** Không: không thay đổi dữ liệu; lưu biên bản rà soát.

### TC-INS-002: Kiểm tra không có phụ thuộc hoặc tham chiếu tới helpdesk, `nev_*`, `dwo_*` khác và module OCA

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-INS-01 |
| Coverage Item | CI-2 (Phụ thuộc cấm (helpdesk, `nev_*`, `dwo_*`, OCA)) |
| Requirement Ref | REQ-INST-002 AC1 (negative: phần KHÔNG ĐƯỢC) |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. Mã nguồn `custom-addons/dwo_sla_core/` ở commit đang test (ghi vào biên bản).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| lệnh gợi ý | `grep -rEn "sh_all_in_one_helpdesk|nev_|dwo_(?!sla_core)|oca|OCA" custom-addons/dwo_sla_core --include=*.py --include=*.xml --include=*.csv` | Loại trừ thư mục `docs/` và `tests/` demo |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Chạy tìm kiếm trên manifest, mã Python, XML, CSV của module (trừ `docs/`). | Không có kết quả khớp trong `depends`, `import`, hoặc xmlid dạng `<module>.<id>` trỏ module cấm. |
| 2 | Rà soát từng kết quả (nếu có) xem có phải tham chiếu thật. | Mọi kết quả (nếu có) chỉ là chuỗi trong comment/tài liệu, không phải phụ thuộc thật. |

**Pass/Fail Criteria:** ✅ Pass: Không có phụ thuộc cấm. ❌ Fail: Có phụ thuộc cấm.

**Postconditions:** Không: không thay đổi dữ liệu; lưu biên bản rà soát.

### TC-INS-003: Pylint đạt điểm không dưới 9 trên mọi file Python của module

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-INS-02 |
| Coverage Item | CI-1 (Pylint trên file Python) |
| Requirement Ref | REQ-BUILD-001 AC1 |
| Priority | P2-High |
| Test Type | Inspection |
| Automation | Automated (CI lint) |

**Preconditions:**
1. Môi trường CI/shell có pylint với plugin `pylint_odoo` theo `.pylintrc` của repo (Python 3 của image).
2. Mã nguồn `custom-addons/dwo_sla_core/` ở commit đang test (ghi vào biên bản).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| lệnh | `pylint --rcfile=.pylintrc --fail-under=9 $(git ls-files 'custom-addons/dwo_sla_core/*.py')` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Chạy lệnh pylint. | Mã thoát 0. |
| 2 | Đọc dòng 'Your code has been rated at X/10'. | X >= 9.00. |

**Pass/Fail Criteria:** ✅ Pass: Mã thoát 0 và điểm >= 9. ❌ Fail: Mã thoát khác 0 hoặc điểm < 9.

**Postconditions:** Không: lưu log pylint vào kết quả CI.

### TC-INS-004: Mã JS của module (nếu có) qua eslint và prettier của repo

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-INS-02 |
| Coverage Item | CI-2 (eslint/prettier cho JS (nếu có)) |
| Requirement Ref | REQ-BUILD-001 Statement (vế JS) |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Automated (CI lint) |

**Preconditions:**
1. Mã nguồn `custom-addons/dwo_sla_core/` ở commit đang test (ghi vào biên bản).
2. Kiểm tra trước: `git ls-files 'custom-addons/dwo_sla_core/**/*.js'`. Nếu rỗng, ca đạt vì không áp dụng (ghi 'N/A' vào biên bản).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| lệnh | `npm run lint-diff` (eslint) và `npx prettier --check` trên các file JS của module |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Liệt kê file JS của module. | Danh sách (có thể rỗng). |
| 2 | Nếu có: chạy eslint và prettier. | 0 lỗi eslint; prettier `--check` đạt. |

**Pass/Fail Criteria:** ✅ Pass: Không có JS, hoặc có JS và qua cả hai công cụ. ❌ Fail: Có lỗi eslint hoặc prettier.

**Postconditions:** Không.

### TC-INS-005: Xác nhận `.pylintrc` không bỏ qua `dwo_sla_core` nên điểm lint có ý nghĩa

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-INS-02 |
| Coverage Item | CI-3 (Module không bị `ignore-patterns` bỏ qua) |
| Requirement Ref | REQ-BUILD-001 AC1 (độ tin cậy của phép đo) |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. Môi trường CI/shell có pylint với plugin `pylint_odoo` theo `.pylintrc` của repo (Python 3 của image).
2. Mã nguồn `custom-addons/dwo_sla_core/` ở commit đang test (ghi vào biên bản).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| file | `.pylintrc`, mục `ignore-patterns` | Repo ignore `^nexis_.*` và `^nev_.*` |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đọc `ignore-patterns` trong `.pylintrc`. | Không có mẫu nào khớp `dwo_sla_core`. |
| 2 | Chạy pylint với `--verbose` hoặc `--list-msgs-enabled` trên một file của module cố ý có lỗi định dạng (bản sao tạm ngoài repo). | Pylint báo lỗi cho file đó (không bị bỏ qua). |
| 3 | Xóa file tạm. | Không còn thay đổi. |

**Pass/Fail Criteria:** ✅ Pass: Module không bị bỏ qua. ❌ Fail: Module bị bỏ qua (điểm lint vô nghĩa).

**Postconditions:** Không: không thay đổi dữ liệu; lưu biên bản rà soát.

### TC-INS-006: Rà soát có comment lý do tại chỗ cài đặt cho mục: Hook trên ORM

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-INS-03 |
| Coverage Item | CI-1 (Mục 1: Hook trên ORM) |
| Requirement Ref | REQ-MAINT-001 AC1 |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. Mã nguồn `custom-addons/dwo_sla_core/` ở commit đang test (ghi vào biên bản).
2. Người rà soát là developer khác tác giả (code review).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| mục cần có comment | quan sát cả sửa trực tiếp lẫn tính lại field compute có lưu (hook `write`/`create` và hook tính lại) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Xác định vị trí cài đặt (hàm/lớp) của quyết định này trong mã (dùng tìm kiếm theo tên hook/hàm). | Tìm được vị trí cài đặt. |
| 2 | Đọc comment/docstring tại vị trí đó. | Có comment nêu lý do (WHY), không chỉ mô tả cái gì. |
| 3 | Đối chiếu nội dung comment với mục cần có. | Comment nêu đủ ý chính: quan sát cả sửa trực tiếp lẫn tính lại field compute có lưu (hook `write`/`create` và hook tính lại). |

**Pass/Fail Criteria:** ✅ Pass: Comment hiện diện tại vị trí cài đặt và nêu đúng lý do. ❌ Fail: Không có comment, hoặc comment không nêu lý do, hoặc ở sai vị trí.

**Postconditions:** Không: không thay đổi dữ liệu; lưu biên bản rà soát.

### TC-INS-007: Rà soát có comment lý do tại chỗ cài đặt cho mục: Cô lập lỗi engine

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-INS-03 |
| Coverage Item | CI-2 (Mục 2: Cô lập lỗi engine) |
| Requirement Ref | REQ-MAINT-001 AC1 |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. Mã nguồn `custom-addons/dwo_sla_core/` ở commit đang test (ghi vào biên bản).
2. Người rà soát là developer khác tác giả (code review).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| mục cần có comment | engine lỗi không chặn lưu record, nêu đánh đổi và biện pháp bù (event `error`, nút đánh giá lại) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Xác định vị trí cài đặt (hàm/lớp) của quyết định này trong mã (dùng tìm kiếm theo tên hook/hàm). | Tìm được vị trí cài đặt. |
| 2 | Đọc comment/docstring tại vị trí đó. | Có comment nêu lý do (WHY), không chỉ mô tả cái gì. |
| 3 | Đối chiếu nội dung comment với mục cần có. | Comment nêu đủ ý chính: engine lỗi không chặn lưu record, nêu đánh đổi và biện pháp bù (event `error`, nút đánh giá lại). |

**Pass/Fail Criteria:** ✅ Pass: Comment hiện diện tại vị trí cài đặt và nêu đúng lý do. ❌ Fail: Không có comment, hoặc comment không nêu lý do, hoặc ở sai vị trí.

**Postconditions:** Không: không thay đổi dữ liệu; lưu biên bản rà soát.

### TC-INS-008: Rà soát có comment lý do tại chỗ cài đặt cho mục: Đánh giá lại

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-INS-03 |
| Coverage Item | CI-3 (Mục 3: Đánh giá lại) |
| Requirement Ref | REQ-MAINT-001 AC1 |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. Mã nguồn `custom-addons/dwo_sla_core/` ở commit đang test (ghi vào biên bản).
2. Người rà soát là developer khác tác giả (code review).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| mục cần có comment | đánh giá lại dùng thời điểm hiện tại và không sửa ngược task đã kết thúc |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Xác định vị trí cài đặt (hàm/lớp) của quyết định này trong mã (dùng tìm kiếm theo tên hook/hàm). | Tìm được vị trí cài đặt. |
| 2 | Đọc comment/docstring tại vị trí đó. | Có comment nêu lý do (WHY), không chỉ mô tả cái gì. |
| 3 | Đối chiếu nội dung comment với mục cần có. | Comment nêu đủ ý chính: đánh giá lại dùng thời điểm hiện tại và không sửa ngược task đã kết thúc. |

**Pass/Fail Criteria:** ✅ Pass: Comment hiện diện tại vị trí cài đặt và nêu đúng lý do. ❌ Fail: Không có comment, hoặc comment không nêu lý do, hoặc ở sai vị trí.

**Postconditions:** Không: không thay đổi dữ liệu; lưu biên bản rà soát.

### TC-INS-009: Rà soát có comment lý do tại chỗ cài đặt cho mục: Nhật ký sự kiện

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-INS-03 |
| Coverage Item | CI-4 (Mục 4: Nhật ký sự kiện) |
| Requirement Ref | REQ-MAINT-001 AC1 |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. Mã nguồn `custom-addons/dwo_sla_core/` ở commit đang test (ghi vào biên bản).
2. Người rà soát là developer khác tác giả (code review).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| mục cần có comment | ý nghĩa của nhật ký sự kiện (`sla.event`: nguồn sự thật cho lịch sử, đối soát) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Xác định vị trí cài đặt (hàm/lớp) của quyết định này trong mã (dùng tìm kiếm theo tên hook/hàm). | Tìm được vị trí cài đặt. |
| 2 | Đọc comment/docstring tại vị trí đó. | Có comment nêu lý do (WHY), không chỉ mô tả cái gì. |
| 3 | Đối chiếu nội dung comment với mục cần có. | Comment nêu đủ ý chính: ý nghĩa của nhật ký sự kiện (`sla.event`: nguồn sự thật cho lịch sử, đối soát). |

**Pass/Fail Criteria:** ✅ Pass: Comment hiện diện tại vị trí cài đặt và nêu đúng lý do. ❌ Fail: Không có comment, hoặc comment không nêu lý do, hoặc ở sai vị trí.

**Postconditions:** Không: không thay đổi dữ liệu; lưu biên bản rà soát.

### TC-INS-010: Rà soát có comment lý do tại chỗ cài đặt cho mục: Field compute không lưu

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-INS-03 |
| Coverage Item | CI-5 (Mục 5: Field compute không lưu) |
| Requirement Ref | REQ-MAINT-001 AC1 |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. Mã nguồn `custom-addons/dwo_sla_core/` ở commit đang test (ghi vào biên bản).
2. Người rà soát là developer khác tác giả (code review).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| mục cần có comment | giới hạn của field compute không lưu và quan hệ xa (dựa vào đánh giá lại thủ công, REQ-FUNC-042) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Xác định vị trí cài đặt (hàm/lớp) của quyết định này trong mã (dùng tìm kiếm theo tên hook/hàm). | Tìm được vị trí cài đặt. |
| 2 | Đọc comment/docstring tại vị trí đó. | Có comment nêu lý do (WHY), không chỉ mô tả cái gì. |
| 3 | Đối chiếu nội dung comment với mục cần có. | Comment nêu đủ ý chính: giới hạn của field compute không lưu và quan hệ xa (dựa vào đánh giá lại thủ công, REQ-FUNC-042). |

**Pass/Fail Criteria:** ✅ Pass: Comment hiện diện tại vị trí cài đặt và nêu đúng lý do. ❌ Fail: Không có comment, hoặc comment không nêu lý do, hoặc ở sai vị trí.

**Postconditions:** Không: không thay đổi dữ liệu; lưu biên bản rà soát.

### TC-INS-011: Một lệnh trên database trống chạy toàn bộ test và báo kết quả đạt

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-INS-04 |
| Coverage Item | CI-1 (Database trống, một lệnh) |
| Requirement Ref | REQ-MAINT-002 AC1 |
| Priority | P2-High |
| Test Type | Positive |
| Automation | Automated (CI) |

**Preconditions:**
1. Database `sla_empty` vừa tạo, chỉ có `base`; image theo Dockerfile của repo.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| lệnh | `odoo -d sla_empty -i dwo_sla_core,dwo_sla_demo_ticket --test-enable --test-tags /dwo_sla_core,/dwo_sla_demo_ticket --stop-after-init` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Chạy lệnh. | Lệnh kết thúc, không treo. |
| 2 | Đọc log cuối. | Có dòng tổng kết số test đã chạy (> 0), `0 failed, 0 error(s)`. |
| 3 | Kiểm tra mã thoát. | = 0. |

**Pass/Fail Criteria:** ✅ Pass: Test chạy xong, kết quả đạt và mã thoát 0. ❌ Fail: Không chạy được hoặc có test lỗi.

**Postconditions:** Hủy DB `sla_empty`.

### TC-INS-012: Kiểm tra suite generic chạy trên `res.partner` và không phụ thuộc model ticket

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-INS-04 |
| Coverage Item | CI-2 (Suite generic trên `res.partner`) |
| Requirement Ref | REQ-MAINT-002 Statement |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. Mã nguồn `custom-addons/dwo_sla_core/` ở commit đang test (ghi vào biên bản).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| thư mục | `custom-addons/dwo_sla_core/tests/` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Liệt kê test case của `dwo_sla_core`; đếm số ca dùng `res.partner`. | Có ít nhất 1 lớp test dùng `res.partner` (FX-DEF-STD). |
| 2 | Tìm `demo.ticket`, `sh.helpdesk.ticket`, `dwo_sla_demo_ticket` trong `tests/` của `dwo_sla_core`. | Không có tham chiếu (manifest không phụ thuộc). |

**Pass/Fail Criteria:** ✅ Pass: Suite generic dùng `res.partner`, không tham chiếu model ticket. ❌ Fail: Thiếu suite hoặc phụ thuộc ticket.

**Postconditions:** Không: không thay đổi dữ liệu; lưu biên bản rà soát.

### TC-INS-013: Suite end-to-end trên `demo.ticket` tồn tại và được chạy bởi lệnh test

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-INS-04 |
| Coverage Item | CI-3 (Suite end-to-end trên `demo.ticket`) |
| Requirement Ref | REQ-MAINT-002 Statement |
| Priority | P3-Medium |
| Test Type | Positive |
| Automation | Automated (CI) |

**Preconditions:**
1. `dwo_sla_demo_ticket` cài trên `sla_empty`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| tag | `/dwo_sla_demo_ticket` |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Chạy `odoo -d sla_empty -i dwo_sla_demo_ticket --test-enable --test-tags /dwo_sla_demo_ticket --stop-after-init`. | Mã thoát 0. |
| 2 | Đọc log: số test chạy. | > 0 test; mọi test đạt. |

**Pass/Fail Criteria:** ✅ Pass: Có test end-to-end và đạt. ❌ Fail: Không có test hoặc có test lỗi.

**Postconditions:** Hủy DB.

### TC-INS-014: Lệnh test báo không đạt (mã thoát khác 0) khi một test cố ý thất bại

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-INS-04 |
| Coverage Item | CI-4 (Test lỗi → mã thoát khác 0) |
| Requirement Ref | REQ-MAINT-002 AC1 (đạt hoặc không đạt) |
| Priority | P4-Low |
| Test Type | Negative |
| Automation | Automated (CI) |

**Preconditions:**
1. Thêm tạm một test cố ý `self.fail('x')` vào bản sao module trong DB `sla_empty2` (không commit).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| lệnh | `odoo -d sla_empty2 -i dwo_sla_core,dwo_sla_demo_ticket --test-enable --test-tags /dwo_sla_core,/dwo_sla_demo_ticket --stop-after-init` | chạy trong database và bản sao module cô lập `sla_empty2`, không chạy trên pipeline chính |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Chạy lệnh. | Log có `1 failed`/`FAIL`. |
| 2 | Kiểm tra mã thoát hoặc kết quả job CI. | Khác 0 / job CI đỏ. |

**Pass/Fail Criteria:** ✅ Pass: Thất bại được phản ánh trong kết quả. ❌ Fail: Lệnh báo đạt dù có test lỗi.

**Postconditions:** Hủy DB `sla_empty2`, xóa bản sao module chứa test cố ý thất bại (không commit, không đẩy lên nhánh dùng chung).

### TC-INS-015: Rà soát MR gây phá vỡ có script nâng cấp và dòng Revision History

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-INS-05 |
| Coverage Item | CI-1 (MR gây phá vỡ có migration và Revision History) |
| Requirement Ref | REQ-CM-001 AC1 |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. Có MR đổi chữ ký điểm mở rộng hoặc đổi cấu trúc dữ liệu SLA (ví dụ đổi tên cột).

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| checklist | Danh sách kiểm tra MR (Test Plan mục 9) |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Xác định MR thuộc loại gây phá vỡ (đổi chữ ký điểm mở rộng hoặc cấu trúc dữ liệu). | MR được gắn nhãn/phân loại 'gây phá vỡ'. |
| 2 | Tìm script nâng cấp trong `custom-addons/dwo_sla_core/migrations/<version>/`. | Có script `pre-`/`post-migration` xử lý dữ liệu hiện có. |
| 3 | Mở `docs/010_...Requirements-Specification.md`, mục Revision History. | Có dòng mới nêu thay đổi và phiên bản. |

**Pass/Fail Criteria:** ✅ Pass: Có phân loại, script nâng cấp và dòng Revision History. ❌ Fail: Thiếu bất kỳ mục nào.

**Postconditions:** Không: không thay đổi dữ liệu; lưu biên bản rà soát.

### TC-INS-016: Rà soát MR gây phá vỡ thiếu script nâng cấp bị đánh dấu không đạt

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-INS-05 |
| Coverage Item | CI-2 (MR gây phá vỡ thiếu migration (negative)) |
| Requirement Ref | REQ-CM-001 AC1 (negative) |
| Priority | P3-Medium |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. MR đổi chữ ký điểm mở rộng nhưng không có thư mục `migrations/` mới và không đổi Revision History.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| checklist | Danh sách kiểm tra MR |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Áp checklist MR gây phá vỡ lên MR này (checklist gồm: có script nâng cấp trong `migrations/`; có dòng Revision History). | Mục 'có script nâng cấp' và 'có dòng Revision History' đều không đạt. |
| 2 | Ghi quyết định rà soát. | MR bị đánh dấu 'cần sửa' (không được merge). |

**Pass/Fail Criteria:** ✅ Pass: Checklist phát hiện thiếu và chặn merge. ❌ Fail: Checklist cho qua MR thiếu migration.

**Postconditions:** Không: không thay đổi dữ liệu; lưu biên bản rà soát.

### TC-INS-017: Rà soát MR đổi cấu trúc dữ liệu SLA (đổi cột/CHECK) được phân loại gây phá vỡ

| Field | Giá trị |
|---|---|
| Test Condition Ref | TCOND-INS-05 |
| Coverage Item | CI-3 (Đổi cấu trúc dữ liệu cũng là thay đổi gây phá vỡ) |
| Requirement Ref | REQ-CM-001 Statement (cấu trúc dữ liệu) |
| Priority | P4-Low |
| Test Type | Inspection |
| Automation | Manual |

**Preconditions:**
1. MR đổi tên cột `sla_task.duration` hoặc đổi CHECK của `stage`.

**Test Data:**

| Field | Giá trị | Ghi chú |
|---|---|---|
| checklist | Danh sách kiểm tra MR |  |

**Steps & Expected Results:**

| Step | Action | Expected Result |
|---|---|---|
| 1 | Đọc diff của MR ở file model và `030_Database-Design.md`. | Xác định có thay đổi cấu trúc dữ liệu hiện có. |
| 2 | Đối chiếu bảng phân loại thay đổi trong Database Design (mục tiến hóa). | Loại 'Breaking'; yêu cầu script nâng cấp trong `migrations/` và dòng Revision History. |

**Pass/Fail Criteria:** ✅ Pass: Phân loại đúng là gây phá vỡ. ❌ Fail: Bị phân loại sai (non-breaking).

**Postconditions:** Không: không thay đổi dữ liệu; lưu biên bản rà soát.


---


## Bổ sung 19.0.1.1.0 cho TG-01 đến TG-20 (ca mới và biến thể)

Các ca dưới đây được thêm cho test đã có mà bản 0.2 của tài liệu chưa mô tả (ID nối tiếp nhóm cũ; không dùng lại ID của ca đã gỡ). Test chưa có ca riêng nhưng cùng mục tiêu với một ca cũ được ghi là biến thể trong bảng ánh xạ ở Phụ lục C.

### TC-BRE-024: Task `paused` không bị xử lý nền so với `planned_end_time`

- **Truy vết:** REQ-FUNC-022 (AC5) · TCOND-03-24 · P2-High · Negative · Automated: `test_bre_paused_task_not_breached_by_processor`
- **Precondition:** FX-DEF-STD, hạn T0+4h; task `in_progress`.
- **Bước → Kết quả:** (1) Pause lúc T0+1h. (2) Xử lý nền tại T0+10h (quá hạn) → `has_breached` = False.
- **Pass/Fail:** Pass nếu không vi phạm.

### TC-BRE-025: Phần trăm đã dùng của task đang chạy tính cả đoạn đang chạy

- **Truy vết:** REQ-INT-023 (AC4) · TCOND-03-25 · P1-Critical · Positive · Automated: `test_bre_017b_running_percent_live`
- **Precondition:** task `in_progress` mục tiêu 4 giờ, lịch `none`, gắn lúc T0.
- **Bước → Kết quả:** (1) Xem lúc T0+1h → `business_percent_used` = 25. (2) Xem lúc T0+5h → 125 (không cắt ở 100). Ở cả hai lần `business_duration` (cột lưu) vẫn 0,0 và stage `in_progress`.
- **Pass/Fail:** Pass nếu 25 và 125.

### TC-BRE-026: `settle_batch` cho kết quả bằng `settle` từng task

- **Truy vết:** REQ-INT-023, REQ-PERF-002 · TCOND-03-26 · P2-High · Positive · Automated: `test_bre_017c_settle_batch_equals_settle`
- **Precondition:** lịch FX-CAL-VN có ngày nghỉ T0+24h đến T0+48h; năm mốc start (T0, +5h, +30h, +100h, +400h); mốc kết thúc T0+300h.
- **Bước → Kết quả:** (1) Với lịch FX-CAL-VN và với "không có lịch": `settle_batch(calendar, starts, end)` từng phần tử bằng `settle(calendar, start, end)` (sai số 1e-6).
- **Pass/Fail:** Pass nếu mọi cặp bằng nhau.

### TC-PRC-001: `process_due` xử lý task đến hạn

- **Truy vết:** REQ-FUNC-022, REQ-REL-002 · TCOND-08-70 · P1-Critical · Positive · Automated: `test_process_due_handles_due_tasks`
- **Bước → Kết quả:** (1) Task mới có `next_due_at` = T0+4h. (2) Gọi `process_due()` tại T0+5h → `has_breached` True; `next_due_at` rỗng.
- **Pass/Fail:** Pass nếu đúng.

### TC-PRC-002: `process_due` bỏ qua task chưa đến hạn

- **Truy vết:** REQ-FUNC-022, REQ-REL-002 · TCOND-08-70 · P2-High · Negative · Automated: `test_process_due_skips_tasks_not_due`
- **Bước → Kết quả:** (1) Gọi `process_due()` tại T0+1h với task hạn T0+4h → `has_breached` False.
- **Pass/Fail:** Pass nếu không vi phạm.

### TC-PRC-003: `batch_size` là trần mỗi lần gọi `process_due`

- **Truy vết:** REQ-REL-002 (AC1) · TCOND-08-71 · P1-Critical · Boundary · Automated: `test_process_due_batch_size_caps_each_call`
- **Precondition:** `dwo_sla_core.batch_size` = 2; 3 task đều quá hạn tại T0+5h.
- **Bước → Kết quả:** (1) `process_due()` lần 1 → 2 task vi phạm. (2) Lần 2 → cả 3 task vi phạm.
- **Pass/Fail:** Pass nếu 2 rồi 3.

### TC-EML-001: Mốc email người nhận `fixed` gửi tới địa chỉ cố định

- **Truy vết:** REQ-FUNC-064 (AC1) · TCOND-08-72 · P1-Critical · Positive · Automated: `test_esc_060_fixed_email`
- **Precondition:** mốc 75% `action_type=email`, `email_recipient_type=fixed`, `email_fixed_address=oncall@example.com`.
- **Bước → Kết quả:** (1) Xử lý nền khi đạt 75% → đúng 1 `mail.mail` tới `oncall@example.com`, subject chứa tên định nghĩa; mốc nằm trong `done_escalation_ids`.
- **Pass/Fail:** Pass nếu đúng.

### TC-EML-002: Người nhận `field` đọc field email của record gốc

- **Truy vết:** REQ-FUNC-065 (AC4) · TCOND-08-72 · P1-Critical · Positive · Automated: `test_esc_061_field_email`
- **Bước → Kết quả:** (1) Mốc `field` trỏ `res.partner.email`; partner có email `customer@example.com`; xử lý nền → 1 mail tới địa chỉ đó.
- **Pass/Fail:** Pass nếu đúng.

### TC-EML-003: Người nhận `responsible` lấy email của user/partner ở field Many2one

- **Truy vết:** REQ-FUNC-065 (AC5) · TCOND-08-72 · P1-Critical · Positive · Automated: `test_esc_062_responsible_email`
- **Bước → Kết quả:** (1) Mốc `responsible` trỏ `res.partner.user_id`; gán user admin; xử lý nền → 1 mail tới email của admin.
- **Pass/Fail:** Pass nếu đúng.

### TC-EML-004: `responsible` trên field x2many: một mail, nhiều người nhận

- **Truy vết:** REQ-FUNC-065 (AC6) · TCOND-08-72 · P2-High · Positive · Automated: `test_esc_064_responsible_x2many_multiple_to`
- **Bước → Kết quả:** (1) Mốc `responsible` trỏ `child_ids`; hai liên hệ `a@example.com`, `b@example.com`; xử lý nền → đúng 1 mail có `email_to` = `a@example.com,b@example.com`.
- **Pass/Fail:** Pass nếu một mail, hai người nhận.

### TC-EML-005: Không resolve được người nhận: `escalate_failed`, không ném lỗi ra ngoài

- **Truy vết:** REQ-FUNC-065 (AC3), REQ-FUNC-026 · TCOND-08-73 · P1-Critical · Negative · Automated: `test_esc_063_no_recipient_marks_failed`
- **Bước → Kết quả:** (1) Mốc `field` trỏ `email`, partner không có email; xử lý nền (log ERROR được ghi nhận) → 1 event `escalate_failed`; không exception.
- **Pass/Fail:** Pass nếu đúng 1 event lỗi.

### TC-EML-006: Không có template: dùng nội dung mặc định

- **Truy vết:** REQ-FUNC-064 (AC3) · TCOND-08-74 · P2-High · Positive · Automated: `test_esc_065_no_template_falls_back_to_plain_body`
- **Bước → Kết quả:** (1) Mốc email `fixed` với `email_template_id` xoá; xử lý nền → 1 mail tới `oncall@example.com`, subject chứa tên định nghĩa, body chứa ký tự `%`.
- **Pass/Fail:** Pass nếu đúng.

### TC-EML-007: Template không thuộc model `sla.task` bị từ chối khi lưu

- **Truy vết:** REQ-FUNC-064 (AC4) · TCOND-08-74 · P2-High · Negative · Automated: `test_esc_066_template_wrong_model_rejected`
- **Bước → Kết quả:** (1) Lưu mốc email với template của model `res.partner` → `ValidationError`.
- **Pass/Fail:** Pass nếu bị từ chối.

### TC-ERR-030: Exception gốc trích giá trị field: ghi chú và log chỉ còn `<redacted>`

- **Truy vết:** REQ-OBS-003 (AC2), REQ-FUNC-026 · TCOND-12-30 · P1-Critical · Negative · Automated: `test_err_011b_raw_exception_values_redacted`
- **Precondition:** mốc 50% với server action `raise UserError('failed for ' + record.comment)`; partner `comment`='SECRET-123'.
- **Bước → Kết quả:** (1) Xử lý nền tại T0+2h (log ERROR được thu) → log không chứa `SECRET-123`; `note` của event `escalate_failed` chứa "failed for" và `<redacted>`, không chứa `SECRET-123`.
- **Pass/Fail:** Pass nếu giá trị nhạy cảm không lộ.

### TC-CMP-017: Điều kiện start dùng field related không lưu vẫn gắn task khi field nguồn đổi

- **Truy vết:** REQ-FUNC-005, REQ-FUNC-042 · TCOND-13-17 · P1-Critical · Regression · Automated: `test_start_on_unstored_related_field_still_attaches`
- **Precondition:** start `[('country_code','=','VN')]` (`country_code` là related không lưu), các điều kiện khác trống; partner chưa có quốc gia.
- **Bước → Kết quả:** (1) Chưa có task. (2) Ghi `country_id` = Việt Nam lúc T0+1h → có đúng 1 task.
- **Pass/Fail:** Pass nếu task được gắn.

### TC-INF-036: Không xoá được công ty hoặc lịch đang được định nghĩa dùng (RESTRICT)

- **Truy vết:** REQ-FUNC-001 (AC4), `030` mục 4 · TCOND-14-36 · P2-High · Negative · Automated: `test_inf_ondelete_company_calendar_restricted`
- **Precondition:** định nghĩa "Scoped" gán công ty "SLA Co"; định nghĩa "Fixed" dùng lịch FX-CAL-VN.
- **Bước → Kết quả:** (1) Xoá công ty → lỗi CSDL. (2) Xoá lịch → lỗi CSDL. (3) Cả hai vẫn tồn tại.
- **Pass/Fail:** Pass nếu cả hai bị chặn.

### TC-INF-037: `next_due_at` chỉ có một index từng phần

- **Truy vết:** REQ-PERF-003, `030` mục 6 · TCOND-14-37 · P3-Low · Positive · Automated: `test_inf_next_due_at_only_partial_index`
- **Bước → Kết quả:** (1) Truy vấn `pg_indexes` của bảng `sla_task` với index chứa `(next_due_at)` → đúng 1 index và có mệnh đề `WHERE`.
- **Pass/Fail:** Pass nếu một index từng phần.

### TC-SEC-025: Quản trị hệ thống mặc định là SLA Manager

- **Truy vết:** REQ-SEC-001 (AC5) · TCOND-16-25 · P1-Critical · Positive · Automated: `test_sec_admin_default_sla_manager`
- **Bước → Kết quả:** (1) `group_sla_manager` nằm trong `implied_ids` của `base.group_system`. (2) User `admin` có `group_sla_manager` và `group_sla_user`. (3) Một user nội bộ được thêm `base.group_system` cũng có `group_sla_manager`, và thấy menu gốc SLA.
- **Pass/Fail:** Pass nếu cả ba đúng.

### TC-PRF-011: Tải 300 ticket x 30 task (opt-in `SLA_PERF=1`)

- **Truy vết:** REQ-PERF-001, REQ-PERF-002, REQ-REL-002 · TCOND-18-11 · P3-Low · Performance · Automated, chỉ chạy khi đặt `SLA_PERF=1`: `test_prf_load_300_tickets_30_tasks`
- **Precondition:** 30 định nghĩa cùng khớp, 6 định nghĩa có mốc email 50/75/100% (9000 task, 1800 task có escalation).
- **Bước → Kết quả:** (1) Đo từng pha (attach, ghi hàng loạt, stop hàng loạt, `process_due`) và ghi log tiền tố "SLA-PERF" → không lỗi; số liệu ghi vào Test Summary Report.
- **Pass/Fail:** Pass nếu mọi pha hoàn tất; ngưỡng thời gian lấy từ Test Plan.

### TC-PRF-012: Đọc `business_percent_used` của 80 task (một trang list), có lịch và không lịch

- **Truy vết:** REQ-INT-023, REQ-PERF-002 · TCOND-18-12 · P2-High · Performance · Automated, opt-in `SLA_PERF=1`: `test_prf_percent_used_list_80`
- **Bước → Kết quả:** (1) 80 task `in_progress` cho mỗi cấu hình (không lịch, lịch FX-CAL-VN); tại T0+2h đọc `business_percent_used` → mọi giá trị = 50; số truy vấn và thời gian được ghi log.
- **Pass/Fail:** Pass nếu mọi giá trị bằng 50.

### TC-PRF-013: Như TC-PRF-012 với lịch có ngày nghỉ lễ và task chạy 120 ngày

- **Truy vết:** REQ-INT-023, REQ-PERF-002 · TCOND-18-12 · P3-Low · Performance · Automated, opt-in `SLA_PERF=1`: `test_prf_percent_used_list_80_holidays`
- **Bước → Kết quả:** (1) Lịch có 11 ngày nghỉ/năm x 3 năm; 80 task đã chạy 120 ngày; đọc `business_percent_used` → hoàn tất, thời gian được ghi log.
- **Pass/Fail:** Pass nếu hoàn tất không lỗi.

## TG-21 — Field metadata của định nghĩa (type, vendor, service commitment, target)

Fixture: FX-DEF-STD trên `res.partner` (hàm `make_definition`). Không có task nào cần dựng trừ ca TC-MDF-010.

### TC-MDF-001: Định nghĩa không truyền `type`: mặc định `sla`

- **Truy vết:** REQ-FUNC-070 (AC1) · TCOND-28-01 · P3-Low · Positive · Automated: `test_type_default_sla`
- **Precondition:** module đã cài.
- **Bước → Kết quả mong đợi:** (1) Tạo định nghĩa không truyền `type` → `type` = `sla`.
- **Pass/Fail:** Pass nếu `type == 'sla'`; Fail nếu khác.

### TC-MDF-002: Định nghĩa với `type='ola'`: lưu và đọc lại đúng

- **Truy vết:** REQ-FUNC-070 (AC1) · TCOND-28-01 · P3-Low · Positive · Automated: `test_type_ola`
- **Bước → Kết quả:** (1) Tạo định nghĩa `type='ola'` → đọc lại `type` = `ola`.
- **Pass/Fail:** Pass nếu `type == 'ola'`.

### TC-MDF-003: Chọn nhà cung cấp (`vendor_id`): lưu đúng partner

- **Truy vết:** REQ-FUNC-070 (AC2) · TCOND-28-02 · P3-Low · Positive · Automated: `test_vendor_id_set`
- **Precondition:** partner "Vendor Co" đã tạo.
- **Bước → Kết quả:** (1) Tạo định nghĩa với `vendor_id` = Vendor Co → `d.vendor_id` = Vendor Co.
- **Pass/Fail:** Pass nếu đúng partner.

### TC-MDF-004: Không chọn nhà cung cấp: `vendor_id` rỗng

- **Truy vết:** REQ-FUNC-070 (AC2) · TCOND-28-02 · P3-Low · Positive · Automated: `test_vendor_id_default_empty`
- **Bước → Kết quả:** (1) Tạo định nghĩa không truyền `vendor_id` → `vendor_id` rỗng.
- **Pass/Fail:** Pass nếu rỗng.

### TC-MDF-005: Không truyền `service_commitment`: mặc định `False`

- **Truy vết:** REQ-FUNC-070 (AC3) · TCOND-28-03 · P3-Low · Positive · Automated: `test_service_commitment_default_false`
- **Bước → Kết quả:** (1) Tạo định nghĩa mặc định → `service_commitment` = `False`.
- **Pass/Fail:** Pass nếu `False`.

### TC-MDF-006: `service_commitment=True`: lưu đúng

- **Truy vết:** REQ-FUNC-070 (AC3) · TCOND-28-03 · P3-Low · Positive · Automated: `test_service_commitment_true`
- **Bước → Kết quả:** (1) Tạo định nghĩa `service_commitment=True` → đọc lại `True`.
- **Pass/Fail:** Pass nếu `True`.

### TC-MDF-007: Không chọn `target`: rỗng

- **Truy vết:** REQ-FUNC-070 (AC4) · TCOND-28-04 · P3-Low · Positive · Automated: `test_target_default_empty`
- **Bước → Kết quả:** (1) Tạo định nghĩa mặc định → `target` rỗng.
- **Pass/Fail:** Pass nếu rỗng.

### TC-MDF-008: `target='response'`: lưu đúng

- **Truy vết:** REQ-FUNC-070 (AC4) · TCOND-28-04 · P3-Low · Positive · Automated: `test_target_response`
- **Bước → Kết quả:** (1) Tạo định nghĩa `target='response'` → đọc lại `response`.
- **Pass/Fail:** Pass nếu `response`.

### TC-MDF-009: `target='resolution'`: lưu đúng

- **Truy vết:** REQ-FUNC-070 (AC4) · TCOND-28-04 · P3-Low · Positive · Automated: `test_target_resolution`
- **Bước → Kết quả:** (1) Tạo định nghĩa `target='resolution'` → đọc lại `resolution`.
- **Pass/Fail:** Pass nếu `resolution`.

### TC-MDF-010: Bốn field metadata không đổi hành vi engine

- **Truy vết:** REQ-FUNC-070 (AC5) · TCOND-28-05 · P2-High · Regression · Automated: `test_metadata_fields_do_not_change_engine_behaviour`
- **Precondition:** định nghĩa `type='ola'`, `service_commitment=True`, `target='response'`, start khớp `ref`=NEW.
- **Bước → Kết quả:** (1) Tạo partner `ref`='NEW' → có đúng 1 task, `stage` = `in_progress`.
- **Pass/Fail:** Pass nếu task được gắn như định nghĩa thường; Fail nếu không gắn hoặc stage khác.

## TG-22 — Retroactive pause

Fixture: FX-RETRO-PAUSE: field manual `x_hold3` (boolean, `tracking=1`) và `x_retro3` (datetime) trên `res.partner`; định nghĩa `retroactive=True`, `start_field_id=x_retro3`, `pause_domain=[('x_hold3','=',True)]`, `duration`=4, lịch `none`. `ict(d,h)` = 2026-03-`d` giờ `h` ICT đổi sang UTC. Lịch sử pause dựng bằng `mail.message` + `mail.tracking.value` (không qua `write()`), vì mail.thread gộp các lần đổi trong một giao dịch.

### TC-RPS-001: Model không có `mail.thread`: cảnh báo nêu rõ model

- **Truy vết:** REQ-FUNC-071 (AC1) · TCOND-29-01 · P2-High · Negative · Automated: `test_warning_model_not_trackable`
- **Precondition:** model `res.partner.category` (không có `mail.thread`).
- **Bước → Kết quả:** (1) Tạo định nghĩa trên model đó với `retroactive_pause=True` → lưu được (không bị chặn); `retroactive_pause_warning` chứa "not change-tracked" và tên model `res.partner.category`.
- **Pass/Fail:** Pass nếu cảnh báo đúng nội dung và lưu thành công.

### TC-RPS-002: Field trong `pause_domain` không bật tracking: cảnh báo nêu tên field

- **Truy vết:** REQ-FUNC-071 (AC1) · TCOND-29-01 · P2-High · Negative · Automated: `test_warning_field_not_tracked`
- **Precondition:** FX-DEF-STD (`pause_domain` dùng `ref`, không `tracking=True`).
- **Bước → Kết quả:** (1) Tạo định nghĩa `retroactive_pause=True` → cảnh báo không rỗng và chứa `ref`.
- **Pass/Fail:** Pass nếu cảnh báo nêu `ref`.

### TC-RPS-003: Mọi field pause đều có tracking: không cảnh báo

- **Truy vết:** REQ-FUNC-071 (AC1) · TCOND-29-01 · P3-Low · Positive · Automated: `test_no_warning_when_all_pause_fields_tracked`
- **Precondition:** field `x_hold_w1` boolean `tracking=1`.
- **Bước → Kết quả:** (1) Tạo định nghĩa `retroactive_pause=True`, `pause_domain=[('x_hold_w1','=',True)]` → `retroactive_pause_warning` rỗng.
- **Pass/Fail:** Pass nếu rỗng.

### TC-RPS-004: Tính năng tắt: không tính cảnh báo

- **Truy vết:** REQ-FUNC-071 (AC1) · TCOND-29-01 · P3-Low · Positive · Automated: `test_no_warning_when_feature_off`
- **Bước → Kết quả:** (1) Tạo định nghĩa `retroactive_pause=False` (pause dùng `ref` không tracking) → cảnh báo rỗng.
- **Pass/Fail:** Pass nếu rỗng.

### TC-RPS-005: Đổi `pause_domain`: cảnh báo tính lại

- **Truy vết:** REQ-FUNC-071 (AC1) · TCOND-29-01 · P3-Low · Positive · Automated: `test_warning_recomputes_when_pause_domain_changes`
- **Precondition:** field `x_hold_w2` `tracking=1`; định nghĩa `retroactive_pause=True`, pause dùng `ref`.
- **Bước → Kết quả:** (1) Đọc cảnh báo → có. (2) Đổi `pause_domain` sang `x_hold_w2` → cảnh báo rỗng.
- **Pass/Fail:** Pass nếu cảnh báo mất sau bước 2.

### TC-RPS-006: Có lịch sử pause trong khoảng quá khứ: trừ đúng thời gian pause, dời hạn

- **Truy vết:** REQ-FUNC-071 (AC2) · TCOND-29-02 · P1-Critical · Positive · Automated: `test_excludes_tracked_pause_history`
- **Precondition:** FX-RETRO-PAUSE, `retroactive_pause=True`; mốc `x_retro3` = 08:00 ICT; lịch sử tracking `x_hold3` False → True lúc 09:00 ICT, vẫn True lúc attach; `now` = 11:00 ICT.
- **Bước → Kết quả:** (1) Gọi `evaluate(P, now=11:00)` → 1 task; `start_time` = 08:00 ICT; `business_duration` = `duration` = 1,0 giờ; `business_pause_duration` = `pause_duration` = 2,0 giờ; `planned_end_time` = 08:00 + 6 giờ; `original_breach_time` = `planned_end_time`; `has_breached` = False.
- **Pass/Fail:** Pass nếu mọi giá trị khớp (sai số 0,001); Fail nếu hạn chót vẫn là 12:00.

### TC-RPS-007: Cùng lịch sử nhưng `retroactive_pause` tắt: không trừ gì

- **Truy vết:** REQ-FUNC-071 (AC3) · TCOND-29-03 · P2-High · Negative · Automated: `test_flag_off_counts_full_backdated_window`
- **Precondition:** FX-RETRO-PAUSE; partner có `x_hold3` True 09:00 rồi False 10:00 (ghi qua hook); `retroactive_pause=False`.
- **Bước → Kết quả:** (1) `evaluate(P, now=11:00)` → `business_duration` = 3,0; `business_pause_duration` = 0; `planned_end_time` = 08:00 + 4 giờ.
- **Pass/Fail:** Pass nếu không trừ pause.

### TC-RPS-008: Không có thay đổi tracking trong khoảng: không trừ gì

- **Truy vết:** REQ-FUNC-071 (AC3) · TCOND-29-03 · P2-High · Positive · Automated: `test_no_history_in_window_no_effect`
- **Precondition:** `retroactive_pause=True`; `x_hold3` giữ mặc định False suốt khoảng.
- **Bước → Kết quả:** (1) `evaluate(P, now=11:00)` → `business_duration` = 3,0; `business_pause_duration` = 0.
- **Pass/Fail:** Pass nếu khớp.

### TC-RPS-009: Field pause không tracking: bỏ qua, không trừ dù tính năng bật

- **Truy vết:** REQ-FUNC-071 (AC4) · TCOND-29-04 · P2-High · Negative · Automated: `test_untracked_pause_field_falls_back_no_effect`
- **Precondition:** `x_retro4` datetime; định nghĩa `retroactive=True`, `retroactive_pause=True`, `pause_domain=[('ref','=','HOLD')]`.
- **Bước → Kết quả:** (1) `evaluate(P, now=11:00)` với `x_retro4`=08:00 → `business_duration` = 3,0; `business_pause_duration` = 0.
- **Pass/Fail:** Pass nếu không trừ gì.

## TG-23 — Timezone override của lịch (bản sao calendar)

Fixture: FX-CAL-VN (`make_calendar`: tz `Asia/Ho_Chi_Minh`, T2–T6 08:00–17:00), định nghĩa `schedule_source='definition'`.

### TC-TZO-001: Timezone SLA khác tz của lịch: hạn chót tính theo tz của SLA

- **Truy vết:** REQ-FUNC-067 (AC2) · TCOND-30-01 · P1-Critical · Positive · Automated: `test_override_shifts_working_hours`
- **Precondition:** hai định nghĩa trên cùng lịch FX-CAL-VN, `duration`=2: D-plain (tz mặc định của lịch) và D-override (`calendar_tz_override='UTC'`); hai partner `ref`='NEW' tạo tại T0 (02:00 UTC = 09:00 ICT).
- **Bước → Kết quả:** (1) Task của D-plain → `planned_end_time` = 04:00 UTC. (2) Task của D-override → `planned_end_time` = 10:00 UTC (02:00 UTC trước giờ làm 08:00–17:00 UTC nên dời tới 08:00 rồi cộng 2 giờ). (3) Hai hạn chót khác nhau.
- **Pass/Fail:** Pass nếu đúng hai giá trị.

### TC-TZO-002: Hai định nghĩa cùng lịch, cùng tz: dùng chung một bản sao

- **Truy vết:** REQ-FUNC-067 (AC4) · TCOND-30-02 · P2-High · Positive · Automated: `test_override_reuses_cached_clone_no_duplicate`
- **Precondition:** hai định nghĩa D-1, D-2 cùng lịch, `calendar_tz_override='UTC'`.
- **Bước → Kết quả:** (1) Tạo partner `ref`='NEW' (gắn cả hai) → số `resource.calendar` có `sla_tz_override_source_id` = lịch gốc và `tz`='UTC' là 1.
- **Pass/Fail:** Pass nếu đúng 1 bản sao.

### TC-TZO-003: Lịch gốc không bị đổi timezone

- **Truy vết:** REQ-FUNC-067 (AC4) · TCOND-30-02 · P1-Critical · Negative · Automated: `test_override_does_not_mutate_source_calendar`
- **Bước → Kết quả:** (1) Định nghĩa `calendar_tz_override='UTC'`, tạo partner `ref`='NEW' → `cal.tz` vẫn `Asia/Ho_Chi_Minh`.
- **Pass/Fail:** Pass nếu `tz` không đổi.

### TC-TZO-004: Bản sao giữ nguyên khung giờ làm của lịch gốc

- **Truy vết:** REQ-FUNC-067 (AC4) · TCOND-30-02 · P2-High · Positive · Automated: `test_clone_copies_attendance_pattern`
- **Bước → Kết quả:** (1) Sau khi attach với tz override UTC → có đúng 1 bản sao và `len(clone.attendance_ids)` = `len(cal.attendance_ids)`.
- **Pass/Fail:** Pass nếu bằng nhau.

### TC-TZO-005: Tz của SLA trùng tz của lịch: không tạo bản sao

- **Truy vết:** REQ-FUNC-067 (AC5) · TCOND-30-03 · P2-High · Positive · Automated: `test_no_override_no_clone_created`
- **Bước → Kết quả:** (1) Định nghĩa dùng lịch FX-CAL-VN, tz mặc định theo lịch, tạo partner `ref`='NEW' → không có `resource.calendar` nào có `sla_tz_override_source_id` = lịch gốc.
- **Pass/Fail:** Pass nếu không có bản sao.

## TG-24 — Hạn chót ban đầu và thời lượng giờ đồng hồ

### TC-CLK-001: `original_breach_time` đặt một lần lúc attach, không đổi khi resume

- **Truy vết:** REQ-FUNC-072 (AC1) · TCOND-31-01 · P1-Critical · Positive · Automated: `test_set_once_at_attach_never_rewritten_on_resume`
- **Precondition:** FX-DEF-STD, lịch `none`, duration 4; partner `ref`='NEW' tại T0.
- **Bước → Kết quả:** (1) Đọc `original_breach_time` = T0 + 4h. (2) Pause lúc T0+1h (`ref`=HOLD), resume lúc T0+3h (`ref`=WORK). (3) `original_breach_time` giữ T0 + 4h; `planned_end_time` = T0 + 6h; hai giá trị khác nhau.
- **Pass/Fail:** Pass nếu `original_breach_time` không đổi.

### TC-CLK-002: Apply Current Settings không đổi `original_breach_time`

- **Truy vết:** REQ-FUNC-072 (AC1) · TCOND-31-01 · P2-High · Negative · Automated: `test_unaffected_by_action_recalculate`
- **Precondition:** task đang chạy; user SLA Manager.
- **Bước → Kết quả:** (1) Manager gọi `action_recalculate` → `original_breach_time` giữ nguyên.
- **Pass/Fail:** Pass nếu không đổi.

### TC-CLK-003: Không có lịch (24x7): `duration`/`pause_duration` bằng bản giờ làm việc

- **Truy vết:** REQ-FUNC-072 (AC2) · TCOND-31-02 · P2-High · Positive · Automated: `test_equals_business_without_calendar`
- **Precondition:** FX-DEF-STD lịch `none`.
- **Bước → Kết quả:** (1) Attach T0, pause T0+2h, resume T0+5h, stop T0+9h. (2) `business_duration` = `duration` = 6,0; `business_pause_duration` = `pause_duration` = 3,0.
- **Pass/Fail:** Pass nếu các cặp bằng nhau và đúng 6,0 / 3,0.

### TC-CLK-004: Có lịch, pause qua cuối tuần: giờ đồng hồ khác giờ làm việc

- **Truy vết:** REQ-FUNC-072 (AC2) · TCOND-31-02 · P1-Critical · Positive · Automated: `test_differs_from_business_across_weekend`
- **Precondition:** lịch FX-CAL-VN, `schedule_source='definition'`.
- **Bước → Kết quả:** (1) Attach; pause thứ Sáu 17:00 ICT (ngày 6); resume thứ Hai 08:00 ICT (ngày 9). (2) `business_pause_duration` = 0,0; `pause_duration` = 63,0; hai giá trị khác nhau.
- **Pass/Fail:** Pass nếu 0,0 và 63,0.

## TG-25 — Bật/tắt định nghĩa, domain `[]` là chưa cấu hình, timezone bắt buộc

Quy ước: `MATCH_ALL` = `[('id', '!=', 0)]`. Hàm `make_definition` mặc định `active=True`, lịch `none`, FX-DEF-STD.

### TC-ENB-001: Định nghĩa tạo mới không truyền `active`: mặc định tắt, start là `[]`

- **Truy vết:** REQ-FUNC-066 (AC1) · TCOND-20-01 · P1-Critical · Positive · Automated: `test_new_definition_is_disabled_by_default`
- **Bước → Kết quả:** (1) Tạo định nghĩa chỉ có `name`, `model_id`, `duration` → `active` = False; `start_domain` = `[]`.
- **Pass/Fail:** Pass nếu cả hai đúng.

### TC-ENB-002: `model_name` là related có lưu, theo `model_id`

- **Truy vết:** REQ-FUNC-001 (AC1), REQ-INT-001 · TCOND-20-02 · P2-High · Positive · Automated: `test_model_name_related_stored`
- **Bước → Kết quả:** (1) Tạo FX-DEF-STD → `model_name` = `res.partner` (không truyền tay). (2) Đổi `model_id` sang `res.partner.category` → `model_name` = `res.partner.category`.
- **Pass/Fail:** Pass nếu `model_name` đổi theo.

### TC-ENB-003: Enable/Disable đảo `active` và trả về soft reload

- **Truy vết:** REQ-FUNC-066 (AC2) · TCOND-20-03 · P1-Critical · Positive · Automated: `test_enable_disable_toggle_and_reload`
- **Precondition:** định nghĩa `active=False` có start cấu hình.
- **Bước → Kết quả:** (1) `action_enable()` → `active` True; action trả `tag='soft_reload'`. (2) `action_disable()` → `active` False; `tag='soft_reload'`.
- **Pass/Fail:** Pass nếu trạng thái và tag đúng.

### TC-ENB-004: Enable khi start chưa cấu hình: bật được kèm cảnh báo

- **Truy vết:** REQ-FUNC-066 (AC3) · TCOND-20-03 · P1-Critical · Negative · Automated: `test_enable_without_start_warns_but_enables`
- **Precondition:** định nghĩa `active=False`, `start_domain='[]'`.
- **Bước → Kết quả:** (1) `action_enable()` → `active` True; action là `display_notification`, `params.type` = `warning`, `params.next.tag` = `soft_reload`.
- **Pass/Fail:** Pass nếu bật được và có cảnh báo.

### TC-ENB-005: Định nghĩa đã bật gắn task cho record mới, định nghĩa tắt thì không

- **Truy vết:** REQ-FUNC-066 (AC1, AC2) · TCOND-20-04 · P1-Critical · Positive · Automated: `test_enabled_attaches_disabled_does_not`
- **Precondition:** định nghĩa `active=False`; partner `ref`='NEW'.
- **Bước → Kết quả:** (1) Không có task. (2) `action_enable()`, rồi ghi `ref`='WORK' lúc T0+1h → có đúng 1 task.
- **Pass/Fail:** Pass nếu chỉ gắn sau khi bật.

### TC-ENB-006: Định nghĩa tắt còn task đang chạy: model vẫn được patch; hết task thì gỡ

- **Truy vết:** REQ-FUNC-066 (AC4) · TCOND-20-05 · P1-Critical · Positive · Automated: `test_hook_models_disabled_with_running_task`
- **Precondition:** định nghĩa bật, 1 task `in_progress`; sau đó đặt `active=False`.
- **Bước → Kết quả:** (1) `_get_hook_models()` chứa `res.partner`. (2) Ghi `ref`='DONE' → task `achieved`. (3) `_get_hook_models()` không còn `res.partner`.
- **Pass/Fail:** Pass nếu cả ba bước đúng.

### TC-ENB-007: Định nghĩa tắt, không có task đang chạy: engine không so khớp điều kiện

- **Truy vết:** REQ-FUNC-066 (AC5), REQ-PERF-001 · TCOND-20-05 · P2-High · Positive · Automated: `test_disabled_without_running_task_skips_condition_matching`
- **Precondition:** định nghĩa `active=False`; partner `ref`='NEW'; `Engine._match_sets` được bọc mock.
- **Bước → Kết quả:** (1) `evaluate(P, T0)` → `_match_sets` không được gọi; không có task.
- **Pass/Fail:** Pass nếu mock không bị gọi.

### TC-ENB-008: Định nghĩa tắt nhưng còn task đang chạy: vẫn đánh giá, task kết thúc khi stop khớp

- **Truy vết:** REQ-FUNC-066 (AC4), REQ-FUNC-060 · TCOND-20-05 · P1-Critical · Positive · Automated: `test_disabled_with_running_task_still_evaluated`
- **Bước → Kết quả:** (1) Tạo task, đặt `active=False`. (2) Ghi `ref`='DONE' lúc T0+1h → task `achieved`.
- **Pass/Fail:** Pass nếu `achieved`.

### TC-CND-001: `_get_domain` trả `None` cho `[]`, domain thật cho điều kiện đã cấu hình

- **Truy vết:** REQ-FUNC-003 (AC2) · TCOND-20-06 · P1-Critical · Positive · Automated: `test_get_domain_empty_list_is_none`
- **Bước → Kết quả:** (1) Định nghĩa `start_domain='[]'` → `_get_domain('start')` là `None`; `_get_domain('stop')` = `[('ref','=','DONE')]`.
- **Pass/Fail:** Pass nếu đúng cả hai.

### TC-CND-002: Start `[]` không bao giờ gắn task

- **Truy vết:** REQ-FUNC-003 (AC2) · TCOND-20-06 · P1-Critical · Negative · Automated: `test_start_empty_list_never_attaches`
- **Bước → Kết quả:** (1) Định nghĩa `start_domain='[]'`; tạo partner `ref`='NEW' → không có task.
- **Pass/Fail:** Pass nếu không có task.

### TC-CND-003: Start `MATCH_ALL` gắn task cho mọi record

- **Truy vết:** REQ-FUNC-003 (AC2) · TCOND-20-06 · P1-Critical · Positive · Automated: `test_start_match_all_attaches`
- **Bước → Kết quả:** (1) Định nghĩa `start_domain=MATCH_ALL`; tạo partner `ref`=False → có đúng 1 task.
- **Pass/Fail:** Pass nếu 1 task.

### TC-CND-004: Stop `[]` không bao giờ kết thúc task

- **Truy vết:** REQ-FUNC-003 (AC1) · TCOND-20-06 · P1-Critical · Negative · Automated: `test_stop_empty_list_never_completes`
- **Bước → Kết quả:** (1) Định nghĩa `stop_domain='[]'`, `start_domain=MATCH_ALL`; partner `ref`='NEW', ghi `ref`='DONE' lúc T0+1h → task vẫn `in_progress`.
- **Pass/Fail:** Pass nếu `in_progress`.

### TC-CND-005: Mọi điều kiện `[]`: hook không đặt dấu `*` (không chạy engine ở mỗi lần ghi)

- **Truy vết:** REQ-FUNC-003, REQ-PERF-001 · TCOND-20-07 · P2-High · Positive · Automated: `test_new_definition_has_no_star_watch`
- **Bước → Kết quả:** (1) Tạo định nghĩa mới chỉ có tên, model, duration → `_get_watched_field_names('res.partner')` không chứa `*`.
- **Pass/Fail:** Pass nếu không có `*`.

### TC-CND-006: Điều kiện reset có domain nhưng không có field theo dõi: theo dõi mọi field (`*`)

- **Truy vết:** REQ-FUNC-013, REQ-FUNC-051 · TCOND-20-07 · P2-High · Positive · Automated: `test_reset_condition_without_fields_watches_all`
- **Bước → Kết quả:** (1) Định nghĩa `reset_domain=[('ref','=','RESET')]`, không đặt field theo dõi → `_get_watched_field_names('res.partner')` chứa `*`.
- **Pass/Fail:** Pass nếu chứa `*`.

### TC-TZR-001: Tạo định nghĩa không truyền timezone: điền tz của người dùng hoặc `UTC`

- **Truy vết:** REQ-FUNC-067 (AC6) · TCOND-20-08 · P1-Critical · Positive · Automated: `test_create_fills_user_tz_or_utc`
- **Bước → Kết quả:** (1) Tạo FX-DEF-STD → `calendar_tz_override` = `env.user.tz` hoặc `UTC` nếu người dùng chưa có tz.
- **Pass/Fail:** Pass nếu đúng.

### TC-TZR-002: Nguồn `definition` với lịch cố định: điền tz của lịch

- **Truy vết:** REQ-FUNC-067 (AC6) · TCOND-20-08 · P1-Critical · Positive · Automated: `test_create_fills_fixed_calendar_tz`
- **Precondition:** lịch tz `Asia/Tokyo`.
- **Bước → Kết quả:** (1) Tạo định nghĩa `schedule_source='definition'`, `schedule_id`=lịch → `calendar_tz_override` = `Asia/Tokyo`.
- **Pass/Fail:** Pass nếu `Asia/Tokyo`.

### TC-TZR-003: Timezone truyền tường minh được giữ nguyên

- **Truy vết:** REQ-FUNC-067 (AC6) · TCOND-20-08 · P2-High · Positive · Automated: `test_create_keeps_explicit_tz`
- **Bước → Kết quả:** (1) Tạo định nghĩa `calendar_tz_override='Europe/Paris'` → giữ `Europe/Paris`.
- **Pass/Fail:** Pass nếu giữ nguyên.

### TC-TZR-004: Onchange trên bản ghi chưa lưu: luôn lấy tz của lịch

- **Truy vết:** REQ-FUNC-067 (AC6) · TCOND-20-09 · P2-High · Positive · Automated: `test_onchange_new_record_takes_calendar_tz`
- **Bước → Kết quả:** (1) Bản ghi `new()` nguồn `definition`, lịch tz `Asia/Tokyo`, tz đang là `UTC`; gọi `_onchange_schedule_suggest_tz` → tz = `Asia/Tokyo`.
- **Pass/Fail:** Pass nếu `Asia/Tokyo`.

### TC-TZR-005: Onchange trên bản ghi đã lưu: chỉ điền khi tz đang trống

- **Truy vết:** REQ-FUNC-067 (AC6) · TCOND-20-09 · P2-High · Positive · Automated: `test_onchange_saved_record_fills_only_when_empty`
- **Bước → Kết quả:** (1) Định nghĩa đã lưu tz `UTC`, lịch `Asia/Tokyo`; gọi onchange → vẫn `UTC`. (2) Xoá tz rồi gọi onchange → `Asia/Tokyo`.
- **Pass/Fail:** Pass nếu bước 1 giữ, bước 2 điền.

### TC-TZR-006: Onchange bỏ qua nguồn không phải `definition`

- **Truy vết:** REQ-FUNC-067 (AC6) · TCOND-20-09 · P3-Low · Negative · Automated: `test_onchange_ignores_non_definition_source`
- **Bước → Kết quả:** (1) Bản ghi `new()` `schedule_source='none'`, có `schedule_id` tz Tokyo; gọi onchange → tz khác `Asia/Tokyo`.
- **Pass/Fail:** Pass nếu tz không bị lấy từ lịch.

### TC-TZR-007: Form mới có sẵn tz mặc định và theo tz lịch khi chọn lịch

- **Truy vết:** REQ-FUNC-067 (AC1, AC6) · TCOND-20-10 · P1-Critical · Positive · Automated: `test_form_new_has_default_tz_and_follows_calendar`
- **Bước → Kết quả:** (1) Mở `Form` mới → tz = tz người dùng hoặc `UTC`. (2) Nhập tên, model; chọn nguồn `definition` và lịch Tokyo → tz = `Asia/Tokyo`. (3) Lưu → bản ghi có tz `Asia/Tokyo`.
- **Pass/Fail:** Pass nếu cả ba đúng.

### TC-TZR-008: Bản sao calendar theo tz sao chép ngày nghỉ chung

- **Truy vết:** REQ-FUNC-067 (AC7) · TCOND-20-11 · P2-High · Positive · Automated: `test_tz_variant_copies_global_leaves`
- **Precondition:** lịch FX-CAL-VN có 1 ngày nghỉ chung "Holiday" (2026-03-03).
- **Bước → Kết quả:** (1) `_sla_get_tz_variant(cal, 'UTC')` → bản sao có `global_leave_ids` tên "Holiday" và `date_from` bằng lịch gốc.
- **Pass/Fail:** Pass nếu sao chép đủ.

### TC-TZR-009: Đổi timezone định nghĩa không đổi hạn của task đang chạy

- **Truy vết:** REQ-FUNC-067 (AC2), REQ-FUNC-021 · TCOND-20-12 · P1-Critical · Positive · Automated: `test_changing_definition_tz_keeps_running_task_deadline`
- **Precondition:** định nghĩa nguồn `definition` lịch FX-CAL-VN, duration 2, có 1 task.
- **Bước → Kết quả:** (1) Ghi nhận `planned_end_time` và `schedule_id` của task. (2) Đặt `calendar_tz_override='UTC'` → task giữ nguyên cả hai.
- **Pass/Fail:** Pass nếu không đổi.

## TG-26 — Trải nghiệm form/list định nghĩa và task

Quy ước: `raw_task(definition, partner, stage, **extra)` tạo trực tiếp một `sla.task` (sudo) với `start_time` = T0, `target_duration` 4, `planned_end_time` = T0+4h, `running_since` = T0 khi `in_progress`. `arch(model, view_type)` lấy arch đã kế thừa của view. Với nhóm DUE: Settings `dwo_sla_core.due_soon_hours` = 4; ba định nghĩa Default (`due_soon_hours` trống), Short (1), Long (10); `now` = T0+1h; ba task `in_progress` cùng `planned_end_time` = now+3h.

### TC-DUE-001: Sắp đến hạn theo ngưỡng riêng của định nghĩa, nếu trống theo Settings

- **Truy vết:** REQ-INT-012 (AC4) · TCOND-21-01 · P1-Critical · Positive · Automated: `test_compute_uses_definition_then_settings`
- **Bước → Kết quả:** (1) Tính lại `is_due_soon` tại `now` → Default True (còn 3h ≤ 4h), Short False (3h > 1h), Long True (3h ≤ 10h).
- **Pass/Fail:** Pass nếu (True, False, True).

### TC-DUE-002: Đổi Settings chỉ tác động định nghĩa chưa đặt ngưỡng riêng

- **Truy vết:** REQ-INT-012 (AC3, AC5) · TCOND-21-01 · P2-High · Positive · Automated: `test_settings_change_applies_to_empty_only`
- **Bước → Kết quả:** (1) Đặt Settings = 2 → Default False (3h > 2h), Short False, Long True.
- **Pass/Fail:** Pass nếu (False, False, True).

### TC-DUE-003: Tìm kiếm `is_due_soon` đúng với các toán tử `=`, `!=`, `in`, `not in`

- **Truy vết:** REQ-INT-012 (AC4) · TCOND-21-02 · P1-Critical · Positive · Automated: `test_search_operators`
- **Bước → Kết quả:** (1) Với 8 domain trên `is_due_soon` (`= True`, `!= False`, `in [True]`, `= False`, `!= True`, `in [False]`, `not in [True]`, `not in [False]`) → tập kết quả lần lượt là {Default, Long} cho 3 domain đầu và `not in [False]`, {Short} cho các domain còn lại.
- **Pass/Fail:** Pass nếu cả 8 domain đúng.

### TC-DUE-004: Task paused hoặc đã vi phạm không bao giờ "sắp đến hạn"

- **Truy vết:** REQ-INT-012 (AC2) · TCOND-21-02 · P1-Critical · Negative · Automated: `test_search_excludes_breached_and_paused`
- **Precondition:** một task `paused` và một task `has_breached=True`, `planned_end_time` = now+1h, định nghĩa Long.
- **Bước → Kết quả:** (1) Tìm `is_due_soon = True` trên hai task → rỗng. (2) Tìm `is_due_soon = False` → cả hai task.
- **Pass/Fail:** Pass nếu đúng cả hai.

### TC-DUE-005: `due_soon_hours` âm bị CSDL từ chối

- **Truy vết:** REQ-INT-012 (AC5) · TCOND-21-03 · P2-High · Negative · Automated: `test_negative_value_rejected`
- **Bước → Kết quả:** (1) Ghi `due_soon_hours = -1` (trong savepoint) → phát sinh lỗi CHECK.
- **Pass/Fail:** Pass nếu có exception.

### TC-LCK-001: Định nghĩa đã có task không đổi được model

- **Truy vết:** REQ-FUNC-069 (AC1) · TCOND-21-04 · P1-Critical · Negative · Automated: `test_model_change_blocked_with_tasks`
- **Bước → Kết quả:** (1) Tạo task cho định nghĩa; đổi `model_id` sang `res.partner.category` → `ValidationError`; `model_name` vẫn `res.partner`.
- **Pass/Fail:** Pass nếu bị từ chối và model không đổi.

### TC-LCK-002: Ghi lại cùng model (kèm sửa field khác) vẫn được khi đã có task

- **Truy vết:** REQ-FUNC-069 (AC1) · TCOND-21-04 · P2-High · Positive · Automated: `test_same_model_write_allowed_with_tasks`
- **Bước → Kết quả:** (1) `write({'model_id': <res.partner>, 'duration': 6})` → thành công, `duration` = 6.
- **Pass/Fail:** Pass nếu `duration == 6`.

### TC-LCK-003: Định nghĩa chưa có task đổi model được

- **Truy vết:** REQ-FUNC-069 (AC1) · TCOND-21-04 · P2-High · Positive · Automated: `test_model_change_allowed_without_tasks`
- **Bước → Kết quả:** (1) Ghi `model_id` = `res.partner.category` cùng domain mới hợp lệ (start `MATCH_ALL`, các điều kiện khác `[]`) → `model_name` = `res.partner.category`.
- **Pass/Fail:** Pass nếu đổi được.

### TC-AUD-001: Đổi `duration` sinh dấu vết trong chatter

- **Truy vết:** REQ-FUNC-069 (AC3) · TCOND-21-05 · P2-High · Positive · Automated: `test_tracked_change_posts_message`
- **Bước → Kết quả:** (1) Tạo định nghĩa duration 4, chạy precommit; bật tracking, đổi `duration` = 8, chạy precommit → `message_ids.tracking_value_ids` có field `duration`.
- **Pass/Fail:** Pass nếu có.

### TC-AUD-002: Đổi điều kiện (`stop_domain`) được theo dõi

- **Truy vết:** REQ-FUNC-069 (AC3) · TCOND-21-05 · P2-High · Positive · Automated: `test_condition_change_is_tracked`
- **Bước → Kết quả:** (1) Đổi `stop_domain` sang `[('ref','=','CLOSED')]` (tracking bật) → tracking value có field `stop_domain`.
- **Pass/Fail:** Pass nếu có.

### TC-AUD-003: Form định nghĩa có chatter

- **Truy vết:** REQ-FUNC-069 (AC3) · TCOND-21-05 · P3-Low · Positive · Automated: `test_form_has_chatter`
- **Bước → Kết quả:** (1) Lấy arch form `sla.definition` → có phần tử `<chatter>`.
- **Pass/Fail:** Pass nếu có.

### TC-SBT-001: Số task đang chạy đếm `in_progress` và `paused`, không đếm task đã đóng

- **Truy vết:** REQ-INT-025 (AC1) · TCOND-21-06 · P1-Critical · Positive · Automated: `test_running_task_count_counts_in_progress_and_paused`
- **Precondition:** định nghĩa D có 3 task (`in_progress`, `paused`, `achieved`); định nghĩa Other có 1 task `in_progress`.
- **Bước → Kết quả:** (1) Đọc `running_task_count` → D = 2, Other = 1.
- **Pass/Fail:** Pass nếu (2, 1).

### TC-SBT-002: Định nghĩa không có task: số đếm bằng 0

- **Truy vết:** REQ-INT-025 (AC1) · TCOND-21-06 · P3-Low · Positive · Automated: `test_count_zero_without_tasks`
- **Bước → Kết quả:** (1) Định nghĩa mới → `running_task_count` = 0.
- **Pass/Fail:** Pass nếu 0.

### TC-SBT-003: Nút Running Tasks mở mọi task của đúng định nghĩa

- **Truy vết:** REQ-INT-025 (AC2) · TCOND-21-07 · P1-Critical · Positive · Automated: `test_action_opens_all_tasks_of_definition`
- **Precondition:** D có 2 task (một `achieved`); định nghĩa khác có 1 task.
- **Bước → Kết quả:** (1) `action_view_tasks()` → `res_model` = `sla.task`; `search(action['domain'])` trả 2 task; `context` = `{}` (không lọc theo trạng thái).
- **Pass/Fail:** Pass nếu đúng.

### TC-SBT-004: Form định nghĩa có nút `action_view_tasks` trong button box và `js_class`

- **Truy vết:** REQ-INT-025 (AC3), REQ-FUNC-069 (AC2) · TCOND-21-07 · P2-High · Positive · Automated: `test_form_arch_button_and_js_class`
- **Bước → Kết quả:** (1) Arch form có `js_class='sla_definition_form'`; (2) đúng 1 nút `action_view_tasks` trong `div[@name='button_box']`; (3) có field `running_task_count`.
- **Pass/Fail:** Pass nếu cả ba đúng.

### TC-DLV-001: List định nghĩa: mờ khi tắt, nút Enable/Disable có xác nhận, cột mặc định

- **Truy vết:** REQ-FUNC-066 (AC6) · TCOND-21-08 · P2-High · Positive · Automated: `test_list_arch`
- **Bước → Kết quả:** (1) `decoration-muted` = `not active`. (2) Các nút trên list: `action_enable`, `action_disable`, đều có thuộc tính `confirm`. (3) Cột hiển thị mặc định (không `optional`, không ẩn): `name`, `model_id`, `type`, `duration`, `schedule_source`, `calendar_tz_override`. (4) Không có cột `running_task_count`.
- **Pass/Fail:** Pass nếu cả bốn đúng.

### TC-DLV-002: Action của list hiện cả định nghĩa tắt và không nhóm sẵn

- **Truy vết:** REQ-FUNC-066 (AC6) · TCOND-21-08 · P2-High · Positive · Automated: `test_action_shows_inactive_without_grouping`
- **Bước → Kết quả:** (1) Context của `action_sla_definition` không chứa `search_default_group_model`. (2) Tìm theo domain của action → thấy định nghĩa `active=False`.
- **Pass/Fail:** Pass nếu đúng cả hai.

### TC-EHS-001: Tab Escalation của task chỉ liệt kê event `escalate` và `escalate_failed`

- **Truy vết:** REQ-INT-026 (AC1) · TCOND-21-09 · P2-High · Positive · Automated: `test_only_escalation_events`
- **Precondition:** task có 4 event: `escalate`, `escalate_failed`, `pause`, `error`.
- **Bước → Kết quả:** (1) `escalation_event_ids` = {`escalate`, `escalate_failed`}; `event_ids` vẫn 4.
- **Pass/Fail:** Pass nếu đúng.

### TC-EHS-002: Lịch sử escalation sắp mới nhất trước

- **Truy vết:** REQ-INT-026 (AC1) · TCOND-21-09 · P3-Low · Positive · Automated: `test_newest_first`
- **Bước → Kết quả:** (1) Hai event `escalate` lúc T0 và T0+2h → `escalation_event_ids` = [mới, cũ].
- **Pass/Fail:** Pass nếu mới trước cũ.

### TC-EHS-003: Form task hiển thị lịch sử escalation với 3 cột

- **Truy vết:** REQ-INT-026 (AC1) · TCOND-21-09 · P3-Low · Positive · Automated: `test_form_arch_lists_events`
- **Bước → Kết quả:** (1) Trang `escalation` của form task chứa `escalation_event_ids` với các cột `event_dt`, `event`, `note`.
- **Pass/Fail:** Pass nếu đúng thứ tự cột.

### TC-OSR-001: Nút Open Source Record mở form của record gốc

- **Truy vết:** REQ-INT-026 (AC2) · TCOND-21-10 · P1-Critical · Positive · Automated: `test_opens_source_record`
- **Bước → Kết quả:** (1) Gọi `action_open_source_record()` → action `ir.actions.act_window`, `res_model` = `res.partner`, `res_id` = id partner, `view_mode` = `form`, `target` = `current`.
- **Pass/Fail:** Pass nếu đúng năm giá trị.

### TC-OSR-002: Record gốc đã bị xoá: báo lỗi thân thiện

- **Truy vết:** REQ-INT-026 (AC3) · TCOND-21-10 · P2-High · Negative · Automated: `test_missing_record_friendly_error`
- **Bước → Kết quả:** (1) Xoá partner rồi gọi `action_open_source_record()` → `UserError` chứa "no longer exists".
- **Pass/Fail:** Pass nếu đúng thông báo.

### TC-OSR-003: Model của record gốc không còn tồn tại: báo lỗi thân thiện

- **Truy vết:** REQ-INT-026 (AC3) · TCOND-21-10 · P2-High · Negative · Automated: `test_unknown_model_friendly_error`
- **Bước → Kết quả:** (1) Đặt `res_model='x.not.installed'` rồi gọi action → `UserError` chứa "no longer exists".
- **Pass/Fail:** Pass nếu đúng thông báo.

### TC-OSR-004: Nút nằm trong header của form task, luôn hiện, không có trong list

- **Truy vết:** REQ-INT-026 (AC2) · TCOND-21-10 · P3-Low · Positive · Automated: `test_button_in_form_header_always_visible`
- **Bước → Kết quả:** (1) Đúng 1 nút `action_open_source_record` trong `//header`; thuộc tính `invisible` không có. (2) Không có nút này trong `list`.
- **Pass/Fail:** Pass nếu đúng.

### TC-TLV-001: List task: cột mặc định, thanh tiến độ, tô đỏ task vi phạm

- **Truy vết:** REQ-INT-027 (AC1) · TCOND-21-11 · P2-High · Positive · Automated: `test_default_columns_and_progressbar`
- **Bước → Kết quả:** (1) `decoration-danger` = `has_breached`. (2) Cột hiển thị mặc định: `sla_id`, `target_duration`, `schedule_id`, `stage`, `start_time`, `planned_end_time`, `business_duration_live`, `duration_live`, `business_percent_used`. (3) `business_percent_used` dùng widget `progressbar` có `overflow_class`. (4) `display_name`, `res_model`, `res_id` là `optional="hide"`.
- **Pass/Fail:** Pass nếu cả bốn đúng.

### TC-LGT-001: SCSS của widget chỉ có light mode

- **Truy vết:** REQ-INT-024 (AC5) · TCOND-21-12 · P3-Low · Positive · Automated: `test_scss_has_no_dark_block`
- **Bước → Kết quả:** (1) Đọc `static/src/sla_progress/sla_progress_widget.scss` → không chứa `prefers-color-scheme`.
- **Pass/Fail:** Pass nếu không có.

### TC-TOUR-001: Tour trình duyệt: lưu định nghĩa có task đang chạy hiện hộp xác nhận

- **Truy vết:** REQ-FUNC-069 (AC2) · TCOND-21-13 · P1-Critical · Positive · Automated (HttpCase tour): `test_confirm_save_with_running_tasks`
- **Precondition:** định nghĩa "Tour SLA" trên `res.partner` có 1 task `in_progress`; đăng nhập `admin`.
- **Bước → Kết quả:** (1) Chạy tour `dwo_sla_definition_confirm_save` trên `/odoo/action-dwo_sla_core.action_sla_definition/<id>` → bundle JS tải được, sửa điều kiện và lưu hiện hộp xác nhận nêu số task, tour hoàn tất.
- **Pass/Fail:** Pass nếu tour kết thúc không lỗi.

## TG-27 — Re-check Conditions (giới hạn một định nghĩa)

Fixture: `U-MGR` (`tg27_manager`, SLA Manager), `U-VIEW` (`tg27_viewer`, SLA User). `REL_STOP` = `[('parent_id.ref', '=', 'DONE')]` (điều kiện qua quan hệ: engine không tự đánh giá khi parent đổi, REQ-FUNC-042). `recheck(tasks, now)` = `tasks.with_user(U-MGR).action_reevaluate()` với đồng hồ giả `now`.

### TC-RCK-001: Re-check task của B không đụng task của A và không gắn task của định nghĩa C

- **Truy vết:** REQ-INT-020 (AC4), REQ-FUNC-032 (AC4) · TCOND-22-01 · P1-Critical · Positive · Automated: `test_scope_is_one_definition`
- **Precondition:** định nghĩa A, B (stop `REL_STOP`); parent P và child C1 (`ref`='NEW', `parent_id`=P) có task A và task B `in_progress`; định nghĩa C tạo sau (C1 chưa có task C); ghi `ref`='DONE' vào P lúc T0+1h (C1 không được ghi).
- **Bước → Kết quả:** (1) Hai task vẫn `in_progress`. (2) Re-check task B lúc T0+2h → task B `achieved`; task A vẫn `in_progress`; C1 không có task C. (3) Kết quả là `display_notification` với `next` = `soft_reload` và thông báo chứa "1 task(s) checked, 1 changed".
- **Pass/Fail:** Pass nếu đúng cả ba; Fail nếu task A đổi hoặc task C xuất hiện.

### TC-RCK-002: Task đã đóng không đổi nhưng vẫn ghi event `reevaluate` kèm người bấm

- **Truy vết:** REQ-INT-020 (AC3, AC5) · TCOND-22-02 · P1-Critical · Negative · Automated: `test_closed_task_unchanged_with_event`
- **Precondition:** task `achieved` (stop lúc T0+1h).
- **Bước → Kết quả:** (1) Re-check lúc T0+3h → `stage`, `end_time`, `business_duration` không đổi; thông báo "1 task(s) checked, 0 changed"; có đúng 1 event `reevaluate` có "No change" và tên manager trong `note`.
- **Pass/Fail:** Pass nếu đúng.

### TC-RCK-003: Task đổi stage: event ghi stage cũ và mới

- **Truy vết:** REQ-INT-020 (AC5) · TCOND-22-02 · P2-High · Positive · Automated: `test_changed_event_records_old_and_new_stage`
- **Precondition:** như TC-RCK-001 với một định nghĩa.
- **Bước → Kết quả:** (1) Re-check lúc T0+2h → event `reevaluate` có `event_dt` = T0+2h, `note` chứa "In Progress -> Achieved", `definition_id` = định nghĩa.
- **Pass/Fail:** Pass nếu đúng.

### TC-RCK-004: Nhiều task thuộc hai định nghĩa trong một lần bấm: mỗi task theo định nghĩa của nó

- **Truy vết:** REQ-INT-020 (AC4) · TCOND-22-03 · P2-High · Positive · Automated: `test_many_tasks_grouped_per_definition`
- **Bước → Kết quả:** (1) Hai task (A, B) của cùng record, điều kiện stop qua parent đã khớp; re-check cả hai → cả hai `achieved`; 2 event `reevaluate`; thông báo "2 task(s) checked, 2 changed".
- **Pass/Fail:** Pass nếu đúng.

### TC-RCK-005: SLA User không dùng được Re-check

- **Truy vết:** REQ-INT-020 (AC2), REQ-FUNC-032 (AC3) · TCOND-22-04 · P1-Critical · Negative · Automated: `test_viewer_cannot_recheck`
- **Bước → Kết quả:** (1) `U-VIEW` gọi `action_reevaluate` → `AccessError`.
- **Pass/Fail:** Pass nếu bị từ chối.

### TC-RCK-006: `Engine.evaluate(definitions=...)` chỉ xét định nghĩa được truyền

- **Truy vết:** REQ-FUNC-032 (AC4) · TCOND-22-05 · P1-Critical · Positive · Automated: `test_engine_definitions_param_limits_scope`
- **Precondition:** định nghĩa A có task cho partner P; định nghĩa B tạo sau (P chưa có task B).
- **Bước → Kết quả:** (1) `evaluate(P, now=T0, definitions=A)` → P không có task B. (2) `evaluate(P, now=T0)` (không giới hạn) → P có 1 task B.
- **Pass/Fail:** Pass nếu đúng cả hai.

## TG-28 — Apply Current Settings

Fixture: `U-MGR` (`tg28_manager`), định nghĩa D `duration`=8, `apply(tasks, now)` = `tasks.with_user(U-MGR).action_recalculate()` với đồng hồ giả `now`.

### TC-APS-001: Task đang chạy nhận mục tiêu mới, ghi event `recalculate`, báo kết quả

- **Truy vết:** REQ-INT-005 (AC2, AC6) · TCOND-23-01 · P1-Critical · Positive · Automated: `test_running_task_gets_new_target_and_event`
- **Precondition:** task `in_progress` gắn tại T0 (hạn T0+8h); đổi `duration` của D thành 4.
- **Bước → Kết quả:** (1) Apply lúc T0+1h → `target_duration` = 4; `planned_end_time` = T0+1h + 4h (thời gian đã chốt = 0); `original_breach_time` không đổi. (2) Có đúng 1 event `recalculate`, `note` chứa tên manager và "8.00 h -> 4.00 h". (3) Kết quả là `display_notification` + `soft_reload`, thông báo "1 task(s) updated, 0 skipped".
- **Pass/Fail:** Pass nếu đúng cả ba.

### TC-APS-002: Task đã vi phạm giữ nguyên hạn chót

- **Truy vết:** REQ-INT-005 (AC5) · TCOND-23-02 · P1-Critical · Positive · Automated: `test_breached_task_keeps_deadline`
- **Bước → Kết quả:** (1) Engine ghi vi phạm tại T0+9h (`has_breached`). (2) Đổi `duration`=4 rồi Apply lúc T0+10h → `target_duration` = 4; `planned_end_time` và `original_breach_time` giữ nguyên; có 1 event `recalculate`.
- **Pass/Fail:** Pass nếu hạn giữ nguyên.

### TC-APS-003: Task paused đổi mục tiêu nhưng giữ hạn chót (xếp lại khi resume)

- **Truy vết:** REQ-INT-005 (statement) · TCOND-23-03 · P2-High · Positive · Automated: `test_paused_task_keeps_deadline`
- **Bước → Kết quả:** (1) Pause lúc T0+1h; đổi `duration`=4; Apply lúc T0+2h → `stage`=`paused`, `target_duration`=4; `planned_end_time`, `original_breach_time` không đổi.
- **Pass/Fail:** Pass nếu đúng.

### TC-APS-004: Task không có gì đổi: không ghi event nhưng vẫn tính vào "updated"

- **Truy vết:** REQ-INT-005 (AC7) · TCOND-23-04 · P2-High · Positive · Automated: `test_unchanged_task_has_no_event_but_counts_updated`
- **Bước → Kết quả:** (1) Apply ngay tại T0 với cấu hình không đổi → `planned_end_time` = T0+8h; không có event `recalculate`; thông báo "1 task(s) updated, 0 skipped".
- **Pass/Fail:** Pass nếu đúng.

### TC-APS-005: Task đã đóng bị bỏ qua

- **Truy vết:** REQ-INT-005 (AC3) · TCOND-23-05 · P1-Critical · Negative · Automated: `test_closed_tasks_skipped`
- **Bước → Kết quả:** (1) Task `achieved`; đổi `duration`=4; Apply → `target_duration` vẫn 8; không có event `recalculate`; thông báo "0 task(s) updated, 1 skipped".
- **Pass/Fail:** Pass nếu đúng.

### TC-APS-006: Nhiều task trong một lần bấm: mỗi task đúng một event

- **Truy vết:** REQ-INT-005 (AC6) · TCOND-23-06 · P2-High · Positive · Automated: `test_many_tasks_one_event_each`
- **Bước → Kết quả:** (1) Hai task `in_progress`; đổi `duration`=4; Apply cả hai → 2 event `recalculate`; thông báo "2 task(s) updated, 0 skipped".
- **Pass/Fail:** Pass nếu đúng.

## TG-29 — Apply to Existing Records (wizard, `sla.apply.job`, cron)

Fixture: `U-MGR` (`tg29_manager`), `U-VIEW` (`tg29_viewer`); `_commit_progress` được thay bằng "không giới hạn thời gian" (test không được commit). `existing_records(n)` = tạo định nghĩa tắt, `n` partner `ref`='NEW' TRƯỚC khi bật, bật định nghĩa, xác nhận chưa có task nào. `apply(d, filter_domain, now)` = tạo wizard (U-MGR), gọi `action_apply()` với đồng hồ giả, trả về job mới nhất của định nghĩa.

### TC-APX-001: Áp dụng cho record có sẵn: đủ task, chạy lại không tạo trùng

- **Truy vết:** REQ-FUNC-068 (AC1) · TCOND-24-01 · P1-Critical · Positive · Automated: `test_all_matching_records_get_task_and_rerun_has_no_duplicates`
- **Precondition:** `existing_records(10)`.
- **Bước → Kết quả:** (1) Wizard `match_count` = 10. (2) `apply` → job `done`, `total`=`processed`=`attached`=10, `error_count`=0; 10 task đúng 10 partner; kết quả `display_notification` với `next` = `act_window_close`. (3) `apply` lần hai → job mới khác job cũ, `done`, `processed`=10, `attached`=0; vẫn 10 task; có 2 job.
- **Pass/Fail:** Pass nếu đúng cả ba; Fail nếu có task trùng.

### TC-APX-002: Domain lọc thu hẹp tập record

- **Truy vết:** REQ-FUNC-068 (AC4) · TCOND-24-02 · P2-High · Positive · Automated: `test_filter_domain_narrows_set`
- **Bước → Kết quả:** (1) `existing_records(10)`; apply với `filter_domain` = id của 3 partner → `total`=`processed`=`attached`=3; chỉ 3 partner đó có task.
- **Pass/Fail:** Pass nếu đúng.

### TC-APX-003: Domain lọc không mở rộng được điều kiện Start

- **Truy vết:** REQ-FUNC-068 (AC4) · TCOND-24-02 · P1-Critical · Negative · Automated: `test_filter_cannot_widen_start_condition`
- **Precondition:** 2 partner khớp Start; 1 partner `ref`='DONE' không khớp.
- **Bước → Kết quả:** (1) Apply với filter chứa cả 3 id → `processed`=`attached`=2; partner `DONE` không có task.
- **Pass/Fail:** Pass nếu partner không khớp không được gắn.

### TC-APX-004: Start chưa cấu hình (`[]`): job không nạp record nào

- **Truy vết:** REQ-FUNC-068 (AC5), REQ-FUNC-003 (AC2) · TCOND-24-03 · P2-High · Negative · Automated: `test_unconfigured_start_loads_nothing`
- **Bước → Kết quả:** (1) Định nghĩa bật `start_domain='[]'`, có partner `NEW`; apply → job `done`, `total`=`processed`=`attached`=0; không task.
- **Pass/Fail:** Pass nếu không task nào.

### TC-APX-005: Định nghĩa đang tắt: từ chối áp dụng

- **Truy vết:** REQ-FUNC-068 (AC5) · TCOND-24-03 · P1-Critical · Negative · Automated: `test_inactive_definition_rejected`
- **Bước → Kết quả:** (1) Wizard cho định nghĩa `active=False`; `action_apply()` → `UserError`.
- **Pass/Fail:** Pass nếu bị từ chối.

### TC-APX-006: Chia lô: lô đầu chạy ngay, phần còn lại do cron, không xử lý trùng

- **Truy vết:** REQ-FUNC-068 (AC2, AC3), REQ-REL-002 · TCOND-24-04 · P1-Critical · Positive · Automated: `test_batching_first_batch_now_rest_by_cron`
- **Precondition:** `dwo_sla_core.batch_size` = 3; `existing_records(10)`.
- **Bước → Kết quả:** (1) Apply → job `running`, `processed`=`attached`=3, `last_id` = id thứ 3; có bản ghi `ir.cron.trigger` cho cron `ir_cron_sla_apply`. (2) Tạo wizard mới và `action_apply()` khi job còn chạy → `UserError`. (3) Chạy `Job._cron_run()` → job `done`, `processed`=`attached`=10, `last_id` = id cuối; 10 task đúng 10 partner, không trùng.
- **Pass/Fail:** Pass nếu đúng ba bước.

### TC-APX-007: Job `queued` cũng chặn tạo job mới cùng định nghĩa

- **Truy vết:** REQ-FUNC-068 (AC3) · TCOND-24-04 · P2-High · Negative · Automated: `test_queued_job_also_blocks_new_job`
- **Bước → Kết quả:** (1) Có job `queued` của định nghĩa; wizard mới `action_apply()` → `UserError`.
- **Pass/Fail:** Pass nếu bị từ chối.

### TC-APX-008: Hủy job: dừng xử lý, cho phép tạo job mới

- **Truy vết:** REQ-FUNC-068 (AC6) · TCOND-24-05 · P1-Critical · Positive · Automated: `test_cancel_stops_job`
- **Precondition:** batch_size 3; `existing_records(10)`; apply (job `running`, đã xử lý 3).
- **Bước → Kết quả:** (1) U-MGR `action_cancel()` → `cancelled`, có `end_time`. (2) `_cron_run()` → job vẫn `cancelled`, `processed`=3; có 3 task. (3) Apply lần nữa → job mới khác job cũ.
- **Pass/Fail:** Pass nếu đúng ba bước.

### TC-APX-009: Lô lỗi làm job `failed` kèm ghi chú

- **Truy vết:** REQ-FUNC-068 (AC7) · TCOND-24-05 · P2-High · Negative · Automated: `test_failed_batch_marks_job_failed`
- **Bước → Kết quả:** (1) Tạo job với `filter_domain=[('bad_field','=',1)]`; `_cron_run()` → `state`=`failed`; `note` không rỗng.
- **Pass/Fail:** Pass nếu `failed` kèm ghi chú.

### TC-APX-010: Autovacuum xoá job đã kết thúc quá hạn lưu, giữ job đang chạy/chờ/mới

- **Truy vết:** REQ-FUNC-068 (AC8), REQ-INT-010 · TCOND-24-06 · P2-High · Positive · Automated: `test_autovacuum_removes_old_finished_keeps_running`
- **Precondition:** 5 job: `done` 400 ngày trước, `cancelled` 400 ngày trước, `running`, `queued`, `done` 1 ngày trước; retention mặc định 365.
- **Bước → Kết quả:** (1) `_gc_old_jobs()` → hai job cũ đã kết thúc bị xoá; ba job còn lại còn.
- **Pass/Fail:** Pass nếu đúng tập bị xoá.

### TC-APX-011: Backfill retroactive: mốc escalation đã vượt được đánh dấu xong, không bắn hồi tố

- **Truy vết:** REQ-FUNC-068 (AC9), REQ-FUNC-053 · TCOND-24-07 · P1-Critical · Positive · Automated: `test_backfill_retroactive_leaves_no_pending_passed_escalation`
- **Precondition:** field `x_retro_dt`; định nghĩa tắt `retroactive=True`; partner có mốc retroactive cách đây 10 giờ (250% của 4 giờ); mốc escalation 50%, 100%, 300%; bật định nghĩa.
- **Bước → Kết quả:** (1) Apply → `attached`=1. (2) Task `has_breached`; `done_escalation_ids` = {50%, 100%} (không có 300%). (3) `_next_due_escalation(task, T0)` rỗng; `next_due_at` > T0. (4) Chạy `_process_task(task, T0)` → `done_escalation_ids` không đổi; không có event `escalate`/`escalate_failed`.
- **Pass/Fail:** Pass nếu không có escalation hồi tố.

### TC-APX-012: Phân quyền: chỉ SLA Manager tạo wizard và sửa job

- **Truy vết:** REQ-FUNC-068 (AC10), REQ-SEC-001 · TCOND-24-08 · P1-Critical · Negative · Automated: `test_security`
- **Bước → Kết quả:** (1) U-VIEW tạo wizard → `AccessError`. (2) U-MGR đọc job → thấy (state `queued`). (3) U-VIEW đọc job → `AccessError`. (4) U-MGR ghi trực tiếp `state='done'` → `AccessError`.
- **Pass/Fail:** Pass nếu đúng bốn bước.

## TG-30 — Chip trạng thái SLA trên form record

Quy ước: `raw_task(definition, partner, stage, **extra)` dựng task trực tiếp theo đồng hồ thật (`start_time` = now-1h, `target_duration` 4, `planned_end_time` = now+10h, `running_since` = now-10 phút khi `in_progress`). `summary(P)` = `sla.task.get_record_sla_summary('res.partner', P.id)`. Fixture: định nghĩa "Chip SLA" trên `res.partner`, partner "Chip P".

### TC-FST-001: Record chưa có task: `state` rỗng

- **Truy vết:** REQ-INT-024 (AC6) · TCOND-25-01 · P1-Critical · Positive · Automated: `test_no_task_is_none`
- **Bước → Kết quả:** (1) `summary(P)` khi chưa có task → `state` = None.
- **Pass/Fail:** Pass nếu None.

### TC-FST-002: `res_id` rỗng: trả `{'state': None}`

- **Truy vết:** REQ-INT-024 (AC6) · TCOND-25-01 · P3-Low · Negative · Automated: `test_missing_id_is_none`
- **Bước → Kết quả:** (1) `get_record_sla_summary('res.partner', False)` → `{'state': None}`.
- **Pass/Fail:** Pass nếu đúng.

### TC-FST-003: Task đang chạy, chưa trễ: `state` = `running`

- **Truy vết:** REQ-INT-024 (AC6) · TCOND-25-02 · P1-Critical · Positive · Automated: `test_running`
- **Bước → Kết quả:** (1) Một task `in_progress` hạn sau 10 giờ → `state`=`running`, `count`=1, `late_count`=0, `lines` có 1 phần tử.
- **Pass/Fail:** Pass nếu đúng.

### TC-FST-004: Hạn trong ngưỡng Sắp đến hạn: `state` = `due_soon`

- **Truy vết:** REQ-INT-024 (AC6), REQ-INT-012 · TCOND-25-02 · P1-Critical · Positive · Automated: `test_due_soon`
- **Bước → Kết quả:** (1) Task `in_progress` có `planned_end_time` = now+1h → `state`=`due_soon`.
- **Pass/Fail:** Pass nếu đúng.

### TC-FST-005: Task paused: `state` = `paused`, `percent` theo thời gian đã dùng

- **Truy vết:** REQ-INT-024 (AC6) · TCOND-25-02 · P2-High · Positive · Automated: `test_paused`
- **Bước → Kết quả:** (1) Task `paused`, `business_duration`=1 (mục tiêu 4) → `state`=`paused`, `percent`=25.
- **Pass/Fail:** Pass nếu đúng.

### TC-FST-006: Task trễ nhiều: `state` = `breached`, `percent` bị chặn ở 100

- **Truy vết:** REQ-INT-024 (AC4) · TCOND-25-03 · P1-Critical · Boundary · Automated: `test_breached_running_percent_capped`
- **Bước → Kết quả:** (1) Task `in_progress`, `has_breached`, `business_duration`=10 (250%) → `state`=`breached`, `late_count`=1, `percent`=100, mọi dòng trong `lines` có `percent` ≤ 100.
- **Pass/Fail:** Pass nếu không có % lớn hơn 100.

### TC-FST-007: Task đã `achieved`: `state` = `met`

- **Truy vết:** REQ-INT-024 (AC6) · TCOND-25-02 · P2-High · Positive · Automated: `test_met`
- **Bước → Kết quả:** (1) Một task `achieved` → `state`=`met`, `count`=1, `late_count`=0.
- **Pass/Fail:** Pass nếu đúng.

### TC-FST-008: Task đã `breached` (đóng trễ): `state` = `missed`

- **Truy vết:** REQ-INT-024 (AC6) · TCOND-25-02 · P2-High · Positive · Automated: `test_missed`
- **Bước → Kết quả:** (1) Một task stage `breached` → `state`=`missed`, `late_count`=1.
- **Pass/Fail:** Pass nếu đúng.

### TC-FST-009: Chỉ có task `cancelled`: không có trạng thái

- **Truy vết:** REQ-INT-024 (AC6) · TCOND-25-01 · P2-High · Negative · Automated: `test_cancelled_only_is_none`
- **Bước → Kết quả:** (1) Một task `cancelled` → `state` = None.
- **Pass/Fail:** Pass nếu None.

### TC-FST-010: Nhiều task: chọn trạng thái khẩn nhất

- **Truy vết:** REQ-INT-024 (AC6) · TCOND-25-04 · P1-Critical · Positive · Automated: `test_multiple_tasks_pick_most_urgent`
- **Bước → Kết quả:** (1) Hai định nghĩa: task thứ nhất đang chạy (3 giờ đã dùng), task thứ hai đã vi phạm → `state`=`breached`, `count`=2, `late_count`=1.
- **Pass/Fail:** Pass nếu đúng.

### TC-FST-011: Task đang hoạt động thắng task đã đóng

- **Truy vết:** REQ-INT-024 (AC6) · TCOND-25-04 · P2-High · Positive · Automated: `test_active_task_wins_over_done_ones`
- **Bước → Kết quả:** (1) Một task stage `breached` (đã đóng) và một task `in_progress` → `state`=`running`.
- **Pass/Fail:** Pass nếu `running`.

### TC-FST-012: Người dùng không thuộc nhóm SLA gọi RPC bị từ chối (không `sudo`)

- **Truy vết:** REQ-INT-024 (AC7), REQ-SEC-002 · TCOND-25-05 · P1-Critical · Negative · Automated: `test_no_sudo_user_without_group_is_refused`
- **Bước → Kết quả:** (1) Người dùng chỉ có `base.group_user` gọi `get_record_sla_summary` → `AccessError`.
- **Pass/Fail:** Pass nếu bị từ chối.

### TC-FST-013: SLA User đọc được tóm tắt

- **Truy vết:** REQ-INT-024 (AC7) · TCOND-25-05 · P1-Critical · Positive · Automated: `test_sla_user_can_read`
- **Bước → Kết quả:** (1) Người dùng `group_sla_user` gọi RPC → `state`=`running`.
- **Pass/Fail:** Pass nếu đúng.

### TC-FST-014: Chưa có bản ghi tham số cờ: coi là bật

- **Truy vết:** REQ-INT-024 (AC8) · TCOND-25-06 · P2-High · Positive · Automated: `test_flag_on_when_never_configured`
- **Bước → Kết quả:** (1) Xoá bản ghi `dwo_sla_core.show_form_sla_status`; `_sla_show_form_status()` → True.
- **Pass/Fail:** Pass nếu True.

### TC-FST-015: Tắt cờ qua Settings lưu chuỗi `'False'` tường minh

- **Truy vết:** REQ-INT-024 (AC8) · TCOND-25-06 · P2-High · Positive · Automated: `test_setting_off_is_stored_explicitly`
- **Bước → Kết quả:** (1) Settings đặt `sla_show_form_status=False`, `execute()` → tham số lưu chuỗi `False` (bản ghi còn); `_sla_show_form_status()` → False.
- **Pass/Fail:** Pass nếu đúng.

### TC-FST-016: `session_info` liệt kê model có SLA cho SLA User

- **Truy vết:** REQ-INT-024 (AC3) · TCOND-25-07 · P1-Critical · Positive · Automated (HttpCase): `test_models_listed_for_sla_user`
- **Precondition:** định nghĩa "Session SLA" bật trên `res.partner`.
- **Bước → Kết quả:** (1) Đăng nhập admin, gọi `/web/session/get_session_info` → `dwo_sla_models` chứa `res.partner`.
- **Pass/Fail:** Pass nếu có.

### TC-FST-017: Cờ tắt: `dwo_sla_models` rỗng

- **Truy vết:** REQ-INT-024 (AC3) · TCOND-25-07 · P1-Critical · Negative · Automated (HttpCase): `test_empty_when_setting_off`
- **Bước → Kết quả:** (1) Đặt tham số cờ = `'False'`; admin lấy session info → `dwo_sla_models` = [].
- **Pass/Fail:** Pass nếu rỗng.

### TC-FST-018: Người dùng không thuộc nhóm SLA: `dwo_sla_models` rỗng

- **Truy vết:** REQ-INT-024 (AC3) · TCOND-25-07 · P1-Critical · Negative · Automated (HttpCase): `test_empty_without_sla_group`
- **Bước → Kết quả:** (1) Người dùng nội bộ không thuộc nhóm SLA lấy session info → `dwo_sla_models` = [].
- **Pass/Fail:** Pass nếu rỗng.

### TC-FST-019: Tour: form partner có chip, bấm chip mở list task của record

- **Truy vết:** REQ-INT-024 (AC1) · TCOND-25-08 · P1-Critical · Positive · Automated (HttpCase tour): `test_chip_on_partner_form`
- **Precondition:** định nghĩa "Chip Tour SLA" và một task `in_progress` cho partner "Chip Tour P"; đăng nhập admin.
- **Bước → Kết quả:** (1) Chạy tour `dwo_sla_form_status_chip` trên `/odoo/res.partner/<id>` → chip hiện cạnh pager; bấm chip mở list task của partner; tour hoàn tất.
- **Pass/Fail:** Pass nếu tour kết thúc không lỗi.

### TC-FST-020: Tour: form của model không có SLA không có chip

- **Truy vết:** REQ-INT-024 (AC2) · TCOND-25-08 · P1-Critical · Negative · Automated (HttpCase tour): `test_no_chip_without_sla`
- **Bước → Kết quả:** (1) Chạy tour `dwo_sla_form_status_chip_absent` trên form `res.partner.category` → không có chip, tour hoàn tất.
- **Pass/Fail:** Pass nếu tour kết thúc không lỗi.

## TG-31 — Tab Note, chuỗi giao diện không lỗi thời

Quy ước: `note(model)` = văn bản của `<page name="note">` trong arch form (chuẩn hoá khoảng trắng); `MODULE_PATH` = thư mục module.

### TC-NOT-001: Tab Note của định nghĩa có đủ 9 nhóm tiêu đề

- **Truy vết:** REQ-INT-029 (AC1) · TCOND-26-01 · P3-Low · Positive · Automated: `test_definition_note_has_nine_groups`
- **Bước → Kết quả:** (1) Lấy arch form `sla.definition` → trong `page[@name='note']` có đúng 9 phần tử `<h4>`.
- **Pass/Fail:** Pass nếu 9.

### TC-NOT-002: Tab Note của định nghĩa nêu các điểm cần lưu ý của đợt 1.1.0

- **Truy vết:** REQ-INT-029 (AC2), REQ-FUNC-003, REQ-FUNC-067, REQ-INT-024 · TCOND-26-01 · P2-High · Positive · Automated: `test_definition_note_content`
- **Bước → Kết quả:** (1) Văn bản tab Note chứa lần lượt: "Match all records" (giải thích `[]` không phải match-all), `[('id', '!=', 0)]`, "not kept in sync" (bản sao calendar), "public holidays", "reload the page" (chip cho model mới), "Re-check Conditions", "equal to or longer than the Duration" (ngưỡng sắp đến hạn), "Disable".
- **Pass/Fail:** Pass nếu đủ cả tám cụm từ.

### TC-NOT-003: Tab Note của task có 4 nhóm và 3 kịch bản đánh số

- **Truy vết:** REQ-INT-029 (AC3) · TCOND-26-02 · P3-Low · Positive · Automated: `test_task_note_has_four_groups_and_three_scenarios`
- **Bước → Kết quả:** (1) Arch form `sla.task` → `page[@name='note']` có 4 `<h4>` và 3 `<li>` trong `<ol>`. (2) Văn bản chứa "Apply Current Settings", "Re-check Conditions", "Original Breach Time", "from the moment you press the button", "creates a new one".
- **Pass/Fail:** Pass nếu đúng cả hai.

### TC-NOT-004: Không còn tên nút cũ "Recalculate"/"Re-evaluate" trong chuỗi hiển thị

- **Truy vết:** REQ-INT-029 (AC4), REQ-INT-005, REQ-INT-020 · TCOND-26-03 · P2-High · Negative · Automated: `test_no_old_button_names_in_user_strings`
- **Bước → Kết quả:** (1) `constants/message.py` không có chuỗi "Recalculate"/"Re-evaluate" trong dấu nháy kép. (2) Help của mọi field `sla.definition`, `sla.task`, `sla.escalation` không chứa "Recalculate" hoặc "Re-evaluate". (3) `views/sla_definition_views.xml` và `views/sla_task_views.xml` không có `string="Recalculate"`/`string="Re-evaluate"` và không có chuỗi `"Re-evaluate"`.
- **Pass/Fail:** Pass nếu không còn xuất hiện.

## TG-32 — Duration (live) và Business Duration (live)

Fixture: FX-DEF-STD (lịch `none`, duration 4). Hai field live là compute không lưu, chỉ để hiển thị: giá trị đã chốt cộng đoạn đang chạy tới `fields.Datetime.now()`.

### TC-DUR-001: Task đang chạy: cột lưu đứng yên, bản live cộng đoạn tới hiện tại

- **Truy vết:** REQ-INT-028 (AC1) · TCOND-27-01 · P2-High · Positive · Automated: `test_running_adds_current_period`
- **Bước → Kết quả:** (1) Tạo task lúc T0; xem lúc T0+1,5h → `business_duration` = `duration` = 0,0 (cột lưu); `business_duration_live` = `duration_live` = 1,5.
- **Pass/Fail:** Pass nếu đúng.

### TC-DUR-002: Task paused: live bằng giá trị đã lưu

- **Truy vết:** REQ-INT-028 (AC2) · TCOND-27-02 · P2-High · Positive · Automated: `test_paused_equals_stored`
- **Bước → Kết quả:** (1) Pause lúc T0+1h; xem lúc T0+3h → `stage`=`paused`; `business_duration_live` = `business_duration` = 1,0; `duration_live` = `duration`.
- **Pass/Fail:** Pass nếu đúng.

### TC-DUR-003: Có lịch: live theo giờ làm khác live theo giờ đồng hồ

- **Truy vết:** REQ-INT-028 (AC3) · TCOND-27-03 · P2-High · Positive · Automated: `test_calendar_counts_working_hours_only`
- **Precondition:** lịch FX-CAL-VN (T2–T6 08:00–17:00 ICT); định nghĩa nguồn `definition`, start `ref`='CAL'; task gắn lúc T0.
- **Bước → Kết quả:** (1) Xem lúc T0+24h → `duration_live` = 24,0; 0 < `business_duration_live` < 24.
- **Pass/Fail:** Pass nếu đúng.

### TC-DUR-004: List task hiện hai cột live mặc định, hai cột lưu vẫn có nhưng ẩn

- **Truy vết:** REQ-INT-028 (AC4) · TCOND-27-04 · P3-Low · Positive · Automated: `test_list_shows_live_and_hides_stored`
- **Bước → Kết quả:** (1) Arch list `sla.task`: `business_duration_live` và `duration_live` có `optional="show"`; `business_duration` và `duration` có `optional="hide"`.
- **Pass/Fail:** Pass nếu đúng bốn giá trị.

---

## Phụ lục A — Vấn đề SRS, TAD phát hiện khi viết test, quyết định đã chốt và giả định còn lại

Mỗi mục dưới đây là một câu hỏi cho người sở hữu tài liệu. Cột "Trạng thái": **ĐÃ CHỐT** (kèm nguồn: D-xx trong `TASKS.md` hoặc code đã hiện thực) nghĩa là test case đã cập nhật theo quyết định; **CÒN MỞ** nghĩa là chưa có quyết định, test case dùng giả định ghi ở cột "Giả định / quyết định đã dùng" và có dòng "Phụ thuộc: TA-xx" hoặc ghi chú tại ca. Đối chiếu code ngày 2026-10-12.

> Tiền tố TA- để không trùng A-xx của SRS/TAD (A-01..A-07 là Giả định ở SRS mục 2.5). Trạng thái **ĐÃ SỬA** (code) nghĩa là lệch giữa SRS và code đã được xử lý bằng cách sửa code (TASKS T13).

| # | Vấn đề | REQ / tài liệu | Giả định / quyết định đã dùng trong test | Đề xuất xử lý | Trạng thái |
|---|--------|----------------|------------------------------------------|---------------|------------|
| TA-01 | Hook không nhận `now` nên test không đặt được thời điểm khi đi qua hook | TAD 5.1, 8.5; Test Plan 6.4 | Hook gọi `evaluate(records, now=None, changed)` và lấy `fields.Datetime.now()`; không có hàm `now` riêng. Test qua hook patch `odoo.fields.Datetime.now` (`unittest.mock.patch`); test thuần Engine truyền `now` | Ghi vào TAD 8.5 | ĐÃ CHỐT (D7, code) |
| TA-02 | Tên hàm test phải gọi | TAD 5.1, 5.2; REQ-INT-007, 015 đến 018 | Tên thật theo code: Background Processor `sla.processor.process_due()` (KHÔNG nhận `now`; khóa và lưu từng task, báo `ir.cron._commit_progress(1, remaining=R)`, dừng khi hết task đến hạn, chạm `batch_size` hoặc thời gian còn lại <= 0); `sla.processor._process_task(task, now)` (xử lý đúng một task tại `now`); `sla.engine.evaluate(records, now=None, changed=None)`; `sla.task.action_reevaluate()`, `sla.task.action_recalculate()`, `sla.event.action_reevaluate_batch()`, `sla.event.action_mark_resolved()`; điểm mở rộng của `sla.definition`: `_get_calendar`, `_get_target_hours`, `_get_start_dt`, `_get_domain`, `_after_transition`; `sla.mixin`: `sla_task_count`, `action_view_sla_tasks()`; `sla.time.resolve_calendar/plan/settle/next_due_at`. Người dùng chọn SỬA TC theo code, không sửa code | Bổ sung "Interface spec" vào TAD | ĐÃ CHỐT (code) |
| TA-03 | Khi reset, task cũ ghi những event nào | REQ-FUNC-012, REQ-FUNC-029 | TC khẳng định task cũ nhận event `cancel` (reset_action `cancel`) hoặc `complete` (reset_action `complete`) rồi event `reset`, theo code `sla_engine._reset` | Người dùng chọn giữ code; SRS ghi cả hai event (D2 ban đầu đề xuất chỉ ghi `reset`) | ĐÃ CHỐT (người dùng, giữ code) |
| TA-04 | Attach thẳng vào `paused`: có ghi `pause` không | REQ-FUNC-006 AC2 | Đúng 1 event `attach`, 0 event `pause` | Ghi vào SRS | ĐÃ CHỐT (D2, code) |
| TA-05 | `event_dt` của `breach` và thứ tự với mốc | REQ-FUNC-022 | Breach khi `now >= planned_end_time`, `event_dt` = `now` lúc xử lý; task `paused` không bị so với `planned_end_time`; `breach` ghi TRƯỚC mọi mốc >= 100% (AC3) | Ghi vào SRS | ĐÃ CHỐT (D3, code) |
| TA-06 | `percent` Integer ép 75,5 thành 75 im lặng | REQ-FUNC-023 AC2 | `percent` là FLOAT8; số không nguyên bị `ValidationError` ("is not an integer"); `percent` <= 0 bị CHECK CSDL `sla_escalation_percent_check` | Cập nhật SRS và 030 | ĐÃ CHỐT (D6, code) |
| TA-07 | Thêm mốc khi task đang chạy: tính lại `next_due_at` | REQ-FUNC-053 AC2 | Mốc đã vượt chèn `done_escalation_ids` không event; mốc chưa tới thì tính lại `next_due_at` (D4) | Ghi vào SRS | ĐÃ CHỐT (D4) về thiết kế; lệch code xem TA-24 |
| TA-08 | Mốc đang chờ thử lại khi task pause, stop, cancel, reset (và resume) | REQ-FUNC-055 AC2, REQ-FUNC-058 | Hành vi ĐÃ ĐỔI: thêm boolean `cancel_retry_on_stop` trên `sla.escalation` (nhãn 'Cancel Retries When Task Stops', mặc định True, một cờ chung cho pause, stop, cancel, reset). Cờ True (mặc định): dòng `sla.escalation.retry` đang chờ bị xóa khi pause, stop, cancel, reset (như trước; TC-ESC-016, 030..032). Cờ False: dòng retry được giữ và tiến trình nền vẫn chạy lượt thử (event `escalate_retry`, `escalate_failed` hoặc `escalate`) dù task `paused`, `achieved`, `breached` hay `cancelled`; KHÔNG bắn mốc mới trên task không `in_progress` (REQ-FUNC-054 không đổi) (TC-ESC-060). Resume không còn xóa lượt thử (chỉ các dòng của cờ True đã bị xóa từ lúc pause) | Ghi vào SRS | ĐÃ CHỐT (người dùng, code đã đổi 2026-10-12) |
| TA-09 | AC3 REQ-FUNC-031 chấp nhận hai kết quả | REQ-FUNC-031 | Event không phải `error` bị bỏ qua lặng lẽ (không ném lỗi, không đổi `is_resolved`) | Sửa câu chữ AC | ĐÃ CHỐT (D5) |
| TA-10 | Mẫu thử lại khi `retry` = false | REQ-FUNC-028 | Không kiểm khi `retry` = false; ví dụ trong thông báo "Valid example: [1, 10, 20, 60]." | Ghi vào SRS | ĐÃ CHỐT (D5) |
| TA-11 | "Đã vi phạm" (bộ lọc, gồm task đã kết thúc) khác "số đang vi phạm" (chỉ `in_progress`, `paused`) | REQ-INT-011, REQ-FUNC-062 | Hai số khác nhau (ví dụ 4 và 3) | Đặt tên khác nhau trong giao diện | ĐÃ CHỐT (bộ lọc "Has Breached", đo lường pivot "Currently Breaching"; SRS INT-011 đã ghi) |
| TA-12 | Màn hình cấu hình SLA: tên field "Sắp đến hạn", quyền Manager, kiểm giá trị 0 hoặc âm | REQ-INT-010, 012, REQ-REL-002 | Field Settings `sla_event_retention_days`, `sla_due_soon_hours`, `sla_batch_size`; giá trị <= 0 bị `ValidationError`; SLA User bị `AccessError` | Chốt khi thiết kế giao diện | ĐÃ CHỐT (code) |
| TA-13 | Hiệu năng: "trước khi cài" cần hai database; độ trễ mốc; ngưỡng 5% | REQ-PERF-001, 003 | Hai database (chưa cài, đã cài); độ trễ L = 60 giây (chu kỳ cron) + D_k (tổng thời gian các lần gọi `process_due()` liên tiếp tới khi hết task đến hạn), ngưỡng p95(L) <= 120 giây | Test Plan 11.1 | ĐÃ CHỐT (O-01 đóng 2026-10-12: ngưỡng 5%) |
| TA-14 | `REQ-FUNC-041`: "kiểu ngày giờ" có gồm `Date` không | REQ-FUNC-041 | Chỉ field Datetime, không có ca cho field Date | Ghi vào SRS | ĐÃ CHỐT (D5) |
| TA-15 | AC1 REQ-FUNC-001 "cùng cấu hình điều kiện" cho hai model khác nhau; module demo `dwo_sla_demo_ticket` chưa hiện thực | REQ-FUNC-001, REQ-INST-004 | "Cùng cấu trúc cấu hình"; `demo.ticket` có `priority`, `team_id` | Sửa câu chữ AC; hiện thực module demo | CÒN MỞ |
| TA-16 | Nội dung thông báo lỗi và ghi chú event | REQ-FUNC-003, 018, 020, 061; REQ-INT-019 | Thông báo `ValidationError`, `AccessError` và `note` bằng tiếng Anh từ `constants/message.py`; TC chỉ kiểm từ khóa hoặc loại lỗi | Không cần thêm | ĐÃ CHỐT (code, CLAUDE.md) |
| TA-17 | Loại lỗi khi sửa event ngoài `is_resolved` | REQ-SEC-006 | `AccessError` (ACL `sla.event` chỉ đọc; ghi `is_resolved` qua `action_mark_resolved()`) | Ghi vào SRS | ĐÃ CHỐT (code) |
| TA-18 | Chế độ cancel khi test AC của REQ-FUNC-005 AC2 và REQ-FUNC-006 AC4 | REQ-FUNC-005, 006 | `start_unmatched` (riêng ca cancel khớp dùng `condition`); điều kiện cancel khớp luôn chặn attach, không phụ thuộc `cancel_mode` (`_maybe_attach`) | Nêu trong AC | ĐÃ CHỐT (code) |
| TA-19 | Mô phỏng "server action chậm 30 giây" và đồng thời bằng thời gian thật không ổn định | REQ-REL-001 AC2; Test Plan 6.4 | Giữ giao dịch của cursor nền mở bằng barrier, không dùng `sleep`; kết quả quan sát là trạng thái đã lưu | Cập nhật Test Plan nếu cần | CÒN MỞ |
| TA-20 | AC2 REQ-FUNC-014 "cả hai giao dịch lưu record thành công" không thể đúng nếu cùng ghi một dòng | REQ-FUNC-014 | TC-ERR-005 viết lại: hai cursor cùng gọi `evaluate` cho (định nghĩa, record) mà không ghi record; kết quả dựa trên chỉ mục `sla_task_one_active_uniq`. SRS AC2 được viết lại: chỉ một task hoạt động tồn tại, không có task trùng, bên thua ghi event `error` hoặc kết thúc mà không tạo task trùng; không yêu cầu cả hai giao dịch lưu record | Ghi vào SRS | ĐÃ CHỐT (người dùng; TC đã sửa) |
| TA-21 | Gỡ module (REQ-INT-007 AC3, REQ-INST-001) cần database riêng | REQ-INT-007, REQ-INST-001 | Ca Automated (CI) trên database riêng | Ghi vào Test Plan 6.4 | CÒN MỞ |
| TA-22 | `business_percent_used`: lưu hay tính khi đọc, có gồm đoạn đang chạy không | REQ-INT-023 | `business_percent_used` KHÔNG lưu: tính khi đọc và với task `in_progress` gồm cả đoạn từ `running_since` tới thời điểm xem (code đổi 2026-10-12, `sla.time.settle_batch`). TC-BRE-015 đến 021 vẫn pause trước để có số cố định; TC-BRE-015 thêm ví dụ chạy trực tiếp (mục tiêu 4 giờ: chạy 1 giờ = 25%, chạy 5 giờ = 125%) | Ghi vào SRS | ĐÃ CHỐT (người dùng, code) |
| TA-23 | Định dạng và múi giờ của giờ thử kế tiếp trong `note` của `escalate_retry` | REQ-FUNC-027 AC1 | Code ghi "Error: %s. Will retry at %s." với chuỗi datetime UTC; TC-ESC-020 kiểm '2026-03-02 03:01:00' | Nêu định dạng trong SRS | CÒN MỞ |
| TA-24 | `sla_escalation.create` chỉ chèn mốc đã vượt vào `done_escalation_ids`, chưa tính lại `next_due_at` cho mốc chưa tới | REQ-FUNC-053 AC2 (D4) | TC-ESC-047, TC-CHG-013 kỳ vọng `next_due_at` = 12:36 | Sửa code | ĐÃ SỬA (code, TASKS T13) |
| TA-25 | `action_recalculate` trên task đã kết thúc: code bỏ qua lặng lẽ, không `UserError`; AC3 REQ-INT-005 viết "không có nút" | REQ-INT-005 AC3, AC4 | Mức kiểm: (1) arch view `views/sla_task_views.xml` có `invisible="stage not in ('in_progress', 'paused')"` và `groups="dwo_sla_core.group_sla_manager"`; (2) gọi hàm trực tiếp không đổi task; (3) SLA User bị `AccessError`. Hiển thị trên trình duyệt kiểm bằng Demonstration TG-17 | Không cần thêm | ĐÃ CHỐT (code) |
| TA-26 | AC5 REQ-FUNC-012 ("reset khớp mà start không khớp thì kết thúc task cũ theo reset_action") mâu thuẫn FUNC-008 (nhánh reset chỉ vào khi reset VÀ start cùng khớp) | REQ-FUNC-012 AC5, REQ-FUNC-008 | Giữ code theo FUNC-008: reset khớp mà start không khớp KHÔNG đóng task cũ (TC-CAN-016 dùng `cancel_mode` = `never`); với `start_unmatched` task cũ bị đóng bởi quy tắc cancel | SRS REQ-FUNC-012 AC5 đang được viết lại cho khớp FUNC-008 | ĐÃ CHỐT (người dùng, giữ code) |
| TA-27 | Code chưa gọi `flush_recordset()` tường minh trước `create` task mới khi reset hoặc attach lại, trong khi 030 mục 6 yêu cầu | 030 mục 6, REQ-FUNC-012, 007 | TC-CAN-032 kiểm kết quả quan sát (không event `error`, không vi phạm `sla_task_one_active_uniq`) | Xác nhận hoặc sửa code | CÒN MỞ (phía code) |
| TA-28 | Cơ chế lọc giá trị field khỏi thông báo lỗi gốc; code lưu `str(exc)` thô vào `note` | REQ-OBS-003 | TC-ERR-011 kỳ vọng 'SECRET-123' không xuất hiện | Cơ chế lọc: `sla.event._scrub_values` thay giá trị field `char`/`text`/`html` (từ 3 ký tự) của record gốc bằng `<redacted>` trước khi ghi `note` và log (áp dụng cho `_log_error` và lỗi action escalation; SRS OBS-003 AC2) | ĐÃ CHỐT (code đã sửa) |
| TA-29 | Nơi đặt hành động Re-check Conditions cho record chưa có task (hiện chỉ có trên task và event `error`) | REQ-FUNC-032, REQ-INT-020 | TG-13 gọi `sla.engine.evaluate(K, changed=set())` như lõi của hành động | Quyết định giao diện | CÒN MỞ |
| TA-30 | Measure "Tỷ lệ đạt" và "Đang vi phạm" tính sẵn trong pivot/graph | REQ-FUNC-036, 062, REQ-INT-013 | Code đã thêm `sla.task.achieved_rate` (avg chỉ tính task `achieved`/`breached`) và `breaching_count` (sum) dạng cột lưu cho pivot/graph; TC-UIX-039 đến 042 mô tả theo AC | Cập nhật 030 (cột mới) | ĐÃ SỬA (code, TASKS T13) |
| TA-31 | `res.partner` cho phép partner con khác công ty với mẹ (fixture TC-SEC-016, 017) | REQ-SEC-005 | Giả định fixture; nếu Odoo từ chối thì dùng model liên kết khác | Xác nhận khi dựng fixture | CÒN MỞ |
| TA-32 | `res.config.settings.execute()` của Odoo chỉ cho quản trị viên (`env.is_admin()`), trong khi các ca Settings (ESC-056..058, INF-018..022, UIX-023, UIX-025; INF-017 chỉ đọc giá trị mặc định) giả định SLA Manager lưu được | REQ-INT-010, 012, REQ-REL-002, REQ-SEC-001 | Ca viết như SRS (Manager lưu được); ca của U-USR bị từ chối vẫn đúng nhưng chưa chứng minh quy tắc SLA | Quyết định: giữ cơ chế chuẩn của Odoo (chỉ quản trị hệ thống lưu Settings; `base.group_system` kế thừa SLA Manager); SRS SEC-001 AC5 đã ghi | ĐÃ CHỐT |
| TA-33 | `process_due()` đọc task bằng `sudo()` nên server action chạy với quyền superuser, không theo quyền user cron hoặc công ty của record | REQ-SEC-004, REQ-INT-019 | TC-SEC-013/014 và TC-ESC-050..052 gọi `process_due()` bằng `with_user(U-CRON)` và kỳ vọng theo SRS | Sửa code | ĐÃ SỬA (code, TASKS T13) |
| TA-34 | `sla.event.action_mark_resolved` ghi bằng `sudo()` và không kiểm tra nhóm Manager | REQ-SEC-006 | TC-SEC-022 gọi bằng U-USR và kỳ vọng `AccessError` | Thêm kiểm tra nhóm | ĐÃ SỬA (code, TASKS T13) |

Các giả định riêng của nhóm TG-04, TG-05, TG-07, TG-09 nằm ở Phụ lục B (G1 đến G12).

---

### Ghi chú đối chiếu

- **Cờ thử lại `cancel_retry_on_stop`** (TA-08): thuộc `sla.escalation`, nhãn 'Cancel Retries When Task Stops', mặc định True, một cờ chung cho pause, stop, cancel, reset. Mặc định True giữ hành vi cũ (xóa lượt thử đang chờ: TC-ESC-016, 030..032); False giữ lượt thử và tiến trình nền vẫn chạy (TC-ESC-060) nhưng không bắn mốc mới trên task không `in_progress` (REQ-FUNC-054).
- **Mốc escalation là cấu hình dùng chung, không có snapshot theo task**: sửa `percent`, xóa hoặc thêm mốc trên định nghĩa áp dụng ngay cho mọi task đang chạy của định nghĩa đó (`next_due_at` được tính lại). Quyết định đã chốt: giữ hành vi code hiện tại; REQ-FUNC-053 chỉ yêu cầu cho trường hợp thêm mốc (TC-ESC-047, TC-CHG-013), các trường hợp sửa `percent` hoặc xóa mốc không có yêu cầu riêng.

## Phụ lục B — Giả định dùng trong nhóm TG-04, TG-05, TG-07, TG-09

- G1: để điều khiển `now`, test ghi giá trị field không qua hook (ví dụ ghi bằng SQL hoặc tắt hook của test rồi invalidate cache) rồi gọi `evaluate(records, now, changed)` với `changed` tường minh; không dùng `sleep`. G2: trên task cũ, reset ghi `cancel` (reset_action `cancel`) hoặc `complete` (reset_action `complete`) rồi `reset` (xem TA-03, CÒN MỞ).
- G3: ở `cancel_mode` = `start_unmatched`, domain cancel không có tác dụng (theo `_cancel_matches`). G4: task gắn lại sau `cancelled` ghi event `attach`.
- G5: field compute có lưu dùng `res.partner.complete_name` (phụ thuộc `name`). G6: hai giao dịch mô phỏng bằng hai cursor gọi `evaluate`; kết quả dựa trên chỉ mục `sla_task_one_active_uniq` (xem TA-20).
- G7: thay bằng TA-26: AC5 của REQ-FUNC-012 mâu thuẫn FUNC-008, TC-CAN-016 theo code. G8: attach vào `paused` ghi đúng 1 event `attach` (TA-04).
- G9: `RETRO-DT` là một field Datetime ghi được của `res.partner` do module test cung cấp. G10: từ khóa `note` của event `attach` do `constants/message.py` (NOTE_005: "Start-marker field '%s' is empty; using the current time instead."). G11: breach khi `now >= planned_end_time` (TA-05). G12: nội dung `note` của event `error` do code ghi (`str(exc)` hoặc `constants/message.py`); TC chỉ kiểm không rỗng.

## Phụ lục C — Ánh xạ hàm test sang test case (435 hàm)

Mỗi dòng là một hàm `def test_` trong `tests/`. Một hàm có thể phủ nhiều test case (cột Test case); test case do hàm đó phủ là biến thể hoặc hợp nhất khi hàm gom nhiều ca tương tự. Cột REQ-ID là hợp REQ-ID của các test case đó.

| # | File | Class | Hàm test | Test case | REQ-ID |
|---|---|---|---|---|---|
| 1 | `test_tg01_lifecycle.py` | TestAttachStop | `test_att_007_attach` | TC-ATT-007 | FUNC-006 |
| 2 | `test_tg01_lifecycle.py` | TestAttachStop | `test_att_019_create_record_attaches` | TC-ATT-019 | FUNC-004 |
| 3 | `test_tg01_lifecycle.py` | TestAttachStop | `test_att_017_stop_achieved` | TC-ATT-017 | FUNC-009 |
| 4 | `test_tg01_lifecycle.py` | TestAttachStop | `test_att_012_achieved_not_reattached` | TC-ATT-012 | FUNC-007 |
| 5 | `test_tg01_lifecycle.py` | TestAttachStop | `test_att_014_achieved_not_reset` | TC-ATT-014 | FUNC-007 |
| 6 | `test_tg01_lifecycle.py` | TestAttachStop | `test_att_015_cancelled_reattach` | TC-ATT-015 | FUNC-007 |
| 7 | `test_tg01_lifecycle.py` | TestAttachStop | `test_att_022_unrelated_field_no_change` | TC-ATT-022 | FUNC-004 |
| 8 | `test_tg01_lifecycle.py` | TestAttachStop | `test_att_023_reevaluate_idempotent` | TC-ATT-023 | FUNC-015 |
| 9 | `test_tg01_lifecycle.py` | TestAttachStop | `test_att_001_empty_stop_never_matches` | TC-ATT-001 | FUNC-003 |
| 10 | `test_tg01_lifecycle.py` | TestAttachStop | `test_att_002_empty_list_matches_all` | TC-ATT-002 | FUNC-003 |
| 11 | `test_tg01_lifecycle.py` | TestPauseResume | `test_pau_001_pause` | TC-PAU-001 | FUNC-011 |
| 12 | `test_tg01_lifecycle.py` | TestPauseResume | `test_pau_004_and_009_resume_replans_deadline` | TC-PAU-004, TC-PAU-009 | FUNC-037, FUNC-044 |
| 13 | `test_tg01_lifecycle.py` | TestPauseResume | `test_pau_008_011_full_lifecycle` | TC-PAU-008, TC-PAU-011 | FUNC-029, FUNC-048 |
| 14 | `test_tg01_lifecycle.py` | TestPauseResume | `test_pau_resume_pause_unmatched_mode` | TC-PAU-008 | FUNC-048 |
| 15 | `test_tg01_lifecycle.py` | TestPauseResume | `test_pau_resume_condition_not_matching_stays_paused` | TC-PAU-005 | FUNC-037 |
| 16 | `test_tg01_lifecycle.py` | TestPriorityCancelReset | `test_can_001_stop_beats_pause` | TC-CAN-001 | FUNC-008 |
| 17 | `test_tg01_lifecycle.py` | TestPriorityCancelReset | `test_can_002_stop_beats_cancel` | TC-CAN-002 | FUNC-008 |
| 18 | `test_tg01_lifecycle.py` | TestPriorityCancelReset | `test_can_003_cancel_beats_pause` | TC-CAN-003 | FUNC-008 |
| 19 | `test_tg01_lifecycle.py` | TestPriorityCancelReset | `test_can_004_reset_beats_pause` | TC-CAN-004 | FUNC-008 |
| 20 | `test_tg01_lifecycle.py` | TestPriorityCancelReset | `test_can_005_nothing_matches_no_change` | TC-CAN-005 | FUNC-008 |
| 21 | `test_tg01_lifecycle.py` | TestPriorityCancelReset | `test_can_007_start_unmatched_cancels` | TC-CAN-007 | FUNC-010 |
| 22 | `test_tg01_lifecycle.py` | TestPriorityCancelReset | `test_can_008_condition_cancels_while_start_matches` | TC-CAN-008 | FUNC-010 |
| 23 | `test_tg01_lifecycle.py` | TestPriorityCancelReset | `test_can_009_never_does_not_cancel` | TC-CAN-009 | FUNC-010 |
| 24 | `test_tg01_lifecycle.py` | TestPriorityCancelReset | `test_reset_complete_action` | TC-CAN-013 | FUNC-012 |
| 25 | `test_tg01_lifecycle.py` | TestPriorityCancelReset | `test_reset_only_when_tracked_field_changes` | TC-CAN-021, TC-CAN-026 | FUNC-013, FUNC-050 |
| 26 | `test_tg01_lifecycle.py` | TestMisconfig | `test_mis_001_start_subset_of_stop` | TC-MIS-001 | FUNC-016 |
| 27 | `test_tg01_lifecycle.py` | TestMisconfig | `test_mis_004_attach_paused` | TC-MIS-004 | FUNC-016 |
| 28 | `test_tg01_lifecycle.py` | TestMisconfig | `test_mis_005_leaving_hold_cancels` | TC-MIS-005 | FUNC-016 |
| 29 | `test_tg01_lifecycle.py` | TestMisconfig | `test_mis_006_exclusive_start_pause_cancel_no_pause_event` | TC-MIS-006 | FUNC-008, FUNC-016 |
| 30 | `test_tg01_lifecycle.py` | TestMisconfig | `test_mis_007_exclusive_never_pauses` | TC-MIS-007 | FUNC-016 |
| 31 | `test_tg01_lifecycle.py` | TestMultipleDefinitions | `test_mul_001_002_independent_tasks` | TC-MUL-001, TC-MUL-002 | FUNC-014 |
| 32 | `test_tg01_lifecycle.py` | TestMultipleDefinitions | `test_mul_004_second_active_task_rejected` | TC-MUL-004, TC-MUL-006 | FUNC-014 |
| 33 | `test_tg01_lifecycle.py` | TestMultipleDefinitions | `test_mul_008_conflict_logged_as_error_event` | TC-MUL-008 | FUNC-014, FUNC-030 |
| 34 | `test_tg01_lifecycle.py` | TestGeneric | `test_gen_001_two_models` | TC-GEN-001 | FUNC-001 |
| 35 | `test_tg01_more.py` | TestConditionSaving | `test_att_003_unknown_field_rejected` | TC-ATT-003 | FUNC-003 |
| 36 | `test_tg01_more.py` | TestConditionSaving | `test_att_004_function_call_rejected` | TC-ATT-004 | FUNC-003 |
| 37 | `test_tg01_more.py` | TestConditionSaving | `test_att_005_variable_rejected` | TC-ATT-005 | FUNC-003 |
| 38 | `test_tg01_more.py` | TestConditionSaving | `test_att_006_literal_saved` | TC-ATT-006 | FUNC-003 |
| 39 | `test_tg01_more.py` | TestAttachEdges | `test_att_008_start_and_pause_attach_paused` | TC-ATT-008 | FUNC-006 |
| 40 | `test_tg01_more.py` | TestAttachEdges | `test_att_009_start_and_stop_no_attach` | TC-ATT-009 | FUNC-006 |
| 41 | `test_tg01_more.py` | TestAttachEdges | `test_att_010_start_and_cancel_no_attach` | TC-ATT-010 | FUNC-006 |
| 42 | `test_tg01_more.py` | TestAttachEdges | `test_att_011_020_start_unmatched` | TC-ATT-011, TC-ATT-020 | FUNC-004, FUNC-006 |
| 43 | `test_tg01_more.py` | TestAttachEdges | `test_att_013_breached_not_reattached` | TC-ATT-013 | FUNC-007 |
| 44 | `test_tg01_more.py` | TestAttachEdges | `test_att_016_cancelled_start_and_stop` | TC-ATT-016 | FUNC-007 |
| 45 | `test_tg01_more.py` | TestAttachEdges | `test_att_018_stop_again_noop` | TC-ATT-018 | FUNC-009 |
| 46 | `test_tg01_more.py` | TestAttachEdges | `test_att_021_stop_running_task` | TC-ATT-021 | FUNC-004 |
| 47 | `test_tg01_more.py` | TestAttachEdges | `test_att_024_paused_reevaluate_noop` | TC-ATT-024 | FUNC-015 |
| 48 | `test_tg01_more.py` | TestAttachEdges | `test_att_025_026_no_change_no_event` | TC-ATT-025, TC-ATT-026 | FUNC-029 |
| 49 | `test_tg01_more.py` | TestAttachEdges | `test_att_027_hook_self_heals` | TC-ATT-027 | FUNC-004 |
| 50 | `test_tg01_more.py` | TestPauseResumeEdges | `test_pau_002_pause_again_noop` | TC-PAU-002 | FUNC-011 |
| 51 | `test_tg01_more.py` | TestPauseResumeEdges | `test_pau_003_achieved_ignores_pause` | TC-PAU-003 | FUNC-011 |
| 52 | `test_tg01_more.py` | TestPauseResumeEdges | `test_pau_005_condition_mode_needs_resume_match` | TC-PAU-005 | FUNC-037 |
| 53 | `test_tg01_more.py` | TestPauseResumeEdges | `test_pau_006_pause_unmatched_resumes` | TC-PAU-006 | FUNC-048 |
| 54 | `test_tg01_more.py` | TestPauseResumeEdges | `test_pau_007_pause_unmatched_still_paused` | TC-PAU-007 | FUNC-048 |
| 55 | `test_tg01_more.py` | TestPauseResumeEdges | `test_pau_010_resume_keeps_planned_end_after_breach` | TC-PAU-010 | FUNC-044 |
| 56 | `test_tg03_08_breach_escalation.py` | TestBreach | `test_bre_002_at_planned_end` | TC-BRE-002 | FUNC-022 |
| 57 | `test_tg03_08_breach_escalation.py` | TestBreach | `test_bre_before_planned_end` | TC-BRE-001 | FUNC-022 |
| 58 | `test_tg03_08_breach_escalation.py` | TestBreach | `test_bre_003_004_once_only` | TC-BRE-003, TC-BRE-004 | FUNC-022 |
| 59 | `test_tg03_08_breach_escalation.py` | TestBreach | `test_bre_005_pause_before_processor` | TC-BRE-005 | FUNC-022 |
| 60 | `test_tg03_08_breach_escalation.py` | TestBreach | `test_bre_009_stop_after_planned_end` | TC-BRE-009 | FUNC-009 |
| 61 | `test_tg03_08_breach_escalation.py` | TestBreach | `test_bre_013_flag_survives_pause_resume` | TC-BRE-013, TC-PAU-010 | FUNC-044, FUNC-046 |
| 62 | `test_tg03_08_breach_escalation.py` | TestBreach | `test_bre_paused_task_not_breached_by_processor` | TC-BRE-024 | FUNC-022 |
| 63 | `test_tg03_08_breach_escalation.py` | TestBreach | `test_bre_023_cross_check_constraints` | TC-BRE-023 | FUNC-009, FUNC-046 |
| 64 | `test_tg03_08_breach_escalation.py` | TestRetroactive | `test_ret_002_retroactive_breach_on_attach` | TC-RET-002 | FUNC-017 |
| 65 | `test_tg03_08_breach_escalation.py` | TestRetroactive | `test_ret_retroactive_not_yet_due` | TC-RET-005 | FUNC-017 |
| 66 | `test_tg03_08_breach_escalation.py` | TestEscalation | `test_esc_001_three_milestones` | TC-ESC-001 | FUNC-023 |
| 67 | `test_tg03_08_breach_escalation.py` | TestEscalation | `test_bre_007_breach_before_100_escalation` | TC-BRE-007 | FUNC-022 |
| 68 | `test_tg03_08_breach_escalation.py` | TestEscalation | `test_esc_008_not_refired` | TC-ESC-008 | FUNC-024 |
| 69 | `test_tg03_08_breach_escalation.py` | TestEscalation | `test_esc_not_before_threshold` | TC-ESC-006 | FUNC-023 |
| 70 | `test_tg03_08_breach_escalation.py` | TestEscalation | `test_bre_014_elapsed_survives_pause` | TC-BRE-014 | FUNC-046 |
| 71 | `test_tg03_08_breach_escalation.py` | TestEscalation | `test_esc_048_context_and_record` | TC-ESC-048, TC-ESC-049 | INT-008 |
| 72 | `test_tg03_08_breach_escalation.py` | TestEscalation | `test_esc_018_019_failure_isolated` | TC-ESC-018, TC-ESC-019 | FUNC-026 |
| 73 | `test_tg03_08_breach_escalation.py` | TestProcessDue | `test_process_due_handles_due_tasks` | TC-PRC-001 | FUNC-022, REL-002 |
| 74 | `test_tg03_08_breach_escalation.py` | TestProcessDue | `test_process_due_skips_tasks_not_due` | TC-PRC-002 | FUNC-022, REL-002 |
| 75 | `test_tg03_08_breach_escalation.py` | TestProcessDue | `test_process_due_batch_size_caps_each_call` | TC-PRC-003 | REL-002 |
| 76 | `test_tg03_more.py` | TestBreachMore | `test_bre_001_before_planned_end` | TC-BRE-001 | FUNC-022 |
| 77 | `test_tg03_more.py` | TestBreachMore | `test_bre_006_pause_at_target` | TC-BRE-006 | FUNC-022 |
| 78 | `test_tg03_more.py` | TestBreachMore | `test_bre_008_breach_before_escalate` | TC-BRE-008 | FUNC-022 |
| 79 | `test_tg03_more.py` | TestBreachMore | `test_bre_010_long_pause_then_stop` | TC-BRE-010 | FUNC-009 |
| 80 | `test_tg03_more.py` | TestBreachMore | `test_bre_011_stop_paused_breached` | TC-BRE-011 | FUNC-009 |
| 81 | `test_tg03_more.py` | TestBreachMore | `test_bre_012_stop_after_breach_no_duplicate` | TC-BRE-012 | FUNC-009 |
| 82 | `test_tg03_more.py` | TestBreachMore | `test_bre_015_016_percent_used` | TC-BRE-015, TC-BRE-016 | INT-023 |
| 83 | `test_tg03_more.py` | TestBreachMore | `test_bre_017b_running_percent_live` | TC-BRE-025 | INT-023 |
| 84 | `test_tg03_more.py` | TestBreachMore | `test_bre_017c_settle_batch_equals_settle` | TC-BRE-026 | INT-023, PERF-002 |
| 85 | `test_tg03_more.py` | TestBreachMore | `test_bre_017_paused_percent_stable` | TC-BRE-017 | INT-023 |
| 86 | `test_tg03_more.py` | TestBreachMore | `test_bre_018_021_percent_boundaries` | TC-BRE-018, TC-BRE-019, TC-BRE-020, TC-BRE-021 | INT-023 |
| 87 | `test_tg03_more.py` | TestBreachMore | `test_bre_022_failed_action_note` | TC-BRE-022 | FUNC-029 |
| 88 | `test_tg03_more.py` | TestBreachMore | `test_bre_023_task_db_constraints` | TC-BRE-023 | FUNC-009, FUNC-046 |
| 89 | `test_tg04_more.py` | TestCancelRules | `test_can_006_cancel_beats_reset` | TC-CAN-006 | FUNC-008 |
| 90 | `test_tg04_more.py` | TestCancelRules | `test_can_010_condition_mode_needs_cancel_match` | TC-CAN-010 | FUNC-010 |
| 91 | `test_tg04_more.py` | TestCancelRules | `test_can_011_start_unmatched_needs_start_gone` | TC-CAN-011 | FUNC-010 |
| 92 | `test_tg04_more.py` | TestResetAction | `test_can_012_reset_cancel` | TC-CAN-012 | FUNC-012 |
| 93 | `test_tg04_more.py` | TestResetAction | `test_can_013_reset_complete` | TC-CAN-013 | FUNC-012 |
| 94 | `test_tg04_more.py` | TestResetAction | `test_can_014_new_task_paused` | TC-CAN-014 | FUNC-012 |
| 95 | `test_tg04_more.py` | TestResetAction | `test_can_015_latest_achieved_not_reset` | TC-CAN-015 | FUNC-007, FUNC-012 |
| 96 | `test_tg04_more.py` | TestResetAction | `test_can_016_reset_without_start_no_branch` | TC-CAN-016 | FUNC-008, FUNC-012 |
| 97 | `test_tg04_more.py` | TestResetAction | `test_can_017_reset_paused_task` | TC-CAN-017 | FUNC-012 |
| 98 | `test_tg04_more.py` | TestResetAction | `test_can_018_reset_complete_after_planned_end` | TC-CAN-018 | FUNC-009, FUNC-012 |
| 99 | `test_tg04_more.py` | TestResetAction | `test_can_019_attach_after_cancelled_not_reset` | TC-CAN-019 | FUNC-007, FUNC-012 |
| 100 | `test_tg04_more.py` | TestResetAction | `test_can_032_reset_then_reattach_unique_index` | TC-CAN-032 | FUNC-007, FUNC-012 |
| 101 | `test_tg04_more.py` | TestResetOnField | `test_can_020_30_field_changed_resets` | TC-CAN-020, TC-CAN-030 | FUNC-013, FUNC-051 |
| 102 | `test_tg04_more.py` | TestResetOnField | `test_can_021_25_unchanged_values_no_reset` | TC-CAN-021, TC-CAN-025 | FUNC-013, FUNC-050 |
| 103 | `test_tg04_more.py` | TestResetOnField | `test_can_022_computed_stored_field` | TC-CAN-022 | FUNC-013 |
| 104 | `test_tg04_more.py` | TestResetOnField | `test_can_023_reset_condition_unmatched` | TC-CAN-023 | FUNC-013 |
| 105 | `test_tg04_more.py` | TestResetOnField | `test_can_024_one_of_two_fields` | TC-CAN-024, TC-CAN-031 | FUNC-013, FUNC-051 |
| 106 | `test_tg04_more.py` | TestResetOnField | `test_can_026_other_field_no_reset` | TC-CAN-026 | FUNC-050 |
| 107 | `test_tg04_more.py` | TestResetOnField | `test_can_027_28_manual_and_background_no_reset` | TC-CAN-027, TC-CAN-028 | FUNC-050 |
| 108 | `test_tg04_more.py` | TestResetOnField | `test_can_029_empty_reset_domain` | TC-CAN-029 | FUNC-051 |
| 109 | `test_tg06_time_calendar.py` | TestTimePlanning | `test_tim_001_over_weekend` | TC-TIM-001 | FUNC-018 |
| 110 | `test_tg06_time_calendar.py` | TestTimePlanning | `test_tim_002_global_leave` | TC-TIM-002 | FUNC-018 |
| 111 | `test_tg06_time_calendar.py` | TestTimePlanning | `test_tim_003_zero_target` | TC-TIM-003 | FUNC-018 |
| 112 | `test_tg06_time_calendar.py` | TestTimePlanning | `test_tim_004_start_at_closing_time` | TC-TIM-004 | FUNC-018 |
| 113 | `test_tg06_time_calendar.py` | TestTimePlanning | `test_tim_005_local_timezone` | TC-TIM-005 | FUNC-018 |
| 114 | `test_tg06_time_calendar.py` | TestTimePlanning | `test_tim_006_no_calendar_24x7` | TC-TIM-006 | FUNC-018 |
| 115 | `test_tg06_time_calendar.py` | TestTimePlanning | `test_tim_007_unplannable_calendar` | TC-TIM-007 | FUNC-018 |
| 116 | `test_tg06_time_calendar.py` | TestTimeElapsed | `test_tim_008_accumulate_across_pause` | TC-TIM-008, TC-TIM-010, TC-TIM-011 | FUNC-043 |
| 117 | `test_tg06_time_calendar.py` | TestTimeElapsed | `test_tim_009_working_hours_only` | TC-TIM-009 | FUNC-043 |
| 118 | `test_tg06_time_calendar.py` | TestCalendarSource | `test_cal_001_empty_calendar_rejected` | TC-CAL-001 | FUNC-039 |
| 119 | `test_tg06_time_calendar.py` | TestCalendarSource | `test_cal_002_valid_calendar_saved` | TC-CAL-002 | FUNC-039 |
| 120 | `test_tg06_time_calendar.py` | TestCalendarSource | `test_cal_003_flexible_calendar_rejected` | TC-CAL-003 | INT-009 |
| 121 | `test_tg06_time_calendar.py` | TestCalendarSource | `test_cal_006_007_invalid_paths` | TC-CAL-006, TC-CAL-007 | FUNC-019 |
| 122 | `test_tg06_time_calendar.py` | TestCalendarSource | `test_cal_008_none_is_24x7` | TC-CAL-008 | FUNC-019 |
| 123 | `test_tg06_time_calendar.py` | TestCalendarSource | `test_cal_005_009_path_resolves_record_calendar` | TC-CAL-005, TC-CAL-009 | FUNC-019 |
| 124 | `test_tg06_time_calendar.py` | TestCalendarSource | `test_cal_011_013_fallbacks` | TC-CAL-011, TC-CAL-013 | FUNC-020 |
| 125 | `test_tg07_retroactive.py` | TestRetroactiveStart | `test_ret_001_start_from_field` | TC-RET-001 | FUNC-017 |
| 126 | `test_tg07_retroactive.py` | TestRetroactiveStart | `test_ret_003_empty_field_uses_now` | TC-RET-003 | FUNC-017 |
| 127 | `test_tg07_retroactive.py` | TestRetroactiveStart | `test_ret_004_breach_at_attach` | TC-RET-004 | FUNC-017 |
| 128 | `test_tg07_retroactive.py` | TestRetroactiveStart | `test_ret_005_one_minute_left` | TC-RET-005 | FUNC-017 |
| 129 | `test_tg07_retroactive.py` | TestRetroactiveStart | `test_ret_006_paused_before_attach` | TC-RET-006 | FUNC-017 |
| 130 | `test_tg07_retroactive.py` | TestRetroactiveStart | `test_ret_007_calendar_across_weekend` | TC-RET-007 | FUNC-017, FUNC-018 |
| 131 | `test_tg07_retroactive.py` | TestRetroactiveFieldValidation | `test_ret_008_char_field_rejected` | TC-RET-008 | FUNC-041 |
| 132 | `test_tg07_retroactive.py` | TestRetroactiveFieldValidation | `test_ret_009_other_model_rejected` | TC-RET-009 | FUNC-041 |
| 133 | `test_tg07_retroactive.py` | TestRetroactiveFieldValidation | `test_ret_010_reset_field_other_model_rejected` | TC-RET-010 | FUNC-041 |
| 134 | `test_tg07_retroactive.py` | TestRetroactiveFieldValidation | `test_ret_011_012_valid_fields` | TC-RET-011, TC-RET-012 | FUNC-041 |
| 135 | `test_tg08_more.py` | TestEscalationValidation | `test_esc_002_003_percent_not_positive` | TC-ESC-002, TC-ESC-003 | FUNC-023 |
| 136 | `test_tg08_more.py` | TestEscalationValidation | `test_esc_004_percent_not_integer` | TC-ESC-004 | FUNC-023 |
| 137 | `test_tg08_more.py` | TestEscalationValidation | `test_esc_005_percent_one` | TC-ESC-005 | FUNC-023 |
| 138 | `test_tg08_more.py` | TestEscalationValidation | `test_esc_044_045_action_model` | TC-ESC-044, TC-ESC-045 | FUNC-038 |
| 139 | `test_tg08_more.py` | TestEscalationFiring | `test_esc_006_007_threshold` | TC-ESC-006, TC-ESC-007 | FUNC-023 |
| 140 | `test_tg08_more.py` | TestEscalationFiring | `test_esc_010_save_does_not_run_action` | TC-ESC-010 | FUNC-025 |
| 141 | `test_tg08_more.py` | TestEscalationFiring | `test_esc_011_to_014_no_fire_when_not_running` | TC-ESC-011, TC-ESC-012, TC-ESC-013, TC-ESC-014 | FUNC-054 |
| 142 | `test_tg08_more.py` | TestEscalationFiring | `test_esc_015_resume_recomputes_due` | TC-ESC-015 | FUNC-055 |
| 143 | `test_tg08_more.py` | TestEscalationFiring | `test_esc_017_paused_not_recomputed` | TC-ESC-017 | FUNC-055 |
| 144 | `test_tg08_more.py` | TestEscalationFiring | `test_esc_024_failed_action_marks_done_no_retry` | TC-ESC-024 | FUNC-026 |
| 145 | `test_tg08_more.py` | TestEscalationFiring | `test_esc_046_late_escalation_not_caught_up` | TC-ESC-046 | FUNC-053 |
| 146 | `test_tg08_more.py` | TestEscalationFiring | `test_esc_047_late_escalation_fires_at_threshold` | TC-ESC-047 | FUNC-053 |
| 147 | `test_tg08_more.py` | TestEmailEscalation | `test_esc_060_fixed_email` | TC-EML-001 | FUNC-064 |
| 148 | `test_tg08_more.py` | TestEmailEscalation | `test_esc_061_field_email` | TC-EML-002 | FUNC-065 |
| 149 | `test_tg08_more.py` | TestEmailEscalation | `test_esc_062_responsible_email` | TC-EML-003 | FUNC-065 |
| 150 | `test_tg08_more.py` | TestEmailEscalation | `test_esc_064_responsible_x2many_multiple_to` | TC-EML-004 | FUNC-065 |
| 151 | `test_tg08_more.py` | TestEmailEscalation | `test_esc_063_no_recipient_marks_failed` | TC-EML-005 | FUNC-026, FUNC-065 |
| 152 | `test_tg08_more.py` | TestEmailEscalation | `test_esc_065_no_template_falls_back_to_plain_body` | TC-EML-006 | FUNC-064 |
| 153 | `test_tg08_more.py` | TestEmailEscalation | `test_esc_066_template_wrong_model_rejected` | TC-EML-007 | FUNC-064 |
| 154 | `test_tg08_more.py` | TestEscalationCompanyAndProgress | `test_esc_050_runs_in_record_company` | TC-ESC-050 | INT-019 |
| 155 | `test_tg08_more.py` | TestEscalationCompanyAndProgress | `test_esc_051_no_company_access_fails_once` | TC-ESC-051 | INT-019 |
| 156 | `test_tg08_more.py` | TestEscalationCompanyAndProgress | `test_esc_053_progress_reported_per_task` | TC-ESC-053 | REL-002 |
| 157 | `test_tg08_more.py` | TestEscalationCompanyAndProgress | `test_esc_054_resume_after_interruption` | TC-ESC-054 | REL-002 |
| 158 | `test_tg08_more.py` | TestEscalationCompanyAndProgress | `test_esc_055_no_time_left` | TC-ESC-055 | REL-002 |
| 159 | `test_tg08_more.py` | TestEscalationCompanyAndProgress | `test_esc_056_058_batch_size_setting` | TC-ESC-056, TC-ESC-057, TC-ESC-058 | REL-002 |
| 160 | `test_tg11_change_archive.py` | TestChangeConfig | `test_chg_001_running_task_keeps_target` | TC-CHG-001 | FUNC-021 |
| 161 | `test_tg11_change_archive.py` | TestChangeConfig | `test_chg_003_new_task_uses_new_target` | TC-CHG-003 | FUNC-021 |
| 162 | `test_tg11_change_archive.py` | TestChangeConfig | `test_chg_007_recalculate_applies_new_target` | TC-CHG-007 | INT-005 |
| 163 | `test_tg11_change_archive.py` | TestChangeConfig | `test_chg_006_recalculate_keeps_elapsed` | TC-CHG-006 | INT-005 |
| 164 | `test_tg11_change_archive.py` | TestChangeConfig | `test_chg_008_010_recalculate_ignores_finished` | TC-CHG-008, TC-CHG-009, TC-CHG-010 | INT-005 |
| 165 | `test_tg11_change_archive.py` | TestChangeConfig | `test_chg_011_recalculate_paused` | TC-CHG-011 | INT-005 |
| 166 | `test_tg11_change_archive.py` | TestChangeConfig | `test_chg_028_viewer_cannot_recalculate` | TC-CHG-028 | INT-005 |
| 167 | `test_tg11_change_archive.py` | TestChangeConfig | `test_chg_012_013_escalation_added_late` | TC-CHG-012, TC-CHG-013 | FUNC-053 |
| 168 | `test_tg11_change_archive.py` | TestArchiveDelete | `test_chg_015_017_archive_unarchive` | TC-CHG-015, TC-CHG-016, TC-CHG-017 | FUNC-033 |
| 169 | `test_tg11_change_archive.py` | TestArchiveDelete | `test_chg_019_archived_keeps_breach` | TC-CHG-019 | FUNC-060 |
| 170 | `test_tg11_change_archive.py` | TestArchiveDelete | `test_chg_021_023_archived_still_transitions` | TC-CHG-021, TC-CHG-022, TC-CHG-023 | FUNC-060 |
| 171 | `test_tg11_change_archive.py` | TestArchiveDelete | `test_chg_024_027_reject_delete_with_tasks` | TC-CHG-024, TC-CHG-026, TC-CHG-027 | FUNC-061 |
| 172 | `test_tg11_change_archive.py` | TestArchiveDelete | `test_chg_025_delete_without_tasks` | TC-CHG-025 | FUNC-061 |
| 173 | `test_tg11_more.py` | TestDefinitionSaving | `test_gen_002_full_definition_roundtrip` | TC-GEN-002 | FUNC-001 |
| 174 | `test_tg11_more.py` | TestDefinitionSaving | `test_gen_003_model_required` | TC-GEN-003 | FUNC-001 |
| 175 | `test_tg11_more.py` | TestDefinitionSaving | `test_gen_004_negative_target_rejected` | TC-GEN-004 | FUNC-001 |
| 176 | `test_tg11_more.py` | TestDefinitionSaving | `test_gen_005_zero_target_accepted` | TC-GEN-005 | FUNC-001 |
| 177 | `test_tg11_more.py` | TestMisconfigMore | `test_mis_002_003_start_subset_of_stop` | TC-MIS-002, TC-MIS-003 | FUNC-016 |
| 178 | `test_tg11_more.py` | TestMisconfigMore | `test_mis_008_exclusive_start_pause` | TC-MIS-008 | FUNC-016 |
| 179 | `test_tg11_more.py` | TestMultipleMore | `test_mul_003_independent_tasks` | TC-MUL-003 | FUNC-014 |
| 180 | `test_tg11_more.py` | TestMultipleMore | `test_mul_005_new_active_after_cancelled` | TC-MUL-005 | FUNC-007, FUNC-014 |
| 181 | `test_tg11_more.py` | TestChangeCalendar | `test_chg_002_definition_calendar_snapshot` | TC-CHG-002 | FUNC-021 |
| 182 | `test_tg11_more.py` | TestChangeCalendar | `test_chg_004_005_path_calendar_snapshot_and_recalculate` | TC-CHG-004, TC-CHG-005 | FUNC-052 |
| 183 | `test_tg11_more.py` | TestChangeCalendar | `test_chg_018_archived_stop_one_of_30` | TC-CHG-018 | FUNC-060 |
| 184 | `test_tg11_more.py` | TestChangeCalendar | `test_chg_020_archived_no_new_task` | TC-CHG-020 | FUNC-060 |
| 185 | `test_tg11_more.py` | TestCalendarFallbacks | `test_cal_004_flexible_falls_back` | TC-CAL-004 | INT-009 |
| 186 | `test_tg11_more.py` | TestCalendarFallbacks | `test_cal_010_empty_step` | TC-CAL-010 | FUNC-020 |
| 187 | `test_tg11_more.py` | TestCalendarFallbacks | `test_cal_012_no_working_hours` | TC-CAL-012 | FUNC-020 |
| 188 | `test_tg11_more.py` | TestCalendarFallbacks | `test_cal_014_record_without_company_uses_current` | TC-CAL-014 | FUNC-020 |
| 189 | `test_tg11_more.py` | TestCalendarFallbacks | `test_cal_015_user_without_read_access` | TC-CAL-015 | FUNC-020 |
| 190 | `test_tg12_errors.py` | TestEngineErrors | `test_err_001_002_record_saved_with_error_event` | TC-ERR-001, TC-ERR-002, TC-ERR-006, TC-ERR-012 | FUNC-030, FUNC-040, OBS-001 |
| 191 | `test_tg12_errors.py` | TestEngineErrors | `test_err_008_log_line` | TC-ERR-008 | OBS-002 |
| 192 | `test_tg12_errors.py` | TestEngineErrors | `test_err_009_011_no_field_values_leak` | TC-ERR-009, TC-ERR-011 | OBS-003 |
| 193 | `test_tg12_errors.py` | TestEngineErrors | `test_err_011c_engine_error_value_in_message` | TC-ERR-011 | OBS-003 |
| 194 | `test_tg12_errors.py` | TestEngineErrors | `test_err_011b_raw_exception_values_redacted` | TC-ERR-030 | FUNC-026, OBS-003 |
| 195 | `test_tg12_errors.py` | TestEngineErrors | `test_err_013_mark_resolved` | TC-ERR-013 | FUNC-040 |
| 196 | `test_tg12_errors.py` | TestEngineErrors | `test_err_014_reevaluate_resolves` | TC-ERR-014, TC-ERR-016 | FUNC-031, FUNC-040 |
| 197 | `test_tg12_errors.py` | TestEngineErrors | `test_err_015_still_broken` | TC-ERR-015 | FUNC-040 |
| 198 | `test_tg12_errors.py` | TestEngineErrors | `test_err_017_keeps_achieved_task` | TC-ERR-017 | FUNC-031 |
| 199 | `test_tg12_errors.py` | TestEngineErrors | `test_err_018_ignores_non_error_events` | TC-ERR-018 | FUNC-031 |
| 200 | `test_tg12_errors.py` | TestEngineErrors | `test_err_019_viewer_denied` | TC-ERR-019 | FUNC-031 |
| 201 | `test_tg12_errors.py` | TestEngineErrors | `test_err_020_start_now_without_retroactive` | TC-ERR-020 | FUNC-031 |
| 202 | `test_tg12_more.py` | TestEngineErrorsMore | `test_err_003_007_empty_calendar` | TC-ERR-003, TC-ERR-007 | FUNC-030, OBS-001 |
| 203 | `test_tg12_more.py` | TestEngineErrorsMore | `test_err_004_isolation_per_record` | TC-ERR-004 | FUNC-030 |
| 204 | `test_tg12_more.py` | TestEngineErrorsMore | `test_err_021_retroactive_reevaluate` | TC-ERR-021 | FUNC-031 |
| 205 | `test_tg12_more.py` | TestEngineErrorsMore | `test_err_022_023_unresolved_count` | TC-ERR-022, TC-ERR-023 | INT-022 |
| 206 | `test_tg12_more.py` | TestEngineErrorsMore | `test_err_024_non_group_hidden` | TC-ERR-024 | INT-022 |
| 207 | `test_tg13_compute.py` | TestStoredCompute | `test_cmp_001_stage_drives_stored_compute` | TC-CMP-001 | FUNC-005 |
| 208 | `test_tg13_compute.py` | TestStoredCompute | `test_cmp_002_three_writes_no_extra_events` | TC-CMP-002 | FUNC-005 |
| 209 | `test_tg13_compute.py` | TestStoredCompute | `test_cmp_003_compute_change_same_condition_result` | TC-CMP-003 | FUNC-005 |
| 210 | `test_tg13_compute.py` | TestStoredCompute | `test_cmp_004_child_change_drives_parent_stop` | TC-CMP-004 | FUNC-005 |
| 211 | `test_tg13_compute.py` | TestStoredCompute | `test_cmp_005_unwatched_recompute_skipped` | TC-CMP-005 | FUNC-005 |
| 212 | `test_tg13_compute.py` | TestManualReevaluate | `test_cmp_006_010_relation_condition_needs_reevaluate` | TC-CMP-006, TC-CMP-010 | FUNC-032, FUNC-042 |
| 213 | `test_tg13_compute.py` | TestManualReevaluate | `test_cmp_007_008_unstored_compute_no_error` | TC-CMP-007, TC-CMP-008 | FUNC-042 |
| 214 | `test_tg13_compute.py` | TestManualReevaluate | `test_cmp_011_batch_attaches_only_matching` | TC-CMP-011 | FUNC-032 |
| 215 | `test_tg13_compute.py` | TestManualReevaluate | `test_cmp_012_015_reevaluate_idempotent_and_now` | TC-CMP-012, TC-CMP-015 | FUNC-032 |
| 216 | `test_tg13_compute.py` | TestManualReevaluate | `test_cmp_013_viewer_denied` | TC-CMP-013 | FUNC-032 |
| 217 | `test_tg13_compute.py` | TestManualReevaluate | `test_cmp_014_no_reset_on_manual_reevaluate` | TC-CMP-014 | FUNC-032 |
| 218 | `test_tg13_compute.py` | TestManualReevaluate | `test_cmp_016_stop_beats_cancel` | TC-CMP-016 | FUNC-032 |
| 219 | `test_tg13_compute.py` | TestDerivedConditionFields | `test_start_on_unstored_related_field_still_attaches` | TC-CMP-017 | FUNC-005, FUNC-042 |
| 220 | `test_tg14_infra.py` | TestModelRestrictions | `test_inf_001_to_006_forbidden_models` | TC-INF-001, TC-INF-002, TC-INF-003, TC-INF-004, TC-INF-005, TC-INF-006 | FUNC-002 |
| 221 | `test_tg14_infra.py` | TestModelRestrictions | `test_inf_007_partner_accepted` | TC-INF-007 | FUNC-002 |
| 222 | `test_tg14_infra.py` | TestModelRestrictions | `test_inf_009_ir_model_not_observed` | TC-INF-009 | FUNC-002 |
| 223 | `test_tg14_infra.py` | TestHousekeeping | `test_inf_010_orphans_removed` | TC-INF-010 | FUNC-034 |
| 224 | `test_tg14_infra.py` | TestHousekeeping | `test_inf_011_012_keep_existing_records` | TC-INF-011, TC-INF-012 | FUNC-034 |
| 225 | `test_tg14_infra.py` | TestHousekeeping | `test_inf_013_to_016_retention` | TC-INF-013, TC-INF-014, TC-INF-015, TC-INF-016 | FUNC-035 |
| 226 | `test_tg14_infra.py` | TestRetentionSetting | `test_inf_017_default_365` | TC-INF-017 | INT-010 |
| 227 | `test_tg14_infra.py` | TestRetentionSetting | `test_inf_018_019_invalid_values` | TC-INF-018, TC-INF-019 | INT-010 |
| 228 | `test_tg14_infra.py` | TestRetentionSetting | `test_inf_020_021_valid_values` | TC-INF-020, TC-INF-021 | INT-010 |
| 229 | `test_tg14_infra.py` | TestRetentionSetting | `test_inf_022_viewer_denied` | TC-INF-022 | INT-010 |
| 230 | `test_tg14_infra.py` | TestSchemaAndSource | `test_inf_027_029_no_columns_added` | TC-INF-027, TC-INF-029 | INST-003 |
| 231 | `test_tg14_infra.py` | TestSchemaAndSource | `test_inf_ondelete_company_calendar_restricted` | TC-INF-036 | FUNC-001 |
| 232 | `test_tg14_infra.py` | TestSchemaAndSource | `test_inf_next_due_at_only_partial_index` | TC-INF-037 | PERF-003 |
| 233 | `test_tg14_infra.py` | TestSchemaAndSource | `test_inf_034_only_stdlib_and_odoo_imports` | TC-INF-034 | PORT-001 |
| 234 | `test_tg14_infra.py` | TestSchemaAndSource | `test_ins_001_depends` | TC-INS-001 | INST-002 |
| 235 | `test_tg14_infra.py` | TestSchemaAndSource | `test_ins_002_no_forbidden_references` | TC-INS-002 | INST-002 |
| 236 | `test_tg14_infra.py` | TestSchemaAndSource | `test_ins_004_js_scoped_to_static_src` | TC-INS-004 | BUILD-001 |
| 237 | `test_tg14_infra.py` | TestSchemaAndSource | `test_ins_005_pylintrc_covers_module` | TC-INS-005 | BUILD-001 |
| 238 | `test_tg14_infra.py` | TestSchemaAndSource | `test_ins_012_suite_is_generic` | TC-INS-012 | MAINT-002 |
| 239 | `test_tg16_more.py` | TestSecurityMore | `test_sec_admin_default_sla_manager` | TC-SEC-025 | SEC-001 |
| 240 | `test_tg16_more.py` | TestSecurityMore | `test_sec_015_escalation_permission_note` | TC-SEC-015 | SEC-004 |
| 241 | `test_tg16_more.py` | TestSecurityMore | `test_sec_001_menu_hidden` | TC-SEC-001 | SEC-001 |
| 242 | `test_tg16_more.py` | TestSecurityMore | `test_sec_013_denied_action_fails` | TC-SEC-013 | SEC-004 |
| 243 | `test_tg16_more.py` | TestSecurityMore | `test_sec_021_recalculate_by_manager` | TC-SEC-021 | SEC-006 |
| 244 | `test_tg16_more.py` | TestSecurityMore | `test_sec_023_readonly_views` | TC-SEC-023 | SEC-006 |
| 245 | `test_tg16_more.py` | TestSecurityLinkedRecord | `test_sec_016_calendar_resolved_without_read_access` | TC-SEC-016 | SEC-005 |
| 246 | `test_tg16_more.py` | TestSecurityLinkedRecord | `test_sec_017_no_leak_of_linked_record` | TC-SEC-017 | SEC-005 |
| 247 | `test_tg16_security.py` | TestSecurity | `test_sec_002_003_definition_write` | TC-SEC-002, TC-SEC-003 | SEC-001 |
| 248 | `test_tg16_security.py` | TestSecurity | `test_sec_004_viewer_reads` | TC-SEC-004 | SEC-001 |
| 249 | `test_tg16_security.py` | TestSecurity | `test_sec_005_007_plain_user_denied` | TC-SEC-005, TC-SEC-007 | SEC-001, SEC-002 |
| 250 | `test_tg16_security.py` | TestSecurity | `test_sec_006_task_created_with_record_rights_only` | TC-SEC-006 | SEC-002 |
| 251 | `test_tg16_security.py` | TestSecurity | `test_sec_018_manager_cannot_write_tasks` | TC-SEC-018 | SEC-006 |
| 252 | `test_tg16_security.py` | TestSecurity | `test_sec_019_020_event_rights` | TC-SEC-019, TC-SEC-020 | SEC-006 |
| 253 | `test_tg16_security.py` | TestSecurity | `test_sec_022_viewer_cannot_mark_resolved` | TC-SEC-022 | SEC-006 |
| 254 | `test_tg16_security.py` | TestSecurity | `test_sec_024_viewer_cannot_create_escalation` | TC-SEC-024 | SEC-001 |
| 255 | `test_tg16_security.py` | TestMultiCompany | `test_sec_008_009_hidden_other_company` | TC-SEC-008, TC-SEC-009 | SEC-003 |
| 256 | `test_tg16_security.py` | TestMultiCompany | `test_sec_010_definition_visibility` | TC-SEC-010 | SEC-003 |
| 257 | `test_tg16_security.py` | TestMultiCompany | `test_sec_011_012_definition_company_scope` | TC-SEC-011, TC-SEC-012 | SEC-003 |
| 258 | `test_tg17_ui.py` | TestDefinitionForm | `test_uix_001_save_via_form` | TC-UIX-001 | INT-001 |
| 259 | `test_tg17_ui.py` | TestDefinitionForm | `test_uix_002_viewer_readonly` | TC-UIX-002 | INT-001 |
| 260 | `test_tg17_ui.py` | TestDefinitionForm | `test_uix_004_005_help_warnings` | TC-CMP-009, TC-UIX-004, TC-UIX-005 | FUNC-042, INT-002 |
| 261 | `test_tg17_ui.py` | TestDefinitionForm | `test_uix_009_calendar_fallback_note_in_arch` | TC-UIX-009 | INT-003 |
| 262 | `test_tg17_ui.py` | TestTaskViews | `test_uix_010_list_fields` | TC-UIX-010 | INT-004 |
| 263 | `test_tg17_ui.py` | TestTaskViews | `test_uix_011_form_readonly` | TC-UIX-011 | INT-004 |
| 264 | `test_tg17_ui.py` | TestTaskViews | `test_uix_013_to_016_action_binding` | TC-UIX-013, TC-UIX-014, TC-UIX-015, TC-UIX-016 | INT-006 |
| 265 | `test_tg17_ui.py` | TestTaskFilters | `test_uix_018_019_status_filters` | TC-UIX-018, TC-UIX-019 | INT-011 |
| 266 | `test_tg17_ui.py` | TestTaskFilters | `test_uix_020_to_024_due_soon` | TC-UIX-020, TC-UIX-021, TC-UIX-022, TC-UIX-023, TC-UIX-024 | INT-012 |
| 267 | `test_tg17_ui.py` | TestTaskFilters | `test_uix_023_025_setting_roles` | TC-UIX-023, TC-UIX-025 | INT-012 |
| 268 | `test_tg17_ui.py` | TestTaskFilters | `test_uix_026_027_grouping` | TC-UIX-026, TC-UIX-027 | INT-013 |
| 269 | `test_tg17_ui.py` | TestReevaluateAndEvents | `test_uix_032_033_034_reevaluate_action` | TC-UIX-032, TC-UIX-033, TC-UIX-034 | INT-020 |
| 270 | `test_tg17_ui.py` | TestReevaluateAndEvents | `test_uix_035_to_038_event_filters_grouping` | TC-UIX-035, TC-UIX-036, TC-UIX-037, TC-UIX-038 | INT-021 |
| 271 | `test_tg17_ui.py` | TestReportMeasures | `test_uix_039_achieved_rate_excludes_cancelled` | TC-UIX-039 | FUNC-036 |
| 272 | `test_tg17_ui.py` | TestReportMeasures | `test_uix_040_no_ended_tasks_is_undefined` | TC-UIX-040 | FUNC-036 |
| 273 | `test_tg17_ui.py` | TestReportMeasures | `test_uix_041_month_boundary_timezone` | TC-UIX-041 | FUNC-036 |
| 274 | `test_tg17_ui.py` | TestReportMeasures | `test_uix_042_043_044_breaching_counts` | TC-UIX-042, TC-UIX-043, TC-UIX-044 | FUNC-062 |
| 275 | `test_tg18_more.py` | TestQueryCount | `test_prf_003_attach_batch` | TC-PRF-003 | PERF-002 |
| 276 | `test_tg18_more.py` | TestQueryCount | `test_prf_004_no_match_batch` | TC-PRF-004 | PERF-002 |
| 277 | `test_tg18_more.py` | TestQueryCount | `test_prf_005_stop_batch` | TC-PRF-005 | PERF-002 |
| 278 | `test_tg18_more.py` | TestBackgroundScale | `test_prf_007_200_escalations_four_calls` | TC-PRF-007 | PERF-003 |
| 279 | `test_tg18_more.py` | TestBackgroundScale | `test_prf_008_200_breaches_four_calls` | TC-PRF-008 | PERF-003 |
| 280 | `test_tg18_more.py` | TestBackgroundScale | `test_prf_006_cycle_time_independent_of_total` | TC-PRF-006 | PERF-003 |
| 281 | `test_tg18_more.py` | TestCronAndPatches | `test_prf_009_cron_every_minute` | TC-PRF-009 | PERF-003 |
| 282 | `test_tg18_more.py` | TestCronAndPatches | `test_prf_010_patch_only_models_with_definition` | TC-PRF-010 | FUNC-004, FUNC-005, PERF-001 |
| 283 | `test_tg18_performance.py` | TestPerformanceLoad | `test_prf_load_300_tickets_30_tasks` | TC-PRF-011 | PERF-001, PERF-002, REL-002 |
| 284 | `test_tg18_performance.py` | TestPerformanceLoad | `test_prf_percent_used_list_80` | TC-PRF-012 | INT-023, PERF-002 |
| 285 | `test_tg18_performance.py` | TestPerformanceLoad | `test_prf_percent_used_list_80_holidays` | TC-PRF-013 | INT-023, PERF-002 |
| 286 | `test_tg19_extension.py` | TestCalendarExtension | `test_ext_001_team_calendar` | TC-EXT-001 | INT-007 |
| 287 | `test_tg19_extension.py` | TestCalendarExtension | `test_ext_002_005_fallback_on_unusable` | TC-EXT-002, TC-EXT-005 | INT-007 |
| 288 | `test_tg19_extension.py` | TestCalendarExtension | `test_ext_004_default_sources` | TC-EXT-004 | INT-007 |
| 289 | `test_tg19_extension.py` | TestValueExtensions | `test_ext_006_007_010_target_hours` | TC-EXT-006, TC-EXT-007, TC-EXT-010 | INT-015 |
| 290 | `test_tg19_extension.py` | TestValueExtensions | `test_ext_008_negative_hours` | TC-EXT-008 | INT-015 |
| 291 | `test_tg19_extension.py` | TestValueExtensions | `test_ext_009_zero_hours` | TC-EXT-009 | INT-015 |
| 292 | `test_tg19_extension.py` | TestValueExtensions | `test_ext_011_012_start_dt` | TC-EXT-011, TC-EXT-012 | INT-016 |
| 293 | `test_tg19_extension.py` | TestValueExtensions | `test_ext_013_retroactive_field` | TC-EXT-013 | INT-016 |
| 294 | `test_tg19_extension.py` | TestValueExtensions | `test_ext_014_015_016_domain_override` | TC-EXT-014, TC-EXT-015, TC-EXT-016 | INT-017 |
| 295 | `test_tg19_extension.py` | TestTransitionHook | `test_ext_017_pause_calls_hook_once` | TC-EXT-017 | INT-018 |
| 296 | `test_tg19_extension.py` | TestTransitionHook | `test_ext_018_no_transition_no_call` | TC-EXT-018 | INT-018 |
| 297 | `test_tg19_extension.py` | TestTransitionHook | `test_ext_019_complete_calls_hook` | TC-EXT-019 | INT-018 |
| 298 | `test_tg19_extension.py` | TestTransitionHook | `test_ext_attach_calls_hook` | TC-EXT-021 | REUSE-001 |
| 299 | `test_tg19_extension.py` | TestSignatureContract | `test_ext_022_contract` | TC-EXT-022 | REUSE-001 |
| 300 | `test_tg19_extension.py` | TestSignatureContract | `test_ext_020_default_hook_noop` | TC-EXT-020 | INT-018 |
| 301 | `test_tg20_concurrency.py` | TestConcurrentAttach | `test_err_005_mul_007_two_transactions_attach_same_record` | TC-ERR-005, TC-MUL-007 | FUNC-014, FUNC-030, REL-001 |
| 302 | `test_tg20_concurrency.py` | TestConcurrentProcessing | `test_esc_009_locked_task_skipped` | TC-ESC-009 | FUNC-024 |
| 303 | `test_tg20_concurrency.py` | TestConcurrentProcessing | `test_esc_059_stop_other_task_not_blocked` | TC-ESC-059 | REL-002 |
| 304 | `test_tg20_concurrency.py` | TestConcurrentProcessing | `test_err_027_029_task_stopped_before_lock` | TC-ERR-027, TC-ERR-029 | REL-001, REL-002 |
| 305 | `test_tg20_concurrency.py` | TestConcurrentProcessing | `test_err_026_stop_conflicts_with_committed_processing` | TC-ERR-026 | REL-001 |
| 306 | `test_tg21_new_fields.py` | TestNewMetadataFields | `test_type_default_sla` | TC-MDF-001 | FUNC-070 |
| 307 | `test_tg21_new_fields.py` | TestNewMetadataFields | `test_type_ola` | TC-MDF-002 | FUNC-070 |
| 308 | `test_tg21_new_fields.py` | TestNewMetadataFields | `test_vendor_id_set` | TC-MDF-003 | FUNC-070 |
| 309 | `test_tg21_new_fields.py` | TestNewMetadataFields | `test_vendor_id_default_empty` | TC-MDF-004 | FUNC-070 |
| 310 | `test_tg21_new_fields.py` | TestNewMetadataFields | `test_service_commitment_default_false` | TC-MDF-005 | FUNC-070 |
| 311 | `test_tg21_new_fields.py` | TestNewMetadataFields | `test_service_commitment_true` | TC-MDF-006 | FUNC-070 |
| 312 | `test_tg21_new_fields.py` | TestNewMetadataFields | `test_target_default_empty` | TC-MDF-007 | FUNC-070 |
| 313 | `test_tg21_new_fields.py` | TestNewMetadataFields | `test_target_response` | TC-MDF-008 | FUNC-070 |
| 314 | `test_tg21_new_fields.py` | TestNewMetadataFields | `test_target_resolution` | TC-MDF-009 | FUNC-070 |
| 315 | `test_tg21_new_fields.py` | TestNewMetadataFields | `test_metadata_fields_do_not_change_engine_behaviour` | TC-MDF-010 | FUNC-070 |
| 316 | `test_tg22_retroactive_pause.py` | TestRetroactivePauseWarning | `test_warning_model_not_trackable` | TC-RPS-001 | FUNC-071 |
| 317 | `test_tg22_retroactive_pause.py` | TestRetroactivePauseWarning | `test_warning_field_not_tracked` | TC-RPS-002 | FUNC-071 |
| 318 | `test_tg22_retroactive_pause.py` | TestRetroactivePauseWarning | `test_no_warning_when_all_pause_fields_tracked` | TC-RPS-003 | FUNC-071 |
| 319 | `test_tg22_retroactive_pause.py` | TestRetroactivePauseWarning | `test_no_warning_when_feature_off` | TC-RPS-004 | FUNC-071 |
| 320 | `test_tg22_retroactive_pause.py` | TestRetroactivePauseWarning | `test_warning_recomputes_when_pause_domain_changes` | TC-RPS-005 | FUNC-071 |
| 321 | `test_tg22_retroactive_pause.py` | TestRetroactivePauseAlgorithm | `test_excludes_tracked_pause_history` | TC-RPS-006 | FUNC-071 |
| 322 | `test_tg22_retroactive_pause.py` | TestRetroactivePauseAlgorithm | `test_flag_off_counts_full_backdated_window` | TC-RPS-007 | FUNC-071 |
| 323 | `test_tg22_retroactive_pause.py` | TestRetroactivePauseAlgorithm | `test_no_history_in_window_no_effect` | TC-RPS-008 | FUNC-071 |
| 324 | `test_tg22_retroactive_pause.py` | TestRetroactivePauseAlgorithm | `test_untracked_pause_field_falls_back_no_effect` | TC-RPS-009 | FUNC-071 |
| 325 | `test_tg23_tz_override.py` | TestCalendarTzOverride | `test_override_shifts_working_hours` | TC-TZO-001 | FUNC-067 |
| 326 | `test_tg23_tz_override.py` | TestCalendarTzOverride | `test_override_reuses_cached_clone_no_duplicate` | TC-TZO-002 | FUNC-067 |
| 327 | `test_tg23_tz_override.py` | TestCalendarTzOverride | `test_override_does_not_mutate_source_calendar` | TC-TZO-003 | FUNC-067 |
| 328 | `test_tg23_tz_override.py` | TestCalendarTzOverride | `test_clone_copies_attendance_pattern` | TC-TZO-004 | FUNC-067 |
| 329 | `test_tg23_tz_override.py` | TestCalendarTzOverride | `test_no_override_no_clone_created` | TC-TZO-005 | FUNC-067 |
| 330 | `test_tg24_clock_duration.py` | TestOriginalBreachTime | `test_set_once_at_attach_never_rewritten_on_resume` | TC-CLK-001 | FUNC-072 |
| 331 | `test_tg24_clock_duration.py` | TestOriginalBreachTime | `test_unaffected_by_action_recalculate` | TC-CLK-002 | FUNC-072 |
| 332 | `test_tg24_clock_duration.py` | TestClockDuration | `test_equals_business_without_calendar` | TC-CLK-003 | FUNC-072 |
| 333 | `test_tg24_clock_duration.py` | TestClockDuration | `test_differs_from_business_across_weekend` | TC-CLK-004 | FUNC-072 |
| 334 | `test_tg25_enable_conditions_tz.py` | TestEnableDisable | `test_new_definition_is_disabled_by_default` | TC-ENB-001 | FUNC-066 |
| 335 | `test_tg25_enable_conditions_tz.py` | TestEnableDisable | `test_model_name_related_stored` | TC-ENB-002 | FUNC-001, INT-001 |
| 336 | `test_tg25_enable_conditions_tz.py` | TestEnableDisable | `test_enable_disable_toggle_and_reload` | TC-ENB-003 | FUNC-066 |
| 337 | `test_tg25_enable_conditions_tz.py` | TestEnableDisable | `test_enable_without_start_warns_but_enables` | TC-ENB-004 | FUNC-066 |
| 338 | `test_tg25_enable_conditions_tz.py` | TestEnableDisable | `test_enabled_attaches_disabled_does_not` | TC-ENB-005 | FUNC-066 |
| 339 | `test_tg25_enable_conditions_tz.py` | TestHotPath | `test_hook_models_disabled_with_running_task` | TC-ENB-006 | FUNC-066 |
| 340 | `test_tg25_enable_conditions_tz.py` | TestHotPath | `test_disabled_without_running_task_skips_condition_matching` | TC-ENB-007 | FUNC-066, PERF-001 |
| 341 | `test_tg25_enable_conditions_tz.py` | TestHotPath | `test_disabled_with_running_task_still_evaluated` | TC-ENB-008 | FUNC-060, FUNC-066 |
| 342 | `test_tg25_enable_conditions_tz.py` | TestEmptyListNotConfigured | `test_get_domain_empty_list_is_none` | TC-CND-001 | FUNC-003 |
| 343 | `test_tg25_enable_conditions_tz.py` | TestEmptyListNotConfigured | `test_start_empty_list_never_attaches` | TC-CND-002 | FUNC-003 |
| 344 | `test_tg25_enable_conditions_tz.py` | TestEmptyListNotConfigured | `test_start_match_all_attaches` | TC-CND-003 | FUNC-003 |
| 345 | `test_tg25_enable_conditions_tz.py` | TestEmptyListNotConfigured | `test_stop_empty_list_never_completes` | TC-CND-004 | FUNC-003 |
| 346 | `test_tg25_enable_conditions_tz.py` | TestEmptyListNotConfigured | `test_new_definition_has_no_star_watch` | TC-CND-005 | FUNC-003, PERF-001 |
| 347 | `test_tg25_enable_conditions_tz.py` | TestEmptyListNotConfigured | `test_reset_condition_without_fields_watches_all` | TC-CND-006 | FUNC-013, FUNC-051 |
| 348 | `test_tg25_enable_conditions_tz.py` | TestTimezoneRequired | `test_create_fills_user_tz_or_utc` | TC-TZR-001 | FUNC-067 |
| 349 | `test_tg25_enable_conditions_tz.py` | TestTimezoneRequired | `test_create_fills_fixed_calendar_tz` | TC-TZR-002 | FUNC-067 |
| 350 | `test_tg25_enable_conditions_tz.py` | TestTimezoneRequired | `test_create_keeps_explicit_tz` | TC-TZR-003 | FUNC-067 |
| 351 | `test_tg25_enable_conditions_tz.py` | TestTimezoneRequired | `test_onchange_new_record_takes_calendar_tz` | TC-TZR-004 | FUNC-067 |
| 352 | `test_tg25_enable_conditions_tz.py` | TestTimezoneRequired | `test_onchange_saved_record_fills_only_when_empty` | TC-TZR-005 | FUNC-067 |
| 353 | `test_tg25_enable_conditions_tz.py` | TestTimezoneRequired | `test_onchange_ignores_non_definition_source` | TC-TZR-006 | FUNC-067 |
| 354 | `test_tg25_enable_conditions_tz.py` | TestTimezoneRequired | `test_form_new_has_default_tz_and_follows_calendar` | TC-TZR-007 | FUNC-067 |
| 355 | `test_tg25_enable_conditions_tz.py` | TestTimezoneRequired | `test_tz_variant_copies_global_leaves` | TC-TZR-008 | FUNC-067 |
| 356 | `test_tg25_enable_conditions_tz.py` | TestTimezoneRequired | `test_changing_definition_tz_keeps_running_task_deadline` | TC-TZR-009 | FUNC-021, FUNC-067 |
| 357 | `test_tg26_definition_ux.py` | TestDueSoonPerDefinition | `test_compute_uses_definition_then_settings` | TC-DUE-001 | INT-012 |
| 358 | `test_tg26_definition_ux.py` | TestDueSoonPerDefinition | `test_settings_change_applies_to_empty_only` | TC-DUE-002 | INT-012 |
| 359 | `test_tg26_definition_ux.py` | TestDueSoonPerDefinition | `test_search_operators` | TC-DUE-003 | INT-012 |
| 360 | `test_tg26_definition_ux.py` | TestDueSoonPerDefinition | `test_search_excludes_breached_and_paused` | TC-DUE-004 | INT-012 |
| 361 | `test_tg26_definition_ux.py` | TestDueSoonPerDefinition | `test_negative_value_rejected` | TC-DUE-005 | INT-012 |
| 362 | `test_tg26_definition_ux.py` | TestModelLock | `test_model_change_blocked_with_tasks` | TC-LCK-001 | FUNC-069 |
| 363 | `test_tg26_definition_ux.py` | TestModelLock | `test_same_model_write_allowed_with_tasks` | TC-LCK-002 | FUNC-069 |
| 364 | `test_tg26_definition_ux.py` | TestModelLock | `test_model_change_allowed_without_tasks` | TC-LCK-003 | FUNC-069 |
| 365 | `test_tg26_definition_ux.py` | TestAuditTrail | `test_tracked_change_posts_message` | TC-AUD-001 | FUNC-069 |
| 366 | `test_tg26_definition_ux.py` | TestAuditTrail | `test_condition_change_is_tracked` | TC-AUD-002 | FUNC-069 |
| 367 | `test_tg26_definition_ux.py` | TestAuditTrail | `test_form_has_chatter` | TC-AUD-003 | FUNC-069 |
| 368 | `test_tg26_definition_ux.py` | TestSmartButton | `test_running_task_count_counts_in_progress_and_paused` | TC-SBT-001 | INT-025 |
| 369 | `test_tg26_definition_ux.py` | TestSmartButton | `test_count_zero_without_tasks` | TC-SBT-002 | INT-025 |
| 370 | `test_tg26_definition_ux.py` | TestSmartButton | `test_action_opens_all_tasks_of_definition` | TC-SBT-003 | INT-025 |
| 371 | `test_tg26_definition_ux.py` | TestSmartButton | `test_form_arch_button_and_js_class` | TC-SBT-004 | FUNC-069, INT-025 |
| 372 | `test_tg26_definition_ux.py` | TestDefinitionListView | `test_list_arch` | TC-DLV-001 | FUNC-066 |
| 373 | `test_tg26_definition_ux.py` | TestDefinitionListView | `test_action_shows_inactive_without_grouping` | TC-DLV-002 | FUNC-066 |
| 374 | `test_tg26_definition_ux.py` | TestTaskEscalationHistory | `test_only_escalation_events` | TC-EHS-001 | INT-026 |
| 375 | `test_tg26_definition_ux.py` | TestTaskEscalationHistory | `test_newest_first` | TC-EHS-002 | INT-026 |
| 376 | `test_tg26_definition_ux.py` | TestTaskEscalationHistory | `test_form_arch_lists_events` | TC-EHS-003 | INT-026 |
| 377 | `test_tg26_definition_ux.py` | TestOpenSourceRecord | `test_opens_source_record` | TC-OSR-001 | INT-026 |
| 378 | `test_tg26_definition_ux.py` | TestOpenSourceRecord | `test_missing_record_friendly_error` | TC-OSR-002 | INT-026 |
| 379 | `test_tg26_definition_ux.py` | TestOpenSourceRecord | `test_unknown_model_friendly_error` | TC-OSR-003 | INT-026 |
| 380 | `test_tg26_definition_ux.py` | TestOpenSourceRecord | `test_button_in_form_header_always_visible` | TC-OSR-004 | INT-026 |
| 381 | `test_tg26_definition_ux.py` | TestTaskListView | `test_default_columns_and_progressbar` | TC-TLV-001 | INT-027 |
| 382 | `test_tg26_definition_ux.py` | TestLightModeOnly | `test_scss_has_no_dark_block` | TC-LGT-001 | INT-024 |
| 383 | `test_tg26_definition_ux.py` | TestDefinitionFormTour | `test_confirm_save_with_running_tasks` | TC-TOUR-001 | FUNC-069 |
| 384 | `test_tg27_recheck_conditions.py` | TestRecheckConditions | `test_scope_is_one_definition` | TC-RCK-001 | FUNC-032, INT-020 |
| 385 | `test_tg27_recheck_conditions.py` | TestRecheckConditions | `test_closed_task_unchanged_with_event` | TC-RCK-002 | INT-020 |
| 386 | `test_tg27_recheck_conditions.py` | TestRecheckConditions | `test_changed_event_records_old_and_new_stage` | TC-RCK-003 | INT-020 |
| 387 | `test_tg27_recheck_conditions.py` | TestRecheckConditions | `test_many_tasks_grouped_per_definition` | TC-RCK-004 | INT-020 |
| 388 | `test_tg27_recheck_conditions.py` | TestRecheckConditions | `test_viewer_cannot_recheck` | TC-RCK-005 | FUNC-032, INT-020 |
| 389 | `test_tg27_recheck_conditions.py` | TestRecheckConditions | `test_engine_definitions_param_limits_scope` | TC-RCK-006 | FUNC-032 |
| 390 | `test_tg28_apply_settings.py` | TestApplyCurrentSettings | `test_running_task_gets_new_target_and_event` | TC-APS-001 | INT-005 |
| 391 | `test_tg28_apply_settings.py` | TestApplyCurrentSettings | `test_breached_task_keeps_deadline` | TC-APS-002 | INT-005 |
| 392 | `test_tg28_apply_settings.py` | TestApplyCurrentSettings | `test_paused_task_keeps_deadline` | TC-APS-003 | INT-005 |
| 393 | `test_tg28_apply_settings.py` | TestApplyCurrentSettings | `test_unchanged_task_has_no_event_but_counts_updated` | TC-APS-004 | INT-005 |
| 394 | `test_tg28_apply_settings.py` | TestApplyCurrentSettings | `test_closed_tasks_skipped` | TC-APS-005 | INT-005 |
| 395 | `test_tg28_apply_settings.py` | TestApplyCurrentSettings | `test_many_tasks_one_event_each` | TC-APS-006 | INT-005 |
| 396 | `test_tg29_apply_existing.py` | TestApplyExisting | `test_all_matching_records_get_task_and_rerun_has_no_duplicates` | TC-APX-001 | FUNC-068 |
| 397 | `test_tg29_apply_existing.py` | TestApplyExisting | `test_filter_domain_narrows_set` | TC-APX-002 | FUNC-068 |
| 398 | `test_tg29_apply_existing.py` | TestApplyExisting | `test_filter_cannot_widen_start_condition` | TC-APX-003 | FUNC-068 |
| 399 | `test_tg29_apply_existing.py` | TestApplyExisting | `test_unconfigured_start_loads_nothing` | TC-APX-004 | FUNC-003, FUNC-068 |
| 400 | `test_tg29_apply_existing.py` | TestApplyExisting | `test_inactive_definition_rejected` | TC-APX-005 | FUNC-068 |
| 401 | `test_tg29_apply_existing.py` | TestApplyExisting | `test_batching_first_batch_now_rest_by_cron` | TC-APX-006 | FUNC-068, REL-002 |
| 402 | `test_tg29_apply_existing.py` | TestApplyExisting | `test_queued_job_also_blocks_new_job` | TC-APX-007 | FUNC-068 |
| 403 | `test_tg29_apply_existing.py` | TestApplyExisting | `test_cancel_stops_job` | TC-APX-008 | FUNC-068 |
| 404 | `test_tg29_apply_existing.py` | TestApplyExisting | `test_failed_batch_marks_job_failed` | TC-APX-009 | FUNC-068 |
| 405 | `test_tg29_apply_existing.py` | TestApplyExisting | `test_autovacuum_removes_old_finished_keeps_running` | TC-APX-010 | FUNC-068, INT-010 |
| 406 | `test_tg29_apply_existing.py` | TestApplyExisting | `test_backfill_retroactive_leaves_no_pending_passed_escalation` | TC-APX-011 | FUNC-053, FUNC-068 |
| 407 | `test_tg29_apply_existing.py` | TestApplyExisting | `test_security` | TC-APX-012 | FUNC-068, SEC-001 |
| 408 | `test_tg30_form_status.py` | TestRecordSlaSummary | `test_no_task_is_none` | TC-FST-001 | INT-024 |
| 409 | `test_tg30_form_status.py` | TestRecordSlaSummary | `test_missing_id_is_none` | TC-FST-002 | INT-024 |
| 410 | `test_tg30_form_status.py` | TestRecordSlaSummary | `test_running` | TC-FST-003 | INT-024 |
| 411 | `test_tg30_form_status.py` | TestRecordSlaSummary | `test_due_soon` | TC-FST-004 | INT-012, INT-024 |
| 412 | `test_tg30_form_status.py` | TestRecordSlaSummary | `test_paused` | TC-FST-005 | INT-024 |
| 413 | `test_tg30_form_status.py` | TestRecordSlaSummary | `test_breached_running_percent_capped` | TC-FST-006 | INT-024 |
| 414 | `test_tg30_form_status.py` | TestRecordSlaSummary | `test_met` | TC-FST-007 | INT-024 |
| 415 | `test_tg30_form_status.py` | TestRecordSlaSummary | `test_missed` | TC-FST-008 | INT-024 |
| 416 | `test_tg30_form_status.py` | TestRecordSlaSummary | `test_cancelled_only_is_none` | TC-FST-009 | INT-024 |
| 417 | `test_tg30_form_status.py` | TestRecordSlaSummary | `test_multiple_tasks_pick_most_urgent` | TC-FST-010 | INT-024 |
| 418 | `test_tg30_form_status.py` | TestRecordSlaSummary | `test_active_task_wins_over_done_ones` | TC-FST-011 | INT-024 |
| 419 | `test_tg30_form_status.py` | TestRecordSlaSummary | `test_no_sudo_user_without_group_is_refused` | TC-FST-012 | INT-024, SEC-002 |
| 420 | `test_tg30_form_status.py` | TestRecordSlaSummary | `test_sla_user_can_read` | TC-FST-013 | INT-024 |
| 421 | `test_tg30_form_status.py` | TestSessionInfo | `test_flag_on_when_never_configured` | TC-FST-014 | INT-024 |
| 422 | `test_tg30_form_status.py` | TestSessionInfo | `test_setting_off_is_stored_explicitly` | TC-FST-015 | INT-024 |
| 423 | `test_tg30_form_status.py` | TestSessionInfo | `test_models_listed_for_sla_user` | TC-FST-016 | INT-024 |
| 424 | `test_tg30_form_status.py` | TestSessionInfo | `test_empty_when_setting_off` | TC-FST-017 | INT-024 |
| 425 | `test_tg30_form_status.py` | TestSessionInfo | `test_empty_without_sla_group` | TC-FST-018 | INT-024 |
| 426 | `test_tg30_form_status.py` | TestFormStatusTour | `test_chip_on_partner_form` | TC-FST-019 | INT-024 |
| 427 | `test_tg30_form_status.py` | TestFormStatusTour | `test_no_chip_without_sla` | TC-FST-020 | INT-024 |
| 428 | `test_tg31_notes_i18n.py` | TestNotePages | `test_definition_note_has_nine_groups` | TC-NOT-001 | INT-029 |
| 429 | `test_tg31_notes_i18n.py` | TestNotePages | `test_definition_note_content` | TC-NOT-002 | FUNC-003, FUNC-067, INT-024, INT-029 |
| 430 | `test_tg31_notes_i18n.py` | TestNotePages | `test_task_note_has_four_groups_and_three_scenarios` | TC-NOT-003 | INT-029 |
| 431 | `test_tg31_notes_i18n.py` | TestNoStaleButtonNames | `test_no_old_button_names_in_user_strings` | TC-NOT-004 | INT-005, INT-020, INT-029 |
| 432 | `test_tg32_duration_live.py` | TestDurationLive | `test_running_adds_current_period` | TC-DUR-001 | INT-028 |
| 433 | `test_tg32_duration_live.py` | TestDurationLive | `test_paused_equals_stored` | TC-DUR-002 | INT-028 |
| 434 | `test_tg32_duration_live.py` | TestDurationLive | `test_calendar_counts_working_hours_only` | TC-DUR-003 | INT-028 |
| 435 | `test_tg32_duration_live.py` | TestDurationLive | `test_list_shows_live_and_hides_stored` | TC-DUR-004 | INT-028 |

## Phụ lục D — Test case không có hàm test trong `tests/`

Gồm ba loại: **Đã gỡ (D12)** (cơ chế thử lại; không còn hiệu lực, ID giữ nguyên để không đánh số lại); **Manual** (Inspection, Demonstration; thực hiện thủ công và ghi kết quả ở Test Summary Report); **Ngoài `tests/`** (lệnh cài/gỡ trong CI, benchmark `odoo shell`, lint, hoặc ca chưa tự động hóa như các ca `demo.ticket`, Docker và mixin `sla.mixin` TC-UIX-029, TC-UIX-031). Ca ngoài `tests/` vẫn là yêu cầu kiểm tra; việc chưa có hàm test là việc còn dở của `docs/TASKS.md`.

| Test case | Trạng thái | Requirement Ref | Mục tiêu |
|---|---|---|---|
| TC-ERR-010 | Manual (Inspection hoặc Demonstration) | REQ-OBS-003 | Kiểm tra mã nguồn: đường ghi event error và log chỉ dùng tên model, id và tên định nghĩa |
| TC-ERR-025 | Manual (Inspection hoặc Demonstration) | REQ-INT-022 | Trình diễn nhãn số event lỗi chưa xử lý trên menu SLA cho Manager và ẩn với người không thuộc nhóm SLA |
| TC-ERR-028 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-REL-001 AC2 | Đo thời gian chờ khóa của lần lưu record khác khi action nền đang chậm (p95 qua 20 lần ≤ 5 giây) |
| TC-ESC-016 | Đã gỡ (D12), không có test | REQ-FUNC-055 AC2 | Tính lại mốc đang chờ thử lại như mốc chưa xử lý khi resume |
| TC-ESC-020 | Đã gỡ (D12), không có test | REQ-FUNC-027 AC1 | Ghi escalate_retry nêu giờ thử kế tiếp 10:01 khi action lỗi lúc 10:00 |
| TC-ESC-021 | Đã gỡ (D12), không có test | REQ-FUNC-027 AC1 | Không thử lại sớm hơn giờ thử kế tiếp (10:00:59 < 10:01:00) |
| TC-ESC-022 | Đã gỡ (D12), không có test | REQ-FUNC-027 AC1 | Thử lại chạy khi now đúng bằng giờ thử kế tiếp 10:01:00 |
| TC-ESC-023 | Đã gỡ (D12), không có test | REQ-FUNC-027 AC1 | Lần thử lại chạy trong khoảng 10:01 đến 10:03 với tick cron lệch 30 giây |
| TC-ESC-025 | Đã gỡ (D12), không có test | REQ-FUNC-056 AC1 | Ghi escalate_retry rồi escalate khi action lỗi một lần rồi thành công |
| TC-ESC-026 | Đã gỡ (D12), không có test | REQ-FUNC-056 AC2 | Không chạy lại action sau khi thử lại đã thành công |
| TC-ESC-027 | Đã gỡ (D12), không có test | REQ-FUNC-057 AC1 | Ghi 2 escalate_retry rồi escalate_failed khi mẫu [1, 10] và action luôn lỗi |
| TC-ESC-028 | Đã gỡ (D12), không có test | REQ-FUNC-057 AC2 | Chỉ thử lại đúng 1 lần với mẫu một phần tử [5] |
| TC-ESC-029 | Đã gỡ (D12), không có test | REQ-FUNC-057 AC3 | Không ghi escalate_failed khi lần thử lại cuối cùng thành công |
| TC-ESC-030 | Đã gỡ (D12), không có test | REQ-FUNC-058 AC1 | Hủy lượt thử lại đang chờ khi task bị stop |
| TC-ESC-031 | Đã gỡ (D12), không có test | REQ-FUNC-058 AC2 | Hủy lượt thử lại đang chờ khi task bị cancel |
| TC-ESC-032 | Đã gỡ (D12), không có test | REQ-FUNC-058 AC3 | Hủy lượt thử lại đang chờ khi task chuyển paused |
| TC-ESC-033 | Đã gỡ (D12), không có test | REQ-FUNC-059 AC1 | Giữ nguyên giờ thử 10:01 của lượt chờ khi sửa mẫu sang [1, 30] |
| TC-ESC-034 | Đã gỡ (D12), không có test | REQ-FUNC-059 AC2 | Tính giờ thử kế tiếp 10:31 theo mẫu mới [1, 30] khi lần thử 10:01 lại lỗi |
| TC-ESC-035 | Đã gỡ (D12), không có test | REQ-FUNC-028 AC1 | Từ chối mẫu thử lại rỗng khi bật thử lại |
| TC-ESC-036 | Đã gỡ (D12), không có test | REQ-FUNC-028 AC1 | Từ chối mẫu thử lại chứa số 0 |
| TC-ESC-037 | Đã gỡ (D12), không có test | REQ-FUNC-028 AC1 | Từ chối mẫu thử lại có số âm |
| TC-ESC-038 | Đã gỡ (D12), không có test | REQ-FUNC-028 AC1 | Từ chối mẫu thử lại có số không nguyên |
| TC-ESC-039 | Đã gỡ (D12), không có test | REQ-FUNC-028 AC1 | Từ chối mẫu thử lại không phải danh sách ('abc') |
| TC-ESC-040 | Đã gỡ (D12), không có test | REQ-FUNC-028 AC1 | Từ chối mẫu thử lại 11 phần tử (vượt biên trên 10) |
| TC-ESC-041 | Đã gỡ (D12), không có test | REQ-FUNC-028 AC2 | Chấp nhận mẫu thử lại hợp lệ [1, 10, 20, 60] |
| TC-ESC-042 | Đã gỡ (D12), không có test | REQ-FUNC-028 AC2 | Chấp nhận mẫu thử lại 10 phần tử (biên trên) |
| TC-ESC-043 | Đã gỡ (D12), không có test | REQ-FUNC-028 | Không kiểm tra mẫu khi tắt thử lại (retry = false) |
| TC-ESC-052 | Đã gỡ (D12), không có test | REQ-INT-019 AC2 | Ghi escalate_retry thay cho escalate_failed ở lần lỗi quyền đầu tiên khi mốc bật thử lại |
| TC-ESC-060 | Đã gỡ (D12), không có test | REQ-FUNC-058 (mở rộng theo TA-08), REQ-FUNC-054 | Giữ lượt thử lại đang chờ và vẫn chạy khi cờ `cancel_retry_on_stop` = False (pause, stop, cancel, reset) |
| TC-EXT-003 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-INT-007 AC3 | Gỡ module mẫu đưa định nghĩa nguồn `team` về nguồn `none` không lỗi |
| TC-EXT-023 | Manual (Inspection hoặc Demonstration) | REQ-REUSE-001 AC2 | Rà soát MR đổi chữ ký điểm mở rộng có tuân thủ REQ-CM-001 |
| TC-INF-008 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-FUNC-002 AC3 (mở rộng) | Chấp nhận lưu định nghĩa trỏ tới model `demo.ticket` |
| TC-INF-023 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-INST-001 AC1 | Cài `dwo_sla_core` trên database có dữ liệu không lỗi và không làm đổi dữ liệu |
| TC-INF-024 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-INST-001 AC1 | Nâng cấp `dwo_sla_core` đã cài không lỗi và không làm đổi dữ liệu |
| TC-INF-025 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-INST-001 AC1 | Gỡ `dwo_sla_core` không lỗi và dữ liệu `res.partner`, `sh.helpdesk.ticket` nguyên vẹn |
| TC-INF-026 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-INST-001 AC1 (phần sau gỡ) | Sau khi gỡ, sửa record không phát sinh event hay task |
| TC-INF-028 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-INST-003 AC1 | Bảng `sh_helpdesk_ticket` không đổi cột sau khi cài module |
| TC-INF-030 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-INST-004 AC1 | Gỡ `dwo_sla_demo_ticket` xóa hết task của `demo.ticket` và không lỗi |
| TC-INF-031 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-INST-004 AC1 | Gỡ `dwo_sla_demo_ticket` xóa 4 định nghĩa mẫu |
| TC-INF-032 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-INST-004 AC1 (negative bổ sung) | Gỡ `dwo_sla_demo_ticket` không xóa task của `res.partner` |
| TC-INF-033 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-PORT-001 AC1 | Cài module trên image dựng từ Dockerfile của repo không cần thêm gói Python |
| TC-INF-035 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-INST-001 (mở rộng: gỡ module có model gắn SLA) | Gỡ module chứa model có định nghĩa SLA: CASCADE xóa định nghĩa, task, event, lượt thử lại và dấu mốc đã xử lý, không lỗi và `dwo_sla_core` vẫn hoạt động |
| TC-INS-003 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-BUILD-001 AC1 | Pylint đạt điểm không dưới 9 trên mọi file Python của module |
| TC-INS-006 | Manual (Inspection hoặc Demonstration) | REQ-MAINT-001 AC1 | Rà soát có comment lý do tại chỗ cài đặt cho mục: Hook trên ORM |
| TC-INS-007 | Manual (Inspection hoặc Demonstration) | REQ-MAINT-001 AC1 | Rà soát có comment lý do tại chỗ cài đặt cho mục: Cô lập lỗi engine |
| TC-INS-008 | Manual (Inspection hoặc Demonstration) | REQ-MAINT-001 AC1 | Rà soát có comment lý do tại chỗ cài đặt cho mục: Đánh giá lại |
| TC-INS-009 | Manual (Inspection hoặc Demonstration) | REQ-MAINT-001 AC1 | Rà soát có comment lý do tại chỗ cài đặt cho mục: Nhật ký sự kiện |
| TC-INS-010 | Manual (Inspection hoặc Demonstration) | REQ-MAINT-001 AC1 | Rà soát có comment lý do tại chỗ cài đặt cho mục: Field compute không lưu |
| TC-INS-011 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-MAINT-002 AC1 | Một lệnh trên database trống chạy toàn bộ test và báo kết quả đạt |
| TC-INS-013 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-MAINT-002 Statement | Suite end-to-end trên `demo.ticket` tồn tại và được chạy bởi lệnh test |
| TC-INS-014 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-MAINT-002 AC1 (đạt hoặc không đạt) | Lệnh test báo không đạt (mã thoát khác 0) khi một test cố ý thất bại |
| TC-INS-015 | Manual (Inspection hoặc Demonstration) | REQ-CM-001 AC1 | Rà soát MR gây phá vỡ có script nâng cấp và dòng Revision History |
| TC-INS-016 | Manual (Inspection hoặc Demonstration) | REQ-CM-001 AC1 (negative) | Rà soát MR gây phá vỡ thiếu script nâng cấp bị đánh dấu không đạt |
| TC-INS-017 | Manual (Inspection hoặc Demonstration) | REQ-CM-001 Statement (cấu trúc dữ liệu) | Rà soát MR đổi cấu trúc dữ liệu SLA (đổi cột/CHECK) được phân loại gây phá vỡ |
| TC-PRF-001 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-PERF-001 AC1 | Đo overhead ghi hàng loạt 1000 `res.partner` trước và sau khi cài module (10 lần lặp) |
| TC-PRF-002 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-PERF-001 AC1 (biến thể) | Đo overhead trên `res.partner` khi `demo.ticket` có 4 định nghĩa mẫu (10 lần lặp) |
| TC-SEC-014 | Đã gỡ (D12), không có test | REQ-SEC-004 (AC1 (nhánh retry)) | Ghi escalate_retry khi action vượt quyền U-CRON và mốc bật retry |
| TC-UIX-003 | Manual (Inspection hoặc Demonstration) | REQ-INT-001 (Statement) | Trình diễn bố cục form định nghĩa SLA |
| TC-UIX-006 | Manual (Inspection hoặc Demonstration) | REQ-INT-002 (AC1 (hiển thị)) | Trình diễn hiển thị help của start và pause trên giao diện |
| TC-UIX-007 | Manual (Inspection hoặc Demonstration) | REQ-INT-003 (AC1) | Trình diễn ghi chú lịch dự phòng khi nguồn lịch là record |
| TC-UIX-008 | Manual (Inspection hoặc Demonstration) | REQ-INT-003 (AC2) | Trình diễn ghi chú ẩn khi nguồn lịch là none hoặc definition |
| TC-UIX-012 | Manual (Inspection hoặc Demonstration) | REQ-INT-004 (AC1, AC2) | Trình diễn danh sách và form chi tiết task SLA ở chế độ chỉ đọc |
| TC-UIX-017 | Manual (Inspection hoặc Demonstration) | REQ-INT-006 (AC1, AC4 (hiển thị)) | Trình diễn action SLA trong menu Action của form partner |
| TC-UIX-028 | Manual (Inspection hoặc Demonstration) | REQ-INT-013 (AC2) | Trình diễn chế độ xem pivot và graph của task SLA |
| TC-UIX-029 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-INT-014 (AC1) | Đếm task của record và mở danh sách task qua nút |
| TC-UIX-030 | Manual (Inspection hoặc Demonstration) | REQ-INT-014 (AC1) | Trình diễn nút số task SLA trên form record |
| TC-UIX-031 | Ngoài `tests/` (CI, benchmark) hoặc chưa tự động hóa | REQ-INT-014 (AC2) | Ẩn nút số task SLA với người dùng không thuộc nhóm SLA |
