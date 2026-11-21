# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
{
    "name": "Orphan Mail Router",
    "version": "18.0.1.0.0",
    "live_test_url": "https://demo-orphan.duotek.io.vn",
    "summary": "Catch incoming emails that Odoo cannot attach to any record, suggest the right record and route them in one click. Keywords: lost messages, lost emails, orphan emails, orphan mail, unrouted email, unrouted emails, unmatched email, catchall, catch-all, catch-all mailbox, email routing, route email, route email manually, manual routing, manual email routing, incoming email, incoming emails, mail gateway, email inbox, reassign email, move email to record, move message to record, email to chatter, mail alias, alias bounce, bounce catchall, fetchmail, email rules, email digest, routing rules.",
    "description": "Orphan Mail Router keeps the incoming emails that no alias, reply or record can take. They land in an "
                   "inbox with filters, suggested target records (reply headers, codes in the subject, the sender), "
                   "one-click or bulk routing into the chatter of the record, automatic rules, a daily digest and a report.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Discuss",
    "depends": ["mail"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/orphan_views.xml",
        "views/rule_views.xml",
        "wizard/route_wizard_views.xml",
        "views/res_config_settings_views.xml",
        "views/menus.xml",
    ],
    "images": ["static/description/banner.png"],
    "price": 25,
    "currency": "EUR",
    "application": True,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
