# -*- coding: utf-8 -*-
"""A chatter with every kind of message. Run it again with: uninstall, install."""
from datetime import timedelta

from markupsafe import Markup

from odoo import fields

TAG = "dwo_chatter_filter_demo"
LOGINS = ("linh.tran.cf", "minh.vu.cf")


def post_init_hook(env):
    admin = env.ref("base.user_admin")
    if not admin.email:
        admin.partner_id.write({"name": "Hieu Nguyen", "email": "hieu.nguyen@duotek.example"})
    env = env(user=admin, context=dict(
        env.context, mail_notify_force_send=False, mail_create_nolog=True, mail_notrack=True))
    Partner, Message = env["res.partner"], env["mail.message"].sudo()
    now = fields.Datetime.now()
    tag = env["res.partner.category"].create({"name": TAG})

    group_ids = [(6, 0, [env.ref("base.group_user").id, env.ref("base.group_partner_manager").id])]
    linh, minh = env["res.users"].with_context(no_reset_password=True).create([
        {"name": "Linh Tran", "login": LOGINS[0], "password": "demo", "email": "linh.tran@duotek.example", "group_ids": group_ids},
        {"name": "Minh Vu", "login": LOGINS[1], "password": "demo", "email": "minh.vu@duotek.example", "group_ids": group_ids},
    ])

    aurora = Partner.create({"name": "Aurora Logistics", "email": "contact@aurora-logistics.example",
                             "is_company": True, "city": "Da Nang", "category_id": [(4, tag.id)]})
    lan = Partner.create({"name": "Lan Pham", "email": "lan.pham@aurora-logistics.example",
                          "parent_id": aurora.id, "type": "contact"})
    aurora.message_subscribe(partner_ids=(linh | minh).partner_id.ids)

    def when(message, days_ago, hours=0):
        message.sudo().write({"date": now - timedelta(days=days_ago, hours=hours)})
        return message

    def discussion(days_ago, body, author=admin, partners=()):
        message = aurora.with_user(author).message_post(
            body=Markup(body), message_type="comment", subtype_xmlid="mail.mt_comment",
            partner_ids=[p.id for p in partners], notify_skip_followers=not partners)
        return when(message, days_ago)

    def note(days_ago, body, author=admin):
        return when(aurora.with_user(author).message_post(
            body=Markup(body), message_type="comment", subtype_xmlid="mail.mt_note"), days_ago)

    def email_in(days_ago, subject, body, author):
        return when(Message.create({
            "model": "res.partner", "res_id": aurora.id, "message_type": "email", "subject": subject,
            "body": body, "author_id": author.id, "email_from": f"{author.name} <{author.email}>",
            "subtype_id": env.ref("mail.mt_comment").id}), days_ago)

    def email_out(days_ago, subject, body):
        return when(aurora.message_post(
            body=Markup(body), subject=subject, message_type="email_outgoing", subtype_xmlid="mail.mt_comment",
            partner_ids=lan.ids, notify_skip_followers=True), days_ago)

    def tracking(days_ago, field, old, new):
        message = Message.create({
            "model": "res.partner", "res_id": aurora.id, "message_type": "notification", "body": "",
            "subtype_id": env.ref("mail.mt_note").id, "author_id": admin.partner_id.id})
        env["mail.tracking.value"].sudo().create({
            "field_id": env["ir.model.fields"]._get("res.partner", field).id, "mail_message_id": message.id,
            "old_value_char": old, "new_value_char": new})
        return when(message, days_ago)

    def automatic(days_ago, body):
        return when(Message.create({
            "model": "res.partner", "res_id": aurora.id, "message_type": "auto_comment", "body": body,
            "subtype_id": env.ref("mail.mt_note").id, "author_id": env.ref("base.partner_root").id}), days_ago)

    def done_activity(days_ago, xmlid, summary, feedback):
        """A planned activity marked as done: Odoo leaves a message with the subtype Activities."""
        activity = aurora.activity_schedule(
            xmlid, summary=summary, user_id=admin.id, date_deadline=(now - timedelta(days=days_ago)).date())
        activity.action_feedback(feedback=feedback)
        message = Message.search([("model", "=", "res.partner"), ("res_id", "=", aurora.id),
                                  ("subtype_id", "=", env.ref("mail.mt_activities").id)], order="id desc", limit=1)
        return when(message, days_ago)

    # oldest first
    note(9, "<p>Key account: ships every Tuesday. Ask for the packing plan before booking.</p>", linh)
    discussion(8, "<p>Kick-off with the team: Aurora wants 200 pallets a month from February.</p>", linh)
    email_in(8, "Pallets for February", "<p>Hello, we would like a quotation for 200 pallets a month from February.</p>", lan)
    discussion(7, "<p>Quotation sent to Lan. Waiting for her answer.</p>", admin, partners=lan)
    tracking(7, "phone", "", "+84 236 555 0142")
    email_out(6, "RE: Pallets for February", "<p>Hello Lan, our quotation is attached: 200 pallets a month, delivery every Tuesday.</p>")
    automatic(6, "<p>Quotation reminder: the customer has not answered for 3 days.</p>")
    discussion(5, "<p>Lan agrees on the price. She asks for a 30 day payment term.</p>", minh)
    email_in(5, "RE: Pallets for February", "<p>Thank you, the price is fine. Can we have 30 days to pay?</p>", lan)
    note(4, "<p>30 days is above our limit for new customers. Ask Linh before answering.</p>", minh)
    tracking(4, "website", "", "https://aurora-logistics.example")
    discussion(3, "<p>@Linh can you approve 30 days for Aurora? The first order is small.</p>", minh)
    discussion(3, "<p>Approved for the first 3 months, then back to 15 days.</p>", linh)
    email_out(2, "Payment terms", "<p>Hello Lan, we accept 30 days for the first 3 months. Best regards.</p>")
    tracking(2, "city", "Hanoi", "Da Nang")
    discussion(1, "<p>Order confirmed by phone. Lan will send the purchase order tomorrow.</p>", admin, partners=lan)
    note(1, "<p>Remember to add the customer to the Tuesday delivery route.</p>", admin)
    done_activity(5, "mail.mail_activity_data_call", "Call Lan about the quotation", "She will answer tomorrow.")
    done_activity(0, "mail.mail_activity_data_call", "Call the customer to confirm the first delivery",
                  "Confirmed for next Tuesday.")
    automatic(0, "<p>Reminder: the purchase order of Aurora Logistics is expected tomorrow.</p>")

    # a planned activity: the badges come under it
    aurora.activity_schedule(
        "mail.mail_activity_data_call", summary="Call the customer about the delivery date",
        user_id=admin.id, date_deadline=fields.Date.today() + timedelta(days=1))

    env["mail.mail"].sudo().search([("state", "=", "outgoing")]).write({"state": "cancel"})


def uninstall_hook(env):
    tag = env["res.partner.category"].search([("name", "=", TAG)])
    partners = env["res.partner"].search([("id", "child_of", env["res.partner"].search([("category_id", "in", tag.ids)]).ids)])
    env["mail.mail"].sudo().search([("model", "=", "res.partner"), ("res_id", "in", partners.ids)]).unlink()
    env["mail.message"].sudo().search([("model", "=", "res.partner"), ("res_id", "in", partners.ids)]).unlink()
    partners.unlink()
    env["res.users"].with_context(active_test=False).search([("login", "in", LOGINS)]).unlink()
    tag.unlink()
