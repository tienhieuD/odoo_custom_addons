# dwo_mail_bcc

Bcc cho composer, hàng đợi `mail.mail` và `message_post` của Odoo 19. Miễn phí, LGPL-3, chỉ phụ thuộc `mail`.

Tài liệu thiết kế đầy đủ nằm **trong module**: [`dwo_mail_bcc/docs/README.md`](../../odoo_custom_addons19/dwo_mail_bcc/docs/README.md)
(cơ chế, 10 quyết định thiết kế D1 đến D11, giới hạn đã biết, cách test, điểm móc).

Tóm tắt: nối `email_bcc` từ composer xuống SMTP envelope bằng cách đặt Bcc vào header của đúng một thư con,
không override `_send`, không để lộ Bcc qua To, Cc hay `X-Msg-To-Add`. Chỉ làm cho bản 19.
