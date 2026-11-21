# -*- coding: utf-8 -*-
"""Demo scenarios for dwo_mail_compose. Run it again with: uninstall, install."""
import base64
import io
from datetime import timedelta
from unittest.mock import patch

from odoo import fields, tools

TAG = "dwo_mail_compose_demo"
ME_NAME, ME_EMAIL = "Hieu Nguyen", "hieu.nguyen@duotek.example"
BOSS_EMAIL = "linh.tran@duotek.example"


def _png(text, color_a=(135, 90, 123), color_b=(255, 200, 87), size=(520, 200)):
    """A small illustration for the inline image (what a user would paste from the clipboard)."""
    from PIL import Image, ImageDraw
    image = Image.new("RGB", size)
    draw = ImageDraw.Draw(image)
    for x in range(size[0]):
        ratio = x / size[0]
        draw.line([(x, 0), (x, size[1])], fill=tuple(int(a + (b - a) * ratio) for a, b in zip(color_a, color_b)))
    draw.rectangle([20, 20, size[0] - 20, size[1] - 20], outline=(255, 255, 255), width=3)
    draw.text((40, 80), text, fill=(255, 255, 255))
    buffer = io.BytesIO()
    image.save(buffer, "PNG")
    return buffer.getvalue()


def _address(name, email):
    return {"name": name, "email": email}


