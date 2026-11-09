# -*- coding: utf-8 -*-
{
    "name": "Message Filter on Chatter",
    "version": "14.0.1.1.0",
    "summary": "Badges above the chatter to show only discussions, emails, activities, notes or tracking messages.",
    "description": "Adds a row of badges at the top of the chatter, under Send message, Log note and Activity: All, Discussions, Emails, Activities, Notes, Tracking and Other, each with its number of messages. A click shows only that kind of message, loaded from the server, so Load more keeps working. Requires only the standard mail module.",
    "author": "DUO-TEK Software Vietnam",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Productivity/Discuss",
    "images": ["static/description/banner.png"],
    "depends": ["mail"],
    # Odoo 14: the bundles are extended by a template (views/assets.xml), the Owl templates are listed in qweb
    "data": ["views/assets.xml"],
    "qweb": [
        "static/src/components/dwo_message_filter/dwo_message_filter.xml",
        "static/src/components/chatter_patch.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
    "price": 9.00,
    "currency": "EUR",
}  # type: ignore
