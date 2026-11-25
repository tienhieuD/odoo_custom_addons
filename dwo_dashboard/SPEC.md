# Dynamic Dashboard specification

Two JSON documents, both closed (unknown keys are errors, one canonical form for everything), so a person, the UI and
an AI assistant can all read and edit them:

- a **page** (`dwo-dashboard/1`): the grid of widgets and the page filters;
- a **dataset definition** (`dwo-dataset/1`): what a page must not carry (metrics, field overrides, SQL).

Model: a **dataset** has typed fields (dimension or measure); a **widget** picks a dataset and puts fields in the
**wells** of its visual type (Power BI "field wells"); **metrics** are named, reusable measures; page **filters** bind
to a field of each dataset.

- JSON Schemas: `static/schema/dwo-dashboard-1.schema.json`, `dwo-dataset-1.schema.json` (core snapshot); the live ones,
  including installed plugins: `env["dwo.dashboard.spec"].get_schema()` / `get_dataset_schema()`.
- Validate: `validate(spec)` and `validate_dataset(defn)` on `dwo.dashboard.spec` ->
  `{"valid": bool, "errors": [{"path", "code", "message"}]}`. `path` is an RFC 6901 JSON Pointer
  (`/widgets/2/wells/values/0/agg`), the same addressing JSON Patch uses.
- Examples: `spec/samples/pages/*.json`, `spec/samples/datasets/*.json`.
- Code: `spec/constants.py` (vocabulary), `spec/registry.py` (visual and dataset types), `spec/structure.py` (shape of a
  page), `spec/dataset.py` (shape of a definition), `spec/semantic.py` (database checks), `spec/schema_gen.py`.
  `python3 spec/schema_gen.py` rewrites the static schemas; `uv run tools/check_schema.py` checks them with the
  reference `jsonschema` library.

## Page

```json
{"schema": "dwo-dashboard/1", "title": "Sales", "description": "optional", "grid": {"cols": 12},
 "filters": [ ... up to 10 ... ], "widgets": [ ... up to 40 ... ]}
```
`grid.cols` 6 to 120 (default 12; the editor raises it to the right-most widget). Widgets sit on the grid with `x, y, w, h` (`x + w <= cols`, no overlap). The editor packs them upwards (a widget slides up until it meets another one) and never sideways, so a page can be as wide as it needs.

## Widget

```json
{"id": "monthly", "type": "bar", "title": "Revenue per month", "x": 6, "y": 0, "w": 6, "h": 4,
 "dataset": "orm:sale.order",
 "wells": {"axis": {"field": "date_order", "interval": "month"}, "legend": {"field": "user_id"},
           "values": [{"metric": "revenue"}]},
 "where": [["state", "in", ["sale", "done"]]],
 "order": [{"field": "date_order", "dir": "asc"}], "limit": 12, "series_limit": 8,
 "options": {"stacked": true, "legend": "bottom"}, "ignore_filters": ["period"]}
```

`icon` (optional): a Font Awesome 4 class (`^fa-[a-z0-9]+(-[a-z0-9]+){0,4}$`, e.g. `fa-money`) shown before the title; without it the card
shows the icon of its type (`fa-hashtag` KPI, `fa-list` table, `fa-th` pivot, `fa-bar-chart`, `fa-line-chart`, `fa-area-chart`,
`fa-pie-chart`, `fa-circle-o-notch` doughnut).

`id`: `^[a-z][a-z0-9_]{0,31}$`, unique in the page, never reused for another meaning (diffs and AI edits refer to it).

### Dataset reference: `<type>:<name>`
`orm:sale.order` (an Odoo model, including Studio models like `orm:x_thing`), `sql:sales_by_person` (a SQL dataset by
code). The prefix is the dataset type and a namespace for plugins (`csv:...`). An `orm` dataset needs no definition: it
exposes all the fields of the model that the viewer may read. A definition adds metrics, labels and hides fields.

### Wells (per visual type)
A well whose `max` is 1 holds **one object**, any other well holds an **array**. Items: dimension
`{"field": "date_order", "interval": "month", "label"?}`; measure `{"metric": "revenue"}` or
`{"field": "amount_total", "agg": "sum", "label"?}` (`agg`: `sum avg min max count count_distinct`; `{"agg": "count"}`
alone counts records); column `{"field": "partner_id.country_id", "label"?}`.

