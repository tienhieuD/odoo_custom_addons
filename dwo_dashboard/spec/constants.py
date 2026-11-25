# -*- coding: utf-8 -*-
"""Vocabulary shared by the validators and the JSON Schema generator. What depends on the installed plugins (visual
types, dataset types, their wells and options) is NOT here: it lives in the registry (registry.py)."""

SCHEMA_ID = "dwo-dashboard/1"
DATASET_SCHEMA_ID = "dwo-dataset/1"

AGGS = ("sum", "avg", "min", "max", "count", "count_distinct")
NUMERIC_AGGS = ("sum", "avg", "min", "max")
INTERVALS = ("day", "week", "month", "quarter", "year")
FILTER_TYPES = ("date", "relation", "selection")
DATE_PRESETS = (
    "all", "today", "yesterday", "last_7_days", "last_30_days", "last_90_days",
    "this_week", "last_week", "this_month", "last_month", "this_quarter", "last_quarter", "this_year", "last_year",
)
LEGENDS = ("none", "top", "bottom", "left", "right")
FORMATS = ("number", "currency", "percent")
DIRECTIONS = ("asc", "desc")
ROLES = ("dimension", "measure")
WELL_KINDS = ("dimension", "measure", "column")
QUERY_KINDS = ("grouped", "records")
OPTION_KINDS = ("bool", "enum", "int", "number", "text", "colors")
TRENDS = ("up", "down")
COMPARE_AGAINST = ("previous_period", "previous_year")
COMPARE_DEFAULT_PERIOD = "this_month"
TREND_INTERVALS = ("day", "week", "month")
TREND_POINTS_MIN, TREND_POINTS_MAX, TREND_POINTS_DEFAULT = 3, 60, 12
TREND_INTERVAL_DEFAULT = "month"

# domain. `any!` / `not any!` exist in Odoo 19 (they skip the record rules of the comodel): never allowed here.
DOMAIN_LOGIC = ("&", "|", "!")
DOMAIN_OPS = (
    "=", "!=", ">", ">=", "<", "<=", "like", "not like", "ilike", "not ilike", "=like", "=ilike",
    "in", "not in", "child_of", "parent_of", "any", "not any",
)
LIST_OPS = ("in", "not in")
SUBDOMAIN_OPS = ("any", "not any")
# a value can be {"ctx": "<name>"} (never a "$uid"-like string, which would clash with real text)
CTX_SCALAR = ("uid", "company_id", "today", "now")
CTX_LIST = ("company_ids",)
CTX_NAMES = CTX_SCALAR + CTX_LIST

# SQL datasets
SQL_TYPES = ("text", "integer", "numeric", "boolean", "date", "datetime")
SQL_NUMERIC_TYPES = ("integer", "numeric")
SQL_DATE_TYPES = ("date", "datetime")
SQL_PARAMS = ("uid", "company_id", "company_ids", "lang", "today", "now")

# limits
MAX_WIDGETS = 40
MAX_FILTERS = 10
MAX_BINDS = 10
MAX_METRICS = 50
MAX_SQL_COLUMNS = 100
MAX_SQL_LENGTH = 20000
MAX_DOMAIN_LEAVES = 50
MAX_DOMAIN_DEPTH = 5
MAX_ORDER = 3
GRID_COLS_MIN, GRID_COLS_MAX, GRID_COLS_DEFAULT = 6, 120, 12  # a page grows to the right like a sheet: 120 columns is 11 520 px
MAX_HEIGHT = 40

ID_PATTERN = r"^[a-z][a-z0-9_]{0,31}$"
MODEL_PATTERN = r"^[a-z][a-z0-9_.]{0,63}$"
ICON_PATTERN = r"^fa-[a-z0-9]+(-[a-z0-9]+){0,4}$"  # a Font Awesome 4 class (the set Odoo ships), without the "fa" prefix class
FIELD_PATTERN = r"^[a-z_][a-z0-9_]{0,63}$"
FIELD_PATH_PATTERN = r"^[a-z_][a-z0-9_]{0,63}(\.[a-z_][a-z0-9_]{0,63}){0,4}$"
COLUMN_PATTERN = r"^[a-z_][a-z0-9_]{0,62}$"
COLOR_PATTERN = r"^#[0-9a-fA-F]{6}$"
XMLID_PATTERN = r"^[a-z0-9_]+\.[a-z0-9_]+$"
DATASET_REF_PATTERN = r"^[a-z][a-z0-9_]{0,15}:[A-Za-z0-9_.]{1,64}$"
SQL_PLACEHOLDER = r"%\((\w+)\)s"


def measure_key(item):
    """Name of a measure in results and in ``order``: the metric name, ``__count`` for a record count, or
    ``<field>:<agg>``."""
    if "metric" in item:
        return item["metric"]
    if item.get("agg") == "count" and not item.get("field"):
        return "__count"
    return "%s:%s" % (item.get("field"), item.get("agg"))
