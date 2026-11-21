# -*- coding: utf-8 -*-
"""Writes the login page settings: the login page of the demo is the demo."""
SETTINGS = {
    "enabled": "True", "layout": "intro", "preset": "ocean", "primary": "#1E6FD9", "button": "#1E6FD9",
    "bg_type": "gallery", "bg_mode": "random", "bg_pool": "all",
    "page_title": "DuoTEK demo", "welcome_title": "Welcome back", "welcome_text": "Sign in to the demo",
    "intro_title": "Login Themes", "intro_items": "14 layouts\nColours and presets\nBundled or your own backgrounds\nLogo and fixed announcement",
    "footer_text": "Demo by DuoTEK",
    "ann_enabled": "True", "ann_kind": "info",
    "ann_html": "This login page is made by the module. Reload to see another background.",
}


def post_init_hook(env):
    icp = env["ir.config_parameter"].sudo()
    for key, value in SETTINGS.items():
        icp.set_param("dwo_login." + key, value)
