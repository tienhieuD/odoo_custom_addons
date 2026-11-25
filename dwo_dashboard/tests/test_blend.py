# -*- coding: utf-8 -*-
import copy
import datetime as dt
import json
from unittest.mock import patch

from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase

from ..engine import dates
from .test_engine import EngineCase

PREFIX = "Bl "


def definition(**extra):
    """Bytes of attachments (a datetime) beside the exchange rates recorded (a date), by month and by who created them."""
    defn = {
        "schema": "dwo-dataset/1", "type": "blend", "code": "files_rates", "label": "Files and rates",
        "sources": [{"name": "files", "dataset": "orm:ir.attachment", "where": [["name", "like", PREFIX]]},
                    {"name": "rates", "dataset": "orm:res.currency.rate"}],
        "dimensions": [
            {"name": "month", "label": "Date", "kind": "date", "map": {"files": "create_date", "rates": "name"}},
            {"name": "who", "label": "Who", "kind": "many2one", "comodel": "res.users",
             "map": {"files": "create_uid", "rates": "create_uid"}}],
        "metrics": [
            {"name": "bytes", "label": "Bytes", "source": "files", "agg": "sum", "field": "file_size"},
            {"name": "avg_bytes", "label": "Average file", "source": "files", "agg": "avg", "field": "file_size"},
            {"name": "rates", "label": "Rates", "source": "rates", "agg": "count"},
            {"name": "big_rates", "label": "Rates above 1", "source": "rates", "agg": "count", "where": [["rate", ">", 1]]}]}
    defn.update(extra)
    return defn


class BlendCase(EngineCase):

    def setUp(self):
        super().setUp()
        self.admin = self.env.ref("base.user_admin")
        self.manager = self.env["res.users"].create({"name": "Bl Manager", "login": "bl_manager", "group_ids": [
            (6, 0, [self.env.ref("base.group_user").id, self.env.ref("dwo_dashboard.group_dwo_dashboard_manager").id])]})
        # files: (created at UTC, bytes). 20:00 UTC on 31 Dec is already 1 January in Ho Chi Minh City (UTC+7)
        for i, (stamp, size) in enumerate([("2025-12-31 20:00:00", 100), ("2025-12-31 20:00:00", 50), ("2025-11-10 08:00:00", 7)]):
            att = self.env["ir.attachment"].create({"name": "%s%d" % (PREFIX, i), "raw": b"x" * size})
            self.env.cr.execute("UPDATE ir_attachment SET create_date = %s WHERE id = %s", [stamp, att.id])
        # rates: dates (a date field): two in January 2026 (one above 1), one in March 2026
        self.env["res.currency.rate"].search([("name", ">=", "2025-11-01")]).unlink()
        usd, eur = self.env.ref("base.USD"), self.env.ref("base.EUR")
        company = self.env.company
        for cur, day, rate in ((usd, "2026-01-15", 1.5), (eur, "2026-01-20", 0.8), (eur, "2026-03-05", 2.0)):
            self.env["res.currency.rate"].create({"currency_id": cur.id, "name": day, "rate": rate, "company_id": company.id})
        self.env.invalidate_all()
        self.dataset = self.env["dwo.dataset"].create({"kind": "blend", "code": "files_rates", "label": "Files and rates",
                                                       "definition_text": json.dumps(definition())})

    def widget(self, kind="bar", axis=None, values=("bytes", "rates"), **extra):
        wells = {"axis": axis or {"field": "month", "interval": "month"}, "values": [{"metric": m} for m in values]}
        if kind in ("pie", "doughnut"):
            wells = {"category": wells["axis"], "value": wells["values"][0]}
        return dict({"id": "b", "type": kind, "dataset": "blend:files_rates", "wells": wells}, **extra)

    def run_w(self, widget, user=None, tz="Asia/Ho_Chi_Minh", **kw):
        response = self.run_as(user or self.admin, widget, tz=tz, **kw)
        self.assertTrue(response["ok"], response)
        return response["result"]

    def table(self, result):
        return {r["labels"][0]: r["values"] for r in result["rows"]}


