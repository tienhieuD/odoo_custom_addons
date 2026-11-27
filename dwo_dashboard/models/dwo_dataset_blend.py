# -*- coding: utf-8 -*-
"""The lines of a model of several tables (a blend), edited with Odoo lists.

The document (``dwo-dataset/1``, ``type: blend``) is what is stored and what the engine reads; the lines are another way to
write it, and map to it one to one:

    document                                  lines
    sources[]  {name, dataset, label, where}  dwo.dataset.table      (name, model_id, label, where)
    dimensions[] {name, label, kind, comodel, map}  dwo.dataset.dimension (name, label, kind) + .map lines
    dimensions[].map {source: field path}     dwo.dataset.dimension.map (table_id, field_path)
    metrics[]  {name, source, agg, field, ...} dwo.dataset.metric        (name, table_id, agg, field_id, ...)

Two pure steps keep them equal: lines -> document (``DwoDataset._blend_document``) and document -> lines
(``DwoDataset._sync_from_document``). ``comodel`` is not a line: it is the model the mapped fields point to."""
import ast
import json
import logging
import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..spec import constants as C

_logger = logging.getLogger(__name__)


def slug(text, taken, fallback):
    """A name for the document (lower case letters, digits, _), not in ``taken``."""
    base = re.sub(r"[^a-z0-9]+", "_", str(text or "").lower()).strip("_")
    if not base or not base[0].isalpha():
        base = ("%s_%s" % (fallback, base)).strip("_")
    base = base[:28]
    name, n = base, 2
    while name in taken:
        name = "%s_%d" % (base, n)
        n += 1
    return name


def domain_text(value):
    return str(value) if value else False


def domain_list(text, what):
    try:
        value = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        raise ValidationError(_("The condition of %s is not a plain domain.", what))
    if not isinstance(value, list):
        raise ValidationError(_("The condition of %s must be a list.", what))
    return json.loads(json.dumps(value))  # tuples become lists, as in the document


