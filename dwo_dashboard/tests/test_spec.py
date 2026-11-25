# -*- coding: utf-8 -*-
import copy
import glob
import json
import os
from unittest.mock import patch

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase

from ..spec import Registry, constants as C, core_visual_types, core_dataset_types
from ..spec import validate_dataset_semantics, validate_dataset_structure, validate_semantics, validate_structure
from ..spec.schema_gen import DATASET_FILE, PAGE_FILE, build_dataset_schema, build_schema

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "spec", "samples")
CORE = Registry.core()


def load(kind, name):
    with open(os.path.join(SAMPLES, kind, name + ".json")) as handle:
        return json.load(handle)


def page(name="partners_overview"):
    return load("pages", name)


def dataset(name):
    return load("datasets", name)


def resolver(ref):
    """Fixture lookup standing in for the stored definitions of a later phase."""
    path = os.path.join(SAMPLES, "datasets", ref.replace(":", "_").replace(".", "_") + ".json")
    if os.path.exists(path):
        with open(path) as handle:
            return json.load(handle)
    return None


def widget(spec, wid):
    return next(w for w in spec["widgets"] if w["id"] == wid)


def pairs(errors):
    return {(e["path"], e["code"]) for e in errors}


def scatter():
    """A visual type a plugin could add: reuses the grouped engine, brings its own wells."""
    return {"label": "Scatter", "query": "grouped", "limit": {"default": 500, "max": 2000}, "series_limit": None,
            "wells": {"x": {"accepts": "measure", "min": 1, "max": 1}, "y": {"accepts": "measure", "min": 1, "max": 1},
                      "size": {"accepts": "measure", "min": 0, "max": 1},
                      "detail": {"accepts": "dimension", "min": 1, "max": 1}},
            "options": {"jitter": {"kind": "bool"}}, "constraints": []}


