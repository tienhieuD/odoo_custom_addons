# dwo_mail_compose: Advanced Email Composer (Odoo 19)

Module trả phí của DUO-TEK. Phụ thuộc `mail` và `dwo_mail_bcc`. License OPL-1.
Tài liệu này là **tài liệu nền** cho hướng dẫn sử dụng và trang giới thiệu: mọi quyết định thiết kế
và lý do nằm ở đây. Khi đổi hành vi, cập nhật tài liệu trước.

## 1. Vấn đề cần giải quyết

Chatter của Odoo có ba kiểu tin nhắn, và người dùng dễ lẫn:

| Kiểu | Subtype | Ai nhận email | Bản chất |
|---|---|---|---|
| **Log note** | `mt_note` | Không ai (trừ người được @mention) | Trao đổi nội bộ thuần |
| **Send message** | `mt_comment` | Mọi follower, kể cả follower là khách ngoài. Mỗi người một email riêng, dùng layout thông báo | Thảo luận chung, **không phải thư từ chính thức** |
| **Send email** (module này) | `message_type = email_outgoing`, subtype `mt_comment`, cờ `dwo_is_from_compose` | Chỉ To, Cc, Bcc được chọn, đúng một email thật | **Thư chính thức** |

Send message vẫn gửi email ra ngoài nếu thread có follower ngoài, nên không thể coi là "nội bộ".
Với thư chính thức, doanh nghiệp cần: người nhận thấy đúng To/Cc như một email bình thường, trích dẫn thư trước,
trả lời tất cả (reply-all), nháp, và phân biệt rõ trong lịch sử.

## 2. Tính năng

- Nút **Send email** cạnh Send message. Form mở **ngay tại vùng chatter**, không bật dialog.
- Form gọn: chỉ **From, To, Subject, Body**. **Cc** và **Bcc** là hai nút nhỏ bên phải ô To (kiểu Google): bấm nút nào thì dòng đó hiện ra; dòng đã có giá trị (reply-all, template, nạp lại email) thì hiện sẵn.
- Các ô địa chỉ là **badge**: gõ để gợi ý từ `res.users`, `res.partner` và sổ địa chỉ; gõ tự do email hợp lệ. **Không giới hạn giữa To, Cc, Bcc**: cùng một địa chỉ gõ được ở cả ba (chỉ chặn trùng trong cùng một ô).
- Thanh công cụ dưới body: **Attach**, **Template** (menu như composer gốc), **Advanced** (thêm các trường phụ, hiện tại là Reply-To). Mỗi nhãn có dấu `*` đỏ nếu bắt buộc và biểu tượng (i) giải thích bằng tooltip, nằm cùng dòng với nhãn.
- Mặc định reply-all, subject `RE:`, quote thư trước ngay trong body.
- Nút **Send email** mở menu hai lựa chọn: **Send now** hoặc **Request approval and send** (nhờ người duyệt rồi gửi). Dòng mờ phía trên nút nhắc: email gửi trực tiếp tới người nhận, không thông báo follower.
- Mỗi message email có một hàng nút outline secondary có icon ngay dưới From/To/Cc: **Reply** (chỉ người gửi, không Cc), **Reply all** (người gửi + To + Cc, giống Send email khi thread đã có email) và **Forward**. Hàng nút này tách khỏi menu tuỳ chọn của message (module không thêm mục nào vào menu đó). Chế độ gọi server: `reply_sender`, `reply` (reply-all), `forward`.
- Ô địa chỉ: bấm lại vào ô đang có focus (sau khi vừa chọn một gợi ý) vẫn mở lại dropdown; bấm vào vùng trống của ô cũng đặt con trỏ vào và mở gợi ý. Chọn một gợi ý (hoặc Enter, dấu phẩy) huỷ yêu cầu gợi ý đang chờ, nên danh sách không tự mở lại.
- **Body khi bắt đầu soạn**: 3 dòng trống (`<p><br></p>` x3) để viết vào, rồi chữ ký, rồi khối quote nếu là reply/forward (`_initial_body`). Chọn template khi chưa viết gì (nội dung phía trên quote không đổi so với lúc nạp) thì nội dung template **thay vào 3 dòng trống đó**, chữ ký và quote giữ nguyên (chế độ `fill`). Nếu người dùng đã viết thì vẫn hỏi Overwrite/Append như trước (Overwrite thay cả phần trên quote). Template lưu từ form bỏ các dòng trống ở đầu.
- **Sửa địa chỉ ngay trên chip**: bấm vào chip thì chip thành ô nhập địa chỉ tại chỗ. Enter, Tab hoặc dấu phẩy lưu và thay đúng vị trí đó (chip mới đánh dấu `new`); rời ô cũng lưu nếu địa chỉ hợp lệ, không hợp lệ thì giữ địa chỉ cũ; Enter với địa chỉ sai báo lỗi và giữ ô để sửa; Esc huỷ; xoá hết chữ rồi lưu thì bỏ chip; sửa thành địa chỉ đã có trong cùng ô thì chip bị gộp (không trùng). Chip dài được cắt bằng `...` và tooltip hiện `Tên <email>`.
- Khung form và khung danh sách email dùng nền `bg-view` (biến màu của sheet FormView), nên theo dark mode.
- **Ảnh dán từ clipboard**: server đổi mọi `<img src="data:image/...;base64,...">` thành attachment của bản ghi, link `/web/image/<id>?access_token=...` (`_externalize_images`), ngay khi lưu nháp và trước khi gửi. Làm ở server vì một điểm duy nhất phủ cả nháp, gửi trực tiếp và gửi qua duyệt. Cùng một ảnh (theo checksum) chỉ lưu một lần dù autosave gửi lại nhiều lần. Phía JS vẫn tải ảnh lên trước khi gửi khi editor làm được, server là lớp bảo đảm cuối.
- Dữ liệu demo để chụp ảnh giới thiệu: module lab `.lab/dwo_mail_compose_demo_data` (không đăng).
- Tiêu đề của form luôn là **Compose email**. Form và danh sách email là **hai khung riêng**, mỗi khung có viền riêng nên thấy rõ hai vùng.
- **Delete draft** là nút outline secondary nằm cạnh nút Send email, hover thì đỏ. **Mọi thao tác xoá đều hỏi trước** (Delete draft, nút xoá ở mọi dòng của danh sách kể cả email nháp, gỡ tệp đính kèm); gỡ badge người nhận, gỡ template hay ẩn ô Reply-To không phải là xoá nên không hỏi.
- Form **chiếm chỗ của chatter**: khi đang mở, vùng message (lịch sử, hoạt động, tệp) bị ẩn (`display: none !important`), đóng form là hiện lại bình thường.
- Thân thư **thấp hơn** (khoảng hai phần ba trước đây) và có nút **Expand** để sửa riêng thân thư trên toàn màn hình (Back to the form hoặc phím Esc để thu lại; vẫn là cùng một editor nên không có gì phải đồng bộ).
- Mỗi người có thể có **nhiều email** chưa gửi trên một bản ghi (nháp, chờ duyệt, bị từ chối), tự lưu; danh sách nằm phía dưới form, bấm vào một dòng để nạp vào form.
- Message email có **badge Email** và các dòng From, To, Cc ngay dưới tiêu đề, phân biệt với Message và Note.
- Sổ địa chỉ riêng lưu các email đã gõ mà không thuộc user hoặc partner, để gợi ý lần sau.
- **Template**: áp dụng tiêu đề, nội dung, From, To, Cc, Bcc và đính kèm, mọi placeholder được tính trên record đang mở. Chỉ liệt kê template của đúng model.
- **Duyệt trước khi gửi**: chọn một hoặc nhiều người duyệt (kể cả chính mình), bất kỳ ai duyệt là gửi. Công ty có thể **bắt buộc** mọi email phải qua duyệt.

