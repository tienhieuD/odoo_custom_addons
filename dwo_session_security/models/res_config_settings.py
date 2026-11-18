# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import fields, models

from .util import PARAM


def _int(name, help=None):
    return fields.Integer(config_parameter=PARAM + name, help=help)


def _bool(name, help=None):
    return fields.Boolean(config_parameter=PARAM + name, help=help)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    dwo_enabled = _bool("enabled", "Master switch. Switch it off to disable every rule of the module at once.")
    dwo_lock_enabled = _bool("lock_enabled")
    dwo_lock_after_min = _int("lock_after_min", "Minutes without activity before the screen is locked (users with a PIN).")
    dwo_idle_logout_min = _int("idle_logout_min", "Minutes without activity before the session ends, checked on the server. 0 = never.")
    dwo_absolute_min = _int("absolute_min", "Minutes after the sign-in when the session ends, whatever the activity. 0 = never.")
    dwo_warn_enabled = _bool("warn_enabled")
    dwo_warn_min = _int("warn_min", "Minutes before the end of the session when the warning appears.")
    dwo_extend_enabled = _bool("extend_enabled")
    dwo_extend_min = _int("extend_min", "Minutes added each time the user extends the session.")
    dwo_extend_max = _int("extend_max", "How many times a session can be extended.")
    dwo_close_browser = _bool("close_browser", "Closing the browser ends the session: the next visit asks for the password.")
    dwo_browser_grace_sec = _int("browser_grace_sec", "Seconds without a heartbeat after which the browser counts as closed (min. 60).")
    dwo_pin_digits = fields.Selection([("both", "4 or 6 digits"), ("4", "4 digits"), ("6", "6 digits")],
                                      config_parameter=PARAM + "pin_digits")
    dwo_pin_max_tries = _int("pin_max_tries", "Wrong PINs before the user is signed out.")
    dwo_pin_lock_sec = _int("pin_lock_sec", "Seconds of pause after 3 wrong PINs in a row.")
    dwo_save_before_lock = _bool("save_before_lock", "Try to save the open form before the screen locks. Off by default: the lock "
                                 "often comes when nobody is there, and a save would write data nobody confirmed.")
    dwo_forgot_relogin = _bool("forgot_relogin")
    dwo_forgot_admin = _bool("forgot_admin")
    dwo_forgot_otp = _bool("forgot_otp")
    dwo_forgot_temp = _bool("forgot_temp")
    dwo_force_new_pin_after_relogin = _bool("force_new_pin_after_relogin")
    dwo_reset_request_limit = _int("reset_request_limit", "Reset requests a user can make per day.")
    dwo_approval_enabled = _bool("approval_enabled", "Users of the group Session approval required wait for an administrator after the sign-in.")
    dwo_approval_timeout_min = _int("approval_timeout_min", "Minutes before a request that nobody decided is refused.")
    dwo_notify_toast = _bool("notify_toast")
    dwo_notify_email = _bool("notify_email")
    dwo_notify_activity = _bool("notify_activity")
    dwo_log_days = _int("log_days", "Days the log is kept. 0 = forever.")
