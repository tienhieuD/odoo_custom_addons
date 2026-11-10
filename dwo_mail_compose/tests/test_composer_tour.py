# -*- coding: utf-8 -*-
import base64

from .common import mail_new_test_user
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install", "dwo_mail_compose")
class TestComposerTour(HttpCase):

    def setUp(self):
        # Odoo 13: an HttpCase has no class-level environment, the data is made for each test
        super().setUp()
        cls = self
        admin = cls.env.ref("base.user_admin")
        admin.write({"name": "Administrator", "email": "admin@dwo.example", "tz": "Asia/Tokyo"})
        cls.env["mail.mail"].sudo().search([]).unlink()
        cls.record = cls.env["res.partner"].create({"name": "DWO Mail Tour Partner"})

    def start_tour(self, url_path, tour_name, **kwargs):
        # Odoo 12 has no start_tour: the tour is started by hand and waited for
        tour = "odoo.__DEBUG__.services['web_tour.tour']"
        self.browser_js(
            url_path, "%s.run('%s')" % (tour, tour_name), "%s.tours.%s.ready" % (tour, tour_name), **kwargs)

    def _warm_up(self):
        """The first page of a new database builds the bundles of the assets (a minute): done here, before the
        browser waits for a tour to be ready."""
        if not getattr(TestComposerTour, "_warm", False):
            self.authenticate("admin", "admin")
            self.url_open("/web?debug=assets")
            self.url_open("/web")
            TestComposerTour._warm = True

    def _start(self, tour):
        self._warm_up()
        self.start_tour(f"/web#action=base.action_partner_form&id={self.record.id}&view_type=form", tour, login="admin")

    def test_send_email_tour(self):
        self._start("dwo_mail_compose_send")
        message = self.env["mail.message"].search(
            [("model", "=", "res.partner"), ("res_id", "=", self.record.id), ("dwo_is_from_compose", "=", True)])
        self.assertEqual(len(message), 1)
        self.assertEqual(message.sudo().outgoing_email_bcc, "hidden.boss@acme.example")
        self.assertIn("new.person@acme.example", message.outgoing_email_to)
        self.assertIn("second.person@acme.example", message.sudo().outgoing_email_cc)
        self.assertIn("new.person@acme.example", message.sudo().outgoing_email_cc, "no limit between To and Cc")

    def test_image_is_uploaded_not_embedded_tour(self):
        """A pasted image is saved as an attachment of the record and linked, never kept as base64."""
        self._start("dwo_mail_compose_image")
        message = self.env["mail.message"].search(
            [("model", "=", "res.partner"), ("res_id", "=", self.record.id), ("dwo_is_from_compose", "=", True)])
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
            "subject": "Quote for ${object.name}",
            "body_html": '<p>Dear ${object.name}, here is your quote.</p>',
            "email_to": "${object.email}", "email_cc": "cc.tpl@acme.example",
            "email_bcc": "bcc.tpl@acme.example",
            "attachment_ids": [(0, 0, {
                "name": "terms.txt", "datas": base64.b64encode(b"terms"), "res_model": "mail.template", "res_id": 0})],
        })

    def test_template_tour(self):
        self.env.ref("base.user_admin").signature = "<p>Tour signature</p>"
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
        self.record.message_post(body="History message", message_type="comment", subtype="mail.mt_note")
        self._start("dwo_mail_compose_layout")

    def test_rapid_clicks_on_the_list_create_nothing_tour(self):
        admin = self.env.ref("base.user_admin")
        composer = self.env["dwo.mail.composer"].sudo(admin)
        for name in ("Mail A", "Mail B", "Mail C"):
            composer.save_email("res.partner", self.record.id, False, {
                "from": "admin@dwo.example", "to": ["a@acme.example"], "subject": name, "body": f"<p>{name} body</p>"})
        self._start("dwo_mail_compose_rapid_clicks")
        self.assertEqual(self.env["dwo.mail.email"].search_count([("res_id", "=", self.record.id)]), 3)

    def test_delete_then_idle_creates_nothing_tour(self):
        admin = self.env.ref("base.user_admin")
        composer = self.env["dwo.mail.composer"].sudo(admin)
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

    def test_draft_tour(self):
        self._start("dwo_mail_compose_draft")
        self.assertFalse(self.env["dwo.mail.email"].search([("res_id", "=", self.record.id)]))

    def test_reply_tour(self):
        # something to suggest when the field is clicked again with nothing typed
        self.env["dwo.mail.address"].create({"email": "someone.else@acme.example", "name": "Someone Else"})
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

    def test_reply_buttons_tour(self):
        """Reply, Reply all and Forward sit under From/To/Cc. Reply writes to the sender only."""
        self.env["mail.message"].create({
            "model": "res.partner", "res_id": self.record.id, "message_type": "email",
            "subject": "Incoming question", "email_from": "Customer <customer@acme.example>",
            # the core keeps no To for an email sent to an alias: the raw To is what is displayed
            "incoming_email_to": "", "dwo_incoming_email_to_all": "catchall@dwo.example",
            "incoming_email_cc": "colleague@acme.example",
            "date": "2026-11-06 09:12:00", "body": "<p>Can you send the quote?</p>",
        })
        self._start("dwo_mail_compose_reply_buttons")
        stored = self.env["dwo.mail.email"].search([("res_id", "=", self.record.id)])
        self.assertEqual([a["email"] for a in stored.to_json], ["customer@acme.example"])
        self.assertFalse(stored.cc_json)

    # ------------------------------------------------------------
    # approval
    # ------------------------------------------------------------

    def _use_approval(self, exempt=True):
        """The approval flow is on; the administrator (the tour user) can still send now, unless not exempt."""
        company = self.env.ref("base.user_admin").company_id
        company.dwo_mail_require_approval = True
        if not exempt:
            company.dwo_mail_exempt_user_ids = False

    def test_request_approval_tour(self):
        self._use_approval()
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
            [("model", "=", "res.partner"), ("res_id", "=", self.record.id), ("dwo_is_from_compose", "=", True)])), 1)

    def test_approval_required_tour(self):
        self._use_approval(exempt=False)
        self.env.ref("base.user_admin").company_id.dwo_mail_allow_self_approval = False
        self._start("dwo_mail_compose_approval_required")

    def test_direct_only_tour(self):
        self._start("dwo_mail_compose_direct_only")

    def test_email_list_tour(self):
        self._use_approval()
        admin = self.env.ref("base.user_admin")
        composer = self.env["dwo.mail.composer"].sudo(admin)
        base = {"from": "admin@dwo.example", "to": ["a@acme.example"], "body": "<p>x</p>"}
        rejected = composer.save_email("res.partner", self.record.id, False, dict(base, subject="Rejected one"))
        composer.request_approval("res.partner", self.record.id, rejected["id"], dict(base, subject="Rejected one"),
                                  admin.ids, None)
        self.env["dwo.mail.email"].browse(rejected["id"]).sudo(admin).action_reject("Not like this")
        composer.save_email("res.partner", self.record.id, False, dict(base, subject="Second draft"))
        self._start("dwo_mail_compose_email_list")

    def test_approver_approves_tour(self):
        self._use_approval()
        approver = mail_new_test_user(
            self.env, login="tour_approver", groups="base.group_user", name="Tour Approver",
            email="tour.approver@dwo.example", password="tour_approver")
        admin = self.env.ref("base.user_admin")
        result = self.env["dwo.mail.composer"].sudo(admin).request_approval(
            "res.partner", self.record.id, False,
            {"from": "admin@dwo.example", "to": ["customer@acme.example"], "subject": "Tour approval",
             "body": "<p>Please check this text</p>"},
            approver.ids, "check it")
        self.start_tour(
            f"/web#action=dwo_mail_compose.dwo_mail_email_action&id={result['id']}&view_type=form",
            "dwo_mail_compose_approver_approves", login="tour_approver")
        email = self.env["dwo.mail.email"].browse(result["id"])
        self.assertEqual(email.state, "sent")
        self.assertEqual(email.decision_comment, "Looks good")
        message = self.env["mail.message"].search(
            [("model", "=", "res.partner"), ("res_id", "=", self.record.id), ("dwo_is_from_compose", "=", True)])
        self.assertEqual(len(message), 1)
        self.assertEqual(message.author_id, admin.partner_id)
