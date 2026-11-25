# -*- coding: utf-8 -*-
"""Semantic validation against the database: the dataset exists, its fields are real, stored where needed, of the right
type, readable by the author (model access AND field groups), and metrics exist.

It does NOT decide what a viewer may see. That is checked again, for the viewer, every time a widget runs (no sudo, so
access rights, record rules and company rules apply). Same error format as structure.py (JSON Pointer paths).

``resolve_dataset(ref)`` returns the definition (dwo-dataset/1) of a dataset or None. ORM datasets work without a
definition (implicit: every field, no metrics); other types need one. In Phase 0 tests pass fixtures; a later phase
passes a lookup of the stored definitions."""
import inspect

from odoo.exceptions import AccessError
from odoo.models import BaseModel

from . import constants as C
from .structure import ptr

NUMERIC_TYPES = ("integer", "float", "monetary")
DATE_TYPES = ("date", "datetime")
NOT_GROUPABLE = ("one2many", "binary", "html", "properties", "json", "serialized")
NOT_COUNTABLE = ("one2many", "many2many", "binary", "html", "properties", "json", "serialized")
NOT_DISPLAYABLE = ("binary", "html", "properties", "json", "serialized")
FILTER_FIELD_TYPES = {"date": DATE_TYPES, "relation": ("many2one", "many2many"), "selection": ("selection",)}
SQL_FILTER_TYPES = {"date": C.SQL_DATE_TYPES, "relation": ("integer",), "selection": ("text",)}


def groupable(env, field):
    """Can ``_read_group`` group by this field? Asks Odoo itself (it tries the group-by), so related and other
    non-stored fields that Odoo can group are accepted and the rest rejected; falls back to ``store``."""
    if field.type in NOT_GROUPABLE:
        return False
    ask = getattr(field, "_description_groupable", None)
    return bool(ask(env)) if ask else bool(field.store)


def aggregable(env, field):
    ask = getattr(field, "_description_aggregator", None)
    return bool(field.store or (ask and ask(env)))


def supports_groupby_path():
    """Odoo 19 follows many2one paths in ``_read_group`` group-bys (``partner_id.country_id``); 17 and 18 do not."""
    return "alias" in inspect.signature(BaseModel._read_group_groupby).parameters


def validate_semantics(env, spec, registry, resolve_dataset=None, check_access=True, checkers=None):
    """Assumes validate_structure found no error.

    ``check_access``: the author must be allowed to read each model and field and to use each dataset. Unless the author
    is a system administrator, "does not exist" and "you cannot read it" are reported identically, so nobody learns what
    is installed or the shape of what they cannot read. ``checkers``: {dataset type: callable(ref, widget_path, widget,
    definition) -> [errors]} for the dataset types added by plugins (core types are checked here); a plugin type without
    a checker is refused, never skipped."""
    return _Check(env, registry, resolve_dataset or (lambda ref: None), check_access, checkers or {}).page(spec)


def validate_dataset_semantics(env, defn, registry, check_access=True):
    """Assumes validate_dataset_structure found no error. SQL datasets have nothing to check in the database here:
    their query is only run (read-only, with a timeout) by the SQL phase."""
    chk = _Check(env, registry, lambda ref: None, check_access)
    if defn.get("type") == "orm":
        chk.orm_definition(defn)
    return chk.errors


