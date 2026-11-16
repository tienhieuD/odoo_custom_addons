# Screenshots for the Odoo Apps page (dwo_attpreview_core)

Folder: `static/description/screenshots/`, used by `static/description/index.html` (#72). Taken again all at once on 2026-11-15 (#72) on Odoo 19.0 (20260412), English UI, 1600x900, admin, temporary database without demo data (core + office + mail), fictional data: company "Northwind Staffing", partner "Sakura Manufacturing Ltd.", English sample files (`_scratch/attpreview_samples/listing72/`: copies of `jp_labor_2024/japan-labour-market-2024.{xlsx,docx,pptx}`, `open_positions.csv`, a random `legacy-export.bin`). No personal data, no machine path.

| Picture | Scene | Script |
| --- | --- | --- |
| `01-chatter-attachments.png` | Chatter of a partner with attachments of several types (xlsx, docx, pptx, pdf, picture, unknown file) | `listing_shots.mjs` 01 |
| `06-toast-unsupported-file.png` | Notice for a file that cannot be previewed (file name, reason, Download), no dialog | `listing_shots.mjs` 06 |
| `07-preview-engines.png` | Settings > Attachment Preview: max file size and engine tick boxes (office "Not installed", mail "Installed") | `listing_shots.mjs` 07 |
| `08-engine-popup.png` | Popup of an engine that is not in the addons (office): file types, its Odoo Apps page (catalog copy), note, "Open on Odoo Apps" | `listing_shots.mjs` 08 |
| `09-binary-field-preview.png` | Crop: "File Content" field of an attachment form with the Preview eye before Edit / Download / Clear | `field_shots.py` |
| `10-binary-field-dialog.png` | The dialog opened from that field (docx drawn by the office engine) | `field_shots.py` |
| `11-binary-and-many2one-preview.png` | Crop: binary field of a partner (PDF) and many2one to an attachment, each with its eye | `field_shots.py` |
| `12-many2many-binary-preview.png` | Crop: `many2many_binary` field, eye next to each file | `field_shots.py` |
| `13-attachment-list-preview.png` | Crop: many2many list of attachments with the Preview column | `field_shots.py` |
| `14-attachment-kanban-preview.png` | Crop: card of the Attachments menu (kanban) with its eye | `field_shots.py` |

Pictures 02-05 and 15-19 (office files in the dialog) belong to `dwo_attpreview_office/static/description/screenshots/`.

## Taking them again

1. Start Odoo 19 on a temporary database (`tmp_odoo19_*`, never the dev database) with core + office + mail, another port than the dev server, e.g. `odoo-bin -c odoo19.conf -d tmp_odoo19_shots -i dwo_attpreview_core,dwo_attpreview_office,dwo_attpreview_mail --http-port=8792 --gevent-port=8794`.
2. Playwright (npm for the `.mjs`, Python for `field_shots.py`) and Chrome for Testing (`CHROME`). The `.mjs` scripts import `playwright`: link a `node_modules` next to them while shooting and remove the link afterwards (it must not ship with the module).
3. `node docs/tools/listing_shots.mjs PORT DB SAMPLES_DIR OUT_DIR 01,02,03,04,05,06`, then `python3 docs/tools/field_shots.py PORT OUT_DIR SAMPLES_ROOT` (SAMPLES_ROOT holds `jp_labor_2024/`), then `node ../dwo_attpreview_office/docs/tools/listing_extra_shots.mjs PORT DB SAMPLES_DIR OUT_DIR`.
4. Only after the office `index.html` is final and `sync_attpreview_catalog.py` has run: mark office as not in the addons (`UPDATE ir_module_module SET state='uninstallable' WHERE name='dwo_attpreview_office'`, read on every load of Settings) and take 07 and 08 (`ENGINE_POPUP` chooses the engine).
5. Look at every picture, copy the chosen ones to `static/description/screenshots/` of the right module, run the sync script again, drop the database.
