# Test Design Specification

## Cho `dwo_sla_core` (SLA generic cho Odoo 19) — phiên bản 1

TDS ID: TDS-SLACORE-001
Version: 0.3
Status: Draft
Prepared by: hieudt
Date: 2026-11-12
Parent Test Plan: TP-SLACORE-001 (`040_Test-Plan.md`)

> **Phạm vi 19.0.1.1.0 (2026-11-12):** bản 0.3 bổ sung mục 7: Feature FT-20 đến FT-31 (nhóm TG-25 đến TG-32 của đợt 1.1.0 và TG-21 đến TG-24 của các bổ sung trước đó), cùng test condition mới của FT-03, FT-08, FT-12, FT-13, FT-14, FT-16 và FT-18 cho các test chưa có coverage item. Các test condition và coverage item cũ về cơ chế thử lại (`retry`, D12) và về hành vi `[]` khớp mọi record đã được ghi chú hoặc sửa tại chỗ (mục 4–5 của FT-01, FT-04, FT-08). Tên field dùng theo code: `duration`, `target_duration`, `schedule_source`, `schedule_id`, `start_time`, `end_time`, `planned_end_time`, `business_duration`, `business_percent_used`.

## Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-10-09 | 0.1 | hieudt | Khởi tạo từ SRS 0.2 và Test Plan 0.1: 126 test condition, 431 coverage item |
| 2026-10-12 | 0.2 | hieudt | Đối chiếu với code, SRS 0.4 và Test Plan 0.2: đủ 437 coverage item (thêm CI cho TC-SEC-024, TG-11 và ca cờ `cancel_retry_on_stop` của REQ-FUNC-058); bỏ dòng và heading `# TDS-SLACORE-001 — Phần A3` lạc do ghép file; cập nhật phiên bản tài liệu tham chiếu |
| 2026-11-12 | 0.3 | hieudt | Đợt 1.1.0: thêm mục 7 (FT-20 đến FT-31, 88 test condition mới, 151 coverage item mới cho 151 test case mới), đổi tên field theo code, sửa test condition về `[]` (chưa cấu hình, không còn khớp mọi record: TCOND-01-01, TCOND-04-06), đánh dấu test condition về thử lại là đã gỡ (D12) |

---

## 1. TDS Identifier & References

- **TDS ID:** TDS-SLACORE-001, version 0.3, trạng thái Draft (theo ISO/IEC/IEEE 29119-3:2021, mục Test Design Specification).
- **Test Plan cha:** TP-SLACORE-001 (`040_Test-Plan.md`): các FT-01 đến FT-31 dưới đây là Feature của Test Plan (FT-20 đến FT-27 theo Test Plan 0.3; FT-28 đến FT-31 thêm ở bản này cho TG-21 đến TG-24).
- **SRS:** `010_Software-Requirements-Specification.md` 0.7: mọi REQ-ID `active` đều có ít nhất một test condition (bảng ở mục 6 và mục 7.14); REQ-ID đã gỡ (FUNC-027, 028, 056 đến 059) không còn test condition đang hiệu lực.
- **Tài liệu kế tiếp:** `060_Test-Case-Specification.md` (TCS-SLACORE-001): mỗi coverage item sinh một test case.
- **Phạm vi:** FT-01 đến FT-31 và nhóm Inspection (FT-INS, các yêu cầu BUILD, MAINT, CM, INST-002 kiểm bằng danh sách kiểm tra).
- **Đồng bộ với code:** 435 hàm `def test_` trong `tests/` (3 hàm hiệu năng chạy khi đặt `SLA_PERF=1`); bảng ánh xạ hàm test sang test case ở Phụ lục C của `060`.
- **Quy ước ID:** `TCOND-<TG>-<NN>` (ví dụ `TCOND-08-03`); `CI-<n>` đánh số trong từng test condition; nhóm Inspection dùng `TCOND-INS-<NN>`.

## 2. Features to Be Tested

| Feature ID | Feature | Nhóm test | Số test condition |
|-----------|---------|-----------|-------------------|
| FT-01 | Gắn, kết thúc, điều kiện, kích hoạt đánh giá | TG-01 | 8 |
| FT-02 | Pause và resume | TG-02 | 5 |
| FT-03 | Vi phạm và quanh hạn | TG-03 | 10 |
| FT-04 | Cancel và reset (kể cả reset theo field) | TG-04 | 6 |
| FT-05 | Ba cấu hình dễ sai | TG-05 | 3 |
| FT-06 | Giờ làm việc | TG-06 | 6 |
| FT-07 | Retroactive start | TG-07 | 2 |
| FT-08 | Escalation (email và server action), xử lý nền (phần thử lại đã gỡ, D12) | TG-08 | 23 |
| FT-09 | Nhiều SLA song song | TG-09 | 2 |
| FT-10 | Tính generic | TG-10 | 3 |
| FT-11 | Đổi cấu hình khi đang chạy và archive | TG-11 | 7 |
| FT-12 | Lỗi engine và đồng thời | TG-12 | 10 |
| FT-13 | Field compute có lưu | TG-13 | 4 |
| FT-14 | Hạ tầng: cài, nâng cấp, gỡ, dọn dẹp, tham số | TG-14 | 12 |
| FT-15 | Nguồn lịch | TG-15 | 4 |
| FT-16 | Phân quyền và đa công ty | TG-16 | 7 |
| FT-17 | Giao diện và báo cáo | TG-17 | 13 |
| FT-18 | Hiệu năng | TG-18 | 5 |
| FT-19 | Điểm mở rộng | TG-19 | 6 |
| FT-INS | Inspection và kiểm tra CI (BUILD, MAINT, CM, INST-002) | INS | 5 |
| FT-20 | Bật/tắt định nghĩa, `[]` là chưa cấu hình, timezone bắt buộc | TG-25 | 12 |
| FT-21 | Giao diện định nghĩa và task (due soon theo định nghĩa, khóa model, audit, nút Running Tasks, list, Open Source Record) | TG-26 | 13 |
| FT-22 | Re-check Conditions giới hạn một định nghĩa | TG-27 | 5 |
| FT-23 | Apply Current Settings ghi event và báo kết quả | TG-28 | 6 |
| FT-24 | Apply to Existing Records (wizard, job, cron, hủy, dọn, backfill) | TG-29 | 8 |
| FT-25 | Chip trạng thái trên form record gốc | TG-30 | 8 |
| FT-26 | Tab Note, chuỗi không lỗi thời | TG-31 | 3 |
| FT-27 | Duration (live) và Business Duration (live) | TG-32 | 4 |
| FT-28 | Field phân loại của định nghĩa (type, vendor, service commitment, target) | TG-21 | 5 |
| FT-29 | Retroactive pause | TG-22 | 4 |
| FT-30 | Timezone override của lịch (bản sao calendar) | TG-23 | 3 |
| FT-31 | Hạn chót ban đầu và thời lượng giờ đồng hồ | TG-24 | 2 |

Chi tiết REQ-ID của từng Feature nằm ở bảng Traceability của từng nhóm (mục 4 và 5) và bảng tổng hợp (mục 6).

## 3. Test Design Approach

Kỹ thuật chọn cho từng Feature và lý do:

**FT-01 / TG-01 — Gắn, kết thúc, điều kiện, kích hoạt đánh giá.** Decision Table (điều kiện attach), State Transition (không gắn lại, stop), EP (domain, kích hoạt). Attach là tổ hợp bốn điều kiện start/stop/cancel/pause nên dùng bảng quyết định; trạng thái task quyết định có gắn lại hay không nên dùng chuyển trạng thái; domain và field liên quan chia theo lớp tương đương.

**FT-02 / TG-02 — Pause và resume.** State Transition (vòng đời `in_progress` ↔ `paused`), Decision Table (chế độ resume × trạng thái pause/resume), EP (cờ vi phạm bật/tắt khi xếp lại hạn). Pause/resume là chuyển trạng thái có điều kiện; chế độ resume tạo bảng quyết định nhỏ.

**FT-03 / TG-03 — Vi phạm và quanh hạn.** BVA (mốc `planned_end_time`, phần trăm đã dùng), Decision Table (kết quả stop theo trạng thái × cờ vi phạm), EP (nơi phát hiện vi phạm), Error Guessing (escalate lỗi). Vi phạm xảy ra tại ngưỡng thời gian cụ thể nên dùng BVA; kết quả stop phụ thuộc tổ hợp nên dùng bảng quyết định.

**FT-04 / TG-04 — Cancel và reset (kể cả reset theo field).** Decision Table + State Transition — Thứ tự ưu tiên stop > cancel/start_unmatched > reset > pause > resume là một bảng quyết định nhiều điều kiện; vòng đời task (`in_progress`, `paused` sang `cancelled`, `achieved`, `breached`, task mới) là chuyển trạng thái. Reset theo field là tổ hợp (điều kiện reset khớp) x (field đổi giá trị), nên dùng bảng quyết định và Error Guessing cho các trường hợp không được kích hoạt.

**FT-05 / TG-05 — Ba cấu hình dễ sai.** Decision Table + Error Guessing — Ba cấu hình sai thường gặp (start ⊂ stop, pause ⊂ start, start và pause loại trừ) kết hợp với chế độ cancel cho kết quả khác nhau; liệt kê từng tổ hợp thành bảng quyết định, các ca này là lỗi người cấu hình hay mắc nên chọn theo Error Guessing.

**FT-06 / TG-06 — Giờ làm việc.** BVA kết hợp EP. Hạn chót và thời gian đã trôi có nhiều điểm biên theo lịch (mục tiêu 0, mốc đúng giờ đóng cửa, qua cuối tuần, global leave, múi giờ); EP dùng cho các lớp lịch (có lịch, không lịch, lịch không xếp được hạn).

**FT-07 / TG-07 — Retroactive start.** BVA + EP — Quyết định breach ngay lúc attach phụ thuộc khoảng cách giữa mốc và now so với mục tiêu (BVA quanh đúng 4 giờ); các lớp field mốc (trống, có giá trị) và kiểu field cấu hình hợp lệ hay không là EP.

**FT-08 / TG-08 — Escalation, thử lại, xử lý nền.** **EP + BVA + State Transition + Decision Table + Error Guessing** — EP/BVA cho phần trăm mốc, mẫu thử lại, kích thước lô và thời điểm đến hạn; State Transition cho vòng đời mốc (chưa xử lý → chờ thử lại → đã xử lý) và cho stage task; Decision Table cho stage task × có bắn hay không; Error Guessing cho đồng thời, ngắt giữa chừng, lỗi quyền công ty.

**FT-09 / TG-09 — Nhiều SLA song song.** EP + Error Guessing — Phân lớp theo định nghĩa (khác nhau) và record (khác nhau) cho tính độc lập; tính duy nhất dưới giao dịch đồng thời là lỗi dễ sót nên dùng Error Guessing với hai cursor điều khiển thứ tự.

**FT-10 / TG-10 — Tính generic.** EP — cùng một cấu hình định nghĩa phải áp dụng được cho các lớp model khác nhau (model của base, model demo); lớp dữ liệu không hợp lệ (thiếu model, thời lượng âm) tách riêng. BVA cho thời lượng mục tiêu tại 0.

**FT-11 / TG-11 — Đổi cấu hình khi đang chạy và archive.** State Transition kết hợp Decision Table. Archive định nghĩa và stage của task tạo ra các chuyển trạng thái (định nghĩa active/archive; task in_progress/paused/kết thúc) với hành vi khác nhau; Decision Table cho tương quan giữa thay đổi cấu hình và task đã có hoặc attach mới.

**FT-12 / TG-12 — Lỗi engine và đồng thời.** **Error Guessing + EP + State Transition** — Error Guessing cho các nguồn lỗi engine (field bị gỡ, lịch rỗng, lỗi một record trong lô, vi phạm duy nhất khi đồng thời, xung đột tuần tự hóa); EP chia lớp theo đường kích hoạt (create/write) và theo người dùng (Manager, SLA User, không có quyền SLA); State Transition cho trạng thái event `error` (chưa xử lý ⇄ đã xử lý).

**FT-13 / TG-13 — Field compute có lưu.** **EP + Decision Table + Error Guessing** — EP chia lớp theo loại field điều kiện (compute có lưu, compute không lưu, quan hệ xa) và theo việc kết quả điều kiện có đổi hay không; Decision Table cho bảng ưu tiên khi đánh giá lại thủ công; Error Guessing cho nhiều lần ghi trong một giao dịch và recompute qua quan hệ con.

**FT-14 / TG-14 — Hạ tầng: cài, nâng cấp, gỡ, dọn dẹp, tham số.** EP — các lớp model (hợp lệ, transient, abstract, `_auto=False`, tiền tố `sla.`/`ir.`/`mail.`); BVA — ngưỡng ngày lưu nhật ký và tham số 0/âm; Error Guessing — cài/gỡ trên database có dữ liệu thật, task mồ côi lẫn task còn record.

**FT-15 / TG-15 — Nguồn lịch.** Decision Table kết hợp EP. Kết quả lịch của task là hàm của nguồn lịch (`none`/`definition`/`record`), tính hợp lệ của đường dẫn, tính dùng được của calendar và của lịch công ty; mỗi tổ hợp có ý nghĩa là một quy tắc. EP phân lớp calendar (fully_fixed có giờ, flexible, không giờ làm).

**FT-16 / TG-16 — Phân quyền và đa công ty.** Decision Table + Error Guessing — quyền và cô lập công ty là tổ hợp (vai trò, thao tác, công ty) nên dùng bảng quyết định; các lỗi quyền gián tiếp (server action, đọc qua record liên kết) khó đoán nên dùng Error Guessing.

**FT-17 / TG-17 — Giao diện và báo cáo.** Equivalence Partitioning + Boundary Value Analysis + Decision Table — bộ lọc và báo cáo chia lớp theo stage và dấu vi phạm, biên theo tham số X và kỳ end_time; điều kiện hiển thị theo nguồn lịch và quyền dùng bảng quyết định; phần hiển thị trực quan dùng Demonstration/Inspection dạng checklist.

**FT-18 / TG-18 — Hiệu năng.** BVA/EP trên kích thước lô (10 vs 100) và quy mô dữ liệu (1000 vs 100000 task); đo thống kê (trung vị, p95) với số lần lặp cố định. Không phải kiểm tra chức năng.

**FT-19 / TG-19 — Điểm mở rộng.** Error Guessing + EP — mỗi điểm mở rộng có lớp 'có module mẫu override' và 'không có module mẫu (mặc định)'; lớp đầu ra không hợp lệ (âm, flexible) tách riêng; Decision Table cho nhánh hook.

**FT-INS / INS — Inspection và kiểm tra CI (BUILD, MAINT, CM, INST-002).** Inspection (rà soát có checklist) và kiểm tra tự động trong CI; mỗi mục AC tương ứng một mục checklist nhị phân. Không dùng kỹ thuật thiết kế dữ liệu test.

**FT-20 / TG-25 — Bật/tắt, `[]` là chưa cấu hình, timezone bắt buộc.** State Transition (định nghĩa tắt, bật, tắt còn task đang chạy), Decision Table (nguồn lịch × tz điền sẵn, onchange bản ghi mới và đã lưu), EP (domain `[]` so với domain luôn đúng). Đợt 1.1.0 đổi nghĩa của `[]` và thêm trạng thái tắt nên cần phủ chuyển trạng thái và từng lớp domain.

**FT-21 / TG-26 — Giao diện định nghĩa và task.** EP + BVA (ngưỡng Sắp đến hạn theo định nghĩa, giá trị âm), Decision Table (khóa model_id theo việc đã có task, toán tử tìm kiếm), kiểm tra arch view (Inspection tự động) và một tour trình duyệt cho hộp xác nhận khi lưu.

**FT-22 / TG-27 — Re-check Conditions.** Decision Table (định nghĩa A, B, C × task đã có hay chưa × quyền), EP (task đã đóng so với đang chạy). Điểm cần phòng là nút chạm sang định nghĩa khác của cùng record.

**FT-23 / TG-28 — Apply Current Settings.** EP theo stage của task (đang chạy, đã vi phạm, paused, đã đóng) và theo việc có gì đổi hay không; kiểm event `recalculate` và thông báo "N updated, M skipped".

**FT-24 / TG-29 — Apply to Existing Records.** State Transition (job `queued`, `running`, `done`, `cancelled`, `failed`), BVA (kích thước lô, job chồng nhau), Decision Table (domain lọc × điều kiện start × trạng thái định nghĩa × quyền), Error Guessing (lô lỗi, ngắt giữa chừng, backfill escalation đã vượt).

**FT-25 / TG-30 — Chip trạng thái.** State Transition và Decision Table cho hàm tóm tắt (stage × cờ vi phạm × ngưỡng sắp đến hạn × số task), BVA cho `percent` ≤ 100, EP cho quyền và cờ Settings, hai tour trình duyệt (có chip, không chip).

**FT-26 / TG-31 — Tab Note.** Inspection tự động trên arch view và trên chuỗi hiển thị (số nhóm, cụm từ bắt buộc, không còn tên nút cũ).

**FT-27 / TG-32 — Duration (live).** EP theo stage (đang chạy, paused) và theo lịch (24x7, có lịch), kiểm cột trên list.

**FT-28 / TG-21 — Field phân loại.** EP theo từng field (giá trị mặc định, giá trị chọn) và một ca hồi quy xác nhận không đổi hành vi engine.

**FT-29 / TG-22 — Retroactive pause.** Decision Table (model có tracking × field có tracking × cờ bật), BVA (khoảng pause bắt đầu đúng mốc), dựng lịch sử bằng `mail.tracking.value` trực tiếp để điều khiển thời điểm.

**FT-30 / TG-23 — Timezone override.** EP (tz trùng tz lịch, tz khác), kiểm tính duy nhất của bản sao và bất biến của lịch gốc.

**FT-31 / TG-24 — Hạn chót ban đầu và thời lượng giờ đồng hồ.** State Transition (pause, resume không đổi `original_breach_time`), EP (24x7, có lịch qua cuối tuần).

## 4–5. Test Conditions và Coverage Items

Mỗi test condition ghi Feature, REQ-ID, kỹ thuật, mô tả điều kiện (không có bước thực thi) và bảng coverage item. Mỗi nhóm kết thúc bằng bảng Traceability riêng của nhóm.

### FT-01 / TG-01 — Gắn, kết thúc, điều kiện, kích hoạt đánh giá

**Technique:** Decision Table (điều kiện attach), State Transition (không gắn lại, stop), EP (domain, kích hoạt). Attach là tổ hợp bốn điều kiện start/stop/cancel/pause nên dùng bảng quyết định; trạng thái task quyết định có gắn lại hay không nên dùng chuyển trạng thái; domain và field liên quan chia theo lớp tương đương.

#### TCOND-01-01 — Điều kiện rỗng và domain `[]`

**Feature:** FT-01 | **REQ-ID:** REQ-FUNC-003 | **Technique:** EP

**Mô tả điều kiện:** Từ 19.0.1.1.0, điều kiện rỗng và domain `[]` đều là chưa cấu hình và không bao giờ khớp; muốn khớp mọi record phải dùng domain luôn đúng `[('id', '!=', 0)]` (REQ-FUNC-003). Hai lớp tương đương phân biệt "chưa cấu hình" với "khớp tất cả"; phần phủ `[]` nằm ở TCOND-20-06.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Lớp: stop rỗng (chưa cấu hình) | Stop không khớp với record bất kỳ (kể cả record có giá trị trùng giá trị stop thông thường) |
| CI-2 | Lớp: start = `[('id', '!=', 0)]` (domain luôn đúng) | Start khớp mọi record, bất kể giá trị field |

#### TCOND-01-02 — Từ chối domain không hợp lệ khi lưu

**Feature:** FT-01 | **REQ-ID:** REQ-FUNC-003 | **Technique:** EP

**Mô tả điều kiện:** Khi lưu định nghĩa, domain phải hợp lệ với model và chỉ chứa giá trị literal. Lớp không hợp lệ: field không tồn tại; lời gọi hàm; biến `uid`. Lớp hợp lệ: literal thuần (kể cả ngày giờ literal).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Lớp không hợp lệ: field không tồn tại | Lưu bị từ chối, thông báo nêu tên field |
| CI-2 | Lớp không hợp lệ: lời gọi hàm `context_today()` | Lưu bị từ chối, thông báo nêu giới hạn literal |
| CI-3 | Lớp không hợp lệ: biến `uid` | Lưu bị từ chối, thông báo nêu giới hạn literal |
| CI-4 | Lớp hợp lệ: domain literal (gồm ngày giờ literal) | Lưu thành công, giá trị domain được giữ nguyên |

#### TCOND-01-03 — Quy tắc attach

**Feature:** FT-01 | **REQ-ID:** REQ-FUNC-006 | **Technique:** Decision Table

**Mô tả điều kiện:** Gắn SLA nếu và chỉ nếu start khớp, stop không khớp, cancel không khớp. Bảng quyết định (Y = khớp):

| Rule | start | stop | cancel | pause | Kết quả |
|---|---|---|---|---|---|
| R1 | Y | N | N | N | 1 task `in_progress` + 1 event `attach` |
| R2 | Y | N | N | Y | task `paused` |
| R3 | Y | Y | - | - | không tạo task |
| R4 | Y | N | Y | - | không tạo task |
| R5 | N | - | - | - | không tạo task |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | R1 | Đúng 1 task `in_progress`, đúng 1 event `attach`, hạn tính từ mốc bắt đầu |
| CI-2 | R2 | Task `paused` ngay lúc attach |
| CI-3 | R3 (negative) | Không có task, không có event |
| CI-4 | R4 (negative) | Không có task, không có event |
| CI-5 | R5 (negative) | Không có task |

#### TCOND-01-04 — Không gắn lại sau khi đã kết thúc

**Feature:** FT-01 | **REQ-ID:** REQ-FUNC-007 | **Technique:** State Transition

**Mô tả điều kiện:** Chuyển trạng thái theo task gần nhất của (định nghĩa, record) khi start khớp lại:

| Task gần nhất | Sự kiện | Kết quả |
|---|---|---|
| `achieved` | sửa record, start khớp | giữ nguyên, không task mới |
| `breached` | sửa record, start khớp | giữ nguyên, không task mới |
| `achieved` | reset và start cùng khớp | giữ nguyên, không reset, không task mới |
| `cancelled` | start khớp, stop và cancel không khớp | tạo task mới `in_progress` |
| `cancelled` | start khớp, stop khớp | không tạo task mới |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | achieved + start khớp lại | Không tạo task mới, task cũ `achieved` |
| CI-2 | breached + start khớp lại | Không tạo task mới, task cũ `breached` |
| CI-3 | achieved + reset và start cùng khớp | Task vẫn `achieved`, không task mới, không event `reset` |
| CI-4 | cancelled + start khớp lại | Tạo task mới `in_progress`, task cũ vẫn `cancelled` |
| CI-5 | cancelled + start khớp nhưng stop khớp (negative) | Không tạo task mới |

#### TCOND-01-05 — Hoàn thành khi stop khớp (task chưa vi phạm)

**Feature:** FT-01 | **REQ-ID:** REQ-FUNC-009 | **Technique:** State Transition

**Mô tả điều kiện:** Task `in_progress` chưa quá hạn khi stop khớp chuyển `achieved`, ghi `end_time` và 1 event `complete`; task đã kết thúc không đổi khi stop khớp lần nữa. (Phần vi phạm và paused: TCOND-03-04.)

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | in_progress chưa vi phạm → stop | `achieved`, `end_time` = thời điểm stop, đúng 1 event `complete` |
| CI-2 | achieved → stop khớp lần nữa (negative) | Task và số event không đổi |

#### TCOND-01-06 — Kích hoạt đánh giá khi tạo hoặc sửa record

**Feature:** FT-01 | **REQ-ID:** REQ-FUNC-004 | **Technique:** EP

**Mô tả điều kiện:** Lớp tạo record khớp start; tạo record không khớp; sửa field nằm trong điều kiện; sửa field không liên quan (không được làm phát sinh event hay đổi task).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Tạo record khớp start | Có 1 task `in_progress` |
| CI-2 | Tạo record không khớp start | Không có task |
| CI-3 | Sửa field nằm trong điều kiện stop | Task chuyển `achieved` |
| CI-4 | Sửa field không thuộc điều kiện nào (negative) | Số task và số event không đổi |
| CI-5 | Patch hook bị xóa (lưu automation rule) rồi tự phục hồi | xử lý tiếp theo đăng ký lại patch; record tạo sau đó có task |

#### TCOND-01-07 — Đánh giá lặp lại không đổi kết quả

**Feature:** FT-01 | **REQ-ID:** REQ-FUNC-015 | **Technique:** State Transition

**Mô tả điều kiện:** Đánh giá lần hai trên dữ liệu không đổi không được tạo task, đổi trạng thái hay ghi event. Kiểm ở hai trạng thái: `in_progress` vừa attach và `paused`.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Lặp lại ngay sau attach (`in_progress`) | Số task, giá trị task, số event không đổi |
| CI-2 | Lặp lại khi task `paused` (negative) | Số task, giá trị task, số event không đổi |

#### TCOND-01-08 — Không ghi event khi không đổi trạng thái

**Feature:** FT-01 | **REQ-ID:** REQ-FUNC-029 | **Technique:** EP

**Mô tả điều kiện:** Lần ghi record không làm đổi trạng thái task thì không có event mới. Hai lớp: sửa field điều kiện sang giá trị vẫn cho cùng kết quả đánh giá; ghi lại đúng giá trị cũ.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Đổi giá trị field điều kiện nhưng kết quả đánh giá không đổi | Không event mới |
| CI-2 | Ghi lại đúng giá trị cũ | Không event mới |

**Traceability TG-01**

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-FUNC-003 | TCOND-01-01 | CI-1 | TC-ATT-001 |
| REQ-FUNC-003 | TCOND-01-01 | CI-2 | TC-ATT-002 |
| REQ-FUNC-003 | TCOND-01-02 | CI-1 | TC-ATT-003 |
| REQ-FUNC-003 | TCOND-01-02 | CI-2 | TC-ATT-004 |
| REQ-FUNC-003 | TCOND-01-02 | CI-3 | TC-ATT-005 |
| REQ-FUNC-003 | TCOND-01-02 | CI-4 | TC-ATT-006 |
| REQ-FUNC-006 | TCOND-01-03 | CI-1 | TC-ATT-007 |
| REQ-FUNC-006 | TCOND-01-03 | CI-2 | TC-ATT-008 |
| REQ-FUNC-006 | TCOND-01-03 | CI-3 | TC-ATT-009 |
| REQ-FUNC-006 | TCOND-01-03 | CI-4 | TC-ATT-010 |
| REQ-FUNC-006 | TCOND-01-03 | CI-5 | TC-ATT-011 |
| REQ-FUNC-007 | TCOND-01-04 | CI-1 | TC-ATT-012 |
| REQ-FUNC-007 | TCOND-01-04 | CI-2 | TC-ATT-013 |
| REQ-FUNC-007 | TCOND-01-04 | CI-3 | TC-ATT-014 |
| REQ-FUNC-007 | TCOND-01-04 | CI-4 | TC-ATT-015 |
| REQ-FUNC-007 | TCOND-01-04 | CI-5 | TC-ATT-016 |
| REQ-FUNC-009 | TCOND-01-05 | CI-1 | TC-ATT-017 |
| REQ-FUNC-009 | TCOND-01-05 | CI-2 | TC-ATT-018 |
| REQ-FUNC-004 | TCOND-01-06 | CI-1 | TC-ATT-019 |
| REQ-FUNC-004 | TCOND-01-06 | CI-2 | TC-ATT-020 |
| REQ-FUNC-004 | TCOND-01-06 | CI-3 | TC-ATT-021 |
| REQ-FUNC-004 | TCOND-01-06 | CI-4 | TC-ATT-022 |
| REQ-FUNC-004 | TCOND-01-06 | CI-5 | TC-ATT-027 |
| REQ-FUNC-015 | TCOND-01-07 | CI-1 | TC-ATT-023 |
| REQ-FUNC-015 | TCOND-01-07 | CI-2 | TC-ATT-024 |
| REQ-FUNC-029 | TCOND-01-08 | CI-1 | TC-ATT-025 |
| REQ-FUNC-029 | TCOND-01-08 | CI-2 | TC-ATT-026 |

---

### FT-02 / TG-02 — Pause và resume

**Technique:** State Transition (vòng đời `in_progress` ↔ `paused`), Decision Table (chế độ resume × trạng thái pause/resume), EP (cờ vi phạm bật/tắt khi xếp lại hạn). Pause/resume là chuyển trạng thái có điều kiện; chế độ resume tạo bảng quyết định nhỏ.

#### TCOND-02-01 — Pause task đang chạy

**Feature:** FT-02 | **REQ-ID:** REQ-FUNC-011 | **Technique:** State Transition

**Mô tả điều kiện:** Chuyển trạng thái khi pause khớp:

| Trạng thái trước | Sự kiện | Kết quả |
|---|---|---|
| `in_progress` | pause khớp | `paused`, chốt thời gian đã trôi, 1 event `pause` |
| `paused` | pause vẫn khớp | không đổi, không event |
| `achieved` | pause khớp | không đổi |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | `in_progress` → pause | `paused`, `business_duration` = giờ đã chạy, đúng 1 event `pause` |
| CI-2 | `paused` + pause vẫn khớp (negative) | Không có event mới |
| CI-3 | `achieved` + pause khớp (negative) | Task không đổi |

#### TCOND-02-02 — Resume ở chế độ `condition`

**Feature:** FT-02 | **REQ-ID:** REQ-FUNC-037 | **Technique:** Decision Table

**Mô tả điều kiện:** | Rule | pause | resume | Kết quả (resume_mode = `condition`) |
|---|---|---|---|
| R1 | N | Y | `in_progress`, 1 event `resume` |
| R2 | N | N | vẫn `paused`, không event |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | R1: resume khớp | `in_progress`, đúng 1 event `resume` |
| CI-2 | R2: pause hết khớp, resume chưa khớp (negative) | Vẫn `paused`, không event `resume` |

#### TCOND-02-03 — Resume ở chế độ `pause_unmatched`

**Feature:** FT-02 | **REQ-ID:** REQ-FUNC-048 | **Technique:** Decision Table

**Mô tả điều kiện:** | Rule | pause | resume | Kết quả (resume_mode = `pause_unmatched`) |
|---|---|---|---|
| R1 | N | N | `in_progress`, 1 event `resume` |
| R2 | Y | Y | vẫn `paused` |

Cộng một kịch bản đầu cuối (cấu hình khuyến nghị) theo State Transition: attach → pause → (pause→pause không event) → resume → complete.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | R1: pause hết khớp | `in_progress`, đúng 1 event `resume` (dù resume không khớp) |
| CI-2 | R2: pause vẫn khớp, resume khớp (negative) | Vẫn `paused`, không event `resume` |
| CI-3 | Đầu cuối: in_progress → waiting_customer → resolved → in_progress → closed | 1 task; 4 event [attach, pause, resume, complete]; task `achieved` |

#### TCOND-02-04 — Xếp lại hạn khi resume

**Feature:** FT-02 | **REQ-ID:** REQ-FUNC-044 | **Technique:** EP

**Mô tả điều kiện:** Hai lớp theo dấu vi phạm lúc resume: chưa bật thì `planned_end_time` = thời điểm resume + (mục tiêu − đã trôi, tối thiểu 0); đã bật thì `planned_end_time` giữ nguyên.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Dấu vi phạm chưa bật | `planned_end_time` = thời điểm resume + phần còn lại |
| CI-2 | Dấu vi phạm đã bật (negative) | `planned_end_time` không đổi |

#### TCOND-02-05 — Nhật ký đủ bốn event của vòng đời

**Feature:** FT-02 | **REQ-ID:** REQ-FUNC-029 | **Technique:** State Transition

**Mô tả điều kiện:** Vòng đời attach → pause → resume → stop ghi đúng 4 event theo thứ tự thời gian.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Vòng đời đầy đủ | Đúng 4 event: `attach`, `pause`, `resume`, `complete` theo thứ tự thời gian |

**Traceability TG-02**

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-FUNC-011 | TCOND-02-01 | CI-1 | TC-PAU-001 |
| REQ-FUNC-011 | TCOND-02-01 | CI-2 | TC-PAU-002 |
| REQ-FUNC-011 | TCOND-02-01 | CI-3 | TC-PAU-003 |
| REQ-FUNC-037 | TCOND-02-02 | CI-1 | TC-PAU-004 |
| REQ-FUNC-037 | TCOND-02-02 | CI-2 | TC-PAU-005 |
| REQ-FUNC-048 | TCOND-02-03 | CI-1 | TC-PAU-006 |
| REQ-FUNC-048 | TCOND-02-03 | CI-2 | TC-PAU-007 |
| REQ-FUNC-048 | TCOND-02-03 | CI-3 | TC-PAU-008 |
| REQ-FUNC-044 | TCOND-02-04 | CI-1 | TC-PAU-009 |
| REQ-FUNC-044 | TCOND-02-04 | CI-2 | TC-PAU-010 |
| REQ-FUNC-029 | TCOND-02-05 | CI-1 | TC-PAU-011 |

---

### FT-03 / TG-03 — Vi phạm và quanh hạn

**Technique:** BVA (mốc `planned_end_time`, phần trăm đã dùng), Decision Table (kết quả stop theo trạng thái × cờ vi phạm), EP (nơi phát hiện vi phạm), Error Guessing (escalate lỗi). Vi phạm xảy ra tại ngưỡng thời gian cụ thể nên dùng BVA; kết quả stop phụ thuộc tổ hợp nên dùng bảng quyết định.

#### TCOND-03-01 — Phát hiện vi phạm bằng xử lý nền quanh `planned_end_time`

**Feature:** FT-03 | **REQ-ID:** REQ-FUNC-022 | **Technique:** BVA

