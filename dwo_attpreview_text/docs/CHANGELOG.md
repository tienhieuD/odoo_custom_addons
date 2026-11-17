# CHANGELOG - dwo_attpreview_text

## 2026-11-17 - 20.0.1.1.0 - Web pictures through the server, link confirmation (#87)

**Added:** Markdown, HTML and notebook previews show the pictures they link from the internet: the Odoo server downloads
them (https only by default, real pictures only, re-encoded; an address ending like a program or script is refused) and
the viewer shows them; one that cannot be shown gets a red error with the reason. Settings > Attachment Preview >
"Text and code pictures": "Load web pictures through the server" and "Only secure (HTTPS) pictures", both on by default
(`dwo_attpreview_text.remote_images` / `.remote_https_only`). Off: pictures stay blocked, with a button per file.
Route `/dwo_attpreview_text/remote_image` (auth user): the file is access-checked like the preview and `url` must be an
address written in that file, so it cannot fetch any other address. A click on a link opens a confirmation dialog with
the full address, then a new tab (`noopener,noreferrer`).

- Same frame as the Mail preview: one script by nonce, no `allow-popups`. Engine version 2 (HTML result has
  `remote_urls`, pictures are markers).

## 2026-11-17 - 20.0.1.0.0 - 20.0 port of 19.0.1.0.0 (#83)

Same features and behaviour as 19.0.1.0.0 (below), for core 20.0.1.3.0. Odoo 20 differences: Owl 3 components
(`useProps()`, `static dwoAttPreviewProps` incl. `source` and `fileUrl`, `proxy`, `signal.ref()`, `useListener`),
templates with `this.` and `t-out`, `oi` icons; the chatter patch reads `attachmentGroups`. See
`dwo_attpreview_core/docs/PORTING.md` (section "#83").

## 2026-11-16 - 19.0.1.0.0 - first version (#83)

**Secure Text & Code Preview: MD, HTML, XML, JSON, YAML, LOG** (OPL-1, 15 EUR). Engine of Secure Attachment Preview
(core 19.0.1.3.0). Engine code `text`, priority 200 (a generic reader: an engine made for an extension wins, e.g. office
for csv), result type `json` with its own viewer, dialog width `wide`, the size limit of the core; the text shown is
cut at 10 MB.

**Views** (bar at the top, only the views that make sense; the first one opens):

| Group | Extensions | Preview | Structure |
|---|---|---|---|
| Markdown | md, markdown, mdx | rendered, table of contents | outline of the headings (opens the line in Raw) |
| HTML | html, htm, xhtml | sanitized page | tree of elements (DOMParser, inert) |
| XML | xml, xsd, xsl, xslt, svg, rss, atom, plist, kml, gpx, wsdl, xlf, xliff, resx | svg: picture (`<img>`) | tree of elements, attributes, text, line (server) |
| JSON | json, jsonc, json5, geojson, webmanifest; ndjson, jsonl; ipynb | ipynb: notebook | tree with types, counts and path `$.a[0].b` |
| Config | yaml, yml, toml, ini, cfg, conf, env, properties | | tree |
| Code | py, js, ts, css, scss, sql, sh, java, c, cpp, cs, go, rs, php, rb, kt, swift, dart, lua, r, pl, ... | | |
| Log | log, out, err | lines coloured by level, filter by level | |
| Diff | diff, patch | two columns | files changed (+/-) |
| Subtitles | srt, vtt | table of cues | |
| PO | po, pot | table, filter untranslated / fuzzy / translated | |
| Text | txt, text, rst, adoc, asciidoc, nfo | | |

**Raw** (all files): virtual list of lines with numbers (TanStack Virtual of the core), syntax colours with
highlight.js up to 1.5 MB / 40 000 lines (computed once after the first paint, cut into lines with the spans that
cross lines closed and opened again), wrap toggle (wrapped rows are measured), find (Ctrl+F, Enter / Shift+Enter, the
marks keep the colours), go to line (Ctrl+G), copy the whole text. Log and table views are virtual too.

**Server** (`text_tools.py`): encoding: BOM (UTF-8/16/32), UTF-16 without BOM (NUL bytes every other byte), strict
UTF-8, else chardet / charset_normalizer, fallback Windows-1252; binary content (NUL bytes, control characters)
refused with a short message (toast). Line endings (LF/CRLF/CR/mixed). XML tree with `safe_xml` of the core (no
entities, no DTD, no network; at most 200 000 elements). HTML: `html_sanitize` (background shorthands kept as
colours first), every picture that is not a `data:` URI replaced by a small placeholder (address in its tooltip) and
counted. Notebooks: cells, outputs (text, errors without colour codes, pictures as `data:` URIs, HTML sanitized,
JavaScript and widgets left out), lone surrogates replaced.

**Safety:** Markdown (markdown-it, raw HTML off, links checked, outside links in a new tab, pictures that are not
`data:` replaced), HTML and notebooks are shown in an iframe `sandbox="allow-popups allow-popups-to-escape-sandbox"`
(no script, no same origin) with the CSP `default-src 'none'; img-src data:; style-src 'unsafe-inline'; font-src data:`:
nothing is loaded from the network; a note says how many pictures were not loaded. An SVG is shown in an `<img>`.

**Chatter:** text files that Odoo shows itself as bare text (text/plain, html, json, css, js: `isText`) open in the
preview dialog (patch of `AttachmentList.onClickAttachment`).

**Tests:** `tests/test_text.py`: extensions, result, encodings (UTF-8, BOM, UTF-16/32, UTF-16 without BOM,
Windows-1252), binary refused (also through `/info`), cut at 10 MB, HTML sanitized (script, events, javascript:,
iframe, form, remote pictures), XML tree, XXE and entity bomb, 200 000+ elements, notebooks, controller. Tours:
Markdown / HTML / SVG payloads (sandbox, CSP, nothing runs), JSON of about 120 000 values (only visible rows, End,
filter, path, go to line), log of 200 000 lines (levels, filter, Ctrl+F, wrap, go to line), diff / PO / SRT / YAML /
UTF-16.
