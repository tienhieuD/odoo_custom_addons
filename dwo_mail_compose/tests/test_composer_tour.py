# -*- coding: utf-8 -*-
from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install", "dwo_mail_compose")
class TestComposerTour(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        admin = cls.env.ref("base.user_admin")
        admin.write({"email": "admin@dwo.example", "tz": "Asia/Tokyo"})
        cls.env["mail.mail"].sudo().search([]).unlink()
        cls.record = cls.env["res.partner"].create({"name": "DWO Mail Tour Partner"})

    def _start(self, tour):
        self.start_tour(f"/odoo/action-base.action_partner_form/{self.record.id}", tour, login="admin")

    def test_send_email_tour(self):
        self._start("dwo_mail_compose_send")
        message = self.env["mail.message"].search(
            [("model", "=", "res.partner"), ("res_id", "=", self.record.id), ("dwo_is_official_email", "=", True)])
        self.assertEqual(len(message), 1)
        self.assertEqual(message.sudo().outgoing_email_bcc, "hidden.boss@acme.example")
        self.assertIn("new.person@acme.example", message.outgoing_email_to)
        self.assertIn("second.person@acme.example", message.sudo().outgoing_email_cc)
        self.assertIn("new.person@acme.example", message.sudo().outgoing_email_cc, "no limit between To and Cc")

    def test_image_is_uploaded_not_embedded_tour(self):
        """A pasted image is saved as an attachment of the record and linked, never kept as base64."""
        self._start("dwo_mail_compose_image")
        message = self.env["mail.message"].search(
            [("model", "=", "res.partner"), ("res_id", "=", self.record.id), ("dwo_is_official_email", "=", True)])
        self.assertEqual(len(message), 1)
        self.assertNotIn("data:image", message.body)
        self.assertIn("/web/image/", message.body)
        self.assertIn("access_token=", message.body)
        image = self.env["ir.attachment"].search(
            [("res_model", "=", "res.partner"), ("res_id", "=", self.record.id), ("mimetype", "like", "image/")])
        self.assertTrue(image, "the image became an attachment of the record")

    def _tour_template(self):
        self.record.email = "tpl.customer@acme.example"
        return self.env["mail.template"].create({
            "name": "Tour template", "model_id": self.env["ir.model"]._get("res.partner").id,
            "subject": "Quote for {{ object.name }}", "use_default_to": False,
            "body_html": '<p>Dear <t t-out="object.name"/>, here is your quote.</p>',
            "email_to": "{{ object.email }}", "email_cc": "cc.tpl@acme.example",
            "email_bcc": "bcc.tpl@acme.example",
            "attachment_ids": [(0, 0, {
                "name": "terms.txt", "raw": b"terms", "res_model": "mail.template", "res_id": 0})],
        })

    def test_template_tour(self):
        self._tour_template()
        self._start("dwo_mail_compose_template")

    def test_template_asks_before_overwriting_tour(self):
        self._tour_template()
        self._start("dwo_mail_compose_template_dirty")

    def test_interface_tour(self):
        self._start("dwo_mail_compose_ui")

    def test_save_as_template_tour(self):
        self._start("dwo_mail_compose_save_template")
        template = self.env["mail.template"].search([("name", "=", "Saved from the composer")])
        self.assertEqual(len(template), 1)
        self.assertEqual(template.model, "res.partner")
        self.assertEqual(template.subject, "My reusable subject")
        self.assertIn("My reusable text", template.body_html)

    def test_cc_shown_when_it_has_values_tour(self):
        self.env["mail.message"].create({
            "model": "res.partner", "res_id": self.record.id, "message_type": "email",
            "subject": "Incoming", "email_from": "Customer <customer@acme.example>",
            "incoming_email_to": "admin@dwo.example", "incoming_email_cc": "cc.person@acme.example",
            "date": "2026-11-06 09:12:00", "body": "<p>Hello</p>",
        })
        self._start("dwo_mail_compose_shown_values")

    def test_layout_tour(self):
        self.record.message_post(body="History message", message_type="comment", subtype_xmlid="mail.mt_note")
        self._start("dwo_mail_compose_layout")

    def test_rapid_clicks_on_the_list_create_nothing_tour(self):
        admin = self.env.ref("base.user_admin")
        composer = self.env["dwo.mail.composer"].with_user(admin)
        for name in ("Mail A", "Mail B", "Mail C"):
            composer.save_email("res.partner", self.record.id, False, {
                "from": "admin@dwo.example", "to": ["a@acme.example"], "subject": name, "body": f"<p>{name} body</p>"})
        self._start("dwo_mail_compose_rapid_clicks")
        self.assertEqual(self.env["dwo.mail.email"].search_count([("res_id", "=", self.record.id)]), 3)

    def test_delete_then_idle_creates_nothing_tour(self):
        admin = self.env.ref("base.user_admin")
        composer = self.env["dwo.mail.composer"].with_user(admin)
        for name in ("Mail A", "Mail B"):
            composer.save_email("res.partner", self.record.id, False, {
                "from": "admin@dwo.example", "to": ["a@acme.example"], "subject": name, "body": f"<p>{name} body</p>"})
        self._start("dwo_mail_compose_delete_then_idle")
        self.assertEqual(self.env["dwo.mail.email"].search_count([("res_id", "=", self.record.id)]), 1)

    def test_close_always_keeps_what_was_typed_tour(self):
        self._start("dwo_mail_compose_close_saves")
        emails = self.env["dwo.mail.email"].search([("res_id", "=", self.record.id)], order="id")
        self.assertEqual(len(emails), 3)
        self.assertIn("Only the body", emails[0].body)
        self.assertEqual([a["email"] for a in emails[1].to_json], ["pending.person@acme.example"])
        self.assertIn("Third body", emails[2].body)

    def test_approver_chosen_with_search_more_keeps_its_name_tour(self):
        for i in range(1, 11):
            mail_new_test_user(
                self.env, login=f"searchable_{i}", groups="base.group_user", name=f"Searchable User {i}",
                email=f"searchable.{i}@dwo.example")
        self._start("dwo_mail_compose_approver_search_more")
        email = self.env["dwo.mail.email"].search([("res_id", "=", self.record.id)])
        self.assertEqual(email.approver_ids.mapped("name"), ["Searchable User 3"])

    def test_draft_tour(self):
        self._start("dwo_mail_compose_draft")
        self.assertFalse(self.env["dwo.mail.email"].search([("res_id", "=", self.record.id)]))

    def test_reply_tour(self):
        self.env["mail.message"].create({
            "model": "res.partner", "res_id": self.record.id, "message_type": "email",
            "subject": "Incoming question", "email_from": "Customer <customer@acme.example>",
            "incoming_email_to": "admin@dwo.example", "date": "2026-11-06 09:12:00",
            "body": "<p>Can you send the quote?</p>",
        })
        self._start("dwo_mail_compose_reply")
        # a reply is a new email: it was stored when the form opened, not at the first edit
        stored = self.env["dwo.mail.email"].search([("res_id", "=", self.record.id)])
        self.assertEqual((len(stored), stored.state, stored.subject, stored.mode), (1, "draft", "RE: Incoming question", "reply"))

    # ------------------------------------------------------------
    # approval
    # ------------------------------------------------------------

    def test_request_approval_tour(self):
        self._start("dwo_mail_compose_request_approval")
        email = self.env["dwo.mail.email"].search([("res_id", "=", self.record.id)])
        self.assertEqual(len(email), 1)
        admin = self.env.ref("base.user_admin")
        self.assertEqual(email.approver_ids, admin)
        self.assertEqual(email.request_comment, "Could you look at it?")
        self.assertIn("Please check this text", email.body)
        # the tour then approved it while the form was open: it left, and the late edit was not written
        self.assertEqual(email.state, "sent")
        self.assertEqual(email.subject, "Needs approval edited", "edits stop once it is sent; before that it stays editable")
        self.assertEqual(len(self.env["mail.message"].search(
            [("model", "=", "res.partner"), ("res_id", "=", self.record.id), ("dwo_is_official_email", "=", True)])), 1)

    def test_approval_required_tour(self):
        self.env.ref("base.user_admin").company_id.dwo_mail_require_approval = True
        self._start("dwo_mail_compose_approval_required")

    def test_email_list_tour(self):
        admin = self.env.ref("base.user_admin")
        composer = self.env["dwo.mail.composer"].with_user(admin)
        base = {"from": "admin@dwo.example", "to": ["a@acme.example"], "body": "<p>x</p>"}
        rejected = composer.save_email("res.partner", self.record.id, False, dict(base, subject="Rejected one"))
        composer.request_approval("res.partner", self.record.id, rejected["id"], dict(base, subject="Rejected one"),
                                  admin.ids, None)
        self.env["dwo.mail.email"].browse(rejected["id"]).with_user(admin).action_reject("Not like this")
        composer.save_email("res.partner", self.record.id, False, dict(base, subject="Second draft"))
        self._start("dwo_mail_compose_email_list")

    def test_approver_approves_tour(self):
        approver = mail_new_test_user(
            self.env, login="tour_approver", groups="base.group_user", name="Tour Approver",
            email="tour.approver@dwo.example", password="tour_approver")
        admin = self.env.ref("base.user_admin")
        result = self.env["dwo.mail.composer"].with_user(admin).request_approval(
            "res.partner", self.record.id, False,
            {"from": "admin@dwo.example", "to": ["customer@acme.example"], "subject": "Tour approval",
             "body": "<p>Please check this text</p>"},
            approver.ids, "check it")
        self.start_tour(
            f"/odoo/action-dwo_mail_compose.dwo_mail_email_action/{result['id']}",
            "dwo_mail_compose_approver_approves", login="tour_approver")
        email = self.env["dwo.mail.email"].browse(result["id"])
        self.assertEqual(email.state, "sent")
        self.assertEqual(email.decision_comment, "Looks good")
        message = self.env["mail.message"].search(
            [("model", "=", "res.partner"), ("res_id", "=", self.record.id), ("dwo_is_official_email", "=", True)])
        self.assertEqual(len(message), 1)
        self.assertEqual(message.author_id, admin.partner_id)