**Mô tả điều kiện:** Task bắt đầu 09:00, mục tiêu 4 giờ, lịch 24x7 nên `planned_end_time` = 13:00. Biên: ngay trước hạn (12:59), đúng hạn (13:00), sau hạn (13:01); thêm lần xử lý thứ hai để kiểm "đúng một lần".

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Trước biên: now = 12:59 (negative) | Không bật dấu vi phạm, không event `breach` |
| CI-2 | Tại biên: now = 13:00 | Bật dấu vi phạm, 1 event `breach` |
| CI-3 | Sau biên: now = 13:01 | Bật dấu vi phạm, đúng 1 event `breach`, task vẫn `in_progress` |
| CI-4 | Xử lý nền chạy lần hai sau khi đã vi phạm (negative) | Vẫn đúng 1 event `breach` |

#### TCOND-03-02 — Phát hiện vi phạm khi record được cập nhật

**Feature:** FT-03 | **REQ-ID:** REQ-FUNC-022 | **Technique:** BVA

**Mô tả điều kiện:** Nếu record được cập nhật (pause) trước khi xử lý nền chạy, vi phạm được phát hiện tại lúc cập nhật. Hai điểm: sau hạn (14:00) và đúng hạn (13:00).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Pause sau `planned_end_time` (14:00), chưa có xử lý nền | Dấu vi phạm bật; event `breach` lúc 14:00 ghi trước event `pause`; task `paused` |
| CI-2 | Pause đúng `planned_end_time` (13:00), đã trôi = mục tiêu | Dấu vi phạm bật (chạm hạn), event `breach` rồi `pause` |

#### TCOND-03-03 — Event `breach` ghi trước các mốc escalation từ 100%

**Feature:** FT-03 | **REQ-ID:** REQ-FUNC-022 | **Technique:** EP

**Mô tả điều kiện:** Hai lớp mốc: đúng 100% và trên 100% (120%), đến hạn cùng lần xử lý với vi phạm.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Mốc 100% cùng đến hạn với vi phạm | `breach` có thứ tự ghi và `event_dt` không muộn hơn `escalate` của mốc 100% |
| CI-2 | Mốc 120% đến hạn trong cùng lần xử lý với vi phạm | `breach` ghi trước `escalate` của mốc 120% |

#### TCOND-03-04 — Kết quả stop theo trạng thái và dấu vi phạm

**Feature:** FT-03 | **REQ-ID:** REQ-FUNC-009 | **Technique:** Decision Table

**Mô tả điều kiện:** | Rule | Trạng thái lúc stop | Dấu vi phạm trước stop | Đã quá `planned_end_time` lúc stop | Kết quả |
|---|---|---|---|---|
| R1 | `in_progress` | tắt | không | `achieved` (TC-ATT-017) |
| R2 | `in_progress` | tắt | có (chưa xử lý nền) | `breached` |
| R3 | `paused` | tắt | có | `achieved` (không so với `planned_end_time`) |
| R4 | `paused` | bật | có | `breached` |
| R5 | `in_progress` | bật (đã xử lý nền) | có | `breached`, `breach` không bị ghi trùng |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | R2 | `breached`, `end_time` = thời điểm stop, event [attach, breach, complete] |
| CI-2 | R3 (boundary: paused 5 ngày làm việc, còn dư 2 giờ) | `achieved`, `has_breached` tắt |
| CI-3 | R4 | `breached` |
| CI-4 | R5 | `breached`, đúng 1 event `breach`, đúng 1 `complete` |

#### TCOND-03-05 — Dấu vi phạm không tắt và mức vượt được giữ

**Feature:** FT-03 | **REQ-ID:** REQ-FUNC-046 | **Technique:** State Transition

**Mô tả điều kiện:** Task đã vi phạm đi qua pause và resume: cờ vẫn bật; thời gian đã trôi được cộng dồn nên mốc 120% bắn khi tổng đã trôi đạt 4,8 giờ.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Cờ bật → resume (negative: cờ không tắt) | `has_breached` vẫn bật |
| CI-2 | Đã trôi 4,4 giờ (110%) → pause → resume → mốc 120% | Mốc 120% bắn khi tổng đã trôi = 4,8 giờ, không sớm hơn |
| CI-3 | CHECK chéo của task (dấu vi phạm và stage nhất quán) | CSDL từ chối ghi sai |

#### TCOND-03-06 — Phần trăm thời lượng đã dùng

**Feature:** FT-03 | **REQ-ID:** REQ-INT-023 | **Technique:** BVA

**Mô tả điều kiện:** Phần trăm = floor(đã trôi / mục tiêu × 100) tại thời điểm xem; cho phép vượt 100%; không đổi khi `paused`. Mục tiêu 4 giờ. Biên: 0, 99, 100, vượt 100; làm tròn xuống tại 49,58%.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | 1 giờ trên 4 giờ | 25% |
| CI-2 | Vượt mục tiêu (5 giờ trên 4 giờ) (boundary) | 125% |
| CI-3 | Task `paused`, xem hai lần cách nhau 2 giờ làm việc (negative) | Phần trăm không đổi |
| CI-4 | Làm tròn xuống: 1h59m trên 4 giờ (49,58%) | 49% |
| CI-5 | Ngay dưới biên: 3h59m (99,58%) | 99% |
| CI-6 | Đúng biên: 4h | 100% |
| CI-7 | Biên dưới: vừa attach (0h) | 0% |

#### TCOND-03-07 — Ghi chú lỗi của event `escalate_failed`

**Feature:** FT-03 | **REQ-ID:** REQ-FUNC-029 | **Technique:** Error Guessing

**Mô tả điều kiện:** Server action của mốc escalation ném lỗi và không bật thử lại: event `escalate_failed` phải có ghi chú không rỗng chứa thông báo lỗi.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Server action lỗi, retry tắt | Có event `escalate_failed`, `note` không rỗng và chứa thông báo lỗi |

**Traceability TG-03**

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-FUNC-022 | TCOND-03-01 | CI-1 | TC-BRE-001 |
| REQ-FUNC-022 | TCOND-03-01 | CI-2 | TC-BRE-002 |
| REQ-FUNC-022 | TCOND-03-01 | CI-3 | TC-BRE-003 |
| REQ-FUNC-022 | TCOND-03-01 | CI-4 | TC-BRE-004 |
| REQ-FUNC-022 | TCOND-03-02 | CI-1 | TC-BRE-005 |
| REQ-FUNC-022 | TCOND-03-02 | CI-2 | TC-BRE-006 |
| REQ-FUNC-022 | TCOND-03-03 | CI-1 | TC-BRE-007 |
| REQ-FUNC-022 | TCOND-03-03 | CI-2 | TC-BRE-008 |
| REQ-FUNC-009 | TCOND-03-04 | CI-1 | TC-BRE-009 |
| REQ-FUNC-009 | TCOND-03-04 | CI-2 | TC-BRE-010 |
| REQ-FUNC-009 | TCOND-03-04 | CI-3 | TC-BRE-011 |
| REQ-FUNC-009 | TCOND-03-04 | CI-4 | TC-BRE-012 |
| REQ-FUNC-046 | TCOND-03-05 | CI-1 | TC-BRE-013 |
| REQ-FUNC-046 | TCOND-03-05 | CI-2 | TC-BRE-014 |
| REQ-FUNC-046 | TCOND-03-05 | CI-3 | TC-BRE-023 |
| REQ-INT-023 | TCOND-03-06 | CI-1 | TC-BRE-015 |
| REQ-INT-023 | TCOND-03-06 | CI-2 | TC-BRE-016 |
| REQ-INT-023 | TCOND-03-06 | CI-3 | TC-BRE-017 |
| REQ-INT-023 | TCOND-03-06 | CI-4 | TC-BRE-018 |
| REQ-INT-023 | TCOND-03-06 | CI-5 | TC-BRE-019 |
| REQ-INT-023 | TCOND-03-06 | CI-6 | TC-BRE-020 |
| REQ-INT-023 | TCOND-03-06 | CI-7 | TC-BRE-021 |
| REQ-FUNC-029 | TCOND-03-07 | CI-1 | TC-BRE-022 |

---

### FT-04 / TG-04 — Cancel và reset (kể cả reset theo field)

**Technique:** Decision Table + State Transition — Thứ tự ưu tiên stop > cancel/start_unmatched > reset > pause > resume là một bảng quyết định nhiều điều kiện; vòng đời task (`in_progress`, `paused` sang `cancelled`, `achieved`, `breached`, task mới) là chuyển trạng thái. Reset theo field là tổ hợp (điều kiện reset khớp) x (field đổi giá trị), nên dùng bảng quyết định và Error Guessing cho các trường hợp không được kích hoạt.

#### TCOND-04-01 — Thứ tự ưu tiên khi task đang hoạt động

**Feature:** FT-04 | **REQ-ID:** REQ-FUNC-008 | **Technique:** Decision Table

**Mô tả điều kiện:** Quy tắc (REQ-FUNC-008): kiểm tra từ trên xuống, dừng ở mục đầu tiên khớp. Bảng quyết định (S=stop, C=cancel theo chế độ, R=reset, P=pause; 1=khớp):

| Luật | S | C | R (+start) | P | Kết quả mong đợi | CI |
|---|---|---|---|---|---|---|
| L1 | 1 | 0 | 0 | 1 | kết thúc theo stop, không `pause` | CI-1 |
| L2 | 1 | 1 | 0 | 0 | kết thúc theo stop, không `cancel` | CI-2 |
| L3 | 0 | 1 (condition) | 0 | 1 | `cancelled` | CI-3 |
| L4 | 0 | 0 | 1 | 1 | reset, task mới `paused`, task cũ không `pause` | CI-4 |
| L5 | 0 | 0 | 0 | 0 | không đổi | CI-5 |
| L6 | 0 | 1 (condition) | 1 | 0 | `cancelled`, không reset | CI-6 |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | stop khớp + pause khớp -> kết thúc theo stop | Task `achieved` và không có event `pause`. |
| CI-2 | stop khớp + cancel khớp -> stop thắng | Task `achieved`, không có event `cancel`. |
| CI-3 | cancel (condition) khớp + pause khớp -> cancelled | Task `cancelled`, không có event `pause`. |
| CI-4 | reset + start + pause cùng khớp -> reset thắng pause | T-old không có event `pause`, có event `reset`; T-new tồn tại. |
| CI-5 | không điều kiện nào khớp -> không đổi | Không có task hoặc event mới, `stage` không đổi. |
| CI-6 | cancel (condition) khớp + reset khớp -> cancel thắng reset | Task `cancelled`, không có task mới, không có event `reset`. |

#### TCOND-04-02 — Ba chế độ cancel

**Feature:** FT-04 | **REQ-ID:** REQ-FUNC-010 | **Technique:** Decision Table

**Mô tả điều kiện:** Chế độ cancel (REQ-FUNC-010) x (start còn khớp?, cancel khớp?):

| Chế độ | start khớp | cancel khớp | Kết quả | CI |
|---|---|---|---|---|
| start_unmatched | 0 | 0 | `cancelled`, có `end_time`, 1 `cancel` | CI-1 |
| condition | 1 | 1 | `cancelled` | CI-2 |
| never | 0 | 1 | không hủy | CI-3 |
| condition | 0 | 0 | không hủy | CI-4 |
| start_unmatched | 1 | 1 | không hủy [G3] | CI-5 |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | start_unmatched: start hết khớp -> cancelled | Task `cancelled`, `end_time` có giá trị, đúng 1 event `cancel`. |
| CI-2 | condition: cancel khớp -> cancelled | Task `cancelled` dù start vẫn khớp. |
| CI-3 | never: start hết khớp và cancel khớp -> không hủy | Task vẫn `in_progress`, không event `cancel`. |
| CI-4 | condition: start hết khớp nhưng cancel chưa khớp -> không hủy | Task không bị hủy vì chế độ condition chỉ xét cancel. |
| CI-5 | start_unmatched: cancel khớp nhưng start vẫn khớp -> không hủy | Task không bị hủy; domain cancel không có tác dụng ở chế độ start_unmatched. |

#### TCOND-04-03 — Reset: hành động, trạng thái nguồn và điều kiện áp dụng

**Feature:** FT-04 | **REQ-ID:** REQ-FUNC-012 | **Technique:** State Transition

**Mô tả điều kiện:** Chuyển trạng thái khi điều kiện reset khớp (REQ-FUNC-012):

| Trạng thái nguồn | Hành động reset | Điều kiện | Task cũ | Task mới | CI |
|---|---|---|---|---|---|
| in_progress | cancel | start khớp | cancelled | in_progress | CI-1 |
| in_progress | complete (chưa quá hạn) | start khớp | achieved | in_progress | CI-2 |
| in_progress | complete | start + pause khớp | achieved | paused | CI-3 |
| achieved | bất kỳ | reset + start khớp | không đổi | không có | CI-4 |
| in_progress | cancel | start không khớp | cancelled | không có | CI-5 |
| paused | cancel | start khớp | cancelled | in_progress | CI-6 |
| in_progress | complete (quá hạn) | start khớp | breached | in_progress | CI-7 |
| cancelled | bất kỳ | reset + start khớp | không reset; gắn bằng attach | in_progress | CI-8 |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | reset_action=cancel, task in_progress | T-old `cancelled`, T-new `in_progress`, 1 event `reset`. |
| CI-2 | reset_action=complete, chưa quá hạn -> achieved | T-old `achieved`, task mới `in_progress`. |
| CI-3 | reset + pause cùng khớp -> task mới paused | Task mới `paused`. |
| CI-4 | task gần nhất achieved -> reset không áp dụng | Không có task mới, task `achieved` bất biến, không event mới. |
| CI-5 | reset khớp nhưng start không khớp -> kết thúc theo reset, không task mới | Task cũ `cancelled`, không có task mới. |
| CI-6 | reset áp dụng cho task paused | Reset hoạt động trên task `paused`. |
| CI-7 | reset_action=complete, quá hạn -> breached | T-old `breached`, task mới `in_progress`. |
| CI-8 | task gần nhất cancelled: reset không áp dụng, gắn lại theo attach | T2 được gắn bằng attach; không có event `reset`. |
| CI-9 | Reset và attach lại: ghi task cũ trước khi tạo task mới | không vi phạm chỉ mục duy nhất, không event `error` |

#### TCOND-04-04 — Reset chỉ khi field theo dõi đổi giá trị

**Feature:** FT-04 | **REQ-ID:** REQ-FUNC-013 | **Technique:** Decision Table

**Mô tả điều kiện:** Reset xảy ra khi và chỉ khi (điều kiện reset khớp) VÀ (ít nhất một field theo dõi đổi giá trị) (REQ-FUNC-013):

| Điều kiện reset khớp | Field theo dõi đổi | Kết quả | CI |
|---|---|---|---|
| 1 | 1 (field thường) | reset | CI-1 |
| 1 | 0 | không reset | CI-2 |
| 1 | 1 (compute có lưu, do tính lại) | reset | CI-3 |
| 0 | 1 | không reset | CI-4 |
| 1 | 1 trên 2 field theo dõi, chỉ 1 field đổi | reset | CI-5 |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | field theo dõi đổi giá trị -> reset | Có reset đúng 1 lần. |
| CI-2 | field theo dõi giữ nguyên giá trị -> không reset | Không reset. |
| CI-3 | field compute có lưu đổi do tính lại -> reset | Reset xảy ra khi giá trị compute có lưu đổi. |
| CI-4 | field theo dõi đổi nhưng điều kiện reset không khớp -> không reset | Không reset vì điều kiện reset không khớp. |
| CI-5 | danh sách nhiều field, chỉ một field đổi -> reset | Reset xảy ra dù chỉ một field đổi. |

#### TCOND-04-05 — Bốn trường hợp không kích hoạt reset theo field

**Feature:** FT-04 | **REQ-ID:** REQ-FUNC-050 | **Technique:** Error Guessing

**Mô tả điều kiện:** Khi có cấu hình field kích hoạt reset (REQ-FUNC-050), bốn nguồn sau không được reset dù điều kiện reset khớp: ghi field theo dõi bằng giá trị cũ (CI-1); chỉ ghi field khác (CI-2); Đánh giá lại thủ công, `changed` rỗng (CI-3); xử lý nền theo thời gian, `changed` rỗng (CI-4).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | ghi field theo dõi bằng đúng giá trị cũ -> không reset | Không reset. |
| CI-2 | chỉ ghi field khác -> không reset | Không reset. |
| CI-3 | Đánh giá lại thủ công -> không reset | Không reset. |
| CI-4 | xử lý nền theo thời gian -> không reset | Không reset. |

#### TCOND-04-06 — Điều kiện reset rỗng và ghi chú field đã đổi

**Feature:** FT-04 | **REQ-ID:** REQ-FUNC-051 | **Technique:** Decision Table

**Mô tả điều kiện:** REQ-FUNC-051: reset rỗng hoặc `[]` nghĩa là chưa cấu hình, kể cả khi có field theo dõi; muốn reset chỉ theo field thì đặt domain luôn đúng `[('id', '!=', 0)]`.

| reset_domain | Field theo dõi đổi | Kết quả | CI |
|---|---|---|---|
| rỗng hoặc `[]` | 1 | không reset | CI-1 |
| `[('id', '!=', 0)]` | `user_id` | reset, `note` chứa `user_id` | CI-2 |
| `[('id', '!=', 0)]` | `user_id` và `comment` | `note` chứa cả hai | CI-3 |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | điều kiện reset rỗng + có field theo dõi -> không reset | Không reset. |
| CI-2 | reset [] + field theo dõi đổi -> ghi chú event reset chứa tên field | `note` của event `reset` chứa `user_id`. |
| CI-3 | hai field đổi -> ghi chú chứa cả hai tên | `note` chứa đủ cả hai tên field. |

**Traceability TG-04**

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-FUNC-008 | TCOND-04-01 | CI-1 | TC-CAN-001 |
| REQ-FUNC-008 | TCOND-04-01 | CI-2 | TC-CAN-002 |
| REQ-FUNC-008 | TCOND-04-01 | CI-3 | TC-CAN-003 |
| REQ-FUNC-008 | TCOND-04-01 | CI-4 | TC-CAN-004 |
| REQ-FUNC-008 | TCOND-04-01 | CI-5 | TC-CAN-005 |
| REQ-FUNC-008 | TCOND-04-01 | CI-6 | TC-CAN-006 |
| REQ-FUNC-010 | TCOND-04-02 | CI-1 | TC-CAN-007 |
| REQ-FUNC-010 | TCOND-04-02 | CI-2 | TC-CAN-008 |
| REQ-FUNC-010 | TCOND-04-02 | CI-3 | TC-CAN-009 |
| REQ-FUNC-010 | TCOND-04-02 | CI-4 | TC-CAN-010 |
| REQ-FUNC-010 | TCOND-04-02 | CI-5 | TC-CAN-011 |
| REQ-FUNC-012 | TCOND-04-03 | CI-1 | TC-CAN-012 |
| REQ-FUNC-012 | TCOND-04-03 | CI-2 | TC-CAN-013 |
| REQ-FUNC-012 | TCOND-04-03 | CI-3 | TC-CAN-014 |
| REQ-FUNC-012 | TCOND-04-03 | CI-4 | TC-CAN-015 |
| REQ-FUNC-012 | TCOND-04-03 | CI-5 | TC-CAN-016 |
| REQ-FUNC-012 | TCOND-04-03 | CI-6 | TC-CAN-017 |
| REQ-FUNC-012 | TCOND-04-03 | CI-7 | TC-CAN-018 |
| REQ-FUNC-012 | TCOND-04-03 | CI-8 | TC-CAN-019 |
| REQ-FUNC-012 | TCOND-04-03 | CI-9 | TC-CAN-032 |
| REQ-FUNC-013 | TCOND-04-04 | CI-1 | TC-CAN-020 |
| REQ-FUNC-013 | TCOND-04-04 | CI-2 | TC-CAN-021 |
| REQ-FUNC-013 | TCOND-04-04 | CI-3 | TC-CAN-022 |
| REQ-FUNC-013 | TCOND-04-04 | CI-4 | TC-CAN-023 |
| REQ-FUNC-013 | TCOND-04-04 | CI-5 | TC-CAN-024 |
| REQ-FUNC-050 | TCOND-04-05 | CI-1 | TC-CAN-025 |
| REQ-FUNC-050 | TCOND-04-05 | CI-2 | TC-CAN-026 |
| REQ-FUNC-050 | TCOND-04-05 | CI-3 | TC-CAN-027 |
| REQ-FUNC-050 | TCOND-04-05 | CI-4 | TC-CAN-028 |
| REQ-FUNC-051 | TCOND-04-06 | CI-1 | TC-CAN-029 |
| REQ-FUNC-051 | TCOND-04-06 | CI-2 | TC-CAN-030 |
| REQ-FUNC-051 | TCOND-04-06 | CI-3 | TC-CAN-031 |

### FT-05 / TG-05 — Ba cấu hình dễ sai

**Technique:** Decision Table + Error Guessing — Ba cấu hình sai thường gặp (start ⊂ stop, pause ⊂ start, start và pause loại trừ) kết hợp với chế độ cancel cho kết quả khác nhau; liệt kê từng tổ hợp thành bảng quyết định, các ca này là lỗi người cấu hình hay mắc nên chọn theo Error Guessing.

#### TCOND-05-01 — (a) start là tập con của stop

**Feature:** FT-05 | **REQ-ID:** REQ-FUNC-016 | **Technique:** Decision Table

**Mô tả điều kiện:** Start ⊂ stop thì mọi chế độ cancel đều không gắn SLA (REQ-FUNC-016 AC1):

| cancel_mode | Kết quả | CI |
|---|---|---|
| start_unmatched | không gắn | CI-1 |
| condition | không gắn | CI-2 |
| never | không gắn | CI-3 |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | (a) start ⊂ stop, cancel_mode=start_unmatched -> không gắn | Không có task nào được gắn. |
| CI-2 | (a) start ⊂ stop, cancel_mode=condition -> không gắn | Không có task nào được gắn. |
| CI-3 | (a) start ⊂ stop, cancel_mode=never -> không gắn | Không có task nào được gắn. |

#### TCOND-05-02 — (b) pause là tập con của start

**Feature:** FT-05 | **REQ-ID:** REQ-FUNC-016 | **Technique:** State Transition

**Mô tả điều kiện:** Chuỗi chuyển: (không có task) → `paused` (attach khi pause khớp) → `cancelled` (pause hết khớp kéo theo start hết khớp, chế độ start_unmatched). CI-1 phủ bước đầu, CI-2 phủ bước sau (REQ-FUNC-016 AC2).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | (b) pause ⊂ start: gắn ở paused | Task `paused` được gắn. |
| CI-2 | (b) pause ⊂ start: hết hold -> cancelled | Task chuyển `paused` -> `cancelled`. |

#### TCOND-05-03 — (c) start và pause loại trừ nhau

**Feature:** FT-05 | **REQ-ID:** REQ-FUNC-008, REQ-FUNC-016 | **Technique:** Decision Table

**Mô tả điều kiện:** Record chuyển sang giá trị thỏa pause (và không còn thỏa start) (REQ-FUNC-016 AC3, AC4; REQ-FUNC-008):

| cancel_mode | Kết quả | CI |
|---|---|---|
| start_unmatched | `cancelled`, không `pause` | CI-1 |
| never | `paused` | CI-2 |
| condition (cancel chưa khớp) | `paused` | CI-3 |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | (c) start_unmatched: cancel trước khi kịp pause | Task `cancelled` và không có event `pause`. |
| CI-2 | (c) never: ở lại và pause | Task `paused`, không event `cancel`. |
| CI-3 | (c) condition, cancel chưa khớp: ở lại và pause | Task `paused`, không bị hủy. |

**Traceability TG-05**

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-FUNC-016 | TCOND-05-01 | CI-1 | TC-MIS-001 |
| REQ-FUNC-016 | TCOND-05-01 | CI-2 | TC-MIS-002 |
| REQ-FUNC-016 | TCOND-05-01 | CI-3 | TC-MIS-003 |
| REQ-FUNC-016 | TCOND-05-02 | CI-1 | TC-MIS-004 |
| REQ-FUNC-016 | TCOND-05-02 | CI-2 | TC-MIS-005 |
| REQ-FUNC-016 | TCOND-05-03 | CI-1 | TC-MIS-006 |
| REQ-FUNC-008 | TCOND-05-03 | CI-1 | TC-MIS-006 |
| REQ-FUNC-016 | TCOND-05-03 | CI-2 | TC-MIS-007 |
| REQ-FUNC-016 | TCOND-05-03 | CI-3 | TC-MIS-008 |

### FT-06 / TG-06 — Giờ làm việc

**Technique:** BVA kết hợp EP. Hạn chót và thời gian đã trôi có nhiều điểm biên theo lịch (mục tiêu 0, mốc đúng giờ đóng cửa, qua cuối tuần, global leave, múi giờ); EP dùng cho các lớp lịch (có lịch, không lịch, lịch không xếp được hạn).

#### TCOND-06-01 — Hạn chót cộng theo giờ làm việc của lịch, trừ ngày nghỉ

**Feature:** FT-06 | **REQ-ID:** REQ-FUNC-018 | **Technique:** EP

**Mô tả điều kiện:** Hạn chót được cộng theo giờ làm việc của lịch từ mốc bắt đầu. Hai lớp tương đương: (a) khoảng cộng đi qua ngày không làm việc (cuối tuần); (b) khoảng cộng đi qua ngày nghỉ global leave của lịch.

| Lớp | Ngày không làm việc trên đường đi | Cách xử lý mong đợi |
|---|---|---|
| a | Thứ Bảy, Chủ Nhật | Bỏ qua, phần giờ còn lại tính vào thứ Hai |
| b | Thứ Hai là global leave | Bỏ qua cả thứ Hai, phần còn lại tính vào thứ Ba |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Lớp a: cộng 8 giờ từ thứ Sáu 16:00, lịch T2-T6 08:00-17:00 | `planned_end_time` = thứ Hai 15:00 (1 giờ thứ Sáu + 7 giờ thứ Hai) |
| CI-2 | Lớp b: như trên, thứ Hai là global leave | `planned_end_time` = thứ Ba 15:00 |

#### TCOND-06-02 — Biên của hạn chót: mục tiêu 0 giờ và mốc đúng giờ đóng cửa

**Feature:** FT-06 | **REQ-ID:** REQ-FUNC-018 | **Technique:** BVA

**Mô tả điều kiện:** Hai biên: (1) mục tiêu bằng 0, giá trị nhỏ nhất được chấp nhận (REQ-FUNC-018 AC3); (2) mốc bắt đầu trùng giờ kết thúc ca cuối tuần.

| Biên | Điểm kiểm | Mong đợi |
|---|---|---|
| Mục tiêu | 0 giờ | hạn = mốc bắt đầu |
| Giờ bắt đầu | đúng 17:00 thứ Sáu, mục tiêu 1 giờ | hạn = thứ Hai 09:00 |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Biên mục tiêu = 0 giờ | `planned_end_time` = `start_time` |
| CI-2 | Biên mốc đúng 17:00 thứ Sáu, mục tiêu 1 giờ | `planned_end_time` = thứ Hai 09:00 |

#### TCOND-06-03 — Múi giờ của lịch khi quy đổi sang UTC

**Feature:** FT-06 | **REQ-ID:** REQ-FUNC-018 | **Technique:** EP

**Mô tả điều kiện:** Lịch có múi giờ `Asia/Ho_Chi_Minh` (UTC+7); mốc và hạn lưu UTC. Một lớp: mốc bắt đầu trong giờ làm việc, hạn nằm cùng ngày.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Mốc 09:00 giờ địa phương, mục tiêu 2 giờ | `planned_end_time` = 11:00 giờ địa phương = 04:00 UTC (không lệch 7 giờ) |

#### TCOND-06-04 — Task không có lịch cộng thẳng theo 24x7

**Feature:** FT-06 | **REQ-ID:** REQ-FUNC-018 | **Technique:** EP

**Mô tả điều kiện:** Khi không có lịch, thời lượng mục tiêu cộng thẳng vào mốc bắt đầu theo đồng hồ.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Không lịch, mục tiêu 4 giờ | `planned_end_time` = `start_time` + 4 giờ |

#### TCOND-06-05 — Lịch không xếp được hạn

**Feature:** FT-06 | **REQ-ID:** REQ-FUNC-018 | **Technique:** Error Guessing

**Mô tả điều kiện:** Lịch có ngày nghỉ phủ kín quá giới hạn tìm kiếm (100 cửa sổ 14 ngày liên tiếp) nên không xếp được hạn: attach thất bại có kiểm soát (REQ-FUNC-030).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Ngày nghỉ phủ kín > 100 cửa sổ 14 ngày | Không có task; có event `error` cho record; record vẫn lưu được |

#### TCOND-06-06 — Thời gian đã trôi theo giờ làm việc, cộng dồn qua pause, có thể vượt mục tiêu

**Feature:** FT-06 | **REQ-ID:** REQ-FUNC-043 | **Technique:** BVA

**Mô tả điều kiện:** Thời gian đã trôi = tổng giờ làm việc của các đoạn `in_progress`; đoạn `paused` không tính; không bị cắt ở mục tiêu.

| Lịch | Chuỗi đoạn | Đã trôi |
|---|---|---|
| 24x7 | chạy 1h, pause 8h, chạy 2h | 3h |
| T2-T6 08:00-17:00 | thứ Sáu 16:00 đến thứ Hai 10:00 | 3h |
| bất kỳ | paused 6 giờ làm việc | không đổi |
| bất kỳ | mục tiêu 4h, chạy 5h | 5h |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Lịch 24x7: 1h chạy, 8h pause, 2h chạy | `business_duration` = 3 giờ |
| CI-2 | Lịch T2-T6: thứ Sáu 16:00 đến thứ Hai 10:00 | `business_duration` = 3 giờ |
| CI-3 | Negative: task paused 6 giờ làm việc | `business_duration` không tăng |
| CI-4 | Biên: mục tiêu 4 giờ, đã trôi 5 giờ | `business_duration` = 5 (không cắt ở 4) |

#### Traceability — TG-06

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-FUNC-018 | TCOND-06-01 | CI-1 | TC-TIM-001 |
| REQ-FUNC-018 | TCOND-06-01 | CI-2 | TC-TIM-002 |
| REQ-FUNC-018 | TCOND-06-02 | CI-1 | TC-TIM-003 |
| REQ-FUNC-018 | TCOND-06-02 | CI-2 | TC-TIM-004 |
| REQ-FUNC-018 | TCOND-06-03 | CI-1 | TC-TIM-005 |
| REQ-FUNC-018 | TCOND-06-04 | CI-1 | TC-TIM-006 |
| REQ-FUNC-018 | TCOND-06-05 | CI-1 | TC-TIM-007 |
| REQ-FUNC-043 | TCOND-06-06 | CI-1 | TC-TIM-008 |
| REQ-FUNC-043 | TCOND-06-06 | CI-2 | TC-TIM-009 |
| REQ-FUNC-043 | TCOND-06-06 | CI-3 | TC-TIM-010 |
| REQ-FUNC-043 | TCOND-06-06 | CI-4 | TC-TIM-011 |

### FT-07 / TG-07 — Retroactive start

**Technique:** BVA + EP — Quyết định breach ngay lúc attach phụ thuộc khoảng cách giữa mốc và now so với mục tiêu (BVA quanh đúng 4 giờ); các lớp field mốc (trống, có giá trị) và kiểu field cấu hình hợp lệ hay không là EP.

#### TCOND-07-01 — Retroactive start: start_time, planned_end_time và breach lúc attach

**Feature:** FT-07 | **REQ-ID:** REQ-FUNC-017 | **Technique:** BVA

**Mô tả điều kiện:** Khoảng cách d = now − mốc so với mục tiêu 4 giờ (lịch 24x7, trừ CI-7): d=1h (không breach), d=3h59m (không breach, biên dưới), d=4h (biên, breach theo Dấu vi phạm chạm hoặc vượt), d=6h (breach, event `breach`). Lớp EP khác: mốc trống (dùng now, có ghi chú), mốc khi record đang paused (không trừ thời gian), mốc có lịch giờ làm việc (CI-7).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | mốc cách 1h, mục tiêu 4h, lịch 24x7 | Giá trị đúng như bước 2. |
| CI-2 | mốc cách 6h -> breach ngay lúc attach | `has_breached`=true và đúng 1 event `breach`. |
| CI-3 | mốc trống -> dùng thời điểm attach + ghi chú | `start_time`=now và `note` của `attach` giải thích. |
| CI-4 | biên: mốc đúng 4h trước (planned_end_time = now) -> breach | Chạm đúng hạn thì breach (theo định nghĩa Dấu vi phạm). |
| CI-5 | biên: mốc cách 3h59m -> chưa breach | Chưa breach. |
| CI-6 | thời gian paused trước attach không được trừ | `planned_end_time` đúng bằng mốc + mục tiêu. |
| CI-7 | retroactive với lịch giờ làm việc | `planned_end_time`=2026-03-02 11:00 ICT, chưa breach. |

#### TCOND-07-02 — Kiểm tra field cấu hình thuộc đúng model và đúng kiểu

**Feature:** FT-07 | **REQ-ID:** REQ-FUNC-041 | **Technique:** EP

**Mô tả điều kiện:** Lớp không hợp lệ: field retroactive không phải kiểu ngày giờ (Char); field retroactive thuộc model khác; field kích hoạt reset thuộc model khác. Lớp hợp lệ: Datetime của đúng model; field reset của đúng model (REQ-FUNC-041).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | field retroactive là Char -> từ chối | Định nghĩa không được lưu. |
| CI-2 | field retroactive thuộc model khác -> từ chối | Định nghĩa không được lưu. |
| CI-3 | field kích hoạt reset thuộc model khác -> từ chối | Định nghĩa không được lưu. |
| CI-4 | field retroactive Datetime đúng model -> lưu được | Định nghĩa được lưu. |
| CI-5 | field kích hoạt reset thuộc đúng model -> lưu được | Định nghĩa được lưu. |