class _Check:
    def __init__(self, env, registry, resolve, check_access, checkers=None):
        self.env, self.registry, self.resolve, self.check_access = env, registry, resolve, check_access
        self.checkers = checkers or {}
        # an author who is not a system administrator must not be able to tell "missing" from "forbidden"
        self.opaque = bool(check_access and not env.is_system())
        self.errors = []
        self.path_ok = supports_groupby_path()

    def add(self, path, code, message):
        self.errors.append({"path": path, "code": code, "message": message})

    # ------------------------------------------------------------------------------------------------- page
    def page(self, spec):
        used = {}  # dataset ref -> usable (True/False)
        for i, widget in enumerate(spec.get("widgets", [])):
            path = ptr("/widgets", i)
            ref = widget["dataset"]
            if ref not in used:
                used[ref] = self.dataset_ok(ref, ptr(path, "dataset"))
            if used[ref]:
                self.widget(path, widget, ref)
        for i, flt in enumerate(spec.get("filters", [])):
            self.filter(ptr("/filters", i), flt, used)
        return self.errors

    def dataset_ok(self, ref, path):
        """Does the dataset exist, and may the author use it?"""
        prefix, name = ref.split(":", 1)
        if prefix == "orm":
            return self.model(path, name) is not None
        defn = self.resolve(ref)
        if defn is None:
            return self.unavailable(path, "dataset", "no dataset %r" % ref)
        if prefix == "sql":
            groups = defn["sql"]["groups"]
            if self.check_access and not self.in_groups(groups):
                return self.unavailable(path, "access", "no dataset %r" % ref, hidden=True)
            return True
        if prefix not in self.checkers:
            self.add(path, "unchecked", "dataset type %r has no semantic checker installed" % prefix)
            return False
        return True

    def unavailable(self, path, code, detail, hidden=False):
        """Report a missing or forbidden thing; an opaque author gets one message for both."""
        if self.opaque:
            self.add(path, "access", "this dataset is not available to you")
        else:
            self.add(path, code, detail if not hidden else "you are not in any group allowed to use %s" % detail)
        return False

    def in_groups(self, groups):
        """Is the author in at least one of the groups (system administrators always are)?"""
        if self.env.su or self.env.is_system():
            return True
        for xmlid in groups:
            try:
                if self.env.user._has_group(xmlid):
                    return True
            except ValueError:  # group not installed here
                continue
        return False

    def model(self, path, name):
        if name not in self.env:
            self.unavailable(path, "model", "model %r does not exist (or its module is not installed)" % name)
            return None
        if self.check_access and not self.env[name].has_access("read"):
            self.unavailable(path, "access", "you cannot read model %r" % name)
            return None
        return self.env[name]

    def widget(self, path, widget, ref):
        prefix, name = ref.split(":", 1)
        vdef = self.registry.visuals[widget["type"]]
        defn = self.resolve(ref)
        if prefix == "orm":
            model = self.env[name]
            ctx = _Orm(self, model, defn)
            if "where" in widget:
                self.domain(ptr(path, "where"), widget["where"], model)
        elif prefix == "sql":
            ctx = _Sql(self, defn)
        else:
            self.errors.extend(self.checkers[prefix](ref, path, widget, defn))
            return
        for wname, wdef in vdef["wells"].items():
            value = widget["wells"].get(wname)
            if value is None:
                continue
            items = [value] if wdef["max"] == 1 else value
            for j, item in enumerate(items):
                ipath = ptr(path, "wells", wname) if wdef["max"] == 1 else ptr(path, "wells", wname, j)
                if wdef["accepts"] == "dimension":
                    ctx.dimension(ipath, item, vdef["query"])
                elif wdef["accepts"] == "column":
                    ctx.column(ipath, item)
                else:
                    ctx.measure(ipath, item)

    # --------------------------------------------------------------------------------------------- field access
    def field_readable(self, path, model, field, what):
        """Model-level and field-level (``groups=``) read access of the author."""
        if not self.check_access:
            return True
        try:
            model._check_field_access(field, "read")
        except AccessError:
            self.add(path, "access", ("%s: this field is not available to you" % what) if self.opaque else
                     "%s: you cannot read field %s.%s" % (what, model._name, field.name))
            return False
        return True

    def follow(self, path, model, dotted, what, last_stored=True, many2one_only=True):
        """Follow ``a.b.c`` through relations; returns (model of the last field, last field) or None."""
        parts = dotted.split(".")
        for n, part in enumerate(parts):
            field = model._fields.get(part)
            if field is None:
                if self.opaque:
                    self.add(path, "access", "%s: this field is not available to you" % what)
                else:
                    self.add(path, "field", "%s: model %s has no field %r" % (what, model._name, part))
                return None
            if not self.field_readable(path, model, field, what):
                return None
            if n < len(parts) - 1:
                allowed = ("many2one",) if many2one_only else ("many2one", "one2many", "many2many")
                if field.type not in allowed:
                    self.add(path, "type", "%s: %r must be a %s to continue with %r" % (
                        what, part, "many2one" if many2one_only else "relation", parts[n + 1]))
                    return None
                model = self.env[field.comodel_name]
                if self.check_access and not model.has_access("read"):
                    self.add(path, "access", ("%s: this field is not available to you" % what) if self.opaque else
                             "%s: you cannot read model %r" % (what, model._name))
                    return None
        return model, field

    def domain(self, path, domain, model):
        for i, token in enumerate(domain):
            if not isinstance(token, list):
                continue
            p = ptr(path, i)
            found = self.follow(ptr(p, 0), model, token[0], "condition", many2one_only=False)
            if found is None:
                continue
            field = found[1]
            if not (field.store or field.search):
                self.add(ptr(p, 0), "type", "%s cannot be searched" % token[0])
            if token[1] in C.SUBDOMAIN_OPS:
                if field.type in ("one2many", "many2many", "many2one"):
                    self.domain(ptr(p, 2), token[2], self.env[field.comodel_name])
                else:
                    self.add(ptr(p, 1), "type", "%r needs a relation field" % token[1])

    # ---------------------------------------------------------------------------------------------- filters
    def filter(self, path, flt, used):
        """One picker serves every bound dataset: relation binds must all point to the filter's model, selection binds
        must offer every declared value. A SQL integer column has no comodel: the filter's ``model`` is trusted."""
        if flt["type"] == "relation":
            self.model(ptr(path, "model"), flt["model"])  # the author must be able to read the offered model
        for j, bind in enumerate(flt["bind"]):
            ref, p = bind["dataset"], ptr(path, "bind", j)
            if not used.get(ref):
                continue
            prefix, name = ref.split(":", 1)
            if prefix == "orm":
                self.orm_bind(p, flt, self.env[name], bind["field"])
            elif prefix == "sql":
                col = {c["name"]: c for c in self.resolve(ref)["sql"]["columns"]}.get(bind["field"])
                if col is None:
                    self.add(ptr(p, "field"), "field", "dataset %s has no column %r" % (name, bind["field"]))
                elif col["type"] not in SQL_FILTER_TYPES[flt["type"]]:
                    self.add(ptr(p, "field"), "type", "a %s filter needs a %s column; %s is %s" % (
                        flt["type"], "/".join(SQL_FILTER_TYPES[flt["type"]]), bind["field"], col["type"]))

    def orm_bind(self, p, flt, model, fname):
        fpath = ptr(p, "field")
        field = model._fields.get(fname)
        if field is None:
            if self.opaque:
                self.add(fpath, "access", "filter: this field is not available to you")
            else:
                self.add(fpath, "field", "model %s has no field %r" % (model._name, fname))
            return
        if not self.field_readable(fpath, model, field, "filter"):
            return
        if field.type not in FILTER_FIELD_TYPES[flt["type"]] or not (field.store or field.search):
            self.add(fpath, "type", "a %s filter needs a %s field; %s.%s is %s" % (
                flt["type"], "/".join(FILTER_FIELD_TYPES[flt["type"]]), model._name, fname, field.type))
        elif flt["type"] == "relation" and field.comodel_name != flt["model"]:
            self.add(fpath, "type", "%s.%s points to %s, but the filter offers %s records" % (
                model._name, fname, field.comodel_name, flt["model"]))
        elif flt["type"] == "selection":
            keys = {k for k, _label in field._description_selection(self.env)}
            missing = [v for v in flt["values"] if v not in keys]
            if missing:
                self.add(fpath, "type", "%s.%s has no value %s" % (model._name, fname, ", ".join(map(repr, missing))))

    # ------------------------------------------------------------------------------------- orm definitions
    def orm_definition(self, defn):
        model = self.model("/model", defn["model"])
        if model is None:
            return
        for name in defn.get("fields", {}):
            if name not in model._fields:
                self.add(ptr("/fields", name), "field", "model %s has no field %r" % (model._name, name))
        for i, m in enumerate(defn.get("metrics", [])):
            _Orm(self, model, defn).metric_def(ptr("/metrics", i), m)


