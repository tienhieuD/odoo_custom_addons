# Dialog preview, toast và icon (dwo_attpreview_core)

## Service `dwo_attpreview`

`env.services.dwo_attpreview.open(attachmentId, { ids })` (`ids` is accepted but unused: there is no previous/next file navigation) (async, trả `true` nếu mở dialog).

1. Hỏi server `/dwo_attpreview/info`.
2. `mode` là `native` hoặc `rendered`: mở dialog (`AttPreviewDialog`).
3. Mọi trường hợp khác: **không mở dialog**, hiện toast (notification service) và dừng.
   - Tiêu đề toast = tên file; nội dung = lý do; nút **Download** tải file ngay.
   - Lý do: `unsupported` + `reason` = `no_engine` ("No preview is available for this file type": không có engine nào đã cài hỗ trợ đuôi này; engine bật khi module của nó đã cài, không còn công tắc riêng); `denied` (không có quyền đọc); `error` (Core từ chối trước khi mở: quá giới hạn dung lượng, zip hỏng/thiếu phần chính, engine server báo lỗi); lỗi RPC.
4. Lỗi chỉ trình duyệt mới biết (viewer phía client không vẽ được file, ví dụ iframe office báo lỗi thư viện) vẫn hiện **trong dialog** (khung cảnh báo + liên kết Download), vì dialog đã mở.

`ids` (tùy chọn): danh sách attachment để chuyển trước/sau (nút và phím mũi tên trái/phải, vòng tròn). Chatter truyền toàn bộ attachment của tin nhắn. Khi chuyển tới một file không preview được, dialog hiện thông báo ngay trong khung nội dung (không toast, vì đang ở trong dialog).

Mọi nơi tích hợp (hiện có: chatter qua patch `AttachmentList`) chỉ cần gọi `open`: toast cho file không hỗ trợ là hành vi của service, không lặp lại ở từng nơi.

## Dialog

- Cỡ: 95vw x 92vh, margin 4vh (CSS `static/src/scss/attachment_preview.scss`); màn hình nhỏ: Odoo tự cho full; nút "Full screen" chuyển qua lại 100vw x 100vh.
- Thanh trên cùng: icon loại file, tên file (cắt bằng dấu ...; tooltip là tên đầy đủ), `n / tổng` khi có nhiều file, các nút: trước, sau, tải về, mở tab mới (chỉ file native: PDF/ảnh/video/audio; file render bởi engine không có URL xem trực tiếp), toàn màn hình, đóng. Esc đóng.
- Màu theo biến Bootstrap của Odoo (`--bs-body-bg`, `--bs-secondary-bg`...), nên theo theme sáng/tối. Khung bên trong viewer office (iframe sandbox) vẫn nền sáng riêng.
- Native: PDF dùng iframe của trình duyệt (**không** còn `sandbox`: Chrome không hiện trình xem PDF trong iframe sandbox, trước đây khung PDF trống), ảnh `object-fit: contain`, video/audio có controls.
- Viewer client-side (`dwo_attpreview.viewers`): component nhận `content`, `attachmentId`, `downloadUrl`; nên chiếm hết chiều cao của `.o_dwo_ap_content` (flex), không đặt chiều cao cứng.

## Notice (banner cảnh báo của engine)

Engine khai báo cảnh báo cho từng đuôi file bằng `_dwo_engine_notice(self, extension)` (mixin `dwo.attpreview.engine`, đuôi chữ thường không dấu chấm; trả chuỗi đã dịch hoặc `False`, mặc định `False`). Ví dụ office: `.doc/.xls/.ppt` trả "Legacy format (.doc/.xls/.ppt): support is limited. The file may show incorrectly or fail to open. Download it to see it in full.".

