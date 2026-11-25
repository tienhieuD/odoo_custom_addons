# -*- coding: utf-8 -*-
"""Structural validation: types, required keys, enums, limits, layout, references between the parts of one page.

Pure Python (no Odoo, no external library): ``validate_structure(spec, registry)``. Returns a list of errors, empty
when valid. An error is ``{"path": "/widgets/2/wells/values/0/agg", "code": "enum", "message": "..."}``; ``path`` is
an RFC 6901 JSON Pointer ("" is the whole document), which is also what JSON Patch uses.

Models, fields and permissions are checked by semantic.py, which needs a database."""
import re

from . import constants as C

_ID = re.compile(C.ID_PATTERN)
_FIELD = re.compile(C.FIELD_PATTERN)
_FIELD_PATH = re.compile(C.FIELD_PATH_PATTERN)
_COLOR = re.compile(C.COLOR_PATTERN)
_REF = re.compile(C.DATASET_REF_PATTERN)


def ptr(base, *parts):
    """Append reference tokens to a JSON Pointer (escaping ~ and /)."""
    return base + "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in parts)


class Errors:
    def __init__(self):
        self.items = []

    def add(self, path, code, message):
        self.items.append({"path": path, "code": code, "message": message})

    # -- primitives: each returns True when the value is usable
    def obj(self, path, value, required=(), optional=()):
        if not isinstance(value, dict):
            self.add(path, "type", "must be an object")
            return False
        for key in required:
            if key not in value:
                self.add(ptr(path, key), "required", "is required")
        for key in value:
            if key not in required and key not in optional:
                self.add(ptr(path, key), "unknown_key", "is not allowed here")
        return True

    def string(self, path, value, max_len=120, pattern=None, what="a string"):
        if not isinstance(value, str) or not value.strip():
            self.add(path, "type", "must be %s (not empty)" % what)
            return False
        if len(value) > max_len:
            self.add(path, "too_long", "must be at most %d characters" % max_len)
            return False
        if pattern is not None and not pattern.match(value):
            self.add(path, "pattern", "has an invalid format: %r" % value)
            return False
        return True

    def integer(self, path, value, minimum=None, maximum=None):
        if isinstance(value, bool) or not isinstance(value, int):
            self.add(path, "type", "must be an integer")
            return False
        if minimum is not None and value < minimum or maximum is not None and value > maximum:
            self.add(path, "range", "must be between %s and %s" % (minimum, maximum))
            return False
        return True

    def boolean(self, path, value):
        if not isinstance(value, bool):
            self.add(path, "type", "must be true or false")
            return False
        return True

    def enum(self, path, value, allowed):
        if not isinstance(value, str) or value not in allowed:
            self.add(path, "enum", "must be one of: %s" % ", ".join(allowed))
            return False
        return True

    def array(self, path, value, min_items=0, max_items=None):
        if not isinstance(value, list):
            self.add(path, "type", "must be an array")
            return False
        if len(value) < min_items or max_items is not None and len(value) > max_items:
            self.add(path, "length", "must have between %d and %s items" % (min_items, max_items or "many"))
            return False
        return True


# ================================================================================================== the page
def validate_structure(spec, registry):
    """Validate a page (already parsed JSON) against the registry of installed visual and dataset types."""
    e = Errors()
    if not e.obj("", spec, required=("schema", "widgets"), optional=("title", "description", "grid", "filters")):
        return e.items
    if spec.get("schema") != C.SCHEMA_ID:
        e.add("/schema", "schema", "must be %r (got %r)" % (C.SCHEMA_ID, spec.get("schema")))
    if "title" in spec:
        e.string("/title", spec["title"], 120)
    if "description" in spec:
        e.string("/description", spec["description"], 500)
    cols = C.GRID_COLS_DEFAULT
    if "grid" in spec:
        grid = spec["grid"]
        if e.obj("/grid", grid, optional=("cols",)) and "cols" in grid:
            if e.integer("/grid/cols", grid["cols"], C.GRID_COLS_MIN, C.GRID_COLS_MAX):
                cols = grid["cols"]
    filters = _filters(e, spec.get("filters", []), registry)
    used = _widgets(e, spec.get("widgets"), cols, filters, registry)
    for i, flt in enumerate(spec.get("filters", []) if isinstance(spec.get("filters", []), list) else []):
        for j, bind in enumerate(flt.get("bind", []) if isinstance(flt, dict) and isinstance(flt.get("bind"), list) else []):
            if isinstance(bind, dict) and isinstance(bind.get("dataset"), str) and bind["dataset"] not in used:
                e.add(ptr("/filters", i, "bind", j, "dataset"), "reference",
                      "no widget uses dataset %r" % bind["dataset"])
    return e.items


