# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""The state of every session, kept on the server: active, locked, pending_approval or expired.

The state lives in this table (not in the session file and not in the browser) and is read by the ``ir.http``
hook on every request, so a locked session cannot call anything even with the developer tools open. The row is
found by a random key stored in the session, which survives the rotation of the session id."""
import json
import secrets
import time
from datetime import timedelta

from odoo import api, fields, models, release
from odoo.exceptions import AccessError
from odoo.http import request

from .compat import get_store, session_logout
from .util import APPROVER_GROUP, EXEMPT_GROUP, NEEDS_APPROVAL_GROUP, cfg_bool, cfg_int, describe_agent, safe_path, tr

TOUCH_STEP = 30          # seconds: the last activity is written at most this often
SERVER_LOCK_GRACE = 45   # seconds added to the idle lock on the server, so the browser (which can save the forms) goes first
RELOAD_GRACE = 15        # seconds: a closed tab that comes back (reload) is the same browser


class DwoSession(models.Model):
    _name = "dwo.session"
    _description = "Secure session"
    _order = "last_activity desc, id desc"
    _rec_name = "user_id"

    key = fields.Char(required=True, index=True, readonly=True, copy=False)
    sid = fields.Char("Session id (last)", readonly=True, copy=False)
    user_id = fields.Many2one("res.users", string="User", required=True, ondelete="cascade", index=True, readonly=True)
    state = fields.Selection([
        ("active", "Active"),
        ("locked", "Locked"),
        ("pending_approval", "Waiting for approval"),
        ("expired", "Ended"),
    ], default="active", required=True, index=True, readonly=True)
    login_time = fields.Datetime(default=fields.Datetime.now, readonly=True)
    last_activity = fields.Datetime(default=fields.Datetime.now, readonly=True)
    ip = fields.Char("IP address", readonly=True)
    user_agent = fields.Char(readonly=True)
    browser = fields.Char(compute="_compute_browser")
    return_url = fields.Char(readonly=True)
    lock_reason = fields.Char(readonly=True)
    locked_at = fields.Datetime(readonly=True)
    ended_at = fields.Datetime(readonly=True)
    end_reason = fields.Selection([
        ("logout", "Signed out"),
        ("idle", "Idle too long"),
        ("absolute", "Maximum duration reached"),
        ("browser_closed", "Browser closed"),
        ("forced", "Closed by an administrator"),
        ("pin_failed", "Too many wrong PINs"),
        ("relogin", "Signed in again"),
        ("rejected", "Approval rejected"),
        ("approval_timeout", "Approval timed out"),
    ], readonly=True)
    tabs = fields.Text(readonly=True, help="Browser tabs seen by the heartbeat: {tab: [last seen, closed at]}")
    flash = fields.Char(help="A message for the lock page (kept here, so a link cannot write its own text on the page).")
    can_set_pin = fields.Boolean(readonly=True, help="The user proved who they are and may now choose a new PIN.")
    extended_seconds = fields.Integer(readonly=True)
    extensions = fields.Integer(readonly=True)
    approval_id = fields.Many2one("dwo.session.request", readonly=True, ondelete="set null")
    is_current = fields.Boolean(compute="_compute_is_current")

    if release.version_info[0] >= 19:
        _key_uniq = models.Constraint("unique(key)", "Session key must be unique.")
    else:
        _sql_constraints = [("key_uniq", "unique(key)", "Session key must be unique.")]

    # -- display -------------------------------------------------------------------------------------------
    @api.depends("user_agent")
    def _compute_browser(self):
        for rec in self:
            rec.browser = describe_agent(rec.user_agent)

    def _compute_is_current(self):
        key = request.session.get("dwo_key") if request else None
        for rec in self:
            rec.is_current = bool(key) and rec.key == key

    # -- finding / opening the row of the current request -------------------------------------------------
    @api.model
    def _dwo_current(self, create=True):
        """The row of the current request (created at the first authenticated request of a session)."""
        sess = request.session
        if not sess.get("uid"):
            return self.browse()
        Model = self.sudo()
        key = sess.get("dwo_key")
        row = Model.search([("key", "=", key)], limit=1) if key else Model.browse()
        if row and row.user_id.id != sess.uid:
            row = Model.browse()
        if not row and create:
            row = Model._dwo_open()
        elif row and row.sid != sess.sid and row.state != "expired":
            row.sid = sess.sid
        return row

    def _dwo_is_exempt(self):
        self.ensure_one()
        user = self.user_id
        return user.id == 1 or user.has_group(EXEMPT_GROUP)

    @api.model
    def _dwo_open(self):
        """First authenticated request of a session: record it and decide its first state."""
        sess = request.session
        user = self.env["res.users"].sudo().browse(sess.uid)
        Pin = self.env["dwo.user.pin"]
        state, reason, can_set = "active", False, False
        need_approval = (
            cfg_bool(self.env, "approval_enabled") and user.has_group(NEEDS_APPROVAL_GROUP)
            and not user.has_group("base.group_system") and user.id != 1
        )
        pin = Pin._of(user.id)
        if need_approval:
            state = "pending_approval"
        elif pin and pin.must_change:
            state, reason, can_set = "locked", "must_change", True
        httpreq = request.httprequest
        row = self.create({
            "key": secrets.token_urlsafe(24),
            "sid": sess.sid,
            "user_id": user.id,
            "state": state,
            "lock_reason": reason,
            "can_set_pin": can_set,
            "locked_at": fields.Datetime.now() if state == "locked" else False,
            "ip": httpreq.remote_addr,
            "user_agent": (httpreq.user_agent.string or "")[:250],
            "return_url": False,
        })
        sess["dwo_key"] = row.key
        self.env["dwo.session.log"].add("login", user, note=state if state != "active" else None)
        if need_approval:
            row.approval_id = self.env["dwo.session.request"].sudo()._create_for_session(row)
        return row

    # -- tabs and the closed browser ----------------------------------------------------------------------
    def _tabs(self):
        try:
            return json.loads(self.tabs or "{}")
        except ValueError:
            return {}

    @staticmethod
    def _tab_alive(entry, now, grace):
        seen, closed = entry
        if closed:
            return now - closed <= RELOAD_GRACE
        return now - seen <= grace

    def _browser_ok(self, tab=None, register=False):
        """False if, by the heartbeat of the tabs, the browser was closed since the last time it was seen."""
        self.ensure_one()
        if not cfg_bool(self.env, "close_browser"):
            return True
        now = time.time()
        grace = max(60, cfg_int(self.env, "browser_grace_sec"))
        tabs = self._tabs()
        alive_any = any(self._tab_alive(e, now, grace) for e in tabs.values())
        if not tabs:
            ok = True
        elif tab and tab in tabs:
            ok = self._tab_alive(tabs[tab], now, grace)
        else:
            ok = alive_any
        if ok and register and tab:
            tabs[tab] = [now, 0]
            for name in [n for n, e in tabs.items() if now - max(e) > 86400]:
                tabs.pop(name)
            self.tabs = json.dumps(tabs)
        return ok

    def _tab_closed(self, tab):
        self.ensure_one()
        tabs = self._tabs()
        if tab in tabs:
            tabs[tab] = [tabs[tab][0], time.time()]
            self.tabs = json.dumps(tabs)

    # -- the rules ---------------------------------------------------------------------------------------
    def _dwo_seconds_since(self, value):
        return (fields.Datetime.now() - value).total_seconds() if value else 0

    def _dwo_limits(self):
        """Seconds of each limit that applies to this session (0 = none)."""
        self.ensure_one()
        exempt = self._dwo_is_exempt()
        absolute = cfg_int(self.env, "absolute_min")
        return {
            "lock": 0 if exempt or not cfg_bool(self.env, "lock_enabled") else cfg_int(self.env, "lock_after_min") * 60,
            "idle": 0 if exempt else cfg_int(self.env, "idle_logout_min") * 60,
            "absolute": 0 if exempt or not absolute else absolute * 60 + (self.extended_seconds or 0),
        }

    def _dwo_apply_rules(self, nav=False):
        """Apply the server-side rules (end of session, idle lock, browser closed). Returns the state."""
        self.ensure_one()
        if self.state == "expired":
            return "expired"
        if self.state == "pending_approval":
            req = self.approval_id
            if req and req.state == "pending" and req.expires_at and req.expires_at < fields.Datetime.now():
                req._expire()
                self._dwo_expire("approval_timeout")
            elif req and req.state in ("rejected", "expired", "cancelled"):
                self._dwo_expire("rejected")
            return self.state
        if nav and not self._browser_ok():
            self._dwo_expire("browser_closed", event="browser_closed")
            return "expired"
        lim = self._dwo_limits()
        if lim["absolute"] and self._dwo_seconds_since(self.login_time) > lim["absolute"]:
            self._dwo_expire("absolute")
        elif lim["idle"] and self._dwo_seconds_since(self.last_activity) > lim["idle"]:
            self._dwo_expire("idle")
        elif (self.state == "active" and lim["lock"] and self._dwo_seconds_since(self.last_activity) > lim["lock"] + SERVER_LOCK_GRACE
              and self.env["dwo.user.pin"].has_pin(self.user_id.id)):
            self._dwo_lock(reason="idle")
        return self.state

    # -- transitions -------------------------------------------------------------------------------------
    def _dwo_expire(self, reason, event=None):
        """End the session: mark it, log it and make the session file useless."""
        for rec in self:
            if rec.state == "expired":
                continue
            rec.write({"state": "expired", "ended_at": fields.Datetime.now(), "end_reason": reason, "can_set_pin": False})
            self.env["dwo.session.log"].add(event or ("forced" if reason == "forced" else "expired"), rec.user_id,
                                            note=dict(self._fields["end_reason"].selection).get(reason))
            if request and request.session.get("dwo_key") == rec.key:
                request.dwo_ended = reason
                session_logout(request.session)
            elif rec.sid:
                try:
                    stored = get_store().get(rec.sid)
                    if stored.get("dwo_key") == rec.key:
                        get_store().delete(stored)
                except Exception:   # the file is already gone or the store is not a file system
                    pass

    def _dwo_lock(self, url=None, reason="manual"):
        for rec in self:
            if rec.state != "active":
                continue
            rec.write({"state": "locked", "locked_at": fields.Datetime.now(), "lock_reason": reason,
                       "return_url": safe_path(url) if url else rec.return_url})
            self.env["dwo.session.log"].add("lock", rec.user_id, note=reason)

    def _dwo_activate(self):
        for rec in self:
            rec.write({"state": "active", "lock_reason": False, "can_set_pin": False,
                       "last_activity": fields.Datetime.now()})

    def _dwo_touch(self, idle):
        """The browser tells how many seconds the user has been idle: only this counts as activity."""
        self.ensure_one()
        try:
            idle = max(0.0, min(float(idle), 86400.0))
        except (TypeError, ValueError):
            return
        stamp = fields.Datetime.now() - timedelta(seconds=idle)
        if self.state == "active" and (not self.last_activity or stamp > self.last_activity + timedelta(seconds=TOUCH_STEP)):
            self.last_activity = stamp

    def _dwo_extend(self):
        """Give more time before the maximum duration (when the administrator allows it)."""
        self.ensure_one()
        if not cfg_bool(self.env, "extend_enabled") or self.state != "active":
            return False
        if self.extensions >= (cfg_int(self.env, "extend_max") or 3):
            return False
        self.write({"extended_seconds": self.extended_seconds + (cfg_int(self.env, "extend_min") or 60) * 60,
                    "extensions": self.extensions + 1, "last_activity": fields.Datetime.now()})
        self.env["dwo.session.log"].add("extended", self.user_id)
        return True

    def _dwo_payload(self):
        """What the browser needs to know (no application data)."""
        self.ensure_one()
        lim = self._dwo_limits()
        expires_in, kind = None, None
        if self.state == "active":
            candidates = []
            if lim["absolute"]:
                candidates.append((lim["absolute"] - self._dwo_seconds_since(self.login_time), "absolute"))
            if lim["idle"]:
                candidates.append((lim["idle"] - self._dwo_seconds_since(self.last_activity), "idle"))
            if candidates:
                expires_in, kind = min(candidates)
                expires_in = max(0, int(expires_in))
        has_pin = self.env["dwo.user.pin"].has_pin(self.user_id.id)
        warn = cfg_int(self.env, "warn_min") * 60 if cfg_bool(self.env, "warn_enabled") else 0
        if kind == "idle" and lim["idle"]:
            warn = min(warn, lim["idle"] // 2)
        return {
            "state": self.state,
            "reason": self.end_reason or False,
            "lock_after": lim["lock"] if has_pin else 0,
            "can_lock": has_pin,
            "expires_in": expires_in,
            "expires_kind": kind,
            "warn": warn,
            "extend": bool(cfg_bool(self.env, "extend_enabled") and kind == "absolute"
                           and self.extensions < (cfg_int(self.env, "extend_max") or 3)),
            "interval": 30,
            "save_before_lock": cfg_bool(self.env, "save_before_lock"),
            "can_set_pin": bool(self.can_set_pin),
            "reset": self.approval_id.state if self.approval_id and self.approval_id.kind == "pin_reset" else False,
        }

    # -- administration ----------------------------------------------------------------------------------
    def action_force_logout(self):
        if not self.env.user.has_group("base.group_system") and any(r.user_id != self.env.user for r in self):
            raise AccessError(tr(self.env, "Only administrators can close the sessions of other users."))
        mine = self.sudo().filtered(lambda r: r.state != "expired")
        mine._dwo_expire("forced")
        return True

    @api.autovacuum
    def _gc_sessions(self):
        """End the sessions nobody uses any more and drop old rows (the session files are removed by Odoo)."""
        now = fields.Datetime.now()
        stale = max(cfg_int(self.env, "idle_logout_min") * 2, 60 * 24 * 8)   # minutes
        for rec in self.sudo().search([("state", "!=", "expired"), ("last_activity", "<", now - timedelta(minutes=stale))]):
            rec._dwo_expire("idle")
        self.sudo().search([("state", "=", "expired"), ("ended_at", "<", now - timedelta(days=30))]).unlink()