**Traceability TG-07**

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-FUNC-017 | TCOND-07-01 | CI-1 | TC-RET-001 |
| REQ-FUNC-017 | TCOND-07-01 | CI-2 | TC-RET-002 |
| REQ-FUNC-017 | TCOND-07-01 | CI-3 | TC-RET-003 |
| REQ-FUNC-017 | TCOND-07-01 | CI-4 | TC-RET-004 |
| REQ-FUNC-017 | TCOND-07-01 | CI-5 | TC-RET-005 |
| REQ-FUNC-017 | TCOND-07-01 | CI-6 | TC-RET-006 |
| REQ-FUNC-017 | TCOND-07-01 | CI-7 | TC-RET-007 |
| REQ-FUNC-041 | TCOND-07-02 | CI-1 | TC-RET-008 |
| REQ-FUNC-041 | TCOND-07-02 | CI-2 | TC-RET-009 |
| REQ-FUNC-041 | TCOND-07-02 | CI-3 | TC-RET-010 |
| REQ-FUNC-041 | TCOND-07-02 | CI-4 | TC-RET-011 |
| REQ-FUNC-041 | TCOND-07-02 | CI-5 | TC-RET-012 |

### FT-08 / TG-08 — Escalation, thử lại, xử lý nền

> **Trạng thái 19.0.1.1.0:** cơ chế thử lại (`retry`, `retry_pattern`, `cancel_retry_on_stop`, event `escalate_retry`, model `sla.escalation.retry`) đã gỡ ở D12 (2026-11-07). Các test condition TCOND-08-08 đến TCOND-08-13 và các coverage item thử lại ở TCOND-08-05, TCOND-08-06, TCOND-08-07, TCOND-08-17 **không còn hiệu lực**; test case tương ứng (TC-ESC-016, 020 đến 023, 025 đến 043, 052, 060, TC-SEC-014) mang trạng thái "Đã gỡ (D12)" ở `060` Phụ lục D và không có test tự động. Hành vi hiện hành khi action lỗi: ghi `escalate_failed` một lần và coi mốc là đã xong (REQ-FUNC-026, TC-ESC-024). Mốc email (REQ-FUNC-064, 065) được phủ ở TCOND-08-72 đến TCOND-08-74 (mục 7.1).

**Technique:** **EP + BVA + State Transition + Decision Table + Error Guessing** — EP/BVA cho phần trăm mốc, mẫu thử lại, kích thước lô và thời điểm đến hạn; State Transition cho vòng đời mốc (chưa xử lý → chờ thử lại → đã xử lý) và cho stage task; Decision Table cho stage task × có bắn hay không; Error Guessing cho đồng thời, ngắt giữa chừng, lỗi quyền công ty.

#### TCOND-08-01 — Mốc escalation theo phần trăm: bắn đúng mốc, kiểm tra phần trăm khi lưu

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-023 | **Technique:** BVA + EP

**Mô tả điều kiện:** Mỗi mốc gồm `percent` nguyên dương (trên 100 là quá hạn), server action và thứ tự. Lớp hợp lệ: `percent` ≥ 1 nguyên. Lớp không hợp lệ: 0, âm, không nguyên. Biên: 0 (từ chối), 1 (chấp nhận). Khi task chạm mốc, hệ thống chạy action trên record gốc, ghi 1 event `escalate` và đánh dấu mốc đã xử lý. Mục tiêu 4 giờ 24x7: 75% = 3 giờ, 100% = 4 giờ, 120% = 4,8 giờ.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: ba mốc 75/100/120% bắn lần lượt tại 3h, 4h, 4,8h | 3 action chạy tuần tự trên record gốc, mỗi mốc 1 event `escalate` |
| CI-2 | AC2: percent = 0 (biên dưới) bị từ chối | bị từ chối |
| CI-3 | AC2: percent âm (-10) bị từ chối | bị từ chối |
| CI-4 | AC2: percent không nguyên (75,5) bị từ chối | bị từ chối |
| CI-5 | Biên hợp lệ: percent = 1 được chấp nhận | lưu thành công |

#### TCOND-08-02 — Biên thời điểm đến hạn của mốc

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-023 | **Technique:** BVA

**Mô tả điều kiện:** Biên dưới/trên của thời điểm bắn mốc 75% (3 giờ làm việc đã trôi): ngay trước biên (2 giờ 59 phút) chưa bắn; đúng biên (3 giờ 00) bắn.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Biên: đã trôi 2h59 (ngay dưới 75%) | chưa bắn; next_due_at = 12:00 |
| CI-2 | Biên: đã trôi đúng 3h00 (đúng 75%) | bắn đúng 1 lần |

#### TCOND-08-03 — Mỗi mốc bắn đúng một lần

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-024 | **Technique:** State Transition + Error Guessing

**Mô tả điều kiện:** Vòng đời mốc: `chưa xử lý` → (bắn thành công) → `đã xử lý`; từ `đã xử lý` mọi lần xử lý nền tiếp theo không đổi gì. Hai cách tác động lặp: chạy tuần tự hai lần; hai tiến trình đồng thời cùng chọn một task (khóa dòng `SKIP LOCKED`, mô phỏng bằng hai cursor, thứ tự điều khiển bằng mã test).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: xử lý nền chạy hai lần liên tiếp | action 1 lần, 1 event `escalate` |
| CI-2 | AC2: hai tiến trình xử lý nền đồng thời trên cùng task | mốc không bắn hai lần |

#### TCOND-08-04 — Escalation không chạy trong thao tác lưu

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-025 | **Technique:** Error Guessing

**Mô tả điều kiện:** Lưu record (qua Engine) đúng lúc task chạm mốc không được chạy action và không ghi event `escalate`; chỉ xử lý nền mới chạy. Kết quả lần lưu không bị thay đổi.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: lưu record khi task chạm 75% chưa chạy action | chưa có action/event cho tới khi xử lý nền chạy |

#### TCOND-08-05 — Không bắn escalation khi task không ở in_progress

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-054 | **Technique:** Decision Table

**Mô tả điều kiện:** Bảng quyết định theo `stage` của task có mốc chưa xử lý đã quá hạn theo đồng hồ thật:

| stage | Bắn escalation? |
|---|---|
| in_progress | Có (đối chứng, TCOND-08-01) |
| paused | Không |
| achieved | Không |
| breached | Không |
| cancelled | Không |

Mỗi dòng 'Không' là một CI.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: task paused đã qua thời điểm của mốc | không có event `escalate`, action không chạy |
| CI-2 | AC2: task achieved còn mốc chưa xử lý | không có event `escalate`, action không chạy |
| CI-3 | Statement: task breached | không có event `escalate`, action không chạy |
| CI-4 | Statement: task cancelled | không có event `escalate`, action không chạy |

#### TCOND-08-06 — Tính lại mốc khi resume

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-055 | **Technique:** State Transition

**Mô tả điều kiện:** Chuyển trạng thái: in_progress → paused (mốc chưa bắn không bắn, lượt thử lại bị hủy) → in_progress (resume: tính lại thời điểm mọi mốc chưa xử lý theo giờ làm còn lại, kể cả mốc từng chờ thử lại, không giữ lượt thử cũ). Trong lúc `paused` không tính lại và không bắn.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: resume tính lại mốc 75% theo giờ còn lại | mốc 75% bắn 16:00 |
| CI-2 | AC2: mốc đang chờ thử lại khi pause rồi resume | mốc tính lại như chưa xử lý, không còn lượt thử cũ |
| CI-3 | AC3: task vẫn paused thì không tính lại, không bắn | next_due_at NULL, không bắn |

#### TCOND-08-07 — Escalation lỗi (không còn thử lại từ D12)

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-026 | **Technique:** Error Guessing + State Transition

**Mô tả điều kiện:** Khi action của mốc lỗi (không có cơ chế thử lại): ghi `escalate_failed` kèm thông báo lỗi, đánh dấu mốc đã xử lý (chuyển `chưa xử lý` → `đã xử lý`), cô lập lỗi: task/mốc khác vẫn chạy bình thường; các lần xử lý nền sau không chạy lại action.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: action task 1 lỗi, task 2 vẫn bắn | task 1 `escalate_failed`, task 2 `escalate` |
| CI-2 | AC2: chạy nền lần nữa không chạy lại action lỗi | call_count không đổi, không event mới |
| CI-3 | Action lỗi: ghi `escalate_failed` đúng một lần, mốc coi là đã xong ngay, không thử lại (D12) | 1 event `escalate_failed`, mốc nằm trong `done_escalation_ids`, không event thử lại |

#### TCOND-08-08 — Cấu hình thử lại và thời điểm thử lại

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-027 | **Technique:** BVA + State Transition

**Mô tả điều kiện:** Mốc có `retry` = true và `retry_pattern` = danh sách phút. Lần lỗi đầu ghi `escalate_retry` kèm lỗi và giờ thử kế tiếp = giờ lỗi + phút thứ nhất, chưa đánh dấu xử lý; lần thử chạy không sớm hơn `retry_at` và không muộn hơn `retry_at` + 2 phút. Biên: ngay trước `retry_at` (không chạy), đúng `retry_at` (chạy), độ trễ tick cron (≤ 2 phút). Mốc `retry` = false: không có `escalate_retry`.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: lỗi lúc 10:00 ghi 1 escalate_retry với giờ 10:01 | 1 event `escalate_retry`, `retry_at` = 10:01 |
| CI-2 | Biên dưới: chạy lúc 10:00:59 (ngay trước retry_at) | chưa thử lại |
| CI-3 | Biên: chạy đúng retry_at (10:01:00) | thử lại chạy |
| CI-4 | Trễ tick cron: lần thử chạy trong [10:01, 10:03] | lần thử chạy ở tick 10:01:30 |
| CI-5 | AC2: mốc không bật thử lại, action lỗi | không có escalate_retry |

#### TCOND-08-09 — Thử lại thành công

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-056 | **Technique:** State Transition

**Mô tả điều kiện:** Chuyển trạng thái của mốc: `chờ thử lại` → (lần thử thành công) → `đã xử lý` kèm event `escalate`; sau đó không chạy lại.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: lỗi một lần rồi thành công | 1 escalate_retry rồi 1 escalate, mốc đã xử lý |
| CI-2 | AC2: sau khi thành công, chạy nền thêm | action không chạy lại |

#### TCOND-08-10 — Hết số lần thử lại

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-057 | **Technique:** BVA + State Transition

**Mô tả điều kiện:** Số lần thử lại tối đa = độ dài mẫu (biên: mẫu 1 phần tử `[5]` → 1 lần thử). Chuỗi chuyển trạng thái với mẫu `[1, 10]` và action luôn lỗi: lỗi lần 0 (10:00) → `chờ thử` (retry 10:01) → lỗi (10:01) → `chờ thử` (retry 10:11) → lỗi (10:11) → `đã xử lý` kèm `escalate_failed`. Lần thử cuối thành công thì không có `escalate_failed`.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: mẫu [1,10], action luôn lỗi | 2 escalate_retry, 1 escalate_failed, không thử thêm |
| CI-2 | AC2 biên: mẫu [5] → đúng 1 lần thử lại | 1 escalate_retry rồi escalate_failed |
| CI-3 | AC3: lần thử cuối thành công | không có escalate_failed |

#### TCOND-08-11 — Hủy lượt thử lại khi task dừng

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-058 | **Technique:** Decision Table

**Mô tả điều kiện:** Task đang chờ thử lại (có 1 dòng retry, `retry_at` = 10:01) bị tác động:

| Tác động lên task | stage sau | Lượt thử đang chờ |
|---|---|---|
| stop | achieved | Hủy, không chạy |
| cancel | cancelled | Hủy, không chạy |
| pause | paused | Hủy, không chạy |
| stop, cancel, pause, reset khi mốc tắt `cancel_retry_on_stop` | achieved, cancelled, paused, cancelled | Giữ, vẫn chạy theo giờ đã hẹn |

Mỗi dòng là một CI; kiểm chứng bằng `call_count` không đổi sau thời điểm `retry_at`.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: task bị stop khi đang chờ thử lại | dòng retry bị hủy, action không chạy |
| CI-2 | AC2: task bị cancel khi đang chờ thử lại | dòng retry bị hủy, action không chạy |
| CI-3 | AC3: task chuyển paused khi đang chờ thử lại | dòng retry bị hủy, action không chạy |
| CI-4 | AC4, AC5: reset hủy lượt chờ (cờ bật); mốc tắt `cancel_retry_on_stop` thì pause, stop, cancel, reset đều giữ lượt chờ và chạy lại | cờ bật: lượt chờ bị hủy; cờ tắt: lượt chờ vẫn còn, chạy lúc 10:05 và 10:20, cuối cùng `escalate_failed`, 3 lần gọi action |

#### TCOND-08-12 — Sửa mẫu thử lại khi đang có lượt chờ

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-059 | **Technique:** State Transition + BVA

**Mô tả điều kiện:** Đang có lượt chờ (`retry_at` = 10:01 từ mẫu `[1, 10]`). Sửa mẫu thành `[1, 30]` lúc 10:00:30: giờ của lượt chờ không đổi; lần lỗi tiếp theo dùng số phút thứ hai của mẫu mới (30).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: giờ lượt chờ không đổi sau khi sửa mẫu | retry_at vẫn 10:01 |
| CI-2 | AC2: lần thử kế tiếp theo mẫu mới | retry_at kế tiếp = 10:31 |

#### TCOND-08-13 — Kiểm tra mẫu thử lại khi lưu mốc

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-028 | **Technique:** EP + BVA

**Mô tả điều kiện:** Khi `retry` = true, `retry_pattern` phải là danh sách không rỗng tối đa 10 số nguyên dương; lỗi phải kèm ví dụ hợp lệ.

| Lớp | Mẫu đại diện | Kết quả |
|---|---|---|
| Rỗng | '', False, '[]' | Từ chối |
| Chứa 0 | '[0, 5]' | Từ chối |
| Âm | '[-1]' | Từ chối |
| Không nguyên | '[1.5]' | Từ chối |
| Không phải danh sách | 'abc' | Từ chối |
| 11 phần tử (biên trên + 1) | '[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]' | Từ chối |
| Hợp lệ điển hình | '[1, 10, 20, 60]' | Chấp nhận |
| 10 phần tử (biên trên) | '[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]' | Chấp nhận |
| `retry` = false, mẫu rác | 'abc' | Không kiểm tra (chấp nhận) |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: mẫu rỗng | bị từ chối kèm ví dụ hợp lệ |
| CI-2 | AC1: mẫu chứa 0 | bị từ chối kèm ví dụ hợp lệ |
| CI-3 | AC1: mẫu có số âm | bị từ chối kèm ví dụ hợp lệ |
| CI-4 | AC1: mẫu có số không nguyên | bị từ chối kèm ví dụ hợp lệ |
| CI-5 | AC1: mẫu không phải danh sách | bị từ chối kèm ví dụ hợp lệ |
| CI-6 | AC1 biên: 11 phần tử | bị từ chối kèm ví dụ hợp lệ |
| CI-7 | AC2: mẫu hợp lệ [1, 10, 20, 60] | lưu thành công |
| CI-8 | AC2 biên: 10 phần tử | lưu thành công |
| CI-9 | Statement: retry = false không kiểm tra mẫu | lưu thành công |

#### TCOND-08-14 — Server action của mốc phải cùng model với định nghĩa

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-038 | **Technique:** EP

**Mô tả điều kiện:** Hai lớp: server action cùng model với định nghĩa (hợp lệ) và khác model (không hợp lệ, thông báo nêu cả hai model).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: server action của res.users trên định nghĩa res.partner | bị từ chối, thông báo nêu 2 model |
| CI-2 | AC2: server action của res.partner | lưu thành công |

#### TCOND-08-15 — Không bắn bù mốc thêm sau

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-053 | **Technique:** Decision Table

**Mô tả điều kiện:** Mốc được thêm khi task đang ở 80% (đã trôi 3,2 giờ trên mục tiêu 4 giờ):

| Phần trăm mốc thêm | So với 80% | Kết quả |
|---|---|---|
| 75% | đã qua | Không bao giờ bắn cho task này |
| 90% | chưa tới | Bắn khi tới 90% (đã trôi 3,6 giờ = 12:36) |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: thêm mốc 75% khi task đang ở 80% | mốc 75% không bao giờ bắn |
| CI-2 | AC2: thêm mốc 90% khi task đang ở 80% | mốc 90% bắn khi tới 90% (12:36) |

#### TCOND-08-16 — Ngữ cảnh record khi gọi server action

**Feature:** FT-08 | **REQ-ID:** REQ-INT-008 | **Technique:** EP

**Mô tả điều kiện:** Server action nhận ngữ cảnh Odoo chuẩn: `active_model`, `active_id`, `active_ids` của record gốc. Hai lớp: một record due; hai record cùng due (mỗi action chỉ tác động record của mình).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: ghi chú xuất hiện trên đúng record gốc | ngữ cảnh đúng, ghi chú nằm trên record gốc |
| CI-2 | AC2: hai record cùng đến hạn, ghi chú không lẫn | mỗi chatter chỉ có ghi chú của chính record |

#### TCOND-08-17 — Công ty khi chạy server action

**Feature:** FT-08 | **REQ-ID:** REQ-INT-019 | **Technique:** Decision Table

**Mô tả điều kiện:** Record thuộc CO-B; bảng quyết định:

| Quyền công ty của U-CRON | `retry` của mốc | Kết quả |
|---|---|---|
| CO-A và CO-B | (bất kỳ) | Action chạy với công ty CO-B, ghi được vào record, event `escalate` |
| Chỉ CO-A | false | 1 event `escalate_failed` (lỗi quyền), không chạy lại |
| Chỉ CO-A | true | `escalate_retry` thay cho `escalate_failed` ở lần lỗi đầu |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: U-CRON có quyền A và B | action chạy với công ty B và ghi được record |
| CI-2 | AC2: U-CRON chỉ có CO-A, mốc không bật thử lại | 1 escalate_failed (lỗi quyền), không chạy lại |
| CI-3 | AC2 nhánh retry: U-CRON chỉ có CO-A, mốc bật thử lại | escalate_retry thay cho escalate_failed ở lần lỗi đầu |

#### TCOND-08-18 — Xử lý nền theo lô, báo tiến độ và nhường tài nguyên

**Feature:** FT-08 | **REQ-ID:** REQ-REL-002 | **Technique:** BVA + Error Guessing

**Mô tả điều kiện:** Xử lý nền xử lý từng task một: khóa đúng task, xử lý, lưu rồi báo `ir.cron._commit_progress(1, remaining)`; mỗi lần gọi dừng khi hết task đến hạn, khi chạm kích thước lô tối đa (`dwo_sla_core.batch_size`, mặc định 50, chỉ là trần mỗi lần gọi) hoặc khi thời gian còn lại bằng 0; phần còn lại xử lý ở lần gọi sau, không mất, không lặp. Biên: 120 task / lô 50 qua 3 lần gọi (50, 50, 20 lần báo tiến độ, số còn lại cuối mỗi lần gọi 70, 20, 0); thời gian còn lại = 0 sau task đầu thì chỉ 1 task được xử lý và `remaining` = 99; kích thước lô 0 và âm bị từ chối, 1 hợp lệ. Ngắt giữa chừng sau task đầu rồi chạy lại: task đó không xử lý lại. Task đang xử lý chậm không làm lần stop task khác phải chờ (AC5).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: 120 task, lô 50, ba lần gọi | 50, 50, 20 lần báo tiến độ; số còn lại cuối mỗi lần gọi 70, 20, 0 |
| CI-2 | AC2: dừng sau task thứ nhất rồi chạy lại | task thứ nhất không xử lý lại, các task còn lại được xử lý |
| CI-3 | AC4: thời gian còn lại bằng 0 sau task đầu | chỉ 1 task được xử lý, remaining = 99 |
| CI-4 | AC3: batch_size = 0 | bị từ chối, tham số không đổi |
| CI-5 | AC3: batch_size âm (-5) | bị từ chối, tham số không đổi |
| CI-6 | Biên hợp lệ: batch_size = 1 | lưu thành công |
| CI-7 | AC5: stop task khác trong lúc xử lý nền đang xử lý task chậm | lần lưu không phải chờ; task chưa bị khóa |

#### Traceability TG-08

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-FUNC-023 | TCOND-08-01 | CI-1 | TC-ESC-001 |
| REQ-FUNC-023 | TCOND-08-01 | CI-2 | TC-ESC-002 |
| REQ-FUNC-023 | TCOND-08-01 | CI-3 | TC-ESC-003 |
| REQ-FUNC-023 | TCOND-08-01 | CI-4 | TC-ESC-004 |
| REQ-FUNC-023 | TCOND-08-01 | CI-5 | TC-ESC-005 |
| REQ-FUNC-023 | TCOND-08-02 | CI-1 | TC-ESC-006 |
| REQ-FUNC-023 | TCOND-08-02 | CI-2 | TC-ESC-007 |
| REQ-FUNC-024 | TCOND-08-03 | CI-1 | TC-ESC-008 |
| REQ-FUNC-024 | TCOND-08-03 | CI-2 | TC-ESC-009 |
| REQ-FUNC-025 | TCOND-08-04 | CI-1 | TC-ESC-010 |
| REQ-FUNC-054 | TCOND-08-05 | CI-1 | TC-ESC-011 |
| REQ-FUNC-054 | TCOND-08-05 | CI-2 | TC-ESC-012 |
| REQ-FUNC-054 | TCOND-08-05 | CI-3 | TC-ESC-013 |
| REQ-FUNC-054 | TCOND-08-05 | CI-4 | TC-ESC-014 |
| REQ-FUNC-055 | TCOND-08-06 | CI-1 | TC-ESC-015 |
| REQ-FUNC-055 | TCOND-08-06 | CI-2 | TC-ESC-016 (đã gỡ D12) |
| REQ-FUNC-055 | TCOND-08-06 | CI-3 | TC-ESC-017 |
| REQ-FUNC-026 | TCOND-08-07 | CI-1 | TC-ESC-018 |
| REQ-FUNC-026 | TCOND-08-07 | CI-2 | TC-ESC-019 |
| REQ-FUNC-027 | TCOND-08-08 | CI-1 | TC-ESC-020 (đã gỡ D12) |
| REQ-FUNC-027 | TCOND-08-08 | CI-2 | TC-ESC-021 (đã gỡ D12) |
| REQ-FUNC-027 | TCOND-08-08 | CI-3 | TC-ESC-022 (đã gỡ D12) |
| REQ-FUNC-027 | TCOND-08-08 | CI-4 | TC-ESC-023 (đã gỡ D12) |
| REQ-FUNC-026 | TCOND-08-07 | CI-3 | TC-ESC-024 |
| REQ-FUNC-056 | TCOND-08-09 | CI-1 | TC-ESC-025 (đã gỡ D12) |
| REQ-FUNC-056 | TCOND-08-09 | CI-2 | TC-ESC-026 (đã gỡ D12) |
| REQ-FUNC-057 | TCOND-08-10 | CI-1 | TC-ESC-027 (đã gỡ D12) |
| REQ-FUNC-057 | TCOND-08-10 | CI-2 | TC-ESC-028 (đã gỡ D12) |
| REQ-FUNC-057 | TCOND-08-10 | CI-3 | TC-ESC-029 (đã gỡ D12) |
| REQ-FUNC-058 | TCOND-08-11 | CI-1 | TC-ESC-030 (đã gỡ D12) |
| REQ-FUNC-058 | TCOND-08-11 | CI-2 | TC-ESC-031 (đã gỡ D12) |
| REQ-FUNC-058 | TCOND-08-11 | CI-3 | TC-ESC-032 (đã gỡ D12) |
| REQ-FUNC-058 | TCOND-08-11 | CI-4 | TC-ESC-060 (đã gỡ D12) |
| REQ-FUNC-059 | TCOND-08-12 | CI-1 | TC-ESC-033 (đã gỡ D12) |
| REQ-FUNC-059 | TCOND-08-12 | CI-2 | TC-ESC-034 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-1 | TC-ESC-035 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-2 | TC-ESC-036 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-3 | TC-ESC-037 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-4 | TC-ESC-038 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-5 | TC-ESC-039 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-6 | TC-ESC-040 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-7 | TC-ESC-041 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-8 | TC-ESC-042 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-9 | TC-ESC-043 (đã gỡ D12) |
| REQ-FUNC-038 | TCOND-08-14 | CI-1 | TC-ESC-044 |
| REQ-FUNC-038 | TCOND-08-14 | CI-2 | TC-ESC-045 |
| REQ-FUNC-053 | TCOND-08-15 | CI-1 | TC-ESC-046 |
| REQ-FUNC-053 | TCOND-08-15 | CI-2 | TC-ESC-047 |
| REQ-INT-008 | TCOND-08-16 | CI-1 | TC-ESC-048 |
| REQ-INT-008 | TCOND-08-16 | CI-2 | TC-ESC-049 |
| REQ-INT-019 | TCOND-08-17 | CI-1 | TC-ESC-050 |
| REQ-INT-019 | TCOND-08-17 | CI-2 | TC-ESC-051 |
| REQ-INT-019 | TCOND-08-17 | CI-3 | TC-ESC-052 (đã gỡ D12) |
| REQ-REL-002 | TCOND-08-18 | CI-1 | TC-ESC-053 |
| REQ-REL-002 | TCOND-08-18 | CI-2 | TC-ESC-054 |
| REQ-REL-002 | TCOND-08-18 | CI-3 | TC-ESC-055 |
| REQ-REL-002 | TCOND-08-18 | CI-4 | TC-ESC-056 |
| REQ-REL-002 | TCOND-08-18 | CI-5 | TC-ESC-057 |
| REQ-REL-002 | TCOND-08-18 | CI-6 | TC-ESC-058 |
| REQ-REL-002 | TCOND-08-18 | CI-7 | TC-ESC-059 |

### FT-09 / TG-09 — Nhiều SLA song song

**Technique:** EP + Error Guessing — Phân lớp theo định nghĩa (khác nhau) và record (khác nhau) cho tính độc lập; tính duy nhất dưới giao dịch đồng thời là lỗi dễ sót nên dùng Error Guessing với hai cursor điều khiển thứ tự.

#### TCOND-09-01 — Tính độc lập giữa các task và tính duy nhất task hoạt động

**Feature:** FT-09 | **REQ-ID:** REQ-FUNC-014 | **Technique:** EP

**Mô tả điều kiện:** Lớp: (hai định nghĩa, một record) → 2 task độc lập; (một định nghĩa, hai record) → mỗi record một task; ràng buộc duy nhất: `paused` cũng là hoạt động (bị chặn), task đã `cancelled` thì cho phép task mới (REQ-FUNC-014).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | hai định nghĩa cùng khớp -> 2 task độc lập | Hai task độc lập, mỗi định nghĩa đúng một. |
| CI-2 | stop của D-RES không đổi task D-RESP | `D-RES` achieved; `D-RESP` không đổi. |
| CI-3 | cùng định nghĩa, hai record khác nhau | Mỗi record một task; kết quả của record này không ảnh hưởng record kia. |
| CI-4 | ràng buộc duy nhất: task paused vẫn là hoạt động | Chỉ mục duy nhất chặn task hoạt động thứ hai. |
| CI-5 | ràng buộc duy nhất chỉ áp cho task hoạt động: được có task mới sau khi cancelled | Ràng buộc chỉ giới hạn task hoạt động. |

#### TCOND-09-02 — Gắn trùng do hai giao dịch đồng thời

**Feature:** FT-09 | **REQ-ID:** REQ-FUNC-014 | **Technique:** Error Guessing

**Mô tả điều kiện:** Hai cursor `cr-A`, `cr-B`; `cr-B` giữ snapshot cũ (chưa thấy task), `cr-A` gắn và commit trước, rồi `cr-B` cố gắn (REQ-FUNC-014 AC2). Quan sát: số task hoạt động (CI-1), commit của cả hai thành công và không lỗi với người dùng (CI-2), event `error` của bên thua (CI-3).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | hai giao dịch cùng gắn -> chỉ 1 task hoạt động | Đúng 1 task hoạt động. |
| CI-2 | cả hai giao dịch commit thành công, người dùng không thấy lỗi | Hai COMMIT đều thành công; không lỗi nổi lên người dùng. |
| CI-3 | bên gặp xung đột có event error | Có đúng 1 event `error` từ bên thua xung đột. |

**Traceability TG-09**

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-FUNC-014 | TCOND-09-01 | CI-1 | TC-MUL-001 |
| REQ-FUNC-014 | TCOND-09-01 | CI-2 | TC-MUL-002 |
| REQ-FUNC-014 | TCOND-09-01 | CI-3 | TC-MUL-003 |
| REQ-FUNC-014 | TCOND-09-01 | CI-4 | TC-MUL-004 |
| REQ-FUNC-014 | TCOND-09-01 | CI-5 | TC-MUL-005 |
| REQ-FUNC-014 | TCOND-09-02 | CI-1 | TC-MUL-006 |
| REQ-FUNC-014 | TCOND-09-02 | CI-2 | TC-MUL-007 |
| REQ-FUNC-014 | TCOND-09-02 | CI-3 | TC-MUL-008 |

### FT-10 / TG-10 — Tính generic

**Technique:** EP — cùng một cấu hình định nghĩa phải áp dụng được cho các lớp model khác nhau (model của base, model demo); lớp dữ liệu không hợp lệ (thiếu model, thời lượng âm) tách riêng. BVA cho thời lượng mục tiêu tại 0.

#### TCOND-10-01 — Cùng cấu hình chạy trên hai model khác nhau

**Feature:** FT-10 | **REQ-ID:** REQ-FUNC-001 | **Technique:** EP

**Mô tả điều kiện:** Hai định nghĩa trỏ tới hai model khác nhau nhưng có cùng cấu trúc cấu hình (6 domain, mục tiêu, nguồn lịch, chế độ cancel/resume). Khi record của mỗi model thỏa điều kiện start thì mỗi record có đúng một task, không có nhánh code theo model.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Hai model (`res.partner`, `demo.ticket`) cùng cấu hình | Mỗi record có 1 task `in_progress`, `target_duration` = 4 |

#### TCOND-10-02 — Lưu định nghĩa với đầy đủ tùy chọn cấu hình

**Feature:** FT-10 | **REQ-ID:** REQ-FUNC-001 | **Technique:** EP

**Mô tả điều kiện:** Người cấu hình chọn được toàn bộ tùy chọn nêu ở Statement (model, mục tiêu, nguồn lịch, 6 điều kiện, cancel, resume, reset, field reset, retroactive, escalation, công ty, active, sequence) và giá trị được lưu đúng.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Lưu định nghĩa đặt đủ mọi tùy chọn | Đọc lại bản ghi: mọi giá trị khớp |

#### TCOND-10-03 — Từ chối cấu hình thiếu model hoặc thời lượng âm; biên 0

**Feature:** FT-10 | **REQ-ID:** REQ-FUNC-001 | **Technique:** BVA

**Mô tả điều kiện:** Bảng biên cho `duration`: âm (từ chối), 0 (chấp nhận, biên dưới hợp lệ). Thiếu model: từ chối.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Thiếu model | Lưu bị từ chối |
| CI-2 | `duration` = -1 (âm) | Lưu bị từ chối |
| CI-3 | `duration` = 0 (biên hợp lệ) | Lưu thành công |

**Traceability TG-10**

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-FUNC-001 | TCOND-10-01 | CI-1 | TC-GEN-001 |
| REQ-FUNC-001 | TCOND-10-02 | CI-1 | TC-GEN-002 |
| REQ-FUNC-001 | TCOND-10-03 | CI-1 | TC-GEN-003 |
| REQ-FUNC-001 | TCOND-10-03 | CI-2 | TC-GEN-004 |
| REQ-FUNC-001 | TCOND-10-03 | CI-3 | TC-GEN-005 |

### FT-11 / TG-11 — Đổi cấu hình khi đang chạy và archive

**Technique:** State Transition kết hợp Decision Table. Archive định nghĩa và stage của task tạo ra các chuyển trạng thái (định nghĩa active/archive; task in_progress/paused/kết thúc) với hành vi khác nhau; Decision Table cho tương quan giữa thay đổi cấu hình và task đã có hoặc attach mới.

#### TCOND-11-01 — Snapshot mục tiêu và lịch lúc attach

**Feature:** FT-11 | **REQ-ID:** REQ-FUNC-021 | **Technique:** Decision Table

**Mô tả điều kiện:** Task sao chép thời lượng mục tiêu (`duration` của định nghĩa vào `target_duration` của task) và lịch lúc attach; sửa định nghĩa chỉ ảnh hưởng task attach sau đó.

| Thời điểm sửa định nghĩa | Task đã có | Task attach sau khi sửa |
|---|---|---|
| Mục tiêu 4 -> 8 | giữ 4, `planned_end_time` không đổi | dùng 8 |
| Lịch L1 -> L2 | giữ L1 | dùng L2 |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Task đang chạy, mục tiêu định nghĩa 4 -> 8 | `target_duration` = 4, `planned_end_time` không đổi |
| CI-2 | Task đang chạy, lịch định nghĩa L1 -> L2 | Task vẫn dùng L1 |
| CI-3 | Record attach sau khi sửa | Task mới dùng giá trị mới (8 giờ, L2) |

#### TCOND-11-02 — Snapshot lịch lấy từ record và áp dụng bằng Apply Current Settings

**Feature:** FT-11 | **REQ-ID:** REQ-FUNC-052 | **Technique:** Decision Table

**Mô tả điều kiện:** Lịch lấy từ record được chốt lúc attach; đổi ở record gốc hoặc record liên kết chỉ có hiệu lực sau Apply Current Settings.