def dataset_ref(e, path, value, registry):
    """Check ``orm:sale.order`` style references; returns the dataset type definition or None."""
    if not e.string(path, value, 90, _REF, "a dataset reference like 'orm:sale.order'"):
        return None
    prefix, name = value.split(":", 1)
    dtype = registry.datasets.get(prefix)
    if dtype is None:
        e.add(path, "enum", "unknown dataset type %r (installed: %s)" % (prefix, ", ".join(sorted(registry.datasets))))
        return None
    if not re.match(dtype["name_pattern"], name):
        e.add(path, "pattern", "%r is not a valid %s dataset name" % (name, prefix))
        return None
    return dtype


# --------------------------------------------------------------------------------------------------- filters
def _filters(e, value, registry):
    """Returns {filter id: filter type} of the valid filters."""
    found = {}
    if not e.array("/filters", value, 0, C.MAX_FILTERS):
        return found
    for i, flt in enumerate(value):
        path = ptr("/filters", i)
        if not e.obj(path, flt, required=("id", "type", "bind"), optional=("label", "default", "model", "values")):
            continue
        ok_id = e.string(ptr(path, "id"), flt.get("id"), 32, _ID, "an identifier like 'period'")
        kind = flt.get("type")
        ok_type = e.enum(ptr(path, "type"), kind, C.FILTER_TYPES)
        if "label" in flt:
            e.string(ptr(path, "label"), flt["label"], 60)
        if ok_type:
            _filter_kind(e, path, flt, kind)
        binds = flt.get("bind")
        if e.array(ptr(path, "bind"), binds, 1, C.MAX_BINDS):
            seen = set()
            for j, bind in enumerate(binds):
                bpath = ptr(path, "bind", j)
                if not e.obj(bpath, bind, required=("dataset", "field")):
                    continue
                dataset_ref(e, ptr(bpath, "dataset"), bind.get("dataset"), registry)
                e.string(ptr(bpath, "field"), bind.get("field"), 64, _FIELD, "a field or column name")
                if bind.get("dataset") in seen:
                    e.add(bpath, "duplicate", "dataset %r is bound twice" % bind.get("dataset"))
                seen.add(bind.get("dataset"))
        if ok_id:
            if flt["id"] in found:
                e.add(ptr(path, "id"), "duplicate", "filter id %r is used twice" % flt["id"])
            elif ok_type:
                found[flt["id"]] = kind
    return found


def _filter_kind(e, path, flt, kind):
    """What each filter type needs so that ONE picker can serve every bound dataset."""
    if kind == "relation":
        if "model" in flt:
            e.string(ptr(path, "model"), flt["model"], 64, re.compile(C.MODEL_PATTERN),
                     "the model whose records are offered, like 'res.country'")
        else:
            e.add(ptr(path, "model"), "required", "a relation filter needs the model whose records it offers")
    elif "model" in flt:
        e.add(ptr(path, "model"), "not_allowed", "only a relation filter has a model")
    if kind == "selection":
        if "values" not in flt:
            e.add(ptr(path, "values"), "required", "a selection filter lists the values it offers")
        elif e.array(ptr(path, "values"), flt["values"], 1, 100):
            seen = set()
            for i, v in enumerate(flt["values"]):
                if e.string(ptr(path, "values", i), v, 64):
                    if v in seen:
                        e.add(ptr(path, "values", i), "duplicate", "value %r is listed twice" % v)
                    seen.add(v)
    elif "values" in flt:
        e.add(ptr(path, "values"), "not_allowed", "only a selection filter has values")
    if "default" in flt:
        if kind == "date":
            e.enum(ptr(path, "default"), flt["default"], C.DATE_PRESETS)
        elif kind == "selection":
            if e.string(ptr(path, "default"), flt["default"], 64) and isinstance(flt.get("values"), list) \
                    and flt["default"] not in flt["values"]:
                e.add(ptr(path, "default"), "reference", "%r is not one of the values" % flt["default"])
        else:
            e.add(ptr(path, "default"), "not_allowed", "a relation filter has no default")