def post_init_hook(env):
    admin = env.ref("base.user_admin")
    if not admin.email:
        admin.partner_id.write({"name": ME_NAME, "email": ME_EMAIL})
        admin.write({"signature": "<p>Best regards,<br/>%s<br/>DUO-TEK Software Vietnam</p>" % ME_NAME})
    me_email = admin.email
    me_name = admin.name
    env.company.partner_id.email = env.company.partner_id.email or "sales@duotek.example"
    env = env(user=admin)
    Partner, Message = env["res.partner"], env["mail.message"]
    composer = env["dwo.mail.composer"]
    now = fields.Datetime.now()
    tag = env["res.partner.category"].create({"name": TAG})

    def partner(name, email, **vals):
        return Partner.create(dict(name=name, email=email, category_id=[(4, tag.id)], **vals))

    managers = env["res.users"].with_context(no_reset_password=True).create([
        {"name": "Linh Tran", "login": "linh.tran.demo", "password": "demo", "email": BOSS_EMAIL,
         "group_ids": [(6, 0, [env.ref("base.group_user").id, env.ref("base.group_partner_manager").id])]},
        {"name": "Minh Vu", "login": "minh.vu.demo", "password": "demo", "email": "minh.vu@duotek.example",
         "group_ids": [(6, 0, [env.ref("base.group_user").id, env.ref("base.group_partner_manager").id])]},
    ])
    linh, minh = managers
    # the approval flow is on: Linh and Minh are the approvers, the administrator can still send now
    env.company.write({
        "dwo_mail_require_approval": True,
        "dwo_mail_allow_self_approval": True,
        "dwo_mail_approver_ids": [(6, 0, managers.ids)],
        "dwo_mail_exempt_user_ids": [(6, 0, admin.ids)],
    })

    def incoming(record, days_ago, sender, to, cc, subject, body, attachments=()):
        """An email received: what the mail gateway would have stored."""
        # the author is the contact who wrote, as the mail gateway would find or create it
        name, address = tools.mail.email_split_tuples(sender)[0]
        author = Partner.sudo().search([("email", "=", address)], limit=1) or Partner.sudo().create(
            {"name": name or address, "email": address, "parent_id": record.id, "type": "contact"})
        return Message.sudo().create({
            "author_id": author.id,
            "model": record._name, "res_id": record.id, "message_type": "email",
            "subtype_id": env.ref("mail.mt_comment").id, "email_from": sender,
            "incoming_email_to": to, "incoming_email_cc": cc or False,
            "subject": subject, "body": body, "date": now - timedelta(days=days_ago, hours=1),
            "attachment_ids": [(6, 0, [a.id for a in attachments])],
        })

    def send(record, days_ago, to, cc, bcc, subject, body, ref=None):
        """An official email, sent through the real code. Nothing leaves: the queue row is marked sent."""
        vals = {"from": me_email, "to": to, "cc": cc, "bcc": bcc, "subject": subject, "body": body,
                "ref_message_id": ref.id if ref else False, "attachment_ids": []}
        with patch.object(type(env["mail.mail"]), "_send", lambda self, *a, **k: None):
            message = composer.with_context(mail_notify_force_send=False)._send_email(record._name, record.id, vals)
        env["mail.mail"].sudo().search([("mail_message_id", "=", message.id)]).write({"state": "sent"})
        message.sudo().write({"date": now - timedelta(days=days_ago)})
        return message

    # address book for the suggestions
    for name, email in [("Quang Do (Sakura)", "quang.do@sakura-trading.example"),
                        ("Mai Hoang (Mekong)", "mai.hoang@mekong-logistics.example"),
                        ("Accounting", "accounting@duotek.example"),
                        ("Tuan Pham (Pacific)", "tuan.pham@pacific-foods.example")]:
        env["dwo.mail.address"].create({"email": email, "name": name})

    # --- 1. a long conversation: incoming, official reply, customer answer, note and message
    sakura = partner("Sakura Trading Co.", "contact@sakura-trading.example", is_company=True, city="Ho Chi Minh City")
    spec = env["ir.attachment"].create({
        "name": "Specification.txt", "raw": b"Sakura Trading - warehouse scanners\n200 units, delivery in Q1.\n",
        "mimetype": "text/plain", "res_model": "res.partner", "res_id": sakura.id})
    first = incoming(
        sakura, 9, "Lan Pham <lan.pham@sakura-trading.example>", "%s <%s>" % (me_name, me_email),
        "Thu Le <thu.le@sakura-trading.example>", "Quotation for 200 warehouse scanners",
        "<p>Hello %s,</p><p>Could you send us a quotation for 200 handheld scanners, delivery in Q1? "
        "The specification is attached.</p><p>Thanks,<br/>Lan</p>" % me_name, attachments=spec)
    reply = send(
        sakura, 8, [_address("Lan Pham", "lan.pham@sakura-trading.example")],
        [_address("Thu Le", "thu.le@sakura-trading.example")], [_address("Linh Tran", BOSS_EMAIL)],
        "RE: Quotation for 200 warehouse scanners",
        "<p>Hello Lan,</p><p>Thank you for your request. Our quotation <b>Q-2026-0142</b> is ready: "
        "200 units, delivery in February, 12 months of warranty.</p>"
        "<p><img src=\"data:image/png;base64,%s\" style=\"width: 100%%; max-width: 520px;\"/></p>"
        "<p>Best regards,<br/>%s</p>" % (base64.b64encode(_png("Quotation Q-2026-0142")).decode(), me_name), ref=first)
    incoming(
        sakura, 6, "Lan Pham <lan.pham@sakura-trading.example>",
        "%s <%s>" % (me_name, me_email), "Thu Le <thu.le@sakura-trading.example>, Quang Do <quang.do@sakura-trading.example>",
        "RE: Quotation for 200 warehouse scanners",
        "<p>Hello %s,</p><p>Thank you. Our director Quang is now in copy. Can you do <b>15 February</b> for "
        "the first 100 units?</p><p>Lan</p>" % me_name)
    sakura.message_post(body="Customer wants a first delivery of 100 units on 15 February.",
                        message_type="comment", subtype_xmlid="mail.mt_note")
    sakura.with_context(mail_notify_force_send=False).message_post(
        body="@Linh can you confirm the stock for 15 February?", message_type="comment", subtype_xmlid="mail.mt_comment")

    # --- 2. an unsent draft with an inline image (pasted, so stored as an attachment link) and a second draft
    mekong = partner("Mekong Logistics", "contact@mekong-logistics.example", is_company=True, city="Can Tho")
    asked = incoming(
        mekong, 3, "Mai Hoang <mai.hoang@mekong-logistics.example>", "%s <%s>" % (me_name, me_email),
        "Tuan Nguyen <tuan.nguyen@mekong-logistics.example>", "Delivery schedule for March",
        "<p>Hello,</p><p>Please confirm the delivery schedule for March and send us the packing plan.</p><p>Mai</p>")
    defaults = composer.get_defaults("res.partner", mekong.id, asked.id, "reply")
    composer.save_email("res.partner", mekong.id, False, {
        "mode": "reply", "ref_message_id": asked.id, "from": me_email, "to": defaults["to"],
        "cc": defaults["cc"], "bcc": [_address("Accounting", "accounting@duotek.example")],
        "subject": defaults["subject"],
        "body": "<p>Hello Mai,</p><p>The March plan is below, we ship every Tuesday.</p>"
                "<p><img src=\"data:image/png;base64,%s\" style=\"width: 100%%; max-width: 520px;\"/></p><p>Regards</p>%s"
                % (base64.b64encode(_png("March delivery plan", (14, 124, 102), (91, 141, 184))).decode(), defaults["body"]),
    })
    composer.save_email("res.partner", mekong.id, False, {
        "mode": "new", "from": me_email, "to": [_address("Mai Hoang", "mai.hoang@mekong-logistics.example")],
        "subject": "Invoice for February", "body": "<p>Hello Mai, the February invoice is attached.</p>"})

    # --- 3. waiting for approval
    steel = partner("Hanoi Steel JSC", "procurement@hanoi-steel.example", is_company=True, city="Hanoi")
    steel_msg = incoming(
        steel, 2, "Procurement <procurement@hanoi-steel.example>", "%s <%s>" % (me_name, me_email), "",
        "Price list for the new year", "<p>Please send your price list and payment terms for 2027.</p>")
    saved = composer.save_email("res.partner", steel.id, False, {
        "mode": "reply", "ref_message_id": steel_msg.id, "from": me_email,
        "to": [_address("Procurement", "procurement@hanoi-steel.example")], "cc": [], "bcc": [],
        "subject": "RE: Price list for the new year",
        "body": "<p>Hello,</p><p>Our 2027 price list is attached to this email. Payment terms: "
                "<b>30 days</b> after invoice, with a 3% discount above 500 units.</p>"})
    env["dwo.mail.email"].browse(saved["id"]).request_approval(
        linh + minh, "New payment terms for a large customer, please check before it goes out.")

    # --- 4. rejected
    seafood = partner("Da Nang Seafood", "owner@danang-seafood.example", is_company=True, city="Da Nang")
    saved = composer.save_email("res.partner", seafood.id, False, {
        "mode": "new", "from": me_email, "to": [_address("Owner", "owner@danang-seafood.example")],
        "subject": "Special offer: 30% off", "body": "<p>Hello, as a loyal customer you get <b>30% off</b> this month.</p>"})
    pending = env["dwo.mail.email"].browse(saved["id"])
    pending.request_approval(linh, "Discount for a loyal customer.")
    pending.with_user(linh).action_reject("30% is above our limit. Please use 15% and ask again.")

    # --- 5. a forward: an incoming email with an attachment
    pacific = partner("Pacific Foods", "contact@pacific-foods.example", is_company=True, city="Hai Phong")
    layout = env["ir.attachment"].create({
        "name": "warehouse-layout.png", "raw": _png("Warehouse layout", (74, 47, 69), (91, 141, 184)),
        "mimetype": "image/png", "res_model": "res.partner", "res_id": pacific.id})
    incoming(
        pacific, 1, "Tuan Pham <tuan.pham@pacific-foods.example>", "%s <%s>" % (me_name, me_email), "",
        "New warehouse layout", "<p>Hello, here is the layout of our new warehouse. Can your team check the shelving?</p>",
        attachments=layout)

    # --- 6. a clean thread, and a template with a Bcc, to start an email from nothing
    partner("Blue Ocean Studio", "hello@blue-ocean.example", is_company=True, city="Da Lat")
    env["mail.template"].create({
        "name": "Quotation follow-up (demo)", "model_id": env["ir.model"]._get("res.partner").id,
        "subject": "Following up on your request, {{ object.name }}",
        "email_to": "{{ object.email }}", "email_bcc": BOSS_EMAIL,
        "body_html": '<p>Hello <t t-out="object.name"/>,</p><p>We wanted to check whether you had the time to look at '
                     'our quotation. We are happy to answer any question.</p>',
    })
    # notices to the approvers and the message to followers: nothing must leave from a lab database
    env["mail.mail"].sudo().search([("state", "=", "outgoing")]).write({"state": "cancel"})


def uninstall_hook(env):
    tag = env["res.partner.category"].search([("name", "=", TAG)])
    partners = env["res.partner"].search([("id", "child_of", env["res.partner"].search([("category_id", "in", tag.ids)]).ids)])
    env["dwo.mail.email"].sudo().search([("res_model", "=", "res.partner"), ("res_id", "in", partners.ids)]).unlink()
    env["mail.message"].sudo().search([("model", "=", "res.partner"), ("res_id", "in", partners.ids)]).unlink()
    partners.unlink()
    env["mail.template"].search([("name", "=", "Quotation follow-up (demo)")]).unlink()
    env["res.users"].with_context(active_test=False).search(
        [("login", "in", ("linh.tran.demo", "minh.vu.demo"))]).unlink()
    tag.unlink()
