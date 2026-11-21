# -*- coding: utf-8 -*-
{
    "name": "Demo: List Header Filter",
    "version": "19.0.1.0.0",
    "summary": "300 contacts spread over two years, with tags, countries and companies, to try dwo_listview_header_filter.",
    "description": "Install only on demo servers. Creates companies and people with countries, tags and creation dates "
                   "over the last two years: a list worth filtering from the column headers.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "category": "Hidden/Tools",
    "depends": ["demo_users", "contacts", "dwo_listview_header_filter"],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
