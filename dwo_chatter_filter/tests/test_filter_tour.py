# -*- coding: utf-8 -*-
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install", "dwo_chatter_filter")
class TestMessageFilterTour(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.record = cls.env["res.partner"].with_context(mail_create_nolog=True, mail_notrack=True).create(
            {"name": "Filter tour partner"})
        mt_comment, mt_note = cls.env.ref("mail.mt_comment"), cls.env.ref("mail.mt_note")
        Message = cls.env["mail.message"]
        base = {"model": "res.partner", "res_id": cls.record.id}
        Message.create(dict(base, body="<p>Talk about the order</p>", message_type="comment", subtype_id=mt_comment.id))
        Message.create(dict(base, body="<p>Private reminder</p>", message_type="comment", subtype_id=mt_note.id))
        Message.create(dict(base, body="<p>Email from the customer</p>", message_type="email", subtype_id=mt_comment.id))
        tracking = Message.create(dict(base, body="", message_type="notification", subtype_id=mt_note.id))
        # a planned activity: the badges come under it
        cls.record.activity_schedule("mail.mail_activity_data_todo", summary="Call the customer")
        cls.env["mail.tracking.value"].create({
            "field_id": cls.env["ir.model.fields"]._get("res.partner", "name").id,
            "mail_message_id": tracking.id, "old_value_char": "Old name", "new_value_char": "Name changed"})
        Message.create(dict(base, body="<p>Call done with the customer</p>", message_type="notification",
                            subtype_id=cls.env.ref("mail.mt_activities").id))
        Message.create(dict(base, body="<p>Automatic message</p>", message_type="auto_comment", subtype_id=mt_note.id))

    def test_filter_tour(self):
        self.start_tour(f"/odoo/action-base.action_partner_form/{self.record.id}", "dwo_chatter_filter", login="admin")

    def test_filter_search_tour(self):
        self.start_tour(f"/odoo/action-base.action_partner_form/{self.record.id}", "dwo_chatter_filter_search", login="admin")

    def test_filter_edit_tour(self):
        self.start_tour(f"/odoo/action-base.action_partner_form/{self.record.id}", "dwo_chatter_filter_edit", login="admin")

    def test_filter_no_edit_for_an_employee_tour(self):
        self.env["res.users"].with_context(no_reset_password=True).create({
            "name": "Chip employee", "login": "chip_employee", "password": "chip_employee",
            "group_ids": [(6, 0, [self.env.ref("base.group_user").id])]})
        self.start_tour(f"/odoo/action-base.action_partner_form/{self.record.id}", "dwo_chatter_filter_no_edit",
                        login="chip_employee")
