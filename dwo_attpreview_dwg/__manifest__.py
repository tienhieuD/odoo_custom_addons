# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the GNU General Public License v3.0 (GPL-3).
{
    "name": "Secure DWG Preview: AutoCAD drawings",
    "version": "18.0.1.0.1",
    "summary": "Free: preview AutoCAD DWG drawings in Odoo without downloading or converting. Files never leave your Odoo server. Keywords: dwg preview, preview dwg, dwg viewer, autocad preview, autocad viewer, cad viewer, drawing viewer, open dwg file, attachment preview.",
    "description": "Engine for Secure Attachment Preview (dwo_attpreview_core). Opens AutoCAD DWG drawings (R13 up to 2018 and later, as far as LibreDWG reads them) from the chatter and from file fields, with pan, zoom, fit-to-view and a layer list. The drawing is converted in the browser by LibreDWG (WebAssembly, GPL-3) and drawn by dxf-viewer (MPL-2.0), inside a sandboxed iframe with no network access: nothing is uploaded to any service and nothing is installed on the server. Some complex drawings may show with missing details. Free and open source (GPL-3).",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Productivity/Documents",
    "depends": ["dwo_attpreview_core", "dwo_attpreview_webgl"],
    "data": ["views/res_config_settings_views.xml"],
    "assets": {
        "web.assets_backend": ["dwo_attpreview_dwg/static/src/js/*.js"],
        "web.assets_tests": ["dwo_attpreview_dwg/static/tests/tours/*.js"],
    },
    "images": ["static/description/banner.png"],
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "GPL-3",
}