## 3. Quy tắc nội dung mặc định (đã chốt)

"Email tham chiếu" là email chính thức mới nhất của thread: thư đến (`message_type='email'`) hoặc thư đã gửi bằng module này.
Note và Message thường **bị bỏ qua**.

| Tình huống | From | To | Cc | Bcc | Subject | Body |
|---|---|---|---|---|---|---|
| **A. Thread chưa có email nào** | User hiện tại (bắt buộc) | rỗng | rỗng | rỗng | rỗng | chữ ký |
| **B. Email mới nhất là thư đến** (reply-all) | Địa chỉ của mình đã nhận thư; không có thì User hiện tại | Người gửi | (To + Cc cũ) trừ mình, trừ To, trừ alias hệ thống | rỗng | `RE: ...` | chữ ký + quote |
| **C. Email mới nhất là thư mình đã gửi** | Giống thư đó | Giống thư đó | Giống thư đó | Giống thư đó | `RE: ...` | chữ ký + quote |
| **D. Bấm Reply/Forward trên một message** | Theo B hoặc C, lấy message đó làm tham chiếu (Forward: User hiện tại) | Forward: rỗng | Forward: rỗng | Forward: rỗng | `RE:` hoặc `FW:` | chữ ký + quote |
| **E. Xoá email đang soạn** | Quay về đúng logic A/B/C/D hiện tại, ngay tại chỗ (form không đóng) | | | | | |

Ghi chú:
- Ca C là tổng quát hoá của "chỉ có thư đi": cùng logic khi bạn trả lời lại thư mình đã gửi mà khách chưa phản hồi.
- Subject không lặp tiền tố: nhận ra `Re:`, `RE:`, `Fw:`, `Fwd:`, `FW:`, `TR:`, `AW:`, `SV:`, `RV:`.
- Forward sao chép đính kèm của thư gốc (bản sao tạm, thư gốc giữ nguyên bản của nó).

## 4. Khối quote (kiểu Outlook)

```
---------- Original message ----------
From: Lan Pham <lan.pham@khachhang.vn>
To: Hieu Nguyen <hieu@dwo.vn>
Cc: Thu Le <thu.le@khachhang.vn>
Date: 2026-11-06 18:12 (JST)

...nội dung gốc đã làm sạch...
```

- Cấu trúc HTML: `<div id="divRplyFwdMsg">` bọc **toàn bộ** header và nội dung. Odoo nhận diện id này là quote
  (`tools/mail.py`), nên chatter tự gập cả khối. Bộ làm sạch HTML của Odoo giữ nguyên id và tự gắn `data-o-mail-quote`.
- Forward dùng nhãn `Forwarded message`.
- Dòng **To** và **Cc** chỉ in khi có giá trị. Dòng **Bcc không bao giờ được in**: nếu in, reply thư mình đã gửi có Bcc
  sẽ làm lộ địa chỉ Bcc cho mọi người ở To và Cc.
- **Date** theo timezone **người soạn** (`res.users.tz`, thiếu thì timezone của trình duyệt, thiếu nữa thì UTC).
  Dùng chữ viết tắt nếu có (JST, CET). Nếu tzdata chỉ cho `+07` (ví dụ `Asia/Ho_Chi_Minh`) thì in `UTC+07:00`.
- Giá trị Date được **chốt vào body** lúc tạo quote. Đổi timezone sau đó không làm đổi email đã lưu; nút
  "Apply defaults again" mới tính lại.
- Quote nằm **trong body, sửa được**. Template chèn nội dung **phía trên** quote, không ghi đè quote.
- Nhãn cố định tiếng Anh (`From`, `To`, `Cc`, `Date`, `Original message`) theo thông lệ thư công việc.

## 4b. Template

Chọn template gọi `dwo.mail.composer.apply_template`, dùng đúng cơ chế render của core (`mail.template._generate_template`),
nên `{{ object... }}` và `<t t-out="object..."/>` được tính cho record đang mở.

| Phần của template | Cách áp dụng vào form |
|---|---|
| Tiêu đề | Thay subject (nếu template có) |
| Nội dung | Chèn **phía trên** khối quote; quote giữ nguyên |
| From | Thay From nếu địa chỉ nằm trong danh sách được phép; nếu không, giữ nguyên và hiện cảnh báo |
| To (email và partner) | **Thêm vào** người đã có, bỏ trùng (reply-all không bị mất người) |
| Cc, Bcc | Thêm vào như To; Bcc được tính từ `dwo_mail_bcc` |
| Đính kèm file của template | Sao chép thành tệp tạm của người dùng (bản gốc của template không đổi), gỡ được như tệp tự đính kèm |
| Báo cáo đính kèm (PDF) | Sinh ra khi chọn, thành tệp tạm |