class TestBlendEngine(BlendCase):

    def test_a_date_and_a_datetime_meet_in_the_viewers_months(self):
        result = self.run_w(self.widget())
        self.assertEqual([m["key"] for m in result["measures"]], ["bytes", "rates"])
        self.assertEqual(self.table(result), {
            "November 2025": [7, 0],       # files only
            "January 2026": [150, 2],      # 20:00 UTC on 31 Dec is January here: files and rates share the row
            "March 2026": [0, 1]})         # rates only
        self.assertEqual([r["labels"][0] for r in result["rows"]], ["November 2025", "January 2026", "March 2026"])  # by date
        utc = self.run_w(self.widget(), tz="UTC")
        self.assertEqual(self.table(utc), {"November 2025": [7, 0], "December 2025": [150, 0], "January 2026": [0, 2], "March 2026": [0, 1]})

    def test_what_a_source_does_not_have_is_zero_or_empty(self):
        rows = self.table(self.run_w(self.widget(values=("avg_bytes", "rates", "big_rates"))))
        self.assertEqual(rows["January 2026"], [75, 2, 1])
        self.assertEqual(rows["March 2026"], [None, 1, 1])     # no file: an average of nothing is empty, not 0
        self.assertEqual(rows["November 2025"], [7, 0, 0])

    def test_order_and_limit_come_after_the_merge(self):
        widget = self.widget(order=[{"measure": "rates", "dir": "desc"}], limit=2)
        result = self.run_w(widget)
        self.assertEqual([r["labels"][0] for r in result["rows"]], ["January 2026", "March 2026"])
        self.assertTrue(result["truncated"]["axis"])
        widget = self.widget(order=[{"field": "month", "dir": "desc"}])
        self.assertEqual([r["labels"][0] for r in self.run_w(widget)["rows"]], ["March 2026", "January 2026", "November 2025"])

    def test_a_many2one_dimension(self):
        result = self.run_w(self.widget(axis={"field": "who"}))
        total = {k: sum(r["values"][i] for r in result["rows"]) for i, k in enumerate(("bytes", "rates"))}
        self.assertEqual(total, {"bytes": 157, "rates": 3})
        self.assertEqual({r["labels"][0] for r in result["rows"]} - {"None"}, {r["labels"][0] for r in result["rows"] if r["keys"][0]})

    def test_a_kpi_and_a_pie(self):
        kpi = self.run_w({"id": "k", "type": "kpi", "dataset": "blend:files_rates", "wells": {"value": {"metric": "bytes"}}})
        self.assertEqual(kpi["rows"][0]["values"], [157.0])
        pie = self.run_w(self.widget("pie", values=("rates",), order=[{"measure": "rates", "dir": "desc"}]))
        self.assertEqual(sum(r["values"][0] for r in pie["rows"]), 3)

    def test_a_page_filter_reaches_every_source(self):
        flt = {"id": "who", "type": "relation", "model": "res.users", "label": "Who",
               "bind": [{"dataset": "blend:files_rates", "field": "who"}]}
        mine = self.run_w(self.widget(axis={"field": "month", "interval": "month"}), filters=[flt], values={"who": [self.admin.id]})
        none = self.run_w(self.widget(axis={"field": "month", "interval": "month"}), filters=[flt], values={"who": [self.manager.id]})
        self.assertEqual(sum(r["values"][0] for r in none["rows"]), 0)   # nothing by that person, in either source
        self.assertEqual(sum(r["values"][1] for r in none["rows"]), 0)
        everything = self.run_w(self.widget(axis={"field": "month", "interval": "month"}))
        self.assertLessEqual(sum(r["values"][0] for r in mine["rows"]), sum(r["values"][0] for r in everything["rows"]))

    def test_a_date_filter_reaches_both_a_date_and_a_datetime(self):
        flt = {"id": "when", "type": "date", "label": "When", "default": "all", "bind": [{"dataset": "blend:files_rates", "field": "month"}]}
        with patch.object(dates, "today_in_tz", return_value=dt.date(2026, 6, 15)):
            everything = self.run_w(self.widget(), filters=[flt], values={"when": "all"})
            # "this year" is 2026: the rates of January and March (dates), and the files created on 31 December at 20:00 UTC,
            # which is 1 January in Ho Chi Minh City (a datetime); the file of November 2025 is out
            inside = self.run_w(self.widget(), filters=[flt], values={"when": "this_year"})
            before = self.run_w(self.widget(), filters=[flt], values={"when": "last_year"})
        self.assertEqual((sum(r["values"][0] for r in everything["rows"]), sum(r["values"][1] for r in everything["rows"])), (157, 3))
        self.assertEqual(self.table(inside), {"January 2026": [150, 2], "March 2026": [0, 1]})
        self.assertEqual(self.table(before), {"November 2025": [7, 0]})

    def test_one_source_the_viewer_cannot_read_refuses_the_whole_widget(self):
        self.env["ir.model.access"].search([("model_id.model", "=", "res.currency.rate")]).write({"perm_read": False})
        self.env.registry.clear_cache()
        plain = self.env["res.users"].create({"name": "Plain", "login": "bl_plain", "group_ids": [(6, 0, [self.env.ref("base.group_user").id])]})
        answer = self.run_as(plain, self.widget())
        self.assertEqual((answer["ok"], answer["error"]["code"]), (False, "access"))   # not half the numbers

    def test_the_time_budget_is_shared(self):
        self.env["ir.config_parameter"].sudo().set_param("dwo_dashboard.query_timeout", "1")
        self.assertTrue(self.run_as(self.admin, self.widget())["ok"])   # a normal blend is far under it


