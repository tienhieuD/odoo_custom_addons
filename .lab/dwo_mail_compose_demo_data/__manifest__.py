# -*- coding: utf-8 -*-
{
    "name": "DWO Email Composer - Demo Data (Lab)",
    "summary": "Developer-only: realistic email scenarios on contacts, for screenshots of dwo_mail_compose.",
    "description": """
Lab module, NOT for publishing. Creates a few customers (res.partner), each one a ready-made
scenario to open and capture: a long conversation (incoming emails, an official reply, a note and a
message), an unsent draft with an inline image, a second draft, an email waiting for approval, a
rejected one, a forward, a clean thread and an email template with a Bcc.

Emails are created through the real code (dwo.mail.composer), as the admin user, and nothing leaves
the server: the outgoing mail rows are marked as sent. Everything is removed on uninstall.
    """,
    "author": "DUO-TEK Software Vietnam",
    "license": "LGPL-3",
    "category": "Hidden/Tools",
    "version": "19.0.1.0.0",
    "depends": ["dwo_mail_compose", "contacts"],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": False,
}
