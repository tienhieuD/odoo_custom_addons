# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import http
from odoo.exceptions import UserError
from odoo.http import request

from odoo.addons.dwo_session_security.models.util import JSON, cfg_bool, safe_path, tr

from . import pages

NO_STORE = [("Cache-Control", "no-store"), ("Pragma", "no-cache")]


def _env():
    return request.env


def _row():
    """The row of the current session, or an empty recordset (not signed in, or the module is off)."""
    if not request.session.get("uid"):
        return _env()["dwo.session"].browse()
    return _env()["dwo.session"].sudo()._dwo_current(create=False)


def _html(content):
    return request.make_response(content, [("Content-Type", "text/html; charset=utf-8")] + NO_STORE)


def _go(url):
    response = request.redirect(url, 303)
    response.headers["Cache-Control"] = "no-store"
    return response


def _login_redirect(url=None):
    return request.redirect_query("/web/login", {"redirect": safe_path(url)} if url else {}, 303)


def _back(row, kind, text, otp=False):
    """Come back to the lock page with a message (kept on the server: a link cannot put its own text on the page)."""
    row.flash = "%s|%s" % (kind, text)
    return _go("/dwo/session/locked" + ("?otp=1" if otp else ""))


class DwoSessionController(http.Controller):

    # -- used by the web client and by the two pages (JSON) ---------------------------------------------
    @http.route("/dwo/session/heartbeat", type=JSON, auth="public")
    def heartbeat(self, tab=None, idle=None, **kw):
        row = _row()
        if not row:
            return {"state": "expired", "reason": getattr(request, "dwo_ended", False)}
        tab = str(tab)[:64] if tab else None
        if row.state != "expired" and not row._browser_ok(tab, register=True):
            row._dwo_expire("browser_closed", event="browser_closed")
        if row.state != "expired":
            row._dwo_apply_rules()
        if row.state == "active" and idle is not None:
            row._dwo_touch(idle)
        return row._dwo_payload()

    @http.route("/dwo/session/lock", type=JSON, auth="public")
    def lock(self, url=None, reason="manual", **kw):
        row = _row()
        if not row or row.state != "active":
            return {"state": row.state if row else "expired"}
        if not _env()["dwo.user.pin"].has_pin(row.user_id.id):
            return {"state": "active", "error": "no_pin"}
        row._dwo_lock(url, "idle" if reason == "idle" else "manual")
        return {"state": row.state}

    @http.route("/dwo/session/extend", type=JSON, auth="public")
    def extend(self, **kw):
        row = _row()
        if not row or row.state != "active":
            return {"state": row.state if row else "expired"}
        done = row._dwo_extend()
        payload = row._dwo_payload()
        payload["extended"] = bool(done)
        return payload

    @http.route("/dwo/session/bye", type=JSON, auth="public")
    def bye(self, tab=None, **kw):
        row = _row()
        if row and tab:
            row._tab_closed(str(tab)[:64])
        return True

    # -- pages -------------------------------------------------------------------------------------------------
    @http.route("/dwo/session/locked", type="http", auth="public", methods=["GET"])
    def locked_page(self, otp=None, **kw):
        row = _row()
        if not row or row.state == "expired":
            return _go("/web/login")
        if row.state == "active":
            return _go("/dwo/session/resume")
        if row.state == "pending_approval":
            return _go("/dwo/session/waiting")
        flash = row.flash or ""
        if flash:
            row.flash = False
        kind, _sep, text = flash.partition("|")
        return _html(pages.lock_page(_env(), row, request.csrf_token(), text if kind == "err" else None,
                                     text if kind == "ok" else None, otp=bool(otp)))

    @http.route("/dwo/session/waiting", type="http", auth="public", methods=["GET"])
    def waiting_page(self, **kw):
        row = _row()
        if not row or row.state == "expired":
            return _go("/web/login")
        if row.state == "active":
            return _go("/dwo/session/resume")
        if row.state == "locked":
            return _go("/dwo/session/locked")
        return _html(pages.waiting_page(_env(), row))

    @http.route("/dwo/session/resume", type="http", auth="public", methods=["GET"])
    def resume(self, **kw):
        """Back to the screen the user was on (the address is kept on the server, not in the page)."""
        row = _row()
        if not row or row.state == "expired":
            return _go("/web/login")
        if row.state != "active":
            return _go("/dwo/session/waiting" if row.state == "pending_approval" else "/dwo/session/locked")
        return _go(safe_path(row.return_url))

    @http.route("/dwo/session/relogin", type="http", auth="public", methods=["GET"])
    def relogin(self, r=None, **kw):
        """Sign in again through the normal login page (password, SSO, 2FA), then come back to the screen."""
        row = _row()
        url = r or (row.return_url if row else None)
        if row and row.state == "active":
            return _go("/web")
        if row and row.state == "locked":
            if cfg_bool(_env(), "forgot_relogin"):
                if cfg_bool(_env(), "force_new_pin_after_relogin"):
                    pin = _env()["dwo.user.pin"]._of(row.user_id.id)
                    if pin.pin_hash:
                        pin.must_change = True
                row._dwo_expire("relogin")
            else:
                return _go("/dwo/session/locked")
        elif row and row.state == "pending_approval":
            row._dwo_expire("relogin")
        elif request.session.get("uid"):
            request.session.logout(keep_db=True)
        response = _login_redirect(url)
        response.headers["Cache-Control"] = "no-store"
        return response

    # -- forms of the lock page (POST, CSRF protected by Odoo) -------------------------------------------------
    def _locked_row(self):
        row = _row()
        return row if row and row.state == "locked" else None

    @http.route("/dwo/session/unlock", type="http", auth="public", methods=["POST"], csrf=True)
    def unlock(self, pin="", **kw):
        row = self._locked_row()
        if not row:
            return _go("/dwo/session/resume")
        env = _env()
        rec = env["dwo.user.pin"]._of(row.user_id.id)
        if not rec or row.can_set_pin:
            return _go("/dwo/session/locked")
        if rec.seconds_locked():
            return _back(row, "err", tr(env, "Too many wrong PINs. Wait a moment."))
        if rec.verify_pin((pin or "").strip()):
            rec.register_success()
            env["dwo.session.log"].add("unlock", row.user_id)
            if rec.must_change:
                row.write({"can_set_pin": True, "lock_reason": "must_change"})
                return _go("/dwo/session/locked")
            row._dwo_activate()
            return _go("/dwo/session/resume")
        return self._wrong(row, rec, "wrong")

    def _wrong(self, row, rec, error):
        env = _env()
        left, cooldown, too_many = rec.register_failure()
        env["dwo.session.log"].add("unlock_fail", row.user_id, note="%s left" % left)
        if too_many:
            row._dwo_expire("pin_failed")
            return _login_redirect()
        text = tr(env, "Too many wrong PINs. Wait a moment.") if cooldown else (
            tr(env, "Wrong password.") if error == "pwd" else tr(env, "Wrong PIN."))
        return _back(row, "err", text)

    @http.route("/dwo/session/unlock_password", type="http", auth="public", methods=["POST"], csrf=True)
    def unlock_password(self, password="", **kw):
        row = self._locked_row()
        env = _env()
        if not row or not cfg_bool(env, "forgot_relogin"):
            return _go("/dwo/session/resume")
        rec = env["dwo.user.pin"]._of(row.user_id.id, create=True)
        if rec.seconds_locked():
            return _back(row, "err", tr(env, "Too many wrong PINs. Wait a moment."))
        if row.user_id._dwo_check_password(password):
            rec.register_success()
            env["dwo.session.log"].add("unlock", row.user_id, note="password", method="password")
            if cfg_bool(env, "force_new_pin_after_relogin") or not rec.pin_hash:
                row.write({"can_set_pin": True, "lock_reason": "password"})
                return _go("/dwo/session/locked")
            row._dwo_activate()
            return _go("/dwo/session/resume")
        return self._wrong(row, rec, "pwd")

    @http.route("/dwo/session/setpin", type="http", auth="public", methods=["POST"], csrf=True)
    def setpin(self, pin="", pin2="", **kw):
        row = self._locked_row()
        if not row or not row.can_set_pin:
            return _go("/dwo/session/resume")
        env = _env()
        if pin != pin2:
            return _back(row, "err", tr(env, "The two PINs are different."))
        try:
            env["dwo.user.pin"].set_pin(row.user_id.id, pin)
        except UserError as exc:
            return _back(row, "err", str(exc.args[0]))
        env["dwo.session.log"].add("pin_set", row.user_id, method="lock page")
        row._dwo_activate()
        return _go("/dwo/session/resume")

    @http.route("/dwo/session/request_reset", type="http", auth="public", methods=["POST"], csrf=True)
    def request_reset(self, **kw):
        row = self._locked_row()
        if not row or not cfg_bool(_env(), "forgot_admin"):
            return _go("/dwo/session/resume")
        try:
            _env()["dwo.session.request"].sudo()._create_pin_reset(row)
        except UserError as exc:
            return _back(row, "err", str(exc.args[0]))
        return _back(row, "ok", tr(_env(), "The administrators were notified."))

    @http.route("/dwo/session/send_otp", type="http", auth="public", methods=["POST"], csrf=True)
    def send_otp(self, **kw):
        row = self._locked_row()
        env = _env()
        if not row or not cfg_bool(env, "forgot_otp") or not row.user_id.email:
            return _go("/dwo/session/resume")
        pin = env["dwo.user.pin"]._of(row.user_id.id, create=True)
        try:
            code = pin.new_otp()
        except UserError as exc:
            return _back(row, "err", str(exc.args[0]))
        env["mail.mail"].sudo().create({
            "subject": tr(env, "Your PIN code"), "email_to": row.user_id.email, "auto_delete": True,
            "body_html": "<p>%s</p><p style=\"font-size:24px;letter-spacing:4px\"><b>%s</b></p>" % (
                tr(env, "Use this code to choose a new PIN. It is valid for 10 minutes."), code),
        })
        env["dwo.session.log"].add("otp_sent", row.user_id)
        return _back(row, "ok", tr(env, "A code was sent to your email."), otp=True)

    @http.route("/dwo/session/verify_otp", type="http", auth="public", methods=["POST"], csrf=True)
    def verify_otp(self, code="", **kw):
        row = self._locked_row()
        env = _env()
        if not row or not cfg_bool(env, "forgot_otp"):
            return _go("/dwo/session/resume")
        pin = env["dwo.user.pin"]._of(row.user_id.id, create=True)
        if pin.seconds_locked():
            return _back(row, "err", tr(env, "Too many wrong PINs. Wait a moment."), otp=True)
        if pin.check_otp(code):
            env["dwo.session.log"].add("pin_reset", row.user_id, note="code by email", method="otp")
            row.write({"can_set_pin": True, "lock_reason": "otp"})
            return _go("/dwo/session/locked")
        left, cooldown, too_many = pin.register_failure()
        if too_many:
            row._dwo_expire("pin_failed")
            return _login_redirect()
        return _back(row, "err", tr(env, "Wrong or expired code."), otp=True)
