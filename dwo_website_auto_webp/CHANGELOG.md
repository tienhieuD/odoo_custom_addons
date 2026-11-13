# Changelog

## 15.0.1.0.2 - 2026-11-13

- Fix: the installation-guide tab links in `views/website_config_views.xml` (`data-toggle="tab"`) now have `aria-controls` pointing to their tab pane, and the `role="presentation"` on their `<li>` is removed (Odoo rejects it). Odoo 15 logged two aria warnings for the view `res.config.settings.view.form.auto.webp` at every module load; they are gone. Markup/accessibility only, no visible or behavioural change.
- No model/field change, no migration. Tests unchanged (56).

## 15.0.1.0.1 - 2026-11-12

- Fix: saving the WebP cache (INSERT of the `webp_cache:...` `ir.attachment`) in the helper `dwo.webp.helper._webp_process_response` (called by the `WebpBinary` controller) now runs in `with self.env.cr.savepoint():`. A real database error while saving the cache (constraint violation, overload...) no longer aborts the transaction of the request: the image is still served as WebP (HTTP 200) and later queries of the same request work. Other errors are still swallowed as before.
- Test: `test_cache_save_real_database_error_keeps_transaction_usable` (real failing INSERT, then `SELECT 1` must work). Without the savepoint this test fails. Total tests: 56.
- No model/field/view change, no migration.
- Note: 15 has no `ir.binary` override (the logic lives in the helper) and no `readonly=True` on `/web/image`, so no ReadOnlySqlTransaction handling is needed here.

## 15.0.1.0.0

- First version with automated tests (55).
