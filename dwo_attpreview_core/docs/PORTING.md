# Porting notes - Attachment Preview (#73)

Applies to the three modules: `dwo_attpreview_core` (LGPL-3), `dwo_attpreview_office` (OPL-1), `dwo_attpreview_mail` (OPL-1).
Every place where the 18.0 code differs from 19.0 carries a comment `# Odoo 18: ...` / `// Odoo 18: ...` / `<!-- Odoo 18: ... -->`
(`grep -rn "Odoo 18" dwo_attpreview_*` lists them). The 17.0 port should start from this 18.0 code.

## 19.0 -> 18.0

### Source

- 19.0 branch of `odoo_custom_addons19` at commit `10cb032` (2026-11-16): core 19.0.1.1.0, office 19.0.1.0.2, mail 19.0.2.0.0.
  Versions keep the x.y.z part: core 18.0.1.1.0, office 18.0.1.0.2, mail 18.0.2.0.0.
- Copied with `git archive` (tracked files only), without `__pycache__` and without `dwo_attpreview_core/migrations/19.0.1.0.1/`
  (it only drops an orphan table of an old 19.0 build; an 18.0 database never had it).
- **`dwo_attpreview_office/static/lib/silurus/` is not in git** (the repository `.gitignore` has `lib/`; 19.0 `10cb032` does not
  contain it either). It was copied from the 19.0 working tree (74 files, about 20 MB, `@silurus/ooxml` 0.89.11 with the local
  patches of `docs/SILURUS_PATCHES.md`). Without it the office viewer cannot load (asset route 404, every office tour fails).
  A checkout of the branch alone does not give a working office engine: the library must be added (or force-added to git).
- Tests: 149 tests (the 148 of 19.0 plus `test_08b`), all green on Odoo 18.0 (`odoo-18.0.20260412`, Chrome headless shell).

### dwo_attpreview_core

