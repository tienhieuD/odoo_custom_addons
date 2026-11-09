# -*- coding: utf-8 -*-
import unittest

from odoo.addons.mail.tests.common import MailCommon
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tools import mail as mail_tools

BCC = "hidden.boss@example.com"
BCC2 = "archive@example.com"
CC = "colleague@example.com"
CC2 = "manager@example.com"
REPLY_TO = "replies@example.com"


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
            self.record.with_user(self.user_admin).message_post(
                body="Hello", subject="Subject", message_type="comment",
                subtype_xmlid="mail.mt_comment", **kwargs)
            self.env.cr.flush()
            self.env["mail.mail"].sudo().search([("state", "=", "outgoing")]).send()

    @staticmethod
    def _header(mail, name):
        """A header of the sent message (older mocks have no msg_to / msg_cc keys)."""
        import email as email_lib
        return email_lib.message_from_string(mail["message"]).get(name) or ""

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
        )
        self.assertEqual(len(self._envelopes_with(BCC)), 1)
        self._assert_no_leak()
        recipients = {addr for mail in self.emails for addr in mail["smtp_to_list"]}
        self.assertIn("cust.a@example.com", recipients)
        self.assertIn("cust.b@example.com", recipients)

    @unittest.skip("Odoo 16 has no outgoing_email_to: an email to raw addresses only is an Odoo 19 feature")
    def test_message_post_email_only_recipients(self):
        """Raw emails go in one email: real To header, Bcc hidden, one envelope."""
        self._post(
            outgoing_email_to="one@example.com, two@example.com",
            outgoing_email_bcc=f"{BCC}, {BCC2}",
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
        )
        for mail in self.emails:
            self.assertNotIn(BCC, self._header(mail, "To") or "")
            self.assertNotIn(BCC, self._header(mail, "Cc"))

    def test_no_bcc_no_change(self):
        """Without Bcc the sending behavior is the core one."""
        self._post(partner_ids=[self.customer_a.id])
        self.assertEqual(len(self.emails), 1)
        self.assertEqual(self.emails[0]["smtp_to_list"], ["cust.a@example.com"])

    def test_bcc_deduplicated_against_visible_recipients(self):
        """An address both in the recipients and in Bcc is mailed once."""
        self._post(
            partner_ids=[self.customer_a.id],
            outgoing_email_bcc=f"{self.customer_a.email}, {BCC}",
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
        self.assertIn("cc@example.com", self._header(email, "Cc"))
        self._assert_no_leak()

    def test_wizard_bcc_comment_mode(self):
        """Full composer: Bcc typed in the wizard ends up in the envelope only."""
        composer = self.env["mail.compose.message"].with_user(self.user_admin).with_context(
            default_model="res.partner", default_res_id=self.record.id,
            default_composition_mode="comment",
        ).create({
            "subject": "Wizard", "body": "<p>Hello</p>",
            "partner_ids": [(6, 0, [self.customer_a.id])],
            "email_bcc": f" {BCC} ; {BCC2} ",
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
        composer = self.env["mail.compose.message"].with_user(self.user_admin).with_context(
            default_model="res.partner", default_res_id=self.record.id,
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
            "groups_id": [(6, 0, [self.env.ref("base.group_portal").id])],
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
        values = template.generate_email(
            [self.record.id], ["email_to", "email_cc", "email_bcc", "subject"])[self.record.id]
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
        composer = self.env["mail.compose.message"].with_user(self.user_admin).with_context(
            default_model="res.partner", default_res_id=self.record.id,
            default_composition_mode="comment",
        ).create({
            "subject": "Wizard", "body": "<p>Hello</p>", "template_id": template.id,
            "partner_ids": [(6, 0, [self.customer_a.id])], "email_bcc": BCC2,
        })
        with self.mock_mail_gateway():
            composer._action_send_mail()
            self.env.cr.flush()
            self.env["mail.mail"].sudo().search([("state", "=", "outgoing")]).send()
        self.assertEqual(len(self._envelopes_with(BCC)), 1)
        self.assertEqual(len(self._envelopes_with(BCC2)), 1)
        self._assert_no_leak()


    # ------------------------------------------------------------
    # CC
    # ------------------------------------------------------------

    def _composer(self, **values):
        vals = {"subject": "Wizard", "body": "<p>Hello</p>", "partner_ids": [(6, 0, [self.customer_a.id])],}
        vals.update(values)
        return self.env["mail.compose.message"].with_user(self.user_admin).with_context(
            default_model="res.partner", default_res_id=self.record.id,
            default_composition_mode="comment",
        ).create(vals)

    def _send_composer(self, composer):
        with self.mock_mail_gateway():
            composer._action_send_mail()
            self.env.cr.flush()
            self.env["mail.mail"].sudo().search([("state", "=", "outgoing")]).send()

    def test_message_post_cc_is_visible_and_received_once(self):
        """The Cc is written in the headers of one email and its people get one copy."""
        self._post(
            partner_ids=[self.customer_a.id, self.customer_b.id],
            outgoing_email_cc=f"{CC}, {CC2}")
        copies = self._envelopes_with(CC)
        self.assertEqual(len(copies), 1)
        self.assertIn(CC, self._header(copies[0], "Cc"))
        self.assertIn(CC2, self._header(copies[0], "Cc"))
        self.assertEqual(len(self._envelopes_with(CC2)), 1)

    def test_cc_and_bcc_together(self):
        self._post(
            partner_ids=[self.customer_a.id], outgoing_email_cc=CC, outgoing_email_bcc=BCC)
        self.assertEqual(len(self._envelopes_with(CC)), 1)
        self.assertEqual(len(self._envelopes_with(BCC)), 1)
        self._assert_no_leak()
        for mail in self.emails:
            self.assertNotIn(BCC, self._header(mail, "Cc"))

    def test_wizard_cc_comment_mode(self):
        composer = self._composer(email_cc=f"{CC}, {CC2}")
        self._send_composer(composer)
        message = self.record.message_ids[0]
        self.assertEqual(
            sorted(mail_tools.email_normalize_all(message.sudo().outgoing_email_cc)), sorted([CC, CC2]))
        self.assertEqual(len(self._envelopes_with(CC)), 1)
        self.assertIn(CC, self._header(self._envelopes_with(CC)[0], "Cc"))

    def test_wizard_cc_invalid(self):
        composer = self._composer(email_cc="not-an-email")
        with self.assertRaises(UserError):
            composer._action_send_mail()

    def test_wizard_cc_not_for_a_log_note(self):
        composer = self._composer(email_cc=CC)
        composer.is_log = True
        values = composer.sudo().get_mail_values(self.record.ids)[self.record.id]
        self.assertFalse(values.get("outgoing_email_cc"))

    def test_wizard_cc_mass_mail(self):
        """Mass mailing: the Cc typed is the Cc of each email. (Core turns the Cc of a template into
        recipients of the email, it does not keep it as a Cc.)"""
        template = self._template(email_bcc=False)
        records = self.record + self.customer_a
        composer = self.env["mail.compose.message"].with_user(self.user_admin).with_context(
            default_model="res.partner", active_ids=records.ids,
            default_composition_mode="mass_mail",
        ).create({"subject": "Mass", "body": "<p>Hello</p>", "template_id": template.id, "email_cc": f"{CC}, {CC2}"})
        with self.mock_mail_gateway():
            composer._action_send_mail()
        mails = self.env["mail.mail"].sudo().search([("model", "=", "res.partner"), ("res_id", "in", records.ids)])
        self.assertEqual(len(mails), 2)
        for mail in mails:
            self.assertEqual(sorted(mail_tools.email_normalize_all(mail.email_cc)), sorted([CC, CC2]))

    def test_direct_mail_mail_cc_is_core(self):
        """The Cc of a mail.mail is the core field: it still works as before."""
        mail = self.env["mail.mail"].sudo().create({
            "subject": "Direct", "body_html": "<p>x</p>", "email_from": "from@example.com",
            "email_to": "to@example.com", "email_cc": CC})
        with self.mock_mail_gateway():
            mail.send()
        self.assertEqual(len(self._envelopes_with(CC)), 1)
        self.assertIn(CC, self._header(self.emails[0], "Cc"))

    # ------------------------------------------------------------
    # REPLY-TO
    # ------------------------------------------------------------

    def test_wizard_reply_to_comment_mode(self):
        """Send message with a Reply-To: the header carries it and the answers leave the record."""
        composer = self._composer(reply_to=REPLY_TO)
        self._send_composer(composer)
        message = self.record.message_ids[0]
        self.assertEqual(message.reply_to, REPLY_TO)
        self.assertTrue(message.reply_to_force_new)
        self.assertTrue(any(REPLY_TO in mail["message"] and "Reply-To" in mail["message"] for mail in self.emails))

    def test_wizard_without_reply_to_keeps_the_default(self):
        composer = self._composer()
        self.assertFalse(composer.reply_to)
        self._send_composer(composer)
        message = self.record.message_ids[0]
        self.assertNotEqual(message.reply_to, REPLY_TO)
        self.assertFalse(message.reply_to_force_new)

    def test_wizard_reply_to_must_be_one_valid_address(self):
        for bad in ("not-an-email", "a@example.com, b@example.com"):
            composer = self._composer(reply_to=bad)
            with self.assertRaises(UserError, msg=bad):
                composer._action_send_mail()

    def test_wizard_reply_to_with_a_placeholder_is_checked_when_rendered(self):
        composer = self._composer(reply_to="{{ object.email }}")
        composer._dwo_check_reply_to()   # not refused: it is rendered for each record at sending

    def test_template_reply_to_reaches_the_composer(self):
        template = self._template(reply_to=REPLY_TO, email_bcc=False)
        composer = self._composer(template_id=template.id)
        composer._onchange_template_id_wrapper()   # what the form does when the template is picked
        self.assertEqual(composer.reply_to, REPLY_TO)
