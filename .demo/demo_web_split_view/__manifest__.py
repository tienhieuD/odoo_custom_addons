# -*- coding: utf-8 -*-
{
    "name": "Demo: Split View",
    "version": "19.0.1.0.0",
    "summary": "A hundred contacts to try the split view (list and form side by side) of web_split_view.",
    "description": "Install only on demo servers. Creates companies and people so the Contacts list has something to browse "
                   "in the split view.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "category": "Hidden/Tools",
    "depends": ["demo_users", "contacts", "web_split_view"],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
