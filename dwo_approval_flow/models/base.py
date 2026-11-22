# -*- coding: utf-8 -*-
"""Put the approval buttons / status bar in the header of the form of any model that has a flow."""
from lxml import etree

from odoo import api, models

from . import guard


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "form" and self.pool.ready and "dwo.approval.flow" in self.pool \
                and not self._transient and self._name != "dwo.approval.flow":
            flows = self.env["dwo.approval.flow"].sudo().search([
                ("model_name", "=", self._name), ("active", "=", True)])
            if flows:
                flows._inject_form(arch)
        return arch, view

    def write(self, vals):
        # the own-state field of a flow can only be changed by the arrows (and by system code)
        if "x_dwo_approval_state_id" in vals and not guard.is_bypassed() and not self.env.su:
            self.env["dwo.approval.flow"]._guard_write_refused()
        return super().write(vals)
