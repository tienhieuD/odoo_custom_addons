# Changelog

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
