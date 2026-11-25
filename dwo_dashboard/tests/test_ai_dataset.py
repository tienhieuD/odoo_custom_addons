# -*- coding: utf-8 -*-
import copy
import json

from odoo.exceptions import AccessError, UserError

from .test_blend import BlendCase, definition

MODELS = ["orm:ir.attachment", "orm:res.currency.rate"]


class AIDatasetCase(BlendCase):

    def setUp(self):
        super().setUp()
        self.calls, self.answers = [], []
        ai_class = self.env.registry["dwo.dashboard.ai"]

        def fake(model, prompt, history):
            self.calls.append((prompt, history))
            return self.answers.pop(0)
        self.patch(ai_class, "_complete_olg", fake)
        self.plain = self.env["res.users"].create({"name": "Plain", "login": "ai_plain", "group_ids": [
            (6, 0, [self.env.ref("base.group_user").id])]})

    def answer(self, value):
        self.answers.append(value if isinstance(value, str) else json.dumps(value))

    def ai(self, user=None):
        return self.env["dwo.dashboard.ai"].with_user(user or self.manager)

    def prompts(self):
        return "\n".join(p + json.dumps(h) for p, h in self.calls)


class TestProposeBlend(AIDatasetCase):

    def test_a_good_blend_is_a_proposal_and_nothing_is_saved(self):
        before = self.env["dwo.dataset"].search_count([])
        self.answer(definition())
        result = self.ai().propose_dataset("blend", "files and rates by month", MODELS)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["definition"]["code"], "files_rates")
        self.assertEqual(self.env["dwo.dataset"].search_count([]), before)
        prompt = self.calls[0][0]
        self.assertIn("dwo-dataset/1", prompt)
        self.assertIn("file_size", prompt)          # field names are described...
        self.assertNotIn("Bl 0", prompt)            # ...records never are

    def test_an_invalid_answer_is_corrected_once(self):
        bad = copy.deepcopy(definition())
        bad["metrics"][0]["source"] = "nowhere"
        self.answer(bad)
        self.answer(definition())
        result = self.ai().propose_dataset("blend", "files and rates", MODELS)
        self.assertTrue(result["ok"] and result["retried"], result)
        self.assertIn("nowhere", self.calls[1][0])  # the second call is told what was wrong

    def test_garbage_twice_is_a_clear_failure(self):
        self.answer("I cannot do that")
        self.answer("{ nope")
        result = self.ai().propose_dataset("blend", "files and rates", MODELS)
        self.assertFalse(result["ok"])
        self.assertTrue(result["retried"] and result["message"])

    def test_only_a_manager_may_ask(self):
        with self.assertRaises(AccessError):
            self.ai(self.plain).propose_dataset("blend", "files and rates", MODELS)
        self.assertEqual(self.calls, [])

    def test_a_model_the_manager_cannot_read_is_never_sent(self):
        with self.assertRaises(UserError):
            self.ai().propose_dataset("blend", "x", ["orm:ir.config_parameter", "orm:res.currency.rate"])
        self.assertEqual(self.calls, [])

    def test_two_models_are_needed(self):
        with self.assertRaises(UserError):
            self.ai().propose_dataset("blend", "x", ["orm:res.currency.rate"])

    def test_the_switch_turns_it_off(self):
        self.env["ir.config_parameter"].sudo().set_param("dwo_dashboard.ai_enabled", "0")
        with self.assertRaises(UserError):
            self.ai().propose_dataset("blend", "x", MODELS)
        self.assertEqual(self.calls, [])

    def test_the_current_definition_is_sent_only_when_given(self):
        self.answer(definition())
        self.ai().propose_dataset("blend", "files and rates", MODELS)
        self.assertNotIn("CURRENT DEFINITION", self.calls[0][0])
        self.answer(definition())
        self.ai().propose_dataset("blend", "files and rates", MODELS, '{"code": "mine"}')
        self.assertIn('CURRENT DEFINITION', self.calls[1][0])


class TestProposeMetrics(AIDatasetCase):

    def test_metrics_of_a_model(self):
        self.answer({"metrics": [{"name": "big_rates", "label": "Big", "agg": "count", "where": [["rate", ">", 1]]},
                                 {"name": "top_rate", "agg": "max", "field": "rate"}]})
        result = self.ai().propose_dataset("orm", "rates above one, and the highest", ["res.currency.rate"])
        self.assertTrue(result["ok"], result)
        self.assertEqual([m["name"] for m in result["metrics"]], ["big_rates", "top_rate"])

    def test_a_field_that_does_not_exist_goes_back_to_the_model(self):
        self.answer({"metrics": [{"name": "x", "agg": "sum", "field": "no_such_field"}]})
        self.answer({"metrics": [{"name": "x", "agg": "sum", "field": "rate"}]})
        result = self.ai().propose_dataset("orm", "sum of rates", ["orm:res.currency.rate"])
        self.assertTrue(result["ok"] and result["retried"], result)
        self.assertIn("/metrics/0/field", self.calls[1][0])


