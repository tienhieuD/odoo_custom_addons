# dwo_record_concurrency (Record Concurrency Guard)

Cảnh báo **mềm** khi hai người cùng sửa một bản ghi: người lưu sau thấy bảng so sánh "giá trị của tôi / dữ liệu mới nhất / ai lưu cuối" và tự chọn **Force Save**, **Discard My Updates** hoặc **Cancel**. Làm cho Odoo **12 đến 20** (16 đến 20 là OWL, 12 đến 15 là kiến trúc legacy).
Bán trên Odoo Apps: **39 USD**, license **OPL-1**, tác giả DUO-TEK Software Vietnam, tên hiển thị **Record Concurrency Guard** (24 ký tự, store giới hạn 25), **tên kỹ thuật giữ nguyên `dwo_record_concurrency`** (đổi tên kỹ thuật làm gãy các DB đã cài).
Chưa có email `support` trong manifest (chủ dự án không cấp), nên trình kiểm tra của skill luôn báo 1 WARN này: không cần sửa.
Version manifest hiện tại: `<NN>.0.1.1.0` (1.0 là bản cũ chỉ dùng bus).

## Ý tưởng và quyết định thiết kế (đọc trước khi sửa)

1. **Chỉ chặn mềm, không bao giờ từ chối ghi.** Chủ dự án quyết định: server **không `raise`** vì xung đột. Lý do đã cân nhắc: khoá lạc quan bằng `write_date` tạo cảnh báo giả (một cron, workflow hay field khác của người khác cũng đổi `write_date`), làm user mất dữ liệu đang gõ nếu client không bắt lỗi đúng, phải xử lý mọi đường ghi (nút object, wizard, onchange, import, RPC), và không khả thi nếu chỉ dùng Python (server không biết user đang cầm phiên bản nào). Lõi Odoo có khoá kiểu này đến 16 và đã bỏ từ 17 (chỉ kiểm chứng phía Python, đừng trích như "lịch sử đã xác nhận").
2. **Phát hiện ở lúc lưu, theo từng field.** Khi form mở, client chụp giá trị các field được theo dõi (`dwo_snapshot`). Khi lưu, server so snapshot với giá trị hiện tại **chỉ trên các field người dùng đang sửa** (`dwo_check_conflict`). B sửa field khác thì A không bị hỏi. Nếu RPC kiểm tra lỗi thì vẫn cho lưu.
3. **Bus chỉ để báo sớm, không phải cơ chế duy nhất.** Bản cũ phụ thuộc bus nên bus rớt hoặc mở form sau khi người khác đã lưu thì không có cảnh báo. Giờ bus chỉ gây toast "X changed fields you are editing" và cờ `stale` cho `beforeunload`.
4. **Bus không mang giá trị.** Bản cũ phát `data` (giá trị mới đọc bằng quyền của người ghi) lên kênh chuỗi `dwo_record_presence:<model>:<id>`; ai đăng ký kênh đoán trước là nhận được, kể cả khi không có quyền đọc bản ghi, và field binary đẩy cả base64. Giờ chỉ gửi `{model, res_id, user_id, user_name, current_tab_id, state, fields[]}` và **kênh bị lọc theo quyền đọc** bản ghi.
5. **Cache cấu hình.** `write()` bị override trên `base` nên chạy cho mọi model; không được `search` mỗi lần. Danh sách field theo dõi được `ormcache` theo tên model và xoá khi cấu hình đổi.
6. **Mô tả chỉ nêu điều đúng với code, kể cả giới hạn:** chỉ form view (không sửa tại chỗ trong list, kanban, import, API ngoài), cần bus để có toast, field phải `store` và không readonly.

## Cấu trúc (bản 19 là bản chuẩn)

