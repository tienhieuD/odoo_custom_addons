# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
{
    "name": "Secure WebGL Preview Base",
    "version": "19.0.1.0.0",
    "summary": "Shared 3D viewer base (three.js) for Secure 3D, CAD and BIM Preview modules. Installed automatically; previews no file by itself.",
    "description": "Base of the Secure Attachment Preview design-file modules (3D models, CAD drawings, BIM). Bundles three.js (MIT) and a sandboxed viewer frame with orbit controls, fit-to-view, wireframe, grid and background switches. Everything is served by your own Odoo server: no CDN, no network access from the viewer. It previews no file by itself.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Productivity/Documents",
    "depends": ["dwo_attpreview_core"],
    "assets": {
        "web.assets_backend": [
            "dwo_attpreview_webgl/static/src/js/*.js",
            "dwo_attpreview_webgl/static/src/xml/*.xml",
        ],
    },
    "images": ["static/description/banner.png"],
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}