| Sự kiện | Task dùng lịch |
|---|---|
| Đổi lịch ở công ty mẹ | L1 (không đổi) |
| Sau đó SLA Manager bấm Apply Current Settings | L2 |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Đổi lịch ở công ty mẹ sau khi attach | Task vẫn dùng L1 |
| CI-2 | Bấm Apply Current Settings sau khi đổi | Task dùng L2 |

#### TCOND-11-03 — Hành động Apply Current Settings trên task SLA

**Feature:** FT-11 | **REQ-ID:** REQ-INT-005 | **Technique:** State Transition

**Mô tả điều kiện:** Apply Current Settings có hiệu lực theo stage của task, giữ nguyên thời gian đã trôi.

| Stage | Hành động Apply Current Settings | Kết quả |
|---|---|---|
| `in_progress` | khả dụng | áp lịch hoặc mục tiêu hiện hành, giữ thời gian đã trôi, xếp lại `planned_end_time` ngay |
| `paused` | khả dụng | áp mục tiêu mới; `planned_end_time` xếp lại khi resume |
| `achieved` | không khả dụng | từ chối |
| `breached` | không khả dụng | từ chối |
| `cancelled` | không khả dụng | từ chối |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Transition in_progress: lịch record đổi, đã trôi 3 giờ, mục tiêu 4 | đã trôi 3; `planned_end_time` = hiện tại + 1 giờ làm việc theo lịch mới |
| CI-2 | Transition in_progress: mục tiêu 4 -> 8 | mục tiêu task = 8; `planned_end_time` = hiện tại + 5 giờ |
| CI-3 | Negative: task achieved | Không có Apply Current Settings |
| CI-4 | Negative: task breached | Không có Apply Current Settings |
| CI-5 | Negative: task cancelled | Không có Apply Current Settings |
| CI-6 | Transition paused | Mục tiêu mới ngay; `planned_end_time` xếp lại khi resume |
| CI-7 | AC4 negative: SLA User không có nút Apply Current Settings | không có nút ở view; gọi trực tiếp bị từ chối |

#### TCOND-11-04 — Mốc escalation thêm sau không bắn bù

**Feature:** FT-11 | **REQ-ID:** REQ-FUNC-053 | **Technique:** Decision Table

**Mô tả điều kiện:** Mốc thêm khi task đã vượt mức phần trăm của mốc không bắn; mốc chưa tới mức bắn khi tới mức.

| Mức hiện tại của task | Mốc thêm | Hành vi |
|---|---|---|
| 80% | 75% (đã qua) | không bao giờ bắn |
| 80% | 90% (chưa tới) | bắn khi tới 90% |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Mốc 75% thêm khi task ở 80% | Không bao giờ bắn |
| CI-2 | Mốc 90% thêm khi task ở 80% | Bắn khi tới 90% |

#### TCOND-11-05 — Archive định nghĩa dừng gắn mới, bỏ archive hoạt động lại

**Feature:** FT-11 | **REQ-ID:** REQ-FUNC-033 | **Technique:** State Transition

**Mô tả điều kiện:** Định nghĩa archive không gắn task mới; bỏ archive thì hoạt động lại bình thường và không sinh task trùng.

| Trạng thái định nghĩa | Record mới thỏa start | Record đã có task, được sửa |
|---|---|---|
| archive | không có task | (xem TG-11 REQ-FUNC-060) |
| bỏ archive | gắn task | vẫn đúng 1 task đang hoạt động |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Archive: record mới thỏa start | Không có task |
| CI-2 | Archive rồi bỏ archive, sửa record đã có task | Đúng 1 task đang hoạt động |
| CI-3 | Bỏ archive: record mới thỏa start | Gắn task bình thường |

#### TCOND-11-06 — Task đang chạy tiếp tục sau khi archive định nghĩa

**Feature:** FT-11 | **REQ-ID:** REQ-FUNC-060 | **Technique:** State Transition

**Mô tả điều kiện:** Sau archive, task hoạt động vẫn nhận stop, cancel, pause, resume, breach, escalation, kể cả định nghĩa cuối của model.

| Sự kiện sau archive | Mong đợi |
|---|---|
| stop khớp (nhiều task, còn định nghĩa khác) | task kết thúc đúng |
| quá `planned_end_time`, xử lý nền | event `breach`, escalation bắn |
| record mới thỏa start | không có task |
| cancel khớp (chế độ `condition`) | `cancelled` |
| pause rồi resume khớp | `paused` rồi `in_progress` |
| stop khớp, định nghĩa cuối của model | task kết thúc |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Archive D có 30 task, stop một record | Task của record đó kết thúc đúng |
| CI-2 | Task quá `planned_end_time`, xử lý nền chạy | Có event `breach`, escalation bắn |
| CI-3 | Negative: record mới thỏa start | Không có task |
| CI-4 | Cancel khớp, chế độ `condition` | Task `cancelled` |
| CI-5 | Pause khớp rồi resume khớp | `paused` rồi `in_progress` |
| CI-6 | Edge: D là định nghĩa cuối của model, stop khớp | Task kết thúc, không kẹt `in_progress` |

#### TCOND-11-07 — Không xóa định nghĩa còn task tham chiếu

**Feature:** FT-11 | **REQ-ID:** REQ-FUNC-061 | **Technique:** EP

**Mô tả điều kiện:** Xóa bị chặn khi còn bất kỳ task nào tham chiếu, bất kể stage hoặc trạng thái archive.

| Task tham chiếu | Định nghĩa | Xóa |
|---|---|---|
| `achieved` | đang bật | từ chối, gợi ý archive |
| `in_progress` | đang bật | từ chối |
| `cancelled` | archive | từ chối |
| không có | đang bật | thành công |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Còn 1 task `achieved` | Từ chối, thông báo gợi ý archive |
| CI-2 | Chưa từng có task | Xóa thành công |
| CI-3 | Còn task `in_progress` (lớp stage hoạt động) | Từ chối |
| CI-4 | Đã archive, còn task `cancelled` | Từ chối |

#### Traceability — TG-11

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-FUNC-021 | TCOND-11-01 | CI-1 | TC-CHG-001 |
| REQ-FUNC-021 | TCOND-11-01 | CI-2 | TC-CHG-002 |
| REQ-FUNC-021 | TCOND-11-01 | CI-3 | TC-CHG-003 |
| REQ-FUNC-052 | TCOND-11-02 | CI-1 | TC-CHG-004 |
| REQ-FUNC-052 | TCOND-11-02 | CI-2 | TC-CHG-005 |
| REQ-INT-005 | TCOND-11-03 | CI-1 | TC-CHG-006 |
| REQ-INT-005 | TCOND-11-03 | CI-2 | TC-CHG-007 |
| REQ-INT-005 | TCOND-11-03 | CI-3 | TC-CHG-008 |
| REQ-INT-005 | TCOND-11-03 | CI-4 | TC-CHG-009 |
| REQ-INT-005 | TCOND-11-03 | CI-5 | TC-CHG-010 |
| REQ-INT-005 | TCOND-11-03 | CI-6 | TC-CHG-011 |
| REQ-INT-005 | TCOND-11-03 | CI-7 | TC-CHG-028 |
| REQ-FUNC-053 | TCOND-11-04 | CI-1 | TC-CHG-012 |
| REQ-FUNC-053 | TCOND-11-04 | CI-2 | TC-CHG-013 |
| REQ-FUNC-033 | TCOND-11-05 | CI-1 | TC-CHG-015 |
| REQ-FUNC-033 | TCOND-11-05 | CI-2 | TC-CHG-016 |
| REQ-FUNC-033 | TCOND-11-05 | CI-3 | TC-CHG-017 |
| REQ-FUNC-060 | TCOND-11-06 | CI-1 | TC-CHG-018 |
| REQ-FUNC-060 | TCOND-11-06 | CI-2 | TC-CHG-019 |
| REQ-FUNC-060 | TCOND-11-06 | CI-3 | TC-CHG-020 |
| REQ-FUNC-060 | TCOND-11-06 | CI-4 | TC-CHG-021 |
| REQ-FUNC-060 | TCOND-11-06 | CI-5 | TC-CHG-022 |
| REQ-FUNC-060 | TCOND-11-06 | CI-6 | TC-CHG-023 |
| REQ-FUNC-061 | TCOND-11-07 | CI-1 | TC-CHG-024 |
| REQ-FUNC-061 | TCOND-11-07 | CI-2 | TC-CHG-025 |
| REQ-FUNC-061 | TCOND-11-07 | CI-3 | TC-CHG-026 |
| REQ-FUNC-061 | TCOND-11-07 | CI-4 | TC-CHG-027 |

### FT-12 / TG-12 — Lỗi engine và đồng thời

**Technique:** **Error Guessing + EP + State Transition** — Error Guessing cho các nguồn lỗi engine (field bị gỡ, lịch rỗng, lỗi một record trong lô, vi phạm duy nhất khi đồng thời, xung đột tuần tự hóa); EP chia lớp theo đường kích hoạt (create/write) và theo người dùng (Manager, SLA User, không có quyền SLA); State Transition cho trạng thái event `error` (chưa xử lý ⇄ đã xử lý).

#### TCOND-12-01 — Lỗi engine không chặn lưu record

**Feature:** FT-12 | **REQ-ID:** REQ-FUNC-030 | **Technique:** Error Guessing + EP

**Mô tả điều kiện:** Khi đánh giá SLA của một record lỗi, hệ thống hoàn tác phần SLA của record đó (savepoint), ghi 1 event `error` (record, định nghĩa, thông báo), và vẫn lưu thay đổi của người dùng. Nguồn lỗi: (a) domain trỏ field đã bị gỡ; (b) lịch của định nghĩa mất toàn bộ giờ làm; (c) lỗi ở một record trong lô, record khác vẫn bình thường; (d) vi phạm tính duy nhất khi hai giao dịch cùng attach. Đường kích hoạt: `write` và `create`.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: domain trỏ field đã bị gỡ (đường write) | record lưu, 0 task, 1 event error |
| CI-2 | AC1 (đường create): domain lỗi khi tạo record | record được tạo, 0 task, 1 event error |
| CI-3 | AC2: calendar mất toàn bộ giờ làm sau khi định nghĩa đã lưu | 0 task, 1 event error, record vẫn lưu |
| CI-4 | AC3: lỗi ở R1 trong lô R1 và R2, R2 vẫn bình thường | R1 error, R2 attach |
| CI-5 | Vi phạm tính duy nhất khi hai giao dịch cùng attach | giao dịch thua ghi error, không tạo trùng, record vẫn lưu |

#### TCOND-12-02 — Event error có đủ ngữ cảnh

**Feature:** FT-12 | **REQ-ID:** REQ-OBS-001 | **Technique:** EP

**Mô tả điều kiện:** Mỗi event `error` chứa: tên model, id record, định nghĩa liên quan (tên), thông báo lỗi không rỗng. Hai lớp nguồn lỗi đại diện: domain lỗi, lịch rỗng.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: lỗi do domain trỏ field bị gỡ | event error có model, id, định nghĩa, thông báo |
| CI-2 | AC1: lỗi do calendar không xếp được hạn | event error có model, id, định nghĩa, thông báo |

#### TCOND-12-03 — Ghi log máy chủ cho lỗi engine

**Feature:** FT-12 | **REQ-ID:** REQ-OBS-002 | **Technique:** EP

**Mô tả điều kiện:** Mỗi lỗi engine tạo đúng 1 dòng log mức ERROR chứa tên model, id record và tên định nghĩa.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: lỗi engine ghi 1 dòng ERROR có model, id, tên định nghĩa | 1 dòng log ERROR đủ 3 thông tin |

#### TCOND-12-04 — Không ghi dữ liệu nhạy cảm vào event và log

**Feature:** FT-12 | **REQ-ID:** REQ-OBS-003 | **Technique:** Error Guessing + Inspection

**Mô tả điều kiện:** Event và log chỉ chứa định danh (model, id), không chứa giá trị field của record gốc. Kiểm chứng bằng: (a) test tự động tìm chuỗi 'SECRET-123' trong mọi cột chuỗi của event và log; (b) Inspection mã nguồn đường ghi lỗi; (c) trường hợp thông báo lỗi gốc có chứa giá trị field.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: record có SECRET-123 gây lỗi engine | SECRET-123 không xuất hiện trong event và log |
| CI-2 | AC1 (Inspection): mã nguồn đường ghi lỗi chỉ dùng định danh | checklist đạt |
| CI-3 | Thông báo lỗi gốc chứa giá trị field | giá trị field không lọt vào note và log |

#### TCOND-12-05 — Trạng thái xử lý của event lỗi

**Feature:** FT-12 | **REQ-ID:** REQ-FUNC-040 | **Technique:** State Transition

**Mô tả điều kiện:** Bảng chuyển trạng thái của event `error`:

| Trạng thái hiện tại | Sự kiện | Trạng thái sau | Ghi chú |
|---|---|---|---|
| (mới tạo) | engine ghi lỗi | chưa xử lý (`is_resolved` = false) | |
| chưa xử lý | SLA Manager đánh dấu | đã xử lý | số cảnh báo giảm 1 |
| chưa xử lý | đánh giá lại record liên quan thành công | đã xử lý | |
| chưa xử lý | đánh giá lại vẫn lỗi | chưa xử lý | sinh thêm event `error` mới |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: event error mới ở trạng thái chưa xử lý | is_resolved = false |
| CI-2 | AC2: SLA Manager đánh dấu đã xử lý | đổi trạng thái, số cảnh báo giảm 1 |
| CI-3 | AC3: đánh giá lại record liên quan thành công | event chuyển đã xử lý |
| CI-4 | AC4: đánh giá lại vẫn lỗi | event cũ vẫn chưa xử lý, có event error mới |

#### TCOND-12-06 — Đánh giá lại hàng loạt từ danh sách event lỗi

**Feature:** FT-12 | **REQ-ID:** REQ-FUNC-031 | **Technique:** EP + Decision Table

**Mô tả điều kiện:** Hành động 'Đánh giá lại' trên event đã chọn:

| Lựa chọn / người dùng | Kết quả |
|---|---|
| 3 event `error`, nguyên nhân đã sửa, U-MGR | 3 record được đánh giá, task thiếu được tạo, 3 event đã xử lý |
| Record có task `achieved` | Task không đổi |
| Có event không phải `error` | Từ chối hoặc bỏ qua event đó kèm thông báo |
| `group_sla_user` | Không có/không thực hiện được |
| Không bật retroactive | `start_time` = thời điểm hiện tại lúc đánh giá lại |
| Bật retroactive | `start_time` lấy từ field ngày giờ của record |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: chọn 3 event error sau khi sửa nguyên nhân | 3 record đánh giá, 3 task, 3 event đã xử lý |
| CI-2 | AC2: record có task achieved không đổi | task achieved giữ nguyên |
| CI-3 | AC3: chọn event không phải error | bị từ chối hoặc bỏ qua kèm thông báo |
| CI-4 | AC4: người dùng group_sla_user | không thực hiện được |
| CI-5 | Thời điểm hiện tại, không retroactive | start_time = thời điểm đánh giá lại |
| CI-6 | Retroactive start bật: lấy mốc từ field của record | start_time = giá trị field |

#### TCOND-12-07 — Cảnh báo số event lỗi chưa xử lý

**Feature:** FT-12 | **REQ-ID:** REQ-INT-022 | **Technique:** EP

**Mô tả điều kiện:** Số cảnh báo = số event `error` có `is_resolved` = false mà người dùng được phép thấy. Lớp: SLA Manager (thấy số đúng), người dùng không thuộc nhóm SLA (không thấy). Phần hiển thị trên giao diện (nhãn số bên mục menu) kiểm bằng Demonstration.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: 3 event chưa xử lý, SLA Manager thấy số 3 | số = 3 |
| CI-2 | AC2: đánh dấu 1 event đã xử lý | số = 2 |
| CI-3 | AC3: người dùng không thuộc nhóm SLA | không thấy số này |
| CI-4 | Demonstration: nhãn số trên menu và danh sách event | nhãn số đúng, ẩn với người không có quyền |

#### TCOND-12-08 — An toàn khi đồng thời giữa người dùng và xử lý nền

**Feature:** FT-12 | **REQ-ID:** REQ-REL-001 | **Technique:** Error Guessing + EP

**Mô tả điều kiện:** Hai giao dịch REPEATABLE READ (cursor C1 = xử lý nền, C2 = người dùng stop) tác động cùng task T. Hai thứ tự điều khiển bằng mã test: (A) C2 đọc snapshot trước, C1 commit trước → C2 gặp lỗi tuần tự hóa và được thử lại; (B) C2 commit trước, C1 đã có snapshot cũ → lô của C1 bị bỏ và chạy lại sau. Kết quả cuối phải nhất quán, không event trùng. Ngoài ra: action chậm của xử lý nền không làm lần lưu record khác chờ khóa quá 5 giây (p95 qua 20 lần).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1 thứ tự A: xử lý nền commit trước, user stop gặp xung đột và thử lại | 1 trạng thái cuối nhất quán, không event trùng |
| CI-2 | AC1 thứ tự B: user stop commit trước, lô xử lý nền bị bỏ | không escalate, 1 complete |
| CI-3 | AC2: action chậm không làm user chờ khóa quá 5 giây (p95/20) | p95 ≤ 5 giây |

#### TCOND-12-09 — Lô xung đột bị bỏ và chạy lại ở lần sau

**Feature:** FT-12 | **REQ-ID:** REQ-REL-002 | **Technique:** Error Guessing

**Mô tả điều kiện:** Giao dịch của lô bị xung đột tuần tự hóa thì bỏ cả lô (không lưu kết quả dở dang) và xử lý ở lần chạy kế tiếp mà không bắn lặp.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Lô chứa task bị user stop đồng thời | lô bị bỏ, lần sau xử lý đúng |

#### Traceability TG-12

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-FUNC-030 | TCOND-12-01 | CI-1 | TC-ERR-001 |
| REQ-FUNC-030 | TCOND-12-01 | CI-2 | TC-ERR-002 |
| REQ-FUNC-030 | TCOND-12-01 | CI-3 | TC-ERR-003 |
| REQ-FUNC-030 | TCOND-12-01 | CI-4 | TC-ERR-004 |
| REQ-FUNC-030 | TCOND-12-01 | CI-5 | TC-ERR-005 |
| REQ-REL-001 | TCOND-12-01 | CI-5 | TC-ERR-005 |
| REQ-OBS-001 | TCOND-12-02 | CI-1 | TC-ERR-006 |
| REQ-OBS-001 | TCOND-12-02 | CI-2 | TC-ERR-007 |
| REQ-OBS-002 | TCOND-12-03 | CI-1 | TC-ERR-008 |
| REQ-OBS-003 | TCOND-12-04 | CI-1 | TC-ERR-009 |
| REQ-OBS-003 | TCOND-12-04 | CI-2 | TC-ERR-010 |
| REQ-OBS-003 | TCOND-12-04 | CI-3 | TC-ERR-011 |
| REQ-FUNC-040 | TCOND-12-05 | CI-1 | TC-ERR-012 |
| REQ-FUNC-040 | TCOND-12-05 | CI-2 | TC-ERR-013 |
| REQ-FUNC-040 | TCOND-12-05 | CI-3 | TC-ERR-014 |
| REQ-FUNC-040 | TCOND-12-05 | CI-4 | TC-ERR-015 |
| REQ-FUNC-031 | TCOND-12-06 | CI-1 | TC-ERR-016 |
| REQ-FUNC-031 | TCOND-12-06 | CI-2 | TC-ERR-017 |
| REQ-FUNC-031 | TCOND-12-06 | CI-3 | TC-ERR-018 |
| REQ-FUNC-031 | TCOND-12-06 | CI-4 | TC-ERR-019 |
| REQ-FUNC-031 | TCOND-12-06 | CI-5 | TC-ERR-020 |
| REQ-FUNC-031 | TCOND-12-06 | CI-6 | TC-ERR-021 |
| REQ-INT-022 | TCOND-12-07 | CI-1 | TC-ERR-022 |
| REQ-INT-022 | TCOND-12-07 | CI-2 | TC-ERR-023 |
| REQ-INT-022 | TCOND-12-07 | CI-3 | TC-ERR-024 |
| REQ-INT-022 | TCOND-12-07 | CI-4 | TC-ERR-025 |
| REQ-REL-001 | TCOND-12-08 | CI-1 | TC-ERR-026 |
| REQ-REL-001 | TCOND-12-08 | CI-2 | TC-ERR-027 |
| REQ-REL-001 | TCOND-12-08 | CI-3 | TC-ERR-028 |
| REQ-REL-002 | TCOND-12-09 | CI-1 | TC-ERR-029 |

### FT-13 / TG-13 — Field compute có lưu

**Technique:** **EP + Decision Table + Error Guessing** — EP chia lớp theo loại field điều kiện (compute có lưu, compute không lưu, quan hệ xa) và theo việc kết quả điều kiện có đổi hay không; Decision Table cho bảng ưu tiên khi đánh giá lại thủ công; Error Guessing cho nhiều lần ghi trong một giao dịch và recompute qua quan hệ con.

#### TCOND-13-01 — Đánh giá khi field compute có lưu đổi giá trị

**Feature:** FT-13 | **REQ-ID:** REQ-FUNC-005 | **Technique:** EP + Error Guessing

**Mô tả điều kiện:** Khi điều kiện dùng field compute `store=True` và giá trị đổi do tính lại (không qua ghi trực tiếp field đó), engine đánh giá record như một lần sửa. Lớp:

| Tình huống | Kết quả |
|---|---|
| Giá trị đổi và làm kết quả điều kiện đổi | Chuyển trạng thái đúng 1 lần (1 event) |
| 3 lần ghi trong một giao dịch | Số event = số chuyển trạng thái thực, không attach/cancel dư |
| Giá trị đổi nhưng kết quả điều kiện không đổi | Không event mới |
| Recompute do thay đổi ở record con (phụ thuộc qua quan hệ) | Vẫn đánh giá |
| Field compute không nằm trong domain của định nghĩa nào | Không đánh giá, không lỗi |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: stage đổi sang resolved làm is_resolved đổi → stop | task kết thúc đúng 1 lần (1 event complete) |
| CI-2 | AC2: 3 lần ghi trong một giao dịch | số event = số chuyển trạng thái thực |
| CI-3 | AC3: field compute đổi nhưng kết quả điều kiện không đổi | không có event mới |
| CI-4 | Recompute qua quan hệ con làm field cha đổi | task của record cha kết thúc 1 lần |
| CI-5 | Field compute có lưu không nằm trong domain của định nghĩa nào | không đánh giá, không lỗi |

#### TCOND-13-02 — Giới hạn: field không lưu và điều kiện qua quan hệ

**Feature:** FT-13 | **REQ-ID:** REQ-FUNC-042 | **Technique:** EP + Inspection

**Mô tả điều kiện:** Với field compute không lưu và điều kiện đi qua quan hệ khi chỉ record liên quan đổi, hệ thống CÓ THỂ không tự đánh giá (không bị yêu cầu), nhưng không được ghi event `error`; 'Đánh giá lại' phải cho kết quả đúng với dữ liệu hiện tại; help text trên form định nghĩa phải nêu giới hạn.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: điều kiện qua quan hệ, partner đổi country sang VN rồi Đánh giá lại | task được gắn |
| CI-2 | AC2: field compute không lưu, field gốc đổi, chưa đánh giá lại | không có event error |
| CI-3 | Đánh giá lại cho kết quả đúng với dữ liệu hiện tại (field không lưu) | task được gắn theo dữ liệu hiện tại |
| CI-4 | AC3 (Inspection): help text nêu giới hạn | có câu nêu giới hạn ở các điều kiện |

#### TCOND-13-03 — Đánh giá lại thủ công

**Feature:** FT-13 | **REQ-ID:** REQ-FUNC-032 | **Technique:** Decision Table + EP

**Mô tả điều kiện:** SLA Manager đánh giá lại một lô record bằng cùng quy tắc như khi record thay đổi (ưu tiên stop > cancel > reset > pause > resume), không kích hoạt reset theo field (`changed` rỗng), dùng thời điểm hiện tại. Bảng:

| Tình huống | Kết quả |
|---|---|
| Start khớp sau khi dữ liệu liên quan đổi, chưa có task | Gắn task |
| Chạy lần hai liền sau | Không đổi gì (REQ-FUNC-015) |
| `group_sla_user` | Không thực hiện được |
| Có field theo dõi reset đã khác giá trị cũ nhưng `changed` rỗng | Không reset |
| Không bật retroactive | `start_time` = now lúc đánh giá lại |
| Khớp đồng thời stop và cancel | stop thắng (task `achieved`, không `cancel`) |
| Lô 2 record, 1 khớp | Chỉ record khớp có task |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | AC1: partner đổi country sang VN rồi đánh giá lại (một record) | task được gắn |
| CI-2 | Lô 2 record, chỉ 1 record khớp | chỉ record khớp có task |
| CI-3 | AC2: đánh giá lại hai lần liên tiếp | lần hai không đổi gì |
| CI-4 | AC3: người dùng group_sla_user | không thực hiện được |
| CI-5 | Statement: không kích hoạt reset theo field | không có reset, task giữ nguyên |
| CI-6 | Statement: dùng thời điểm hiện tại, không retroactive | start_time = now |
| CI-7 | Statement: áp dụng cùng quy tắc ưu tiên (stop thắng cancel) | task achieved, không cancel |

#### Traceability TG-13

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-FUNC-005 | TCOND-13-01 | CI-1 | TC-CMP-001 |
| REQ-FUNC-005 | TCOND-13-01 | CI-2 | TC-CMP-002 |
| REQ-FUNC-005 | TCOND-13-01 | CI-3 | TC-CMP-003 |
| REQ-FUNC-005 | TCOND-13-01 | CI-4 | TC-CMP-004 |
| REQ-FUNC-005 | TCOND-13-01 | CI-5 | TC-CMP-005 |
| REQ-FUNC-042 | TCOND-13-02 | CI-1 | TC-CMP-006 |
| REQ-FUNC-042 | TCOND-13-02 | CI-2 | TC-CMP-007 |
| REQ-FUNC-042 | TCOND-13-02 | CI-3 | TC-CMP-008 |
| REQ-FUNC-042 | TCOND-13-02 | CI-4 | TC-CMP-009 |
| REQ-FUNC-032 | TCOND-13-03 | CI-1 | TC-CMP-010 |
| REQ-FUNC-032 | TCOND-13-03 | CI-2 | TC-CMP-011 |
| REQ-FUNC-032 | TCOND-13-03 | CI-3 | TC-CMP-012 |
| REQ-FUNC-032 | TCOND-13-03 | CI-4 | TC-CMP-013 |
| REQ-FUNC-032 | TCOND-13-03 | CI-5 | TC-CMP-014 |
| REQ-FUNC-032 | TCOND-13-03 | CI-6 | TC-CMP-015 |
| REQ-FUNC-032 | TCOND-13-03 | CI-7 | TC-CMP-016 |

### FT-14 / TG-14 — Hạ tầng: cài, nâng cấp, gỡ, dọn dẹp, tham số

**Technique:** EP — các lớp model (hợp lệ, transient, abstract, `_auto=False`, tiền tố `sla.`/`ir.`/`mail.`); BVA — ngưỡng ngày lưu nhật ký và tham số 0/âm; Error Guessing — cài/gỡ trên database có dữ liệu thật, task mồ côi lẫn task còn record.

#### TCOND-14-01 — Từ chối model không được phép

**Feature:** FT-14 | **REQ-ID:** REQ-FUNC-002 | **Technique:** EP

**Mô tả điều kiện:** Lớp model bị cấm: tên bắt đầu `ir.`, `sla.`, `mail.`; model transient; model abstract; model `_auto = False`. Mọi lớp phải bị từ chối khi lưu định nghĩa, kèm thông báo nêu lý do.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | model tiền tố `ir.` (`ir.attachment`) | Lưu bị từ chối với thông báo nêu lý do |
| CI-2 | model tiền tố `sla.` (`sla.task`) | Lưu bị từ chối với thông báo nêu lý do |
| CI-3 | model transient (`base.language.install`) | Lưu bị từ chối với thông báo nêu lý do |
| CI-4 | model abstract (`image.mixin`) | Lưu bị từ chối với thông báo nêu lý do |
| CI-5 | model `_auto = False` (model chỉ dành cho test `x_test.sqlview` khai báo `_auto = False`) | Lưu bị từ chối với thông báo nêu lý do |
| CI-6 | model tiền tố `mail.` (`mail.message`) | Lưu bị từ chối với thông báo nêu lý do |

#### TCOND-14-02 — Chấp nhận model hợp lệ

**Feature:** FT-14 | **REQ-ID:** REQ-FUNC-002 | **Technique:** EP

**Mô tả điều kiện:** Model thường có bảng (`res.partner`, `demo.ticket`) lưu được.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | `res.partner` | Lưu thành công |
| CI-2 | `demo.ticket` (model ngoài base) | Lưu thành công |

#### TCOND-14-03 — Bỏ qua model bị cấm khi quan sát thay đổi

**Feature:** FT-14 | **REQ-ID:** REQ-FUNC-002 | **Technique:** Error Guessing

**Mô tả điều kiện:** Nếu dữ liệu đã có định nghĩa trỏ tới model bị cấm (lọt qua đường tắt, ví dụ SQL), hook vẫn bỏ qua model đó khi tạo/sửa record.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Định nghĩa trỏ `ir.attachment` lọt qua bằng SQL | Hook bỏ qua, không task, không event |

#### TCOND-14-04 — Dọn task mồ côi

**Feature:** FT-14 | **REQ-ID:** REQ-FUNC-034 | **Technique:** EP

**Mô tả điều kiện:** Lớp: record gốc đã xóa (task và phụ thuộc bị dọn), record còn tồn tại (giữ nguyên), lô hỗn hợp (chỉ dọn phần mồ côi).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Record bị xóa, có 2 task và 1 lượt thử lại | 2 task, lượt thử lại và event bị xóa |
| CI-2 | Record còn tồn tại | Task giữ nguyên |
| CI-3 | Lô hỗn hợp (1 record xóa, 1 record còn) | Chỉ dọn task của record đã xóa |

#### TCOND-14-05 — Dọn nhật ký cũ theo ngưỡng ngày

**Feature:** FT-14 | **REQ-ID:** REQ-FUNC-035 | **Technique:** BVA

**Mô tả điều kiện:** Ngưỡng N ngày. Biên: tuổi < N giữ, tuổi = N giữ, tuổi = N + 1 phút xóa, tuổi >> N xóa. Ngưỡng đọc từ tham số (REQ-INT-010).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Event 100 ngày (A) và 10 ngày (B), ngưỡng 90 | A bị xóa, B còn |
| CI-2 | Event đúng 90 ngày (biên) | Không bị xóa |
| CI-3 | Event 90 ngày + 1 phút (ngay trên biên) | Bị xóa |
| CI-4 | Ngưỡng đổi thành 30, event 40 ngày | Bị xóa theo ngưỡng mới |

#### TCOND-14-06 — Tham số số ngày lưu nhật ký

**Feature:** FT-14 | **REQ-ID:** REQ-INT-010 | **Technique:** BVA

**Mô tả điều kiện:** Bảng biên: mặc định 365; hợp lệ >= 1 (biên 1); không hợp lệ 0 và âm; quyền sửa chỉ SLA Manager.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Hệ thống mới cài | Tham số tồn tại, = 365 |
| CI-2 | Giá trị 0 (biên không hợp lệ) | Lưu bị từ chối |
| CI-3 | Giá trị -1 (âm) | Lưu bị từ chối |
| CI-4 | Giá trị 1 (biên hợp lệ thấp nhất) | Lưu thành công, tham số = 1 |
| CI-5 | SLA Manager chỉnh 180 | Lưu thành công, tham số = 180 |
| CI-6 | SLA User (không phải Manager) | Không sửa được |

#### TCOND-14-07 — Cài, nâng cấp, gỡ trên database có dữ liệu

**Feature:** FT-14 | **REQ-ID:** REQ-INST-001 | **Technique:** Error Guessing

**Mô tả điều kiện:** Database chứa `res.partner` và `sh.helpdesk.ticket`. Vòng đời: cài, nâng cấp, gỡ. Mỗi bước không lỗi và dữ liệu gốc nguyên vẹn; sau gỡ không còn hành vi SLA.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Cài mới | Exit 0, dữ liệu nguyên vẹn |
| CI-2 | Nâng cấp | Exit 0, dữ liệu nguyên vẹn |
| CI-3 | Gỡ | Exit 0, dữ liệu gốc nguyên vẹn |
| CI-4 | Sau gỡ | Không còn hành vi SLA |
| CI-5 | Gỡ module sở hữu model gắn SLA | CASCADE xóa định nghĩa, task, event; dữ liệu SLA model khác nguyên vẹn |

#### TCOND-14-08 — Không thêm cột vào bảng model gốc

**Feature:** FT-14 | **REQ-ID:** REQ-INST-003 | **Technique:** EP

**Mô tả điều kiện:** So sánh danh sách cột (tên, kiểu, nullable) của bảng model gốc trước và sau khi cài; và registry field của model.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Bảng `res_partner` | Danh sách cột trước = sau |
| CI-2 | Bảng `sh_helpdesk_ticket` | Danh sách cột trước = sau |
| CI-3 | Mọi model có định nghĩa SLA (kể cả sau khi tạo định nghĩa) | Không có cột mới sau khi dùng |

#### TCOND-14-09 — Gỡ module demo dọn dữ liệu của nó

**Feature:** FT-14 | **REQ-ID:** REQ-INST-004 | **Technique:** EP

**Mô tả điều kiện:** Task `demo.ticket` bị xóa, định nghĩa mẫu bị xóa không bị chặn bởi REQ-FUNC-061; dữ liệu SLA của model khác giữ nguyên.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Task `demo.ticket` khi gỡ demo | Task `demo.ticket` = 0, không lỗi |
| CI-2 | Định nghĩa mẫu khi gỡ demo | 4 định nghĩa mẫu bị xóa |
| CI-3 | Dữ liệu SLA của model khác khi gỡ demo | Task `res.partner` giữ nguyên |

