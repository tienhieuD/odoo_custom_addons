# -*- coding: utf-8 -*-
"""Builds the JSON Schemas (draft 2020-12) from the registry, so a schema cannot drift from the validator.

- ``build_schema(registry)``: a dashboard page (dwo-dashboard/1). One ``widget_<type>`` definition per visual type, so a
  pie accepts one group-by and a bar two. Installing a plugin adds definitions: ``get_schema()`` rebuilds it.
- ``build_dataset_schema(registry)``: a dataset definition (dwo-dataset/1).

``python3 spec/schema_gen.py`` rewrites the two static files in static/schema/ with the CORE registry (a snapshot for
people and tools outside Odoo; a test checks they are up to date).

What a schema cannot say (the validators do): prefix-operator arity of a domain, overlapping widgets, unique ids,
``order`` that must name something used in the wells, references to filters, and everything that needs the database."""
import json
import os
import sys

if __package__:
    from . import constants as C
    from .registry import Registry
else:  # run as a script: python3 spec/schema_gen.py (no Odoo needed)
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    from spec import constants as C
    from spec.registry import Registry

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static", "schema")
PAGE_FILE = os.path.join(DIR, "dwo-dashboard-1.schema.json")
DATASET_FILE = os.path.join(DIR, "dwo-dataset-1.schema.json")


def _ref(name):
    return {"$ref": "#/$defs/" + name}


def _text(max_len, **extra):
    return dict({"type": "string", "minLength": 1, "maxLength": max_len}, **extra)


def _ctx(names):
    return {"type": "object", "additionalProperties": False, "required": ["ctx"],
            "properties": {"ctx": {"enum": list(names)}}}


def _common_defs():
    scalar = {"type": ["string", "number", "boolean", "null"]}
    return {
        "id": {"type": "string", "pattern": C.ID_PATTERN},
        "dataset_ref": {"type": "string", "pattern": C.DATASET_REF_PATTERN,
                        "description": "<dataset type>:<name>, e.g. orm:sale.order or sql:sales_by_person"},
        "domain": {
            "type": "array", "default": [],
            "description": "Odoo domain, prefix notation. Values: plain, or {\"ctx\": ...}.",
            "items": {"oneOf": [
                {"enum": list(C.DOMAIN_LOGIC)},
                {"type": "array", "minItems": 3, "maxItems": 3, "prefixItems": [
                    {"type": "string", "pattern": C.FIELD_PATH_PATTERN},
                    {"enum": list(C.DOMAIN_OPS)},
                    {"anyOf": [scalar, _ctx(C.CTX_NAMES),
                               {"type": "array", "items": {"anyOf": [scalar, _ctx(C.CTX_SCALAR)]}},
                               {"type": "array", "description": "sub-domain for any / not any"}]}]}]}},
        "dimension": {"type": "object", "additionalProperties": False, "required": ["field"], "properties": {
            "field": {"type": "string", "pattern": C.FIELD_PATH_PATTERN},
            "interval": {"enum": list(C.INTERVALS), "description": "required for date and datetime fields"},
            "label": _text(60)}},
        "measure": {"oneOf": [
            {"type": "object", "additionalProperties": False, "required": ["metric"], "properties": {
                "metric": {"type": "string", "pattern": C.ID_PATTERN}, "label": _text(60)}},
            {"type": "object", "additionalProperties": False, "required": ["agg"], "properties": {
                "agg": {"enum": list(C.AGGS)},
                "field": {"type": "string", "pattern": C.FIELD_PATTERN, "description": "omit only for agg=count"},
                "label": _text(60)}}]},
        "column": {"type": "object", "additionalProperties": False, "required": ["field"], "properties": {
            "field": {"type": "string", "pattern": C.FIELD_PATH_PATTERN}, "label": _text(60)}},
        "order": {"type": "array", "maxItems": C.MAX_ORDER, "items": {"type": "object", "additionalProperties": False,
                  "properties": {"field": {"type": "string"}, "measure": {"type": "string"},
                                 "dir": {"enum": list(C.DIRECTIONS)}},
                  "oneOf": [{"required": ["field"]}, {"required": ["measure"]}]}},
        "filter": {
            "type": "object", "additionalProperties": False, "required": ["id", "type", "bind"], "properties": {
                "id": _ref("id"), "type": {"enum": list(C.FILTER_TYPES)}, "label": _text(60),
                "default": {"type": "string", "description": "date: one of %s; selection: one of values; relation: "
                                                             "none" % ", ".join(C.DATE_PRESETS)},
                "model": {"type": "string", "pattern": C.MODEL_PATTERN,
                          "description": "relation only: the model whose records the picker offers; every bound "
                                         "ORM field must point to it (a SQL integer column is trusted to)"},
                "values": {"type": "array", "minItems": 1, "maxItems": 100, "uniqueItems": True,
                           "items": {"type": "string", "maxLength": 64},
                           "description": "selection only: the values offered"},
                "bind": {"type": "array", "minItems": 1, "maxItems": C.MAX_BINDS, "items": {
                    "type": "object", "additionalProperties": False, "required": ["dataset", "field"], "properties": {
                        "dataset": _ref("dataset_ref"),
                        "field": {"type": "string", "pattern": C.FIELD_PATTERN}}}}},
            "allOf": [
                {"if": {"properties": {"type": {"const": "relation"}}, "required": ["type"]},
                 "then": {"required": ["model"], "not": {"required": ["default"]}}, "else": {"not": {"required": ["model"]}}},
                {"if": {"properties": {"type": {"const": "selection"}}, "required": ["type"]},
                 "then": {"required": ["values"]}, "else": {"not": {"required": ["values"]}}}]},
    }


