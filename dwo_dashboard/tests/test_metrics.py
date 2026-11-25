# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase

from .test_engine import EngineCase

PREFIX = "Mx "
PDF, TXT = "application/pdf", "text/plain"
# (res_model, mimetype, size): three groups; B has no PDF, C has no text
FILES = [("res.partner", PDF, 100), ("res.partner", TXT, 300), ("res.partner", PDF, 50),
         ("res.users", TXT, 200), ("res.users", TXT, 10), ("res.company", PDF, 70)]


class MetricCase(EngineCase):

    def setUp(self):
        super().setUp()
        for i, (model, mime, size) in enumerate(FILES):
            self.env["ir.attachment"].create({"name": "%s%d" % (PREFIX, i), "res_model": model, "mimetype": mime,
                                              "raw": b"x" * size})
        self.admin = self.env.ref("base.user_admin")
        self.dataset = self.env["dwo.dataset"].create({
            "model_id": self.env.ref("base.model_ir_attachment").id, "label": "Files",
            "metric_ids": [
                (0, 0, {"name": "total", "label": "All bytes", "agg": "sum", "field_id": self.field("ir.attachment", "file_size")}),
                (0, 0, {"name": "pdf", "label": "PDF bytes", "agg": "sum", "field_id": self.field("ir.attachment", "file_size"),
                        "where": "[('mimetype', '=', '%s')]" % PDF}),
                (0, 0, {"name": "txt", "label": "Text bytes", "agg": "sum", "field_id": self.field("ir.attachment", "file_size"),
                        "where": "[('mimetype', '=', '%s')]" % TXT}),
                (0, 0, {"name": "pdf_n", "label": "PDF files", "agg": "count", "where": "[('mimetype', '=', '%s')]" % PDF}),
                (0, 0, {"name": "pdf_avg", "label": "Average PDF", "agg": "avg", "field_id": self.field("ir.attachment", "file_size"),
                        "where": "[('mimetype', '=', '%s')]" % PDF}),
            ]})
        self.where = [["name", "like", PREFIX]]

    def field(self, model, name):
        return self.env["ir.model.fields"]._get(model, name).id

    def widget(self, wid, kind, wells, **extra):
        return dict({"id": wid, "type": kind, "dataset": "orm:ir.attachment", "where": self.where, "wells": wells}, **extra)

    def run_w(self, widget, user=None):
        response = self.run_as(user or self.admin, widget)
        self.assertTrue(response["ok"], response)
        return response["result"]

    def by_model(self, mime=None, agg="sum"):
        out = {}
        for model, m, size in FILES:
            if mime is None or m == mime:
                out[model] = out.get(model, 0) + (size if agg == "sum" else 1)
        return out

    def table(self, result):
        return {r["keys"][0]: r["values"] for r in result["rows"]}


