# -*- coding: utf-8 -*-
{
    "name": "Demo: Attachment Preview Lab",
    "version": "19.0.2.0.0",
    "summary": "Attachment Preview Lab: one record per preview module, with every kind of file field and sample files.",
    "description": "Install only on demo servers. The model awesome.preview has one record per dwo_attpreview_* module, "
                   "with a binary field, a many2one, a many2many and a one2many of files and a chatter. Visitors may "
                   "upload files (10 per record, 100 MB each; the extra ones are deleted).",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "category": "Hidden/Tools",
    "depends": [
        "demo_users", "mail", "dwo_attpreview_core", "dwo_attpreview_webgl", "dwo_attpreview_text",
        "dwo_attpreview_office", "dwo_attpreview_archive", "dwo_attpreview_mail", "dwo_attpreview_3d",
        "dwo_attpreview_cad", "dwo_attpreview_bim",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/lab_views.xml",
        "data/lab_data.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
