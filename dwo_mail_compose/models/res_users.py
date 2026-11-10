# -*- coding: utf-8 -*-
from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def _bus_send(self, notification_type, message, subchannel=None):
        """Odoo 13: bus.bus.sendone(channel, message), the channel of a partner is (db, 'res.partner', id)."""
        for user in self:
            self.env["bus.bus"].sendone(
                (self.env.cr.dbname, "res.partner", user.partner_id.id), {"type": notification_type, "payload": message})