| File | 19.0 | 18.0 |
|---|---|---|
| `__manifest__.py` | `19.0.1.1.0` | `18.0.1.1.0` |
| `controllers/main.py` | routes `/dwo_attpreview/info`, `/field_info`, `/part_info` with `type="jsonrpc"` | `type="json"` (same JSON-RPC protocol; the client `rpc()` is unchanged) |
| `controllers/main.py` `_dwo_field_access` | `record._check_field_access(field, "read")` | `record.check_field_access_rights("read", [field.name])` (raises `AccessError` the same way) |
| `controllers/main.py` `_dwo_field_access` | `record._has_field_access(ffield, "read")` | `ffield.is_accessible(env)` (same rule: superuser, or no `groups`, or the user is in them) |
| `models/cache.py` | `_att_engine_uniq = models.Constraint(...)` | `_sql_constraints = [("att_engine_uniq", "unique(attachment_id, engine_code)", ...)]` |
| `models/res_config_settings.py` | the first `onchange()` of the Settings form runs the compute of `dwo_attpreview_engines` (Json, no `depends`) | 18 fills every field without a default with `False` and does not run that compute: the engine widget had no data (technical names, "Not installed"). Added `default_get` that returns `dwo_attpreview_engines` |
| `static/src/js/attachment_list_patch.js` | patches `AttachmentList.onClickAttachment(attachment)` | 18 has no `onClickAttachment`: the template calls `this.fileViewer.open(attachment, props.attachments)` directly, and that `open` ignores non-viewable files. `setup()` wraps `this.fileViewer` so a non-viewable file goes to the `dwo_attpreview` service |
| `static/src/js/field_preview.js` | patches `Many2One` (`@web/views/fields/many2one/many2one`), value `props.value = {id, display_name}`, `props.relation` | 18 has only `Many2OneField` (`@web/views/fields/many2one/many2one_field`): value `[id, display_name]`, getters `relation`, `resId`, `urlRelation`, `displayName`, `classFromDecoration`, handler `onClick` |
| `static/src/xml/field_preview.xml` | extends `web.Many2One`: button before `//t[@t-if='hasLinkButton']`; read-only `//t[@t-if='props.readonly']/t[@t-if='props.value']` hidden when previewable | extends `web.Many2OneField`: button before `//t[@t-if='hasExternalButton']`; read-only: `t[@t-if='!props.canOpen']` and `t[@t-else='']/a` get `and !(value and dwoCanPreview)`, and the same `o_dwo_ap_m2o_readonly` block (link `/odoo/<urlRelation>/<id>` + eye) is added inside `props.readonly`. Same DOM classes as 19 |
| `static/src/xml/field_preview.xml` (binary, many2many_binary, kanban card, list column) | - | unchanged: `web.BinaryField` (`button.o_select_file_button`, `a.o_form_uri`), `web.Many2ManyBinaryField.attachment_preview` (`div.caption.small/a`), `web.KanbanRecord` (`article/t[@t-call='{{ this.constructor.menuTemplate }}']`) and `ListRenderer.processAllColumn` exist in 18 |
| `static/tests/tours/preview_tour.js` | chatter card `.o-mail-AttachmentContainer` | `.o-mail-AttachmentCard` (files; images are `.o-mail-AttachmentImage`) |
| `static/tests/tours/preview_tour.js` | "Form is clean": `.o_form_view:not(.o_form_dirty)` | `.o_form_renderer:not(.o_form_dirty)` (in 18 the class is on the renderer, so the 19 step was always true at once and the tour ended with a dirty form: "Tour finished with an open form view in edition mode") |
| `tests/test_core.py` | `group_ids` | `groups_id` |
| `tests/test_settings.py` | `test_09`: unticking an installed engine, `execute()` returns the `base.module.uninstall` wizard | 18 warns in `onchange_module` and `execute()` calls `button_immediate_uninstall()` (mocked in the test). New `test_08b_form_gets_engine_infos` (regression test of the `default_get` above) |
| `docs/CHANGELOG.md` | - | entry "18.0 port of 19.0.1.1.0" |
| `docs/tools/listing_shots.mjs`, `docs/tools/field_shots.py` | 19 selectors (`.o-mail-AttachmentContainer`) | not changed: screenshot tools for the listing, run against a 19.0 database |

### dwo_attpreview_office

| File | 19.0 | 18.0 |
|---|---|---|
| `__manifest__.py` | `19.0.1.0.2` | `18.0.1.0.2` |
| `README.md` | "Odoo 19" | "Odoo 18" |
| `static/tests/tours/office_tour.js` | `.o-mail-AttachmentContainer` | `.o-mail-AttachmentCard` |
| `tests/test_engine.py` | `group_ids` | `groups_id` (two places) |
| `tests/test_engine.py` | - | mixin `_AssetRouteWithoutTestCookie` (`check_test_cursor` override) on both tour classes, `TestOfficeRoutes` and `TestOfficeFieldPreview` (see below) |
| `docs/tools/*.mjs` | 19 selectors | not changed (listing screenshot tools) |

**Test cookie (tests only, product unchanged).** After `start_tour`, `HttpCase.check_test_cursor` of Odoo 18 refuses (400) every request
without the `test_request_key` cookie ("cookie is mandatory after a browser_js call"). The office viewer runs in a sandboxed iframe
(opaque origin), so the browser sends no cookie with its requests to the public route `/dwo_attpreview_office/asset/...`:
viewer.js / viewer.css / the library get 400 and every office tour waits forever for `data-state=ready`. The override lets exactly
the prefix `/dwo_attpreview_office/asset/` through (public route, `auth="none"`, no session needed); everything else keeps the strict
check. Odoo 19 does not refuse these requests.
Operational note (18 and 19 alike): iframe requests carry no session cookie, so the server must pick the database by itself (one
database, `dbfilter` or `-d`).

### dwo_attpreview_mail

| File | 19.0 | 18.0 |
|---|---|---|
| `__manifest__.py` | `19.0.2.0.0` | `18.0.2.0.0` |
| `static/tests/tours/mail_tour.js` | `.o-mail-AttachmentContainer` | `.o-mail-AttachmentCard` |

