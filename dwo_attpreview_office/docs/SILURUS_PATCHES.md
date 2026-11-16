# Local patches to the bundled silurus build (technical note, not for customers)

`static/lib/silurus/` is **`@silurus/ooxml` 0.89.11 + local patches `0001`** (XLSX connectors/arrows) **and `0003`** (XLSX search highlight, see the section at the end) **+ `@silurus/ooxml-legacy-office` 0.89.11 with local patch `0002`** (old .doc/.xls/.ppt). It is NOT the stock npm build.

| Item | Value |
|---|---|
| Upstream | https://github.com/yukiyokotani/office-open-xml-viewer (MIT, see `static/lib/silurus/LICENSE`) |
| Base | tag `v0.89.11` |
| Patched build | base + `patches/silurus/0001-xlsx-render-cxnSp-connectors-with-line-ends.patch` |
| Marked as | fork `tienhieuD/office-open-xml-viewer`, branch `v0.89.11-xlsx-connectors`, tag `v0.89.11-xlsx-connectors.1` |
| Upstream issue / PR | issue #2240, PR #2243 (the PR carries the subset of the patch without the rotation part, rebased on `main`: `patches/silurus/upstream-pr-2243-for-main.patch`) |
| Files in `static/lib/silurus` | the subset used by `viewer.js` (xlsx/docx/pptx entries, workers, wasm, `assets/`), same selection as the stock build; `LICENSE` and `THIRD_PARTY_NOTICES.md` kept unchanged |

## What was wrong (0.89.11)
1. Rust parser `packages/xlsx/parser/src/drawing.rs`: the shape collector only handled `sp`, `pic`, `grpSp` ("Ignore `xdr:cxnSp` ... for this minimal pass"). Every connector (`straightConnector1`, `bentConnector2..5`, `curvedConnector2..5`) was dropped. Horizontal/vertical lines with `ext cx=0` or `cy=0` were also dropped.
2. Renderer `packages/xlsx/src/renderer.ts`: `headEnd`/`tailEnd` reached the stroke but nothing drew arrowheads (PPTX does it with `drawArrowHead` / `getConnectorAnchors` from `@silurus/ooxml-core`).
3. Connectors rotated 90/270 degrees in a stand-alone anchor were drawn in the un-rotated frame.

## What the patch does
- Parser: accepts `cxnSp` like `sp` (stand-alone and inside groups); allows one axis with ext = 0 for connectors.
- Renderer: for connector presets with head/tail ends, redraws a shortened path and draws the arrowhead through the core helpers (triangle, stealth, diamond, oval, arrow), same as PPTX.
- Renderer: swaps the frame width/height for stand-alone connectors rotated 90/270. **Not verified against a workbook saved by real Excel and not in the upstream PR.**
- Tests added: 3 Rust (`drawing.rs`, `connector_tests`) + 5 vitest (`packages/xlsx/src/connector-paint.test.ts`).

## Known limits
- `xdr:absoluteAnchor` is not read by the xlsx parser for any shape (connectors included).
- Non-connector shapes rotated 90/270 inside an anchor are still drawn in the un-rotated frame; double lines (`cmpd`) with arrowheads keep a single stroke; no arrowheads for `custGeom`.
- Verified on synthetic and generated sheets (flowchart, UML, bent/curved/dashed/flipped, all line ends); PPTX/DOCX output is pixel-identical before/after; 100k-row xlsx load time unchanged.

