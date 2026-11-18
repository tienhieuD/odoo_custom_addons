# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
{
    "name": "Login Page Themes",
    "version": "18.0.1.0.2",
    "summary": "Change only the look of the Odoo login page: 14 layouts, colours, backgrounds, logo and a fixed announcement. Keywords: login page, custom login, login background, login layout, login theme, login screen, login page design, login announcement, login notice, login message, login logo, custom login page, login page customization, login page background, login page layout, login page theme, login background image, login page template, login form design, login page style, change login page, customize login page, login branding, login page logo, login screen background, login screen design, sign in page, sign in page design, login page announcement, login page notice, maintenance notice login, login page colors, login gradient, login slideshow, random login background, glass login page, dark login page, split login page, show hide password, password toggle, login page title, login favicon, login welcome message, login page footer, hide powered by odoo, remove powered by odoo, login debrand.",
    "description": "Changes only the appearance of the standard login page: the form, the buttons and every other sign-in "
                   "option of Odoo (password reset, sign up, OAuth, two-factor, database selector) stay as they are. "
                   "Pick one of 14 layouts with a preview in Settings, a colour preset, a bundled free background, your "
                   "own image, a solid colour or a gradient, your own logo, a welcome text, a fixed announcement "
                   "(sanitized HTML) shown to everybody on the login page, and an option to hide \"Powered by Odoo\". Needs the Python library Pillow, which "
                   "Odoo already requires.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Extra Tools",
    "depends": ["web"],
    "data": [
        "views/login_templates.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "dwo_login_themes/static/src/scss/login_theme.scss",
            "dwo_login_themes/static/src/js/login_theme.js",
        ],
        "web.assets_backend": [
            "dwo_login_themes/static/src/scss/settings.scss",
        ],
        "web.assets_tests": ["dwo_login_themes/static/tests/tours/*.js"],
    },
    "uninstall_hook": "uninstall_hook",
    "images": ["static/description/banner.png"],
    "price": 22,
    "currency": "EUR",
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