# --------------------------------------------------------------------------------------------------- widgets
def _widgets(e, value, cols, filters, registry):
    """Returns the set of dataset references used by the widgets."""
    used = set()
    if not e.array("/widgets", value, 0, C.MAX_WIDGETS):
        return used
    seen, boxes = set(), []
    for i, widget in enumerate(value):
        path = ptr("/widgets", i)
        if not e.obj(path, widget, required=("id", "type", "x", "y", "w", "h", "dataset", "wells"),
                     optional=("title", "where", "order", "limit", "series_limit", "options", "ignore_filters",
                               "compare", "trend")):
            continue
        if e.string(ptr(path, "id"), widget.get("id"), 32, _ID, "an identifier like 'w1'"):
            if widget["id"] in seen:
                e.add(ptr(path, "id"), "duplicate", "widget id %r is used twice" % widget["id"])
            seen.add(widget["id"])
        kind = widget.get("type")
        vdef = registry.visuals.get(kind) if isinstance(kind, str) else None
        if vdef is None:
            e.add(ptr(path, "type"), "enum", "must be one of: %s" % ", ".join(sorted(registry.visuals)))
        if "title" in widget:
            e.string(ptr(path, "title"), widget["title"], 120)
        ok_box = all([
            e.integer(ptr(path, "x"), widget.get("x"), 0, cols - 1),
            e.integer(ptr(path, "y"), widget.get("y"), 0, 10000),
            e.integer(ptr(path, "w"), widget.get("w"), 1, cols),
            e.integer(ptr(path, "h"), widget.get("h"), 1, C.MAX_HEIGHT),
        ])
        if ok_box:
            if widget["x"] + widget["w"] > cols:
                e.add(ptr(path, "w"), "layout", "x + w (%d) is wider than the grid (%d columns)"
                      % (widget["x"] + widget["w"], cols))
            else:
                boxes.append((path, widget["id"], widget["x"], widget["y"], widget["w"], widget["h"]))
        dtype = dataset_ref(e, ptr(path, "dataset"), widget.get("dataset"), registry)
        if dtype is not None:
            used.add(widget["dataset"])
        if "where" in widget:
            if dtype is not None and not dtype["where"]:
                e.add(ptr(path, "where"), "not_allowed", "a %s dataset has no 'where': use the page filters"
                      % widget["dataset"].split(":")[0])
            else:
                domain(e, ptr(path, "where"), widget["where"])
        if "ignore_filters" in widget:
            ign = widget["ignore_filters"]
            if e.array(ptr(path, "ignore_filters"), ign, 0, C.MAX_FILTERS):
                for j, fid in enumerate(ign):
                    if fid not in filters:
                        e.add(ptr(path, "ignore_filters", j), "reference", "unknown filter %r" % (fid,))
        if vdef is not None:
            _visual(e, path, widget, vdef)
            if "compare" in widget:
                _compare(e, ptr(path, "compare"), widget["compare"], vdef, widget)
            if "trend" in widget:
                _trend(e, ptr(path, "trend"), widget["trend"], vdef, widget["type"])
    _overlaps(e, boxes)
    return used


def _compare(e, path, value, vdef, widget):
    """``{"field": "date_order", "period": "this_month", "against": "previous_period"}``.

    On a KPI (``compare`` = "value"): the same number for the previous period. On a line or area chart (``compare`` =
    "series"): the previous period drawn over the chart, each point against the same position in the previous period; the
    axis must be that date field, with one series (a legend or several values would not say what is compared with what).
    The period is the one of a page date filter bound to the same field, if there is one."""
    kind = widget["type"]
    if not vdef.get("compare"):
        e.add(path, "not_allowed", "a %s cannot be compared with a previous period" % kind)
        return
    if not e.obj(path, value, required=("field",), optional=("period", "against")):
        return
    e.string(ptr(path, "field"), value.get("field"), 64, _FIELD, "a date field")
    if "period" in value and e.enum(ptr(path, "period"), value["period"], C.DATE_PRESETS) and value["period"] == "all":
        e.add(ptr(path, "period"), "enum", "there is nothing to compare 'all' with")
    if "against" in value:
        e.enum(ptr(path, "against"), value["against"], C.COMPARE_AGAINST)
    if vdef["compare"] == "series" and isinstance(widget.get("wells"), dict):
        wells = widget["wells"]
        axis = wells.get("axis")
        if isinstance(axis, dict) and axis.get("field") != value.get("field"):
            e.add(ptr(path, "field"), "constraint", "the comparison is drawn over the axis: it must be the axis field (%s)"
                  % axis.get("field"))
        if wells.get("legend"):
            e.add(ptr(path, "field"), "constraint", "a chart with a legend cannot be compared with a previous period")
        values = wells.get("values")
        if isinstance(values, list) and len(values) > 1:
            e.add(ptr(path, "field"), "constraint", "compare one measure at a time (this chart has %d)" % len(values))


