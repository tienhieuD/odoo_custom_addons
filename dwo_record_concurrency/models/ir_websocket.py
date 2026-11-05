from odoo import models

from .dwo_record_presence import CHANNEL_PREFIX


class IrWebsocket(models.AbstractModel):
    _inherit = 'ir.websocket'

    def _dwo_channel_allowed(self, channel):
        """Presence channels are plain strings chosen by the client: only let a user listen to the records
        he is allowed to read."""
        if not isinstance(channel, str) or not channel.startswith(CHANNEL_PREFIX + ':'):
            return True
        try:
            _prefix, model, res_id = channel.split(':', 2)
            record = self.env[model].browse(int(res_id))
            return record.exists().has_access('read')
        except Exception:  # noqa: BLE001 - malformed or unknown channel: refuse it
            return False

    def _dwo_filter_channels(self, channels):
        return [channel for channel in channels if self._dwo_channel_allowed(channel)]

    def _build_bus_channel_list(self, channels):
        return super()._build_bus_channel_list(self._dwo_filter_channels(channels))