# ===================================================================================== structure of a page
class TestPageStructure(TransactionCase):

    def codes(self, spec):
        return pairs(validate_structure(spec, CORE))

    def test_samples_are_valid(self):
        files = sorted(glob.glob(os.path.join(SAMPLES, "pages", "*.json")))
        self.assertGreaterEqual(len(files), 4)
        for name in files:
            with open(name) as handle:
                self.assertEqual(validate_structure(json.load(handle), CORE), [], os.path.basename(name))

    def test_root(self):
        self.assertEqual(self.codes([]), {("", "type")})
        spec = page()
        spec["schema"] = "dwo-dashboard/2"
        spec["colour"] = "red"
        del spec["widgets"]
        found = self.codes(spec)
        self.assertLessEqual({("/schema", "schema"), ("/colour", "unknown_key"), ("/widgets", "required")}, found)

    def test_the_icon_of_a_widget(self):
        spec = page()
        widget(spec, "total")["icon"] = "fa-line-chart"
        self.assertEqual(self.codes(spec), set())
        for bad in ("fa fa-list", "list", "fa-", "FA-list", "fa-list;color:red", "<b>", 5, "", "fa-" + "a" * 60):
            widget(spec, "total")["icon"] = bad
            self.assertTrue(any(path == "/widgets/0/icon" for path, _code in self.codes(spec)), bad)

    def test_paths_are_json_pointers(self):
        spec = page()
        widget(spec, "total")["wells"]["value"]["agg"] = "sum"  # a metric item cannot also have an agg
        spec["widgets"][1]["id"] = "a/b~c"
        found = self.codes(spec)
        self.assertIn(("/widgets/0/wells/value/agg", "unknown_key"), found)
        self.assertIn(("/widgets/1/id", "pattern"), found)

    def test_unknown_keys_and_types(self):
        spec = page()
        widget(spec, "total")["sql"] = "select 1"
        widget(spec, "by_country")["options"]["glow"] = True
        widget(spec, "kind")["type"] = "funnel"  # not installed
        found = self.codes(spec)
        self.assertLessEqual({("/widgets/0/sql", "unknown_key"), ("/widgets/2/options/glow", "unknown_key"),
                              ("/widgets/4/type", "enum")}, found)

    def test_dataset_references(self):
        spec = page()
        widget(spec, "total")["dataset"] = "sale.order"  # no prefix
        widget(spec, "companies")["dataset"] = "csv:sales"  # type not installed
        widget(spec, "by_country")["dataset"] = "orm:Bad Name"
        widget(spec, "by_month")["dataset"] = "sql:Bad.Name"  # sql names are identifiers
        found = self.codes(spec)
        self.assertLessEqual({("/widgets/0/dataset", "pattern"), ("/widgets/1/dataset", "enum"),
                              ("/widgets/2/dataset", "pattern"), ("/widgets/3/dataset", "pattern")}, found)
        spec = page()
        widget(spec, "total")["dataset"] = "orm:x_studio_thing"  # a Studio model has no dot: fine
        self.assertEqual(self.codes(spec), set())

    def test_where_only_on_datasets_that_have_it(self):
        spec = page("sales_by_person_sql")
        widget(spec, "orders")["where"] = [["a", "=", 1]]
        self.assertIn(("/widgets/0/where", "not_allowed"), self.codes(spec))

    def test_wells_shape(self):
        spec = page()
        widget(spec, "by_country")["wells"]["axis"] = [{"field": "country_id"}]  # max 1 -> an object
        widget(spec, "by_month")["wells"]["values"] = {"agg": "count"}  # max 5 -> an array
        widget(spec, "kind")["wells"].pop("value")
        widget(spec, "mine")["wells"]["colour"] = {"field": "x"}
        found = self.codes(spec)
        self.assertLessEqual({("/widgets/2/wells/axis", "type"), ("/widgets/3/wells/values", "type"),
                              ("/widgets/4/wells/value", "required"), ("/widgets/6/wells/colour", "unknown_key")}, found)

    def test_measure_items(self):
        spec = page()
        widget(spec, "by_country")["wells"]["values"] = [{"agg": "sum"}]  # field missing
        widget(spec, "by_month")["wells"]["values"] = [{"agg": "median", "field": "id"}]
        widget(spec, "matrix")["wells"]["values"] = [{"agg": "count"}, {"agg": "count"}]
        found = self.codes(spec)
        self.assertLessEqual({("/widgets/2/wells/values/0/field", "required"),
                              ("/widgets/3/wells/values/0/agg", "enum")}, found)
        self.assertIn(("/widgets/5/wells", "duplicate"), found)

    def test_a_chart_with_legend_has_one_measure(self):
        spec = page("sales_example")
        widget(spec, "monthly")["wells"]["values"] = [{"metric": "revenue"}, {"agg": "count"}]
        self.assertIn(("/widgets/2/wells/values", "constraint"), self.codes(spec))

    def test_pivot_needs_rows_or_columns(self):
        spec = page()
        wells = widget(spec, "matrix")["wells"]
        wells.pop("rows")
        wells.pop("columns")
        self.assertIn(("/widgets/5/wells", "required"), self.codes(spec))

    def test_the_same_field_cannot_be_two_dimensions(self):
        spec = page()
        widget(spec, "matrix")["wells"]["columns"] = [{"field": "country_id"}]
        self.assertIn(("/widgets/5/wells", "duplicate"), self.codes(spec))

    def test_order_refers_to_the_wells(self):
        spec = page()
        widget(spec, "by_country")["order"] = [{"field": "name"}, {"measure": "nope"}, {"dir": "asc"}]
        widget(spec, "latest")["order"] = [{"measure": "__count"}]
        found = self.codes(spec)
        self.assertLessEqual({("/widgets/2/order/0/field", "reference"), ("/widgets/2/order/1/measure", "reference"),
                              ("/widgets/2/order/2", "required"), ("/widgets/7/order/0/measure", "not_allowed")}, found)
        spec = page()
        widget(spec, "by_country")["order"] = [{"field": "country_id", "measure": "__count"}]
        self.assertIn(("/widgets/2/order/0", "required"), self.codes(spec))

    def test_limits_follow_the_visual_type(self):
        spec = page()
        widget(spec, "total")["limit"] = 5  # a KPI has no limit
        widget(spec, "by_country")["limit"] = 10000
        widget(spec, "by_country")["series_limit"] = 50
        widget(spec, "kind")["series_limit"] = 3  # a doughnut has one dimension
        found = self.codes(spec)
        self.assertLessEqual({("/widgets/0/limit", "not_allowed"), ("/widgets/2/limit", "range"),
                              ("/widgets/2/series_limit", "range"), ("/widgets/4/series_limit", "not_allowed")}, found)

    def test_options_belong_to_the_visual_type(self):
        spec = page()
        widget(spec, "by_month")["options"] = {"horizontal": True}  # bar only
        widget(spec, "by_country")["options"].update({"colors": ["red"], "decimals": 9})
        found = self.codes(spec)
        self.assertLessEqual({("/widgets/3/options/horizontal", "unknown_key"),
                              ("/widgets/2/options/colors/0", "pattern"), ("/widgets/2/options/decimals", "range")}, found)

    def test_compare_is_for_a_kpi_and_has_a_shape(self):
        spec = page()
        widget(spec, "total")["compare"] = {"field": "create_date", "period": "this_month", "against": "previous_year"}
        self.assertNotIn("/widgets/0/compare", {p for p, _c in self.codes(spec)})
        widget(spec, "total")["compare"] = {"period": "all", "against": "last_decade", "colour": 1}
        found = self.codes(spec)
        self.assertLessEqual({("/widgets/0/compare/field", "required"), ("/widgets/0/compare/period", "enum"),
                              ("/widgets/0/compare/against", "enum"), ("/widgets/0/compare/colour", "unknown_key")}, found)
        widget(spec, "by_country")["compare"] = {"field": "create_date"}  # a bar cannot be compared
        self.assertIn(("/widgets/2/compare", "not_allowed"), self.codes(spec))

    def test_kpi_and_chart_options(self):
        spec = page()
        widget(spec, "total")["options"] = {"goal": 1000, "trend_good": "down", "prefix": "$", "suffix": " pcs"}
        widget(spec, "by_country")["options"] = {"show_values": True, "target": 12.5, "horizontal": True}
        self.assertFalse({p for p, _c in self.codes(spec) if "/options" in p})
        widget(spec, "total")["options"] = {"goal": "lots", "trend_good": "sideways", "prefix": "a very long prefix"}
        found = self.codes(spec)
        self.assertLessEqual({("/widgets/0/options/goal", "type"), ("/widgets/0/options/trend_good", "enum"),
                              ("/widgets/0/options/prefix", "too_long")}, found)

    def test_percent_needs_a_stack(self):
        spec = page("sales_example")
        bar = widget(spec, "monthly")  # has a legend: a 100% stack is meaningful
        bar["options"] = {"percent": True}
        self.assertNotIn(("/widgets/2/options/percent", "constraint"), self.codes(spec))
        bar["wells"].pop("legend")
        self.assertIn(("/widgets/2/options/percent", "constraint"), self.codes(spec))
        bar["options"] = {"percent": True, "stacked": True}  # stacked series of several measures
        self.assertNotIn(("/widgets/2/options/percent", "constraint"), self.codes(spec))

    def test_other_only_for_aggregates_that_add_up(self):
        spec = page()
        kind = widget(spec, "kind")
        kind["options"] = {"other": True}
        self.assertNotIn(("/widgets/4/wells/value", "constraint"), self.codes(spec))  # count
        for agg in ("avg", "min", "max", "count_distinct"):
            kind["wells"]["value"] = {"agg": agg, "field": "id"}
            self.assertIn(("/widgets/4/wells/value", "constraint"), self.codes(spec), agg)
        kind["wells"]["value"] = {"agg": "sum", "field": "id"}
        self.assertNotIn(("/widgets/4/wells/value", "constraint"), self.codes(spec))

    def test_layout(self):
        spec = page()
        widget(spec, "companies")["x"] = 1  # overlaps "total"
        widget(spec, "latest")["w"] = 13
        widget(spec, "kind")["x"] = 10  # x + w beyond the 12 columns
        found = self.codes(spec)
        self.assertLessEqual({("/widgets/1", "layout"), ("/widgets/7/w", "range"), ("/widgets/4/w", "layout")}, found)
        spec = page()
        spec["grid"] = {"cols": 4}
        self.assertIn(("/grid/cols", "range"), self.codes(spec))

    def test_ids(self):
        spec = page()
        spec["widgets"][1]["id"] = "total"
        spec["filters"][1]["id"] = "created"
        found = self.codes(spec)
        self.assertLessEqual({("/widgets/1/id", "duplicate"), ("/filters/1/id", "duplicate")}, found)

    def test_filters(self):
        spec = page()
        spec["filters"][0]["default"] = "next_decade"
        spec["filters"][1]["default"] = "1"
        spec["filters"][0]["bind"].append({"dataset": "orm:res.partner", "field": "write_date"})  # same dataset twice
        spec["filters"][1]["bind"] = [{"dataset": "orm:never.used", "field": "country_id"}]
        widget(spec, "total")["ignore_filters"] = ["nope"]
        found = self.codes(spec)
        self.assertLessEqual({
            ("/filters/0/default", "enum"), ("/filters/1/default", "not_allowed"),
            ("/filters/0/bind/1", "duplicate"), ("/filters/1/bind/0/dataset", "reference"),
            ("/widgets/0/ignore_filters/0", "reference")}, found)
        spec = page()
        spec["filters"][0]["bind"] = []
        self.assertIn(("/filters/0/bind", "length"), self.codes(spec))

    def test_filter_shapes(self):
        spec = page()
        del spec["filters"][1]["model"]  # a relation filter needs its model
        spec["filters"][0]["model"] = "res.country"  # a date filter has none
        spec["filters"][0]["values"] = ["a"]
        found = self.codes(spec)
        self.assertLessEqual({("/filters/1/model", "required"), ("/filters/0/model", "not_allowed"),
                              ("/filters/0/values", "not_allowed")}, found)
        spec = page("attachments_usage")
        spec["filters"][1]["values"] = ["binary", "binary"]
        spec["filters"][1]["default"] = "other"
        self.assertLessEqual({("/filters/1/values/1", "duplicate"), ("/filters/1/default", "reference")},
                             self.codes(spec))
        del spec["filters"][1]["values"]
        self.assertIn(("/filters/1/values", "required"), self.codes(spec))

    def test_booleans_are_not_integers(self):
        spec = page()
        widget(spec, "total")["x"] = True
        self.assertIn(("/widgets/0/x", "type"), self.codes(spec))


