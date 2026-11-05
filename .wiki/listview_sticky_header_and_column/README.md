# listview_sticky_header_and_column

Ghim (đóng băng) cột bên trái của list, header luôn hiện khi cuộn. Có cho **Odoo 12 đến 20**, mỗi version một nhánh (`<version>.0`) của repo.
Hiện tại `version` = `<odoo>.0.0.4.0`; giá theo từng nhánh (EUR): 12: 16.44, 13: 18.44, 14 và 15: 21.44, 16: 26, 17: 30, 18: 34, 19 và 20: 38. License `LGPL-3`.
Tên hiển thị "List View Sticky Header & Freeze Column" dài 39 ký tự (store giới hạn 25): trình kiểm tra báo FAIL này, **chủ dự án đã chọn giữ tên gốc**. Thiếu email `support` (chủ dự án không cấp). Trường `website` của manifest vẫn trỏ tới một file gif trên Flickr (chưa đổi).
`images` = `banner.png` (bìa) + `theme_screenshot.png` (ảnh cũ, đã lỗi thời).

## Hành vi

- Rê chuột vào tiêu đề cột: hiện nút ghim (`span.display-on-hover.js_pin_this_column`). Bấm: ghim cột đó **và mọi cột bên trái** (cột checkbox cũng tính). Bấm lại: bỏ ghim.
- Header chỉ dính đầu trang **khi có cột đang ghim** (không phải lúc nào cũng dính).
- Mỗi list nhớ cột đã ghim trong `localStorage` của trình duyệt: khóa `listview_sticky_header_and_column__viewId_<viewId>` (16 đến 20), thêm hậu tố `__field_<tên field>` cho list x2many trong form; bản 12 đến 15 dùng `..._model_<model>` (+ field), vì renderer cũ không có viewId.
- Mỗi list nhúng trong form ghim độc lập; cột ghim giữ nguyên độ rộng, kéo resize vẫn chạy, vị trí cột ghim cập nhật theo.

## Cách làm (16 đến 20): `static/src/js/main.js`

Patch `ListRenderer`: mỗi renderer có `lshcUid`; khi ghim, chèn `<style name="listview_sticky_header_and_column" data-owner="<uid>">` có phạm vi `.o_content .table-responsive[data-lshc-id="<uid>"]`.
- `left` của cột i = **tổng `getBoundingClientRect().width` của các cột ghim trước nó**. **Không dùng `offsetLeft`** (khi đã sticky nó là vị trí đã bị cuộn).
- `ResizeObserver` tính lại khi đổi độ rộng cột. Chờ ~300ms sau khi ghim để layout ổn.
- `overflow: visible` trên `.table-responsive` chỉ cho list chính (cuộn bằng `.o_content`); list nhúng form giữ overflow của nó.
- Màu lấy từ theme (`--ListRenderer-thead-bg-color`, biến bảng Bootstrap); viền chỉ ở cột ghim cuối bằng `box-shadow` inset (border thật không hoạt động vì `border-collapse: collapse`).
- Các thứ **đã thử và bỏ**, đừng thử lại mù quáng (chi tiết ở `changelog/<v>.0.0.2.md` và `0.3.md` trong module): ép `table-layout: auto`, `white-space: nowrap` (làm cột rộng ra, hỏng resize), màu cứng, đổ bóng phía phải cột ghim cuối.
- Bản 12 đến 15 là **viết lại riêng** (jQuery): `ListRenderer.include` với `_renderHeaderCell` (thêm nút), `_renderView` (ghim lại sau mỗi lần dựng bảng), `destroy`; màu nền ô ghim đọc từ DOM; `position: sticky !important` (bắt buộc: dòng đang sửa bị Odoo đặt lại `position: relative`).

## Khác biệt theo version

| Vấn đề | Chi tiết |
|---|---|
| Chọn th để thêm nút | 16 đến 19: `th[data-tooltip-delay="1000"]`; 20 và 12 đến 15: `th[data-name]` (20 không còn thuộc tính tooltip) |
| Phần tử gốc của renderer | 16 đến 19: `this.rootRef.el`; 20 (Owl 3): `this.rootRef()` |
| Template `static/src/xml/style.xml` | chỉ 16 đến 19 (xpath trên `th[@data-tooltip-delay]`); **đã xóa ở 20 vì xpath không khớp sẽ làm hỏng cả web client**; 12 đến 15 cũng đã bỏ |
| Icon nút | FontAwesome `fa-thumb-tack`; **20: `<i class="oi oi-fw" data-icon="push_pin">`** (không còn FontAwesome) |
| Nền header | 20: biến `--ListRenderer-thead-bg-color` là gradient trong suốt hoặc màu thường tùy list: dùng `background: var(...)` rồi `background-color: var(--body-bg)` riêng (hai lớp trong một khai báo bị vô hiệu khi biến là màu) |
| Ô ghim trong suốt | **16** (Bootstrap 5.1, ô không có nền): thêm `background-color` mờ đục lấy từ DOM (`lshcOpaqueBackground`) |
| Hiện nút ghim khi hover | scss phải có cả `.o_list_view thead > tr > th` và `.o_list_renderer thead > tr > th` (list nhúng form không có `.o_list_view`) |
| Patch API | 16: `patch(proto, "name", {...})` + `this._super`; 17+: `patch(proto, {...})` + `super` |
| 12 đến 15 | 12: khung `.o_list_view` là chính `<table>`, tên cột chỉ lưu bằng jQuery `.data('name')` (không có thuộc tính `data-name`); 15: đã xóa dòng asset `account/static/src/scss/variables.scss` (làm trang lỗi 500 khi chưa cài account); 12: tour test nạp vào `web.assets_backend` (không có `web.assets_tests`) |
| `view_mode` list | `tree` (16, 17) vs `list` (18+) chỉ ảnh hưởng module lab |

