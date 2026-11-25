# -*- coding: utf-8 -*-
"""Domains of a widget: its own ``where`` (context values resolved), plus the page filters."""
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


def widget_domain(env, model, spec, widget, filter_values):
    """AND of the widget's ``where`` (context resolved) and of every page filter that applies to it."""
    from odoo.fields import Domain
    domain = Domain(resolve_ctx(env, model, widget.get("where", [])))
    ignored = set(widget.get("ignore_filters", []))
    filter_values = filter_values if isinstance(filter_values, dict) else {}
    for flt in spec.get("filters", []):
        if flt["id"] in ignored:
            continue
        for bind in flt["bind"]:
            if bind["dataset"] == widget["dataset"]:
                domain &= Domain(filter_domain(env, model, flt, filter_values.get(flt["id"]), bind["field"]))
    return domain
