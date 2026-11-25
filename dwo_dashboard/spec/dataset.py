# -*- coding: utf-8 -*-
"""Structural validation of a dataset definition (schema ``dwo-dataset/1``).

A page refers to a dataset (``orm:sale.order``, ``sql:sales_by_person``); the definition adds what the page must not
carry: metrics (named, reusable measures), field overrides, and for SQL datasets the query, its columns and who may
see it. Phase 0 only defines and validates the shape; the models that store definitions and the SQL execution are
built in later phases. Pure Python, same error format as structure.py."""
import re

from . import constants as C
from .structure import Errors, domain, ptr

_ID = re.compile(C.ID_PATTERN)
_FIELD = re.compile(C.FIELD_PATTERN)
_COLUMN = re.compile(C.COLUMN_PATTERN)
_MODEL = re.compile(C.MODEL_PATTERN)
_XMLID = re.compile(C.XMLID_PATTERN)
_PLACEHOLDER = re.compile(C.SQL_PLACEHOLDER)


def validate_dataset_structure(defn, registry):
    e = Errors()
    if not isinstance(defn, dict):
        e.add("", "type", "must be an object")
        return e.items
    kind = defn.get("type")
    dtype = registry.datasets.get(kind) if isinstance(kind, str) else None
    if dtype is None:
        e.add("/type", "enum", "must be one of: %s" % ", ".join(sorted(registry.datasets)))
        return e.items
    spec = dtype["definition"]
    common = ("schema", "type", "label", "metrics")
    e.obj("", defn, required=("schema", "type") + tuple(spec["required"]),
          optional=common[2:] + tuple(spec["optional"]))
    if defn.get("schema") != C.DATASET_SCHEMA_ID:
        e.add("/schema", "schema", "must be %r (got %r)" % (C.DATASET_SCHEMA_ID, defn.get("schema")))
    if "label" in defn:
        e.string("/label", defn["label"], 120)
    if kind == "orm":
        _orm(e, defn)
    elif kind == "sql":
        columns = _sql(e, defn)
    metrics = defn.get("metrics")
    if metrics is not None:
        _metrics(e, defn, metrics, dtype, kind, columns if kind == "sql" else None)
    return e.items


def _orm(e, defn):
    if "model" in defn:
        e.string("/model", defn["model"], 64, _MODEL, "a model name like 'sale.order'")
    fields = defn.get("fields")
    if fields is None:
        return
    if not isinstance(fields, dict):
        e.add("/fields", "type", "must be an object {field name: overrides}")
        return
    for name, over in fields.items():
        p = ptr("/fields", name)
        if not _FIELD.match(name):
            e.add(p, "pattern", "is not a valid field name")
        if e.obj(p, over, optional=("label", "role", "hidden", "format")):
            if "label" in over:
                e.string(ptr(p, "label"), over["label"], 120)
            if "role" in over:
                e.enum(ptr(p, "role"), over["role"], C.ROLES)
            if "hidden" in over:
                e.boolean(ptr(p, "hidden"), over["hidden"])
            if "format" in over:
                e.enum(ptr(p, "format"), over["format"], C.FORMATS)


