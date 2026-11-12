# dwo_chatter_filter: Chatter Quick Filter (Odoo 17)

Module của DUO-TEK, chỉ phụ thuộc `mail`. License LGPL-3. Giá 9 EUR (Odoo Apps tối thiểu 9 EUR). Tên kỹ thuật giữ là
`dwo_chatter_filter`; tên hiển thị đổi từ "Message Filter on Chatter" thành **Chatter Quick Filter** ở `17.0.2.0.0`.
Bản 17 port từ bản 19 (2.0.0: chip chỉnh được).

## 1. Vấn đề

Chatter của một bản ghi lâu ngày có hàng trăm message trộn lẫn (trao đổi, email, ghi chú, thay đổi trường, thông báo tự
động). Ô tìm kiếm của core chỉ tìm theo chữ, nên muốn xem riêng một loại phải cuộn.

## 2. Tính năng

Một hàng chip có nhãn **Filter by:**, dưới danh sách Planned Activities (`o-mail-ActivityList`) và trên danh sách message
(`o-mail-Thread`): **All** rồi các chip do admin định nghĩa, mỗi chip có số message.

- Bấm một chip thì chỉ hiện message của chip đó; **một chip tại một thời điểm**; bấm **All** để quay về. Không lưu lựa chọn.
- Chip có số 0 thì mờ và không bấm được (trừ All). Chip có filter hỏng (trường của module đã gỡ) hiện dấu `?`.
- Lọc ở **máy chủ**, nên "Load more" chạy đúng trên danh sách đã lọc. Message mới đến khi đang lọc: chờ ~0,4 giây rồi tải lại
  danh sách đã lọc (máy chủ quyết định message đó có thuộc chip hay không).
- Một message có thể thuộc **nhiều chip** (các chip do admin tạo có thể chồng nhau).
- Chỉ người dùng nội bộ. Tối đa 15 chip hiển thị (mỗi chip tốn một lần đếm khi mở bản ghi).
- Chip đang chọn bị archive/xoá thì quay về All. Admin đổi chip thì người khác thấy ở lần mở bản ghi kế tiếp (tải lại).

## 3. Chỉnh sửa chip (chỉ admin: `base.group_system`)

- Link **Edit** nằm sau chip cuối cùng, chỉ hiện với admin; quyền thật được chặn ở máy chủ (ACL: người dùng nội bộ chỉ đọc).
- **List**: tay cầm (`handle`) kéo thả đổi thứ tự (lưu bằng `web_resequence`), cột màu, nút bật/tắt **Active** (archive).
  Dòng đã archive vẫn hiện (mờ) để bật lại; action dùng `domain active in [True, False]`, không đổi context.
- **Form**: tên, Active, màu, bộ chọn domain trên `mail.message` (có trường `Kind of message`, xem mục 4).
- **Màu** của chip mới tự sinh: hue ở giữa khoảng trống lớn nhất giữa các màu đang dùng (có ngẫu nhiên nhẹ), tối đến mức
  độ tương phản với nền trắng ≥ 4,5:1 (độ sáng tương đối ≤ 0,18) nên đọc được trên nền sáng ở cả chip viền lẫn chip đặc.
  Màu lưu dạng `#rrggbb`; chữ trên chip đặc là trắng hoặc đen, chọn cái dễ đọc hơn.
- Chip mới nhận thứ tự cuối. Sáu chip mặc định xoá/archive/sửa được như chip khác.

## 4. Sáu chip mặc định và trường `dwo_kind`

Thứ tự, tên, màu như bản 1.1.0: Discussions `#71639e`, Emails `#17a2b8`, Activities `#6f42c1`, Notes `#ffac00`, Tracking
`#28a745`, Other `#dc3545`. Domain của chúng là `[('dwo_kind', '=', ...)]`.

`mail.message.dwo_kind` là trường **không lưu, tìm kiếm được** (Selection) giữ nguyên luật phân loại loại trừ của bản cũ
(`MailMessage._dwo_category_domain`, kiểm tra theo thứ tự, loại đầu khớp thì giữ message):