#### TCOND-14-10 — Môi trường chạy

**Feature:** FT-14 | **REQ-ID:** REQ-PORT-001 | **Technique:** EP

**Mô tả điều kiện:** Cài trên image dựng từ Dockerfile của repo không cần cài thêm gói; module chỉ import thư viện chuẩn và `odoo`.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Image từ Dockerfile của repo | Cài thành công, `pip freeze` không đổi |
| CI-2 | Import trong mã nguồn | Chỉ stdlib + `odoo` |

**Traceability TG-14**

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-FUNC-002 | TCOND-14-01 | CI-1 | TC-INF-001 |
| REQ-FUNC-002 | TCOND-14-01 | CI-2 | TC-INF-002 |
| REQ-FUNC-002 | TCOND-14-01 | CI-3 | TC-INF-003 |
| REQ-FUNC-002 | TCOND-14-01 | CI-4 | TC-INF-004 |
| REQ-FUNC-002 | TCOND-14-01 | CI-5 | TC-INF-005 |
| REQ-FUNC-002 | TCOND-14-01 | CI-6 | TC-INF-006 |
| REQ-FUNC-002 | TCOND-14-02 | CI-1 | TC-INF-007 |
| REQ-FUNC-002 | TCOND-14-02 | CI-2 | TC-INF-008 |
| REQ-FUNC-002 | TCOND-14-03 | CI-1 | TC-INF-009 |
| REQ-FUNC-034 | TCOND-14-04 | CI-1 | TC-INF-010 |
| REQ-FUNC-034 | TCOND-14-04 | CI-2 | TC-INF-011 |
| REQ-FUNC-034 | TCOND-14-04 | CI-3 | TC-INF-012 |
| REQ-FUNC-035 | TCOND-14-05 | CI-1 | TC-INF-013 |
| REQ-FUNC-035 | TCOND-14-05 | CI-2 | TC-INF-014 |
| REQ-FUNC-035 | TCOND-14-05 | CI-3 | TC-INF-015 |
| REQ-FUNC-035 | TCOND-14-05 | CI-4 | TC-INF-016 |
| REQ-INT-010 | TCOND-14-06 | CI-1 | TC-INF-017 |
| REQ-INT-010 | TCOND-14-06 | CI-2 | TC-INF-018 |
| REQ-INT-010 | TCOND-14-06 | CI-3 | TC-INF-019 |
| REQ-INT-010 | TCOND-14-06 | CI-4 | TC-INF-020 |
| REQ-INT-010 | TCOND-14-06 | CI-5 | TC-INF-021 |
| REQ-INT-010 | TCOND-14-06 | CI-6 | TC-INF-022 |
| REQ-INST-001 | TCOND-14-07 | CI-1 | TC-INF-023 |
| REQ-INST-001 | TCOND-14-07 | CI-2 | TC-INF-024 |
| REQ-INST-001 | TCOND-14-07 | CI-3 | TC-INF-025 |
| REQ-INST-001 | TCOND-14-07 | CI-4 | TC-INF-026 |
| REQ-INST-001 | TCOND-14-07 | CI-5 | TC-INF-035 |
| REQ-INST-003 | TCOND-14-08 | CI-1 | TC-INF-027 |
| REQ-INST-003 | TCOND-14-08 | CI-2 | TC-INF-028 |
| REQ-INST-003 | TCOND-14-08 | CI-3 | TC-INF-029 |
| REQ-INST-004 | TCOND-14-09 | CI-1 | TC-INF-030 |
| REQ-INST-004 | TCOND-14-09 | CI-2 | TC-INF-031 |
| REQ-INST-004 | TCOND-14-09 | CI-3 | TC-INF-032 |
| REQ-PORT-001 | TCOND-14-10 | CI-1 | TC-INF-033 |
| REQ-PORT-001 | TCOND-14-10 | CI-2 | TC-INF-034 |

### FT-15 / TG-15 — Nguồn lịch

**Technique:** Decision Table kết hợp EP. Kết quả lịch của task là hàm của nguồn lịch (`none`/`definition`/`record`), tính hợp lệ của đường dẫn, tính dùng được của calendar và của lịch công ty; mỗi tổ hợp có ý nghĩa là một quy tắc. EP phân lớp calendar (fully_fixed có giờ, flexible, không giờ làm).

#### TCOND-15-01 — Từ chối lưu calendar không có giờ làm khi nguồn là definition

**Feature:** FT-15 | **REQ-ID:** REQ-FUNC-039 | **Technique:** EP

**Mô tả điều kiện:** Khi nguồn lịch là `definition`, calendar không có giờ làm trong tuần bị từ chối lúc lưu; calendar có giờ làm được chấp nhận.

| Calendar chọn | Có giờ làm trong tuần | Kết quả lưu |
|---|---|---|
| FX-CAL-EMPTY | Không | Bị từ chối |
| FX-CAL-VN | Có (T2-T6) | Thành công |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Calendar không có dòng giờ làm | Lưu bị từ chối |
| CI-2 | Calendar fully_fixed có giờ T2-T6 (happy path) | Lưu thành công |

#### TCOND-15-02 — Chỉ chấp nhận calendar fully_fixed

**Feature:** FT-15 | **REQ-ID:** REQ-INT-009 | **Technique:** Decision Table

**Mô tả điều kiện:** Calendar không phải `fully_fixed` bị từ chối khi chọn cố định, và bị coi là không dùng được khi lấy từ record.

| Nguồn | Calendar flexible | Kết quả |
|---|---|---|
| `definition` | chọn cố định trên định nghĩa | Lưu bị từ chối |
| `record` | trả về từ đường dẫn lúc attach | Dùng lịch dự phòng, event `attach` ghi lý do |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Nguồn definition chọn calendar flexible | Lưu bị từ chối |
| CI-2 | Nguồn record trả calendar flexible | Dùng lịch dự phòng; event `attach` ghi lý do |

#### TCOND-15-03 — Ba nguồn lịch và kiểm tra đường dẫn khi lưu

**Feature:** FT-15 | **REQ-ID:** REQ-FUNC-019 | **Technique:** Decision Table

**Mô tả điều kiện:** Nguồn `none` cho 24x7; `definition` cho calendar cố định; `record` đi theo đường dẫn Many2one nhiều bước. Khi lưu, từng bước phải là Many2one trên model của bước trước và bước cuối phải trỏ tới `resource.calendar`.

| Đường dẫn | Bước giữa | Bước cuối | Kết quả lưu |
|---|---|---|---|
| `parent_id.x_calendar_id` | Many2one | `resource.calendar` | Hợp lệ |
| `x_calendar_id` | (không có) | `resource.calendar` | Hợp lệ (biên: 1 bước) |
| `child_ids.x_calendar_id` | One2many | `resource.calendar` | Từ chối |
| `parent_id.company_id` | Many2one | `res.company` | Từ chối |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Đường dẫn hợp lệ 2 bước, các bước đều có giá trị | Task dùng calendar tại cuối đường dẫn |
| CI-2 | Bước giữa không phải Many2one (One2many) | Lưu bị từ chối |
| CI-3 | Bước cuối không phải `resource.calendar` | Lưu bị từ chối |
| CI-4 | Nguồn `none` | Task không có lịch, chạy 24x7 |
| CI-5 | Biên: đường dẫn 1 bước (field trên chính record) | Task dùng calendar của field |

#### TCOND-15-04 — Lịch dự phòng cho nguồn record

**Feature:** FT-15 | **REQ-ID:** REQ-FUNC-020 | **Technique:** Decision Table

**Mô tả điều kiện:** Với nguồn `record`, không lấy được lịch thì dùng lịch mặc định của công ty của record (record không có công ty thì dùng công ty hiện tại); nếu lịch này cũng không dùng được thì 24x7. Lý do ghi vào `note` event `attach`.

| Nguyên nhân không lấy được lịch | Công ty record | Lịch công ty dùng được | Lịch task | Ghi chú event |
|---|---|---|---|---|
| Bước trong đường dẫn trống | có | có | lịch công ty record | nêu bước trống |
| Calendar cuối trống | có | có | lịch công ty record | nêu lý do |
| Calendar cuối không có giờ làm | có | có | lịch công ty record | nêu lý do |
| Bước trống | có | không | 24x7 | nêu lý do |
| Bước trống | không (dùng công ty hiện tại) | có | lịch công ty hiện tại | nêu lý do |
| Người dùng không đọc được record liên kết | có | (không cần) | calendar đúng của đường dẫn | không có lỗi |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Bước đường dẫn trống (khách hàng không có công ty mẹ) | Lịch công ty của record; `note` nêu bước trống |
| CI-2 | Calendar cuối đường dẫn trống | Lịch công ty của record; `note` nêu lý do |
| CI-3 | Calendar cuối không có giờ làm | Lịch công ty của record; `note` nêu lý do |
| CI-4 | Lịch mặc định của công ty cũng không dùng được | Task 24x7 (không lịch); `note` nêu lý do |
| CI-5 | Biên: record không có công ty | Lịch mặc định của công ty hiện tại |
| CI-6 | Negative: người dùng không có quyền đọc record liên kết | Lịch vẫn đúng, không lỗi |

#### Traceability — TG-15

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-FUNC-039 | TCOND-15-01 | CI-1 | TC-CAL-001 |
| REQ-FUNC-039 | TCOND-15-01 | CI-2 | TC-CAL-002 |
| REQ-INT-009 | TCOND-15-02 | CI-1 | TC-CAL-003 |
| REQ-INT-009 | TCOND-15-02 | CI-2 | TC-CAL-004 |
| REQ-FUNC-019 | TCOND-15-03 | CI-1 | TC-CAL-005 |
| REQ-FUNC-019 | TCOND-15-03 | CI-2 | TC-CAL-006 |
| REQ-FUNC-019 | TCOND-15-03 | CI-3 | TC-CAL-007 |
| REQ-FUNC-019 | TCOND-15-03 | CI-4 | TC-CAL-008 |
| REQ-FUNC-019 | TCOND-15-03 | CI-5 | TC-CAL-009 |
| REQ-FUNC-020 | TCOND-15-04 | CI-1 | TC-CAL-010 |
| REQ-FUNC-020 | TCOND-15-04 | CI-2 | TC-CAL-011 |
| REQ-FUNC-020 | TCOND-15-04 | CI-3 | TC-CAL-012 |
| REQ-FUNC-020 | TCOND-15-04 | CI-4 | TC-CAL-013 |
| REQ-FUNC-020 | TCOND-15-04 | CI-5 | TC-CAL-014 |
| REQ-FUNC-020 | TCOND-15-04 | CI-6 | TC-CAL-015 |

### FT-16 / TG-16 — Phân quyền và đa công ty

**Technique:** Decision Table + Error Guessing — quyền và cô lập công ty là tổ hợp (vai trò, thao tác, công ty) nên dùng bảng quyết định; các lỗi quyền gián tiếp (server action, đọc qua record liên kết) khó đoán nên dùng Error Guessing.

#### TCOND-16-01 — Quyền theo nhóm SLA (đọc, sửa, menu)

**Feature:** FT-16 | **REQ-ID:** REQ-SEC-001 | **Technique:** Decision Table

**Mô tả điều kiện:** Hành vi quyền phụ thuộc vai trò và thao tác. Bảng quyết định:

| Vai trò | Thấy menu SLA | Đọc định nghĩa, task | Sửa định nghĩa | Đọc trực tiếp mọi model SLA |
|---|---|---|---|---|
| Không nhóm (U-NONE) | Không | Không | Không | Bị từ chối |
| group_sla_user (U-USR) | Có | Có | Không (bị từ chối) | Có |
| group_sla_manager (U-MGR) | Có | Có | Có | Có |

Phần "action và nút" của REQ-SEC-001 được kiểm ở TCOND-17-05 và TCOND-17-09.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | U-NONE không thấy menu SLA | Tập menu hiển thị của U-NONE không chứa menu gốc SLA |
| CI-2 | U-USR sửa định nghĩa bị từ chối | write trên sla.definition bởi U-USR ném AccessError |
| CI-3 | U-MGR sửa định nghĩa thành công | write trên sla.definition bởi U-MGR thành công |
| CI-4 | U-USR đọc định nghĩa và task | search và read sla.definition, sla.task thành công cho U-USR |
| CI-5 | U-NONE đọc trực tiếp dữ liệu SLA | search trên 4 model SLA bởi U-NONE ném AccessError |
| CI-6 | U-USR thêm mốc escalation bị từ chối | tạo `sla.escalation` bởi U-USR ném AccessError, số mốc không đổi |

#### TCOND-16-02 — Người dùng nghiệp vụ kích hoạt SLA không cần quyền SLA

**Feature:** FT-16 | **REQ-ID:** REQ-SEC-002 | **Technique:** Equivalence Partitioning

**Mô tả điều kiện:** Lớp: người dùng chỉ có quyền sửa record gốc, không thuộc nhóm SLA. Lớp con cần kiểm: (a) hệ quả ghi dữ liệu SLA vẫn thành công; (b) đọc trực tiếp dữ liệu SLA vẫn bị từ chối.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | U-BIZ đổi partner thỏa start, task được tạo | Có đúng 1 task in_progress của partner sau khi U-BIZ ghi |
| CI-2 | U-BIZ đọc task bị từ chối | search sla.task bởi U-BIZ ném AccessError |

#### TCOND-16-03 — Cô lập đa công ty cho task, event, định nghĩa

**Feature:** FT-16 | **REQ-ID:** REQ-SEC-003 | **Technique:** Decision Table

**Mô tả điều kiện:** Hai trục: công ty của định nghĩa (rỗng hoặc CO-A) và công ty của record gốc (CO-A hoặc CO-B); thêm trục phạm vi nhìn thấy của người dùng. Bảng quyết định áp dụng:

| Định nghĩa | Record công ty | Gắn task? |
|---|---|---|
| company_id rỗng | CO-A | Có |
| company_id rỗng | CO-B | Có |
| company_id = CO-A | CO-A | Có |
| company_id = CO-A | CO-B | Không |

Phạm vi nhìn thấy: người dùng chỉ thuộc CO-A không thấy task, event, định nghĩa gán CO-B; thấy định nghĩa không gán công ty.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | U-A không thấy task CO-B | search task của CO-B bởi U-A trả rỗng |
| CI-2 | U-A không thấy event CO-B | search event của CO-B bởi U-A trả rỗng |
| CI-3 | U-A thấy định nghĩa CO-A và không gán, không thấy CO-B | search định nghĩa bởi U-A trả đúng 2 trong 3 |
| CI-4 | Định nghĩa CO-A không gắn record CO-B | 0 task cho PB; có 1 task cho PA (đối chứng) |
| CI-5 | Định nghĩa company_id rỗng gắn cả A và B | 1 task cho mỗi PA và PB |

#### TCOND-16-04 — Server action của escalation chạy theo quyền user xử lý nền

**Feature:** FT-16 | **REQ-ID:** REQ-SEC-004 | **Technique:** Error Guessing

**Mô tả điều kiện:** Đoán lỗi: server action cần quyền mà user xử lý nền (U-CRON) không có. Hai nhánh theo cấu hình retry của mốc (tắt: `escalate_failed`; bật: `escalate_retry`). Cộng một điểm Inspection: form escalation có ghi chú nêu quyền của user xử lý nền.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Action lỗi quyền, retry=false | 1 event escalate_failed, 0 escalate_retry, 0 escalate |
| CI-2 | Action lỗi quyền, retry=true | 1 event escalate_retry và 1 dòng sla.escalation.retry với retry_at = 12:01 |
| CI-3 | Form escalation có ghi chú quyền | Ghi chú nêu user xử lý nền, quyền, không phải người sửa record |

#### TCOND-16-05 — Đọc lịch qua record liên kết không phụ thuộc quyền

**Feature:** FT-16 | **REQ-ID:** REQ-SEC-005 | **Technique:** Error Guessing

**Mô tả điều kiện:** Đoán lỗi: người dùng không đọc được record liên kết (công ty mẹ ở đường dẫn lịch). Hai khía cạnh: tính đúng lịch (không bị lỗi quyền hoặc rơi về 24x7) và không làm lộ dữ liệu record liên kết.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Attach dùng lịch FX-CAL-VN dù U-BIZ-S không đọc PM | task.schedule_id = FX-CAL-VN và planned_end_time = 13:00 giờ địa phương |
| CI-2 | Task và event không chứa dữ liệu PM ngoài tên calendar | Không field nào của task/event chứa 'PM-Secret' hay tên CO-B |

#### TCOND-16-06 — Task và event chỉ do hệ thống ghi

**Feature:** FT-16 | **REQ-ID:** REQ-SEC-006 | **Technique:** Decision Table

**Mô tả điều kiện:** Bảng thao tác theo đối tượng và vai trò (U-MGR trừ khi ghi khác):

| Đối tượng | Tạo | Sửa | Xóa |
|---|---|---|---|
| sla.task | Bị từ chối | Bị từ chối | Bị từ chối |
| sla.event | Bị từ chối | Chỉ `is_resolved` của event `error` (U-MGR) | Bị từ chối |

Hành động hợp lệ ("Apply Current Settings") thay đổi task qua đường hệ thống. U-USR không có ngoại lệ.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | U-MGR không ghi trực tiếp task | create, write, unlink trên sla.task bởi U-MGR đều ném AccessError |
| CI-2 | U-MGR không ghi event ngoài ngoại lệ | create, unlink, write(note) trên sla.event bởi U-MGR bị từ chối |
| CI-3 | U-MGR sửa is_resolved thành công | is_resolved đổi từ False sang True |
| CI-4 | Apply Current Settings là đường ghi hợp lệ | planned_end_time đổi từ 13:00 sang 17:00 sau Apply Current Settings |
| CI-5 | U-USR không có ngoại lệ is_resolved | write is_resolved bởi U-USR bị từ chối |
| CI-6 | View task và event không có create/edit/delete | Arch của list/form task và event có create=0, edit=0 (trừ is_resolved), delete=0 |

**Traceability TG-16**

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-SEC-001 | TCOND-16-01 | CI-1 | TC-SEC-001 |
| REQ-SEC-001 | TCOND-16-01 | CI-2 | TC-SEC-002 |
| REQ-SEC-001 | TCOND-16-01 | CI-3 | TC-SEC-003 |
| REQ-SEC-001 | TCOND-16-01 | CI-4 | TC-SEC-004 |
| REQ-SEC-001 | TCOND-16-01 | CI-5 | TC-SEC-005 |
| REQ-SEC-001 | TCOND-16-01 | CI-6 | TC-SEC-024 |
| REQ-SEC-002 | TCOND-16-02 | CI-1 | TC-SEC-006 |
| REQ-SEC-002 | TCOND-16-02 | CI-2 | TC-SEC-007 |
| REQ-SEC-003 | TCOND-16-03 | CI-1 | TC-SEC-008 |
| REQ-SEC-003 | TCOND-16-03 | CI-2 | TC-SEC-009 |
| REQ-SEC-003 | TCOND-16-03 | CI-3 | TC-SEC-010 |
| REQ-SEC-003 | TCOND-16-03 | CI-4 | TC-SEC-011 |
| REQ-SEC-003 | TCOND-16-03 | CI-5 | TC-SEC-012 |
| REQ-SEC-004 | TCOND-16-04 | CI-1 | TC-SEC-013 |
| REQ-SEC-004 | TCOND-16-04 | CI-2 | TC-SEC-014 (đã gỡ D12) |
| REQ-SEC-004 | TCOND-16-04 | CI-3 | TC-SEC-015 |
| REQ-SEC-005 | TCOND-16-05 | CI-1 | TC-SEC-016 |
| REQ-SEC-005 | TCOND-16-05 | CI-2 | TC-SEC-017 |
| REQ-SEC-006 | TCOND-16-06 | CI-1 | TC-SEC-018 |
| REQ-SEC-006 | TCOND-16-06 | CI-2 | TC-SEC-019 |
| REQ-SEC-006 | TCOND-16-06 | CI-3 | TC-SEC-020 |
| REQ-SEC-006 | TCOND-16-06 | CI-4 | TC-SEC-021 |
| REQ-SEC-006 | TCOND-16-06 | CI-5 | TC-SEC-022 |
| REQ-SEC-006 | TCOND-16-06 | CI-6 | TC-SEC-023 |

### FT-17 / TG-17 — Giao diện và báo cáo

**Technique:** Equivalence Partitioning + Boundary Value Analysis + Decision Table — bộ lọc và báo cáo chia lớp theo stage và dấu vi phạm, biên theo tham số X và kỳ end_time; điều kiện hiển thị theo nguồn lịch và quyền dùng bảng quyết định; phần hiển thị trực quan dùng Demonstration/Inspection dạng checklist.

#### TCOND-17-01 — Form định nghĩa SLA: lưu cấu hình và chế độ chỉ đọc

**Feature:** FT-17 | **REQ-ID:** REQ-INT-001 | **Technique:** Equivalence Partitioning

**Mô tả điều kiện:** Hai lớp người dùng: SLA Manager (có quyền ghi, lưu được giá trị cấu hình nhập qua form) và group_sla_user (form chỉ đọc). Thêm một điểm Demonstration cho bố cục form (chọn model, công cụ chọn domain, mục tiêu, nguồn lịch, danh sách escalation nội tuyến).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Lưu và mở lại giữ đúng model, start, target | model_name='res.partner', start_domain đúng chuỗi, duration=4.0 |
| CI-2 | U-USR không sửa được form | Không có quyền ghi; form không có nút Lưu |
| CI-3 | Form đủ thành phần cấu hình | Checklist 6 mục hiển thị đúng |

#### TCOND-17-02 — Help text ba cấu hình dễ sai

**Feature:** FT-17 | **REQ-ID:** REQ-INT-002 | **Technique:** Equivalence Partitioning

**Mô tả điều kiện:** Lớp field điều kiện: (a) start và pause phải nêu đủ ba cảnh báo (start là tập con của stop; pause là tập con của start; start và pause loại trừ nhau); (b) cancel và resume không chứa cảnh báo. Kiểm bằng Inspection nội dung help và Demonstration hiển thị tooltip.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Help start và pause có 3 cảnh báo | Mỗi help chứa 3 ý cảnh báo |
| CI-2 | Help cancel và resume sạch | Không chứa 3 cảnh báo |
| CI-3 | Help hiện ra trên giao diện | Tooltip hiện đủ, đọc được, không bị cắt |

#### TCOND-17-03 — Ghi chú lịch dự phòng theo nguồn lịch

**Feature:** FT-17 | **REQ-ID:** REQ-INT-003 | **Technique:** Decision Table

**Mô tả điều kiện:** Hiển thị ghi chú phụ thuộc giá trị `schedule_source`:

| schedule_source | Ghi chú vàng dưới field nguồn lịch |
|---|---|
| record | Hiện, nêu 2 bước dự phòng (lịch mặc định của công ty, rồi 24x7) |
| none | Ẩn |
| definition | Ẩn |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Ghi chú hiện khi source=record | Ghi chú vàng nằm ngay dưới field nguồn lịch, nêu 2 bước dự phòng |
| CI-2 | Ghi chú ẩn khi source khác record | Không có ghi chú ở none và definition |
| CI-3 | Arch có ghi chú điều kiện theo schedule_source | Ghi chú có điều kiện ẩn khi schedule_source != 'record' và chứa cả hai bước |

#### TCOND-17-04 — Danh sách và form chỉ đọc cho task SLA

**Feature:** FT-17 | **REQ-ID:** REQ-INT-004 | **Technique:** Equivalence Partitioning

**Mô tả điều kiện:** Lớp: (a) người xem (SLA User) thấy đủ cột tối thiểu của task đang chạy; (b) SLA Manager không có thao tác sửa, xóa; (c) bố cục hiển thị (Demonstration).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | List task có đủ cột và dòng của task | Arch list chứa 9 field, dòng task đọc được đúng giá trị |
| CI-2 | Form task chỉ đọc cho U-MGR | create, edit, delete = 0 trên view; ACL ghi bị chặn |
| CI-3 | List và form task hiển thị đủ, chỉ đọc | Checklist 9 cột + form chỉ đọc |

#### TCOND-17-05 — Action SLA trên record gốc theo trạng thái định nghĩa và task

**Feature:** FT-17 | **REQ-ID:** REQ-INT-006 | **Technique:** Decision Table

**Mô tả điều kiện:** Action "SLA" hiện hay ẩn theo trạng thái model và người dùng:

| Định nghĩa đang bật của model | Task đang hoạt động | Người dùng thuộc nhóm SLA | Action hiện? |
|---|---|---|---|
| Có | Bất kỳ | Có | Có (lọc theo record đang chọn) |
| Không (đã archive) | Có | Có | Có |
| Không | Không | Có | Không |
| Bất kỳ | Bất kỳ | Không | Không |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Action SLA lọc theo record | Action mở đúng 2 task của P, không có task của Q |
| CI-2 | Action còn khi còn task đang hoạt động | Action 'SLA' vẫn có trong bindings |
| CI-3 | Action biến mất khi hết cả hai | Action 'SLA' không còn trong bindings |
| CI-4 | U-NONE không thấy action | Bindings của U-NONE không có action 'SLA' |
| CI-5 | Action SLA trên giao diện | Checklist menu Action |

#### TCOND-17-06 — Bộ lọc trạng thái Đang chạy, Tạm dừng, Đã vi phạm

**Feature:** FT-17 | **REQ-ID:** REQ-INT-011 | **Technique:** Equivalence Partitioning

**Mô tả điều kiện:** Lớp dữ liệu theo stage và dấu vi phạm: in_progress, paused, breached, achieved có dấu vi phạm. Lớp rỗng: không task nào thỏa bộ lọc.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Ba bộ lọc trả đúng số task | Đang chạy = 2, Tạm dừng = 1, Đã vi phạm = 2 |
| CI-2 | Bộ lọc không có kết quả trả rỗng | 3 bộ lọc trả 0, không lỗi |

#### TCOND-17-07 — Bộ lọc Sắp đến hạn và tham số X

**Feature:** FT-17 | **REQ-ID:** REQ-INT-012 | **Technique:** Boundary Value Analysis

**Mô tả điều kiện:** Điều kiện: stage = in_progress, has_breached = false, planned_end_time <= now + X giờ. Biên tại X (mặc định 4):

| Giá trị planned_end_time tương đối now | Kết quả (X = 6) |
|---|---|
| now - 10 phút (chưa vi phạm) | Có |
| now + 5h59m | Có |
| now + 6h01m | Không |

Lớp loại trừ: paused, achieved, đã vi phạm. Tham số X chỉnh được bởi SLA Manager; mặc định 4.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Bộ lọc theo X | Trả task sau 1h và 5h, không trả sau 3 ngày |
| CI-2 | Biên planned_end_time quanh now + X | Trong biên (5h59m, quá hạn chưa vi phạm) có; ngoài biên (6h01m) không |
| CI-3 | Task ngoài lớp không xuất hiện | Kết quả rỗng |
| CI-4 | SLA Manager đổi X | Sau đổi chỉ còn task trong 1 giờ |
| CI-5 | Mặc định 4 | X = 4: task sau 3h có, sau 5h không |
| CI-6 | U-USR không đổi được X | Ghi X bị từ chối, giá trị không đổi |

#### TCOND-17-08 — Nhóm, pivot, graph cho task SLA

**Feature:** FT-17 | **REQ-ID:** REQ-INT-013 | **Technique:** Equivalence Partitioning

**Mô tả điều kiện:** Lớp: nhóm theo định nghĩa, nhóm theo model và stage (dữ liệu), chế độ xem pivot và graph (hiển thị, Demonstration).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Nhóm theo definition_id | 2 nhóm, đếm 3 và 2 |
| CI-2 | Nhóm theo res_model và stage | Nhóm đúng số lượng |
| CI-3 | Pivot và graph mở được, tổng khớp danh sách | Checklist 5 mục |

#### TCOND-17-09 — Nút số task SLA trên form của model dùng sla.mixin

**Feature:** FT-17 | **REQ-ID:** REQ-INT-014 | **Technique:** Equivalence Partitioning

**Mô tả điều kiện:** Lớp: số task của record (dữ liệu), nút hiện với người dùng nhóm SLA (Demonstration), nút ẩn với người không thuộc nhóm (kiểm arch theo quyền).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Số và action của nút đúng | Đếm = 2; action trả 2 task |
| CI-2 | Nút hiện số 2 và mở danh sách | Checklist 4 mục |
| CI-3 | Nút ẩn với U-NONE | Arch form theo quyền U-NONE không có nút; U-USR có |

#### TCOND-17-10 — Hành động Đánh giá lại trên task

**Feature:** FT-17 | **REQ-ID:** REQ-INT-020 | **Technique:** State Transition

**Mô tả điều kiện:** Chuyển trạng thái do hành động Re-check Conditions:

| Trạng thái hiện tại | Điều kiện stop (qua quan hệ) | Người bấm | Kết quả |
|---|---|---|---|
| in_progress | đã khớp nhưng chưa kết thúc | SLA Manager | achieved |
| achieved | bất kỳ | SLA Manager | không đổi (REQ-FUNC-031 AC3) |
| in_progress | bất kỳ | group_sla_user | không có nút, gọi hàm bị từ chối |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Đánh giá lại kéo task về achieved | stage = achieved, end_time = thời điểm đánh giá |
| CI-2 | U-USR không có nút Re-check Conditions | Arch không có nút; gọi hàm bị từ chối |
| CI-3 | Task kết thúc bất biến | stage, end_time, số event không đổi |

#### TCOND-17-11 — Danh sách sự kiện SLA: lọc, nhóm, chỉ đọc

**Feature:** FT-17 | **REQ-ID:** REQ-INT-021 | **Technique:** Equivalence Partitioning

**Mô tả điều kiện:** Lớp lọc: theo loại sự kiện; theo trạng thái xử lý của event error. Nhóm theo định nghĩa và theo loại. Lớp chỉ đọc: không tạo, sửa, xóa trên danh sách.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Bộ lọc loại sự kiện | Lọc error = 2 event |
| CI-2 | Bộ lọc chưa xử lý và đã xử lý | Chưa xử lý = 1, đã xử lý = 1 |
| CI-3 | Nhóm theo definition_id và event | Số nhóm và số lượng đúng |
| CI-4 | Danh sách event chỉ đọc | create=0, delete=0 trên list; ACL create/unlink False |

#### TCOND-17-12 — Tỷ lệ đạt theo định nghĩa và kỳ end_time

**Feature:** FT-17 | **REQ-ID:** REQ-FUNC-036 | **Technique:** Boundary Value Analysis

**Mô tả điều kiện:** Tỷ lệ = achieved / (achieved + breached); cancelled bị loại. Biên: mẫu số 0 (hiển thị 'không xác định', không chia cho 0); biên kỳ (cuối tháng 9 và đầu tháng 10 thuộc hai kỳ khác nhau theo end_time).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | 8 achieved, 2 breached, 5 cancelled cho 80% | achieved_rate = 80% |
| CI-2 | Mẫu số 0 không chia cho 0 | Tỷ lệ rỗng ('không xác định'), không lỗi |
| CI-3 | Kỳ theo end_time | 2 nhóm kỳ: 2026-09 và 2026-10, mỗi nhóm 1 task |

#### TCOND-17-13 — Số SLA đang vi phạm theo định nghĩa

**Feature:** FT-17 | **REQ-ID:** REQ-FUNC-062 | **Technique:** Equivalence Partitioning

**Mô tả điều kiện:** Số đang vi phạm = số task có has_breached = true và stage thuộc {in_progress, paused}. Lớp: hỗn hợp stage (3 đang vi phạm), không có vi phạm (0), tách theo định nghĩa.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Số đang vi phạm = 3 | Count = 3 |
| CI-2 | Không vi phạm cho 0 | Count = 0 |
| CI-3 | Theo định nghĩa | D1 = 2, D2 = 1 |