- **Template là một menu cạnh nút Attach**, làm theo `mail_composer_template_selector` của composer gốc: danh sách template (của riêng bạn trước, rồi template dùng chung, tối đa 80, kèm **Search More…**), **Save as Template**, **Manage Templates**. Chỉ template có `model = model của record`.
- **Save as Template**: hỏi tên, tạo `mail.template` của bạn (`user_id` là bạn, `use_default_to` bật) từ tiêu đề (bỏ tiền tố `RE:`/`FW:`), nội dung **không có khối quote** (nếu không template sẽ mang theo email của khách lần trước) và đính kèm. Khác composer gốc: đính kèm được **sao chép** sang template (gốc chuyển file đi, làm email đang soạn mất file).
- Template đang dùng hiện thành huy hiệu bên cạnh, bấm ✕ để gỡ: người nhận và tệp template đã thêm bị gỡ, chữ của bạn giữ nguyên.
- **From** là ô tự gợi ý (autocomplete) trên danh sách địa chỉ được phép; đó không phải bản ghi nên không dùng many2one, và chỉ nhận địa chỉ trong danh sách.
- **Khi bạn đã soạn dở** (tiêu đề hoặc phần chữ phía trên khối quote khác với lúc form được nạp hoặc template điền gần nhất), chọn template sẽ hiện hộp thoại 3 nút:
  **Overwrite** (template thay tiêu đề và nội dung), **Add after my text** (giữ tiêu đề và chữ của bạn, nội dung template nối phía sau, trước khối quote), **Cancel** (không đổi gì, ô Template về giá trị cũ).
  Người nhận, From và tệp của template luôn được áp dụng theo quy tắc bên dưới (chỉ thêm vào, không làm mất gì). Nếu form chưa bị sửa thì áp dụng ngay, không hỏi.
- Chọn template khác hoặc "No template": phần người nhận và tệp mà template trước đã thêm được **gỡ ra** trước,
  người nhận bạn đã có sẵn thì giữ. (Sau khi tải lại từ email đã lưu, form không còn nhớ phần nào do template thêm.)
- Chỉ template có `model` trùng model của record được liệt kê và được chấp nhận; template khác model bị từ chối ở backend.
- Cờ **Default Recipients** của template (`use_default_to`, mặc định bật trong core): khi bật, core dùng người nhận mặc định của record
  (ví dụ chính khách hàng) và bỏ qua To/Cc của template. Module tôn trọng hành vi này. Tắt cờ để dùng To/Cc của template.
- Lỗi render (placeholder sai) hiện cảnh báo chuẩn của Odoo, form không đổi.

## 4c. Reply-To

Reply-To là nơi trả lời của người nhận được gửi tới. **Đây là logic của Odoo**, không phải của module này:
`message_post` gọi `_notify_get_reply_to` của model, theo thứ tự: alias gắn với bản ghi, rồi catchall của công ty, rồi chính người gửi.
Riêng CRM ghi đè (`crm_lead.py`): lead thuộc một team bán hàng thì Reply-To là **địa chỉ alias của team** (ví dụ `sales@công-ty`).

Lý do Odoo làm vậy: thư trả lời về địa chỉ do Odoo nhận thì **quay lại đúng bản ghi** (vừa nhờ `In-Reply-To`, vừa nhờ alias).
Nếu ép Reply-To về hộp thư riêng của người gửi, câu trả lời của khách vào thẳng hộp thư đó và **không về lại chatter**.

Cách module xử lý:
- Reply-To nằm trong menu **Advanced**, mục *Reply to (default: sales@…)* hiện giá trị mặc định đúng bằng logic của model (CRM thì ra địa chỉ team). Bấm vào thì thêm một ô Reply-To lên form.
- Mặc định đi theo From đã chọn và tự cập nhật khi đổi From. Không có đoạn mô tả bên dưới ô; nút **Use the default** nằm liền bên phải ô nhập (hiện khi bạn đã sửa), và dấu **cảnh báo vàng** cạnh ô nếu địa chỉ sửa không phải catchall hay alias của Odoo. Lời cảnh báo chỉ nói **khả năng** ("Odoo may not receive this address…"), không khẳng định, vì module không biết hết cấu hình thu thư của hệ thống.
- Đã sửa thì ô hiện sẵn khi mở lại email. Chưa sửa thì có nút ✕ để ẩn.
- Không sửa thì module không truyền Reply-To, `message_post` tự tính (cùng một hàm với giá trị hiển thị nên không thể lệch nhau).

## 5. Email lưu trữ (nháp, chờ duyệt, bị từ chối)

Model `dwo.mail.email` (kế thừa `mail.thread` và `mail.activity.mixin`). Mỗi người có thể có **nhiều** email trên một bản ghi.

