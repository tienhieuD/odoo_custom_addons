# Changelog

## 15.0.1.0.1 - 2026-11-12

- Fix: saving the WebP cache (INSERT of the `webp_cache:...` `ir.attachment`) in the helper `dwo.webp.helper._webp_process_response` (called by the `WebpBinary` controller) now runs in `with self.env.cr.savepoint():`. A real database error while saving the cache (constraint violation, overload...) no longer aborts the transaction of the request: the image is still served as WebP (HTTP 200) and later queries of the same request work. Other errors are still swallowed as before.
- Test: `test_cache_save_real_database_error_keeps_transaction_usable` (real failing INSERT, then `SELECT 1` must work). Without the savepoint this test fails. Total tests: 56.
- No model/field/view change, no migration.
- Note: 15 has no `ir.binary` override (the logic lives in the helper) and no `readonly=True` on `/web/image`, so no ReadOnlySqlTransaction handling is needed here.

## 15.0.1.0.0

- First version with automated tests (55).