def _option(desc):
    kind = desc["kind"]
    if kind == "bool":
        return {"type": "boolean"}
    if kind == "enum":
        return {"enum": list(desc["values"])}
    if kind == "int":
        return {"type": "integer", "minimum": desc["min"], "maximum": desc["max"]}
    if kind == "number":
        out = {"type": "number"}
        if "min" in desc:
            out["minimum"] = desc["min"]
        if "max" in desc:
            out["maximum"] = desc["max"]
        return out
    if kind == "text":
        return {"type": "string", "minLength": 1, "maxLength": desc["max"]}
    return {"type": "array", "minItems": 1, "maxItems": desc["max"],
            "items": {"type": "string", "pattern": C.COLOR_PATTERN}}


def _widget(name, vdef):
    wells, required_wells = {}, []
    for wname, w in vdef["wells"].items():
        item = _ref(w["accepts"] if w["accepts"] != "measure" else "measure")
        wells[wname] = item if w["max"] == 1 else {"type": "array", "minItems": w["min"], "maxItems": w["max"],
                                                    "items": item}
        if w["min"] >= 1:
            required_wells.append(wname)
    props = {
        "id": _ref("id"), "type": {"const": name}, "title": _text(120),
        "x": {"type": "integer", "minimum": 0, "maximum": C.GRID_COLS_MAX - 1},
        "y": {"type": "integer", "minimum": 0},
        "w": {"type": "integer", "minimum": 1, "maximum": C.GRID_COLS_MAX},
        "h": {"type": "integer", "minimum": 1, "maximum": C.MAX_HEIGHT},
        "dataset": _ref("dataset_ref"),
        "wells": {"type": "object", "additionalProperties": False, "required": required_wells, "properties": wells},
        "where": _ref("domain"), "order": _ref("order"),
        "options": {"type": "object", "additionalProperties": False,
                    "properties": {k: _option(v) for k, v in (vdef.get("options") or {}).items()}},
        "ignore_filters": {"type": "array", "maxItems": C.MAX_FILTERS, "items": _ref("id")},
    }
    if vdef.get("compare"):
        props["compare"] = {
            "type": "object", "additionalProperties": False, "required": ["field"], "properties": {
                "field": {"type": "string", "pattern": C.FIELD_PATTERN,
                          "description": "a date or datetime field" + (", the axis field of the chart"
                                                                       if vdef["compare"] == "series" else "")},
                "period": {"enum": [p for p in C.DATE_PRESETS if p != "all"], "default": C.COMPARE_DEFAULT_PERIOD,
                           "description": "ignored when a page date filter is bound to the same field"},
                "against": {"enum": list(C.COMPARE_AGAINST), "default": "previous_period"}}}
    if vdef.get("trend"):
        props["trend"] = {
            "type": "object", "additionalProperties": False, "required": ["field"], "properties": {
                "field": {"type": "string", "pattern": C.FIELD_PATTERN, "description": "a date or datetime field"},
                "interval": {"enum": list(C.TREND_INTERVALS), "default": C.TREND_INTERVAL_DEFAULT},
                "points": {"type": "integer", "minimum": C.TREND_POINTS_MIN, "maximum": C.TREND_POINTS_MAX,
                           "default": C.TREND_POINTS_DEFAULT}}}
    for key in ("limit", "series_limit"):
        if vdef.get(key):
            props[key] = {"type": "integer", "minimum": 1, "maximum": vdef[key]["max"], "default": vdef[key]["default"]}
    return {"type": "object", "additionalProperties": False, "description": vdef.get("label", name),
            "required": ["id", "type", "x", "y", "w", "h", "dataset", "wells"], "properties": props}


