from odoo import models, api


class RecordPresence(models.AbstractModel):
    _name = "dwo.record.presence"
    _description = "Record Presence Publisher"

    @api.model
    def publish_presence(self, model: str, res_id: int, state: str = 'stale', data: dict | None = None):
        user = self.env.user
        channel = f"dwo_record_presence:{model}:{res_id}"
        notification_type = 'dwo_record_presence'
        data = data or {}

        message = {
            "model": model,
            "res_id": res_id,
            "user_id": user.id,
            "user_name": user.name,
            "current_tab_id": self.env.context.get('current_tab_id'),
            "state": state,
            "data": data
        }

        self.env["bus.bus"]._sendone(channel=channel, notification_type=notification_type, message=message)
