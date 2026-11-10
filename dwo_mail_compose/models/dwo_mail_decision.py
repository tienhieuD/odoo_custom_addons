# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError


class DwoMailDecision(models.TransientModel):
    """Popup of the three decisions of an approver. The comment is optional in every case."""
    _name = "dwo.mail.decision"
    _description = "Decision on an email waiting for approval"

    email_id = fields.Many2one("dwo.mail.email", required=True, ondelete="cascade")
    decision = fields.Selection(
        [("approve", "Approve and send"), ("reject", "Reject"), ("reassign", "Reassign")], required=True)
    comment = fields.Text(help="Saved on the email. Optional.")
    user_ids = fields.Many2many(
        "res.users", string="Who takes over", domain=[("share", "=", False)],
        help="The people who become approvers in your place.")

    def action_confirm(self):
        self.ensure_one()
        email = self.email_id
        if self.decision == "approve":
            email.action_approve(self.comment)
        elif self.decision == "reject":
            email.action_reject(self.comment)
        else:
            if not self.user_ids:
                raise UserError(_("Choose who takes over."))
            email.action_reassign(self.user_ids, self.comment)
        return {"type": "ir.actions.act_window_close"}
