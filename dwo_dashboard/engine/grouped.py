# -*- coding: utf-8 -*-
"""The ``grouped`` engine: KPI, charts and pivot, on Odoo's own ``formatted_read_group`` (the call the graph and pivot
views make): interval labels, timezones, many2one names and ``__extra_domain`` come from Odoo, not from us.

Top-N is never computed on silently truncated data: a first query finds the top groups of the first dimension, the second
one reads the other dimensions only for those groups. Wherever a cap still applies the result says ``truncated``."""
from odoo import _
from odoo.fields import Domain

from ..spec import constants as C
from . import guard

YES_NO = {True: "Yes", False: "No"}


class Plan:
    """What a widget asks for, in the words of ``formatted_read_group``."""

    def __init__(self, model, vdef, widget):
        self.model, self.widget = model, widget
        wells = widget["wells"]
        self.dims = []      # {"well", "field", "interval", "spec"}
        self.measures = []  # {"key", "spec", "label", "agg", "field"}
        for wname, wdef in vdef["wells"].items():
            value = wells.get(wname)
            if value is None:
                continue
            for item in [value] if wdef["max"] == 1 else value:
                if wdef["accepts"] == "dimension":
                    spec = item["field"] + (":" + item["interval"] if item.get("interval") else "")
                    self.dims.append({"well": wname, "field": item["field"], "interval": item.get("interval"),
                                      "spec": spec, "label": item.get("label")})
                elif wdef["accepts"] == "measure":
                    self.measures.append(self.measure(item))
        self.series_well = "legend" if "legend" in vdef["wells"] else "columns" if "columns" in vdef["wells"] else None
        limits, series = vdef.get("limit"), vdef.get("series_limit")
        self.limit = widget.get("limit", limits["default"] if limits else None)
        self.series_limit = widget.get("series_limit", series["default"] if series else None)

    def measure(self, item):
        field = item.get("field")
        agg = item["agg"]
        spec = "__count" if agg == "count" and not field else "%s:%s" % (field, agg)
        if spec == "__count":
            label = item.get("label") or _("Count")
        else:
            string = self.model._fields[field].string
            label = item.get("label") or ("%s (%s)" % (string, agg) if agg != "sum" else string)
        return {"key": C.measure_key(item), "spec": spec, "label": label, "agg": agg, "field": field}

    def order_string(self, default):
        """The ``order`` of ``formatted_read_group`` from the widget's ``order`` (or ``default``)."""
        parts = []
        for o in self.widget.get("order", []):
            if "field" in o:
                spec = next((d["spec"] for d in self.dims if d["field"] == o["field"]), None)
            else:
                spec = next((m["spec"] for m in self.measures if m["key"] == o["measure"]), None)
            if spec:
                parts.append("%s %s" % (spec, o.get("dir", "asc")))
        return ", ".join(parts) or default


def run(env, model, vdef, widget, domain):
    plan = Plan(model, vdef, widget)
    cap = guard.max_rows(env)
    aggregates = [m["spec"] for m in plan.measures]
    flags = {"axis": False, "series": False, "rows": False}

    if not plan.dims:  # a KPI: one row
        groups = model.formatted_read_group(domain, [], aggregates)
        rows = [_row(model, plan, g, []) for g in groups]
        return _result(model, plan, rows, flags)

    first = plan.dims[0]
    first_measure = plan.measures[0]["spec"]
    default = "%s asc" % first["spec"] if first["interval"] else "%s desc" % first_measure
    order1 = plan.order_string(default)
    limit = plan.limit
    top = model.formatted_read_group(domain, [first["spec"]], aggregates, order=order1, limit=(limit or cap) + 1)
    if limit and len(top) > limit:
        flags["axis"] = True
        top = top[:limit]
    if len(plan.dims) == 1:
        return _result(model, plan, [_row(model, plan, g, [first]) for g in top], flags)

    extra = [Domain(g["__extra_domain"]) for g in top]
    if not extra:
        return _result(model, plan, [], flags)
    restricted = Domain(domain) & Domain.OR(extra)
    specs = [d["spec"] for d in plan.dims]
    groups = model.formatted_read_group(restricted, specs, aggregates, limit=cap)
    flags["rows"] = len(groups) >= cap
    rows = [_row(model, plan, g, plan.dims) for g in groups]
    axis_position = {_group_key(model, first, g[first["spec"]]): i for i, g in enumerate(top)}
    rows.sort(key=lambda r: axis_position.get(r["keys"][0], len(axis_position)))  # stable: keeps the order inside
    rows = _cap_series(plan, rows, flags)
    result = _result(model, plan, rows, flags)
    if widget.get("options", {}).get("show_totals"):
        result["totals"] = _totals(env, model, plan, restricted, aggregates)
    return result


