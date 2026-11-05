# web_split_view

Màn hình chia đôi: list bên trái, form của bản ghi đang chọn bên phải. Làm cho Odoo **12 đến 20**: 16 đến 20 viết bằng OWL (mô tả chính ở dưới), **12 đến 15 viết bằng kiến trúc legacy** (xem mục "Bản legacy 12 đến 15").
Bán trên Odoo Apps: giá **39 USD**, license **OPL-1** (đã bỏ file `LICENSE` public domain cũ), tác giả DUO-TEK Software Vietnam.
Chưa có email `support` trong manifest (chủ dự án không cấp), nên trình kiểm tra của skill luôn báo 1 WARN này: không cần sửa.

## Ý tưởng và quyết định thiết kế

- **Không bắt người dùng tạo view.** Bản đầu là một view type `split` phải tạo tay (`<split list_view_ref= form_view_ref=/>` + wizard trong menu debug): khó dùng, tốn công port. Bản hiện tại **tự thêm nút Split vào view switcher của mọi action cửa sổ có list và form**, dựng từ list, form và search view của chính action đó. View `<split>` tạo tay vẫn dùng được và **ghi đè** chế độ tự động cho model đó (view split mặc định của model được tìm theo model, nên áp cho mọi action của model).
- Nút Split chèn ngay sau list, **không bao giờ là view mặc định**.
- Tắt được: `Settings > Split View` (toàn DB, tham số `web_split_view.auto_split`) và checkbox `No split view` trên action (`ir.actions.act_window.no_split_view`, thấy ở developer mode).
- Trong chế độ split bấm dòng luôn mở form bên phải, **không sửa tại chỗ** (list bị ép không editable).
- Nút `New` ngoài cùng tạo bản ghi ở panel phải; nút New và pager của form nhúng bị ẩn bằng CSS. Nút expand (góc phải panel form) mở bản ghi ở form view đầy đủ của action; đã bỏ nút Reload vì thừa.
- Màn hẹp (< 768px): hai panel xếp chồng (chỉ có CSS, **chưa test trên điện thoại**).

## Cấu trúc

```
models/ir_actions.py          _compute_views: thêm (False, 'split') vào action.views; field no_split_view
models/base.py                _get_default_split_view() -> <split/> (view mặc định, không cần bản ghi view);
                              get_id_by_xmlid() cho list_view_ref/form_view_ref
models/ir_ui_view.py          type 'split' (selection_add); 18+: _get_view_info (icon + display name)
models/res_config_settings.py boolean web_split_view_auto <-> ir.config_parameter web_split_view.auto_split
models/create_view_split_wizard.py   wizard tạo/xóa view split tay (menu debug)
views/res_config_settings_views.xml  mục Settings riêng + checkbox trên form action
static/src/split_view/
  split_view.js               đăng ký view 'split' (ArchParser, Controller, buttonTemplate)
  split_arch_parser.js        đọc <split> (refs hoặc list/form inline); rỗng = dùng view của action
  split_controller.js         toàn bộ logic: dựng props cho list/form, chọn/tạo/xóa, expand, resizer, lưu trạng thái
  split_pane.js               host một view nhúng trong sub-env riêng (ẩn view switcher/breadcrumb của action)
  split_list_view.js          patch ListRenderer: tô sáng dòng đang mở (đọc env.splitState)
  split_view.xml / .scss      template + CSS (resizer, highlight, ẩn pager/New của form, màn hẹp)
  debug_items.js              menu debug thêm/xóa split view tay
tests/test_auto_split.py      kiểm tra views của action, opt-out, setting, view mặc định
tests/test_split_view_tour.py + static/tests/tours/split_view_tour.js   6 tour (split tay, auto, state, expand, back)
```

## Cách hoạt động (chế độ tự động)

1. Server: `ir.actions.act_window._compute_views` chèn `(False, 'split')` sau view list nếu action có list và form, không phải `target=new`, model không transient, không phải `res.config.settings`, chưa có split và `no_split_view` tắt.
2. `get_views([(False,'split')])` -> `_get_default_split_view` trả `<split/>`; `SplitArchParser` không thấy ref hay arch inline nên **lấy view id từ `this.env.config.views`** của action (list, form, search). Từ 16 đến 17 kiểu list tên là `tree`: code dò cả `list` lẫn `tree`.
3. `SplitController` dựng hai `View` nhúng (list trái, form phải), mỗi cái bọc trong `SplitPane` (sub-env: `splitState`, `config` với `viewSwitcherEntries: []`, không breadcrumb, `historyBack` đóng panel).
4. List nhúng nhận `selectRecord` (mở form bên phải) và bị ép không sửa tại chỗ (`readonly: true` ở 19/20, `editable: false` ở 16/17/18).