- Tự lưu sau 1,5 giây ngừng sửa và khi đóng form (đợi lưu xong rồi mới đóng). Các lần lưu **nối tiếp nhau** và luôn mang id của lần lưu đầu, nên không bao giờ sinh bản ghi trùng.
- Nội dung lưu ở dạng **đã inline style** (như widget `html_mail`), để email gửi từ trình duyệt và email do máy chủ gửi sau khi duyệt giống hệt nhau.
- **Form mở ra email nào:** (1) email người dùng **vừa mở gần nhất trên màn hình này** (bấm vào danh sách, hoặc email vừa tạo), nếu còn; (2) không có thì email **tạo gần nhất** trong các email chưa gửi của họ trên bản ghi này, **bất kể trạng thái** (nháp, chờ duyệt, bị từ chối); (3) không có email nào thì mặc định A/B/C/D. Sửa một email cũ **không** làm nó thành "mới nhất": thứ tự là ngày tạo.
- **Ghi nhớ lựa chọn:** nằm trong state của chatter nên sống đến khi **đổi bản ghi, đổi màn hình hoặc tải lại trang**; khi đó quay về quy tắc (2).
- **Danh sách** phía dưới form: sắp **ngày tạo mới nhất lên trước**, mỗi dòng có tiêu đề, trạng thái, **ngày tạo** và **ngày cập nhật cuối**, nút **xoá** (thùng rác), và **cuộn** khi dài. Xoá được cả email đã gửi đi nhờ duyệt, email bị từ chối và email nháp; **cả ba đều hỏi xác nhận**. Xoá email đang mở trong form thì form về mặc định; xoá email đang chờ duyệt thì yêu cầu duyệt đóng lại và người duyệt được báo. Nút **+ New email** lưu email đang soạn, rồi **tạo ngay một bản nháp trong DB** từ nội dung mặc định: nó hiện luôn trong danh sách, được ghi nhớ, và có mặt khi mở lại form dù chưa gõ gì.
- **Danh sách luôn lấy lại từ máy chủ** mỗi lần form mở (cùng lời gọi nạp trạng thái), và được tải lại sau mỗi lần lưu, mở, tạo, xoá hay nhờ duyệt. Email do nơi khác tạo hoặc đổi trạng thái (người duyệt, một tab khác) vì vậy hiện đúng khi mở lại.
- **Chỉ có chữ do người dùng gõ mới tạo ra email.** Mở form rồi đóng mà không gõ gì, hoặc xoá email đang mở rồi bấm một dòng của danh sách, **không tạo bản nháp nào**. (Trình soạn tự chuẩn hoá HTML nên HTML của nó khác HTML máy chủ gửi ngay từ đầu; chỉ khi nội dung khác với *chính nội dung editor vừa nạp* mới tính là đã sửa. Trước đây sự khác biệt này bị coi là chỉnh sửa và lần lưu kế tiếp, ví dụ lúc bấm một dòng, sinh ra một bản nháp thừa.)
- **Nút ✕ luôn lưu những gì đã gõ**, dù gõ xong là đóng ngay: nội dung thân thư gõ dở, tiêu đề, và cả địa chỉ đã gõ nhưng chưa thành badge (được chuyển thành badge trước khi lưu). Đóng form thành công kể cả khi lưu lỗi.
- **Reply/Forward trên một message** mở một **email mới**, được **lưu ngay lúc form mở** (không đợi lần sửa đầu); không ghi đè email nào và không có hộp thoại xác nhận.
- **Delete draft** xoá email đang mở (nếu đang chờ duyệt thì báo cho người duyệt là yêu cầu đã đóng) và đưa form về mặc định ngay tại chỗ.
- **Email mới đến sau khi lưu nháp**: hiện banner kèm nút "Apply defaults again" và "Dismiss"; không bao giờ tự đè nội dung.

## 5b. Duyệt trước khi gửi

**Trạng thái:** `draft` (nháp) → `pending` (chờ duyệt) → `sent` (đã duyệt và gửi) hoặc `rejected` (từ chối). Ở mọi trạng thái, người soạn vẫn sửa và tự lưu như bình thường, và vẫn có thể bấm **Send now** hoặc **Request approval** lần nữa để quay lại vòng duyệt.

**Nhờ duyệt.** Popup chọn **một hoặc nhiều** người duyệt (bắt buộc, chỉ user nội bộ, **được chọn chính mình**) và lời nhắn (tuỳ chọn). **Chỉ cần một người duyệt là đủ.**

**Người duyệt nhận được:**
- một email (qua `message_notify`; người dùng đặt "Handle in Odoo" thì chỉ nhận ở hộp thư Odoo, đó là tuỳ chọn của họ và module không ghi đè);
- một **thông báo trên màn hình** (bus, kênh riêng của từng người) kèm nút mở trang chi tiết email;
- một **hoạt động** loại "Email approval" trong danh sách việc cần làm.

Người thực hiện hành động không tự nhận thông báo về hành động của mình (nên người tự chọn mình làm người duyệt chỉ thấy hoạt động).

**Trang chi tiết email** (form view chuẩn, menu Discuss > Email Approvals hoặc nút trong thông báo): nội dung, người nhờ, lời nhắn, người duyệt, huy hiệu cảnh báo nếu người soạn **sửa sau khi nhờ duyệt** (người duyệt luôn thấy nội dung hiện tại), nút nhảy tới bản ghi gốc (chỉ hiện nếu người duyệt có quyền đọc bản ghi đó; xem email thì không cần), nhật ký trong chatter, và ba nút, mỗi nút mở popup có ô comment (**không bắt buộc ở mọi trường hợp**), comment được lưu trên email:
- **Approve and send**: duyệt và gửi luôn. Email đi **từ địa chỉ của người soạn, với quyền và công ty của người soạn**; nếu người soạn không còn quyền đăng trên bản ghi thì báo lỗi và email giữ nguyên chờ duyệt.
- **Reject**: trạng thái `rejected`, người soạn được báo. Quyết định đầu tiên thắng: **một người từ chối là đủ**.
- **Reassign**: chọn một hoặc nhiều người thay thế. Chỉ **người đang thao tác** rời vòng duyệt, những người duyệt khác giữ nguyên; người mới nhận hoạt động và thông báo, người soạn được báo.

**Hoạt động của người duyệt được đánh dấu xong** (rồi biến khỏi danh sách) khi email được duyệt, bị từ chối, người soạn gửi trực tiếp, hoặc bị xoá; với Reassign thì chỉ hoạt động của người chuyển đi.

**Gửi trực tiếp hoặc xoá khi đang chờ duyệt:** yêu cầu duyệt đóng lại, người duyệt được báo, và bản lưu bị xoá (tin trong chatter đã là bản ghi).

**Gửi trực tiếp không có bản lưu:** email gửi ngay (không qua duyệt) không giữ `dwo.mail.email`. Email được duyệt và gửi giữ bản ghi trạng thái `sent` (kèm nhật ký duyệt).

**Quyền xem:** người soạn, người duyệt hiện tại và **mọi người từng là người duyệt** (kể cả đã chuyển đi) được đọc. Chỉ người soạn được sửa hoặc xoá; người duyệt quyết định qua các nút, không sửa nội dung. Quản trị viên (`base.group_system`) thấy tất cả.

**Duyệt khi form của người soạn còn mở:** lần tự lưu kế tiếp nhận về trạng thái `sent`, máy chủ **không ghi** lần sửa muộn, form khoá lại, báo "This email was approved and sent" kèm nút *Start a new email*, nút Send bị tắt, và nút ✕ vẫn đóng được (đóng không đợi lưu thành công). Nếu trạng thái đổi sang bị từ chối hay đã chuyển người, form cập nhật phần thông tin duyệt mà không đụng vào chữ đang gõ.

**Chống gửi đôi:** mỗi thao tác chuyển trạng thái và gửi trực tiếp lấy **khoá hàng** (`SELECT … FOR UPDATE`) rồi **đọc lại trạng thái**; chỉ trạng thái hợp lệ mới được đi tiếp. Hai người duyệt cùng lúc, hoặc người duyệt và người soạn bấm Send now cùng lúc, chỉ một bên gửi.

