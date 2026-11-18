# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""Small helpers shared by the models and the controllers."""
import re
from urllib.parse import urlsplit

from odoo import release

JSON = "jsonrpc" if release.version_info[0] >= 19 else "json"
PARAM = "dwo_session."
DEFAULT_URL = "/web"
EXEMPT_GROUP = "dwo_session_security.group_dwo_session_exempt"
NEEDS_APPROVAL_GROUP = "dwo_session_security.group_dwo_session_approval"
APPROVER_GROUP = "dwo_session_security.group_dwo_session_approver"

DEFAULTS = {
    "enabled": "1",
    "lock_enabled": "1",
    "lock_after_min": "15",
    "idle_logout_min": "240",
    "absolute_min": "720",
    "warn_enabled": "1",
    "warn_min": "30",
    "extend_enabled": "1",
    "extend_min": "60",
    "extend_max": "3",
    "close_browser": "1",
    "browser_grace_sec": "180",
    "pin_digits": "both",
    "pin_max_tries": "5",
    "pin_lock_sec": "30",
    "save_before_lock": "0",
    "forgot_relogin": "1",
    "forgot_admin": "1",
    "forgot_otp": "0",
    "forgot_temp": "0",
    "force_new_pin_after_relogin": "1",
    "reset_request_limit": "3",
    "approval_enabled": "0",
    "approval_timeout_min": "15",
    "notify_toast": "1",
    "notify_email": "0",
    "notify_activity": "1",
    "log_days": "90",
}


def cfg(env, key):
    """Value of a setting (string)."""
    # a missing parameter means off / 0: Odoo removes the parameter when a setting is saved as unchecked or 0;
    # the defaults of DEFAULTS are written once, when the module is installed (see ``post_init``)
    return env["ir.config_parameter"].sudo().get_param(PARAM + key, "") or ""


def cfg_bool(env, key):
    return str(cfg(env, key)).strip().lower() in ("1", "true", "yes", "on")


def cfg_int(env, key):
    try:
        return max(0, int(float(cfg(env, key))))
    except (TypeError, ValueError):
        return 0


def safe_path(url, default=DEFAULT_URL):
    """Only an internal path can be a return address: no scheme, no host, no protocol-relative
    address, no backslash or control character, and never one of the pages of the module or the logout."""
    if not url or not isinstance(url, str) or len(url) > 2000:
        return default
    if any(ord(c) < 32 or c in "\\" for c in url) or re.search(r"%(0[0-9a-f]|5c|2f%2f)", url, re.I):
        return default
    if not url.startswith("/") or url.startswith("//"):
        return default
    parts = urlsplit(url)
    if parts.scheme or parts.netloc:
        return default
    if parts.path.startswith("/dwo/session/") or parts.path.startswith("/web/session/") or parts.path.startswith("/web/login"):
        return default
    return url


def describe_agent(user_agent):
    """A short readable browser name from a User-Agent header (no external library)."""
    ua = user_agent or ""
    browser = "Browser"
    for needle, name in (("Edg/", "Edge"), ("OPR/", "Opera"), ("Firefox/", "Firefox"), ("Chrome/", "Chrome"),
                         ("Safari/", "Safari")):
        if needle in ua:
            browser = name
            break
    system = ""
    for needle, name in (("Windows", "Windows"), ("Android", "Android"), ("iPhone", "iOS"), ("iPad", "iOS"),
                         ("Mac OS X", "macOS"), ("Linux", "Linux")):
        if needle in ua:
            system = name
            break
    return "%s on %s" % (browser, system) if system else browser


def tr(env, message, *args):
    """Translate a message (``env._`` exists from Odoo 18; before, the ``_`` function of Odoo)."""
    if hasattr(env, "_"):
        return env._(message, *args)
    from odoo import _
    return _(message, *args)


def post_init(env):
    """Write the default settings once (a setting that the administrator saves as off or 0 is removed by Odoo)."""
    icp = env["ir.config_parameter"].sudo()
    for key, value in DEFAULTS.items():
        if icp.get_param(PARAM + key, None) is None:
            icp.set_param(PARAM + key, value)
