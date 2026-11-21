# -*- coding: utf-8 -*-
"""Contacts with a long chatter history: the focus mode hides it or opens it as a drawer."""
import random

FIRST = ["Alice", "Bruno", "Chloe", "Daniel", "Elena", "Felix", "Grace", "Hugo", "Iris", "Jonas", "Kira", "Liam"]
LAST = ["Anders", "Bauer", "Costa", "Dubois", "Evans", "Fischer", "Garcia", "Hansen", "Jensen", "Klein", "Lopez", "Moreau"]
COMPANIES = ["Northwind", "Contoso", "Globex", "Initech", "Umbrella", "Hooli"]
ROLES = ["Sales Manager", "Buyer", "Accountant", "CEO", "Logistics Lead", "Support Agent"]
NOTES = [
    "Called the customer to discuss the new offer.",
    "Offer sent by email, waiting for feedback.",
    "Customer asked for a discount on 100 units.",
    "Discount approved by the sales manager, contract in preparation.",
    "Contract sent for signature.",
    "Signed contract received, order created.",
    "Delivery planned for next week, customer informed.",
    "Customer confirmed the delivery address.",
    "Invoice sent, payment terms 30 days.",
    "Payment received, thanks!",
]


def post_init_hook(env):
    rnd = random.Random(11)
    Partner = env["res.partner"]
    companies = Partner.create([{"name": "%s Ltd" % n, "is_company": True} for n in COMPANIES])
    people = Partner.create([{
        "name": "%s %s" % (rnd.choice(FIRST), rnd.choice(LAST)), "parent_id": rnd.choice(companies).id,
        "function": rnd.choice(ROLES), "email": "contact%d@example.com" % i, "phone": "+1 555 %04d" % rnd.randint(0, 9999)}
        for i in range(30)])
    for person in people[:12]:
        for text in NOTES:
            person.message_post(body=text, message_type="comment", subtype_xmlid="mail.mt_note")
        person.activity_schedule("mail.mail_activity_data_todo", summary="Call back about the offer")
