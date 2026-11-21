# -*- coding: utf-8 -*-
{
    "name": "Demo: Attachment Preview suite",
    "version": "19.0.1.0.0",
    "summary": "Sample contacts with Office, text, archive, email, 3D, CAD and BIM files to try the attachment preview modules.",
    "description": "Install only on demo servers. Creates contacts whose chatter holds sample files of every kind the "
                   "dwo_attpreview_* modules can open (the files come from the tests/files folders of those modules).",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "category": "Hidden/Tools",
    "depends": [
        "demo_users", "contacts", "dwo_attpreview_core", "dwo_attpreview_webgl", "dwo_attpreview_text",
        "dwo_attpreview_office", "dwo_attpreview_archive", "dwo_attpreview_mail", "dwo_attpreview_3d",
        "dwo_attpreview_cad", "dwo_attpreview_bim",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
