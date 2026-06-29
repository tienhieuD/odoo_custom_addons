from datetime import timedelta

from odoo import api, fields, models, _


class DwoExpiryRecord(models.Model):
    _name = "dwo.expiry.record"
    _description = "Tracked Expiry Record"
    _order = "expiry_datetime asc, id asc"
    _rec_name = "record_name"

    state = fields.Selection(
        [("upcoming", "Upcoming"), ("expired", "Expired")],
        required=True,
        default="upcoming",
        index=True,
    )
    record_name = fields.Char(string="Record Name", required=True)
    expiry_field_id = fields.Many2one("ir.model.fields", string="Expiry Field", ondelete="set null")
    expiry_datetime = fields.Datetime(string="Expiry Datetime", required=True, index=True)

    rule_id = fields.Many2one("dwo.expiry.rule", string="Rule", required=True, ondelete="cascade", index=True)
    rule_user_id = fields.Many2one("res.users", string="Rule Owner", related="rule_id.rule_user_id", store=True, index=True)
    model = fields.Char(string="Model", required=True, index=True)
    res_id = fields.Integer(string="Record ID", required=True, index=True)
    company_id = fields.Many2one("res.company", string="Company", required=True, index=True)

    last_seen_at = fields.Datetime(string="Last Seen At", required=True, default=fields.Datetime.now)
    last_notified_at = fields.Datetime(string="Last Notified At")
    last_notified_state = fields.Selection([("upcoming", "Upcoming"), ("expired", "Expired")], string="Last Notified State")
    needs_notification = fields.Boolean(
        string="Pending Notification",
        default=False,
        index=True,
        help="Flag set by scan phase. Notify cron picks up records with this flag.",
    )

    _sql_constraints = [
        (
            "uniq_rule_record",
            "unique(rule_id, model, res_id)",
            "This record is already tracked by the same rule.",
        ),
    ]

    def action_open_record(self):
        """Open the source business record in form view after verifying access."""
        self.ensure_one()
        target = self.env[self.model].browse(self.res_id)
        target.check_access_rights("read")
        target.check_access_rule("read")
        return {
            "type": "ir.actions.act_window",
            "name": _("Business Record"),
            "res_model": self.model,
            "res_id": self.res_id,
            "view_mode": "form",
            "target": "current",
        }

    @api.autovacuum
    def _autovacuum_expiry_record_retention(self):
        """Delete tracked rows older than 30 days in safe batches."""
        cutoff = fields.Datetime.now() - timedelta(days=30)
        stale_domain = [("create_date", "<", cutoff)]
        while True:
            stale_rows = self.search(stale_domain, limit=1000, order="id asc")
            if not stale_rows:
                break
            stale_rows.unlink()