No other change: the parsers, `models/engine.py` and the OWL viewer run as is (luxon is global in 18, the hoot `:last` selector of
the tour exists in 18).

### Checked on 18 and unchanged

- `self.env._(...)` (exists since 18), `record.check_access("read")`, `http.Stream(type="data", ..., as_attachment=..., etag=False)`,
  `Stream.from_path(path, public=True)`, `file_open`, `file_path`, `fields.Json`, `ir.cron` without `numbercall`, `make_jsonrpc_request`.
- JS: `rpc` from `@web/core/network/rpc`, `Dialog` props (`header`, `footer`, `withBodyPadding`, `fullscreen`, `contentClass`, `size`),
  `@dwo_attpreview_core/js/...` imports between modules, `registry.category("web_tour.tours")` with `steps: () => [...]`, `run: "click"`,
  hoot selectors `:contains`, `:last`, URLs `/odoo/res.partner/<id>` and `/odoo/action-<xmlid>`, Settings `<app>/<block>/<setting>`,
  Bootstrap 5.3 CSS variables, Font Awesome 4.
- Demo data: loaded by default on 18 (19 needs `--with-demo`).

### For the 17.0 port (start from this 18.0 code)

- `self.env._(...)` does not exist on 17: use `_()` (many places in `controllers/main.py`: `field_info`, `part_info`,
  `_dwo_source_file`, `_dwo_resolve_part`; also models and the office/mail engines).
- `check_access("read")` -> `check_access_rights("read")` + `check_access_rule("read")` (core and office controllers).
- `check_field_access_rights` and `Field.is_accessible` exist on 17 (check the signatures).
- JS: `rpc` comes from `useService("rpc")` / `@web/core/network/rpc_service`; tour URLs `/web#id=..&model=..` instead of `/odoo/...`;
  steps that only check need `run: () => {}`; check the `:last` / `:contains` selectors against the 17 tour runner (jQuery);
  check `AttachmentList`, `Many2OneField`, `KanbanRecord` templates and the `Dialog` props on 17.
- Odoo 17 ignores `ODOO_BROWSER_BIN` (the test script patches the browser) and needs `browser_size = "1366,768"`.
- Copy `dwo_attpreview_office/static/lib/silurus/` by hand (not in git, see above).

## 18.0 -> 17.0

### Source

- 18.0 branch of `odoo_custom_addons18` at commit `878790b` (2026-11-16): core 18.0.1.1.0, office 18.0.1.0.2, mail 18.0.2.0.0,
  copied with `git archive` (the office library `static/lib/silurus` is tracked on 18, 74 files).
  Versions keep the x.y.z part: core 17.0.1.1.0, office 17.0.1.0.2, mail 17.0.2.0.0.
- The repository `.gitignore` ignores `lib/`: `!dwo_attpreview_office/static/lib/` was added right after it (as on 18/19/20).
- Tests: the same 149 tests, all green on Odoo 17.0 (`odoo-17.0.20240624`, Chrome headless shell, `browser_size = "1366,768"`).
- Every place where the 17.0 code differs from 18.0 carries a comment `# Odoo 17: ...` / `// Odoo 17: ...` / `<!-- Odoo 17: ... -->`.

### dwo_attpreview_core

