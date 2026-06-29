from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError


class ResUsers(models.Model):
    _inherit = "res.users"

    SELF_WRITEABLE_FIELDS = ["expiry_notify_muted", "expiry_dismiss_until"]

    expiry_notify_muted = fields.Boolean(
        string="Mute Expiry Notifications",
        help="Disable expiry notifications and form-view expiry alerts.",
    )
    expiry_dismiss_until = fields.Datetime(
        string="Dismiss Expiry Notifications Until",
        help="Notifications are skipped until this datetime.",
    )
    expiry_access_alert_mute = fields.Boolean(
        string="Mute Expiry Notifications (Legacy)",
        related="expiry_notify_muted",
        readonly=False,
        help="Legacy compatibility alias for expiry notification mute preference.",
    )
    expiry_access_alert_dismiss_until = fields.Datetime(
        string="Dismiss Expiry Notifications Until (Legacy)",
        related="expiry_dismiss_until",
        readonly=False,
        help="Legacy compatibility alias for expiry dismiss-until datetime.",
    )
    expiry_access_alert_mode = fields.Selection(
        selection=[("summary", "Summary"), ("detailed", "Detailed")],
        string="Expiry Alert Mode (Legacy)",
        default="summary",
        help="Legacy compatibility field kept for older inherited user views.",
    )
    expiry_access_alert_limit = fields.Integer(
        string="Expiry Alert Limit (Legacy)",
        default=20,
        help="Legacy compatibility field kept for older inherited user views.",
    )
    expiry_access_alert_ignore_until = fields.Datetime(
        string="Ignore Expiry Alerts Until (Legacy)",
        related="expiry_dismiss_until",
        readonly=False,
        help="Legacy compatibility alias for old ignore-until preference.",
    )

    @api.model
    def _allowed_dismiss_minutes(self):
        """Return supported dismiss duration options in minutes."""
        return [5, 15, 30, 60, 120, 240, 480, 1440, 4320, 10080, 43200]

    @api.model
    def action_set_expiry_dismiss(self, minutes):
        """Set dismiss-until datetime for the current user based on a preset duration."""
        if minutes not in self._allowed_dismiss_minutes():
            raise ValidationError(_("Invalid dismiss duration."))

        user = self.env.user
        if not user:
            raise AccessError(_("No active user found for dismiss action."))
        user.expiry_dismiss_until = fields.Datetime.now() + timedelta(minutes=minutes)
        user.expiry_notify_muted = False
        return True

    @api.model
    def action_clear_expiry_dismiss(self):
        """Clear dismiss-until datetime for the current user."""
        user = self.env.user
        if not user:
            raise AccessError(_("No active user found for dismiss clear action."))
        user.expiry_dismiss_until = False
        return True