| Type | Wells (min..max) | Notes |
|---|---|---|
| `kpi` | `value` measure 1 | no `limit` |
| `table` | `columns` 1..20 | `limit` default 50, max 500; reads records |
| `bar`, `line`, `area` | `axis` dimension 1, `legend` dimension 0..1, `values` measure 1..5 | with a `legend`, `values` has exactly 1 item (series would be ambiguous) |
| `pie`, `doughnut` | `category` dimension 1, `value` measure 1 | |
| `pivot` | `rows` dimension 0..3, `columns` dimension 0..2, `values` measure 1..5 | at least one of rows or columns |

A dimension is a groupable field/column, a measure an aggregable one. A date or datetime dimension **needs** an
`interval` (`day week month quarter year`), any other must not have one. Each field appears at most once in the
dimensions.

### `limit`, `series_limit`, `order`
- `limit` is the maximum number of groups of the **first** dimension well (top-N axis groups, rows of a pivot, slices of
  a pie), or rows for a table. `series_limit` caps the groups of the second dimension (legend series, pivot columns).
  Neither is split per combination, so a series is never cut halfway. "Other" bucketing is not part of v1.
- `order`: up to 3 items, each exactly one of `{"field": <a dimension or column used in the wells>}` or
  `{"measure": <metric name | "field:agg" | "__count">}`, plus `"dir": "asc"|"desc"`.

### `where` (ORM datasets only)
An Odoo domain as JSON, prefix notation, static values: `["|", ["state", "=", "sale"], ["amount_total", ">", 100]]`.
Operators: `= != > >= < <= like ilike not like not ilike =like =ilike in not in child_of parent_of any not any`.
Field paths follow relations (`partner_id.country_id`); `any` takes a sub-domain. Max 50 conditions, 5 levels. `any!` and
`not any!` (they skip the comodel's record rules) are never allowed.

Context values are objects, never `"$uid"`-like strings (so real text such as `"$100"` stays text):
`{"ctx": "uid"}`, `{"ctx": "company_id"}`, `{"ctx": "today"}`, `{"ctx": "now"}` anywhere a plain value fits, and
`{"ctx": "company_ids"}` only as the whole value of `in` / `not in`. `today` for a date field is the viewer's current
date in their timezone; for a datetime field the comparison uses the start of that day in their timezone, converted to
UTC. Data-dependent filtering of SQL datasets uses the page filters and the SQL parameters instead.

### Options
Per type (a key a type does not list is an error). Kinds: yes/no, a choice, an integer, a number, a short text (12 characters).

| Type | Options |
|---|---|
| all | `format` (`number currency percent`), `decimals` (0..6); charts also `colors` (1..12 of `#rrggbb`) and `legend` (`none top bottom left right`) |
| `kpi` | `goal` (number: draws a progress bar), `trend_good` (`up` default, or `down`: a falling cost is green), `prefix`, `suffix` (e.g. `$`, ` pcs`) |
| `bar` | `stacked`, `horizontal`, `percent` (100% stacked), `show_values`, `target` (number: a dashed reference line), `y_min`, `y_max` |
| `line` | `smooth`, `show_values`, `target`, `y_min`, `y_max` |
| `area` | `smooth`, `stacked`, `percent`, `show_values`, `target`, `y_min`, `y_max` |
| `pie`, `doughnut` | `show_percent`, `other` (the groups beyond `limit` become one "Other" slice) |
| `pivot` | `show_totals`, `heatmap` (the larger the value, the stronger the colour), `other` (see below) |
| `table` | `open_records` (a click on a row opens the record in its form: the standard action enforces access) |

`other` is checked on inline measures and on metrics (a metric whose aggregate is not sum or count is refused).

`y_min` must be lower than `y_max`; neither can be used with `percent` (a 100% stack has its own axis).

**`other` on a pivot** gathers what is beyond the limits: the first row dimension beyond `limit` becomes one row "Other", the
first column dimension beyond `series_limit` one column "Other", and the corner (Other x Other) is computed too, so every row and
column adds up to the real total. Cells are the real total minus what is shown, which is why it is for `sum` and `count` only.
It needs a row dimension. With `show_totals`, the totals are over all rows, Other included.

Rules: `percent` needs `stacked`, or a `legend` well (a 100% stack of one series says nothing). `other` is for `sum` and `count`
only: an average, a minimum, a maximum or a distinct count of the rest is not the total minus the top, so the validator
refuses it (`constraint`). Still not in v1: "Other" beyond the first dimension, drill-down.

### `trend` (KPI only)
```json
"trend": {"field": "date_order", "interval": "month", "points": 12}
```
A small line under the number: the measure of the last `points` (3..60, default 12) days, weeks or months (default `month`) up to
the current one, in the viewer's time zone. A quiet interval is a zero on the line (an average, minimum or maximum has a gap:
nobody, so no average). The line is about the evolution, so a page date filter on the same field does **not** cut it (like for a
comparison, its own condition is replaced); every other filter and `where` still apply.

