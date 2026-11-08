# -*- coding: utf-8 -*-
"""Demo data for dwo_mail_bcc: emails with Cc, Bcc and Reply-To. Run it again with: uninstall, install."""
from datetime import timedelta
from unittest.mock import patch

from odoo import fields

TAG = "dwo_mail_ccbcc_demo"
TEMPLATE = "Order follow-up (demo)"


def post_init_hook(env):
    admin = env.ref("base.user_admin")
    if not admin.email:
        admin.partner_id.write({"name": "Hieu Nguyen", "email": "hieu.nguyen@duotek.example"})
        admin.write({"signature": "<p>Best regards,<br/>Hieu Nguyen<br/>DUO-TEK Software Vietnam</p>"})
    env.company.partner_id.email = env.company.partner_id.email or "sales@duotek.example"
    env = env(user=admin)
    Partner = env["res.partner"]
    tag = env["res.partner.category"].create({"name": TAG})
    now = fields.Datetime.now()

    def company(name, email, city):
        return Partner.create({"name": name, "email": email, "is_company": True, "city": city,
                               "category_id": [(4, tag.id)]})

    def contact(parent, name, email):
        return Partner.create({"name": name, "email": email, "parent_id": parent.id, "type": "contact"})

    # a template with the three fields
    env["mail.template"].create({
        "name": TEMPLATE, "model_id": env["ir.model"]._get("res.partner").id,
        "subject": "Your order, {{ object.name }}",
        "use_default_to": False,
        "email_to": "{{ object.email }}",
        "email_cc": "accounting@duotek.example",
        "email_bcc": "archive@duotek.example",
        "reply_to": "orders@duotek.example",
        "body_html": '<p>Hello <t t-out="object.name"/>,</p><p>Your order is confirmed and will ship this week.</p>',
    })

    # 1. a thread where the full composer was used: To, Cc, Bcc and Reply-To
    orion = company("Orion Retail", "contact@orion-retail.example", "Ho Chi Minh City")
    minh = contact(orion, "Minh Chau", "minh.chau@orion-retail.example")
    contact(orion, "Hanh Le", "hanh.le@orion-retail.example")

    def send_with_composer(record, days_ago, subject, body, partner, cc, bcc, reply_to):
        composer = env["mail.compose.message"].with_context(
            default_model=record._name, default_res_ids=record.ids, default_composition_mode="comment",
            mail_notify_force_send=False,
        ).create({
            "subject": subject, "body": body, "partner_ids": [(6, 0, partner.ids)],
            "email_cc": cc, "email_bcc": bcc, "reply_to": reply_to,
            "notify_skip_followers": True, "auto_delete": False,
        })
        with patch.object(type(env["mail.mail"]), "_send", lambda self, *a, **k: None):
            composer._action_send_mail()
        message = record.message_ids[:1]
        env["mail.mail"].sudo().search([("mail_message_id", "=", message.id)]).write({"state": "sent"})
        message.sudo().write({"date": now - timedelta(days=days_ago)})
        return message

    send_with_composer(
        orion, 3, "Order confirmation SO-2026-0412",
        "<p>Hello Minh,</p><p>Your order <b>SO-2026-0412</b> is confirmed: 200 units, delivery on 15 February.</p>"
        "<p>Best regards,<br/>Hieu</p>",
        minh, "hanh.le@orion-retail.example, quang.do@duotek.example",
        "archive@duotek.example", "orders@duotek.example")
    send_with_composer(
        orion, 1, "Delivery update",
        "<p>Hello Minh,</p><p>The delivery moves to 17 February. Sorry for the delay.</p>",
        minh, "Hanh Le <hanh.le@orion-retail.example>", False, False)

    # 2. a clean thread, to show the composer with its fields
    polar = company("Polar Foods", "contact@polar-foods.example", "Hanoi")
    contact(polar, "Tuan Pham", "tuan.pham@polar-foods.example")
    contact(polar, "Lan Nguyen", "lan.nguyen@polar-foods.example")

    env["mail.mail"].sudo().search([("state", "=", "outgoing")]).write({"state": "cancel"})


def uninstall_hook(env):
    tag = env["res.partner.category"].search([("name", "=", TAG)])
    partners = env["res.partner"].search([("id", "child_of", env["res.partner"].search([("category_id", "in", tag.ids)]).ids)])
    env["mail.mail"].sudo().search([("model", "=", "res.partner"), ("res_id", "in", partners.ids)]).unlink()
    env["mail.message"].sudo().search([("model", "=", "res.partner"), ("res_id", "in", partners.ids)]).unlink()
    partners.unlink()
    env["mail.template"].search([("name", "=", TEMPLATE)]).unlink()
    tag.unlink()
