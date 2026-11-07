# -*- coding: utf-8 -*-
{
    "name": "Record Concurrency Guard",
    "version": "20.0.1.1.0",
    "summary": "Warn users before they overwrite each other's changes: field-level conflict check at save, with a clear comparison.",
    "description": "Soft concurrency control for form views. Choose the models and fields to watch; when another user changed a field you are saving, a dialog compares both values and lets you force save, discard or cancel. It never blocks a save. Requires the standard base, web and bus modules, no external library.",
    "author": "DUO-TEK Software Vietnam",
    "website": "https://apps.odoo.com/apps/modules/browse?author=DUO-TEK%20Software%20Vietnam",
    "category": "Extra Tools",
    "depends": ["base", "web", "bus"],
    "data": [
        "security/ir.access.csv",
        "views/dwo_model_concurrency_views.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": ["dwo_record_concurrency/static/src/**/*"],
        "web.assets_tests": ["dwo_record_concurrency/static/tests/**/*"],
    },
    "images": ["static/description/banner.png"],
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
    'price': 35.00,
    'currency': 'EUR',
} # type: ignore
