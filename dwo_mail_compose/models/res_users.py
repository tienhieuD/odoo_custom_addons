# -*- coding: utf-8 -*-
from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def _bus_send(self, notification_type, message, /, *, subchannel=None):
        """Odoo 18 has this method (bus.listener.mixin); Odoo 17 sends to the partner channel."""
        for user in self:
            self.env["bus.bus"]._sendone(user.partner_id, notification_type, message)