### `compare` on a line or area chart
```json
"compare": {"field": "create_date", "period": "this_month", "against": "previous_period"}
```
The previous period is drawn over the chart as a dashed grey line. The k-th point of one is the k-th interval of the other
("the 3rd day of this month" against "the 3rd day of last month"), not the same calendar date, so months of different lengths
line up from their start. Both series show every interval of their range (the empty ones as zero). The period and the ranges
are those of the KPI comparison below. Constraints: `field` must be the axis field, the chart has one measure and no legend.

### `compare` (KPI)
```json
"compare": {"field": "date_order", "period": "this_month", "against": "previous_period"}
```
Adds to the KPI result `compare: {current, previous, change_pct, range, previous_range, ...}`; the client shows the change
since the previous period (green or red according to `trend_good`), what it is measured against, and "No data in ..." when
there is nothing to divide by (`change_pct` is then null: never "+∞ %").
- **Which period.** A page date filter bound to the same dataset and field (and not ignored by the widget) decides: its
  current choice, or its default. Otherwise `period` (default `this_month`; `all` is refused: nothing to compare it with).
  If the filter is at `all` there is nothing to compare and no `compare` result.
- **The filter's own condition is replaced** by the two ranges, not added to them; every other filter, and `where`, apply to
  both periods.
- **Ranges** (end excluded, calendar units, the viewer's time zone). `this_*` are *to date*: on 25 Nov, `this_month` is
  [1 Nov, 26 Nov) against [1 Oct, 26 Oct); the shift is a month, a quarter, a year or a week, never a number of days (31 Mar
  minus a month clamps to the end of February). `last_*` are complete periods against the complete period before. `today`,
  `yesterday` and `last_N_days` are compared with the span of the same length just before. `against: "previous_year"`
  shifts the current range back one calendar year (29 Feb clamps to 28 Feb).

## Filters
```json
{"id": "country", "type": "relation", "model": "res.country", "label": "Country",
 "bind": [{"dataset": "orm:res.partner", "field": "country_id"}, {"dataset": "sql:invoices", "field": "country_id"}]}
```
One picker serves every bound dataset, so the filter says what it offers:
- `date`: a date or datetime field/column. `default` is one of `all today yesterday last_7_days last_30_days last_90_days
  this_week last_week this_month last_month this_quarter last_quarter this_year last_year`.
- `relation`: **requires `model`**, the model whose records the picker offers (no `default`). Every bound ORM field must be a
  many2one or many2many **to that model**; a bound SQL column must be an integer and is **trusted** to hold ids of that
  model (a SQL column has no comodel; the author declares it). The author must be able to read the model.
- `selection`: **requires `values`** (1..100 strings, no duplicates), the choices offered; `default` must be one of them.
  Every bound ORM selection field must have all those values; a bound SQL column must be text.

`bind` lists, for each dataset the filter acts on, the field to filter. A widget on a dataset that is not bound is not
filtered, and `ignore_filters` opts one widget out. Every bound dataset must be used by a widget.

## Dataset definition (`dwo-dataset/1`)

```json
{"schema": "dwo-dataset/1", "type": "orm", "model": "sale.order", "label": "Sales orders",
 "fields": {"message_bounce": {"hidden": true}, "name": {"label": "Number"}},
 "metrics": [{"name": "revenue", "label": "Revenue", "agg": "sum", "field": "amount_untaxed",
              "format": "currency", "where": [["state", "in", ["sale", "done"]]]}]}
```
- **Metric**: a named measure usable as `{"metric": "revenue"}`. On an ORM dataset it may carry a `where`. Cost to accept:
  a metric with its own `where` is a separate `_read_group` call, merged with the others by group key; a widget mixing N
  distinct filters runs N queries (all as the viewer).
- **SQL dataset** (`"type": "sql"`): `code`, and a `sql` block: `query` (one `SELECT` / `WITH ... SELECT`, parameters as
  `%(name)s`, a literal percent as `%%`), `params` (from `uid company_id company_ids lang today now`, each declared **and**
  used), `company_scoped` (then `company_ids` must be a used parameter), `groups` (at least one group that may see
  it), `columns` (`name`, `type` text|integer|numeric|boolean|date|datetime, `role` dimension|measure, `label`). On SQL
  columns the roles are **hard rules** (a dimension column cannot be summed, a measure must be a number); on ORM fields
  they are hints for the Explore screen (a numeric year may be a dimension), and the real constraint is the field type.
- `fields.<name>.hidden` is **curation, not security**: a hidden field is refused in the wells, but not in `where`, filter
  binds or relation paths. Security is the viewer's own permissions (ORM) or the dataset's groups (SQL).
- Phase 0 defines and validates the shape only. Running SQL (read-only transaction, restricted DB role, timeout, row cap,
  warnings) is Phase 3b; the models that store definitions arrive in Phase 3.

## Permissions (what the validators and the UI rely on)
- A spec holds no data and grants no access. Every widget on an ORM dataset runs with the permissions of the person
  viewing the page (no `sudo`): access rights, record rules, field groups and companies apply. Two people see different
  numbers on the same page; someone who cannot read a model sees "no access" in that widget only.
- The validator checks that the **author** can read each model and each field used (through relation paths, in `where`,
  in metrics and in filter binds) and, for a SQL dataset, belongs to one of its groups (system administrators always do).
  For an author who is not a system administrator, "does not exist" and "you cannot read it" are reported identically
  (code `access`, one message), so nobody learns what is installed or the shape of what they cannot read. This is not the
  viewer's check. The public `validate` takes no `check_access` parameter (RPC cannot switch the check off), and
  `validate_dataset` is for system administrators only.
- No raw SQL in a page, no expressions, no code. SQL lives in datasets only, written by system administrators.

## Error codes (stable: the UI and AI key on them)
`type`, `required`, `unknown_key`, `too_long`, `pattern`, `range`, `enum`, `length`, `duplicate`, `not_allowed` (shape);
`schema` (wrong `schema` value); `layout` (grid size or overlap); `reference` (points to something that is not there:
a filter, a well item, a bound dataset); `constraint` (a visual type rule, e.g. one measure when a legend is used);
`domain`, `too_deep`, `too_many` (domains); `param`, `company`, `role` (SQL datasets); `json` (not JSON);
`model`, `field`, `dataset`, `metric` (does not exist; only shown to system administrators); `access` (not available to
the author); `hidden`; `capability` (needs a newer Odoo); `unchecked` (a plugin dataset type with no checker installed).

## Compatibility
- Grouping through a relation (`product_id.categ_id`) is supported by `_read_group` from Odoo **19**; 17 and 18 only
  group by the model's own fields. The validator reports it as `capability` when the running Odoo cannot do it.
  Aggregates (measures) are always direct fields of the dataset's model.
- Many2many group-bys are allowed (stored many2many): a record in two groups is counted in both, so totals double-count.
- `sum_currency` (monetary conversion) exists in Odoo 19's `_read_group`; it is not in v1.

## Plugins and versioning
- A **visual type** is data (see `spec/registry.py`): wells, options, limits, constraints, and whether it uses the
  `grouped` engine (`_read_group`) or `records` (`search_read`). A new chart that reuses the grouped engine only needs a
  JS renderer registered for its name. An addon registers it by extending `_dwo_visual_types()` on `dwo.dashboard.spec`
  (`_inherit` + `super()`), so it exists only in the databases where it is installed; the JSON Schema is rebuilt from the
  registry. Dataset types work the same way (`_dwo_dataset_types()`), and bring their semantic check with
  `_dwo_dataset_checkers()` (`{type: callable(ref, widget_path, widget, definition) -> errors}`); a plugin type without a
  checker is refused (`unchecked`), never skipped.
- **Strict on save, tolerant on render**: a page that uses a type that is not installed fails `validate` (it cannot be
  saved), but a stored page must still open, with a placeholder in that widget only.
- `schema` is `dwo-dashboard/<major>`. A non-compatible change gets a new major (a migration upgrades saved pages);
  additive changes (a new type, a new option, a new aggregate) stay in the same major and go in CHANGELOG.

## Metrics (Phase 3)
A dataset can have a stored definition (`dwo.dataset`, Dashboard > Configuration > Datasets and metrics, dashboard managers
write, everybody reads: a definition holds no data). It compiles to a `dwo-dataset/1` document; `{"metric": "revenue"}` in a
value well is replaced by the measure it names (field, aggregate, label, format, `where`) before the widget runs, and the
metric's name stays the key of the measure (`order: [{"measure": "revenue"}]`). A metric is not a permission: the engine runs
as the viewer, saving a page checks that the author can read the metric's field and the fields of its `where`, and `hidden`
flags of a definition only hide a field in the interface.

A metric without `where` is one more column of the widget's single `formatted_read_group`. A metric with a `where` (a plain
domain; dynamic values are not supported yet) is read by a query of its own, over the same groups, and merged by group:
- the groups are those of the widget's own domain and page filters, whatever the metric matches: a group with records but none
  matching keeps its place, with 0 for a sum, a count or a distinct count and an empty value for an average, minimum or maximum;
