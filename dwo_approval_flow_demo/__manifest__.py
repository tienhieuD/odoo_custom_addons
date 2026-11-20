# -*- coding: utf-8 -*-
{
    "name": "Dynamic Approval Workflow - Demo Data",
    "version": "19.0.1.0.0",
    "summary": "Demo users, purchase orders and a ready-made approval flow for dwo_approval_flow.",
    "description": "Install only on demo servers. Creates three users (demo_alice, demo_bob, demo_carol, password demo), "
                   "some vendors, products and purchase orders, and a purchase approval flow that replaces the status bar.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "category": "Extra Tools",
    "depends": ["dwo_approval_flow", "purchase"],
    "data": ["data/demo_data.xml"],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
