# -*- coding: utf-8 -*-
import copy
import json
from unittest.mock import patch

from odoo.exceptions import AccessError, UserError
from odoo.tests.common import TransactionCase

from .test_sharing import SharingCase


def new_widget(wid="w9", **extra):
    return dict({"id": wid, "type": "kpi", "dataset": "orm:res.partner", "x": 3, "y": 0, "w": 3, "h": 2,
                 "wells": {"value": {"agg": "count"}}}, **extra)


class AICase(SharingCase):

    def setUp(self):
        super().setUp()
        self.AI = self.env["dwo.dashboard.ai"]
        self.calls = []
        self.answers = []
        ai_class = self.env.registry["dwo.dashboard.ai"]
        self.real_gateway = ai_class._complete_olg

        def fake(model, prompt, history):
            self.calls.append((prompt, history))
            return self.answers.pop(0)
        self.patch(ai_class, "_complete_olg", fake)

    def ai(self, user):
        return self.as_(user, "dwo.dashboard.ai")

    def spec_plus(self, *widgets):
        spec = copy.deepcopy(self.page.spec)
        spec["widgets"] += list(widgets)
        return spec

    def answer(self, value):
        self.answers.append(value if isinstance(value, str) else json.dumps(value))

    def propose(self, user, request="add a count", datasets=None):
        return self.ai(user).propose(self.page_id, request, datasets)


class TestAnswers(AICase):

    def test_a_good_answer_is_a_proposal_and_nothing_is_saved(self):
        self.answer(self.spec_plus(new_widget()))
        result = self.propose(self.owner)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["diff"], {"added": ["w9"], "removed": [], "changed": [], "page_changed": False})
        self.assertEqual([w["id"] for w in self.page.spec["widgets"]], ["k"])  # the page itself is untouched
        self.assertEqual(self.page.revision, self.page.revision)

    def test_the_draft_in_the_editor_is_what_the_assistant_works_on(self):
        draft = self.spec_plus(new_widget("draft1", x=6))  # an unsaved widget
        self.answer(dict(draft, widgets=draft["widgets"] + [new_widget("w9", x=9)]))
        result = self.ai(self.owner).propose(self.page_id, "one more", None, draft)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["diff"]["added"], ["w9"])  # not "draft1": it was already there
        self.assertIn('"id":"draft1"', self.calls[0][0])

    def test_fences_and_words_around_the_json_are_ignored(self):
        self.answer("Here is your page:\n```json\n%s\n```\nAnything else?" % json.dumps(self.spec_plus(new_widget())))
        self.assertTrue(self.propose(self.owner)["ok"])

    def test_a_wrong_answer_gets_a_second_chance_with_the_errors(self):
        self.answer(self.spec_plus(dict(new_widget(), type="spaceship")))
        self.answer(self.spec_plus(new_widget()))
        result = self.propose(self.owner)
        self.assertTrue(result["ok"] and result["retried"], result)
        self.assertEqual(len(self.calls), 2)
        prompt, history = self.calls[1]
        self.assertIn("/widgets/1/type", prompt)           # told where it went wrong
        self.assertEqual([m["role"] for m in history], ["user", "assistant"])  # and what it said

    def test_garbage_twice_is_an_error_not_a_page(self):
        self.answer("I cannot do that.")
        self.answer("{not json")
        result = self.propose(self.owner)
        self.assertFalse(result["ok"])
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(self.page.spec["widgets"][0]["id"], "k")

    def test_a_widget_laid_over_another_one_is_moved_to_the_bottom(self):
        self.answer(self.spec_plus(new_widget(x=0, y=0, w=3, h=2)))  # on top of "k"
        result = self.propose(self.owner)
        self.assertTrue(result["ok"], result)
        self.assertEqual(len(self.calls), 1)
        moved = next(w for w in result["spec"]["widgets"] if w["id"] == "w9")
        self.assertEqual((moved["x"], moved["y"]), (0, 2))  # below "k", which is 2 rows high

    def test_a_sort_by_something_that_is_not_a_measure_is_dropped(self):
        self.answer(self.spec_plus(new_widget(order=[{"measure": "id:count", "dir": "desc"}])))
        result = self.propose(self.owner)
        self.assertTrue(result["ok"], result)
        self.assertNotIn("order", next(w for w in result["spec"]["widgets"] if w["id"] == "w9"))

    def test_what_the_caller_may_not_write_is_refused_even_when_the_model_says_so(self):
        self.patch(self.env["res.partner"]._fields["color"], "groups", "base.group_system")
        widget = new_widget(wells={"value": {"field": "color", "agg": "sum"}})
        self.answer(self.spec_plus(widget))
        self.answer(self.spec_plus(widget))
        result = self.propose(self.editor)
        self.assertFalse(result["ok"], result)  # validated as the person who asked, not as the service

    def test_the_diff_names_what_changed(self):
        spec = self.spec_plus(new_widget())
        spec["widgets"][0]["title"] = "Renamed"
        self.answer(spec)
        self.assertEqual(self.propose(self.owner)["diff"], {"added": ["w9"], "removed": [], "changed": ["k"], "page_changed": False})