def build_schema(registry):
    defs = _common_defs()
    for name, vdef in sorted(registry.visuals.items()):
        defs["widget_" + name] = _widget(name, vdef)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://duotek.io.vn/schema/dwo-dashboard-1.schema.json",
        "title": "Dynamic Dashboard page specification",
        "description": "One dashboard page: a grid of widgets and the page filters. A widget picks a dataset and "
                       "puts fields in the named wells of its visual type. Queries always run with the permissions "
                       "of the person who views the page.",
        "type": "object", "additionalProperties": False, "required": ["schema", "widgets"],
        "properties": {
            "schema": {"const": C.SCHEMA_ID}, "title": _text(120), "description": _text(500),
            "grid": {"type": "object", "additionalProperties": False, "properties": {
                "cols": {"type": "integer", "minimum": C.GRID_COLS_MIN, "maximum": C.GRID_COLS_MAX,
                         "default": C.GRID_COLS_DEFAULT}}},
            "filters": {"type": "array", "maxItems": C.MAX_FILTERS, "items": _ref("filter")},
            "widgets": {"type": "array", "maxItems": C.MAX_WIDGETS,
                        "items": {"oneOf": [_ref("widget_" + n) for n in sorted(registry.visuals)]}},
        },
        "$defs": defs,
    }


def build_dataset_schema(registry):
    metric = {"type": "object", "additionalProperties": False, "required": ["name", "agg"], "properties": {
        "name": {"type": "string", "pattern": C.ID_PATTERN}, "label": _text(120), "agg": {"enum": list(C.AGGS)},
        "field": {"type": "string", "pattern": C.FIELD_PATTERN, "description": "omit only for agg=count"},
        "where": {"type": "array", "description": "domain (ORM datasets only), same shape as in a page"},
        "format": {"enum": list(C.FORMATS)}}}
    orm = {"type": "object", "additionalProperties": False, "required": ["schema", "type", "model"], "properties": {
        "schema": {"const": C.DATASET_SCHEMA_ID}, "type": {"const": "orm"}, "label": _text(120),
        "model": {"type": "string", "pattern": C.MODEL_PATTERN},
        "fields": {"type": "object", "propertyNames": {"pattern": C.FIELD_PATTERN}, "additionalProperties": {
            "type": "object", "additionalProperties": False, "properties": {
                "label": _text(120), "role": {"enum": list(C.ROLES)}, "hidden": {"type": "boolean"},
                "format": {"enum": list(C.FORMATS)}}}},
        "metrics": {"type": "array", "maxItems": C.MAX_METRICS, "items": metric}}}
    sql = {"type": "object", "additionalProperties": False, "required": ["schema", "type", "code", "sql"],
           "properties": {
               "schema": {"const": C.DATASET_SCHEMA_ID}, "type": {"const": "sql"}, "label": _text(120),
               "code": {"type": "string", "pattern": C.ID_PATTERN},
               "sql": {"type": "object", "additionalProperties": False, "required": ["query", "columns", "groups"],
                       "properties": {
                           "query": _text(C.MAX_SQL_LENGTH, description="one SELECT / WITH...SELECT; parameters as "
                                          "%(name)s, a literal percent sign as %%"),
                           "params": {"type": "array", "uniqueItems": True, "items": {"enum": list(C.SQL_PARAMS)}},
                           "company_scoped": {"type": "boolean"},
                           "groups": {"type": "array", "minItems": 1, "maxItems": 20,
                                      "items": {"type": "string", "pattern": C.XMLID_PATTERN}},
                           "columns": {"type": "array", "minItems": 1, "maxItems": C.MAX_SQL_COLUMNS, "items": {
                               "type": "object", "additionalProperties": False, "required": ["name", "type", "role"],
                               "properties": {"name": {"type": "string", "pattern": C.COLUMN_PATTERN},
                                              "type": {"enum": list(C.SQL_TYPES)},
                                              "role": {"enum": list(C.ROLES)}, "label": _text(120)}}}}},
               "metrics": {"type": "array", "maxItems": C.MAX_METRICS, "items": metric}}}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://duotek.io.vn/schema/dwo-dataset-1.schema.json",
        "title": "Dynamic Dashboard dataset definition",
        "description": "Metrics and field overrides of an Odoo model (orm), or a SQL dataset (query, columns, groups).",
        "oneOf": [orm, sql],
    }


def _dump(path, data):
    with open(path, "w") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


if __name__ == "__main__":
    core = Registry.core()
    _dump(PAGE_FILE, build_schema(core))
    _dump(DATASET_FILE, build_dataset_schema(core))
    print("wrote", os.path.normpath(PAGE_FILE), "and", os.path.normpath(DATASET_FILE))
