# Screenshots for the Odoo Apps page (dwo_attpreview_office)

Folder: `static/description/screenshots/`, used by `static/description/index.html` and mirrored into the Settings popup of the core (`sync_attpreview_catalog.py`). Taken again all at once on 2026-11-15 (#72): Odoo 19.0 (20260412), English UI, 1600x900, admin, temporary database (core + office + mail), fictional data (company "Northwind Staffing", partner "Sakura Manufacturing Ltd."), English sample files in `_scratch/attpreview_samples/listing72/` (copies of `jp_labor_2024/japan-labour-market-2024.{xlsx,docx,pptx}`, `open_positions.csv`); the old .xls/.doc are the Apache POI samples of `tests/files`.

| Picture | Scene | Script |
| --- | --- | --- |
| `02-xlsx-sheet-with-charts.png` | xlsx in the large dialog, sheet "Status & Industry": table, formats, doughnut chart | `listing_shots.mjs` 02 |
| `03-xlsx-hiring-flow-arrows.png` | Sheet "Hiring Flow": shapes and connector arrows (patch 0001) | `listing_shots.mjs` 03 |
| `04-docx-continuous-scroll.png` | docx as a continuous scroll (page 2 of 10, table of headline figures) | `listing_shots.mjs` 04 |
| `05-pptx-slide-with-chart.png` | pptx slide 4 with two charts, previous/next | `listing_shots.mjs` 05 |
| `15-docx-search.png` | Search bar in a docx: "minimum wage", 1 / 12, match highlighted | `listing_extra_shots.mjs` 15 |
| `17-legacy-xls-warning.png` | Old .xls under the warning banner | `listing_extra_shots.mjs` 17 |
| `18-legacy-doc-warning.png` | Old .doc under the warning banner | `listing_extra_shots.mjs` 18 |
| `19-csv-as-sheet.png` | csv shown as a sheet of text cells (leading zeros kept) | `listing_extra_shots.mjs` 19 |

`listing_extra_shots.mjs` also takes `16-xlsx-search` (left out: some highlight boxes of the xlsx search are drawn about half a row above the matched cell, see #72), `20-xlsm-macros-not-run` and `21-xlsx-from-binary-field` (left out: they look the same as an xlsx). Pictures 01, 06-14 belong to `dwo_attpreview_core`.

How to take them again: `dwo_attpreview_core/docs/SCREENSHOTS.md` ("Taking them again"); this module's `docs/tools/listing_shots.mjs` is an older copy (its scene 07 uses a removed menu): use the core one.

## Older shots outside the module

Legacy formats and csv/tsv of #69: `_scratch/attpreview_samples/office_legacy_v11/shots/`; search of #71: `_scratch/attpreview_samples/search_v12/`; variants of #70: `_scratch/attpreview_samples/variants/shots/` (some use Vietnamese sample data: not for the listing).
