# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
{
    "name": "List Header Filter: Quick Column Filter",
    "version": "19.0.1.0.0",
    "live_test_url": "https://demo-headerfilter.duotek.io.vn",
    "summary": "Filter any list column from its header: checkboxes with search for many2one, many2many and selection, quick dates and fiscal year, Odoo's own operators. The filter joins the search bar as a facet. Keywords: list header filter, column filter, header filter, header search, list view filter, tree view filter, table filter, excel filter, filter by column, quick filter, list filter popover, fiscal year filter, date quick filter, multi select filter, search bar facet.",
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
