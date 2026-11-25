# -*- coding: utf-8 -*-
{
    "name": "Dynamic Dashboard",
    "version": "19.0.0.1.0",
    "summary": "Personal dashboards with drag-and-drop pages, charts, pivots and tables, shared with permissions kept. "
               "Keywords: dashboard, dashboards, drag and drop dashboard, pivot, chart, kpi.",
    "description": "A private dashboard for each user: pages, a drag-and-drop grid of KPIs, tables, charts and pivots, filters, "
                   "and an Explore panel to pick data. Every query runs with the permissions of the person who views the page. "
                   "Requires the base and web modules, no external library.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Extra Tools",
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "security/dwo_dashboard_security.xml",
        "views/menu.xml",
        "views/dataset_views.xml",
    ],
    "assets": {
        "web.assets_backend": ["dwo_dashboard/static/src/**/*"],
        "web.assets_tests": ["dwo_dashboard/static/tests/**/*"],
    },
    "application": True,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
    "price": 99.00,
    "currency": "EUR",
} # type: ignore
