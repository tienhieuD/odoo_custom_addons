# /// script
# dependencies = ["jsonschema"]
# ///
"""Independent check of the two JSON Schemas with the reference `jsonschema` library (the Odoo tests cannot import it):
the schemas are valid, every sample page and dataset fixture validates, and a list of wrong documents is rejected.
Run: uv run dwo_dashboard/tools/check_schema.py"""
import copy
import glob
import json
import os
import sys

from jsonschema import Draft202012Validator

here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def load(*parts):
    with open(os.path.join(here, *parts)) as handle:
        return json.load(handle)


page_schema = load("static", "schema", "dwo-dashboard-1.schema.json")
dataset_schema = load("static", "schema", "dwo-dataset-1.schema.json")
for schema in (page_schema, dataset_schema):
    Draft202012Validator.check_schema(schema)
page_v, dataset_v = Draft202012Validator(page_schema), Draft202012Validator(dataset_schema)
failed = 0

for kind, validator in (("pages", page_v), ("datasets", dataset_v)):
    for path in sorted(glob.glob(os.path.join(here, "spec", "samples", kind, "*.json"))):
        errors = list(validator.iter_errors(load(path)))
        failed += bool(errors)
        print(kind, os.path.basename(path), "OK" if not errors else [e.message[:100] for e in errors[:3]])

base = load("spec", "samples", "pages", "partners_overview.json")
sql = load("spec", "samples", "datasets", "sql_sales_by_person.json")


def widget(spec, wid):
    return next(w for w in spec["widgets"] if w["id"] == wid)


def must_reject(label, validator, document, change):
    global failed
    doc = copy.deepcopy(document)
    change(doc)
    rejected = bool(list(validator.iter_errors(doc)))
    failed += not rejected
    print("REJECTED" if rejected else "ACCEPTED (bug)", label)


blend = load("spec", "samples", "datasets", "blend_sales_vs_purchases.json")
must_reject("a blend with one source", dataset_v, blend, lambda d: d.update(sources=d["sources"][:1]))
must_reject("a blend source that is not an Odoo model", dataset_v, blend, lambda d: d["sources"][0].update(dataset="sql:x"))
must_reject("a blend dimension of an unknown kind", dataset_v, blend, lambda d: d["dimensions"][0].update(kind="money"))
must_reject("a blend with no metrics", dataset_v, blend, lambda d: d.update(metrics=[]))
must_reject("a blend with an unknown key", dataset_v, blend, lambda d: d.update(sql={"query": "select 1"}))
must_reject("icon with a space and a second class", page_v, base, lambda s: widget(s, "total").update(icon="fa fa-list"))
must_reject("icon that is not Font Awesome", page_v, base, lambda s: widget(s, "total").update(icon="<script>"))
must_reject("unknown top-level key", page_v, base, lambda s: s.update(colour="red"))
must_reject("sql text in a widget", page_v, base, lambda s: widget(s, "total").update(sql="select 1"))
must_reject("old-style query", page_v, base, lambda s: widget(s, "total").update(query={"model": "res.partner"}))
must_reject("pie with two dimensions", page_v, base,
            lambda s: widget(s, "kind")["wells"].update(category=[{"field": "a"}, {"field": "b"}]))
must_reject("well that does not exist for the type", page_v, base,
            lambda s: widget(s, "by_country")["wells"].update(colour={"field": "x"}))
must_reject("kpi with a limit", page_v, base, lambda s: widget(s, "total").update(limit=5))
must_reject("bar option on a line", page_v, base, lambda s: widget(s, "by_month")["options"].update(horizontal=True))
must_reject("bad dataset reference", page_v, base, lambda s: widget(s, "total").update(dataset="sale.order"))
must_reject("any! operator", page_v, base, lambda s: widget(s, "latest").update(where=[["a", "any!", []]]))
must_reject("bad colour", page_v, base, lambda s: widget(s, "by_country")["options"].update(colors=["red"]))
must_reject("filter without bind", page_v, base, lambda s: s["filters"][0].pop("bind"))
must_reject("measure without agg or metric", page_v, base, lambda s: widget(s, "by_country")["wells"].update(values=[{"field": "id"}]))
must_reject("relation filter without model", page_v, base, lambda s: s["filters"][1].pop("model"))
must_reject("date filter with a model", page_v, base, lambda s: s["filters"][0].update(model="res.country"))
must_reject("selection filter without values", page_v,
            load("spec", "samples", "pages", "attachments_usage.json"), lambda s: s["filters"][1].pop("values"))
must_reject("compare on a bar", page_v, base, lambda s: widget(s, "by_country").update(compare={"field": "create_date"}))
must_reject("compare with period all", page_v, base,
            lambda s: widget(s, "total").update(compare={"field": "create_date", "period": "all"}))
must_reject("goal as text", page_v, base, lambda s: widget(s, "total").update(options={"goal": "lots"}))
must_reject("prefix too long", page_v, base, lambda s: widget(s, "total").update(options={"prefix": "x" * 20}))
must_reject("heatmap on a bar", page_v, base, lambda s: widget(s, "by_country")["options"].update(heatmap=True))
must_reject("trend on a bar", page_v, base, lambda s: widget(s, "by_country").update(trend={"field": "create_date"}))
must_reject("trend with 1 point", page_v, base, lambda s: widget(s, "total").update(trend={"field": "create_date", "points": 1}))
must_reject("trend with a year interval", page_v, base,
            lambda s: widget(s, "total").update(trend={"field": "create_date", "interval": "year"}))
must_reject("y_min on a pie", page_v, base, lambda s: widget(s, "kind")["options"].update(y_min=0))
must_reject("other on a table", page_v, base, lambda s: widget(s, "latest").update(options={"other": True}))
must_reject("sql dataset without groups", dataset_v, sql, lambda d: d["sql"].pop("groups"))
must_reject("sql column with unknown type", dataset_v, sql, lambda d: d["sql"]["columns"][0].update(type="money"))
must_reject("orm dataset with a sql block", dataset_v, load("spec", "samples", "datasets", "orm_res_partner.json"),
            lambda d: d.update(sql=sql["sql"]))
sys.exit(1 if failed else 0)
