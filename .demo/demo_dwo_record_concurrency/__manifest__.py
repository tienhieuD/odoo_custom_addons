# -*- coding: utf-8 -*-
{
    "name": "Demo: Record Concurrency",
    "version": "19.0.1.0.0",
    "summary": "Watches the contact fields and creates sample contacts, so two demo users can collide on the same record.",
    "description": "Install only on demo servers. Turns the conflict check on for the main fields of Contacts and creates "
                   "a few contacts. Log in as demo_alice in one browser and demo_bob in another, edit the same contact.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "category": "Hidden/Tools",
    "depends": ["demo_users", "contacts", "dwo_record_concurrency"],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
