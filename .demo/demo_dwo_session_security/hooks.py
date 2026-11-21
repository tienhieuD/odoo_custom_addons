# -*- coding: utf-8 -*-
"""Short times so a visitor sees the lock screen and the warning within minutes; PIN 1234 for the demo users."""
SETTINGS = {
    "enabled": "True", "lock_enabled": "True", "lock_after_min": "2",
    "idle_logout_min": "10", "warn_enabled": "True", "warn_min": "1",
    "extend_enabled": "True", "extend_min": "5", "extend_max": "3",
    "approval_enabled": "False",       # a demo visitor must never wait for an administrator
}
PIN = "1234"


def post_init_hook(env):
    icp = env["ir.config_parameter"].sudo()
    for key, value in SETTINGS.items():
        icp.set_param("dwo_session." + key, value)
    users = env["res.users"].search([("login", "in", ["demo_alice", "demo_bob", "demo_carol"])])
    for user in users:
        env["dwo.user.pin"].set_pin(user.id, PIN, check=False)
