# -*- coding: utf-8 -*-
from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def _bus_send(self, notification_type, message, /, *, subchannel=None):
        """Odoo 18 has this method (bus.listener.mixin); Odoo 14 sends to the channel of the partner, with
        the type and the payload in one dict (it has no bus.bus._sendone and no notification types)."""
        for user in self:
            self.env["bus.bus"].sendone(
                (self._cr.dbname, "res.partner", user.partner_id.id),
                {"type": notification_type, "payload": message},
            )
