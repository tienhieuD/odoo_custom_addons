# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""The bus must not deliver private messages to a session that is locked, waiting for approval or ended."""
import functools

from odoo import models

try:
    from odoo.addons.bus import websocket as _ws
except ImportError:   # pragma: no cover
    _ws = None


def session_is_active(session, env):
    """False if the dwo.session row of this session says it is not active."""
    try:
        key = session.get("dwo_key")
        if not key or "dwo.session" not in env:
            return True
        enabled = env["ir.config_parameter"].sudo().get_param("dwo_session.enabled", "")
        if str(enabled).lower() not in ("1", "true"):
            return True
        row = env["dwo.session"].sudo().search([("key", "=", key)], limit=1)
        return not row or row.state == "active"
    except Exception:
        return False


if _ws is not None and not getattr(_ws.check_session, "_dwo_session", False):
    _orig_check = _ws.check_session

    @functools.wraps(_orig_check)
    def _check_session(session, env, *args, **kwargs):
        ok = _orig_check(session, env, *args, **kwargs)
        return bool(ok) and session_is_active(session, env)

    _check_session._dwo_session = True
    _ws.check_session = _check_session


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
