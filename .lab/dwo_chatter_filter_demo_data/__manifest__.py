# -*- coding: utf-8 -*-
{
    "name": "DWO Message Filter on Chatter - Demo Data (Lab)",
    "summary": "Developer-only: a record whose chatter holds every kind of message, for screenshots of dwo_chatter_filter.",
    "description": """
Lab module, NOT for publishing. Creates a customer whose chatter holds discussions (with followers and
with the customer), notes, emails received and sent, tracking messages and automatic messages, spread
over several days. Nothing leaves the server. Everything is removed on uninstall.
    """,
    "author": "DUO-TEK Software Vietnam",
    "license": "LGPL-3",
    "category": "Hidden/Tools",
    "version": "19.0.1.0.0",
    "depends": ["dwo_chatter_filter", "contacts"],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": False,
}
