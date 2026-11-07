# Test Plan

## Cho `dwo_sla_core` (SLA generic cho Odoo 19) — phiên bản 1

Test Plan ID: TP-SLACORE-001
Version: 0.2
Status: Draft
Prepared by: hieudt
Date: 2026-10-12
Parent document: N/A — không có Test Strategy riêng cấp tổ chức

## Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-10-09 | 0.1 | hieudt | Khởi tạo từ SRS 0.2, TAD 0.1, Database Design 0.1 |
| 2026-10-12 | 0.2 | hieudt | Đối chiếu với code và test đã viết (FT-06 bỏ FUNC-044, INT-014 theo SRS mục 4): TI-01 đã có code; EC-03 và Smoke theo bộ Smoke của `060`; thêm nhóm FT-INS (Inspection) và INS-001 theo `web` (D1); ngưỡng PERF-001 đã chốt (O-01); số test case 437; thẻ test dùng `tg_xx`; cập nhật phiên bản tài liệu tham chiếu |

---

## 1. Test Plan Identifier

- **ID:** TP-SLACORE-001, version 0.2, trạng thái Draft.
- **Tài liệu test liên quan:** `050_Test-Design-Specification.md` (TDS-SLACORE-001), `060_Test-Case-Specification.md` (TCS-SLACORE-001).

## 2. Introduction

**Mục đích:** kế hoạch kiểm thử cho phiên bản 1 của module `dwo_sla_core` và module demo `dwo_sla_demo_ticket` (chỉ dùng để test).

**Phạm vi:** kiểm thử chức năng, hiệu năng, bảo mật, độ tin cậy, cài đặt và nâng cấp của module trên Odoo 19, ở mức tích hợp trong Odoo (xem 6.1). Không bao gồm SLO, dashboard SLO (`dwo_sla_analysis`).

**Đối tượng đọc:** QA, developer, người sở hữu sản phẩm.

**Tài liệu liên quan:** SRS (`010_Software-Requirements-Specification.md`, 0.4), TAD (`020_...`, 0.3), Database Design (`030_...`, 0.3), bản thiết kế gốc `.claude/plans/010_SLA.md`.

## 3. Test Items

| Item ID | Component | Version / Build | Source |
|---------|-----------|-----------------|--------|
| TI-01 | `dwo_sla_core` | Đã có code và bộ test tự động (`tests/`), xem `docs/TASKS.md` | `custom-addons/dwo_sla_core/` |
| TI-02 | `dwo_sla_demo_ticket` | TBD — dự kiến giai đoạn 6 | thư mục addons riêng, không nằm trong `addons_path` của production |
| TI-03 | Schema database của module | Theo `030_Database-Design.md` 0.3 | Sinh bởi ORM khi cài |
| TI-04 | Image nền | `odoo:19.0-20260421` | Dockerfile của repo |

Build, commit cụ thể được ghi vào bảng này trước mỗi chu kỳ test (Entry criteria EC-01).

## 4. Features to Be Tested

Mỗi Feature tương ứng một nhóm test (TG) trong SRS mục 4. Ma trận REQ-ID đầy đủ nằm ở SRS mục 4 và ở bảng truy vết của `050`/`060`.

