# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestExplore(TransactionCase):

    def setUp(self):
        super().setUp()
        self.internal = self.env["res.users"].create({
            "name": "Ian", "login": "exp_ian", "group_ids": [(6, 0, [self.env.ref("base.group_user").id])]})
        self.Explore = self.env["dwo.dashboard.explore"]

    def test_the_list_has_readable_business_models_only(self):
        refs = {d["ref"] for d in self.Explore.with_user(self.internal).list_datasets()}
        self.assertIn("orm:res.partner", refs)
        self.assertFalse({r for r in refs if r.startswith(("orm:ir.", "orm:base."))})
        self.assertNotIn("orm:res.users.apikeys", refs)
        admin_refs = {d["ref"] for d in self.Explore.with_user(self.env.ref("base.user_admin")).list_datasets()}
        self.assertIn("orm:ir.model", admin_refs)  # administrators may explore the technical models

    def test_a_model_the_user_cannot_read_is_absent(self):
        self.assertNotIn("orm:ir.cron", {d["ref"] for d in self.Explore.with_user(self.internal).list_datasets()})
        with self.assertRaises(AccessError):
            self.Explore.with_user(self.internal).describe_dataset("orm:ir.cron")
        with self.assertRaises(AccessError):
            self.Explore.with_user(self.internal).describe_dataset("orm:no.such.model")
        with self.assertRaises(AccessError):
            self.Explore.with_user(self.internal).describe_dataset("sql:thing")

    def test_fields_say_what_they_can_be(self):
        fields = {f["name"]: f for f in self.Explore.with_user(self.internal).describe_dataset("orm:res.partner")["fields"]}
        self.assertTrue(fields["country_id"]["dimension"] and fields["country_id"]["relation"] == "res.country")
        self.assertEqual(fields["create_date"]["intervals"], ["day", "week", "month", "quarter", "year"])
        self.assertTrue(fields["id"]["measure"] or "count_distinct" in fields["id"]["aggs"])
        self.assertIn("sum", fields["partner_latitude"]["aggs"])
        self.assertFalse(fields["child_ids"]["dimension"])  # a one2many cannot be grouped
        self.assertFalse(fields["image_1920"]["column"])  # binary: not a table column
        self.assertEqual(fields["type"]["type"], "selection")
        self.assertEqual({k for k, _l in fields["type"]["selection"]}, {"contact", "invoice", "delivery", "other"})

    def test_a_field_restricted_by_groups_is_absent_for_those_outside_the_group(self):
        field = self.env["res.partner"]._fields["ref"]
        self.addCleanup(setattr, field, "groups", field.groups)
        field.groups = "base.group_system"
        mine = {f["name"] for f in self.Explore.with_user(self.internal).describe_dataset("orm:res.partner")["fields"]}
        admin = {f["name"] for f in self.Explore.with_user(self.env.ref("base.user_admin")).describe_dataset(
            "orm:res.partner")["fields"]}
        self.assertNotIn("ref", mine)
        self.assertIn("ref", admin)

    def test_filter_options_use_the_callers_permissions(self):
        self.env["res.partner"].create({"name": "Picker One"})
        found = self.Explore.with_user(self.internal).filter_options("res.partner", "Picker One")
        self.assertEqual([name for _id, name in found], ["Picker One"])
        self.assertEqual(self.Explore.with_user(self.internal).filter_options("ir.cron", ""), [])
        self.assertEqual(self.Explore.with_user(self.internal).filter_options("no.such.model", ""), [])
        self.assertLessEqual(len(self.Explore.with_user(self.internal).filter_options("res.country", "", 10 ** 6)), 50)

    def test_report_models_are_offered_and_can_be_explored(self):
        """The SQL-view reports of Odoo (sale.report...) are how tables are combined: they must not be hidden."""
        if "sale.report" not in self.env:
            self.skipTest("the Sales app is not installed")
        user = self.env["res.users"].create({
            "name": "Sally", "login": "exp_sally",
            "group_ids": [(6, 0, [self.env.ref("base.group_user").id, self.env.ref("sales_team.group_sale_manager").id])]})
        refs = {d["ref"] for d in self.Explore.with_user(user).list_datasets()}
        self.assertIn("orm:sale.report", refs)
        widget = {"id": "r", "type": "kpi", "dataset": "orm:sale.report", "wells": {"value": {"agg": "count"}}}
        self.assertTrue(self.env["dwo.dashboard.engine"].with_user(user).run_preview(widget)["ok"])
