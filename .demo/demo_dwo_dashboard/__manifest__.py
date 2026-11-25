# -*- coding: utf-8 -*-
{
    "name": "Demo: Dynamic Dashboard",
    "version": "19.0.1.0.0",
    "summary": "Two years of sales orders and a ready-made dashboard for each demo user, to try dwo_dashboard.",
    "description": "Install only on demo servers. Creates customers, products, about 360 sales orders over 24 months "
                   "and gives demo_alice, demo_bob, demo_carol and demo_admin (a dashboard manager, without Settings rights) a Sales page and a Contacts page.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "category": "Hidden/Tools",
    "depends": ["demo_users", "sale", "contacts", "dwo_dashboard"],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
