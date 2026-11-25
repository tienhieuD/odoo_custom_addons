# -*- coding: utf-8 -*-
"""Clicks on a chart: cross-filter (a bar, a slice or a pivot row narrows the other widgets) and drill-down (a year
becomes its quarters, then its months...).

The client sends only WHAT was clicked: the id of the source widget and the group key it was given by the server. The
field, the interval and the type come from the saved page, and the conditions are built here, then added to the ``where``
of the widget before it is validated and run like any other (as the viewer, with the same access checks). A domain is
never taken from the client, and anything that does not fit is ignored: a stale click never breaks a page."""
import copy
import datetime as dt
import pytz

from . import dates, domain as dom

INTERVALS = ["year", "quarter", "month", "week", "day"]
PRIMARY_WELLS = ("axis", "category", "rows")
MAX_DEPTH = len(INTERVALS) - 1


def primary(widget):
    """The first dimension of a widget (the one a click on a bar, a slice or a row stands for), or None."""
    wells = widget.get("wells")
    if not isinstance(wells, dict):
        return None
    for name in PRIMARY_WELLS:
        item = wells.get(name)
        item = item[0] if isinstance(item, list) and item else item
        if isinstance(item, dict) and isinstance(item.get("field"), str):
            return item
    return None


def drill_chain(item):
    """The intervals a time axis goes through when drilled, from its own interval down to the day."""
    if item and item.get("interval") in INTERVALS:
        return INTERVALS[INTERVALS.index(item["interval"]):]
    return []


def _drills(interactions, widget_id):
    drills = interactions.get("drills") if isinstance(interactions, dict) else None
    drills = drills.get(widget_id) if isinstance(drills, dict) else None
    return drills if isinstance(drills, list) else None


def depth(interactions, widget_id, item):
    drills = _drills(interactions, widget_id)
    return min(len(drills), len(drill_chain(item)) - 1) if isinstance(drills, list) else 0


def apply(env, spec, widget, interactions):
    """The widget as it must run now: drilled into, and narrowed by the selection made in another widget."""
    if not isinstance(interactions, dict):
        return widget
    widget = copy.deepcopy(widget)
    leaves = []
    item = primary(widget)
    drills = _drills(interactions, widget.get("id"))
    chain = drill_chain(item)
    if item and chain and isinstance(drills, list) and widget.get("dataset", "").startswith("orm:"):
        try:
            model = env[widget["dataset"][4:]]
            steps = drills[:MAX_DEPTH]
            for level, key in enumerate(steps):
                leaves += key_leaves(env, model, item, chain[level], key)
            item["interval"] = chain[len(steps)]
        except (ValueError, KeyError, TypeError):
            leaves = []
    select = interactions.get("select")
    if isinstance(select, dict) and "key" in select and select.get("widget") != widget.get("id"):
        try:
            leaves += _selection_leaves(env, spec, widget, select, interactions)
        except (ValueError, KeyError, TypeError):
            pass
    if leaves:
        widget["where"] = list(widget.get("where", [])) + leaves
    return widget


def _selection_leaves(env, spec, widget, select, interactions):
    source = next((w for w in spec.get("widgets", []) if isinstance(w, dict) and w.get("id") == select.get("widget")), None)
    if source is None or not widget.get("dataset", "").startswith("orm:"):
        return []
    item = primary(source)
    chain = drill_chain(item)
    interval = chain[depth(interactions, source["id"], item)] if chain else None
    target = env[widget["dataset"][4:]]
    own = env[source["dataset"][4:]]
    src_field, dst_field = dom.field_at(own, item["field"]), dom.field_at(target, item["field"])
    if src_field is None or dst_field is None or src_field.type != dst_field.type \
            or getattr(src_field, "comodel_name", None) != getattr(dst_field, "comodel_name", None):
        return []  # another dataset without the same field: this widget does not take part
    return key_leaves(env, target, dict(item, interval=interval), interval, select.get("key"))


def key_leaves(env, model, item, interval, key):
    """The conditions that select one group, written for ``model``. Raises ValueError for a key that cannot be one."""
    name = item["field"]
    field = dom.field_at(model, name)
    if field is None:
        raise ValueError("unknown field")
    if key == "__other" or isinstance(key, (dict, list)):
        raise ValueError("not a group")
    if key is None or (key is False and field.type != "boolean") or key == "":
        return [[name, "=", False]]
    if field.type == "boolean":
        return [[name, "=", bool(key)]]
    if field.type in ("date", "datetime") and interval:
        start = _local_day(env, field, key)
        end = _next(start, interval)
        return [[name, ">=", dom.day_value(env, field, start)], [name, "<", dom.day_value(env, field, end)]]
    if field.type in ("many2one", "many2many", "one2many", "integer"):
        if isinstance(key, bool) or not isinstance(key, int):
            raise ValueError("an id is a whole number")
        return [[name, "=", key]]
    if field.type in ("float", "monetary"):
        if isinstance(key, bool) or not isinstance(key, (int, float)):
            raise ValueError("a number")
        return [[name, "=", key]]
    if not isinstance(key, str):
        raise ValueError("a text")
    return [[name, "=", key]]


def _local_day(env, field, key):
    """The first day of the group named by ``key`` (what the server wrote in the result), in the viewer's calendar."""
    if not isinstance(key, str):
        raise ValueError("a date")
    if field.type == "date":
        return dates.fromiso(key[:10])
    stamp = dt.datetime.strptime(key[:19], "%Y-%m-%d %H:%M:%S")
    tz = dates.tz_of(env.context.get("tz") or env.user.tz)
    return pytz.utc.localize(stamp).astimezone(tz).date()


def _next(day, interval):
    if interval == "day":
        return day + dt.timedelta(days=1)
    if interval == "week":
        return day + dt.timedelta(days=7)
    return dates.shift_months(day, {"month": 1, "quarter": 3, "year": 12}[interval])
