# -*- coding: utf-8 -*-
{
    "name": "Record Concurrency Guard",
    "version": "17.0.1.1.0",
    "summary": "Stop users from overwriting each other's changes: conflict check at save. Keywords: concurrency, concurrent editing, concurrent edit, record lock, lock record, edit conflict, prevent overwrite, simultaneous editing, optimistic locking, multi user editing.",
    "description": "Soft concurrency control for form views. Choose the models and fields to watch; when another user changed a field you are saving, a dialog compares both values and lets you force save, discard or cancel. It never blocks a save. Requires the standard base, web and bus modules, no external library.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Extra Tools",
    "depends": ["base", "web", "bus"],
    "data": [
        "security/ir.model.access.csv",
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
