# Dynamic Dashboard (`dwo_dashboard`): handoff for the next developer or AI

Written when the previous session ran out of tokens. Everything below is true of the code in the commit that adds this file.
Issue with the history of the work: https://github.com/tienhieuD/agentm4/issues/93 (read its comments; this file is the summary).

## 0. Who the owner is and how to work
- The owner is Vietnamese: **reply in Vietnamese, short**. They often read on a phone: send screenshots with `SendUserFile`.
- **Commit/push/deploy only when the owner says so** (they say "commit, push và deploy kèm --rebuild"). Stage only `dwo_dashboard` and
  `.demo/demo_dwo_dashboard` (and `_agent` demo-server files when they changed). Never store secrets. Never drop DBs starting `odoo_` or `odoo18_`.
- Project layout, test commands and rules: `~/Documents/Project/CLAUDE.md` and `_agent/rules/core.md`. Repo `odoo_custom_addons`, branch `19.0`,
  folder `~/Documents/Project/odoo_appstore/odoo_custom_addons19/`. Only Odoo 19 exists for this module (no ports yet).
- Use the `advisor` tool before building and before reporting; the owner asked for it. Ask the owner before decisions that are theirs.

## 1. What exists (all committed; demo at https://demo-dashboard.duotek.io.vn, users demo_alice/bob/carol/demo_admin, password `demo`)
Spec `dwo-dashboard/1` (page) and `dwo-dataset/1` (dataset) are in `SPEC.md`, `spec/` and `static/schema/` (JSON Schema is generated: `python3 dwo_dashboard/spec/schema_gen.py`; check: `uv run dwo_dashboard/tools/check_schema.py`).
- **Phase 1** per-user dashboards, pages, grid (gridstack, fixed 84 px columns, up to 120 columns, packs upwards), KPI/table/bar/line/area/pie/doughnut/pivot, page filters, Explore panel, engine runs every widget **as the viewer** (no sudo).
- **Phase 2** sharing a page with users/groups (View/Edit), "Shared with me", revoke, log; cross-filter, drill-down, drill-through (`engine/interact.py`, server builds conditions from a key; never a client domain).
- **Phase 3 metrics**: `dwo.dataset` (kind orm) + `dwo.dataset.metric`; metrics with a `where` are read by separate queries and merged (`engine/measures.py`, the only caller of `formatted_read_group`).
- **Phase 3c blend** (`blend:<code>`, `engine/blend.py`): 2-3 Odoo models merged by shared dimensions, as the viewer.
- **Phase 3b SQL** (`sql:<code>`, `engine/sql.py`, `spec/sqlscan.py`): see section 3 (security).
- **Related paths** in Explore: `partner_id.country_id` (`describe_related`).
- **Phase 4 AI** (`models/dwo_dashboard_ai.py`, `spec/grammar.py`): "Ask AI" in edit mode; Odoo AI gateway (olg.api.odoo.com) default or an OpenAI-compatible API; proposal loads as a draft, never saved by the assistant.
- **Groups**: Dashboard User (implied by every internal user) and Dashboard Manager (configures datasets/metrics/AI; administrators are managers; **managers do not read others' private dashboards**).
- UI: cards, header icons (`icon` key, Font Awesome 4), phone = view only (Edit hidden under 768 px; owner has not decided on a one-column editor).

## 2. Map of the code
- `spec/`: pure Python. `registry.py` (visual and dataset types as data), `structure.py` (shape), `semantic.py` (needs the DB: fields readable by the *caller*), `dataset.py` (dataset shape), `sqlscan.py`, `grammar.py` (prompt text for the AI), `schema_gen.py`.
- `engine/`: `grouped.py` (KPI/charts/pivot), `records.py` (table), `measures.py`, `blend.py`, `sql.py`, `interact.py`, `domain.py`, `dates.py`, `fill.py` (empty intervals; Odoo's `fill_temporal` fails with datetime+tz), `guard.py` (timeout/row cap).
- `models/`: `dwo_dashboard.py` (dashboard, page, sharing methods), `dwo_dashboard_share.py`, `dwo_dataset.py` (kinds orm/blend/sql; SQL form pieces `sql_query`, `sql_group_ids`, `sql_options` compile into `definition_text`), `dwo_dashboard_engine.py` (`run_widget`, `run_preview(widget, filters, values, page_id)`, `drill_records`), `dwo_dashboard_explore.py` (datasets and fields the caller can read), `dwo_dashboard_spec.py` (validators, `_dwo_resolve_dataset`, `_sql_enabled`), `dwo_dashboard_ai.py`, `dwo_dashboard_ai_settings.py` (`dwo.ai.config` wizard).
- `static/src/`: Owl client action (`dashboard_action.*`), `explore_panel.*`, `widget_card.*`, `renderers/`, `share_dialog.*`, `ai_dialog.*`, `page_name_dialog.*`, `filter_*`. SCSS in `dashboard.scss`.
- `.demo/demo_dwo_dashboard/`: demo data (sales orders, metrics dataset, blend dataset, pages, demo_admin). Demo server scripts: `_agent/scripts/demo-server` (`demos.d/dashboard.conf`).
- Tests: `tests/` (291 at last run, 0 failed). Tours in `static/tests/tours/`.

## 3. Security model of SQL datasets (read before touching `engine/sql.py`)
A SQL dataset **ignores record rules**. Everybody who can open a page using it sees the output; only Dashboard Managers can write one or read its text. Who sees it: the groups in "Who can use it" (default Dashboard User) plus the page being readable (owner or shared); `run_preview` needs a page the person can edit.
**The boundary is a PostgreSQL login of its own**, created by `tools/sql_role_setup.sql` (run once as superuser), given to Odoo as env vars `DWO_SQL_USER` / `DWO_SQL_PASSWORD` (never in the DB). It can SELECT only columns that do not look like credentials, nothing on secret tables, read-only, timeout. Odoo refuses a login that is a superuser/createrole/createdb/bypassrls or that can read a credential-looking column. Without the env vars SQL datasets say "not set up". Other layers (defence in depth): single-statement scanner, wrapped subquery with declared identifiers and bound values, `EXPLAIN (VERBOSE)` plan denylist (tables, function scans), timeout, row cap, rollback, nothing logged.
**SQL is OFF on the public demo** (no login configured) on purpose: `demo_admin` has a public password. Do not enable it there without the owner's explicit OK.
Local dev: the local Postgres user `odoo` is a superuser, so tests can create a login (`tests/test_sql.py` creates and drops `dwo_t_reader`). On the demo server `odoo` is not superuser and cannot create roles; the SQL tests skip themselves there.

## 4. How to run things
```bash
cd ~/Documents/Project/odoo_core/odoo-19.0.20260412
export ODOO_BROWSER_BIN="$(ls -d ~/Library/Caches/ms-playwright/chromium-[0-9]*/chrome-mac-arm64/Google\ Chrome\ for\ Testing.app/Contents/MacOS/Google\ Chrome\ for\ Testing | tail -1)"
DB=tmp_odoo19_dashboard_$(date +%Y%m%d%H%M%S); C=~/Documents/Project/odoo_appstore/_conf/odoo19.conf
./venv/bin/python odoo-bin -c $C -d $DB -i sale --without-demo=True --stop-after-init            # install Sales FIRST (sale tests skip otherwise)
./venv/bin/python odoo-bin -c $C -d $DB -i dwo_dashboard --test-tags /dwo_dashboard --http-port=8795 --gevent-port=8796 --stop-after-init > /tmp/full.log 2>&1
grep -n "FAIL:\|ERROR:\|tests when loading" /tmp/full.log | tail     # expect 0 failed
./venv/bin/python ~/Documents/Project/odoo_appstore/_tools/dbs.py drop tmp_odoo19_dash                     # always drop the temp DBs; also rm __pycache__
```
Demo: `cd ~/Documents/Project/_agent/scripts/demo-server && ./push.sh root@165.22.106.204`, then on the server `/opt/demo-server/deploy.sh --force; /opt/demo-server/add-demo.sh dashboard --rebuild; /opt/demo-server/demo-check.sh dashboard --public` (ssh root@165.22.106.204; the admin password is in `/var/lib/demo/dashboard.admin`, format `admin / <password>`).
Screenshot helpers used before are throw-away Playwright scripts (`uv run script.py`, `# /// script dependencies = ["playwright"]`); for a quick local UI check, install `sale` + `demo_dwo_dashboard` into a DB and run a server on port 8791.

## 5. Gotchas learned the hard way
- **Odoo 19 CSS variables have NO `bs` prefix** (`--body-bg`, `--border-color`, `--table-bg`). A `--bs-*` name is empty and silently drops the whole declaration.
- Never let Owl own the inline `style` of the gridstack container (it wipes gridstack's variables; widgets collapse to width 0). `--dwo-cols` is set with `style.setProperty`.
- `formatted_read_group` keys: a date and a datetime do not write the same key; blend normalises keys itself.
- ORM constraints run as superuser: author-access checks are in `create`/`write` with the caller's env.
- In tours, `<option>` elements are not "visible": trigger on `select:has(option[value=...])`.
- Test helpers must not be named `run` (it overrides unittest's `run`).
- `dwo.dataset` fields `definition_text`, `sql_query`, `sql_options`, `sql_group_ids` are manager-only (`groups=`); read them through `sudo()` in server code.
- The server-side `deploy.sh` upgrades each demo template; check upgrades from the previous demo commit with `git archive <commit> | tar -x -C /tmp/old_addons`, an extra addons path, then `-u`.

## 6. TO DO NEXT (the owner asked for item A; the rest is the remaining plan)
**A. AI assistance when creating a dataset (DONE and committed; NOT yet tried in a browser).** `dwo.dashboard.ai.propose_dataset(kind, request, refs, current)` (kinds `blend`, `orm` metrics, `sql`; managers only; one retry with the validation errors; never saves), `spec/grammar.dataset_help(kind)`, `dwo.dashboard.ai._describe_tables` (information_schema; skips the SQL denylist and `SECRET_COLUMN` columns, max 8 tables), wizard `models/dwo_ai_dataset_wizard.py` (Ask -> shows the answer -> "Use it" writes it), views in `views/dataset_views.xml` (button "Ask AI" in the dataset form, menu Configuration > Create a dataset with AI), access row, tests `tests/test_ai_dataset.py` (311 tests pass on 19). A SQL answer is run through `sql_engine.sample` only when a read-only login exists; otherwise it is marked untested. The current definition is sent only if the manager ticks the box. Still to do, in this order: (1) **try the wizard in a real browser with Playwright against the real Odoo AI gateway (provider `odoo_olg`, the default; the owner does not want a fake server)**: Ask AI from a dataset form and from Configuration > Create a dataset with AI, for blend, SQL and metrics; press Use it, then Check; look at the layout of the dialog (the answer box, the error box, the footer buttons) and at the text sent (field names only). The owner asked to run it in Docker (`odoo:19.0` image + `mcr.microsoft.com/playwright/python`, a draft compose file was in /tmp/dwo_ai_e2e and is lost; Postgres is the `postgres179` container, `host.docker.internal:5179`, odoo/odoo, mount `odoo_custom_addons19` read-only on /mnt/extra-addons); the assistant that did this work was refused permission for `docker compose`, so either allow it or run natively (`odoo_core/odoo-19.0.20260412/venv`, Playwright in a temp venv, Chrome at `~/Library/Caches/ms-playwright/chromium-1255/chrome-mac-x64`). (2) changelog entry and manifest version bump, listing/duotek text if the owner wants the feature announced, (3) ports to the other versions, (4) deploy to the demo only with the owner's OK (SQL stays off there). Known limits: the OLG gateway of a database without credit or IAP may refuse, which shows as the usual "could not answer" message; the SQL answer is tested on the database only when `DWO_SQL_USER` is set, otherwise it is marked untested.
**B. Other open items:** (1) "Preview as another user" was left undone on purpose (it would show the owner another person's data; if done, administrators only; owner said "để lại"). (2) Editing on a phone (currently view only; owner undecided: one-column editor or keep). (3) A structured form for blend (today: JSON with a Check button). (4) Formula metrics for blend (`a - b`, `a / b`): ask the owner first. (5) Ports to Odoo 12-18/20 (none done). (6) Enabling SQL on a real server: run `tools/sql_role_setup.sql`, set the env vars, restart. (7) Possible later phases in issue #93: alerts, e-mail digests, change history, more chart types. (8) Dark mode of Odoo is untested (Enterprise only).
**C. Not verified:** OpenAI-compatible provider against a real service (only mocked); the AI settings form's OpenAI fields in a browser; WebKit/Safari on a real iPhone; SQL on a real production database; the owner's report that "admin cannot use the dashboard / add a page" could not be reproduced (they are investigating).

## 6b. Datasets "like Power BI" (owner's request, issue #93, 2026-11-27)
Decisions: (1) Explore already groups/filters through many2one paths (the "relationships"). (2) The blend keeps its engine and its JSON
(`kind` value `blend`, ref `blend:<code>`) but is presented as a **model of several tables** and edited with Odoo one2many lists
(owner: "dùng kiểu của Odoo, vẫn lưu JSON, JSON và record map 1-1"). Models `dwo.dataset.table`, `.dimension`, `.dimension.map`
(file `models/dwo_dataset_blend.py`) and `dwo.dataset.metric.table_id`. Two pure functions: records -> document
(`_blend_document`) and document -> records (`_sync_from_document`); the stored JSON is the canonical rebuilt one.
(3) Rules: rebuild the JSON only when a write carries child commands (never on a plain write: an old blend has JSON but no lines
until the post-migrate creates them); a write with both `definition_text` and child commands is refused; a blend with no
dimension or no measure is a **draft** (saved, hidden from Explore, `_definition()` is `{}`), because lines can only point to saved
tables; dimension and measure lists are read-only until the record is saved. A map line keeps the field PATH (`field_path`, may be
dotted); `field_id` is its picker. Tables may repeat a model (the demo reads `sale.order` twice). (4) A widget on a multi-table
model groups only by the shared dimensions; one table's own fields are used through its Odoo model dataset + Metrics.
(5) Not done: row-level joins such as `mail.message` (`model` + `res_id`), `dwo-dataset/2`, converting one-model blends to metrics.

## 7. State of the repos at handoff
- `odoo_custom_addons` branch `19.0`: the demo server runs commit `e760997`. The commit that adds this file (related paths, blend, SQL, review fixes)
  is pushed but **NOT deployed**; deploying needs the owner's OK and `--rebuild` (demo data changed: new blend dataset and widgets).
- `_agent` repo: demo-server `dashboard.conf` and README are already pushed; nothing pending.
