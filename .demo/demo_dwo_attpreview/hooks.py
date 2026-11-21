# -*- coding: utf-8 -*-
"""Creates contacts whose chatter holds a sample file of every kind the attachment preview modules open.

Every sample is English (see tools/make_samples.py for how the files were built)."""
import json

from odoo.tools import file_open

# (contact, note, [file in static/samples])
FILES = [
    ("Office documents", "Word, Excel, PowerPoint, OpenDocument and CSV: click a file to preview it.", [
        "sample.docx", "long.docx", "sample.xlsx", "sample.pptx", "sample.odt", "sample.ods", "sample.odp",
        "sample.csv", "sample_semicolon.csv", "sample.tsv"]),
    ("Emails", "EML emails with attachments, even an email inside an email.", ["quarterly-report.eml", "meeting.eml"]),
    ("3D models", "STL, OBJ, GLB, 3MF, PLY, FBX, DAE, STEP and IGES: rotate, zoom, wireframe.", [
        "spur-gear.stl", "spur-gear.glb", "spur-gear.obj", "spur-gear.3mf", "spur-gear.ply", "spur-gear.fbx",
        "spur-gear.dae", "rounded-cube.step", "cube-10x10.igs"]),
    ("CAD and BIM", "A DXF floor plan and an IFC building model.", ["floor-plan.dxf", "office-building.ifc"]),
    ("Archives", "ZIP, TAR.GZ and 7Z archives: browse the folder tree and open the files inside.", [
        "project.zip", "project.tar.gz", "project.7z"]),
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


def post_init_hook(env):
    Partner, Attachment = env["res.partner"], env["ir.attachment"]

    def make(name, note, files):
        partner = Partner.create({"name": name, "comment": note})
        ids = []
        for filename, raw in files:
            if raw is not None:
                ids.append(Attachment.create({
                    "name": filename, "raw": raw, "res_model": "res.partner", "res_id": partner.id}).id)
        partner.message_post(body=note, attachment_ids=ids, message_type="comment", subtype_xmlid="mail.mt_note")

    for name, note, files in FILES:
        make(name, note, [(f, _read(f)) for f in files])
    make("Text and code", "Raw text with colours, Markdown, JSON, XML and YAML trees, logs and diffs.", _text_files())
