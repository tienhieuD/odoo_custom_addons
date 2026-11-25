# -*- coding: utf-8 -*-
import ast
import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..spec import constants as C

AGGS = [("sum", "Sum"), ("count", "Count"), ("avg", "Average"), ("min", "Minimum"), ("max", "Maximum"),
        ("count_distinct", "Distinct count")]
FORMATS = [("number", "Number"), ("currency", "Currency"), ("percent", "Percent")]


def _plain(value):
    """A domain literal as JSON data: tuples become lists. Anything that is not a literal (``user.id``, a function) is refused."""
    if isinstance(value, (tuple, list)):
        return [_plain(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise ValueError("not a plain value")


class DwoDataset(models.Model):
    """What the dashboards know about one model beyond its fields: named, reusable measures (*metrics*). Written by system
    administrators; read by every internal user (a definition holds no data). It compiles to a ``dwo-dataset/1`` document,
    which is what the page validator and the engine use. A metric is not a permission: whoever runs it needs to read the
    fields it reads (the engine runs as the viewer) and the field ``hidden`` flags of a definition only hide them in the
    interface, they protect nothing."""
    _name = "dwo.dataset"
    _description = "Dashboard dataset"
    _rec_name = "label"
    _order = "label, id"

    model_id = fields.Many2one("ir.model", string="Model", required=True, ondelete="cascade", index=True,
                               domain=[("transient", "=", False)])
    model_name = fields.Char(related="model_id.model", store=True, index=True)
    label = fields.Char(required=True, translate=True)
    ref = fields.Char(compute="_compute_ref", store=True, index=True)
    metric_ids = fields.One2many("dwo.dataset.metric", "dataset_id", string="Metrics", copy=True)

    _model_unique = models.Constraint("UNIQUE(model_id)", "This model already has a dataset.")

    @api.depends("model_name")
    def _compute_ref(self):
        for rec in self:
            rec.ref = "orm:%s" % rec.model_name if rec.model_name else False

    @api.onchange("model_id")
    def _onchange_model_id(self):
        if self.model_id and not self.label:
            self.label = self.model_id.name

    def _definition(self):
        """The ``dwo-dataset/1`` document of this record."""
        self.ensure_one()
        metrics = []
        for m in self.metric_ids.sorted("sequence"):
            item = {"name": m.name, "agg": m.agg}
            if m.field_id:
                item["field"] = m.field_id.name
            if m.label:
                item["label"] = m.label
            if m.where:
                item["where"] = m._where_list()
            if m.format:
                item["format"] = m.format
            metrics.append(item)
        defn = {"schema": C.DATASET_SCHEMA_ID, "type": "orm", "model": self.model_name, "label": self.label}
        if metrics:
            defn["metrics"] = metrics
        return defn

    @api.constrains("model_id", "label", "metric_ids")
    def _check_definition(self):
        Spec = self.env["dwo.dashboard.spec"]
        for rec in self:
            result = Spec._validate_dataset(rec._definition(), False)
            if not result["valid"]:
                raise ValidationError(_("The dataset is not valid:\n%s") % "\n".join(
                    "%(path)s: %(message)s" % e for e in result["errors"][:5]))


class DwoDatasetMetric(models.Model):
    _name = "dwo.dataset.metric"
    _description = "Dashboard metric"
    _order = "dataset_id, sequence, id"

    dataset_id = fields.Many2one("dwo.dataset", required=True, ondelete="cascade", index=True)
    model_name = fields.Char(related="dataset_id.model_name")
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, help="Technical name, used in dashboards: lower case letters, digits and _ (e.g. won_revenue).")
    label = fields.Char(translate=True, help="What the widgets show; the name if empty.")
    agg = fields.Selection(AGGS, string="Aggregate", required=True, default="sum")
    field_id = fields.Many2one("ir.model.fields", string="Field", ondelete="cascade",
                               domain="[('model_id', '=', parent.model_id), ('store', '=', True)]",
                               help="Empty to count the records.")
    where = fields.Char(string="Only records", help="A domain: the metric counts only the records that match it, whatever the filters of the page.")
    format = fields.Selection(FORMATS)

    _name_unique = models.Constraint("UNIQUE(dataset_id, name)", "A metric name is used once per dataset.")

    @api.constrains("name")
    def _check_name(self):
        for rec in self:
            if not re.match(C.ID_PATTERN, rec.name or ""):
                raise ValidationError(_("The name of a metric is lower case letters, digits and _, starting with a letter (e.g. won_revenue)."))

    @api.constrains("agg", "field_id")
    def _check_field(self):
        for rec in self:
            if rec.agg != "count" and not rec.field_id:
                raise ValidationError(_("A metric needs a field unless it counts records."))

    @api.constrains("where")
    def _check_where(self):
        for rec in self:
            if rec.where:
                rec._where_list()

    @api.constrains("name", "agg", "field_id", "where", "format")
    def _check_in_dataset(self):
        """The metric is checked as part of the whole definition (a field that does not exist, an average of a text...)."""
        self.dataset_id._check_definition()

    def _where_list(self):
        self.ensure_one()
        try:
            value = _plain(ast.literal_eval(self.where))
        except (ValueError, SyntaxError):
            raise ValidationError(_("The condition of the metric %s is not a plain domain (dynamic values such as the current user are not supported yet).", self.name))
        if not isinstance(value, list):
            raise ValidationError(_("The condition of the metric %s must be a list.", self.name))
        return value