```
models/dwo_model_concurrency.py   model cấu hình (model_id + field_ids); _get_watched_field_names (ormcache);
                                  get_watched_fields / dwo_snapshot / dwo_check_conflict / _normalize_value
models/base.py                    override write(): sau khi ghi, nếu model có cấu hình và field đổi thì publish ping
models/dwo_record_presence.py     publish_presence(): gửi ping KHÔNG có giá trị (xem khác biệt bus theo bản)
models/ir_websocket.py            16 đến 20: lọc kênh presence theo quyền đọc (_build_bus_channel_list)
controllers/main.py               12 đến 15: cùng việc đó bằng cách override route poll của bus
security/ir.model.access.csv      user: chỉ đọc; base.group_system: toàn quyền (20: ir.access.csv)
views/                            form/list/search + menu Settings > Technical > Concurrency > Model Concurrency
static/src/utils/tab_id.js        id riêng mỗi lần tải trang (DWO_TAB_ID) và tiền tố kênh
static/src/components/RecordPatch gắn current_tab_id vào context khi lưu
static/src/components/FormControllerPatch   toàn bộ logic client (snapshot, kiểm tra, dialog, toast, beforeunload)
static/src/components/ConcurrencyDialog     dialog OWL (bảng so sánh, tự escape, không dựng chuỗi HTML)
static/description/               index.html, icon, banner, flow, screenshot_1..3 (sinh bằng skill odoo-apps-listing)
tests/test_concurrency.py         Python (20 test; 19 ở 12-15)       tests/test_concurrency_tour.py + static/tests/tours/concurrency_tour.js (3 tour)
```
12 đến 15: client là một file `static/src/js/concurrency.js` (không có thư mục components, không có dialog OWL).

## Luồng chạy

1. Form mở -> client hỏi `get_watched_fields(model)` (cache theo model cho cả trang) rồi `dwo_snapshot(model, id)`: dict giá trị đã chuẩn hoá của các field theo dõi. Đồng thời `addChannel('dwo_record_presence:<model>:<id>')`.
2. Người khác `write` field được theo dõi -> `BaseModel.write` publish ping (kèm `current_tab_id` lấy từ context). Client nhận: bỏ qua ping của chính tab mình (`DWO_TAB_ID`), còn lại ghi nhớ `stale` + hiện toast **nếu người dùng đang sửa đúng field đó**.
3. Người dùng Save (nút, pager, rời form, tab bị ẩn đều đi qua một điểm duy nhất, xem bảng khác biệt) -> lấy các field đang sửa giao với field theo dõi -> `dwo_check_conflict(model, id, snapshot, dirty)` -> danh sách xung đột `{name, label, type, server, write_uid_name}`. Rỗng thì lưu bình thường. Không rỗng: tab đang ẩn thì **giữ nguyên thay đổi, không hỏi, không ghi đè**; còn lại hiện dialog.
4. Dialog: Force Save (đi tiếp), Discard My Updates (huỷ phần sửa **rồi tải lại bản ghi để hiện dữ liệu mới nhất**), Cancel (ở lại, giữ phần sửa). Lưu thành công thì xoá `stale` và chụp lại snapshot.
5. `beforeunload`: nếu form dirty và đã biết bản ghi bị người khác đổi thì `preventDefault()` **đồng bộ** (sau `await` thì không còn tác dụng) và không gọi `super`, tránh urgent save ghi đè.

`_normalize_value` chuẩn hoá để so sánh ổn định: many2one -> id; x2many -> danh sách id đã sắp xếp (đổi thứ tự không phải xung đột); float -> làm tròn theo digits; date/datetime -> chuỗi; selection -> (giá trị, nhãn); binary -> sha1 (chỉ tính khi field đó nằm trong tập đang sửa).

## Khác biệt theo phiên bản (nơi dễ hỏng khi port)

