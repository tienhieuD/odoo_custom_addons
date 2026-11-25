# -*- coding: utf-8 -*-
"""The SQL engine: a query written by a dashboard manager, run for people it does not trust to write it.

A SQL dataset ignores the record rules of Odoo, so what protects the server is layered, and each layer is checked by a test:

1. **Who can reach it.** A widget on a SQL dataset runs only from a stored page the viewer may read (``run_widget``), or from
   Explore on a page the person may edit (``run_preview`` needs the page); the viewer must be in a group the dataset lists.
2. **A database login of its own.** The query runs on a separate connection as a PostgreSQL role that can only SELECT, set up once
   by an administrator (``tools/sql_role_setup.sql``; the user and password come from ``DWO_SQL_USER`` / ``DWO_SQL_PASSWORD``, never
   from the database). A role that is a superuser, can create roles or databases, or bypass row security is refused. There is
   no ``SET ROLE`` on the Odoo connection: a query could undo it.
3. **One statement, wrapped.** The text is scanned (``spec/sqlscan.py``: a single SELECT, no ``;``, balanced parentheses, strings and
   comments closed, ``%`` escaped) and run as ``SELECT <declared columns> FROM (<query>) q ...``: the identifiers come from the
   declared column list only, every value is a bound parameter.
4. **A read-only transaction with a timeout and a row cap**, on the connection, always rolled back and closed.
5. **The plan.** ``EXPLAIN`` lists the tables the statement touches (views expanded): the ones that hold secrets (users, API keys,
   configuration parameters, mail and payment credentials...) are refused even if the role could read them, and so is any
   function scan, which is how a query would call a function that reads a file or another server.

Nothing of the query result or its parameters is logged."""
import datetime as dt
import decimal
import logging
import os
import re
import time

import psycopg2
import psycopg2.errors
import pytz
from psycopg2 import sql as pgsql

from odoo import _, sql_db

from ..spec import constants as C
from ..spec.sqlscan import DENIED_CALLS, scan
from . import dates, fill, guard
from .domain import viewer_today

_logger = logging.getLogger(__name__)

ENV_USER, ENV_PASSWORD = "DWO_SQL_USER", "DWO_SQL_PASSWORD"
# the tables nobody reads through a dashboard, whatever the role can read; a database may add to the list
SENSITIVE_TABLES = frozenset((
    "res_users", "res_users_apikeys", "res_users_apikeys_description", "res_users_identitycheck", "res_users_settings",
    "res_users_log", "auth_totp_device", "auth_passkey_key", "ir_config_parameter", "ir_mail_server", "fetchmail_server",
    "iap_account", "payment_provider", "payment_token", "auth_oauth_provider", "ir_cron", "ir_actions_server",
    "ir_module_module", "ir_model_data", "base_import_mapping", "ir_attachment_access"))
ALLOWED_FUNCTIONS = frozenset(("generate_series", "unnest"))
# Columns that hold credentials, wherever they live: the setup script grants no SELECT on them, and a login that can read one is
# refused (a list of tables can never be complete; the privileges of the login are what holds)
SECRET_COLUMN = r"(password|passwd|secret|token|api_?key|private|pkcs|credential|signing_key|totp|otp_|backup_code|webhook|salt$|_hash$|^hash$)"
_CHECKED = {}
AGG_SQL = {"sum": "SUM", "avg": "AVG", "min": "MIN", "max": "MAX"}
TYPE_NAMES = {"text": "char", "integer": "integer", "numeric": "float", "boolean": "boolean", "date": "date", "datetime": "datetime"}


class SqlSetupError(Exception):
    """The server has no usable read-only role for SQL datasets."""


class SqlRefused(Exception):
    """The statement touches something a dataset may not."""


# ---------------------------------------------------------------------------------------------------- connection and role
def credentials():
    user, password = os.environ.get(ENV_USER), os.environ.get(ENV_PASSWORD)
    if not user or not password:
        raise SqlSetupError("no read-only database login is configured (%s and %s)" % (ENV_USER, ENV_PASSWORD))
    return user, password


