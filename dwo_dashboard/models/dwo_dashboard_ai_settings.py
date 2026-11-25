# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import AccessError

PREFIX = "dwo_dashboard.ai_"


class ResConfigSettings(models.TransientModel):
    """Who answers the assistant. System administrators only (the transient model and its view are theirs). The key is
    written, never read back: the form shows only whether one is set."""
    _inherit = "res.config.settings"

    dwo_ai_provider = fields.Selection([("odoo_olg", "Odoo AI (default, nothing to set up)"), ("openai", "OpenAI-compatible API")],
                                       string="Provider", config_parameter=PREFIX + "provider", default="odoo_olg")
    dwo_ai_endpoint = fields.Char(string="Endpoint", config_parameter=PREFIX + "endpoint",
                                  help="Empty for api.openai.com. Any server that speaks the chat completions API.")
    dwo_ai_model = fields.Char(string="Model", config_parameter=PREFIX + "model", help="Empty for gpt-4o-mini.")
    dwo_ai_api_key = fields.Char(string="API key", help="Written, never shown again.")
    dwo_ai_key_set = fields.Boolean(string="A key is set", readonly=True)

    @api.model
    def get_values(self):
        res = super().get_values()
        res["dwo_ai_api_key"] = False  # never sent to the browser
        res["dwo_ai_key_set"] = bool(self.env["ir.config_parameter"].sudo().get_param(PREFIX + "api_key"))
        return res

    def set_values(self):
        super().set_values()
        if self.dwo_ai_api_key:
            if not self.env.is_system():
                raise AccessError(_("Only administrators set the AI key."))
            self.env["ir.config_parameter"].sudo().set_param(PREFIX + "api_key", self.dwo_ai_api_key.strip())
