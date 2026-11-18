# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo.exceptions import AccessError, UserError
from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase

RAW = (
    "From: {frm}\n"
    "To: {to}\n"
    "Subject: {subject}\n"
    "Message-Id: <{mid}@mail.example>\n"
    "{extra}"
    "MIME-Version: 1.0\n"
    "Content-Type: {ctype}\n\n"
    "{body}\n"
)


@tagged("post_install", "-at_install", "dwo_mail_orphan_routing")
class TestOrphan(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Orphan = cls.env["dwo.mail.orphan"]
        cls.Thread = cls.env["mail.thread"]
        cls.partner_model = cls.env["ir.model"]._get("res.partner")
        cls.customer = cls.env["res.partner"].create({"name": "Lan Pham", "email": "lan@client.example"})
        cls.target = cls.env["res.partner"].create({"name": "Acme Project", "ref": "PRJ-4242"})
        cls.target2 = cls.env["res.partner"].create({"name": "Other Project", "ref": "PRJ-9999"})
        cls.env["ir.config_parameter"].sudo().set_param("dwo_orphan.target_models", "res.partner")
        cls.env["ir.config_parameter"].sudo().set_param("dwo_orphan.enabled", "1")
        cls.n = 0

    def _mail(self, subject="Hello", frm="Lan Pham <lan@client.example>", to="nobody@unknown.example",
              extra="", body="Please help.", ctype="text/plain; charset=utf-8"):
        self.n += 1
        raw = RAW.format(frm=frm, to=to, subject=subject, mid="m%s-%s" % (self.id(), self.n), extra=extra,
                         ctype=ctype, body=body)
        self.Thread.message_process(False, raw)
        return self.Orphan.search([("message_id", "=", "<m%s-%s@mail.example>" % (self.id(), self.n))])

    # --- capture ---------------------------------------------------------

    def test_unroutable_mail_becomes_orphan(self):
        orphan = self._mail(subject="Where is my order?")
        self.assertEqual(len(orphan), 1)
        self.assertEqual(orphan.state, "new")
        self.assertEqual(orphan.subject, "Where is my order?")
        self.assertEqual(orphan.author_id, self.customer)
        self.assertEqual(orphan.rcpt_address, "nobody@unknown.example")
        self.assertIn("No alias or record", orphan.reason)
        self.assertFalse(self.env["mail.message"].search([("message_id", "=", orphan.message_id)]))

    def test_disabled_keeps_standard_behaviour(self):
        self.env["ir.config_parameter"].sudo().set_param("dwo_orphan.enabled", "0")
        with self.assertRaises(ValueError):
            self._mail()
        self.assertFalse(self.Orphan.search([("subject", "=", "Hello")]))

    def test_duplicate_message_id_stored_once(self):
        orphan = self._mail()
        raw = RAW.format(frm="Lan Pham <lan@client.example>", to="nobody@unknown.example", subject="Hello",
                         mid="m%s-%s" % (self.id(), self.n), extra="", ctype="text/plain", body="again")
        self.Thread.message_process(False, raw)
        self.assertEqual(self.Orphan.search_count([("message_id", "=", orphan.message_id)]), 1)

    def test_catchall_bounce_is_captured(self):
        domain = self.env["mail.alias.domain"].search([], limit=1)
        if not domain:
            self.skipTest("no alias domain")
        orphan = self._mail(to=domain.catchall_email)
        self.assertEqual(len(orphan), 1)

    def test_alias_contact_restriction_is_captured_with_alias(self):
        domain = self.env["mail.alias.domain"].search([], limit=1)
        if not domain:
            self.skipTest("no alias domain")
        alias = self.env["mail.alias"].create({
            "alias_name": "orphan-test", "alias_model_id": self.partner_model.id, "alias_contact": "followers",
            "alias_domain_id": domain.id, "alias_force_thread_id": self.target.id})
        orphan = self._mail(to=alias.alias_full_name, frm="Stranger <who@other.example>")
        self.assertEqual(orphan.alias_id, alias)
        self.assertEqual(orphan.rcpt_address, alias.alias_full_name)

    def test_html_is_sanitized_and_attachment_kept(self):
        raw = (
            "From: Lan Pham <lan@client.example>\nTo: nobody@unknown.example\nSubject: Files\n"
            "Message-Id: <att-%s@mail.example>\nMIME-Version: 1.0\n"
            "Content-Type: multipart/mixed; boundary=XX\n\n--XX\nContent-Type: text/html; charset=utf-8\n\n"
            "<p>Hi</p><script>alert(1)</script><img src=x onerror=alert(2)>\n--XX\n"
            "Content-Type: text/plain; name=\"note.txt\"\nContent-Disposition: attachment; filename=\"note.txt\"\n\n"
            "hello file\n--XX--\n" % self.id())
        self.Thread.message_process(False, raw)
        orphan = self.Orphan.search([("message_id", "=", "<att-%s@mail.example>" % self.id())])
        self.assertTrue(orphan)
        self.assertNotIn("<script", orphan.body_html)
        self.assertNotIn("onerror", orphan.body_html)
        self.assertEqual(orphan.attachment_ids.mapped("name"), ["note.txt"])
        self.assertEqual(orphan.attachment_count, 1)

    # --- suggestions -----------------------------------------------------

    def test_suggestion_from_subject_code(self):
        orphan = self._mail(subject="Re: question about PRJ-4242 delivery")
        top = orphan.suggestion_ids[:1]
        self.assertEqual((top.res_model, top.res_id), ("res.partner", self.target.id))
        self.assertIn("PRJ-4242", top.reason)

    def test_suggestion_from_reply_header(self):
        message = self.target.message_post(body="Our offer", message_type="comment")
        message.message_id = "<offer-1@odoo.example>"
        orphan = self._mail(subject="Thanks", extra="In-Reply-To: <offer-1@odoo.example>\nReferences: <offer-1@odoo.example>\n")
        # the reply would normally be routed by Odoo: orphan built by hand from the same headers
        orphan = orphan or self.Orphan.create({"subject": "Thanks", "in_reply_to": "<offer-1@odoo.example>"})
        orphan._compute_suggestions()
        self.assertEqual(orphan.suggestion_ids[0].res_id, self.target.id)
        self.assertEqual(orphan.suggestion_ids[0].score, 100)

    def test_suggestion_from_sender_history(self):
        self.target2.message_post(body="Hi", message_type="comment", author_id=self.customer.id)
        orphan = self._mail(subject="No code here")
        ids = orphan.suggestion_ids.mapped("res_id")
        self.assertIn(self.target2.id, ids)
        self.assertIn(self.customer.id, ids)
        self.assertLessEqual(len(ids), 3)

    # --- routing ---------------------------------------------------------

    def test_route_single_with_attachment(self):
        raw = (
            "From: Lan Pham <lan@client.example>\nTo: nobody@unknown.example\nSubject: Contract PRJ-4242\n"
            "Message-Id: <route-%s@mail.example>\nMIME-Version: 1.0\n"
            "Content-Type: multipart/mixed; boundary=XX\n\n--XX\nContent-Type: text/plain; charset=utf-8\n\n"
            "See file\n--XX\nContent-Type: text/plain; name=\"note.txt\"\n"
            "Content-Disposition: attachment; filename=\"note.txt\"\n\nhello file\n--XX--\n" % self.id())
        self.Thread.message_process(False, raw)
        orphan = self.Orphan.search([("message_id", "=", "<route-%s@mail.example>" % self.id())])
        orphan.suggestion_ids[0].action_route()
        self.assertEqual(orphan.state, "routed")
        msg = orphan.routed_message_id
        self.assertEqual((msg.model, msg.res_id), ("res.partner", self.target.id))
        self.assertEqual(msg.message_id, orphan.message_id)
        self.assertEqual(msg.author_id, self.customer)
        self.assertEqual(msg.attachment_ids.mapped("name"), ["note.txt"])
        self.assertFalse(orphan.suggestion_ids)
        self.assertIn("Acme Project", orphan.target_display)

    def test_route_follow_sender(self):
        orphan = self._mail()
        orphan._route_to("res.partner", self.target.id, follow=True)
        self.assertIn(self.customer, self.target.message_partner_ids)

    def test_bulk_route_and_reroute(self):
        a, b, c = self._mail(subject="One"), self._mail(subject="Two"), self._mail(subject="Three")
        wiz = Form(self.env["dwo.mail.orphan.route.wizard"].with_context(default_orphan_ids=(a | b | c).ids))
        wiz.model_id = self.partner_model
        wiz.res_id = self.target.id
        wiz = wiz.save()
        self.assertEqual(wiz.total_count, 3)
        wiz.action_route()
        self.assertEqual((a | b | c).mapped("state"), ["routed"] * 3)
        self.assertEqual(len((a | b | c).mapped("routed_message_id")), 3)
        # reroute one to another record: the same message moves
        msg = a.routed_message_id
        a._route_to("res.partner", self.target2.id)
        self.assertEqual(a.routed_message_id, msg)
        self.assertEqual(msg.res_id, self.target2.id)

    def test_wizard_includes_same_sender(self):
        a, b = self._mail(subject="One"), self._mail(subject="Two")
        other = self._mail(subject="Else", frm="Bob <bob@other.example>")
        wiz = self.env["dwo.mail.orphan.route.wizard"].with_context(default_orphan_ids=a.ids).create({
            "model_id": self.partner_model.id, "res_id": self.target.id, "include_same_sender": True})
        self.assertEqual(wiz.total_count, 2)
        wiz.action_route()
        self.assertEqual((a | b).mapped("state"), ["routed", "routed"])
        self.assertEqual(other.state, "new")

    def test_target_model_not_allowed(self):
        orphan = self._mail()
        with self.assertRaises(UserError):
            orphan._route_to("res.users", self.env.uid)

    def test_ignore_and_restore(self):
        orphan = self._mail()
        orphan.action_ignore()
        self.assertEqual(orphan.state, "ignored")
        orphan.action_restore()
        self.assertEqual(orphan.state, "new")
        orphan._route_to("res.partner", self.target.id)
        with self.assertRaises(UserError):
            orphan.action_ignore()
        with self.assertRaises(UserError):
            orphan.action_restore()

    # --- rules -----------------------------------------------------------

    def test_rule_routes_on_arrival(self):
        rule = self.env["dwo.mail.orphan.rule"].create({
            "name": "Client Lan", "sender_contains": "client.example", "subject_contains": "invoice",
            "action": "route", "model_id": self.partner_model.id, "res_id": self.target.id})
        orphan = self._mail(subject="Your Invoice")
        self.assertEqual(orphan.state, "routed")
        self.assertEqual(orphan.rule_id, rule)
        self.assertEqual(rule.hit_count, 1)
        self.assertEqual(orphan.routed_message_id.res_id, self.target.id)
        # not matching: stays new
        self.assertEqual(self._mail(subject="Hello").state, "new")

    def test_rule_ignores_spam(self):
        self.env["dwo.mail.orphan.rule"].create({"name": "Spam", "sender_contains": "@spam.example", "action": "ignore"})
        orphan = self._mail(frm="Promo <ads@spam.example>")
        self.assertEqual(orphan.state, "ignored")

    def test_rule_needs_condition(self):
        with self.assertRaises(Exception):
            self.env["dwo.mail.orphan.rule"].create({"name": "Empty", "action": "ignore"})

    # --- security --------------------------------------------------------

    def _user(self, login, manager=True):
        groups = [self.env.ref("base.group_user").id]
        if manager:
            groups.append(self.env.ref("dwo_mail_orphan_routing.group_dwo_orphan_manager").id)
        return self.env["res.users"].with_context(no_reset_password=True).create({
            "name": login, "login": login, "email": login + "@dwo.example", "group_ids": [(6, 0, groups)]})

    def test_group_required(self):
        orphan = self._mail()
        plain = self._user("plain", manager=False)
        with self.assertRaises(AccessError):
            orphan.with_user(plain).read(["subject"])

    def test_alias_restriction(self):
        domain = self.env["mail.alias.domain"].search([], limit=1)
        if not domain:
            self.skipTest("no alias domain")
        make = lambda n: self.env["mail.alias"].create({
            "alias_name": n, "alias_model_id": self.partner_model.id, "alias_contact": "followers",
            "alias_domain_id": domain.id, "alias_force_thread_id": self.target.id})
        a1, a2 = make("sales-orphan"), make("support-orphan")
        o1 = self._mail(to=a1.alias_full_name, frm="X <x@one.example>")
        o2 = self._mail(to=a2.alias_full_name, frm="Y <y@two.example>")
        o3 = self._mail()
        user = self._user("restricted")
        self.assertEqual(self.Orphan.with_user(user).search([("id", "in", (o1 | o2 | o3).ids)]), o1 | o2 | o3)
        user.write({"dwo_orphan_all_aliases": False, "dwo_orphan_alias_ids": [(6, 0, a1.ids)]})
        self.assertEqual(self.Orphan.with_user(user).search([("id", "in", (o1 | o2 | o3).ids)]), o1)
        self.assertEqual(o1.with_user(user).suggestion_ids.orphan_id, o1)

    def test_route_needs_write_on_target(self):
        orphan = self._mail()
        user = self._user("limited")
        user.write({"group_ids": [(4, self.env.ref("base.group_partner_manager").id)]})
        rule = self.env["ir.rule"].create({
            "name": "no write on target", "model_id": self.env["ir.model"]._get("res.partner").id,
            "domain_force": "[('id', '!=', %s)]" % self.target.id, "perm_read": False, "perm_write": True,
            "perm_create": False, "perm_unlink": False, "global": True})
        self.assertTrue(rule)
        with self.assertRaises(AccessError):
            orphan.with_user(user)._route_to("res.partner", self.target.id)
        orphan.with_user(user)._route_to("res.partner", self.target2.id)
        self.assertEqual(orphan.state, "routed")

    # --- notifications, report, settings ----------------------------------

    def test_daily_digest_and_purge(self):
        self.env["res.users"].browse(self.env.uid).sudo().email = "admin@dwo.example"
        mails_before = self.env["mail.mail"].search_count([])
        self._mail(subject="Digest me")
        self.env["ir.config_parameter"].sudo().set_param("dwo_orphan.digest", "1")
        self.env["ir.config_parameter"].sudo().set_param("dwo_orphan.last_digest", "2000-01-01 00:00:00")
        self.Orphan._cron_digest()
        self.assertGreater(self.env["mail.mail"].search_count([]), mails_before)
        # purge: handled emails older than N days
        old = self._mail(subject="Old one")
        old.action_ignore()
        old.sudo().write({"date": "2020-01-01 00:00:00"})
        new_old = self._mail(subject="Old but new state")
        new_old.sudo().write({"date": "2020-01-01 00:00:00"})
        self.env["ir.config_parameter"].sudo().set_param("dwo_orphan.keep_days", "30")
        self.Orphan._cron_purge()
        self.assertFalse(old.exists())
        self.assertTrue(new_old.exists())

    def test_report_grouping(self):
        self._mail()
        self._mail(subject="Again")
        data = self.Orphan._read_group([], ["rcpt_address", "date:week"], ["__count"])
        self.assertEqual(sum(row[-1] for row in data), 2)

    def test_settings_models(self):
        settings = self.env["res.config.settings"].create({})
        settings.dwo_orphan_model_ids = self.partner_model
        settings.set_values()
        self.assertEqual(self.Orphan._target_models(), ["res.partner"])
        self.assertEqual(self.env["res.config.settings"].get_values()["dwo_orphan_model_ids"][0][2], self.partner_model.ids)

    def test_form_views_load(self):
        orphan = self._mail(subject="PRJ-4242")
        with Form(orphan) as form:
            self.assertEqual(form.subject, "PRJ-4242")
        self.assertTrue(orphan.action_route_wizard())
        self.assertTrue(orphan.suggestion_ids[0].action_open_record())