| Feature ID | Feature | Nhóm test | REQ-ID chính | Priority | Test Level |
|-----------|---------|-----------|--------------|----------|------------|
| FT-01 | Gắn, kết thúc, điều kiện, kích hoạt đánh giá | TG-01 | REQ-FUNC-003, 004, 006, 007, 009, 015, 032 | High | Integration |
| FT-02 | Pause và resume, thời gian đã trôi | TG-02 | REQ-FUNC-011, 037, 043, 044, 048 | High | Integration |
| FT-03 | Vi phạm và quanh hạn | TG-03 | REQ-FUNC-009, 022, 046, REQ-INT-023 | High | Integration |
| FT-04 | Cancel và reset (kể cả reset theo field) | TG-04 | REQ-FUNC-008, 010, 012, 013, 050, 051 | High | Integration |
| FT-05 | Ba cấu hình dễ sai | TG-05 | REQ-FUNC-016 | High | Integration |
| FT-06 | Giờ làm việc | TG-06 | REQ-FUNC-018, 043 (FUNC-044 kiểm ở TG-02, TG-03) | High | Integration |
| FT-07 | Retroactive start | TG-07 | REQ-FUNC-017, 041 | Medium | Integration |
| FT-08 | Escalation, thử lại, xử lý nền | TG-08 | REQ-FUNC-023 đến 028, 038, 053 đến 059, REQ-INT-008, 019, REQ-REL-002 | High | Integration |
| FT-09 | Nhiều SLA song song | TG-09 | REQ-FUNC-014 | High | Integration |
| FT-10 | Tính generic | TG-10 | REQ-FUNC-001 | High | System |
| FT-11 | Đổi cấu hình khi đang chạy, archive | TG-11 | REQ-FUNC-021, 033, 052, 053, 060, 061 | High | Integration |
| FT-12 | Lỗi engine và đồng thời | TG-12 | REQ-FUNC-014, 030, 031, 040, REQ-REL-001, REQ-OBS-001 đến 003 | High | Integration |
| FT-13 | Field compute có lưu | TG-13 | REQ-FUNC-005, 042 | High | Integration |
| FT-14 | Hạ tầng: cài, nâng cấp, gỡ, dọn dẹp, tham số | TG-14 | REQ-FUNC-002, 034, 035, REQ-INST-001 đến 004, REQ-INT-010, REQ-PORT-001 | High | System |
| FT-15 | Nguồn lịch | TG-15 | REQ-FUNC-019, 020, 039, REQ-INT-009 | High | Integration |
| FT-16 | Phân quyền và đa công ty | TG-16 | REQ-SEC-001 đến 006 | High | Integration |
| FT-17 | Giao diện và báo cáo | TG-17 | REQ-INT-001 đến 006, 011 đến 014, 020 đến 023, REQ-FUNC-036, 062 | Medium | System + Demonstration |
| FT-18 | Hiệu năng | TG-18 | REQ-PERF-001 đến 003 | High | Performance |
| FT-19 | Điểm mở rộng | TG-19 | REQ-INT-007, 015 đến 018, REQ-REUSE-001 | Medium | Integration |
| FT-INS | Inspection, review code, hạ tầng ngoài test chạy | TC-INS-* | REQ-INST-002, REQ-MAINT-001, REQ-CM-001, REQ-BUILD-001 và các mục kiểm tra thủ công | Medium | Inspection |

**Yêu cầu kiểm chứng không bằng chạy test** (Inspection): REQ-INT-002 (một phần), REQ-INST-002, REQ-MAINT-001, REQ-CM-001, REQ-BUILD-001 (lint trong CI). Danh sách kiểm tra ở mục 9.

## 5. Features Not to Be Tested

| Feature | Lý do | Kế hoạch |
|---------|-------|----------|
| SLO, dashboard SLO, chiều phân tích theo model | Ngoài phạm vi phiên bản 1 (SRS 2.6) | Test Plan của `dwo_sla_analysis` |
| Hành vi ServiceNow thực tế (đối chiếu) | Không có quyền truy cập instance; là việc của spike giai đoạn 0 (A-03) | Ghi kết quả vào SRS khi có |
| Widget JS riêng cho mẫu thử lại | Không làm ở phiên bản 1 (kiểm tra bằng constraint phía server) | Nếu làm sau thì thêm test |
| Retroactive pause, relative duration, OLA, `overrides` | Ngoài phạm vi (SRS 1.2) | Không có |
| Penetration test, stress test vượt quy mô benchmark | Không có yêu cầu trong SRS | Đánh giá khi có yêu cầu |
| Test trình duyệt, đa thiết bị | Giao diện là view chuẩn của Odoo | Dựa vào framework Odoo |

## 6. Test Approach

### 6.1 Test Levels

| Level | Ai thực hiện | Scope |
|-------|--------------|-------|
| Unit | Dev | Hàm thuần (tính lịch, parse mẫu thử lại, kiểm tra domain); viết cùng code, không thuộc TCS này trừ khi nêu |
| Integration (mức chính) | Dev và QA | Test của Odoo (`TransactionCase`) trên database thật: hook, engine, cron, ràng buộc database. Phần lớn ca trong TCS ở mức này |
| System | QA | Luồng đầu cuối trên `demo.ticket`, cài và gỡ module, giao diện |
| Performance | QA | Benchmark hook và xử lý nền (TG-18) |
| UAT | Product Owner | Ngoài tài liệu này; demo giao diện giai đoạn 5 |

### 6.2 Test Types

