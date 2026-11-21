# -*- coding: utf-8 -*-
{
    "name": "Demo: Users",
    "version": "19.0.1.0.0",
    "summary": "The three demo users shared by every demo (demo_alice, demo_bob, demo_carol; password demo).",
    "description": "Install only on demo servers. Each demo_<module> depends on this module and adds the groups its demo needs.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "category": "Hidden/Tools",
    "depends": ["base"],
    "data": ["data/users.xml"],
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
