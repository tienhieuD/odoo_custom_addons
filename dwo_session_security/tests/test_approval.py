# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged

from .common import WEBCLIENT, DOC, SessionCase


@tagged("post_install", "-at_install")
class TestApproval(SessionCase):

    def setUp(self):
        super().setUp()
        self.set("approval_enabled", "1")
        gfield = "group_ids" if "group_ids" in self.user._fields else "groups_id"
        self.user.write({gfield: [(4, self.env.ref("dwo_session_security.group_dwo_session_approval").id)]})

    def _wait(self):
        self.authenticate(self.user.login, "Dwo-Test-Pass-1!")
        self.url_open("/dwo/session/heartbeat", data='{"params": {}}', headers={"Content-Type": "application/json"})
        row = self.row()
        self.assertEqual(row.state, "pending_approval")
        return row

    def test_new_session_waits_and_cannot_call_anything(self):
        row = self._wait()
        self.assertEqual(row.approval_id.kind, "login")
        res = self.rpc("/web/dataset/call_kw/res.users/read", model="res.users", method="read", args=[[self.user.id], ["name"]], kwargs={})
        self.assertIn("error", res)
        self.assertEqual(self.go(WEBCLIENT).headers["Location"], "/dwo/session/waiting")
        self.assertEqual(self.url_open("/web/image/res.users/%s/avatar_128" % self.user.id, allow_redirects=False).status_code, 403)
        page = self.go("/dwo/session/waiting")
        self.assertIn("Waiting for approval", page.text)
        self.assertNotIn("web.assets", page.text)
        self.assertEqual(self.beat()["state"], "pending_approval")
        # the lock page is not a way in
        self.assertEqual(self.go("/dwo/session/locked").headers["Location"], "/dwo/session/waiting")

    def test_approver_notified_by_activity_toast_and_email(self):
        self.set("notify_email", "1")
        row = self._wait()
        req = row.approval_id
        self.assertTrue(req.activity_ids.filtered(lambda a: a.user_id == self.admin))
        self.assertTrue(self.env["mail.mail"].sudo().search([("subject", "ilike", "Session security")]))
        self.assertTrue(self.env["bus.bus"].sudo().search([("channel", "ilike", "dwo")]) is not None)

    def test_approve_opens_odoo(self):
        row = self._wait()
        row.approval_id.with_user(self.admin).action_approve()
        self.assertEqual(self.row().state, "active")
        self.assertEqual(self.beat()["state"], "active")
        res = self.rpc("/web/dataset/call_kw/res.users/read", model="res.users", method="read", args=[[self.user.id], ["name"]], kwargs={})
        self.assertIn("result", res)
        self.assertEqual(row.approval_id.decided_by, self.admin)
        self.assertFalse(row.approval_id.activity_ids)
        self.assertTrue(self.env["dwo.session.log"].search([("event", "=", "approved"), ("user_id", "=", self.user.id)]))

    def test_reject_ends_the_session(self):
        row = self._wait()
        row.approval_id.with_user(self.admin).action_reject()
        self.assertEqual(self.row().state, "expired")
        self.assertEqual(self.row().end_reason, "rejected")
        self.assertEqual(self.beat()["state"], "expired")

    def test_request_times_out(self):
        row = self._wait()
        row.approval_id.expires_at = fields.Datetime.now() - timedelta(minutes=1)
        self.assertEqual(self.beat()["state"], "expired")
        self.assertEqual(row.approval_id.state, "expired")
        with self.assertRaises(UserError):
            row.approval_id.with_user(self.admin).action_approve()

    def test_nobody_but_an_approver_decides_and_nobody_decides_own_request(self):
        row = self._wait()
        with self.assertRaises(AccessError):
            row.approval_id.with_user(self.user).action_approve()
        # another ordinary user is not an approver
        other = self._make_user("dwo_other")
        with self.assertRaises(AccessError):
            row.approval_id.with_user(other).action_approve()
        # an approver that is also the requester cannot approve himself
        self.user.write({("group_ids" if "group_ids" in self.user._fields else "groups_id"): [(4, self.env.ref("dwo_session_security.group_dwo_session_approver").id)]})
        with self.assertRaises(AccessError):
            row.approval_id.with_user(self.user).action_approve()

    def test_cancel_by_signing_out(self):
        self._wait()
        out = self.post("/web/session/logout?redirect=/web/login")
        self.assertEqual(out.status_code, 303)

    def test_administrators_and_other_users_are_not_asked(self):
        self.admin.write({("group_ids" if "group_ids" in self.admin._fields else "groups_id"): [(4, self.env.ref("dwo_session_security.group_dwo_session_approval").id)]})
        row = self.sign_in(self.admin)
        self.assertEqual(row.state, "active")
        other = self._make_user("dwo_free")
        self.assertEqual(self.sign_in(other).state, "active")

    def test_switch_off(self):
        self.set("approval_enabled", "0")
        row = self.sign_in()
        self.assertEqual(row.state, "active")

    def test_approval_comes_before_the_pin_rules(self):
        self.Pin.set_pin(self.user.id, "4826", must_change=True, check=False)
        row = self._wait()
        row.approval_id.with_user(self.admin).action_approve()
        self.assertEqual(self.row().state, "active")