- **Functional:** theo SRS, mỗi REQ có ít nhất một ca happy path và một ca negative.
- **Regression:** chạy toàn bộ bộ test tự động trên mỗi merge request.
- **Smoke:** cài module trên database trống và chạy bộ Smoke của `060` (TC-ATT-007, TC-ATT-015, TC-ATT-017, TC-ATT-019) trước mỗi chu kỳ.
- **Concurrency và lỗi:** hai giao dịch đồng thời, lỗi cố ý của engine và server action (TG-12).
- **Performance:** benchmark có số đo (TG-18).
- **Security:** quyền và đa công ty (TG-16).
- **Installation:** cài, nâng cấp, gỡ trên database có dữ liệu (TG-14).
- **Exploratory:** 10% thời gian của chu kỳ system test, ghi chú vào log test.

### 6.3 Test Techniques

Black-box: Equivalence Partitioning, Boundary Value Analysis (hạn chót, giờ làm việc, ngưỡng tham số), Decision Table (điều kiện attach, thứ tự ưu tiên, cấu hình dễ sai), State Transition (vòng đời task, retry), Error Guessing (lỗi cấu hình, đồng thời). Kỹ thuật chọn cho từng nhóm ghi ở `050`.

### 6.4 Automation Strategy

- **Công cụ:** framework test của Odoo 19 (`odoo.tests.common.TransactionCase`, `HttpCase` khi cần), chạy bằng `odoo --test-enable --test-tags`.
- **Thời điểm:** engine nhận `now` làm tham số nên test đặt thời điểm cụ thể mà không cần đóng băng đồng hồ; riêng xử lý nền, test gọi trực tiếp hàm xử lý với `now` truyền vào.
- **Gắn thẻ:** `@tagged('post_install', '-at_install', 'dwo_sla_core', 'tg_xx')`.
- **Tự động hóa:** toàn bộ TG-01 đến TG-16, TG-18, TG-19; TG-14 gồm cả các ca chạy bằng lệnh cài và gỡ trong CI; TG-17 tự động phần dữ liệu và bộ lọc, phần hiển thị (REQ-INT-002, 003 ngoài help text, 013) kiểm bằng Demonstration có biên bản; REQ-INT-014 kiểm bằng Test (TC-UIX-029, 031) và Demonstration cho một ca (TC-UIX-030).
- **Tỷ lệ mục tiêu:** ≥ 90% ca test tự động khi kết thúc giai đoạn 6.
- **Cố định:** không dùng `sleep` thật; thời gian xử lý nền và thử lại dùng `now` truyền vào.

## 7. Item Pass/Fail Criteria

### 7.1 Entry criteria

| ID | Tiêu chí |
|----|----------|
| EC-01 | Có build cụ thể (commit) của `dwo_sla_core` đã ghi vào mục 3 |
| EC-02 | Module cài thành công trên database trống `sla_test` bằng lệnh ở mục 11 (lệnh thoát với mã 0, log không có ERROR) |
| EC-03 | Smoke test (4 ca Smoke của `060`: TC-ATT-007, 015, 017, 019) đạt 100% |
| EC-04 | Lint pass: pylint ≥ 9 theo `.pylintrc` của repo trên các file đã đổi |
| EC-05 | SRS ở trạng thái đã review (không còn BLOCKER mở) và các giá trị O-01 đến O-05 đã chốt hoặc có giá trị tạm ghi trong test |

### 7.2 Per-Feature Criteria

| Feature | Pass Criteria |
|---------|---------------|
| FT-01 đến FT-13, FT-15, FT-16, FT-19 | 100% ca P1 và P2 đạt; ≥ 95% ca P3 và P4 đạt; 0 defect Critical hoặc High còn mở |
| FT-14 | 100% ca đạt (cài, nâng cấp, gỡ không có ngoại lệ); 0 defect Critical hoặc High còn mở |
| FT-17 | ≥ 95% ca tự động đạt; mọi mục Demonstration có biên bản xác nhận; 0 defect Critical hoặc High còn mở |
| FT-18 | REQ-PERF-001: trung vị thời gian sau cài ≤ 105% trước cài (ngưỡng đã chốt ở O-01); REQ-PERF-002: chênh số truy vấn giữa lô 100 và lô 10 ≤ 5; REQ-PERF-003: p95 độ trễ mốc ≤ 2 phút qua 20 chu kỳ |

### 7.3 Overall Release Criteria (Exit Criteria)

