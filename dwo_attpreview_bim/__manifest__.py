# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
{
    "name": "Secure BIM Preview: IFC models",
    "version": "20.0.1.0.1",
    "live_test_url": "https://demo-attpreview.duotek.io.vn",
    "summary": "Preview BIM models (IFC) in Odoo without downloading: 3D view, storey tree, element properties. Files never leave your Odoo server. Keywords: ifc preview, preview ifc, ifc viewer, bim preview, preview bim, bim viewer, building model viewer, revit ifc, archicad ifc, attachment preview.",
    "description": "Engine for Secure Attachment Preview (dwo_attpreview_core). Opens IFC building models (IFC2x3 and IFC4) from the chatter and from file fields in a large dialog: orbit and zoom, a tree of site, building and storeys with a show/hide switch for each storey, and the properties and property sets of the element you click. The viewer (web-ifc, MPL-2.0, and three.js, MIT) is bundled and runs in the browser inside a sandboxed iframe with no network access: nothing is uploaded to any service. Large models take time to open; the size limit is set in Settings.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Productivity/Documents",
    "depends": ["dwo_attpreview_core", "dwo_attpreview_webgl"],
    "data": ["views/res_config_settings_views.xml"],
    "price": 50,
    "assets": {
        "web.assets_backend": ["dwo_attpreview_bim/static/src/js/*.js"],
        "web.assets_tests": ["dwo_attpreview_bim/static/tests/tours/*.js"],
    },
    "currency": "EUR",
    "images": ["static/description/banner.png"],
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}