## When a new silurus version comes out
1. Check whether upstream fixed it (look for `cxnSp` handling in `packages/xlsx/parser/src/drawing.rs`, and issue #2240 / PR #2243). If yes: use the stock `dist` and delete this file, `patches/silurus/`, and the note in `README.md`.
2. If not, re-apply on the new tag:
   ```
   git clone https://github.com/yukiyokotani/office-open-xml-viewer && cd office-open-xml-viewer
   git checkout <new-tag>
   git apply --3way <module>/patches/silurus/0001-xlsx-render-cxnSp-connectors-with-line-ends.patch
   ```
   If it does not apply cleanly (the file `drawing.rs` and `renderer.ts` are the ones touched), port the idea by hand using the "What the patch does" list; the upstream-for-main patch is a good second reference.
3. Build (Rust + wasm-pack are needed; the repo CI uses wasm-pack 0.13.1, built here with Rust 1.100 stable, target `wasm32-unknown-unknown`):
   ```
   pnpm install --frozen-lockfile
   pnpm --filter @silurus/ooxml-docx wasm && pnpm --filter @silurus/ooxml-xlsx wasm && pnpm --filter @silurus/ooxml-pptx wasm
   vite build && node scripts/build-model-source-sidecars.mjs && node scripts/bundle-declarations.mjs   # -> dist/
   ```
4. Replace the content of `static/lib/silurus/` with the used subset of the new `dist` (do not merge with old files: chunk names contain hashes; do not forget `xlsx_parser_bg.wasm`, `docx_parser_bg.wasm`, `pptx_parser_bg.wasm`, and the `assets/` folder). Keep `LICENSE` and `THIRD_PARTY_NOTICES.md`. Update the version cell in `README.md`.
5. Smoke test: open a sheet with a flowchart (connectors with arrowheads) plus a docx and a pptx, then run the module tests. `dwo_attpreview_all_in_one` copies this folder (paused since 2026-11-15, kept in `_scratch/attpreview_backup/paused/`): when it comes back, rebuild it with `_tools/build_attpreview_bundles.py`.

The full investigation notes and the screenshots are kept outside the module (`_scratch/attpreview_samples/silurus_fix/`).

## Legacy add-on `@silurus/ooxml-legacy-office` 0.89.11 (doc, xls, ppt) and patch `0002`

Since 19.0.1.0.2 the viewer also opens the old binary formats with the optional add-on (MIT, same author and version as the main library; `static/lib/silurus/LICENSE.ooxml-legacy-office` and `THIRD_PARTY_NOTICES.ooxml-legacy-office.md` keep its licence and its Rust crate notices; the main `LICENSE` / `THIRD_PARTY_NOTICES.md` are unchanged).

| Item | Value |
|---|---|
| Package | `@silurus/ooxml-legacy-office@0.89.11` from npm (peer-pinned to `@silurus/ooxml` 0.89.11) |
| Files in `static/lib/silurus` | `doc.mjs`, `xls.mjs`, `ppt.mjs`, `legacy-source-Dds5PgNt.js` (shared chunk), `legacy-{doc,xls,ppt}-source-module.mjs` (loaded by the Worker), `legacy_{doc,xls,ppt}_direct_bg.wasm` (about 1.2 / 1.3 / 1.4 MB, loaded only when such a file is opened), `internal-companion.mjs` (copied unchanged from the stock `@silurus/ooxml@0.89.11` `dist`) |
| Patch | `patches/silurus/0002-legacy-addon-relative-companion-import.patch` (one string in `legacy-source-Dds5PgNt.js`) |

**What is patched.** The shared chunk imports the companion runtime by a bare specifier, `"@silurus/ooxml/internal/companion"`. A page without an import map cannot resolve it, and the viewer CSP has no `'unsafe-inline'` for scripts, so an inline import map is refused. The patch changes it to `"./internal-companion.mjs"`, a copy of the stock file that sits next to it (it imports `model-source-COXegBNA.js`, which the patched build already has; checked byte for byte equal to the stock one).

**Version check.** `internal-companion.mjs` compares two hard-coded strings (`"0.89.11"` and `"ooxml-model-source-module/v2"`) with what the add-on declares; it does not measure the viewer actually loaded. Patch `0001` keeps the same version and protocol, so the check passes. A future build with another protocol would NOT be detected: the module tests open one file of each old format.

**Upgrade rule: the add-on must be upgraded together with `@silurus/ooxml`** (same version number; the add-on refuses another one, and the chunk names carry hashes). To re-apply:
```
mkdir /tmp/legacy && cd /tmp/legacy && npm init -y && npm i --ignore-scripts @silurus/ooxml@<V> @silurus/ooxml-legacy-office@<V>
D=node_modules/@silurus/ooxml-legacy-office/dist ; L=<module>/static/lib/silurus
# remove the old add-on files first (doc.mjs xls.mjs ppt.mjs legacy-*.js legacy-*.mjs legacy_*_direct_bg.wasm internal-companion.mjs)
cp $D/{doc,xls,ppt}.mjs $D/legacy-source-*.js $D/legacy-*-source-module.mjs $D/legacy_*_direct_bg.wasm $L/
cp node_modules/@silurus/ooxml/dist/internal-companion.mjs $L/
cp node_modules/@silurus/ooxml-legacy-office/LICENSE $L/LICENSE.ooxml-legacy-office
cp node_modules/@silurus/ooxml-legacy-office/THIRD_PARTY_NOTICES.md $L/THIRD_PARTY_NOTICES.ooxml-legacy-office.md
cd $L && patch -p1 < <module>/patches/silurus/0002-legacy-addon-relative-companion-import.patch
```
If the patch does not apply (the chunk file name or the import line changed), do by hand: in the shared chunk, replace the bare `"@silurus/ooxml/internal/companion"` with `"./internal-companion.mjs"` and regenerate the patch with `diff -u`. Then check `grep -rn "@silurus/" doc.mjs xls.mjs ppt.mjs legacy-*` finds no import, update the chunk name in `tests/test_engine.py` (`test_03_asset_route...`), and run the tests (one real .xls, .ppt, .doc, and a .doc the add-on refuses).

**Viewer options** (`static/viewer/viewer.js`): `createLegacyDoc/Xls/Ppt({ maxInputBytes })` (128 MiB; the add-on has no ceiling of its own) passed as `legacyDoc` to `DocxScrollViewer`, `legacyXls` to `XlsxViewer`, `legacyPpt` to `PptxViewer`. The add-on recognises the file by content (CFB signature and stream names), not by extension. Its error codes (`unsupported-content`, `legacy-binary-format`, `unsupported-encryption`, `encrypted`, `not-ooxml`, `ooxml-resource-limit`, `parser-crashed`...) are only logged in the browser console; the user sees "This legacy file cannot be previewed." and a Download button.

Test results of the add-on on about 130 Apache POI files (kept outside the module, `_scratch/attpreview_samples/legacy_office/NOTES.md`): about 70% of .xls and .ppt, about 40% of .doc open; no crash or hang on 180 mutated files. A single unsupported structure makes the add-on refuse the whole document (hyperlinks, merged table cells, footnotes, most embedded pictures in .doc).

## Patch `0003`: XLSX search highlight (#71)

| Item | Value |
|---|---|
| File | `static/lib/silurus/xlsx-BGxOngVB.js` (built output, no source rebuild needed), `updateOverlay()` of the XLSX find overlay |
| Patch | `patches/silurus/0003-xlsx-find-overlay-visible-matches-only.patch` |
| Upstream | not reported yet (to do together with the connector PR) |

**What was wrong.** After `findText()`, each match of the current sheet got its own absolutely positioned `<div>`, appended one by one, while `cellRect()` reads the layout (`canvasArea.clientWidth`) for every match: the layout is recomputed after each append, so the time grows with the square of the match count. Measured on a 100,000-row sheet: 11,112 matches took 70 s for `findText` and 37 s more for `findNext`; 100,000 matches never finished. The overlay is also rebuilt on every scroll.

**What the patch does.** Skips the matches outside the visible area (no box; the cell is not drawn anyway) and appends the boxes through a single `DocumentFragment`. Search results, counts and navigation are unchanged. After the patch: 11,112 matches 1.1 s, 100,000 matches 1.0 s (tour `find_xlsx_big`).

**On upgrade.** Check whether `updateOverlay()` still appends per match (search for `appendFind(` in the xlsx chunk). If yes, re-apply: `cd static/lib/silurus && patch -p1 < <module>/patches/silurus/0003-*.patch`; the chunk name carries a hash, so on a new build edit by hand (same two changes) and regenerate the patch with `diff -u`. Run the tour `dwo_attpreview_office_tour_find_xlsx_big`.
