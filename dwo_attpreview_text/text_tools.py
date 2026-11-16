# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""Server side of the text engine, without Odoo models: kinds of files, encoding, XML tree, notebooks, HTML preview.

Everything that runs here is a reader: no file content is ever executed. Parsing that is free in the browser (JSON,
YAML, TOML, INI, logs, diffs, subtitles, PO) is done by the viewer; this module does what needs the server: decoding
the bytes, the XML tree (with the XXE-safe parser of the core), sanitizing HTML (Odoo's ``html_sanitize``) and
reading notebooks (their HTML outputs are sanitized here too).
"""
import base64
import codecs
import json
import re

from lxml import etree

# --- kinds of files ------------------------------------------------------------------------------------------------
# extension -> (group, highlight.js language). The group decides the views of the viewer (static/src/js/formats.js).
_GROUPS = {
    "markdown": ({"md": "markdown", "markdown": "markdown", "mdx": "markdown"}),
    "html": ({"html": "xml", "htm": "xml", "xhtml": "xml"}),
    "xml": {ext: "xml" for ext in ("xml", "xsd", "xsl", "xslt", "svg", "rss", "atom", "plist", "kml", "gpx", "wsdl",
                                   "xlf", "xliff", "resx")},
    "json": {ext: "json" for ext in ("json", "jsonc", "json5", "geojson", "webmanifest")},
    "ndjson": {"ndjson": "json", "jsonl": "json"},
    "notebook": {"ipynb": "json"},
    "yaml": {"yaml": "yaml", "yml": "yaml"},
    "toml": {"toml": "ini"},
    "ini": {"ini": "ini", "cfg": "ini", "conf": "ini", "env": "bash", "properties": "properties"},
    "code": {
        "py": "python", "pyi": "python", "js": "javascript", "mjs": "javascript", "cjs": "javascript",
        "jsx": "javascript", "ts": "typescript", "tsx": "typescript", "vue": "xml", "css": "css", "scss": "scss",
        "sass": "scss", "less": "css", "sql": "sql", "sh": "bash", "bash": "bash", "zsh": "bash", "ps1": "powershell",
        "bat": "dos", "cmd": "dos", "java": "java", "kt": "kotlin", "kts": "kotlin", "swift": "swift", "c": "c",
        "h": "c", "cpp": "cpp", "cc": "cpp", "cxx": "cpp", "hpp": "cpp", "hh": "cpp", "cs": "csharp", "go": "go",
        "rs": "rust", "php": "php", "rb": "ruby", "dart": "dart", "lua": "lua", "r": "r", "pl": "perl", "pm": "perl",
        "scala": "scala", "groovy": "groovy", "gradle": "gradle", "dockerfile": "dockerfile", "mk": "makefile",
        "makefile": "makefile", "tex": "latex",
    },
    "log": {"log": "", "out": "", "err": ""},
    "diff": {"diff": "diff", "patch": "diff"},
    "subtitles": {"srt": "", "vtt": ""},
    "po": {"po": "", "pot": ""},
    "text": {ext: "" for ext in ("txt", "text", "rst", "adoc", "asciidoc", "nfo")},
}
FORMATS = {ext: (group, lang) for group, exts in _GROUPS.items() for ext, lang in exts.items()}
EXTENSIONS = tuple(FORMATS)

MAX_TEXT_BYTES = 10 * 1024 * 1024  # bytes shown; a larger file is cut (the viewer says so)
MAX_HTML_PREVIEW = 5 * 1024 * 1024  # characters of HTML sanitized for the preview
MAX_XML_NODES = 200_000
MAX_VALUE = 300  # characters of an attribute value or a text shown in the XML tree
MAX_NOTEBOOK_PICTURES = 20 * 1024 * 1024  # bytes of pictures in the outputs of a notebook


class TextError(Exception):
    """A clean, user-facing refusal (the engine turns it into a ``UserError``)."""


def file_format(filename):
    """``(extension, group, highlight.js language)`` of a file name (``("", "text", "")`` when unknown)."""
    name = filename or ""
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    group, lang = FORMATS.get(ext, ("text", ""))
    return ext, group, lang


# --- encoding ------------------------------------------------------------------------------------------------------
_BOMS = (
    (codecs.BOM_UTF32_LE, "utf-32-le", "UTF-32 LE"),
    (codecs.BOM_UTF32_BE, "utf-32-be", "UTF-32 BE"),
    (codecs.BOM_UTF8, "utf-8", "UTF-8 (BOM)"),
    (codecs.BOM_UTF16_LE, "utf-16-le", "UTF-16 LE"),
    (codecs.BOM_UTF16_BE, "utf-16-be", "UTF-16 BE"),
)
_CONTROL_OK = {"\t", "\n", "\r", "\f", "\v", "\x1b", "\x00"}


def _utf16_without_bom(sample):
    """``"utf-16-le"`` / ``"utf-16-be"`` when NUL bytes sit on every other byte (Latin text in UTF-16), else ``None``."""
    sample = sample[: len(sample) - len(sample) % 2]
    if len(sample) < 4:
        return None
    even = sample[0::2].count(0) / (len(sample) / 2)
    odd = sample[1::2].count(0) / (len(sample) / 2)
    if odd > 0.4 and even < 0.05:
        return "utf-16-le"
    if even > 0.4 and odd < 0.05:
        return "utf-16-be"
    return None


def _guess_legacy(data):
    """Best guess for bytes that are not UTF-8: chardet, then charset_normalizer (when installed; chardet is better
    with short Western texts), else Windows-1252. ISO-8859-1 is read as Windows-1252, its superset (as browsers do)."""
    sample = data[:200_000]
    guess = None
    try:
        import chardet
        found = chardet.detect(sample) or {}
        if found.get("encoding") and (found.get("confidence") or 0) >= 0.5:
            guess = found["encoding"]
    except Exception:  # noqa: BLE001 - optional library: any failure means "no guess"
        pass
    if not guess:
        try:
            from charset_normalizer import from_bytes
            best = from_bytes(sample).best()
            guess = best.encoding if best else None
        except Exception:  # noqa: BLE001
            pass
    guess = guess or "cp1252"
    try:
        return "cp1252" if codecs.lookup(guess).name in ("latin-1", "iso8859-1", "ascii") else guess
    except LookupError:
        return "cp1252"


def _label(encoding):
    try:
        name = codecs.lookup(encoding).name
    except LookupError:
        name = encoding
    return {"cp1252": "Windows-1252", "utf-8": "UTF-8", "ascii": "ASCII", "latin-1": "ISO-8859-1",
            "iso8859-1": "ISO-8859-1"}.get(name, name.upper())


def decode_text(content, truncated=False):
    """Decode the bytes of a text file: ``(text, encoding label)``. BOM first (UTF-8/16/32), then UTF-16 without BOM,
    then strict UTF-8, then a guess (fallback Windows-1252). Raise ``TextError`` for binary data (a picture, a zip...
    with a text extension). ``truncated``: the bytes were cut, the last character may be incomplete."""
    for bom, encoding, label in _BOMS:
        if content.startswith(bom):
            return content[len(bom):].decode(encoding, "replace"), label
    head = content[:8192]
    if b"\x00" in head:
        encoding = _utf16_without_bom(head)
        if not encoding:
            raise TextError("binary")
        return content.decode(encoding, "replace"), _label(encoding).replace("UTF-16-", "UTF-16 ") + " (no BOM)"
    try:
        text, label = content.decode("utf-8"), "UTF-8"
    except UnicodeDecodeError as e:
        if truncated and e.start >= len(content) - 3:  # a character cut by the size limit
            text, label = content[: e.start].decode("utf-8"), "UTF-8"
        else:
            encoding = _guess_legacy(content)
            try:
                text, label = content.decode(encoding, "replace"), _label(encoding)
            except LookupError:
                text, label = content.decode("cp1252", "replace"), "Windows-1252"
    if label == "UTF-8" and text.isascii():
        label = "ASCII"
    sample = text[:8192]
    controls = sum(1 for ch in sample if (ch < " " and ch not in _CONTROL_OK) or ch == "\x7f")
    if sample and controls / len(sample) > 0.02:
        raise TextError("binary")
    return text, label


def line_endings(text):
    """``"LF"``, ``"CRLF"``, ``"CR"``, ``"mixed"`` or ``""`` (one line)."""
    crlf = text.count("\r\n")
    cr = text.count("\r") - crlf
    lf = text.count("\n") - crlf
    kinds = [name for name, count in (("CRLF", crlf), ("LF", lf), ("CR", cr)) if count]
    return kinds[0] if len(kinds) == 1 else ("mixed" if kinds else "")


# --- XML tree ------------------------------------------------------------------------------------------------------
def _short(value):
    value = " ".join((value or "").split())
    return value if len(value) <= MAX_VALUE else value[: MAX_VALUE - 1] + "…"


def _qname(name, nsmap):
    """``prefix:local`` for ``{uri}local`` (the prefix declared for the URI), else the local name."""
    if not name.startswith("{"):
        return name
    uri, local = name[1:].split("}", 1)
    for prefix, ns in (nsmap or {}).items():
        if ns == uri and prefix:
            return "%s:%s" % (prefix, local)
    return local


def xml_tree(root):
    """The elements of a parsed XML document as flat rows ``[parent, name, [[attr, value], ...], text, line]``
    (parent: index of the parent row, -1 for the root). Comments and processing instructions are skipped.
    At most ``MAX_XML_NODES`` rows; returns ``{"nodes": rows, "truncated": bool}``."""
    rows, index = [], {}
    truncated = False
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        if len(rows) >= MAX_XML_NODES:
            truncated = True
            break
        parent = el.getparent()
        while parent is not None and parent not in index:
            parent = parent.getparent()
        attrs = [[_qname(k, el.nsmap), _short(v)] for k, v in el.attrib.items()]
        index[el] = len(rows)
        rows.append([index.get(parent, -1), _qname(el.tag, el.nsmap), attrs, _short(el.text), el.sourceline or 0])
    return {"nodes": rows, "truncated": truncated}


# --- HTML preview --------------------------------------------------------------------------------------------------
# a light grey frame with a crossed picture: the place of a picture that is not loaded
BLOCKED_PICTURE = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='36' "
                   "viewBox='0 0 48 36'%3E%3Crect x='.5' y='.5' width='47' height='35' rx='3' fill='%23f3f4f6' "
                   "stroke='%23c4c8cf'/%3E%3Cpath d='M12 26l8-9 6 6 4-4 6 7z' fill='%23c4c8cf'/%3E%3Cpath d='M8 "
                   "6l32 24' stroke='%23c4c8cf' stroke-width='2'/%3E%3C/svg%3E")
_IMG = re.compile(r"<img\b[^>]*>", re.I)
_ATTR = r'\s%s\s*=\s*"([^"]*)"'
_SRC = re.compile(_ATTR % "src", re.I)
_ALT = re.compile(_ATTR % "alt", re.I)
# pages colour cells with bgcolor="" and "background: #fff" shorthands; html_sanitize keeps only background-color:
# turn them into it first (white text on a coloured header would become invisible otherwise). Same as the email engine.
_BACKGROUND = re.compile(r"(?<![-\w])background\s*:\s*([^;]+)", re.I)
_COLOR = re.compile(r"#[0-9a-f]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)|\b[a-z]{3,20}\b", re.I)
_NOT_COLORS = {"url", "none", "repeat", "no", "center", "top", "left", "right", "bottom", "fixed", "scroll",
               "inherit", "initial", "unset", "cover", "contain", "auto", "padding", "border", "content", "local",
               "space", "round", "box", "x", "y"}


def _background_color(match):
    for token in _COLOR.findall(re.sub(r"url\([^)]*\)", " ", match.group(1))):
        if token.split("(")[0].lower() not in _NOT_COLORS and not token.lower().startswith(("repeat", "no-")):
            return "background-color:%s" % token
    return ""


def _keep_backgrounds(html):
    """``bgcolor`` attributes and ``background`` shorthands -> ``background-color``."""
    from lxml import html as lxml_html
    try:
        doc = lxml_html.document_fromstring(html)
    except (etree.ParserError, ValueError):
        return html
    changed = False
    for el in doc.iter():
        if not isinstance(el.tag, str):
            continue
        style = el.get("style") or ""
        bgcolor = (el.attrib.pop("bgcolor", None) or "").strip()
        if bgcolor and _COLOR.fullmatch(bgcolor):
            style = "background-color:%s;%s" % (bgcolor, style)
        if "background" in style.lower():
            style = _BACKGROUND.sub(_background_color, style)
        if style != (el.get("style") or ""):
            el.set("style", style)
            changed = True
    return lxml_html.tostring(doc, encoding="unicode") if changed else html


def preview_html(html):
    """Odoo's ``html_sanitize`` (no script, event handler, form, unsafe style), then every picture that is not a
    ``data:`` URI is replaced by a small placeholder (its address in the tooltip): the preview frame loads nothing
    from the network. Returns ``(html, number of pictures not loaded)``."""
    from odoo.tools.mail import html_sanitize
    if not html.strip():
        return "", 0
    clean = str(html_sanitize(_keep_backgrounds(html), sanitize_attributes=True, sanitize_style=True,
                              sanitize_form=True, strip_classes=False) or "")
    blocked = 0

    def block(match):
        nonlocal blocked
        tag = match.group(0)
        src = _SRC.search(tag)
        if src and src.group(1).lower().startswith("data:image/"):
            return tag
        blocked += 1
        alt = _ALT.search(tag)
        return '<img src="%s" alt="%s" title="%s" width="48" height="36" data-dwo-blocked="1">' % (
            BLOCKED_PICTURE, alt.group(1) if alt else "", src.group(1) if src else "")

    return _IMG.sub(block, clean), blocked


def _clean(value):
    """JSON-safe text: lone surrogates (damaged UTF-16 escapes in a JSON file) and NUL characters replaced."""
    if isinstance(value, str):
        return value.encode("utf-8", "replace").decode("utf-8").replace("\x00", "")
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clean(v) for v in value]
    return value


# --- notebooks (.ipynb) --------------------------------------------------------------------------------------------
_ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
_PICTURES = ("image/png", "image/jpeg", "image/gif", "image/webp", "image/svg+xml")


def _joined(value):
    return "".join(value) if isinstance(value, list) else (value if isinstance(value, str) else "")


def notebook(text):
    """A Jupyter notebook (nbformat 4, and 3 for the cells) as ``{language, cells: [{type, source, count,
    outputs}]}``. Outputs: ``{"kind": "text"|"error"|"image"|"html"|"markdown", ...}``; HTML outputs are sanitized,
    pictures become ``data:`` URIs (SVG pictures are shown in an ``<img>``, where scripts never run), JavaScript
    outputs and widgets are left out. Raise ``ValueError`` when it is not a notebook."""
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("not a notebook")
    meta = data.get("metadata") or {}
    language = ((meta.get("language_info") or {}).get("name") or (meta.get("kernelspec") or {}).get("language")
                or "python")
    cells = data.get("cells")
    if cells is None:  # nbformat 3
        cells = [c for ws in data.get("worksheets") or [] for c in ws.get("cells") or []]
    if not isinstance(cells, list):
        raise ValueError("not a notebook")
    pictures = 0
    out_cells = []
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        kind = cell.get("cell_type") or "code"
        outputs = []
        for output in cell.get("outputs") or []:
            if not isinstance(output, dict):
                continue
            otype = output.get("output_type")
            if otype == "stream":
                outputs.append({"kind": "text", "text": _ANSI.sub("", _joined(output.get("text"))),
                                "stderr": output.get("name") == "stderr"})
            elif otype in ("error", "pyerr"):
                trace = "\n".join(output.get("traceback") or []) or "%s: %s" % (
                    output.get("ename", ""), output.get("evalue", ""))
                outputs.append({"kind": "error", "text": _ANSI.sub("", trace)})
            elif otype in ("execute_result", "display_data", "pyout"):
                bundle = output.get("data") or {}
                picture = next((m for m in _PICTURES if m in bundle), None)
                if picture:
                    raw = _joined(bundle[picture])
                    if picture == "image/svg+xml":
                        raw = base64.b64encode(raw.encode()).decode()
                    raw = "".join(raw.split())
                    pictures += len(raw) * 3 // 4
                    if pictures <= MAX_NOTEBOOK_PICTURES:
                        outputs.append({"kind": "image", "src": "data:%s;base64,%s" % (picture, raw)})
                        continue
                if "text/html" in bundle:
                    html, _blocked = preview_html(_joined(bundle["text/html"]))
                    outputs.append({"kind": "html", "html": html})
                elif "text/markdown" in bundle:
                    outputs.append({"kind": "markdown", "text": _joined(bundle["text/markdown"])})
                elif "text/plain" in bundle:
                    outputs.append({"kind": "text", "text": _ANSI.sub("", _joined(bundle["text/plain"]))})
        source = _joined(cell.get("source") if "source" in cell else cell.get("input"))
        if kind == "markdown" or kind == "raw":
            outputs = []
        out_cells.append({"type": kind if kind in ("code", "markdown", "raw") else "raw", "source": source,
                          "count": cell.get("execution_count", cell.get("prompt_number")), "outputs": outputs})
    return _clean({"language": str(language).lower(), "cells": out_cells})

