# -*- coding: utf-8 -*-
import ast
import json
import re

import psycopg2
import psycopg2.errors
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from ..spec import constants as C
from ..spec.sqlscan import scan

MANAGER = "dwo_dashboard.group_dwo_dashboard_manager"
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


class DwoDatasetLines(models.AbstractModel):
    _name = "dwo.dataset.lines"
    _description = "Lines of a dataset: they rebuild the document of their dataset"

    def _blend_datasets(self):
        raise NotImplementedError

    def _rebuild(self, datasets):
        if self.env.context.get("dwo_skip_rebuild"):
            return
        datasets.filtered(lambda d: d.exists() and d.kind == "blend")._rebuild_blend_document()

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        self._rebuild(recs._blend_datasets())
        return recs

    def write(self, vals):
        datasets = self._blend_datasets()
        res = super().write(vals)
        self._rebuild(datasets | self._blend_datasets())
        return res

    def unlink(self):
        datasets = self._blend_datasets()
        res = super().unlink()
        self._rebuild(datasets)
        return res


class DwoDataset(models.Model):
    """What the dashboards know about a data source beyond its fields. Three kinds:
    * ``orm``: an Odoo model with named, reusable measures (*metrics*);
    * ``blend``: several Odoo models read separately (each as the viewer) and merged by shared dimensions;
    * ``sql``: a query written by a dashboard manager (see engine/sql.py for what protects it).
    Written by dashboard managers; read by every internal user (a definition holds no data). It compiles to a
    ``dwo-dataset/1`` document, which is what the page validator and the engine use. A metric is not a permission: whoever
    runs it needs to read the fields it reads (the engine runs as the viewer) and the field ``hidden`` flags of a definition
    only hide them in the interface, they protect nothing."""
    _name = "dwo.dataset"
    _description = "Dashboard dataset"
    _rec_name = "label"
    _order = "label, id"

    kind = fields.Selection([("orm", "Odoo model"), ("blend", "Model of several tables"), ("sql", "SQL query")], required=True,
                            default="orm", index=True)
    model_id = fields.Many2one("ir.model", string="Model", ondelete="cascade", index=True,
                               domain=[("transient", "=", False)])
    model_name = fields.Char(related="model_id.model", store=True, index=True)
    code = fields.Char(help="The name of a blend or SQL dataset in dashboards: lower case letters, digits and _ (blend:code, sql:code).")
    label = fields.Char(required=True, translate=True)
    ref = fields.Char(compute="_compute_ref", store=True, index=True)
    metric_ids = fields.One2many("dwo.dataset.metric", "dataset_id", string="Metrics", copy=True)
    # a query is read by managers only: a plain dashboard user may run a SQL dataset, never read its text (Explore and the engine
    # read it with sudo)
    definition_text = fields.Text(string="Definition", groups=MANAGER, help="The dwo-dataset/1 document of a blend or a SQL dataset (JSON).")
    sql_query = fields.Text(string="Query", compute="_compute_sql_parts", inverse="_inverse_sql_query", groups=MANAGER,
                            help="One SELECT. Parameters: %(uid)s, %(company_id)s, %(company_ids)s, %(lang)s, %(today)s, %(now)s "
                                 "(declare the ones you use in the options). Write a percent sign as %%.")
    sql_group_ids = fields.Many2many("res.groups", string="Who can use it", compute="_compute_sql_parts",
                                     inverse="_inverse_sql_groups", groups=MANAGER,
                                     help="The groups whose members can see what the query returns, on any page they can open.")
    sql_options = fields.Text(string="Columns and options", compute="_compute_sql_parts", inverse="_inverse_sql_options",
                              groups=MANAGER, help="JSON: the columns of the query (name, type, role, label), its parameters and its metrics.")

    _model_unique = models.Constraint("UNIQUE(model_id)", "This model already has a dataset.")
    _ref_unique = models.Constraint("UNIQUE(ref)", "A dataset with this name already exists.")

    @api.depends("kind", "model_name", "code")
    def _compute_ref(self):
        for rec in self:
            if rec.kind == "orm":
                rec.ref = "orm:%s" % rec.model_name if rec.model_name else False
            else:
                rec.ref = "%s:%s" % (rec.kind, rec.code) if rec.code else False

    @api.onchange("model_id")
    def _onchange_model_id(self):
        if self.model_id and not self.label:
            self.label = self.model_id.name

    def _definition(self):
        """The ``dwo-dataset/1`` document of this record, as dashboards use it: nothing for a draft."""
        self.ensure_one()
        if self.kind == "blend" and self.draft:
            return {}
        return self._document()

    def _document(self):
        """The ``dwo-dataset/1`` document of this record, a draft included."""
        self.ensure_one()
        if self.kind != "orm":
            try:
                defn = json.loads(self.sudo().definition_text or "{}")
            except ValueError:
                return {}
            if not isinstance(defn, dict):
                return {}
            # the record is the truth for what it is called (renaming a dataset in the JSON would break the pages that use it)
            return dict(defn, schema=C.DATASET_SCHEMA_ID, type=self.kind, code=self.code, label=self.label)
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

    @api.constrains("kind", "model_id", "code", "label", "metric_ids", "definition_text", "draft")
    def _check_definition(self):
        Spec = self.env["dwo.dashboard.spec"]
        for rec in self:
            if rec.kind == "orm":
                if not rec.model_id:
                    raise ValidationError(_("An Odoo model dataset needs its model."))
            elif not re.match(C.ID_PATTERN, rec.code or ""):
                raise ValidationError(_("The code of a blend or SQL dataset is lower case letters, digits and _ (e.g. sales_vs_costs)."))
            if rec.kind == "blend" and rec.draft:
                continue  # tables only so far: it is checked when it is complete
            defn = rec._document()
            if rec.kind == "sql" and not (defn.get("sql") or {}).get("columns"):
                # a draft: the query and the groups are checked, the columns come from the button "Fill the columns from the query"
                problems, _names = scan((defn.get("sql") or {}).get("query") or "SELECT 1")
                if problems:
                    raise ValidationError(_("The query has problems:\n%s") % "\n".join(problems))
                continue
            result = Spec._validate_dataset(defn, False)
            if not result["valid"]:
                raise ValidationError(_("The dataset is not valid:\n%s") % "\n".join(
                    "%(path)s: %(message)s" % e for e in result["errors"][:8]))

    # ---- a SQL dataset in three editable pieces (the query, who can use it, the columns and options), kept in one document
    def _sql_doc(self):
        self.ensure_one()
        defn = self._definition() if self.sudo().definition_text else {}
        defn = dict(defn or {"schema": C.DATASET_SCHEMA_ID})
        block = dict(defn.get("sql") or {})
        block.setdefault("query", "")
        block.setdefault("groups", [])
        block.setdefault("columns", [])
        defn["sql"] = block
        return defn

    def _write_sql_doc(self, defn):
        self.sudo().with_context(dwo_sql_doc=True).write({"definition_text": json.dumps(defn, indent=1, ensure_ascii=False)})

    @api.depends("kind", "definition_text")
    def _compute_sql_parts(self):
        for rec in self:
            defn = rec.sudo()._definition() if rec.kind == "sql" else {}
            block = defn.get("sql") if isinstance(defn.get("sql"), dict) else {}
            rec.sql_query = block.get("query") or False
            groups = self.env["res.groups"]
            for xmlid in block.get("groups") or []:
                group = self.env.ref(xmlid, raise_if_not_found=False)
                if group and group._name == "res.groups":
                    groups |= group
            rec.sql_group_ids = groups
            options = {k: block[k] for k in ("params", "company_scoped") if k in block}
            options["columns"] = block.get("columns", [])
            options["metrics"] = defn.get("metrics", [])
            rec.sql_options = json.dumps(options, indent=1, ensure_ascii=False) if rec.kind == "sql" else False

    def _inverse_sql_query(self):
        for rec in self.filtered(lambda r: r.kind == "sql"):
            defn = rec._sql_doc()
            defn["sql"]["query"] = rec.sql_query or ""
            rec._write_sql_doc(defn)

    def _inverse_sql_groups(self):
        for rec in self.filtered(lambda r: r.kind == "sql"):
            defn = rec._sql_doc()
            xmlids = []
            for group in rec.sql_group_ids:
                xmlid = group.get_external_id().get(group.id)
                if not xmlid:
                    raise ValidationError(_("The group %s has no external identifier: a dataset can only name groups that have one.", group.display_name))
                xmlids.append(xmlid)
            defn["sql"]["groups"] = xmlids
            rec._write_sql_doc(defn)

    def _inverse_sql_options(self):
        for rec in self.filtered(lambda r: r.kind == "sql"):
            try:
                options = json.loads(rec.sql_options or "{}")
            except ValueError:
                raise ValidationError(_("The columns and options are not valid JSON."))
            if not isinstance(options, dict):
                raise ValidationError(_("The columns and options are an object: {\"columns\": [...]}."))
            defn = rec._sql_doc()
            for key in ("params", "company_scoped", "columns"):
                defn["sql"].pop(key, None)
            defn["sql"].update({k: v for k, v in options.items() if k in ("params", "company_scoped", "columns")})
            if "metrics" in options:
                defn["metrics"] = options["metrics"]
            rec._write_sql_doc(defn)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:  # a SQL dataset written as a document without groups: every dashboard user, as the form shows
            if vals.get("kind") == "sql" and vals.get("definition_text"):
                try:
                    defn = json.loads(vals["definition_text"])
                except ValueError:
                    continue
                if isinstance(defn, dict) and isinstance(defn.get("sql"), dict) and not defn["sql"].get("groups"):
                    defn["sql"]["groups"] = ["dwo_dashboard.group_dwo_dashboard_user"]
                    vals["definition_text"] = json.dumps(defn)
        lines = ("table_ids", "dimension_ids", "metric_ids")
        for vals in vals_list:  # a blend written with lines: a draft until the document the lines write is complete
            if vals.get("kind") == "blend":
                if any(vals.get(k) for k in lines) and vals.get("definition_text"):
                    raise UserError(_("Write a model of several tables with its lines or with its definition, not both."))
                if not vals.get("definition_text"):
                    vals["draft"] = True  # lines, or nothing yet: it is complete when the lines say so
        recs = super(DwoDataset, self.with_context(dwo_skip_rebuild=True)).create(vals_list)
        recs = recs.with_context(dwo_skip_rebuild=self.env.context.get("dwo_skip_rebuild", False))
        for rec, vals in zip(recs, vals_list):
            if rec.kind == "blend" and not self.env.context.get("dwo_sync"):
                if rec.draft:
                    rec._rebuild_blend_document()
                elif vals.get("definition_text"):
                    rec._sync_from_document()
        user_group = "dwo_dashboard.group_dwo_dashboard_user"
        for rec in recs.filtered(lambda r: r.kind == "sql"):
            defn = rec._sql_doc()
            if not defn["sql"]["groups"]:
                defn["sql"]["groups"] = [user_group]  # by default every dashboard user: the form shows it, and a manager can narrow it
                rec._write_sql_doc(defn)
        return recs

    def write(self, vals):
        lines = ("table_ids", "dimension_ids", "metric_ids")
        blends = self.filtered(lambda r: r.kind == "blend") if not self.env.context.get("dwo_sync") else self.browse()
        by_lines = blends and any(k in vals for k in lines)
        if by_lines and vals.get("definition_text"):
            raise UserError(_("Edit a model of several tables with its lines or with its definition, not both."))
        if by_lines:
            res = super(DwoDataset, self.with_context(dwo_skip_rebuild=True)).write(dict(vals, draft=True) if len(blends) == len(self) else vals)
            blends._rebuild_blend_document()
            return res
        if blends and vals.get("definition_text"):
            vals = dict(vals, draft=False)  # a whole document is checked as one, and writes the lines
        res = super().write(vals)
        if blends and vals.get("definition_text"):
            blends._sync_from_document()
        return res

    def _sql_block(self):
        self.ensure_one()
        if self.kind != "sql":
            raise UserError(_("Only a SQL dataset has a query to run."))
        self.check_access("write")  # a manager's tool: reading the dataset is not enough to try a query
        if not self.env["dwo.dashboard.spec"]._sql_enabled():
            raise UserError(_("SQL datasets are not set up on this server: an administrator has to configure the read-only database login "
                              "(see the setup script in the module, tools/sql_role_setup.sql)."))
        block = self._definition().get("sql")
        if not isinstance(block, dict) or not block.get("query"):
            raise UserError(_("Write the query first."))
        return block

    def _run_sample(self):
        from ..engine import sql as sql_engine
        block = self._sql_block()
        try:
            return sql_engine.sample(self.env, block)
        except sql_engine.SqlSetupError as exc:
            raise UserError(_("SQL datasets are not set up safely on this server: %s.", exc))
        except sql_engine.SqlRefused as exc:
            raise UserError(_("The query is refused: %s.", exc))
        except psycopg2.errors.QueryCanceled:
            raise UserError(_("The query took too long and was stopped."))
        except psycopg2.errors.InsufficientPrivilege:
            raise UserError(_("The query reads something the read-only database login may not read."))
        except psycopg2.Error as exc:
            raise UserError(_("The database refused the query: %s", (exc.pgerror or str(exc)).strip().splitlines()[0]))

    def action_test(self):
        """Run the query (20 rows, every guard) and show what it returns."""
        self.ensure_one()
        names, types, rows = self._run_sample()
        declared = {c.get("name"): c for c in (self._definition().get("sql") or {}).get("columns", []) if isinstance(c, dict)}
        missing = [n for n in declared if n not in names]
        if missing:
            raise UserError(_("The query does not return the column(s) %s that the dataset declares. Name them with AS, or press "
                              "'Fill the columns from the query'.", ", ".join(missing)))
        wrong = ["%s (declared %s, the query gives %s)" % (n, declared[n].get("type"), t) for n, t in zip(names, types)
                 if n in declared and declared[n].get("type") != t]
        extra = [n for n in names if n not in declared]
        lines = ["%s" % ", ".join(names)] + [", ".join("" if v is None else str(v)[:30] for v in row) for row in rows[:5]]
        if wrong:
            lines.append(_("Type differs: %s. Press 'Fill the columns from the query' to correct it.", "; ".join(wrong)))
        if extra:
            lines.append(_("Not declared yet (not usable in dashboards): %s.", ", ".join(extra)))
        return {"type": "ir.actions.client", "tag": "display_notification",
                "params": {"title": _("The query works: %d columns", len(names)), "message": "\n".join(lines),
                           "type": "warning" if wrong or extra else "success", "sticky": True}}

    def action_fill_columns(self):
        """Write the column list of the definition from what the query returns: the person only chooses each column's role."""
        self.ensure_one()
        names, types, _rows = self._run_sample()
        bad = [n for n in names if not re.match(C.COLUMN_PATTERN, n)]
        if bad:
            raise UserError(_("Name these columns in lower case with AS (letters, digits, _): %s", ", ".join(bad)))
        defn = self._definition()
        old = {c.get("name"): c for c in defn["sql"].get("columns", []) if isinstance(c, dict)}
        columns = []
        for name, kind in zip(names, types):
            column = dict(old.get(name) or {"name": name, "type": kind, "label": name.replace("_", " ").title(),
                                            "role": "measure" if kind in C.SQL_NUMERIC_TYPES and not name.endswith("id") else "dimension"})
            column["type"] = kind
            if column.get("role") == "measure" and kind not in C.SQL_NUMERIC_TYPES:
                column["role"] = "dimension"
            columns.append(column)
        defn["sql"]["columns"] = columns
        self.definition_text = json.dumps(defn, indent=1, ensure_ascii=False)
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_check(self):
        """Check the definition as the person who presses the button (their own access: a field they cannot read is an error)."""
        self.ensure_one()
        if self.kind == "blend" and self.draft:
            raise UserError(_("This model is still a draft: it needs at least two tables, a dimension and a measure."))
        result = self.env["dwo.dashboard.spec"]._validate_dataset(self._document(), True)
        if not result["valid"]:
            raise UserError(_("The definition has problems:\n%s") % "\n".join(
                "%(path)s: %(message)s" % e for e in result["errors"][:12]))
        return {"type": "ir.actions.client", "tag": "display_notification",
                "params": {"title": _("Valid"), "message": _("The definition is valid and you can read everything it uses."),
                           "type": "success", "sticky": False}}


