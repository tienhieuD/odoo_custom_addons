# -*- coding: utf-8 -*-
"""The registry: which visual types (bar, pie, ...) and dataset types (orm, sql, ...) exist, as plain data.

Pure Python. The Odoo side (models/dwo_dashboard_spec.py) builds it from two hook methods that plugins extend with
``_inherit`` + ``super()``, so a plugin installed in one database never leaks into another one.

Visual type definition:
    {"label": "Bar chart",
     "query": "grouped" | "records",        # grouped = _read_group engine (charts, pivot, kpi), records = search_read
     "wells": {"axis": {"accepts": "dimension", "min": 1, "max": 1}, ...},   # accepts: dimension|measure|column
     "options": {"stacked": {"kind": "bool"}, "legend": {"kind": "enum", "values": [...]},
                 "decimals": {"kind": "int", "min": 0, "max": 6}, "colors": {"kind": "colors", "max": 12}},
     "limit": {"default": 100, "max": 500} | None,         # grouped: top-N groups of the first dimension well
     "series_limit": {"default": 10, "max": 20} | None,    # grouped: groups of the second dimension well
     "constraints": [{"kind": "any_of", "wells": ["rows", "columns"]},
                     {"kind": "max_if_present", "well": "values", "if": "legend", "max": 1}]}
A well whose ``max`` is 1 holds one object, any other holds an array. Most new charts are just a new entry with a
JS renderer: they reuse the "grouped" engine.

Dataset type definition:
    {"label": "...", "name_pattern": "<regex of the part after the prefix>", "where": True|False,
     "definition": {"required": [...], "optional": [...]}}   # top-level keys of a dwo-dataset/1 document
"""
import copy
import re

from . import constants as C


def bool_option():
    return {"kind": "bool"}


def enum_option(values):
    return {"kind": "enum", "values": list(values)}


def int_option(minimum, maximum):
    return {"kind": "int", "min": minimum, "max": maximum}


def colors_option(maximum=12):
    return {"kind": "colors", "max": maximum}


def _well(accepts, minimum, maximum):
    return {"accepts": accepts, "min": minimum, "max": maximum}


def core_visual_types():
    fmt = {"format": enum_option(C.FORMATS), "decimals": int_option(0, 6)}
    chart = dict(fmt, colors=colors_option(), legend=enum_option(C.LEGENDS))
    series = [{"kind": "max_if_present", "well": "values", "if": "legend", "max": 1}]
    series_limit = {"default": 10, "max": 20}

    def axis_chart(label, **extra):
        return {
            "label": label, "query": "grouped",
            "wells": {"axis": _well("dimension", 1, 1), "legend": _well("dimension", 0, 1),
                      "values": _well("measure", 1, 5)},
            "options": dict(chart, **extra), "limit": {"default": 100, "max": 500},
            "series_limit": dict(series_limit), "constraints": copy.deepcopy(series)}

    def slice_chart(label):
        return {
            "label": label, "query": "grouped",
            "wells": {"category": _well("dimension", 1, 1), "value": _well("measure", 1, 1)},
            "options": dict(chart), "limit": {"default": 20, "max": 100}, "series_limit": None, "constraints": []}

    return {
        "kpi": {"label": "KPI", "query": "grouped", "wells": {"value": _well("measure", 1, 1)},
                "options": dict(fmt), "limit": None, "series_limit": None, "constraints": []},
        "table": {"label": "Table", "query": "records", "wells": {"columns": _well("column", 1, 20)},
                  "options": dict(fmt), "limit": {"default": 50, "max": 500}, "series_limit": None,
                  "constraints": []},
        "bar": axis_chart("Bar chart", stacked=bool_option(), horizontal=bool_option()),
        "line": axis_chart("Line chart", smooth=bool_option()),
        "area": axis_chart("Area chart", smooth=bool_option(), stacked=bool_option()),
        "pie": slice_chart("Pie chart"),
        "doughnut": slice_chart("Doughnut chart"),
        "pivot": {
            "label": "Pivot table", "query": "grouped",
            "wells": {"rows": _well("dimension", 0, 3), "columns": _well("dimension", 0, 2),
                      "values": _well("measure", 1, 5)},
            "options": dict(fmt, show_totals=bool_option()),
            "limit": {"default": 200, "max": 500}, "series_limit": {"default": 12, "max": 24},
            "constraints": [{"kind": "any_of", "wells": ["rows", "columns"]}]},
    }


def core_dataset_types():
    return {
        "orm": {"label": "Odoo model", "name_pattern": C.MODEL_PATTERN, "where": True,
                "definition": {"required": ["model"], "optional": ["fields"]}},
        "sql": {"label": "SQL dataset", "name_pattern": C.ID_PATTERN, "where": False,
                "definition": {"required": ["code", "sql"], "optional": []}},
    }


