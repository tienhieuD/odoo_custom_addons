from odoo.http import request
from odoo.addons.bus.controllers.main import BusController

from ..models.dwo_record_presence import dwo_channel_allowed


class DwoBusController(BusController):

    def poll(self, channels, last, options=None):
        """Presence channels are plain strings chosen by the client: only let a user listen to the records
        he is allowed to read. (The route of the parent method is kept.)"""
        channels = [channel for channel in channels if dwo_channel_allowed(request.env, channel)]
        return super(DwoBusController, self).poll(channels, last, options)
