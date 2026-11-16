# CHANGELOG - dwo_attpreview_core

## 2026-11-15 - Name and Odoo Apps listing (#72)

- Manifest: name `Secure Attachment Preview` (was "Attachment Preview Core"), new summary/description (large dialog, file fields, nothing sent outside), `images` = `static/description/banner.png`. Technical name unchanged.
- Engine name of the office engine in `data/engine_catalog.json` and the label of `module_dwo_attpreview_office` in `res.config.settings`: `Secure Office Preview: DOCX, DOC, XLSX, XLS, PPTX, PPT, CSV, TSV`.
- Odoo Apps description page `static/description/index.html`, `icon.png`, `banner.png`, `flow.png` (skill odoo-apps-listing, config `odoo_appstore/_listings/dwo_attpreview_core.json`). All screenshots taken again in English (`docs/SCREENSHOTS.md`).
- Catalog: the office `index.html`, `flow.png` and screenshots mirrored with `sync_attpreview_catalog.py`; the Settings popup shows the new page (checked: readable without the tab script, every picture loads, no price).
- `docs/DIALOG.md`: the office viewer now takes `fileUrl` (Office files in binary fields open in the dialog). No model or data change: version stays 19.0.1.0.2.

## 2026-11-15 - Preview buttons on file fields (#75)