def _trend(e, path, value, vdef, kind):
    """``{"field": "date_order", "interval": "month", "points": 12}`` on a KPI: a small line of its last points."""
    if not vdef.get("trend"):
        e.add(path, "not_allowed", "a %s has no trend line" % kind)
        return
    if not e.obj(path, value, required=("field",), optional=("interval", "points")):
        return
    e.string(ptr(path, "field"), value.get("field"), 64, _FIELD, "a date field")
    if "interval" in value:
        e.enum(ptr(path, "interval"), value["interval"], C.TREND_INTERVALS)
    if "points" in value:
        e.integer(ptr(path, "points"), value["points"], C.TREND_POINTS_MIN, C.TREND_POINTS_MAX)


def _overlaps(e, boxes):
    for a in range(len(boxes)):
        for b in range(a + 1, len(boxes)):
            p1, id1, x1, y1, w1, h1 = boxes[a]
            p2, id2, x2, y2, w2, h2 = boxes[b]
            if x1 < x2 + w2 and x2 < x1 + w1 and y1 < y2 + h2 and y2 < y1 + h1:
                e.add(p2, "layout", "widget %r overlaps widget %r" % (id2, id1))


def _visual(e, path, widget, vdef):
    """Wells, order, limits and options of one widget, against its visual type definition."""
    facts = _wells(e, ptr(path, "wells"), widget.get("wells"), vdef, widget.get("options"))
    if "order" in widget:
        _order(e, ptr(path, "order"), widget["order"], facts, vdef["query"])
    for key in ("limit", "series_limit"):
        if key in widget:
            spec = vdef.get(key)
            if spec is None:
                e.add(ptr(path, key), "not_allowed", "a %s has no %r" % (widget["type"], key))
            else:
                e.integer(ptr(path, key), widget[key], 1, spec["max"])
    if "options" in widget:
        _options(e, ptr(path, "options"), widget["options"], vdef.get("options") or {})


# ----------------------------------------------------------------------------------------------------- wells
def _wells(e, path, wells, vdef, options=None):
    """Returns {"dimensions": [field...], "measures": [key...], "columns": [field...]} of the valid items."""
    facts = {"dimensions": [], "measures": [], "columns": []}
    if not e.obj(path, wells, optional=tuple(vdef["wells"])):
        return facts
    counts, raw = {}, {}
    for name, wdef in vdef["wells"].items():
        value, wpath = wells.get(name), ptr(path, name)
        counts[name] = 0
        raw[name] = value
        if value is None:
            if wdef["min"] >= 1:
                e.add(wpath, "required", "is required")
            continue
        if wdef["max"] == 1:
            items, paths = [value], [wpath]
        else:
            if not e.array(wpath, value, wdef["min"], wdef["max"]):
                continue
            items, paths = value, [ptr(wpath, j) for j in range(len(value))]
        counts[name] = len(items)
        for item, ipath in zip(items, paths):
            _item(e, ipath, item, wdef["accepts"], facts)
    for kind in ("dimensions", "measures", "columns"):
        dup = {x for x in facts[kind] if facts[kind].count(x) > 1}
        if dup:
            e.add(path, "duplicate", "%s used twice: %s" % (kind, ", ".join(sorted(dup))))
    for con in vdef.get("constraints") or []:
        if con["kind"] == "any_of" and not any(counts.get(w) for w in con["wells"]):
            e.add(path, "required", "at least one of these wells is needed: %s" % ", ".join(con["wells"]))
        elif con["kind"] == "max_if_present" and counts.get(con["if"]) and counts.get(con["well"], 0) > con["max"]:
            e.add(ptr(path, con["well"]), "constraint", "at most %d item(s) in %r when %r is used"
                  % (con["max"], con["well"], con["if"]))
        elif con["kind"] == "option_needs" and isinstance(options, dict) and options.get(con["option"]):
            ok = any((c.get("option") and options.get(c["option"])) or (c.get("well") and counts.get(c["well"]))
                     for c in con["any_of"])
            if not ok:
                e.add(ptr(path.rsplit("/wells", 1)[0], "options", con["option"]), "constraint",
                      "%r needs %s" % (con["option"], " or ".join(c.get("option") or "a %s" % c["well"]
                                                                  for c in con["any_of"])))
        elif con["kind"] == "option_less" and isinstance(options, dict):
            low, high = options.get(con["low"]), options.get(con["high"])
            numbers = all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (low, high))
            if numbers and low >= high:
                e.add(ptr(path.rsplit("/wells", 1)[0], "options", con["low"]), "constraint",
                      "%s (%s) must be lower than %s (%s)" % (con["low"], low, con["high"], high))
        elif con["kind"] == "option_excludes" and isinstance(options, dict) and options.get(con["option"]) is not None:
            for other in con["with"]:
                if options.get(other):
                    e.add(ptr(path.rsplit("/wells", 1)[0], "options", con["option"]), "constraint",
                          "%s cannot be used with %s" % (con["option"], other))
        elif con["kind"] == "option_aggs" and isinstance(options, dict) and options.get(con["option"]):
            items = raw.get(con["well"])
            for item in items if isinstance(items, list) else [items]:
                if isinstance(item, dict) and item.get("agg") not in con["aggs"] and "metric" not in item:
                    e.add(ptr(path, con["well"]), "constraint", "%r is only valid when the measure is %s (the "
                          "other aggregates cannot be added up)" % (con["option"], " or ".join(con["aggs"])))
    return facts


