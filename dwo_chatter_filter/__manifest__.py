# -*- coding: utf-8 -*-
{
    "name": "Chatter Quick Filter",
    "version": "15.0.2.0.0",
    "live_test_url": "https://demo-chatterfilter.duotek.io.vn",
    "summary": "Filter the chatter in one click: emails, notes, discussions, tracking or your own filters. Keywords: chatter filter, filter chatter, chatter search, search chatter, message filter, filter messages, filter emails, log note filter, tracking filter, chatter tabs.",
    "description": "Adds a row of chips at the top of the chatter, under Send message, Log note and Activity: All, then the chips of your choice, each with its number of messages. The chips that come with the module are Discussions, Emails, Activities, Notes, Tracking and Other. Administrators have an Edit link after the chips: a list to drag the chips in the order they want and to archive them, and a form to change the name, the colour and the filter of a chip or to make a new one. A click on a chip shows only its messages, loaded from the server, so Load more keeps working. Requires only the standard mail module.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Productivity/Discuss",
    "images": ["static/description/banner.png"],
    "depends": ["mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/dwo_chatter_filter_data.xml",
        "views/dwo_chatter_filter_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "dwo_chatter_filter/static/src/**/*.js",
            "dwo_chatter_filter/static/src/**/*.scss",
        ],
        # Odoo 15: the Owl templates are in their own bundle
        "web.assets_qweb": ["dwo_chatter_filter/static/src/**/*.xml"],
        "web.assets_tests": ["dwo_chatter_filter/static/tests/**/*"],
    },
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
    "price": 9.00,
    "currency": "EUR",
}  # type: ignore
