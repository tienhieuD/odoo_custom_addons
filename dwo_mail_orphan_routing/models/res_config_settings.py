# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import api, fields, models

PARAM = "dwo_orphan."


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    dwo_orphan_enabled = fields.Boolean("Keep orphan emails", config_parameter="dwo_orphan.enabled")
    dwo_orphan_digest = fields.Boolean("Daily digest", config_parameter="dwo_orphan.digest")
    dwo_orphan_keep_days = fields.Integer("Keep handled emails (days)", config_parameter="dwo_orphan.keep_days")
    dwo_orphan_follow_sender = fields.Boolean("Add the sender as follower", config_parameter="dwo_orphan.follow_sender")
    dwo_orphan_model_ids = fields.Many2many(
        "ir.model", "dwo_orphan_config_model_rel", "config_id", "model_id", string="Allowed target models",
        domain="[('is_mail_thread', '=', True), ('transient', '=', False)]")

    @api.model
    def get_values(self):
        res = super().get_values()
        names = self.env["dwo.mail.orphan"]._target_models()
        res["dwo_orphan_model_ids"] = [(6, 0, self.env["ir.model"].search([("model", "in", names)]).ids)]
        return res

    def set_values(self):
        super().set_values()
        names = ",".join(sorted(self.dwo_orphan_model_ids.mapped("model"))) or "-"
        self.env["dwo.mail.orphan"]._icp_set("target_models", names)
