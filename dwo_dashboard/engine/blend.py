# -*- coding: utf-8 -*-
"""The ``blend`` engine: several Odoo models read one by one and merged by shared dimensions.

Each source runs as the viewer through the very engine a widget on that model would use (``grouped.Plan`` and
``measures.read``), grouped by what the shared dimension is in that source, and the results are merged by the *normalised*
key of the group: a many2one id, a selection value, a calendar day (the first day of the bucket, in the viewer's time zone,
whether the field is a date or a datetime), never the raw key of ``formatted_read_group`` (a date and a datetime do not
write it the same way). The merge is a full outer join of the grouped results:
* a group that only some sources have is a row, with 0 for a sum or a count and nothing for an average, a minimum or a
  maximum where a source has no record;
* the label is computed from the normalised key, not taken from whichever source answered first;
* order and limit are applied after the merge, in Python;
* if the viewer cannot read ONE of the sources the whole widget is refused (a half-blend would look like real numbers);
* all the sources share one time budget (``dwo_dashboard.query_timeout``), and each is cut at ``max_rows``."""
import time

from odoo import _
from odoo.fields import Domain
from odoo.exceptions import AccessError

from . import fill, guard, grouped
from .domain import field_at, filter_domain, resolve_ctx
from .interact import _local_day
from .measures import ZERO_WHEN_EMPTY, read as mread

DIMENSION_WELLS = ("axis", "category", "rows")


def _split(vdef, widget):
    """(dimension well, its item or None, measure well, [metric items])."""
    dim_well = next((w for w, d in vdef["wells"].items() if d["accepts"] == "dimension" and w in DIMENSION_WELLS), None)
    measure_well = next(w for w, d in vdef["wells"].items() if d["accepts"] == "measure")
    value = widget["wells"].get(dim_well) if dim_well else None
    item = value[0] if isinstance(value, list) and value else value
    items = widget["wells"].get(measure_well)
    return dim_well, item, measure_well, items if isinstance(items, list) else [items]


def _normalise(env, model, field_path, dim, interval, value):
    """``(key, label)`` of a group, the same whatever source it came from."""
    kind = dim["kind"]
    if kind == "boolean":
        return bool(value), _("Yes") if value else _("No")
    if value is False or value is None:
        return None, _("None")
    if kind == "date":
        field = field_at(model, field_path)
        key = value[0] if isinstance(value, (list, tuple)) else value
        day = _local_day(env, field, key)
        return day.isoformat(), fill.key_and_label(env, "date", interval, day)[1]
    if kind == "many2one":
        return (value[0], value[1]) if isinstance(value, (list, tuple)) else (value, str(value))
    if kind == "selection":
        field = field_at(model, field_path)
        return value, dict(field._description_selection(model.env)).get(value, str(value))
    return value, str(value)


def _source_domain(env, model, src, spec, widget, filter_values, dims, sname):
    domain = Domain(resolve_ctx(env, model, src.get("where", [])))
    ignored = set(widget.get("ignore_filters", []))
    values = filter_values if isinstance(filter_values, dict) else {}
    for flt in spec.get("filters", []):
        if flt["id"] in ignored:
            continue
        for bind in flt["bind"]:
            if bind["dataset"] == widget["dataset"]:  # every source maps every dimension (checked when the dataset is saved)
                domain &= Domain(filter_domain(env, model, flt, values.get(flt["id"]), dims[bind["field"]]["map"][sname]))
    return domain


