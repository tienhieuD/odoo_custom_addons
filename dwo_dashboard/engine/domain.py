# -*- coding: utf-8 -*-
"""Domains of a widget: its own ``where`` (context values resolved), plus the page filters."""
import datetime as dt

from odoo import fields
from odoo.tools import get_lang

from ..spec import constants as C
from . import dates

MAX_IDS = 200


def viewer_today(env):
    return dates.today_in_tz(env.context.get("tz") or env.user.tz)


def first_weekday(env):
    try:
        return int(get_lang(env).week_start) - 1
    except (TypeError, ValueError):
        return 0


def field_at(model, dotted):
    """The last field of ``a.b.c`` (None if a step is unknown)."""
    field = None
    for part in dotted.split("."):
        field = model._fields.get(part)
        if field is None:
            return None
        if field.relational:
            model = model.env[field.comodel_name]
    return field


def day_value(env, field, day):
    """A calendar day as the value to compare with ``field`` (date: the day; datetime: its start in the viewer's tz, UTC)."""
    if field is not None and field.type == "datetime":
        return fields.Datetime.to_string(dates.to_utc(day, env.context.get("tz") or env.user.tz))
    return fields.Date.to_string(day)


def resolve_ctx(env, model, domain):
    """Replace ``{"ctx": name}`` values by what they mean for the viewer. Returns a new domain."""
    out = []
    for token in domain:
        if not isinstance(token, list):
            out.append(token)
            continue
        name, op, value = token
        field = field_at(model, name)
        if op in C.SUBDOMAIN_OPS:
            out.append((name, op, resolve_ctx(env, model.env[field.comodel_name], value)))
        elif isinstance(value, dict):
            out.append((name, op, _ctx_value(env, field, value["ctx"])))
        elif isinstance(value, list):
            out.append((name, op, [_ctx_value(env, field, v["ctx"]) if isinstance(v, dict) else v for v in value]))
        else:
            out.append((name, op, value))
    return out


def _ctx_value(env, field, name):
    if name == "uid":
        return env.uid
    if name == "company_id":
        return env.company.id
    if name == "company_ids":
        return list(env.companies.ids)
    if name == "today":
        return day_value(env, field, viewer_today(env))
    if name == "now":
        if field is not None and field.type == "date":
            return fields.Date.to_string(viewer_today(env))
        return fields.Datetime.to_string(fields.Datetime.now())
    raise ValueError("unknown context value %r" % name)


def filter_domain(env, model, flt, value, field_name):
    """The domain one page filter adds to a widget of ``model``. ``value`` comes from the client and is NEVER used as it
    is: dates are preset names, relations are integers, selections are among the filter's declared values."""
    field = field_at(model, field_name)
    if field is None:
        return []
    kind = flt["type"]
    if kind == "date":
        preset = value if value in C.DATE_PRESETS else flt.get("default", "all")
        span = dates.preset_range(preset, viewer_today(env), first_weekday(env))
        if span is None:
            return []
        return [(field_name, ">=", day_value(env, field, span[0])), (field_name, "<", day_value(env, field, span[1]))]
    if kind == "relation":
        ids = [v for v in (value if isinstance(value, list) else [value])
               if isinstance(v, int) and not isinstance(v, bool)][:MAX_IDS]
        return [(field_name, "in", ids)] if ids else []
    if kind == "selection":
        wanted = [v for v in (value if isinstance(value, list) else [value]) if v in flt["values"]]
        return [(field_name, "in", wanted)] if wanted else []
    return []


def widget_domain(env, model, spec, widget, filter_values, skip_filters=()):
    """AND of the widget's ``where`` (context resolved) and of every page filter that applies to it, except the filters
    listed in ``skip_filters`` (a comparison replaces the date condition of its own field)."""
    from odoo.fields import Domain
    domain = Domain(resolve_ctx(env, model, widget.get("where", [])))
    ignored = set(widget.get("ignore_filters", [])) | set(skip_filters)
    filter_values = filter_values if isinstance(filter_values, dict) else {}
    for flt in spec.get("filters", []):
        if flt["id"] in ignored:
            continue
        for bind in flt["bind"]:
            if bind["dataset"] == widget["dataset"]:
                domain &= Domain(filter_domain(env, model, flt, filter_values.get(flt["id"]), bind["field"]))
    return domain


