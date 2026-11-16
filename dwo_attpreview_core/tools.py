# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
"""Helpers shared by engine modules (safe XML, zip limits, HTML escaping)."""
import html
import io
import zipfile

from lxml import etree

from odoo.exceptions import UserError

MAX_ZIP_ENTRIES = 5000
MAX_ZIP_UNCOMPRESSED = 200 * 1024 * 1024
MAX_ZIP_RATIO = 200


def esc(text):
    return html.escape(text if isinstance(text, str) else str(text or ""), quote=True)


def safe_xml(data):
    """Parse XML with entities, DTD loading and network disabled (XXE safe)."""
    parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False,
                             dtd_validation=False, huge_tree=False, remove_pis=True)
    try:
        return etree.fromstring(data, parser)
    except etree.XMLSyntaxError:
        raise UserError("The file is corrupted (invalid XML).")


def open_zip(content):
    """Open a zip file, refusing zip bombs (entry count, total size, ratio)."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile:
        raise UserError("The file is corrupted (not a valid zip).")
    infos = zf.infolist()
    total = sum(i.file_size for i in infos)
    packed = sum(i.compress_size for i in infos) or 1
    if len(infos) > MAX_ZIP_ENTRIES or total > MAX_ZIP_UNCOMPRESSED or (total / packed > MAX_ZIP_RATIO and total > 10 * 1024 * 1024):
        raise UserError("The archive looks unsafe (too large or too many entries).")
    return zf


def read_zip_member(zf, name, limit=20 * 1024 * 1024):
    try:
        info = zf.getinfo(name)
    except KeyError:
        return None
    if info.file_size > limit:
        raise UserError("An inner file is too large to preview.")
    return zf.read(info)


def table_html(rows, header=False, max_rows=2000, max_cols=100):
    out = ["<table border='1' cellspacing='0' cellpadding='3' style='border-collapse:collapse;font-family:sans-serif;font-size:13px'>"]
    for i, row in enumerate(rows[:max_rows]):
        tag = "th" if header and i == 0 else "td"
        out.append("<tr>" + "".join("<%s>%s</%s>" % (tag, esc(c), tag) for c in row[:max_cols]) + "</tr>")
    out.append("</table>")
    if len(rows) > max_rows:
        out.append("<p><i>Showing the first %d rows of %d.</i></p>" % (max_rows, len(rows)))
    return "".join(out)
