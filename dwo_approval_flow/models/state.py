# -*- coding: utf-8 -*-
import re

from odoo import api, fields, models


class DwoApprovalState(models.Model):
    _name = "dwo.approval.state"
    _description = "Approval Flow State"
    _order = "sequence, id"

    flow_id = fields.Many2one("dwo.approval.flow", required=True, ondelete="cascade", index=True)
    name = fields.Char(required=True, translate=True)
    key = fields.Char(required=True)
    value = fields.Char(help="Value of the model's own field this state mirrors (state mode: field).")
    sequence = fields.Integer(default=10)
    pos_x = fields.Integer(default=10)
    pos_y = fields.Integer(default=170)
    color = fields.Integer(default=0)
    always_visible = fields.Boolean(
        string="Always shown on the status bar", default=True,
        help="Off: the status bar shows this state only while the document is in it (like Odoo's statusbar_visible).")
    missing = fields.Boolean(help="The value no longer exists on the model's field.")

    _sql_constraints = [("key_unique", "unique(flow_id, key)", "A state key must be unique inside a flow.")]

    @api.model
    def slugify(self, text):
        return re.sub(r"\W+", "_", (text or "").strip().lower()).strip("_") or "state"

    def _doc_value(self):
        """Value written in / compared with the document's state field."""
        self.ensure_one()
        return self.value if self.flow_id.state_mode == "field" else str(self.id)
