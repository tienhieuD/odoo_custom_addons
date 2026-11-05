from odoo import api, models

CHANNEL_PREFIX = 'dwo_record_presence'


class RecordPresence(models.AbstractModel):
    _name = "dwo.record.presence"
    _description = "Record Presence Publisher"

    @api.model
    def publish_presence(self, model, res_id, state='stale', fields=None):
        """Publish a payload-less ping: who changed which fields of which record."""
        user = self.env.user
        message = {
            "model": model,
            "res_id": res_id,
            "user_id": user.id,
            "user_name": user.name,
            "current_tab_id": self.env.context.get('current_tab_id'),
            "state": state,
            "fields": list(fields or []),
        }
        self.env["bus.bus"]._sendone(
            f"{CHANNEL_PREFIX}:{model}:{res_id}", 'dwo_record_presence', message)
