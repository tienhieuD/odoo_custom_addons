# -*- coding: utf-8 -*-
{
    "name": "DWO Email Cc Bcc Reply-To - Demo Data (Lab)",
    "summary": "Developer-only: records and emails with Cc, Bcc and Reply-To, for screenshots of dwo_mail_bcc.",
    "description": """
Lab module, NOT for publishing. Creates a few customers with contacts, an email template with Cc,
Bcc and Reply-To, and emails sent through the real full composer (Cc, Bcc and Reply-To filled), so
the outgoing email and the message log show the three fields. Nothing leaves the server: the mail
queue rows are marked as sent. Everything is removed on uninstall.
    """,
    "author": "DUO-TEK Software Vietnam",
    "license": "LGPL-3",
    "category": "Hidden/Tools",
    "version": "19.0.1.0.0",
    "depends": ["dwo_mail_bcc", "contacts"],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": False,
}