| | 20 | 19 | 18 | 17 | 16 | 15 | 14 | 13 | 12 |
|---|---|---|---|---|---|---|---|---|---|
| Client | OWL 3 | OWL | OWL | OWL | OWL | legacy | legacy | legacy | legacy |
| Điểm chặn khi lưu | `FormController.onWillSaveRecord(record, changes)` | idem | idem | idem | patch `Record.save` (basic_relational_model); controller gắn `model.dwoBeforeSave/dwoAfterSave` | `FormController.include({saveRecord})` | idem | idem | idem, trả **jQuery Deferred** |
| Theo dõi record đang mở | `onWillLoadRoot(config)` + `onRecordSaved` | idem | idem | idem | `useEffect` theo `[resModel, resId]` | override `update()` | idem | idem | idem |
| Phần đang gõ chưa vào record | `root.getChanges()` | idem | idem | `await root.isDirty()` rồi `root._getChanges()` | `await record.askChanges()` rồi `localData[h]._changes` | `renderer.commitChanges(handle)` | idem | idem | idem |
| Lọc kênh bus | `ir.websocket` | idem | idem | idem | idem | controller `poll` | idem | idem | idem |
| Quyền đọc bản ghi | `has_access('read')` | idem | idem | `check_access_rights` + `check_access_rule` | idem | idem | idem | idem | idem |
| Gửi ping | `_sendone(ch, 'dwo_record_presence', msg)` | idem | idem | idem | idem | idem | `sendone(ch, {'type','payload'})` | idem | idem |
| Dạng notification ở client | `{type, payload}` | idem | idem | idem | idem | `{type, payload}` | `[channel, {type, payload}]` | idem | idem |
| Xoá cache cấu hình | `_clear_cache_name = 'default'` (core tự xoá; **không còn `registry.clear_cache`**) | `registry.clear_cache()` trong create/write/unlink | idem | idem | `registry.clear_caches()` | idem | idem | idem | idem |
| File access | `security/ir.access.csv` (`operation` = `r`/`crud`, `model_id` là tên model) | `ir.model.access.csv` | idem | idem | idem | idem | idem | idem | idem |
| View list | `<list>` | `<list>` | `<list>` | `<tree>` | `<tree>` | `<tree>` | `<tree>` | `<tree>` | `<tree>` |
| Cú pháp view | `invisible="active"`, `domain="field_domain"` | idem | idem | idem | **attrs + domain tường minh** | idem | idem | idem | idem |
| `ondelete='cascade'` của `model_id` | có | có | có | có | có | có | có | **không** | **không** |
| Assets | `assets` trong manifest | idem | idem | idem | idem | idem | `views/assets.xml` | idem | `views/assets.xml`, tour chung bundle backend (không có `web.assets_tests`) |
| Header `/** @odoo-module **/` | không cần | không cần | không cần | **cần** | cần | n/a (`odoo.define`) | idem | idem | idem |

Còn lại cần nhớ khi chép giữa các bản:
- **Owl 3 (20):** không có `static props`; khai báo bằng `props = useProps({...t.function()...})`, template dùng tiền tố `this.` (`this.props.conflicts`, `this.choose(...)`), `t-out` thay `t-esc`; xem `ConfirmationDialog` của core làm mẫu.
- **16:** `owl="1"` bắt buộc trên `<t t-name>`; `Component` lấy từ global `owl` (không có `@odoo/owl`); `patch(obj, "tên.duy.nhất", {...})` và `this._super`, mà **`_super` chỉ dùng được trước `await` đầu tiên** (lấy `const superSave = this._super.bind(this)` ngay đầu hàm); `jsonrpc` có chữ ký khác nên tour dùng `fetch`/XHR.
- **17 đến 12:** dialog dùng getter `title` (`title.translate="..."` báo "Invalid prop suffix"); notification là `{type, payload}` hay `[channel, message]` như bảng.
- **15 đến 12:** không có model `ir.websocket` (khai báo `_inherit` sẽ lỗi), nên model `ir_websocket.py` **bị xoá** và thay bằng `controllers/main.py`. Route `poll` đóng cursor trước khi gọi `dispatch.poll` nên **phải lọc kênh trong `poll`**, không phải trong `_poll`. Override `poll` không cần `@route` (Odoo giữ route của hàm gốc). Hàm kiểm tra quyền dùng chung `dwo_channel_allowed(env, channel)` nằm ở `models/dwo_record_presence.py`.
- **12:** `do_warn` thay `displayNotification`; không có `with_user` (dùng `sudo(user)`), không có `new_test_user` (tự tạo user trong test), field ảnh là `image` (không phải `image_1920`), `res.currency.rate.name` là datetime.
- **13:** xoá `ir.model` kèm `ondelete='cascade'` làm tính lại field `related` đã lưu trên bản ghi vừa bị xoá và chặn việc xoá; bỏ cascade (hệ quả: xoá model thì dòng cấu hình còn lại với model trống, vô hại).

