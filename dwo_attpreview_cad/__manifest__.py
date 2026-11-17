# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
{
    "name": "Secure CAD Preview: DXF drawings",
    "version": "19.0.1.0.0",
    "summary": "Preview DXF drawings in Odoo without downloading: layers, lines, arcs, text, hatches. Files never leave your Odoo server. Keywords: dxf preview, dxf viewer, cad preview, cad viewer, autocad preview, drawing viewer, 2d drawing preview, attachment preview.",
    "description": "Engine for Secure Attachment Preview (dwo_attpreview_core). Opens DXF drawings from the chatter and from file fields in a large dialog with pan, zoom, fit-to-view and a layer list (show or hide each layer). The viewer (dxf-viewer, MPL-2.0, and three.js, MIT) is bundled and runs in the browser inside a sandboxed iframe with no network access: nothing is uploaded to any service. ASCII DXF only; for DWG files see the free Secure DWG Preview module. Size limit in Settings.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Productivity/Documents",
    "depends": ["dwo_attpreview_core", "dwo_attpreview_webgl"],
    "data": ["views/res_config_settings_views.xml"],
    "price": 40,
    "assets": {
        "web.assets_backend": ["dwo_attpreview_cad/static/src/js/*.js"],
        "web.assets_tests": ["dwo_attpreview_cad/static/tests/tours/*.js"],
    },
    "currency": "EUR",
    "images": ["static/description/banner.png"],
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}
