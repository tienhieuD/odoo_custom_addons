# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DwoMailOrphanRouteWizard(models.TransientModel):
    _name = "dwo.mail.orphan.route.wizard"
    _description = "Route orphan emails"

    orphan_ids = fields.Many2many("dwo.mail.orphan", string="Emails")
    allowed_model_ids = fields.Many2many("ir.model", compute="_compute_allowed_model_ids")
    model_id = fields.Many2one("ir.model", "Target model", required=True, domain="[('id', 'in', allowed_model_ids)]")
    res_model = fields.Char(related="model_id.model")
    res_id = fields.Many2oneReference("Target record", model_field="res_model", required=True)
    follow_sender = fields.Boolean("Add the sender as follower")
    include_same_sender = fields.Boolean("Also the new emails from the same senders")
    include_same_thread = fields.Boolean("Also the new emails of the same threads")
    total_count = fields.Integer("Emails to route", compute="_compute_total_count")

    @api.depends_context("uid")
    def _compute_allowed_model_ids(self):
        names = self.env["dwo.mail.orphan"]._target_models()
        models_ = self.env["ir.model"].sudo().search([("model", "in", names)])
        for wiz in self:
            wiz.allowed_model_ids = models_

    @api.depends("orphan_ids", "include_same_sender", "include_same_thread")
    def _compute_total_count(self):
        for wiz in self:
            wiz.total_count = len(wiz._orphans())

    def _orphans(self):
        self.ensure_one()
        # in the form (onchange) the records are virtual copies: work on the real ids
        orphans = self.env["dwo.mail.orphan"].browse(sorted({o._origin.id or o.id for o in self.orphan_ids}))
        if self.include_same_sender or self.include_same_thread:
            orphans |= orphans._related_orphans(self.include_same_sender, self.include_same_thread)
        return orphans

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        orphans = self.env["dwo.mail.orphan"].browse(self.env.context.get("default_orphan_ids") or self.env.context.get("active_ids") or [])
        if "orphan_ids" in fields_list and not res.get("orphan_ids"):
            res["orphan_ids"] = [(6, 0, orphans.ids)]
        res.setdefault("follow_sender", self.env["dwo.mail.orphan"]._icp("follow_sender", "0") in ("1", "True", "true"))
        if len(orphans) == 1 and orphans.suggestion_ids:
            top = orphans.suggestion_ids[0]
            model = self.env["ir.model"]._get(top.res_model)
            res.update({"model_id": model.id, "res_id": top.res_id})
        return res

    def action_route(self):
        self.ensure_one()
        orphans = self._orphans()
        if not orphans:
            raise UserError(_("Select at least one email."))
        orphans._route_to(self.res_model, self.res_id, follow=self.follow_sender)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Routed"),
                "message": _("%s email(s) moved to the record.", len(orphans)),
                "type": "success",
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