class TestMetricsEngine(MetricCase):

    def test_a_kpi_of_a_metric_with_a_where(self):
        for name, expected in (("total", 730), ("pdf", 220), ("txt", 510), ("pdf_n", 3), ("pdf_avg", 220 / 3)):
            result = self.run_w(self.widget("k", "kpi", {"value": {"metric": name}}))
            self.assertAlmostEqual(result["rows"][0]["values"][0], expected, msg=name)

    def test_two_metrics_of_the_same_field_and_aggregate_do_not_collide(self):
        result = self.run_w(self.widget("t", "bar", {"axis": {"field": "res_model"},
                                                     "values": [{"metric": "total"}, {"metric": "pdf"}, {"metric": "txt"}]}))
        self.assertEqual([m["key"] for m in result["measures"]], ["total", "pdf", "txt"])
        self.assertEqual(self.table(result), {"res.partner": [450, 150, 300], "res.users": [210, 0, 210],
                                              "res.company": [70, 70, 0]})  # B keeps its place, with 0 PDF bytes

    def test_a_group_without_matching_records_shows_nothing_for_an_average_and_zero_for_a_count(self):
        result = self.run_w(self.widget("t", "bar", {"axis": {"field": "res_model"},
                                                     "values": [{"metric": "pdf_avg"}, {"metric": "pdf_n"}]}))
        self.assertEqual(self.table(result), {"res.partner": [75, 2], "res.users": [None, 0], "res.company": [70, 1]})

    def test_order_and_limit_by_a_metric_with_a_where_are_those_of_the_whole_widget(self):
        def top(direction, limit):
            result = self.run_w(self.widget("t", "bar", {"axis": {"field": "res_model"}, "values": [{"metric": "pdf"}]},
                                            order=[{"measure": "pdf", "dir": direction}], limit=limit))
            return [(r["keys"][0], r["values"][0]) for r in result["rows"]], result["truncated"]["axis"]
        self.assertEqual(top("desc", 2), ([("res.partner", 150), ("res.company", 70)], True))
        # ascending: the group with no PDF at all is the first, not missing (the database could not have said so)
        self.assertEqual(top("asc", 2), ([("res.users", 0), ("res.company", 70)], True))
        self.assertEqual(top("desc", 5)[1], False)

    def test_a_time_axis_is_ordered_by_its_dates_not_by_the_names_of_the_months(self):
        stamps = {"res.partner": "2025-11-10 08:00:00", "res.users": "2025-12-10 08:00:00", "res.company": "2026-01-10 08:00:00"}
        for att in self.env["ir.attachment"].search([("name", "like", PREFIX)]):
            self.env.cr.execute("UPDATE ir_attachment SET create_date = %s WHERE id = %s", [stamps[att.res_model], att.id])
        self.env.invalidate_all()
        def labels(direction):
            result = self.run_w(self.widget("t", "bar", {"axis": {"field": "create_date", "interval": "month"},
                                                         "values": [{"metric": "pdf"}]},
                                            order=[{"field": "create_date", "dir": direction}]))
            return [r["labels"][0] for r in result["rows"]]
        self.assertEqual(labels("asc"), ["November 2025", "December 2025", "January 2026"])  # alphabetically: D, J, N
        self.assertEqual(labels("desc"), ["January 2026", "December 2025", "November 2025"])

    def test_a_legend_and_a_pivot_with_totals(self):
        wells = {"axis": {"field": "res_model"}, "legend": {"field": "mimetype"}, "values": [{"metric": "pdf"}]}
        result = self.run_w(self.widget("t", "bar", wells))
        cells = {tuple(r["keys"]): r["values"][0] for r in result["rows"]}
        self.assertEqual(cells[("res.partner", PDF)], 150)
        self.assertEqual(cells[("res.partner", TXT)], 0)  # PDF bytes of the text files: none
        pivot = self.run_w(self.widget("p", "pivot", {"rows": [{"field": "res_model"}], "columns": [{"field": "mimetype"}],
                                                     "values": [{"metric": "pdf"}, {"metric": "total"}]},
                                       options={"show_totals": True}))
        self.assertEqual(pivot["totals"]["grand"][0]["values"], [220, 730])
        self.assertEqual({tuple(r["keys"]): r["values"] for r in pivot["totals"]["rows"]},
                         {("res.partner",): [150, 450], ("res.users",): [0, 210], ("res.company",): [70, 70]})

    def test_other_on_a_pie_with_a_sum_metric_adds_up_to_the_total(self):
        result = self.run_w(self.widget("p", "pie", {"category": {"field": "res_model"}, "value": {"metric": "pdf"}},
                                        order=[{"measure": "pdf", "dir": "desc"}], limit=1, options={"other": True}))
        self.assertEqual([(r["keys"][0], r["values"][0]) for r in result["rows"]], [("res.partner", 150), ("__other", 70)])
        self.assertEqual(sum(r["values"][0] for r in result["rows"]), 220)

    def test_other_on_a_pivot_with_a_sum_metric_adds_up_to_the_total(self):
        pivot = self.run_w(self.widget("p", "pivot", {"rows": [{"field": "res_model"}], "columns": [{"field": "mimetype"}],
                                                     "values": [{"metric": "pdf"}]},
                                       order=[{"measure": "pdf", "dir": "desc"}], limit=1, options={"other": True, "show_totals": True}))
        rows = {tuple(r["keys"]): r["values"][0] for r in pivot["rows"]}
        shown = sum(v for k, v in rows.items() if k[0] != "__other")
        other = sum(v for k, v in rows.items() if k[0] == "__other")
        self.assertEqual(shown + other, 220)
        self.assertEqual(pivot["totals"]["grand"][0]["values"], [220])

    def test_other_with_an_average_metric_is_refused_when_the_page_is_saved(self):
        widget = dict(self.widget("p", "pie", {"category": {"field": "res_model"}, "value": {"metric": "pdf_avg"}},
                                  options={"other": True}), x=0, y=0, w=4, h=3)
        page = {"schema": "dwo-dashboard/1", "grid": {"cols": 12}, "widgets": [widget]}
        result = self.env["dwo.dashboard.spec"].with_user(self.admin).validate(page)
        self.assertIn("/widgets/0/options/other", {e["path"] for e in result["errors"]})

    def last_month(self, *indexes):
        """Move some of the files to the first day of last month (12 hours in, so any time zone sees the same day)."""
        for i in indexes:
            self.env.cr.execute("UPDATE ir_attachment SET create_date = date_trunc('month', now() AT TIME ZONE 'utc')"
                                " - interval '1 month' + interval '12 hours' WHERE name = %s", ["%s%d" % (PREFIX, i)])
        self.env.invalidate_all()

    def test_a_kpi_with_compare_and_trend_on_a_metric(self):
        self.last_month(0, 3)  # a PDF of 100 bytes and a text of 200: the previous period holds the PDF only
        widget = self.widget("k", "kpi", {"value": {"metric": "pdf"}}, compare={"field": "create_date", "period": "this_month"},
                             trend={"field": "create_date", "interval": "month", "points": 3})
        result = self.run_w(widget)
        self.assertEqual(result["rows"][0]["values"][0], 120)
        self.assertEqual((result["compare"]["current"], result["compare"]["previous"]), (120, 100))
        self.assertEqual([p["value"] for p in result["trend"]["points"]], [0, 100, 120])

    def test_a_line_with_the_previous_period_over_it(self):
        self.last_month(0, 3)
        widget = self.widget("l", "line", {"axis": {"field": "create_date", "interval": "day"}, "values": [{"metric": "pdf"}]},
                             compare={"field": "create_date", "period": "this_month"}, order=[{"field": "create_date", "dir": "asc"}])
        result = self.run_w(widget)
        self.assertEqual(sum(r["values"][0] for r in result["rows"]), 120)
        self.assertEqual(sum(v or 0 for v in result["compare"]["series"]["values"]), 100)  # the text file is not a PDF

    def test_a_metric_that_does_not_exist_is_a_validation_error_not_a_failure(self):
        for name in ("nope",):
            response = self.run_as(self.admin, self.widget("k", "kpi", {"value": {"metric": name}}))
            self.assertEqual((response["ok"], response["error"]["code"]), (False, "invalid"))
            self.assertIn("no metric", response["error"]["message"])
        self.dataset.metric_ids.filtered(lambda m: m.name == "pdf").unlink()  # a metric deleted after a page used it
        response = self.run_as(self.admin, self.widget("k", "kpi", {"value": {"metric": "pdf"}}))
        self.assertEqual((response["ok"], response["error"]["code"]), (False, "invalid"))

    def test_a_widget_without_a_conditional_metric_still_takes_the_direct_path(self):
        result = self.run_w(self.widget("t", "bar", {"axis": {"field": "res_model"}, "values": [{"metric": "total"}]},
                                        order=[{"measure": "total", "dir": "desc"}]))
        self.assertEqual([(r["keys"][0], r["values"][0]) for r in result["rows"]],
                         [("res.partner", 450), ("res.users", 210), ("res.company", 70)])