## Test

Chạy từ thư mục này: `tools/conc_test.sh <NN> <thư mục source odoo>` (xem phần cuối). Kết quả lần port gần nhất (đều qua, tour chạy thật):

| 20 | 19 | 18 | 17 | 16 | 15 | 14 | 13 | 12 |
|---|---|---|---|---|---|---|---|---|
| 25 test | 23 | 23 | 23 | 23 | 22 | 22 | 22 | 22 |

Python (20 test ở 16 đến 20, 19 test ở 12 đến 15 vì bỏ test của `ir.websocket`): ping chỉ có tên field (không giá trị), không ping cho field/model không theo dõi, cache được xoá đúng lúc (`assertQueryCount(0)` ở lần gọi thứ hai), chuẩn hoá từng kiểu field, xung đột chỉ trên field đang sửa, người ghi cuối, snapshot của bản ghi không tồn tại, lọc kênh theo quyền, quyền cấu hình.
Tour (3): `dwo_concurrency_conflict` (dialog hai giá trị, Cancel giữ phần sửa, rồi Force Save), `dwo_concurrency_no_conflict` (người khác đổi field không theo dõi thì lưu thẳng), `dwo_concurrency_discard` (Discard hiện dữ liệu mới nhất của server).
**Chưa có test tự động cho:** toast từ bus, `beforeunload`, việc giao tin thật qua websocket/longpolling.

## Kinh nghiệm sửa (những cái đã làm mất thời gian, đọc kỹ)

**Test chạy "qua" giả**
- Nếu không có Chrome, `HttpCase` **bỏ qua tour mà vẫn báo 0 failed** ("skipped ... Chrome executable not found"). Luôn xem số tour thực sự chạy. 16, 17 và legacy cần `tools/odoo_wrap.py` (vá đường dẫn Chrome và cổng) qua biến `WRAP`; `tools/conc_test.sh` in `skipped=` để thấy.
- Odoo 12 không in "test successful": kiểm tra bằng cách đếm các dòng `console log: Tour <tên>: step ...` và bước cuối phải `succeeded`.
- Bản 12 cần cài thêm `web_tour` (`INSTALL=dwo_record_concurrency,web_tour`).

**Tour**
- 17 trở xuống: khi có modal mở, tour tìm trigger **bên trong modal**; selector `.modal ...` thành "modal trong modal" và không bao giờ khớp. Dùng `.modal-title:contains(...)`, `button:contains(...)`, `table td:contains(...)`.
- 17: `run: "text X"` (không có `edit`), không có pseudo `:value()`; kiểm giá trị bằng `run` async (`this.$anchor.val()`) có vòng chờ.
- 16 trở xuống (tour legacy): **`run` trả về promise không được chờ.** Hai thứ làm tour chập chờn: (a) bước "người khác ghi" async chưa xong thì đã bấm Save; (b) snapshot cần hai RPC nối tiếp nên chưa có khi người khác ghi. Cách xử lý đang dùng: ghi bằng **XHR đồng bộ**, và chờ bằng **một phần tử hiển thị** được thêm sau 2 giây (`.dwo_wait_done`) rồi dùng làm trigger. Trigger dạng hàm trong tour legacy không dùng được (báo "visible trigger: 0").
- 18 trở lên: `run` async được chờ, dùng bình thường (`await` + `rpc`).
- Dạng URL: 18+ `/odoo/action-base.action_partner_form/<id>`, còn lại `/web#action=base.action_partner_form&id=<id>&view_type=form` (test chọn theo `odoo.release.version_info`).
- Form partner: field `name` là `textarea` (widget `text`), nhưng khi cài thêm `contacts` (partner_autocomplete) là `input`; legacy 12 đến 15 chính thẻ `<input>` mới có class `o_field_widget`. Selector tour nên chấp nhận cả hai.
- Chờ "form sạch" bằng `.o_form_view:not(:has(.o_form_status_indicator_buttons:not(.invisible)))`: tour chỉ khớp phần tử **đang hiển thị** nên không thể chờ `.invisible`; và class `.o_form_dirty` **không tồn tại ở 19** (bước kiểm tra qua ngay, tour kết thúc khi form còn dirty và Odoo báo "Tour finished with a dirty form view").
- Legacy 12 đến 15: form mở ở chế độ đọc, phải bấm `.o_form_button_edit` trước; kết thúc chờ `.o_form_view.o_form_readonly .o_field_widget[name=name]:contains(...)`.

