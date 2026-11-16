# Porting notes - Secure Attachment Preview (core, office, mail)

The 19.0 branch is the source of truth. Each section lists every change made for another Odoo version, file by
file, so a later change on 19.0 can be synced quickly. In the code, each of these places carries a comment
`# Odoo 20: ...` (Python) or `// Odoo 20: ...` / `<!-- Odoo 20: ... -->` (JavaScript, XML).

## 19.0 -> 20.0

Port of core 19.0.1.1.0, office 19.0.1.0.2 and mail 19.0.2.0.0 (issue #73). Versions: core 20.0.1.1.0,
office 20.0.1.0.2, mail 20.0.2.0.0. The `migrations/19.0.*` folder of the core is not copied: a 20.0 database
never ran the 19.0 code. Behaviour is the same as on 19.0. Full test suite: 148 test methods, all green.

### What changed in Odoo 20 (and why it matters here)

| Odoo 20 change | Effect on these modules |
|---|---|
| `odoo.http` is a package; `Stream` is in `odoo.http.stream` | import `Stream` from there (`request` stays in `odoo.http`) |
| `ir.model.access` is replaced by `ir.access` (`security/ir.access.csv`: `model_id` is the model name, `operation` is a subset of `crud`) | access file rewritten |
| `ir.config_parameter.get_param` / `set_param` are gone; typed `get_int`, `get_str`, `set_int`... | settings read with `get_int` |
| Binary fields read as a `BinaryValue` (raw bytes, lazy), no longer base64 `bytes`; writing `bytes` raises `TypeError` (base64 must be a `str`, or a `BinaryValue`) | engines get `bytes(...)`; the cache stores base64 as `str` and the controller re-encodes |
| `ir.attachment.datas` is gone; the file is `raw` (the form view shows `raw`) | test and tour use `raw`; the controller still accepts both names |
| `res.company.layout_background_image` is gone | tests use `ir.ui.menu.web_icon_data` (stored as an attachment, readable by internal users, char `name`) |
| `_check_field_access` is deprecated; the environment memoizes the fields it may read | `check_field_access`; the access test clears the memo after patching `groups` |
| Owl 3: templates read the component through `this.`; no `static props` (throws), props come from `useProps()`; `useState` -> `proxy`; `useRef` -> `signal.ref()` read as `ref()` | every template and component of the three modules |
| Font Awesome is gone; icons are `<i class="oi" data-icon="<material symbol>"/>` | every icon |
| `t-esc` is deprecated (warning) | `t-out` (same escaping) |
| Binary field widget: no Edit button any more, the file name input opens the file chooser; a saved file reads `{size, checksum[, filename]}` (`isBinarySize` is gone), a file just uploaded `{filename, content}` | eye button placed right after the file name; "saved" test changed |
| `many2many_binary` is drawn by `Many2XBinary` (template `web.Many2XBinary.attachment_preview`), also used by `many2one_binary` | template and patch moved; eye only when `multiUpload` (many2many_binary, as in 19) |
| `AttachmentList` (mail) gets `attachmentGroups` instead of `attachments`, and a selection mode | patch reads `attachmentGroups`, leaves selection clicks to Odoo |
| Odoo's own file viewer now also opens csv, markdown, xml and audio | these still open the Attachment Preview dialog as in 19; when no engine can preview one, Odoo's viewer opens it instead of the toast |
| `o_form_dirty` is set on `.o_form_renderer`, inside `.o_form_view`; Discard of the settings reloads the form after the click (dirty for a moment) | settings tours wait after Discard until no `.o_form_dirty` for one second, then check `body:not(:has(.o_form_dirty))` |

### dwo_attpreview_core

- `__manifest__.py`: version `20.0.1.1.0`; data `security/ir.access.csv` (was `security/ir.model.access.csv`).
- `security/ir.access.csv` (new name): `access_cache_system,dwo.attpreview.cache system,dwo.attpreview.cache,base.group_system,rd,` (same rights as 19: read + unlink for administrators).
- `models/cache.py`:
  - `_param`: `get_int("dwo_attpreview." + key, int(default))` instead of `int(get_param(...))`.
  - `_render`: `content = bytes(attachment.raw or b"")`.
  - `_get_or_render`: the base64 `bytes` of `_dwo_render_values` is decoded to `str` before `create` (the field stores raw bytes). `_dwo_render_values` is unchanged (still base64 bytes, used in memory for fields stored in a table).
  - Docstring: `ir.access.csv`.
- `controllers/main.py`:
  - `from odoo.http.stream import Stream`; `/dwo_attpreview/part` builds `Stream(...)` (was `http.Stream`).
  - `_dwo_cache_values`: `data` is `rec.data.to_base64().encode()` (the cache field reads as raw bytes).
  - `field_info` (field stored in its table): `size = value.size`, `raw = bytes(value)`; render with `bytes(value)` (was `len(value) * 3 // 4` and `b64decode`).
  - `_dwo_field_access`: `check_field_access` (was `_check_field_access`).
  - `_dwo_source_file`: `bytes(att.raw or b"")` in both lambdas; field stored in its table: `value.size`, `bytes(value)`.
- `static/src/js/field_preview.js`:
  - `isBinarySize` import removed; `BinaryField.dwoCanPreview`: saved file = value is an object without `content`.
  - `Many2ManyBinaryField` patch -> `Many2XBinary` patch (`@web/views/fields/many2x_binary/many2x_binary`); `dwoCanPreviewFile` also checks `this.props.multiUpload`.
  - `AttPreviewListButton`: `props = useProps()` instead of `static props`.
- `static/src/js/attachment_list_patch.js`: `attachmentGroups`; `isSelecting` left to Odoo; `dwoOdoo19Viewable()` (Odoo-viewable as in 19: not csv, markdown, xml, audio); for those files `open(..., {onUnavailable})` falls back to Odoo's viewer.
- `static/src/js/attachment_preview.js`:
  - `AttPreviewDialog`: `props = useProps()`, `proxy` instead of `useState`.
  - Viewer contract: `dwoViewerProps(viewer)` reads `static dwoAttPreviewProps` (array of prop names) instead of `viewer.props`; used for `source` (viewerProps) and `fileUrl` (viewerTakesFileUrl).
  - Service `open(attachmentId, {ids, onUnavailable})`: `onUnavailable` is called instead of the toast (except `denied`).
- `static/src/js/engine_boolean.js`: `EngineStoreDialog`: `props = useProps()`, `proxy` instead of `useState`.
- `static/src/xml/attachment_preview.xml`, `engine_boolean.xml`: `this.` everywhere, `t-out`, icons `download`, `open_in_new`, `fullscreen` / `fullscreen_exit`, `close`, `warning`.
- `static/src/xml/field_preview.xml`:
  - Binary (edit): eye appended to the `toggler` slot (right after the file name), class `btn btn-link lh-1 oi o_dwo_ap_field_preview`, `data-icon="visibility"`. Read-only: unchanged place (after `a.o_form_uri`).
  - many2many_binary: inherits `web.Many2XBinary.attachment_preview` (template renamed `dwo_attpreview_core.Many2XBinary.attachment_preview`).
  - Many2One: xpaths on `this.hasLinkButton`, `this.props.readonly`, `this.props.value`; the read-only block copies the Odoo 20 markup (`t-out`).
  - Kanban, list button: `this.` and `oi` icons.
- `static/src/scss/field_preview.scss`: `.o_dwo_ap_field_preview.oi` (was `.fa`).
- Tests:
  - `tests/test_core.py`: `bytes(rec.data)` (was `b64decode(rec.data)`); `set_int`.
  - `tests/test_field_preview.py`: `ir.ui.menu` / `web_icon_data` instead of `res.company` / `layout_background_image` (the attribute is still called `company`); `field="raw"` in `test_01`; base64 written as `str`; `_field_access_memo` cleared before the `groups` patches in `test_06`; `set_int`.
  - `tests/test_part_preview.py`: same field replacement in `test_07`; `set_int`.
  - `tests/test_field_tour.py`, `tests/test_settings.py`: base64 as `str`; `get_str` / `set_int`.
  - `docs/DIALOG.md`: the `fileUrl` viewer prop is declared in `static dwoAttPreviewProps`.
  - `static/tests/tours/field_tour.js`: `[name=raw]`; "eye right after the file name" (`input.o_select_file_button + button.o_dwo_ap_field_preview`) instead of "before the Edit button".
  - `static/tests/tours/preview_tour.js`: banner icon `.oi[data-icon=warning]`; Discard step waits for the reload to settle; clean form check `body:not(:has(.o_form_dirty)) .o_form_view`.

### dwo_attpreview_office

- `__manifest__.py`: version `20.0.1.0.2`.
- `controllers/office.py`: `from odoo.http.stream import Stream`; `/dwo_attpreview_office/file/<id>` sends `bytes(sudo.raw or b"")`.
- `static/src/js/office_viewer.js`: `static dwoAttPreviewProps = ["content", "attachmentId", "downloadUrl", "fileUrl"]` + `props = useProps()` instead of `static props`; `signal.ref()` read as `this.frame()` instead of `useRef("frame")` / `.el`; `proxy` instead of `useState`.
- `static/src/xml/office_viewer.xml`: `this.` everywhere, `t-ref="this.frame"`, `t-out`.
- `tests/test_engine.py`: `bytes(rec.data)`; base64 written as `str`; `set_int`; `test_63` checks `dwoAttPreviewProps` (was the static `fileUrl` prop).

### dwo_attpreview_mail

- `__manifest__.py`: version `20.0.2.0.0`.
- `static/src/js/mail_viewer.js`: `static dwoAttPreviewProps = ["content", "attachmentId", "downloadUrl", "fileUrl", "source"]` + `props = useProps()`.
- `static/src/xml/mail_viewer.xml`: `this.` for every member of the component, `t-out`, icons `security`, `download`, `calendar_today`, `account_circle`.
- `static/src/scss/mail_viewer.scss`: `.o_dwo_mail_card_top > .oi` (was `.fa`).
- `tests/test_engine.py`: `bytes(rec.data)`.

### #79 - remote pictures through the server (mail 19.0.2.1.0 -> 20.0.2.1.0)

- `dwo_attpreview_mail/__manifest__.py`: version `20.0.2.1.0`.
- `controllers/main.py`: `from odoo.http.stream import Stream` (was `http.Stream`); `_dwo_mail_settings` reads the two
  parameters with `get_bool` (was `bool(get_param(...))`). The `noupdate` data file still stores `True`, which
  `get_bool` reads as on; Boolean `config_parameter` fields of `res.config.settings` use `get_bool` / `set_bool` in
  Odoo 20 (unticking stores `False` instead of deleting the parameter).
- `static/src/js/mail_viewer.js`: `this.remote = proxy(...)` (was `useState`).
- `static/src/xml/mail_viewer.xml`: banners read `this.remote...`, `t-out` for the failed count, icon `oi` `security`.
- `tests/test_remote.py`: `get_bool` / `set_bool` (was `get_param` / `set_param`).
- `parsers/remote.py`, `models/engine.py`, `models/res_config_settings.py`, the data and view files, the tour and
  `dwo_attpreview_core/tests/test_settings.py`: same as 19.0.

### 19.0 -> 20.0 (#82) - archive engine (archive 19.0.1.0.0 -> 20.0.1.0.0, core 19.0.1.2.0 -> 20.0.1.2.0)

**dwo_attpreview_core 20.0.1.2.0:** same changes as 19.0.1.2.0, no Odoo 20 specific code: `module_dwo_attpreview_archive`
tick (model + view), catalog entry and `static/catalog/dwo_attpreview_archive/`, `MAX_PART_INDEX = 1_000_000`, icons
`dwo_attpreview_{folder,folder_open,lock,link}.svg` and `dwoAttPreviewSpecialIconUrl` + more extensions in
`file_kind.js`, tests (`test_core.py` test_13, `test_part_preview.py` bad path `"9999999"`, `test_settings.py`).

**dwo_attpreview_archive 20.0.1.0.0:**
- `__manifest__.py`: version `20.0.1.0.0`. `.gitignore`: `!dwo_attpreview_archive/static/lib/` (the generic `lib/`
  rule would drop the vendored tree libraries).
- Unchanged: `parsers/__init__.py`, `thirdparty/rarfile`, `models/engine.py` (the Core already passes `bytes`; the size
  limit is read through `cache._param`, which uses `get_int`), `static/lib/tree_libs/tree_libs.min.js`
  (framework-agnostic bundle, copied as is), the tour.
- `static/src/js/archive_viewer.js`: `static dwoAttPreviewProps = ["content", "attachmentId", "downloadUrl", "fileUrl",
  "source"]` + `props = useProps()` instead of `static props`; `this.ui = proxy(...)` instead of `useState`;
  `this.root = signal.ref()` (was `useRef("tree")`). The listing (up to 100 000 rows) stays in plain fields.
- `static/src/js/tree_view.js` (`DwoTreeView`): `props = useProps()`; `this.ticks = proxy({n: 0})` (the single
  counter that re-renders); `this.scroll` / `this.list` are `signal.ref()` read as `this.scroll()` / `this.list()`.
  Kept from 19: `tree.rebuildTree()` only in `onMounted` / `onWillUpdateProps` (when `version` changes) and in
  `expandItems`, never while rendering (a rebuild notifies a change: endless render loop); state changes through
  `tree.applySubStateUpdate("expandedItems", ...)` (`setState` only notifies).
- `static/src/xml/archive_viewer.xml`: `this.` for every member, `t-ref="this.scroll"` / `this.list` / `this.root`,
  `t-out`, handlers as arrow functions, `.bind="this.method"` props; icons `oi` `arrow_drop_down` / `arrow_right`
  (folder chevron, was `fa-caret-down/right`), `search`, `download`.
- `static/src/scss/archive_viewer.scss`: `.o_dwo_arc_search > .oi` (was `.fa`).
- `tests/test_archive.py`: `set_int` (was `set_param`); attachments created with `raw` (bytes) as on 19.

### Syncing a change from 19.0

- Python: binary values are `BinaryValue` (use `bytes(v)`, `v.size`), never base64; write base64 as `str`.
- Settings: typed getters/setters of `ir.config_parameter`.
- Templates: prefix every member of the component with `this.`, use `t-out`, `oi` icons; no `static props` (use `useProps()`), `proxy` / `signal.ref()`.
- A new viewer prop the Core must detect goes into `static dwoAttPreviewProps`.

## #84 - silurus 0.90.0 + ODT/ODS/ODP (office 20.0.1.1.0; core version unchanged)

Copied as is from 19.0 (`421592b`, `adb7794`): `static/lib/silurus` (silurus 0.90.0 dist + legacy and OpenDocument
add-ons, patches 0002/0003 applied), `static/viewer/*`, `patches/silurus/`, `docs/SILURUS_PATCHES.md`, the test samples
`tests/files/sample.od?`, the listing (`static/description/*`, banner, screenshots 20-21) and, in the Core, the catalog
entry, the Settings label, `file_kind.js` (ott/ots/otp icons) and the catalog copy of the office page. The office
controller needed no change (the asset route serves the new `.mjs` / `.wasm` files by extension).

Differences from 19.0:

- `static/src/xml/office_viewer.xml`: the hunk adapted to the Owl 3 template (`t-elif="this.isText or
  this.isOpenDocument"`).
- `tests/test_engine.py` test_23: `bytes(rec.data).decode()` (binary fields read as raw bytes) instead of
  `base64.b64decode(rec.data)`.
- Tour `find_ods`: one extra step waits for `data-find-where*='Notes'` after the second search. Both searches of that
  tour have one match, so without it the check could read the result of the first search (it failed once on 20.0;
  19.0 has the same race, it passed there by timing).
