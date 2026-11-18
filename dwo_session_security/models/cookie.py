# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""The session cookie becomes a browser-session cookie (no Expires, no Max-Age): the browser forgets it when it is
closed. Odoo sets Max-Age on it at every save (``get_session_max_inactivity``) and ``FutureResponse`` forces a
one-year Expires; both are removed here, for every place that writes the cookie."""
import functools
import inspect

from odoo import http

from .compat import FutureResponse, Response

_PATCHED = "_dwo_session_cookie"


def _enabled():
    try:
        request = http.request
        if not request or not request.db or "dwo.session" not in request.env:
            return False
        from .util import cfg_bool
        return cfg_bool(request.env, "close_browser") and cfg_bool(request.env, "enabled")
    except Exception:
        return False


def _wrap(orig):
    sig = inspect.signature(orig)

    @functools.wraps(orig)
    def set_cookie(self, key, value="", *args, **kwargs):
        if key == "session_id" and value and _enabled():
            bound = sig.bind(self, key, value, *args, **kwargs)
            if bound.arguments.get("max_age") != 0:
                bound.arguments["max_age"] = None
                bound.arguments["expires"] = None
            return orig(*bound.args, **bound.kwargs)
        return orig(self, key, value, *args, **kwargs)

    setattr(set_cookie, _PATCHED, True)
    return set_cookie


for _cls in (FutureResponse, Response):
    if not getattr(_cls.set_cookie, _PATCHED, False):
        _cls.set_cookie = _wrap(_cls.set_cookie)