class Registry:
    """Immutable view of the visual and dataset types of one database. Raises ValueError if a plugin registered a
    malformed definition (so the mistake shows at once, with the type name)."""

    def __init__(self, visuals=None, datasets=None):
        self.visuals = copy.deepcopy(core_visual_types() if visuals is None else visuals)
        self.datasets = copy.deepcopy(core_dataset_types() if datasets is None else datasets)
        problems = self.problems()
        if problems:
            raise ValueError("invalid dashboard registry: " + "; ".join(problems))

    @classmethod
    def core(cls):
        return cls()

    # ------------------------------------------------------------------------------------------------- checking
    def problems(self):
        out = []
        ident = re.compile(C.ID_PATTERN)
        for name, vdef in self.visuals.items():
            tag = "visual %r" % name
            if not ident.match(name):
                out.append("%s: bad name" % tag)
                continue
            out += ["%s: %s" % (tag, p) for p in self._visual_problems(vdef, ident)]
        for name, ddef in self.datasets.items():
            tag = "dataset type %r" % name
            if not re.match(r"^[a-z][a-z0-9_]{0,15}$", name):
                out.append("%s: bad name" % tag)
                continue
            try:
                re.compile(ddef.get("name_pattern", ""))
            except re.error:
                out.append("%s: name_pattern is not a valid regex" % tag)
            if not isinstance(ddef.get("where"), bool):
                out.append("%s: 'where' must be true or false" % tag)
            definition = ddef.get("definition")
            if not isinstance(definition, dict) or not {"required", "optional"} <= set(definition):
                out.append("%s: 'definition' needs 'required' and 'optional'" % tag)
        return out

    @staticmethod
    def _visual_problems(vdef, ident):
        out = []
        if vdef.get("query") not in C.QUERY_KINDS:
            out.append("query must be one of %s" % ", ".join(C.QUERY_KINDS))
        wells = vdef.get("wells")
        if not isinstance(wells, dict) or not wells:
            return out + ["needs at least one well"]
        for wname, wdef in wells.items():
            if not ident.match(wname):
                out.append("well %r: bad name" % wname)
            if wdef.get("accepts") not in C.WELL_KINDS:
                out.append("well %r: accepts must be one of %s" % (wname, ", ".join(C.WELL_KINDS)))
            lo, hi = wdef.get("min"), wdef.get("max")
            if not (isinstance(lo, int) and isinstance(hi, int) and 0 <= lo <= hi and hi >= 1):
                out.append("well %r: needs integers 0 <= min <= max, max >= 1" % wname)
            if vdef.get("query") == "records" and wdef.get("accepts") != "column":
                out.append("well %r: a 'records' visual only has column wells" % wname)
            if vdef.get("query") == "grouped" and wdef.get("accepts") == "column":
                out.append("well %r: a 'grouped' visual has dimension and measure wells" % wname)
        if vdef.get("query") == "grouped" and not any(w.get("accepts") == "measure" for w in wells.values()):
            out.append("a 'grouped' visual needs a measure well")
        for oname, odef in (vdef.get("options") or {}).items():
            kind = odef.get("kind")
            if kind not in C.OPTION_KINDS:
                out.append("option %r: kind must be one of %s" % (oname, ", ".join(C.OPTION_KINDS)))
            elif kind == "enum" and not odef.get("values"):
                out.append("option %r: enum needs values" % oname)
        for key in ("limit", "series_limit"):
            spec = vdef.get(key)
            if spec is not None and not (isinstance(spec, dict) and 1 <= spec.get("default", 0) <= spec.get("max", 0)):
                out.append("%s needs {'default': n, 'max': m} with 1 <= n <= m, or None" % key)
        if vdef.get("series_limit") is not None and sum(
                1 for w in wells.values() if w.get("accepts") == "dimension") < 2:
            out.append("series_limit needs two dimension wells")
        for con in vdef.get("constraints") or []:
            kind = con.get("kind")
            if kind == "any_of":
                if not set(con.get("wells", ())) <= set(wells) or not con.get("wells"):
                    out.append("constraint any_of: unknown wells")
            elif kind == "max_if_present":
                if not {con.get("well"), con.get("if")} <= set(wells) or not isinstance(con.get("max"), int):
                    out.append("constraint max_if_present: unknown wells or max")
            else:
                out.append("unknown constraint kind %r" % kind)
        return out

    # ---------------------------------------------------------------------------------------------- helpers
    def dataset_type(self, ref):
        """The dataset type definition of a reference like ``orm:sale.order``, or None."""
        return self.datasets.get(ref.split(":", 1)[0]) if isinstance(ref, str) and ":" in ref else None