def available():
    """Is a login configured? (Whether it is safe is checked every time a connection opens.)"""
    return bool(os.environ.get(ENV_USER) and os.environ.get(ENV_PASSWORD))


def _check_columns(conn, key):
    """The login must not be able to read a column that looks like a credential: Postgres is what enforces it, so this asks
    Postgres (``has_column_privilege``). Remembered for a minute per database and login."""
    if time.monotonic() - _CHECKED.get(key, -1e9) < 60:
        return
    with conn.cursor() as cr:
        cr.execute("SELECT c.relname, a.attname FROM pg_attribute a JOIN pg_class c ON c.oid = a.attrelid "
                   "JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'public' AND c.relkind IN ('r', 'v', 'm', 'p') "
                   "AND a.attnum > 0 AND NOT a.attisdropped AND a.attname ~* %s "
                   "AND has_column_privilege(current_user, c.oid, a.attnum, 'SELECT') LIMIT 1", [SECRET_COLUMN])
        row = cr.fetchone()
    conn.rollback()
    if row:
        raise SqlSetupError("the login can read the column %s.%s, which looks like a credential: run the setup script again" % tuple(row))
    _CHECKED[key] = time.monotonic()


def connect(env):
    user, password = credentials()
    info = dict(sql_db.connection_info_for(env.cr.dbname)[1])
    info.update(user=user, password=password, application_name="dwo_sql")
    conn = psycopg2.connect(**info)
    conn.set_session(readonly=True, autocommit=False)
    try:
        with conn.cursor() as cr:
            cr.execute("SELECT rolsuper OR rolcreaterole OR rolcreatedb OR rolbypassrls OR rolreplication "
                       "FROM pg_roles WHERE rolname = current_user")
            row = cr.fetchone()
            if row is None or row[0]:
                raise SqlSetupError("the database login of the SQL datasets is too powerful: it must only be able to read")
        _check_columns(conn, (env.cr.dbname, user))
    except Exception:
        conn.close()
        raise
    return conn


def denied_tables(env):
    extra = env["ir.config_parameter"].sudo().get_param("dwo_dashboard.sql_denied_tables", "")
    return SENSITIVE_TABLES | {t.strip().lower() for t in extra.split(",") if t.strip()}


def check_plan(cr, statement, params, denied):
    """Refuse a statement that touches a table that holds secrets, or scans a function (see the module docstring)."""
    cr.execute(pgsql.SQL("EXPLAIN (VERBOSE, FORMAT JSON) ") + statement, params)
    plan = cr.fetchone()[0][0]["Plan"]
    stack = [plan]
    while stack:
        node = stack.pop()
        name = (node.get("Relation Name") or "").lower()
        if name and (name in denied or node.get("Schema") in ("pg_catalog", "information_schema")):
            raise SqlRefused("the query reads a table that dashboards may not read")
        if node.get("Node Type") == "Function Scan" and (node.get("Function Name") or "").lower() not in ALLOWED_FUNCTIONS:
            raise SqlRefused("the query scans a function: only generate_series and unnest are allowed")
        if node.get("Node Type") in ("Foreign Scan", "Custom Scan"):
            raise SqlRefused("the query reads a foreign table")
        stack.extend(node.get("Plans", []))


PG_TYPES = {21: "integer", 23: "integer", 20: "integer", 700: "numeric", 701: "numeric", 1700: "numeric", 16: "boolean",
            1082: "date", 1114: "datetime", 1184: "datetime"}


def execute(env, statement, params, limit, types=None):
    """Run one statement as the read-only role; returns ``(column names, rows)``. Everything on a connection of its own.
    ``types``: a list that receives the dataset type of each column (what the Test button of the form needs)."""
    started = time.monotonic()
    timeout = guard.timeout_seconds(env)
    conn = connect(env)
    try:
        with conn.cursor() as cr:
            cr.execute("SET LOCAL statement_timeout = %s", ["%ds" % timeout])
            cr.execute("SET LOCAL lock_timeout = '2s'")
            cr.execute("SET LOCAL TIME ZONE 'UTC'")
            check_plan(cr, statement, params, denied_tables(env))
            cr.execute(statement, params)
            rows = cr.fetchmany(limit)
            names = [d[0] for d in cr.description]
            if types is not None:
                types.extend(PG_TYPES.get(d[1], "text") for d in cr.description)
        return names, rows
    finally:
        conn.rollback()
        conn.close()
        _logger.info("dashboard sql: a query ran for %.2f s", time.monotonic() - started)  # no text, no parameters, no rows