**Python test**
- Patch bus từ registry, không import class: `patch.object(type(self.env['bus.bus']), '_sendone', ...)` (class tên `BusBus` ở 19 nhưng `ImBus` ở 18). Bản 12 đến 14 patch `sendone(channel, message)` và đọc `message['type']`.
- `setUpClass` có `env` chỉ từ 15; 12 đến 14 phải dùng `setUp` (script `legacy_setup.py`).
- Trong test dùng `new_test_user(..., groups=...)` (13+). Không dùng `assertQueryCount` cho thứ phụ thuộc cache chưa nóng.

**Client**
- **Phần người dùng đang gõ chưa nằm trong `record._changes`/`dirty`** cho tới khi field commit (blur hoặc lúc lưu). Handler của bus phải gọi `await root.getChanges()` (hoặc `isDirty()`/`askChanges`/`commitChanges` tuỳ bản) trước khi đọc các field đã sửa, nếu không toast **không bao giờ hiện** khi người dùng đang gõ. Và đừng viết `root.dirty ? await root.getChanges() : {}`: `dirty` cũng chưa bật.
- Ở 19, service `multi_tab` **không còn `currentTabId`** (mã cũ so `undefined === undefined` nên tab khác của cùng user bị coi là chính mình). Dùng `DWO_TAB_ID` tự sinh.
- Sau Discard phải **tải lại bản ghi**, nếu không form hiện lại giá trị lúc mở chứ không phải dữ liệu mới nhất. Thực hiện trong `setTimeout` vì bước kiểm tra đang chạy trong mutex của model (await trực tiếp sẽ deadlock).
- Mọi nơi dựng HTML từ giá trị người dùng phải đi qua template/escape (bản cũ dựng chuỗi HTML và chỉ escape một phần; legacy dùng `$('<span/>').text(...)`).
- Dùng API công khai khi có (`getChanges`) và chỉ rơi xuống `_getChanges` ở 17 trở xuống.

**Chụp ảnh / listing**
- Websocket **không giao tin** trong Chrome headless ở môi trường này (kể cả broadcast của core). Ảnh toast là phát lại đúng payload server đã ghi trong `bus_bus` qua `bus_service.trigger('notification', [...])` (cần `?debug=1` để lấy `odoo.__WOWL_DEBUG__.root.env.services`). Ảnh ghi rõ điều đó; muốn ảnh "thật" thì chụp tay trên hai trình duyệt.
- Ẩn huy hiệu debug (tên DB, "Administrator") bằng **một thẻ `<style>` với `!important`** (`.o_debug_manager, .oe_topbar_name {display:none !important}`, thêm `.o_notification_manager` khi chụp dialog). Đặt `style.display` trực tiếp bị OWL ghi đè khi render lại.
- Ảnh trong trang mô tả chụp từ giao diện **19** và dùng chung cho mọi bản; giao diện 12 đến 15 khác (nút Edit, dialog kiểu cũ). Chưa chụp riêng.
- Banner: tiêu đề quá dài bị icon che; chiều rộng chỉ vừa khoảng 11 ký tự ở dòng 1 (đang dùng "Concurrency" + "Guard Against Overwrites").

**Git**
- Khi `rsync` module từ bản này sang bản khác nhớ `--exclude __pycache__ --exclude .DS_Store`: bản 17, 18, 20 từng **track `.DS_Store`** nên bị báo xoá.
- Mỗi lần port là sao chép toàn bộ module rồi sửa; nếu đổi phần chung (Python, mô tả, test) phải đồng bộ lại sang các bản khác.

