# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import AccessError

PREFIX = "dwo_dashboard.ai_"
MANAGER = "dwo_dashboard.group_dwo_dashboard_manager"


class DwoAiConfig(models.TransientModel):
    """Who answers the assistant, and whether it is on. Dashboard managers (and so administrators). The key is written, never
    read back: the form shows only whether one is set. It is a form of its own, not the Settings app, so that a manager does
    not need the rights of an administrator."""
    _name = "dwo.ai.config"
    _description = "Dashboard AI assistant settings"

    enabled = fields.Boolean(string="Assistant on", default=True)
    provider = fields.Selection([("odoo_olg", "Odoo AI (default, nothing to set up)"), ("openai", "OpenAI-compatible API")],
                                default="odoo_olg", required=True)
    endpoint = fields.Char(help="Empty for api.openai.com. Any server that speaks the chat completions API.")
    model = fields.Char(help="Empty for gpt-4o-mini.")
    api_key = fields.Char(string="API key", help="Written, never shown again.")
    key_set = fields.Boolean(string="A key is set", readonly=True)

    def _manager(self):
        if not self.env.user.has_group(MANAGER):
            raise AccessError(_("Only dashboard managers configure the assistant."))

    @api.model
    def default_get(self, names):
        res = super().default_get(names)
        self._manager()
        params = self.env["ir.config_parameter"].sudo()
        res.update(enabled=params.get_param(PREFIX + "enabled", "1") not in ("0", "False", "false"),
                   provider=params.get_param(PREFIX + "provider") or "odoo_olg",
                   endpoint=params.get_param(PREFIX + "endpoint") or False, model=params.get_param(PREFIX + "model") or False,
                   key_set=bool(params.get_param(PREFIX + "api_key")), api_key=False)  # the key itself never leaves the server
        return res

    def action_save(self):
        self._manager()
        params = self.env["ir.config_parameter"].sudo()
        for rec in self:
            params.set_param(PREFIX + "enabled", "1" if rec.enabled else "0")
            params.set_param(PREFIX + "provider", rec.provider)
            params.set_param(PREFIX + "endpoint", (rec.endpoint or "").strip())
            params.set_param(PREFIX + "model", (rec.model or "").strip())
            if rec.api_key:
                params.set_param(PREFIX + "api_key", rec.api_key.strip())
        return {"type": "ir.actions.act_window_close"}