def compare_setup(env, model, spec, widget, filter_values):
    """For a KPI with ``compare``: the domain of the current period, the domain of the previous one and what to tell the
    client; None when there is nothing to compare (the period is ``all``).

    The period is the one of a page date filter bound to the same dataset and field (unless the widget ignores it),
    else ``compare.period``. That filter's own condition is REPLACED by the two ranges, not added to them: otherwise
    the previous period would always be empty. Every other filter and the widget's ``where`` still apply to both."""
    from odoo.fields import Domain
    cmp = widget["compare"]
    name, dataset = cmp["field"], widget["dataset"]
    values = filter_values if isinstance(filter_values, dict) else {}
    preset, skip = cmp.get("period", C.COMPARE_DEFAULT_PERIOD), []
    for flt in spec.get("filters", []):
        bound = flt["type"] == "date" and flt["id"] not in widget.get("ignore_filters", []) and any(
            b["dataset"] == dataset and b["field"] == name for b in flt["bind"])
        if bound:
            skip.append(flt["id"])
            if len(skip) == 1:
                value = values.get(flt["id"])
                preset = value if value in C.DATE_PRESETS else flt.get("default", "all")
    if preset == "all":
        return None
    field = field_at(model, name)
    start, end, prev_start, prev_end = dates.compare_ranges(
        preset, viewer_today(env), first_weekday(env), cmp.get("against", "previous_period"))
    base = widget_domain(env, model, spec, widget, filter_values, skip_filters=skip)

    def within(a, b):
        return base & Domain([(name, ">=", day_value(env, field, a)), (name, "<", day_value(env, field, b))])

    one_day = dt.timedelta(days=1)
    to_s = fields.Date.to_string
    return {"domain": within(start, end), "previous_domain": within(prev_start, prev_end),
            "info": {"field": name, "period": preset, "against": cmp.get("against", "previous_period"),
                     "range": [to_s(start), to_s(end)], "previous_range": [to_s(prev_start), to_s(prev_end)],
                     # inclusive bounds for Odoo's fill_temporal (a line chart draws every interval of both ranges)
                     "fill": {"from": to_s(start), "to": to_s(end - one_day),
                              "previous_from": to_s(prev_start), "previous_to": to_s(prev_end - one_day)}}}


def trend_setup(env, model, spec, widget, filter_values):
    """The sparkline of a KPI: its measure over the last ``points`` intervals up to today, whatever period the page shows
    (a trend is about the evolution, so the page's date filter on the same field is replaced, like for a comparison; every
    other filter and ``where`` still apply)."""
    from odoo.fields import Domain
    trend = widget["trend"]
    name, dataset = trend["field"], widget["dataset"]
    interval = trend.get("interval", C.TREND_INTERVAL_DEFAULT)
    points = trend.get("points", C.TREND_POINTS_DEFAULT)
    skip = [flt["id"] for flt in spec.get("filters", []) if flt["type"] == "date"
            and flt["id"] not in widget.get("ignore_filters", [])
            and any(b["dataset"] == dataset and b["field"] == name for b in flt["bind"])]
    today = viewer_today(env)
    start, end = dates.trend_range(interval, points, today, first_weekday(env))
    field = field_at(model, name)
    base = widget_domain(env, model, spec, widget, filter_values, skip_filters=skip)
    domain = base & Domain([(name, ">=", day_value(env, field, start)), (name, "<", day_value(env, field, end))])
    return {"domain": domain, "field": name, "interval": interval,
            "from": fields.Date.to_string(start), "to": fields.Date.to_string(today)}