**Traceability TG-17**

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-INT-001 | TCOND-17-01 | CI-1 | TC-UIX-001 |
| REQ-INT-001 | TCOND-17-01 | CI-2 | TC-UIX-002 |
| REQ-INT-001 | TCOND-17-01 | CI-3 | TC-UIX-003 |
| REQ-INT-002 | TCOND-17-02 | CI-1 | TC-UIX-004 |
| REQ-INT-002 | TCOND-17-02 | CI-2 | TC-UIX-005 |
| REQ-INT-002 | TCOND-17-02 | CI-3 | TC-UIX-006 |
| REQ-INT-003 | TCOND-17-03 | CI-1 | TC-UIX-007 |
| REQ-INT-003 | TCOND-17-03 | CI-2 | TC-UIX-008 |
| REQ-INT-003 | TCOND-17-03 | CI-3 | TC-UIX-009 |
| REQ-INT-004 | TCOND-17-04 | CI-1 | TC-UIX-010 |
| REQ-INT-004 | TCOND-17-04 | CI-2 | TC-UIX-011 |
| REQ-INT-004 | TCOND-17-04 | CI-3 | TC-UIX-012 |
| REQ-INT-006 | TCOND-17-05 | CI-1 | TC-UIX-013 |
| REQ-INT-006 | TCOND-17-05 | CI-2 | TC-UIX-014 |
| REQ-INT-006 | TCOND-17-05 | CI-3 | TC-UIX-015 |
| REQ-INT-006 | TCOND-17-05 | CI-4 | TC-UIX-016 |
| REQ-INT-006 | TCOND-17-05 | CI-5 | TC-UIX-017 |
| REQ-INT-011 | TCOND-17-06 | CI-1 | TC-UIX-018 |
| REQ-INT-011 | TCOND-17-06 | CI-2 | TC-UIX-019 |
| REQ-INT-012 | TCOND-17-07 | CI-1 | TC-UIX-020 |
| REQ-INT-012 | TCOND-17-07 | CI-2 | TC-UIX-021 |
| REQ-INT-012 | TCOND-17-07 | CI-3 | TC-UIX-022 |
| REQ-INT-012 | TCOND-17-07 | CI-4 | TC-UIX-023 |
| REQ-INT-012 | TCOND-17-07 | CI-5 | TC-UIX-024 |
| REQ-INT-012 | TCOND-17-07 | CI-6 | TC-UIX-025 |
| REQ-INT-013 | TCOND-17-08 | CI-1 | TC-UIX-026 |
| REQ-INT-013 | TCOND-17-08 | CI-2 | TC-UIX-027 |
| REQ-INT-013 | TCOND-17-08 | CI-3 | TC-UIX-028 |
| REQ-INT-014 | TCOND-17-09 | CI-1 | TC-UIX-029 |
| REQ-INT-014 | TCOND-17-09 | CI-2 | TC-UIX-030 |
| REQ-INT-014 | TCOND-17-09 | CI-3 | TC-UIX-031 |
| REQ-INT-020 | TCOND-17-10 | CI-1 | TC-UIX-032 |
| REQ-INT-020 | TCOND-17-10 | CI-2 | TC-UIX-033 |
| REQ-INT-020 | TCOND-17-10 | CI-3 | TC-UIX-034 |
| REQ-INT-021 | TCOND-17-11 | CI-1 | TC-UIX-035 |
| REQ-INT-021 | TCOND-17-11 | CI-2 | TC-UIX-036 |
| REQ-INT-021 | TCOND-17-11 | CI-3 | TC-UIX-037 |
| REQ-INT-021 | TCOND-17-11 | CI-4 | TC-UIX-038 |
| REQ-FUNC-036 | TCOND-17-12 | CI-1 | TC-UIX-039 |
| REQ-FUNC-036 | TCOND-17-12 | CI-2 | TC-UIX-040 |
| REQ-FUNC-036 | TCOND-17-12 | CI-3 | TC-UIX-041 |
| REQ-FUNC-062 | TCOND-17-13 | CI-1 | TC-UIX-042 |
| REQ-FUNC-062 | TCOND-17-13 | CI-2 | TC-UIX-043 |
| REQ-FUNC-062 | TCOND-17-13 | CI-3 | TC-UIX-044 |

### FT-18 / TG-18 — Hiệu năng

**Technique:** BVA/EP trên kích thước lô (10 vs 100) và quy mô dữ liệu (1000 vs 100000 task); đo thống kê (trung vị, p95) với số lần lặp cố định. Không phải kiểm tra chức năng.

#### TCOND-18-01 — Overhead hook trên model không có định nghĩa

**Feature:** FT-18 | **REQ-ID:** REQ-PERF-001 | **Technique:** EP

**Mô tả điều kiện:** So sánh thời gian ghi hàng loạt trên `res.partner` (không có định nghĩa) giữa môi trường chưa cài và đã cài module; ngưỡng trung vị sau / trước <= 1.05 (đề xuất, O-01).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Mô hình không có định nghĩa, hai DB (trước/sau cài) | Trung vị sau <= 105% trung vị trước |
| CI-2 | Model không có định nghĩa khi model khác có 4 định nghĩa mẫu | Trung vị <= 105% |
| CI-3 | Model không có định nghĩa không bị patch (AD-01 patch động) | không có dấu patch trên model không định nghĩa |

#### TCOND-18-02 — Số truy vấn không tăng theo kích thước lô

**Feature:** FT-18 | **REQ-ID:** REQ-PERF-002 | **Technique:** BVA

**Mô tả điều kiện:** Biên chênh số truy vấn |Q(100) - Q(10)| <= 5 cho ba dạng lô: khớp start (attach), không khớp, đã có task và khớp stop.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Lô khớp start (attach hàng loạt) | |Q(100) - Q(10)| <= 5 |
| CI-2 | Lô không khớp điều kiện nào | |Q(100) - Q(10)| <= 5 |
| CI-3 | Lô có task, khớp stop | |Q(100) - Q(10)| <= 5 |

#### TCOND-18-03 — Độ trễ và khả năng mở rộng của xử lý nền

**Feature:** FT-18 | **REQ-ID:** REQ-PERF-003 | **Technique:** EP

**Mô tả điều kiện:** Khả năng mở rộng theo số task đang chạy (1000 vs 100000), độ trễ xử lý 200 mốc (escalation, breach) và chu kỳ cron tối thiểu 1 phút.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | 100000 vs 1000 task đang chạy, 10 mốc đến hạn | Tỷ lệ thời gian chu kỳ <= 2 |
| CI-2 | 200 mốc escalation đến hạn tại T | Hoàn tất trong T + 2 phút (p95 qua 20 chu kỳ) |
| CI-3 | 200 task vượt `planned_end_time` tại T | Dấu vi phạm bật trong T + 2 phút (p95) |
| CI-4 | Chu kỳ cron | Cron xử lý nền chạy mỗi 1 phút |

**Traceability TG-18**

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-PERF-001 | TCOND-18-01 | CI-1 | TC-PRF-001 |
| REQ-PERF-001 | TCOND-18-01 | CI-2 | TC-PRF-002 |
| REQ-PERF-001 | TCOND-18-01 | CI-3 | TC-PRF-010 |
| REQ-PERF-002 | TCOND-18-02 | CI-1 | TC-PRF-003 |
| REQ-PERF-002 | TCOND-18-02 | CI-2 | TC-PRF-004 |
| REQ-PERF-002 | TCOND-18-02 | CI-3 | TC-PRF-005 |
| REQ-PERF-003 | TCOND-18-03 | CI-1 | TC-PRF-006 |
| REQ-PERF-003 | TCOND-18-03 | CI-2 | TC-PRF-007 |
| REQ-PERF-003 | TCOND-18-03 | CI-3 | TC-PRF-008 |
| REQ-PERF-003 | TCOND-18-03 | CI-4 | TC-PRF-009 |

### FT-19 / TG-19 — Điểm mở rộng

**Technique:** Error Guessing + EP — mỗi điểm mở rộng có lớp 'có module mẫu override' và 'không có module mẫu (mặc định)'; lớp đầu ra không hợp lệ (âm, flexible) tách riêng; Decision Table cho nhánh hook.

#### TCOND-19-01 — Điểm mở rộng nguồn lịch

**Feature:** FT-19 | **REQ-ID:** REQ-INT-007 | **Technique:** EP

**Mô tả điều kiện:** Lớp: module mẫu thêm giá trị `team` (có calendar hợp lệ), trả calendar `flexible`, trả rỗng, gỡ module, không có module mẫu.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Module mẫu thêm nguồn `team`, record có team T | Task dùng calendar của T |
| CI-2 | Module mẫu trả calendar `flexible` | Áp dụng lịch dự phòng |
| CI-3 | Gỡ module mẫu | Định nghĩa quay về `none`, không lỗi |
| CI-4 | Không có module mẫu: các giá trị mặc định | Chỉ `none`, `definition`, `record` |
| CI-5 | Module mẫu trả rỗng (không có calendar) | Áp dụng lịch dự phòng [Giả định] |

#### TCOND-19-02 — Điểm mở rộng thời lượng mục tiêu

**Feature:** FT-19 | **REQ-ID:** REQ-INT-015 | **Technique:** BVA

**Mô tả điều kiện:** Giá trị trả về: 3 (hợp lệ, khác định nghĩa), mặc định (không override), âm (từ chối), 0 (biên hợp lệ), record không thuộc quy tắc override.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Module mẫu trả 3 cho `priority = p1` | `target_duration` = 3 |
| CI-2 | Không có module mẫu | `target_duration` = 4 |
| CI-3 | Module mẫu trả -1 | Không tạo task, event `error` |
| CI-4 | Module mẫu trả 0 (biên hợp lệ) | Task tạo, `target_duration` = 0 |
| CI-5 | Record không thuộc quy tắc override (`p2`) | `target_duration` = 4 |

#### TCOND-19-03 — Điểm mở rộng mốc bắt đầu

**Feature:** FT-19 | **REQ-ID:** REQ-INT-016 | **Technique:** EP

**Mô tả điều kiện:** Lớp: module mẫu trả mốc trong quá khứ; không có module mẫu và không retroactive; không có module mẫu nhưng bật retroactive.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Module mẫu trả mốc T0 - 2h | `start_time` = T0 - 2h |
| CI-2 | Không có module mẫu, không retroactive | `start_time` = now |
| CI-3 | Không có module mẫu, bật retroactive | `start_time` = giá trị field retroactive |

#### TCOND-19-04 — Điểm mở rộng domain của điều kiện

**Feature:** FT-19 | **REQ-ID:** REQ-INT-017 | **Technique:** EP

**Mô tả điều kiện:** Lớp: module mẫu thay domain của start; không có module mẫu; override chỉ một điều kiện, điều kiện khác dùng domain lưu.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Module mẫu trả domain khác cho start | Kết quả theo domain của module mẫu |
| CI-2 | Không có module mẫu | Dùng domain đã lưu |
| CI-3 | Module mẫu chỉ đổi `start`, điều kiện `stop` dùng domain lưu | Stop theo domain lưu |

#### TCOND-19-05 — Điểm mở rộng sau chuyển trạng thái

**Feature:** FT-19 | **REQ-ID:** REQ-INT-018 | **Technique:** Decision Table

**Mô tả điều kiện:** Bảng quyết định: (có chuyển trạng thái, có override) → số lần gọi hook:
| Chuyển trạng thái | Có module mẫu | Hành vi |
|---|---|---|
| Có | Có | gọi đúng 1 lần với (cũ, mới, loại event) |
| Không | Có | không gọi |
| Có | Không | mặc định không làm gì, không lỗi |

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | `in_progress` → `paused` | Gọi 1 lần với (`in_progress`,`paused`,`pause`) |
| CI-2 | Đánh giá không đổi trạng thái | Không gọi hook |
| CI-3 | `in_progress` → `achieved` | Gọi 1 lần với (`in_progress`,`achieved`,`complete`) |
| CI-4 | Không có module mẫu (mặc định) | Chuyển trạng thái chạy bình thường |

#### TCOND-19-06 — Không phá vỡ điểm mở rộng trong cùng phiên bản chính

**Feature:** FT-19 | **REQ-ID:** REQ-REUSE-001 | **Technique:** Error Guessing

**Mô tả điều kiện:** Module mẫu override cả 5 điểm vẫn chạy sau nâng cấp; thay đổi chữ ký bị phát hiện bởi test hợp đồng và bởi rà soát MR.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Module mẫu override đủ 5 điểm sau nâng cấp | Module mẫu vẫn chạy, test điểm mở rộng đạt |
| CI-2 | Thay đổi chữ ký điểm mở rộng | Test hợp đồng thất bại |
| CI-3 | MR đổi chữ ký điểm mở rộng (Inspection) | Rà soát MR đánh dấu thay đổi gây phá vỡ |

**Traceability TG-19**

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-INT-007 | TCOND-19-01 | CI-1 | TC-EXT-001 |
| REQ-INT-007 | TCOND-19-01 | CI-2 | TC-EXT-002 |
| REQ-INT-007 | TCOND-19-01 | CI-3 | TC-EXT-003 |
| REQ-INT-007 | TCOND-19-01 | CI-4 | TC-EXT-004 |
| REQ-INT-007 | TCOND-19-01 | CI-5 | TC-EXT-005 |
| REQ-INT-015 | TCOND-19-02 | CI-1 | TC-EXT-006 |
| REQ-INT-015 | TCOND-19-02 | CI-2 | TC-EXT-007 |
| REQ-INT-015 | TCOND-19-02 | CI-3 | TC-EXT-008 |
| REQ-INT-015 | TCOND-19-02 | CI-4 | TC-EXT-009 |
| REQ-INT-015 | TCOND-19-02 | CI-5 | TC-EXT-010 |
| REQ-INT-016 | TCOND-19-03 | CI-1 | TC-EXT-011 |
| REQ-INT-016 | TCOND-19-03 | CI-2 | TC-EXT-012 |
| REQ-INT-016 | TCOND-19-03 | CI-3 | TC-EXT-013 |
| REQ-INT-017 | TCOND-19-04 | CI-1 | TC-EXT-014 |
| REQ-INT-017 | TCOND-19-04 | CI-2 | TC-EXT-015 |
| REQ-INT-017 | TCOND-19-04 | CI-3 | TC-EXT-016 |
| REQ-INT-018 | TCOND-19-05 | CI-1 | TC-EXT-017 |
| REQ-INT-018 | TCOND-19-05 | CI-2 | TC-EXT-018 |
| REQ-INT-018 | TCOND-19-05 | CI-3 | TC-EXT-019 |
| REQ-INT-018 | TCOND-19-05 | CI-4 | TC-EXT-020 |
| REQ-REUSE-001 | TCOND-19-06 | CI-1 | TC-EXT-021 |
| REQ-REUSE-001 | TCOND-19-06 | CI-2 | TC-EXT-022 |
| REQ-REUSE-001 | TCOND-19-06 | CI-3 | TC-EXT-023 |

### FT-INS / INS — Inspection và kiểm tra CI (BUILD, MAINT, CM, INST-002)

**Technique:** Inspection (rà soát có checklist) và kiểm tra tự động trong CI; mỗi mục AC tương ứng một mục checklist nhị phân. Không dùng kỹ thuật thiết kế dữ liệu test.

#### TCOND-INS-01 — Phụ thuộc tối thiểu của module

**Feature:** FT-INS | **REQ-ID:** REQ-INST-002 | **Technique:** Inspection

**Mô tả điều kiện:** Kiểm tra `depends` trong `__manifest__.py` chỉ gồm `base` và `resource`; không có phụ thuộc cấm (helpdesk, `nev_*`, `dwo_*` khác, OCA).

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | `depends` của manifest | Đúng {base, resource} |
| CI-2 | Phụ thuộc cấm (helpdesk, `nev_*`, `dwo_*`, OCA) | Không có tham chiếu |

#### TCOND-INS-02 — Tuân thủ lint của repo

**Feature:** FT-INS | **REQ-ID:** REQ-BUILD-001 | **Technique:** Inspection

**Mô tả điều kiện:** Pylint theo `.pylintrc` đạt điểm >= 9 trên mọi file Python; eslint/prettier cho JS nếu có; xác nhận module không bị `ignore-patterns` bỏ qua.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Pylint trên file Python | Exit 0, điểm >= 9 |
| CI-2 | eslint/prettier cho JS (nếu có) | Không lỗi |
| CI-3 | Module không bị `ignore-patterns` bỏ qua | Pylint thực sự phân tích module |

#### TCOND-INS-03 — Comment lý do tại chỗ cài đặt

**Feature:** FT-INS | **REQ-ID:** REQ-MAINT-001 | **Technique:** Inspection

**Mô tả điều kiện:** Năm mục quyết định không hiển nhiên, mỗi mục có comment tại vị trí cài đặt: (1) quan sát sửa trực tiếp và tính lại field compute có lưu; (2) engine lỗi không chặn lưu và đánh đổi kèm biện pháp bù; (3) đánh giá lại dùng thời điểm hiện tại, không sửa ngược task đã kết thúc; (4) ý nghĩa nhật ký sự kiện; (5) giới hạn field compute không lưu.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Mục 1: Hook trên ORM | Có comment tại vị trí cài đặt |
| CI-2 | Mục 2: Cô lập lỗi engine | Có comment tại vị trí cài đặt |
| CI-3 | Mục 3: Đánh giá lại | Có comment tại vị trí cài đặt |
| CI-4 | Mục 4: Nhật ký sự kiện | Có comment tại vị trí cài đặt |
| CI-5 | Mục 5: Field compute không lưu | Có comment tại vị trí cài đặt |

#### TCOND-INS-04 — Bộ test tự động chạy bằng một lệnh

**Feature:** FT-INS | **REQ-ID:** REQ-MAINT-002 | **Technique:** Inspection

**Mô tả điều kiện:** Một lệnh trên database trống chạy toàn bộ test; suite generic dùng `res.partner`; suite end-to-end dùng `demo.ticket`; kết quả đạt/không đạt phản ánh qua mã thoát.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | Database trống, một lệnh | Chạy hết test và báo kết quả |
| CI-2 | Suite generic trên `res.partner` | Có và không phụ thuộc model ticket |
| CI-3 | Suite end-to-end trên `demo.ticket` | Có và chạy được |
| CI-4 | Test lỗi → mã thoát khác 0 | Báo không đạt |

#### TCOND-INS-05 — Quản lý thay đổi gây phá vỡ

**Feature:** FT-INS | **REQ-ID:** REQ-CM-001 | **Technique:** Inspection

**Mô tả điều kiện:** MR đổi chữ ký điểm mở rộng hoặc cấu trúc dữ liệu SLA phải được phân loại phá vỡ, có script nâng cấp và dòng Revision History.

| CI | Class / Rule / Boundary / Transition | Hành vi mong đợi |
|---|---|---|
| CI-1 | MR gây phá vỡ có migration và Revision History | Cả hai có |
| CI-2 | MR gây phá vỡ thiếu migration (negative) | MR bị từ chối |
| CI-3 | Đổi cấu trúc dữ liệu cũng là thay đổi gây phá vỡ | Được phân loại phá vỡ |

**Traceability INS**

| REQ-ID | TCOND | CI | TC-ID |
|---|---|---|---|
| REQ-INST-002 | TCOND-INS-01 | CI-1 | TC-INS-001 |
| REQ-INST-002 | TCOND-INS-01 | CI-2 | TC-INS-002 |
| REQ-BUILD-001 | TCOND-INS-02 | CI-1 | TC-INS-003 |
| REQ-BUILD-001 | TCOND-INS-02 | CI-2 | TC-INS-004 |
| REQ-BUILD-001 | TCOND-INS-02 | CI-3 | TC-INS-005 |
| REQ-MAINT-001 | TCOND-INS-03 | CI-1 | TC-INS-006 |
| REQ-MAINT-001 | TCOND-INS-03 | CI-2 | TC-INS-007 |
| REQ-MAINT-001 | TCOND-INS-03 | CI-3 | TC-INS-008 |
| REQ-MAINT-001 | TCOND-INS-03 | CI-4 | TC-INS-009 |
| REQ-MAINT-001 | TCOND-INS-03 | CI-5 | TC-INS-010 |
| REQ-MAINT-002 | TCOND-INS-04 | CI-1 | TC-INS-011 |
| REQ-MAINT-002 | TCOND-INS-04 | CI-2 | TC-INS-012 |
| REQ-MAINT-002 | TCOND-INS-04 | CI-3 | TC-INS-013 |
| REQ-MAINT-002 | TCOND-INS-04 | CI-4 | TC-INS-014 |
| REQ-CM-001 | TCOND-INS-05 | CI-1 | TC-INS-015 |
| REQ-CM-001 | TCOND-INS-05 | CI-2 | TC-INS-016 |
| REQ-CM-001 | TCOND-INS-05 | CI-3 | TC-INS-017 |


---

## 6. Traceability Table (tổng hợp)

REQ-ID → Test Condition → Coverage Item → Test Case (ID định nghĩa ở `060_Test-Case-Specification.md`). Một số REQ xuất hiện ở nhiều nhóm vì có Acceptance Criteria thuộc nhiều nhóm test.

