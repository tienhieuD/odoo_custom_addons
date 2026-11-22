# -*- coding: utf-8 -*-
"""v2.0 of the flow: tell people when a document needs them, and what became of it.

Everything is set on the arrows (and nothing is sent until an arrow asks for it, so upgrading never
sends a mail by itself):

* Who: "Notify the approvers" with three channels, a system notification (bus), an Odoo activity and an
  email (an inbox message, according to the preference of the user). The people are worked out when the
  document enters the step the arrow starts from, with the same check as the real buttons.
* Followers: one note with the subtype "Approval", so only the followers who subscribed to it are told.
* Creator: the person who created the document is told when somebody presses the arrow or votes.
* A cron reminds the approvers who did not answer; "Waiting for my approval" lists the open requests.
* Every try is written in ``dwo.approval.notify.log``. A failing channel never blocks an approval.
"""
import logging
from datetime import timedelta

from markupsafe import Markup

from odoo import api, fields, models

from .expression import eval_expression
from .flow import CHANNELS

_logger = logging.getLogger(__name__)

ACTIVITY_XMLID = "dwo_approval_flow.mail_activity_type_to_approve"
SUBTYPE_XMLID = "dwo_approval_flow.mt_approval"
CRON_BATCH = 200


class DwoApprovalFlowNotify(models.Model):
    _inherit = "dwo.approval.flow"

    notify_template_id = fields.Many2one(
        "mail.template", string="Email template", ondelete="set null",
        domain="[('model_id', '=', model_id)]",
        help="Your own mail template for the email to the approvers. Empty: the default text.")
    remind_after = fields.Integer(
        string="Remind after (hours)", help="Remind approvers who did not answer after this many hours. 0: never.")
    remind_max = fields.Integer(string="Reminders at most", default=3)

    # ------------------------------------------------------------------
    # after an arrow was pressed
    # ------------------------------------------------------------------
    def _notify_after_press(self, record, transition, actor, outcome, reason):
        """Called by ``dwo.approval.transition._press`` once the press is done (nothing raised)."""
        self.ensure_one()
        Pending = self.env["dwo.approval.pending"].sudo()
        waiting = outcome.get("status") == "waiting"
        domain = [("res_model", "=", record._name), ("res_id", "=", record.id)]
        if waiting:
            domain.append(("user_id", "=", actor.id))
        Pending.search(domain)._close()
        if hasattr(record, "activity_unlink"):  # also the activities nobody listed (followers)
            record.sudo().activity_unlink([ACTIVITY_XMLID], user_id=actor.id if waiting else None)
        if waiting:
            if transition.notify_creator:
                self._notify_creator(record, actor, transition, reason, "%s/%s" % (
                    outcome.get("count"), outcome.get("needed")))
            return
        current = self._current_state(record)
        if current != transition.to_state_id:
            return  # a wizard opened: the document has not moved yet
        if transition.notify_creator:
            self._notify_creator(record, actor, transition, reason)
        arrows = self._notify_arrows(current)
        if arrows:
            self._notify_arrived(record, current, actor, reason, arrows)

    def _notify_arrows(self, current):
        """The arrows that start from ``current`` (or from any state) and ask to notify somebody."""
        self.ensure_one()
        return self.transition_ids.filtered(
            lambda t: (t._notifies_approvers() or t._notifies_followers())
            and (t.from_state_id == current or (not t.from_state_id and t.to_state_id != current)))

    # ------------------------------------------------------------------
    # the document reached a step: approvers and followers
    # ------------------------------------------------------------------
    def _notify_recipients(self, record, arrows, actor):
        """``{user: set of channels}``: who can press, right now, an arrow whose approver line ticks a channel.

        The people are collected from each approver line (the ticks of the matrix of the "Who" dialog are
        on the line), then every one is tested with the check of the real buttons, so a person is told
        only when the button will really be there. An arrow that anybody can press tells nobody (it would
        be every employee).
        """
        self.ensure_one()
        found = {}
        for tr in arrows:
            for line in tr.approver_ids:
                channels = line._notify_channels()
                if not channels:
                    continue
                for user in line._notify_candidates(record, actor):
                    if user == actor or not user.active or user.share:
                        continue
                    if user not in found and not record.with_user(user).has_access("read"):
                        continue
                    if tr._check_available(record, user)[0]:
                        found.setdefault(user, set()).update(channels)
        return found

    def _notify_follower_users(self, record, actor):
        """Internal users who follow the document with the subtype "Approval"."""
        subtype = self.env.ref(SUBTYPE_XMLID, raise_if_not_found=False)
        if not subtype or not hasattr(record, "message_follower_ids"):
            return self.env["res.users"]
        followers = record.sudo().message_follower_ids.filtered(lambda f: subtype in f.subtype_ids)
        users = followers.partner_id.user_ids.filtered(lambda u: u.active and not u.share and u != actor)
        return users.filtered(lambda u: record.with_user(u).has_access("read"))

    def _notify_arrived(self, record, current, actor, reason, arrows):
        recipients = self._notify_recipients(record, arrows, actor)
        approvers = self.env["res.users"].union(*recipients)
        subject, text, body = self._notify_texts(record, actor, current, reason)
        follower_channels = {c for tr in arrows for c in CHANNELS if tr["notify_followers_" + c]}
        per_user = {user: set(channels) for user, channels in recipients.items()}
        if follower_channels & {"bus", "activity"}:
            for user in self._notify_follower_users(record, actor):
                per_user.setdefault(user, set()).update(follower_channels & {"bus", "activity"})
        activities = {}
        for user, channels in per_user.items():
            kind = "approver" if user in recipients else "followers"
            if "activity" in channels and hasattr(record, "activity_schedule"):
                activities[user] = self._notify_try(
                    record, user, kind, "activity", lambda u=user: record.sudo().activity_schedule(
                        ACTIVITY_XMLID, summary=subject, note=body, user_id=u.id)[:1])
            if "bus" in channels:
                self._notify_try(record, user, kind, "bus", lambda u=user: u.sudo()._bus_send(
                    "simple_notification", {"type": "info", "title": subject, "message": text, "sticky": False}))
            if "email" in recipients.get(user, ()):
                self._notify_try(record, user, kind, "email",
                                 lambda u=user: self._notify_email(record, u, actor, subject, body))
        Pending = self.env["dwo.approval.pending"].sudo()
        for user in approvers:
            Pending.create({
                "res_model": record._name, "res_id": record.id, "record_name": record.display_name,
                "flow_id": self.id, "state_id": current.id, "user_id": user.id,
                "activity_id": activities[user].id if activities.get(user) else False})
        if "email" in follower_channels and hasattr(record, "message_post"):
            # one note with the subtype "Approval": the followers who kept it are told as they prefer (email or inbox)
            names = ", ".join(approvers.mapped("name"))
            note = Markup("<b>%s</b> %s<br/>%s") % (
                self.env._("Waiting for approval:") if names else self.env._("New step:"),
                names or current.name, body)
            self._notify_try(record, False, "followers", "email", lambda: record.sudo().message_post(
                body=note, message_type="notification", subtype_xmlid=SUBTYPE_XMLID,
                author_id=actor.partner_id.id).id)

    def _notify_email(self, record, user, actor, subject, body):
        """An inbox message: an email, or a Discuss message when the person chose that in their preferences."""
        if self.notify_template_id:
            return self.notify_template_id.sudo().send_mail(
                record.id, force_send=False,
                email_values={"email_to": False, "email_cc": False, "recipient_ids": [(6, 0, user.partner_id.ids)]})
        return record.sudo().message_notify(
            partner_ids=user.partner_id.ids, subject=subject, body=body, author_id=actor.partner_id.id,
            email_layout_xmlid="mail.mail_notification_light").id

    # ------------------------------------------------------------------
    # the person who created the document
    # ------------------------------------------------------------------
    def _notify_creator(self, record, actor, transition, reason, votes=None):
        creator = record.sudo().create_uid if "create_uid" in record._fields else self.env["res.users"]
        if not creator or creator == actor or not creator.active:
            return
        env = self.env
        if votes:
            text = env._("%(user)s approved “%(button)s” (%(votes)s). Waiting for the others.",
                         user=actor.name, button=transition.name, votes=votes)
        else:
            text = env._("%(user)s pressed “%(button)s” on “%(doc)s”: %(to)s.",
                         user=actor.name, button=transition.name, doc=record.display_name,
                         to=transition.to_state_id.name)
        body = Markup("%s") % text
        if reason:
            body += Markup("<br/><i>%s</i>") % reason
        body += Markup("<br/>") + self._notify_link(record)
        subject = env._("%(doc)s: %(button)s", doc=record.display_name, button=transition.name)
        self._notify_try(record, creator, "creator", "email", lambda: record.sudo().message_notify(
            partner_ids=creator.partner_id.ids, subject=subject, body=body, author_id=actor.partner_id.id,
            email_layout_xmlid="mail.mail_notification_light").id)

    # ------------------------------------------------------------------
    # texts
    # ------------------------------------------------------------------
    def _notify_link(self, record):
        url = "%s/odoo/%s/%s" % (record.get_base_url(), record._name, record.id)
        return Markup('<a href="%s">%s</a>') % (url, self.env._("Open the document"))

    def _notify_texts(self, record, actor, state, reason):
        """``(subject, plain text, html body)`` of the default message."""
        env = self.env
        subject = env._("To approve: %(doc)s", doc=record.display_name)
        text = env._("%(user)s moved “%(doc)s” to “%(state)s”. It is waiting for your approval.",
                     user=actor.name, doc=record.display_name, state=state.name)
        body = Markup("%s") % text
        if reason:
            body += Markup("<br/><i>%s</i>") % env._("Reason: %(reason)s", reason=reason)
        body += Markup("<br/>") + self._notify_link(record)
        return subject, text, body

    # ------------------------------------------------------------------
    # one send, with its log line
    # ------------------------------------------------------------------
    def _notify_try(self, record, user, kind, channel, send, users=None):
        """Run ``send`` in a savepoint; write the outcome in the log. Never raises. Returns the result."""
        Log = self.env["dwo.approval.notify.log"].sudo()
        targets = users if users is not None else [user or False]
        try:
            with self.env.cr.savepoint():
                result = send()
        except Exception as error:  # a broken template or a missing mail server must not block the approval
            _logger.warning("Approval notification failed (%s, %s): %s", channel, record, error, exc_info=True)
            for target in targets:
                Log.create(self._notify_log_vals(record, target, kind, channel, False, str(error)[:500]))
            return False
        for target in targets:
            Log.create(self._notify_log_vals(record, target, kind, channel, True, False))
        return result

    def _notify_log_vals(self, record, user, kind, channel, ok, error):
        return {"flow_id": self.id, "res_model": record._name, "res_id": record.id, "record_name": record.display_name,
                "user_id": user.id if user else False, "kind": kind, "channel": channel, "ok": ok, "error": error}

    # ------------------------------------------------------------------
    # reminders (cron)
    # ------------------------------------------------------------------
    @api.model
    def _cron_remind(self):
        now = fields.Datetime.now()
        Pending = self.env["dwo.approval.pending"].sudo()
        last_id = 0
        while True:  # in batches by id: rows that reached their last reminder must not hide the ones after them
            rows = Pending.search([("flow_id.remind_after", ">", 0), ("id", ">", last_id)], limit=CRON_BATCH, order="id")
            if not rows:
                break
            last_id = rows[-1].id
            for row in rows:
                self._cron_remind_one(row, now)
        return True

    def _cron_remind_one(self, row, now):
        flow = row.flow_id
        if row.reminder_count >= flow.remind_max:
            return
        if (row.last_reminder or row.since) + timedelta(hours=flow.remind_after) > now:
            return
        record = self.env[row.res_model].sudo().browse(row.res_id).exists()
        if not record or not row._still_waiting(record):
            row._close()
            return
        actor = row.user_id
        subject = self.env._("Reminder: %(doc)s is waiting for your approval", doc=record.display_name)
        body = Markup("%s<br/>") % self.env._(
            "“%(doc)s” is still in “%(state)s” and waiting for your approval.",
            doc=record.display_name, state=row.state_id.name) + flow._notify_link(record)
        with self.env.cr.savepoint():
            flow._notify_try(record, actor, "reminder", "email", lambda: record.message_notify(
                partner_ids=actor.partner_id.ids, subject=subject, body=body,
                email_layout_xmlid="mail.mail_notification_light").id)
            row.write({"reminder_count": row.reminder_count + 1, "last_reminder": now})


