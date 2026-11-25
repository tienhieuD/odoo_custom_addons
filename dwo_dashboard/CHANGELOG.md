# Changelog

## Groups (not released)
- Two groups under Settings > Users > Dashboard: **User** (uses the dashboards; implied for every internal user, as before) and
  **Manager** (also writes datasets and metrics and configures the assistant; implies User; administrators are managers). A manager
  needs no Settings right. The AI form is now its own model (`dwo.ai.config`, with an on/off switch) instead of the Settings app.
- A manager has full rights on the configuration and none on private pages: nobody reads somebody else's private dashboard.

## Phase 4 (not released): the assistant
- "Ask AI" in the editor: a request in words becomes a proposed page, loaded as the draft (nothing is saved by the assistant).
  Providers: Odoo AI (default, no setup) or an OpenAI-compatible API (Dashboard > Configuration > AI assistant; the key is written
  and never read back). Validated as the caller; two harmless mistakes repaired; one retry with the errors. No record is sent.
  See SPEC "The assistant".
- The grid is as wide as its widgets (up to 120 columns), widgets stay where they are dropped (no packing), and a page grows to
  the right while editing, with a sheet-like cell grid.
- Drill-through of a widget of metrics lists the records the metrics count (all measures with the same `where`), or the whole
  group when they differ, with a notice.

