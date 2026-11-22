# -*- coding: utf-8 -*-
"""Creates the records of the Attachment Preview Lab: one per preview module, each with its sample files in every
kind of file field (binary, many2one, many2many, one2many lines) and in the chatter.

Every sample is English (see tools/make_samples.py for how the files were built)."""
import base64
import json
import struct
import zlib

from odoo.tools import file_open

# (record name, module, what to try, [file in static/samples], None = the text files made below)
LAB = [
    ("Core: PDF, images, video, audio", "dwo_attpreview_core",
     "PDF and images open in a large dialog. Add a video or an audio file of your own to try them too.",
     ["sample.pdf", "sample.png"]),
    ("Text and code", "dwo_attpreview_text",
     "Raw text with colours, Markdown, JSON, XML and YAML trees, logs and diffs.", None),
    ("Office documents", "dwo_attpreview_office",
     "Word, Excel, PowerPoint, OpenDocument and CSV: click a file to preview it.", [
         "sample.docx", "long.docx", "sample.xlsx", "sample.pptx", "sample.odt", "sample.ods", "sample.odp",
         "sample.csv", "sample_semicolon.csv", "sample.tsv"]),
    ("Archives", "dwo_attpreview_archive",
     "ZIP, TAR.GZ and 7Z archives: browse the folder tree and open the files inside.",
     ["project.zip", "project.tar.gz", "project.7z"]),
    ("Emails", "dwo_attpreview_mail",
     "EML emails with attachments, even an email inside an email.", ["quarterly-report.eml", "meeting.eml"]),
    ("3D models", "dwo_attpreview_3d",
     "STL, OBJ, GLB, 3MF, PLY, FBX, DAE, STEP and IGES: rotate, zoom, wireframe.", [
         "spur-gear.stl", "spur-gear.glb", "spur-gear.obj", "spur-gear.3mf", "spur-gear.ply", "spur-gear.fbx",
         "spur-gear.dae", "rounded-cube.step", "cube-10x10.igs"]),
    ("CAD drawings", "dwo_attpreview_cad", "A DXF floor plan: pan, zoom, switch layers.", ["floor-plan.dxf"]),
    ("BIM models", "dwo_attpreview_bim", "An IFC building model: rotate, zoom, pick an element.",
     ["office-building.ifc"]),
]


def _read(name):
    """A sample file shipped with this module (English content only, see tools/make_samples.py)."""
    with file_open("demo_dwo_attpreview/static/samples/%s" % name, "rb") as handle:
        return handle.read()


def _text_files():
    data = {"name": "Demo", "items": [{"id": 1, "tags": ["a", "b"]}, {"id": 2, "tags": []}], "ok": True}
    return [
        ("README.md", b"# Project notes\n\nThis is **Markdown**, rendered by the text preview.\n\n"
                      b"- First item\n- Second item\n\n```python\nprint('hello')\n```\n"),
        ("data.json", json.dumps(data, indent=2).encode()),
        ("config.xml", b"<?xml version='1.0'?>\n<config>\n  <server host='localhost' port='8069'/>\n"
                       b"  <modules><module name='base'/><module name='mail'/></modules>\n</config>\n"),
        ("settings.yaml", b"server:\n  host: localhost\n  port: 8069\nmodules:\n  - base\n  - mail\n"),
        ("script.py", b"def total(lines):\n    \"\"\"Sum the amounts.\"\"\"\n    return sum(l['amount'] for l in lines)\n"),
        ("page.html", b"<h1>Hello</h1><p>A <b>simple</b> page.</p>"),
        ("server.log", b"2026-11-21 08:00:01 INFO  started\n2026-11-21 08:00:05 WARN  slow query (1.2 s)\n"
                       b"2026-11-21 08:00:09 ERROR connection reset by peer\n"),
        ("change.diff", b"--- a/app.py\n+++ b/app.py\n@@ -1,3 +1,3 @@\n def run():\n-    return 1\n+    return 2\n"),
    ]


def _png():
    """A small PNG made on the fly (a gradient), so no binary image is stored in the repository."""
    width, height = 320, 200
    rows = b"".join(b"\x00" + b"".join(bytes((x * 255 // width, y * 255 // height, 160)) for x in range(width))
                    for y in range(height))

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


def _pdf():
    """A one-page PDF with a line of text."""
    stream = b"BT /F1 18 Tf 20 70 Td (Sample PDF for the preview) Tj ET"
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out, offsets = b"%PDF-1.4\n", []
    for number, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n%s\nendobj\n" % (number, body)
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    out += b"".join(b"%010d 00000 n \n" % off for off in offsets)
    return out + b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)


def post_init_hook(env):
    Lab, Attachment = env["awesome.preview"], env["ir.attachment"]
    generated = {"sample.png": _png, "sample.pdf": _pdf}

    for sequence, (name, module, note, names) in enumerate(LAB, 1):
        files = _text_files() if names is None else [
            (f, generated[f]() if f in generated else _read(f)) for f in names]
        rec = Lab.create({"name": name, "sequence": sequence * 10, "module_name": module, "description": note})
        atts = Attachment.browse()
        for filename, raw in files:
            atts |= Attachment.create({
                "name": filename, "raw": raw, "res_model": "awesome.preview", "res_id": rec.id})
        # the same files in every kind of field: single fields take one file, the lists take them all
        first = files[0]
        rec.write({"file_binary": base64.b64encode(first[1]), "file_binary_name": first[0],
                   "file_m2o": atts[-1].id, "file_m2m": [(6, 0, atts.ids)]})
        for filename, raw in files[:3]:
            env["awesome.preview.file"].create({
                "preview_id": rec.id, "name": filename, "file": base64.b64encode(raw), "file_name": filename})
        rec.message_post(body=note, attachment_ids=atts.ids, message_type="comment", subtype_xmlid="mail.mt_note")

    # everything made up to here is a sample: the limits (10 files per record, 100 MB) count only what visitors add
    param = env["ir.config_parameter"].sudo()
    param.set_param("demo_dwo_attpreview.sample_attachment_id", Attachment.search([], order="id desc", limit=1).id)
    param.set_param("demo_dwo_attpreview.sample_line_id",
                    env["awesome.preview.file"].search([], order="id desc", limit=1).id)