# ---------------------------------------------------------------------------------------------------- the statement
def _params(env, declared):
    tz = env.context.get("tz") or env.user.tz or "UTC"
    values = {"uid": env.uid, "company_id": env.company.id, "company_ids": list(env.companies.ids),
              "lang": env.lang or "en_US", "today": viewer_today(env), "now": dt.datetime.utcnow()}
    out = {name: values[name] for name in declared if name in values}
    out["__tz"] = tz if tz in pytz.all_timezones_set else "UTC"
    return out


def _wrap(block, columns, select, extra_where, tail):
    """``SELECT <select> FROM (<query>) q WHERE ... <tail>``: the query text is the only raw piece, between its own lines."""
    query = block["query"].strip()
    where = pgsql.SQL(" WHERE ") + pgsql.SQL(" AND ").join(extra_where) if extra_where else pgsql.SQL("")
    return pgsql.SQL("SELECT ") + select + pgsql.SQL(" FROM (\n") + pgsql.SQL(query) + pgsql.SQL("\n) AS q") + where + tail


def _filters(env, spec, widget, columns, filter_values, params):
    """Page filters bound to columns of this dataset, as bound conditions. The value comes from the client and is never used as
    it is: dates are preset names, relations are whole numbers, selections are among the declared values."""
    out = []
    ignored = set(widget.get("ignore_filters", []))
    values = filter_values if isinstance(filter_values, dict) else {}
    tz = params["__tz"]
    for n, flt in enumerate(spec.get("filters", [])):
        if flt["id"] in ignored:
            continue
        for k, bind in enumerate(flt["bind"]):
            if bind["dataset"] != widget["dataset"] or bind["field"] not in columns:
                continue
            col, name = columns[bind["field"]], "f_%d_%d" % (n, k)
            ident, value = pgsql.Identifier(bind["field"]), values.get(flt["id"])
            if flt["type"] == "date":
                preset = value if value in C.DATE_PRESETS else flt.get("default", "all")
                span = dates.preset_range(preset, viewer_today(env), 0)
                if span is None:
                    continue
                lo, hi = span if col["type"] == "date" else (dates.to_utc(span[0], tz), dates.to_utc(span[1], tz))
                params[name + "a"], params[name + "b"] = lo, hi
                out.append(pgsql.SQL("{} >= {} AND {} < {}").format(
                    ident, pgsql.Placeholder(name + "a"), ident, pgsql.Placeholder(name + "b")))
            elif flt["type"] == "relation":
                ids = [v for v in (value if isinstance(value, list) else [value]) if isinstance(v, int) and not isinstance(v, bool)][:200]
                if ids:
                    params[name] = ids
                    out.append(pgsql.SQL("{} = ANY({})").format(ident, pgsql.Placeholder(name)))
            elif flt["type"] == "selection":
                wanted = [v for v in (value if isinstance(value, list) else [value]) if v in flt["values"]]
                if wanted:
                    params[name] = wanted
                    out.append(pgsql.SQL("{}::text = ANY({})").format(ident, pgsql.Placeholder(name)))
    return out


def _dimension_expr(col, name, interval, params):
    ident = pgsql.Identifier(name)
    if col["type"] in C.SQL_DATE_TYPES and interval in C.INTERVALS:
        if col["type"] == "datetime":  # a datetime column is UTC; the buckets are days in the viewer's time zone
            return pgsql.SQL("date_trunc({}, ({}::timestamp AT TIME ZONE 'UTC') AT TIME ZONE {})").format(
                pgsql.Literal(interval), ident, pgsql.Placeholder("__tz"))
        return pgsql.SQL("date_trunc({}, {})").format(pgsql.Literal(interval), ident)
    return ident


