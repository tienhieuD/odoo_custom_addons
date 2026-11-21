# -*- coding: utf-8 -*-
{
    "name": "List View Sticky Header & Freeze Column - Demo Data",
    "version": "19.0.1.0.0",
    "summary": "Demo users and 150 contacts (a long, wide list) to try listview_sticky_header_and_column.",
    "description": "Install only on demo servers. Creates three users (demo_alice, demo_bob, demo_carol, password demo) "
                   "and 150 sample contacts, so the Contacts list scrolls both ways.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "category": "Extra Tools",
    "depends": ["listview_sticky_header_and_column", "contacts"],
    "data": ["data/demo_users.xml"],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