| File | 18.0 | 17.0 |
|---|---|---|
| `__manifest__.py` | `18.0.1.1.0` | `17.0.1.1.0` |
| `controllers/main.py` | `env._(...)` / `request.env._(...)` | `_(...)` from `odoo` (`env._` exists from 18) |
| `controllers/main.py` `_get_attachment`, `_dwo_field_access` | `check_access("read")` | `check_access_rights("read")` + `check_access_rule("read")` |
| `controllers/main.py` `_dwo_field_access` | `ffield.is_accessible(env)` | `env.su or not ffield.groups or Model.user_has_groups(ffield.groups)` (same rule; `Field.is_accessible` does not exist on 17). `check_field_access_rights` is unchanged |
| `models/cache.py` | `self.env._(...)` | `_(...)` |
| `models/engine.py` | docstring "use `self.env._()`" | "use `_()`" |
| `data/ir_cron.xml` | - | `numbercall = -1`: on 17 a cron runs `numbercall` times (default 1) then stops; 18/19 have no such field and always repeat |
| `static/src/js/attachment_preview.js` | `rpc` imported from `@web/core/network/rpc` | `useService("rpc")` in the dialog; the service depends on `rpc` |
| `static/src/js/attachment_preview.js` (toast) | `autocloseDelay: 10000` | 17 has no `autocloseDelay` (fixed 4 s, and the prop would fail validation): `sticky: true` and the toast is closed after 10 s with `browser.setTimeout` |
| `static/src/xml/field_preview.xml` (many2one) | read-only link `/odoo/${urlRelation}/${id}` | `#id=${id}&model=${relation}`, as in the 17 `web.Many2OneField` (no `urlRelation`) |
| `static/src/xml/field_preview.xml` (many2many_binary) | extends `web.Many2ManyBinaryField.attachment_preview` | 17 names that template `Many2ManyBinaryField.attachment_preview` (no addon prefix) and cannot inherit it. `web.Many2ManyBinaryField` is extended to call `dwo_attpreview_core.Many2ManyBinaryField.attachment_preview`, a copy of the 17.0 template with the eye. Same DOM as 18/19 |
| `static/src/xml/field_preview.xml` (kanban card) | `//article/t[@t-call=menuTemplate]` | `//div[@role='article']/t[...]` (17 card root is `<div role="article">`) |
| `static/src/scss/attachment_preview.scss` | `var(--bs-border-color-translucent)`, `var(--bs-border-color)`, `var(--bs-border-radius)` | same with fallbacks (Bootstrap 5.1 in 17 has no such variables). `text-bg-*` is backported by Odoo 17 |
| `static/tests/tours/tour_compat.js` | - | new: `dwoAddTour(name, tour)` registers a tour with `test: true` and adapts each 19 step to the 17 (jQuery) tour runner: a step without `run` gets `isCheck: true` (17 would click it), every step gets `in_modal: false` (17 searches only inside the open dialog, so `.modal ...` and toast selectors never match), and `run()` gets `this.anchor` (17 only gives `this.$anchor`). `:contains`, `:has`, `:last` are jQuery selectors on 17 |
| `static/tests/tours/preview_tour.js`, `field_tour.js` | `registry.category("web_tour.tours").add` | `dwoAddTour`; "still on the partner" checks `location.href` (17 keeps the record in the hash: `/web#id=..&model=res.partner`) |
| `tests/test_*tour*.py`, `test_part_preview.py` | URLs `/odoo/res.partner/<id>`, `/odoo/action-<xmlid>[/<id>]` | `/web#id=<id>&model=res.partner&view_type=form`, `/web#action=<xmlid>[&id=<id>&view_type=form]`; `browser_size = "1366,768"` on every `HttpCase` class |
| `tests/test_field_tour.py` | inline `<list>` | `<tree>`; the attachment count excludes `/web/assets/` (17 builds the bus worker bundle, an attachment, on the first page of each test) |
| `docs/CHANGELOG.md` | - | entry "17.0 port of 19.0.1.1.0 (via 18.0)" |

### dwo_attpreview_office

| File | 18.0 | 17.0 |
|---|---|---|
| `__manifest__.py`, `README.md` | `18.0.1.0.2`, "Odoo 18" | `17.0.1.0.2`, "Odoo 17" |
| `models/engine.py` | `self.env._(...)` | `_(...)` |
| `controllers/office.py` | `check_access("read")` | `check_access_rights("read")` + `check_access_rule("read")` |
| `static/tests/tours/office_tour.js` | `registry...add` | `dwoAddTour` from `@dwo_attpreview_core/../tests/tours/tour_compat` |
| `tests/test_engine.py` | `_AssetRouteWithoutTestCookie` needed | kept, but never called: 17 has no `check_test_cursor` (no test cookie check) |
| `tests/test_engine.py` | URLs `/odoo/...`; `_counts` | `/web#...`, `browser_size`; `_counts` excludes `/web/assets/` attachments (see core) |