class TestDomain(TransactionCase):

    def check(self, domain):
        spec = page()
        widget(spec, "latest")["where"] = domain
        return pairs(validate_structure(spec, CORE))

    def test_valid_domains(self):
        for domain in [
            [], [["a", "=", 1]], [["a", "=", 1], ["b", "!=", False]],
            ["|", ["a", "=", 1], ["b", "in", [1, 2]]], ["!", ["a", "ilike", "x"]],
            ["&", "|", ["a", "=", 1], ["b", "=", 2], ["c", "=", 3]],
            [["partner_id.country_id", "=", None]], [["line_ids", "any", [["qty", ">", 0]]]],
            [["user_id", "=", {"ctx": "uid"}]], [["company_id", "in", {"ctx": "company_ids"}]],
            [["date", ">=", {"ctx": "today"}]], [["user_id", "in", [{"ctx": "uid"}, 2]]],
        ]:
            found = self.check(domain)
            self.assertFalse({p for p in found if p[0].startswith("/widgets/7/where")}, (domain, found))

    def test_invalid_domains(self):
        for domain, code in [
            (["|", ["a", "=", 1]], "domain"), ([["a", "=", 1], "&"], "domain"), ([["a", "=="]], "domain"),
            ([["a", "regex", 1]], "enum"), ([["a", "in", 1]], "type"), ([["a", "=", [1, 2]]], "type"),
            ([["a", "=", {"x": 1}]], "type"), ([["A B", "=", 1]], "pattern"),
            ([["a", "any", [["b", "=", 1]]], ["c", "any", ["x"]]], "domain"), ("a = 1", "type"),
            ([["a", "any!", [["b", "=", 1]]]], "enum"),  # skips record rules: never allowed
            ([["a", "not any!", []]], "enum"),
            ([["a", "=", "$uid"]], None),  # a plain string stays a plain string (no magic)
            ([["a", "=", {"ctx": "company_ids"}]], "type"),  # a list token needs in / not in
            ([["a", "in", {"ctx": "uid"}]], "type"), ([["a", "=", {"ctx": "nope"}]], "type"),
        ]:
            found = {c for p, c in self.check(domain) if p.startswith("/widgets/7/where")}
            if code is None:
                self.assertFalse(found, domain)
            else:
                self.assertIn(code, found, "%r -> %r" % (domain, found))

    def test_limits(self):
        deep = [["a", "=", 1]]
        for _ in range(C.MAX_DOMAIN_DEPTH + 1):
            deep = [["x", "any", deep]]
        self.assertIn("too_deep", {c for _p, c in self.check(deep)})
        self.assertIn("too_many", {c for _p, c in self.check([["a", "=", i] for i in range(C.MAX_DOMAIN_LEAVES + 1)])})