- `order` and `limit` of such a widget are applied after the merge, in Python (the top N by a metric computed from its own
  subset would not be the top N of the widget); a date group is ordered by its date, a many2one group by its name;
- two metrics of the same field and aggregate with different `where` keep separate columns;
- `other` accepts sum and count metrics only; `show_totals`, `compare` and `trend` work with metrics.

## The assistant (Phase 4)
`dwo.dashboard.ai.propose(page_id, request, datasets, current)` returns a new page for a request in words; it never saves. The
caller must be able to edit the page. The page proposed is validated as the caller (`validate`), so the assistant can never
produce what the person could not write by hand; two harmless mistakes are repaired (a widget laid over another goes to the
bottom, a sort by something that is not a measure is dropped); anything else goes back to the model once with the errors, then
the answer is refused. The editor loads a proposal as its draft: Save and Discard decide, and the revision check protects the page.

What leaves the server: the format of a page (`spec/grammar.py`, generated from the registry), the names and kinds of the fields
the caller can read in the datasets in play (those of the page and the ones chosen), the metrics, the page as it is now and the
request. No record. Providers (`_dwo_ai_providers`): Odoo's gateway `olg.api.odoo.com` (what the HTML editor uses: plain text in,
plain text out, no system role, one prompt of about 9 000 characters is accepted, a call takes 15 to 30 s) or any
OpenAI-compatible chat API. The provider and the key are set by system administrators; the key is written, never read back.

