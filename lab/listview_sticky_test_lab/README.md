# List View Sticky - Test Lab (developer only, do not publish)

Test bed for `listview_sticky_header_and_column`: wide lists with fake data, a search panel and a form
full of different `x2many` lists.

* **Where**: top-level app **List Sticky Test Lab** (no developer mode needed).
* **No database objects**: the models are `_auto = False` and define `_table_query` (a SELECT over
  `generate_series`), so no table, no view and no stored row is created. Data is deterministic (hash of the id)
  and read-only: edits are accepted but not saved, creating a record raises an error.
* **Lists**: wide list (52 columns, ~30 widgets, search panel), editable list (40 columns), grouped list.
* **Form** (record > tabs): 7-column list full width, 17-column editable list, 38-column list, two half-width lists, more fields.
* **Tests**: `odoo-bin -d <db> -i listview_sticky_test_lab --test-tags /listview_sticky_test_lab` drives pin + scroll checks
  (sticky header, pinned columns aligned after horizontal/vertical scroll, per-list pins in a form, editing a row).
* `tools/` holds the generator of `models/models.py` and `views/lshc_test_views.xml` (needs Pillow).