- Server: `/dwo_attpreview/info` thêm `notice` (chuỗi hoặc `false`) vào kết quả mode `rendered` và `error`; chuỗi dịch theo ngôn ngữ của người dùng (module hiện chưa có file `i18n`, nên là tiếng Anh).
- Dialog: `<div class="alert alert-warning o_dwo_ap_notice">` ngay dưới `.o_dwo_ap_bar`, có icon `fa-exclamation-triangle`, văn bản, nút đóng (`.o_dwo_ap_notice_close`, trạng thái `noticeClosed`). Nằm ngoài viewer của engine nên vẫn hiện khi viewer báo lỗi (cùng nút Download của viewer). File Core từ chối trước (toast) không mở dialog nên không có banner.
- Viewer client-side không cần làm gì cho banner.

## Icon

Bộ SVG tự viết `static/img/dwo_attpreview_<kind>.svg` (giấy phép như module, LGPL-3; không dùng logo thương hiệu, chỉ hình tài liệu chung + chữ W/X/P): `pdf` (đỏ), `word` (xanh dương), `sheet` (xanh lá), `slide` (cam), `image`, `video`, `audio`, `archive`, `text`, `code`, `markdown`, `mail`, `cad`, `default`. Ánh xạ đuôi file -> kind ở `static/src/js/file_kind.js` (`dwoAttPreviewKind`), fallback theo mimetype. Lý do không dùng `web/static/img/mimetypes/`: Odoo không có icon cho email/markdown/code/cad và không phân màu Word/Excel/PowerPoint.

## Preview buttons on file fields (#75)

`static/src/js/field_preview.js`, `static/src/xml/field_preview.xml`, `static/src/scss/field_preview.scss`. Every button only calls the service; Odoo's own actions on these fields (download, edit, clear, delete, internal link) are unchanged.

| Widget | Where the button is | What it opens |
| --- | --- | --- |
| `binary` (form, edit mode) | eye button right **before** the Edit button (`aria-label="Edit"`), outlined in the action colour of the theme | `ir.attachment` `datas`/`raw`: `open(record id)` (same as the chatter); any other field: `openField(...)` |
| `binary` (read-only) | "Preview" button after the file name link | same |
| `many2many_binary` | eye next to the extension of each saved file | `open(attachment id)` |
| list of `ir.attachment` (one2many / many2many fields shown as a list, the Attachments menu) | an extra narrow column (view widget `dwo_attpreview_button`) added by a patch of `ListRenderer.processAllColumn` when the list model is `ir.attachment` | `open(row id)` |
| kanban of `ir.attachment` (the Attachments menu opens on it) | eye in the top right corner of each card, left of the card menu (patch of `KanbanRecord`) | `open(card id)` |
| `many2one` to `ir.attachment` | eye before the internal link (edit), after the name (read-only) | `open(value id)` |

The binary button shows only for a saved file (`record.resId` and the value is a size, i.e. loaded from the server); a file just uploaded and not saved has no preview until the record is saved. New list rows (no id) and URL attachments in a kanban have no button. Not done: `image`/`pdf_viewer` (they already show the file).

### `openField({ model, resId, field, filenameField })` and `/dwo_attpreview/field_info`

Same answer as `/info` plus `source: "field"`, `download_url` and `file_url` (both `/web/content?model=...&id=...&field=...&filename_field=...&download=true`, which checks the access again).

