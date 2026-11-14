# Changelog

## 16.0.2.1.2 - 2026-11-14

Security fix: the result zip no longer leaks the server's paths (GitHub issue #2).

- `protection-manifest.json` (written by jProtect) listed absolute server paths (job work dir under the Odoo data dir, including the OS user name). The add-on now rewrites it after protecting each module: `module_root` / `output_root` are the module's technical name, every file list is relative to the module folder, error reasons have server paths removed. The file stays in the zip with the same keys.
- The compiled `.so`/`.pyd` carried absolute build paths (job dir, temporary build dir) in their debug symbols, because Python builds extensions with `-g`. Extensions are now compiled with `-g0` (appended to `CFLAGS` only while a module is being protected).
- `__pycache__/`, `*.pyc`, `*.pyo`, `__MACOSX/` and `.DS_Store` of the uploaded zip are no longer copied to the result: they held the uploader's own build paths and stale bytecode of the unprotected source.
- No jProtect release needed (requirement unchanged). The same absolute paths still appear when using the jProtect CLI directly.
- Tests: `test_result_zip_does_not_leak_server_paths`, `test_result_manifest_uses_relative_paths`, `test_result_zip_strips_uploaded_bytecode` (red before the fix, green after).
- No new fields/models/views; no migration.
