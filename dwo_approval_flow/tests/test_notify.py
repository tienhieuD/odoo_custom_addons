# -*- coding: utf-8 -*-
import json
from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

SCHEMA = "dwo_approval_flow/1"
ACTIVITY = "dwo_approval_flow.mail_activity_type_to_approve"


@tagged("post_install", "-at_install")
class TestApprovalNotify(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Users = cls.env["res.users"].with_context(no_reset_password=True)
        cls.group = cls.env["res.groups"].create({"name": "Test Notify Legal"})
        base = {"groups_id": [(6, 0, [cls.env.ref("base.group_user").id, cls.env.ref("base.group_partner_manager").id])]}
        cls.alice = Users.create(dict(base, name="Alice", login="alice_n"))
        cls.bob = Users.create(dict(base, name="Bob", login="bob_n"))
        cls.carol = Users.create(dict(base, name="Carol", login="carol_n"))
        cls.dave = Users.create(dict(base, name="Dave", login="dave_n"))
        cls.carol.groups_id = [(4, cls.group.id)]
        cls.model = cls.env["ir.model"]._get("res.partner")
        # Alice is the creator of the document
        cls.partner = cls.env["res.partner"].with_user(cls.alice).create({"name": "ACME N"})

    # -- helpers ---------------------------------------------------------
    def _flow(self, transitions, **vals):
        flow = self.env["dwo.approval.flow"].create(dict({
            "name": "Notify flow", "model_id": self.model.id, "state_mode": "custom"}, **vals))
        flow.graph = json.dumps({"schema": SCHEMA, "states": [
            {"key": "draft", "name": "Draft"}, {"key": "review", "name": "Review"},
            {"key": "done", "name": "Done"}, {"key": "refused", "name": "Refused"}], "transitions": transitions})
        return flow

    def _tr(self, name, src, dst, **kw):
        return dict({"name": name, "from": src, "to": dst}, **kw)

    def _who(self, *lines, **approvals):
        return {"approvers": list(lines), "approvals": approvals or {"mode": "any"}}

    def _press(self, flow, name, user, reason=None):
        tr = flow.transition_ids.filtered(lambda t: t.name == name)
        return self.env["dwo.approval.flow"].with_user(user).press(
            "res.partner", self.partner.id, tr.id, reason)

    def _pending(self):
        return self.env["dwo.approval.pending"].sudo().search([("res_id", "=", self.partner.id)]).user_id

    def _activities(self):
        return self.env["mail.activity"].sudo().search([
            ("res_model", "=", "res.partner"), ("res_id", "=", self.partner.id),
            ("activity_type_id", "=", self.env.ref(ACTIVITY).id)]).user_id

    def _log(self, **domain):
        return self.env["dwo.approval.notify.log"].sudo().search(
            [("res_id", "=", self.partner.id)] + [(k, "=", v) for k, v in domain.items()])

    CH = {"bus": True, "activity": True, "email": True}

    def _line(self, kind, notify):
        return dict(kind, notify=dict(notify))

    def _standard(self, line=None, arrow=None, **vals):
        """draft -> review (anybody) -> done; Carol's group, Bob and Carol, approve or refuse in review.

        ``line``: the channels ticked on every approver line; ``arrow``: the "notify" of the arrows (followers, creator).
        """
        line = self.CH if line is None else line
        arrow = {"followers": self.CH, "creator": True} if arrow is None else arrow
        group = self._line({"type": "group", "group_id": self.group.id}, line)
        user = self._line({"type": "users", "user_ids": [self.bob.id, self.carol.id]}, line)
        return self._flow([
            self._tr("Submit", "draft", "review"),
            self._tr("ByGroup", "review", "done", who=self._who(group), notify=arrow),
            self._tr("ByUsers", "review", "done", who=self._who(user), notify=arrow),
            self._tr("Reject", "review", "refused", ask_reason=True, who=self._who(user), notify=arrow),
            self._tr("Reopen", "refused", "draft"),
        ], **vals)

    def _subtype_messages(self, partner=None):
        partner = partner or self.partner
        return self.env["mail.message"].search([
            ("model", "=", "res.partner"), ("res_id", "=", partner.id),
            ("subtype_id", "=", self.env.ref("dwo_approval_flow.mt_approval").id)])

    # -- tests ------------------------------------------------------------
    def test_off_by_default(self):
        flow = self._flow([
            self._tr("Submit", "draft", "review"),
            self._tr("Approve", "review", "done", who=self._who({"type": "users", "user_ids": [self.bob.id]})),
        ])
        self.assertFalse(any(t._notifies_approvers() or t._notifies_followers() for t in flow.transition_ids))
        self._press(flow, "Submit", self.alice)
        self.assertFalse(self._pending())
        self.assertFalse(self._log())
        self.assertFalse(self._subtype_messages())

    def test_right_people_told_once(self):
        flow = self._standard()
        self._press(flow, "Submit", self.alice)
        # Carol is on two arrows and Bob on two: told once. Alice (actor) and Dave (no right) are not told.
        self.assertEqual(self._pending(), self.bob | self.carol)
        self.assertEqual(self._activities(), self.bob | self.carol)
        self.assertEqual(len(self.env["dwo.approval.pending"].sudo().search([("res_id", "=", self.partner.id)])), 2)
        for channel in ("activity", "bus", "email"):
            told = self._log(kind="approver", channel=channel)
            self.assertEqual(told.user_id, self.bob | self.carol, channel)
            self.assertEqual(len(told), 2, channel)
            self.assertTrue(all(told.mapped("ok")), channel)

    def test_channels_are_ticked_per_line(self):
        flow = self._standard(line={"activity": True}, arrow={})
        self._press(flow, "Submit", self.alice)
        self.assertEqual(self._log(kind="approver").mapped("channel"), ["activity", "activity"])
        self.assertEqual(self._activities(), self.bob | self.carol)
        # the group line (Carol) ticks nothing more than the users line: tick only the group line
        flow.active = False
        group = self._line({"type": "group", "group_id": self.group.id}, {"bus": True})
        users = self._line({"type": "users", "user_ids": [self.bob.id]}, {})
        flow2 = self._flow([
            self._tr("Submit", "draft", "review"),
            self._tr("Approve", "review", "done", who=self._who(group, users)),
        ])
        partner = self.env["res.partner"].with_user(self.alice).create({"name": "One line"})
        tr = flow2.transition_ids.filtered(lambda t: t.name == "Submit")
        self.env["dwo.approval.flow"].with_user(self.alice).press("res.partner", partner.id, tr.id)
        logs = self.env["dwo.approval.notify.log"].sudo().search([("res_id", "=", partner.id)])
        self.assertEqual(logs.user_id, self.carol)  # Bob's line ticks nothing: he is not told
        self.assertEqual(logs.mapped("channel"), ["bus"])
        # nothing ticked at all: nobody is listed either
        partner2 = self.env["res.partner"].with_user(self.alice).create({"name": "No tick"})
        flow3 = self._standard(line={}, arrow={})
        flow2.active = False
        tr3 = flow3.transition_ids.filtered(lambda t: t.name == "Submit")
        self.env["dwo.approval.flow"].with_user(self.alice).press("res.partner", partner2.id, tr3.id)
        self.assertFalse(self.env["dwo.approval.pending"].sudo().search([("res_id", "=", partner2.id)]))

    def test_followers_who_subscribed_are_told(self):
        flow = self._standard()
        Users = self.env["res.users"].with_context(no_reset_password=True)
        eve = Users.create({"name": "Eve", "login": "eve_n", "groups_id": [(6, 0, [self.env.ref("base.group_user").id])]})
        subtype = self.env.ref("dwo_approval_flow.mt_approval")
        self.partner.sudo().message_subscribe(partner_ids=self.dave.partner_id.ids, subtype_ids=subtype.ids)
        self.partner.sudo().message_subscribe(
            partner_ids=eve.partner_id.ids, subtype_ids=[self.env.ref("mail.mt_comment").id])
        self._press(flow, "Submit", self.alice)
        note = self._subtype_messages()
        self.assertEqual(len(note), 1)
        self.assertIn("Bob", note.body)
        self.assertNotIn("Dave", note.body)
        self.assertIn(self.dave.partner_id, note.notification_ids.res_partner_id)
        self.assertNotIn(eve.partner_id, note.notification_ids.res_partner_id)
        # the system notification and the activity go to the followers one by one
        self.assertEqual(self._log(kind="followers", channel="bus").user_id, self.dave)
        self.assertEqual(self._log(kind="followers", channel="activity").user_id, self.dave)
        self.assertIn(self.dave, self._activities())
        self.assertNotIn(self.dave, self._pending())  # followers are not in the queue
        self.assertNotIn(eve, self._activities())
        # the activities go away when the document moves
        self._press(flow, "ByUsers", self.bob)
        self.assertFalse(self._activities())
        # an arrow that does not tick the followers writes nothing
        flow.active = False
        flow2 = self._standard(arrow={})
        partner = self.env["res.partner"].with_user(self.alice).create({"name": "No followers"})
        tr = flow2.transition_ids.filtered(lambda t: t.name == "Submit")
        self.env["dwo.approval.flow"].with_user(self.alice).press("res.partner", partner.id, tr.id)
        self.assertFalse(self._subtype_messages(partner))

    def test_no_one_without_the_right_is_told(self):
        flow = self._standard()
        # the rule of the arrow is not met for anybody: nobody is told
        flow.transition_ids.filtered(lambda t: t.name in ("ByGroup", "ByUsers", "Reject")).write({
            "rule_ids": [(0, 0, {"domain": "[('name', '=', 'nothing like this')]"})]})
        self._press(flow, "Submit", self.alice)
        self.assertFalse(self._pending())
        self.assertFalse(self._activities())

    def test_arrow_without_approvers_notifies_nobody(self):
        flow = self._flow([
            self._tr("Submit", "draft", "review"),
            self._tr("Anyone", "review", "done", notify={"followers": {"activity": True}}),
        ])
        self._press(flow, "Submit", self.alice)
        self.assertFalse(self._pending())

    def test_switch_per_line(self):
        flow = self._standard(arrow={})
        quiet = {"notify_bus": False, "notify_activity": False, "notify_email": False}
        for name in ("ByGroup", "Reject"):
            flow.transition_ids.filtered(lambda t: t.name == name).approver_ids.write(quiet)
        self._press(flow, "Submit", self.alice)
        self.assertEqual(self._pending(), self.bob | self.carol)  # still through ByUsers
        flow.transition_ids.filtered(lambda t: t.name == "ByUsers").approver_ids.write(quiet)
        self._press(flow, "ByUsers", self.bob)
        self.assertFalse(self._pending())

    def test_activity_closed_on_move_and_only_voter_on_vote(self):
        users = self._line({"type": "users", "user_ids": [self.bob.id, self.carol.id]}, {"activity": True})
        flow = self._flow([
            self._tr("Submit", "draft", "review"),
            self._tr("Approve", "review", "done", who=self._who(users, mode="n", n=2)),
        ])
        self._press(flow, "Submit", self.alice)
        self.assertEqual(self._activities(), self.bob | self.carol)
        self.assertEqual(self._press(flow, "Approve", self.bob)["status"], "waiting")
        self.assertEqual(self._activities(), self.carol)  # only the voter's is closed
        self.assertEqual(self._pending(), self.carol)
        self.assertEqual(self._press(flow, "Approve", self.carol)["status"], "done")
        self.assertFalse(self._activities())
        self.assertFalse(self._pending())

    def test_creator_told(self):
        flow = self._standard()
        self._press(flow, "Submit", self.alice)  # Submit does not ask to tell the creator
        self.assertFalse(self._log(kind="creator"))
        self._press(flow, "ByUsers", self.bob)
        self.assertEqual(self._log(kind="creator").user_id, self.alice)

    def test_creator_told_of_a_reason_and_of_votes(self):
        flow = self._standard()
        self._press(flow, "Submit", self.alice)
        self._press(flow, "Reject", self.bob, reason="Too expensive")
        self.assertTrue(any("Too expensive" in (m.body or "") for m in self.partner.message_ids))
        self.assertEqual(self._log(kind="creator", channel="email").user_id, self.alice)
        # a flow that needs two approvals: the creator hears "1/2"
        flow.active = False
        flow2 = self._flow([
            self._tr("Submit", "draft", "review"),
            self._tr("Approve", "review", "done", notify={"creator": True}, who=self._who(
                {"type": "users", "user_ids": [self.bob.id, self.carol.id]}, mode="n", n=2)),
        ])
        partner = self.env["res.partner"].with_user(self.alice).create({"name": "Second N"})
        tr = lambda name: flow2.transition_ids.filtered(lambda t: t.name == name)  # noqa: E731
        Flow = self.env["dwo.approval.flow"]
        Flow.with_user(self.carol).press("res.partner", partner.id, tr("Submit").id)
        Flow.with_user(self.bob).press("res.partner", partner.id, tr("Approve").id)
        body = " ".join(self.env["mail.message"].search([
            ("model", "=", "res.partner"), ("res_id", "=", partner.id)]).mapped("body"))
        self.assertIn("1/2", body)

    def test_loop_back_does_not_hide_the_new_round(self):
        flow = self._standard()
        self._press(flow, "Submit", self.alice)
        self._press(flow, "Reject", self.bob, reason="no")
        self.assertFalse(self._pending())
        self._press(flow, "Reopen", self.alice)
        self._press(flow, "Submit", self.alice)
        self.assertEqual(self._pending(), self.bob | self.carol)

    def test_failing_channel_never_blocks(self):
        template = self.env["mail.template"].create({
            "name": "Fine", "model_id": self.model.id, "subject": "x", "body_html": "<p>x</p>"})
        flow = self._standard(notify_template_id=template.id)
        with patch.object(type(template), "send_mail", side_effect=ValueError("no mail server")):
            result = self._press(flow, "Submit", self.alice)
        self.assertEqual(result["status"], "done")
        self.assertEqual(self.partner.x_dwo_approval_state_id.key, "review")
        self.assertEqual(self._pending(), self.bob | self.carol)  # the queue still works
        failed = self._log(channel="email", ok=False)
        self.assertEqual(failed.user_id, self.bob | self.carol)
        self.assertTrue(all("no mail server" in e for e in failed.mapped("error")))
        self.assertEqual(self._activities(), self.bob | self.carol)  # the other channels went on
        self.assertEqual(len(self._log(channel="bus", ok=True)), 2)

    def test_own_template_is_used(self):
        template = self.env["mail.template"].create({
            "name": "Mine", "model_id": self.model.id, "subject": "Please look at {{ object.name }}",
            "body_html": "<p>Hello</p>", "email_from": "x@example.com"})
        flow = self._standard(notify_template_id=template.id)
        before = self.env["mail.mail"].sudo().search_count([("subject", "=", "Please look at ACME N")])
        self._press(flow, "Submit", self.alice)
        after = self.env["mail.mail"].sudo().search_count([("subject", "=", "Please look at ACME N")])
        self.assertEqual(after - before, 2)

    def test_reminders_have_a_limit(self):
        flow = self._standard(remind_after=2, remind_max=2)
        self._press(flow, "Submit", self.alice)
        Pending = self.env["dwo.approval.pending"].sudo()
        rows = Pending.search([("res_id", "=", self.partner.id)])
        Flow = self.env["dwo.approval.flow"]
        Flow._cron_remind()
        self.assertEqual(rows.mapped("reminder_count"), [0, 0])  # too early
        old = fields.Datetime.now() - timedelta(hours=3)
        rows.write({"since": old})
        Flow._cron_remind()
        self.assertEqual(rows.mapped("reminder_count"), [1, 1])
        self.assertEqual(len(self._log(kind="reminder")), 2)
        Flow._cron_remind()  # the last reminder was just now: not again yet
        self.assertEqual(rows.mapped("reminder_count"), [1, 1])
        rows.write({"last_reminder": old})
        Flow._cron_remind()
        rows.write({"last_reminder": old})
        Flow._cron_remind()  # the limit of 2 is reached
        self.assertEqual(rows.mapped("reminder_count"), [2, 2])
        self.assertEqual(len(self._log(kind="reminder")), 4)

    def test_reminders_are_not_blocked_by_rows_at_their_limit(self):
        flow = self._standard(remind_after=1, remind_max=1)
        self._press(flow, "Submit", self.alice)
        rows = self.env["dwo.approval.pending"].sudo().search([("res_id", "=", self.partner.id)], order="id")
        old = fields.Datetime.now() - timedelta(hours=5)
        rows.write({"since": old})
        rows[0].reminder_count = 1  # done with its reminders, and first in line
        with patch("odoo.addons.dwo_approval_flow.models.notify.CRON_BATCH", 1):
            self.env["dwo.approval.flow"]._cron_remind()
        self.assertEqual(rows.mapped("reminder_count"), [1, 1])  # the second row was still reached

    def test_reminder_drops_rows_that_are_no_longer_waiting(self):
        flow = self._standard(remind_after=1)
        self._press(flow, "Submit", self.alice)
        rows = self.env["dwo.approval.pending"].sudo().search([("res_id", "=", self.partner.id)])
        rows.write({"since": fields.Datetime.now() - timedelta(hours=5)})
        # the state changes outside the arrows (this is possible with the state field of the model)
        self.partner.sudo().write({"x_dwo_approval_state_id": flow.state_ids.filtered(lambda s: s.key == "done").id})
        self.env["dwo.approval.flow"]._cron_remind()
        self.assertFalse(rows.exists())
        self.assertFalse(self._log(kind="reminder"))

    def test_queue_is_private(self):
        flow = self._standard()
        self._press(flow, "Submit", self.alice)
        Pending = self.env["dwo.approval.pending"]
        self.assertEqual(Pending.with_user(self.bob).search([]).user_id, self.bob)
        self.assertFalse(Pending.with_user(self.dave).search([]))
        row = Pending.with_user(self.bob).search([])
        self.assertEqual(row.action_open_document()["res_id"], self.partner.id)

    def test_json_carries_notify_and_old_json_loads(self):
        flow = self._standard()
        data = json.loads(flow.graph)
        everything = {"followers": self.CH, "creator": True}
        self.assertEqual(data["transitions"][1]["notify"], everything)
        self.assertEqual(data["transitions"][1]["who"]["approvers"][0]["notify"], self.CH)
        self.assertEqual(data["transitions"][0]["notify"],
                         {"followers": dict.fromkeys(self.CH, False), "creator": False})
        shared = json.loads(self.env["dwo.approval.flow"].graph_to_share(flow.graph))
        self.assertTrue(shared["transitions"][1]["notify"]["followers"]["bus"])
        self.assertTrue(shared["transitions"][1]["who"]["approvers"][0]["notify"]["email"])
        # a JSON written before this version has no notify block
        for tr in data["transitions"]:
            tr.pop("notify")
            for line in (tr["who"] or {}).get("approvers", []):
                line.pop("notify")
        flow.graph = json.dumps(data)
        self.assertFalse(any(t._notifies_approvers() or t._notifies_followers() or t.notify_creator
                             for t in flow.transition_ids))
        result = self.env["dwo.approval.flow"].share_to_graph(self.model.id, "custom", False, json.dumps(
            {"schema": SCHEMA, "states": [{"key": "a", "name": "A"}], "transitions": []}))
        self.assertIn("graph", result)
