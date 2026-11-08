# -*- coding: utf-8 -*-
from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.addons.mail.tests.common import MailCommon, mail_new_test_user
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import tagged

CUSTOMER = "lan.pham@customer.example"
ACTIVITY = "dwo_mail_compose.mail_activity_type_email_approval"


@tagged("post_install", "-at_install", "dwo_mail_compose")
class TestApproval(MailCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = cls.user_admin
        cls.author.write({"email": "hieu@dwo.example", "tz": "Asia/Tokyo"})
        cls.approver_a = cls.user_employee
        cls.approver_b = mail_new_test_user(
            cls.env, login="approver_b", groups="base.group_user", name="Approver B", email="appr.b@x.example")
        cls.approver_c = mail_new_test_user(
            cls.env, login="approver_c", groups="base.group_user", name="Approver C", email="appr.c@x.example")
        cls.env["mail.mail"].sudo().search([]).unlink()
        cls.record = cls.env["res.partner"].create({"name": "Approval thread"})
        cls.Email = cls.env["dwo.mail.email"]

    # ------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------

    def _composer(self, user=None):
        return self.env["dwo.mail.composer"].with_user(user or self.author)

    def _request(self, approvers, comment="please check", **vals):
        """The author writes an email and asks for approval. Returns the stored email."""
        payload = {
            "from": "hieu@dwo.example", "to": [CUSTOMER], "subject": "Quote for approval",
            "body": "<p>Here is the quote.</p>",
        }
        payload.update(vals)
        composer = self._composer()
        result = composer.request_approval(
            "res.partner", self.record.id, payload.pop("email_id", False), payload, approvers.ids, comment)
        return self.Email.browse(result["id"])

    def _open_activities(self, email):
        activity_type = self.env.ref(ACTIVITY)
        return email.sudo().activity_ids.filtered(lambda a: a.activity_type_id == activity_type)

    def _approve(self, email, user, comment=None):
        with self.mock_mail_gateway():
            email.with_user(user).action_approve(comment)
            self.env.cr.flush()
            self.env["mail.mail"].sudo().search([("state", "=", "outgoing")]).send()

    def _official_messages(self):
        return self.env["mail.message"].search([
            ("model", "=", "res.partner"), ("res_id", "=", self.record.id), ("dwo_is_official_email", "=", True)])

    def _capture_bus(self):
        """Capture the screen notifications of the module (the other modules use the bus too)."""
        sent = []

        def _bus_send(users, notification_type, message, /, *, subchannel=None):
            if notification_type == "dwo_mail_approval":
                for user in users:
                    sent.append((user, notification_type, message))
        return sent, patch.object(type(self.env["res.users"]), "_bus_send", _bus_send)

    # ------------------------------------------------------------
    # the request
    # ------------------------------------------------------------

    def test_request_makes_the_email_pending_and_tells_the_approvers(self):
        sent, patcher = self._capture_bus()
        with patcher:
            email = self._request(self.approver_a | self.approver_b)
        self.assertEqual(email.state, "pending")
        self.assertEqual(email.approver_ids, self.approver_a | self.approver_b)
        self.assertEqual(email.request_comment, "please check")
        self.assertEqual(self._open_activities(email).user_id, self.approver_a | self.approver_b)
        self.assertEqual(self.env["res.users"].union(*[user for user, _, _ in sent]),
                         self.approver_a | self.approver_b)
        payload = sent[0][2]
        self.assertEqual((payload["kind"], payload["email_id"]), ("request", email.id))
        # the email that reaches an approver carries a link to the page of the email
        self.env.cr.flush()
        notice_mail = self.env["mail.mail"].sudo().search([("mail_message_id.model", "=", "dwo.mail.email")])
        body = " ".join(notice_mail.mapped("body_html"))
        self.assertIn("dwo.mail.email", body)
        self.assertIn(str(email.id), body)
        # the approvers got a message on the email, with a way to open it
        notice = self.env["mail.message"].search([
            ("model", "=", "dwo.mail.email"), ("res_id", "=", email.id), ("message_type", "=", "user_notification")])
        self.assertTrue(notice)
        self.assertEqual(notice.partner_ids, (self.approver_a | self.approver_b).partner_id)

    def test_comment_is_optional(self):
        email = self._request(self.approver_a, comment=False)
        self.assertEqual(email.state, "pending")
        email.with_user(self.approver_a).action_reject()  # no comment either
        self.assertEqual(email.state, "rejected")

    def test_the_author_can_be_the_approver(self):
        email = self._request(self.author)
        self.assertEqual(email.approver_ids, self.author)
        self._approve(email, self.author)
        self.assertEqual(email.state, "sent")
        self.assertEqual(len(self._official_messages()), 1)

    def test_an_email_that_cannot_be_sent_is_not_sent_for_approval(self):
        with self.assertRaises(UserError):
            self._request(self.approver_a, to=[])
        self.assertFalse(self.Email.search([("res_id", "=", self.record.id)]))

    def test_approvers_are_required(self):
        with self.assertRaises(UserError):
            self._composer().request_approval("res.partner", self.record.id, False, {
                "from": "hieu@dwo.example", "to": [CUSTOMER], "body": "<p>x</p>"}, [], None)

    # ------------------------------------------------------------
    # approve
    # ------------------------------------------------------------

    def test_approve_sends_as_the_author_and_closes_the_activities(self):
        email = self._request(self.approver_a | self.approver_b)
        sent, patcher = self._capture_bus()
        with patcher:
            self._approve(email, self.approver_a, "fine")
        self.assertEqual(email.state, "sent")
        self.assertEqual((email.decided_by_id, email.decision_comment), (self.approver_a, "fine"))
        message = self._official_messages()
        self.assertEqual(len(message), 1)
        self.assertEqual(message.author_id, self.author.partner_id, "the email leaves as its author")
        self.assertIn("hieu@dwo.example", message.email_from)
        self.assertEqual(email.sent_message_id, message)
        self.assertFalse(self._open_activities(email), "the activities of every approver are done")
        self.assertIn(self.author, [user for user, _, payload in sent if payload["kind"] == "approved"])

    def test_only_one_email_leaves_when_two_approvers_approve(self):
        email = self._request(self.approver_a | self.approver_b)
        self._approve(email, self.approver_a)
        with self.assertRaises(UserError):
            self._approve(email, self.approver_b)
        self.assertEqual(len(self._official_messages()), 1)
        mails = self.env["mail.mail"].sudo().search([("mail_message_id", "=", self._official_messages().id)])
        self.assertEqual(len(mails), 1, "exactly one mail.mail")

    def test_approve_after_the_author_sent_directly_is_refused(self):
        email = self._request(self.approver_a)
        with self.mock_mail_gateway():
            self._composer().send("res.partner", self.record.id, {
                "email_id": email.id, "from": "hieu@dwo.example", "to": [CUSTOMER], "body": "<p>x</p>"})
        self.assertFalse(email.exists(), "the stored copy is gone")
        with self.assertRaises(UserError):
            self._approve(email, self.approver_a)

    def test_a_non_approver_cannot_decide(self):
        email = self._request(self.approver_a)
        with self.assertRaises(AccessError):
            email.with_user(self.approver_b).action_approve()
        with self.assertRaises(AccessError):
            email.with_user(self.approver_b).action_reject()
        with self.assertRaises(AccessError):
            email.with_user(self.approver_b).action_open_approve()
        self.assertEqual(email.state, "pending")

    def test_an_approver_without_access_to_the_record_can_open_and_approve(self):
        """The approver may not read the record (a CRM lead, say): the email is still theirs to decide,
        and it leaves with the rights of its author."""
        group = self.env["res.groups"].create({"name": "Cannot read the thread"})
        self.env["ir.rule"].create({
            "name": "hide the thread", "model_id": self.env["ir.model"]._get("res.partner").id,
            "domain_force": f"[('id', '!=', {self.record.id})]", "groups": [(4, group.id)],
            "perm_read": True, "perm_write": True, "perm_create": True, "perm_unlink": True})
        self.approver_b.write({"group_ids": [(4, group.id)]})
        with self.assertRaises(AccessError):
            self.record.with_user(self.approver_b).check_access("read")
        email = self._request(self.approver_b)
        as_approver = email.with_user(self.approver_b)
        self.assertIn("Here is the quote.", as_approver.body)
        self.assertFalse(as_approver.can_open_record)
        self._approve(email, self.approver_b)
        self.assertEqual(email.state, "sent")
        self.assertEqual(self._official_messages().author_id, self.author.partner_id)

    def test_an_approver_cannot_edit_the_email(self):
        email = self._request(self.approver_a)
        with self.assertRaises(AccessError):
            email.with_user(self.approver_a).write({"subject": "changed by the approver"})

    # ------------------------------------------------------------
    # reject, reassign, ask again
    # ------------------------------------------------------------

    def test_reject_by_any_approver_closes_everybody_activities(self):
        email = self._request(self.approver_a | self.approver_b)
        sent, patcher = self._capture_bus()
        with patcher:
            email.with_user(self.approver_b).action_reject("not like this")
        self.assertEqual((email.state, email.decision_comment), ("rejected", "not like this"))
        self.assertFalse(self._open_activities(email))
        self.assertIn(self.author, [user for user, _, payload in sent if payload["kind"] == "rejected"])
        self.assertFalse(self._official_messages())

    def test_rejected_email_can_be_edited_and_asked_again_to_other_people(self):
        email = self._request(self.approver_a)
        email.with_user(self.approver_a).action_reject("redo")
        # the author edits and asks somebody else
        self._composer().save_email("res.partner", self.record.id, email.id, {
            "from": "hieu@dwo.example", "to": [CUSTOMER], "subject": "Quote v2", "body": "<p>v2</p>"})
        again = self._request(self.approver_b, email_id=email.id, subject="Quote v2", body="<p>v2</p>")
        self.assertEqual(again, email)
        self.assertEqual((email.state, email.approver_ids), ("pending", self.approver_b))
        self.assertFalse(email.decision_comment)
        # whoever was an approver can still read the email
        self.assertTrue(self.Email.with_user(self.approver_a).search([("id", "=", email.id)]))
        self.assertTrue(self.Email.with_user(self.approver_b).search([("id", "=", email.id)]))
        self.assertFalse(self.Email.with_user(self.approver_c).search([("id", "=", email.id)]))

    def test_reassign_replaces_only_the_acting_approver(self):
        email = self._request(self.approver_a | self.approver_b)
        sent, patcher = self._capture_bus()
        with patcher:
            email.with_user(self.approver_a).action_reassign(self.approver_c, "you know this better")
        self.assertEqual(email.approver_ids, self.approver_b | self.approver_c)
        self.assertEqual(self._open_activities(email).user_id, self.approver_b | self.approver_c)
        self.assertEqual(email.state, "pending")
        self.assertIn(self.approver_c, [user for user, _, payload in sent if payload["kind"] == "request"])
        # the one who handed over still reads the email, and can no longer decide
        self.assertTrue(self.Email.with_user(self.approver_a).search([("id", "=", email.id)]))
        with self.assertRaises(AccessError):
            email.with_user(self.approver_a).action_approve()
        # the new approver can approve
        self._approve(email, self.approver_c)
        self.assertEqual(email.state, "sent")

    def test_reassign_needs_somebody_internal_and_active(self):
        email = self._request(self.approver_a)
        with self.assertRaises(UserError):
            email.with_user(self.approver_a).action_reassign(self.env["res.users"])
        portal = self.env["res.users"].with_context(no_reset_password=True).create({
            "name": "Portal", "login": "portal_reassign", "email": "portal.r@x.example",
            "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])]})
        with self.assertRaises(UserError):
            email.with_user(self.approver_a).action_reassign(portal)
        self.assertEqual(email.approver_ids, self.approver_a)

    # ------------------------------------------------------------
    # decision popup
    # ------------------------------------------------------------

    def test_decision_popup(self):
        email = self._request(self.approver_a)
        wizard = self.env["dwo.mail.decision"].with_user(self.approver_a).create({
            "email_id": email.id, "decision": "reject"})
        wizard.action_confirm()  # no comment needed
        self.assertEqual(email.state, "rejected")
        email2 = self._request(self.approver_a)
        wizard = self.env["dwo.mail.decision"].with_user(self.approver_a).create({
            "email_id": email2.id, "decision": "reassign"})
        with self.assertRaises(UserError):
            wizard.action_confirm()
        action = email2.with_user(self.approver_a).action_open_reassign()
        self.assertEqual(action["context"]["default_decision"], "reassign")

    # ------------------------------------------------------------
    # the author acts while somebody waits
    # ------------------------------------------------------------

    def test_direct_send_closes_the_request_and_tells_the_approvers(self):
        email = self._request(self.approver_a | self.approver_b)
        sent, patcher = self._capture_bus()
        with patcher, self.mock_mail_gateway():
            self._composer().send("res.partner", self.record.id, {
                "email_id": email.id, "from": "hieu@dwo.example", "to": [CUSTOMER], "body": "<p>x</p>"})
        self.assertFalse(email.exists())
        self.assertFalse(self.env["mail.activity"].sudo().search([
            ("res_model", "=", "dwo.mail.email"), ("res_id", "=", email.id)]), "no activity is left open")
        closed = [user for user, _, payload in sent if payload["kind"] == "closed"]
        self.assertEqual(self.env["res.users"].union(*closed), self.approver_a | self.approver_b)
        self.assertEqual(len(self._official_messages()), 1)

    def test_deleting_a_pending_email_withdraws_the_request(self):
        email = self._request(self.approver_a)
        sent, patcher = self._capture_bus()
        with patcher:
            self._composer().delete_email("res.partner", self.record.id, email.id)
        self.assertFalse(email.exists())
        self.assertIn(self.approver_a, [user for user, _, payload in sent if payload["kind"] == "closed"])

    def test_editing_while_pending_keeps_the_request_and_is_flagged(self):
        email = self._request(self.approver_a)
        self.assertFalse(email.edited_after_request)
        self._composer().save_email("res.partner", self.record.id, email.id, {
            "from": "hieu@dwo.example", "to": [CUSTOMER], "subject": "Changed", "body": "<p>new</p>"})
        self.assertEqual((email.state, email.subject), ("pending", "Changed"))
        self.assertTrue(email.edited_after_request)
        # the approver approves what is there now
        self._approve(email, self.approver_a)
        self.assertIn("new", self._official_messages().body)

    def test_a_sent_email_is_not_written_again(self):
        """Approved while the author still had the form open: the next autosave writes nothing and
        tells the state, so the form can stop saving."""
        email = self._request(self.approver_a)
        self._approve(email, self.approver_a)
        saved = self._composer().save_email("res.partner", self.record.id, email.id, {
            "from": "hieu@dwo.example", "subject": "late edit", "body": "<p>late</p>"})
        self.assertEqual((saved["id"], saved["state"]), (email.id, "sent"))
        self.assertEqual(email.subject, "Quote for approval")
        self.assertNotIn("late", email.body)

    def test_the_list_of_the_composer_has_the_unsent_emails_only(self):
        draft = self._composer().save_email("res.partner", self.record.id, False, {"from": "hieu@dwo.example", "subject": "d"})
        pending = self._request(self.approver_a, subject="p")
        sent = self._request(self.approver_a, subject="s")
        self._approve(sent, self.approver_a)
        listed = {e["id"]: e["state"] for e in self._composer().list_emails("res.partner", self.record.id)}
        self.assertEqual(listed, {draft["id"]: "draft", pending.id: "pending"})

    # ------------------------------------------------------------
    # settings
    # ------------------------------------------------------------

    def test_require_approval_refuses_the_direct_send_on_the_server(self):
        self.author.company_id.dwo_mail_require_approval = True
        with self.assertRaises(UserError):
            self._composer().send("res.partner", self.record.id, {
                "from": "hieu@dwo.example", "to": [CUSTOMER], "body": "<p>x</p>"})
        self.assertFalse(self._official_messages())
        self.assertTrue(self._composer().get_state("res.partner", self.record.id)["policy"]["require_approval"])
        # the approval path still works, even with oneself as approver
        email = self._request(self.author)
        self._approve(email, self.author)
        self.assertEqual(len(self._official_messages()), 1)

    def test_direct_send_is_allowed_without_the_setting(self):
        self.assertFalse(self._composer().get_state("res.partner", self.record.id)["policy"]["require_approval"])
        with self.mock_mail_gateway():
            self._composer().send("res.partner", self.record.id, {
                "from": "hieu@dwo.example", "to": [CUSTOMER], "body": "<p>x</p>"})
        self.assertEqual(len(self._official_messages()), 1)

    def test_retention_follows_the_setting_and_covers_every_state(self):
        params = self.env["ir.config_parameter"].sudo()
        draft = self.Email.create({"user_id": self.author.id, "res_model": "res.partner", "res_id": self.record.id})
        pending = self._request(self.approver_a)
        sent = self._request(self.approver_a)
        self._approve(sent, self.approver_a)
        rejected = self._request(self.approver_a)
        rejected.with_user(self.approver_a).action_reject()
        old = fields.Datetime.now() - timedelta(days=11)
        self.env.flush_all()  # a value still waiting in the cache would overwrite the dates set below
        for email in (draft, pending, sent, rejected):
            self.env.cr.execute("UPDATE dwo_mail_email SET last_action_date = %s WHERE id = %s", [old, email.id])
        self.Email.invalidate_model()
        params.set_param("dwo_mail_compose.retention_days", "30")
        self.env.registry.clear_cache()
        self.Email._gc_old_emails()
        self.assertEqual(len(self.Email.search([("res_id", "=", self.record.id)])), 4, "11 days is within 30")
        params.set_param("dwo_mail_compose.retention_days", "10")
        self.env.registry.clear_cache()
        self.Email._gc_old_emails()
        left = self.Email.search([("res_id", "=", self.record.id)])
        self.assertFalse(left, f"11 days is past 10, in every state; left: {left.mapped('state')} {left.mapped('last_action_date')}")
        self.assertFalse(self.env["mail.activity"].sudo().search([("res_model", "=", "dwo.mail.email")]),
                         "the activities go with the email")

    def test_retention_falls_back_to_180_days_for_a_bad_value(self):
        params = self.env["ir.config_parameter"].sudo()
        params.set_param("dwo_mail_compose.retention_days", "0")
        self.env.registry.clear_cache()
        recent = self.Email.create({"user_id": self.author.id, "res_model": "res.partner", "res_id": self.record.id})
        old = self.Email.create({"user_id": self.author.id, "res_model": "res.partner", "res_id": self.record.id})
        self.env.flush_all()
        self.env.cr.execute("UPDATE dwo_mail_email SET last_action_date = %s WHERE id = %s",
                            [fields.Datetime.now() - timedelta(days=100), recent.id])
        self.env.cr.execute("UPDATE dwo_mail_email SET last_action_date = %s WHERE id = %s",
                            [fields.Datetime.now() - timedelta(days=181), old.id])
        self.Email.invalidate_model()
        self.Email._gc_old_emails()
        self.assertTrue(recent.exists())
        self.assertFalse(old.exists())

    def test_touching_an_email_postpones_its_deletion(self):
        email = self.Email.create({"user_id": self.author.id, "res_model": "res.partner", "res_id": self.record.id})
        self.env.flush_all()
        self.env.cr.execute("UPDATE dwo_mail_email SET last_action_date = %s WHERE id = %s",
                            [fields.Datetime.now() - timedelta(days=170), email.id])
        self.Email.invalidate_model()
        email.write({"subject": "still working on it"})
        self.assertLess(fields.Datetime.now() - email.last_action_date, timedelta(minutes=5))

    def test_settings(self):
        """The module has its own block in the settings: the retention in days and the approval switch."""
        settings = self.env["res.config.settings"].with_user(self.author).create({
            "dwo_mail_retention_days": 45, "dwo_mail_require_approval": True})
        settings.execute()
        self.assertEqual(self.env["ir.config_parameter"].sudo().get_param("dwo_mail_compose.retention_days"), "45")
        self.assertTrue(self.author.company_id.dwo_mail_require_approval)
        with self.assertRaises(ValidationError):
            self.env["res.config.settings"].with_user(self.author).create({"dwo_mail_retention_days": 0})
        view = self.env["res.config.settings"].with_user(self.author).get_view(view_type="form")["arch"]
        self.assertIn("dwo_mail_compose", view)
        self.assertIn("dwo_mail_require_approval", view)
