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
        'A field of a dimension or a table column may be a path through many2one fields, up to 2 steps ("partner_id.country_id": the country of the customer).\n'
        'A dimension item is {"field":F} or, for a date field, {"field":F,"interval":"day|week|month|quarter|year"} (an interval is required for dates).\n'
        'A measure item is {"field":F,"agg":"sum|avg|min|max|count_distinct"}, {"agg":"count"} (count of records) or {"metric":NAME} (a metric listed under the data).\n'
        'A date filter is {"id":"period","type":"date","label":str,"default":"last_90_days","bind":[{"dataset":"orm:x","field":F}]}; '
        'a relation filter also has "model"; a selection filter has "values". Every dataset bound by a filter must be used by a widget.\n'
        'KPI extras: "compare":{"field":date,"period":"this_month","against":"previous_period"} and "trend":{"field":date,"interval":"month","points":12}.\n'
        'Domains are lists of [field, operator, value] with plain values only.\n'
        'Visual types:\n%(visuals)s' % {"schema": C.SCHEMA_ID, "max": C.GRID_COLS_MAX, "visuals": visual_lines(registry)})


def dataset_help(kind):
    """The rules of a dataset (blend or Odoo-model metrics), for the assistant that helps write one."""
    if kind == "blend":
        return (
            'A blend is {"schema":"%(schema)s","type":"blend","code":"lower_case_id","label":str,'
            '"sources":[{"name":"sales","dataset":"orm:sale.order","where":[domain]?}],'
            '"dimensions":[{"name":"month","label":str,"kind":"%(kinds)s","map":{"<source>":"<field of that model>"},"comodel":"res.partner"}],'
            '"metrics":[{"name":"revenue","source":"<source>","agg":"sum|avg|min|max|count_distinct|count","field":F,"where":[domain]?,'
            '"label":str,"format":"number|currency|percent"}]}.\n'
            '%(min)s to %(max)s sources, each an Odoo model "orm:<model>". Up to %(dims)s dimensions: the groupings the sources share '
            '(the month of a date, a customer, a state). Every dimension maps EVERY source to one field of that source; the fields mapped '
            'must be of the same kind (dates with dates, a many2one with a many2one to the same comodel; "comodel" only for kind many2one). '
            'A metric reads ONE source; "field" is required unless agg is "count" (count of records). '
            'Use only the models and fields listed under the data. Domains are lists of [field, operator, value] with plain values only.'
            % {"schema": C.DATASET_SCHEMA_ID, "kinds": "|".join(C.BLEND_DIM_KINDS), "min": 2, "max": C.MAX_BLEND_SOURCES,
               "dims": C.MAX_BLEND_DIMS})
    if kind == "orm":
        return (
            'Reply with {"metrics":[{"name":"won_revenue","label":str,"agg":"sum|avg|min|max|count_distinct|count","field":F,'
            '"where":[domain]?,"format":"number|currency|percent"}]}. A metric is a named measure of the model: name is lower case letters, '
            'digits and _, starting with a letter; "field" is a stored field of the model listed under the data, required unless agg is '
            '"count" (count of records); "where" is a domain of plain values that keeps only some records. Use only the listed fields.')
    return (
        'Reply with {"code":"lower_case_id","label":str,"query":"SELECT ..."}. The query is ONE PostgreSQL SELECT (no semicolon, no comment '
        'that hides code), reading only the tables and columns listed under the data. Give every output column a lower case name with AS '
        '(letters, digits, _). Odoo tables are named after the model with dots as underscores (sale.order is sale_order); a many2one is '
        'a column "<field>_id" holding the id of the other table. Parameters you may use: %(uid)s %(company_id)s %(company_ids)s %(lang)s '
        '%(today)s %(now)s; write a literal percent sign as %%. Dates and measures should be real columns (date, numeric), not text.')
