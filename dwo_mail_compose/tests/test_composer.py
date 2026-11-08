# -*- coding: utf-8 -*-
import email
import email.policy
from unittest.mock import patch

from odoo import tools
from odoo.addons.mail.tests.common import MailCommon
from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged

CUSTOMER = "lan.pham@customer.example"
COLLEAGUE = "thu.le@customer.example"
BOSS = "boss@customer.example"
HIDDEN = "archive.hidden@elsewhere.example"


@tagged("post_install", "-at_install", "dwo_mail_compose")
class TestComposer(MailCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin = cls.user_admin
        cls.admin.write({"email": "hieu@dwo.example", "tz": "Asia/Tokyo"})
        # changing the email queues a security notice: drop it so it never pollutes the SMTP assertions
        cls.env["mail.mail"].sudo().search([]).unlink()
        cls.record = cls.env["res.partner"].create({"name": "Quotation thread"})
        cls.composer = cls.env["dwo.mail.composer"].with_user(cls.admin)

    def _incoming(self, subject="Quotation S00042", email_from=f"Lan Pham <{CUSTOMER}>",
                  to=f"Hieu <hieu@dwo.example>", cc=f"{COLLEAGUE}, {BOSS}", date="2026-11-06 09:12:00"):
        return self.env["mail.message"].create({
            "model": "res.partner", "res_id": self.record.id, "message_type": "email",
            "subject": subject, "email_from": email_from, "incoming_email_to": to,
            "incoming_email_cc": cc, "date": date, "body": "<p>Please lower the quantity to 30.</p>",
        })

    def _send(self, **vals):
        payload = {
            "from": "hieu@dwo.example", "to": [CUSTOMER], "cc": [COLLEAGUE], "bcc": [HIDDEN],
            "subject": "Quotation S00042", "body": "<p>Here is the new quote.</p>",
        }
        payload.update(vals)
        with self.mock_mail_gateway():
            result = self.composer.send("res.partner", self.record.id, payload)
            self.env.cr.flush()
            self.env["mail.mail"].sudo().search([("state", "=", "outgoing")]).send()
        return result

    # ------------------------------------------------------------
    # DEFAULTS
    # ------------------------------------------------------------

    def test_defaults_no_email(self):
        """A. empty thread: only From is set, to the current user."""
        state = self.composer.get_state("res.partner", self.record.id)
        d = state["defaults"]
        self.assertEqual(d["from"], "hieu@dwo.example")
        self.assertEqual((d["to"], d["cc"], d["bcc"], d["subject"], d["ref_message_id"]), ([], [], [], "", False))
        self.assertFalse(state["current"])

    def test_defaults_reply_all_to_incoming(self):
        """B. reply-all: To is the sender, Cc is the others without me, subject RE."""
        incoming = self._incoming()
        d = self.composer.get_defaults("res.partner", self.record.id)
        self.assertEqual([a["email"] for a in d["to"]], [CUSTOMER])
        self.assertEqual(sorted(a["email"] for a in d["cc"]), sorted([COLLEAGUE, BOSS]))
        self.assertEqual(d["bcc"], [])
        self.assertEqual(d["from"], "hieu@dwo.example")
        self.assertEqual(d["subject"], "RE: Quotation S00042")
        self.assertEqual(d["ref_message_id"], incoming.id)

    def test_defaults_subject_prefix_not_repeated(self):
        self._incoming(subject="RE: Re: FW: Quotation S00042")
        d = self.composer.get_defaults("res.partner", self.record.id)
        self.assertEqual(d["subject"], "RE: Quotation S00042")

    def test_quote_meta_outlook_style(self):
        """The quote is an Outlook block, in the author's timezone, without Bcc."""
        self._incoming(cc="", date="2026-11-06 09:12:00")
        body = self.composer.get_defaults("res.partner", self.record.id)["body"]
        self.assertIn('id="divRplyFwdMsg"', body)
        self.assertIn("---------- Original message ----------", body)
        self.assertIn("<b>From:</b>", body)
        self.assertIn("<b>To:</b>", body)
        self.assertNotIn("<b>Cc:</b>", body, "an empty Cc line must not be written")
        self.assertNotIn("Bcc", body)
        self.assertIn("2026-11-06 18:12 (JST)", body)
        self.assertIn("Please lower the quantity to 30.", body)

    def test_quote_date_zone_without_letters(self):
        self.admin.tz = "Asia/Ho_Chi_Minh"
        self._incoming()
        body = self.composer.get_defaults("res.partner", self.record.id)["body"]
        self.assertIn("2026-11-06 16:12 (UTC+07:00)", body)

    def test_defaults_after_our_email_copy_everyone(self):
        """C. last email is ours: same From, To, Cc and Bcc."""
        self._send()
        d = self.composer.get_defaults("res.partner", self.record.id)
        self.assertEqual([a["email"] for a in d["to"]], [CUSTOMER])
        self.assertEqual([a["email"] for a in d["cc"]], [COLLEAGUE])
        self.assertEqual([a["email"] for a in d["bcc"]], [HIDDEN])
        self.assertEqual(d["subject"], "RE: Quotation S00042")
        self.assertNotIn(HIDDEN, d["body"], "the Bcc must not leak into the quote")

    def test_defaults_forward(self):
        incoming = self._incoming()
        d = self.composer.get_defaults("res.partner", self.record.id, incoming.id, "forward")
        self.assertEqual((d["to"], d["cc"], d["bcc"]), ([], [], []))
        self.assertEqual(d["subject"], "FW: Quotation S00042")
        self.assertIn("Forwarded message", d["body"])

    # ------------------------------------------------------------
    # SENDING
    # ------------------------------------------------------------

    def test_send_single_email_real_headers(self):
        """One SMTP email: To and Cc visible, Bcc only in the envelope, followers not notified."""
        follower = self.env["res.partner"].create({"name": "Follower", "email": "follower@x.example"})
        self.record.message_subscribe(partner_ids=follower.ids)
        result = self._send()
        self.assertEqual(len(self.emails), 1, [e["smtp_to_list"] for e in self.emails])
        mail = self.emails[0]
        self.assertEqual(
            sorted(mail["smtp_to_list"]), sorted([CUSTOMER, COLLEAGUE, HIDDEN]))
        self.assertIn(CUSTOMER, mail["msg_to"])
        self.assertIn(COLLEAGUE, mail["msg_cc"])
        self.assertNotIn(HIDDEN, mail["message"])
        self.assertNotIn("follower@x.example", mail["message"])
        message = self.env["mail.message"].browse(result["message_id"])
        self.assertTrue(message.dwo_is_from_compose)
        self.assertEqual(message.sudo().outgoing_email_bcc, HIDDEN)

    def test_sent_mail_is_kept_not_auto_deleted(self):
        """The mail.mail of an official email stays after sending (core deletes notifications by default)."""
        with self.mock_mail_gateway(mail_unlink_sent=True):
            result = self.composer.send("res.partner", self.record.id, {
                "from": "hieu@dwo.example", "to": [CUSTOMER], "subject": "Kept", "body": "<p>Keep me</p>"})
            self.env.cr.flush()
            self.env["mail.mail"].sudo().search([("state", "=", "outgoing")]).send()
        mails = self.env["mail.mail"].sudo().search([("mail_message_id", "=", result["message_id"])])
        self.assertEqual(len(mails), 1, "the mail.mail was deleted after sending")
        self.assertFalse(mails.auto_delete)
        self.assertEqual(mails.state, "sent")

    def test_same_address_may_be_in_to_cc_and_bcc(self):
        """No limit between the fields: an address typed in To can be typed again in Cc and Bcc."""
        self._send(to=[CUSTOMER], cc=[CUSTOMER, COLLEAGUE], bcc=[CUSTOMER, HIDDEN])
        message = self.env["mail.message"].search(
            [("model", "=", "res.partner"), ("res_id", "=", self.record.id), ("dwo_is_from_compose", "=", True)])
        self.assertIn(CUSTOMER, message.outgoing_email_to)
        self.assertIn(CUSTOMER, message.sudo().outgoing_email_cc)
        self.assertIn(CUSTOMER, message.sudo().outgoing_email_bcc)

    def test_send_clean_layout(self):
        """The official email is the body only: no notification header or footer."""
        self._send()
        html = self.emails[0]["message"]
        self.assertNotIn("Powered by", html)
        self.assertIn("Here is the new quote.", html)

    def test_send_registers_unknown_addresses_only(self):
        known = self.env["res.partner"].create({"name": "Known", "email": "known@x.example"})
        self._send(to=[CUSTOMER, "Known <known@x.example>"], cc=[], bcc=[])
        book = self.env["dwo.mail.address"].search([]).mapped("email")
        self.assertIn(CUSTOMER, book)
        self.assertNotIn(known.email, book)
        # sending again increments the usage instead of duplicating the row
        self._send(to=[CUSTOMER], cc=[], bcc=[])
        rows = self.env["dwo.mail.address"].search([("email", "=", CUSTOMER)])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows.use_count, 2)

    def test_send_validations(self):
        with self.assertRaises(UserError):
            self.composer.send("res.partner", self.record.id, {"from": "hieu@dwo.example", "to": [], "body": "x"})
        with self.assertRaises(UserError):
            self.composer.send("res.partner", self.record.id, {"from": "hieu@dwo.example", "to": ["not-an-email"], "body": "x"})
        with self.assertRaises(AccessError):
            self.composer.send("res.partner", self.record.id, {"from": "ceo@other.example", "to": [CUSTOMER], "body": "x"})

    def test_reply_of_customer_comes_back_to_thread(self):
        """A reply with In-Reply-To of our email lands in the same record (threading)."""
        result = self._send()
        message = self.env["mail.message"].browse(result["message_id"])
        self.assertTrue(message.message_id)
        raw = (
            f"From: Lan Pham <{CUSTOMER}>\n"
            "To: hieu@dwo.example\n"
            "Subject: Re: Quotation S00042\n"
            "Message-Id: <customer-reply-1@customer.example>\n"
            f"In-Reply-To: {message.message_id}\n"
            f"References: {message.message_id}\n"
            "MIME-Version: 1.0\n"
            "Content-Type: text/plain; charset=utf-8\n\n"
            "Thank you, approved.\n"
        )
        self.env["mail.thread"].sudo().message_process(False, raw)
        replies = self.env["mail.message"].search([
            ("model", "=", "res.partner"), ("res_id", "=", self.record.id), ("message_type", "=", "email")])
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies.parent_id, message)
        # and the next default is a reply-all to the customer
        d = self.composer.get_defaults("res.partner", self.record.id)
        self.assertEqual([a["email"] for a in d["to"]], [CUSTOMER])

    # ------------------------------------------------------------
    # DRAFT
    # ------------------------------------------------------------

    def _save(self, email_id=False, **vals):
        payload = {"from": "hieu@dwo.example"}
        payload.update(vals)
        return self.composer.save_email("res.partner", self.record.id, email_id, payload)

    def test_email_save_load_delete(self):
        self._incoming()
        first = self._save(to=[{"email": CUSTOMER, "name": "Lan"}], subject="RE: Quotation S00042",
                           body="<p>work in progress</p>")
        second = self._save(first["id"], to=[{"email": CUSTOMER, "name": "Lan"}], subject="RE: Quotation S00042",
                            body="<p>work in progress 2</p>")
        self.assertEqual(first["id"], second["id"], "the id of the first save is used by the next ones")
        self.assertEqual(len(self.env["dwo.mail.email"].search([("res_id", "=", self.record.id)])), 1)
        state = self.composer.get_state("res.partner", self.record.id)
        self.assertIn("work in progress 2", state["current"]["body"])
        self.assertEqual([e["id"] for e in state["emails"]], [first["id"]])
        # deleting returns the initial logic, here a reply-all
        defaults = self.composer.delete_email("res.partner", self.record.id, first["id"])
        self.assertFalse(self.env["dwo.mail.email"].search([("res_id", "=", self.record.id)]))
        self.assertEqual(defaults["subject"], "RE: Quotation S00042")
        self.assertEqual([a["email"] for a in defaults["to"]], [CUSTOMER])

    def test_several_emails_on_one_record(self):
        first = self._save(subject="First", body="<p>1</p>")
        second = self._save(subject="Second", body="<p>2</p>")
        self.assertNotEqual(first["id"], second["id"])
        listed = {e["subject"] for e in self.composer.list_emails("res.partner", self.record.id)}
        self.assertEqual(listed, {"First", "Second"})
        self.assertEqual(self.composer.load_email(first["id"])["subject"], "First")

    def test_the_form_opens_on_the_newest_created_email_unless_one_was_chosen(self):
        oldest = self._save(subject="Oldest", body="<p>1</p>")
        middle = self._save(subject="Middle", body="<p>2</p>")
        newest = self._save(subject="Newest", body="<p>3</p>")
        # editing an older one does not make it the newest: the order is the creation date
        self._save(oldest["id"], subject="Oldest, edited last", body="<p>1</p>")
        state = self.composer.get_state("res.partner", self.record.id)
        self.assertEqual(state["current"]["id"], newest["id"])
        self.assertEqual([e["id"] for e in state["emails"]], [newest["id"], middle["id"], oldest["id"]],
                         "the list is newest created first")
        # the email chosen last on this screen wins, when it is still there
        chosen = self.composer.get_state("res.partner", self.record.id, middle["id"])
        self.assertEqual(chosen["current"]["id"], middle["id"])
        self.composer.delete_email("res.partner", self.record.id, middle["id"])
        gone = self.composer.get_state("res.partner", self.record.id, middle["id"])
        self.assertEqual(gone["current"]["id"], newest["id"], "a deleted choice falls back to the newest")

    def test_the_form_opens_on_a_waiting_or_rejected_email_too(self):
        """The newest created is shown whatever its state, not only a draft."""
        draft = self._save(subject="A draft", body="<p>d</p>")
        newer = self._save(subject="Asked", body="<p>p</p>", to=[CUSTOMER])
        self.composer.request_approval("res.partner", self.record.id, newer["id"], {
            "from": "hieu@dwo.example", "to": [CUSTOMER], "subject": "Asked", "body": "<p>p</p>"},
            self.admin.ids, None)
        state = self.composer.get_state("res.partner", self.record.id)
        self.assertEqual((state["current"]["id"], state["current"]["state"]), (newer["id"], "pending"))
        summaries = {e["id"]: e for e in state["emails"]}
        self.assertTrue(summaries[draft["id"]]["created"] and summaries[draft["id"]]["updated"])

    def test_deleting_a_waiting_email_from_the_list(self):
        """A submitted or rejected email can be deleted too; the approvers are told."""
        saved = self._save(subject="To delete", body="<p>x</p>", to=[CUSTOMER])
        self.composer.request_approval("res.partner", self.record.id, saved["id"], {
            "from": "hieu@dwo.example", "to": [CUSTOMER], "subject": "To delete", "body": "<p>x</p>"},
            self.user_employee.ids, None)
        self.composer.delete_email("res.partner", self.record.id, saved["id"])
        self.assertFalse(self.env["dwo.mail.email"].search([("id", "=", saved["id"])]))
        self.assertFalse(self.composer.list_emails("res.partner", self.record.id))

    def test_email_is_private_to_its_author(self):
        saved = self._save(body="<p>mine</p>")
        other = self.env["dwo.mail.composer"].with_user(self.user_employee)
        self.assertFalse(other.get_state("res.partner", self.record.id)["current"])
        with self.assertRaises(AccessError):
            other.load_email(saved["id"])

    def test_sending_directly_removes_the_stored_email(self):
        saved = self._save(to=[CUSTOMER], body="<p>x</p>")
        with self.mock_mail_gateway():
            self.composer.send("res.partner", self.record.id, {
                "email_id": saved["id"], "from": "hieu@dwo.example", "to": [CUSTOMER], "body": "<p>x</p>"})
        self.assertFalse(self.env["dwo.mail.email"].search([("id", "=", saved["id"])]))

    def test_newer_email_banner(self):
        self._incoming(date="2026-11-06 09:00:00")
        self._save(body="<p>x</p>")
        # an email arrives after the draft was saved
        self._incoming(subject="Another", date="2999-01-01 00:00:00")
        state = self.composer.get_state("res.partner", self.record.id)
        self.assertTrue(state["newer_email"])

    # ------------------------------------------------------------
    # SUGGESTIONS
    # ------------------------------------------------------------

    def test_suggestions_are_unique(self):
        self.env["res.partner"].create({"name": "Dup Partner", "email": "dup@x.example"})
        self.env["dwo.mail.address"].create({"email": "DUP@x.example", "name": "Dup Book"})
        self.env["dwo.mail.address"].create({"email": "only.book@x.example"})
        found = self.composer.suggest("x.example")
        emails = [f["email"] for f in found]
        self.assertEqual(len(emails), len(set(emails)))
        self.assertIn("dup@x.example", emails)
        self.assertIn("only.book@x.example", emails)
        self.assertEqual(next(f for f in found if f["email"] == "dup@x.example")["source"], "partner")
        self.assertEqual(self.composer.suggest("x.example", exclude=["dup@x.example"]).count(
            next(f for f in found if f["email"] == "dup@x.example")), 0)

    def test_address_book_unique_per_company(self):
        self.env["dwo.mail.address"].create({"email": "Same@x.example"})
        with self.assertRaises(Exception), self.cr.savepoint():
            self.env["dwo.mail.address"].create({"email": "same@X.example"})

    # ------------------------------------------------------------
    # HOSTILE CALLERS
    # ------------------------------------------------------------

    def test_portal_user_cannot_use_the_api(self):
        """The API reads messages in sudo: a portal user must not reach it, even on a record they can read."""
        note = self.env["mail.message"].create({
            "model": "res.partner", "res_id": self.record.id, "message_type": "comment",
            "subtype_id": self.env.ref("mail.mt_note").id, "body": "<p>secret internal note</p>"})
        portal = self.env["res.users"].with_context(no_reset_password=True).create({
            "name": "Portal", "login": "portal_composer", "email": "portal@x.example",
            "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])]})
        api = self.env["dwo.mail.composer"].with_user(portal)
        with self.assertRaises(AccessError):
            api.get_defaults("res.partner", portal.partner_id.id, note.id, "reply")
        with self.assertRaises(AccessError):
            api.get_state("res.partner", portal.partner_id.id)
        with self.assertRaises(AccessError):
            api.suggest("a")

    def test_notes_cannot_be_quoted(self):
        """Even for an internal user, only emails can be the reference of a reply or forward."""
        note = self.env["mail.message"].create({
            "model": "res.partner", "res_id": self.record.id, "message_type": "comment",
            "subtype_id": self.env.ref("mail.mt_note").id, "body": "<p>secret internal note</p>"})
        defaults = self.composer.get_defaults("res.partner", self.record.id, note.id, "reply")
        self.assertNotIn("secret internal note", defaults["body"])

    def test_foreign_attachment_is_refused(self):
        """An internal user cannot mail out an attachment that is not their own pending upload."""
        foreign = self.env["ir.attachment"].sudo().create({
            "name": "payroll.txt", "raw": b"salaries", "res_model": "res.partner", "res_id": self.record.id})
        with self.assertRaises(AccessError):
            self.composer.send("res.partner", self.record.id, {
                "from": "hieu@dwo.example", "to": [CUSTOMER], "body": "<p>x</p>",
                "attachment_ids": [foreign.id]})
        # and a draft never keeps it
        self._save(attachment_ids=[foreign.id])
        stored = self.env["dwo.mail.email"].search([("res_id", "=", self.record.id)])
        self.assertFalse(stored.attachment_ids)

    def test_own_pending_attachment_is_sent(self):
        pending = self.env["ir.attachment"].with_user(self.admin).sudo().create({
            "name": "quote.pdf", "raw": b"%PDF", "res_model": "mail.compose.message", "res_id": 0})
        self.assertEqual(pending.create_uid, self.admin)
        result = self._send(attachment_ids=[pending.id])
        message = self.env["mail.message"].browse(result["message_id"])
        self.assertEqual(message.attachment_ids.name, "quote.pdf")

    # ------------------------------------------------------------
    # TEMPLATE
    # ------------------------------------------------------------

    def _template(self, **values):
        self.record.email = "cust.tpl@x.example"
        extra = self.env["res.partner"].create({"name": "Extra Partner", "email": "extra.partner@x.example"})
        static = self.env["ir.attachment"].create({
            "name": "terms.txt", "raw": b"terms", "res_model": "mail.template", "res_id": 0})
        vals = {
            "name": "Quote template", "model_id": self.env["ir.model"]._get("res.partner").id,
            "subject": "Quote for {{ object.name }}", "use_default_to": False,
            "body_html": '<p>Dear <t t-out="object.name"/>, here is your quote.</p>',
            "email_from": "hieu@dwo.example", "email_to": "{{ object.email }}",
            "partner_to": str(extra.id), "email_cc": "cc.tpl@x.example",
            "email_bcc": "bcc.{{ object.id }}@x.example", "attachment_ids": [(6, 0, static.ids)],
        }
        vals.update(values)
        return self.env["mail.template"].create(vals)

    def test_template_applies_everything_computed(self):
        template = self._template()
        result = self.composer.apply_template(template.id, "res.partner", self.record.id)
        self.assertEqual(result["subject"], f"Quote for {self.record.name}")
        self.assertIn(f"Dear {self.record.name}, here is your quote.", result["body"])
        self.assertEqual(result["from"], "hieu@dwo.example")
        self.assertEqual(sorted(a["email"] for a in result["to"]), ["cust.tpl@x.example", "extra.partner@x.example"])
        self.assertEqual([a["email"] for a in result["cc"]], ["cc.tpl@x.example"])
        self.assertEqual([a["email"] for a in result["bcc"]], [f"bcc.{self.record.id}@x.example"])
        self.assertEqual([a["name"] for a in result["attachments"]], ["terms.txt"])
        self.assertEqual(result["warnings"], [])

    def test_template_attachments_are_pending_copies_that_can_be_sent(self):
        template = self._template()
        result = self.composer.apply_template(template.id, "res.partner", self.record.id)
        copy = self.env["ir.attachment"].browse(result["attachments"][0]["id"])
        self.assertEqual((copy.res_model, copy.res_id, copy.create_uid), ("mail.compose.message", 0, self.admin))
        self.assertNotIn(copy, template.attachment_ids, "the template keeps its own file")
        sent = self._send(attachment_ids=[copy.id])
        self.assertEqual(self.env["mail.message"].browse(sent["message_id"]).attachment_ids.name, "terms.txt")

    def test_template_of_another_model_is_refused(self):
        template = self._template(model_id=self.env["ir.model"]._get("res.users").id,
                                  email_to=False, partner_to=False, email_bcc=False)
        with self.assertRaises(UserError):
            self.composer.apply_template(template.id, "res.partner", self.record.id)

    def test_template_sender_not_allowed_is_ignored_with_a_warning(self):
        template = self._template(email_from="ceo@other.example")
        result = self.composer.apply_template(template.id, "res.partner", self.record.id)
        self.assertFalse(result["from"])
        self.assertEqual(len(result["warnings"]), 1)

    def test_template_default_recipients_mode(self):
        """With "Default Recipients" on, core uses the recipients of the record, not the To/Cc of the template."""
        template = self._template(use_default_to=True)
        result = self.composer.apply_template(template.id, "res.partner", self.record.id)
        self.assertEqual([a["email"] for a in result["to"]], ["cust.tpl@x.example"])
        self.assertEqual(result["cc"], [])
        # the Bcc does not depend on this switch
        self.assertEqual([a["email"] for a in result["bcc"]], [f"bcc.{self.record.id}@x.example"])

    # ------------------------------------------------------------
    # REPLY-TO
    # ------------------------------------------------------------

    def _odoo_reply_to(self):
        formatted = self.record._notify_get_reply_to(default="x@x.example", author_id=self.admin.partner_id.id)
        return tools.email_normalize(formatted[self.record.id])

    def test_default_reply_to_is_the_one_odoo_computes_for_the_record(self):
        d = self.composer.get_defaults("res.partner", self.record.id)
        self.assertEqual(d["reply_to"], self._odoo_reply_to())
        self.assertFalse(d["reply_to_custom"])
        self.assertTrue(d["reply_to_managed"], "the catchall is handled by Odoo")

    def test_default_reply_to_follows_a_model_override_like_crm_team_alias(self):
        """CRM answers with the alias of the sales team: the form shows what the model says."""
        def team_alias(records, default=None, author_id=False):
            return {record.id: '"Sales" <sales.team@x.example>' for record in records}
        with patch.object(type(self.env["res.partner"]), "_notify_get_reply_to", team_alias):
            d = self.composer.get_defaults("res.partner", self.record.id)
            self.assertEqual(d["reply_to"], "sales.team@x.example")
            sent = self._send()
        self.assertIn("sales.team@x.example", self.emails[0]["message"].split("Reply-To:")[1].split("\r\n")[0])
        self.assertTrue(sent["message_id"])

    def test_sent_email_keeps_the_odoo_reply_to_by_default(self):
        self._send()
        header = self.emails[0]["message"].split("Reply-To:")[1].split("\r\n")[0]
        self.assertIn(self._odoo_reply_to(), header)

    def test_custom_reply_to_is_used_and_validated(self):
        self._send(reply_to="me.direct@dwo.example", reply_to_custom=True)
        header = self.emails[0]["message"].split("Reply-To:")[1].split("\r\n")[0]
        self.assertIn("me.direct@dwo.example", header)
        self.assertNotIn(self._odoo_reply_to(), header)
        with self.assertRaises(UserError):
            self.composer.send("res.partner", self.record.id, {
                "from": "hieu@dwo.example", "to": [CUSTOMER], "body": "<p>x</p>",
                "reply_to": "not an email", "reply_to_custom": True})

    def test_reply_to_managed_flag(self):
        outside = self.composer.get_reply_to("res.partner", self.record.id, "hieu@dwo.example", "someone@elsewhere.example")
        self.assertFalse(outside["managed"], "a mailbox outside Odoo does not bring the reply back to the record")
        inside = self.composer.get_reply_to("res.partner", self.record.id, "hieu@dwo.example")
        self.assertTrue(inside["managed"])
        self.assertEqual(inside["default"]["email"], self._odoo_reply_to())

    def test_draft_keeps_the_reply_to_choice(self):
        self._save(reply_to="me.direct@dwo.example", reply_to_custom=True)
        draft = self.composer.get_state("res.partner", self.record.id)["current"]
        self.assertEqual((draft["reply_to"], draft["reply_to_custom"]), ("me.direct@dwo.example", True))

    # ------------------------------------------------------------
    # SAVE AS TEMPLATE
    # ------------------------------------------------------------

    def test_save_as_template_drops_the_quote_and_copies_attachments(self):
        pending = self.env["ir.attachment"].with_user(self.admin).sudo().create({
            "name": "keep.pdf", "raw": b"%PDF", "res_model": "mail.compose.message", "res_id": 0})
        body = ('<p>Dear customer, thanks.</p><div id="divRplyFwdMsg"><div>---------- Original message ----------</div>'
                '<div>secret quoted text</div></div>')
        result = self.composer.save_as_template("res.partner", self.record.id, "My quote answer", {
            "subject": "RE: FW: Quotation S00042", "body": body, "attachment_ids": [pending.id]})
        template = self.env["mail.template"].browse(result["id"])
        self.assertEqual(template.model, "res.partner")
        self.assertEqual(template.user_id, self.admin)
        self.assertEqual(template.subject, "Quotation S00042")
        self.assertIn("Dear customer, thanks.", template.body_html)
        self.assertNotIn("secret quoted text", template.body_html)
        self.assertNotIn("divRplyFwdMsg", template.body_html)
        self.assertEqual(template.attachment_ids.mapped("name"), ["keep.pdf"])
        self.assertNotEqual(template.attachment_ids, pending)
        self.assertEqual(pending.res_model, "mail.compose.message", "the file stays pending for the email")
        with self.assertRaises(UserError):
            self.composer.save_as_template("res.partner", self.record.id, "  ", {"body": "<p>x</p>"})

    # ------------------------------------------------------------
    # REPLY BUTTONS AND PASTED IMAGES
    # ------------------------------------------------------------

    def test_reply_to_sender_only_has_no_cc(self):
        """The Reply button writes to the sender only; Reply all keeps the others in Cc."""
        self._incoming()
        only = self.composer.get_defaults("res.partner", self.record.id, False, "reply_sender")
        self.assertEqual([a["email"] for a in only["to"]], [CUSTOMER])
        self.assertEqual(only["cc"], [])
        self.assertEqual(only["mode"], "reply")
        self.assertEqual(only["subject"], "RE: Quotation S00042")
        everyone = self.composer.get_defaults("res.partner", self.record.id, False, "reply")
        self.assertEqual(len(everyone["cc"]), 2)

    PIXEL = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")

    def _body_with_image(self):
        return '<p>See:</p><img src="data:image/png;base64,%s" style="width: 50%%;"/>' % self.PIXEL

    def test_pasted_image_becomes_an_attachment_link_when_the_draft_is_saved(self):
        saved = self.composer.save_email("res.partner", self.record.id, False, {"body": self._body_with_image()})
        body = self.env["dwo.mail.email"].browse(saved["id"]).body
        self.assertNotIn("base64", body)
        attachment = self.env["ir.attachment"].search([
            ("res_model", "=", "res.partner"), ("res_id", "=", self.record.id), ("mimetype", "=", "image/png")])
        self.assertEqual(len(attachment), 1)
        self.assertIn("/web/image/%d?access_token=%s" % (attachment.id, attachment.access_token), body)
        # autosave sends the same picture again: it is not stored twice
        self.composer.save_email("res.partner", self.record.id, saved["id"], {"body": self._body_with_image()})
        self.assertEqual(self.env["ir.attachment"].search_count([
            ("res_model", "=", "res.partner"), ("res_id", "=", self.record.id), ("mimetype", "=", "image/png")]), 1)

    def test_pasted_image_is_never_sent_as_base64(self):
        self._send(cc=[], bcc=[], body=self._body_with_image())
        message = self.env["mail.message"].search([
            ("model", "=", "res.partner"), ("res_id", "=", self.record.id), ("dwo_is_from_compose", "=", True)])
        self.assertNotIn("base64", message.body)
        self.assertIn("/web/image/", message.body)

    # ------------------------------------------------------------
    # EMAIL SENT TO THE SYSTEM (CATCHALL)
    # ------------------------------------------------------------

    def test_reply_to_my_own_email_to_the_system_goes_to_the_sender(self):
        """I wrote to the catchall to answer a thread: the core keeps no To (aliases are removed) and
        I am the sender. The reply still defaults To to the address it came from."""
        self._incoming(email_from="Hieu <hieu@dwo.example>", to="", cc="")
        d = self.composer.get_defaults("res.partner", self.record.id, False, "reply")
        self.assertEqual([a["email"] for a in d["to"]], ["hieu@dwo.example"])
        self.assertEqual(d["cc"], [])
        only = self.composer.get_defaults("res.partner", self.record.id, False, "reply_sender")
        self.assertEqual([a["email"] for a in only["to"]], ["hieu@dwo.example"])

    def test_the_to_of_an_email_sent_to_the_catchall_is_kept(self):
        """The core drops the aliases from incoming_email_to: the raw To is kept next to it."""
        catchall = self.mail_alias_domain.catchall_email
        raw = (
            "From: Hieu <hieu@dwo.example>\r\nTo: " + catchall + "\r\nSubject: Re: Quotation\r\n"
            "Message-Id: <abc@dwo.example>\r\nContent-Type: text/plain\r\n\r\nHello\r\n")
        msg_dict = self.env["mail.thread"].message_parse(email.message_from_string(raw, policy=email.policy.SMTP))
        self.assertEqual(msg_dict["to_filtered"], "")
        self.assertEqual(msg_dict["dwo_incoming_email_to_all"], catchall)
        message = self.env["mail.message"].create({
            "model": "res.partner", "res_id": self.record.id, "message_type": "email",
            "email_from": "hieu@dwo.example", "dwo_incoming_email_to_all": msg_dict["dwo_incoming_email_to_all"],
            "body": "<p>Hello</p>",
        })
        ref = self.composer._message_addresses(message)
        self.assertEqual([a["email"] for a in ref[1]], [catchall])

    def test_official_email_is_an_outgoing_email_message(self):
        """Not editable (only comments are) and easy to filter: the type is email_outgoing, and the
        badge still comes from the flag."""
        self._send(cc=[], bcc=[])
        message = self.env["mail.message"].search([
            ("model", "=", "res.partner"), ("res_id", "=", self.record.id), ("dwo_is_from_compose", "=", True)])
        self.assertEqual((message.message_type, message.subtype_id), ("email_outgoing", self.env.ref("mail.mt_comment")))

    def test_received_to_keeps_the_order_and_shows_an_address_once(self):
        """The core builds To from a set (order lost), and Delivered-To repeats an address."""
        catchall = self.mail_alias_domain.catchall_email
        raw = (
            "From: Lan <%s>\r\nTo: Zed Last <zed@x.example>, Anna First <anna@x.example>, Mid <mid@x.example>, %s\r\n"
            "Delivered-To: anna@x.example\r\nSubject: Order\r\nMessage-Id: <order@x.example>\r\n"
            "Content-Type: text/plain\r\n\r\nHello\r\n" % (CUSTOMER, catchall))
        msg_dict = self.env["mail.thread"].message_parse(email.message_from_string(raw, policy=email.policy.SMTP))
        parsed = self.composer._parse(msg_dict["dwo_incoming_email_to_all"])
        self.assertEqual(
            [(a["email"], a["name"]) for a in parsed],
            [("zed@x.example", "Zed Last"), ("anna@x.example", "Anna First"),
             ("mid@x.example", "Mid"), (catchall, "")])

    def test_parse_keeps_the_name_when_an_address_is_repeated(self):
        parsed = self.composer._parse("a@x.example, Bob <b@x.example>, Anna <a@x.example>")
        self.assertEqual([(a["email"], a["name"]) for a in parsed], [("a@x.example", "Anna"), ("b@x.example", "Bob")])

    # ------------------------------------------------------------
    # EMPTY LINES TO WRITE IN
    # ------------------------------------------------------------

    def test_a_new_email_starts_with_three_empty_lines_then_the_signature(self):
        self.admin.signature = "<p>Best regards, Hieu</p>"
        body = self.composer.get_defaults("res.partner", self.record.id)["body"]
        self.assertTrue(body.startswith("<p><br></p>" * 3), body)
        self.assertIn("Best regards, Hieu", body[len("<p><br></p>" * 3):])

    def test_the_empty_lines_come_before_the_quote_of_a_reply(self):
        self._incoming()
        body = self.composer.get_defaults("res.partner", self.record.id)["body"]
        self.assertTrue(body.startswith("<p><br></p>" * 3), body)
        self.assertLess(body.index("<p><br></p>"), body.index("divRplyFwdMsg"))

    def test_a_saved_template_does_not_keep_the_empty_lines(self):
        body = "<p><br></p><p><br></p><p><br></p><p>Dear customer</p><p><br></p>"
        self.assertEqual(self.composer._body_without_quote(body), "<p>Dear customer</p><p><br></p>")