def _cap_series(plan, rows, flags):
    """Keep the ``series_limit`` series with the largest total of the first measure."""
    if plan.series_well is None or not plan.series_limit:
        return rows
    index = next((i for i, d in enumerate(plan.dims) if d["well"] == plan.series_well), None)
    if index is None:
        return rows
    totals = {}
    for r in rows:
        totals[r["keys"][index]] = totals.get(r["keys"][index], 0) + (r["values"][0] or 0)
    keep = sorted(totals, key=lambda k: -totals[k])[:plan.series_limit]
    if len(totals) > len(keep):
        flags["series"] = True
    return [r for r in rows if r["keys"][index] in keep]


def _totals(env, model, plan, domain, aggregates):
    """Row, column and grand totals of a pivot, computed by the database (an average of averages would be wrong)."""
    by_well = lambda well: [d for d in plan.dims if d["well"] == well]  # noqa: E731
    out = {}
    for name, dims in (("rows", by_well("rows")), ("columns", by_well("columns")), ("grand", [])):
        if name != "grand" and not dims:
            continue
        groups = model.formatted_read_group(domain, [d["spec"] for d in dims], aggregates, limit=guard.max_rows(env))
        out[name] = [_row(model, plan, g, dims) for g in groups]
    return out


def _key(value):
    """The comparable key of a group value: many2one and dates arrive as (key, label)."""
    if isinstance(value, (tuple, list)) and len(value) == 2:
        return value[0]
    return value if value is not False else None


def _group_key(model, dim, value):
    """``_key``, except that ``False`` is a real value (not "empty") for a boolean dimension."""
    owner = _target(model, dim)
    field = owner._fields.get(dim["field"].split(".")[-1])
    if field is not None and field.type == "boolean":
        return bool(value)
    return _key(value)


def _label(model, dim, value):
    """``model`` owns the last field of the dimension's path."""
    field = model._fields.get(dim["field"].split(".")[-1])
    if field is not None and field.type == "boolean":
        return _(YES_NO[bool(value)])
    if isinstance(value, (tuple, list)) and len(value) == 2:
        return value[1]
    if value is False or value is None:
        return _("None")
    if field is None:
        return str(value)
    if field.type == "selection":
        return dict(field._description_selection(model.env)).get(value, str(value))
    return str(value)


def _row(model, plan, group, dims):
    values = []
    for m in plan.measures:
        v = group.get(m["spec"])
        values.append(float(v) if v is not None else (None if m["agg"] in ("avg", "min", "max") else 0))
    return {"keys": [_group_key(model, d, group[d["spec"]]) for d in dims],
            "labels": [_label(_target(model, d), d, group[d["spec"]]) for d in dims], "values": values}


def _target(model, dim):
    """The model that owns the last field of a (possibly dotted) group-by."""
    current = model
    parts = dim["field"].split(".")
    for part in parts[:-1]:
        current = current.env[current._fields[part].comodel_name]
    return current


def _result(model, plan, rows, flags):
    dims = []
    for d in plan.dims:
        owner = _target(model, d)
        name = d["field"].split(".")[-1]
        dims.append({"well": d["well"], "field": d["field"], "interval": d["interval"],
                     "label": d["label"] or owner._fields[name].string, "type": owner._fields[name].type})
    return {"kind": "grouped", "dims": dims, "rows": rows, "truncated": flags,
            "measures": [{"key": m["key"], "label": m["label"], "agg": m["agg"]} for m in plan.measures]}