Phiên bản 1 được phép đi tiếp (UAT, production) khi:
- Tất cả FT-01 đến FT-19 đạt theo 7.2;
- Run rate ≥ 95% (số ca đã chạy chia tổng số ca đã lên kế hoạch), và 100% ca P1 đã chạy;
- 0 defect Critical, ≤ 2 defect High còn mở (kèm workaround đã duyệt), 0 defect High liên quan REQ-FUNC-014, REQ-FUNC-030, REQ-INST-001;
- Cài, nâng cấp, gỡ sạch trên database có dữ liệu đạt (REQ-INST-001);
- Benchmark TG-18 đạt;
- Ma trận truy vết SRS mục 4: mọi REQ-ID có trạng thái `Passed` hoặc `Waived` (có lý do);
- Người sở hữu sản phẩm ký nhận.

**Mức độ defect:** Critical (mất dữ liệu, chặn lưu record của model khác, task sai kết quả đo hàng loạt); High (một chức năng chính sai, không có workaround); Medium (sai ở ca biên hoặc có workaround); Low (cosmetic, văn bản).

## 8. Suspension & Resumption Criteria

### 8.1 Suspension

Dừng chu kỳ test nếu bất kỳ điều kiện nào xảy ra:
1. Cài module trên database trống thất bại ở hai lần build liên tiếp.
2. ≥ 30% ca đã chạy trong cùng một ngày thất bại.
3. Có defect Critical đang mở chặn ≥ 3 Feature không test được.
4. Môi trường test không khả dụng liên tục > 4 giờ trong giờ làm việc.
5. Dữ liệu hoặc database test bị hỏng ngoài ý muốn (không khôi phục được từ bản sao lưu fixture trong 1 giờ).

### 8.2 Resumption

Tiếp tục khi:
1. Developer xác nhận nguyên nhân gốc và build mới đạt smoke test (EC-03).
2. Với điều kiện 2: tỷ lệ đạt của chạy lại các ca đã thất bại ≥ 90%.
3. Với defect Critical: đã sửa, kiểm lại và regression nhóm liên quan đạt 100%.
4. Môi trường ổn định liên tục ≥ 1 giờ.
5. Người phụ trách QA (hoặc người thay thế được chỉ định) sẵn sàng.

## 9. Test Deliverables

**Trước khi test:**
- Test Plan này, `050_Test-Design-Specification.md`, `060_Test-Case-Specification.md`.
- Fixture và dữ liệu test (mục 11), code test trong `custom-addons/dwo_sla_core/tests/` (khi có code).
- Danh sách kiểm tra Inspection:
  - REQ-INST-002: file khai báo module chỉ phụ thuộc `base`, `resource` và `web` (Deviation D1 của REQ-INST-002).
  - REQ-MAINT-001: comment lý do tại chỗ cài đặt (5 mục ở SRS).
  - REQ-CM-001: merge request đổi chữ ký điểm mở rộng có script nâng cấp và dòng Revision History.
  - REQ-INT-002: help text ba cấu hình dễ sai.
  - REQ-SEC-004 (một phần): ghi chú quyền của user cron trên form escalation.

**Trong khi test:**
- Nhật ký chạy test của CI (mỗi merge request).
- Báo cáo defect (hệ thống theo dõi của dự án, nhãn `dwo_sla_core`).
- Biên bản Demonstration cho mục giao diện.

**Sau khi test:**
- Test Summary Report (TSR-SLACORE-001).
- Ma trận truy vết cập nhật trạng thái (SRS mục 4: Planned → Passed hoặc Failed hoặc Waived).
- Danh sách defect cuối kèm trạng thái.

## 10. Testing Tasks & Schedule

Thời lượng chưa ghi vì phụ thuộc kết quả spike giai đoạn 0 và nhân lực (cùng nguyên tắc với kế hoạch triển khai R1). Phụ thuộc theo giai đoạn của R1:

| Task | Owner | Phụ thuộc | Thời gian |
|------|-------|-----------|-----------|
| Review SRS, TAD, DB, Test docs; chốt O-01 đến O-05 | hieudt | SRS 0.2 | TBD |
| Viết code test (khung, fixture) song song với giai đoạn 1 | Dev (TBD) | Giai đoạn 1 xong | TBD |
| Test TG-01, TG-04, TG-05, TG-09, TG-10, TG-12, TG-13 | Dev và QA (TBD) | Giai đoạn 2 xong | TBD |
| Test TG-02, TG-03, TG-06, TG-07, TG-11, TG-15 | Dev và QA (TBD) | Giai đoạn 3 xong | TBD |
| Test TG-08, TG-19 và các ca xử lý nền của TG-12 | Dev và QA (TBD) | Giai đoạn 4 xong | TBD |
| Test TG-16, TG-17; demo giao diện | QA (TBD) | Giai đoạn 5 xong | TBD |
| Test TG-14, TG-18; chạy CI từ database trống | QA và DevOps (TBD) | Giai đoạn 6 xong | TBD |
| Regression toàn bộ, Test Summary Report | QA (TBD) | Tất cả | TBD |

