# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
{
    "name": "Secure Attachment Preview",
    "version": "18.0.1.3.1",
    "summary": "Preview attachments and file fields in a large popup: PDF, images, video, audio. Keywords: attachment preview, preview attachment, file preview, preview file, document preview, pdf preview, preview pdf, pdf viewer, image preview, video preview, binary field preview, attachment viewer, preview without download.",
    "description": "Core of the Attachment Preview family. Opens PDF, images, video and audio in a large preview dialog from the chatter and from file fields (binary, many2many_binary, attachment lists, kanban and many2one). Files that cannot be previewed show a short notice with a Download button. Provides the engine registry, render cache (lazy, auto-cleaned), access-checked controller and a Settings page where engine modules are ticked to be installed. No CDN, no external service: nothing is sent outside your server.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Productivity/Documents",
    "depends": ["base", "web", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # Headless Tree + TanStack Virtual (MIT, global DwoTreeLibs): the tree view shared by the engines
            "dwo_attpreview_core/static/lib/tree_libs/tree_libs.min.js",
            "dwo_attpreview_core/static/src/js/*.js",
            "dwo_attpreview_core/static/src/scss/*.scss",
            "dwo_attpreview_core/static/src/xml/*.xml",
        ],
        "web.assets_tests": ["dwo_attpreview_core/static/tests/tours/*.js"],
    },
    "images": ["static/description/banner.png"],
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}  # type: ignore