## Phase 3 (not released): metrics
- `dwo.dataset` and `dwo.dataset.metric` (admin form with a field picker and Odoo's domain widget), compiled to `dwo-dataset/1`;
  `_dwo_resolve_dataset` reads them. Metrics with and without `where`, see SPEC "Metrics". `engine/measures.py` is the only
  place that calls `formatted_read_group`. `other` with a non-additive metric is refused on save; the author's access to a
  metric's fields is checked on save and the viewer's at render. Explore lists the metrics under "Metrics of this data"; a
  metric's `format` is the default format of the widget that shows it.
- Fixed in Explore: sorting by the sum (or any other aggregate) of a field was parsed wrongly ("amount_total:sum").
- Demo: the Sales page runs on five metrics (revenue, orders, average order, open quotations, quoted amount).

## Interface pass 4 (not released)
- On a computer the grid has a fixed size: one column is 84 px wide (12 columns = 1140 px), in the view and the edit mode alike. A wide
  window shows an empty grey area at the right, a narrow one scrolls sideways. Only the phone layout (under 768 px) is responsive.

## Interface pass 3 (not released)
- New widget key `icon` (a Font Awesome class) shown before the title; default per type (KPI `fa-hashtag`, table `fa-list`, pivot
  `fa-th`, charts their own). Chosen in Explore ("Icon and title"). Schema snapshot, `check_schema.py` and tests updated.
- Card header: more space (46 px, 16 px at the sides, the same as the body) and a border under it.
- KPI: one block centred in the card both ways; the trend is a background, full width, stuck to the bottom edge, 30% of the card.
- Tables and pivots run edge to edge in the card (their first and last cells keep the 16 px).

## Interface pass 2 (not released)
- Cards: white, rounded, soft shadow, on a faint grey canvas; the gap between cards is one value (12 px) shared by the view and
  the edit mode (gridstack uses `cellHeight = row + gap`, so a card has the same height in both).
- Colours use Odoo's own CSS variables, which are NOT prefixed in Odoo 19 (`--body-bg`, `--border-color`, `--table-bg`): a
  `--bs-*` name is empty and drops the whole declaration. This was why table headers had no background and overlapped rows.
- "Arrange" is "Edit", "Cancel" is "Discard" (as in Odoo forms); "Add widget" and "Add filter" only show while editing; buttons are
  Odoo's standard ones with `gap-1`.
- "+" asks for a name in a dialog and creates the page on OK only (Enter works, empty is refused); rename uses the same dialog.
  A new page goes to the end of the list.
- Pages are reordered by dragging their handle (shown on hover, always on touch screens; not on a phone, where "Move up/down"
  stays). Dragging by the name does nothing.
- Tables and pivots: sticky header with the card's colour, pivot with a sticky first column, no wrapping, scroll shadows; dates
  without seconds; chart legends use round markers; KPI content starts at the same height in every card; the demo KPIs are 3 rows high.
- Share dialog: select no longer overlaps its arrow, the history is of the page, with words and local times.
- The click menu stays inside the window.

## Phase 2 (not released): sharing and interaction
- **Sharing**: a page can be shared with users and groups (`dwo.dashboard.share`), level View or Edit. Recipients see it under
  "Shared with me" and run every widget with their own access rights. Editors change the content only (spec); the owner alone
  renames, deletes, orders and manages shares. Revoking, leaving a group or losing the share closes the page at once. "Save a
  copy" puts a copy in the caller's own dashboard. A share log (readable by the person who shared) records grants, level
  changes and revocations. Recipients are internal users only.
- Not provided on purpose: "preview as another user". Running the engine as someone else shows the owner that person's data;
  it needs the owner's decision (see issue #93).
- **Cross-filter**: a click on a bar, a slice or a pivot row (menu: Filter the other widgets) narrows the other widgets of the
  same data, and those of other data that have the same field; a chip in the toolbar clears it.
- **Drill-down**: a time axis goes year, quarter, month, week, day; the card shows the path and a way back up.
- **Drill-through**: "Show records" opens the records behind the click as a list.
- The client sends only the group key it was given (`interactions`); the server writes the conditions from the saved page
  (`engine/interact.py`), never from a client domain. Clicks are not saved in the page.

## Phase 1, second pass (not released): interface review
- KPI cards: change since the previous period (`compare`), goal bar, prefix and suffix, `trend_good`.
- New options: `show_values`, `target`, `percent` (100% stack), `show_percent`, `other`, `heatmap`, `open_records`; new
  option kinds `number` and `text`; registry constraints `option_needs` and `option_aggs`.
- Charts use a categorical palette (6 clearly different colours); tables show dates in the viewer's language and time zone,
  numbers right-aligned, rows can open the record; empty widgets say "No data"; notes such as "Top 8" are muted.
- Explore: one selector per required well already in place and "Count" already chosen, icons for the visuals, the preview on
  top, a searchable data list (this page's data first, then recent), titles written for you ("Count by Country"), options with
  readable names. Page tools moved into a menu.
- Page filters can now be created in the interface ("Add filter": a period, some records, or a choice), bound by themselves
  to every data source of the page that has the field.
- Third pass: the options that were deferred: `y_min` / `y_max` (checked: lower than each other, not with `percent`), a KPI
  `trend` (sparkline), the previous period drawn over a line or area chart (`compare` on a chart), `other` on a pivot (Other
  row, Other column and the corner, totals over all rows). Empty intervals are filled by `engine/fill.py` with the keys and
  labels of `formatted_read_group` (Odoo's own `fill_temporal` fails with a datetime and a time zone); a test compares them for
  every interval, both field types and four time zones.
- Still deferred: drill-down (Phase 2), the `other` check on metrics (Phase 3).

## Phase 1 (not released): the dashboard, usable by one person
- Models `dwo.dashboard` (one per user, private: global record rules, administrators included) and `dwo.dashboard.page`
  (`spec` JSON validated as the person who saves it, in `create`/`write`: ORM constraints run as superuser and cannot
  know what the writer may read; revisions refuse a save from a stale tab).
- `dwo.dashboard.engine`: `run_widget` (stored page) and `run_preview` (Explore): one RPC per widget, always as the caller
  (no sudo), validated again as the caller, filter values re-checked, errors per widget (`access`, `invalid`, `timeout`,
  `failed`), `statement_timeout` inside a savepoint (default 60 s, `dwo_dashboard.query_timeout`), row cap
  (`dwo_dashboard.max_rows`). Grouped widgets use Odoo's own `formatted_read_group`; top-N is exact (first the top groups
  of the first dimension, then the other dimensions for those groups only); pivot totals come from the database; a
  time zone PostgreSQL does not know falls back to UTC.
- `dwo.dashboard.explore`: `list_datasets`, `describe_dataset` (built on `fields_get`), `filter_options`: only what the
  caller may read.
- Client action: pages on the left, grid (plain CSS grid to view, gridstack 13.3.0 to edit, loaded lazily), filter bar
  (date presets, relation, selection), Explore panel (dataset, visual, wells, sort, limit, options, filter, live preview),
  renderers registered in `dwo_dashboard.visuals` (kpi, table, bar, line, area, pie, doughnut with Chart.js, pivot).
- Not in Phase 1: metrics (`{"metric": ...}` needs stored dataset definitions: Phase 3), SQL datasets (3b), sharing (2).

## 19.0.0.1.0 (Phase 0', not released)
- Specification redone on a BI model (datasets, named field wells, metrics, bound page filters): pages `dwo-dashboard/1`
  and dataset definitions `dwo-dataset/1`, with JSON Schemas generated from a registry of visual and dataset types.
- Plugin hooks `_dwo_visual_types`, `_dwo_dataset_types`, `_dwo_resolve_dataset` on `dwo.dashboard.spec`.
- Validators: structure (pure Python, JSON Pointer paths), dataset definition, semantics (models, fields, types,
  author's model and field access, relation paths).
- `validate`, `validate_dataset`, `get_schema`, `get_dataset_schema`, `get_registry`.
- Review fixes: public `validate` takes no `check_access`; `validate_dataset` is admin-only; opaque access errors for
  non-admin authors; SQL dataset `groups` apply to the author; relation filters declare `model`, selection filters
  `values` (one picker for every bound dataset); plugin dataset types need a checker.
- Samples (4 pages, 3 dataset fixtures), 70 tests. No user interface and no SQL execution yet.
