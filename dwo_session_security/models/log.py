# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from datetime import timedelta

from odoo import api, fields, models

from .util import cfg_int


class DwoSessionLog(models.Model):
    _name = "dwo.session.log"
    _description = "Session security log"
    _order = "id desc"

    user_id = fields.Many2one("res.users", ondelete="set null", index=True)
    event = fields.Selection([
        ("login", "Session started"),
        ("lock", "Locked"),
        ("unlock", "Unlocked"),
        ("unlock_fail", "Wrong PIN"),
        ("pin_set", "PIN set"),
        ("pin_reset", "PIN reset"),
        ("reset_request", "PIN reset requested"),
        ("otp_sent", "PIN code sent by email"),
        ("temp_pin", "Temporary PIN set by an administrator"),
        ("expired", "Session expired"),
        ("forced", "Session closed by an administrator"),
        ("browser_closed", "Browser was closed"),
        ("extended", "Session extended"),
        ("approval_request", "Approval requested"),
        ("approved", "Session approved"),
        ("rejected", "Session rejected"),
    ], required=True, index=True)
    note = fields.Char()
    ip = fields.Char("IP address")
    user_agent = fields.Char("Browser")
    method = fields.Char()

    @api.model
    def add(self, event, user=None, note=None, **extra):
        from odoo.http import request
        vals = {"event": event, "user_id": int(user) if user else False, "note": note and str(note)[:250]}
        try:
            if request and request.httprequest:
                vals["ip"] = request.httprequest.remote_addr
                vals["user_agent"] = (request.httprequest.user_agent.string or "")[:200]
        except RuntimeError:
            pass
        vals.update(extra)
        return self.sudo().create(vals)

    @api.autovacuum
    def _gc_logs(self):
        days = cfg_int(self.env, "log_days")
        if days:
            self.sudo().search([("create_date", "<", fields.Datetime.now() - timedelta(days=days))]).unlink()
