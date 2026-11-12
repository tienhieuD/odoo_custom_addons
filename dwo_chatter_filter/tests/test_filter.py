# -*- coding: utf-8 -*-
from odoo.tests.common import SavepointCase
from odoo.exceptions import AccessError, UserError
from odoo.osv import expression
from odoo.tests import tagged

from odoo.addons.dwo_chatter_filter.models.mail_message import CATEGORIES


@tagged("post_install", "-at_install", "dwo_chatter_filter")
class TestMessageFilter(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Odoo 12 has no mail.tests.common (test_mail has it): the employee is made here
        cls.user_employee = cls.env["res.users"].with_context(no_reset_password=True).create({
            "name": "Employee Filter", "login": "employee_filter", "email": "employee.filter@example.com",
            "groups_id": [(6, 0, [cls.env.ref("base.group_user").id])]})
        # no "created" message: the messages of the record are the ones made here
        quiet = cls.env["res.partner"].with_context(mail_create_nolog=True, mail_notrack=True)
        cls.record = quiet.create({"name": "Thread record", "email": "thread@example.com"})
        cls.other = quiet.create({"name": "Another record"})
        cls.mt_comment = cls.env.ref("mail.mt_comment")
        cls.mt_note = cls.env.ref("mail.mt_note")
        Message = cls.env["mail.message"]
        base = {"model": "res.partner", "res_id": cls.record.id, "body": "<p>x</p>"}
        # two discussions: one for the followers, one with a customer on the record
        cls.discussion_1 = Message.create(dict(base, message_type="comment", subtype_id=cls.mt_comment.id))
        cls.discussion_2 = Message.create(dict(base, message_type="comment", subtype_id=cls.mt_comment.id))
        cls.note = Message.create(dict(base, message_type="comment", subtype_id=cls.mt_note.id))
        cls.email_in = Message.create(dict(base, message_type="email", subtype_id=cls.mt_comment.id))
        # an email sent by the composer is outgoing AND has the subtype Discussions: it is an email
        cls.email_out = Message.create(dict(base, message_type="email", subtype_id=cls.mt_comment.id))
        cls.tracking = Message.create(dict(base, message_type="notification", subtype_id=cls.mt_note.id))
        cls.env["mail.tracking.value"].create({
            "field": cls.env["ir.model.fields"]._get("res.partner", "name").id, "field_desc": "Name",
            "mail_message_id": cls.tracking.id, "old_value_char": "Old name", "new_value_char": "New name"})
        # the message left by a done activity (its subtype is Activities)
        cls.activity = Message.create(dict(
            base, message_type="notification", subtype_id=cls.env.ref("mail.mt_activities").id))
        cls.auto = Message.create(dict(base, message_type="notification", subtype_id=cls.mt_note.id))
        cls.system = Message.create(dict(base, message_type="notification", subtype_id=cls.mt_note.id))
        # another record: never counted
        Message.create(dict(base, res_id=cls.other.id, message_type="comment", subtype_id=cls.mt_comment.id))

    def _ids(self, category):
        return set(self.env["mail.message"].search(expression.AND([
            [("model", "=", "res.partner"), ("res_id", "=", self.record.id)],
            self.env["mail.message"]._dwo_category_domain(category)])).ids)

    def test_each_kind_has_its_messages(self):
        self.assertEqual(self._ids("discussion"), {self.discussion_1.id, self.discussion_2.id})
        self.assertEqual(self._ids("note"), {self.note.id})
        self.assertEqual(self._ids("email"), {self.email_in.id, self.email_out.id})
        self.assertEqual(self._ids("tracking"), {self.tracking.id})
        self.assertEqual(self._ids("activity"), {self.activity.id})
        self.assertEqual(self._ids("other"), {self.auto.id, self.system.id})

    def test_the_kinds_do_not_overlap_and_cover_everything(self):
        every = {m.id for m in self.env["mail.message"].search(
            [("model", "=", "res.partner"), ("res_id", "=", self.record.id)])}
        seen = set()
        for category in CATEGORIES:
            ids = self._ids(category)
            self.assertFalse(seen & ids, "%s overlaps another kind" % category)
            seen |= ids
        self.assertEqual(seen, every)

    def test_an_email_sent_by_the_composer_is_an_email_not_a_discussion(self):
        self.assertIn(self.email_out.id, self._ids("email"))
        self.assertNotIn(self.email_out.id, self._ids("discussion"))

    def test_a_done_activity_is_an_activity_unless_it_tracks_a_field(self):
        self.assertIn(self.activity.id, self._ids("activity"))
        self.assertNotIn(self.activity.id, self._ids("other"))
        # tracking wins over the subtype, as everywhere else
        self.env["mail.tracking.value"].create({
            "field": self.env["ir.model.fields"]._get("res.partner", "name").id, "field_desc": "Name",
            "mail_message_id": self.activity.id, "old_value_char": "A", "new_value_char": "B"})
        self.assertIn(self.activity.id, self._ids("tracking"))
        self.assertNotIn(self.activity.id, self._ids("activity"))

    def test_a_tracking_message_is_tracking_even_with_the_subtype_note(self):
        self.assertIn(self.tracking.id, self._ids("tracking"))
        self.assertNotIn(self.tracking.id, self._ids("note"))

    def _chip(self, kind):
        return self.env.ref("dwo_chatter_filter.dwo_filter_" + kind)

    def test_counts(self):
        result = self.env["mail.message"].sudo(self.user_employee).dwo_filter_chips("res.partner", self.record.id)
        self.assertEqual(result["all"], 9)
        counts = {chip["name"]: chip["count"] for chip in result["chips"]}
        self.assertEqual(counts, {"Tracking": 1, "Emails": 2, "Activities": 1, "Notes": 1, "Discussions": 2, "Other": 2})
        self.assertEqual(sum(counts.values()), result["all"])
        # in the order of the sequence
        self.assertEqual([c["name"] for c in result["chips"]],
                         ["Discussions", "Emails", "Activities", "Notes", "Tracking", "Other"])

    def test_the_kind_is_a_field_that_can_be_searched_and_read(self):
        Message = self.env["mail.message"]
        base = [("model", "=", "res.partner"), ("res_id", "=", self.record.id)]
        self.assertEqual(set(Message.search(base + [("dwo_kind", "=", "email")]).ids),
                         {self.email_in.id, self.email_out.id})
        self.assertEqual(len(Message.search(base + [("dwo_kind", "in", ["note", "tracking"])])), 2)
        self.assertEqual(len(Message.search(base + [("dwo_kind", "!=", "email")])), 7)
        self.assertEqual((self.note | self.email_in | self.tracking).mapped("dwo_kind"), ["note", "email", "tracking"])

    def test_the_ids_of_one_chip(self):
        # Odoo 13 shows the messages of a record by their ids: the server tells the ids of a chip, newest first
        Message = self.env["mail.message"].sudo(self.user_employee)
        chip = self._chip("email")
        ids = Message.dwo_filter_ids("res.partner", self.record.id, chip.id)
        self.assertEqual(set(ids), {self.email_in.id, self.email_out.id})
        self.assertEqual(ids, sorted(ids, reverse=True), "newest first")
        tracking = Message.dwo_filter_ids("res.partner", self.record.id, self._chip("tracking").id)
        self.assertEqual(tracking, [self.tracking.id])

    def test_an_archived_or_deleted_chip_filters_nothing(self):
        Message = self.env["mail.message"].sudo(self.user_employee)
        chip = self._chip("email")
        chip.active = False
        self.assertFalse(Message.dwo_filter_ids("res.partner", self.record.id, chip.id))
        gone = chip.id
        chip.unlink()
        self.assertFalse(Message.dwo_filter_ids("res.partner", self.record.id, gone))

    def test_unknown_kind_is_refused(self):
        with self.assertRaises(UserError):
            self.env["mail.message"]._dwo_category_domain("nonsense")

    def test_portal_cannot_ask_for_chips(self):
        portal = self.env["res.users"].with_context(no_reset_password=True).create({
            "name": "Portal", "login": "portal_filter", "email": "portal.filter@example.com",
            "groups_id": [(6, 0, [self.env.ref("base.group_portal").id])]})
        with self.assertRaises(AccessError):
            self.env["mail.message"].sudo(portal).dwo_filter_chips("res.partner", self.record.id)
