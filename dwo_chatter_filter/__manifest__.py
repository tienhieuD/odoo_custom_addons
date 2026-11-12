# -*- coding: utf-8 -*-
{
    "name": "Chatter Quick Filter",
    "version": "13.0.2.0.0",
    "summary": "Quick filter chips above the chatter, in the colours and order you choose: show only discussions, emails, notes, tracking or any filter you define.",
    "description": "Adds a row of chips at the top of the chatter, under Send message, Log note and Activity: All, then the chips of your choice, each with its number of messages. The chips that come with the module are Discussions, Emails, Activities, Notes, Tracking and Other. Administrators have an Edit link after the chips: a list to drag the chips in the order they want and to archive them, and a form to change the name, the colour and the filter of a chip or to make a new one. A click on a chip shows only its messages, loaded from the server, so Load more keeps working. Requires only the standard mail module.",
    "author": "DUO-TEK Software Vietnam",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Productivity/Discuss",
    "images": ["static/description/banner.png"],
    "depends": ["mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/dwo_chatter_filter_data.xml",
        "views/dwo_chatter_filter_views.xml",
        "views/assets.xml",
    ],
    # Odoo 13: the bundles are extended by a template (views/assets.xml), the widget templates are in qweb
    "qweb": ["static/src/xml/dwo_chatter_filter.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
    "price": 9.00,
    "currency": "EUR",
}  # type: ignore
