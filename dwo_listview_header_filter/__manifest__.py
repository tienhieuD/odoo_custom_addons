# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
{
    "name": "List Header Filter: Quick Column Filter",
    "version": "19.0.1.0.0",
    "summary": "Filter icon on every list column header: pick values, dates or operators and the filter joins the search bar. Keywords: list view filter, column filter, header filter, header search, table filter, excel filter, quick filter, list view search, tree view filter, filter by column.",
    "description": "A filter icon in the header of each list column. Click it to choose what to show: checkboxes with search "
                   "for many2one, many2many and selection fields (the chosen values move to the top), quick dates "
                   "(today, this week, this month, fiscal year...) or a day range for date fields, the operators of "
                   "Odoo's own filters for text and numbers. The condition becomes a facet of the search bar, and "
                   "clearing it in either place clears the other. Works next to the list sticky header and column "
                   "freeze module of DuoTEK.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Extra Tools",
    "depends": ["web"],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "dwo_listview_header_filter/static/src/js/*.js",
            "dwo_listview_header_filter/static/src/xml/*.xml",
            "dwo_listview_header_filter/static/src/scss/*.scss",
        ],
        "web.assets_tests": ["dwo_listview_header_filter/static/tests/tours/*.js"],
    },
    "images": ["static/description/banner.png"],
    "price": 12,
    "currency": "EUR",
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