## Trạng thái được nhớ

| Gì | Ở đâu | Phạm vi |
|---|---|---|
| Độ rộng 2 panel | `localStorage` `web_split_view_width_<actionId>_<model>_<viewId>` | mỗi action, vĩnh viễn, theo trình duyệt |
| Bản ghi đang mở | `sessionStorage` `web_split_view_record_<cùng khóa>` | mỗi action, trong tab; F5 mở lại đúng bản ghi (kiểm tra còn tồn tại và còn khớp domain) |
| Search/filter/group by/phân trang/scroll của list, tab/scroll của form | state export của action service (`getGlobalState`/`getLocalState`), trả lại khi quay lại từ form đầy đủ; cũng dùng khi list remount sau khi lưu | trong phiên làm việc, không qua F5 |

**Không dùng tham số URL** (tránh xung đột với `debug=1` và router của Odoo; URL có `resId` còn làm Odoo mở form view thường).
Mỗi view nhúng export state vào recorder riêng của nó: từ 17 truyền `__getGlobalState__`/`__getLocalState__` làm **props** của `View`; ở 16 `View` không nhận props này nên dùng `useSubEnv` trong `SplitPane`.

## Khác biệt theo phiên bản (nơi dễ hỏng khi port)

| | 16 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|
| Kiểu list trong `action.views` | `tree` | `tree` | `list` | `list` | `list` |
| Header JS | `/** @odoo-module **/` | cần | không | không | không |
| Import action hook | `@web/webclient/actions/action_hook` | idem | `@web/search/action_hook` | idem | idem |
| `relatedModels` của View | `{model: fields}` | idem | `{model: {fields}}` | idem | idem |
| Tắt sửa tại chỗ | `editable: false` | idem | idem | `readonly: true` | `readonly: true` |
| Patch `ListRenderer` | `patch(proto, "name", {...})` + `_super` | `patch(proto, {...})` + `super` | idem | idem | idem, dùng `this.env.splitState` (reactive) |
| Recorder state cho view nhúng | env (`SplitPane`) | props | props | props | props |
| Layout / control panel | display `top-left`/`top-right`; save indicator nằm trong breadcrumb, nên pane form giữ 1 breadcrumb cố định "Details" | `layoutActions` | idem | idem | `buttons`/`actions`, slot `control-panel-buttons` |
| Template | `owl="1"`, `t-name` trần | idem | không | không | tiền tố `this.`, `t-on-click="() => this.x()"` |
| Component | Owl 2 | Owl 2 | Owl 2 | Owl 2 | **Owl 3**: `props = useProps({...t.*})`, `proxy`, `signal.ref()`, `useSubEnv` từ `@web/owl2/utils` |
| Icon nút Split | FontAwesome `fa fa-columns` (JS) | idem (JS) | `_get_view_info` | `_get_view_info` | `_get_view_info` + **Material Symbols `view_column`** (không còn FontAwesome) |
| Settings | khối `app_settings_block` kiểu cũ | `<app>/<block>/<setting>` | idem | idem | idem |
| Tham số cấu hình | `get_param/set_param` | idem | idem | idem | **`get_bool/set_bool`** (typed) |
| Security | `ir.model.access.csv` | idem | idem | idem | **`ir.access.csv`** (cột `model_id` là tên model, `operation` r/cru/crud) |
| `odoo.http` | module | module | module | module | package: `from odoo.http.stream import Stream` (không liên quan module này, nhưng dễ gặp khi port module khác) |
| URL test/ảnh | `/web#action=...&view_type=split` | idem | `/odoo/action-...?view_type=split` | idem | idem |