class TestMetricDrill(MetricCase):
    """The records behind a bar are the ones its measures count."""

    def setUp(self):
        super().setUp()
        spec = {"schema": "dwo-dashboard/1", "grid": {"cols": 12}, "widgets": [
            dict(self.widget("pdfbar", "bar", {"axis": {"field": "res_model"}, "values": [{"metric": "pdf"}]}), x=0, y=0, w=4, h=3),
            dict(self.widget("same", "bar", {"axis": {"field": "res_model"}, "values": [{"metric": "pdf"}, {"metric": "pdf_n"}]}),
                 x=4, y=0, w=4, h=3),
            dict(self.widget("mixed", "bar", {"axis": {"field": "res_model"}, "values": [{"metric": "pdf"}, {"metric": "txt"}]}),
                 x=8, y=0, w=4, h=3),
            dict(self.widget("plain", "bar", {"axis": {"field": "res_model"}, "values": [{"metric": "total"}]}), x=0, y=3, w=4, h=3),
        ]}
        dashboard = self.env["dwo.dashboard"].with_user(self.admin).get_my_dashboard()
        self.page = self.env["dwo.dashboard.page"].browse(dashboard["pages"][0]["id"]).with_user(self.admin)
        self.page.write({"spec": spec})

    def drill(self, wid, key="res.partner"):
        answer = self.env["dwo.dashboard.engine"].with_user(self.admin).drill_records(self.page.id, wid, key)
        self.assertTrue(answer["ok"], answer)
        result = answer["result"]
        names = self.env["ir.attachment"].browse(result["ids"]).mapped("name")
        return sorted(n[len(PREFIX):] for n in names), result["mixed"]

    def test_a_metric_with_a_where_lists_only_the_records_it_counts(self):
        self.assertEqual(self.drill("pdfbar"), (["0", "2"], False))   # the two PDF files of res.partner, not the text one
        self.assertEqual(self.drill("same"), (["0", "2"], False))     # several metrics, the same condition

    def test_measures_that_count_different_records_list_the_whole_group_and_say_so(self):
        self.assertEqual(self.drill("mixed"), (["0", "1", "2"], True))

    def test_a_metric_without_a_where_lists_the_whole_group(self):
        self.assertEqual(self.drill("plain"), (["0", "1", "2"], False))


