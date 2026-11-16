# CHANGELOG - dwo_attpreview_archive

## 2026-11-16 - 17.0.1.0.0 - 17.0 port of 19.0.1.0.0 (via 18.0.1.0.0) (#82)

- Same features and behaviour as 19.0.1.0.0, engine of Secure Attachment Preview core 17.0.1.2.0; the entries below are
  the history of the 18.0 and 19.0 series.
- Odoo 17 differences: `models/engine.py` uses `_()` (no `self.env._` on 17); the tour is added through
  `dwoAddTour` (core `static/tests/tours/tour_compat.js`) and types with `run: "text ..."` (18/19: `"edit ..."`);
  the tour test opens `/web#id=..&model=res.partner&view_type=form` with `browser_size = "1366,768"`.
- Parsers, `thirdparty/rarfile`, `static/lib/tree_libs` and the OWL viewer are unchanged (see
  `dwo_attpreview_core/docs/PORTING.md`, section "18.0 -> 17.0 (#82)").

## 2026-11-16 - 18.0.1.0.0 - 18.0 port of 19.0.1.0.0 (#82)

- Same features and behaviour as 19.0.1.0.0 (entry below), engine of Secure Attachment Preview core 18.0.1.2.0.
- Odoo 18 difference: the tour `dwo_attpreview_archive_tour` clicks the chatter card `.o-mail-AttachmentCard`
  (19: `.o-mail-AttachmentContainer`). Parsers, `thirdparty/rarfile`, `static/lib/tree_libs` and the OWL viewer are
  unchanged (see `dwo_attpreview_core/docs/PORTING.md`, section "19.0 -> 18.0 (#82)").

## 2026-11-16 - 19.0.1.0.0 - first version (#82)

**Secure Archive Preview: ZIP, RAR, 7Z, TAR** (OPL-1, 25 EUR). Engine of Secure Attachment Preview (core 19.0.1.2.0).

**Reading (server, `parsers/__init__.py`, no Odoo code):** the format is found by the first bytes (a `.tar.gz` arrives
with the extension `gz`):
- zip (`zipfile`): names stored as UTF-8 without the UTF-8 flag are read as UTF-8 (else kept as cp437); folders that
  have no entry of their own are made from the paths; `..` and absolute paths are only names.
- tar, tar.gz, tar.bz2, tar.xz, and a single compressed file (`.gz`, `.bz2`, `.xz`) (`tarfile`, `gzip`, `bz2`, `lzma`),
  read as a stream that stops at 512 MB decompressed (bombs); links and devices are marked, they have no content.
- rar: `rarfile` 4.5 shipped in `thirdparty/rarfile` (ISC, unmodified): always listed; a compressed member needs
  unrar/unar/7z/bsdtar on the server, else a message says to install unrar (banner in the viewer + message on open).
- 7z: `py7zr` when installed (optional, never in the manifest; `extract(factory=BytesIOFactory(limit))`); without it,
  a message says `pip install py7zr`.
- At most 100 000 entries listed (`truncated`); password protected files are marked and never opened.

**Files inside:** `_dwo_extract_part` returns file number N of the listing (decompressed in memory, at most
max(preview limit, 100 MB), zip ratio check); the Core opens it in a second dialog with the engines installed, or
downloads it; a zip in a zip (or a zip in an email) opens level after level.

**Viewer:** folder tree drawn with OWL (`static/src/js/tree_view.js`, `DwoTreeView`), tree logic by Headless Tree 1.8.0 and
virtual scrolling by TanStack Virtual 3.19.11 (both MIT, one bundle `static/lib/tree_libs`, see BUILD.md): only the
visible rows are in the page; keyboard (arrows, Home, End, Enter); folders first, natural order; size, date and a file
count per folder; filter by name (matches and their folders, opened); expand all up to 3 000 folders; Download per file.
The data (100 000 rows) stays outside OWL reactivity; the tree is rebuilt before a render, never during one.

**Tests:** `tests/test_archive.py` (zip tree, extraction by position, nested zip, UTF-8 names without the flag, tar
family and single gz, bombs and limits, garbage, rar samples incl. password and Unicode, 7z without py7zr, a 12 000 file
zip through `/part_info` (index above 10 000), a zip inside an email) and the tour `dwo_attpreview_archive_tour` (a
zip of 20 002 files: fewer than 120 rows in the page, End reaches the last row, filter, zip in a zip, a picture inside).
