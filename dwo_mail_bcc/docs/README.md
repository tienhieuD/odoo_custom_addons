# dwo_mail_bcc: Mail BCC Support (Odoo 19)

Module miễn phí, công khai cho cộng đồng. Chỉ phụ thuộc `mail`. License LGPL-3.
Đây là nền tảng Bcc cho `dwo_mail_compose` (module soạn email nâng cao), nhưng dùng độc lập được.

## 1. Vấn đề

Odoo 19 có sẵn `mail.mail.email_cc` và tầng gửi (`ir.mail.server._build_email__`) đã hỗ trợ `email_bcc`,
nhưng không có chỗ nào nối Bcc từ giao diện soạn thư xuống tầng gửi:
`mail.mail` không có trường Bcc, `_prepare_outgoing_list` không trả Bcc, `_send` không truyền `email_bcc`,
`message_post` không nhận Bcc, composer không có ô Bcc.
Module này nối các điểm đó lại, không viết lại tầng gửi.

## 2. Tính năng

| Vị trí | Thay đổi |
|---|---|
| `mail.mail` | Trường `email_bcc` (Char), hiện trên form `mail.mail` (menu Technical) |
| `mail.message` | Trường `outgoing_email_bcc`, chỉ nhóm `base.group_user` đọc được, hiện trong tab Recipients |
| `message_post(...)` | Nhận `outgoing_email_bcc="a@x.com, b@y.com"` |
| Composer đầy đủ (`mail.compose.message`) | Ô Bcc cho chế độ comment (Send message) và mass mail. Không hiện khi Log note |
| `mail.template` | Trường `email_bcc`, dùng được placeholder như `{{ object.user_id.email }}`, tính riêng cho từng record. Có mặt trên form template, `send_mail`, mass mail và Send message dùng template |

Bcc nhận được thư. Địa chỉ Bcc không bao giờ xuất hiện trong header của thư tới người khác.

## 3. Cách hoạt động

```
message_post(outgoing_email_bcc=...)
  -> mail.message.outgoing_email_bcc                (lưu để tra cứu)
  -> _notify_by_email_get_base_mail_values          (mail_thread.py)  đặt email_bcc vào mọi mail.mail của message
  -> mail.mail.create                               chỉ mail.mail đầu tiên của message giữ email_bcc
  -> mail.mail._prepare_outgoing_list               đặt Bcc vào header của đúng 1 thư con + thêm vào send_validated_to
  -> ir.mail.server._build_email__                  copy headers vào message (Bcc có trong message)
  -> ir.mail.server._prepare_smtp_to_list           đưa Bcc vào danh sách SMTP envelope
  -> ir.mail.server._alter_message__                xoá header Bcc trước khi gửi
```

## 4. Các quyết định thiết kế