def run(env, spec, widget, defn, vdef, filter_values):
    cap = guard.max_rows(env)
    started, budget = time.monotonic(), guard.timeout_seconds(env)
    sources = {s["name"]: s for s in defn["sources"]}
    dims = {d["name"]: d for d in defn["dimensions"]}
    metrics = {m["name"]: m for m in defn["metrics"]}
    dim_well, dim_item, measure_well, items = _split(vdef, widget)
    dim = dims[dim_item["field"]] if dim_item else None
    interval = dim_item.get("interval") if dim_item else None
    n = len(items)
    # every model of the blend must be readable by the viewer, before a single query runs
    for src in sources.values():
        if not env[src["dataset"][4:]].has_access("read"):
            raise AccessError(_("You cannot read all the data of this blend."))
    by_source = {}
    for index, item in enumerate(items):
        by_source.setdefault(metrics[item["metric"]]["source"], []).append((index, item))
    rows, order, truncated = {}, [], False
    for sname, entries in by_source.items():
        left = budget - (time.monotonic() - started)
        if left <= 0:
            raise TimeoutError("the blend used its time")
        model, src = env[sources[sname]["dataset"][4:]], sources[sname]
        inline = []
        for _index, item in entries:
            m = metrics[item["metric"]]
            inline.append({"metric": m["name"], "agg": m["agg"], "label": item.get("label") or m.get("label"),
                           **{k: m[k] for k in ("field", "where", "format") if k in m}})
        wells = {measure_well: inline if vdef["wells"][measure_well]["max"] != 1 else inline[0]}
        field_path = dim["map"][sname] if dim else None
        if dim:
            wells[dim_well] = {"field": field_path, **({"interval": interval} if interval else {})}
        plan = grouped.Plan(model, vdef, {"wells": wells})
        domain = _source_domain(env, model, src, spec, widget, filter_values, dims, sname)
        with guard.guarded(env, max(1, int(left))):
            groups = mread(env, model, plan, domain, [plan.dims[0]["spec"]] if dim else [], limit=cap, cap=cap)
        truncated = truncated or len(groups) >= cap
        for g in groups:
            key, label = _normalise(env, model, field_path, dim, interval, g[plan.dims[0]["spec"]]) if dim else ((), "")
            row = rows.get(key)
            if row is None:
                row = rows[key] = {"label": label, "values": [None] * n}
                order.append(key)
            for (index, _item), m in zip(entries, plan.measures):
                row["values"][index] = g.get(m["spec"])
    for row in rows.values():
        for index, item in enumerate(items):
            if row["values"][index] is None:
                row["values"][index] = 0 if metrics[item["metric"]]["agg"] in ZERO_WHEN_EMPTY else None
            else:
                row["values"][index] = float(row["values"][index])
    keys = _sorted(order, rows, widget, dim, items)
    limit = widget.get("limit", vdef["limit"]["default"] if vdef.get("limit") else None)
    cut = bool(limit) and len(keys) > limit
    if cut:
        keys = keys[:limit]
    out = [{"keys": [] if not dim else [k], "labels": [] if not dim else [rows[k]["label"]], "values": rows[k]["values"]}
           for k in keys]
    dims_out = [] if not dim else [{"well": dim_well, "field": dim["name"], "interval": interval,
                                    "label": dim.get("label") or dim["name"], "type": "date" if dim["kind"] == "date" else dim["kind"]}]
    return {"kind": "grouped", "dims": dims_out, "rows": out, "truncated": {"axis": cut, "series": False, "rows": truncated},
            "measures": [{"key": it["metric"], "label": it.get("label") or metrics[it["metric"]].get("label") or it["metric"],
                          "agg": metrics[it["metric"]]["agg"], "format": metrics[it["metric"]].get("format")} for it in items]}


def _sorted(keys, rows, widget, dim, items):
    """The order of the widget (or: a date axis by date, the rest by the first measure, largest first); empty values last."""
    asked = (widget.get("order") or [{}])[0]
    by_measure = "measure" in asked
    if by_measure:
        names = [it["metric"] for it in items]
        index = names.index(asked["measure"]) if asked["measure"] in names else 0
        reverse = asked.get("dir", "asc") == "desc"
    elif "field" in asked or (dim and dim["kind"] == "date"):
        reverse = asked.get("dir", "asc") == "desc"
        index = None
    else:
        index, reverse = 0, True
    if index is None:
        return _by_key(keys, rows, dim, reverse)
    known = [k for k in keys if rows[k]["values"][index] is not None]
    empty = [k for k in keys if rows[k]["values"][index] is None]
    known.sort(key=lambda k: rows[k]["values"][index], reverse=reverse)
    return known + empty


def _by_key(keys, rows, dim, reverse):
    """By the key of the group: a date by its day, a many2one by its name, the rest by its value."""
    by_label = dim and dim["kind"] in ("many2one", "selection")
    value = (lambda k: rows[k]["label"].lower()) if by_label else (lambda k: k)
    known = [k for k in keys if k is not None]
    known.sort(key=value, reverse=reverse)
    return known + [k for k in keys if k is None]