def _sql(e, defn):
    """Returns {column name: column} of the valid columns."""
    columns = {}
    if "code" in defn:
        e.string("/code", defn["code"], 32, _ID, "an identifier like 'sales_by_person'")
    block = defn.get("sql")
    if block is None or not e.obj("/sql", block, required=("query", "columns", "groups"),
                                  optional=("params", "company_scoped")):
        return columns
    query = block.get("query")
    ok_query = e.string("/sql/query", query, C.MAX_SQL_LENGTH, what="the SQL text")
    declared = []
    if "params" in block and e.array("/sql/params", block["params"], 0, len(C.SQL_PARAMS)):
        for i, name in enumerate(block["params"]):
            if e.enum(ptr("/sql/params", i), name, C.SQL_PARAMS):
                if name in declared:
                    e.add(ptr("/sql/params", i), "duplicate", "parameter %r is declared twice" % name)
                declared.append(name)
    if ok_query:
        used = set(_PLACEHOLDER.findall(query))
        for name in sorted(used - set(declared)):
            e.add("/sql/query", "param", "uses %%(%s)s, which is not in 'params'" % name)
        for name in sorted(set(declared) - used):
            e.add("/sql/params", "param", "declares %r but the query does not use it" % name)
    if "company_scoped" in block and e.boolean("/sql/company_scoped", block["company_scoped"]):
        if block["company_scoped"] and "company_ids" not in declared:
            e.add("/sql/company_scoped", "company", "a company-scoped dataset must declare and use 'company_ids'")
    groups = block.get("groups")
    if e.array("/sql/groups", groups, 1, 20):
        for i, xmlid in enumerate(groups):
            e.string(ptr("/sql/groups", i), xmlid, 100, _XMLID, "a group external id like 'sales_team.group_sale_manager'")
    cols = block.get("columns")
    if e.array("/sql/columns", cols, 1, C.MAX_SQL_COLUMNS):
        for i, col in enumerate(cols):
            p = ptr("/sql/columns", i)
            if not e.obj(p, col, required=("name", "type", "role"), optional=("label",)):
                continue
            name_ok = e.string(ptr(p, "name"), col.get("name"), 63, _COLUMN, "a lower-case column name")
            type_ok = e.enum(ptr(p, "type"), col.get("type"), C.SQL_TYPES)
            role_ok = e.enum(ptr(p, "role"), col.get("role"), C.ROLES)
            if "label" in col:
                e.string(ptr(p, "label"), col["label"], 120)
            if type_ok and role_ok and col["role"] == "measure" and col["type"] not in C.SQL_NUMERIC_TYPES:
                e.add(ptr(p, "role"), "role", "a measure must be a number column, %s is %s" % (col.get("name"), col["type"]))
            if name_ok:
                if col["name"] in columns:
                    e.add(ptr(p, "name"), "duplicate", "column %r is declared twice" % col["name"])
                columns[col["name"]] = col
    return columns


def _metrics(e, defn, metrics, dtype, kind, sql_columns):
    if not e.array("/metrics", metrics, 0, C.MAX_METRICS):
        return
    seen = set()
    for i, m in enumerate(metrics):
        p = ptr("/metrics", i)
        if not e.obj(p, m, required=("name", "agg"), optional=("label", "field", "where", "format")):
            continue
        if e.string(ptr(p, "name"), m.get("name"), 32, _ID, "an identifier like 'revenue'"):
            if m["name"] in seen:
                e.add(ptr(p, "name"), "duplicate", "metric %r is declared twice" % m["name"])
            seen.add(m["name"])
        ok = e.enum(ptr(p, "agg"), m.get("agg"), C.AGGS)
        if "field" in m:
            e.string(ptr(p, "field"), m["field"], 64, _FIELD, "a field name")
        elif ok and m["agg"] != "count":
            e.add(ptr(p, "field"), "required", "is required unless agg is 'count' (record count)")
        if "label" in m:
            e.string(ptr(p, "label"), m["label"], 120)
        if "format" in m:
            e.enum(ptr(p, "format"), m["format"], C.FORMATS)
        if "where" in m:
            if not dtype["where"]:
                e.add(ptr(p, "where"), "not_allowed", "a %s dataset has no 'where' on metrics" % kind)
            else:
                domain(e, ptr(p, "where"), m["where"])
        if sql_columns is not None and "field" in m and m["field"] not in sql_columns:
            e.add(ptr(p, "field"), "reference", "%r is not a column of this dataset" % m["field"])
        elif sql_columns is not None and ok and "field" in m and m["field"] in sql_columns:
            col = sql_columns[m["field"]]
            if m["agg"] in C.NUMERIC_AGGS and col["role"] != "measure":
                e.add(ptr(p, "field"), "role", "%r needs a measure column; %s is a %s" % (
                    m["agg"], m["field"], col["role"]))
