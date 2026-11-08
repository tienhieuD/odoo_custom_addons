# dwo_chatter_filter: Message Filter on Chatter (Odoo 19)

Module của DUO-TEK, chỉ phụ thuộc `mail`. License LGPL-3. Giá 9 EUR (đặt tròn, vì Odoo Apps tối thiểu 9 EUR; 9 USD
quy ra khoảng 8,1 EUR là dưới mức đó). Chỉ làm cho bản 19.

## 1. Vấn đề

Chatter của một bản ghi lâu ngày có hàng trăm message: trao đổi, email, ghi chú, thay đổi trường, thông báo tự động
trộn lẫn. Muốn xem riêng email hay riêng các lần thay đổi trường thì phải cuộn, vì ô tìm kiếm của core chỉ tìm theo chữ.

## 2. Tính năng

Một hàng badge ở đầu vùng nội dung chatter, ngay dưới hàng nút Send message, Log note, Activity:

**All · Discussions · Emails · Notes · Tracking · Other**, mỗi badge có số message.

- Bấm một badge thì chỉ hiện loại đó. **Chọn một loại tại một thời điểm**; bấm **All** để quay về tất cả.
- Không lưu lựa chọn: mở lại bản ghi là thấy tất cả (tránh việc ai đó bỏ sót message mà không biết đang lọc).
- Badge có số 0 thì mờ và không bấm được (trừ All).
- Lọc ở **máy chủ**, nên nút "Load more" chạy đúng trên danh sách đã lọc, không chỉ trên 30 message đã tải.
- Message mới đến (bus) khi đang lọc: hiện nếu đúng loại, ẩn nếu khác; số đếm cập nhật sau khoảng 0,4 giây.
- Tự ẩn khi form Send email của `dwo_mail_compose` đang mở (nằm trong vùng nội dung chatter) và khi đang tìm kiếm.
- Chỉ người dùng nội bộ (portal không dùng được `dwo_filter_counts`).

## 3. Quy tắc phân loại

Mỗi message thuộc **đúng một** loại. Kiểm tra theo thứ tự, loại đầu tiên khớp thì giữ message:

| # | Loại | Điều kiện |
|---|---|---|
| 1 | **Tracking** | có `mail.tracking.value` trỏ tới message (một trường đã đổi) |
| 2 | **Emails** | `message_type` là `email` hoặc `email_outgoing` (thư đến và thư đi) |
| 3 | **Notes** | `message_type = comment` và subtype `mt_note` (Log note) |
| 4 | **Discussions** | `message_type = comment` và subtype `mt_comment` (Send message, dù người nhận là follower nội bộ hay khách gắn trên bản ghi) |
| 5 | **Other** | phần còn lại: `auto_comment`, `notification` không có tracking, `out_of_office`, subtype tuỳ biến |

Hệ quả cần nhớ:
- Email gửi từ `dwo_mail_compose` là `email_outgoing` kèm subtype `mt_comment`: nó là **Emails**, không phải Discussions.
- Message tracking thường có subtype `mt_note`: nó là **Tracking**, không phải Notes.
- Message `comment` mang subtype nội bộ khác (ví dụ subtype riêng của một app) rơi vào **Other**.
- Tổng số các loại luôn bằng số message của bản ghi, nên không có message thất lạc.

Quy tắc được viết hai lần và phải giữ giống nhau: Python `MailMessage._dwo_category_domain` và JavaScript `dwoCategoryOf`
(`static/src/message_patch.js`).

## 4. Cách hoạt động

- `mail.message._message_fetch(..., dwo_category=...)` (ghi đè): route `/mail/thread/messages` đã chuyển nguyên
  `fetch_params` vào hàm này nên không cần route mới. Hàm thêm domain của loại vào domain gốc.
- Điều kiện "có tracking" dùng subselect trên bảng `mail_tracking_value`, **không** dùng trường `tracking_value_ids`: trường
  này chỉ dành cho nhóm quản trị, người dùng thường truy vấn sẽ bị `AccessError`.
- `mail.message.dwo_filter_counts(res_model, res_id)`: trả `{all, tracking, email, note, discussion, other}` bằng 6
  `search_count` (index `(model, res_id)`).
- JS: `Thread` (model) có thêm `dwoFilter`, `dwoCounts`; `fetchMessagesData` gửi thêm `dwo_category`. Đổi bộ lọc thì **bỏ
  hết message đã tải** rồi tải lại từ đầu (`dwoSetFilter`), để khi quay về All không bị hổng danh sách giữa hai lần tải.
  `Thread` (component) lọc `orderedMessages` theo `message.dwoCategory` cho các message đến qua bus.
- Component `DwoMessageFilter` chèn bằng xpath vào `mail.Chatter`, trước nội dung. Khi đóng bản ghi hoặc đổi sang bản ghi
  khác, `dwoReset()` trả bộ lọc về All và bỏ message đã tải, nên lần mở sau tải đủ.

## 5. Kiểm thử

```
odoo-bin -c <conf> -d <db_moi> -i dwo_chatter_filter --test-tags /dwo_chatter_filter --stop-after-init
```

- `test_filter.py` (9 test): mỗi loại có đúng message của nó, các loại không giao nhau và phủ hết, email gửi từ compose là
  email, tracking thắng subtype note, số đếm, phân trang trên danh sách đã lọc, không lọc thì như core, loại lạ bị từ chối,
  portal không đếm được.
- `test_filter_tour.py` + `filter_tour.js`: thấy badge ở đúng chỗ với số đúng, bấm từng loại thì danh sách chỉ còn loại
  đó, quay về All thì đủ. Body của email nằm trong shadow DOM nên tour đọc qua `shadowRoot`.
- Đã chạy chung với `dwo_mail_compose` và `dwo_mail_bcc`.

## 6. Giới hạn đã biết

- Chỉ chatter của bản ghi (form view), không áp cho Discuss hay Inbox.
- Chọn một loại tại một thời điểm, không chọn nhiều.
- Tìm kiếm (kính lúp) và bộ lọc không dùng chung: mở tìm kiếm thì badge ẩn và bộ lọc về All.
- Chỉ bản 19. Mã chatter thay đổi nhiều giữa các phiên bản Odoo nên cần kiểm tra lại khi nâng version.

## 7. Dữ liệu demo

Module lab `.lab/dwo_chatter_filter_demo_data` (không đăng): một khách hàng có đủ năm loại message trải trong nhiều ngày.