class _Orm:
    """Checks of the items of a widget on an ORM dataset (a model, optionally with a definition)."""

    def __init__(self, chk, model, defn):
        self.chk, self.model = chk, model
        self.defn = defn or {}
        self.metrics = {m["name"]: m for m in self.defn.get("metrics", [])}
        self.hidden = {n for n, o in self.defn.get("fields", {}).items() if o.get("hidden")}

    def _hidden(self, path, dotted):
        first = dotted.split(".")[0]
        if first in self.hidden:
            self.chk.add(path, "hidden", "field %r is hidden by the dataset definition" % first)
            return True
        return False

    def dimension(self, path, item, query_kind):
        field_path = ptr(path, "field")
        if self._hidden(field_path, item["field"]):
            return
        dotted = item["field"]
        if "." in dotted and not self.chk.path_ok:
            self.chk.add(field_path, "capability", "grouping through a relation (%s) needs Odoo 19 or later" % dotted)
            return
        found = self.chk.follow(field_path, self.model, dotted, "group by")
        if found is None:
            return
        field = found[1]
        if not groupable(self.chk.env, field):
            self.chk.add(field_path, "type", "Odoo cannot group by %s (%s%s)" % (
                dotted, field.type, "" if field.store else ", not stored"))
        elif field.type in DATE_TYPES and "interval" not in item:
            self.chk.add(ptr(path, "interval"), "required", "a %s field needs an interval (%s)" % (
                field.type, ", ".join(C.INTERVALS)))
        elif field.type not in DATE_TYPES and "interval" in item:
            self.chk.add(ptr(path, "interval"), "type", "an interval only applies to date and datetime fields")

    def column(self, path, item):
        field_path = ptr(path, "field")
        if self._hidden(field_path, item["field"]):
            return
        found = self.chk.follow(field_path, self.model, item["field"], "column")
        if found is not None and found[1].type in NOT_DISPLAYABLE:
            self.chk.add(field_path, "type", "%s fields cannot be shown in a table" % found[1].type)

    def measure(self, path, item):
        if "metric" in item:
            m = self.metrics.get(item["metric"])
            if m is None:
                self.chk.add(ptr(path, "metric"), "metric", "dataset has no metric %r" % item["metric"])
            return  # the metric itself is checked with its definition
        self.measure_def(path, item)

    def measure_def(self, path, item):
        if "field" not in item:
            return
        fpath = ptr(path, "field")
        if self._hidden(fpath, item["field"]):
            return
        found = self.chk.follow(fpath, self.model, item["field"], "measure")
        if found is None:
            return
        field = found[1]
        if not aggregable(self.chk.env, field):
            self.chk.add(fpath, "type", "%s is not stored: it cannot be aggregated" % item["field"])
        elif item["agg"] in C.NUMERIC_AGGS and field.type not in NUMERIC_TYPES:
            self.chk.add(ptr(path, "agg"), "type", "%r needs a number field; %s is %s" % (
                item["agg"], item["field"], field.type))
        elif item["agg"] in ("count", "count_distinct") and field.type in NOT_COUNTABLE:
            self.chk.add(fpath, "type", "cannot count %s fields" % field.type)

    def metric_def(self, path, metric):
        self.measure_def(path, metric)
        if "where" in metric:
            self.chk.domain(ptr(path, "where"), metric["where"], self.model)


