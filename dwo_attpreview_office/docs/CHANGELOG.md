# CHANGELOG - dwo_attpreview_office

## 2026-11-18 - 19.0.1.1.1 - silurus 0.90.1 (#94)

**Library:** `@silurus/ooxml`, `@silurus/ooxml-legacy-office`, `@silurus/ooxml-opendocument` 0.90.0 -> **0.90.1** (compatible
patch release, no migration). Fixes for the customer: Word tables without rows (`w:tbl` without `w:tr`, common in
template-generated files) no longer fail with "Document page budget exceeded"; page/column breaks in header, footer,
footnote and endnote no longer give "Unsupported story block"; relative `wasmUrl` resolves against `document.baseURI`.
Patches `0002` (relative companion import) and `0003` (xlsx search highlight) re-applied by hand on the new hashed chunks
(`legacy-source-DmlTJjiH.js`, `odf-source-Cee46vyi.js`, `xlsx-CW8XwM_M.js`); patch files regenerated; the stock
`internal-companion.mjs` already says 0.90.1. `static/lib/silurus/` replaced whole (153 files + 6 licence/notice files,
about 25 MB). No code, field, view or migration change. `tests/test_engine.py` (`test_03`) uses the new chunk names.
Details: `docs/SILURUS_PATCHES.md`.

## 2026-11-16 - 19.0.1.1.0 - silurus 0.90.0, OpenDocument (ODT, ODS, ODP) (#84)

**Library:** `@silurus/ooxml`, `@silurus/ooxml-legacy-office` 0.89.11 -> **0.90.0**, new `@silurus/ooxml-opendocument`
0.90.0 (MIT, same author). The main library is the stock npm build again: the xlsx connector/arrow fix (our local patch
`0001`, upstream PR #2243) is merged upstream, so `0001` and its upstream-for-main copy are removed (checked: sheet
"Hiring Flow" of the sample workbook draws its connectors and arrowheads). Patch `0002` (relative import of the
companion runtime) now covers the legacy and the OpenDocument add-on; `0003` (xlsx search highlight, visible matches
only) ported by hand to the new chunk (local names renamed `dwo*`: the old `F` would shadow a minified helper). Licences
and notices of the three packages copied from 0.90.0. `useGoogleFonts` (deprecated in 0.90, warns even when false) is
no longer passed; no font source = no web font. Details: `docs/SILURUS_PATCHES.md`.