def _item(e, path, item, accepts, facts):
    if accepts == "dimension":
        if e.obj(path, item, required=("field",), optional=("interval", "label")):
            if e.string(ptr(path, "field"), item.get("field"), 330, _FIELD_PATH, "a field name or path"):
                facts["dimensions"].append(item["field"])
            if "interval" in item:
                e.enum(ptr(path, "interval"), item["interval"], C.INTERVALS)
            if "label" in item:
                e.string(ptr(path, "label"), item["label"], 60)
    elif accepts == "column":
        if e.obj(path, item, required=("field",), optional=("label",)):
            if e.string(ptr(path, "field"), item.get("field"), 330, _FIELD_PATH, "a field name or path"):
                facts["columns"].append(item["field"])
            if "label" in item:
                e.string(ptr(path, "label"), item["label"], 60)
    else:
        _measure(e, path, item, facts)


def _measure(e, path, item, facts):
    """``{"metric": "revenue"}`` or ``{"field": "amount_total", "agg": "sum", "label": "..."}``."""
    if not isinstance(item, dict):
        e.add(path, "type", "must be an object")
        return
    if "metric" in item:
        if e.obj(path, item, required=("metric",), optional=("label",)):
            if e.string(ptr(path, "metric"), item["metric"], 32, _ID, "a metric name"):
                facts["measures"].append(item["metric"])
            if "label" in item:
                e.string(ptr(path, "label"), item["label"], 60)
        return
    if not e.obj(path, item, required=("agg",), optional=("field", "label")):
        return
    ok = e.enum(ptr(path, "agg"), item.get("agg"), C.AGGS)
    if "field" in item:
        e.string(ptr(path, "field"), item["field"], 64, _FIELD, "a field name")
    elif ok and item["agg"] != "count":
        e.add(ptr(path, "field"), "required", "is required unless agg is 'count' (record count)")
    if "label" in item:
        e.string(ptr(path, "label"), item["label"], 60)
    if ok and ("field" in item or item["agg"] == "count"):
        facts["measures"].append(C.measure_key(item))


def _order(e, path, value, facts, query_kind):
    if not e.array(path, value, 0, C.MAX_ORDER):
        return
    for i, o in enumerate(value):
        p = ptr(path, i)
        if not e.obj(p, o, required=(), optional=("field", "measure", "dir")):
            continue
        if ("field" in o) == ("measure" in o):
            e.add(p, "required", "give exactly one of 'field' or 'measure'")
        elif "field" in o:
            known = facts["columns"] if query_kind == "records" else facts["dimensions"]
            if e.string(ptr(p, "field"), o["field"], 330) and o["field"] not in known:
                e.add(ptr(p, "field"), "reference", "%r is not used in the wells (%s)" % (
                    o["field"], ", ".join(known) or "-"))
        else:
            if query_kind == "records":
                e.add(ptr(p, "measure"), "not_allowed", "a table has no measures")
            elif e.string(ptr(p, "measure"), o["measure"], 80) and o["measure"] not in facts["measures"]:
                e.add(ptr(p, "measure"), "reference", "%r is not a measure of this widget (%s)" % (
                    o["measure"], ", ".join(facts["measures"]) or "-"))
        if "dir" in o:
            e.enum(ptr(p, "dir"), o["dir"], C.DIRECTIONS)