## Quy trình port / cập nhật (chuỗi nguồn)

Bản chuẩn là **19**. 20 và 18 chép từ 19 (xử lý riêng: `ir.access.csv`, `useProps`/`this.`, `_clear_cache_name` ở 20). 17 chép từ 18 rồi `tools/adapt_conc.py 17`. 16 chép từ 17 (viết lại `RecordPatch`/`FormControllerPatch`, `owl="1"`, tour `tour.register`). 15 chép từ 16 (viết lại client legacy; `tools/legacy_py.sh 15`, `legacy_tests.py`). 14 và 13 chép từ 15 bằng `tools/legacy_port.sh <NN>` (+ `legacy_view.py`, `legacy_setup.py`, `legacy_cascade.py` cho 13, `legacy_tour_wait.py`). 12 chép từ 13 (xem phần "12" ở trên).
`tools/adapt_conc.py` **không idempotent**: nó là bản ghi các sửa đổi đã áp cho bản 17 (từ bản 18) và được viết thêm từng đoạn; đọc nó như tài liệu "cần đổi gì", đừng chạy lại lên module đã port. Các script trong `tools/` ghi sẵn đường dẫn máy của chủ dự án (`/Users/hieu/Documents/Odoo/...`, thư mục scratchpad cho Chrome headless); chỉnh lại khi dùng ở máy khác.

Quy trình nên làm khi sửa một tính năng: sửa ở 19 + chạy test; chép sang 20 và 18 (kiểm tra theo bảng khác biệt); sang 17 rồi 16, rồi nhóm legacy; **chạy test từng bản** (`conc_test.sh`), commit từng bản, cập nhật wiki, chép `wiki/` sang mọi nhánh.

## Đóng gói và listing

- Cấu hình trang mô tả: `wiki/listings/dwo_record_concurrency.json`; sinh bằng skill `odoo-apps-listing` (`gen_assets.py`, `gen_flow.py`, `build_index.py`) rồi chép `static/description/*` y nguyên sang mọi bản, chỉ đổi `version` trong manifest. Chụp ảnh bằng `tools/shoot_listing.py`, bằng chứng từng bước bằng `tools/shoot_evidence.py`.
- Chạy `validate_listing.py` trên từng module: phải **0 FAIL**. Changelog trong trang: 1.1 (2026-11-05) và 1.0 (2026-04-12, ngày commit đầu tiên của module).
- Không để khuyến mãi, emoji, JS hay style ngoài danh sách cho phép trong `index.html`.

## Giới hạn đã biết / việc có thể làm tiếp

- Chỉ form view; chưa có list inline editable, kanban.
- Cấu hình đổi khi form đang mở thì form đó chưa cập nhật tập field theo dõi (chỉ ảnh hưởng form mở trước đó).
- Gỡ module: không để lại dữ liệu trong model khác (chỉ bảng cấu hình của chính nó); chưa kiểm tra quy trình gỡ như đã làm với `web_split_view`.
- Chưa test `beforeunload` và giao tin bus thật; chưa chụp ảnh riêng cho giao diện 12 đến 15.

## Chạy test nhanh

```bash
# 17 đến 20: trực tiếp; 12 đến 17 cần WRAP (vá đường dẫn Chrome)
tools/conc_test.sh 19 odoo-19.0.20260412
WRAP=tools/odoo_wrap.py tools/conc_test.sh 16 odoo-16.0.20261021
INSTALL=dwo_record_concurrency,web_tour WRAP=tools/odoo_wrap.py tools/conc_test.sh 12 odoo-12.0.20211011
```
Kết quả in `exit=… tours_ok=… skipped=…` (nhớ: `tours_ok` đếm "tour succeeded" nên chỉ có nghĩa từ 18; ở bản khác đếm `grep -c "test successful"` hoặc xem số bước). Log đầy đủ ở `/tmp/conc<NN>.log`.