class DwoApprovalTransitionNotify(models.Model):
    _inherit = "dwo.approval.transition"

    notify_followers_bus = fields.Boolean(string="Followers: system notification")
    notify_followers_activity = fields.Boolean(string="Followers: activity")
    notify_followers_email = fields.Boolean(
        string="Followers: email (inbox)",
        help="Post a note with the subtype \"Approval\": only the followers who subscribed to it are told.")
    notify_creator = fields.Boolean(
        string="Notify the creator",
        help="Tell the person who created the document when somebody presses this button or votes (\"1/2\").")

    def _notifies_approvers(self):
        return any(line._notify_channels() for line in self.approver_ids)

    def _notifies_followers(self):
        return bool(self.notify_followers_bus or self.notify_followers_activity or self.notify_followers_email)

    def _press(self, record, user, reason=None):
        outcome = super()._press(record, user, reason)
        flow = self.flow_id
        try:
            with self.env.cr.savepoint():
                flow._notify_after_press(record, self, user, outcome, (reason or "").strip())
        except Exception:  # the approval is already done; only the notification failed
            _logger.exception("Approval notification of %s failed", record)
        return outcome


class DwoApprovalApproverNotify(models.Model):
    _inherit = "dwo.approval.approver"

    notify_bus = fields.Boolean(string="System notification")
    notify_activity = fields.Boolean(string="Activity")
    notify_email = fields.Boolean(string="Email (inbox)")

    def _notify_channels(self):
        self.ensure_one()
        return {c for c in CHANNELS if self["notify_" + c]}

    def _notify_candidates(self, record, actor):
        """People this line may stand for (before the check of the real button)."""
        self.ensure_one()
        Users = self.env["res.users"].sudo()
        if self.kind == "users":
            return self.user_ids
        if self.kind == "group":
            return self.group_id.users
        if self.kind == "dept":
            rec = record.sudo()
            if "department_id" in rec._fields and rec.department_id and "employee_ids" in Users._fields:
                return Users.search([("employee_ids.department_id", "=", rec.department_id.id)])
            return Users
        expr = ("record." + (self.value or "id")) if self.kind == "field" else self.value
        return Users.browse(sorted(eval_expression(record, actor, expr)))


