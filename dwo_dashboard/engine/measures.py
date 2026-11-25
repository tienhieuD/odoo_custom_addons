# -*- coding: utf-8 -*-
"""Reading the measures of a widget: one ``formatted_read_group``, or several when a metric has its own ``where``.

A metric with a ``where`` ("won revenue" = the revenue of the confirmed orders) cannot be a column of the same database
query as the other measures, which count every record of the widget. So each distinct ``where`` is a query of its own,
over the same groups, and the answers are merged by group.

Rules (written in SPEC.md):
* the groups are those of the widget's own domain (and its page filters), whatever the metric's ``where``: a group with
  records but none matching a metric shows 0 for a sum or a count and nothing for an average, a minimum or a maximum;
* the order and the limit of such a widget are applied here, after the merge, never by the database on a single metric
  (the top N of a metric computed from its own subset would not be the top N of the widget);
* a widget that has no metric with a ``where`` takes the direct path, byte for byte the call it always made."""
import json

from odoo.fields import Domain

INTERVALS = ("day", "week", "month", "quarter", "year")
ZERO_WHEN_EMPTY = ("sum", "count", "count_distinct")


def read(env, model, plan, domain, groupby, order=None, limit=None, measures=None, cap=None):
    """The groups of ``domain`` by ``groupby`` with every measure of ``measures`` (default: all of the plan's)."""
    measures = plan.measures if measures is None else measures
    if not any(m.get("where") for m in measures):
        return model.formatted_read_group(domain, groupby, [m["spec"] for m in measures], order=order, limit=limit)
    cap = cap or limit or 0
    base = [m for m in measures if not m.get("where")]
    by_where = {}
    for m in measures:
        if m.get("where"):
            by_where.setdefault(json.dumps(m["where"], sort_keys=True), []).append(m)
    universe = model.formatted_read_group(domain, groupby, [m["spec"] for m in base] or ["__count"], limit=cap or None)
    if cap and len(universe) >= cap:
        plan.truncated = True
    keyed = {_key(g, groupby): g for g in universe}
    for where_key, items in by_where.items():
        extra = Domain(domain) & Domain(items[0]["where"])
        if groupby and universe and cap and len(universe) >= cap:
            # the groups were cut at the cap: read the same groups, not whichever the metric happens to reach first (the
            # restriction is a long OR, so it is only written when it matters)
            extra &= Domain.OR([Domain(g["__extra_domain"]) for g in universe])
        found = model.formatted_read_group(extra, groupby, [m["read"] for m in items], limit=cap or None)
        found = {_key(g, groupby): g for g in found}
        for key, group in keyed.items():
            source = found.get(key)
            for m in items:
                value = source.get(m["read"]) if source else None
                group[m["spec"]] = (0 if m["agg"] in ZERO_WHEN_EMPTY else None) if value is None else value
    groups = list(keyed.values())
    if order:
        groups = _sort(groups, order)
    return groups[:limit] if limit else groups


def _key(group, groupby):
    return tuple(str(group.get(spec)) for spec in groupby)


def _sort(groups, order):
    """``order`` as Odoo writes it: "spec dir, spec dir". Empty values go last in either direction."""
    for part in reversed([p.strip() for p in order.split(",") if p.strip()]):
        spec, _sp, direction = part.partition(" ")
        reverse = direction.strip().lower() == "desc"
        by_key = ":" in spec and spec.split(":")[-1] in INTERVALS  # a date group is (key, label): the key is the date
        known = [g for g in groups if _sortable(g.get(spec), by_key) is not None]
        empty = [g for g in groups if _sortable(g.get(spec), by_key) is None]
        known.sort(key=lambda g: _sortable(g.get(spec), by_key), reverse=reverse)
        groups = known + empty
    return groups


def _sortable(value, by_key=False):
    if isinstance(value, (tuple, list)) and len(value) == 2:
        value = value[0] if by_key else value[1]  # a many2one group: its name, as Odoo orders them; a date: its key
    if value is None or value is False:
        return None
    return value


def resolve_metrics(widget, definition):
    """The widget with every ``{"metric": name}`` written out as the measure the definition gives it (field, aggregate, label,
    format and ``where``), keeping the metric's name as the key of the measure so that ``order`` can still refer to it.
    A name the definition does not have is left alone: the validation that comes before has already refused it."""
    metrics = {m["name"]: m for m in (definition or {}).get("metrics", [])}
    out = dict(widget, wells=dict(widget["wells"]))
    for well, value in widget["wells"].items():
        items = value if isinstance(value, list) else [value]
        resolved = []
        for item in items:
            m = metrics.get(item.get("metric")) if isinstance(item, dict) else None
            if m is None:
                resolved.append(item)
                continue
            merged = dict(item, agg=m["agg"], label=item.get("label") or m.get("label") or m["name"])
            for key in ("field", "where", "format"):
                if key in m:
                    merged[key] = m[key]
            resolved.append(merged)
        out["wells"][well] = resolved if isinstance(value, list) else resolved[0]
    return out
