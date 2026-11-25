# Changelog

## Phase 1, second pass (not released): interface review
- KPI cards: change since the previous period (`compare`), goal bar, prefix and suffix, `trend_good`.
- New options: `show_values`, `target`, `percent` (100% stack), `show_percent`, `other`, `heatmap`, `open_records`; new
  option kinds `number` and `text`; registry constraints `option_needs` and `option_aggs`.
- Charts use a categorical palette (6 clearly different colours); tables show dates in the viewer's language and time zone,
  numbers right-aligned, rows can open the record; empty widgets say "No data"; notes such as "Top 8" are muted.
- Explore: one selector per required well already in place and "Count" already chosen, icons for the visuals, the preview on
  top, a searchable data list (this page's data first, then recent), titles written for you ("Count by Country"), options with
  readable names. "+ Add widget" works from the view mode. Page tools moved into a menu.
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