Bẫy chung đã gặp:
- **`View` chỉ nhận `__getGlobalState__`... qua props (17+)**: đặt chúng trong env của view nhúng sẽ không có tác dụng.
- Lists có `js_class` riêng (sales, kế toán...) bỏ qua `jsClass` truyền vào: vì vậy highlight dùng patch `ListRenderer` và tắt edit dùng prop, **không** dùng view đăng ký `split_list`.
- Ô của list có nền riêng: CSS highlight phải đặt lên `td`, đặt lên `tr` sẽ không thấy.
- Sắp xếp theo many2one của model `_table_query`/view cần comodel có bảng (không liên quan module này, liên quan lab).
- Tour: từ Odoo 20 hàm `run` không được rỗng (`() => {}` bị từ chối): dùng `() => { void 0; }`; từ 17 trở xuống không có `press Enter`/`edit` (dùng `text` và tự gửi `keydown`), không có `expectUnloadPage`.

## Test

```
odoo-bin -d <db> -i web_split_view --with-demo --test-tags /web_split_view --stop-after-init
```
(Odoo 12: thêm `web_tour` vào `-i`, vì không tự cài nên không có dịch vụ tour.)
(`--with-demo` bắt buộc ở 19/20; 16–18 tự nạp demo.) Cần Chrome: biến `ODOO_BROWSER_BIN` (bản 16/17 không đọc biến này, dùng `tools/odoo_wrap.py` để vá đường dẫn Chrome và cổng; cần `pip install websocket-client` trong venv). Chrome headless của Edge không chạy được tour (requestAnimationFrame không bắn): dùng Chrome for Testing headless-shell.
Tour `state` ở 16 không tải lại trang được (bộ chạy tour cũ) nên chỉ kiểm tra storage.

## Ảnh chụp và trang mô tả

- Cấu hình listing: `../listings/web_split_view.json`; sinh icon/banner/flow/`index.html` bằng skill `odoo-apps-listing` (version-neutral, không nhắc số version Odoo trong nội dung).
- Ảnh `static/description/screenshot_1..4.png` **chụp riêng cho từng version** bằng `tools/shoot_all.py <ver> <thư mục ra>` (cài Odoo + `sale_management` + module vào DB tạm, đăng nhập bằng JSON-RPC, điều khiển Chrome headless qua DevTools). Đường dẫn Chrome trong script là cứng, sửa nếu đổi máy.
- `tools/finish_split.sh <ver>` chép tài sản mô tả của bản 19 + ảnh của version đó, kiểm tra, commit, push (đang dùng như quy trình phát hành).
- Quy tắc store cần nhớ: ảnh bìa `images[0]` là `banner.png` (2:1), icon 128x128, không khuyến mãi/emoji/JS/link ngoài trong mô tả, giá >= 9 USD.

## Hạn chế đã biết

- Chưa test: điện thoại, nút mở popup/wizard trong form bên phải, bản ghi mới đang tạo dở khi tải lại trang (không được lưu).
- Chế độ tự động bật mặc định cho mọi list có form: nếu một action chạy lạ trong split, dùng `No split view` cho action đó.
- Bản 12: không có pager (xem mục legacy). Bản 12 và 13: ô tìm kiếm không mở gợi ý khi gõ bằng script nên ảnh chụp và tour dùng menu Filters thay cho gõ tìm kiếm.
- Bản 12 đến 14: không có wizard và menu debug tạo view split tay (chỉ có chế độ tự động và view `<split>` viết bằng XML); bản 15 giữ wizard và menu debug.

## Bản legacy 12 đến 15

Mã nằm ở `static/src/js/` (`split_view.js`, `split_listview.js`, `split_formview.js`), template `static/src/xml/split_view.xml`; khai báo bằng `odoo.define` (không phải OWL).

- **Cách hoạt động**: `SplitView` là một `BasicView` (kiểu `split`, `withSearchBar: true`): thanh tìm kiếm, bộ lọc, pager của control panel là **của view ngoài**, list và form bên trong là `ListView`/`FormView` legacy tạo bằng `getController(this)` (list không có control panel). Chế độ tự động: khi `<split/>` không có ref hay arch inline, `getController` lấy id view list/form từ `this.params.action.views` (kiểu list tên `tree`), rồi `loadViews`. Phần server giống 16 và 17: `_compute_views` chèn `(False, 'split')`, `_get_default_split_view`, cấu hình, `no_split_view`, khối Settings kiểu cũ `app_settings_block`.
- **Trạng thái**: khóa độ rộng `web_split_view_width_<action>_<model>_<view>` (localStorage), bản ghi mở `web_split_view_record_<...>` (sessionStorage). Quay lại từ form đầy đủ: action manager legacy giữ nguyên controller (hoặc dựng lại) và module mở lại bản ghi từ sessionStorage, ô tìm kiếm do control panel lưu.
- **Expand**: `trigger_up('switch_view', {view_type: 'form', res_id, mode: 'readonly'})`; nếu action không có form thì `do_action`. `canBeRemoved` được ghi đè để hỏi lưu/hủy form nhúng trước khi rời.
- **Highlight dòng**: `SplitListRenderer._renderRow` và `_highlightActiveRow`; **id dòng phải đọc bằng `$(tr).data('id')`** (Odoo 12 không có thuộc tính `data-id`): dùng `node.dataset.id` thì cả danh sách bị tô vì `classList.toggle(name, undefined)` đảo lớp.
- **Khác biệt**:

| | 12 | 13 | 14 | 15 |
|---|---|---|---|---|
| Control panel | legacy; sự kiện `search` | legacy; sự kiện `search` (`_onSearch` ghi đè, chuyển cho list rồi tô lại dòng đang mở) | Owl + `searchModel` (list đăng ký `search` của `searchModel`) | idem 14 |
| `getController` | phải trả **jQuery deferred** tự tạo bằng `$.Deferred()` (jQuery 1.x không nhận Promise native: `$.when(promise)` trả chính promise và gây `widget.on is not a function`) | async | async | async |
| `ListModel` | không có `web.ListModel`: dùng `web.BasicModel` | có | có | có |
| Pager | không có (model ngoài không giữ bản ghi nên `renderPager` bị vô hiệu; list nhúng chỉ hiện trang đầu) | pager ngoài chuyển cho list | idem 13 | idem 13 |
| Khóa theo action | `controller.actionInfo = {action, viewId}` đặt trong `getController` | idem 12 | `controlPanelProps` | `controlPanelProps` |
| Assets | template `views/assets.xml` vào `web.assets_backend` (cả tour: **không có `web.assets_tests`**) + `qweb` trong manifest | template + `web.assets_tests` | idem 13 | `assets` trong manifest (`web.assets_qweb`, `web.assets_tests`) |
| Python | không `ondelete` cho `selection_add`, không `get_views` (dùng `load_views`) | idem 12 (không `ondelete`) | có `ondelete` | idem 14 |
| Tour | `tour.register` kiểu cổ điển; chạy bằng `browser_js(...run(...))`; **cần cài `web_tour`** (không tự cài ở 12) | cổ điển; `start_tour` | cổ điển | ES module `import tour from "web_tour.tour"` |
| Khác | CSS ẩn thêm `.o_cp_right`/`.o_search_options` của form nhúng ở 13 | idem | | `fix_wysiwyg.js` (xem dưới) |

Bẫy riêng của legacy:
- **Bản 15, form có trường html** (sales order...): `Wysiwyg.start` có thể ném `Cannot read properties of undefined (reading '0')` khi form bị thay (mở expand ngay) trong lúc trình soạn thảo đang khởi động. `fix_wysiwyg.js` được nạp ở cả `website.assets_wysiwyg` lẫn `web_editor.assets_wysiwyg` và nuốt lỗi khi widget đã bị hủy.
- Ở 12 và 13, tour không gõ được tìm kiếm (jQuery UI autocomplete không mở bằng sự kiện script): test dùng menu Filters.
- Ô tìm kiếm của 13 đọc `originalEvent.inputType`: sự kiện giả của tour phải là `InputEvent` native.
- 15 giữ trường `'support '` (có dấu cách, chứa email của chủ dự án) trong manifest cũ: khóa sai nên store không đọc được; chưa sửa vì chủ dự án không cấp email support.

## Quy trình khi cần đổi hoặc thêm version

1. Sửa ở bản 19 trước (bản tham chiếu), test, rồi port theo bảng khác biệt ở trên; bản 18 gần giống 19 nhất (patch áp trực tiếp), 20 khác Owl 3, 16/17 khác patch API và tên view `tree`.
2. Chạy test ở từng version (xem trên), **chụp lại ảnh** (`tools/shoot_all.py`), xem ảnh bằng mắt: các lỗi hiển thị (icon thiếu, highlight, view switcher bị lặp) chỉ lộ ra khi xem ảnh, test tự động không bắt được.
3. Giữ `version` dạng `<odoo>.0.x.y.z`; thêm mục vào changelog trong `listings/web_split_view.json` rồi dựng lại `index.html` cho mọi version.
4. Chỉ commit thư mục `web_split_view` (mỗi nhánh một repo); push khi chủ dự án yêu cầu.