class DwoDatasetTable(models.Model):
    _name = "dwo.dataset.table"
    _inherit = "dwo.dataset.lines"
    _description = "A table (an Odoo model) of a model of several tables"
    _order = "dataset_id, sequence, id"

    dataset_id = fields.Many2one("dwo.dataset", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    model_id = fields.Many2one("ir.model", string="Model", required=True, ondelete="cascade", domain=[("transient", "=", False), ("abstract", "=", False)])
    model_name = fields.Char(related="model_id.model")
    name = fields.Char(readonly=True, copy=False, help="The name the document gives this table.")
    label = fields.Char(help="What the dimensions and measures call it; the model's name if empty.")
    where = fields.Char(string="Only records", help="A domain: this table reads only the records that match it.")

    _name_unique = models.Constraint("UNIQUE(dataset_id, name)", "A table name is used once per dataset.")

    def _blend_datasets(self):
        return self.dataset_id

    @api.depends("label", "model_id")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.label or rec.model_id.name or rec.name or ""

    @api.model_create_multi
    def create(self, vals_list):
        recs = self.browse()
        for vals in vals_list:
            if not vals.get("name") and vals.get("model_id") and vals.get("dataset_id"):
                taken = self.search([("dataset_id", "=", vals["dataset_id"])]).mapped("name")
                vals = dict(vals, name=slug(self.env["ir.model"].browse(vals["model_id"]).model, taken, "t"))
            recs |= super().create([vals])
        return recs

    def write(self, vals):
        if "model_id" in vals and "name" not in vals:
            for rec in self:
                taken = (rec.dataset_id.table_ids - rec).mapped("name")
                name = slug(self.env["ir.model"].browse(vals["model_id"]).model, taken, "t")
                super(DwoDatasetTable, rec).write(dict(vals, name=name))
            return True
        return super().write(vals)

    @api.constrains("where")
    def _check_where(self):
        for rec in self.filtered("where"):
            domain_list(rec.where, rec.display_name)


class DwoDatasetDimension(models.Model):
    _name = "dwo.dataset.dimension"
    _inherit = "dwo.dataset.lines"
    _description = "A dimension shared by the tables of a model of several tables"
    _order = "dataset_id, sequence, id"

    dataset_id = fields.Many2one("dwo.dataset", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    label = fields.Char(required=True, help="What the dashboards call it (Date, Salesperson, Customer...).")
    name = fields.Char(readonly=True, copy=False, help="The name the document gives this dimension.")
    kind = fields.Selection([(k, k.title()) for k in C.BLEND_DIM_KINDS], required=True, default="date")
    map_ids = fields.One2many("dwo.dataset.dimension.map", "dimension_id", string="Field of each table", copy=True)
    summary = fields.Char(compute="_compute_summary")

    _name_unique = models.Constraint("UNIQUE(dataset_id, name)", "A dimension name is used once per dataset.")

    def _blend_datasets(self):
        return self.dataset_id

    @api.depends("map_ids.table_id", "map_ids.field_path")
    def _compute_summary(self):
        for rec in self:
            rec.summary = ", ".join("%s: %s" % (m.table_id.display_name, m.field_path or "?") for m in rec.map_ids.sorted("id"))

    @api.model
    def default_get(self, fields_list):
        """A new dimension of a saved dataset starts with one line per table: the person only picks the fields."""
        res = super().default_get(fields_list)
        dataset = self.env["dwo.dataset"].browse(res.get("dataset_id") or 0).exists()
        if "map_ids" in fields_list and dataset:
            res["map_ids"] = [(0, 0, {"table_id": t.id}) for t in dataset.table_ids.sorted(lambda t: (t.sequence, t.id))]
        return res

    @api.onchange("dataset_id")
    def _onchange_dataset_id(self):
        """The web client fills the dataset of a new line: start it with one line per table."""
        if self.dataset_id and not self.map_ids:
            self.map_ids = [(0, 0, {"table_id": t.id}) for t in self.dataset_id.table_ids.sorted(lambda t: (t.sequence, t.id))]

    @api.model_create_multi
    def create(self, vals_list):
        recs = self.browse()
        for vals in vals_list:
            if not vals.get("name") and vals.get("dataset_id"):
                taken = self.search([("dataset_id", "=", vals["dataset_id"])]).mapped("name")
                vals = dict(vals, name=slug(vals.get("label"), taken, "dim"))
            recs |= super().create([vals])
        return recs


class DwoDatasetDimensionMap(models.Model):
    _name = "dwo.dataset.dimension.map"
    _inherit = "dwo.dataset.lines"
    _description = "What a shared dimension is in one table"
    _order = "dimension_id, id"

    dimension_id = fields.Many2one("dwo.dataset.dimension", required=True, ondelete="cascade", index=True)
    dataset_id = fields.Many2one(related="dimension_id.dataset_id", store=True, index=True)
    table_id = fields.Many2one("dwo.dataset.table", required=True, ondelete="cascade", domain="[('dataset_id', '=', dataset_id)]")
    model_id = fields.Many2one(related="table_id.model_id")
    field_path = fields.Char(string="Field", help="A field name, or a path through many2one fields (partner_id.country_id).")
    field_id = fields.Many2one("ir.model.fields", string="Pick a field", compute="_compute_field_id", inverse="_inverse_field_id",
                               domain="[('model_id', '=', model_id), ('store', '=', True)]")

    _table_unique = models.Constraint("UNIQUE(dimension_id, table_id)", "A dimension has one field per table.")

    def _blend_datasets(self):
        return self.dataset_id

    @api.depends("field_path", "model_id")
    def _compute_field_id(self):
        for rec in self:
            path = rec.field_path or ""
            rec.field_id = self.env["ir.model.fields"].sudo().search(
                [("model_id", "=", rec.model_id.id), ("name", "=", path)], limit=1) if path and "." not in path else False

    def _inverse_field_id(self):
        for rec in self:
            if rec.field_id:
                rec.field_path = rec.field_id.name


class DwoDataset(models.Model):
    _inherit = "dwo.dataset"

    table_ids = fields.One2many("dwo.dataset.table", "dataset_id", string="Tables", copy=True)
    dimension_ids = fields.One2many("dwo.dataset.dimension", "dataset_id", string="Dimensions", copy=True)
    draft = fields.Boolean(readonly=True, copy=False,
                           help="A model of several tables with fewer than two tables, no dimension or no measure yet: it is "
                                "saved, but dashboards cannot use it.")

    # ------------------------------------------------------------------------------------------ lines -> document
    def _blend_document(self):
        """The ``dwo-dataset/1`` document written by the lines (what is not a line, such as an extra key, is kept)."""
        self.ensure_one()
        try:
            base = json.loads(self.sudo().definition_text or "{}")
        except ValueError:
            base = {}
        defn = {k: v for k, v in (base if isinstance(base, dict) else {}).items() if k not in ("sources", "dimensions", "metrics")}
        defn.update(schema=C.DATASET_SCHEMA_ID, type="blend", code=self.code, label=self.label)
        tables = self.table_ids.sorted(lambda t: (t.sequence, t.id))
        sources = []
        for t in tables:
            item = {"name": t.name, "dataset": "orm:%s" % t.model_id.model}
            if t.label:
                item["label"] = t.label
            if t.where:
                item["where"] = domain_list(t.where, t.display_name)
            sources.append(item)
        dimensions = []
        for d in self.dimension_ids.sorted(lambda x: (x.sequence, x.id)):
            mapping = {}
            for t in tables:
                line = d.map_ids.filtered(lambda m: m.table_id == t)[:1]
                if line and line.field_path:
                    mapping[t.name] = line.field_path
            item = {"name": d.name, "label": d.label, "kind": d.kind, "map": mapping}
            if d.kind == "many2one":
                comodel = self._comodel_of(tables, mapping)
                if comodel:
                    item["comodel"] = comodel
            dimensions.append(item)
        metrics = []
        for m in self.metric_ids.sorted(lambda x: (x.sequence, x.id)):
            item = {"name": m.name, "source": m.table_id.name, "agg": m.agg}
            if m.label:
                item["label"] = m.label
            if m.field_id:
                item["field"] = m.field_id.name
            if m.where:
                item["where"] = m._where_list()
            if m.format:
                item["format"] = m.format
            metrics.append(item)
        defn.update(sources=sources, dimensions=dimensions, metrics=metrics)
        return defn

    def _comodel_of(self, tables, mapping):
        """The model the mapped fields point to (the first table that gives a many2one field)."""
        for t in tables:
            path = mapping.get(t.name)
            model = self.env.get(t.model_id.model)
            if not path or model is None:
                continue
            field = None
            for part in path.split("."):
                field = model._fields.get(part)
                if field is None or field.type != "many2one":
                    break
                model = self.env[field.comodel_name]
            if field is not None and field.type == "many2one":
                return field.comodel_name
        return None

    def _rebuild_blend_document(self):
        """Write the document the lines say, and whether it is still a draft; the document is then checked as a whole."""
        for rec in self:
            doc = rec._blend_document()
            complete = len(doc["sources"]) >= 2 and bool(doc["dimensions"]) and bool(doc["metrics"])
            rec.with_context(dwo_sync=True).write({"definition_text": json.dumps(doc, indent=1, ensure_ascii=False),
                                                   "draft": not complete})

    # ------------------------------------------------------------------------------------------ document -> lines
    def _sync_from_document(self):
        """Replace the lines by what the stored document says (a document written by the assistant, an import, a test)."""
        for rec in self:
            try:
                defn = json.loads(rec.sudo().definition_text or "")
            except ValueError:
                continue
            if not isinstance(defn, dict) or not isinstance(defn.get("sources"), list):
                continue
            Model = self.env["ir.model"].sudo()
            Field = self.env["ir.model.fields"].sudo()
            ctx = dict(dwo_skip_rebuild=True)
            rec.table_ids.with_context(**ctx).unlink()
            rec.dimension_ids.with_context(**ctx).unlink()
            rec.metric_ids.with_context(**ctx).unlink()
            tables = {}
            for i, src in enumerate(defn["sources"]):
                model = Model.search([("model", "=", str(src.get("dataset", ""))[4:])], limit=1)
                if not model:
                    _logger.warning("dataset %s: no model %s, its lines are not written", rec.code, src.get("dataset"))
                    continue
                tables[src["name"]] = self.env["dwo.dataset.table"].with_context(**ctx).create({
                    "dataset_id": rec.id, "sequence": (i + 1) * 10, "model_id": model.id, "name": src["name"],
                    "label": src.get("label") or False, "where": domain_text(src.get("where"))})
            for i, dim in enumerate(defn.get("dimensions") or []):
                lines = [(0, 0, {"table_id": tables[n].id, "field_path": path}) for n, path in (dim.get("map") or {}).items() if n in tables]
                self.env["dwo.dataset.dimension"].with_context(**ctx).create({
                    "dataset_id": rec.id, "sequence": (i + 1) * 10, "name": dim["name"], "label": dim.get("label") or dim["name"],
                    "kind": dim["kind"], "map_ids": lines})
            for i, m in enumerate(defn.get("metrics") or []):
                table = tables.get(m.get("source"))
                field = Field.search([("model_id", "=", table.model_id.id), ("name", "=", m["field"])], limit=1) \
                    if table and m.get("field") else Field
                self.env["dwo.dataset.metric"].with_context(**ctx).create({
                    "dataset_id": rec.id, "sequence": (i + 1) * 10, "name": m["name"], "label": m.get("label") or False,
                    "table_id": table.id if table else False, "agg": m["agg"], "field_id": field.id or False,
                    "where": domain_text(m.get("where")), "format": m.get("format") or False})
            rec.invalidate_recordset()

    # ------------------------------------------------------------------------------------------ suggestions
    def action_suggest_dimensions(self):
        """Add a dimension for each field that every table has with the same name and kind (dates first, then records)."""
        self.ensure_one()
        tables = self.table_ids.sorted(lambda t: (t.sequence, t.id))
        if len(tables) < 2 or len(self.dimension_ids) >= C.MAX_BLEND_DIMS:
            return {"type": "ir.actions.client", "tag": "display_notification", "params": {
                "title": _("Nothing to suggest"), "type": "warning",
                "message": _("Add at least two tables first (and keep the dimensions under %d).", C.MAX_BLEND_DIMS)}}
        kinds = {"date": "date", "datetime": "date", "many2one": "many2one", "selection": "selection", "char": "char",
                 "integer": "integer", "boolean": "boolean"}
        used = {m.field_path for d in self.dimension_ids for m in d.map_ids}
        skip = {"id", "create_uid", "write_uid", "create_date", "write_date", "display_name"}
        first = self.env[tables[0].model_id.model]
        found = []
        for name, field in first._fields.items():
            kind = kinds.get(field.type)
            if not kind or not field.store or name in skip or name in used or not getattr(field, "groupable", True):
                continue
            others = [self.env[t.model_id.model]._fields.get(name) for t in tables[1:]]
            if all(o is not None and o.store and kinds.get(o.type) == kind and
                   (kind != "many2one" or o.comodel_name == field.comodel_name) for o in others):
                found.append((("date", "many2one", "selection").index(kind) if kind in ("date", "many2one", "selection") else 3,
                              field.string, name, kind))
        found.sort()
        room = C.MAX_BLEND_DIMS - len(self.dimension_ids)
        lines = []
        for _rank, label, name, kind in found[:room]:
            lines.append((0, 0, {"label": label, "kind": kind, "map_ids": [(0, 0, {"table_id": t.id, "field_path": name}) for t in tables]}))
        if not lines:
            return {"type": "ir.actions.client", "tag": "display_notification", "params": {
                "title": _("Nothing to suggest"), "type": "warning",
                "message": _("These tables share no field with the same name and kind: add the dimensions yourself.")}}
        self.write({"dimension_ids": lines})
        return {"type": "ir.actions.client", "tag": "reload"}