**Cấu hình** (Settings > General Settings, khối **Email Composer**):
- *Require approval*: mỗi công ty. Bật thì **không ai** gửi trực tiếp được: menu Send chỉ còn "Request approval", và máy chủ từ chối `send` dù giao diện có bị qua mặt (người duyệt vẫn có thể là chính mình).
- *Delete unfinished emails after (days)*: mặc định **180**. Email nào, ở trạng thái nào, quá số ngày này không có tác động (sửa, đổi trạng thái, quyết định) thì bị dọn bởi `@api.autovacuum`. Giá trị không hợp lệ (≤ 0) thì dùng 180. Xoá email kéo theo xoá hoạt động.

## 6. Sổ địa chỉ

- Model `dwo.mail.address`, một dòng cho mỗi cặp (email chuẩn hoá chữ thường, công ty), unique ở DB.
- **Dùng chung theo công ty** (record rule `company_id in company_ids`), vì đa số doanh nghiệp muốn chia sẻ danh bạ khách.
  Xem xét lại nếu khách hàng lo lộ email giữa các user.
- Chỉ lưu địa chỉ **không** thuộc user hay partner (user và partner đã được gợi ý từ nguồn của chúng).
- Gợi ý theo thứ tự: user, partner, sổ địa chỉ. Một địa chỉ chỉ xuất hiện một lần dù có ở nhiều nguồn.
- Quản trị viên xem và sửa tại Settings > Technical > Email > Email Address Book.

## 7. Gửi email: điều gì xảy ra ở backend

`dwo.mail.composer._send_email` là **nơi duy nhất** gửi: `send` (Send now, có kiểm tra *Require approval*) và việc duyệt (chạy với người soạn: `with_user(author).with_company(company)`) đều gọi nó. Nó gọi `message_post` với:

| Tham số | Giá trị | Lý do |
|---|---|---|
| `outgoing_email_to` | To | Core v19 biến thành **một** `mail.mail` với `email_to` là cả danh sách, nên người nhận thấy đúng To |
| `outgoing_email_cc` | Cc | Thêm bởi module này; đi xuống `mail.mail.email_cc` |
| `outgoing_email_bcc` | Bcc | Thêm bởi `dwo_mail_bcc` |
| `notify_skip_followers` | `True` | Thư chính thức **không** thông báo follower |
| `partner_ids` | không đặt | Nếu đặt partner, core gửi mỗi partner một email riêng và mất header To/Cc thật |
| `email_layout_xmlid` | `dwo_mail_compose.mail_layout_official` | Layout tối giản: chỉ body, không header thông báo, không nút truy cập, không footer |
| `mail_auto_delete` | `False` | Core xoá `mail.mail` của thông báo sau khi gửi. Với thư chính thức, giữ lại để tra cứu trạng thái gửi, lỗi và nội dung đã ra khỏi hệ thống (menu Technical > Email) |
| `email_add_signature` | `False` | Chữ ký đã nằm trong body ở dạng sửa được |
| `dwo_is_from_compose` | `True` | Cờ phân biệt thư chính thức |
| `parent_id` | email tham chiếu | Dựng chuỗi thread; Message-Id, References giữ nguyên của core |

**Khách trả lời quay về thread:** module không đụng vào Message-Id, References, Reply-To mặc định của core.
Thư trả lời mang `In-Reply-To` khớp `mail.message.message_id` nên mail gateway đưa vào đúng record
(đã có test mô phỏng).

Kiểm tra trước khi gửi: có ít nhất một To; mọi địa chỉ hợp lệ; From nằm trong danh sách được phép
(`_dwo_allowed_from_addresses`: email user, email công ty, địa chỉ gửi mặc định của alias domain); người dùng có quyền
đăng bài trên record. Địa chỉ trùng giữa To, Cc, Bcc được loại tự động.

## 8. Các quyết định thiết kế