# =============================================================================================== registry
class TestRegistry(TransactionCase):

    def test_core_registry(self):
        reg = Registry.core()
        self.assertEqual(set(reg.visuals), {"kpi", "table", "bar", "line", "area", "pie", "doughnut", "pivot"})
        self.assertEqual(set(reg.datasets), {"orm", "sql"})

    def test_malformed_plugin_definitions_are_refused_with_a_reason(self):
        for mutate, text in [
            (lambda v: v.update(query="stream"), "query must be one of"),
            (lambda v: v["wells"]["x"].update(accepts="colour"), "accepts must be one of"),
            (lambda v: v["wells"]["x"].update(min=3, max=1), "min <= max"),
            (lambda v: v["wells"].clear(), "at least one well"),
            (lambda v: v["options"].update(bad={"kind": "slider"}), "kind must be one of"),
            (lambda v: v.update(limit={"default": 9, "max": 3}), "limit needs"),
            (lambda v: v.update(constraints=[{"kind": "any_of", "wells": ["nope"]}]), "unknown wells"),
            (lambda v: v.update(series_limit={"default": 1, "max": 2}), "two dimension wells"),
        ]:
            visuals = core_visual_types()
            visuals["scatter"] = scatter()
            mutate(visuals["scatter"])
            with self.assertRaisesRegex(ValueError, text):
                Registry(visuals, core_dataset_types())

    def test_a_synthetic_visual_type_is_validated_by_the_pure_validator(self):
        visuals = core_visual_types()
        visuals["scatter"] = scatter()
        reg = Registry(visuals, core_dataset_types())
        spec = page()
        spec["widgets"] = [{
            "id": "sc", "type": "scatter", "x": 0, "y": 0, "w": 6, "h": 4, "dataset": "orm:res.partner",
            "wells": {"x": {"agg": "count"}, "y": {"field": "id", "agg": "max"}, "detail": {"field": "country_id"}},
            "limit": 1000, "options": {"jitter": True}}]
        spec["filters"] = []
        self.assertEqual(validate_structure(spec, reg), [])
        self.assertIn(("/widgets/0/type", "enum"), pairs(validate_structure(spec, CORE)))  # not in the core registry
        spec["widgets"][0]["wells"]["detail"] = [{"field": "country_id"}]  # max 1 -> object
        self.assertIn(("/widgets/0/wells/detail", "type"), pairs(validate_structure(spec, reg)))
        # the schema grows with the registry, one definition per type
        self.assertIn("widget_scatter", build_schema(reg)["$defs"])
        self.assertNotIn("widget_scatter", build_schema(CORE)["$defs"])

    def test_plugins_extend_the_odoo_hooks_and_stay_per_database(self):
        Spec = self.env["dwo.dashboard.spec"]
        self.assertNotIn("scatter", Spec.get_registry()["visuals"])

        def hooked(self_):
            types = core_visual_types()
            types["scatter"] = scatter()
            return types

        with patch.object(type(Spec), "_dwo_visual_types", hooked):
            self.assertIn("scatter", Spec.get_registry()["visuals"])
            self.assertIn("widget_scatter", Spec.get_schema()["$defs"])
            spec = {"schema": "dwo-dashboard/1", "widgets": [{
                "id": "sc", "type": "scatter", "x": 0, "y": 0, "w": 6, "h": 4, "dataset": "orm:res.partner",
                "wells": {"x": {"agg": "count"}, "y": {"field": "id", "agg": "max"},
                          "detail": {"field": "country_id"}}}]}
            self.assertEqual(Spec.validate(spec), {"valid": True, "errors": []})
        # uninstalled again: a stored page with that widget fails to validate (strict on save)
        self.assertFalse(Spec.validate(spec)["valid"])
        self.assertNotIn("scatter", Spec.get_registry()["visuals"])

    def test_a_dataset_type_plugin(self):
        datasets = core_dataset_types()
        datasets["csv"] = {"label": "CSV", "name_pattern": C.ID_PATTERN, "where": False,
                           "definition": {"required": ["file"], "optional": []}}
        reg = Registry(core_visual_types(), datasets)
        spec = page()
        widget(spec, "total")["dataset"] = "csv:budget"
        self.assertNotIn(("/widgets/0/dataset", "enum"), pairs(validate_structure(spec, reg)))
        self.assertIn(("/widgets/0/dataset", "enum"), pairs(validate_structure(spec, CORE)))
        self.assertEqual(validate_dataset_structure(
            {"schema": "dwo-dataset/1", "type": "csv", "file": "x.csv"}, reg), [])


# ============================================================================================== schemas
class TestSchemas(TransactionCase):

    def test_static_files_are_the_core_snapshot(self):
        with open(PAGE_FILE) as handle:
            self.assertEqual(json.load(handle), build_schema(CORE), "run: python3 dwo_dashboard/spec/schema_gen.py")
        with open(DATASET_FILE) as handle:
            self.assertEqual(json.load(handle), build_dataset_schema(CORE))

    def test_one_definition_per_visual_type_with_its_own_wells(self):
        defs = build_schema(CORE)["$defs"]
        self.assertEqual({k[7:] for k in defs if k.startswith("widget_")}, set(CORE.visuals))
        self.assertEqual(set(defs["widget_pie"]["properties"]["wells"]["properties"]), {"category", "value"})
        self.assertEqual(set(defs["widget_bar"]["properties"]["wells"]["properties"]), {"axis", "legend", "values"})
        self.assertNotIn("limit", defs["widget_kpi"]["properties"])  # a KPI has no limit
        self.assertEqual(defs["widget_bar"]["properties"]["limit"]["maximum"], 500)

    def test_schema_vocabulary_matches_the_constants(self):
        defs = build_schema(CORE)["$defs"]
        self.assertEqual(tuple(defs["dimension"]["properties"]["interval"]["enum"]), C.INTERVALS)
        self.assertEqual(tuple(defs["measure"]["oneOf"][1]["properties"]["agg"]["enum"]), C.AGGS)
        self.assertEqual(tuple(defs["filter"]["properties"]["type"]["enum"]), C.FILTER_TYPES)
        self.assertNotIn("any!", defs["domain"]["items"]["oneOf"][1]["prefixItems"][1]["enum"])


