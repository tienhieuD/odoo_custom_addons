# -*- coding: utf-8 -*-
{
    "name": "Email Cc Bcc Reply-To",
    "version": "12.0.1.1.0",
    "summary": "Cc, Bcc and Reply-To in the Odoo composer, on templates and on outgoing emails. Bcc stays hidden.",
    "description": "Adds Cc, Bcc and Reply-To to the full composer (Send message), and shows them on outgoing emails and in the message log. Bcc recipients receive the email, but their addresses never appear in any header seen by other recipients. Cc is written in the headers and gets one copy. Reply-To sends the answers to the address you choose, with a check that it is one valid address. Templates have a Bcc field. Requires only the standard mail module.",
    "author": "DUO-TEK Software Vietnam",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Productivity/Discuss",
    "images": ["static/description/banner.png"],
    "depends": ["mail"],
    "data": [
        "views/mail_mail_views.xml",
        "views/mail_template_views.xml",
        "wizard/mail_compose_message_views.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}  # type: ignore