## Sharing and clicks (Phase 2)
Sharing is a property of a stored page, not of its spec: who may read or edit it is decided by record rules on
`dwo.dashboard.page` and `dwo.dashboard.share`. The widgets always run as the person who views the page.

`run_widget(page_id, widget_id, filter_values, interactions)`; `interactions` (never saved) is
`{"select": {"widget": id, "key": k}, "drills": {widget id: [k1, k2]}}`, where the keys are those the server returned in
`rows[].keys[0]`. The primary dimension of a widget is the first item of `axis`, `category` or `rows`. The server adds the
conditions to the widget's `where` before validation: a selected key narrows every other widget of the same dataset, and the
widgets of another dataset that have a field of the same name, type and comodel; a drill replaces the interval by the next one
(year, quarter, month, week, day) and keeps the group chosen at each level. A key that does not fit (wrong type, `__other`,
unknown widget) is ignored. `drill_records(page_id, widget_id, key, filter_values, interactions)` gives the ids behind a click
(at most 1000, with the total).

## Editing guide for an AI assistant
1. Start from the current page; change as little as possible; keep every existing `id`.
2. Use only datasets, fields and metrics the person may read (the `describe_dataset` tool, Phase 4); never invent fields.
3. A date dimension always has an `interval`; a time series is ordered by its axis field.
4. Put new widgets below the lowest one (`y` = its `y + h`), `w <= grid.cols`.
5. Validate before proposing; show the person the difference (a JSON Patch over these pointers) and apply it only when
   they accept.
