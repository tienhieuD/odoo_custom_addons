# -*- coding: utf-8 -*-
"""The ``records`` engine (table): ``search`` + the readable columns, as the viewer."""
from odoo import fields
from odoo.exceptions import AccessError

from . import guard

SEE_MORE = 5  # relations shown in one cell


def run(env, model, vdef, widget, domain):
    columns = widget["wells"]["columns"]
    limit = widget.get("limit", vdef["limit"]["default"])
    order = ", ".join("%s %s" % (o["field"], o.get("dir", "asc")) for o in widget.get("order", [])) or None
    records = model.search(domain, order=order, limit=min(limit, guard.max_rows(env)) + 1)
    truncated = len(records) > limit
    records = records[:limit]
    metas = [_meta(model, c) for c in columns]
    rows = [[_cell(rec, c["field"], meta) for c, meta in zip(columns, metas)] for rec in records]
    return {"kind": "records", "columns": metas, "rows": rows, "ids": records.ids, "model": model._name,
            "truncated": {"rows": truncated}}


def _meta(model, column):
    current = model
    parts = column["field"].split(".")
    for part in parts[:-1]:
        current = current.env[current._fields[part].comodel_name]
    field = current._fields[parts[-1]]
    return {"field": column["field"], "label": column.get("label") or field.string, "type": field.type,
            "selection": dict(field._description_selection(model.env)) if field.type == "selection" else None}


def _cell(record, path, meta):
    """One value, JSON-ready. A record the viewer may not read is shown as empty, never as an error for the table."""
    try:
        value = record
        for part in path.split("."):
            value = value[part]
        return _jsonable(value, meta["type"])
    except AccessError:
        return None


def _jsonable(value, kind):
    if kind == "many2one":
        return [value.id, value.display_name] if value else None
    if kind in ("many2many", "one2many"):
        return [[r.id, r.display_name] for r in value[:SEE_MORE]] + ([["more", "…"]] if len(value) > SEE_MORE else [])
    if kind == "date":  # server formats: the client shows them in the viewer's language and time zone
        return fields.Date.to_string(value) if value else None
    if kind == "datetime":
        return fields.Datetime.to_string(value) if value else None
    if kind == "monetary" or kind == "float":
        return float(value)
    if kind in ("integer", "boolean"):
        return value
    return value or None
