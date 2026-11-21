# -*- coding: utf-8 -*-
{
    "name": "Demo: Orphan Mail Routing",
    "version": "19.0.1.0.0",
    "summary": "Project contacts and a dozen incoming emails Odoo could not route, with suggestions, to try dwo_mail_orphan_routing.",
    "description": "Install only on demo servers. Gives the demo users the Orphan Mail Manager group, creates project contacts "
                   "with reference codes and feeds sample emails through the mail gateway so they land in the orphan list.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "category": "Hidden/Tools",
    "depends": ["demo_users", "contacts", "dwo_mail_orphan_routing"],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
