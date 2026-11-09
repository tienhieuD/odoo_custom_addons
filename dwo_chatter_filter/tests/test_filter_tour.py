# -*- coding: utf-8 -*-
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install", "dwo_chatter_filter")
class TestMessageFilterTour(HttpCase):
    # Odoo 16 gives Chrome "1366x768" and a recent Chrome does not understand it: the window stays small
    browser_size = "1366,768"

    def setUp(self):
        # Odoo 14: an HttpCase has no class-level environment, the data is made for each test
        super().setUp()
        self.record = self.env["res.partner"].with_context(mail_create_nolog=True, mail_notrack=True).create(
            {"name": "Filter tour partner"})
        mt_comment, mt_note = self.env.ref("mail.mt_comment"), self.env.ref("mail.mt_note")
        Message = self.env["mail.message"]
        base = {"model": "res.partner", "res_id": self.record.id}
        Message.create(dict(base, body="<p>Talk about the order</p>", message_type="comment", subtype_id=mt_comment.id))
        Message.create(dict(base, body="<p>Private reminder</p>", message_type="comment", subtype_id=mt_note.id))
        Message.create(dict(base, body="<p>Email from the customer</p>", message_type="email", subtype_id=mt_comment.id))
        tracking = Message.create(dict(base, body="", message_type="notification", subtype_id=mt_note.id))
        # a planned activity: the badges come under it
        self.record.activity_schedule("mail.mail_activity_data_todo", summary="Call the customer")
        self.env["mail.tracking.value"].create({
            "field": self.env["ir.model.fields"]._get("res.partner", "name").id, "field_desc": "Name",
            "mail_message_id": tracking.id, "old_value_char": "Old name", "new_value_char": "Name changed"})
        Message.create(dict(base, body="<p>Call done with the customer</p>", message_type="notification",
                            subtype_id=self.env.ref("mail.mt_activities").id))
        Message.create(dict(base, body="<p>Automatic message</p>", message_type="notification", subtype_id=mt_note.id))

    def test_filter_tour(self):
        self.start_tour(f"/web#model=res.partner&view_type=form&id={self.record.id}", "dwo_chatter_filter", login="admin")