# ===================================================================================== dataset definitions
class TestDatasetStructure(TransactionCase):

    def codes(self, defn):
        return pairs(validate_dataset_structure(defn, CORE))

    def test_fixtures_are_valid(self):
        files = sorted(glob.glob(os.path.join(SAMPLES, "datasets", "*.json")))
        self.assertGreaterEqual(len(files), 3)
        for name in files:
            with open(name) as handle:
                self.assertEqual(validate_dataset_structure(json.load(handle), CORE), [], os.path.basename(name))

    def test_type_and_schema(self):
        self.assertIn(("/type", "enum"), self.codes({"schema": "dwo-dataset/1", "type": "excel"}))
        defn = dataset("orm_res_partner")
        defn["schema"] = "dwo-dataset/9"
        defn["code"] = "x"  # not a key of an orm dataset
        self.assertLessEqual({("/schema", "schema"), ("/code", "unknown_key")}, self.codes(defn))

    def test_orm_fields_and_metrics(self):
        defn = dataset("orm_res_partner")
        defn["fields"]["name"] = {"role": "dimension", "hidden": "yes", "colour": 1}
        defn["metrics"].append({"name": "contacts", "agg": "count"})  # duplicate
        defn["metrics"].append({"name": "total", "agg": "sum"})  # field missing
        defn["metrics"].append({"name": "Bad Name", "agg": "median"})
        found = self.codes(defn)
        self.assertLessEqual({
            ("/fields/name/hidden", "type"), ("/fields/name/colour", "unknown_key"),
            ("/metrics/2/name", "duplicate"), ("/metrics/3/field", "required"),
            ("/metrics/4/name", "pattern"), ("/metrics/4/agg", "enum")}, found)

    def test_metric_where_is_a_domain_only_on_orm(self):
        defn = dataset("orm_res_partner")
        defn["metrics"][1]["where"] = [["a", "=="]]
        self.assertIn(("/metrics/1/where/0", "domain"), self.codes(defn))
        defn = dataset("sql_sales_by_person")
        defn["metrics"][0]["where"] = [["revenue", ">", 0]]
        self.assertIn(("/metrics/0/where", "not_allowed"), self.codes(defn))

    def test_sql_dataset_rules(self):
        defn = dataset("sql_sales_by_person")
        defn["sql"]["params"] = ["company_ids", "lang"]  # lang declared, not used
        defn["sql"]["query"] += " AND so.id > %(min_id)s"  # used, not declared
        defn["sql"]["groups"] = []
        defn["sql"]["columns"].append({"name": "revenue", "type": "text", "role": "dimension"})  # duplicate
        defn["sql"]["columns"].append({"name": "Bad", "type": "money", "role": "dimension"})
        found = self.codes(defn)
        self.assertLessEqual({
            ("/sql/query", "param"), ("/sql/params", "param"), ("/sql/groups", "length"),
            ("/sql/columns/4/name", "duplicate"), ("/sql/columns/5/name", "pattern"),
            ("/sql/columns/5/type", "enum")}, found)

    def test_company_scoped_needs_company_ids(self):
        defn = dataset("sql_sales_by_person")
        defn["sql"]["params"] = []
        defn["sql"]["query"] = "SELECT 1 AS order_id"
        self.assertIn(("/sql/company_scoped", "company"), self.codes(defn))

    def test_a_measure_column_must_be_a_number(self):
        defn = dataset("sql_sales_by_person")
        defn["sql"]["columns"][2]["role"] = "measure"  # salesperson is text
        self.assertIn(("/sql/columns/2/role", "role"), self.codes(defn))

    def test_sql_metric_refers_to_a_column_of_the_right_role(self):
        defn = dataset("sql_sales_by_person")
        defn["metrics"][0]["field"] = "nope"
        defn["metrics"][1].update(agg="sum", field="salesperson")  # sum of a dimension
        found = self.codes(defn)
        self.assertLessEqual({("/metrics/0/field", "reference"), ("/metrics/1/field", "role")}, found)


