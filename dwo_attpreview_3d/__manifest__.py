# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
{
    "name": "Secure 3D Preview: STL, OBJ, GLB, 3MF, FBX",
    "version": "19.0.1.0.0",
    "summary": "Preview 3D models in Odoo without downloading: STL, OBJ, GLB, GLTF, 3MF, PLY, FBX, DAE. Rotate, zoom, wireframe. Files never leave your Odoo server. Keywords: 3d preview, stl viewer, obj viewer, glb viewer, gltf viewer, 3mf preview, 3d model viewer, 3d print preview, attachment preview.",
    "description": "Engine for Secure Attachment Preview (dwo_attpreview_core). Opens 3D models from the chatter and from file fields in a large dialog with orbit controls, fit-to-view, wireframe, grid, axes and background switches. The viewer (three.js, MIT) is bundled and runs in the browser inside a sandboxed iframe with no network access: nothing is uploaded to any service. Formats: STL, OBJ, GLB, GLTF (data inside), 3MF, PLY, FBX, DAE. Size limits per group of formats in Settings.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Productivity/Documents",
    "depends": ["dwo_attpreview_core", "dwo_attpreview_webgl"],
    "data": ["views/res_config_settings_views.xml"],
    "price": 30,
    "assets": {
        "web.assets_backend": [
            "dwo_attpreview_3d/static/src/js/*.js",
        ],
        "web.assets_tests": ["dwo_attpreview_3d/static/tests/tours/*.js"],
    },
    "currency": "EUR",
    "images": ["static/description/banner.png"],
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}
