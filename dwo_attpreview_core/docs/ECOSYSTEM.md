# Adding a module to the Secure Attachment Preview family (checklist)

Family = `dwo_attpreview_core` + the engines of `data/engine_catalog.json` (+ `dwo_attpreview_webgl`, a shared base
with no card). Tools live in `odoo_appstore/_tools/`. Do these steps for every Odoo version 17-20 that has the module,
in the same change. Do NOT sync the Odoo Apps store from here (the user scans it).

1. **Module**: engine code, manifest (price, license), tests, `docs/CHANGELOG.md`, listing `_listings/<module>.json`
   (header `tagline` = the one line shown on the cards; optional top-level `eco_line` overrides it), `icon.png`.
2. **Catalog**: add the engine to `core/data/engine_catalog.json` (module, name, extensions, store_url), bump the core
   version and CHANGELOG, then `python3 sync_attpreview_catalog.py --addons odoo_custom_addonsNN` for each version
   (mirrors the engine listing into `core/static/catalog/`, test `test_catalog` fails until you do).
3. **Settings picture of the core**: `python3 shots_attpreview_settings.py` (all versions; `--versions 19` for one).
   It builds a clean temporary database per version with the core and ALL engines, English UI, shoots
   `static/description/screenshots/07-preview-engines.png` (engine tick boxes) and `07b-size-limits.png`, writes
   `docs/settings_screenshot.json` (engine count and names), drops the database and filestore. Look at the pictures.
   `check_attpreview_settings.py` (also run at the end of the catalog sync and of the ecosystem script) warns when the
   count in that file differs from the catalog.
4. **Ecosystem cards**: `python3 gen_attpreview_ecosystem.py`. It rewrites the `ecosystem` section of every family
   listing from the catalog and manifests (name, tagline, price or Free), copies the 128px icons to each module's
   `static/description/img/eco_<short>.png`, rebuilds every `index.html` per series (links
   `/apps/modules/<series>/<technical_name>`, relative only, never `https://apps.odoo.com/...`) and runs
   `validate_listing.py` (0 FAIL, 0 WARN from the cards; long engine names and the GPL-3 of DWG are older findings).
5. **Keywords**: add the module's search phrases to `_listings/keywords.json` and the manifest `summary`
   (`apply_keywords.py`), as for any listing.
6. **Versions**: patch-bump the modules whose description changed (manifest + CHANGELOG), all four versions; run the
   core tests on one version (19) as a smoke test; run the catalog sync again (the index.html files changed).
7. **duotek**: for every changed listing update `src/content/apps-en/<slug>.md` and `src/content/apps/<slug>.md`
   (keep `storeUrl`), the pictures in `src/assets/apps/<module>/`, the "More modules of the preview family" links to
   the other duotek pages (`/apps/<slug>/`, `/vi/apps/<slug>/`) for a new module on every page, then `pnpm build`.
8. **Commit and push** per repo (only the `dwo_attpreview_*` paths), then the user scans the store per series. Open
   one page after the scan and check that the card buttons keep their `/apps/modules/<series>/...` link.