def _number(e, path, value, minimum=None, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        e.add(path, "type", "must be a number")
    elif minimum is not None and value < minimum or maximum is not None and value > maximum:
        e.add(path, "range", "must be between %s and %s" % (minimum, maximum))


def _options(e, path, value, allowed):
    if not e.obj(path, value, optional=tuple(allowed)):
        return
    for key, desc in allowed.items():
        if key not in value:
            continue
        p, v, kind = ptr(path, key), value[key], desc["kind"]
        if kind == "bool":
            e.boolean(p, v)
        elif kind == "enum":
            e.enum(p, v, desc["values"])
        elif kind == "int":
            e.integer(p, v, desc.get("min"), desc.get("max"))
        elif kind == "number":
            _number(e, p, v, desc.get("min"), desc.get("max"))
        elif kind == "text":
            e.string(p, v, desc.get("max", 12))
        elif kind == "colors" and e.array(p, v, 1, desc.get("max", 12)):
            for i, c in enumerate(v):
                e.string(ptr(p, i), c, 7, _COLOR, "a colour like #2997ff")


# ----------------------------------------------------------------------------------------------------- domain
def domain(e, path, value, depth=1, counter=None):
    """An Odoo domain as JSON in prefix notation: ["&", ["state", "=", "sale"], ["amount", ">", 10]].
    Values are plain, or ``{"ctx": "uid"}`` (uid, company_id, company_ids, today, now). No expressions."""
    counter = counter if counter is not None else [0]
    if not e.array(path, value, 0):
        return
    if depth > C.MAX_DOMAIN_DEPTH:
        e.add(path, "too_deep", "sub-domains are nested more than %d levels" % C.MAX_DOMAIN_DEPTH)
        return
    pos = 0
    while pos < len(value):
        pos = _expression(e, path, value, pos, depth, counter)
        if pos < 0:
            return


def _expression(e, path, items, pos, depth, counter):
    """Check one prefix-notation expression starting at items[pos]; returns the next position (-1 on error)."""
    if pos >= len(items):
        e.add(path, "domain", "the logical operators are missing an operand")
        return -1
    token = items[pos]
    p = ptr(path, pos)
    if isinstance(token, str):
        if token not in C.DOMAIN_LOGIC:
            e.add(p, "domain", "%r is not one of & | !" % token)
            return -1
        pos += 1
        for _ in range(1 if token == "!" else 2):
            pos = _expression(e, path, items, pos, depth, counter)
            if pos < 0:
                return -1
        return pos
    if not isinstance(token, list) or len(token) != 3:
        e.add(p, "domain", "a condition must be [field, operator, value]")
        return -1
    counter[0] += 1
    if counter[0] > C.MAX_DOMAIN_LEAVES:
        e.add(p, "too_many", "a domain can have at most %d conditions" % C.MAX_DOMAIN_LEAVES)
        return -1
    field, op, val = token
    if not e.string(ptr(p, 0), field, 330, _FIELD_PATH, "a field name or path like 'partner_id.country_id'"):
        return -1
    if not e.enum(ptr(p, 1), op, C.DOMAIN_OPS):
        return -1
    if op in C.SUBDOMAIN_OPS:
        domain(e, ptr(p, 2), val, depth + 1, counter)
    elif op in C.LIST_OPS:
        if _is_ctx(val, C.CTX_LIST):
            pass
        elif not isinstance(val, list) or not all(_scalar(v) for v in val):
            e.add(ptr(p, 2), "type", "must be an array of plain values (or {\"ctx\": \"company_ids\"}) for %r" % op)
    elif not _scalar(val):
        e.add(ptr(p, 2), "type", "must be a plain value, null or {\"ctx\": one of %s} for %r" % (
            ", ".join(C.CTX_SCALAR), op))
    return pos + 1


def _is_ctx(v, allowed):
    return isinstance(v, dict) and set(v) == {"ctx"} and v["ctx"] in allowed


def _scalar(v):
    return v is None or isinstance(v, (str, int, float, bool)) or _is_ctx(v, C.CTX_SCALAR)
