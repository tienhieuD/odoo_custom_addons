# List View Sticky - Test Lab (developer only, do not publish)

Test bed for `listview_sticky_header_and_column`: wide lists with fake data, a search panel and a form
full of different `x2many` lists.

* **Where**: top-level app **List Sticky Test Lab** (no developer mode needed).
* **No stored data**: on Odoo 12 `_table_query` cannot be used here, so each `_auto = False` model is backed by a SQL VIEW
  created in `init()` (a SELECT over `generate_series`): no table and no stored row. Data is deterministic (hash of the id)
  and read-only: edits are accepted but not saved, creating a record raises an error.
* **Lists**: wide list (52 columns, ~30 widgets, search panel), editable list (40 columns), grouped list.
* **Form** (record > tabs): 7-column list full width, 17-column editable list, 38-column list, two half-width lists, more fields.
* **Tests**: `odoo-bin -d <db> -i listview_sticky_test_lab --test-tags /listview_sticky_test_lab` drives pin + scroll checks
  (sticky header, pinned columns aligned after horizontal/vertical scroll, per-list pins in a form, editing a row).
* `tools/` holds the generator of `models/models.py` and `views/lshc_test_views.xml` (needs Pillow).
* Odoo 12 has no search panel: the wide list has the normal search bar only.