class _Sql:
    """Checks of the items of a widget on a SQL dataset: its columns and roles are hard rules."""

    def __init__(self, chk, defn):
        self.chk = chk
        self.columns = {c["name"]: c for c in defn["sql"]["columns"]}
        self.metrics = {m["name"]: m for m in defn.get("metrics", [])}

    def _column(self, path, name, what):
        col = self.columns.get(name)
        if col is None:
            self.chk.add(ptr(path, "field"), "field", "%s: the dataset has no column %r" % (what, name))
        return col

    def dimension(self, path, item, query_kind):
        col = self._column(path, item["field"], "group by")
        if col is None:
            return
        if col["role"] != "dimension":
            self.chk.add(ptr(path, "field"), "role", "%s is a measure column: it cannot be a dimension" % item["field"])
        elif col["type"] in C.SQL_DATE_TYPES and "interval" not in item:
            self.chk.add(ptr(path, "interval"), "required", "a %s column needs an interval" % col["type"])
        elif col["type"] not in C.SQL_DATE_TYPES and "interval" in item:
            self.chk.add(ptr(path, "interval"), "type", "an interval only applies to date and datetime columns")

    def column(self, path, item):
        self._column(path, item["field"], "column")

    def measure(self, path, item):
        if "metric" in item:
            if item["metric"] not in self.metrics:
                self.chk.add(ptr(path, "metric"), "metric", "dataset has no metric %r" % item["metric"])
            return
        if "field" not in item:
            return
        col = self._column(path, item["field"], "measure")
        if col is None:
            return
        if item["agg"] in C.NUMERIC_AGGS and col["role"] != "measure":
            self.chk.add(ptr(path, "agg"), "role", "%r needs a measure column; %s is a %s" % (
                item["agg"], item["field"], col["role"]))
