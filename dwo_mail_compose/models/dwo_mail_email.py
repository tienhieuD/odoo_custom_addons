# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo import api, fields, models, tools
from odoo.exceptions import AccessError, UserError

ACTIVITY_XMLID = "dwo_mail_compose.mail_activity_type_email_approval"
UNSENT = ("draft", "pending", "rejected")
CONTENT_FIELDS = {
    "mode", "ref_message_id", "email_from", "to_json", "cc_json", "bcc_json", "reply_to",
    "reply_to_custom", "subject", "body", "template_id", "attachment_ids",
}
STATES = [
    ("draft", "Draft"),
    ("pending", "Waiting for approval"),
    ("rejected", "Rejected"),
    ("sent", "Approved and sent"),
]


class DwoMailEmail(models.Model):
    """An email written in the chatter and kept until it leaves.

    It is a draft while it is being written, waits for approval when the author asks for it,
    and is kept as "sent" once an approver approved it and it left. An email sent directly by
    its author does not stay (the message in the chatter is the record). Whatever the state,
    an email nobody touched for the retention period (setting, 180 days by default) is deleted.
    """
    _name = "dwo.mail.email"
    _description = "Email Composed in the Chatter"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "last_action_date desc, id desc"
    # an approver only reads the email: let them write a note in its chatter
    _mail_post_access = "read"

    user_id = fields.Many2one(
        "res.users", "Author", required=True, index=True, ondelete="cascade",
        default=lambda self: self.env.user)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        help="Company the email is sent in: it also decides if an approval is required.")
    res_model = fields.Char("Record model", required=True, index=True)
    res_id = fields.Many2oneReference("Record", model_field="res_model", required=True, index=True)
    record_name = fields.Char(compute="_compute_record_name")
    state = fields.Selection(STATES, default="draft", required=True, index=True, tracking=True)
    approver_ids = fields.Many2many(
        "res.users", "dwo_mail_email_approver_rel", "email_id", "user_id", string="Approvers",
        help="Anyone of them can approve; the first decision counts.")
    approver_history_ids = fields.Many2many(
        "res.users", "dwo_mail_email_history_rel", "email_id", "user_id",
        help="Everyone who has been an approver: they keep the right to read the email.")
    request_comment = fields.Text()
    request_date = fields.Datetime()
    decision_comment = fields.Text()
    decision_date = fields.Datetime()
    decided_by_id = fields.Many2one("res.users")
    content_edited_at = fields.Datetime(help="Last time the author changed the email while it waited for approval.")
    edited_after_request = fields.Boolean(compute="_compute_edited_after_request")
    last_action_date = fields.Datetime(
        default=fields.Datetime.now, index=True,
        help="Last time something happened to the email. The email is deleted after the retention period.")
    sent_message_id = fields.Many2one("mail.message", ondelete="set null")

    # content
    mode = fields.Selection([("new", "New"), ("reply", "Reply"), ("forward", "Forward")], default="new")
    ref_message_id = fields.Integer(help="The message this email answers or forwards.")
    email_from = fields.Char()
    to_json = fields.Json(default=list)
    cc_json = fields.Json(default=list)
    bcc_json = fields.Json(default=list)
    reply_to = fields.Char()
    reply_to_custom = fields.Boolean(help="The author changed the Reply-To. Otherwise it follows the record.")
    subject = fields.Char()
    body = fields.Html(sanitize_style=True)
    template_id = fields.Many2one("mail.template", ondelete="set null")
    attachment_ids = fields.Many2many("ir.attachment", relation="dwo_mail_email_attachment_rel")

    # display only
    to_display = fields.Char(compute="_compute_display_values")
    cc_display = fields.Char(compute="_compute_display_values")
    bcc_display = fields.Char(compute="_compute_display_values")
    attachments_summary = fields.Char(compute="_compute_display_values")
    is_author = fields.Boolean(compute="_compute_current_user_flags")
    is_approver = fields.Boolean(compute="_compute_current_user_flags")
    can_open_record = fields.Boolean(compute="_compute_current_user_flags")

    # ------------------------------------------------------------
    # COMPUTES
    # ------------------------------------------------------------

    @api.depends("subject")
    def _compute_display_name(self):
        for email in self:
            email.display_name = email.subject or self.env._("(No subject)")

    @api.depends("res_model", "res_id")
    def _compute_record_name(self):
        for email in self:
            try:
                record = self.env[email.res_model].sudo().browse(email.res_id).exists()
                email.record_name = record.display_name if record else False
            except KeyError:
                email.record_name = False

    @api.depends("content_edited_at")
    def _compute_edited_after_request(self):
        # the request resets content_edited_at: a value means the author edited after it
        for email in self:
            email.edited_after_request = bool(email.content_edited_at)

    @api.depends("to_json", "cc_json", "bcc_json", "attachment_ids")
    def _compute_display_values(self):
        composer = self.env["dwo.mail.composer"]
        for email in self:
            email.to_display = composer._format_list(email.to_json or [])
            email.cc_display = composer._format_list(email.cc_json or [])
            email.bcc_display = composer._format_list(email.bcc_json or [])
            # sudo: an approver may not read the files of the record, but sees their names
            email.attachments_summary = ", ".join(email.sudo().attachment_ids.mapped("name"))

    @api.depends_context("uid")
    def _compute_current_user_flags(self):
        for email in self:
            email.is_author = email.user_id == self.env.user
            email.is_approver = self.env.user in email.approver_ids
            try:
                self.env[email.res_model].browse(email.res_id).check_access("read")
                email.can_open_record = True
            except Exception:  # noqa: BLE001 - no access, or the record is gone
                email.can_open_record = False

    # ------------------------------------------------------------
    # ORM
    # ------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        return super(DwoMailEmail, self.with_context(
            mail_create_nosubscribe=True, mail_create_nolog=True)).create(vals_list)

    def write(self, vals):
        vals = dict(vals)
        vals.setdefault("last_action_date", fields.Datetime.now())
        watched = self.env["dwo.mail.email"]
        if CONTENT_FIELDS & vals.keys() and "content_edited_at" not in vals:
            watched = self.filtered(lambda email: email.state in ("pending", "rejected"))
        result = super().write(vals)
        if watched:
            super(DwoMailEmail, watched).write({"content_edited_at": fields.Datetime.now()})
        return result

    @api.autovacuum
    def _gc_old_emails(self):
        """Whatever its state, an email nobody touched for the retention period is deleted."""
        days = int(self.env["ir.config_parameter"].sudo().get_param("dwo_mail_compose.retention_days") or 0)
        if days <= 0:
            days = 180
        limit = fields.Datetime.subtract(fields.Datetime.now(), days=days)
        self.sudo().search([("last_action_date", "<", limit)]).unlink()

    # ------------------------------------------------------------
    # DICTS FOR THE WEB CLIENT
    # ------------------------------------------------------------

    def _dwo_summary(self):
        self.ensure_one()
        return {
            "id": self.id,
            "subject": self.subject or "",
            "state": self.state,
            "approvers": self.approver_ids.mapped("name"),
            "created": fields.Datetime.to_string(self.create_date),
            # the last time something happened to it (edit, state change, decision)
            "updated": fields.Datetime.to_string(self.last_action_date),
        }

    def _dwo_to_dict(self):
        self.ensure_one()
        return {
            "id": self.id,
            "state": self.state,
            "mode": self.mode,
            "ref_message_id": self.ref_message_id or False,
            "from": self.email_from or "",
            "to": self.to_json or [],
            "cc": self.cc_json or [],
            "bcc": self.bcc_json or [],
            "reply_to": self.reply_to or "",
            "reply_to_custom": self.reply_to_custom,
            "subject": self.subject or "",
            "body": self.body or "",
            "template_id": self.template_id.id or False,
            "template_name": self.template_id.display_name or "",
            "attachments": [
                {"id": a.id, "name": a.name, "mimetype": a.mimetype, "size": a.file_size}
                for a in self.attachment_ids
            ],
            "saved_at": fields.Datetime.to_string(self.write_date),
            "approvers": [{"id": u.id, "name": u.name} for u in self.approver_ids],
            "request_comment": self.request_comment or "",
            "decision_comment": self.decision_comment or "",
            "decided_by": self.decided_by_id.name or "",
            "edited_after_request": self.edited_after_request,
        }

    def _dwo_send_vals(self):
        """The values the composer needs to send this email."""
        self.ensure_one()
        return {
            "from": self.email_from,
            "to": self.to_json,
            "cc": self.cc_json,
            "bcc": self.bcc_json,
            "reply_to": self.reply_to,
            "reply_to_custom": self.reply_to_custom,
            "subject": self.subject,
            "body": self.body or "",
            "attachment_ids": self.attachment_ids.ids,
            "ref_message_id": self.ref_message_id or False,
        }

    # ------------------------------------------------------------
    # LOCK AND CHECKS
    # ------------------------------------------------------------

    def _lock(self, states):
        """Take the row lock, then read the state again: two approvers, or an approver and the
        author sending directly, can reach the same email at the same time, and only the first
        one may act."""
        self.ensure_one()
        self.flush_recordset()
        self.env.cr.execute("SELECT state FROM dwo_mail_email WHERE id = %s FOR UPDATE", [self.id])
        if not self.env.cr.fetchone():
            raise UserError(self.env._("This email does not exist anymore."))
        self.invalidate_recordset()
        if self.state not in states:
            label = dict(self._fields["state"].selection)[self.state]
            raise UserError(self.env._(
                "This email cannot be changed this way anymore: it is now %(state)s.", state=self.env._(label)))

    def _check_approver(self):
        self.ensure_one()
        if self.env.user not in self.approver_ids:
            raise AccessError(self.env._("You are not an approver of this email."))

    def _check_author(self):
        self.ensure_one()
        if self.user_id != self.env.user:
            raise AccessError(self.env._("Only the author of the email can do this."))

    # ------------------------------------------------------------
    # ACTIVITIES, LOG, NOTIFICATION
    # ------------------------------------------------------------

    def _schedule_activities(self, users, comment=None):
        summary = self.env._("Approve the email: %s", self.display_name)
        for user in users:
            # no email for the assignment: the approval notice below carries the details
            self.sudo().with_context(mail_activity_quick_update=True).activity_schedule(
                ACTIVITY_XMLID, user_id=user.id, summary=summary, note=comment or False)

    def _close_activities(self, users=None, feedback=""):
        """Mark the approval activities as done."""
        activity_type = self.env.ref(ACTIVITY_XMLID)
        activities = self.sudo().activity_ids.filtered(
            lambda a: a.activity_type_id == activity_type and (not users or a.user_id in users))
        if activities:
            activities._action_done(feedback=feedback)

    def _log(self, text, comment=None):
        body = Markup("<p>%s</p>") % text
        if comment:
            body += Markup("<blockquote>%s</blockquote>") % comment
        self.sudo().message_post(
            body=body, subtype_xmlid="mail.mt_note", author_id=self.env.user.partner_id.id)

    def _notify(self, users, kind, title, text, comment=None):
        """Tell users with an email (their notification preference decides between the inbox
        and the email) and a message on the screen. The person who acts is not told about it."""
        users = (users - self.env.user).filtered("active")
        if not users:
            return
        body = Markup("<p>%s</p>") % text
        if comment:
            body += Markup("<p><i>%s</i></p>") % comment
        self.sudo().message_notify(
            partner_ids=users.partner_id.ids, subject=title, body=body,
            author_id=self.env.user.partner_id.id, email_layout_xmlid="mail.mail_notification_light")
        payload = {
            "kind": kind, "email_id": self.id, "title": title, "message": text,
            "comment": comment or "", "subject": self.display_name,
        }
        for user in users:
            user._bus_send("dwo_mail_approval", payload)

    # ------------------------------------------------------------
    # WORKFLOW
    # ------------------------------------------------------------

    def request_approval(self, approvers, comment=None):
        """The author asks one or several people to approve and send. Anyone of them can."""
        self.ensure_one()
        self._check_author()
        if not approvers:
            raise UserError(self.env._("Choose at least one approver."))
        self._lock(UNSENT)
        self._close_activities(feedback=self.env._("Replaced by a new request"))
        self.sudo().write({
            "state": "pending",
            "approver_ids": [(6, 0, approvers.ids)],
            "approver_history_ids": [(4, user.id) for user in approvers],
            "request_comment": comment or False,
            "request_date": fields.Datetime.now(),
            "content_edited_at": False,
            "decision_comment": False,
            "decision_date": False,
            "decided_by_id": False,
        })
        self._schedule_activities(approvers, comment)
        names = ", ".join(approvers.mapped("name"))
        self._log(self.env._("Approval requested from %s.", names), comment)
        self._notify(
            approvers, "request", self.env._("Email waiting for your approval"),
            self.env._("%(author)s asks you to approve and send the email: %(subject)s",
                       author=self.user_id.name, subject=self.display_name),
            comment)

    def _send_as_author(self):
        """The email leaves as if its author sent it: their address, their rights, their company."""
        self.ensure_one()
        composer = self.env["dwo.mail.composer"].with_user(self.user_id).with_company(self.company_id)
        return composer._send_email(self.res_model, self.res_id, self._dwo_send_vals())

    def action_approve(self, comment=None):
        """Approve and send. The first decision wins."""
        self.ensure_one()
        self._lock(("pending",))
        self._check_approver()
        if self.env.user == self.user_id and not self.company_id.dwo_mail_allow_self_approval:
            raise UserError(self.env._("You cannot approve your own email."))
        message = self._send_as_author()
        self.sudo().write({
            "state": "sent",
            "sent_message_id": message.id,
            "decision_comment": comment or False,
            "decision_date": fields.Datetime.now(),
            "decided_by_id": self.env.user.id,
        })
        self._close_activities(feedback=self.env._("Approved by %s", self.env.user.name))
        self._log(self.env._("Approved by %s. The email was sent.", self.env.user.name), comment)
        self._notify(
            self.user_id, "approved", self.env._("Your email was approved and sent"),
            self.env._("%(approver)s approved the email: %(subject)s", approver=self.env.user.name,
                       subject=self.display_name),
            comment)

    def action_reject(self, comment=None):
        self.ensure_one()
        self._lock(("pending",))
        self._check_approver()
        self.sudo().write({
            "state": "rejected",
            "decision_comment": comment or False,
            "decision_date": fields.Datetime.now(),
            "decided_by_id": self.env.user.id,
        })
        self._close_activities(feedback=self.env._("Rejected by %s", self.env.user.name))
        self._log(self.env._("Rejected by %s.", self.env.user.name), comment)
        self._notify(
            self.user_id, "rejected", self.env._("Your email was rejected"),
            self.env._("%(approver)s rejected the email: %(subject)s", approver=self.env.user.name,
                       subject=self.display_name),
            comment)

    def action_reassign(self, users, comment=None):
        """Hand the approval to other people. Only the approver who acts leaves; the others stay."""
        self.ensure_one()
        users = users.filtered(lambda user: user.active and not user.share)
        if not users:
            raise UserError(self.env._("Choose who takes over."))
        self._lock(("pending",))
        self._check_approver()
        self.env["dwo.mail.composer"]._dwo_validate_approvers(users, self.user_id, self.company_id)
        actor = self.env.user
        new_users = users - self.approver_ids
        self.sudo().write({
            "approver_ids": [(6, 0, ((self.approver_ids - actor) | users).ids)],
            "approver_history_ids": [(4, user.id) for user in users],
        })
        if actor not in users:
            self._close_activities(users=actor, feedback=self.env._("Reassigned by %s", actor.name))
        self._schedule_activities(new_users, comment)
        self._log(self.env._("%(actor)s reassigned the approval to %(users)s.",
                             actor=actor.name, users=", ".join(users.mapped("name"))), comment)
        self._notify(
            new_users, "request", self.env._("Email waiting for your approval"),
            self.env._("%(actor)s asks you to approve and send the email: %(subject)s",
                       actor=actor.name, subject=self.display_name),
            comment)
        self._notify(
            self.user_id, "reassigned", self.env._("Your email was handed to other approvers"),
            self.env._("%(actor)s handed the approval of %(subject)s to %(users)s.",
                       actor=actor.name, subject=self.display_name, users=", ".join(users.mapped("name"))),
            comment)

    def _close_request(self, text):
        """The author sends the email directly, or deletes it, while approvers still wait."""
        self.ensure_one()
        if self.state == "pending":
            self._close_activities(feedback=text)
            self._notify(
                self.approver_ids, "closed", self.env._("Email approval closed"),
                self.env._("%(author)s: %(text)s (%(subject)s)", author=self.user_id.name, text=text,
                           subject=self.display_name))

    def _close_after_direct_send(self):
        """The author sent it directly: whoever waited is told and the stored copy goes away."""
        self._close_request(self.env._("the email was sent directly, no approval needed anymore"))
        self.sudo().unlink()

    def _withdraw_and_unlink(self):
        self._lock(UNSENT)
        self._close_request(self.env._("the email was deleted by its author"))
        self.sudo().unlink()

    # ------------------------------------------------------------
    # BUTTONS OF THE FORM
    # ------------------------------------------------------------

    def _decision_wizard(self, decision, title):
        self.ensure_one()
        self._check_approver()
        return {
            "type": "ir.actions.act_window",
            "name": title,
            "res_model": "dwo.mail.decision",
            "view_mode": "form",
            "target": "new",
            "context": {"default_email_id": self.id, "default_decision": decision, "dialog_size": "medium"},
        }

    def action_open_approve(self):
        return self._decision_wizard("approve", self.env._("Approve and send"))

    def action_open_reject(self):
        return self._decision_wizard("reject", self.env._("Reject"))

    def action_open_reassign(self):
        return self._decision_wizard("reassign", self.env._("Reassign"))

    def action_open_record(self):
        self.ensure_one()
        record = self.env[self.res_model].browse(self.res_id)
        record.check_access("read")
        return {
            "type": "ir.actions.act_window",
            "res_model": self.res_model,
            "res_id": self.res_id,
            "view_mode": "form",
            "views": [(False, "form")],
            "target": "current",
        }