| # | Quyết định | Lý do |
|---|---|---|
| P1 | Thêm cờ `dwo_is_from_compose`, **không** thêm giá trị vào `message_type` | Core đã dùng `email` (thư đến) và `email_outgoing` (mailing); thêm giá trị mới dễ xung đột logic có sẵn |
| P2 | Gửi bằng `outgoing_email_to/cc/bcc`, không dùng `partner_ids` | Cần **một** email thật với To/Cc nhìn thấy được, như Gmail/Outlook |
| P3 | Thư chính thức không notify follower | Tách rõ với Send message; tránh follower ngoài nhận thư không định gửi |
| P4 | Toàn bộ luật nội dung ở backend (`dwo.mail.composer`); JS chỉ hiển thị và sửa | Test được bằng unit test, một nguồn sự thật, dễ nâng cấp |
| P5 | Quote Outlook trong body, id `divRplyFwdMsg` | Odoo nhận diện để gập; người nhận dùng Outlook thấy đúng kiểu quen; sửa được |
| P6 | Không bao giờ in Bcc trong quote | Tránh lộ Bcc khi reply thư mình đã gửi |
| P7 | Date theo timezone người soạn, chốt vào body | Người đọc bản nháp và người nhận thấy cùng một giá trị |
| P8 | Một người có **nhiều** email chưa gửi trên một bản ghi (đã đổi so với bản đầu: một draft) | Danh sách ở dưới form, soạn song song, không ghi đè; cần thiết cho luồng duyệt |
| P9 | Xoá draft đưa form về mặc định ngay tại chỗ; Reply/Forward mở email mới | Người dùng không phải mở lại form; không mất email đang soạn |
| P10 | Sổ địa chỉ dùng chung theo công ty, chỉ lưu địa chỉ ngoài user/partner | Ít trùng; không nhân đôi dữ liệu có sẵn |
| P11 | From mặc định là user hiện tại và bắt buộc; chỉ được chọn trong danh sách cho phép | Tránh giả mạo người gửi |
| P12 | Bcc làm ở module tách biệt `dwo_mail_bcc` (miễn phí) | Dùng độc lập được, đóng góp cộng đồng; module này chỉ phụ thuộc, không sửa lại logic Bcc |
| P13 | Trình soạn là editor HTML chuẩn của Odoo (`html_editor` `Wysiwyg`), cấu hình như widget `html_mail`: bỏ plugin cột, link mở tab mới. Khi gửi, CSS được chuyển thành inline style (`toInline`) | Cùng trải nghiệm với composer gốc (link, bảng, màu, căn lề, undo, dán từ Word); mail client không đọc CSS ngoài nên phải inline. Nhúng thẳng `Wysiwyg`, không qua widget field, vì form này không phải một record |
| P14 | Ảnh chèn bằng menu (nút Image, lệnh `/image`), dán hoặc kéo thả đều được **tải lên thành attachment của record** và chèn bằng link có access token. Không nhúng base64. Việc tải lên chạy trước mỗi lần tự lưu và trước khi gửi | Cùng cách của composer gốc; draft và email không phình vì blob base64; người nhận thấy ảnh qua link tuyệt đối do Odoo tạo khi gửi (`_replace_local_links`) |
| P15 | Template: người nhận **thêm vào**, không thay; gỡ phần template trước thêm khi đổi template | Reply-all có sẵn người nhận cần giữ; đổi template không làm người nhận tích luỹ |
| P16 | Template chỉ lấy theo `model` của record và kiểm tra lại ở backend | Không áp template sai model (placeholder sẽ lỗi hoặc sai nghĩa); không tin dữ liệu từ client |
| P17 | Chọn template khi đã soạn dở: hỏi 3 nút Overwrite, Add after my text, Cancel; "đã soạn dở" so với snapshot lúc nạp hoặc lúc template điền gần nhất | Không làm mất chữ người dùng một cách âm thầm; so snapshot (không so với giá trị mặc định cứng) để template chọn tiếp không bị coi là chữ của người dùng |
| P18 | Template dùng `Many2XAutocomplete`; From dùng `AutoComplete` trên danh sách địa chỉ được phép | Template là bản ghi nên dùng many2one thật (tìm kiếm, domain). From là địa chỉ, không phải bản ghi, và phải bị giới hạn theo danh sách cho phép |
| P19 | Reply-To mặc định theo `_notify_get_reply_to` của model, hiển thị và sửa được, cảnh báo khi địa chỉ nằm ngoài Odoo | Giữ thư trả lời quay về bản ghi (mục tiêu của cả module) nhưng cho người dùng chủ động quyết định; không ép về hộp thư của mail server |
| P20 | Cc và Bcc là nút bên phải ô To, hiện sẵn khi có giá trị; tính năng phụ vào menu Advanced | Form gọn cho người mới, đủ cho người cần |
| P21 | Không giới hạn trùng địa chỉ giữa To, Cc, Bcc (chỉ chặn trùng trong cùng một ô) | Yêu cầu của người dùng; `dwo_mail_bcc` (D9) vẫn chỉ gửi một lần một địa chỉ ở tầng gửi |
| P22 | Menu Template dùng lại logic của `mail_composer_template_selector`; Save as Template sao chép đính kèm và bỏ khối quote | Quen thuộc với người dùng Odoo; template không mang email của khách và không làm mất file đang soạn |
| P23 | Send email là menu hai lựa chọn; *Require approval* theo công ty, **kiểm tra ở máy chủ** | Ẩn nút không đủ; người dùng có thể gọi RPC trực tiếp |
| P24 | Người duyệt nhiều người, một người duyệt là gửi, một người từ chối là từ chối; chọn chính mình được | Yêu cầu; quyết định đầu tiên thắng nên không cần bỏ phiếu |
| P25 | Duyệt gửi bằng `with_user(author).with_company(company)` qua `_send_email` | Mọi kiểm tra (nội bộ, From được phép, đính kèm của mình, quyền đăng) chạy với người soạn |
| P26 | Khoá hàng rồi đọc lại trạng thái cho mọi chuyển trạng thái và gửi trực tiếp | Hai người duyệt, hoặc người duyệt và người soạn, không thể cùng gửi |
| P27 | Lưu nội dung đã inline style ở mỗi lần tự lưu | Máy chủ không chạy được `toInline`; thư gửi từ trình duyệt và từ máy chủ giống nhau |
| P28 | Thông báo: `message_notify` (email) + bus theo người + hoạt động; ghi vết bằng ghi chú (`mt_note`) | `message_post` kiểu comment sẽ đăng ký người nhận theo dõi và gửi mọi dòng nhật ký về sau |
| P29 | Hoạt động đánh dấu xong khi duyệt, từ chối, gửi trực tiếp, xoá | Danh sách việc cần làm sạch |
| P30 | Dọn email sau N ngày không tác động, ở mọi trạng thái; N trong Settings, mặc định 180 | Yêu cầu; một nơi cấu hình, một cron |
| P31 | Người duyệt từng được giao vẫn đọc được email (trường lịch sử) | Người đã chuyển đi vẫn mở lại được link trong email cũ |
| P32 | Khi form email mở, vùng message của chatter ẩn bằng `display: none !important`, không gỡ khỏi DOM | Form lấp đầy chỗ; danh sách message giữ nguyên vị trí cuộn và trạng thái khi đóng form |
| P33 | Thân thư thấp còn khoảng 2/3 và có Expand dùng chính editor đó (khung cố định toàn màn hình) | Không có hai editor phải đồng bộ; không mất vị trí con trỏ hay lịch sử hoàn tác |
| P34 | Email mở mặc định là email vừa chọn trên màn hình này, không có thì email **tạo** gần nhất (mọi trạng thái); lựa chọn nhớ trong chatter đến khi đổi màn hình hoặc tải lại | Yêu cầu; ngày tạo ổn định hơn ngày sửa nên form không "nhảy" sang email vừa gõ vài chữ |
| P35 | Danh sách xếp theo ngày tạo, hiện ngày tạo và ngày cập nhật cuối, xoá được ở mọi trạng thái chưa gửi, có xác nhận trừ nháp, cuộn khi dài | Yêu cầu; xoá bản chờ duyệt vẫn báo người duyệt như thường |
| P36 | + New email, Reply và Forward tạo bản nháp trong DB ngay khi mở; riêng form mở lần đầu mà chưa có email nào thì chỉ lưu từ lần sửa đầu | Yêu cầu: email mới có trong danh sách và nhớ được ngay; mở form không tạo rác khi người dùng chỉ xem |
| P37 | Tiêu đề form luôn là "Compose email"; Delete draft đặt cạnh Send, outline secondary, hover đỏ | Yêu cầu; nút huỷ nằm gần nút gửi nhưng không nổi bật như nút gửi |
| P38 | Mọi thao tác xoá (email, dòng danh sách, tệp đính kèm) đều qua hộp xác nhận | Yêu cầu; xoá email chờ duyệt còn ảnh hưởng người duyệt |
| P39 | Cảnh báo Reply-To dùng lời "may/might", không khẳng định | Module chỉ biết catchall và alias của Odoo, không biết mọi cách thu thư của hệ thống |
| P40 | Form và danh sách email là hai khung viền riêng | Phân vùng rõ: đang soạn cái gì, và các email còn lại |
| P41 | Một thay đổi chỉ là "đã sửa" khi khác với nội dung editor vừa nạp (đường lưu muộn), còn sự kiện change của editor luôn tính là sửa | Không sinh bản nháp thừa khi mở, đóng hay bấm dòng; không bỏ sót chữ gõ ngay trước khi đóng |
| P42 | Trước khi lưu lúc đóng, địa chỉ đang gõ dở trong ô To, Cc, Bcc được chuyển thành badge | Draft giữ đúng thứ người dùng đã gõ |
| P43 | Người duyệt chọn từ "Search more…" được tra tên bằng `res.users` khi popup chỉ trả id | Popup của Odoo chỉ trả `{id}`; thiếu bước này chip người duyệt rỗng tên |

