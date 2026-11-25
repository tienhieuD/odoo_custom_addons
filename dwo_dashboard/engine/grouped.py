# -*- coding: utf-8 -*-
"""The ``grouped`` engine: KPI, charts and pivot, on Odoo's own ``formatted_read_group`` (the call the graph and pivot
views make): interval labels, timezones, many2one names and ``__extra_domain`` come from Odoo, not from us.

Top-N is never computed on silently truncated data: a first query finds the top groups of the first dimension, the second
one reads the other dimensions only for those groups. Wherever a cap still applies the result says ``truncated``."""
from odoo import _
from odoo.fields import Domain

from ..spec import constants as C
from . import dates, fill, guard
from .domain import first_weekday

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
        self.row_dims = [d for d in self.dims if d["well"] == "rows"]
        self.col_dims = [d for d in self.dims if d["well"] == "columns"]
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


def run(env, model, vdef, widget, domain, compare=None, trend=None):
    """``compare``: {"previous_domain", "info"} (a KPI against the previous period, or a line/area chart with the previous
    period over it). ``trend``: {"domain", "field", "interval", "from", "to"} (the sparkline of a KPI)."""
    plan = Plan(model, vdef, widget)
    cap = guard.max_rows(env)
    aggregates = [m["spec"] for m in plan.measures]
    flags = {"axis": False, "series": False, "rows": False}

    if compare and vdef.get("compare") == "series":
        return _series_with_previous(env, model, plan, domain, aggregates, compare, flags, cap)

    if not plan.dims:  # a KPI: one row
        groups = model.formatted_read_group(domain, [], aggregates)
        rows = [_row(model, plan, g, []) for g in groups]
        result = _result(model, plan, rows, flags)
        if compare and rows:
            previous = model.formatted_read_group(compare["previous_domain"], [], aggregates)
            before = _row(model, plan, previous[0], [])["values"][0] if previous else None
            now = rows[0]["values"][0]
            change = None if before in (None, 0) or now is None else (now - before) / abs(before) * 100
            result["compare"] = dict(compare["info"], current=now, previous=before, change_pct=change)
        if trend and rows:
            result["trend"] = _trend(model, plan, aggregates, trend)
        return result

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
        rows = [_row(model, plan, g, [first]) for g in top]
        if flags["axis"] and widget.get("options", {}).get("other"):
            rows = _with_other(model, plan, domain, rows)
        return _result(model, plan, rows, flags)

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
    other = None
    if widget.get("options", {}).get("other") and plan.row_dims and (flags["axis"] or flags["series"]):
        other = _pivot_other(env, model, plan, domain, restricted, aggregates, rows, flags,
                             bool(widget.get("options", {}).get("show_totals")))
        rows = rows + other["rows"]
    result = _result(model, plan, rows, flags)
    if widget.get("options", {}).get("show_totals"):
        result["totals"] = other["totals"] if other else _totals(env, model, plan, restricted, aggregates)
    return result


def _with_other(model, plan, domain, rows):
    """A last slice "Other" = the total minus the slices shown. Only for sums and counts (the validator refuses the other
    aggregates: an average or a distinct count of the rest is not the total minus the top)."""
    spec = plan.measures[0]["spec"]
    total = model.formatted_read_group(domain, [], [spec])
    rest = float((total[0].get(spec) if total else 0) or 0) - sum(r["values"][0] or 0 for r in rows)
    if rest > 0:
        rows.append({"keys": ["__other"], "labels": [_("Other")], "values": [rest]})
    return rows


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


# ------------------------------------------------------------------------------------------------ KPI trend (sparkline)
def _trend(model, plan, aggregates, trend):
    """The measure over the last ``points`` intervals. Odoo's ``fill_temporal`` writes the empty intervals (with their
    labels, in the viewer's time zone), so a quiet month is a zero on the line, not a missing point."""
    spec = "%s:%s" % (trend["field"], trend["interval"])
    groups = model.formatted_read_group(trend["domain"], [spec], aggregates[:1])
    groups = fill.fill(model.env, model, spec, groups, aggregates[:1], dates.fromiso(trend["from"]),
                       dates.fromiso(trend["to"]), first_weekday(model.env))
    measure = plan.measures[0]
    points = []
    for g in groups:
        value = g.get(aggregates[0])
        points.append({"label": g[spec][1] if isinstance(g[spec], (tuple, list)) else str(g[spec]),
                       "value": float(value) if value is not None else (None if measure["agg"] in ("avg", "min", "max") else 0)})
    return {"interval": trend["interval"], "points": points}


# --------------------------------------------------------------------- line / area with the previous period over it
def _series_with_previous(env, model, plan, domain, aggregates, compare, flags, cap):
    """The chart of the period and, aligned point by point, the chart of the previous one. Both are filled by Odoo's
    ``fill_temporal`` (every interval of the range is there, in the viewer's time zone), so the k-th point of one is the
    k-th interval of the other: "the 3rd day of this month" against "the 3rd day of last month"."""
    axis = plan.dims[0]
    info = compare["info"]
    bounds = info["fill"]

    def series(dom, start, end):
        groups = model.formatted_read_group(dom, [axis["spec"]], aggregates, limit=cap)
        return fill.fill(model.env, model, axis["spec"], groups, aggregates, dates.fromiso(start), dates.fromiso(end),
                         first_weekday(model.env))[:cap]

    current = series(domain, bounds["from"], bounds["to"])
    previous = series(compare["previous_domain"], bounds["previous_from"], bounds["previous_to"])
    rows = [_row(model, plan, g, [axis]) for g in current]
    before = [_row(model, plan, g, [axis]) for g in previous]
    flags["rows"] = len(current) >= cap
    result = _result(model, plan, rows, flags)
    result["compare"] = dict(info, series={
        "labels": [b["labels"][0] for b in before],
        "values": [b["values"][0] for b in before] + [None] * max(0, len(rows) - len(before)),
    })
    return result


