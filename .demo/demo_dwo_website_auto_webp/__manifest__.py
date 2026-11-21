# -*- coding: utf-8 -*-
{
    "name": "Demo: Website Auto WebP",
    "version": "19.0.1.0.0",
    "summary": "A public page with large PNG and JPEG pictures that dwo_website_auto_webp serves as WebP.",
    "description": "Install only on demo servers. Creates the page /webp-demo (the home page of the demo website) with large "
                   "generated pictures. Open the browser Network tab: the images arrive as WebP, much smaller than the originals.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "category": "Hidden/Tools",
    "depends": ["demo_users", "website", "dwo_website_auto_webp"],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
