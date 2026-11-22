# -*- coding: utf-8 -*-
{
    "name": "Demo: Dynamic Approval Workflow",
    "version": "19.0.1.2.0",
    "summary": "Demo users, purchase orders and a ready-made approval flow for dwo_approval_flow.",
    "description": "Install only on demo servers. Gives the demo users (demo_users) purchase rights, adds demo_admin (can configure the flows) and creates "
                   "some vendors, products and purchase orders, and a purchase approval flow that replaces the status bar.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "category": "Extra Tools",
    "depends": ["demo_users", "dwo_approval_flow", "purchase"],
    "data": ["data/demo_data.xml"],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
