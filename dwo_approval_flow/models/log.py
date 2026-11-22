# -*- coding: utf-8 -*-
from odoo import fields, models


class DwoApprovalLog(models.Model):
    _name = "dwo.approval.log"
    _description = "Approval Log"
    _order = "id desc"

    res_model = fields.Char(required=True, index=True)
    res_id = fields.Many2oneReference(model_field="res_model", required=True, index=True)
    flow_id = fields.Many2one("dwo.approval.flow", ondelete="set null")
    transition_id = fields.Many2one("dwo.approval.transition", ondelete="set null")
    kind = fields.Selection([("move", "State change"), ("vote", "Approval")], required=True)
    button = fields.Char(help="Name of the button, kept if the arrow is deleted later.")
    from_name = fields.Char()
    to_name = fields.Char()
    user_id = fields.Many2one("res.users", ondelete="set null")
    date = fields.Datetime(default=fields.Datetime.now, required=True)
    reason = fields.Text()
    votes = fields.Char(help="Progress such as 1/2 for an approval.")
    skipped = fields.Char()
