# -*- coding: utf-8 -*-
{
    "name": "Mail BCC Support",
    "version": "19.0.1.0.0",
    "summary": "Add a real Bcc to the Odoo mail composer, the outgoing mail queue and the message log.",
    "description": "Adds a Bcc field to the full composer (Send message) and to outgoing emails (mail.mail). Bcc recipients receive the email, but their addresses never appear in any header seen by other recipients. Requires only the standard mail module.",
    "author": "DUO-TEK Software Vietnam",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Productivity/Discuss",
    "images": ["static/description/banner.png"],
    "depends": ["mail"],
    "data": [
        "views/mail_mail_views.xml",
        "views/mail_message_views.xml",
        "views/mail_template_views.xml",
        "wizard/mail_compose_message_views.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}  # type: ignore
