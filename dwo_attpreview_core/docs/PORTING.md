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