## Module test: `.lab/listview_sticky_test_lab` (trong mỗi repo)

Một app gốc **List Sticky Test Lab** (không cần debug) với dữ liệu giả, để thử ghim/cuộn:
- Menu: Showcase (đơn hàng, dùng làm ảnh mô tả), Wide list (52 cột, ~30 loại widget, search panel), Editable list (40 cột), Grouped list. Form: list đủ kiểu (full width, trong tab notebook, nửa form, editable, 7 đến 38 cột).
- **Không có bảng và không có dòng lưu**: model `_auto = False` với `_table_query` (14 đến 19) hoặc `_table_sql` (20), sinh dữ liệu bằng SQL `generate_series` + `hashtext` (ổn định theo id); 12 đến 14 dùng **SQL view** tạo trong `init()` (12 và 13 chưa có `_table_query`, 14 không join được comodel `_table_query`). Chỉ đọc: ghi bị bỏ qua, tạo mới báo lỗi. SQL không được chứa dấu `%` (dùng `mod()`), vì có đường truy vấn không truyền tham số.
- Mã sinh: `.lab/listview_sticky_test_lab/tools/` (`build_lab.py <version> <thư mục addons>` sinh module cho đúng version từ một bộ spec; `gen_lab.py`, `models_part.py`, `lab_tours_*`). Widget không có ở version đó tự bị bỏ.
- Cần thêm `.../odoo_custom_addonsNN/.lab` vào `addons_path` của conf (đã làm cho conf 12 đến 20 và workspace VS Code).
- Khác biệt khi test: 12 không có search panel (bỏ), 13 không có `enable_counters`, ảnh nhị phân: ≤ 17 lưu base64 dạng text, 18+ lưu bytes; tour 20 cấm hàm `run` rỗng; mọi tour kiểm tra bằng `console.error("LABFAIL ...")` (làm test fail).
- 3 tour: `lshc_lab_wide_list` (ghim, cuộn ngang/dọc, cột ghim đúng vị trí và không trong suốt, header dính, bỏ ghim, search panel reload vẫn giữ ghim), `lshc_lab_editable_list` (vào chế độ sửa dòng, ô ghim vẫn thẳng hàng), `lshc_lab_form_lists` (ghim ở một list không lan sang list khác, header ghim mờ đục).

Chạy test: `tools/lab_test.sh <NN> odoo-<NN>.0.<ngày>` (xem script; 16 và 17 cần `WRAP=tools/odoo_wrap.py`; 19 và 20 thêm `EXTRA=--with-demo`; cần `websocket-client` trong venv và Chrome headless-shell, biến `ODOO_BROWSER_BIN`). `tools/sticky_test.sh` là bản cũ tạo tour tạm cho module gốc.

## Ảnh và trang mô tả

- Cấu hình: `../listings/listview_sticky_header_and_column.json` (skill `odoo-apps-listing`); mô tả version-neutral; changelog 0.1 đến 0.4 nằm trong `index.html` và `changelog/*.md`.
- Icon 128x128 và banner 2:1 sinh bằng skill (bản cũ giữ dạng `icon_old.png`, `banner_old.png`).
- `screenshot_1.png` (list ngoài, đã ghim Customer và cuộn) và `screenshot_2.png` (list dòng đơn hàng trong form, ghim Product) chụp **riêng cho từng version** từ menu Showcase của module lab: `tools/shoot_showcase.py <NN> <thư mục ra>` (viewport 1100x860; Chrome headless qua DevTools; đường dẫn Chrome cứng trong script).

## Quy trình khi sửa

1. Sửa code ở version bị lỗi; luôn **chạy lab test cả 9 version** vì lỗi hay chỉ lộ ở một version (16: ô trong suốt; 20: icon, header; 12 đến 15: dòng đang sửa).
2. **Chụp lại ảnh và xem bằng mắt**: icon thiếu, header trong suốt, chữ chồng lên nhau chỉ thấy trên ảnh.
3. Nâng `version`, thêm `changelog/<version>.md` và mục mới trong `listings/...json`, dựng lại `index.html` rồi chép sang mọi version.
4. Commit chỉ thư mục `listview_sticky_header_and_column` (và `lab`) trên từng nhánh; không commit `.DS_Store`.