class TestBlendValidation(BlendCase):

    def page(self, *widgets):
        return {"schema": "dwo-dashboard/1", "grid": {"cols": 12},
                "widgets": [dict(w, x=0, y=3 * i, w=6, h=3) for i, w in enumerate(widgets)]}

    def errors(self, *widgets, user=None):
        result = self.env["dwo.dashboard.spec"].with_user(user or self.admin).validate(self.page(*widgets))
        return {(e["path"], e["code"]) for e in result["errors"]}

    def test_a_good_widget(self):
        self.assertEqual(self.errors(self.widget()), set())

    def test_what_a_blend_widget_cannot_do(self):
        w = self.widget()
        cases = {
            ("/widgets/0/where", "not_allowed"): dict(w, where=[["name", "=", "x"]]),
            ("/widgets/0/wells/axis/field", "field"): dict(w, wells=dict(w["wells"], axis={"field": "nope", "interval": "month"})),
            ("/widgets/0/wells/axis/interval", "required"): dict(w, wells=dict(w["wells"], axis={"field": "month"})),
            ("/widgets/0/wells/axis/interval", "type"): dict(w, wells=dict(w["wells"], axis={"field": "who", "interval": "month"})),
            ("/widgets/0/wells/values/0", "metric"): dict(w, wells=dict(w["wells"], values=[{"agg": "count"}])),
            ("/widgets/0/wells/values/0/metric", "metric"): dict(w, wells=dict(w["wells"], values=[{"metric": "nope"}])),
            ("/widgets/0/wells/legend", "capability"): dict(w, wells=dict(w["wells"], values=[{"metric": "bytes"}], legend={"field": "who"})),
            ("/widgets/0/type", "capability"): dict(w, type="table", wells={"columns": [{"field": "who"}]}),
            ("/widgets/0/options/show_totals", "capability"): dict(self.widget("pivot", wells=None) if False else w, type="pivot", wells={"rows": [{"field": "who"}], "values": [{"metric": "bytes"}]}, options={"show_totals": True}),
        }
        for expected, widget in cases.items():
            self.assertIn(expected, self.errors(widget), expected)
        compare = dict({"id": "k", "type": "kpi", "dataset": "blend:files_rates", "wells": {"value": {"metric": "bytes"}}},
                       compare={"field": "month", "period": "this_month"})
        self.assertTrue(any(code == "capability" for _p, code in self.errors(compare)))
        pie = self.widget("pie", options={"other": True})
        self.assertIn(("/widgets/0/options/other", "capability"), self.errors(pie))

    def test_a_filter_must_fit_the_dimension_it_is_bound_to(self):
        page = self.page(self.widget())
        page["filters"] = [{"id": "f", "type": "date", "label": "x", "default": "all", "bind": [{"dataset": "blend:files_rates", "field": "who"}]}]
        result = self.env["dwo.dashboard.spec"].with_user(self.admin).validate(page)
        self.assertIn("/filters/0/bind/0/field", {e["path"] for e in result["errors"]})
        page["filters"][0]["bind"][0]["field"] = "month"
        self.assertTrue(self.env["dwo.dashboard.spec"].with_user(self.admin).validate(page)["valid"])

    def test_a_field_the_author_cannot_read_is_refused(self):
        self.patch(self.env["res.currency.rate"]._fields["rate"], "groups", "base.group_system")
        plain = self.env["res.users"].create({"name": "Plain", "login": "bl_plain2", "group_ids": [(6, 0, [self.env.ref("base.group_user").id])]})
        self.assertIn(("/widgets/0/dataset", "access"), {(p, c) for p, c in self.errors(self.widget(values=("big_rates",)), user=plain)})

    def test_a_definition_must_be_valid(self):
        Dataset = self.env["dwo.dataset"]

        def make(**change):
            defn = copy.deepcopy(definition(code="other"))
            for key, value in change.items():
                defn[key] = value
            return Dataset.create({"kind": "blend", "code": "other", "label": "x", "definition_text": json.dumps(defn)})
        with self.assertRaises(ValidationError):   # one source is not a blend
            make(sources=definition()["sources"][:1])
        with self.assertRaises(ValidationError):   # a dimension that one source does not map
            make(dimensions=[{"name": "month", "kind": "date", "map": {"files": "create_date"}}])
        with self.assertRaises(ValidationError):   # a metric of a source that does not exist
            make(metrics=[{"name": "m", "source": "ghost", "agg": "count"}])
        with self.assertRaises(ValidationError):   # a date dimension mapped to a text field
            make(dimensions=[{"name": "month", "kind": "date", "map": {"files": "name", "rates": "name"}}])
        with self.assertRaises(ValidationError):   # a many2one that points elsewhere
            make(dimensions=[{"name": "who", "kind": "many2one", "comodel": "res.partner", "map": {"files": "create_uid", "rates": "create_uid"}}])
        with self.assertRaises(ValidationError):   # a sum without a field
            make(metrics=[{"name": "m", "source": "files", "agg": "sum"}])
        with self.assertRaises(ValidationError):   # not JSON
            Dataset.create({"kind": "blend", "code": "bad", "label": "x", "definition_text": "{nope"})
        synced = Dataset.create({"kind": "blend", "code": "synced", "label": "x", "definition_text": json.dumps(definition())})
        self.assertEqual(synced._definition()["code"], "synced")   # the record names the dataset, whatever the JSON says
        with self.assertRaises(Exception):         # the name is unique
            Dataset.create({"kind": "blend", "code": "files_rates", "label": "again", "definition_text": json.dumps(definition())})

    def test_managers_write_blends_and_users_only_use_them(self):
        Dataset = self.env["dwo.dataset"]
        user = self.env["res.users"].create({"name": "U", "login": "bl_user", "group_ids": [(6, 0, [self.env.ref("base.group_user").id])]})
        with self.assertRaises(AccessError):
            Dataset.with_user(user).create({"kind": "blend", "code": "mine", "label": "x", "definition_text": json.dumps(definition(code="mine"))})
        Dataset.with_user(self.manager).create({"kind": "blend", "code": "by_manager", "label": "x",
                                                "definition_text": json.dumps(definition(code="by_manager"))})
        self.assertEqual(self.env["dwo.dashboard.spec"]._dwo_resolve_dataset("blend:by_manager")["code"], "by_manager")
        self.assertIsNone(self.env["dwo.dashboard.spec"]._dwo_resolve_dataset("blend:nope"))

    def test_explore_offers_a_blend_to_whoever_can_read_all_its_models(self):
        explore = self.env["dwo.dashboard.explore"]
        self.assertIn("blend:files_rates", {d["ref"] for d in explore.with_user(self.admin).list_datasets()})
        described = explore.with_user(self.admin).describe_dataset("blend:files_rates")
        self.assertEqual((described["kind"], [f["name"] for f in described["fields"]]), ("blend", ["month", "who"]))
        plain = self.env["res.users"].create({"name": "P", "login": "bl_plain3", "group_ids": [(6, 0, [self.env.ref("base.group_user").id])]})
        self.env["ir.model.access"].search([("model_id.model", "=", "res.currency.rate")]).write({"perm_read": False})
        self.env.registry.clear_cache()
        self.assertNotIn("blend:files_rates", {d["ref"] for d in explore.with_user(plain).list_datasets()})
        with self.assertRaises(AccessError):
            explore.with_user(plain).describe_dataset("blend:files_rates")
        self.assertEqual([m["name"] for m in described["metrics"]], ["bytes", "avg_bytes", "rates", "big_rates"])
