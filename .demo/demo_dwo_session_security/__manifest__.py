# -*- coding: utf-8 -*-
{
    "name": "Demo: Session Security",
    "version": "19.0.1.0.0",
    "summary": "Short screen-lock and idle-logout times and a lock PIN (1234) for the demo users, to try dwo_session_security.",
    "description": "Install only on demo servers. Locks the screen after 2 idle minutes (PIN 1234), warns 1 minute before an "
                   "idle logout at 10 minutes and lets the user extend the session. New sessions need no approval.",
    "author": "DuoTEK",
    "website": "https://duotek.io.vn",
    "category": "Hidden/Tools",
    "depends": ["demo_users", "dwo_session_security"],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}  # type: ignore