### dwo_attpreview_mail

| File | 18.0 | 17.0 |
|---|---|---|
| `__manifest__.py` | `18.0.2.0.0` | `17.0.2.0.0` |
| `models/engine.py` | `self.env._(...)` | `_(...)` |
| `static/tests/tours/mail_tour.js` | `registry...add` | `dwoAddTour` (`.modal:last` is the jQuery positional selector on 17) |
| `tests/test_engine.py` | URL `/odoo/res.partner/<id>` | `/web#id=..&model=res.partner&view_type=form`, `browser_size` |

### Checked on 17 and unchanged

- `type="json"` routes, `check_field_access_rights`, `fields.Json`, `_sql_constraints`, `http.Stream(type="data", ...)`,
  `Stream.from_path(path, public=True)`, `file_open`, `file_path`, `make_jsonrpc_request`, `api.depends_context`.
- JS: `AttachmentList` (same `this.fileViewer.open(...)` from the template and same `useFileViewer` as 18), `Many2OneField`
  (`relation`, `resId`, `displayName`, `classFromDecoration`, `onClick`, `hasExternalButton`), `BinaryField` template,
  `KanbanRecord` `menuTemplate`, `ListRenderer.processAllColumn`, `BooleanField`/`CheckBox` (default slot), `Dialog` props
  (`header`, `footer`, `withBodyPadding`, `fullscreen`, `contentClass`, `size`), `.o-mail-AttachmentCard`, luxon global,
  `/** @odoo-module **/` imports between modules, Settings `<app>/<block>/<setting>`.
- Demo data: loaded by default on 17.

### For a 16.0 port (start from this 17.0 code)

- Check `fields.Json` (17+), `Dialog` / `CheckBox` props, the chatter `AttachmentList` (16 has the old messaging models),
  Settings `<app>/<block>/<setting>` (17+), inline `invisible="1"` (16 uses `attrs`), and `browser_size` again.

## #79 - remote pictures through the server (mail 17.0.2.1.0)

Ported from 19.0 `6f63ca6` + `23226fd` (mail 19.0.2.1.0, core `test_settings` and mail catalog).

| File | 19.0 | 17.0 |
|---|---|---|
| `dwo_attpreview_mail/__manifest__.py` | `19.0.2.1.0` | `17.0.2.1.0` |
| `dwo_attpreview_mail/controllers/main.py` | `/dwo_attpreview_mail/remote_settings` `type="jsonrpc"` | `type="json"` |
| `dwo_attpreview_mail/static/src/js/mail_viewer.js` | `rpc` from `@web/core/network/rpc` | `this.rpc = useService("rpc")` |
| `dwo_attpreview_mail/tests/test_engine.py` (tour) | `/odoo/res.partner/<id>` | `/web#id=..&model=res.partner&view_type=form` (same `fetch_picture` patch: no network) |

Checked on 17 and unchanged: `parsers/remote.py` with urllib3 2.0.7 (17 venv, Python 3.12) and 1.26.5
(`requirements.txt` for Python < 3.12): `HTTPSConnectionPool(server_hostname=, assert_hostname=, cert_reqs=)`,
`response.read(n, decode_content=True)`, `release_conn()` (a real download, a redirect and a refused self-signed
certificate were tried by hand outside the tests); Pillow 10.2 with WebP; `http.Stream(type="data", max_age=,
etag=False, as_attachment=False)` (private cache; `nosniff` and `default-src 'none'` come from `set_csp` for pictures);
the controller subclass of `AttPreviewController`; Settings `<block title= name=>` and `<setting id= string= help=>`;
`fields.Boolean(config_parameter=)`; the new tour step (`:not(:contains())` is jQuery on 17, `run()` gets
`this.anchor` from `tour_compat.js`).
