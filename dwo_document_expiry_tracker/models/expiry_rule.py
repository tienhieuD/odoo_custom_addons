import logging
import re
from datetime import datetime, timedelta

import pytz
from markupsafe import escape

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv.expression import AND, normalize_domain
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class DwoExpiryRule(models.Model):
    _name = "dwo.expiry.rule"
    _description = "Expiry Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence asc, id asc"

    name = fields.Char(string="Name", required=True, tracking=True, index=True,
        help="Give this rule a clear name so you can find it later. Example: 'Contract Expiry - Sales Team'.")
    active = fields.Boolean(string="Active", default=True, index=True,
        help="Turn this on to enable the rule. Turn it off to pause notifications without deleting the rule.")
    sequence = fields.Integer(string="Sequence", default=10, index=True,
        help="Controls the order rules are processed. Lower numbers run first. Example: set 10 for high priority, 50 for normal.")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
        help="Which company this rule belongs to. The rule only scans records within this company.",
    )
    rule_user_id = fields.Many2one(
        "res.users",
        string="Rule Owner",
        required=True,
        default=lambda self: self.env.user,
        index=True,
        help="The person who created this rule. Non-admin users can only send notifications to themselves. This is set automatically.",
    )
    description = fields.Text(string="Description",
        help="Describe what this rule does and why. This helps other team members understand the purpose. Example: 'Notify sales team 3 days before contracts expire'.")
    model_id = fields.Many2one(
        "ir.model",
        string="Target Object",
        required=True,
        domain=[("transient", "=", False)],
        ondelete="cascade",
        index=True,
        tracking=True,
        help="Choose which type of record to monitor. Example: select 'Contact' to track partner expirations, or 'Sale Order' to track order deadlines.",
    )
    model_name = fields.Char(string="Model Name", related="model_id.model", store=True, index=True)

    additional_domain = fields.Text(
        string="Additional Domain",
        default="[]",
        required=True,
        help=(
            "Filter which records to monitor. Only records matching this condition will trigger notifications.\n"
            "Example: [('state', '=', 'confirmed')] — only scan confirmed records.\n"
            "Leave as [] to scan all records of the chosen object."
        ),
    )
    date_mode = fields.Selection(
        [("field_based", "Based on Field"), ("custom", "On Specific Time")],
        string="Mode",
        required=True,
        default="field_based",
        tracking=True,
        help=(
            "How to determine when to send notifications:\n"
            "• Based on Field: uses a date/time value stored on each record (e.g., expiry date, deadline). You can add an offset like '3 days before'.\n"
            "• On Specific Time: sends notifications at one fixed date/time you choose, regardless of record data."
        ),
    )
    datetime_field_id = fields.Many2one(
        "ir.model.fields",
        string="Datetime Field",
        domain="[('model_id', '=', model_id), ('ttype', 'in', ('date', 'datetime'))]",
        ondelete="set null",
        help=(
            "Which date field on the record to use as the reference point.\n"
            "Example: select 'Expiry Date' or 'Deadline' — the system will calculate notification time based on this field's value plus/minus your offset."
        ),
    )
    specific_datetime = fields.Datetime(
        string="Specific Datetime",
        help=(
            "Set a fixed date and time when notifications should be triggered.\n"
            "Example: set '2026-12-31 09:00' to notify everyone on that exact date/time.\n"
            "All matching records will be flagged at this moment."
        ),
    )

    expired_after_year = fields.Integer(
        string="Expired After Year",
        default=0,
        help="Number of years to offset. Use negative to notify BEFORE the date. Example: -1 means notify 1 year before expiry.",
    )
    expired_after_month = fields.Integer(
        string="Expired After Month",
        default=0,
        help="Number of months to offset. Use negative to notify BEFORE the date. Example: -2 means notify 2 months before expiry.",
    )
    expired_after_day = fields.Integer(
        string="Expired After Day",
        default=0,
        help="Number of days to offset. Use negative to notify BEFORE the date. Example: -3 means notify 3 days before expiry. Use 7 to notify 7 days after.",
    )
    expired_after_hour = fields.Integer(
        string="Expired After Hour",
        default=0,
        help="Number of hours to offset. Use negative to notify BEFORE the date. Example: -2 means notify 2 hours before.",
    )
    expired_after_minute = fields.Integer(
        string="Expired After Minute",
        default=0,
        help="Number of minutes to offset. Example: -30 means notify 30 minutes before. Use 15 to notify 15 minutes after.",
    )
    total_expired_after_minutes = fields.Integer(
        string="Total Offset Minutes",
        compute="_compute_total_expired_after_minutes",
        store=True,
        index=True,
    )

    notify_on_form_view = fields.Boolean(
        string="Notify on Form View",
        default=True,
        help=(
            "When enabled, a warning banner appears at the top of the record when someone opens it.\n"
            "This helps users see at a glance that a record is expired or about to expire.\n"
            "Example: opening an expired contract will show a red/yellow alert banner."
        ),
    )
    notify_form_view_template = fields.Text(
        string="Form View Message Template",
        default="[{rule_name}] {record_name} — {state} (at {expiry_datetime})",
        translate=True,
        help=(
            "Customize the message shown in the form view alert banner.\n"
            "Available placeholders: {rule_name}, {record_name}, {expiry_datetime}, {state}.\n"
            "Example: '{record_name} will expire on {expiry_datetime}' shows 'Contract ABC will expire on 2026-12-31 09:00'."
        ),
    )
    notify_bus = fields.Boolean(
        string="Notify on System",
        default=True,
        help=(
            "When enabled, sends a popup notification in the Odoo interface (like a chat message).\n"
            "Users see it immediately without refreshing the page.\n"
            "Great for urgent alerts that need immediate attention."
        ),
    )
    notify_bus_template = fields.Text(
        string="Message Template",
        default="[{rule_name}] {record_name} expires at {expiry_datetime} ({state}).",
        translate=True,
        help=(
            "Customize the system notification message.\n"
            "Available placeholders: {rule_name}, {record_name}, {expiry_datetime}, {state}.\n"
            "Example: 'Attention: {record_name} is {state}!' shows 'Attention: Contract ABC is expired!'."
        ),
    )
    notify_email = fields.Boolean(
        string="Notify by Email",
        default=False,
        help=(
            "When enabled, sends an email to the recipients.\n"
            "Useful for users who are not always logged into Odoo.\n"
            "You can choose an email template below or let the system send a default message."
        ),
    )
    notify_email_template = fields.Many2one(
        "mail.template",
        string="Email Template",
        ondelete="set null",
        help=(
            "Choose a pre-designed email template for richer formatting.\n"
            "If left empty, the system sends a simple text email with expiry details.\n"
            "Tip: create templates under Settings > Technical > Email Templates."
        ),
    )

    notify_to_user_field_ids = fields.Many2many(
        "ir.model.fields",
        string="Document Owner Field",
        domain=(
            "["
            "('model_id', '=', model_id),"
            "('ttype', 'in', ('many2one', 'many2many', 'one2many')),"
            "('relation', '=', 'res.users')"
            "]"
        ),
        help=(
            "Select which field(s) on the record identify the responsible person(s).\n"
            "The system will send notifications to users found in these fields.\n"
            "Example: select 'Salesperson' and 'Reviewer' — both will receive alerts.\n"
            "You can pick multiple fields to notify everyone involved."
        ),
    )
    notify_to_user_ids = fields.Many2many(
        "res.users",
        string="Specific Users",
        help=(
            "Pick specific people who should always receive this notification.\n"
            "These users get notified regardless of who is assigned on the record.\n"
            "Example: add your manager so they always know about expiring items."
        ),
    )
    notify_to_notify_group_ids = fields.Many2many(
        "res.groups",
        string="Specific Groups",
        help=(
            "Pick user groups to notify all members.\n"
            "Everyone in the selected groups will receive the notification.\n"
            "Example: select 'Sales Manager' group to notify all sales managers."
        ),
    )
    use_notify_user_domain = fields.Boolean(
        string="Use User Domain",
        default=False,
        help=(
            "Enable this to filter recipients using a search condition.\n"
            "When checked, only users matching your condition will be notified.\n"
            "Leave unchecked if you don't need domain-based filtering."
        ),
    )
    notify_to_user_domain = fields.Text(
        string="User by Domain",
        default="[]",
        help=(
            "Define a search condition to find recipients automatically.\n"
            "Example: [('department_id.name', '=', 'Sales')] — notify all users in Sales department.\n"
            "Example: [('groups_id.name', 'ilike', 'manager')] — notify all managers.\n"
            "Only applied when 'Use User Domain' is checked."
        ),
    )
    notify_to_formular = fields.Char(
        string="Notify to User by Expression",
        help=(
            "Write a formula to dynamically find recipients based on record data.\n"
            "The formula can access the current record as 'object'.\n"
            "Example: ${object.user_id.ids} — notify the assigned user on each record.\n"
            "Example: ${object.user_id.ids + object.reviewer_id.ids} — notify both assigned user and reviewer.\n"
            "Result must be a list of user IDs."
        ),
    )

    limit_record = fields.Integer(
        string="Max Records per Scan",
        default=1000,
        help=(
            "Limit how many records are checked in one scan run.\n"
            "Set a lower number if you have a very large dataset and want faster scans.\n"
            "Example: 1000 means only the first 1000 matching records are processed per run.\n"
            "Set 0 or negative for no limit (scan everything)."
        ),
    )
    limit_notify_user = fields.Integer(
        string="Max Users per Notification",
        default=200,
        help=(
            "Limit how many people receive notifications per record.\n"
            "Prevents accidentally sending to thousands of users.\n"
            "Example: 200 means at most 200 users are notified per expiring record.\n"
            "Set 0 or negative for no limit."
        ),
    )

    advance_time_select = fields.Boolean(
        string="Advance Time Select",
        default=False,
        help=(
            "Enable this to set precise time offsets using years, months, hours, and minutes.\n"
            "When unchecked, you can only set the offset in days (simpler).\n"
            "Example: check this if you need to notify exactly 2 hours and 30 minutes before expiry."
        ),
    )
    advance_notify_user = fields.Boolean(
        string="Advance Notify User",
        default=False,
        help=(
            "Enable this to access advanced recipient options.\n"
            "When checked, you can add specific users, groups, domain filters, and expressions.\n"
            "When unchecked, notifications only go to users found in the Document Owner Field(s).\n"
            "Tip: keep unchecked for simple setups where the record owner is the only recipient."
        ),
    )

    last_run_at = fields.Datetime(string="Last Run At", readonly=True)
    last_run_summary = fields.Char(string="Last Run Summary", readonly=True)
    tracked_record_count = fields.Integer(
        string="Tracked Records",
        compute="_compute_tracked_record_count",
    )

    _sql_constraints = [
        ("uniq_name_company", "unique(name, company_id)", "Rule name must be unique per company."),
    ]

    @api.depends(
        "expired_after_year",
        "expired_after_month",
        "expired_after_day",
        "expired_after_hour",
        "expired_after_minute",
    )
    def _compute_total_expired_after_minutes(self):
        """Compute total expiry offset in minutes from year/month/day/hour/minute inputs."""
        for rule in self:
            years = rule.expired_after_year or 0
            months = rule.expired_after_month or 0
            days = rule.expired_after_day or 0
            hours = rule.expired_after_hour or 0
            minutes = rule.expired_after_minute or 0
            rule.total_expired_after_minutes = (
                years * 365 * 24 * 60
                + months * 30 * 24 * 60
                + days * 24 * 60
                + hours * 60
                + minutes
            )

    def _compute_tracked_record_count(self):
        """Count tracked expiry records linked to each rule."""
        data = self.env["dwo.expiry.record"].sudo().read_group(
            [("rule_id", "in", self.ids)],
            ["rule_id"],
            ["rule_id"],
        )
        count_map = {d["rule_id"][0]: d["rule_id_count"] for d in data}
        for rule in self:
            rule.tracked_record_count = count_map.get(rule.id, 0)

    def action_open_tracked_records(self):
        """Open list view of tracked expiry records for this rule."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Tracked Records — %s") % self.name,
            "res_model": "dwo.expiry.record",
            "view_mode": "tree,form",
            "domain": [("rule_id", "=", self.id)],
            "context": {"default_rule_id": self.id},
        }

    @api.constrains("date_mode", "datetime_field_id", "specific_datetime", "model_id")
    def _check_datetime_field(self):
        """Validate required date fields for each date mode."""
        for rule in self:
            if rule.date_mode == "field_based":
                if not rule.datetime_field_id:
                    raise ValidationError(_("Datetime field is required for field-based mode."))
                if rule.datetime_field_id.model_id != rule.model_id:
                    raise ValidationError(_("Datetime field must belong to selected model."))
                if rule.datetime_field_id.ttype not in ("date", "datetime"):
                    raise ValidationError(_("Field-based mode supports date or datetime fields only."))
            else:
                if not rule.specific_datetime:
                    raise ValidationError(_("Specific datetime is required for custom mode."))

    @api.constrains("additional_domain", "notify_to_user_domain")
    def _check_domains(self):
        """Validate configured domains for business records and recipient users."""
        for rule in self:
            rule._safe_eval_domain(rule.additional_domain, model_name=rule.model_name)
            rule._safe_eval_domain(rule.notify_to_user_domain, model_name="res.users")

    @api.constrains("notify_email", "notify_email_template", "model_name")
    def _check_email_template_model(self):
        """Ensure email template is set and targets the same model when email is enabled."""
        for rule in self:
            if rule.notify_email:
                if not rule.notify_email_template:
                    raise ValidationError(_("Email Template is required when 'Notify by Email' is enabled."))
                template_model = rule.notify_email_template.model_id.model
                if template_model and template_model != rule.model_name:
                    raise ValidationError(_("Selected email template must target the same model as the rule."))

    @api.constrains("notify_bus", "notify_bus_template", "notify_on_form_view", "notify_form_view_template")
    def _check_notification_templates(self):
        """Ensure message templates are set when their notification channels are enabled."""
        for rule in self:
            if rule.notify_bus and not rule.notify_bus_template:
                raise ValidationError(_("Message Template is required when 'Notify on System' is enabled."))
            if rule.notify_on_form_view and not rule.notify_form_view_template:
                raise ValidationError(_("Form View Message Template is required when 'Notify on Form View' is enabled."))

    @api.constrains("notify_to_user_field_ids", "model_id")
    def _check_notify_user_field_relation(self):
        """Ensure notify user fields are relation fields pointing directly to res.users."""
        for rule in self:
            for field_ref in rule.notify_to_user_field_ids:
                if field_ref.model_id != rule.model_id:
                    raise ValidationError(_("Notify user field '%s' must belong to the selected model.") % field_ref.name)
                if field_ref.ttype not in ("many2one", "many2many", "one2many"):
                    raise ValidationError(
                        _("Notify user field '%s' must be one of: many2one, many2many, or one2many.") % field_ref.name
                    )
                if field_ref.relation != "res.users":
                    raise ValidationError(_("Notify user field '%s' must be linked to res.users.") % field_ref.name)

    @api.model_create_multi
    def create(self, vals_list):
        """Create rules while enforcing non-admin anti-spam defaults."""
        vals_list = [self._enforce_non_admin_policy(dict(vals)) for vals in vals_list]
        return super().create(vals_list)

    def write(self, vals):
        """Update rules while preserving non-admin anti-spam restrictions."""
        vals = self._enforce_non_admin_policy(dict(vals))
        return super().write(vals)

    def _enforce_non_admin_policy(self, vals):
        """Force self-only recipients for custom users to avoid notification abuse."""
        if self.env.user.has_group("base.group_system"):
            return vals

        vals["rule_user_id"] = self.env.user.id
        vals["notify_to_user_ids"] = [(6, 0, [self.env.user.id])]
        vals["notify_to_notify_group_ids"] = [(5, 0, 0)]
        vals["notify_to_user_domain"] = "[]"
        vals["notify_to_formular"] = False
        vals["notify_to_user_field_ids"] = [(5, 0, 0)]
        vals["limit_notify_user"] = 1
        return vals

    def _safe_eval_domain(self, domain_text, model_name=None, object_record=None):
        """Safely evaluate and normalize a domain expression."""
        expr = domain_text or "[]"
        ctx = {
            "uid": self.env.uid,
            "user": self.env.user,
            "today": fields.Date.context_today(self),
            "now": fields.Datetime.now(),
            "object": object_record,
            "record": object_record,
        }
        try:
            domain = safe_eval(expr, ctx)
            if isinstance(domain, tuple):
                domain = list(domain)
            if not isinstance(domain, list):
                raise ValidationError(_("Domain must evaluate to a list."))
            normalize_domain(domain)
        except Exception as err:
            label = model_name or self.model_name or _("unknown model")
            raise ValidationError(_("Invalid domain for %s: %s") % (label, err)) from err
        return domain

    def _safe_eval_formula_user_ids(self, record):
        """Safely evaluate notify formula and return valid `res.users` records."""
        self.ensure_one()
        if not self.notify_to_formular:
            return self.env["res.users"]
        expr = self.notify_to_formular.strip()
        match = re.fullmatch(r"\$\{(.+)\}", expr)
        expr = match.group(1) if match else expr
        result = safe_eval(expr, {"object": record, "record": record, "uid": self.env.uid})
        if isinstance(result, int):
            result = [result]
        if not isinstance(result, (list, tuple, set)):
            raise ValidationError(_("Notify formula must return one user id or a list of user ids."))
        ids = [int(user_id) for user_id in result if isinstance(user_id, int) and user_id > 0]
        return self.env["res.users"].browse(ids).exists()

    def _resolve_users_from_field(self, record):
        """Resolve users from configured notify relation fields linked to res.users."""
        self.ensure_one()
        users = self.env["res.users"]
        for field_ref in self.notify_to_user_field_ids:
            value = record[field_ref.name]
            if field_ref.ttype == "many2one" and value:
                users |= value
            elif field_ref.ttype in ("many2many", "one2many"):
                users |= value
        return users

    def _collect_target_users(self, record):
        """Collect, deduplicate, and limit target users for one business record."""
        self.ensure_one()
        users = self.env["res.users"]
        users |= self._resolve_users_from_field(record)

        if self.advance_notify_user:
            users |= self.notify_to_user_ids
            users |= self.notify_to_notify_group_ids.mapped("users")

            if self.use_notify_user_domain:
                user_domain = self._safe_eval_domain(self.notify_to_user_domain, model_name="res.users", object_record=record)
                if user_domain:
                    users |= self.env["res.users"].search(user_domain)

            users |= self._safe_eval_formula_user_ids(record)

        users = users.exists().filtered(lambda u: u.active and not u.share)

        if not self.rule_user_id.has_group("base.group_system"):
            users = self.rule_user_id

        if self.limit_notify_user > 0:
            users = users[: self.limit_notify_user]
        return users

    def _compute_expiry_datetime(self, record):
        """Compute expiry datetime for one record using selected date mode.

        For date fields (no time component), the date is interpreted as midnight
        in the rule owner's timezone, then converted to UTC for consistent comparison.
        """
        self.ensure_one()
        if self.date_mode == "custom":
            return fields.Datetime.to_datetime(self.specific_datetime)

        source_field = self.datetime_field_id
        value = record[source_field.name] if source_field else False
        if not value:
            return False
        if source_field.ttype == "date":
            base_date = fields.Date.to_date(value)
            # Interpret date as midnight in the rule owner's timezone
            user_tz_name = self.rule_user_id.tz or self.env.context.get("tz") or "UTC"
            try:
                user_tz = pytz.timezone(user_tz_name)
            except pytz.UnknownTimeZoneError:
                user_tz = pytz.UTC
            local_dt = user_tz.localize(datetime.combine(base_date, datetime.min.time()))
            base_dt = local_dt.astimezone(pytz.UTC).replace(tzinfo=None)
        else:
            base_dt = fields.Datetime.to_datetime(value)
        return base_dt + timedelta(minutes=self.total_expired_after_minutes)

    def _record_matches_additional_domain(self, record):
        """Check whether a record still matches the configured additional domain."""
        self.ensure_one()
        domain = self._safe_eval_domain(self.additional_domain, model_name=record._name, object_record=record)
        final_domain = AND([domain, [("id", "=", record.id)]])
        return bool(record.search_count(final_domain))

    def _render_template(self, template, record, state, expiry_datetime):
        """Render notification template with `${expr}` and `{placeholder}` support."""
        self.ensure_one()
        text = template or "[{rule_name}] {record_name} expires at {expiry_datetime} ({state})."
        context = {
            "rule_name": self.name,
            "record_name": record.display_name,
            "record_id": record.id,
            "model_name": record._name,
            "expiry_datetime": expiry_datetime,
            "state": state,
            "object": record,
            "record": record,
            "rule": self,
        }

        def _replace_expr(match):
            """Evaluate one `${...}` expression from template text."""
            expr = match.group(1)
            try:
                value = safe_eval(expr, context)
            except Exception:
                value = ""
            return str(value if value is not None else "")

        text = re.sub(r"\$\{([^}]+)\}", _replace_expr, text)
        try:
            return text.format(
                rule_name=self.name,
                record_name=record.display_name,
                record_id=record.id,
                model_name=record._name,
                expiry_datetime=expiry_datetime,
                state=state,
            )
        except Exception:
            return text

    def _upsert_expiry_record(self, record, state, expiry_datetime):
        """Create or update a tracked expiry row for a business record."""
        self.ensure_one()
        model = self.env["dwo.expiry.record"]
        tracked = model.search(
            [("rule_id", "=", self.id), ("model", "=", record._name), ("res_id", "=", record.id)],
            limit=1,
        )
        vals = {
            "state": state,
            "record_name": record.display_name,
            "expiry_field_id": self.datetime_field_id.id if self.date_mode == "field_based" and self.datetime_field_id else False,
            "expiry_datetime": expiry_datetime,
            "rule_id": self.id,
            "model": record._name,
            "res_id": record.id,
            "company_id": self.company_id.id,
            "last_seen_at": fields.Datetime.now(),
        }
        if tracked:
            tracked.write(vals)
            return tracked
        return model.create(vals)

    def _should_send_notification(self, tracked_record, state):
        """Throttle notifications by state change or 24-hour resend interval."""
        tracked_record.ensure_one()
        now_dt = fields.Datetime.now()
        if not tracked_record.last_notified_at:
            return True
        if tracked_record.last_notified_state != state:
            return True
        return tracked_record.last_notified_at <= now_dt - timedelta(hours=24)

    def _filter_notifiable_users(self, users):
        """Exclude users who muted or dismissed expiry notifications."""
        now_dt = fields.Datetime.now()
        return users.filtered(
            lambda user: (not user.expiry_notify_muted)
            and (not user.expiry_dismiss_until or user.expiry_dismiss_until <= now_dt)
        )

    def _send_bus_notification(self, users, message, state):
        """Send Odoo bus notifications to target users.

        PERFORMANCE NOTE (Risk: Medium-High):
        - Each user triggers a separate bus.bus INSERT → if 500 users, that's 500 INSERTs.
        - Mitigation option A: batch bus notifications using _sendmany() instead of _sendone() loop.
        - Mitigation option B: use a queue (e.g. ir.cron or queue_job) to defer bus sends.
        """
        for user in users:
            self.env["bus.bus"]._sendone(
                user.partner_id,
                "simple_notification",
                {
                    "title": self.name,
                    "message": message,
                    "sticky": state == "expired",
                    "warning": state == "expired",
                },
            )

    def _send_email_notification(self, record, users, message):
        """Send email notification using the configured email template.

        Skips sending if no email template is configured.
        """
        if not self.notify_email_template:
            return
        users = users.filtered(lambda user: user.partner_id and user.partner_id.email)
        if not users:
            return

        if self.notify_email_template.model_id.model == record._name:
            for user in users:
                self.notify_email_template.send_mail(
                    record.id,
                    force_send=False,
                    email_values={"email_to": user.partner_id.email},
                )

    def _notify_record(self, record, tracked_record, state, expiry_datetime):
        """Legacy method: send notifications for a tracked record (used by tests).

        In production, notifications are handled by _cron_send_notifications() instead.
        This method is kept for backward compatibility and manual testing.
        """
        self.ensure_one()
        if not self.notify_bus and not self.notify_email:
            return
        if not self._should_send_notification(tracked_record, state):
            return

        users = self._collect_target_users(record)
        users = self._filter_notifiable_users(users)
        if not users:
            return

        message = self._render_template(self.notify_bus_template, record, state, expiry_datetime)
        if self.notify_bus:
            self._send_bus_notification(users, message, state)
        if self.notify_email:
            self._send_email_notification(record, users, message)

        tracked_record.write(
            {
                "last_notified_at": fields.Datetime.now(),
                "last_notified_state": state,
            }
        )

    def _get_rule_search_order(self):
        """Return deterministic search order for cron scanning."""
        self.ensure_one()
        source_field = self.datetime_field_id if self.date_mode == "field_based" else False
        if source_field and re.match(r'^[a-z_][a-z0-9_]*$', source_field.name):
            return "%s asc, id asc" % source_field.name
        return "id asc"

    def _scan_single_rule(self):
        """Phase 1: Scan records and UPSERT tracked rows using raw SQL for maximum speed.

        This method ONLY updates the dashboard (dwo.expiry.record table).
        Notifications are handled separately by _cron_send_notifications().
        Uses INSERT ... ON CONFLICT DO UPDATE for bulk performance.
        """
        self.ensure_one()
        Model = self.env[self.model_name].sudo().with_company(self.company_id)
        domain = self._safe_eval_domain(self.additional_domain, model_name=self.model_name)
        order = self._get_rule_search_order()
        limit = self.limit_record if self.limit_record > 0 else None
        records = Model.search(domain, order=order, limit=limit)

        if not records:
            self.write({
                "last_run_at": fields.Datetime.now(),
                "last_run_summary": _("No matching records found."),
            })
            return

        now_dt = fields.Datetime.now()
        cr = self.env.cr

        # Build UPSERT data
        upsert_rows = []
        for record in records:
            expiry_datetime = self._compute_expiry_datetime(record)
            if not expiry_datetime:
                continue
            state = "expired" if expiry_datetime <= now_dt else "upcoming"
            upsert_rows.append((
                self.id,                    # rule_id
                record._name,               # model
                record.id,                  # res_id
                state,                      # state
                record.display_name or "",  # record_name
                self.datetime_field_id.id if self.date_mode == "field_based" and self.datetime_field_id else None,
                expiry_datetime,            # expiry_datetime
                self.company_id.id,         # company_id
                now_dt,                     # last_seen_at
                now_dt,                     # create_date
                now_dt,                     # write_date
            ))

        if not upsert_rows:
            self.write({
                "last_run_at": fields.Datetime.now(),
                "last_run_summary": _("Processed %s records, none have valid expiry dates.") % len(records),
            })
            return

        # Batch UPSERT in chunks of 500 for controlled memory usage
        chunk_size = 500
        tracked_count = 0
        for i in range(0, len(upsert_rows), chunk_size):
            chunk = upsert_rows[i:i + chunk_size]
            # Build VALUES placeholder
            values_template = ",".join(
                cr.mogrify(
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    row
                ).decode()
                for row in chunk
            )
            # SQL UPSERT: insert or update on conflict (rule_id, model, res_id)
            # Set needs_notification = true when state changes or first time
            cr.execute("""
                INSERT INTO dwo_expiry_record
                    (rule_id, model, res_id, state, record_name, expiry_field_id,
                     expiry_datetime, company_id, last_seen_at, create_date, write_date)
                VALUES %s
                ON CONFLICT (rule_id, model, res_id) DO UPDATE SET
                    state = EXCLUDED.state,
                    record_name = EXCLUDED.record_name,
                    expiry_field_id = EXCLUDED.expiry_field_id,
                    expiry_datetime = EXCLUDED.expiry_datetime,
                    last_seen_at = EXCLUDED.last_seen_at,
                    write_date = EXCLUDED.write_date,
                    needs_notification = CASE
                        WHEN dwo_expiry_record.last_notified_state IS NULL THEN true
                        WHEN dwo_expiry_record.last_notified_state != EXCLUDED.state THEN true
                        WHEN dwo_expiry_record.last_notified_at IS NULL THEN true
                        WHEN dwo_expiry_record.last_notified_at <= (NOW() AT TIME ZONE 'UTC' - INTERVAL '24 hours') THEN true
                        ELSE dwo_expiry_record.needs_notification
                    END
            """ % values_template)
            tracked_count += len(chunk)

        # Also set needs_notification for newly inserted rows
        cr.execute("""
            UPDATE dwo_expiry_record
            SET needs_notification = true
            WHERE rule_id = %s AND last_seen_at = %s AND last_notified_at IS NULL
        """, (self.id, now_dt))

        self.write({
            "last_run_at": fields.Datetime.now(),
            "last_run_summary": _("Processed %s records, tracked %s.") % (len(records), tracked_count),
        })

    def action_run_scan(self):
        """Manual button action to run scan immediately for selected rules."""
        messages = []
        for rule in self:
            rule.with_user(rule.rule_user_id)._scan_single_rule()
            rule.invalidate_recordset(["last_run_summary", "last_run_at"])
            summary = rule.last_run_summary or _("No results.")
            messages.append(_("Rule '%s': %s") % (rule.name, summary))

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Scan Completed"),
                "message": "\n".join(messages),
                "type": "success",
                "sticky": False,
            },
        }

    @api.model
    def _cron_scan_and_notify(self):
        """Cron Phase 1: Scan all active rules and UPSERT tracked records.

        Fast phase — only database writes, no notification sending.
        Per-rule error isolation via savepoints.
        """
        rules = self.search([("active", "=", True)], order="sequence asc, id asc")
        for rule in rules:
            cr = self.env.cr
            try:
                cr.execute("SAVEPOINT cron_rule_%s" % rule.id)
                rule._scan_single_rule()
                cr.execute("RELEASE SAVEPOINT cron_rule_%s" % rule.id)
            except Exception:
                _logger.exception("Failed to scan rule %s (id=%s)", rule.name, rule.id)
                cr.execute("ROLLBACK TO SAVEPOINT cron_rule_%s" % rule.id)

    @api.model
    def _cron_send_notifications(self):
        """Cron Phase 2: Send pending notifications in batches.

        Processes tracked records flagged with needs_notification=True.
        Batch size is controlled to ensure completion within ~1 minute.
        """
        batch_limit = 200  # max records per cron run to stay under 1 minute
        ExpiryRecord = self.env["dwo.expiry.record"].sudo()

        pending = ExpiryRecord.search(
            [("needs_notification", "=", True)],
            limit=batch_limit,
            order="write_date asc",
        )
        if not pending:
            return

        # Group by rule for efficiency (pre-load rule data once)
        rule_map = {}
        for tracked in pending:
            rule_map.setdefault(tracked.rule_id.id, []).append(tracked)

        for rule_id, tracked_list in rule_map.items():
            rule = self.browse(rule_id)
            if not rule.exists() or not rule.active:
                # Rule deleted/disabled — clear flags
                ExpiryRecord.browse([t.id for t in tracked_list]).write({
                    "needs_notification": False,
                })
                continue

            # Pre-compute static recipients (users + groups) once per rule
            static_users = self.env["res.users"]
            if rule.advance_notify_user:
                static_users |= rule.notify_to_user_ids
                static_users |= rule.notify_to_notify_group_ids.mapped("users")

            for tracked in tracked_list:
                cr = self.env.cr
                try:
                    cr.execute("SAVEPOINT notify_%s" % tracked.id)
                    self._send_notification_for_tracked(rule, tracked, static_users)
                    tracked.write({
                        "needs_notification": False,
                        "last_notified_at": fields.Datetime.now(),
                        "last_notified_state": tracked.state,
                    })
                    cr.execute("RELEASE SAVEPOINT notify_%s" % tracked.id)
                except Exception:
                    _logger.exception(
                        "Failed to notify tracked record %s (rule=%s)",
                        tracked.id, rule.name,
                    )
                    cr.execute("ROLLBACK TO SAVEPOINT notify_%s" % tracked.id)
                    # Clear flag to avoid infinite retry loop
                    try:
                        tracked.write({"needs_notification": False})
                    except Exception:
                        pass

    def _send_notification_for_tracked(self, rule, tracked, static_users):
        """Send bus/email notification for one tracked record."""
        try:
            record = self.env[tracked.model].sudo().browse(tracked.res_id).exists()
        except KeyError:
            return
        if not record:
            return

        if not rule.notify_bus and not rule.notify_email:
            return

        # Resolve dynamic users from Document Owner Field
        users = self.env["res.users"]
        users |= rule._resolve_users_from_field(record)

        # Add pre-computed static users
        if rule.advance_notify_user:
            users |= static_users

            # Domain-based users
            if rule.use_notify_user_domain:
                user_domain = rule._safe_eval_domain(
                    rule.notify_to_user_domain, model_name="res.users", object_record=record
                )
                if user_domain:
                    users |= self.env["res.users"].search(user_domain)

            # Expression-based users
            users |= rule._safe_eval_formula_user_ids(record)

        users = users.exists().filtered(lambda u: u.active and not u.share)

        if not rule.rule_user_id.has_group("base.group_system"):
            users = rule.rule_user_id

        if rule.limit_notify_user > 0:
            users = users[:rule.limit_notify_user]

        users = rule._filter_notifiable_users(users)
        if not users:
            return

        message = rule._render_template(rule.notify_bus_template, record, tracked.state, tracked.expiry_datetime)
        if rule.notify_bus:
            rule._send_bus_notification(users, message, tracked.state)
        if rule.notify_email:
            rule._send_email_notification(record, users, message)

    @api.model
    def get_form_view_alerts(self, model_name, res_id):
        """Return form-view alert payload for one record and current user.

        PERFORMANCE NOTE (Risk: Medium):
        - Called on EVERY form view open for any model → high frequency.
        - Each call runs: search rules + browse record + loop (domain check + compute expiry).
        - If user opens 20 records quickly, this fires 20 times.
        - Mitigation option A: cache results client-side (JS) for N seconds per record.
        - Mitigation option B: add index on (model_name, company_id, active, notify_on_form_view).
        - Mitigation option C: use read_group or prefetch to avoid repeated domain matching.
        """
        user = self.env.user
        now_dt = fields.Datetime.now()
        if user.expiry_notify_muted:
            return {"alerts": [], "more_count": 0}
        if user.expiry_dismiss_until and user.expiry_dismiss_until > now_dt:
            return {"alerts": [], "more_count": 0}

        # Validate inputs to prevent model-name injection
        if not isinstance(model_name, str) or not isinstance(res_id, int):
            return {"alerts": [], "more_count": 0}

        rules = self.search(
            [
                ("active", "=", True),
                ("notify_on_form_view", "=", True),
                ("model_name", "=", model_name),
                ("company_id", "=", self.env.company.id),
            ],
            order="sequence asc, id asc",
        )
        if not rules:
            return {"alerts": [], "more_count": 0}

        try:
            record = self.env[model_name].browse(res_id).exists()
        except KeyError:
            return {"alerts": [], "more_count": 0}
        if not record:
            return {"alerts": [], "more_count": 0}

        alerts = []
        for rule in rules:
            if not rule._record_matches_additional_domain(record.sudo().with_company(rule.company_id)):
                continue
            expiry_datetime = rule._compute_expiry_datetime(record)
            if not expiry_datetime:
                continue
            state = "expired" if expiry_datetime <= now_dt else "upcoming"
            message = rule._render_template(rule.notify_form_view_template or rule.notify_bus_template, record, state, expiry_datetime)
            alerts.append(
                {
                    "rule_id": rule.id,
                    "rule_name": rule.name,
                    "message": message,
                    "state": state,
                    "severity": "danger" if state == "expired" else "warning",
                }
            )

        limit = 5
        return {"alerts": alerts[:limit], "more_count": max(len(alerts) - limit, 0)}
