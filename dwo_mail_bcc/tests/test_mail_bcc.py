# -*- coding: utf-8 -*-
from odoo.addons.mail.tests.common import MailCommon
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tools import mail as mail_tools

BCC = "hidden.boss@example.com"
BCC2 = "archive@example.com"


@tagged("post_install", "-at_install", "dwo_mail_bcc")
class TestMailBcc(MailCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer_a = cls.env["res.partner"].create({"name": "Cust A", "email": "cust.a@example.com"})
        cls.customer_b = cls.env["res.partner"].create({"name": "Cust B", "email": "cust.b@example.com"})
        cls.record = cls.env["res.partner"].create({"name": "Thread record", "email": "thread@example.com"})

    # ------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------

    def _post(self, **kwargs):
        with self.mock_mail_gateway():
            self.record.with_user(self.user_employee).message_post(
                body="Hello", subject="Subject", message_type="comment",
                subtype_xmlid="mail.mt_comment", **kwargs)
            self.env.cr.flush()
            self.env["mail.mail"].sudo().search([("state", "=", "outgoing")]).send()

    def _envelopes_with(self, address):
        return [mail for mail in self.emails if address in mail["smtp_to_list"]]

    def _assert_no_leak(self):
        for mail in self.emails:
            self.assertNotIn(BCC, mail["message"], "Bcc address leaked in the sent message")
            self.assertNotIn("Bcc:", mail["message"], "Bcc header was not stripped")

    # ------------------------------------------------------------
    # tests
    # ------------------------------------------------------------

    def test_message_post_bcc_two_partners(self):
        """2 partners + Bcc: Bcc address in exactly one envelope and in no header."""
        self._post(
            partner_ids=[self.customer_a.id, self.customer_b.id],
            outgoing_email_bcc=BCC,
            notify_skip_followers=True,
        )
        self.assertEqual(len(self._envelopes_with(BCC)), 1)
        self._assert_no_leak()
        recipients = {addr for mail in self.emails for addr in mail["smtp_to_list"]}
        self.assertIn("cust.a@example.com", recipients)
        self.assertIn("cust.b@example.com", recipients)

    def test_message_post_email_only_recipients(self):
        """Raw emails go in one email: real To header, Bcc hidden, one envelope."""
        self._post(
            outgoing_email_to="one@example.com, two@example.com",
            outgoing_email_bcc=f"{BCC}, {BCC2}",
            notify_skip_followers=True,
        )
        self.assertEqual(len(self.emails), 1)
        mail = self.emails[0]
        self.assertEqual(
            sorted(mail["smtp_to_list"]),
            sorted(["one@example.com", "two@example.com", BCC, BCC2]))
        self._assert_no_leak()
        self.assertNotIn(BCC2, mail["message"])

    def test_bcc_not_in_visible_to_via_x_msg_to_add(self):
        """Bcc must never reach the To header through X-Msg-To-Add."""
        self._post(
            partner_ids=[self.customer_a.id],
            outgoing_email_bcc=BCC,
            notify_skip_followers=True,
        )
        for mail in self.emails:
            self.assertNotIn(BCC, mail["msg_to"] or "")
            self.assertNotIn(BCC, mail["msg_cc"] or "")

    def test_no_bcc_no_change(self):
        """Without Bcc the sending behavior is the core one."""
        self._post(partner_ids=[self.customer_a.id], notify_skip_followers=True)
        self.assertEqual(len(self.emails), 1)
        self.assertEqual(self.emails[0]["smtp_to_list"], ["cust.a@example.com"])

    def test_bcc_deduplicated_against_visible_recipients(self):
        """An address both in the recipients and in Bcc is mailed once."""
        self._post(
            partner_ids=[self.customer_a.id],
            outgoing_email_bcc=f"{self.customer_a.email}, {BCC}",
            notify_skip_followers=True,
        )
        a_envelopes = self._envelopes_with("cust.a@example.com")
        self.assertEqual(len(a_envelopes), 1)
        self.assertEqual(len(self._envelopes_with(BCC)), 1)

    def test_only_first_mail_keeps_bcc(self):
        """Several mail.mail for one message: Bcc stays on the first only."""
        message = self.env["mail.message"].create({
            "model": "res.partner", "res_id": self.record.id, "body": "x",
            "message_type": "comment", "outgoing_email_bcc": BCC,
        })
        mails = self.env["mail.mail"].create([
            {"mail_message_id": message.id, "email_to": "a@example.com", "email_bcc": BCC},
            {"mail_message_id": message.id, "email_to": "b@example.com", "email_bcc": BCC},
            {"mail_message_id": message.id, "email_to": "c@example.com", "email_bcc": BCC},
        ])
        self.assertEqual(mails.mapped("email_bcc"), [BCC, False, False])
        # a copy of the same mail (core throttling does this) does not duplicate it either
        copied = mails[0].copy({"mail_message_id": message.id})
        self.assertFalse(copied.email_bcc)

    def test_direct_mail_mail_bcc(self):
        """Direct mail.mail with To + Cc + Bcc: envelope has all, headers hide Bcc."""
        with self.mock_mail_gateway():
            mail = self.env["mail.mail"].create({
                "email_from": "sender@example.com", "subject": "Direct", "body_html": "<p>Hi</p>",
                "email_to": "to@example.com", "email_cc": "cc@example.com", "email_bcc": BCC,
            })
            mail.send()
        self.assertEqual(len(self.emails), 1)
        email = self.emails[0]
        self.assertEqual(
            sorted(email["smtp_to_list"]), sorted(["to@example.com", "cc@example.com", BCC]))
        self.assertIn("cc@example.com", email["msg_cc"])
        self._assert_no_leak()

    def test_wizard_bcc_comment_mode(self):
        """Full composer: Bcc typed in the wizard ends up in the envelope only."""
        composer = self.env["mail.compose.message"].with_user(self.user_employee).with_context(
            default_model="res.partner", default_res_ids=self.record.ids,
            default_composition_mode="comment",
        ).create({
            "subject": "Wizard", "body": "<p>Hello</p>",
            "partner_ids": [(6, 0, [self.customer_a.id])],
            "email_bcc": f" {BCC} ; {BCC2} ",
            "notify_skip_followers": True,
        })
        with self.mock_mail_gateway():
            composer._action_send_mail()
            self.env.cr.flush()
            self.env["mail.mail"].sudo().search([("state", "=", "outgoing")]).send()
        self.assertEqual(len(self._envelopes_with(BCC)), 1)
        self.assertEqual(len(self._envelopes_with(BCC2)), 1)
        self._assert_no_leak()
        message = self.record.message_ids[0]
        self.assertEqual(
            sorted(mail_tools.email_normalize_all(message.sudo().outgoing_email_bcc)),
            sorted([BCC, BCC2]))

    def test_wizard_bcc_invalid(self):
        composer = self.env["mail.compose.message"].with_user(self.user_employee).with_context(
            default_model="res.partner", default_res_ids=self.record.ids,
            default_composition_mode="comment",
        ).create({
            "subject": "Wizard", "body": "<p>Hello</p>",
            "partner_ids": [(6, 0, [self.customer_a.id])],
            "email_bcc": "not-an-email",
        })
        with self.assertRaises(UserError):
            composer._action_send_mail()

    def test_bcc_field_hidden_from_portal(self):
        """The stored Bcc is not readable by portal users."""
        portal = self.env["res.users"].with_context(no_reset_password=True).create({
            "name": "Portal", "login": "portal_bcc", "email": "portal@example.com",
            "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])],
        })
        message = self.env["mail.message"].create({
            "model": "res.partner", "res_id": self.record.id, "body": "x",
            "message_type": "comment", "outgoing_email_bcc": BCC,
        })
        field = self.env["mail.message"].with_user(portal)._fields["outgoing_email_bcc"]
        self.assertEqual(field.groups, "base.group_user")
        self.assertTrue(message.id)

    # ------------------------------------------------------------
    # TEMPLATE
    # ------------------------------------------------------------

    def _template(self, **values):
        vals = {
            "name": "Bcc template", "model_id": self.env["ir.model"]._get("res.partner").id,
            "subject": "Hello {{ object.name }}", "body_html": "<p>Hi</p>",
            "email_from": "sender@example.com", "email_to": "{{ object.email }}",
            "email_bcc": "{{ object.name }}.archive@example.com",
        }
        vals.update(values)
        return self.env["mail.template"].create(vals)

    def test_template_bcc_is_rendered_per_record(self):
        """The placeholders of the template Bcc are computed for each record."""
        template = self._template(email_bcc="bcc.{{ object.id }}@example.com")
        values = template._generate_template(
            [self.record.id], ("email_to", "email_cc", "email_bcc", "subject"))[self.record.id]
        self.assertEqual(values["email_bcc"], f"bcc.{self.record.id}@example.com")

    def test_template_send_mail_reaches_bcc_only_in_envelope(self):
        template = self._template(email_bcc=BCC)
        with self.mock_mail_gateway():
            mail_id = template.send_mail(self.record.id)
            self.assertEqual(self.env["mail.mail"].browse(mail_id).email_bcc, BCC)
            self.env["mail.mail"].browse(mail_id).send()
        self.assertEqual(len(self._envelopes_with(BCC)), 1)
        self._assert_no_leak()

    def test_template_bcc_in_composer_comment_mode(self):
        """Send message with a template: the rendered template Bcc joins the typed Bcc."""
        template = self._template(email_bcc=BCC, email_to=False)
        composer = self.env["mail.compose.message"].with_user(self.user_employee).with_context(
            default_model="res.partner", default_res_ids=self.record.ids,
            default_composition_mode="comment",
        ).create({
            "subject": "Wizard", "body": "<p>Hello</p>", "template_id": template.id,
            "partner_ids": [(6, 0, [self.customer_a.id])], "email_bcc": BCC2,
            "notify_skip_followers": True,
        })
        with self.mock_mail_gateway():
            composer._action_send_mail()
            self.env.cr.flush()
            self.env["mail.mail"].sudo().search([("state", "=", "outgoing")]).send()
        self.assertEqual(len(self._envelopes_with(BCC)), 1)
        self.assertEqual(len(self._envelopes_with(BCC2)), 1)
        self._assert_no_leak()