- **Access:** the model must exist and the field must be a `binary`; `record.check_access("read")` and `record._check_field_access(field, "read")`; the file name field (a `char`) must be readable too. Any failure, a bad model/field/id included, answers `{"mode": "denied"}` (no server error).
- **`ir.attachment.datas` / `raw`:** the record is the attachment: the answer of `/info` plus `attachment_id`.
- **Field stored as an attachment** (`attachment=True`, the default): its attachment (`res_model`, `res_id`, `res_field`) is rendered and cached as usual, but under the **real file name** (`_get_or_render(attachment, engine, filename)`): the attachment of a field is named after the field (`datas`, `x_file`), which would choose no engine.
- **Field stored in its table** (`attachment=False`): the base64 value is read after the access checks; the size is computed from its length before decoding and checked against the limit (`max_file_size_mb`, or the engine's own). The mimetype is guessed from the content (or from the file name). Native files are shown through `/web/content` of the field; other files are rendered **in memory** (`dwo.attpreview.cache._dwo_render_values`, same sanitizing as the cache) and **no attachment and no cache entry are created**: the result is computed again at each opening.
- **Viewers that load the file in the browser** (registry `dwo_attpreview.viewers`, e.g. office): the dialog gives them `fileUrl` for a field. A viewer that does not declare a `fileUrl` prop only knows how to fetch an attachment by id, so for a field the service shows the toast ("This file type can be previewed from the attachments, not yet from this field.") instead of a broken dialog. The office viewer declares it (office CHANGELOG, #72): docx/xlsx/pptx/csv... in a field open in the dialog.
- The toast and the dialog use `info.download_url` when given (the field's own download), else `/web/content/<attachment id>`.

## Files inside a file: email attachments (#78)

An engine can open files that live inside the file it previews (today: the attachments of an email, with the
`dwo_attpreview_mail` engine). Nothing is extracted to the database.

- **Engine side:** return `{"type": "json", ...}` and register a viewer in `dwo_attpreview.viewers` that declares
  the props `source` (and `fileUrl`, so that it also works for a file that is itself inside another file);
  implement `_dwo_extract_part(content, filename, index)` (index = position in the list your result gives).
- **Viewer side:** `this.env.services.dwo_attpreview.openPart(baseSource, path)` where `baseSource` is the
  `source` prop without its `path` and `path` = `source.path ? source.path + "/" + index : index`;
  `partUrl(baseSource, path)` for a download link.
- **Server:** `/dwo_attpreview/part_info {source, path}` answers like `/info` (`mode`, `type`, `content`,
  `download_url`, `file_url`, `source_ref` with the path); `/dwo_attpreview/part?attachment_id=..|model=..&res_id=..&field=..[&filename_field=..]&path=..&download=true|false`
  sends the bytes. Both check the access to the outer file again on every call; at most 20 levels, index < 10000.
- **Dialog:** the inner file opens in a second dialog above the first, with the width of its own kind of file
  (see below); Esc closes the top one only. An inner Office file gets `fileUrl` (the `/part` URL), so the office viewer loads it.

## Dialog width by kind of file (#78)

The server tells the dialog how wide to be (`info.width`), the dialog adds `o_dwo_ap_w_<width>`:

| width | size | for |
| --- | --- | --- |
| `wide` (default) | 95% of the window | sheets, documents, slides, PDF, pictures, video |
| `medium` | min(1080px, 95vw) | emails, invitations, contact cards (engine `mail`) |
| `narrow` | min(640px, 95vw), 320px high | sound files |

An engine sets `_dwo_engine_dialog_width`; native files get `narrow` for audio and `wide` otherwise. Full screen
mode ignores the width.

## Shared tree view (#83)

`DwoTreeView` (`@dwo_attpreview_core/js/tree_view`, template `dwo_attpreview_core.TreeView`): a virtualized tree
(Headless Tree + TanStack Virtual, `static/lib/tree_libs`, global `DwoTreeLibs`, in the backend assets) used by the
archive engine (folder tree) and the text engine (JSON / XML / YAML trees, Markdown outline, files of a diff).

- Props: `rootId`, `getChildren(id)`, `isFolder(id)`, `row(id)` -> `{name, icon, badge, badgeClass, count, muted,
  title, nameClass, <column keys>}`, `onOpen(id)` (Enter / click on a leaf), `version` (bump after changing what
  `getChildren` returns), `expanded`, `label`, `nameLabel`, `columns` (`[{key, label, width, align, classKey}]`),
  `onReady(api)` (`expandAll`, `collapseAll`, `expandItems(ids)`), `onFocus(id)`, `onDownload(id)`, `folderIcon(expanded)`.
- Rules (bugs found on #82): never call `tree.rebuildTree()` while rendering (it is done in `onWillUpdateProps`);
  change the state with `tree.applySubStateUpdate(...)`; keep big data outside reactive state (the parent gives
  functions). Only the visible rows are in the page: 100 000 rows stay smooth.
