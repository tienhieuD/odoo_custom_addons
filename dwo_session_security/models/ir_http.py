# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""The server-side gate. Every request of a session that is not active (locked, waiting for approval, ended) is
refused here, whatever the browser shows: a page, an RPC, a download, an image or a websocket handshake."""
import werkzeug.exceptions

from odoo import models
from odoo.exceptions import AccessDenied
from odoo.http import request

from .compat import SessionExpiredException, get_store, session_logout
from .util import JSON, cfg_bool

ALLOWED_PREFIX = "/dwo/session/"
ALLOWED_PATHS = ("/web/session/logout",)
PUBLIC_LOGO = "/web/binary/company_logo"


def _is_public_css(path):
    """The CSS bundle of Odoo's own login page (and the company logo): public, no data, no script."""
    return path == PUBLIC_LOGO or (
        path.startswith("/web/assets/") and path.endswith(".css") and "web.assets_frontend" in path
    )


NO_BROWSER_CHECK = ("/web/session/logout", "/dwo/session/relogin", "/dwo/session/bye")


class DwoSessionBlocked(AccessDenied):
    """Raised for an RPC of a locked session."""


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    # -- helpers -------------------------------------------------------------------------------------------
    @classmethod
    def _dwo_is_document(cls):
        """True if the browser is loading a page (not a script, an image, an RPC or a websocket)."""
        req = request.httprequest
        if req.method != "GET":
            return False
        if req.headers.get("Sec-Fetch-Mode") == "navigate":   # automated browsers may send Dest "empty" here
            return True
        dest = req.headers.get("Sec-Fetch-Dest")
        if dest:
            return dest in ("document", "iframe", "frame")
        return "text/html" in (req.headers.get("Accept") or "")

    @classmethod
    def _dwo_page_for(cls, state):
        return "/dwo/session/waiting" if state == "pending_approval" else "/dwo/session/locked"

    @classmethod
    def _dwo_gate(cls, endpoint=None):
        sess = request.session
        if not sess.get("uid") or "dwo.session" not in request.env:
            return
        env = request.env
        if not cfg_bool(env, "enabled"):
            return
        row = env["dwo.session"].sudo()._dwo_current()
        if not row:
            return
        path = request.httprequest.path
        allowed = path.startswith(ALLOWED_PREFIX) or path in ALLOWED_PATHS or _is_public_css(path)
        nav = cls._dwo_is_document() and path not in NO_BROWSER_CHECK
        state = row._dwo_apply_rules(nav=nav)
        if state == "active":
            return
        if state == "expired":
            if allowed:
                return
            # an exception rolls the request back and skips the saving of the session: do both here
            sess = request.session
            if sess.get("uid"):
                session_logout(sess)
            get_store().rotate(sess, env)     # saves the signed-out session, drops the old file
            env.cr.commit()
            kind = (endpoint.routing.get("type") if endpoint is not None else "http") or "http"
            if kind in ("json", "jsonrpc"):
                raise SessionExpiredException("dwo_session_expired")
            back = request.httprequest.full_path.rstrip("?")
            response = request.redirect_query("/web/login", {"redirect": back} if cls._dwo_is_document() else {}, 303)
            response.set_cookie("session_id", sess.sid, httponly=True)
            response.headers["Cache-Control"] = "no-store"
            raise werkzeug.exceptions.HTTPException(response=response)
        if allowed:
            return
        kind = (endpoint.routing.get("type") if endpoint is not None else "http") or "http"
        if kind in ("json", "jsonrpc"):
            raise DwoSessionBlocked("dwo_session_%s" % state)
        if cls._dwo_is_document():
            response = request.redirect(cls._dwo_page_for(state), 303)
        else:
            response = request.make_response("Session %s" % state, [("Content-Type", "text/plain")])
            response.status_code = 403
        response.headers["Cache-Control"] = "no-store"
        raise werkzeug.exceptions.HTTPException(response=response)

    # -- hooks ---------------------------------------------------------------------------------------------
    @classmethod
    def _authenticate(cls, endpoint):
        super()._authenticate(endpoint)
        cls._dwo_gate(endpoint)

    @classmethod
    def _serve_fallback(cls):
        # attachments by URL and website pages are served without an authenticated route
        try:
            if request.session.get("uid") and "dwo.session" in request.env and cfg_bool(request.env, "enabled"):
                row = request.env["dwo.session"].sudo()._dwo_current(create=False)
                if row and row.state != "active":
                    return None
        except Exception:
            return None
        return super()._serve_fallback()

    @classmethod
    def _post_dispatch(cls, response):
        super()._post_dispatch(response)
        try:
            if request.session.get("uid") and "dwo.session" in request.env and cfg_bool(request.env, "enabled"):
                mimetype = getattr(response, "mimetype", "") or ""
                if mimetype in ("text/html", "application/json"):
                    response.headers["Cache-Control"] = "no-store"
        except Exception:
            pass
