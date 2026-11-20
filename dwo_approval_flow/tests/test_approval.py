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
        base = {"group_ids": [(6, 0, [cls.env.ref("base.group_user").id])]}
        cls.alice = Users.create(dict(base, name="Alice", login="alice_t"))
        cls.bob = Users.create(dict(base, name="Bob", login="bob_t"))
        cls.carol = Users.create(dict(base, name="Carol", login="carol_t"))
        cls.carol.group_ids = [(4, cls.group.id)]
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
        log = self.env["dwo.approval.log"].search([("kind", "=", "move")])
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
        view = self.env["res.partner"].get_view(view_type="form")
        self.assertIn("dwo_approval_buttons", view["arch"])
        self.assertIn("dwo_approval_panel", view["arch"])  # the partner form has no status bar
        flow.replace_statusbar = True
        view = self.env["res.partner"].get_view(view_type="form")
        self.assertIn("dwo_approval_panel", view["arch"])
        flow.active = False
        view = self.env["res.partner"].get_view(view_type="form")
        self.assertNotIn("dwo_approval_buttons", view["arch"])

    def test_one_active_flow_per_model(self):
        self._flow([])
        with self.assertRaises(ValidationError):
            self._flow([])

    def test_security(self):
        flow = self._flow([self._tr("Submit", "draft", "review")])
        with self.assertRaises(AccessError):
            flow.with_user(self.alice).write({"name": "hack"})
        with self.assertRaises(AccessError):
            self.env["dwo.approval.log"].with_user(self.alice).search([])
