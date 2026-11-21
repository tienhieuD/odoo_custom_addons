# -*- coding: utf-8 -*-
{
    "name": "Demo: Form Focus Mode",
    "version": "19.0.1.0.0",
    "summary": "Contacts with a busy chatter, to try hiding the chatter or opening it as a drawer with dwo_form_focus_mode.",
    "description": "Install only on demo servers. Creates companies and people, a dozen of them with a long chatter history "
                   "(notes, an email, an activity), so the focus buttons next to the pager have something to hide.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "category": "Hidden/Tools",
    "depends": ["demo_users", "contacts", "dwo_form_focus_mode"],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