| # | Quyết định | Lý do |
|---|---|---|
| D1 | Truyền Bcc qua `headers` của từng thư con, không override `_send` | `_send` gọi `_build_email__` với tham số tường minh nên key lạ bị bỏ qua. `_build_email__` copy `headers` nguyên vẹn vào message. Không phải copy cả `_send` (hàng trăm dòng, dễ vỡ khi nâng cấp) |
| D2 | Copy dict `headers` cho thư mang Bcc | Mọi thư con của một `mail.mail` dùng chung một dict `headers`. Không copy thì mọi thư con của từng partner đều mang Bcc |
| D3 | Thêm địa chỉ Bcc đã chuẩn hoá vào `email_to_normalized` của thư mang Bcc | `_send` đặt context `send_validated_to` bằng danh sách này, `_prepare_smtp_to_list` chỉ giữ địa chỉ nằm trong đó. Thiếu bước này thì header Bcc có nhưng không ai nhận thư (lỗi im lặng). Trường Cc của core cũng làm đúng như vậy |
| D4 | Bcc **chỉ** nằm ở thư con đầu tiên của `mail.mail` | Core gửi mỗi partner một thư riêng. Gắn Bcc vào tất cả thì người Bcc nhận nhiều bản |
| D5 | Chỉ `mail.mail` đầu tiên của một message giữ `email_bcc` (xử lý ở `create`) | Một message sinh nhiều `mail.mail` (theo nhóm người nhận, theo lô 50 partner, thêm một cái cho email thô). Kể cả khi core copy `mail.mail` để chia nhỏ theo giới hạn gửi, bản copy bị bỏ Bcc, bản gốc giữ, nên Bcc đi đúng một lần |
| D6 | Địa chỉ Bcc **không** đưa vào `recipients_data` hay `outgoing_email_to` | `recipients_data` tạo header `X-Msg-To-Add`, được nối vào To nhìn thấy được. Đưa Bcc vào đó là lộ địa chỉ |
| D7 | `outgoing_email_bcc` có `groups="base.group_user"` và `copy=False` | Danh sách Bcc là thông tin nhạy cảm, không được lọt vào dữ liệu chatter của portal. Không copy khi nhân bản message |
| D8 | Mở rộng `_get_message_create_valid_field_names` | Core giới hạn field mà `message_post` nhận bằng allow-list. Không thêm thì `message_post(outgoing_email_bcc=...)` báo `ValueError` |
| D9 | Bcc trùng người nhận thấy được thì bỏ khỏi Bcc | Tránh gửi hai bản cho cùng một người |
| D10 | `mail.template.email_bcc` được render bằng cách thêm `email_bcc` vào danh sách field khi core render người nhận (`_generate_template`), và thêm vào `_get_dynamic_field_names` | Core render mọi field không đặc biệt qua `_render_field`, nên chỉ cần khai báo; `send_mail` và mass mail nhận `email_bcc` đã tính và tạo `mail.mail` với nó. Chế độ comment của composer không render người nhận từ template, nên Bcc của template được render và gộp vào `outgoing_email_bcc` ở `_prepare_mail_values` (gộp, bỏ trùng với Bcc gõ tay) |
| D11 | Bcc của template không phụ thuộc cờ "Default Recipients" (`use_default_to`) | Cờ này chỉ thay To/Cc bằng người nhận mặc định của record; Bcc không có bản mặc định nên luôn lấy từ template |

## 5. Giới hạn đã biết

- Bcc cần ít nhất một người nhận khác (To, Cc hoặc partner). Một `mail.mail` chỉ có Bcc không sinh thư con nào nên không được gửi.
  Cũng vì thế, `message_post` chỉ có Bcc mà không có partner hay email nhận thì không tạo thư.
- Với `message_post` theo luồng thông báo chuẩn (nhiều nhóm người nhận), Bcc đi cùng `mail.mail` được tạo đầu tiên,
  có thể là nhóm dùng layout nội bộ. Khi cần thư sạch cho Bcc, gửi theo cách của `dwo_mail_compose` (một thư duy nhất).
- Nếu `mail.mail` mang Bcc gửi lỗi, Bcc chỉ đi khi `mail.mail` đó được gửi lại.
- Composer nhập nhanh trong chatter (không mở full composer) chưa có ô Bcc; chỉ full composer có.
- Nhiều bản ghi cùng lúc (batch comment): cùng một Bcc áp cho tất cả.

## 6. Kiểm thử

```
odoo-bin -c <conf> -d <db_moi> -i dwo_mail_bcc --test-tags /dwo_mail_bcc --stop-after-init --log-level=warn
```

13 test, kiểm tra **SMTP envelope** (mock `smtplib`) chứ không chỉ tham số `_build_email__`:
Bcc có trong đúng một envelope, không có trong chuỗi thư, không có header `Bcc:`, không lọt vào `To`/`Cc`
(kể cả qua `X-Msg-To-Add`), dedup với người nhận thấy được, `mail.mail` thứ hai và bản copy không giữ Bcc,
composer chế độ comment, composer báo lỗi khi Bcc sai định dạng, trường được bảo vệ bằng nhóm, Bcc của template được tính theo record, `send_mail` với template, Send message dùng template.
Đã thử phá dòng D3 và 5/10 test fail, nên test có tác dụng.

## 7. Điểm móc để module khác mở rộng

`dwo_mail_compose` và các module khác dùng ba điểm sau, không sửa lại logic Bcc:
- `message_post(outgoing_email_bcc=...)`
- `mail.mail.email_bcc`
- `mail.compose.message.email_bcc` và `_dwo_get_bcc()` (chuẩn hoá và kiểm tra)

## 8. Việc còn lại trước khi đăng Odoo Apps

- Trang mô tả `static/description/index.html`, icon, banner (skill `odoo-apps-listing`).
- Kiểm tra theo Vendor Guidelines (module miễn phí: không giá, không quảng cáo trong mô tả).
