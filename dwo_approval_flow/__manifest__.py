# -*- coding: utf-8 -*-
{
    "name": "Dynamic Approval Workflow",
    "version": "19.0.2.0.0",
    "live_test_url": "https://demo-approval.duotek.io.vn",
    "summary": "Multi-level approval for any model, drawn as a state diagram, with notifications. Keywords: approval, approval workflow, approval flow, multi level approval, approval matrix, state diagram, dynamic approval, purchase approval, sale approval, expense approval, approval notification, approval reminder, business trip approval, waiting for approval.",
    "description": "Design an approval flow for any model by drawing it: boxes are the document states, arrows are the buttons that move the document. Click an arrow to set who can press it (users, groups, a user on the document, or an expression), how many approvals are needed, who is told and how (a pop-up, a to-do activity, an email or inbox message, for the approvers, the followers of the document and its creator), and what else happens (update a field, run a server action). Includes a Waiting for my approval queue, reminders for people who did not answer, a status and history widget, JSON import and export, and a log of every vote, move and notification. Works on a state field the model already has, or on its own state. Requires only the standard base, web and mail modules.",
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