class TestProposeSql(AIDatasetCase):

    def test_the_schema_sent_never_has_a_denied_table_or_a_credential_column(self):
        self.env.cr.execute("ALTER TABLE res_company ADD COLUMN dwo_probe_api_key varchar")  # rolled back with the test
        text, tables = self.ai()._describe_tables(["res_users", "ir_config_parameter", "res_company", "res_partner"])
        self.assertEqual(tables, ["res_company", "res_partner"])
        self.assertNotIn("res_users", text)
        self.assertNotIn("ir_config_parameter", text)
        self.assertNotIn("dwo_probe_api_key", text)
        self.assertIn("res_company(", text)

    def test_tables_are_found_in_the_request_when_none_is_named(self):
        text, tables = self.ai()._describe_tables([], "the total of res partner by country, and the res_company")
        self.assertIn("res_partner", tables)
        self.assertIn("res_company", tables)

    def test_a_query_is_a_proposal(self):
        self.answer({"code": "partner_names", "label": "Partner names", "query": "SELECT id, name AS partner FROM res_partner WHERE company_id = %(company_id)s;"})
        result = self.ai().propose_dataset("sql", "the partners of my company", ["res_partner"])
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["params"], ["company_id"])
        self.assertNotIn(";", result["query"])
        self.assertIn("res_partner(", self.calls[0][0])

    def test_a_query_that_is_not_one_select_goes_back_to_the_model(self):
        self.answer({"query": "SELECT 1; DROP TABLE res_partner"})
        self.answer({"query": "SELECT id AS partner_id FROM res_partner"})
        result = self.ai().propose_dataset("sql", "partners", ["res_partner"])
        self.assertTrue(result["ok"] and result["retried"], result)
        self.assertEqual(result["code"], "ai_query")

    def test_without_tables_the_manager_is_asked_to_name_them(self):
        with self.assertRaises(UserError):
            self.ai().propose_dataset("sql", "xyz qwerty", [])
        self.assertEqual(self.calls, [])


class TestWizard(AIDatasetCase):

    def wizard(self, **vals):
        return self.env["dwo.ai.dataset.wizard"].with_user(self.manager).create(dict({"request": "files and rates"}, **vals))

    def test_use_it_creates_the_blend_and_a_second_one_gets_another_code(self):
        for expected in ("files_rates_2", "files_rates_3"):  # the setUp of the blend tests already has files_rates
            self.answer(definition())
            w = self.wizard(kind="blend", model_ids=[(6, 0, self.env["ir.model"]._get("ir.attachment").ids + self.env["ir.model"]._get("res.currency.rate").ids)])
            w.action_ask()
            self.assertTrue(w.result_json and "files_rates" in w.result_text, w.message)
            self.assertFalse(self.env["dwo.dataset"].search([("ref", "=", "blend:" + expected)]))
            w.action_apply()
            self.assertTrue(self.env["dwo.dataset"].search([("ref", "=", "blend:" + expected)]))

    def test_a_failed_answer_shows_the_problems_and_cannot_be_used(self):
        self.answer("no")
        self.answer("no")
        w = self.wizard(kind="blend", model_ids=[(6, 0, self.env["ir.model"]._get("ir.attachment").ids + self.env["ir.model"]._get("res.currency.rate").ids)])
        w.action_ask()
        self.assertTrue(w.message)
        with self.assertRaises(UserError):
            w.action_apply()

    def test_metrics_are_added_and_replaced_by_name(self):
        model = self.env["ir.model"]._get("res.currency.rate")
        self.answer({"metrics": [{"name": "top_rate", "label": "Top", "agg": "max", "field": "rate"}]})
        w = self.wizard(kind="orm", model_ids=[(6, 0, model.ids)])
        w.action_ask()
        w.action_apply()
        dataset = self.env["dwo.dataset"].search([("model_id", "=", model.id)])
        self.assertEqual(dataset.metric_ids.mapped("name"), ["top_rate"])
        self.answer({"metrics": [{"name": "top_rate", "label": "Highest", "agg": "avg", "field": "rate"}]})
        w = self.wizard(kind="orm", dataset_id=dataset.id, model_ids=[(6, 0, model.ids)])
        w.action_ask()
        w.action_apply()
        self.assertEqual((len(dataset.metric_ids), dataset.metric_ids.agg), (1, "avg"))

    def test_a_sql_query_creates_a_draft_with_the_default_groups(self):
        self.answer({"code": "partner_names", "label": "Partner names", "query": "SELECT id, name AS partner FROM res_partner"})
        w = self.wizard(kind="sql", tables="res_partner")
        w.action_ask()
        self.assertIn("SELECT", w.result_text)
        w.action_apply()
        dataset = self.env["dwo.dataset"].search([("ref", "=", "sql:partner_names")])
        self.assertTrue(dataset)
        self.assertEqual(dataset.with_user(self.manager).sql_group_ids.mapped("name") != [], True)

    def test_a_plain_user_cannot_open_the_wizard(self):
        with self.assertRaises(AccessError):
            self.env["dwo.ai.dataset.wizard"].with_user(self.plain).create({"request": "x"})
