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


class TestRelatedFields(TransactionCase):
    """The join of Explore: the fields of a record a many2one points to, read as the caller."""

    def setUp(self):
        super().setUp()
        self.explore = self.env["dwo.dashboard.explore"]
        self.user = self.env["res.users"].create({"name": "Rel", "login": "rel_user",
                                                  "group_ids": [(6, 0, [self.env.ref("base.group_user").id])]})

    def test_a_readable_many2one_is_expandable(self):
        fields = {f["name"]: f for f in self.explore.with_user(self.user).describe_dataset("orm:res.partner")["fields"]}
        self.assertTrue(fields["country_id"]["expandable"])
        self.assertTrue(fields["parent_id"]["expandable"])
        self.assertFalse(fields["name"]["expandable"])

    def test_the_fields_of_the_related_record(self):
        answer = self.explore.with_user(self.user).describe_related("orm:res.partner", "country_id")
        names = {f["name"]: f for f in answer["fields"]}
        self.assertEqual(answer["label"], "Country")
        self.assertTrue(names["name"]["dimension"] and names["name"]["column"])
        self.assertTrue(names["currency_id"]["expandable"])          # one more step is allowed...
        deeper = self.explore.with_user(self.user).describe_related("orm:res.partner", "country_id.currency_id")
        self.assertTrue(deeper["fields"])
        self.assertFalse(any(f["expandable"] for f in deeper["fields"]))  # ...and then it stops

    def test_what_is_refused(self):
        for path in ("name", "no_such_field", "country_id.name", "a.b.c", "", "country_id.currency_id.rate_ids"):
            with self.assertRaises(AccessError, msg=path):
                self.explore.with_user(self.user).describe_related("orm:res.partner", path)
        with self.assertRaises(AccessError):
            self.explore.with_user(self.user).describe_related("sql:x", "country_id")

    def test_a_relation_to_a_model_the_caller_cannot_read_is_not_followed(self):
        self.env["ir.model.access"].search([("model_id.model", "=", "res.country")]).write({"perm_read": False})
        self.env.registry.clear_cache()
        fields = {f["name"]: f for f in self.explore.with_user(self.user).describe_dataset("orm:res.partner")["fields"]}
        self.assertFalse(fields["country_id"]["expandable"])
        with self.assertRaises(AccessError):
            self.explore.with_user(self.user).describe_related("orm:res.partner", "country_id")

    def test_a_field_through_a_relation_is_a_dimension_of_the_engine(self):
        """Ground truth: contacts grouped by the country of their parent company."""
        Partner = self.env["res.partner"]
        be, fr = (self.env["res.country"].search([("code", "=", c)]).id for c in ("BE", "FR"))
        a, b = (Partner.create({"name": "Rel Co %s" % c, "country_id": cid}) for c, cid in (("BE", be), ("FR", fr)))
        for i, parent in enumerate([a, a, a, b]):
            Partner.create({"name": "Rel Person %d" % i, "parent_id": parent.id})
        widget = {"id": "w", "type": "bar", "dataset": "orm:res.partner", "where": [["name", "like", "Rel Person"]],
                  "wells": {"axis": {"field": "parent_id.country_id"}, "values": [{"agg": "count"}]},
                  "order": [{"measure": "__count", "dir": "desc"}]}
        answer = self.env["dwo.dashboard.engine"].with_user(self.user).run_preview(widget)
        self.assertTrue(answer["ok"], answer)
        self.assertEqual([(r["labels"][0], r["values"][0]) for r in answer["result"]["rows"]], [("Belgium", 3), ("France", 1)])
