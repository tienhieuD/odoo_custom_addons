# Tài liệu `dwo_sla_core` (12.0.1.1.0)

Bộ tài liệu của module SLA & Escalation cho Odoo 12, theo chuỗi SRS (ISO/IEC/IEEE 29148) → TAD (42010) → Database Design → Test Plan, Test Design, Test Case (29119-3). Cập nhật lần cuối: 2026-11-12.

| File | Nội dung | Phiên bản |
|---|---|---|
| `010_Software-Requirements-Specification.md` | SRS: 115 REQ-ID (111 `active`, 4 `draft`; FUNC-027, 028, 056 đến 059 đã gỡ), ma trận xác minh ở mục 4 | 0.7 |
| `020_Technical-Architecture-Document.md` | Kiến trúc: khối, kịch bản chạy, ADR (AD-01 đến AD-14) | 0.6 |
| `030_Database-Design.md` | Schema: DBML, từ điển dữ liệu, ràng buộc, chỉ mục, quyền, nâng cấp | 0.6 |
| `040_Test-Plan.md` | Kế hoạch kiểm thử, Feature FT-01 đến FT-31 | 0.4 |
| `050_Test-Design-Specification.md` | Test condition và coverage item (214 TCOND); mục 7 là phần của đợt 1.1.0 | 0.3 |
| `060_Test-Case-Specification.md` | 588 test case (ID); Phụ lục C ánh xạ 435 hàm test sang test case; Phụ lục D liệt kê test case không có hàm test | 0.3 |
| `070_User-Guide.md` | Hướng dẫn sử dụng (bản HTML sinh bằng `odoo_appstore/_tools/sla_user_guide_html.py`) | |
| `TASKS.md` | Nhật ký tiến độ và việc còn dở | |

## Số liệu (đối chiếu với code)

- **Hàm test:** 435 (`grep -h "def test_" tests/test_*.py | wc -l`); 432 chạy thường, 3 hàm hiệu năng trong `tests/test_tg18_performance.py` chỉ chạy khi đặt `SLA_PERF=1`.
- **Test case (ID) trong 060:** 588 = 521 có hàm test tự động, 19 manual, 21 phủ bằng CI hoặc benchmark ngoài `tests/`, 27 đã gỡ (cơ chế thử lại, D12).
- **Đợt 1.1.0 (REQ-ID mới):** FUNC-070 đến 072, INT-025 đến 029 (8 REQ-ID), cùng Acceptance Criteria bổ sung cho FUNC-001, 022, 032, 064 đến 069, INT-005, 012, 020, 024.

## Truy vết

REQ-ID (`010`) → Test Condition và Coverage Item (`050`) → Test Case (`060`) → hàm test (`060` Phụ lục C, `tests/`). Cột "Test/Artifact Link" của ma trận SRS mục 4 được sinh từ các test case còn hiệu lực của `060`.

## Quy ước

- Test case mới có tiền tố theo nhóm (`TC-MDF`, `TC-RPS`, `TC-TZO`, `TC-CLK`, `TC-ENB`, `TC-CND`, `TC-TZR`, `TC-DUE`, `TC-LCK`, `TC-AUD`, `TC-SBT`, `TC-DLV`, `TC-EHS`, `TC-OSR`, `TC-TLV`, `TC-LGT`, `TC-TOUR`, `TC-RCK`, `TC-APS`, `TC-APX`, `TC-FST`, `TC-NOT`, `TC-DUR`, và `TC-PRC`, `TC-EML` cho xử lý nền và email). ID không đánh lại số; ID của ca đã gỡ được giữ.
- Tên field theo code: `duration` (định nghĩa) và `target_duration` (task), `schedule_source`, `schedule_id`, `schedule_path`, `calendar_tz_override`, `start_time`, `end_time`, `planned_end_time`, `original_breach_time`, `business_duration`, `business_percent_used`. Tên nút: "Apply Current Settings" (`action_recalculate`) và "Re-check Conditions" (`action_reevaluate`).
- Domain `[]` là "chưa cấu hình, không bao giờ khớp"; muốn khớp mọi record dùng `[('id', '!=', 0)]`.

## Khác biệt ở bản 12

Tài liệu này sao từ bản 19 (SRS, TAD, thiết kế dữ liệu, kế hoạch và ca kiểm thử dùng chung, REQ-ID không đổi); các điểm dưới đây là phần phụ thuộc phiên bản. Số test chạy thật ở bản này: 435 (3 bỏ qua).

- Như bản 13, thêm các đánh đổi riêng của Odoo 12:
- **Không có cột tuỳ chọn** (`optional`): các cột lưu sẵn (Business Duration, Duration...) bị ẩn hẳn khỏi danh sách; chỉ hiện các cột "live".
- **Ribbon "Disabled"** là một nhãn đỏ (12 không có widget `web_ribbon`); **Source Record** hiện id, không có widget tham chiếu.
- **Hook field tính toán có lưu:** 12 không có `_compute_field_value`; module theo dõi thêm qua `_write` (bản ghi đổi do tính lại từ một record khác vẫn được đánh giá lại). Hành động "Re-check Conditions" vẫn là cách bù cho các trường hợp còn lại.
- **Lịch:** không có lịch hai tuần; bản sao đổi múi giờ copy các dòng giờ làm (kể cả ngày hiệu lực) và ngày nghỉ chung.
- **Test:** 3 test bỏ qua (TC-CAL-003, TC-CAL-004 và một test onchange của form, vì 12 ghi ngay giá trị gán và field múi giờ bắt buộc).
- **Tour kiểm thử** nằm trong bundle backend (12 không có `web.assets_tests`).