## 9. Bảo mật

- **API của composer** (`dwo.mail.composer`) chỉ dành cho **người dùng nội bộ**; portal và public bị từ chối ở mọi phương thức, vì API đọc tin nhắn bằng quyền cao để dựng quote.
- Chỉ **email** (thư đến hoặc thư chính thức) mới làm được tham chiếu của Reply/Forward; ghi chú nội bộ và tin thảo luận thì không.
- **Tệp đính kèm:** chỉ nhận tệp tạm do chính người dùng tải lên cho composer; id lạ bị từ chối. Việc duyệt chạy với người soạn nên cũng chỉ thấy tệp của người soạn.
- `outgoing_email_cc` và `outgoing_email_bcc` chỉ nhóm `base.group_user` đọc được; chỉ gửi xuống client cho người dùng nội bộ.
- **Email lưu trữ (`dwo.mail.email`):**
  - đọc: người soạn, người duyệt hiện tại và mọi người từng là người duyệt (trường lịch sử), cộng quản trị viên;
  - ghi, tạo, xoá: **chỉ người soạn** (và quản trị viên). Người duyệt không sửa được nội dung; họ quyết định qua các phương thức `action_approve`, `action_reject`, `action_reassign`, mỗi phương thức kiểm tra họ có đang là người duyệt không sau khi khoá hàng;
  - người duyệt không cần quyền đọc bản ghi gốc để xem và duyệt; nút "Open the record" chỉ hiện khi họ có quyền.
- **Gửi trực tiếp** bị chặn ở máy chủ khi công ty bật *Require approval*, không chỉ bằng cách ẩn nút.
- Sổ địa chỉ: rule theo công ty; xoá chỉ cho `base.group_system`.
- Tệp đính kèm tạm tải lên qua `/mail/attachment/upload` với `is_pending`, theo cơ chế của core.
- HTML vào form đến từ server đã làm sạch (`mail.message.body`, `dwo.mail.email.body`) và được editor của Odoo làm sạch thêm; module không tin nội dung thô.

## 9b. Nâng cấp từ bản có `dwo.mail.draft`

Bản đầu lưu một nháp mỗi người trong `dwo.mail.draft`. Model đó đã được thay bằng `dwo.mail.email`. Khi chạy `-u dwo_mail_compose` trên DB cũ: model, quyền và rule cũ được dọn sạch (đã thử trên bản sao của DB dev: không lỗi, không cảnh báo); bảng `dwo_mail_draft` còn lại nhưng không còn dùng (có thể `DROP TABLE dwo_mail_draft`); **các nháp cũ không được chuyển sang** model mới (module chưa phát hành, nên không có script chuyển).

## 10. Giới hạn đã biết (cho bản sau)

- Cc/Bcc chưa có tracking gửi từng địa chỉ: core chỉ tạo `mail.notification` cho To.
- Ảnh trong thư là link về server Odoo (kèm access token), nên người nhận chỉ thấy ảnh khi server truy cập được từ internet và mail client của họ cho tải ảnh từ xa. Muốn chắc chắn, dùng nút Attach. Chưa chèn được video.
- Đường chèn ảnh bằng hộp thoại media dùng code của core, chưa có tour riêng; tour hiện chỉ kiểm đường dán ảnh.
- Việc quên lựa chọn email khi đổi màn hình hoặc tải lại trang dựa vào vòng đời của chatter; tour kiểm tra phần "nhớ lại khi đóng rồi mở lại", chưa kiểm tự động phần quên (cần kiểm tay).
- Thông báo trên màn hình (bus) có kiểm tra ở phía máy chủ (nội dung gửi đi), chưa có tour cho phía trình duyệt (cần websocket thật).
- Sau khi tải lại từ email đã lưu, form không còn nhớ phần nào do template thêm vào; đổi template lúc đó không gỡ được phần cũ.
- Email chỉ có người nhận trong Bcc không gửi được (cần ít nhất một To), và Cc chỉ hỗ trợ cho đúng một `mail.mail` mà Send email tạo.
- Thông báo email cho người duyệt theo tuỳ chọn thông báo của từng người dùng ("Handle by Emails" hay "Handle in Odoo").
- Người duyệt chưa có cách xem hàng loạt ngoài menu Email Approvals và danh sách hoạt động.
- Chưa có xem trước và chưa có lên lịch gửi (core có `mail.scheduled.message`, chưa nối).
- Email gửi cho nhiều bản ghi cùng lúc (batch) chưa hỗ trợ.
- Chưa có bản dịch (`i18n`); chuỗi giao diện là tiếng Anh.
- Chưa có trang mô tả cho Odoo Apps (`static/description`), icon, banner (dùng skill `odoo-apps-listing`).
- Vì module phụ thuộc `dwo_mail_bcc`, module này phải được đăng cùng hoặc sau `dwo_mail_bcc` trên Odoo Apps.

## 11. Cấu trúc module

