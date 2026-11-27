# -*- coding: utf-8 -*-
import json

from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form

from .test_blend import BlendCase, definition


class TestBlendLines(BlendCase):
    """A model of several tables is edited as lines that map one to one to the document that is stored and run."""

    def test_a_document_gives_its_lines(self):
        ds = self.dataset
        self.assertFalse(ds.draft)
        self.assertEqual([(t.name, t.model_id.model) for t in ds.table_ids], [("files", "ir.attachment"), ("rates", "res.currency.rate")])
        self.assertEqual(ds.table_ids[0].where, "[['name', 'like', 'Bl ']]")
        self.assertEqual([d.name for d in ds.dimension_ids], ["month", "who"])
        self.assertEqual({m.table_id.name: m.field_path for m in ds.dimension_ids[0].map_ids}, {"files": "create_date", "rates": "name"})
        self.assertEqual([(m.name, m.table_id.name, m.agg, m.field_id.name) for m in ds.metric_ids],
                         [("bytes", "files", "sum", "file_size"), ("avg_bytes", "files", "avg", "file_size"),
                          ("rates", "rates", "count", False), ("big_rates", "rates", "count", False)])

    def test_lines_and_document_are_the_same_thing(self):
        self.assertEqual(self.dataset._blend_document(), definition())  # document -> lines -> document, key for key
        self.assertEqual(json.loads(self.dataset.definition_text), definition())

    def test_editing_a_line_writes_the_document_the_engine_runs(self):
        ds = self.dataset
        ds.write({"metric_ids": [(1, ds.metric_ids[0].id, {"label": "Octets"})]})
        self.assertEqual(json.loads(ds.definition_text)["metrics"][0]["label"], "Octets")
        self.assertEqual(ds._definition()["metrics"][0]["label"], "Octets")
        self.run_w(self.widget())  # still runs
        ds.write({"dimension_ids": [(1, ds.dimension_ids[1].id, {"label": "Author"})]})
        self.assertEqual(json.loads(ds.definition_text)["dimensions"][1]["label"], "Author")
        map_line = ds.dimension_ids[0].map_ids.filtered(lambda m: m.table_id.name == "rates")
        ds.write({"dimension_ids": [(1, ds.dimension_ids[0].id, {"map_ids": [(1, map_line.id, {"field_path": "create_date"})]})]})
        self.assertEqual(json.loads(ds.definition_text)["dimensions"][0]["map"]["rates"], "create_date")
        # the other way round: a document written whole writes the lines again
        ds.write({"definition_text": json.dumps(definition())})
        self.assertEqual(ds.metric_ids[0].label, "Bytes")
        self.assertEqual(ds._blend_document(), definition())

    def test_a_line_that_breaks_the_document_is_refused(self):
        ds = self.dataset
        with self.assertRaises(ValidationError):  # a sum without a field
            ds.write({"metric_ids": [(1, ds.metric_ids[0].id, {"field_id": False})]})
        with self.assertRaises(ValidationError):  # a date dimension mapped to a text field
            ds.write({"dimension_ids": [(1, ds.dimension_ids[0].id, {"map_ids": [
                (1, ds.dimension_ids[0].map_ids[0].id, {"field_path": "name"})]})]})

    def test_a_plain_write_does_not_rebuild_the_document(self):
        """An older blend has its document but no lines: renaming it must not turn the document into an empty one."""
        ds = self.dataset
        before = ds.definition_text
        self.env.cr.execute("DELETE FROM dwo_dataset_table WHERE dataset_id = %s", [ds.id])
        self.env.cr.execute("DELETE FROM dwo_dataset_dimension WHERE dataset_id = %s", [ds.id])
        self.env.cr.execute("DELETE FROM dwo_dataset_metric WHERE dataset_id = %s", [ds.id])
        self.env.invalidate_all()
        ds.write({"label": "Renamed"})
        self.assertEqual(ds.definition_text, before)
        ds._sync_from_document()  # what the upgrade does
        self.assertEqual(ds._blend_document(), dict(definition(), label="Renamed"))

    def test_lines_and_document_are_not_written_together(self):
        with self.assertRaises(UserError):
            self.dataset.write({"definition_text": json.dumps(definition()), "metric_ids": [(5,)]})

    def test_a_draft_is_saved_but_dashboards_cannot_use_it(self):
        Model = self.env["ir.model"]
        ds = self.env["dwo.dataset"].create({"kind": "blend", "code": "draft_one", "label": "Draft", "table_ids": [
            (0, 0, {"model_id": Model._get("ir.attachment").id}), (0, 0, {"model_id": Model._get("res.currency.rate").id})]})
        self.assertTrue(ds.draft)
        self.assertEqual([t.name for t in ds.table_ids], ["ir_attachment", "res_currency_rate"])
        self.assertFalse(ds._definition())
        self.assertFalse(self.env["dwo.dashboard.spec"]._dwo_resolve_dataset("blend:draft_one"))
        self.assertNotIn("blend:draft_one", {d["ref"] for d in self.env["dwo.dashboard.explore"].with_user(self.admin).list_datasets()})
        with self.assertRaises(UserError):
            ds.action_check()
        files, rates = ds.table_ids
        ds.write({"dimension_ids": [(0, 0, {"label": "Date", "kind": "date", "map_ids": [
            (0, 0, {"table_id": files.id, "field_path": "create_date"}), (0, 0, {"table_id": rates.id, "field_path": "name"})]})]})
        self.assertTrue(ds.draft)  # no measure yet
        ds.write({"metric_ids": [(0, 0, {"label": "Files", "table_id": files.id, "agg": "count"})]})
        self.assertFalse(ds.draft)
        self.assertEqual(ds.metric_ids.name, "files")  # named after its label
        self.assertTrue(self.env["dwo.dashboard.spec"]._dwo_resolve_dataset("blend:draft_one"))
        self.assertIn("blend:draft_one", {d["ref"] for d in self.env["dwo.dashboard.explore"].with_user(self.admin).list_datasets()})

    def test_suggested_dimensions_are_the_fields_the_tables_share(self):
        Model = self.env["ir.model"]
        ds = self.env["dwo.dataset"].create({"kind": "blend", "code": "suggest", "label": "S", "table_ids": [
            (0, 0, {"model_id": Model._get("ir.attachment").id}), (0, 0, {"model_id": Model._get("res.currency.rate").id})]})
        ds.action_suggest_dimensions()
        self.assertIn("Company", ds.dimension_ids.mapped("label"))
        company = ds.dimension_ids.filtered(lambda d: d.label == "Company")
        self.assertEqual(sorted(company.map_ids.mapped("field_path")), ["company_id", "company_id"])
        self.assertEqual(company.kind, "many2one")

    def test_the_form_adds_tables_then_dimensions_then_measures(self):
        Model = self.env["ir.model"]
        with Form(self.env["dwo.dataset"]) as form:
            form.kind = "blend"
            form.code = "by_form"
            form.label = "By form"
            for model in ("ir.attachment", "res.currency.rate"):
                with form.table_ids.new() as line:
                    line.model_id = Model._get(model)
        ds = form.record
        self.assertTrue(ds.draft)
        with Form(ds) as form:
            with form.dimension_ids.new() as line:
                line.label = "Date"
                line.kind = "date"
                self.assertEqual(len(line.map_ids), 2)  # one line per table: the person only picks the fields
                for index, path in enumerate(("create_date", "name")):
                    with line.map_ids.edit(index) as m:
                        m.field_path = path
            with form.metric_ids.new() as line:
                line.label = "Files"
                line.table_id = ds.table_ids[0]
                line.agg = "count"
        self.assertFalse(ds.draft)
        self.assertEqual(json.loads(ds.definition_text)["metrics"], [{"name": "files", "label": "Files", "source": "ir_attachment", "agg": "count"}])

    def test_a_document_written_onto_a_draft_completes_it(self):
        """The assistant's "Use it" writes a whole document onto a blend the person started with tables."""
        Model = self.env["ir.model"]
        ds = self.env["dwo.dataset"].create({"kind": "blend", "code": "files_rates_2", "label": "Draft", "table_ids": [
            (0, 0, {"model_id": Model._get("ir.attachment").id}), (0, 0, {"model_id": Model._get("res.currency.rate").id})]})
        self.assertTrue(ds.draft)
        ds.write({"definition_text": json.dumps(definition(code="files_rates_2"))})
        self.assertFalse(ds.draft)
        self.assertEqual(ds._blend_document(), definition(code="files_rates_2", label="Draft"))
        self.assertTrue(self.env["dwo.dashboard.spec"]._dwo_resolve_dataset("blend:files_rates_2"))
        with self.assertRaises(ValidationError):  # and a bad document is refused, draft or not
            ds.write({"definition_text": json.dumps(definition(code="files_rates_2", sources=definition()["sources"][:1]))})

    def test_a_blend_with_nothing_yet_is_a_draft(self):
        ds = self.env["dwo.dataset"].create({"kind": "blend", "code": "empty_one", "label": "Empty"})
        self.assertTrue(ds.draft)
        self.assertFalse(ds._definition())
