# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
{
    "name": "Form Focus Mode",
    "version": "19.0.1.0.0",
    "summary": "One click gives the form view the whole screen: hide the chatter, widen the sheet, hide the top bar, and bring the chatter back as a side drawer. Remembered per model. Keywords: full screen form view, fullscreen form, wide form view, hide chatter, chatter toggle, form view width, focus mode, form view layout, maximize form, chatter drawer, form view full width.",
    "description": "A small button in the control panel of every form view cycles three layouts: normal, wide (the chatter is "
                   "hidden and the sheet uses the full width) and focus (the same, and the top navigation bar is hidden "
                   "too). While the chatter is hidden a floating button opens it as a side drawer, so the history is one "
                   "click away. The choice is remembered for each model in your browser. Keyboard shortcut Alt+Shift+F (Ctrl+Shift+F on a Mac).",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Extra Tools",
    "depends": ["web"],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "dwo_form_focus_mode/static/src/js/*.js",
            "dwo_form_focus_mode/static/src/xml/*.xml",
            "dwo_form_focus_mode/static/src/scss/*.scss",
        ],
        "web.assets_tests": ["dwo_form_focus_mode/static/tests/tours/*.js"],
    },
    "images": ["static/description/banner.png"],
    "price": 10,
    "currency": "EUR",
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
