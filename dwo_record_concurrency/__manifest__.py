# -*- coding: utf-8 -*-
{
    "name": "Record Concurrency Control Pro",
    "version": "18.0.1.0.0",
    "summary": "Prevent data conflicts and enhance collaboration with real-time record locking and concurrency warnings.",
    "description": "static/description/index.html",
    "author": "DUO-TEK Software Vietnam",
    "website": "https://apps.odoo.com/apps/modules/browse?author=DUO-TEK%20Software%20Vietnam",
    "category": "Productivity",
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
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
    'price': 59.00,
    'currency': 'EUR',
} # type: ignore
