# -*- coding: utf-8 -*-
"""Creates the records of the Attachment Preview Lab: one per preview module, each with its sample files in every
kind of file field (binary, many2one, many2many, one2many lines) and in the chatter.

Every sample is English (see tools/make_samples.py for how the files were built)."""
import base64

from odoo.tools import file_open

# (record name, module, what to try, [file in static/samples], None = the text files made below)
LAB = [
    ("Core: PDF, images, video, audio", "dwo_attpreview_core",
     "A 3-page PDF report, a photo, a video and an audio file open in a large dialog.",
     ["sample.pdf", "sample.png", "sample.mp4", "sample.mp3"]),
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
    """Longer, realistic text, code, log and diff files (tools/make_rich_samples.py)."""
    names = ["README.md", "data.json", "config.xml", "settings.yaml", "script.py", "page.html", "server.log", "change.diff"]
    return [(n, _read("text/" + n)) for n in names]


def post_init_hook(env):
    Lab, Attachment = env["awesome.preview"], env["ir.attachment"]
    for sequence, (name, module, note, names) in enumerate(LAB, 1):
        files = _text_files() if names is None else [
            (f, _read(f)) for f in names]
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
