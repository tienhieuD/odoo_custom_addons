# -*- coding: utf-8 -*-
import json

from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

SCHEMA = "dwo_approval_flow/1"


@tagged("post_install", "-at_install")
class TestApprovalFlow(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Users = cls.env["res.users"].with_context(no_reset_password=True)
        cls.group = cls.env["res.groups"].create({"name": "Test Legal"})
        base = {"groups_id": [(6, 0, [cls.env.ref("base.group_user").id, cls.env.ref("base.group_partner_manager").id])]}
        cls.alice = Users.create(dict(base, name="Alice", login="alice_t"))
        cls.bob = Users.create(dict(base, name="Bob", login="bob_t"))
        cls.carol = Users.create(dict(base, name="Carol", login="carol_t"))
        cls.carol.groups_id = [(4, cls.group.id)]
        cls.model = cls.env["ir.model"]._get("res.partner")
        cls.partner = cls.env["res.partner"].create({"name": "ACME", "user_id": cls.bob.id})

    # -- helpers ---------------------------------------------------------
    def _graph(self, states, transitions, **extra):
        return json.dumps(dict({"schema": SCHEMA, "states": states, "transitions": transitions}, **extra))

    def _flow(self, transitions=None, mode="custom", states=None, **vals):
        flow = self.env["dwo.approval.flow"].create(dict({
            "name": "Test flow", "model_id": self.model.id, "state_mode": mode}, **vals))
        if mode == "custom":
            flow.graph = self._graph(states or [
                {"key": "draft", "name": "Draft"}, {"key": "review", "name": "Review"},
                {"key": "done", "name": "Done"}], transitions or [])
        return flow

    def _tr(self, name, src, dst, **kw):
        return dict({"name": name, "from": src, "to": dst}, **kw)

    def _press(self, flow, tr_name, user, reason=None, partner=None):
        partner = partner or self.partner
        tr = flow.transition_ids.filtered(lambda t: t.name == tr_name)
        return self.env["dwo.approval.flow"].with_user(user).press(partner._name, partner.id, tr.id, reason)

    def _buttons(self, user):
        data = self.env["dwo.approval.flow"].with_user(user).get_buttons("res.partner", self.partner.id)
        return [b["name"] for b in data["buttons"]]

    # -- tests ------------------------------------------------------------
    def test_custom_flow_creates_field_and_states(self):
        flow = self._flow([self._tr("Submit", "draft", "review")])
        self.assertIn("x_dwo_approval_state_id", self.env["res.partner"]._fields)
        self.assertEqual(flow.state_count, 3)
        self.assertEqual(self._buttons(self.alice), ["Submit"])
        result = self._press(flow, "Submit", self.alice)
        self.assertEqual(result["status"], "done")
        self.assertEqual(self.partner.x_dwo_approval_state_id.key, "review")
        self.assertEqual(self._buttons(self.alice), [])

    def test_history_action(self):
        flow = self._flow([self._tr("Submit", "draft", "review"), self._tr("Done", "review", "done")])
        action = self.env["ir.actions.server"].search([("dwo_approval_flow_id", "=", flow.id), ("dwo_label", "=", "__history__")])
        self.assertEqual(len(action), 1)
        self.assertEqual(action.binding_view_types, "form")
        self.assertEqual(action.binding_model_id, flow.model_id)
        self._press(flow, "Submit", self.alice)
        result = action.with_user(self.bob).with_context(
            active_model="res.partner", active_ids=self.partner.ids, active_id=self.partner.id).run()
        history = self.env["dwo.approval.history"].browse(result["res_id"])
        self.assertEqual(history.record_name, "ACME")
        self.assertEqual(history.current_state, "Review")
        self.assertEqual(history.line_ids.mapped("button"), ["Submit"])
        self.assertEqual(history.line_ids.user_id, self.alice)
        # the generic server action works from any model
        generic = self.env.ref("dwo_approval_flow.server_action_dwo_approval_history")
        result = generic.with_context(active_model="res.partner", active_ids=self.partner.ids).run()
        self.assertEqual(self.env["dwo.approval.history"].browse(result["res_id"]).res_id, self.partner.id)
        flow.history_action = False
        self.assertFalse(self.env["ir.actions.server"].search([("dwo_approval_flow_id", "=", flow.id), ("dwo_label", "=", "__history__")]))

    def test_status_bar_visibility(self):
        flow = self._flow([self._tr("Submit", "draft", "review"), self._tr("Done", "review", "done")])
        self.assertTrue(all(flow.state_ids.mapped("always_visible")))
        graph = json.loads(flow.graph)
        self.assertTrue(all(s["visible"] for s in graph["states"]))
        for state in graph["states"]:
            state["visible"] = state["key"] != "done"
        flow.graph = json.dumps(graph)
        self.assertEqual(flow.state_ids.filtered(lambda s: not s.always_visible).mapped("key"), ["done"])
        data = self.env["dwo.approval.flow"].get_panel_data("res.partner", self.partner.id)
        self.assertEqual({s["key"]: s["visible"] for s in data["states"]}, {"draft": True, "review": True, "done": False})
        # an older JSON without the key keeps every state visible
        for state in graph["states"]:
            state.pop("visible")
        flow.graph = json.dumps(graph)
        self.assertTrue(all(flow.state_ids.mapped("always_visible")))

    def test_field_states_load_before_save(self):
        model = self.env["ir.model"]._get("res.partner")
        field = self.env["ir.model.fields"]._get("res.partner", "type")
        states = self.env["dwo.approval.flow"].field_states(model.id, field.id)
        keys = [s["key"] for s in states]
        self.assertIn("contact", keys)
        self.assertIn("invoice", keys)
        # a new flow saved with those states drawn: no "unknown state" error
        graph = self._graph([{"key": k, "name": s["name"]} for k, s in zip(keys, states)],
                            [self._tr("Go", keys[0], keys[1])])
        flow = self.env["dwo.approval.flow"].create({
            "name": "Field flow", "model_id": model.id, "state_mode": "field", "state_field_id": field.id, "graph": graph})
        self.assertEqual(sorted(flow.state_ids.mapped("key")), sorted(keys))
        self.assertEqual(flow.transition_count, 1)

    def test_flow_admin_without_settings(self):
        """A plain employee who only has the Approval Flow Administrator group can configure flows."""
        admin = self.env["res.users"].with_context(no_reset_password=True).create({
            "name": "Flow Admin", "login": "flow_admin_t",
            "groups_id": [(6, 0, [self.env.ref("base.group_user").id, self.env.ref("dwo_approval_flow.group_approval_manager").id])]})
        Flow = self.env["dwo.approval.flow"].with_user(admin)
        model = self.env["ir.model"].with_user(admin).search([("model", "=", "res.partner")])
        self.assertTrue(model)
        # the designer reads the fields of the model and the options of the pickers
        self.assertTrue(self.env["ir.model.fields"].with_user(admin).search([("model_id", "=", model.id)], limit=1))
        self.env["ir.actions.server"].with_user(admin).search([("model_id", "=", model.id)])
        self.env["mail.template"].with_user(admin).search([("model_id", "=", model.id)])
        self.env["res.groups"].with_user(admin).search([], limit=5).mapped("display_name")
        self.env["res.users"].with_user(admin).search([], limit=5).mapped("name")
        self.env["res.partner"].with_user(admin).fields_get()
        # own states: creates the x_ field behind the scenes
        flow = Flow.create({"name": "By admin", "model_id": model.id, "state_mode": "custom"})
        flow.graph = self._graph(
            [{"key": "draft", "name": "Draft"}, {"key": "review", "name": "Review"}, {"key": "done", "name": "Done"}],
            [self._tr("Submit", "draft", "review", list_action=True, ask_reason=True),
             self._tr("Approve", "review", "done",
                      who={"approvers": [{"type": "group", "group_id": self.group.id},
                                         {"type": "users", "user_ids": [self.alice.id]},
                                         {"type": "field", "value": "user_id"},
                                         {"type": "expr", "value": "record.user_id or user.id"}],
                           "approvals": {"mode": "any"}},
                      rules=["[('active', '=', True)]"],
                      actions=[{"type": "notify", "user_ids": [self.bob.id], "message": "ok"},
                               {"type": "update", "field": "comment", "value": "approved"}])])
        self.assertEqual(flow.state_count, 3)
        self.assertIn("x_dwo_approval_state_id", self.env["res.partner"]._fields)
        flow.read(["graph", "state_count", "transition_count"])
        flow.write({"name": "Renamed", "history_action": False})
        flow.write({"history_action": True, "replace_statusbar": True})
        # field mode on a selection
        field = self.env["ir.model.fields"].with_user(admin).search([("model", "=", "res.partner"), ("name", "=", "type")])
        Flow.field_states(model.id, field.id)
        by_field = Flow.create({"name": "By field", "model_id": model.id, "state_mode": "field", "state_field_id": field.id})
        self.assertTrue(by_field.state_ids)
        # JSON import, export and the AI button
        shared = Flow.graph_to_share(flow.graph)
        self.assertNotIn("errors", Flow.share_to_graph(model.id, "custom", False, shared, flow.id))
        self.assertNotIn("errors", Flow.ai_suggest(model.id, "custom", False, "any flow"))
        self.assertNotIn("errors", Flow.ai_suggest(model.id, "custom", False, "change it", flow.graph, flow.id))
        # a normal user can press the button the admin built
        self.partner.invalidate_cache(ids=self.partner.ids)
        self.assertIn("Submit", self._buttons(self.alice))
        # and the admin can remove the flow
        flow.unlink()
        by_field.unlink()

    def test_ai_suggest_mock(self):
        Flow = self.env["dwo.approval.flow"]
        empty = Flow.ai_suggest(self.model.id, "custom", False, "  ")
        self.assertIn("errors", empty)
        for _i in range(5):
            result = Flow.ai_suggest(self.model.id, "custom", False, "draft, review, approved")
            self.assertNotIn("errors", result, result)
            self.assertTrue(json.loads(result["graph"])["states"])
            self.assertEqual(json.loads(result["json"])["schema"], SCHEMA)
        field = self.env["ir.model.fields"]._get("res.partner", "type")
        result = Flow.ai_suggest(self.model.id, "field", field.id, "invoice then delivery")
        self.assertNotIn("errors", result, result)
        keys = {s["key"] for s in json.loads(result["graph"])["states"]}
        self.assertIn("invoice", keys)
        self.assertIn("errors", Flow.ai_suggest(self.model.id, "field", False, "x"))
        # edit mode: the current diagram goes in, the answer keeps its states and adds one
        flow = self._flow([self._tr("Submit", "draft", "review"), self._tr("Approve", "review", "done")])
        before = {s["key"] for s in json.loads(flow.graph)["states"]}
        result = Flow.ai_suggest(self.model.id, "custom", False, "add a step", flow.graph, flow.id)
        self.assertNotIn("errors", result, result)
        after = {s["key"] for s in json.loads(result["graph"])["states"]}
        self.assertTrue(before < after, (before, after))
        # the prompt holds the fixed text and the live context
        flow = Flow.new({"model_id": self.model.id, "state_mode": "custom"})
        system = Flow._ai_system_prompt() + "\n\n" + flow._ai_context()
        self.assertIn("dwo_approval_flow/1", system)
        self.assertIn("model: res.partner", system)
        self.assertIn("alice_t | Alice", system)

    def test_who_group_user_field_expression(self):
        who = lambda *a, **k: {"approvers": list(a), "approvals": k.get("approvals", {"mode": "any"})}  # noqa: E731
        flow = self._flow([
            self._tr("Submit", "draft", "review"),
            self._tr("ByGroup", "review", "done", who=who({"type": "group", "group_id": self.group.id})),
            self._tr("ByUser", "review", "done", who=who({"type": "users", "user_ids": [self.alice.id]})),
            self._tr("BySalesperson", "review", "done", who=who({"type": "field", "value": "user_id"})),
            self._tr("ByExpr", "review", "done", who=who({"type": "expr", "value": "record.user_id or user.id"})),
        ])
        self._press(flow, "Submit", self.alice)
        self.assertEqual(self._buttons(self.carol), ["ByGroup"])
        self.assertEqual(self._buttons(self.alice), ["ByUser"])
        self.assertEqual(self._buttons(self.bob), ["BySalesperson", "ByExpr"])
        with self.assertRaises(UserError):
            self._press(flow, "ByGroup", self.alice)

    def test_rule_domain_with_user(self):
        flow = self._flow([
            self._tr("Submit", "draft", "review", rules=["[('user_id', '=', user.id)]"]),
        ])
        self.assertEqual(self._buttons(self.alice), [])
        self.assertEqual(self._buttons(self.bob), ["Submit"])

    def test_votes_any_n_all(self):
        approvers = [{"type": "users", "user_ids": [self.alice.id]}, {"type": "users", "user_ids": [self.bob.id]}]
        flow = self._flow([
            self._tr("Submit", "draft", "review"),
            self._tr("Approve", "review", "done",
                     who={"approvers": approvers, "approvals": {"mode": "all"}}),
        ])
        self._press(flow, "Submit", self.carol)
        first = self._press(flow, "Approve", self.alice)
        self.assertEqual(first["status"], "waiting")
        self.assertEqual(self.partner.x_dwo_approval_state_id.key, "review")
        self.assertEqual(self._buttons(self.alice), [])  # already voted
        self.assertEqual(self._buttons(self.bob), ["Approve"])
        second = self._press(flow, "Approve", self.bob)
        self.assertEqual(second["status"], "done")
        self.assertEqual(self.partner.x_dwo_approval_state_id.key, "done")
        kinds = self.env["dwo.approval.log"].search([("res_id", "=", self.partner.id)]).mapped("kind")
        self.assertEqual(sorted(kinds), ["move", "move", "vote", "vote"])

    def test_n_votes_from_one_group(self):
        flow = self._flow([
            self._tr("Submit", "draft", "review"),
            self._tr("Approve", "review", "done", who={
                "approvers": [{"type": "users", "user_ids": [self.alice.id, self.bob.id, self.carol.id]}],
                "approvals": {"mode": "n", "n": 2}}),
        ])
        self._press(flow, "Submit", self.carol)
        self.assertEqual(self._press(flow, "Approve", self.alice)["status"], "waiting")
        panel = self.env["dwo.approval.flow"].get_panel_data("res.partner", self.partner.id)
        self.assertEqual(panel["waiting"][0]["voters"], ["Alice"])
        self.assertEqual(self._press(flow, "Approve", self.bob)["status"], "done")

    def test_reason_required(self):
        flow = self._flow([self._tr("Reject", "draft", "done", ask_reason=True)])
        with self.assertRaises(UserError):
            self._press(flow, "Reject", self.alice)
        self._press(flow, "Reject", self.alice, reason="Too expensive")
        log = self.env["dwo.approval.log"].search([
            ("kind", "=", "move"), ("res_model", "=", "res.partner"), ("res_id", "=", self.partner.id)])
        self.assertEqual(log.reason, "Too expensive")

    def test_any_state_arrow_and_two_way(self):
        flow = self._flow([
            self._tr("Submit", "draft", "review"),
            self._tr("Send back", "review", "draft"),
            self._tr("Cancel", None, "done"),
        ])
        self.assertEqual(self._buttons(self.alice), ["Submit", "Cancel"])
        self._press(flow, "Submit", self.alice)
        self.assertEqual(self._buttons(self.alice), ["Send back", "Cancel"])
        self._press(flow, "Send back", self.alice)
        self.assertEqual(self.partner.x_dwo_approval_state_id.key, "draft")

    def test_actions_update_and_log(self):
        flow = self._flow([self._tr("Submit", "draft", "review", actions=[
            {"type": "update", "field": "comment", "value": "approved by {user}"},
            {"type": "notify", "user_ids": [self.bob.id], "message": "Please look"}])])
        self._press(flow, "Submit", self.alice)
        self.assertIn("Alice", self.partner.comment)
        messages = self.partner.message_ids.mapped("body")
        self.assertTrue(any("Please look" in str(m) for m in messages))

    def test_call_method_custom_and_verify_field_mode(self):
        flow = self._flow([self._tr(
            "Archive", "draft", "done", main_step={"mode": "call_method", "method": "action_archive", "run_as": "system"})])
        self._press(flow, "Archive", self.alice)
        self.assertFalse(self.partner.active)
        self.assertEqual(self.partner.x_dwo_approval_state_id.key, "done")
        # field mode: the method does not move the "type" field, so the check must roll back
        partner = self.env["res.partner"].create({"name": "Beta", "type": "contact"})
        field = self.env["ir.model.fields"]._get("res.partner", "type")
        flow2 = self.env["dwo.approval.flow"].create({
            "name": "By type", "model_id": self.model.id, "state_mode": "field", "state_field_id": field.id,
            "active": False})
        flow2.active = True if not flow.active else flow2.active
        flow.active = False
        flow2.active = True
        states = {s.value: s for s in flow2.state_ids}
        self.assertIn("contact", states)
        tr = self.env["dwo.approval.transition"].create({
            "flow_id": flow2.id, "name": "Archive", "from_state_id": states["contact"].id,
            "to_state_id": states["invoice"].id, "move_mode": "call_method", "method_name": "action_archive"})
        with self.assertRaises(UserError):
            tr._press(partner, self.alice)
        self.assertTrue(partner.active)  # nothing changed

    def test_field_mode_set_state(self):
        field = self.env["ir.model.fields"]._get("res.partner", "type")
        flow = self.env["dwo.approval.flow"].create({
            "name": "By type", "model_id": self.model.id, "state_mode": "field", "state_field_id": field.id})
        states = {s.value: s for s in flow.state_ids}
        self.assertTrue({"contact", "invoice", "delivery"} <= set(states))
        self.env["dwo.approval.transition"].create({
            "flow_id": flow.id, "name": "To invoice", "from_state_id": states["contact"].id,
            "to_state_id": states["invoice"].id})
        partner = self.env["res.partner"].create({"name": "Gamma", "type": "contact"})
        data = self.env["dwo.approval.flow"].with_user(self.alice).get_buttons("res.partner", partner.id)
        self.assertEqual([b["name"] for b in data["buttons"]], ["To invoice"])
        self.env["dwo.approval.flow"].with_user(self.alice).press("res.partner", partner.id, data["buttons"][0]["id"])
        self.assertEqual(partner.type, "invoice")
        # field mode cannot add a state
        flow.graph = flow.graph  # no-op round trip is fine
        bad = json.loads(flow.graph)
        bad["states"].append({"key": "nope", "name": "Nope"})
        with self.assertRaises(ValidationError):
            flow.graph = json.dumps(bad)
        # a value that disappears from the field becomes "missing"
        flow.state_ids.filtered(lambda s: s.value == "other").value = "gone"
        flow.action_refresh_states()
        self.assertTrue(flow.state_ids.filtered(lambda s: s.value == "gone").missing)

    def test_validation_errors(self):
        flow = self._flow([])
        for text in ("record.user_id()", "foo.bar", "record.nope", "record.name", "record"):
            with self.assertRaises(ValidationError, msg=text):
                self.env["dwo.approval.approver"].create({
                    "transition_id": self.env["dwo.approval.transition"].create({
                        "flow_id": flow.id, "name": "x", "to_state_id": flow.state_ids[0].id}).id,
                    "kind": "expr", "value": text})
        bad = json.loads(flow.graph)
        bad["transitions"] = [{"name": "x", "from": "draft", "to": "nowhere", "color": 99}]
        with self.assertRaises(ValidationError):
            flow.graph = json.dumps(bad)

    def test_json_round_trip_and_share(self):
        flow = self._flow([
            self._tr("Submit", "draft", "review", rules=["[('name', '!=', False)]"],
                     who={"approvers": [{"type": "group", "group_id": self.group.id},
                                        {"type": "users", "user_ids": [self.alice.id]}],
                          "approvals": {"mode": "all"}},
                     actions=[{"type": "notify", "user_ids": [self.bob.id], "message": "hi"}]),
        ])
        share = json.loads(self.env["dwo.approval.flow"].graph_to_share(flow.graph))
        self.assertNotIn("id", share["states"][0])
        approvers = share["transitions"][0]["who"]["approvers"]
        self.assertEqual(approvers[1]["value"], "alice_t")
        result = self.env["dwo.approval.flow"].share_to_graph(
            self.model.id, "custom", False, json.dumps(share), flow.id)
        self.assertNotIn("errors", result, result)
        other = self._flow([], states=[{"key": "x", "name": "X"}], active=False)
        other.graph = result["graph"]
        self.assertEqual(other.state_count, 3)
        self.assertEqual(other.transition_ids.approver_ids.mapped("kind"), ["users", "users"][:0] or ["group", "users"])
        bad = self.env["dwo.approval.flow"].share_to_graph(
            self.model.id, "custom", False, json.dumps(dict(share, schema="x")), flow.id)
        self.assertIn("errors", bad)
        broken = self.env["dwo.approval.flow"].share_to_graph(self.model.id, "custom", False, "{nope", flow.id)
        self.assertIn("errors", broken)

    def test_form_header_injection(self):
        flow = self._flow([self._tr("Submit", "draft", "review")])
        view = self.env["res.partner"].fields_view_get(view_type="form")
        self.assertIn("dwo_approval_buttons", view["arch"])
        self.assertIn("dwo_approval_panel", view["arch"])  # the partner form has no status bar
        flow.replace_statusbar = True
        view = self.env["res.partner"].fields_view_get(view_type="form")
        self.assertIn("dwo_approval_panel", view["arch"])
        flow.active = False
        view = self.env["res.partner"].fields_view_get(view_type="form")
        self.assertNotIn("dwo_approval_buttons", view["arch"])

    def test_any_state_arrow_hidden_in_its_target(self):
        flow = self._flow([self._tr("Hold", None, "review")])
        self.assertEqual(self._buttons(self.alice), ["Hold"])
        self._press(flow, "Hold", self.alice)
        self.assertEqual(self._buttons(self.alice), [])

    def test_several_flows_routed_by_domain(self):
        first = self._flow([], name="For ACME", domain="[('name', '=', 'ACME')]", sequence=1)
        second = self._flow([], name="For the rest", sequence=2)
        other = self.env["res.partner"].create({"name": "Other"})
        Flow = self.env["dwo.approval.flow"]
        self.assertEqual(Flow._flow_of(self.partner), first)
        self.assertEqual(Flow._flow_of(other), second)
        first.active = False
        self.assertEqual(Flow._flow_of(self.partner), second)

    def test_describe_domains(self):
        texts = self.env["dwo.approval.flow"].describe_domains(
            "res.partner", ["[('employee', '=', False)]", "[('credit_limit', '>', 1000)]", "[]"])
        self.assertEqual(texts[0], "Employee is not set")
        self.assertTrue(texts[1].endswith("greater than 1000"))
        self.assertEqual(texts[2], "all records")

    def _archive_flow(self, guard=None, **kw):
        step = {"mode": "call_method", "method": "action_archive", "run_as": "system"}
        if guard:
            step["guard"] = guard
        return self._flow([self._tr(
            "Archive", "draft", "done", who={"approvers": [{"type": "users", "user_ids": [self.alice.id]}],
                                             "approvals": {"mode": "any"}}, main_step=step, **kw)])

    def test_guard_goes_through_the_arrow(self):
        flow = self._archive_flow()  # protected by default
        self.assertIn(("res.partner", "action_archive"), self.env["dwo.approval.flow"]._guard_methods())
        partner = self.env["res.partner"].create({"name": "Gamma"})
        Flow = self.env["dwo.approval.flow"].with_user(self.bob)
        with self.assertRaises(UserError):
            Flow._guard_rpc("res.partner", "action_archive", partner.ids)
        self.assertTrue(partner.active)
        free, result = self.env["dwo.approval.flow"].with_user(self.alice)._guard_rpc(
            "res.partner", "action_archive", partner.ids)
        self.assertEqual(free, [])  # the arrow took the press: the original method does not run again
        self.assertFalse(partner.active)  # the arrow called it as system
        self.assertEqual(partner.x_dwo_approval_state_id.key, "done")
        # a document the flow does not govern keeps the original behaviour
        flow.domain = "[('name', '=', 'Gamma')]"
        other = self.env["res.partner"].create({"name": "Other"})
        self.assertEqual(Flow._guard_rpc("res.partner", "action_archive", other.ids), (other.ids, None))

    def test_guard_can_be_switched_off(self):
        flow = self._archive_flow(guard="none")
        self.assertNotIn(("res.partner", "action_archive"), self.env["dwo.approval.flow"]._guard_methods())
        flow.transition_ids.guard_scope = "direct"
        self.assertIn(("res.partner", "action_archive"), self.env["dwo.approval.flow"]._guard_methods())
        data = json.loads(flow.graph)
        self.assertEqual(data["transitions"][0]["main_step"]["guard"], "direct")
        flow.graph = json.dumps(data)  # the designer saves it back unchanged
        self.assertEqual(flow.transition_ids.guard_scope, "direct")

    def test_state_field_cannot_be_written_directly(self):
        flow = self._flow([self._tr("Submit", "draft", "review")])
        review = flow.state_ids.filtered(lambda s: s.key == "review")
        with self.assertRaises(UserError):
            self.partner.with_user(self.alice).write({"x_dwo_approval_state_id": review.id})
        self._press(flow, "Submit", self.alice)
        self.assertEqual(self.partner.x_dwo_approval_state_id, review)
        self.partner.sudo().write({"x_dwo_approval_state_id": flow.state_ids[0].id})  # system code may

    def test_list_action(self):
        flow = self._flow([self._tr("Submit", "draft", "review", list_action=True)])
        action = self.env["ir.actions.server"].search([("dwo_approval_flow_id", "=", flow.id), ("dwo_label", "!=", "__history__")])
        self.assertEqual(action.name, "Test flow: Submit")
        self.assertEqual(action.binding_model_id, self.model)
        other = self.env["res.partner"].create({"name": "Other"})
        other.x_dwo_approval_state_id = flow.state_ids.filtered(lambda s: s.key == "done")
        result = self.env["dwo.approval.flow"].with_user(self.alice).press_label(
            flow.id, "Submit", (self.partner | other).ids)
        self.assertEqual(self.partner.x_dwo_approval_state_id.key, "review")
        self.assertEqual(other.x_dwo_approval_state_id.key, "done")  # not in "draft": skipped
        self.assertIn("1 done", result["params"]["message"])
        flow.transition_ids.list_action = False
        flow._sync_list_actions()
        self.assertFalse(self.env["ir.actions.server"].search([("dwo_approval_flow_id", "=", flow.id), ("dwo_label", "!=", "__history__")]))

    def test_test_wizard(self):
        flow = self._flow([self._tr("Submit", "draft", "review"), self._tr(
            "Approve", "review", "done", who={"approvers": [{"type": "users", "user_ids": [self.alice.id]}],
                                             "approvals": {"mode": "any"}})])
        wizard = self.env["dwo.approval.test"].create({
            "flow_id": flow.id, "res_id": self.partner.id, "user_id": self.alice.id})
        self.assertIn("Submit", wizard.result)
        self.assertIn("Shown", wizard.result)
        self._press(flow, "Submit", self.alice)
        wizard.invalidate_cache(ids=wizard.ids)
        self.assertIn("Review", wizard.result)
        wizard.user_id = self.bob
        self.assertIn("not one of the approvers", wizard.result)

    def test_security(self):
        flow = self._flow([self._tr("Submit", "draft", "review")])
        with self.assertRaises(AccessError):
            flow.with_user(self.alice).write({"name": "hack"})
        with self.assertRaises(AccessError):
            self.env["dwo.approval.log"].with_user(self.alice).search([])
