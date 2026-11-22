# -*- coding: utf-8 -*-
from odoo import fields, models


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    dwo_approval_flow_id = fields.Many2one(
        "dwo.approval.flow", string="Approval Flow", ondelete="cascade", index="btree_not_null", copy=False)
    dwo_label = fields.Char(string="Approval button", copy=False)