## 11. Environmental Needs

### 11.1 Test Environment

- **Môi trường:** container Odoo 19 theo Dockerfile của repo (image nền `odoo:19.0-20260421`), PostgreSQL theo image; database test `sla_test` tạo mới cho mỗi lần chạy; không dùng dữ liệu production.
- **Lệnh chạy** (từ thư mục chứa `docker-compose.yml`):

```bash
docker compose exec -u 0 odoo odoo -d sla_test -i dwo_sla_core,dwo_sla_demo_ticket \
  --test-enable --test-tags /dwo_sla_core,/dwo_sla_demo_ticket --stop-after-init
# một nhóm: --test-tags dwo_sla_core:tg_08 (gắn thẻ tg_xx trên lớp test)
```

- **Môi trường benchmark (TG-18):** cùng cấu hình container, 1 worker HTTP và 1 worker cron, cấu hình CPU và RAM ghi vào biên bản chạy; không chạy song song tác vụ khác. Cấu hình cụ thể TBD (chốt cùng O-01).

### 11.2 Test Data và Fixture dùng chung

Các ca test trong `060` tham chiếu fixture bằng ID để giữ tính độc lập (mỗi ca tự dựng fixture trong Preconditions). Tổng số: 437 test case, 126 test condition, phủ 106 REQ-ID (xem `050` và `060`).

| Fixture | Mô tả |
|---------|-------|
| FX-CAL-VN | Calendar `fully_fixed`, múi giờ `Asia/Ho_Chi_Minh`, T2–T6 08:00–17:00 (nghỉ trưa 12:00–13:00 không cấu hình, tức 9 giờ làm mỗi ngày) |
| FX-CAL-FLEX | Calendar loại `flexible` (dùng cho ca bị từ chối) |
| FX-CAL-EMPTY | Calendar không có dòng giờ làm nào |
| FX-USERS | `U-MGR` (thuộc `group_sla_manager`), `U-USR` (thuộc `group_sla_user`), `U-BIZ` (chỉ quyền sửa `res.partner` và `demo.ticket`), `U-NONE` (không có quyền SLA, không sửa partner) |
| FX-CO | Hai công ty `CO-A`, `CO-B`; `U-CRON` được cấp cả hai (và biến thể chỉ có `CO-A`) |
| FX-PARTNER-MARK | Quy ước dùng field `ref` (Char) của `res.partner` làm "trạng thái" trong test generic: `NEW`, `WORK`, `HOLD`, `DONE`, `CANCEL`, `RESET` |
| FX-DEF-STD | Định nghĩa chuẩn trên `res.partner`: start `[('ref','in',['NEW','WORK','HOLD'])]`, pause `[('ref','=','HOLD')]`, resume `[('ref','=','WORK')]`, stop `[('ref','=','DONE')]`, cancel `[('ref','=','CANCEL')]`, reset rỗng; mục tiêu 4 giờ; nguồn lịch `none` (24x7); chế độ cancel `start_unmatched`, chế độ resume `condition`; không retroactive; không escalation |
| FX-DEF-VN | Như FX-DEF-STD nhưng nguồn lịch `definition` = FX-CAL-VN |
| FX-ESC-STD | Hai mốc 75% và 100% trên FX-DEF-STD, server action "ghi ghi chú vào chatter" của partner |
| FX-DEMO | Dữ liệu của module demo: model `demo.ticket` và bốn định nghĩa mẫu (P1 phản hồi, P1 xử lý, P2 phản hồi, P2 xử lý) cấu hình theo SRS và bản thiết kế |
| FX-CAL-VN-PM | Calendar `fully_fixed`, `Asia/Ho_Chi_Minh`, T2–T6 13:00–18:00 (để phân biệt với FX-CAL-VN khi đổi lịch) |
| FX-CAL-PATH | Field Many2one `x_calendar_id` trên `res.partner` (loại manual) làm đích cho đường dẫn lịch `parent_id.x_calendar_id` |
| FX-EXT | Module mẫu chỉ dùng trong test (`dwo_sla_test_ext`) override các điểm mở rộng |
| FX-CMP | Model kiểm thử `x.sla.cmp.ticket` có field compute có lưu |
| FX-RETRO-DT | Field Datetime ghi được làm mốc retroactive (`res.partner` không có field phù hợp) |
| FX-USERS (bổ sung) | `U-CRON` (nhóm `group_sla_user`, không quyền quản trị người dùng), `U-BIZ-S` (`U-BIZ` cộng `group_sla_user`) |
| FX-T0 | Thời điểm gốc cố định `2026-03-02 09:00` giờ `Asia/Ho_Chi_Minh` (thứ Hai; 02:00 UTC) cho các ca có `now` truyền vào |

