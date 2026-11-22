# -*- coding: utf-8 -*-
{
    "name": "Demo: Login Themes",
    "version": "19.0.1.0.0",
    "summary": "Sets a ready-made login page for dwo_login_themes; the demo users are administrators and land on the login settings.",
    "description": "Install only on demo servers. Writes the login page settings (dwo_login.*) so the login page of the demo "
                   "shows the module at work.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "category": "Hidden/Tools",
    "depends": ["demo_users", "dwo_login_themes", "web"],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