class TestMetricStorageAndAccess(TransactionCase):

    def setUp(self):
        super().setUp()
        internal = self.env.ref("base.group_user")
        self.user = self.env["res.users"].create({"name": "Mia", "login": "mx_mia", "group_ids": [(6, 0, [internal.id, self.env.ref("base.group_partner_manager").id])]})
        self.admin = self.env.ref("base.user_admin")
        self.partner_model = self.env.ref("base.model_res_partner")
        # a stored number that only administrators may read: the "color" index of a contact
        self.patch(self.env["res.partner"]._fields["color"], "groups", "base.group_system")
        self.secret = self.env["ir.model.fields"]._get("res.partner", "color")
        self.dataset = self.env["dwo.dataset"].create({
            "model_id": self.partner_model.id, "label": "Contacts",
            "metric_ids": [(0, 0, {"name": "secret", "agg": "sum", "field_id": self.secret.id}),
                           (0, 0, {"name": "people", "agg": "count", "where": "[('is_company', '=', False)]"})]})

    def page(self, metric):
        widget = {"id": "k", "type": "kpi", "dataset": "orm:res.partner", "x": 0, "y": 0, "w": 3, "h": 3,
                  "wells": {"value": {"metric": metric}}}
        return {"schema": "dwo-dashboard/1", "grid": {"cols": 12}, "widgets": [widget]}

    def test_only_administrators_write_definitions_and_everybody_reads_them(self):
        Dataset = self.env["dwo.dataset"].with_user(self.user)
        self.assertEqual(Dataset.search_count([]), 1)
        with self.assertRaises(AccessError):
            Dataset.create({"model_id": self.env.ref("base.model_res_users").id, "label": "x"})
        with self.assertRaises(AccessError):
            self.dataset.with_user(self.user).write({"label": "mine"})
        with self.assertRaises(AccessError):
            self.dataset.metric_ids[0].with_user(self.user).unlink()

    def test_a_metric_on_a_field_the_viewer_cannot_read_cannot_be_used_or_run_by_them(self):
        result = self.env["dwo.dashboard.spec"].with_user(self.user).validate(self.page("secret"))
        self.assertFalse(result["valid"])
        self.assertEqual({e["path"] for e in result["errors"]}, {"/widgets/0/wells/value/metric"})
        self.assertIn("secret", result["errors"][0]["message"])
        self.assertTrue(self.env["dwo.dashboard.spec"].with_user(self.admin).validate(self.page("secret"))["valid"])
        widget = self.page("secret")["widgets"][0]
        denied = self.env["dwo.dashboard.engine"].with_user(self.user).run_preview(widget)
        self.assertEqual((denied["ok"], denied["error"]["code"]), (False, "access"))

    def test_the_dataset_description_lists_only_the_metrics_the_caller_can_use(self):
        names = lambda user: [m["name"] for m in self.env["dwo.dashboard.explore"].with_user(user).describe_dataset("orm:res.partner")["metrics"]]
        self.assertEqual(names(self.user), ["people"])
        self.assertEqual(sorted(names(self.admin)), ["people", "secret"])

    def test_an_empty_domain_is_no_condition(self):
        metric = self.env["dwo.dataset.metric"].create({"dataset_id": self.dataset.id, "name": "all_people", "agg": "count", "where": "[]"})
        self.assertEqual(metric._where_list(), [])
        widget = {"id": "k", "type": "kpi", "dataset": "orm:res.partner", "wells": {"value": {"metric": "all_people"}}}
        response = self.env["dwo.dashboard.engine"].with_user(self.admin).run_preview(widget)
        self.assertTrue(response["ok"], response)
        self.assertEqual(response["result"]["rows"][0]["values"][0], self.env["res.partner"].search_count([]))

    def test_a_definition_must_be_valid(self):
        Metric = self.env["dwo.dataset.metric"]
        with self.assertRaises(ValidationError):  # a sum needs a field
            Metric.create({"dataset_id": self.dataset.id, "name": "bad", "agg": "sum"})
        with self.assertRaises(ValidationError):  # a name is an identifier
            Metric.create({"dataset_id": self.dataset.id, "name": "Bad Name", "agg": "count"})
        with self.assertRaises(ValidationError):  # a domain is plain data, not code
            Metric.create({"dataset_id": self.dataset.id, "name": "code", "agg": "count", "where": "[('id', '=', user.id)]"})
        with self.assertRaises(ValidationError):  # a condition on a field that does not exist
            Metric.create({"dataset_id": self.dataset.id, "name": "ghost", "agg": "count", "where": "[('nope', '=', 1)]"})
        with self.assertRaises(ValidationError):  # a number cannot be averaged out of a text field
            Metric.create({"dataset_id": self.dataset.id, "name": "avgname", "agg": "avg",
                           "field_id": self.env["ir.model.fields"]._get("res.partner", "name").id})
        with self.assertRaises(Exception):  # one dataset per model
            self.env["dwo.dataset"].create({"model_id": self.partner_model.id, "label": "again"})
