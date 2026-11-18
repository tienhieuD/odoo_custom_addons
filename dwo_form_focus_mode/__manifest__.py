# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
{
    "name": "Form Focus Mode",
    "version": "20.0.1.0.0",
    "summary": "Hide the chatter or open it as a drawer, from three buttons next to the pager. Keywords: hide chatter, hide chatter form, chatter hide, remove chatter, disable chatter, collapse chatter, chatter toggle, toggle chatter, show hide chatter, chatter drawer, chatter sidebar, chatter panel, auto chatter, resizable chatter, full screen form view, fullscreen form, full width form, wide form view, form view width, form view layout, maximize form, form focus, focus mode, form view chatter position, chatter right side, chatter width, widescreen form, more space form view.",
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