**Dữ liệu cho benchmark:** 1000 `res.partner` tạo bằng script, không có định nghĩa cho `res.partner`; 100000 task `in_progress` tạo bằng SQL cho TG-18.

### 11.3 Tools

- Test: framework test của Odoo 19; pylint theo `.pylintrc`; eslint và prettier khi có JS.
- Benchmark: script Python gọi qua `odoo shell` hoặc test riêng, lưu số liệu dạng bảng vào biên bản.
- Theo dõi defect: hệ thống theo dõi công việc của dự án (TBD: tên công cụ).

### 11.4 Access

QA cần quyền: repo (đọc, tạo nhánh test), môi trường container test, quyền chạy `docker compose exec`. Người cấp: DevOps (TBD).

## 12. Roles & Responsibilities

| Role | Người | Trách nhiệm |
|------|-------|-------------|
| Chủ sở hữu tài liệu, QA Lead tạm thời | hieudt | Soạn và duy trì tài liệu test, điều phối, ký nhận Exit criteria cùng người sở hữu sản phẩm |
| Developer | TBD (chưa phân công) | Viết code test mức integration, sửa defect |
| QA Engineer | TBD (chưa phân công) | Chạy system test, Demonstration, benchmark, báo cáo defect |
| DevOps | TBD (chưa phân công) | Duy trì môi trường test và CI |
| Product Owner | TBD (chưa phân công) | Chốt O-01, duyệt waiver, UAT |

**Escalation:** QA → Developer → hieudt → Product Owner. **Triage defect:** theo từng chu kỳ test, QA và Developer.

## 13. Risks & Contingencies

Rủi ro của kế hoạch test (không phải rủi ro sản phẩm, xem TAD mục 11).

| Risk ID | Risk | Probability | Impact | Contingency | Owner |
|---------|------|-------------|--------|-------------|-------|
| TR-01 | Spike giai đoạn 0 làm đổi hành vi (hook `_compute_field_value`, `plan_hours`, ServiceNow) kéo theo sửa nhiều ca | Medium | High | Chia ca theo nhóm TG độc lập; giá trị mong đợi của TG-06 ghi riêng để sửa nhanh | hieudt |
| TR-02 | Ngưỡng hiệu năng O-01 chưa chốt nên TG-18 không có tiêu chí | Medium | Medium | Dùng 5% làm giá trị tạm; ghi rõ trong biên bản, chốt trước giai đoạn 6 | Product Owner |
| TR-03 | Test đồng thời và nền khó lặp lại (flaky) | Medium | High | Mô phỏng bằng hai kết nối riêng và điều khiển thứ tự, không dựa vào thời gian thật; mỗi ca đồng thời chạy 20 lần trong CI định kỳ | Dev |
| TR-04 | Chưa phân công người (Developer, QA, DevOps) | High | High | hieudt nắm vai trò tạm; chốt phân công trước giai đoạn 2 | hieudt |
| TR-05 | Số ca lớn (trên 200) làm chu kỳ dài | Medium | Medium | Ưu tiên P1 và P2 trước; chạy theo nhóm TG song song trong CI | QA |
| TR-06 | Môi trường benchmark không ổn định, số đo nhiễu | Medium | Medium | Lặp 10 lần, lấy trung vị; ghi cấu hình máy; chạy trên máy cố định | DevOps |
| TR-07 | SRS còn mục chưa tách hoặc chưa chốt (REQ-FUNC-022, REQ-PERF-003 gộp nhiều việc) | Medium | Medium | Ca test tách theo từng hành vi; cập nhật khi SRS tách | hieudt |
