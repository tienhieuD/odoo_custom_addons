# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""Requests that an administrator has to decide: let a new session in (session approval) or reset a forgotten PIN."""
from datetime import timedelta

from odoo import api, fields, models, release
from odoo.exceptions import AccessError, UserError
from odoo.tools import html_escape

from .util import APPROVER_GROUP, cfg_bool, cfg_int, describe_agent, tr


class DwoSessionRequest(models.Model):
    _name = "dwo.session.request"
    _description = "Session approval / PIN reset request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(compute="_compute_name", store=True)
    kind = fields.Selection([("login", "Session approval"), ("pin_reset", "PIN reset")], required=True, readonly=True)
    user_id = fields.Many2one("res.users", string="User", required=True, ondelete="cascade", readonly=True, index=True)
    session_key = fields.Char(readonly=True, index=True)
    ip = fields.Char("IP address", readonly=True)
    user_agent = fields.Char(readonly=True)
    browser = fields.Char(compute="_compute_browser")
    state = fields.Selection([("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"),
                              ("expired", "Expired"), ("cancelled", "Cancelled")], default="pending", required=True,
                             readonly=True, index=True, tracking=True)
    expires_at = fields.Datetime(readonly=True)
    decided_by = fields.Many2one("res.users", readonly=True)
    decided_at = fields.Datetime(readonly=True)

    @api.depends("kind", "user_id")
    def _compute_name(self):
        labels = dict(self._fields["kind"].selection)
        for rec in self:
            rec.name = "%s - %s" % (labels.get(rec.kind, ""), rec.user_id.name or "")

    @api.depends("user_agent")
    def _compute_browser(self):
        for rec in self:
            rec.browser = describe_agent(rec.user_agent)

    # -- creation ----------------------------------------------------------------------------------------
    @api.model
    def _create_for_session(self, row, kind="login"):
        minutes = cfg_int(self.env, "approval_timeout_min") or 15
        rec = self.sudo().create({
            "kind": kind, "user_id": row.user_id.id, "session_key": row.key, "ip": row.ip,
            "user_agent": row.user_agent, "expires_at": fields.Datetime.now() + timedelta(minutes=minutes),
        })
        self.env["dwo.session.log"].add("approval_request" if kind == "login" else "reset_request", row.user_id)
        rec._notify()
        return rec

    @api.model
    def _create_pin_reset(self, row):
        """Ask the administrators to reset the PIN. One pending request per user, a limit per day."""
        pending = self.sudo().search([("user_id", "=", row.user_id.id), ("kind", "=", "pin_reset"), ("state", "=", "pending")])
        pending._expire_old()
        pending = pending.filtered(lambda r: r.state == "pending")
        if pending:
            row.sudo().approval_id = pending[0]
            return pending[0]
        limit = cfg_int(self.env, "reset_request_limit") or 3
        since = fields.Datetime.now() - timedelta(days=1)
        if self.sudo().search_count([("user_id", "=", row.user_id.id), ("kind", "=", "pin_reset"), ("create_date", ">", since)]) >= limit:
            raise UserError(tr(self.env, "Too many reset requests today. Try again tomorrow or sign in again."))
        rec = self._create_for_session(row, kind="pin_reset")
        row.sudo().approval_id = rec
        return rec

    def _expire_old(self):
        now = fields.Datetime.now()
        for rec in self.filtered(lambda r: r.state == "pending" and r.expires_at and r.expires_at < now):
            rec._expire()

    def _expire(self):
        self.write({"state": "expired", "decided_at": fields.Datetime.now()})
        self._close_activities()

    # -- notification of the approvers ----------------------------------------------------------------------
    def _approvers(self):
        users = self.env["res.users"].sudo().search([("share", "=", False)])
        return users.filtered(lambda u: u.has_group(APPROVER_GROUP) and u != self.user_id)

    def _record_url(self):
        base = self.env["ir.config_parameter"].sudo().get_param("web.base.url", "")
        if release.version_info[0] >= 18:
            return "%s/odoo/dwo.session.request/%s" % (base, self.id)
        return "%s/web#id=%s&model=dwo.session.request&view_type=form" % (base, self.id)

    def _notify(self):
        self.ensure_one()
        approvers = self._approvers()
        what = tr(self.env, "wants to start a session") if self.kind == "login" else tr(self.env, "asks to reset the PIN")
        text = "%s %s (%s, %s)" % (self.user_id.name, what, self.ip or "?", describe_agent(self.user_agent))
        if cfg_bool(self.env, "notify_toast"):
            for user in approvers:
                self.env["bus.bus"]._sendone(user.partner_id, "dwo_session/request",
                                             {"id": self.id, "kind": self.kind, "message": text})
        if cfg_bool(self.env, "notify_email"):
            for user in approvers.filtered("email"):
                self.env["mail.mail"].sudo().create({
                    "subject": tr(self.env, "Session security: %s", text),
                    "body_html": "<p>%s</p><p><a href=\"%s\">%s</a></p>" % (html_escape(text), html_escape(self._record_url()),
                                                                            tr(self.env, "Open the request")),
                    "email_to": user.email, "auto_delete": True,
                })
        if cfg_bool(self.env, "notify_activity"):
            for user in approvers:
                self.activity_schedule("mail.mail_activity_data_todo", summary=text, user_id=user.id)

    def _close_activities(self):
        try:
            self.activity_unlink(["mail.mail_activity_data_todo"])
        except Exception:
            pass

    # -- decisions ---------------------------------------------------------------------------------------
    def _check_decider(self):
        if not self.env.user.has_group(APPROVER_GROUP):
            raise AccessError(tr(self.env, "Only session approvers can decide this request."))
        for rec in self:
            if rec.user_id == self.env.user:
                raise AccessError(tr(self.env, "You cannot decide your own request."))
            if rec.state != "pending":
                raise UserError(tr(self.env, "This request was already decided."))

    def action_approve(self):
        self._check_decider()
        Row = self.env["dwo.session"].sudo()
        for rec in self.sudo():
            rec._expire_old()
            if rec.state != "pending":
                raise UserError(tr(self.env, "This request has expired."))
            rec.write({"state": "approved", "decided_by": self.env.user.id, "decided_at": fields.Datetime.now()})
            row = Row.search([("key", "=", rec.session_key)], limit=1)
            if rec.kind == "login":
                if row and row.state == "pending_approval":
                    row._dwo_activate()
                self.env["dwo.session.log"].add("approved", rec.user_id, note=self.env.user.name)
            else:
                self.env["dwo.user.pin"].clear_pin(rec.user_id.id, must_change=True)
                if row and row.state != "expired":
                    row.can_set_pin = True
                self.env["dwo.session.log"].add("pin_reset", rec.user_id, note="approved by %s" % self.env.user.name,
                                                method="admin")
                rec._mail_user_pin_reset()
            rec._close_activities()
        return True

    def action_reject(self):
        self._check_decider()
        for rec in self.sudo():
            rec.write({"state": "rejected", "decided_by": self.env.user.id, "decided_at": fields.Datetime.now()})
            self.env["dwo.session.log"].add("rejected", rec.user_id, note="%s by %s" % (rec.kind, self.env.user.name))
            row = self.env["dwo.session"].sudo().search([("key", "=", rec.session_key)], limit=1)
            if rec.kind == "login" and row and row.state == "pending_approval":
                row._dwo_expire("rejected", event="rejected")
            rec._close_activities()
        return True

    def _mail_user_pin_reset(self):
        self.ensure_one()
        if self.user_id.email:
            self.env["mail.mail"].sudo().create({
                "subject": tr(self.env, "Your PIN was reset"),
                "body_html": "<p>%s</p>" % html_escape(tr(
                    self.env, "An administrator reset the lock PIN of your account. If you did not ask for it, contact them.")),
                "email_to": self.user_id.email, "auto_delete": True,
            })

    @api.autovacuum
    def _gc_requests(self):
        self.sudo().search([("state", "=", "pending"), ("expires_at", "<", fields.Datetime.now())])._expire()
