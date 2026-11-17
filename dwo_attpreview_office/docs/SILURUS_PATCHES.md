# Bundled silurus build and its local patches (technical note, not for customers)

`static/lib/silurus/` holds the **stock npm builds** of three packages of the same author and the same version, plus
**two small edits of the built JavaScript** (no source rebuild, no Rust toolchain needed):

| Package (npm, MIT) | Version | Used for | Local patch |
|---|---|---|---|
| `@silurus/ooxml` | 0.90.1 | docx, xlsx, pptx (and their variants), csv, tsv | `0003` (xlsx search highlight speed) |
| `@silurus/ooxml-legacy-office` | 0.90.1 | doc, xls, ppt (optional add-on) | `0002` (relative import) |
| `@silurus/ooxml-opendocument` | 0.90.1 | odt, ods, odp and ott, ots, otp (optional add-on, since 19.0.1.1.0, #84) | `0002` (relative import) |

| Item | Value |
|---|---|
| Upstream | https://github.com/yukiyokotani/office-open-xml-viewer, tag `v0.90.1` |
| Licences | `LICENSE` (main library), `LICENSE.ooxml-legacy-office`, `LICENSE.ooxml-opendocument`; Rust crate notices in `THIRD_PARTY_NOTICES.md`, `THIRD_PARTY_NOTICES.ooxml-legacy-office.md`, `THIRD_PARTY_NOTICES.ooxml-opendocument.md` (all copied unchanged from the 0.90.1 packages; not served by the asset route) |
| Patches | `patches/silurus/0002-addons-relative-companion-import.patch`, `patches/silurus/0003-xlsx-find-overlay-visible-matches-only.patch` |
| Files | only the files reachable from the entries the viewer imports (see "Upgrade" step 3): 153 files (plus the 6 licence/notice files), about 25 MB (the wasm parsers are loaded only when a file of their type is opened) |

## History
- **0.89.11 + patch `0001`** (until 19.0.1.0.2): the xlsx parser dropped connector shapes (`xdr:cxnSp`) and the renderer drew no arrowheads. Fixed by a local source patch (Rust + TypeScript, rebuilt dist), reported upstream as issue #2240 / PR #2243.
- **0.90.0** (19.0.1.1.0, #84): PR #2243 is merged upstream ("Excel: connectors and arrow heads", release notes of v0.90.0). Patch `0001`, its upstream-for-main copy and the custom build are gone: the main library is the stock npm `dist` again. Checked on `japan-labour-market-2024.xlsx`, sheet "Hiring Flow" (connectors, elbow lines and arrowheads drawn). The rotation part of the old patch (connectors rotated 90/270 in a stand-alone anchor) was never upstream; it was not verified against real Excel files either.
- 0.90.0 deprecates `useGoogleFonts`: any value, even `false`, logs a warning. The viewer no longer passes it; without a `fonts` source the library requests no web font.

- **0.90.1** (19.0.1.1.1, #94): compatible patch release (Word: a table without rows no longer fails with "Document page budget exceeded"; page/column breaks in header, footer, footnote, endnote no longer give "Unsupported story block"; a relative `wasmUrl` resolves against `document.baseURI`). Patches `0002` and `0003` re-applied by hand on the new hashed chunks (`legacy-source-DmlTJjiH.js`, `odf-source-Cee46vyi.js`, `xlsx-CW8XwM_M.js`); the code around both is unchanged, so the patch bodies are the same. The stock `internal-companion.mjs` already carries `"0.90.1"`. No new bare import, no CSP change; the selection walk gives the same 153 files as for 0.90.0 (only hashes changed).

## Patch `0002`: relative import of the companion runtime (legacy and OpenDocument add-ons)

| Item | Value |
|---|---|
| Files | `legacy-source-DmlTJjiH.js` (legacy add-on), `odf-source-Cee46vyi.js` (OpenDocument add-on): one string each |
| Next to them | `internal-companion.mjs`, copied unchanged from the stock `@silurus/ooxml@0.90.1` `dist` (it imports `model-source-BwpDCGYU.js` of the same build) |

**What is patched.** Both add-ons import the companion runtime by a bare specifier, `"@silurus/ooxml/internal/companion"`. A page without an import map cannot resolve it, and the viewer CSP has no `'unsafe-inline'` for scripts, so an inline import map is refused. The patch changes it to `"./internal-companion.mjs"`.

**Version check.** `internal-companion.mjs` compares two hard-coded strings (`"0.90.1"` and `"ooxml-model-source-module/v2"`) with what the add-on declares; it does not measure the viewer actually loaded. A mismatched pair fails with `companion-runtime-mismatch`. **The add-ons must be upgraded together with `@silurus/ooxml`** (same version number; the chunk names carry hashes).

**Other `@silurus/` strings.** `source-*.js` of the main library contains `Symbol.for("@silurus/ooxml/font-source")` and `Symbol.for("@silurus/ooxml/font-resolver-ids")`: these are symbol names, not imports; nothing to patch.

## Patch `0003`: XLSX search highlight (#71)

| Item | Value |
|---|---|
| File | `xlsx-CW8XwM_M.js` (built output), `updateOverlay()` of the XLSX find overlay |
| Upstream | not reported yet |

**What was wrong.** After `findText()`, each match of the current sheet got its own absolutely positioned `<div>`, appended one by one, while `cellRect()` reads the layout (`canvasArea.clientWidth`) for every match: the layout is recomputed after each append, so the time grows with the square of the match count. Measured on 0.89.11 with a 100,000-row sheet: 11,112 matches took 70 s for `findText` and 37 s more for `findNext`; 100,000 matches never finished. The code is the same in 0.90.0.

**What the patch does.** Skips the matches outside the visible area (no box; the cell is not drawn anyway) and appends the boxes through a single `DocumentFragment`. Search results, counts and navigation are unchanged. The new local names start with `dwo` (`dwoW`, `dwoH`, `dwoFrag`): a one-letter name could shadow a minified helper of the chunk (in 0.90.0 the frozen-pane helper is called `F`, the name the 0.89.11 patch used for the fragment, which would have thrown a ReferenceError). Tour `dwo_attpreview_office_tour_find_xlsx_big` (100,000 matches) must pass.

The viewer CSS keeps `#stage.xlsx canvas { margin: 0 }` (#76): the highlight boxes are placed in the same box as the canvas.

## OpenDocument add-on (#84)

- The viewer imports `odt.mjs` / `ods.mjs` / `odp.mjs` only when such a file is opened and passes `createOdt()` as the `odt` option of `DocxScrollViewer`, `createOds()` as `ods` of `XlsxViewer`, `createOdp()` as `odp` of `PptxViewer`. The factories take only `{ moduleUrl, wasmUrl }`; the defaults point next to the module (the asset route of this module), so no argument is passed.
- When a file is opened, the parser Worker (a `data:` Worker, see `viewer.js`) imports `<kind>-source-module.mjs` and its wasm (`opendocument_<kind>_bg.wasm`, 1.2 to 1.5 MB) from the asset route.
- The reader claims a package only by its `mimetype` file (the document or the template media type of its family). The server checks the same before the dialog opens (`models/engine.py`, `_dwo_check_opendocument`) and sends `odt`/`ods`/`odp` also for `ott`/`ots`/`otp`.
- The reader rejects corrupt, encrypted (`unsupported-encryption`) and over-limit packages; it never runs scripts, macros or forms and never fetches external resources. The user then gets "This file cannot be previewed." and a Download button (the code is only in the console). No "limited support" banner (user decision, #84), although upstream calls the package experimental.
- Upstream documentation: `docs/opendocument.md` of the repository (what is rendered, known differences from LibreOffice).

## Upgrade to a newer silurus version
1. Read the release notes (`gh release view <tag> -R yukiyokotani/office-open-xml-viewer`): breaking options, CSP needs, new bare imports.
2. Download the three packages at the same version into a scratch folder, never inside the module:
   ```
   mkdir /tmp/silurus && cd /tmp/silurus && npm init -y
   npm i --ignore-scripts @silurus/ooxml@<V> @silurus/ooxml-legacy-office@<V> @silurus/ooxml-opendocument@<V>
   ```
3. Merge the three `dist` folders (without `types/`) into one staging folder. Apply `0002` and `0003` there (`patch -p1 < ...`); the chunk names carry hashes, so on a new build edit by hand (`0002`: replace the bare companion import in each add-on chunk; `0003`: the two changes in `updateOverlay()`, search for `appendFind(` in the xlsx chunk) and regenerate the patches with `diff -u` against the stock files. Then keep only the files reachable from the entries the viewer uses: `xlsx.mjs docx.mjs pptx.mjs doc.mjs xls.mjs ppt.mjs odt.mjs ods.mjs odp.mjs` and the add-on `*-source-module.mjs`, following static and dynamic imports and `new URL("...", import.meta.url)` references (wasm files and `assets/render-worker-*.js` included), plus `internal-companion.mjs`. The script used for 0.90.0 and 0.90.1 is a 30-line regex walk over every quoted `*.js`/`*.mjs`/`*.wasm` name (a plain `import`/`new URL` regex misses the wasm files, which are named in a helper call); on 0.89.11 it gave exactly the shipped file list.
4. Replace the whole content of `static/lib/silurus/` with that selection (do not merge with old files). Copy the three `LICENSE` and `THIRD_PARTY_NOTICES.md` files under the names above. Update `README.md` and this file.
5. Check: `grep -l '"@silurus/' static/lib/silurus/*.js static/lib/silurus/*.mjs` lists no import; update the chunk names in `tests/test_engine.py` (`test_03_asset_route...`); run the module tests and look in the Odoo log for a 404 on `/dwo_attpreview_office/asset/` (a chunk the selection missed). Open by hand a flowchart xlsx, a docx, a pptx, one old doc/xls/ppt and one odt/ods/odp.
6. `dwo_attpreview_all_in_one` copies this folder (paused since 2026-11-15, kept in `_scratch/attpreview_backup/paused/`): when it comes back, rebuild it with `_tools/build_attpreview_bundles.py`.

## Legacy add-on notes (doc, xls, ppt)

**Viewer options** (`static/viewer/viewer.js`): `createLegacyDoc/Xls/Ppt({ maxInputBytes })` (128 MiB; the add-on has no ceiling of its own) passed as `legacyDoc` to `DocxScrollViewer`, `legacyXls` to `XlsxViewer`, `legacyPpt` to `PptxViewer`. The add-on recognises the file by content (CFB signature and stream names), not by extension. Its error codes (`unsupported-content`, `legacy-binary-format`, `unsupported-encryption`, `encrypted`, `not-ooxml`, `ooxml-resource-limit`, `parser-crashed`...) are only logged in the browser console; the user sees "This legacy file cannot be previewed." and a Download button.

Test results of the add-on (0.89.11) on about 130 Apache POI files (kept outside the module, `_scratch/attpreview_samples/legacy_office/NOTES.md`): about 70% of .xls and .ppt, about 40% of .doc open; no crash or hang on 180 mutated files. A single unsupported structure makes the add-on refuse the whole document (hyperlinks, merged table cells, footnotes, most embedded pictures in .doc). Not measured again on 0.90.0 (the module samples open the same).
