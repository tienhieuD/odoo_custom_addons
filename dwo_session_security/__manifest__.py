# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
{
    "name": "Secure Session Login",
    "version": "19.0.1.0.1",
    "summary": "Lock the screen with a PIN, end idle sessions, warn before logout and approve new sessions. Keywords: session timeout, idle logout, auto logout, inactivity timeout, idle timeout, inactive session, lock screen, screen lock, auto lock screen, pin lock, unlock with pin, session lock, lock odoo, session security, secure login, login security, session expiry, session expired, logout warning, session warning, session approval, login approval, approve login, approve session, session manager, session management, active sessions, user sessions, force logout, kill session, close browser logout, browser close logout, session cookie, maximum session duration, session duration, session limit, forgot pin, pin reset, auto lock, idle session, lock session, session timeout warning, logout after inactivity, logout inactive users.",
    "description": "Secure Session Login protects the Odoo session. After a time without activity the screen locks and a PIN "
                   "unlocks it. The lock is enforced by the server, and the locked page does not contain the application. "
                   "Sessions end after an idle time or a maximum duration, with a warning before. Closing the browser "
                   "ends the session. Optional approval of new sessions by an administrator.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "support": "hello@duotek.io.vn",
    "category": "Extra Tools",
    "depends": ["web", "mail", "bus"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/templates.xml",
        "views/dwo_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "dwo_session_security/static/src/js/*.js",
        ],
        "web.assets_tests": ["dwo_session_security/static/tests/tours/*.js"],
    },
    "post_init_hook": "post_init",
    "images": ["static/description/banner.png"],
    "price": 25,
    "currency": "EUR",
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