class DwoDatasetMetric(models.Model):
    _name = "dwo.dataset.metric"
    _inherit = "dwo.dataset.lines"
    _description = "Dashboard metric"
    _order = "dataset_id, sequence, id"

    def _blend_datasets(self):
        return self.dataset_id

    dataset_id = fields.Many2one("dwo.dataset", required=True, ondelete="cascade", index=True)
    table_id = fields.Many2one("dwo.dataset.table", string="Table", ondelete="cascade", domain="[('dataset_id', '=', dataset_id)]",
                               help="The table of a model of several tables that this measure reads.")
    model_id = fields.Many2one("ir.model", compute="_compute_model_id", string="Model")
    model_name = fields.Char(compute="_compute_model_id")
    sequence = fields.Integer(default=10)
    name = fields.Char(required=False, help="Technical name, used in dashboards: lower case letters, digits and _ (e.g. won_revenue).")
    label = fields.Char(translate=True, help="What the widgets show; the name if empty.")
    agg = fields.Selection(AGGS, string="Aggregate", required=True, default="sum")
    field_id = fields.Many2one("ir.model.fields", string="Field", ondelete="cascade",
                               domain="[('model_id', '=', model_id), ('store', '=', True)]",
                               help="Empty to count the records.")
    where = fields.Char(string="Only records", help="A domain: the metric counts only the records that match it, whatever the filters of the page.")
    format = fields.Selection(FORMATS)

    _name_unique = models.Constraint("UNIQUE(dataset_id, name)", "A metric name is used once per dataset.")

    @api.depends("table_id.model_id", "dataset_id.model_id")
    def _compute_model_id(self):
        for rec in self:
            rec.model_id = rec.table_id.model_id or rec.dataset_id.model_id
            rec.model_name = rec.model_id.model

    @api.model_create_multi
    def create(self, vals_list):
        recs = self.browse()
        for vals in vals_list:  # a measure of a model of several tables is named after its label when nobody named it
            if not vals.get("name") and vals.get("dataset_id") and vals.get("label"):
                from .dwo_dataset_blend import slug
                taken = self.search([("dataset_id", "=", vals["dataset_id"])]).mapped("name")
                vals = dict(vals, name=slug(vals["label"], taken, "measure"))
            recs |= super().create([vals])
        return recs

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
        if self.env.context.get("dwo_skip_rebuild"):
            return
        self.dataset_id.filtered(lambda d: d.kind != "blend")._check_definition()

    def _where_list(self):
        self.ensure_one()
        try:
            value = _plain(ast.literal_eval(self.where))
        except (ValueError, SyntaxError):
            raise ValidationError(_("The condition of the metric %s is not a plain domain (dynamic values such as the current user are not supported yet).", self.name))
        if not isinstance(value, list):
            raise ValidationError(_("The condition of the metric %s must be a list.", self.name))
        return value
