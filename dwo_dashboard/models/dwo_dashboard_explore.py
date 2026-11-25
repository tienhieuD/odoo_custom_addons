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


class DwoDashboardExplore(models.AbstractModel):
    """What the Explore screen (and, later, an AI assistant) may know: the datasets and fields the caller can read.
    Everything comes from the caller's own environment, so a field restricted by groups, or a model the caller cannot
    read, is simply absent."""
    _name = "dwo.dashboard.explore"
    _description = "Dashboard explore helpers"

    @api.model
    def list_datasets(self):
        """The models the caller can read (technical models are hidden, except for system administrators)."""
        show_all = self.env.is_system()
        rows = []
        for rec in self.env["ir.model"].sudo().search([("transient", "=", False)]):
            name = rec.model
            if name not in self.env or (not show_all and name.startswith(HIDDEN_PREFIXES)):
                continue
            # SQL-view report models (_auto = False: sale.report, account.invoice.report...) are the way to combine tables
            if self.env[name]._abstract or not self.env[name].has_access("read"):
                continue
            rows.append({"ref": "orm:" + name, "model": name, "label": rec.name or name})
        return sorted(rows, key=lambda r: r["label"].lower())

    @api.model
    def describe_dataset(self, ref):
        """Fields of an ORM dataset with what each can be: dimension, measure, column. ``fields_get`` already drops what the
        caller cannot read and gives translated labels."""
        prefix, _sep, name = (ref or "").partition(":")
        if prefix != "orm" or name not in self.env or not self.env[name].has_access("read"):
            raise AccessError(self.env._("This dataset is not available to you."))
        model = self.env[name]
        out = []
        for fname, f in model.fields_get(attributes=ATTRIBUTES).items():
            kind = f["type"]
            stored = f.get("store", True)
            dimension = bool(f.get("groupable")) and kind not in NOT_GROUPABLE
            numeric = kind in NUMERIC and (stored or f.get("aggregator"))
            countable = stored and kind not in ("one2many", "many2many", "binary", "html", "properties", "json")
            aggs = (["sum", "avg", "min", "max"] if numeric else []) + (["count_distinct"] if countable else [])
            out.append({
                "name": fname, "label": f["string"], "type": kind, "relation": f.get("relation"),
                "selection": f.get("selection") if kind == "selection" else None,
                "dimension": dimension, "measure": bool(aggs), "aggs": aggs,
                "column": kind not in NOT_COLUMN,
                "intervals": list(C.INTERVALS) if kind in DATE else [],
            })
        readable = set(model.fields_get(attributes=["type"]))
        defn = self.env["dwo.dashboard.spec"]._dwo_resolve_dataset(ref) or {}
        metrics = [{"name": m["name"], "label": m.get("label") or m["name"], "agg": m["agg"], "field": m.get("field"),
                    "format": m.get("format"), "conditional": bool(m.get("where"))}
                   for m in defn.get("metrics", []) if not m.get("field") or m["field"] in readable]
        return {"ref": ref, "model": name, "label": self.env["ir.model"]._get(name).name, "metrics": metrics,
                "fields": sorted(out, key=lambda x: x["label"].lower())}

    @api.model
    def filter_options(self, model, search="", limit=20):
        """Records for a relation filter's picker, as the caller (record rules apply)."""
        if model not in self.env or not self.env[model].has_access("read"):
            return []
        limit = max(1, min(int(limit), MAX_OPTIONS))
        return [[rid, display] for rid, display in self.env[model].name_search(search or "", limit=limit)]