```
models/
  dwo_mail_composer.py   luật mặc định, quote, gửi (_send_email), API email lưu trữ, gợi ý (AbstractModel)
  dwo_mail_email.py      email lưu trữ + quy trình duyệt (trạng thái, khoá, hoạt động, thông báo)
  dwo_mail_decision.py   popup Approve / Reject / Reassign
  dwo_mail_address.py    sổ địa chỉ + gợi ý
  mail_message.py        dwo_is_from_compose, outgoing_email_cc, _to_store_defaults
  mail_thread.py         allow-list message_post, đưa Cc xuống mail.mail
  res_company.py / res_config_settings.py   Require approval, số ngày giữ email
views/                   trang chi tiết email, danh sách, menu Email Approvals, popup, khối Settings
data/                    layout thư sạch, loại hoạt động "Email approval"
security/                quyền và rule (tác giả, người duyệt, lịch sử người duyệt, quản trị)
static/src/
  composer/              DwoEmailComposer, DwoAddressInput, menu Template, popup lưu template,
                         popup nhờ duyệt, hộp thoại "ghi đè hay nối thêm"
  chatter/               nút Send email, mở form
  message/               badge Email, dòng From/To/Cc, action Reply/Forward
  approval_service.js    thông báo trên màn hình (bus) kèm nút mở email
```

Điểm mở rộng: `_dwo_allowed_from_addresses()` (đổi danh sách From), `_compute_defaults()` (đổi luật mặc định),
`dwo.mail.address.dwo_suggest()` (thêm nguồn gợi ý), `_send_email()` (một nơi duy nhất để chặn hay ghi log mọi email chính thức).

## 11b. Ghi chú giao diện

Odoo 19 không định nghĩa các biến CSS `--bs-*` (ví dụ `--bs-success`). Module dùng lớp tiện ích Bootstrap (`bg-success`, `text-bg-*`) và biến SCSS (`$primary`, `$danger`), và tour kiểm màu thật của chấm báo draft bằng `getComputedStyle`.

## 12. Kiểm thử

```
export ODOO_BROWSER_BIN="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"   # nếu không có Chrome
odoo-bin -c <conf> -d <db_moi> --http-port=8097 -i dwo_mail_compose --test-tags /dwo_mail_compose,/dwo_mail_bcc --stop-after-init --log-level=warn
```

(`--http-port` khác cổng đang dùng nếu bạn đang chạy Odoo dev.)

- **Backend, composer (`test_composer.py`):** mặc định A/B/C/D, subject không lặp tiền tố, quote (Outlook, múi giờ JST và `UTC+07:00`, không Bcc, bỏ dòng Cc rỗng),
  gửi một email thật (To/Cc nhìn thấy, Bcc chỉ ở envelope, follower không nhận), cùng một địa chỉ ở To/Cc/Bcc, layout sạch, đăng ký sổ địa chỉ,
  khách trả lời quay về đúng thread, email lưu trữ (lưu nối tiếp một id, nạp, xoá, nhiều email, riêng tư, gửi trực tiếp xoá bản lưu, banner email mới), gợi ý không trùng,
  unique của sổ địa chỉ, quyền (portal bị chặn, ghi chú không quote được, tệp lạ bị từ chối), template (mọi trường được tính, tệp đính kèm là bản sao gửi được, sai model bị từ chối, From không được phép, chế độ Default Recipients), Save as Template (bỏ quote, sao chép đính kèm), Reply-To.
- **Backend, duyệt (`test_approval.py`):** nhờ duyệt (trạng thái, hoạt động, thông báo email và bus), lời nhắn tuỳ chọn, tự chọn mình, email không gửi được thì không cho nhờ duyệt, duyệt gửi bằng người soạn và đóng hoạt động, **hai người duyệt chỉ gửi một email**, duyệt sau khi người soạn đã gửi trực tiếp bị từ chối, người không phải người duyệt bị chặn, **người duyệt không có quyền đọc bản ghi gốc vẫn mở và duyệt được**, người duyệt không sửa được nội dung, từ chối rồi sửa rồi nhờ lại, quyền đọc theo lịch sử người duyệt, Reassign chỉ thay người đang thao tác, popup quyết định, gửi trực tiếp và xoá khi đang chờ, sửa khi đang chờ (cờ "đã sửa sau khi nhờ"), email đã gửi không sửa được, danh sách chỉ có email chưa gửi, **Require approval bị từ chối ở máy chủ**, giữ email theo cấu hình ngày (mọi trạng thái, giá trị xấu dùng 180, hoạt động đi cùng email, sửa thì lùi hạn xoá).
- **Tour trình duyệt (`test_composer_tour.py`):** gõ trong editor chuẩn, dán ảnh, gửi email (Cc/Bcc sau nút, trùng địa chỉ giữa các ô), giao diện (nút ✕, dấu `*` đỏ, (i) cùng dòng, ghi chú, biểu tượng gửi, Advanced → Reply-To), Cc hiện sẵn khi có giá trị, draft (lưu, chấm xanh, nạp lại, xoá), Reply by email, menu Template (chọn, gỡ, hỏi ghi đè/nối thêm, Save as Template), nhờ duyệt (popup, trạng thái chờ, danh sách), Require approval (không còn Send now), bố cục (vùng message ẩn khi mở và hiện lại khi đóng, thân thư thấp hơn, Expand toàn màn hình, thu lại bằng nút và bằng Esc), hai khung riêng, mọi thao tác xoá có hỏi (Cancel giữ lại, Delete xoá; cả tệp đính kèm), nút Delete draft cạnh Send, đóng form luôn lưu và không tạo bản nháp thừa (mở rồi đóng không gõ gì, bấm dòng liên tục, xoá rồi bấm dòng), chọn người duyệt trong popup "Search more" giữ tên, danh sách nhiều email (thứ tự theo ngày tạo, ngày tạo/cập nhật, cuộn, nhớ email đã chọn khi đóng rồi mở lại, xoá nháp và xoá email bị từ chối), **người duyệt mở trang chi tiết và duyệt qua popup**.
- Đã thử phá hai chốt chính để chắc test bắt được: bỏ kiểm tra trạng thái sau khoá (test hai người duyệt fail) và bỏ kiểm tra *Require approval* ở `send` (test tương ứng fail).
- **Chưa kiểm bằng mắt** trên giao diện thật ngoài các tour; nên xem thử trên một DB demo trước khi phát hành. Màu chấm khi hover nút Send email dùng `currentColor`; trạng thái `:hover` của CSS không mô phỏng được trong tour.
