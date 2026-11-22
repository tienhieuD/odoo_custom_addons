# -*- coding: utf-8 -*-
{
    "name": "Dynamic Approval Workflow",
    "version": "19.0.2.0.0",
    "live_test_url": "https://demo-approval.duotek.io.vn",
    "summary": "Multi-level approval for any model, configured as a state diagram. Keywords: approval, approval workflow, approval flow, multi level approval, approval matrix, state diagram, dynamic approval, purchase approval, sale approval, expense approval.",
    "description": "Design an approval flow for any model by drawing it: boxes are the document states, arrows are the buttons that move the document. Click an arrow to set who can press it (users, groups, department, a user on the document, an expression, or an Odoo domain), how many approvals are needed, and what else happens (notify, email, update a field, server action). Works on a state field the model already has, or on its own state. Includes a status/history widget, JSON import and export, and a log of every vote and move. Requires only the standard base, web and mail modules.",
    "images": ["static/description/banner.png"],
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Extra Tools",
    "depends": ["base", "web", "mail"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/flow_views.xml",
        "data/mail_data.xml",
        "views/history_views.xml",
        "views/notify_views.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "dwo_approval_flow/static/src/**/*",
        ],
    },
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
    "price": 40.0,
    "currency": "EUR",
}  # type: ignore