class TestWhatIsSentAndWho(AICase):

    def test_only_people_who_can_edit_the_page_may_ask(self):
        for user in (self.viewer, self.member, self.stranger, self.admin):
            with self.assertRaises(AccessError, msg=user.login):
                self.propose(user)
        self.answer(self.spec_plus(new_widget()))
        self.assertTrue(self.propose(self.editor)["ok"])

    def test_the_assistant_can_be_switched_off_for_a_database(self):
        self.env["ir.config_parameter"].sudo().set_param("dwo_dashboard.ai_enabled", "0")
        self.assertFalse(self.ai(self.owner).get_status()["enabled"])
        with self.assertRaises(UserError):
            self.propose(self.owner)
        self.assertEqual(self.calls, [])  # nothing was sent

    def test_the_request_is_bounded(self):
        for text in ("", "   ", "x" * 1501):
            with self.assertRaises(UserError):
                self.propose(self.owner, text)

    def test_the_prompt_holds_the_format_the_page_and_the_request_but_no_record(self):
        self.env["res.partner"].create({"name": "ZZ Secret Customer Name"})
        prompt = self.ai(self.owner)._build_prompt(self.page.spec, "show me XYZ-REQUEST", ["orm:res.partner"])
        for part in ("dwo-dashboard/1", "XYZ-REQUEST", '"id":"k"', "orm:res.partner", "group by:", "Visual types"):
            self.assertIn(part, prompt)
        self.assertNotIn("ZZ Secret Customer Name", prompt)

    def test_the_prompt_names_only_fields_the_caller_can_read(self):
        self.patch(self.env["res.partner"]._fields["color"], "groups", "base.group_system")
        text = lambda user: self.ai(user)._describe_datasets(["orm:res.partner"])
        self.assertNotIn("color(", text(self.owner))
        self.assertIn("color(", text(self.admin))
        self.assertEqual(self.ai(self.stranger)._describe_datasets(["orm:no.such.model"]), "")

    def test_the_provider_and_the_key_are_settings_of_administrators(self):
        Settings = self.env["res.config.settings"]
        with self.assertRaises(AccessError):
            Settings.with_user(self.owner).create({"dwo_ai_provider": "openai", "dwo_ai_api_key": "sk-secret"}).execute()
        settings = Settings.with_user(self.admin).create({"dwo_ai_provider": "openai", "dwo_ai_api_key": "  sk-secret  "})
        settings.execute()
        self.assertEqual(self.env["ir.config_parameter"].sudo().get_param("dwo_dashboard.ai_api_key"), "sk-secret")
        values = Settings.with_user(self.admin).get_values()
        self.assertFalse(values["dwo_ai_api_key"])      # never sent back to a browser
        self.assertTrue(values["dwo_ai_key_set"])
        status = self.ai(self.owner).get_status()
        self.assertNotIn("sk-secret", json.dumps(status))
        self.assertEqual((status["provider"], status["configured"]), ("openai", True))

    def test_openai_provider_uses_the_key_and_never_repeats_it(self):
        self.env["ir.config_parameter"].sudo().set_param("dwo_dashboard.ai_provider", "openai")
        self.env["ir.config_parameter"].sudo().set_param("dwo_dashboard.ai_api_key", "sk-secret")
        sent = {}

        class Reply:
            def raise_for_status(self):
                pass

            def json(self):
                return {"choices": [{"message": {"content": json.dumps(spec)}}]}
        spec = self.spec_plus(new_widget())

        def post(url, headers=None, json=None, timeout=None):
            sent.update(url=url, headers=headers, body=json)
            return Reply()
        with patch("odoo.addons.dwo_dashboard.models.dwo_dashboard_ai.requests.post", post):
            self.assertTrue(self.propose(self.owner)["ok"])
        self.assertEqual(sent["headers"], {"Authorization": "Bearer sk-secret"})
        self.assertEqual(sent["body"]["temperature"], 0)
        self.assertNotIn("sk-secret", json.dumps(sent["body"]))
        import requests

        def failing(*a, **k):
            raise requests.ConnectionError("boom sk-secret")
        with patch("odoo.addons.dwo_dashboard.models.dwo_dashboard_ai.requests.post", failing):
            with self.assertRaises(UserError) as ctx:
                self.propose(self.owner)
        self.assertNotIn("sk-secret", str(ctx.exception))

    def test_a_provider_without_a_key_says_so(self):
        self.env["ir.config_parameter"].sudo().set_param("dwo_dashboard.ai_provider", "openai")
        self.assertFalse(self.ai(self.owner).get_status()["configured"])
        with self.assertRaises(UserError):
            self.propose(self.owner)


class TestOdooGateway(AICase):

    def run_gateway(self, response):
        ai_class = self.env.registry["dwo.dashboard.ai"]
        self.patch(ai_class, "_complete_olg", self.real_gateway)  # the real one, over a fake network
        sent = {}

        def rpc(url, method="call", params=None, timeout=15):
            sent.update(url=url, params=params)
            return response
        with patch("odoo.addons.iap.tools.iap_tools.iap_jsonrpc", rpc):
            return self.env["dwo.dashboard.ai"]._complete_olg("PROMPT", [{"role": "user", "content": "x"}]), sent

    def test_success(self):
        text, sent = self.run_gateway({"status": "success", "content": "{}"})
        self.assertEqual(text, "{}")
        self.assertTrue(sent["url"].endswith("/api/olg/1/chat"))
        self.assertEqual(sent["params"]["prompt"], "PROMPT")
        self.assertEqual(set(sent["params"]), {"prompt", "conversation_history", "database_id"})  # nothing else leaves

    def test_the_limits_of_the_service_become_messages(self):
        for status, word in (("error_prompt_too_long", "too long"), ("limit_call_reached", "limit"), ("anything", "could not answer")):
            with self.assertRaises(UserError, msg=status) as ctx:
                self.run_gateway({"status": status})
            self.assertIn(word, str(ctx.exception))