def _measure_expr(columns, item, metrics):
    if "metric" in item:
        item = metrics[item["metric"]]
    agg, field = item["agg"], item.get("field")
    if agg == "count" and not field:
        return pgsql.SQL("COUNT(*)")
    ident = pgsql.Identifier(field)
    if agg == "count":
        return pgsql.SQL("COUNT({})").format(ident)
    if agg == "count_distinct":
        return pgsql.SQL("COUNT(DISTINCT {})").format(ident)
    return pgsql.SQL("{}({})").format(pgsql.SQL(AGG_SQL[agg]), ident)


def _value(value):
    if isinstance(value, decimal.Decimal):
        return float(value)
    if isinstance(value, dt.datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, dt.date):
        return value.isoformat()
    return value


# ---------------------------------------------------------------------------------------------------- the widgets
def run(env, spec, widget, defn, vdef, filter_values):
    block = defn["sql"]
    problems, _names = scan(block["query"])  # again, whoever wrote the record: only a clean query reaches the database
    if problems:
        raise SqlRefused(problems[0])
    columns = {c["name"]: c for c in block["columns"]}
    metrics = {m["name"]: m for m in defn.get("metrics", [])}
    params = _params(env, block.get("params", []))
    cap = guard.max_rows(env)
    if vdef["query"] == "records":
        return _records(env, spec, widget, vdef, block, columns, params, filter_values, cap)
    return _grouped(env, spec, widget, vdef, block, columns, metrics, params, filter_values, cap)


def _first(widget, vdef, accepts):
    for name, wdef in vdef["wells"].items():
        if wdef["accepts"] == accepts and widget["wells"].get(name):
            value = widget["wells"][name]
            return name, value if isinstance(value, list) else [value]
    return None, []


def _grouped(env, spec, widget, vdef, block, columns, metrics, params, filter_values, cap):
    dim_well = next((w for w, d in vdef["wells"].items() if d["accepts"] == "dimension" and w in ("axis", "category", "rows")), None)
    dim_item = (widget["wells"].get(dim_well) or [None])[0] if dim_well and isinstance(widget["wells"].get(dim_well), list) \
        else widget["wells"].get(dim_well) if dim_well else None
    _well, items = _first(widget, vdef, "measure")
    dim_col = columns[dim_item["field"]] if dim_item else None
    interval = dim_item.get("interval") if dim_item else None
    select = [_dimension_expr(dim_col, dim_item["field"], interval, params)] if dim_item else []
    select += [_measure_expr(columns, it, metrics) for it in items]
    aliased = pgsql.SQL(", ").join(
        e + pgsql.SQL(" AS ") + pgsql.Identifier("c%d" % i) for i, e in enumerate(select))
    order = _order(widget, dim_item, items, dim_col)
    limit = widget.get("limit", vdef["limit"]["default"] if vdef.get("limit") else None)
    fetch = min(cap, (limit + 1) if limit else cap)
    tail = (pgsql.SQL(" GROUP BY 1") if dim_item else pgsql.SQL("")) + order + pgsql.SQL(" LIMIT {}").format(pgsql.Literal(fetch))
    statement = _wrap(block, columns, aliased, _filters(env, spec, widget, columns, filter_values, params), tail)
    _names, rows = execute(env, statement, params, fetch)
    cut = bool(limit) and len(rows) > limit
    rows = rows[:limit] if limit else rows
    out = []
    for row in rows:
        values = [float(v) if isinstance(v, (int, float, decimal.Decimal)) and not isinstance(v, bool) else v for v in row[1 if dim_item else 0:]]
        if dim_item:
            key, label = _group(env, dim_col, interval, row[0])
            out.append({"keys": [key], "labels": [label], "values": values})
        else:
            out.append({"keys": [], "labels": [], "values": values})
    dims = [{"well": dim_well, "field": dim_item["field"], "interval": interval,
             "label": dim_col.get("label") or dim_item["field"], "type": TYPE_NAMES[dim_col["type"]]}] if dim_item else []
    measures = []
    for it in items:
        m = metrics[it["metric"]] if "metric" in it else it
        label = it.get("label") or m.get("label") or (columns[m["field"]].get("label") or m["field"] if m.get("field") else _("Count"))
        measures.append({"key": it["metric"] if "metric" in it else ("__count" if not m.get("field") else "%s:%s" % (m["field"], m["agg"])),
                         "label": label, "agg": m["agg"], "format": m.get("format")})
    return {"kind": "grouped", "dims": dims, "rows": out, "truncated": {"axis": cut, "series": False, "rows": len(rows) >= cap},
            "measures": measures}


