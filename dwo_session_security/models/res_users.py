# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import api, fields, models, release
from odoo.exceptions import AccessDenied
from odoo.http import request

from .util import tr


class ResUsers(models.Model):
    _inherit = "res.users"

    dwo_has_pin = fields.Boolean("Lock PIN set", compute="_compute_dwo_has_pin")

    def _compute_dwo_has_pin(self):
        pins = {p.user_id.id: bool(p.pin_hash) for p in self.env["dwo.user.pin"].sudo().search([("user_id", "in", self.ids)])}
        for user in self:
            user.dwo_has_pin = pins.get(user.id, False)

    def authenticate(self, *args, **kwargs):
        # a new sign-in on a session that already had one: the row of the old sign-in must not be reused
        if request and getattr(request, "session", None) is not None and "dwo_key" in request.session:
            del request.session["dwo_key"]
        return super().authenticate(*args, **kwargs)

    def write(self, vals):
        res = super().write(vals)
        if vals.get("active") is False:
            self.env["dwo.session"].sudo().search([("user_id", "in", self.ids), ("state", "!=", "expired")])._dwo_expire("forced")
        return res

    # -- password check (the signature changed in Odoo 18) ------------------------------------------------
    def _dwo_has_password(self):
        self.env.cr.execute("SELECT password IS NOT NULL AND password != '' FROM res_users WHERE id = %s", [self.id])
        row = self.env.cr.fetchone()
        return bool(row and row[0])

    def _dwo_check_password(self, password):
        self.ensure_one()
        if not password:
            return False
        try:
            if release.version_info[0] >= 18:
                self.sudo()._check_credentials({"type": "password", "password": password}, {"interactive": True})
            else:
                self.sudo()._check_credentials(password, {"interactive": True})
        except AccessDenied:
            return False
        return True

    # -- buttons ---------------------------------------------------------------------------------------------
    def action_dwo_set_pin(self):
        return {
            "type": "ir.actions.act_window", "name": tr(self.env, "Lock PIN"), "res_model": "dwo.pin.wizard",
            "view_mode": "form", "target": "new", "context": {"default_mode": "self"},
        }

    def action_dwo_temp_pin(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window", "name": tr(self.env, "Temporary PIN"), "res_model": "dwo.pin.wizard",
            "view_mode": "form", "target": "new", "context": {"default_mode": "temp", "default_user_id": self.id},
        }

    def action_dwo_my_sessions(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("dwo_session_security.action_dwo_my_sessions")
        return action
