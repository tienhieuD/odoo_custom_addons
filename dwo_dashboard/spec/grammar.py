# -*- coding: utf-8 -*-
"""A compact description of the page format, written for a language model: generated from the registry, so a plugin's
types are in it as soon as they are installed. The JSON Schema says the same thing, but it is several times longer."""
from . import constants as C


def _option(name, o):
    kind = o["kind"]
    if kind == "enum":
        return "%s=%s" % (name, "|".join(o["values"]))
    if kind in ("int", "number"):
        return "%s(%s)" % (name, kind)
    return name  # bool, text, colors


def visual_lines(registry):
    lines = []
    for name, v in sorted(registry.visuals.items()):
        wells = ", ".join("%s:%s%s" % (w, d["accepts"], "" if d["max"] == 1 and d["min"] == 1 else
                                       "[%s..%s]" % (d["min"], d["max"])) for w, d in v["wells"].items())
        opts = ", ".join(_option(k, o) for k, o in sorted((v.get("options") or {}).items()))
        extra = []
        if v.get("compare"):
            extra.append("compare")
        if v.get("trend"):
            extra.append("trend")
        if v.get("limit"):
            extra.append("limit<=%s" % v["limit"]["max"])
        lines.append("- %s: wells {%s}; options {%s}%s" % (name, wells, opts, "; " + ", ".join(extra) if extra else ""))
    return "\n".join(lines)


def format_help(registry):
    """The rules of a page, in the order a model needs them."""
    return (
        'A page is {"schema":"%(schema)s","title":str,"grid":{"cols":12},"filters":[...],"widgets":[...]}.\n'
        'A widget is {"id":"w1","type":T,"title":str,"icon":"fa-...","x":0,"y":0,"w":4,"h":3,"dataset":"orm:model.name",'
        '"wells":{...},"where":[domain],"order":[{"field":F,"dir":"asc"}|{"measure":M,"dir":"desc"}],"limit":n,"options":{...}}.\n'
        'Widgets sit on a grid: x+w<=cols (cols 6..%(max)s, 12 by default), no two overlap, a KPI is about w3 h3, a chart w6 h4, a table w12 h5.\n'
        'id is lower case letters, digits and _, unique, and an existing id keeps its meaning (do not reuse it for something else).\n'
        'A dimension item is {"field":F} or, for a date field, {"field":F,"interval":"day|week|month|quarter|year"} (an interval is required for dates).\n'
        'A measure item is {"field":F,"agg":"sum|avg|min|max|count_distinct"}, {"agg":"count"} (count of records) or {"metric":NAME} (a metric listed under the data).\n'
        'A date filter is {"id":"period","type":"date","label":str,"default":"last_90_days","bind":[{"dataset":"orm:x","field":F}]}; '
        'a relation filter also has "model"; a selection filter has "values". Every dataset bound by a filter must be used by a widget.\n'
        'KPI extras: "compare":{"field":date,"period":"this_month","against":"previous_period"} and "trend":{"field":date,"interval":"month","points":12}.\n'
        'Domains are lists of [field, operator, value] with plain values only.\n'
        'Visual types:\n%(visuals)s' % {"schema": C.SCHEMA_ID, "max": C.GRID_COLS_MAX, "visuals": visual_lines(registry)})
