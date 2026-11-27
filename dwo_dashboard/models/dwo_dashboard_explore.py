# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.exceptions import AccessError

from ..spec import constants as C

HIDDEN_PREFIXES = ("ir.", "base.", "bus.", "mail.", "web.", "iap.", "report.", "res.config", "res.users.", "auth.",
                   "sms.", "payment.", "portal.", "digest.", "phone.", "base_import.", "ir_")
NOT_GROUPABLE = ("one2many", "binary", "html", "properties", "json", "serialized")
NOT_COLUMN = ("binary", "html", "properties", "json", "serialized")
NUMERIC = ("integer", "float", "monetary")
DATE = ("date", "datetime")
ATTRIBUTES = ["string", "type", "relation", "selection", "store", "groupable", "aggregator"]
MAX_OPTIONS = 50
MAX_PATH = 2  # relations followed in one path: partner_id.country_id, partner_id.parent_id.country_id


class DwoDashboardExplore(models.AbstractModel):
    """What the Explore screen (and, later, an AI assistant) may know: the datasets and fields the caller can read.
    Everything comes from the caller's own environment, so a field restricted by groups, or a model the caller cannot
    read, is simply absent."""
    _name = "dwo.dashboard.explore"
    _description = "Dashboard explore helpers"

    @api.model
    def list_datasets(self):
        """The models the caller can read (technical models are hidden, except for system administrators)."""
        show_all = self.env.is_system() or self.env.user.has_group("dwo_dashboard.group_dwo_dashboard_manager")
        rows = []
        for rec in self.env["ir.model"].sudo().search([("transient", "=", False)]):
            name = rec.model
            if name not in self.env or (not show_all and name.startswith(HIDDEN_PREFIXES)):
                continue
            # SQL-view report models (_auto = False: sale.report, account.invoice.report...) are the way to combine tables
            if self.env[name]._abstract or not self.env[name].has_access("read"):
                continue
            rows.append({"ref": "orm:" + name, "model": name, "label": rec.name or name})
        for dataset in self.env["dwo.dataset"].sudo().search([("kind", "=", "blend")]):
            if self._blend_readable(dataset._definition()):
                rows.append({"ref": dataset.ref, "model": dataset.code, "label": "%s (model)" % dataset.label})
        if self.env["dwo.dashboard.spec"]._sql_enabled():
            for dataset in self.env["dwo.dataset"].sudo().search([("kind", "=", "sql")]):
                if self._sql_allowed(dataset._definition()):
                    rows.append({"ref": dataset.ref, "model": dataset.code, "label": "%s (SQL)" % dataset.label})
        return sorted(rows, key=lambda r: r["label"].lower())

    @api.model
    def _sql_allowed(self, defn):
        """May the caller use this SQL dataset: are they in one of the groups it lists (administrators always are)."""
        groups = defn.get("sql", {}).get("groups", []) if isinstance(defn, dict) else []
        if self.env.is_system():
            return True
        for xmlid in groups:
            try:
                if self.env.user.has_group(xmlid):
                    return True
            except ValueError:
                continue
        return False

    @api.model
    def _describe_sql(self, ref):
        """A SQL dataset as Explore sees it: its columns (never its query)."""
        defn = self.env["dwo.dashboard.spec"]._dwo_resolve_dataset(ref)
        if not defn or not self._sql_allowed(defn) or not self.env["dwo.dashboard.spec"]._sql_enabled():
            raise AccessError(self.env._("This dataset is not available to you."))
        kinds = {"text": "char", "integer": "integer", "numeric": "float", "boolean": "boolean", "date": "date", "datetime": "datetime"}
        fields_ = []
        for c in defn["sql"]["columns"]:
            measure = c["role"] == "measure"
            fields_.append({"name": c["name"], "label": c.get("label") or c["name"], "type": kinds[c["type"]], "relation": None,
                            "selection": None, "dimension": not measure, "measure": measure,
                            "aggs": ["sum", "avg", "min", "max"] if measure else [], "column": True, "expandable": False,
                            "intervals": list(C.INTERVALS) if c["type"] in C.SQL_DATE_TYPES else []})
        metrics = [{"name": m["name"], "label": m.get("label") or m["name"], "agg": m["agg"], "field": m.get("field"),
                    "format": m.get("format"), "conditional": False} for m in defn.get("metrics", [])]
        return {"ref": ref, "model": defn["code"], "label": defn.get("label") or defn["code"], "kind": "sql", "metrics": metrics,
                "fields": sorted(fields_, key=lambda x: x["label"].lower())}

    @api.model
    def _blend_readable(self, defn):
        """A blend is offered to whoever can read every one of its models: it cannot run for anybody else."""
        sources = defn.get("sources") if isinstance(defn, dict) else None
        return bool(sources) and all(isinstance(s, dict) and str(s.get("dataset", "")).startswith("orm:") and
                                     s["dataset"][4:] in self.env and self.env[s["dataset"][4:]].has_access("read")
                                     for s in sources)

    @api.model
    def describe_dataset(self, ref):
        """Fields of an ORM dataset with what each can be: dimension, measure, column. ``fields_get`` already drops what the
        caller cannot read and gives translated labels."""
        prefix, _sep, name = (ref or "").partition(":")
        if prefix == "blend":
            return self._describe_blend(ref)
        if prefix == "sql":
            return self._describe_sql(ref)
        if prefix != "orm" or name not in self.env or not self.env[name].has_access("read"):
            raise AccessError(self.env._("This dataset is not available to you."))
        model = self.env[name]
        out = self._describe_fields(model, expandable_depth=MAX_PATH)
        readable = set(model.fields_get(attributes=["type"]))
        defn = self.env["dwo.dashboard.spec"]._dwo_resolve_dataset(ref) or {}
        metrics = [{"name": m["name"], "label": m.get("label") or m["name"], "agg": m["agg"], "field": m.get("field"),
                    "format": m.get("format"), "conditional": bool(m.get("where"))}
                   for m in defn.get("metrics", []) if not m.get("field") or m["field"] in readable]
        return {"ref": ref, "model": name, "label": self.env["ir.model"]._get(name).name, "metrics": metrics, "kind": "orm",
                "fields": sorted(out, key=lambda x: x["label"].lower())}

    @api.model
    def _describe_blend(self, ref):
        """A blend as Explore sees it: its dimensions (as fields to group by) and its metrics, nothing else."""
        defn = self.env["dwo.dashboard.spec"]._dwo_resolve_dataset(ref)
        if not defn or not self._blend_readable(defn):
            raise AccessError(self.env._("This dataset is not available to you."))
        dims = [{"name": d["name"], "label": d.get("label") or d["name"], "type": d["kind"], "relation": d.get("comodel"),
                 "selection": None, "dimension": True, "measure": False, "aggs": [], "column": False, "expandable": False,
                 "intervals": list(C.INTERVALS) if d["kind"] == "date" else []} for d in defn["dimensions"]]
        metrics = [{"name": m["name"], "label": m.get("label") or m["name"], "agg": m["agg"], "field": m.get("field"),
                    "format": m.get("format"), "conditional": bool(m.get("where"))} for m in defn["metrics"]]
        return {"ref": ref, "model": defn["code"], "label": defn.get("label") or defn["code"], "kind": "blend",
                "metrics": metrics, "fields": sorted(dims, key=lambda x: x["label"].lower())}

    @api.model
    def _describe_fields(self, model, expandable_depth=0):
        """The fields of ``model`` the caller can read, with what each can be. A many2one to a model the caller can read is
        ``expandable``: the fields of that record can be used through it (a path such as ``partner_id.country_id``)."""
        out = []
        for fname, f in model.fields_get(attributes=ATTRIBUTES).items():
            kind = f["type"]
            stored = f.get("store", True)
            dimension = bool(f.get("groupable")) and kind not in NOT_GROUPABLE
            numeric = kind in NUMERIC and (stored or f.get("aggregator"))
            countable = stored and kind not in ("one2many", "many2many", "binary", "html", "properties", "json")
            aggs = (["sum", "avg", "min", "max"] if numeric else []) + (["count_distinct"] if countable else [])
            expandable = bool(expandable_depth and kind == "many2one" and stored and f.get("relation") in self.env
                              and self.env[f["relation"]].has_access("read"))
            out.append({
                "name": fname, "label": f["string"], "type": kind, "relation": f.get("relation"),
                "selection": f.get("selection") if kind == "selection" else None,
                "dimension": dimension, "measure": bool(aggs), "aggs": aggs,
                "column": kind not in NOT_COLUMN, "expandable": expandable,
                "intervals": list(C.INTERVALS) if kind in DATE else [],
            })
        return sorted(out, key=lambda x: x["label"].lower())

    @api.model
    def describe_related(self, ref, path):
        """The fields of the record a many2one ``path`` points to (``partner_id``, ``partner_id.parent_id``), as the caller
        can read them: the join of Explore. Every step must be a many2one the caller can read, at most MAX_PATH of them."""
        prefix, _sep, name = (ref or "").partition(":")
        parts = (path or "").split(".")
        if prefix != "orm" or name not in self.env or not self.env[name].has_access("read") or not 0 < len(parts) <= MAX_PATH:
            raise AccessError(self.env._("This dataset is not available to you."))
        model = self.env[name]
        for part in parts:
            field = model.fields_get(attributes=["type", "relation", "store"]).get(part)
            if not field or field["type"] != "many2one" or not field.get("store") or field["relation"] not in self.env \
                    or not self.env[field["relation"]].has_access("read"):
                raise AccessError(self.env._("This relation is not available to you."))
            model = self.env[field["relation"]]
        return {"path": path, "label": self.env["ir.model"]._get(model._name).name,
                "fields": self._describe_fields(model, expandable_depth=MAX_PATH - len(parts))}

    @api.model
    def filter_options(self, model, search="", limit=20):
        """Records for a relation filter's picker, as the caller (record rules apply)."""
        if model not in self.env or not self.env[model].has_access("read"):
            return []
        limit = max(1, min(int(limit), MAX_OPTIONS))
        return [[rid, display] for rid, display in self.env[model].name_search(search or "", limit=limit)]