class DwoApprovalPending(models.Model):
    _name = "dwo.approval.pending"
    _description = "Waiting for approval"
    _order = "since desc, id desc"

    res_model = fields.Char(required=True, index=True)
    res_id = fields.Many2oneReference(model_field="res_model", required=True, index=True)
    record_name = fields.Char(string="Document")
    flow_id = fields.Many2one("dwo.approval.flow", string="Flow", required=True, ondelete="cascade", index=True)
    state_id = fields.Many2one("dwo.approval.state", string="Step", ondelete="cascade")
    user_id = fields.Many2one("res.users", string="Approver", required=True, ondelete="cascade", index=True)
    since = fields.Datetime(default=fields.Datetime.now, required=True)
    activity_id = fields.Many2one("mail.activity", ondelete="set null")
    reminder_count = fields.Integer()
    last_reminder = fields.Datetime()

    _sql_constraints = [(
        "one_per_user", "unique(res_model, res_id, user_id)", "A person is listed once for a document.")]

    def _close(self):
        """Remove the rows and the activities they scheduled."""
        activities = self.activity_id.sudo().exists()
        if activities:
            try:
                activities.unlink()
            except Exception:  # an activity that cannot be closed must not block the approval
                _logger.warning("Could not close the approval activities %s", activities.ids, exc_info=True)
        self.unlink()

    def _still_waiting(self, record):
        """True when the document is still in the step and the person can still press an arrow."""
        self.ensure_one()
        flow = self.flow_id
        if not flow.active or flow._current_state(record) != self.state_id:
            return False
        return any(
            t._notifies_approvers() and t._check_available(record, self.user_id)[0]
            for t in flow.transition_ids if t.from_state_id == self.state_id or not t.from_state_id)

    def action_open_document(self):
        self.ensure_one()
        return {"type": "ir.actions.act_window", "res_model": self.res_model, "res_id": self.res_id,
                "view_mode": "form", "views": [(False, "form")], "target": "current"}


class DwoApprovalNotifyLog(models.Model):
    _name = "dwo.approval.notify.log"
    _description = "Approval notification log"
    _order = "id desc"

    date = fields.Datetime(default=fields.Datetime.now, required=True)
    flow_id = fields.Many2one("dwo.approval.flow", string="Flow", ondelete="cascade", index=True)
    res_model = fields.Char(index=True)
    res_id = fields.Many2oneReference(model_field="res_model")
    record_name = fields.Char(string="Document")
    user_id = fields.Many2one("res.users", string="Told", ondelete="set null")
    kind = fields.Selection(
        [("approver", "Approver"), ("followers", "Followers"), ("creator", "Creator"), ("reminder", "Reminder")],
        required=True)
    channel = fields.Selection(
        [("bus", "System notification"), ("activity", "Activity"), ("email", "Email (inbox)")], required=True)
    ok = fields.Boolean(string="Sent")
    error = fields.Char()