# =============================================================================================== semantics
class TestSemantics(TransactionCase):

    def errors(self, spec, author=None, check_access=True):
        self.assertEqual(validate_structure(spec, CORE), [], "the test spec must be structurally valid")
        env = self.env if author is None else self.env(user=author)
        return pairs(validate_semantics(env, spec, CORE, resolver, check_access))

    def test_samples_are_valid(self):
        for name in ("partners_overview", "attachments_usage", "sales_by_person_sql"):
            self.assertEqual(self.errors(page(name)), set(), name)
        if "sale.order" in self.env:
            self.assertEqual(self.errors(page("sales_example")), set())

    def test_dataset_must_exist(self):
        spec = page()
        widget(spec, "total")["dataset"] = "orm:no.such.model"
        widget(spec, "latest")["dataset"] = "orm:res.users"
        spec2 = page("sales_by_person_sql")
        widget(spec2, "orders")["dataset"] = "sql:nothing"
        self.assertIn(("/widgets/0/dataset", "model"), self.errors(spec))
        self.assertIn(("/widgets/0/dataset", "dataset"), self.errors(spec2))

    def test_unknown_fields_and_metrics(self):
        spec = page()
        widget(spec, "by_country")["wells"]["axis"] = {"field": "nope"}
        widget(spec, "total")["wells"]["value"] = {"metric": "ghost"}
        widget(spec, "latest")["wells"]["columns"] = [{"field": "name"}, {"field": "partner_id.nope"}]
        widget(spec, "latest")["order"] = [{"field": "name"}]
        widget(spec, "mine")["where"] = [["nope.code", "=", 1]]
        found = self.errors(spec)
        self.assertLessEqual({("/widgets/2/wells/axis/field", "field"), ("/widgets/0/wells/value/metric", "metric"),
                              ("/widgets/6/where/0/0", "field")}, found)

    def test_hidden_fields_are_refused(self):
        spec = page()
        widget(spec, "by_country")["wells"]["axis"] = {"field": "comment"}  # hidden by the definition
        self.assertIn(("/widgets/2/wells/axis/field", "hidden"), self.errors(spec))

    def test_group_by_a_relation_path(self):
        spec = page()
        widget(spec, "by_country")["wells"]["axis"] = {"field": "parent_id.country_id"}
        found = self.errors(spec)
        self.assertEqual(found, set())  # Odoo 19 follows many2one paths
        widget(spec, "by_country")["wells"]["axis"] = {"field": "name.code"}  # name is not a relation
        self.assertIn(("/widgets/2/wells/axis/field", "type"), self.errors(spec))
        widget(spec, "by_country")["wells"]["axis"] = {"field": "child_ids.country_id"}  # x2many step
        self.assertIn(("/widgets/2/wells/axis/field", "type"), self.errors(spec))

    def test_group_by_path_needs_odoo_19(self):
        spec = page()
        widget(spec, "by_country")["wells"]["axis"] = {"field": "parent_id.country_id"}
        with patch("odoo.addons.dwo_dashboard.spec.semantic.supports_groupby_path", return_value=False):
            self.assertIn(("/widgets/2/wells/axis/field", "capability"), self.errors(spec))

    def test_group_by_many2many_is_allowed_and_x2many_is_not(self):
        spec = page()
        widget(spec, "by_country")["wells"]["axis"] = {"field": "category_id"}
        self.assertEqual(self.errors(spec), set())
        widget(spec, "by_country")["wells"]["axis"] = {"field": "child_ids"}
        self.assertIn(("/widgets/2/wells/axis/field", "type"), self.errors(spec))

    def test_intervals(self):
        spec = page()
        widget(spec, "by_month")["wells"]["axis"] = {"field": "create_date"}  # interval missing
        widget(spec, "by_country")["wells"]["axis"] = {"field": "country_id", "interval": "month"}
        found = self.errors(spec)
        self.assertLessEqual({("/widgets/3/wells/axis/interval", "required"),
                              ("/widgets/2/wells/axis/interval", "type")}, found)

    def test_measure_types(self):
        spec = page("attachments_usage")
        widget(spec, "bytes")["wells"]["value"] = {"field": "name", "agg": "sum"}  # sum of a char
        widget(spec, "files")["wells"]["value"] = {"field": "datas", "agg": "count_distinct"}
        found = self.errors(spec)
        self.assertIn(("/widgets/1/wells/value/agg", "type"), found)
        spec = page("attachments_usage")
        widget(spec, "files")["wells"]["value"] = {"field": "name", "agg": "count_distinct"}
        self.assertEqual(self.errors(spec), set())

    def test_table_cannot_show_binary(self):
        spec = page()
        widget(spec, "latest")["wells"]["columns"] = [{"field": "name"}, {"field": "image_1920"}]
        widget(spec, "latest")["order"] = [{"field": "name"}]
        self.assertIn(("/widgets/7/wells/columns/1/field", "type"), self.errors(spec))

    def test_filters_need_a_matching_field(self):
        spec = page()
        spec["filters"][0]["bind"][0]["field"] = "name"  # a date filter on a char
        spec["filters"][1]["bind"][0]["field"] = "nope"
        found = self.errors(spec)
        self.assertLessEqual({("/filters/0/bind/0/field", "type"), ("/filters/1/bind/0/field", "field")}, found)
        spec = page("sales_by_person_sql")
        spec["filters"][0]["bind"][0]["field"] = "salesperson"  # text column, not a date
        self.assertIn(("/filters/0/bind/0/field", "type"), self.errors(spec))

    def test_filters_serve_one_picker(self):
        spec = page()
        spec["filters"][1]["model"] = "res.partner"  # the bound country_id points to res.country
        self.assertIn(("/filters/1/bind/0/field", "type"), self.errors(spec))
        spec = page()
        spec["filters"][1]["bind"][0]["field"] = "create_uid"  # many2one to res.users
        self.assertIn(("/filters/1/bind/0/field", "type"), self.errors(spec))
        spec = page("attachments_usage")
        spec["filters"][1]["values"] = ["binary", "nope"]  # the field has no value "nope"
        self.assertIn(("/filters/1/bind/0/field", "type"), self.errors(spec))
        spec = page()
        spec["filters"][1]["model"] = "no.such.model"
        self.assertIn(("/filters/1/model", "model"), self.errors(spec))

    def test_a_sql_relation_column_trusts_the_filter_model(self):
        spec = page("sales_by_person_sql")
        spec["filters"].append({"id": "order", "type": "relation", "model": "res.partner",
                                "bind": [{"dataset": "sql:sales_by_person", "field": "order_id"}]})
        self.assertEqual(self.errors(spec), set())  # an integer column: the filter's model is trusted
        spec["filters"][1]["bind"][0]["field"] = "salesperson"  # text column: cannot hold ids
        self.assertIn(("/filters/1/bind/0/field", "type"), self.errors(spec))

    def test_author_must_read_the_model_and_the_fields(self):
        internal = self.env["res.users"].create({
            "name": "Internal Ian", "login": "dash_internal_ian",
            "group_ids": [(6, 0, [self.env.ref("base.group_user").id])]})
        portal = self.env["res.users"].create({
            "name": "Portal Pat", "login": "dash_portal_pat",
            "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])]})
        spec = page()
        widget(spec, "total")["dataset"] = "orm:ir.cron"
        self.assertIn(("/widgets/0/dataset", "access"), self.errors(spec, author=portal))
        self.assertNotIn("access", {c for _p, c in self.errors(spec, author=portal, check_access=False)})
        self.assertNotIn(("/widgets/0/dataset", "access"), self.errors(spec))  # an administrator may
        # a field restricted by groups (set on the field object for this test only, restored afterwards)
        field = self.env["res.partner"]._fields["ref"]
        self.addCleanup(setattr, field, "groups", field.groups)
        field.groups = "base.group_system"
        spec = page()
        widget(spec, "by_country")["wells"]["axis"] = {"field": "ref"}
        found = self.errors(spec, author=internal)
        self.assertIn(("/widgets/2/wells/axis/field", "access"), found)
        self.assertNotIn("access", {c for _p, c in self.errors(spec, check_access=False, author=internal)})
        self.assertNotIn("access", {c for _p, c in self.errors(spec)})  # an administrator may read it
        # also through a relation path, and as a column, and in a domain
        widget(spec, "by_country")["wells"]["axis"] = {"field": "parent_id.ref"}
        self.assertIn(("/widgets/2/wells/axis/field", "access"), self.errors(spec, author=internal))
        widget(spec, "latest")["wells"]["columns"] = [{"field": "ref"}]
        widget(spec, "latest")["order"] = [{"field": "ref"}]
        widget(spec, "mine")["where"] = [["ref", "=", "x"]]
        found = self.errors(spec, author=internal)
        self.assertLessEqual({("/widgets/7/wells/columns/0/field", "access"), ("/widgets/6/where/0/0", "access")}, found)

    # ---------------------------------------------------------------------------------------- sql datasets
    def test_sql_roles_are_hard_rules(self):
        spec = page("sales_by_person_sql")
        widget(spec, "by_person")["wells"]["axis"] = {"field": "revenue"}  # a measure column as dimension
        widget(spec, "trend")["wells"]["axis"] = {"field": "order_date"}  # date without interval
        widget(spec, "orders")["wells"]["value"] = {"field": "salesperson", "agg": "sum"}  # sum of a dimension
        found = self.errors(spec)
        self.assertLessEqual({("/widgets/2/wells/axis/field", "role"), ("/widgets/3/wells/axis/interval", "required"),
                              ("/widgets/0/wells/value/agg", "role")}, found)

    def test_sql_unknown_column_and_metric(self):
        spec = page("sales_by_person_sql")
        widget(spec, "by_person")["wells"]["axis"] = {"field": "nope"}
        widget(spec, "orders")["wells"]["value"] = {"metric": "ghost"}
        found = self.errors(spec)
        self.assertLessEqual({("/widgets/2/wells/axis/field", "field"), ("/widgets/0/wells/value/metric", "metric")}, found)

    def test_a_count_of_a_sql_dimension_is_fine(self):
        spec = page("sales_by_person_sql")
        widget(spec, "orders")["wells"]["value"] = {"field": "salesperson", "agg": "count_distinct"}
        self.assertEqual(self.errors(spec), set())

    def test_dataset_definition_semantics(self):
        defn = dataset("orm_res_partner")
        defn["fields"]["nope"] = {"hidden": True}
        defn["metrics"].append({"name": "bad", "agg": "sum", "field": "name"})  # sum of a char
        defn["metrics"].append({"name": "bad2", "agg": "count", "where": [["nope", "=", 1]]})
        found = pairs(validate_dataset_semantics(self.env, defn, CORE))
        self.assertLessEqual({("/fields/nope", "field"), ("/metrics/2/agg", "type"),
                              ("/metrics/3/where/0/0", "field")}, found)
        self.assertEqual(validate_dataset_semantics(self.env, dataset("orm_res_partner"), CORE), [])
        self.assertEqual(validate_dataset_semantics(self.env, dataset("sql_sales_by_person"), CORE), [])


# ====================================================================================== the author's access
class TestAuthorAccess(TransactionCase):

    def setUp(self):
        super().setUp()
        Users = self.env["res.users"]
        self.internal = Users.create({"name": "Internal Ian", "login": "dash_ian",
                                      "group_ids": [(6, 0, [self.env.ref("base.group_user").id])]})
        self.portal = Users.create({"name": "Portal Pat", "login": "dash_pat",
                                    "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])]})

    def errors(self, spec, user=None, resolve=resolver, check_access=True):
        env = self.env if user is None else self.env(user=user)
        return validate_semantics(env, spec, CORE, resolve, check_access)

    def test_a_missing_model_and_a_forbidden_one_look_the_same_to_a_non_admin(self):
        missing, forbidden = page(), page()
        widget(missing, "total")["dataset"] = "orm:no.such.model"
        widget(forbidden, "total")["dataset"] = "orm:ir.cron"
        for user in (self.portal, self.internal):
            self.assertEqual(self.errors(missing, user), self.errors(forbidden, user))
            self.assertEqual({e["code"] for e in self.errors(missing, user)}, {"access"})
        # an administrator, who may read everything, is told which it is
        self.assertEqual({e["code"] for e in self.errors(missing)}, {"model"})

    def test_a_missing_field_and_a_forbidden_one_look_the_same_to_a_non_admin(self):
        field = self.env["res.partner"]._fields["ref"]
        self.addCleanup(setattr, field, "groups", field.groups)
        field.groups = "base.group_system"
        missing, forbidden = page(), page()
        widget(missing, "by_country")["wells"]["axis"] = {"field": "nope"}
        widget(forbidden, "by_country")["wells"]["axis"] = {"field": "ref"}
        self.assertEqual(self.errors(missing, self.internal), self.errors(forbidden, self.internal))
        self.assertEqual(self.errors(missing)[0]["code"], "field")

    def test_check_access_is_not_a_public_parameter(self):
        spec = page()
        widget(spec, "total")["dataset"] = "orm:ir.cron"
        Spec = self.env["dwo.dashboard.spec"].with_user(self.portal)
        with self.assertRaises(TypeError):
            Spec.validate(spec, check_access=False)
        result = Spec.validate(spec)
        self.assertFalse(result["valid"])
        self.assertEqual(result["errors"][0]["code"], "access")

    def test_validating_a_dataset_definition_is_for_system_administrators(self):
        for user in (self.internal, self.portal):
            with self.assertRaises(AccessError):
                self.env["dwo.dashboard.spec"].with_user(user).validate_dataset(dataset("orm_res_partner"))
        self.assertTrue(self.env["dwo.dashboard.spec"].validate_dataset(dataset("orm_res_partner"))["valid"])

    def test_a_sql_dataset_needs_one_of_its_groups(self):
        spec = page("sales_by_person_sql")
        # the fixture needs sales_team.group_sale_manager: an internal user is not in it
        found = {(e["path"], e["code"]) for e in self.errors(spec, self.internal)}
        self.assertIn(("/widgets/0/dataset", "access"), found)
        self.assertEqual(self.errors(spec), [])  # a system administrator always may
        self.assertEqual(self.errors(spec, self.internal, check_access=False), [])

        def open_to_employees(ref):
            defn = resolver(ref)
            defn["sql"]["groups"] = ["base.group_user"]
            return defn

        self.assertEqual(self.errors(spec, self.internal, resolve=open_to_employees), [])
        self.assertIn(("/widgets/0/dataset", "access"),
                      {(e["path"], e["code"]) for e in self.errors(spec, self.portal, resolve=open_to_employees)})

    def test_an_unknown_sql_dataset_is_not_told_apart_from_a_forbidden_one(self):
        spec = page("sales_by_person_sql")
        widget(spec, "orders")["dataset"] = "sql:nothing"
        self.assertEqual(self.errors(spec, self.internal)[0], {
            "path": "/widgets/0/dataset", "code": "access", "message": "this dataset is not available to you"})
        self.assertEqual(self.errors(spec)[0]["code"], "dataset")


class TestPluginDatasetChecker(TransactionCase):

    def setUp(self):
        super().setUp()
        datasets = core_dataset_types()
        datasets["csv"] = {"label": "CSV", "name_pattern": C.ID_PATTERN, "where": False,
                           "definition": {"required": ["file"], "optional": []}}
        self.registry = Registry(core_visual_types(), datasets)
        self.spec = {"schema": "dwo-dashboard/1", "widgets": [{
            "id": "w", "type": "kpi", "x": 0, "y": 0, "w": 3, "h": 2, "dataset": "csv:budget",
            "wells": {"value": {"agg": "count"}}}]}
        self.defn = {"schema": "dwo-dataset/1", "type": "csv", "file": "x.csv"}

    def run_checks(self, resolve, checkers=None):
        self.assertEqual(validate_structure(self.spec, self.registry), [])
        return validate_semantics(self.env, self.spec, self.registry, resolve, True, checkers)

    def test_a_plugin_type_without_a_checker_is_refused_not_skipped(self):
        errors = self.run_checks(lambda ref: self.defn)
        self.assertEqual({(e["path"], e["code"]) for e in errors}, {("/widgets/0/dataset", "unchecked")})

    def test_the_checker_of_the_plugin_decides(self):
        calls = []

        def checker(ref, path, widget, defn):
            calls.append((ref, path, defn["type"]))
            return [{"path": path + "/wells/value", "code": "field", "message": "no such column"}]

        errors = self.run_checks(lambda ref: self.defn, {"csv": checker})
        self.assertEqual(calls, [("csv:budget", "/widgets/0", "csv")])
        self.assertEqual({(e["path"], e["code"]) for e in errors}, {("/widgets/0/wells/value", "field")})
        self.assertEqual(self.run_checks(lambda ref: self.defn, {"csv": lambda *a: []}), [])

    def test_the_definition_must_exist(self):
        errors = self.run_checks(lambda ref: None, {"csv": lambda *a: []})
        self.assertEqual({e["code"] for e in errors}, {"dataset"})


# ============================================================================================ the model API
class TestSpecModel(TransactionCase):

    def test_validate_accepts_json_text(self):
        self.assertEqual(self.env["dwo.dashboard.spec"].validate(json.dumps(page("attachments_usage"))),
                         {"valid": True, "errors": []})

    def test_validate_reports_bad_json_without_raising(self):
        result = self.env["dwo.dashboard.spec"].validate("{not json")
        self.assertFalse(result["valid"])
        self.assertEqual(result["errors"][0]["code"], "json")
        self.assertEqual(self.env["dwo.dashboard.spec"].validate_dataset("[")["errors"][0]["code"], "json")

    def test_validate_stops_at_structure_errors(self):
        result = self.env["dwo.dashboard.spec"].validate({"schema": "dwo-dashboard/1", "widgets": [{}]})
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("required", codes)
        self.assertFalse(codes & {"model", "field", "access", "metric"})  # semantic checks did not run

    def test_validate_dataset(self):
        Spec = self.env["dwo.dashboard.spec"]
        self.assertTrue(Spec.validate_dataset(dataset("orm_res_partner"))["valid"])
        self.assertTrue(Spec.validate_dataset(json.dumps(dataset("sql_sales_by_person")))["valid"])
        bad = dataset("orm_res_partner")
        bad["model"] = "no.such.model"
        self.assertEqual(Spec.validate_dataset(bad)["errors"][0]["code"], "model")

    def test_schemas(self):
        Spec = self.env["dwo.dashboard.spec"]
        self.assertEqual(Spec.get_schema(), build_schema(CORE))
        self.assertEqual(Spec.get_dataset_schema(), build_dataset_schema(CORE))
        self.assertEqual(set(Spec.get_registry()), {"visuals", "datasets"})