| # | Loại | Điều kiện |
|---|---|---|
| 1 | tracking | có `mail.tracking.value` trỏ tới message (dùng subselect trên bảng, vì `tracking_value_ids` chỉ admin đọc được) |
| 2 | email | `message_type` là `email` hoặc `email_outgoing` (và không phải tracking) |
| 3 | activity | subtype `mt_activities`, không phải tracking/email |
| 4 | note | `message_type = comment` và subtype `mt_note` |
| 5 | discussion | `message_type = comment` và subtype `mt_comment` |
| 6 | other | phần còn lại |

Nhờ trường này, admin dùng luật cũ trong bộ chọn domain như một điều kiện bình thường và kết hợp với điều kiện khác.
(JavaScript không còn luật phân loại: file `message_patch.js` của bản 1.x đã bỏ.)

## 5. Cách hoạt động

- Model `dwo.chatter.filter` (`models/dwo_chatter_filter.py`): `name` (dịch được), `sequence`, `color`, `domain` (chuỗi),
  `active`. Domain được kiểm khi lưu (cú pháp, trường tồn tại, thử một lần `search_count`) và đánh giá bằng `safe_eval`
  với ngữ cảnh giới hạn (`uid`, `user`, `time`, `datetime`, `relativedelta`, `context_today`), như `ir.rule`.
- RPC `mail.message.dwo_filter_chips(res_model, res_id)`: trả `{all, chips: [{id, name, color, count}]}` theo thứ tự; mỗi chip
  đếm trong một savepoint, chip lỗi trả `count: null` và ghi log, không làm hỏng cả hàng.
- `mail.message._message_fetch(..., dwo_filter_id=...)`: route `/mail/thread/messages` chuyển nguyên `fetch_params`. Chip đã
  xoá/archive/lỗi thì không lọc gì.
- Phía trình duyệt: `DwoMessageFilter` (`static/src/filter/`), patch `Thread` model (`thread_patch.js`) và `Chatter`
  (`chatter_patch.xml`: chèn trước `SearchMessageResult` vì hai phần tử này là cặp `t-if`/`t-else` của core).

## 6. Dữ liệu và nâng cấp

- Sáu chip nằm trong `data/dwo_chatter_filter_data.xml` với `noupdate="1"` và `forcecreate="0"`: cài mới tạo đủ; cập nhật module
  không ghi đè chỉnh sửa và **không tạo lại chip đã xoá**.
- Nâng cấp từ 17.0.1.x: `migrations/17.0.2.0.0/post-migrate.py` nạp file data ở chế độ `init` để tạo sáu chip một lần,
  người dùng cũ thấy đúng như trước.

## 7. Kiểm thử

`tests/test_filter.py` (loại, đếm, lọc theo chip, phân trang), `tests/test_chips.py` (quyền, kiểm domain, màu mặc định,
thứ tự, chip hỏng, giới hạn 15), `tests/test_filter_tour.py` + `static/tests/tours/filter_tour.js` (lọc; admin tạo chip qua
form; nhân viên không thấy Edit). Chạy: `--test-tags /dwo_chatter_filter`. Script thử tay trên trình duyệt thật:
`odoo_appstore/_tools/ui_chips_check.py`.

## Khác biệt ở bản 17

- Không có `Domain`: `expression.AND/OR` y `!` (hàm `_not`). Kiểm quyền: `check_access_rights` + `check_access_rule`; `_()` thay `self.env._`.
- Route `/mail/thread/messages`: `controllers/thread.py` nhận `dwo_filter_id` và đặt vào context (như bản 18).
- JS kiểu service: `ThreadService.fetchMessages` được patch; `dwoSetFilter` / `dwoReset` / `dwoReload` nằm trên service `mail.thread`. `dwoFilter` là thuộc tính thường gán trong `setup()` (không dùng `Record.attr`). `session.is_admin` thay `user.isAdmin`.
- Template chèn trước `<t t-if="props.hasMessageList">` (bản này không có `SearchMessageResult`).
- Tour: bước chỉ kiểm tra phải có `run: () => {}` (mặc định là click); `run: "text ..."` thay `edit`; kiểm màu bằng `document.querySelector`.
- Danh sách chip: kéo thả ghi `sequence` từng dòng (không có `web_resequence`).
