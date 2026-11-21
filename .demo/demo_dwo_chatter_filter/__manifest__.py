# -*- coding: utf-8 -*-
{
    "name": "Demo: Message Filter on Chatter",
    "summary": "Demo data: a record whose chatter holds every kind of message, for screenshots of dwo_chatter_filter.",
    "description": """
Demo module (lives in .demo, never published to the Apps store). Creates a customer whose chatter holds discussions (with followers and
with the customer), notes, emails received and sent, tracking messages and automatic messages, spread
over several days. Nothing leaves the server. Everything is removed on uninstall.
    """,
    "author": "DuoTEK",
    "license": "OPL-1",
    "category": "Hidden/Tools",
    "version": "19.0.1.0.0",
    "depends": ["dwo_chatter_filter", "contacts"],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": False,
}
