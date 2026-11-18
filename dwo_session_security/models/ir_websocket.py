# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""The bus must not deliver private messages to a session that is locked, waiting for approval or ended."""
import functools

from odoo import SUPERUSER_ID, api, models, release

from .util import cfg_bool

WEBSOCKET_HOOK = "none"
try:
    if release.version_info[0] >= 20:
        from odoo.addons.bus import bus_dispatcher as _ws
        WEBSOCKET_HOOK = "check_sessions"
    else:
        from odoo.addons.bus import websocket as _ws
        WEBSOCKET_HOOK = "check_session"
except ImportError:   # pragma: no cover
    _ws = None


def session_is_active(session, env):
    """False if the dwo.session row of this session says it is not active."""
    try:
        key = session.get("dwo_key")
        if not key or "dwo.session" not in env:
            return True
        if not cfg_bool(env, "enabled"):
            return True
        row = env["dwo.session"].sudo().search([("key", "=", key)], limit=1)
        return not row or row.state == "active"
    except Exception:
        return False


if _ws is not None and WEBSOCKET_HOOK == "check_session" and not getattr(_ws.check_session, "_dwo_session", False):
    _orig_check = _ws.check_session

    @functools.wraps(_orig_check)
    def _check_session(session, env, *args, **kwargs):
        ok = _orig_check(session, env, *args, **kwargs)
        return bool(ok) and session_is_active(session, env)

    _check_session._dwo_session = True
    _ws.check_session = _check_session

if _ws is not None and WEBSOCKET_HOOK == "check_sessions" and not getattr(_ws.check_sessions, "_dwo_session", False):
    _orig_check_all = _ws.check_sessions

    @functools.wraps(_orig_check_all)
    def _check_sessions(cr, sessions, *args, **kwargs):   # Odoo 20 checks all the sockets of a dispatch at once
        resolved = _orig_check_all(cr, sessions, *args, **kwargs)
        env = api.Environment(cr, SUPERUSER_ID, {})
        for sid, session in list(resolved.items()):
            if not session_is_active(session, env):
                resolved.pop(sid)
        return resolved

    _check_sessions._dwo_session = True
    _ws.check_sessions = _check_sessions


class IrWebsocket(models.AbstractModel):
    _inherit = "ir.websocket"

    def _build_bus_channel_list(self, channels):
        from odoo.http import request
        try:
            if request and request.session.get("uid") and not session_is_active(request.session, self.env):
                return []
        except RuntimeError:
            pass
        return super()._build_bus_channel_list(channels)
