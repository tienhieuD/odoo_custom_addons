# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
{
    "name": "Form Focus Mode",
    "version": "19.0.1.0.0",
    "summary": "Three buttons next to the pager choose the form layout for all your forms: normal, chatter always hidden, or auto chatter (a bar on the right opens the chatter as a drawer you can resize). Remembered. Keywords: full screen form view, fullscreen form, wide form view, hide chatter, chatter toggle, form view width, auto chatter, chatter drawer, form view layout, maximize form.",
    "description": "Three buttons next to the pager of every form view choose the layout, for all your forms: normal "
                   "(the chatter beside the form, as Odoo does), always hidden (the form uses the full width) and auto "
                   "drawer (the chatter is hidden; a bar on the right with the words Auto chatter opens it as a drawer "
                   "over a dimmed background, as wide as the usual chatter, with a handle to change its width). The "
                   "choice and the width are remembered. Keyboard shortcut Alt+Shift+F (Ctrl+Shift+F on a Mac).",
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
