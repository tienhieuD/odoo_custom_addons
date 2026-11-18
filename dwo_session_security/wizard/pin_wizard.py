# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import secrets

from odoo import fields, models
from odoo.exceptions import AccessError, UserError

from odoo.addons.dwo_session_security.models.pin import weak_reason
from odoo.addons.dwo_session_security.models.util import cfg_bool, tr


class DwoPinWizard(models.TransientModel):
    """Choose a PIN (in the preferences of the user) or give a temporary one to a user (administrator).
    The typed digits live in this short-lived record only until the button is pressed; they are erased at once."""

    _name = "dwo.pin.wizard"
    _description = "Lock PIN"
    _transient_max_hours = 0.1

    mode = fields.Selection([("self", "Own PIN"), ("temp", "Temporary PIN")], default="self", required=True)
    user_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    has_password = fields.Boolean(compute="_compute_has_password")
    has_pin = fields.Boolean(compute="_compute_has_password")
    password = fields.Char()
    pin = fields.Char()
    pin_confirm = fields.Char()

    def _compute_has_password(self):
        for rec in self:
            rec.has_password = rec.user_id.sudo()._dwo_has_password() if rec.user_id else False
            rec.has_pin = bool(rec.user_id) and self.env["dwo.user.pin"].has_pin(rec.user_id.id)

    def _wipe(self):
        self.write({"password": False, "pin": False, "pin_confirm": False})

    def action_confirm(self):
        self.ensure_one()
        pin, confirm, password = self.pin or "", self.pin_confirm or "", self.password or ""
        Pin = self.env["dwo.user.pin"]
        Log = self.env["dwo.session.log"]
        if self.mode == "self":
            user = self.env.user
            if self.user_id != user:
                raise AccessError(tr(self.env, "You can only set your own PIN."))
            if user._dwo_has_password() and not user._dwo_check_password(password):
                self._wipe()
                raise UserError(tr(self.env, "The password is not correct."))
            if pin != confirm:
                self._wipe()
                raise UserError(tr(self.env, "The two PINs are different."))
            try:
                Pin.set_pin(user.id, pin)
            finally:
                self._wipe()
            Log.add("pin_set", user, method="preferences")
            message = tr(self.env, "Your PIN is saved. The screen locks after a period without activity.")
        else:
            if not self.env.user.has_group("base.group_system"):
                raise AccessError(tr(self.env, "Only administrators can set a temporary PIN."))
            if not cfg_bool(self.env, "forgot_temp"):
                raise UserError(tr(self.env, "Temporary PINs are switched off in the settings."))
            if not self.user_id or self.user_id == self.env.user:
                raise UserError(tr(self.env, "Choose another user."))
            if not pin:
                length = 6
                while True:
                    pin = "%06d" % secrets.randbelow(10 ** length)
                    if not weak_reason(pin):
                        break
                shown = True
            else:
                shown = False
                if pin != confirm:
                    self._wipe()
                    raise UserError(tr(self.env, "The two PINs are different."))
                Pin.check_format(pin)
            try:
                Pin.set_pin(self.user_id.id, pin, must_change=True, check=False)
            finally:
                self._wipe()
            Log.add("temp_pin", self.user_id, note="set by %s" % self.env.user.name, method="admin")
            message = (tr(self.env, "Temporary PIN for %s: %s. It is shown only now; the user must change it at the first unlock.",
                          self.user_id.name, pin) if shown else
                       tr(self.env, "Temporary PIN saved. The user must change it at the first unlock."))
        return {"type": "ir.actions.client", "tag": "display_notification",
                "params": {"title": tr(self.env, "Lock PIN"), "message": message, "type": "success", "sticky": True,
                           "next": {"type": "ir.actions.act_window_close"}}}
