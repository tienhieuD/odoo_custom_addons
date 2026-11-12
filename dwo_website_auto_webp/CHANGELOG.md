# Changelog

## 16.0.1.0.1 - 2026-11-12

- Fix: saving the WebP cache (INSERT of the `webp_cache:...` `ir.attachment`) in `models/ir_binary.py` now runs in `with self.env.cr.savepoint():`. A real database error while saving the cache (constraint violation, overload...) no longer aborts the transaction of the request: the image is still served as WebP (HTTP 200) and later queries of the same request work. Other errors are still swallowed as before.
- Test: `test_cache_save_real_database_error_keeps_transaction_usable` (real failing INSERT, then `SELECT 1` must work). Without the savepoint this test fails. Total tests: 55.
- No model/field/view change, no migration.
- Note: 16 has no `readonly=True` on `/web/image` (added in 18), so no ReadOnlySqlTransaction handling is needed here. Same savepoint fix exists in 18 (18.0.1.0.1), 19 and 20.

## 16.0.1.0.0

- First version with automated tests (54).
