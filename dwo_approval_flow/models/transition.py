# -*- coding: utf-8 -*-
import logging

from markupsafe import Markup

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import SQL

from . import guard

_logger = logging.getLogger(__name__)


class DwoApprovalTransition(models.Model):
    _name = "dwo.approval.transition"
    _description = "Approval Flow Button (arrow)"
    _order = "sequence, id"

    flow_id = fields.Many2one("dwo.approval.flow", required=True, ondelete="cascade", index=True)
    name = fields.Char(string="Button", required=True, translate=True)
    sequence = fields.Integer(default=10)
    from_state_id = fields.Many2one(
        "dwo.approval.state", ondelete="cascade", domain="[('flow_id', '=', flow_id)]",
        help="Leave empty for an arrow that starts from every state.")
    to_state_id = fields.Many2one(
        "dwo.approval.state", required=True, ondelete="cascade", domain="[('flow_id', '=', flow_id)]")
    color = fields.Integer(default=0)
    ask_reason = fields.Boolean(string="Ask for a reason")
    vote_mode = fields.Selection(
        [("any", "1 approval"), ("all", "1 approval per approver line"), ("n", "At least N approvals")],
        default="any", required=True)
    vote_n = fields.Integer(string="Approvals needed", default=2)
    move_mode = fields.Selection(
        [("set_state", "Set the state"), ("call_method", "Call a method or server action")],
        default="set_state", required=True)
    method_name = fields.Char(string="Method", help="Public method of the model, such as action_confirm.")
    server_action_id = fields.Many2one("ir.actions.server", ondelete="set null")
    verify = fields.Boolean(
        string="Check the state afterwards", default=True,
        help="After the method ran, the document must be in the target state or everything is rolled back.")
    run_as = fields.Selection([("user", "The user who pressed"), ("system", "System")], default="user", required=True)
    guard_scope = fields.Selection(
        [("direct", "When the original button is pressed"), ("all", "Every call"), ("none", "Do not protect")],
        string="Protect the method", default="direct", required=True,
        help="Direct: the method only runs through the approval when called from a button or RPC. "
             "Every call: also when other code calls it (except as system). None: only the view is changed.")
    list_action = fields.Boolean(
        string="Also allow from the list view",
        help="Adds an entry to the Action menu of the list and form views.")
    approver_ids = fields.One2many("dwo.approval.approver", "transition_id")
    rule_ids = fields.One2many("dwo.approval.rule", "transition_id")
    action_ids = fields.One2many("dwo.approval.action", "transition_id")

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        self.env["dwo.approval.flow"]._guard_sync()
        return result

    def write(self, vals):
        result = super().write(vals)
        if {"move_mode", "method_name", "guard_scope", "flow_id"} & set(vals):
            self.env["dwo.approval.flow"]._guard_sync()
        return result

    def unlink(self):
        result = super().unlink()
        self.env["dwo.approval.flow"]._guard_sync()
        return result

    @api.constrains("move_mode", "method_name", "server_action_id", "vote_mode", "vote_n")
    def _check_transition(self):
        for tr in self:
            if tr.vote_mode == "n" and tr.vote_n < 2:
                raise ValidationError(self.env._("At least 2 approvals are needed for this mode."))
            if tr.move_mode == "call_method":
                if not tr.method_name and not tr.server_action_id:
                    raise ValidationError(self.env._("Pick a method or a server action."))
                if tr.method_name:
                    model = self.env[tr.flow_id.model_name]
                    method = getattr(type(model), tr.method_name, None)
                    if tr.method_name.startswith("_") or not callable(method):
                        raise ValidationError(self.env._(
                            '"%s" is not a public method of the model.', tr.method_name))

    # ------------------------------------------------------------------
    # who can press
    # ------------------------------------------------------------------
    def _needed(self):
        self.ensure_one()
        if not self.approver_ids:
            return 1
        if self.vote_mode == "all":
            return len(self.approver_ids)
        if self.vote_mode == "n":
            return self.vote_n
        return 1

    def _vote_logs(self, record):
        """Votes given on this arrow since the last state change of the document."""
        Log = self.env["dwo.approval.log"].sudo()
        base = [("res_model", "=", record._name), ("res_id", "=", record.id)]
        last_move = Log.search(base + [("kind", "=", "move")], limit=1)
        domain = base + [("kind", "=", "vote"), ("transition_id", "=", self.id)]
        if last_move:
            domain.append(("id", ">", last_move.id))
        return Log.search(domain)

    def _satisfied(self, record, voters):
        self.ensure_one()
        if not voters:
            return False
        needed = self._needed()
        if self.vote_mode == "all" and self.approver_ids:
            free = list(voters)
            for line in self.approver_ids:
                match = next((v for v in free if line._matches(record, v)), None)
                if not match:
                    return False
                free.remove(match)
            return True
        return len(voters) >= needed

    def _check_available(self, record, user):
        """Return ``(True, "")`` or ``(False, reason)`` for ``user`` on ``record``."""
        self.ensure_one()
        flow = self.flow_id
        current = flow._current_state(record)
        if not current:
            return False, self.env._("The document is not in a state of this flow.")
        if self.from_state_id and self.from_state_id != current:
            return False, self.env._("The document is not in the state this button starts from.")
        if not self.from_state_id and self.to_state_id == current:
            return False, self.env._("The document is already in this state.")
        if not flow._applies(record):
            return False, self.env._("This flow does not apply to the document.")
        for rule in self.rule_ids:
            if not rule._holds(record, user):
                return False, self.env._("A rule of this button is not met.")
        if self.approver_ids and not any(line._matches(record, user) for line in self.approver_ids):
            return False, self.env._("You are not one of the approvers of this button.")
        if self._needed() > 1 and user in self._vote_logs(record).user_id:
            return False, self.env._("You already approved. Waiting for the others.")
        return True, ""

    # ------------------------------------------------------------------
    # pressing
    # ------------------------------------------------------------------
    def _lock(self, record):
        record.flush_recordset()
        self.env.cr.execute(SQL("SELECT id FROM %s WHERE id = %s FOR UPDATE", SQL.identifier(record._table), record.id))
        record.invalidate_recordset()

    def _press(self, record, user, reason=None):
        """Press the button as ``user``. Returns a dict for the client."""
        self.ensure_one()
        flow = self.flow_id
        if not flow.active or flow.model_name != record._name:
            raise UserError(self.env._("This button is not active."))
        self._lock(record)
        ok, why = self._check_available(record, user)
        if not ok:
            raise UserError(why)
        reason = (reason or "").strip()
        if self.ask_reason and not reason:
            raise UserError(self.env._("A reason is required."))
        Log = self.env["dwo.approval.log"].sudo()
        current = flow._current_state(record)
        common = {
            "res_model": record._name, "res_id": record.id, "flow_id": flow.id, "transition_id": self.id,
            "button": self.name, "from_name": current.name, "user_id": user.id, "reason": reason or False,
        }
        needed = self._needed()
        if needed > 1:
            Log.create(dict(common, kind="vote"))
            voters = self._vote_logs(record).user_id
            if not self._satisfied(record, voters):
                last = Log.search([("res_model", "=", record._name), ("res_id", "=", record.id),
                                   ("kind", "=", "vote"), ("transition_id", "=", self.id)], limit=1)
                last.votes = "%s/%s" % (len(voters), needed)
                self._post(record, user, self.env._(
                    "approved “%(button)s” (%(votes)s). Waiting for the others.", button=self.name, votes=last.votes), reason)
                return {"status": "waiting", "count": len(voters), "needed": needed}
        action = self._perform(record, user)
        flow._after_move(record, self, user)
        for step in self.action_ids:
            step._run(record, user)
        Log.create(dict(common, kind="move", to_name=self.to_state_id.name))
        self._post(record, user, self.env._(
            "pressed “%(button)s”: %(from)s → %(to)s",
            button=self.name, **{"from": current.name, "to": self.to_state_id.name}), reason)
        return {"status": "done", "action": action or False}

    def _post(self, record, user, text, reason):
        if not hasattr(record, "message_post"):
            return
        body = Markup("%s") % text
        if reason:
            body += Markup("<br/><i>%s</i>") % reason
        record.sudo().message_post(body=body, author_id=user.partner_id.id,
                                   message_type="notification", subtype_xmlid="mail.mt_note")

    def _perform(self, record, user):
        """Run the main step. Returns an action dict (wizard) or False."""
        self.ensure_one()
        flow = self.flow_id
        if self.move_mode == "set_state":
            flow._write_state(record, self.to_state_id)
            return False
        target = record if self.run_as == "user" else record.sudo()
        with guard.bypass():
            if self.server_action_id:
                result = self.server_action_id.sudo().with_env(target.env).with_context(
                    active_model=record._name, active_id=record.id, active_ids=record.ids).run()
            else:
                result = getattr(target, self.method_name)()
        if isinstance(result, dict) and result.get("type"):
            return result  # a wizard: the state changes later, nothing to check now
        if flow.state_mode == "custom":
            flow._write_state(record, self.to_state_id)
        record.invalidate_recordset()
        if self.verify and flow._current_state(record) != self.to_state_id:
            raise UserError(self.env._(
                'The action did not move the document to "%(to)s" (it is in "%(now)s"). Nothing was changed.',
                to=self.to_state_id.name, now=flow._current_state(record).name or "?"))
        return False