def _order(widget, dim_item, items, dim_col):
    """``ORDER BY`` by position (1 is the dimension, then the measures): nothing of the client is written into it."""
    asked = (widget.get("order") or [{}])[0]
    direction = "DESC" if asked.get("dir") == "desc" else "ASC"
    if "measure" in asked:
        keys = [it.get("metric") or ("__count" if not it.get("field") else "%s:%s" % (it["field"], it["agg"])) for it in items]
        if asked["measure"] in keys:
            return pgsql.SQL(" ORDER BY {} {} NULLS LAST").format(pgsql.Literal(keys.index(asked["measure"]) + (2 if dim_item else 1)), pgsql.SQL(direction))
    elif "field" in asked and dim_item and asked["field"] == dim_item["field"]:
        return pgsql.SQL(" ORDER BY 1 {} NULLS LAST").format(pgsql.SQL(direction))
    if dim_item and dim_col["type"] in C.SQL_DATE_TYPES:
        return pgsql.SQL(" ORDER BY 1 ASC NULLS LAST")
    if dim_item and items:
        return pgsql.SQL(" ORDER BY 2 DESC NULLS LAST")
    return pgsql.SQL("")


def _group(env, col, interval, value):
    """``(key, label)`` of a group, as the grouped engine writes them."""
    if value is None:
        return None, _("None")
    if col["type"] in C.SQL_DATE_TYPES and interval:
        day = value.date() if isinstance(value, dt.datetime) else value
        return day.isoformat(), fill.key_and_label(env, "date", interval, day)[1]
    if col["type"] == "boolean":
        return bool(value), _("Yes") if value else _("No")
    return _value(value), str(_value(value))


def _records(env, spec, widget, vdef, block, columns, params, filter_values, cap):
    wanted = [c["field"] for c in widget["wells"]["columns"]]
    limit = widget.get("limit", vdef["limit"]["default"])
    fetch = min(cap, limit + 1)
    select = pgsql.SQL(", ").join(pgsql.Identifier(name) for name in wanted)
    order = pgsql.SQL("")
    asked = [o for o in widget.get("order", []) if o.get("field") in columns]
    if asked:
        order = pgsql.SQL(" ORDER BY ") + pgsql.SQL(", ").join(
            pgsql.SQL("{} {} NULLS LAST").format(pgsql.Identifier(o["field"]), pgsql.SQL("DESC" if o.get("dir") == "desc" else "ASC")) for o in asked)
    statement = _wrap(block, columns, select, _filters(env, spec, widget, columns, filter_values, params),
                      order + pgsql.SQL(" LIMIT {}").format(pgsql.Literal(fetch)))
    _names, rows = execute(env, statement, params, fetch)
    cut = len(rows) > limit
    metas = [{"field": n, "label": columns[n].get("label") or n, "type": TYPE_NAMES[columns[n]["type"]], "selection": None} for n in wanted]
    return {"kind": "records", "columns": metas, "rows": [[_value(v) for v in row] for row in rows[:limit]], "ids": [], "model": None,
            "truncated": {"rows": cut}}


def sample(env, block, rows=20):
    """The first rows of a dataset's query, under every guard above: ``(names, types, rows)``. For the Test button."""
    problems, _names = scan(block["query"])
    if problems:
        raise SqlRefused(problems[0])
    params = _params(env, block.get("params", []))
    statement = _wrap(block, {}, pgsql.SQL("*"), [], pgsql.SQL(" LIMIT {}").format(pgsql.Literal(rows)))
    types = []
    names, result = execute(env, statement, params, rows, types)
    return names, types, [[_value(v) for v in row] for row in result]