**Added:** OpenDocument `odt`, `ods`, `odp` and templates `ott`, `ots`, `otp`, drawn by the docx scroll, xlsx grid and
pptx slide viewers (with search), **without** the "limited support" banner (user decision).
- Server: a sane zip (same unpacked limits as Office files) whose `mimetype` part names the family of the extension
  (document or template; compressed or not first is accepted, like the reader); otherwise a toast ("the mimetype part is
  missing" / "another kind of OpenDocument file"). The viewer receives `odt`/`ods`/`odp`.
- Viewer: loads `odt.mjs`/`ods.mjs`/`odp.mjs` only for such a file and passes `createOdt()`/`createOds()`/`createOdp()`
  as the `odt`/`ods`/`odp` option. A file the reader refuses (encrypted, corrupt, over a limit) shows "This file cannot be
  previewed." and Download, like csv; the code stays in the console; the 90 s load timeout applies.
- Manifest: name `Secure Office Preview: DOCX, XLSX, PPTX, ODT, ODS, ODP, DOC, XLS, PPT, CSV`, summary/keywords and
  description updated; listing page: banner, LibreOffice card, file types, limits, FAQ, two screenshots (ods, odt).

**Tests:** `test_01` (extensions), `test_23` (six extensions accepted, templates both ways, re-zipped package, no
notice), `test_24` (wrong family, missing/oversized `mimetype`, damaged, empty, not a zip), `test_25` (zip bomb, too
many parts), `test_02e` (`/dwo_attpreview/info` without notice, file route), `test_03` (add-on files served, no bare
import), `test_03c` (options, no `useGoogleFonts`), tours `test_70..75` (odt/ods/odp/ott/ots/otp drawn, right layout,
no banner, fills the dialog), `test_76..78` (search in odt/ods/odp: counts, sheet and slide switch), `test_79`
(encrypted odt: short message + Download, no banner). Samples `tests/files/sample.od?` (odfpy, English fictional data);
not tried with files saved by LibreOffice itself.

## 2026-11-15 - Office files in binary fields of any record (#72)

**Fixed:** an Office file in a binary field that is not an `ir.attachment` record (e.g. a custom binary field on a partner, or a field stored in its table) showed the toast "can be previewed from the attachments, not yet from this field" instead of the preview.
- The viewer declares the `fileUrl` prop and loads `props.fileUrl` (given by the Core for a field: `/web/content` of the field, which checks the read access again) or, for an attachment, `/dwo_attpreview_office/file/<id>` as before. Only a path of the same server is accepted.
- No server change: the Core (`/dwo_attpreview/field_info`) chooses the engine by the file name of the field, applies the size limit and the zip/OLE checks before the dialog opens (a damaged or too large file still gives the toast). A field stored as an attachment is cached on its own attachment; a field stored in its table is checked in memory. No attachment is created.

**Tests:** `TestOfficeFieldPreview`: `test_60` (docx, xlsx, xlsm in a partner binary field: rendered by office, `file_url` returns the same bytes, no new attachment), `test_61` (field stored in its table: no attachment, no cache entry), `test_62` (damaged file and size limit give an error before the dialog; a user who cannot read the record gets `denied` and not the file), `test_63` (viewer declares `fileUrl`), tours `test_64` (docx, scroll layout) and `test_65` (xlsx, grid layout) from the Preview button of the field.

## 2026-11-15 - listing and name (#72)

- Manifest: name `Secure Office Preview: DOCX, DOC, XLSX, XLS, PPTX, PPT, CSV, TSV`, price 80 EUR, `images` = banner; Odoo Apps description page (`static/description/index.html`, icon, banner), screenshots taken again in English.

## 2026-11-15 - macro-enabled and template OOXML variants (#70)

**Added:** 11 extensions: `xlsm`, `xltx`, `xltm` (as xlsx), `docm`, `dotx`, `dotm` (as docx), `pptm`, `ppsx`, `ppsm`, `potx`, `potm` (as pptx).
- Server: a variant is checked like its base type (valid zip, main part `xl/workbook.xml` / `word/document.xml` / `ppt/presentation.xml`, unpacked size limits); error messages name the real extension (e.g. "not a valid XLTX file"); the viewer receives the base type (`xlsx`/`docx`/`pptx`), so the viewer and the component are unchanged. No warning banner.
- Macros are never run: the library does not read `vbaProject.bin`, and the sandboxed iframe runs no script of the file. `ppsx`/`ppsm` open as normal slides (not full screen).
- Checked: 11 files built from the module samples (main part content type changed; macro files get an empty OLE `vbaProject.bin` and a `vbaProject` relationship). All 11 open with the same content as the base file. No extension had to be left out. Not tried with files saved by Microsoft Office.
- Core: office catalog lists the 11 extensions and one sentence about them (sync `--check` passed). Manifest: one sentence added to `description` (name, summary and price unchanged: #72).

**Tests:** `test_01` (extensions), `test_22` (the 11 variants are accepted and return the base type; another type's main part, a damaged zip, an empty file, a web page are refused with the right extension; no banner), 11 tours `test_40..50` (each variant drawn, right layout, fills the dialog), `test_51` search in an xlsm.

## 2026-11-15 - search in the preview (#71)

**Added:** find text in the preview (docx, xlsx, pptx, csv, tsv and the old doc/xls/ppt, same viewers).
- Open: magnifier button on the viewer toolbar (xlsx/csv/tsv now have a toolbar too, holding only this button), Ctrl+F (Cmd+F) or `/` in the viewer; Ctrl+F pressed in the dialog (outside the iframe) is forwarded to the viewer, only when the viewer can search (outside the dialog the key keeps its usual meaning).
- Find bar: Enter = next match, Shift+Enter = previous, Esc/x = close and clear the highlight; counter "n / total" ("…" while searching, "0 / 0" in red); case-insensitive plain text (no regex), 250 ms debounce; a newer query or Esc drops the result of an older pending search.
- Uses silurus `findText/findNext/findPrev/clearFind`: whole document (also pages/slides/sheets not shown), every match highlighted, scrolls to the page (docx), goes to the slide (pptx), switches sheet + cell (xlsx). The index comes from the library `matchIndex`. A viewer without the search API hides the button and never opens the bar.
- `enableTextSelection` is not turned on: search and highlight work without it (checked on screenshots). A rough timing of long.docx with it on/off showed no clear difference, but the timing included the Odoo page and the injection of the option was not confirmed: not measured properly.
- xlsx: sheet row/cell ceilings raised like csv (200000 rows / 1500000 cells instead of the library default 100000 rows), for every xlsx: a 100000-row sheet plus a header row showed its first rows before but failed on search or when scrolled to the end.
- **Library patch 0003** (`patches/silurus/0003-xlsx-find-overlay-visible-matches-only.patch`, `docs/SILURUS_PATCHES.md`): the xlsx highlight boxes are only built for visible cells and appended at once. Before: 11112 matches in a 100000-row sheet took 70 s (+37 s for the next match), 100000 matches hung the page; after: 1.1 s and 1.0 s. Scrolling with 100000 highlighted matches was not measured (the overlay still walks every match on each redraw).
- The viewer reports to the component: `find` (can search), match count, index, location of the active match and the sheet/slide shown (`data-find*`, for tests); pptx also reports the slide number (`data-page`).

**Tests:** `test_03d` (find bar, API) and 10 tours `dwo_attpreview_office_tour_find_*`: xlsx (count 2, next/next/previous wrap, a word only on sheet "Notes" switches to that sheet), docx (counts 1 and 3, wrap), 15-page docx (132 matches, the previous of the first is on a later page), pptx (3 matches on slide 2, viewer goes to slide 2), csv, tsv, old xls/ppt/doc, 100000-row xlsx (100000 matches, last row, a word on row 100000); every tour also checks a missing word (0) and closing the bar.
**Screenshots:** `_scratch/attpreview_samples/search_v12/` (typed for real in the iframe: Ctrl+F, magnifier, Enter, Shift+Enter).
**Limits:** find bar labels are English only (static viewer page outside the Odoo translation system); no replace, no regex, no multi-file search; a library error during search (e.g. a resource limit) goes through `onError` and shows the viewer error message, like on opening.

## 2026-11-15 - 19.0.1.0.2 - thêm doc, xls, ppt (#69)

**Thêm:** preview định dạng cũ `.doc`, `.xls`, `.ppt` bằng add-on `@silurus/ooxml-legacy-office` 0.89.11 (MIT, đóng gói trong `static/lib/silurus`, wasm nạp lười khi mở file cũ).
- Server: file OLE/CFB (chữ ký `D0 CF 11 E0 A1 B1 1A E1`, tối thiểu 512 byte) thay cho kiểm tra zip với 3 đuôi cũ; từ chối file rỗng, không phải OLE (trang web/CSV đổi đuôi, docx đổi tên .doc), quá trần Core, kèm thông báo thân thiện (toast + Download). Server không parse file cũ. docx/xlsx/pptx giữ nguyên.
- Cảnh báo: engine khai báo `_dwo_engine_notice(ext)` (cơ chế chung của core #69); dialog hiện banner vàng "Legacy format (.doc/.xls/.ppt): support is limited. ...", đóng được, hiện cả khi file lỗi.
- Viewer: `legacyDoc` (DocxScrollViewer), `legacyXls` (XlsxViewer), `legacyPpt` (PptxViewer), `maxInputBytes` 128 MiB; mọi lỗi của add-on (`unsupported-content`, `legacy-binary-format`, `encrypted`, `ooxml-resource-limit`...) chỉ log console, người dùng thấy "This legacy file cannot be previewed." + nút Download; có timeout 90 s khi parser không trả lời.
- Bản vá `patches/silurus/0002-legacy-addon-relative-companion-import.patch` (import trần `@silurus/ooxml/internal/companion` thành `./internal-companion.mjs`, vì CSP không cho import map nội tuyến); `docs/SILURUS_PATCHES.md` ghi cách áp lại, phải nâng add-on cùng lúc với silurus. Kèm `LICENSE.ooxml-legacy-office`, `THIRD_PARTY_NOTICES.ooxml-legacy-office.md`.
- Manifest: version 19.0.1.0.2 (nhảy từ 19.0.1.0.0 để khớp core), summary/description nêu định dạng cũ hỗ trợ hạn chế. Không có migration (không đổi model/data).

**Thêm csv, tsv (bổ sung #69):** `XlsxSheetViewer.load(buffer, { format: 'delimited-text', delimiter, encoding: 'utf-8' })`, mọi ô giữ dạng chữ. Delimiter: tab cho tsv; csv tự dò `,` `;` tab ở dòng đầu (ngoài ngoặc kép), mặc định `,`; UTF-8 có/không BOM (BOM cắt ở viewer). Server: không rỗng, không có byte NUL (UTF-16/nhị phân bị từ chối), trần Core; không banner. Viewer đặt `xlsxWorksheetLimits` 200000 dòng / 1500000 ô (mặc định thư viện 100000/250000); vượt thì "This file cannot be previewed." + Download. Đo: file 100000 dòng (5 MB) mở trong khoảng 3 giây (tour). Core: catalog office thêm `csv`, `tsv`.
**Not done in this round:** OOXML variants (xlsm, docm, pptm, xltx...): done later in #70 (see above).

**Hạn chế (đã đo ở #68):** khoảng 70% .xls/.ppt và 40% .doc của bộ mẫu Apache POI mở được; .doc có hyperlink, ô gộp, chú thích cuối trang, ảnh nhúng thường bị từ chối cả tài liệu; hiển thị có thể lệch Office mà không báo; wasm là mã mới ("experimental").

**Test:** `tests/test_engine.py` (OLE hợp lệ/không hợp lệ/rỗng/quá trần, notice trong `/dwo_attpreview/info`, file add-on phục vụ đúng MIME, không import trần) và 5 tour mới (xls, ppt, doc mở được; doc bị từ chối: thông báo ngắn + Download + dialog nguyên vẹn; xls giả: toast). File mẫu thật nhỏ từ Apache POI (Apache-2.0) ở `tests/files`, kèm `NOTICE`.

## 2026-11-15 - #66

Theo core #66: engine không còn bản ghi cấu hình (`dwo.attpreview.engine.config`); route `/dwo_attpreview_office/file/<id>` và test dùng `dwo.attpreview.engine._dwo_find_engine`. Hành vi preview không đổi. Ảnh `static/description/screenshots/` được copy sang catalog của core (`_tools/sync_attpreview_catalog.py`).

## 2026-11-15 - bỏ nút chuyển trang docx (#65, theo yêu cầu người dùng)

**Bỏ:** nút ‹ › chuyển trang ở viewer docx (tài liệu cuộn liên tục; nhãn "Page n / total", zoom giữ nguyên). Pptx giữ nút slide trước/sau.

## 2026-11-15 - #65 (docx cuộn trang, viewer lấp đầy dialog)

- DOCX dùng `DocxScrollViewer` (cuộn dọc kiểu trình đọc PDF, ảo hóa trang, `progressiveLayout`): trang rộng khoảng 1000 px căn giữa, thanh nhỏ "Page n / tổng" + trang trước/sau + zoom. PPTX giữ `PptxViewer` từng slide (nút trước/sau, "Slide n / tổng"). XLSX không đổi.
- Không dùng `mode: "worker"` của silurus: Worker tạo từ URL thật bị từ chối trong origin rỗng của iframe sandbox ("cannot be accessed from origin null"); mặc định (parse trong Worker `data:`, vẽ ở main thread) chạy được.
- Iframe và wrapper cao 100% vùng nội dung của dialog Core (bỏ `75vh`). Viewer báo `layout` (`grid`/`scroll`/`slides`) và số trang cho component (`data-layout`, `data-page`, `data-total`) để test.
- File Core từ chối trước (zip hỏng, quá dung lượng) nay hiện toast (xem core #65), không còn khung lỗi trong dialog; lỗi chỉ trình duyệt thấy vẫn trong dialog.
- Test: `tests/files/long.docx` (15 trang), tour `docx_long` (layout scroll, nhiều trang), tour xlsx/docx/pptx kiểm layout + viewer lấp đầy dialog, tour file hỏng kiểm toast không có dialog, test_03b (viewer dùng đúng lớp viewer).

## 2026-11-15 - 19.0.1.0.0 (bản đầu, #62)

**Sửa thư viện (kỹ thuật):** `static/lib/silurus` là silurus 0.89.11 + patch cục bộ 0001 (vẽ connector/mũi tên `xdr:cxnSp` trong xlsx). Patch, cách áp lại khi nâng phiên bản và cách build: `docs/SILURUS_PATCHES.md`, `patches/silurus/`. Đánh dấu ở fork `tienhieuD/office-open-xml-viewer` (nhánh `v0.89.11-xlsx-connectors`, tag `v0.89.11-xlsx-connectors.1`); upstream issue #2240, PR #2243. Hạn chế cũ "mất connector/mũi tên" của xlsx không còn.

**Thêm:** engine `office` (xlsx, docx, pptx; đầu ra client-side) dùng `@silurus/ooxml` 0.89.11 (MIT, đóng gói trong `static/lib/silurus`, kèm LICENSE + THIRD_PARTY_NOTICES). Iframe `sandbox="allow-scripts"` (origin rỗng), CSP không mạng, `useGoogleFonts` tắt, file gửi cho iframe bằng postMessage.
- Controller `/dwo_attpreview_office/file/<id>`: kiểm quyền đọc attachment + engine office + kết quả Core (giới hạn dung lượng, zip hợp lệ).
- Controller `/dwo_attpreview_office/asset/...` (auth none, whitelist thư mục/đuôi): MIME đúng `application/wasm`, CORS `*`, CSP cho trang viewer. Lý do: static của Odoo trả MIME wasm đúng nhưng không có CORS, mà iframe sandbox cần CORS cho module script và wasm.
- Viewer ghi đè `URL.createObjectURL` để silurus dùng Worker `data:` (Chrome chặn Worker module từ `blob:` trong origin rỗng).
- Kiểm tra phía server: zip hợp lệ, có phần chính (`xl/workbook.xml`, `word/document.xml`, `ppt/presentation.xml`), không quá 128 MiB/phần, 256 MiB tổng, 20000 phần (cùng ngưỡng `resourceLimits` của silurus).
- Core: template dialog truyền thêm `attachmentId`, `downloadUrl` cho viewer client-side (thêm thuộc tính).

**Hạn chế chấp nhận (người dùng chốt):** mất connector/mũi tên; công thức hiện giá trị cache; file rất lớn dựa vào silurus + giới hạn Core; không cắt dòng, không vá thư viện.
**Thay thế:** `dwo_attpreview_word`, `dwo_attpreview_sheet`, `dwo_attpreview_slide`, `dwo_attpreview_office_suite` (gỡ khỏi bản phát hành, bản lưu ở `_scratch/attpreview_backup/removed`).
**Test:** `tests/test_engine.py` (unit + 4 tour). Giá 55 EUR.
**Chưa làm:** listing, icon/banner, bản dịch vi, xls/doc/ppt/csv/tsv/ods.
