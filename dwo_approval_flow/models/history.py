# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class DwoApprovalHistory(models.TransientModel):
    """Read-only copy of the approval log of one document, shown to anybody who can read the document."""
    _name = "dwo.approval.history"
    _description = "Approval History"

    res_model = fields.Char(readonly=True)
    res_id = fields.Integer(readonly=True)
    record_name = fields.Char(readonly=True)
    flow_name = fields.Char(readonly=True)
    current_state = fields.Char(readonly=True)
    line_ids = fields.One2many("dwo.approval.history.line", "history_id", readonly=True)

    @api.model
    def open_for(self, record):
        flow = self.env["dwo.approval.flow"].sudo()._flow_of(record.sudo())
        logs = self.env["dwo.approval.log"].sudo().search([("res_model", "=", record._name), ("res_id", "=", record.id)])
        history = self.create({
            "res_model": record._name, "res_id": record.id, "record_name": record.display_name,
            "flow_name": flow.name if flow else False,
            "current_state": flow._current_state(record.sudo()).name if flow else False,
            "line_ids": [(0, 0, {
                "date": log.date, "kind": log.kind, "button": log.button, "from_name": log.from_name,
                "to_name": log.to_name, "user_id": log.user_id.id, "votes": log.votes, "reason": log.reason,
            }) for log in logs]})
        return {
            "type": "ir.actions.act_window", "name": _("Approval history"),
            "res_model": self._name, "res_id": history.id, "view_mode": "form", "target": "new",
            "views": [(self.env.ref("dwo_approval_flow.view_dwo_approval_history_form").id, "form")],
        }


class DwoApprovalHistoryLine(models.TransientModel):
    _name = "dwo.approval.history.line"
    _description = "Approval History Line"
    _order = "date desc, id desc"

    history_id = fields.Many2one("dwo.approval.history", ondelete="cascade", required=True)
    date = fields.Datetime(readonly=True)
    kind = fields.Selection([("move", "State change"), ("vote", "Approval")], readonly=True)
    button = fields.Char(readonly=True)
    from_name = fields.Char(readonly=True)
    to_name = fields.Char(readonly=True)
    user_id = fields.Many2one("res.users", readonly=True)
    votes = fields.Char(readonly=True)
    reason = fields.Text(readonly=True)
