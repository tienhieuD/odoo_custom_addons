# -*- coding: utf-8 -*-
"""Ask the assistant for a dataset (a blend, the metrics of a model, a SQL query). The answer is only shown: it reaches the
dataset when the manager presses "Use it", and the Check and Test buttons of the form apply as for anything written by hand."""
import json
import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..spec import constants as C


class DwoAIDatasetWizard(models.TransientModel):
    _name = "dwo.ai.dataset.wizard"
    _description = "Ask the assistant for a dataset"

    kind = fields.Selection([("blend", "Blend of models"), ("orm", "Metrics of a model"), ("sql", "SQL query")], required=True, default="blend")
    dataset_id = fields.Many2one("dwo.dataset", string="Change this dataset", ondelete="cascade",
                                 help="Empty: a new dataset is created when you use the answer.")
    model_ids = fields.Many2many("ir.model", string="Models", domain=[("transient", "=", False)])
    tables = fields.Char(help="Tables the query may read, separated by commas (for example sale_order, res_partner). Empty: the tables named in the request.")
    request = fields.Text(required=True)
    send_current = fields.Boolean(string="Send the current definition too", help="The text of the current blend or query is sent to the service, "
                                  "so that the answer changes it instead of starting again. Off: it is not sent.")
    result_json = fields.Text()
    result_text = fields.Text(string="Answer", readonly=True)
    message = fields.Text(readonly=True)

    @api.onchange("dataset_id")
    def _onchange_dataset_id(self):
        if self.dataset_id:
            self.kind = self.dataset_id.kind
            self.model_ids = self.dataset_id.model_id if self.dataset_id.kind == "orm" else self.env["ir.model"]

    def _current_text(self):
        d = self.dataset_id
        if not (self.send_current and d):
            return ""
        return (d.definition_text if d.kind == "blend" else d.sql_query if d.kind == "sql" else "") or ""

    def _reopen(self):
        return {"type": "ir.actions.act_window", "res_model": self._name, "res_id": self.id, "view_mode": "form", "target": "new"}

    def action_ask(self):
        self.ensure_one()
        if self.kind != "sql":
            refs = ["orm:" + m for m in self.model_ids.mapped("model")]
        else:
            refs = [t for t in re.split(r"[,\s]+", self.tables or "") if t]
        result = self.env["dwo.dashboard.ai"].propose_dataset(self.kind, self.request, refs, self._current_text())
        if not result["ok"]:
            self.write({"result_json": False, "result_text": False,
                        "message": "%s\n%s" % (result["message"], "\n".join("%(path)s: %(message)s" % e for e in result["errors"]))})
            return self._reopen()
        self.write({"result_json": json.dumps(result, ensure_ascii=False), "result_text": self._show(result), "message": False})
        return self._reopen()

    @api.model
    def _show(self, result):
        if result["kind"] == "blend":
            return json.dumps(result["definition"], indent=1, ensure_ascii=False)
        if result["kind"] == "orm":
            return "\n".join("%s: %s of %s%s" % (m["name"], m["agg"], m.get("field") or _("records"), "  where %s" % m["where"] if m.get("where") else "")
                             for m in result["metrics"])
        note = _("Tested on the database: %d columns.", len(result.get("columns", []))) if result.get("tested") else \
            _("Not tested: this server has no read-only database login for SQL datasets. Press Test the query on the dataset once it is set up.")
        return "%s\n\n-- %s" % (result["query"], note)

    # ------------------------------------------------------------------------------------------------------- use it
    def _unique_code(self, prefix, code):
        taken = set(self.env["dwo.dataset"].search([("code", "=like", code + "%"), ("kind", "=", prefix)]).mapped("code"))
        candidate, n = code, 1
        while candidate in taken:
            n += 1
            candidate = "%s_%d" % (code[:28], n)
        return candidate

    def action_apply(self):
        self.ensure_one()
        if not self.result_json:
            raise UserError(_("Ask first."))
        result = json.loads(self.result_json)
        Dataset = self.env["dwo.dataset"]
        dataset = self.dataset_id
        if result["kind"] == "blend":
            defn = dict(result["definition"])
            if dataset:
                dataset.write({"definition_text": json.dumps(defn, indent=1, ensure_ascii=False)})
            else:
                code = self._unique_code("blend", defn["code"])
                defn["code"] = code
                dataset = Dataset.create({"kind": "blend", "code": code, "label": defn.get("label") or code,
                                          "definition_text": json.dumps(defn, indent=1, ensure_ascii=False)})
        elif result["kind"] == "sql":
            if dataset:
                doc = dataset._sql_doc()
                doc["sql"].update(query=result["query"], params=result["params"], columns=[])
                dataset._write_sql_doc(doc)
            else:
                code = self._unique_code("sql", result["code"])
                doc = {"schema": C.DATASET_SCHEMA_ID, "type": "sql", "code": code, "label": result["label"],
                       "sql": {"query": result["query"], "params": result["params"], "groups": [], "columns": []}}
                dataset = Dataset.create({"kind": "sql", "code": code, "label": result["label"], "definition_text": json.dumps(doc)})
        else:
            model = self.model_ids[:1] or dataset.model_id
            if not model:
                raise UserError(_("Choose the model of the metrics."))
            dataset = dataset or Dataset.search([("model_id", "=", model.id)], limit=1) or Dataset.create(
                {"kind": "orm", "model_id": model.id, "label": model.name})
            for m in result["metrics"]:
                vals = {"name": m["name"], "label": m.get("label") or False, "agg": m["agg"], "format": m.get("format") or False,
                        "where": repr(m["where"]) if m.get("where") else False,
                        "field_id": self.env["ir.model.fields"]._get(model.model, m["field"]).id if m.get("field") else False}
                existing = dataset.metric_ids.filtered(lambda x: x.name == m["name"])
                if existing:
                    existing.write(vals)
                else:
                    dataset.write({"metric_ids": [(0, 0, vals)]})
        return dataset.get_formview_action()