**Added:** a Preview button on the file fields of forms and lists, opening the same dialog as the chatter (toast with Download when the file cannot be previewed). Odoo's own download, edit, clear and delete actions are unchanged. Details: `docs/DIALOG.md` ("Preview buttons on file fields").
- `binary`: eye button right before the Edit button (outlined in the theme's action colour), "Preview" after the file name in read-only mode; only for a saved file. Works for `ir.attachment` (`datas`, e.g. the Attachments menu) and for binary fields of any model.
- `many2many_binary`: eye next to each saved file.
- Lists of `ir.attachment` (one2many/many2many fields shown as a list, the Attachments menu): an extra narrow column with an eye button (view widget `dwo_attpreview_button`, added automatically).
- Kanban of `ir.attachment` (the Attachments menu opens on it): eye in the top right corner of each card.
- `many2one` to `ir.attachment`: eye next to the field.
- Route `/dwo_attpreview/field_info` and service method `openField({model, resId, field, filenameField})`: checks read access on the record, the field and the file name field; a field stored as an attachment is rendered and cached under its real file name (`_get_or_render(attachment, engine, filename)`); a field stored in its table (`attachment=False`) is size-checked before decoding and rendered in memory, creating no attachment and no cache entry.
- Dialog: `attachmentId` is optional; `info.download_url` (the field's own `/web/content` URL) is used for Download when given; engine viewers receive `fileUrl` for a field. A viewer that does not declare `fileUrl` (office for now) is not used for a field: toast instead.

**Tests:** `tests/test_field_preview.py` (access to record/field/file name field, bad requests answer `denied`, size limit, no attachment created, real file name), `tests/test_field_tour.py` + `static/tests/tours/field_tour.js` (binary on the attachment form incl. no file chooser opened and Clear still working; editable and read-only binary/many2one, many2many_binary and a list on a partner; kanban and list of the Attachments menu; a binary field stored in its table). Screenshots 09-14 (`docs/SCREENSHOTS.md`, script `docs/tools/field_shots.py`). No model or data change: version stays 19.0.1.0.2.

## 2026-11-15 - office catalog: search (#71), OOXML variants (#70)

- `static/catalog/dwo_attpreview_office/index.html`: new paragraph "Search in the preview" (#71) and one about macro-enabled/template variants (#70, macros never run).
- `data/engine_catalog.json`: office engine lists `xlsm`, `xltx`, `xltm`, `docm`, `dotx`, `dotm`, `pptm`, `ppsx`, `ppsm`, `potx`, `potm` (#70); `test_settings` checks a few of them.
- Ran `_tools/sync_attpreview_catalog.py --check`. No model/code change: version stays 19.0.1.0.2 (the catalog JSON is read at run time).

## 2026-11-15 - 19.0.1.0.2 - banner cảnh báo (notice) của engine (#69)

**Thêm:** engine có thể khai báo một cảnh báo ngắn, dịch được, theo đuôi file: hook `_dwo_engine_notice(extension)` của mixin `dwo.attpreview.engine` (mặc định `False`; dùng `self.env._()` để chuỗi theo ngôn ngữ người dùng). `/dwo_attpreview/info` trả thêm trường `notice` (chuỗi hoặc `false`) ở mode `rendered` và `error`. Dialog hiện banner vàng nhỏ (icon cảnh báo, nút đóng) dưới thanh tiêu đề; banner nằm ngoài viewer nên vẫn hiện khi viewer báo lỗi. Chi tiết: `docs/DIALOG.md`.
- Catalog: engine office thêm đuôi `doc`, `xls`, `ppt`, `csv`, `tsv` (`data/engine_catalog.json`), mô tả `static/catalog/dwo_attpreview_office/index.html` nêu hỗ trợ hạn chế định dạng cũ.
- Engine mẫu của test (`tests/sample_engine.py`) có notice cho `.sample`; test `test_10`, `test_10b`, tour chính kiểm banner hiện và đóng được; `test_settings` cập nhật danh sách đuôi của office.
- Version 19.0.1.0.2; không đổi model/data nên không cần migration.

## 2026-11-15 - bỏ giá khỏi popup engine (#66, theo yêu cầu người dùng)

**Bỏ:** dòng giá trong popup giới thiệu engine, trường `price`/`currency` trong `engine_catalog.json`, hàm `catalog.entry_price` và thông tin giá trong Settings. Popup chỉ còn tên, đuôi file, mô tả, ảnh và nút mở trang Odoo Apps (giá xem trên trang store).

## 2026-11-15 - 19.0.1.0.1 - Settings tối giản, engine là ô tick cài module (#66)

**Bỏ:** mọi mục Settings trừ "Max file size (MB)" (render timeout, cache lifetime/max size, thống kê, nút Clear cache, "Manage engines"); model `dwo.attpreview.engine.config` cùng view, action, ACL; kiểm timeout hậu kỳ; engine `sample` khỏi module sản phẩm (nay là lớp Python thường ở `tests/sample_engine.py`, chỉ nạp khi chạy test). `controllers`: bỏ lý do `engine_disabled`.

**Đổi:**
- Engine bật = module đã cài. Tra cứu bằng mixin: `dwo.attpreview.engine._dwo_get_engines()` / `_dwo_find_engine(filename)` (trả engine hoặc `None`, nên kiểm `is None`: recordset rỗng là falsy). `priority`, `max_size_mb` là thuộc tính lớp `_dwo_engine_*`; bỏ `_dwo_engine_default_enabled`. `dwo.attpreview.cache._get_or_render(attachment, engine)` nhận đối tượng engine này.
- Cron dọn cache chạy ngầm với hằng số `CACHE_TTL_DAYS = 30`, `CACHE_MAX_MB = 500` (ghi đè ẩn bằng `ir.config_parameter` `dwo_attpreview.cache_ttl_days` / `cache_max_mb`); nay cũng xóa kết quả của engine đã gỡ.
- Migration `19.0.1.0.1`: xóa bảng mồ côi `dwo_attpreview_engine_config` (Odoo không tự xóa khi cập nhật). Nâng cấp `-u` trên DB cài bản cũ đã thử, không lỗi.

**Thêm:**
- Settings: ô tick cho mỗi engine theo cơ chế `module_<tên module>` của Odoo (tick + Save thì cài, bỏ tick thì Odoo hỏi gỡ), widget OWL `dwo_attpreview_engine_boolean` hiện tên, đuôi file, trạng thái (Installed / Available / Not installed). Module chưa có trong addons: tick mở popup (tên, đuôi file, giá, mô tả + ảnh từ catalog, ghi chú, nút "Open on Odoo Apps" mở tab mới), tick không được giữ.
- Catalog engine `data/engine_catalog.json` + `static/catalog/<module>/`; script `_tools/sync_attpreview_catalog.py`; test báo lệch. Chi tiết: `docs/ENGINE_CATALOG.md`.

**Test:** `test_settings.py`, `test_catalog.py`, `test_engine_tour.py` (tour popup và tick thường); `test_core.py` và tour cũ chuyển sang engine mẫu giả; office/mail cập nhật theo API mới.

## 2026-11-15 - bỏ nút chuyển file (#65, theo yêu cầu người dùng)

**Bỏ:** nút Trước/Sau và bộ đếm "n / m" trên thanh tiêu đề dialog, phím mũi tên trái/phải chuyển file. Dialog chỉ còn: icon + tên file, tải về, mở tab mới (file native), toàn màn hình, đóng. Tùy chọn `ids` của `service.open()` vẫn được nhận nhưng không dùng. Tour `preview_tour.js` kiểm không còn các nút này.

## 2026-11-14 - 19.0.1.0.0 (bản đầu, #58)

**Thêm mới**
- Registry engine: mixin `dwo.attpreview.engine` (AbstractModel); engine khai báo `_dwo_engine_*` + `_dwo_render()`. Core tự quét registry và đồng bộ vào `dwo.attpreview.engine.config` (bật/tắt, priority, giới hạn MB). Engine mẫu `sample` (txt, mặc định tắt).
- Cache `dwo.attpreview.cache` (lazy, Binary attachment=True, khóa attachment+engine, vô hiệu khi đổi checksum/phiên bản engine, lỗi cache 10 phút). ACL: chỉ group_system; user thường đọc qua controller. Cron hằng ngày dọn theo TTL và dung lượng tối đa. Tắt/gỡ engine thì xóa cache của engine.
- Controller `/dwo_attpreview/info` (jsonrpc): kiểm `check_access('read')` trên attachment gốc; trả `native` (PDF/ảnh/video/audio), `rendered`, `unsupported`, `error`, `denied`. HTML do engine tạo qua `html_sanitize`; viewer hiển thị trong iframe `sandbox=""`.
- Settings: giới hạn kích thước, timeout, TTL, dung lượng cache, thống kê, nút xóa cache, menu quản lý engine.
- Owl: service `dwo_attpreview.open(attachmentId)` + dialog.

**Test:** 10 test Python xanh (registry, ưu tiên, cache, vô hiệu, ACL, cron, cascade, controller).

**Giới hạn / chưa làm**
- Timeout render chỉ kiểm sau khi render xong (không ngắt giữa chừng).
- Chưa gắn vào chatter/binary field/many2many_binary/mail composer/list; chưa có slider nhiều file, zoom/fullscreen; chưa có tour JS (dialog chưa được test trên trình duyệt).
- Chưa có listing (`_listings`), icon/banner, duotek, bản dịch vi.
- Quyết định (#58): Core LGPL-3, engine OPL-1, giá EUR.

## 2026-11-14 (tiếp) - tích hợp chatter

- Patch `AttachmentList.onClickAttachment` (mail): file Odoo không xem native được (không phải ảnh/PDF/text/video) mở dialog preview của core.
- Tour `dwo_attpreview_core_tour` + `tests/test_tour.py` (chatter -> dialog hiện nội dung engine sample -> đóng). Tổng 11 test xanh.
- Engine `sample` nhận thêm đuôi `sample` (để test không bị Odoo coi là text).
- Vẫn chưa làm: binary field, many2many_binary, danh sách/kanban attachment, mail composer, slider, zoom/fullscreen.

## 2026-11-15 - hỗ trợ engine

- `tools.py`: helper chung cho engine (`safe_xml` chống XXE, `open_zip`/`read_zip_member` chống zip bomb, `esc`, `table_html`).
- Dialog Owl: engine render ở client đăng ký component vào registry `dwo_attpreview.viewers` (key = mã engine); dùng bởi `markdown`.
- Khi cài lẫn engine lẻ và gói bundle: gói chặn bằng `pre_init_hook` (Odoo 19 không có `excludes`); cài gói trước rồi engine lẻ thì không bị chặn (model trùng tên, vô hại).

## 2026-11-15 - #62 (engine office)

- Dialog: viewer client-side nhận thêm prop `attachmentId` và `downloadUrl` (thêm thuộc tính trong `attachment_preview.xml`, viewer cũ như markdown bỏ qua nhờ `"*": true`). Dùng bởi `dwo_attpreview_office` để tự lấy file gốc.
- Sửa lỗi: file 0 byte (attachment không có checksum) làm `INSERT` cache vi phạm NOT NULL và `/dwo_attpreview/info` lỗi 500. Nay checksum rỗng được lưu là chuỗi rỗng. Test: `dwo_attpreview_office` (`test_03`, mục empty.pptx).

## 2026-11-15 - #65 (giao diện dialog, icon, toast)

- Dialog mới: 95vw x 92vh (full trên màn hình nhỏ), thanh công cụ gọn (icon loại file + tên, trước/sau khi có nhiều file, tải về, mở tab mới cho file native, toàn màn hình, đóng), nội dung chiếm hết chiều cao, màu theo biến Bootstrap. Bỏ footer Download/Close cũ. Chi tiết: `docs/DIALOG.md`.
- Chuyển file trước/sau (nút + phím mũi tên): **mới**, trước đây chưa có; chatter truyền danh sách attachment của tin nhắn.
- Bộ icon SVG tự viết `static/img/dwo_attpreview_*.svg` (14 loại) + `file_kind.js`.
- File không preview được (không engine, engine tắt, không quyền, Core từ chối: quá dung lượng/zip hỏng): **không mở dialog**, toast tên file + lý do + nút Download. Service `open()` hỏi server trước (nay trả `Promise<boolean>`). Lỗi chỉ client biết vẫn hiện trong dialog.
- Controller `/dwo_attpreview/info`: thêm `reason` (`no_engine` | `engine_disabled`) cho `mode=unsupported`.
- Sửa lỗi: PDF native trong dialog trống vì iframe có `sandbox` (Chrome không hiện trình xem PDF trong iframe sandbox); bỏ `sandbox` cho iframe PDF (nội dung do Odoo phục vụ `application/pdf` + `nosniff` + CSP `default-src 'none'`).
- Test: `test_core.py` thêm test_11 (reason), test_12 (quá dung lượng báo trước), test_13 (bộ icon); tour: dialog lớn + icon + toolbar + toàn màn hình, toast file không hỗ trợ (không có `.modal`), chuyển trước/sau.
- Hạn chế: nút "Mở tab mới" ẩn với file do engine render; nền trong iframe office luôn sáng (chưa theo theme tối); chatter là nơi tích hợp duy nhất (binary field/list/widget chưa gắn).
