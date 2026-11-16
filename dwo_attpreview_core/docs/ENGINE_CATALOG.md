# Danh mục engine (catalog) và ô tick trong Settings

## Settings

Settings của core (mục **Attachment Preview**) chỉ có: **Max file size (MB)** (mặc định 20) và danh sách **Preview engines**.

- Mỗi engine là một ô tick `module_<tên module>` (`module_dwo_attpreview_office`, `module_dwo_attpreview_mail`) trong `res.config.settings`, dùng cơ chế sẵn của Odoo: tick + Save thì cài module, bỏ tick thì Odoo hỏi gỡ.
- Widget `dwo_attpreview_engine_boolean` (`static/src/js/engine_boolean.js`) vẽ tên, đuôi file và trạng thái. Dữ liệu lấy từ trường tính toán `dwo_attpreview_engines` (Json, ẩn) của `res.config.settings`.

| Trạng thái | Nghĩa (bảng `ir.module.module`) | Khi tick |
| --- | --- | --- |
| Installed | `installed`, `to install`, `to upgrade`, `to remove` | đã tick; bỏ tick thì Odoo hỏi gỡ |
| Available | có trong addons, chưa cài (`uninstalled`) | tick bình thường, Save thì cài |
| Not installed | không có trong addons (không có dòng, hoặc `uninstallable`) | mở popup; tick không được giữ |

Hàm `res.config.settings._dwo_attpreview_module_state(module)` quyết định trạng thái.

## Popup (module chưa có trong addons)

Nội dung: tên engine, đuôi file, giá, mô tả HTML + ảnh của catalog, ghi chú trung tính ("after you get the module, copy it to your addons folder, update the apps list, then tick again here"; Odoo Online không cài được app bên thứ ba) và nút **Open on Odoo Apps** (thẻ `<a>`, `target="_blank"`, `rel="noopener noreferrer"`) tới `https://apps.odoo.com/apps/modules/<module>`.

- Mô tả nằm trong iframe `sandbox=""` (không script), `srcdoc` có `<base>` trỏ `static/catalog/<module>/` và chính sách CSP `default-src 'none'; img-src <origin>/dwo_attpreview_core/static/catalog/ data:` nên ảnh/tài nguyên remote bị chặn. HTML còn được làm sạch (bỏ script, iframe, form, handler `on*`, `href`, `src` tuyệt đối).
- Quy định Odoo Apps: link tới apps.odoo.com **chỉ** nằm trong popup (JS/XML và `data/engine_catalog.json` của core). KHÔNG đưa vào `static/description/index.html` hay manifest của module nào. Văn bản popup trung tính (không "giảm giá", "mua ngay", khuyến mãi).
- Không tự tải/cài module từ mạng; chỉ cài module đã có trong addons.

## Catalog

`data/engine_catalog.json`: mỗi engine một mục `module`, `name`, `extensions`, `store_url`. Giá KHÔNG hiển thị trong popup (quyết định 2026-11-15). Mô tả và ảnh: `static/catalog/<module>/index.html` + ảnh (đường dẫn tương đối).

Thêm engine mới vào Settings: (1) thêm mục vào `engine_catalog.json`, (2) thêm trường `module_<tên>` Boolean vào `res.config.settings` và một dòng `<field ... widget="dwo_attpreview_engine_boolean"/>` trong view, (3) thư mục `static/catalog/<tên>/` (chạy script sync). Test `test_settings` kiểm mỗi mục catalog có trường `module_`.

## Quy trình đồng bộ (rule)

**Engine đổi `static/description/index.html` hay ảnh thì chạy script sync:**

```
python3 odoo_appstore/_tools/sync_attpreview_catalog.py          # copy vào core
python3 odoo_appstore/_tools/sync_attpreview_catalog.py --check  # chỉ báo, exit 1 nếu lệch
```

- Copy `index.html` (nếu có) và mọi ảnh trong `static/description/` (cùng đường dẫn tương đối), trừ `icon.png`, `banner.png` và file > 600 KB. Quy tắc nằm ở `catalog_sync.py` (dùng chung cho script và test).
- Engine chưa có `index.html` (hiện chỉ còn mail): catalog giữ mô tả ngắn tự viết (tiếng Anh) trong `static/catalog/<module>/index.html`; script chỉ đồng bộ ảnh. Khi engine có `index.html`, bản của engine ghi đè: office có trang Odoo Apps riêng từ #72 (index.html, flow.png, screenshots), popup hiện chính trang đó (không có script tab nên các tab hiện nối tiếp; link bị bỏ).
- Test `tests/test_catalog.py::test_03` so hash (sha256) từng file của engine với bản catalog, và **fail** khi lệch (cần nhắc chạy script). Engine không có trong addons path của máy chạy test thì bỏ qua.
- Mô tả/ảnh trong catalog không được có script, địa chỉ http(s), `<iframe>` (test_02).
