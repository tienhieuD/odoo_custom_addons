# -*- coding: utf-8 -*-
{
    "name": "Message Filter on Chatter",
    "version": "16.0.1.1.0",
    "summary": "Badges above the chatter to show only discussions, emails, activities, notes or tracking messages.",
    "description": "Adds a row of badges at the top of the chatter, under Send message, Log note and Activity: All, Discussions, Emails, Activities, Notes, Tracking and Other, each with its number of messages. A click shows only that kind of message, loaded from the server, so Load more keeps working. Requires only the standard mail module.",
    "author": "DUO-TEK Software Vietnam",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Productivity/Discuss",
    "images": ["static/description/banner.png"],
    "depends": ["mail"],
    "assets": {
        "web.assets_backend": ["dwo_chatter_filter/static/src/**/*"],
        "web.assets_tests": ["dwo_chatter_filter/static/tests/**/*"],
    },
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
    "price": 9.00,
    "currency": "EUR",
}  # type: ignore