| REQ-ID | Test Condition | Coverage Item | Test Case |
|---|---|---|---|
| REQ-INT-001 | TCOND-17-01 | CI-1 | TC-UIX-001 |
| REQ-INT-001 | TCOND-17-01 | CI-2 | TC-UIX-002 |
| REQ-INT-001 | TCOND-17-01 | CI-3 | TC-UIX-003 |
| REQ-INT-002 | TCOND-17-02 | CI-1 | TC-UIX-004 |
| REQ-INT-002 | TCOND-17-02 | CI-2 | TC-UIX-005 |
| REQ-INT-002 | TCOND-17-02 | CI-3 | TC-UIX-006 |
| REQ-INT-003 | TCOND-17-03 | CI-1 | TC-UIX-007 |
| REQ-INT-003 | TCOND-17-03 | CI-2 | TC-UIX-008 |
| REQ-INT-003 | TCOND-17-03 | CI-3 | TC-UIX-009 |
| REQ-INT-004 | TCOND-17-04 | CI-1 | TC-UIX-010 |
| REQ-INT-004 | TCOND-17-04 | CI-2 | TC-UIX-011 |
| REQ-INT-004 | TCOND-17-04 | CI-3 | TC-UIX-012 |
| REQ-INT-005 | TCOND-11-03 | CI-1 | TC-CHG-006 |
| REQ-INT-005 | TCOND-11-03 | CI-2 | TC-CHG-007 |
| REQ-INT-005 | TCOND-11-03 | CI-3 | TC-CHG-008 |
| REQ-INT-005 | TCOND-11-03 | CI-4 | TC-CHG-009 |
| REQ-INT-005 | TCOND-11-03 | CI-5 | TC-CHG-010 |
| REQ-INT-005 | TCOND-11-03 | CI-6 | TC-CHG-011 |
| REQ-INT-005 | TCOND-11-03 | CI-7 | TC-CHG-028 |
| REQ-INT-006 | TCOND-17-05 | CI-1 | TC-UIX-013 |
| REQ-INT-006 | TCOND-17-05 | CI-2 | TC-UIX-014 |
| REQ-INT-006 | TCOND-17-05 | CI-3 | TC-UIX-015 |
| REQ-INT-006 | TCOND-17-05 | CI-4 | TC-UIX-016 |
| REQ-INT-006 | TCOND-17-05 | CI-5 | TC-UIX-017 |
| REQ-INT-011 | TCOND-17-06 | CI-1 | TC-UIX-018 |
| REQ-INT-011 | TCOND-17-06 | CI-2 | TC-UIX-019 |
| REQ-INT-012 | TCOND-17-07 | CI-1 | TC-UIX-020 |
| REQ-INT-012 | TCOND-17-07 | CI-2 | TC-UIX-021 |
| REQ-INT-012 | TCOND-17-07 | CI-3 | TC-UIX-022 |
| REQ-INT-012 | TCOND-17-07 | CI-4 | TC-UIX-023 |
| REQ-INT-012 | TCOND-17-07 | CI-5 | TC-UIX-024 |
| REQ-INT-012 | TCOND-17-07 | CI-6 | TC-UIX-025 |
| REQ-INT-013 | TCOND-17-08 | CI-1 | TC-UIX-026 |
| REQ-INT-013 | TCOND-17-08 | CI-2 | TC-UIX-027 |
| REQ-INT-013 | TCOND-17-08 | CI-3 | TC-UIX-028 |
| REQ-INT-014 | TCOND-17-09 | CI-1 | TC-UIX-029 |
| REQ-INT-014 | TCOND-17-09 | CI-2 | TC-UIX-030 |
| REQ-INT-014 | TCOND-17-09 | CI-3 | TC-UIX-031 |
| REQ-INT-020 | TCOND-17-10 | CI-1 | TC-UIX-032 |
| REQ-INT-020 | TCOND-17-10 | CI-2 | TC-UIX-033 |
| REQ-INT-020 | TCOND-17-10 | CI-3 | TC-UIX-034 |
| REQ-INT-021 | TCOND-17-11 | CI-1 | TC-UIX-035 |
| REQ-INT-021 | TCOND-17-11 | CI-2 | TC-UIX-036 |
| REQ-INT-021 | TCOND-17-11 | CI-3 | TC-UIX-037 |
| REQ-INT-021 | TCOND-17-11 | CI-4 | TC-UIX-038 |
| REQ-INT-022 | TCOND-12-07 | CI-1 | TC-ERR-022 |
| REQ-INT-022 | TCOND-12-07 | CI-2 | TC-ERR-023 |
| REQ-INT-022 | TCOND-12-07 | CI-3 | TC-ERR-024 |
| REQ-INT-022 | TCOND-12-07 | CI-4 | TC-ERR-025 |
| REQ-INT-023 | TCOND-03-06 | CI-1 | TC-BRE-015 |
| REQ-INT-023 | TCOND-03-06 | CI-2 | TC-BRE-016 |
| REQ-INT-023 | TCOND-03-06 | CI-3 | TC-BRE-017 |
| REQ-INT-023 | TCOND-03-06 | CI-4 | TC-BRE-018 |
| REQ-INT-023 | TCOND-03-06 | CI-5 | TC-BRE-019 |
| REQ-INT-023 | TCOND-03-06 | CI-6 | TC-BRE-020 |
| REQ-INT-023 | TCOND-03-06 | CI-7 | TC-BRE-021 |
| REQ-INT-007 | TCOND-19-01 | CI-1 | TC-EXT-001 |
| REQ-INT-007 | TCOND-19-01 | CI-2 | TC-EXT-002 |
| REQ-INT-007 | TCOND-19-01 | CI-3 | TC-EXT-003 |
| REQ-INT-007 | TCOND-19-01 | CI-4 | TC-EXT-004 |
| REQ-INT-007 | TCOND-19-01 | CI-5 | TC-EXT-005 |
| REQ-INT-008 | TCOND-08-16 | CI-1 | TC-ESC-048 |
| REQ-INT-008 | TCOND-08-16 | CI-2 | TC-ESC-049 |
| REQ-INT-009 | TCOND-15-02 | CI-1 | TC-CAL-003 |
| REQ-INT-009 | TCOND-15-02 | CI-2 | TC-CAL-004 |
| REQ-INT-010 | TCOND-14-06 | CI-1 | TC-INF-017 |
| REQ-INT-010 | TCOND-14-06 | CI-2 | TC-INF-018 |
| REQ-INT-010 | TCOND-14-06 | CI-3 | TC-INF-019 |
| REQ-INT-010 | TCOND-14-06 | CI-4 | TC-INF-020 |
| REQ-INT-010 | TCOND-14-06 | CI-5 | TC-INF-021 |
| REQ-INT-010 | TCOND-14-06 | CI-6 | TC-INF-022 |
| REQ-INT-015 | TCOND-19-02 | CI-1 | TC-EXT-006 |
| REQ-INT-015 | TCOND-19-02 | CI-2 | TC-EXT-007 |
| REQ-INT-015 | TCOND-19-02 | CI-3 | TC-EXT-008 |
| REQ-INT-015 | TCOND-19-02 | CI-4 | TC-EXT-009 |
| REQ-INT-015 | TCOND-19-02 | CI-5 | TC-EXT-010 |
| REQ-INT-016 | TCOND-19-03 | CI-1 | TC-EXT-011 |
| REQ-INT-016 | TCOND-19-03 | CI-2 | TC-EXT-012 |
| REQ-INT-016 | TCOND-19-03 | CI-3 | TC-EXT-013 |
| REQ-INT-017 | TCOND-19-04 | CI-1 | TC-EXT-014 |
| REQ-INT-017 | TCOND-19-04 | CI-2 | TC-EXT-015 |
| REQ-INT-017 | TCOND-19-04 | CI-3 | TC-EXT-016 |
| REQ-INT-018 | TCOND-19-05 | CI-1 | TC-EXT-017 |
| REQ-INT-018 | TCOND-19-05 | CI-2 | TC-EXT-018 |
| REQ-INT-018 | TCOND-19-05 | CI-3 | TC-EXT-019 |
| REQ-INT-018 | TCOND-19-05 | CI-4 | TC-EXT-020 |
| REQ-INT-019 | TCOND-08-17 | CI-1 | TC-ESC-050 |
| REQ-INT-019 | TCOND-08-17 | CI-2 | TC-ESC-051 |
| REQ-INT-019 | TCOND-08-17 | CI-3 | TC-ESC-052 (đã gỡ D12) |
| REQ-FUNC-001 | TCOND-10-01 | CI-1 | TC-GEN-001 |
| REQ-FUNC-001 | TCOND-10-02 | CI-1 | TC-GEN-002 |
| REQ-FUNC-001 | TCOND-10-03 | CI-1 | TC-GEN-003 |
| REQ-FUNC-001 | TCOND-10-03 | CI-2 | TC-GEN-004 |
| REQ-FUNC-001 | TCOND-10-03 | CI-3 | TC-GEN-005 |
| REQ-FUNC-002 | TCOND-14-01 | CI-1 | TC-INF-001 |
| REQ-FUNC-002 | TCOND-14-01 | CI-2 | TC-INF-002 |
| REQ-FUNC-002 | TCOND-14-01 | CI-3 | TC-INF-003 |
| REQ-FUNC-002 | TCOND-14-01 | CI-4 | TC-INF-004 |
| REQ-FUNC-002 | TCOND-14-01 | CI-5 | TC-INF-005 |
| REQ-FUNC-002 | TCOND-14-01 | CI-6 | TC-INF-006 |
| REQ-FUNC-002 | TCOND-14-02 | CI-1 | TC-INF-007 |
| REQ-FUNC-002 | TCOND-14-02 | CI-2 | TC-INF-008 |
| REQ-FUNC-002 | TCOND-14-03 | CI-1 | TC-INF-009 |
| REQ-FUNC-003 | TCOND-01-01 | CI-1 | TC-ATT-001 |
| REQ-FUNC-003 | TCOND-01-01 | CI-2 | TC-ATT-002 |
| REQ-FUNC-003 | TCOND-01-02 | CI-1 | TC-ATT-003 |
| REQ-FUNC-003 | TCOND-01-02 | CI-2 | TC-ATT-004 |
| REQ-FUNC-003 | TCOND-01-02 | CI-3 | TC-ATT-005 |
| REQ-FUNC-003 | TCOND-01-02 | CI-4 | TC-ATT-006 |
| REQ-FUNC-038 | TCOND-08-14 | CI-1 | TC-ESC-044 |
| REQ-FUNC-038 | TCOND-08-14 | CI-2 | TC-ESC-045 |
| REQ-FUNC-039 | TCOND-15-01 | CI-1 | TC-CAL-001 |
| REQ-FUNC-039 | TCOND-15-01 | CI-2 | TC-CAL-002 |
| REQ-FUNC-041 | TCOND-07-02 | CI-1 | TC-RET-008 |
| REQ-FUNC-041 | TCOND-07-02 | CI-2 | TC-RET-009 |
| REQ-FUNC-041 | TCOND-07-02 | CI-3 | TC-RET-010 |
| REQ-FUNC-041 | TCOND-07-02 | CI-4 | TC-RET-011 |
| REQ-FUNC-041 | TCOND-07-02 | CI-5 | TC-RET-012 |
| REQ-FUNC-004 | TCOND-01-06 | CI-1 | TC-ATT-019 |
| REQ-FUNC-004 | TCOND-01-06 | CI-2 | TC-ATT-020 |
| REQ-FUNC-004 | TCOND-01-06 | CI-3 | TC-ATT-021 |
| REQ-FUNC-004 | TCOND-01-06 | CI-4 | TC-ATT-022 |
| REQ-FUNC-004 | TCOND-01-06 | CI-5 | TC-ATT-027 |
| REQ-FUNC-005 | TCOND-13-01 | CI-1 | TC-CMP-001 |
| REQ-FUNC-005 | TCOND-13-01 | CI-2 | TC-CMP-002 |
| REQ-FUNC-005 | TCOND-13-01 | CI-3 | TC-CMP-003 |
| REQ-FUNC-005 | TCOND-13-01 | CI-4 | TC-CMP-004 |
| REQ-FUNC-005 | TCOND-13-01 | CI-5 | TC-CMP-005 |
| REQ-FUNC-042 | TCOND-13-02 | CI-1 | TC-CMP-006 |
| REQ-FUNC-042 | TCOND-13-02 | CI-2 | TC-CMP-007 |
| REQ-FUNC-042 | TCOND-13-02 | CI-3 | TC-CMP-008 |
| REQ-FUNC-042 | TCOND-13-02 | CI-4 | TC-CMP-009 |
| REQ-FUNC-006 | TCOND-01-03 | CI-1 | TC-ATT-007 |
| REQ-FUNC-006 | TCOND-01-03 | CI-2 | TC-ATT-008 |
| REQ-FUNC-006 | TCOND-01-03 | CI-3 | TC-ATT-009 |
| REQ-FUNC-006 | TCOND-01-03 | CI-4 | TC-ATT-010 |
| REQ-FUNC-006 | TCOND-01-03 | CI-5 | TC-ATT-011 |
| REQ-FUNC-007 | TCOND-01-04 | CI-1 | TC-ATT-012 |
| REQ-FUNC-007 | TCOND-01-04 | CI-2 | TC-ATT-013 |
| REQ-FUNC-007 | TCOND-01-04 | CI-3 | TC-ATT-014 |
| REQ-FUNC-007 | TCOND-01-04 | CI-4 | TC-ATT-015 |
| REQ-FUNC-007 | TCOND-01-04 | CI-5 | TC-ATT-016 |
| REQ-FUNC-008 | TCOND-04-01 | CI-1 | TC-CAN-001 |
| REQ-FUNC-008 | TCOND-04-01 | CI-2 | TC-CAN-002 |
| REQ-FUNC-008 | TCOND-04-01 | CI-3 | TC-CAN-003 |
| REQ-FUNC-008 | TCOND-04-01 | CI-4 | TC-CAN-004 |
| REQ-FUNC-008 | TCOND-04-01 | CI-5 | TC-CAN-005 |
| REQ-FUNC-008 | TCOND-04-01 | CI-6 | TC-CAN-006 |
| REQ-FUNC-008 | TCOND-05-03 | CI-1 | TC-MIS-006 |
| REQ-FUNC-009 | TCOND-01-05 | CI-1 | TC-ATT-017 |
| REQ-FUNC-009 | TCOND-01-05 | CI-2 | TC-ATT-018 |
| REQ-FUNC-009 | TCOND-03-04 | CI-1 | TC-BRE-009 |
| REQ-FUNC-009 | TCOND-03-04 | CI-2 | TC-BRE-010 |
| REQ-FUNC-009 | TCOND-03-04 | CI-3 | TC-BRE-011 |
| REQ-FUNC-009 | TCOND-03-04 | CI-4 | TC-BRE-012 |
| REQ-FUNC-010 | TCOND-04-02 | CI-1 | TC-CAN-007 |
| REQ-FUNC-010 | TCOND-04-02 | CI-2 | TC-CAN-008 |
| REQ-FUNC-010 | TCOND-04-02 | CI-3 | TC-CAN-009 |
| REQ-FUNC-010 | TCOND-04-02 | CI-4 | TC-CAN-010 |
| REQ-FUNC-010 | TCOND-04-02 | CI-5 | TC-CAN-011 |
| REQ-FUNC-011 | TCOND-02-01 | CI-1 | TC-PAU-001 |
| REQ-FUNC-011 | TCOND-02-01 | CI-2 | TC-PAU-002 |
| REQ-FUNC-011 | TCOND-02-01 | CI-3 | TC-PAU-003 |
| REQ-FUNC-037 | TCOND-02-02 | CI-1 | TC-PAU-004 |
| REQ-FUNC-037 | TCOND-02-02 | CI-2 | TC-PAU-005 |
| REQ-FUNC-048 | TCOND-02-03 | CI-1 | TC-PAU-006 |
| REQ-FUNC-048 | TCOND-02-03 | CI-2 | TC-PAU-007 |
| REQ-FUNC-048 | TCOND-02-03 | CI-3 | TC-PAU-008 |
| REQ-FUNC-012 | TCOND-04-03 | CI-1 | TC-CAN-012 |
| REQ-FUNC-012 | TCOND-04-03 | CI-2 | TC-CAN-013 |
| REQ-FUNC-012 | TCOND-04-03 | CI-3 | TC-CAN-014 |
| REQ-FUNC-012 | TCOND-04-03 | CI-4 | TC-CAN-015 |
| REQ-FUNC-012 | TCOND-04-03 | CI-5 | TC-CAN-016 |
| REQ-FUNC-012 | TCOND-04-03 | CI-6 | TC-CAN-017 |
| REQ-FUNC-012 | TCOND-04-03 | CI-7 | TC-CAN-018 |
| REQ-FUNC-012 | TCOND-04-03 | CI-8 | TC-CAN-019 |
| REQ-FUNC-012 | TCOND-04-03 | CI-9 | TC-CAN-032 |
| REQ-FUNC-013 | TCOND-04-04 | CI-1 | TC-CAN-020 |
| REQ-FUNC-013 | TCOND-04-04 | CI-2 | TC-CAN-021 |
| REQ-FUNC-013 | TCOND-04-04 | CI-3 | TC-CAN-022 |
| REQ-FUNC-013 | TCOND-04-04 | CI-4 | TC-CAN-023 |
| REQ-FUNC-013 | TCOND-04-04 | CI-5 | TC-CAN-024 |
| REQ-FUNC-050 | TCOND-04-05 | CI-1 | TC-CAN-025 |
| REQ-FUNC-050 | TCOND-04-05 | CI-2 | TC-CAN-026 |
| REQ-FUNC-050 | TCOND-04-05 | CI-3 | TC-CAN-027 |
| REQ-FUNC-050 | TCOND-04-05 | CI-4 | TC-CAN-028 |
| REQ-FUNC-051 | TCOND-04-06 | CI-1 | TC-CAN-029 |
| REQ-FUNC-051 | TCOND-04-06 | CI-2 | TC-CAN-030 |
| REQ-FUNC-051 | TCOND-04-06 | CI-3 | TC-CAN-031 |
| REQ-FUNC-014 | TCOND-09-01 | CI-1 | TC-MUL-001 |
| REQ-FUNC-014 | TCOND-09-01 | CI-2 | TC-MUL-002 |
| REQ-FUNC-014 | TCOND-09-01 | CI-3 | TC-MUL-003 |
| REQ-FUNC-014 | TCOND-09-01 | CI-4 | TC-MUL-004 |
| REQ-FUNC-014 | TCOND-09-01 | CI-5 | TC-MUL-005 |
| REQ-FUNC-014 | TCOND-09-02 | CI-1 | TC-MUL-006 |
| REQ-FUNC-014 | TCOND-09-02 | CI-2 | TC-MUL-007 |
| REQ-FUNC-014 | TCOND-09-02 | CI-3 | TC-MUL-008 |
| REQ-FUNC-015 | TCOND-01-07 | CI-1 | TC-ATT-023 |
| REQ-FUNC-015 | TCOND-01-07 | CI-2 | TC-ATT-024 |
| REQ-FUNC-016 | TCOND-05-01 | CI-1 | TC-MIS-001 |
| REQ-FUNC-016 | TCOND-05-01 | CI-2 | TC-MIS-002 |
| REQ-FUNC-016 | TCOND-05-01 | CI-3 | TC-MIS-003 |
| REQ-FUNC-016 | TCOND-05-02 | CI-1 | TC-MIS-004 |
| REQ-FUNC-016 | TCOND-05-02 | CI-2 | TC-MIS-005 |
| REQ-FUNC-016 | TCOND-05-03 | CI-1 | TC-MIS-006 |
| REQ-FUNC-016 | TCOND-05-03 | CI-2 | TC-MIS-007 |
| REQ-FUNC-016 | TCOND-05-03 | CI-3 | TC-MIS-008 |
| REQ-FUNC-017 | TCOND-07-01 | CI-1 | TC-RET-001 |
| REQ-FUNC-017 | TCOND-07-01 | CI-2 | TC-RET-002 |
| REQ-FUNC-017 | TCOND-07-01 | CI-3 | TC-RET-003 |
| REQ-FUNC-017 | TCOND-07-01 | CI-4 | TC-RET-004 |
| REQ-FUNC-017 | TCOND-07-01 | CI-5 | TC-RET-005 |
| REQ-FUNC-017 | TCOND-07-01 | CI-6 | TC-RET-006 |
| REQ-FUNC-017 | TCOND-07-01 | CI-7 | TC-RET-007 |
| REQ-FUNC-018 | TCOND-06-01 | CI-1 | TC-TIM-001 |
| REQ-FUNC-018 | TCOND-06-01 | CI-2 | TC-TIM-002 |
| REQ-FUNC-018 | TCOND-06-02 | CI-1 | TC-TIM-003 |
| REQ-FUNC-018 | TCOND-06-02 | CI-2 | TC-TIM-004 |
| REQ-FUNC-018 | TCOND-06-03 | CI-1 | TC-TIM-005 |
| REQ-FUNC-018 | TCOND-06-04 | CI-1 | TC-TIM-006 |
| REQ-FUNC-018 | TCOND-06-05 | CI-1 | TC-TIM-007 |
| REQ-FUNC-043 | TCOND-06-06 | CI-1 | TC-TIM-008 |
| REQ-FUNC-043 | TCOND-06-06 | CI-2 | TC-TIM-009 |
| REQ-FUNC-043 | TCOND-06-06 | CI-3 | TC-TIM-010 |
| REQ-FUNC-043 | TCOND-06-06 | CI-4 | TC-TIM-011 |
| REQ-FUNC-044 | TCOND-02-04 | CI-1 | TC-PAU-009 |
| REQ-FUNC-044 | TCOND-02-04 | CI-2 | TC-PAU-010 |
| REQ-FUNC-019 | TCOND-15-03 | CI-1 | TC-CAL-005 |
| REQ-FUNC-019 | TCOND-15-03 | CI-2 | TC-CAL-006 |
| REQ-FUNC-019 | TCOND-15-03 | CI-3 | TC-CAL-007 |
| REQ-FUNC-019 | TCOND-15-03 | CI-4 | TC-CAL-008 |
| REQ-FUNC-019 | TCOND-15-03 | CI-5 | TC-CAL-009 |
| REQ-FUNC-020 | TCOND-15-04 | CI-1 | TC-CAL-010 |
| REQ-FUNC-020 | TCOND-15-04 | CI-2 | TC-CAL-011 |
| REQ-FUNC-020 | TCOND-15-04 | CI-3 | TC-CAL-012 |
| REQ-FUNC-020 | TCOND-15-04 | CI-4 | TC-CAL-013 |
| REQ-FUNC-020 | TCOND-15-04 | CI-5 | TC-CAL-014 |
| REQ-FUNC-020 | TCOND-15-04 | CI-6 | TC-CAL-015 |
| REQ-FUNC-021 | TCOND-11-01 | CI-1 | TC-CHG-001 |
| REQ-FUNC-021 | TCOND-11-01 | CI-2 | TC-CHG-002 |
| REQ-FUNC-021 | TCOND-11-01 | CI-3 | TC-CHG-003 |
| REQ-FUNC-052 | TCOND-11-02 | CI-1 | TC-CHG-004 |
| REQ-FUNC-052 | TCOND-11-02 | CI-2 | TC-CHG-005 |
| REQ-FUNC-053 | TCOND-08-15 | CI-1 | TC-ESC-046 |
| REQ-FUNC-053 | TCOND-08-15 | CI-2 | TC-ESC-047 |
| REQ-FUNC-053 | TCOND-11-04 | CI-1 | TC-CHG-012 |
| REQ-FUNC-053 | TCOND-11-04 | CI-2 | TC-CHG-013 |
| REQ-FUNC-022 | TCOND-03-01 | CI-1 | TC-BRE-001 |
| REQ-FUNC-022 | TCOND-03-01 | CI-2 | TC-BRE-002 |
| REQ-FUNC-022 | TCOND-03-01 | CI-3 | TC-BRE-003 |
| REQ-FUNC-022 | TCOND-03-01 | CI-4 | TC-BRE-004 |
| REQ-FUNC-022 | TCOND-03-02 | CI-1 | TC-BRE-005 |
| REQ-FUNC-022 | TCOND-03-02 | CI-2 | TC-BRE-006 |
| REQ-FUNC-022 | TCOND-03-03 | CI-1 | TC-BRE-007 |
| REQ-FUNC-022 | TCOND-03-03 | CI-2 | TC-BRE-008 |
| REQ-FUNC-046 | TCOND-03-05 | CI-1 | TC-BRE-013 |
| REQ-FUNC-046 | TCOND-03-05 | CI-2 | TC-BRE-014 |
| REQ-FUNC-046 | TCOND-03-05 | CI-3 | TC-BRE-023 |
| REQ-FUNC-023 | TCOND-08-01 | CI-1 | TC-ESC-001 |
| REQ-FUNC-023 | TCOND-08-01 | CI-2 | TC-ESC-002 |
| REQ-FUNC-023 | TCOND-08-01 | CI-3 | TC-ESC-003 |
| REQ-FUNC-023 | TCOND-08-01 | CI-4 | TC-ESC-004 |
| REQ-FUNC-023 | TCOND-08-01 | CI-5 | TC-ESC-005 |
| REQ-FUNC-023 | TCOND-08-02 | CI-1 | TC-ESC-006 |
| REQ-FUNC-023 | TCOND-08-02 | CI-2 | TC-ESC-007 |
| REQ-FUNC-024 | TCOND-08-03 | CI-1 | TC-ESC-008 |
| REQ-FUNC-024 | TCOND-08-03 | CI-2 | TC-ESC-009 |
| REQ-FUNC-025 | TCOND-08-04 | CI-1 | TC-ESC-010 |
| REQ-FUNC-054 | TCOND-08-05 | CI-1 | TC-ESC-011 |
| REQ-FUNC-054 | TCOND-08-05 | CI-2 | TC-ESC-012 |
| REQ-FUNC-054 | TCOND-08-05 | CI-3 | TC-ESC-013 |
| REQ-FUNC-054 | TCOND-08-05 | CI-4 | TC-ESC-014 |
| REQ-FUNC-055 | TCOND-08-06 | CI-1 | TC-ESC-015 |
| REQ-FUNC-055 | TCOND-08-06 | CI-2 | TC-ESC-016 (đã gỡ D12) |
| REQ-FUNC-055 | TCOND-08-06 | CI-3 | TC-ESC-017 |
| REQ-FUNC-026 | TCOND-08-07 | CI-1 | TC-ESC-018 |
| REQ-FUNC-026 | TCOND-08-07 | CI-2 | TC-ESC-019 |
| REQ-FUNC-027 | TCOND-08-08 | CI-1 | TC-ESC-020 (đã gỡ D12) |
| REQ-FUNC-027 | TCOND-08-08 | CI-2 | TC-ESC-021 (đã gỡ D12) |
| REQ-FUNC-027 | TCOND-08-08 | CI-3 | TC-ESC-022 (đã gỡ D12) |
| REQ-FUNC-027 | TCOND-08-08 | CI-4 | TC-ESC-023 (đã gỡ D12) |
| REQ-FUNC-026 | TCOND-08-07 | CI-3 | TC-ESC-024 |
| REQ-FUNC-056 | TCOND-08-09 | CI-1 | TC-ESC-025 (đã gỡ D12) |
| REQ-FUNC-056 | TCOND-08-09 | CI-2 | TC-ESC-026 (đã gỡ D12) |
| REQ-FUNC-057 | TCOND-08-10 | CI-1 | TC-ESC-027 (đã gỡ D12) |
| REQ-FUNC-057 | TCOND-08-10 | CI-2 | TC-ESC-028 (đã gỡ D12) |
| REQ-FUNC-057 | TCOND-08-10 | CI-3 | TC-ESC-029 (đã gỡ D12) |
| REQ-FUNC-058 | TCOND-08-11 | CI-1 | TC-ESC-030 (đã gỡ D12) |
| REQ-FUNC-058 | TCOND-08-11 | CI-2 | TC-ESC-031 (đã gỡ D12) |
| REQ-FUNC-058 | TCOND-08-11 | CI-3 | TC-ESC-032 (đã gỡ D12) |
| REQ-FUNC-058 | TCOND-08-11 | CI-4 | TC-ESC-060 (đã gỡ D12) |
| REQ-FUNC-059 | TCOND-08-12 | CI-1 | TC-ESC-033 (đã gỡ D12) |
| REQ-FUNC-059 | TCOND-08-12 | CI-2 | TC-ESC-034 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-1 | TC-ESC-035 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-2 | TC-ESC-036 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-3 | TC-ESC-037 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-4 | TC-ESC-038 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-5 | TC-ESC-039 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-6 | TC-ESC-040 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-7 | TC-ESC-041 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-8 | TC-ESC-042 (đã gỡ D12) |
| REQ-FUNC-028 | TCOND-08-13 | CI-9 | TC-ESC-043 (đã gỡ D12) |
| REQ-FUNC-029 | TCOND-01-08 | CI-1 | TC-ATT-025 |
| REQ-FUNC-029 | TCOND-01-08 | CI-2 | TC-ATT-026 |
| REQ-FUNC-029 | TCOND-02-05 | CI-1 | TC-PAU-011 |
| REQ-FUNC-029 | TCOND-03-07 | CI-1 | TC-BRE-022 |
| REQ-FUNC-030 | TCOND-12-01 | CI-1 | TC-ERR-001 |
| REQ-FUNC-030 | TCOND-12-01 | CI-2 | TC-ERR-002 |
| REQ-FUNC-030 | TCOND-12-01 | CI-3 | TC-ERR-003 |
| REQ-FUNC-030 | TCOND-12-01 | CI-4 | TC-ERR-004 |
| REQ-FUNC-030 | TCOND-12-01 | CI-5 | TC-ERR-005 |
| REQ-FUNC-040 | TCOND-12-05 | CI-1 | TC-ERR-012 |
| REQ-FUNC-040 | TCOND-12-05 | CI-2 | TC-ERR-013 |
| REQ-FUNC-040 | TCOND-12-05 | CI-3 | TC-ERR-014 |
| REQ-FUNC-040 | TCOND-12-05 | CI-4 | TC-ERR-015 |
| REQ-FUNC-031 | TCOND-12-06 | CI-1 | TC-ERR-016 |
| REQ-FUNC-031 | TCOND-12-06 | CI-2 | TC-ERR-017 |
| REQ-FUNC-031 | TCOND-12-06 | CI-3 | TC-ERR-018 |
| REQ-FUNC-031 | TCOND-12-06 | CI-4 | TC-ERR-019 |
| REQ-FUNC-031 | TCOND-12-06 | CI-5 | TC-ERR-020 |
| REQ-FUNC-031 | TCOND-12-06 | CI-6 | TC-ERR-021 |
| REQ-FUNC-032 | TCOND-13-03 | CI-1 | TC-CMP-010 |
| REQ-FUNC-032 | TCOND-13-03 | CI-2 | TC-CMP-011 |
| REQ-FUNC-032 | TCOND-13-03 | CI-3 | TC-CMP-012 |
| REQ-FUNC-032 | TCOND-13-03 | CI-4 | TC-CMP-013 |
| REQ-FUNC-032 | TCOND-13-03 | CI-5 | TC-CMP-014 |
| REQ-FUNC-032 | TCOND-13-03 | CI-6 | TC-CMP-015 |
| REQ-FUNC-032 | TCOND-13-03 | CI-7 | TC-CMP-016 |
| REQ-FUNC-033 | TCOND-11-05 | CI-1 | TC-CHG-015 |
| REQ-FUNC-033 | TCOND-11-05 | CI-2 | TC-CHG-016 |
| REQ-FUNC-033 | TCOND-11-05 | CI-3 | TC-CHG-017 |
| REQ-FUNC-060 | TCOND-11-06 | CI-1 | TC-CHG-018 |
| REQ-FUNC-060 | TCOND-11-06 | CI-2 | TC-CHG-019 |
| REQ-FUNC-060 | TCOND-11-06 | CI-3 | TC-CHG-020 |
| REQ-FUNC-060 | TCOND-11-06 | CI-4 | TC-CHG-021 |
| REQ-FUNC-060 | TCOND-11-06 | CI-5 | TC-CHG-022 |
| REQ-FUNC-060 | TCOND-11-06 | CI-6 | TC-CHG-023 |
| REQ-FUNC-061 | TCOND-11-07 | CI-1 | TC-CHG-024 |
| REQ-FUNC-061 | TCOND-11-07 | CI-2 | TC-CHG-025 |
| REQ-FUNC-061 | TCOND-11-07 | CI-3 | TC-CHG-026 |
| REQ-FUNC-061 | TCOND-11-07 | CI-4 | TC-CHG-027 |
| REQ-FUNC-034 | TCOND-14-04 | CI-1 | TC-INF-010 |
| REQ-FUNC-034 | TCOND-14-04 | CI-2 | TC-INF-011 |
| REQ-FUNC-034 | TCOND-14-04 | CI-3 | TC-INF-012 |
| REQ-FUNC-035 | TCOND-14-05 | CI-1 | TC-INF-013 |
| REQ-FUNC-035 | TCOND-14-05 | CI-2 | TC-INF-014 |
| REQ-FUNC-035 | TCOND-14-05 | CI-3 | TC-INF-015 |
| REQ-FUNC-035 | TCOND-14-05 | CI-4 | TC-INF-016 |
| REQ-FUNC-036 | TCOND-17-12 | CI-1 | TC-UIX-039 |
| REQ-FUNC-036 | TCOND-17-12 | CI-2 | TC-UIX-040 |
| REQ-FUNC-036 | TCOND-17-12 | CI-3 | TC-UIX-041 |
| REQ-FUNC-062 | TCOND-17-13 | CI-1 | TC-UIX-042 |
| REQ-FUNC-062 | TCOND-17-13 | CI-2 | TC-UIX-043 |
| REQ-FUNC-062 | TCOND-17-13 | CI-3 | TC-UIX-044 |
| REQ-PERF-001 | TCOND-18-01 | CI-1 | TC-PRF-001 |
| REQ-PERF-001 | TCOND-18-01 | CI-2 | TC-PRF-002 |
| REQ-PERF-001 | TCOND-18-01 | CI-3 | TC-PRF-010 |
| REQ-PERF-002 | TCOND-18-02 | CI-1 | TC-PRF-003 |
| REQ-PERF-002 | TCOND-18-02 | CI-2 | TC-PRF-004 |
| REQ-PERF-002 | TCOND-18-02 | CI-3 | TC-PRF-005 |
| REQ-PERF-003 | TCOND-18-03 | CI-1 | TC-PRF-006 |
| REQ-PERF-003 | TCOND-18-03 | CI-2 | TC-PRF-007 |
| REQ-PERF-003 | TCOND-18-03 | CI-3 | TC-PRF-008 |
| REQ-PERF-003 | TCOND-18-03 | CI-4 | TC-PRF-009 |
| REQ-SEC-001 | TCOND-16-01 | CI-1 | TC-SEC-001 |
| REQ-SEC-001 | TCOND-16-01 | CI-2 | TC-SEC-002 |
| REQ-SEC-001 | TCOND-16-01 | CI-3 | TC-SEC-003 |
| REQ-SEC-001 | TCOND-16-01 | CI-4 | TC-SEC-004 |
| REQ-SEC-001 | TCOND-16-01 | CI-5 | TC-SEC-005 |
| REQ-SEC-001 | TCOND-16-01 | CI-6 | TC-SEC-024 |
| REQ-SEC-002 | TCOND-16-02 | CI-1 | TC-SEC-006 |
| REQ-SEC-002 | TCOND-16-02 | CI-2 | TC-SEC-007 |
| REQ-SEC-003 | TCOND-16-03 | CI-1 | TC-SEC-008 |
| REQ-SEC-003 | TCOND-16-03 | CI-2 | TC-SEC-009 |
| REQ-SEC-003 | TCOND-16-03 | CI-3 | TC-SEC-010 |
| REQ-SEC-003 | TCOND-16-03 | CI-4 | TC-SEC-011 |
| REQ-SEC-003 | TCOND-16-03 | CI-5 | TC-SEC-012 |
| REQ-SEC-004 | TCOND-16-04 | CI-1 | TC-SEC-013 |
| REQ-SEC-004 | TCOND-16-04 | CI-2 | TC-SEC-014 (đã gỡ D12) |
| REQ-SEC-004 | TCOND-16-04 | CI-3 | TC-SEC-015 |
| REQ-SEC-005 | TCOND-16-05 | CI-1 | TC-SEC-016 |
| REQ-SEC-005 | TCOND-16-05 | CI-2 | TC-SEC-017 |
| REQ-SEC-006 | TCOND-16-06 | CI-1 | TC-SEC-018 |
| REQ-SEC-006 | TCOND-16-06 | CI-2 | TC-SEC-019 |
| REQ-SEC-006 | TCOND-16-06 | CI-3 | TC-SEC-020 |
| REQ-SEC-006 | TCOND-16-06 | CI-4 | TC-SEC-021 |
| REQ-SEC-006 | TCOND-16-06 | CI-5 | TC-SEC-022 |
| REQ-SEC-006 | TCOND-16-06 | CI-6 | TC-SEC-023 |
| REQ-REL-001 | TCOND-12-01 | CI-5 | TC-ERR-005 |
| REQ-REL-001 | TCOND-12-08 | CI-1 | TC-ERR-026 |
| REQ-REL-001 | TCOND-12-08 | CI-2 | TC-ERR-027 |
| REQ-REL-001 | TCOND-12-08 | CI-3 | TC-ERR-028 |
| REQ-REL-002 | TCOND-08-18 | CI-1 | TC-ESC-053 |
| REQ-REL-002 | TCOND-08-18 | CI-2 | TC-ESC-054 |
| REQ-REL-002 | TCOND-08-18 | CI-3 | TC-ESC-055 |
| REQ-REL-002 | TCOND-08-18 | CI-4 | TC-ESC-056 |
| REQ-REL-002 | TCOND-08-18 | CI-5 | TC-ESC-057 |
| REQ-REL-002 | TCOND-08-18 | CI-6 | TC-ESC-058 |
| REQ-REL-002 | TCOND-08-18 | CI-7 | TC-ESC-059 |
| REQ-REL-002 | TCOND-12-09 | CI-1 | TC-ERR-029 |
| REQ-OBS-001 | TCOND-12-02 | CI-1 | TC-ERR-006 |
| REQ-OBS-001 | TCOND-12-02 | CI-2 | TC-ERR-007 |
| REQ-OBS-002 | TCOND-12-03 | CI-1 | TC-ERR-008 |
| REQ-OBS-003 | TCOND-12-04 | CI-1 | TC-ERR-009 |
| REQ-OBS-003 | TCOND-12-04 | CI-2 | TC-ERR-010 |
| REQ-OBS-003 | TCOND-12-04 | CI-3 | TC-ERR-011 |
| REQ-INST-001 | TCOND-14-07 | CI-1 | TC-INF-023 |
| REQ-INST-001 | TCOND-14-07 | CI-2 | TC-INF-024 |
| REQ-INST-001 | TCOND-14-07 | CI-3 | TC-INF-025 |
| REQ-INST-001 | TCOND-14-07 | CI-4 | TC-INF-026 |
| REQ-INST-001 | TCOND-14-07 | CI-5 | TC-INF-035 |
| REQ-INST-002 | TCOND-INS-01 | CI-1 | TC-INS-001 |
| REQ-INST-002 | TCOND-INS-01 | CI-2 | TC-INS-002 |
| REQ-INST-003 | TCOND-14-08 | CI-1 | TC-INF-027 |
| REQ-INST-003 | TCOND-14-08 | CI-2 | TC-INF-028 |
| REQ-INST-003 | TCOND-14-08 | CI-3 | TC-INF-029 |
| REQ-INST-004 | TCOND-14-09 | CI-1 | TC-INF-030 |
| REQ-INST-004 | TCOND-14-09 | CI-2 | TC-INF-031 |
| REQ-INST-004 | TCOND-14-09 | CI-3 | TC-INF-032 |
| REQ-BUILD-001 | TCOND-INS-02 | CI-1 | TC-INS-003 |
| REQ-BUILD-001 | TCOND-INS-02 | CI-2 | TC-INS-004 |
| REQ-BUILD-001 | TCOND-INS-02 | CI-3 | TC-INS-005 |
| REQ-MAINT-001 | TCOND-INS-03 | CI-1 | TC-INS-006 |
| REQ-MAINT-001 | TCOND-INS-03 | CI-2 | TC-INS-007 |
| REQ-MAINT-001 | TCOND-INS-03 | CI-3 | TC-INS-008 |
| REQ-MAINT-001 | TCOND-INS-03 | CI-4 | TC-INS-009 |
| REQ-MAINT-001 | TCOND-INS-03 | CI-5 | TC-INS-010 |
| REQ-MAINT-002 | TCOND-INS-04 | CI-1 | TC-INS-011 |
| REQ-MAINT-002 | TCOND-INS-04 | CI-2 | TC-INS-012 |
| REQ-MAINT-002 | TCOND-INS-04 | CI-3 | TC-INS-013 |
| REQ-MAINT-002 | TCOND-INS-04 | CI-4 | TC-INS-014 |
| REQ-REUSE-001 | TCOND-19-06 | CI-1 | TC-EXT-021 |
| REQ-REUSE-001 | TCOND-19-06 | CI-2 | TC-EXT-022 |
| REQ-REUSE-001 | TCOND-19-06 | CI-3 | TC-EXT-023 |
| REQ-PORT-001 | TCOND-14-10 | CI-1 | TC-INF-033 |
| REQ-PORT-001 | TCOND-14-10 | CI-2 | TC-INF-034 |
| REQ-CM-001 | TCOND-INS-05 | CI-1 | TC-INS-015 |
| REQ-CM-001 | TCOND-INS-05 | CI-2 | TC-INS-016 |
| REQ-CM-001 | TCOND-INS-05 | CI-3 | TC-INS-017 |

## 7. Bổ sung 19.0.1.1.0: Feature FT-20 đến FT-31 và test condition mới của FT-03 đến FT-18

Convention: `TCOND-<FT>-<NN>`; với FT-01 đến FT-19 số FT trùng số TG, với FT-20 đến FT-31 số FT khác số TG (ánh xạ ở mục 2). Mỗi coverage item sinh đúng một test case ở `060` (cột Test Case). Kỹ thuật chọn cho từng Feature nằm ở mục 3.

### 7.1. Test condition mới của FT-03 đến FT-18

#### TCOND-03-24 — Task paused không bị so với hạn chót

**Feature:** FT-03 | **REQ-ID:** REQ-FUNC-022 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Task `paused` không bị xử lý nền so với `planned_end_time` | TC-BRE-024 |

#### TCOND-03-25 — Phần trăm đã dùng của task đang chạy tại thời điểm xem

**Feature:** FT-03 | **REQ-ID:** REQ-INT-023 | **Technique:** BVA

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Phần trăm đã dùng của task đang chạy tính cả đoạn đang chạy | TC-BRE-025 |

#### TCOND-03-26 — Tính hàng loạt thời gian đã trôi bằng tính từng task

**Feature:** FT-03 | **REQ-ID:** REQ-INT-023, REQ-PERF-002 | **Technique:** EP (so sánh hai đường tính)

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | `settle_batch` cho kết quả bằng `settle` từng task | TC-BRE-026 |

#### TCOND-08-70 — process_due: task đến hạn và chưa đến hạn

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-022, REQ-REL-002 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | `process_due` xử lý task đến hạn | TC-PRC-001 |
| CI-2 | `process_due` bỏ qua task chưa đến hạn | TC-PRC-002 |

#### TCOND-08-71 — process_due: trần batch_size mỗi lần gọi

**Feature:** FT-08 | **REQ-ID:** REQ-REL-002 | **Technique:** BVA

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | `batch_size` là trần mỗi lần gọi `process_due` | TC-PRC-003 |

#### TCOND-08-72 — Escalation email: bốn cách resolve người nhận

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-064, REQ-FUNC-065 | **Technique:** Decision Table

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Mốc email người nhận `fixed` gửi tới địa chỉ cố định | TC-EML-001 |
| CI-2 | Người nhận `field` đọc field email của record gốc | TC-EML-002 |
| CI-3 | Người nhận `responsible` lấy email của user/partner ở field Many2one | TC-EML-003 |
| CI-4 | `responsible` trên field x2many: một mail, nhiều người nhận | TC-EML-004 |

#### TCOND-08-73 — Escalation email: không resolve được người nhận

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-026, REQ-FUNC-065 | **Technique:** Error Guessing

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Không resolve được người nhận: `escalate_failed`, không ném lỗi ra ngoài | TC-EML-005 |

#### TCOND-08-74 — Escalation email: mẫu email mặc định và mẫu sai model

**Feature:** FT-08 | **REQ-ID:** REQ-FUNC-064 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Không có template: dùng nội dung mặc định | TC-EML-006 |
| CI-2 | Template không thuộc model `sla.task` bị từ chối khi lưu | TC-EML-007 |

#### TCOND-12-30 — Ngoại lệ gốc trích giá trị field không lọt vào nhật ký

**Feature:** FT-12 | **REQ-ID:** REQ-FUNC-026, REQ-OBS-003 | **Technique:** Error Guessing

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Exception gốc trích giá trị field: ghi chú và log chỉ còn `<redacted>` | TC-ERR-030 |

#### TCOND-13-17 — Điều kiện start dùng field related không lưu

**Feature:** FT-13 | **REQ-ID:** REQ-FUNC-005, REQ-FUNC-042 | **Technique:** Error Guessing (hồi quy)

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Điều kiện start dùng field related không lưu vẫn gắn task khi field nguồn đổi | TC-CMP-017 |

#### TCOND-14-36 — Ràng buộc RESTRICT khi xóa công ty hoặc lịch đang dùng

**Feature:** FT-14 | **REQ-ID:** REQ-FUNC-001 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Không xoá được công ty hoặc lịch đang được định nghĩa dùng (RESTRICT) | TC-INF-036 |

#### TCOND-14-37 — Index từng phần của next_due_at

**Feature:** FT-14 | **REQ-ID:** REQ-PERF-003 | **Technique:** Inspection tự động

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | `next_due_at` chỉ có một index từng phần | TC-INF-037 |

#### TCOND-16-25 — Quản trị hệ thống mặc định là SLA Manager

**Feature:** FT-16 | **REQ-ID:** REQ-SEC-001 | **Technique:** Decision Table

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Quản trị hệ thống mặc định là SLA Manager | TC-SEC-025 |

#### TCOND-18-11 — Tải 300 ticket x 30 task (opt-in)

**Feature:** FT-18 | **REQ-ID:** REQ-PERF-001, REQ-PERF-002, REQ-REL-002 | **Technique:** Performance

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Tải 300 ticket x 30 task (opt-in `SLA_PERF=1`) | TC-PRF-011 |

#### TCOND-18-12 — Đọc phần trăm đã dùng của 80 task một trang list (opt-in)

**Feature:** FT-18 | **REQ-ID:** REQ-INT-023, REQ-PERF-002 | **Technique:** Performance

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Đọc `business_percent_used` của 80 task (một trang list), có lịch và không lịch | TC-PRF-012 |
| CI-2 | Như TC-PRF-012 với lịch có ngày nghỉ lễ và task chạy 120 ngày | TC-PRF-013 |

### 7.2. FT-20 / TG-25 — Bật/tắt định nghĩa, `[]` là chưa cấu hình, timezone bắt buộc

#### TCOND-20-01 — Mặc định tắt khi tạo mới

**Feature:** FT-20 | **REQ-ID:** REQ-FUNC-066 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Định nghĩa tạo mới không truyền `active`: mặc định tắt, start là `[]` | TC-ENB-001 |

#### TCOND-20-02 — model_name có ngay khi tạo và theo model_id

**Feature:** FT-20 | **REQ-ID:** REQ-FUNC-001, REQ-INT-001 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | `model_name` là related có lưu, theo `model_id` | TC-ENB-002 |

#### TCOND-20-03 — Enable/Disable và cảnh báo khi start chưa cấu hình

**Feature:** FT-20 | **REQ-ID:** REQ-FUNC-066 | **Technique:** State Transition

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Enable/Disable đảo `active` và trả về soft reload | TC-ENB-003 |
| CI-2 | Enable khi start chưa cấu hình: bật được kèm cảnh báo | TC-ENB-004 |

#### TCOND-20-04 — Chỉ định nghĩa đã bật mới gắn task

**Feature:** FT-20 | **REQ-ID:** REQ-FUNC-066 | **Technique:** State Transition

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Định nghĩa đã bật gắn task cho record mới, định nghĩa tắt thì không | TC-ENB-005 |

