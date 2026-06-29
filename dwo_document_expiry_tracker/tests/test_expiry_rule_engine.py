from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestExpiryRuleEngine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Prepare reusable users, model metadata, and templates for full method coverage tests."""
        super().setUpClass()
        cls.rule_model = cls.env["dwo.expiry.rule"]
        cls.record_model = cls.env["dwo.expiry.record"]
        cls.partner_model = cls.env["res.partner"]
        cls.user_model = cls.env["res.users"]
        cls.mail_template_model = cls.env["mail.template"]

        cls.base_group_user = cls.env.ref("base.group_user")
        cls.custom_group = cls.env.ref("dwo_document_expiry_tracker.group_expiry_custom_user")

        cls.custom_user = cls.user_model.with_context(no_reset_password=True).create(
            {
                "name": "Custom Expiry User",
                "login": "custom_expiry_user",
                "email": "custom.expiry@example.com",
                "groups_id": [(6, 0, [cls.base_group_user.id, cls.custom_group.id])],
            }
        )
        cls.normal_user = cls.user_model.with_context(no_reset_password=True).create(
            {
                "name": "Normal Expiry User",
                "login": "normal_expiry_user",
                "email": "normal.expiry@example.com",
                "groups_id": [(6, 0, [cls.base_group_user.id])],
            }
        )

        cls.model_partner = cls.env["ir.model"]._get("res.partner")
        cls.model_users = cls.env["ir.model"]._get("res.users")
        cls.field_create_date = cls.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "create_date")],
            limit=1,
        )
        cls.field_user_id = cls.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "user_id")],
            limit=1,
        )
        cls.field_color = cls.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "color"), ("ttype", "=", "integer")],
            limit=1,
        )

        cls.partner_template = cls.mail_template_model.create(
            {
                "name": "Partner Expiry Template",
                "model_id": cls.model_partner.id,
                "subject": "Expiry Alert",
                "body_html": "<p>Expiry alert for ${object.name}</p>",
            }
        )
        cls.users_template = cls.mail_template_model.create(
            {
                "name": "Users Template",
                "model_id": cls.model_users.id,
                "subject": "Users Alert",
                "body_html": "<p>Users alert for ${object.name}</p>",
            }
        )

    def _create_partner(self, name, owner):
        """Create a partner with a user owner for rule tests."""
        return self.partner_model.create({"name": name, "user_id": owner.id})

    def _create_rule(self, name, **extra):
        """Create a baseline rule with optional overrides."""
        vals = {
            "name": name,
            "model_id": self.model_partner.id,
            "date_mode": "custom",
            "specific_datetime": fields.Datetime.now(),
            "notify_bus": False,
            "notify_on_form_view": False,
            "notify_email": False,
            "additional_domain": "[]",
        }
        vals.update(extra)
        return self.rule_model.create(vals)

    def test_compute_total_minutes_supports_negative_values(self):
        """Verify total offset minutes supports negative values for pre-expiry alerts."""
        rule = self._create_rule(
            "Minutes Negative",
            expired_after_day=-1,
            expired_after_hour=2,
        )
        self.assertEqual(rule.total_expired_after_minutes, -1320)

    def test_field_based_rule_requires_datetime_field(self):
        """Ensure field-based mode fails without datetime field."""
        with self.assertRaises(ValidationError):
            self._create_rule("Missing Datetime Field", date_mode="field_based", datetime_field_id=False)

    def test_custom_rule_requires_specific_datetime(self):
        """Ensure custom mode fails without specific datetime value."""
        with self.assertRaises(ValidationError):
            self._create_rule("Missing Specific Datetime", date_mode="custom", specific_datetime=False)

    def test_invalid_domains_are_rejected(self):
        """Ensure malformed domains fail during validation."""
        with self.assertRaises(ValidationError):
            self._create_rule("Invalid Domain", additional_domain="[('name', '=', 'A'")
        with self.assertRaises(ValidationError):
            self._create_rule("Invalid User Domain", notify_to_user_domain="[('id', '=', ]")

    def test_email_template_must_match_rule_model(self):
        """Ensure selected email template model must match rule model."""
        with self.assertRaises(ValidationError):
            self._create_rule(
                "Template Mismatch",
                notify_email=True,
                notify_email_template=self.users_template.id,
            )

    def test_non_admin_create_forces_self_recipient_policy(self):
        """Ensure non-admin cannot configure notification recipients for others."""
        rule = self.rule_model.with_user(self.custom_user).create(
            {
                "name": "Custom Self Policy",
                "model_id": self.model_partner.id,
                "date_mode": "custom",
                "specific_datetime": fields.Datetime.now(),
                "notify_to_user_ids": [(6, 0, [self.normal_user.id])],
                "notify_to_notify_group_ids": [(6, 0, [self.base_group_user.id])],
                "notify_to_user_domain": "[('id', '=', %d)]" % self.normal_user.id,
                "notify_to_formular": "${[object.user_id.id]}",
                "limit_notify_user": 999,
            }
        )
        self.assertEqual(rule.rule_user_id, self.custom_user)
        self.assertEqual(rule.notify_to_user_ids, self.custom_user)
        self.assertEqual(rule.notify_to_notify_group_ids, self.env["res.groups"])
        self.assertEqual(rule.notify_to_user_domain, "[]")
        self.assertFalse(rule.notify_to_formular)
        self.assertEqual(rule.limit_notify_user, 1)

    def test_non_admin_write_keeps_self_recipient_policy(self):
        """Ensure non-admin updates still keep self-only recipient constraints."""
        rule = self.rule_model.with_user(self.custom_user).create(
            {
                "name": "Custom Write Policy",
                "model_id": self.model_partner.id,
                "date_mode": "custom",
                "specific_datetime": fields.Datetime.now(),
            }
        )
        rule.with_user(self.custom_user).write({"notify_to_user_ids": [(6, 0, [self.normal_user.id])]})
        self.assertEqual(rule.notify_to_user_ids, self.custom_user)

    def test_safe_eval_domain_and_formula_methods(self):
        """Ensure domain and formula safe-eval helpers return valid values."""
        partner = self._create_partner("Safe Eval Partner", self.normal_user)
        rule = self._create_rule("Safe Eval Rule", notify_to_formular="${[object.user_id.id]}")
        domain = rule._safe_eval_domain("[('id', '=', %d)]" % self.normal_user.id, model_name="res.users")
        self.assertEqual(domain, [("id", "=", self.normal_user.id)])
        users = rule._safe_eval_formula_user_ids(partner)
        self.assertEqual(users, self.normal_user)

    def test_resolve_users_from_field_many2one(self):
        """Ensure m2o res.users field can resolve users."""
        partner = self._create_partner("Field Resolve M2O", self.normal_user)
        rule = self._create_rule("Resolve M2O", notify_to_user_field_ids=[(6, 0, [self.field_user_id.id])])
        users = rule._resolve_users_from_field(partner)
        self.assertEqual(users, self.normal_user)

    def test_notify_user_field_must_be_user_relation_field(self):
        """Ensure notify user field rejects non-relation or non-res.users targets."""
        if not self.field_color:
            self.skipTest("res.partner.color integer field is unavailable in this environment.")
        with self.assertRaises(ValidationError):
            self._create_rule("Reject Integer Notify Field", notify_to_user_field_ids=[(6, 0, [self.field_color.id])])

    def test_collect_target_users_with_domain_formula_and_limit(self):
        """Ensure recipients are merged from explicit users, domain, and formula, then limited."""
        partner = self._create_partner("Collect Users", self.normal_user)
        rule = self._create_rule(
            "Collect Rule",
            advance_notify_user=True,
            use_notify_user_domain=True,
            notify_to_user_ids=[(6, 0, [self.custom_user.id])],
            notify_to_user_domain="[('id', '=', %d)]" % self.normal_user.id,
            notify_to_formular="${[object.user_id.id]}",
            limit_notify_user=1,
        )
        users = rule._collect_target_users(partner)
        self.assertEqual(len(users), 1)

    def test_compute_expiry_datetime_for_both_modes(self):
        """Ensure expiry datetime computes correctly for field and custom modes."""
        partner = self._create_partner("Expiry Compute", self.normal_user)
        custom_target = fields.Datetime.now() + timedelta(hours=2)
        custom_rule = self._create_rule("Custom Datetime", specific_datetime=custom_target, expired_after_minute=10)
        custom_dt = custom_rule._compute_expiry_datetime(partner)
        self.assertEqual(custom_dt, fields.Datetime.to_datetime(custom_target))

        field_rule = self._create_rule(
            "Field Datetime",
            date_mode="field_based",
            datetime_field_id=self.field_create_date.id,
            expired_after_minute=-5,
        )
        field_dt = field_rule._compute_expiry_datetime(partner)
        self.assertEqual(
            field_dt,
            fields.Datetime.to_datetime(partner.create_date) - timedelta(minutes=5),
        )

    def test_record_domain_match_and_template_rendering(self):
        """Ensure domain matching and template rendering with expressions work."""
        partner = self._create_partner("Render Partner", self.normal_user)
        rule = self._create_rule(
            "Template Rule",
            additional_domain="[('id', '=', %d)]" % partner.id,
            notify_bus_template="Rule {rule_name} -> ${object.name} ({state})",
        )
        self.assertTrue(rule._record_matches_additional_domain(partner))
        rendered = rule._render_template(rule.notify_bus_template, partner, "upcoming", fields.Datetime.now())
        self.assertIn("Render Partner", rendered)

    def test_upsert_record_and_throttle_logic(self):
        """Ensure upsert updates existing row and throttle logic behaves as expected."""
        partner = self._create_partner("Upsert Partner", self.normal_user)
        rule = self._create_rule("Upsert Rule")
        tracked = rule._upsert_expiry_record(partner, "upcoming", fields.Datetime.now() + timedelta(hours=1))
        self.assertTrue(tracked)
        tracked_2 = rule._upsert_expiry_record(partner, "expired", fields.Datetime.now() - timedelta(hours=1))
        self.assertEqual(tracked.id, tracked_2.id)
        tracked_2.last_notified_at = fields.Datetime.now()
        tracked_2.last_notified_state = "expired"
        self.assertFalse(rule._should_send_notification(tracked_2, "expired"))
        self.assertTrue(rule._should_send_notification(tracked_2, "upcoming"))

    def test_filter_notifiable_users(self):
        """Ensure muted and dismissed users are excluded from notification targets."""
        self.custom_user.expiry_notify_muted = True
        self.normal_user.expiry_dismiss_until = fields.Datetime.now() + timedelta(hours=1)
        users = self.env["res.users"] | self.custom_user | self.normal_user
        rule = self._create_rule("Filter Users Rule")
        filtered = rule._filter_notifiable_users(users)
        self.assertFalse(filtered)
        self.custom_user.expiry_notify_muted = False
        self.normal_user.expiry_dismiss_until = False

    def test_send_bus_notification(self):
        """Ensure bus notification method calls bus backend for each user."""
        rule = self._create_rule("Bus Send Rule")
        users = self.env["res.users"] | self.custom_user | self.normal_user
        with patch.object(type(self.env["bus.bus"]), "_sendone", autospec=True) as mock_send:
            rule._send_bus_notification(users, "Test bus message", "upcoming")
            self.assertEqual(mock_send.call_count, 2)

    def test_send_email_notification_with_template(self):
        """Ensure email notification sends via template when configured."""
        rule = self._create_rule(
            "Email Send Rule",
            notify_email=True,
            notify_email_template=self.partner_template.id,
        )
        partner = self._create_partner("Email Partner", self.normal_user)
        users = self.env["res.users"] | self.custom_user | self.normal_user
        with patch.object(type(self.partner_template), "send_mail", autospec=True, return_value=True) as mock_send:
            rule._send_email_notification(partner, users, "Email message")
            self.assertTrue(mock_send.called)

    def test_send_email_notification_skips_without_template(self):
        """Ensure email notification is skipped when no template is configured."""
        rule = self._create_rule("Email No Template Rule")
        # Bypass constraint by directly setting field
        rule.notify_email_template = False
        partner = self._create_partner("Email Skip Partner", self.normal_user)
        users = self.env["res.users"] | self.custom_user | self.normal_user
        # Should not raise any error, just skip
        rule._send_email_notification(partner, users, "Email message")

    def test_notify_record_updates_notified_fields(self):
        """Ensure notify record updates tracked notification metadata."""
        partner = self._create_partner("Notify Record Partner", self.normal_user)
        rule = self._create_rule(
            "Notify Record Rule",
            notify_bus=True,
            notify_bus_template="[{rule_name}] {record_name} ({state})",
            advance_notify_user=True,
            notify_to_user_ids=[(6, 0, [self.normal_user.id])],
        )
        tracked = rule._upsert_expiry_record(partner, "expired", fields.Datetime.now() - timedelta(minutes=1))
        with patch.object(type(self.env["bus.bus"]), "_sendone", autospec=True):
            rule._notify_record(partner, tracked, "expired", tracked.expiry_datetime)
        self.assertEqual(tracked.last_notified_state, "expired")
        self.assertTrue(tracked.last_notified_at)

    def test_search_order_scan_and_actions(self):
        """Ensure order generation, scan action, and cron entrypoint execute successfully."""
        partner = self._create_partner("Scan Action Partner", self.normal_user)
        rule = self._create_rule(
            "Scan Action Rule",
            date_mode="field_based",
            datetime_field_id=self.field_create_date.id,
            additional_domain="[('id', '=', %d)]" % partner.id,
            notify_bus=False,
            notify_email=False,
            limit_record=10,
        )
        self.assertIn(self.field_create_date.name, rule._get_rule_search_order())
        rule.action_run_scan()
        self.assertTrue(self.record_model.search([("rule_id", "=", rule.id)]))
        self.rule_model._cron_scan_and_notify()

    def test_get_form_view_alerts(self):
        """Ensure form alert API returns alerts and respects mute/dismiss controls."""
        partner = self._create_partner("Form Alert Partner", self.normal_user)
        rule = self._create_rule(
            "Form Alert Rule",
            notify_on_form_view=True,
            notify_form_view_template="Alert {record_name} ({state})",
            notify_bus=False,
            notify_email=False,
            additional_domain="[('id', '=', %d)]" % partner.id,
        )
        payload = self.rule_model.get_form_view_alerts("res.partner", partner.id)
        self.assertTrue(payload["alerts"])

        self.env.user.expiry_notify_muted = True
        muted_payload = self.rule_model.get_form_view_alerts("res.partner", partner.id)
        self.assertFalse(muted_payload["alerts"])
        self.env.user.expiry_notify_muted = False
        self.env.user.expiry_dismiss_until = fields.Datetime.now() + timedelta(hours=1)
        dismissed_payload = self.rule_model.get_form_view_alerts("res.partner", partner.id)
        self.assertFalse(dismissed_payload["alerts"])
        self.env.user.expiry_dismiss_until = False
        rule.unlink()

    def test_expiry_record_action_and_retention(self):
        """Ensure tracked record action payload and autovacuum retention both work."""
        partner = self._create_partner("Retention Partner", self.normal_user)
        rule = self._create_rule("Retention Rule")
        tracked = self.record_model.create(
            {
                "state": "expired",
                "record_name": "Retention Row",
                "expiry_datetime": fields.Datetime.now() - timedelta(days=35),
                "rule_id": rule.id,
                "model": "res.partner",
                "res_id": partner.id,
                "company_id": self.env.company.id,
                "last_seen_at": fields.Datetime.now(),
            }
        )
        action = tracked.action_open_record()
        self.assertEqual(action["res_model"], "res.partner")
        self.assertEqual(action["res_id"], partner.id)

        old_dt = fields.Datetime.to_string(fields.Datetime.now() - timedelta(days=45))
        self.env.cr.execute("UPDATE dwo_expiry_record SET create_date = %s WHERE id = %s", (old_dt, tracked.id))
        self.record_model._autovacuum_expiry_record_retention()
        self.assertFalse(self.record_model.search([("id", "=", tracked.id)]))

    def test_res_users_dismiss_methods(self):
        """Ensure dismiss helper methods on users set and clear dismiss-until properly."""
        self.user_model.action_set_expiry_dismiss(5)
        self.assertTrue(self.env.user.expiry_dismiss_until)
        self.user_model.action_clear_expiry_dismiss()
        self.assertFalse(self.env.user.expiry_dismiss_until)

    def test_non_admin_can_dismiss_notifications(self):
        """Ensure non-admin users can dismiss and clear expiry notifications (SELF_WRITEABLE_FIELDS)."""
        user_model = self.user_model.with_user(self.custom_user)
        user_model.action_set_expiry_dismiss(15)
        self.assertTrue(self.custom_user.expiry_dismiss_until)
        user_model.action_clear_expiry_dismiss()
        self.assertFalse(self.custom_user.expiry_dismiss_until)

    def test_get_form_view_alerts_rejects_invalid_model(self):
        """Ensure form alerts gracefully handle invalid model names without error."""
        payload = self.rule_model.get_form_view_alerts("nonexistent.model.xyz", 1)
        self.assertEqual(payload["alerts"], [])
        payload2 = self.rule_model.get_form_view_alerts(123, 1)
        self.assertEqual(payload2["alerts"], [])

    def test_action_open_record_checks_access(self):
        """Ensure action_open_record returns action dict for accessible records."""
        partner = self._create_partner("Access Check Partner", self.normal_user)
        rule = self._create_rule("Access Rule")
        tracked = self.record_model.create(
            {
                "state": "upcoming",
                "record_name": "Access Row",
                "expiry_datetime": fields.Datetime.now(),
                "rule_id": rule.id,
                "model": "res.partner",
                "res_id": partner.id,
                "company_id": self.env.company.id,
                "last_seen_at": fields.Datetime.now(),
            }
        )
        action = tracked.action_open_record()
        self.assertEqual(action["res_model"], "res.partner")
        self.assertEqual(action["res_id"], partner.id)

    def test_scan_uses_batch_upsert(self):
        """Ensure scan creates tracked records in batch for multiple matching records."""
        partners = self.partner_model.create([
            {"name": "Batch P1", "user_id": self.normal_user.id},
            {"name": "Batch P2", "user_id": self.normal_user.id},
            {"name": "Batch P3", "user_id": self.normal_user.id},
        ])
        domain = "[('id', 'in', %s)]" % partners.ids
        rule = self._create_rule(
            "Batch Scan Rule",
            additional_domain=domain,
            notify_bus=False,
            notify_email=False,
        )
        rule.action_run_scan()
        tracked = self.record_model.search([("rule_id", "=", rule.id)])
        self.assertEqual(len(tracked), 3)

    def test_scan_sets_needs_notification_flag(self):
        """Ensure scan phase sets needs_notification=True for new tracked records."""
        partner = self._create_partner("Notify Flag Partner", self.normal_user)
        rule = self._create_rule(
            "Notify Flag Rule",
            additional_domain="[('id', '=', %d)]" % partner.id,
        )
        rule._scan_single_rule()
        tracked = self.record_model.search([("rule_id", "=", rule.id), ("res_id", "=", partner.id)])
        self.assertTrue(tracked.needs_notification)

    def test_cron_send_notifications_clears_flag(self):
        """Ensure notify cron processes pending records and clears the flag."""
        partner = self._create_partner("Cron Notify Partner", self.normal_user)
        rule = self._create_rule(
            "Cron Notify Rule",
            notify_bus=True,
            notify_bus_template="[{rule_name}] {record_name}",
            notify_to_user_field_ids=[(6, 0, [self.field_user_id.id])],
            additional_domain="[('id', '=', %d)]" % partner.id,
        )
        rule._scan_single_rule()
        tracked = self.record_model.search([("rule_id", "=", rule.id)])
        self.assertTrue(tracked.needs_notification)

        with patch.object(type(self.env["bus.bus"]), "_sendone", autospec=True):
            self.rule_model._cron_send_notifications()
        tracked.invalidate_recordset()
        self.assertFalse(tracked.needs_notification)
        self.assertTrue(tracked.last_notified_at)

    def test_template_required_when_bus_enabled(self):
        """Ensure bus template is required when notify_bus is enabled."""
        with self.assertRaises(ValidationError):
            self._create_rule(
                "Bus No Template",
                notify_bus=True,
                notify_bus_template=False,
            )

    def test_template_required_when_form_view_enabled(self):
        """Ensure form view template is required when notify_on_form_view is enabled."""
        with self.assertRaises(ValidationError):
            self._create_rule(
                "Form No Template",
                notify_on_form_view=True,
                notify_form_view_template=False,
            )

    def test_advance_notify_user_controls_recipients(self):
        """Ensure advance_notify_user=False excludes advanced recipients from collection."""
        partner = self._create_partner("Advance Off Partner", self.normal_user)
        rule = self._create_rule(
            "Advance Off Rule",
            advance_notify_user=False,
            notify_to_user_ids=[(6, 0, [self.custom_user.id])],
            notify_to_user_field_ids=[(6, 0, [self.field_user_id.id])],
        )
        users = rule._collect_target_users(partner)
        # Only Document Owner Field users, not Specific Users (advance is off)
        self.assertIn(self.normal_user, users)
        self.assertNotIn(self.custom_user, users)