# ------------------------------------------------------------------------------------------------ pivot "Other"
def _pivot_other(env, model, plan, domain, restricted, aggregates, rows, flags, want_totals):
    """The row "Other" (the first row dimension beyond the limit) and the column "Other" (the first column dimension beyond
    ``series_limit``), with their cells, so that every row and column adds up to the real total. Only for sums and counts
    (the validator refuses the rest), so "the rest" is exactly the total minus what is shown.

    With R the shown rows and C the shown columns, per measure:
      Other row, column c      = total of column c (all rows)      - sum over R of cell(r, c)
      row r, Other column      = total of row r (all columns)      - sum over C of cell(r, c)
      Other row, Other column  = grand total - everything above.
    Returns ``{"rows": [...], "totals": {...} or None}``; the totals are over ALL the rows, the Other row included."""
    nr, nc = len(plan.row_dims), len(plan.col_dims)
    cap = guard.max_rows(env)
    zero = [0.0] * len(plan.measures)

    def add(a, b):
        return [x + y for x, y in zip(a, b)]

    def sub(a, b):
        return [x - y for x, y in zip(a, b)]

    labels = {}  # (kind, key tuple) -> the labels of that row or column, to write them on the "Other" cells

    def read(dom, dims, kind=None):
        groups = model.formatted_read_group(dom, [d["spec"] for d in dims], aggregates, limit=cap)
        out = {}
        for g in groups:
            r = _row(model, plan, g, dims)
            out[tuple(r["keys"])] = [float(v or 0) for v in r["values"]]
            if kind:
                labels[(kind, tuple(r["keys"]))] = r["labels"]
        return out

    cells = {(tuple(r["keys"][:nr]), tuple(r["keys"][nr:])): [v or 0 for v in r["values"]] for r in rows}
    for r in rows:
        labels[("row", tuple(r["keys"][:nr]))] = r["labels"][:nr]
        labels[("col", tuple(r["keys"][nr:]))] = r["labels"][nr:]
    shown_rows = list(dict.fromkeys(rk for rk, _ck in cells))
    grand = read(domain, []).get((), zero)
    col_all = read(domain, plan.col_dims, "col") if nc and (flags["axis"] or want_totals) else {}
    kept_cols = list(dict.fromkeys(ck for _rk, ck in cells)) if flags["series"] else (list(col_all) if nc else [()])
    row_shown = read(restricted, plan.row_dims) if (nc and flags["series"]) or want_totals else {}
    other_row = ("__other",) + (None,) * (nr - 1)
    other_col = (("__other",) + (None,) * (nc - 1)) if nc else ()

    def cell_sum(rs, cs):
        total = zero
        for r in rs:
            for c in cs:
                total = add(total, cells.get((r, c), zero))
        return total

    out = []

    def named(kind, key):
        if key and key[0] == "__other":
            return [_("Other")] + [""] * (len(key) - 1)
        return labels.get((kind, key)) or [""] * len(key)

    def emit(rk, ck, values):
        if any(abs(v) > 1e-9 for v in values):
            out.append({"keys": list(rk) + list(ck), "values": values, "labels": named("row", rk) + named("col", ck)})

    row_other = {}  # column -> the cell of the Other row
    col_other = {}  # row -> the cell of the Other column
    if flags["axis"]:
        for c in kept_cols:
            row_other[c] = sub(col_all.get(c, zero) if nc else grand, cell_sum(shown_rows, [c]))
            emit(other_row, c, row_other[c])
    if nc and flags["series"]:
        for r in shown_rows:
            col_other[r] = sub(row_shown.get(r, zero), cell_sum([r], kept_cols))
            emit(r, other_col, col_other[r])
        if flags["axis"]:
            used = cell_sum(shown_rows, kept_cols)
            for values in list(col_other.values()) + list(row_other.values()):
                used = add(used, values)
            emit(other_row, other_col, sub(grand, used))

    totals = None
    if want_totals:
        totals = {"grand": [{"keys": [], "labels": [], "values": grand}], "rows": []}
        shown_total = zero
        for r in shown_rows:
            totals["rows"].append({"keys": list(r), "labels": [], "values": row_shown.get(r, zero)})
            shown_total = add(shown_total, row_shown.get(r, zero))
        if flags["axis"]:
            totals["rows"].append({"keys": list(other_row), "labels": [], "values": sub(grand, shown_total)})
        if nc:
            totals["columns"], shown_cols = [], zero
            for c in kept_cols:
                totals["columns"].append({"keys": list(c), "labels": [], "values": col_all.get(c, zero)})
                shown_cols = add(shown_cols, col_all.get(c, zero))
            if flags["series"]:
                totals["columns"].append({"keys": list(other_col), "labels": [], "values": sub(grand, shown_cols)})
    return {"rows": out, "totals": totals}