#### TCOND-20-05 — Định nghĩa tắt: còn task chạy thì vẫn đánh giá, hết task thì không

**Feature:** FT-20 | **REQ-ID:** REQ-FUNC-060, REQ-FUNC-066, REQ-PERF-001 | **Technique:** State Transition + Decision Table

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Định nghĩa tắt còn task đang chạy: model vẫn được patch; hết task thì gỡ | TC-ENB-006 |
| CI-2 | Định nghĩa tắt, không có task đang chạy: engine không so khớp điều kiện | TC-ENB-007 |
| CI-3 | Định nghĩa tắt nhưng còn task đang chạy: vẫn đánh giá, task kết thúc khi stop khớp | TC-ENB-008 |

#### TCOND-20-06 — Domain `[]` là chưa cấu hình, domain luôn đúng khớp mọi record

**Feature:** FT-20 | **REQ-ID:** REQ-FUNC-003 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | `_get_domain` trả `None` cho `[]`, domain thật cho điều kiện đã cấu hình | TC-CND-001 |
| CI-2 | Start `[]` không bao giờ gắn task | TC-CND-002 |
| CI-3 | Start `MATCH_ALL` gắn task cho mọi record | TC-CND-003 |
| CI-4 | Stop `[]` không bao giờ kết thúc task | TC-CND-004 |

#### TCOND-20-07 — Hook theo dõi field: không đặt `*` khi mọi điều kiện `[]`

**Feature:** FT-20 | **REQ-ID:** REQ-FUNC-003, REQ-FUNC-013, REQ-FUNC-051, REQ-PERF-001 | **Technique:** Decision Table

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Mọi điều kiện `[]`: hook không đặt dấu `*` (không chạy engine ở mỗi lần ghi) | TC-CND-005 |
| CI-2 | Điều kiện reset có domain nhưng không có field theo dõi: theo dõi mọi field (`*`) | TC-CND-006 |

#### TCOND-20-08 — Điền sẵn timezone khi tạo

**Feature:** FT-20 | **REQ-ID:** REQ-FUNC-067 | **Technique:** Decision Table

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Tạo định nghĩa không truyền timezone: điền tz của người dùng hoặc `UTC` | TC-TZR-001 |
| CI-2 | Nguồn `definition` với lịch cố định: điền tz của lịch | TC-TZR-002 |
| CI-3 | Timezone truyền tường minh được giữ nguyên | TC-TZR-003 |

#### TCOND-20-09 — Onchange timezone theo lịch

**Feature:** FT-20 | **REQ-ID:** REQ-FUNC-067 | **Technique:** Decision Table

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Onchange trên bản ghi chưa lưu: luôn lấy tz của lịch | TC-TZR-004 |
| CI-2 | Onchange trên bản ghi đã lưu: chỉ điền khi tz đang trống | TC-TZR-005 |
| CI-3 | Onchange bỏ qua nguồn không phải `definition` | TC-TZR-006 |

#### TCOND-20-10 — Form mới: timezone mặc định và theo lịch

**Feature:** FT-20 | **REQ-ID:** REQ-FUNC-067 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Form mới có sẵn tz mặc định và theo tz lịch khi chọn lịch | TC-TZR-007 |

#### TCOND-20-11 — Bản sao lịch theo timezone sao chép ngày nghỉ chung

**Feature:** FT-20 | **REQ-ID:** REQ-FUNC-067 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Bản sao calendar theo tz sao chép ngày nghỉ chung | TC-TZR-008 |

#### TCOND-20-12 — Đổi timezone không đổi hạn task đang chạy

**Feature:** FT-20 | **REQ-ID:** REQ-FUNC-021, REQ-FUNC-067 | **Technique:** State Transition

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Đổi timezone định nghĩa không đổi hạn của task đang chạy | TC-TZR-009 |

### 7.3. FT-21 / TG-26 — Giao diện định nghĩa và task: due soon theo định nghĩa, khóa model, audit, nút Running Tasks, list, Open Source Record

#### TCOND-21-01 — Ngưỡng Sắp đến hạn: định nghĩa trước, Settings sau

**Feature:** FT-21 | **REQ-ID:** REQ-INT-012 | **Technique:** EP + BVA

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Sắp đến hạn theo ngưỡng riêng của định nghĩa, nếu trống theo Settings | TC-DUE-001 |
| CI-2 | Đổi Settings chỉ tác động định nghĩa chưa đặt ngưỡng riêng | TC-DUE-002 |

#### TCOND-21-02 — Tìm kiếm is_due_soon theo toán tử và loại trừ paused/vi phạm

**Feature:** FT-21 | **REQ-ID:** REQ-INT-012 | **Technique:** Decision Table

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Tìm kiếm `is_due_soon` đúng với các toán tử `=`, `!=`, `in`, `not in` | TC-DUE-003 |
| CI-2 | Task paused hoặc đã vi phạm không bao giờ "sắp đến hạn" | TC-DUE-004 |

#### TCOND-21-03 — due_soon_hours âm

**Feature:** FT-21 | **REQ-ID:** REQ-INT-012 | **Technique:** BVA

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | `due_soon_hours` âm bị CSDL từ chối | TC-DUE-005 |

#### TCOND-21-04 — Khóa model_id khi đã có task

**Feature:** FT-21 | **REQ-ID:** REQ-FUNC-069 | **Technique:** Decision Table

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Định nghĩa đã có task không đổi được model | TC-LCK-001 |
| CI-2 | Ghi lại cùng model (kèm sửa field khác) vẫn được khi đã có task | TC-LCK-002 |
| CI-3 | Định nghĩa chưa có task đổi model được | TC-LCK-003 |

#### TCOND-21-05 — Dấu vết thay đổi định nghĩa (chatter)

**Feature:** FT-21 | **REQ-ID:** REQ-FUNC-069 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Đổi `duration` sinh dấu vết trong chatter | TC-AUD-001 |
| CI-2 | Đổi điều kiện (`stop_domain`) được theo dõi | TC-AUD-002 |
| CI-3 | Form định nghĩa có chatter | TC-AUD-003 |

#### TCOND-21-06 — Đếm task đang chạy của định nghĩa

**Feature:** FT-21 | **REQ-ID:** REQ-INT-025 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Số task đang chạy đếm `in_progress` và `paused`, không đếm task đã đóng | TC-SBT-001 |
| CI-2 | Định nghĩa không có task: số đếm bằng 0 | TC-SBT-002 |

#### TCOND-21-07 — Nút Running Tasks

**Feature:** FT-21 | **REQ-ID:** REQ-FUNC-069, REQ-INT-025 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Nút Running Tasks mở mọi task của đúng định nghĩa | TC-SBT-003 |
| CI-2 | Form định nghĩa có nút `action_view_tasks` trong button box và `js_class` | TC-SBT-004 |

#### TCOND-21-08 — List định nghĩa

**Feature:** FT-21 | **REQ-ID:** REQ-FUNC-066 | **Technique:** Inspection arch

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | List định nghĩa: mờ khi tắt, nút Enable/Disable có xác nhận, cột mặc định | TC-DLV-001 |
| CI-2 | Action của list hiện cả định nghĩa tắt và không nhóm sẵn | TC-DLV-002 |

#### TCOND-21-09 — Lịch sử escalation trên form task

**Feature:** FT-21 | **REQ-ID:** REQ-INT-026 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Tab Escalation của task chỉ liệt kê event `escalate` và `escalate_failed` | TC-EHS-001 |
| CI-2 | Lịch sử escalation sắp mới nhất trước | TC-EHS-002 |
| CI-3 | Form task hiển thị lịch sử escalation với 3 cột | TC-EHS-003 |

#### TCOND-21-10 — Nút Open Source Record

**Feature:** FT-21 | **REQ-ID:** REQ-INT-026 | **Technique:** EP + Error Guessing

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Nút Open Source Record mở form của record gốc | TC-OSR-001 |
| CI-2 | Record gốc đã bị xoá: báo lỗi thân thiện | TC-OSR-002 |
| CI-3 | Model của record gốc không còn tồn tại: báo lỗi thân thiện | TC-OSR-003 |
| CI-4 | Nút nằm trong header của form task, luôn hiện, không có trong list | TC-OSR-004 |

#### TCOND-21-11 — Cột mặc định của list task

**Feature:** FT-21 | **REQ-ID:** REQ-INT-027 | **Technique:** Inspection arch

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | List task: cột mặc định, thanh tiến độ, tô đỏ task vi phạm | TC-TLV-001 |

#### TCOND-21-12 — Widget chỉ có light mode

**Feature:** FT-21 | **REQ-ID:** REQ-INT-024 | **Technique:** Inspection

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | SCSS của widget chỉ có light mode | TC-LGT-001 |

#### TCOND-21-13 — Hộp xác nhận khi lưu định nghĩa có task đang chạy

**Feature:** FT-21 | **REQ-ID:** REQ-FUNC-069 | **Technique:** Demonstration tự động (tour)

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Tour trình duyệt: lưu định nghĩa có task đang chạy hiện hộp xác nhận | TC-TOUR-001 |

### 7.4. FT-22 / TG-27 — Re-check Conditions giới hạn một định nghĩa

#### TCOND-22-01 — Re-check giới hạn một định nghĩa

**Feature:** FT-22 | **REQ-ID:** REQ-FUNC-032, REQ-INT-020 | **Technique:** Decision Table

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Re-check task của B không đụng task của A và không gắn task của định nghĩa C | TC-RCK-001 |

#### TCOND-22-02 — Re-check task đã đóng và ghi event

**Feature:** FT-22 | **REQ-ID:** REQ-INT-020 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Task đã đóng không đổi nhưng vẫn ghi event `reevaluate` kèm người bấm | TC-RCK-002 |
| CI-2 | Task đổi stage: event ghi stage cũ và mới | TC-RCK-003 |

#### TCOND-22-03 — Re-check nhiều task thuộc nhiều định nghĩa

**Feature:** FT-22 | **REQ-ID:** REQ-INT-020 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Nhiều task thuộc hai định nghĩa trong một lần bấm: mỗi task theo định nghĩa của nó | TC-RCK-004 |

#### TCOND-22-04 — Phân quyền Re-check

**Feature:** FT-22 | **REQ-ID:** REQ-FUNC-032, REQ-INT-020 | **Technique:** Decision Table

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | SLA User không dùng được Re-check | TC-RCK-005 |

#### TCOND-22-05 — Tham số definitions của engine

**Feature:** FT-22 | **REQ-ID:** REQ-FUNC-032 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | `Engine.evaluate(definitions=...)` chỉ xét định nghĩa được truyền | TC-RCK-006 |

### 7.5. FT-23 / TG-28 — Apply Current Settings ghi event và báo kết quả

#### TCOND-23-01 — Apply Current Settings trên task đang chạy

**Feature:** FT-23 | **REQ-ID:** REQ-INT-005 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Task đang chạy nhận mục tiêu mới, ghi event `recalculate`, báo kết quả | TC-APS-001 |

#### TCOND-23-02 — Apply Current Settings trên task đã vi phạm

**Feature:** FT-23 | **REQ-ID:** REQ-INT-005 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Task đã vi phạm giữ nguyên hạn chót | TC-APS-002 |

#### TCOND-23-03 — Apply Current Settings trên task paused

**Feature:** FT-23 | **REQ-ID:** REQ-INT-005 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Task paused đổi mục tiêu nhưng giữ hạn chót (xếp lại khi resume) | TC-APS-003 |

#### TCOND-23-04 — Apply Current Settings khi không có gì đổi

**Feature:** FT-23 | **REQ-ID:** REQ-INT-005 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Task không có gì đổi: không ghi event nhưng vẫn tính vào "updated" | TC-APS-004 |

#### TCOND-23-05 — Apply Current Settings trên task đã đóng

**Feature:** FT-23 | **REQ-ID:** REQ-INT-005 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Task đã đóng bị bỏ qua | TC-APS-005 |

#### TCOND-23-06 — Apply Current Settings trên nhiều task

**Feature:** FT-23 | **REQ-ID:** REQ-INT-005 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Nhiều task trong một lần bấm: mỗi task đúng một event | TC-APS-006 |

### 7.6. FT-24 / TG-29 — Apply to Existing Records: wizard, job theo lô, cron, hủy, dọn, backfill escalation

#### TCOND-24-01 — Áp dụng cho record có sẵn

**Feature:** FT-24 | **REQ-ID:** REQ-FUNC-068 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Áp dụng cho record có sẵn: đủ task, chạy lại không tạo trùng | TC-APX-001 |

#### TCOND-24-02 — Domain lọc giao với điều kiện start

**Feature:** FT-24 | **REQ-ID:** REQ-FUNC-068 | **Technique:** Decision Table

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Domain lọc thu hẹp tập record | TC-APX-002 |
| CI-2 | Domain lọc không mở rộng được điều kiện Start | TC-APX-003 |

#### TCOND-24-03 — Start chưa cấu hình và định nghĩa tắt

**Feature:** FT-24 | **REQ-ID:** REQ-FUNC-003, REQ-FUNC-068 | **Technique:** Error Guessing

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Start chưa cấu hình (`[]`): job không nạp record nào | TC-APX-004 |
| CI-2 | Định nghĩa đang tắt: từ chối áp dụng | TC-APX-005 |

#### TCOND-24-04 — Chia lô và chặn job song song

**Feature:** FT-24 | **REQ-ID:** REQ-FUNC-068, REQ-REL-002 | **Technique:** BVA + State Transition

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Chia lô: lô đầu chạy ngay, phần còn lại do cron, không xử lý trùng | TC-APX-006 |
| CI-2 | Job `queued` cũng chặn tạo job mới cùng định nghĩa | TC-APX-007 |

#### TCOND-24-05 — Hủy job và job lỗi

**Feature:** FT-24 | **REQ-ID:** REQ-FUNC-068 | **Technique:** State Transition

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Hủy job: dừng xử lý, cho phép tạo job mới | TC-APX-008 |
| CI-2 | Lô lỗi làm job `failed` kèm ghi chú | TC-APX-009 |

#### TCOND-24-06 — Dọn job cũ

**Feature:** FT-24 | **REQ-ID:** REQ-FUNC-068, REQ-INT-010 | **Technique:** BVA

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Autovacuum xoá job đã kết thúc quá hạn lưu, giữ job đang chạy/chờ/mới | TC-APX-010 |

#### TCOND-24-07 — Backfill không bắn hồi tố escalation

**Feature:** FT-24 | **REQ-ID:** REQ-FUNC-053, REQ-FUNC-068 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Backfill retroactive: mốc escalation đã vượt được đánh dấu xong, không bắn hồi tố | TC-APX-011 |

#### TCOND-24-08 — Phân quyền wizard và job

**Feature:** FT-24 | **REQ-ID:** REQ-FUNC-068, REQ-SEC-001 | **Technique:** Decision Table

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Phân quyền: chỉ SLA Manager tạo wizard và sửa job | TC-APX-012 |

### 7.7. FT-25 / TG-30 — Chip trạng thái trên form record gốc

#### TCOND-25-01 — Chip: không có trạng thái để hiện

**Feature:** FT-25 | **REQ-ID:** REQ-INT-024 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Record chưa có task: `state` rỗng | TC-FST-001 |
| CI-2 | `res_id` rỗng: trả `{'state': None}` | TC-FST-002 |
| CI-3 | Chỉ có task `cancelled`: không có trạng thái | TC-FST-009 |

#### TCOND-25-02 — Chip: các trạng thái của một task

**Feature:** FT-25 | **REQ-ID:** REQ-INT-012, REQ-INT-024 | **Technique:** State Transition

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Task đang chạy, chưa trễ: `state` = `running` | TC-FST-003 |
| CI-2 | Hạn trong ngưỡng Sắp đến hạn: `state` = `due_soon` | TC-FST-004 |
| CI-3 | Task paused: `state` = `paused`, `percent` theo thời gian đã dùng | TC-FST-005 |
| CI-4 | Task đã `achieved`: `state` = `met` | TC-FST-007 |
| CI-5 | Task đã `breached` (đóng trễ): `state` = `missed` | TC-FST-008 |

#### TCOND-25-03 — Chip: percent không vượt 100

**Feature:** FT-25 | **REQ-ID:** REQ-INT-024 | **Technique:** BVA

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Task trễ nhiều: `state` = `breached`, `percent` bị chặn ở 100 | TC-FST-006 |

#### TCOND-25-04 — Chip: nhiều task, chọn khẩn nhất

**Feature:** FT-25 | **REQ-ID:** REQ-INT-024 | **Technique:** Decision Table

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Nhiều task: chọn trạng thái khẩn nhất | TC-FST-010 |
| CI-2 | Task đang hoạt động thắng task đã đóng | TC-FST-011 |

#### TCOND-25-05 — Chip: phân quyền RPC

**Feature:** FT-25 | **REQ-ID:** REQ-INT-024, REQ-SEC-002 | **Technique:** Decision Table

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Người dùng không thuộc nhóm SLA gọi RPC bị từ chối (không `sudo`) | TC-FST-012 |
| CI-2 | SLA User đọc được tóm tắt | TC-FST-013 |

#### TCOND-25-06 — Chip: cờ bật/tắt trong Settings

**Feature:** FT-25 | **REQ-ID:** REQ-INT-024 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Chưa có bản ghi tham số cờ: coi là bật | TC-FST-014 |
| CI-2 | Tắt cờ qua Settings lưu chuỗi `'False'` tường minh | TC-FST-015 |

#### TCOND-25-07 — Chip: danh sách model trong session_info

**Feature:** FT-25 | **REQ-ID:** REQ-INT-024 | **Technique:** Decision Table

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | `session_info` liệt kê model có SLA cho SLA User | TC-FST-016 |
| CI-2 | Cờ tắt: `dwo_sla_models` rỗng | TC-FST-017 |
| CI-3 | Người dùng không thuộc nhóm SLA: `dwo_sla_models` rỗng | TC-FST-018 |

#### TCOND-25-08 — Chip trên trình duyệt (tour)

**Feature:** FT-25 | **REQ-ID:** REQ-INT-024 | **Technique:** Demonstration tự động (tour)

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Tour: form partner có chip, bấm chip mở list task của record | TC-FST-019 |
| CI-2 | Tour: form của model không có SLA không có chip | TC-FST-020 |

### 7.8. FT-26 / TG-31 — Tab Note, chuỗi không lỗi thời

#### TCOND-26-01 — Tab Note của định nghĩa

**Feature:** FT-26 | **REQ-ID:** REQ-FUNC-003, REQ-FUNC-067, REQ-INT-024, REQ-INT-029 | **Technique:** Inspection arch

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Tab Note của định nghĩa có đủ 9 nhóm tiêu đề | TC-NOT-001 |
| CI-2 | Tab Note của định nghĩa nêu các điểm cần lưu ý của đợt 1.1.0 | TC-NOT-002 |

#### TCOND-26-02 — Tab Note của task

**Feature:** FT-26 | **REQ-ID:** REQ-INT-029 | **Technique:** Inspection arch

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Tab Note của task có 4 nhóm và 3 kịch bản đánh số | TC-NOT-003 |

#### TCOND-26-03 — Không còn tên nút cũ

**Feature:** FT-26 | **REQ-ID:** REQ-INT-005, REQ-INT-020, REQ-INT-029 | **Technique:** Inspection tự động

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Không còn tên nút cũ "Recalculate"/"Re-evaluate" trong chuỗi hiển thị | TC-NOT-004 |

### 7.9. FT-27 / TG-32 — Duration (live) và Business Duration (live)

#### TCOND-27-01 — Duration live: task đang chạy

**Feature:** FT-27 | **REQ-ID:** REQ-INT-028 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Task đang chạy: cột lưu đứng yên, bản live cộng đoạn tới hiện tại | TC-DUR-001 |

#### TCOND-27-02 — Duration live: task paused

**Feature:** FT-27 | **REQ-ID:** REQ-INT-028 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Task paused: live bằng giá trị đã lưu | TC-DUR-002 |

#### TCOND-27-03 — Duration live: có lịch

**Feature:** FT-27 | **REQ-ID:** REQ-INT-028 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Có lịch: live theo giờ làm khác live theo giờ đồng hồ | TC-DUR-003 |

#### TCOND-27-04 — Duration live: cột trên list

**Feature:** FT-27 | **REQ-ID:** REQ-INT-028 | **Technique:** Inspection arch

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | List task hiện hai cột live mặc định, hai cột lưu vẫn có nhưng ẩn | TC-DUR-004 |

### 7.10. FT-28 / TG-21 — Field phân loại của định nghĩa (type, vendor, service commitment, target)

#### TCOND-28-01 — Field type

**Feature:** FT-28 | **REQ-ID:** REQ-FUNC-070 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Định nghĩa không truyền `type`: mặc định `sla` | TC-MDF-001 |
| CI-2 | Định nghĩa với `type='ola'`: lưu và đọc lại đúng | TC-MDF-002 |

#### TCOND-28-02 — Field vendor_id

**Feature:** FT-28 | **REQ-ID:** REQ-FUNC-070 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Chọn nhà cung cấp (`vendor_id`): lưu đúng partner | TC-MDF-003 |
| CI-2 | Không chọn nhà cung cấp: `vendor_id` rỗng | TC-MDF-004 |

#### TCOND-28-03 — Field service_commitment

**Feature:** FT-28 | **REQ-ID:** REQ-FUNC-070 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Không truyền `service_commitment`: mặc định `False` | TC-MDF-005 |
| CI-2 | `service_commitment=True`: lưu đúng | TC-MDF-006 |

#### TCOND-28-04 — Field target

**Feature:** FT-28 | **REQ-ID:** REQ-FUNC-070 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Không chọn `target`: rỗng | TC-MDF-007 |
| CI-2 | `target='response'`: lưu đúng | TC-MDF-008 |
| CI-3 | `target='resolution'`: lưu đúng | TC-MDF-009 |

#### TCOND-28-05 — Metadata không đổi hành vi engine

**Feature:** FT-28 | **REQ-ID:** REQ-FUNC-070 | **Technique:** Error Guessing (hồi quy)

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Bốn field metadata không đổi hành vi engine | TC-MDF-010 |

### 7.11. FT-29 / TG-22 — Retroactive pause

#### TCOND-29-01 — Cảnh báo retroactive_pause

**Feature:** FT-29 | **REQ-ID:** REQ-FUNC-071 | **Technique:** Decision Table

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Model không có `mail.thread`: cảnh báo nêu rõ model | TC-RPS-001 |
| CI-2 | Field trong `pause_domain` không bật tracking: cảnh báo nêu tên field | TC-RPS-002 |
| CI-3 | Mọi field pause đều có tracking: không cảnh báo | TC-RPS-003 |
| CI-4 | Tính năng tắt: không tính cảnh báo | TC-RPS-004 |
| CI-5 | Đổi `pause_domain`: cảnh báo tính lại | TC-RPS-005 |

#### TCOND-29-02 — Trừ đoạn pause trong khoảng quá khứ

**Feature:** FT-29 | **REQ-ID:** REQ-FUNC-071 | **Technique:** BVA

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Có lịch sử pause trong khoảng quá khứ: trừ đúng thời gian pause, dời hạn | TC-RPS-006 |

#### TCOND-29-03 — Không trừ khi tắt hoặc không có lịch sử

**Feature:** FT-29 | **REQ-ID:** REQ-FUNC-071 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Cùng lịch sử nhưng `retroactive_pause` tắt: không trừ gì | TC-RPS-007 |
| CI-2 | Không có thay đổi tracking trong khoảng: không trừ gì | TC-RPS-008 |

#### TCOND-29-04 — Không trừ khi field pause không tracking

**Feature:** FT-29 | **REQ-ID:** REQ-FUNC-071 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Field pause không tracking: bỏ qua, không trừ dù tính năng bật | TC-RPS-009 |

### 7.12. FT-30 / TG-23 — Timezone override của lịch (bản sao calendar)

#### TCOND-30-01 — Timezone SLA khác timezone lịch

**Feature:** FT-30 | **REQ-ID:** REQ-FUNC-067 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Timezone SLA khác tz của lịch: hạn chót tính theo tz của SLA | TC-TZO-001 |

#### TCOND-30-02 — Bản sao lịch dùng chung và không đổi lịch gốc

**Feature:** FT-30 | **REQ-ID:** REQ-FUNC-067 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Hai định nghĩa cùng lịch, cùng tz: dùng chung một bản sao | TC-TZO-002 |
| CI-2 | Lịch gốc không bị đổi timezone | TC-TZO-003 |
| CI-3 | Bản sao giữ nguyên khung giờ làm của lịch gốc | TC-TZO-004 |

#### TCOND-30-03 — Timezone trùng thì không tạo bản sao

**Feature:** FT-30 | **REQ-ID:** REQ-FUNC-067 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Tz của SLA trùng tz của lịch: không tạo bản sao | TC-TZO-005 |

### 7.13. FT-31 / TG-24 — Hạn chót ban đầu và thời lượng giờ đồng hồ

#### TCOND-31-01 — original_breach_time bất biến

**Feature:** FT-31 | **REQ-ID:** REQ-FUNC-072 | **Technique:** State Transition

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | `original_breach_time` đặt một lần lúc attach, không đổi khi resume | TC-CLK-001 |
| CI-2 | Apply Current Settings không đổi `original_breach_time` | TC-CLK-002 |

#### TCOND-31-02 — Duration giờ đồng hồ so với giờ làm việc

**Feature:** FT-31 | **REQ-ID:** REQ-FUNC-072 | **Technique:** EP

| CI | Coverage item (lớp, quy tắc, biên hoặc chuyển trạng thái) | Test Case |
|---|---|---|
| CI-1 | Không có lịch (24x7): `duration`/`pause_duration` bằng bản giờ làm việc | TC-CLK-003 |
| CI-2 | Có lịch, pause qua cuối tuần: giờ đồng hồ khác giờ làm việc | TC-CLK-004 |

### 7.14. Traceability bổ sung (REQ-ID mới và REQ-ID mở rộng)

| REQ-ID | Test Condition | Test Case |
|---|---|---|
| REQ-FUNC-001 | TCOND-14-36, TCOND-20-02 | TC-INF-036, TC-ENB-002 |
| REQ-FUNC-003 | TCOND-20-06, TCOND-20-07, TCOND-24-03, TCOND-26-01 | TC-CND-001, TC-CND-002, TC-CND-003, TC-CND-004, TC-CND-005, TC-APX-004, TC-NOT-002 |
| REQ-FUNC-005 | TCOND-13-17 | TC-CMP-017 |
| REQ-FUNC-013 | TCOND-20-07 | TC-CND-006 |
| REQ-FUNC-021 | TCOND-20-12 | TC-TZR-009 |
| REQ-FUNC-022 | TCOND-03-24, TCOND-08-70 | TC-BRE-024, TC-PRC-001, TC-PRC-002 |
| REQ-FUNC-026 | TCOND-08-73, TCOND-12-30 | TC-EML-005, TC-ERR-030 |
| REQ-FUNC-032 | TCOND-22-01, TCOND-22-04, TCOND-22-05 | TC-RCK-001, TC-RCK-005, TC-RCK-006 |
| REQ-FUNC-042 | TCOND-13-17 | TC-CMP-017 |
| REQ-FUNC-051 | TCOND-20-07 | TC-CND-006 |
| REQ-FUNC-053 | TCOND-24-07 | TC-APX-011 |
| REQ-FUNC-060 | TCOND-20-05 | TC-ENB-008 |
| REQ-FUNC-064 | TCOND-08-72, TCOND-08-74 | TC-EML-001, TC-EML-006, TC-EML-007 |
| REQ-FUNC-065 | TCOND-08-72, TCOND-08-73 | TC-EML-002, TC-EML-003, TC-EML-004, TC-EML-005 |
| REQ-FUNC-066 | TCOND-20-01, TCOND-20-03, TCOND-20-04, TCOND-20-05, TCOND-21-08 | TC-ENB-001, TC-ENB-003, TC-ENB-004, TC-ENB-005, TC-ENB-006, TC-ENB-007, TC-ENB-008, TC-DLV-001, TC-DLV-002 |
| REQ-FUNC-067 | TCOND-20-08, TCOND-20-09, TCOND-20-10, TCOND-20-11, TCOND-20-12, TCOND-26-01, TCOND-30-01, TCOND-30-02, TCOND-30-03 | TC-TZR-001, TC-TZR-002, TC-TZR-003, TC-TZR-004, TC-TZR-005, TC-TZR-006, TC-TZR-007, TC-TZR-008, TC-TZR-009, TC-NOT-002, TC-TZO-001, TC-TZO-002, TC-TZO-003, TC-TZO-004, TC-TZO-005 |
| REQ-FUNC-068 | TCOND-24-01, TCOND-24-02, TCOND-24-03, TCOND-24-04, TCOND-24-05, TCOND-24-06, TCOND-24-07, TCOND-24-08 | TC-APX-001, TC-APX-002, TC-APX-003, TC-APX-004, TC-APX-005, TC-APX-006, TC-APX-007, TC-APX-008, TC-APX-009, TC-APX-010, TC-APX-011, TC-APX-012 |
| REQ-FUNC-069 | TCOND-21-04, TCOND-21-05, TCOND-21-07, TCOND-21-13 | TC-LCK-001, TC-LCK-002, TC-LCK-003, TC-AUD-001, TC-AUD-002, TC-AUD-003, TC-SBT-004, TC-TOUR-001 |
| REQ-FUNC-070 | TCOND-28-01, TCOND-28-02, TCOND-28-03, TCOND-28-04, TCOND-28-05 | TC-MDF-001, TC-MDF-002, TC-MDF-003, TC-MDF-004, TC-MDF-005, TC-MDF-006, TC-MDF-007, TC-MDF-008, TC-MDF-009, TC-MDF-010 |
| REQ-FUNC-071 | TCOND-29-01, TCOND-29-02, TCOND-29-03, TCOND-29-04 | TC-RPS-001, TC-RPS-002, TC-RPS-003, TC-RPS-004, TC-RPS-005, TC-RPS-006, TC-RPS-007, TC-RPS-008, TC-RPS-009 |
| REQ-FUNC-072 | TCOND-31-01, TCOND-31-02 | TC-CLK-001, TC-CLK-002, TC-CLK-003, TC-CLK-004 |
| REQ-INT-001 | TCOND-20-02 | TC-ENB-002 |
| REQ-INT-005 | TCOND-23-01, TCOND-23-02, TCOND-23-03, TCOND-23-04, TCOND-23-05, TCOND-23-06, TCOND-26-03 | TC-APS-001, TC-APS-002, TC-APS-003, TC-APS-004, TC-APS-005, TC-APS-006, TC-NOT-004 |
| REQ-INT-010 | TCOND-24-06 | TC-APX-010 |
| REQ-INT-012 | TCOND-21-01, TCOND-21-02, TCOND-21-03, TCOND-25-02 | TC-DUE-001, TC-DUE-002, TC-DUE-003, TC-DUE-004, TC-DUE-005, TC-FST-004 |
| REQ-INT-020 | TCOND-22-01, TCOND-22-02, TCOND-22-03, TCOND-22-04, TCOND-26-03 | TC-RCK-001, TC-RCK-002, TC-RCK-003, TC-RCK-004, TC-RCK-005, TC-NOT-004 |
| REQ-INT-023 | TCOND-03-25, TCOND-03-26, TCOND-18-12 | TC-BRE-025, TC-BRE-026, TC-PRF-012, TC-PRF-013 |
| REQ-INT-024 | TCOND-21-12, TCOND-25-01, TCOND-25-02, TCOND-25-03, TCOND-25-04, TCOND-25-05, TCOND-25-06, TCOND-25-07, TCOND-25-08, TCOND-26-01 | TC-LGT-001, TC-FST-001, TC-FST-002, TC-FST-009, TC-FST-003, TC-FST-004, TC-FST-005, TC-FST-007, TC-FST-008, TC-FST-006, TC-FST-010, TC-FST-011, TC-FST-012, TC-FST-013, TC-FST-014, TC-FST-015, TC-FST-016, TC-FST-017, TC-FST-018, TC-FST-019, TC-FST-020, TC-NOT-002 |
| REQ-INT-025 | TCOND-21-06, TCOND-21-07 | TC-SBT-001, TC-SBT-002, TC-SBT-003, TC-SBT-004 |
| REQ-INT-026 | TCOND-21-09, TCOND-21-10 | TC-EHS-001, TC-EHS-002, TC-EHS-003, TC-OSR-001, TC-OSR-002, TC-OSR-003, TC-OSR-004 |
| REQ-INT-027 | TCOND-21-11 | TC-TLV-001 |
| REQ-INT-028 | TCOND-27-01, TCOND-27-02, TCOND-27-03, TCOND-27-04 | TC-DUR-001, TC-DUR-002, TC-DUR-003, TC-DUR-004 |
| REQ-INT-029 | TCOND-26-01, TCOND-26-02, TCOND-26-03 | TC-NOT-001, TC-NOT-002, TC-NOT-003, TC-NOT-004 |
| REQ-OBS-003 | TCOND-12-30 | TC-ERR-030 |
| REQ-PERF-001 | TCOND-18-11, TCOND-20-05, TCOND-20-07 | TC-PRF-011, TC-ENB-007, TC-CND-005 |
| REQ-PERF-002 | TCOND-03-26, TCOND-18-11, TCOND-18-12 | TC-BRE-026, TC-PRF-011, TC-PRF-012, TC-PRF-013 |
| REQ-PERF-003 | TCOND-14-37 | TC-INF-037 |
| REQ-REL-002 | TCOND-08-70, TCOND-08-71, TCOND-18-11, TCOND-24-04 | TC-PRC-001, TC-PRC-002, TC-PRC-003, TC-PRF-011, TC-APX-006 |
| REQ-SEC-001 | TCOND-16-25, TCOND-24-08 | TC-SEC-025, TC-APX-012 |
| REQ-SEC-002 | TCOND-25-05 | TC-FST-012 |
