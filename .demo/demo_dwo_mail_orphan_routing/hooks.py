# -*- coding: utf-8 -*-
"""Feeds sample emails that no alias or thread can take through the mail gateway: they become orphan emails."""
from email.message import EmailMessage

PROJECTS = [("Northwind refit", "PRJ-1001"), ("Harbor warehouse", "PRJ-1002"), ("Maple street office", "PRJ-1003")]
CUSTOMERS = [("Lan Pham", "lan@northwind.example"), ("Marc Dubois", "marc@harbor.example"), ("Sara Olsen", "sara@maple.example")]

# (from, subject, body, html?, attachment?)
MAILS = [
    ("Lan Pham <lan@northwind.example>", "Question about PRJ-1001 delivery", "When will the last pallet arrive?", False, False),
    ("Marc Dubois <marc@harbor.example>", "Re: PRJ-1002 invoice", "The invoice total looks too high, please check.", False, True),
    ("Sara Olsen <sara@maple.example>", "Floor plan update", "Attached the updated plan for the third floor.", True, True),
    ("Lan Pham <lan@northwind.example>", "Thanks!", "Thank you for the quick answer yesterday.", False, False),
    ("Marc Dubois <marc@harbor.example>", "Meeting next week?", "Can we meet on Tuesday to discuss the schedule?", False, False),
    ("Unknown Buyer <buyer@newclient.example>", "Request for a quotation", "We would like a quote for 20 desks.", True, False),
    ("Sara Olsen <sara@maple.example>", "PRJ-1003 site access", "Our badges expire on Friday. Who can renew them?", False, False),
    ("Support Desk <noreply@vendor.example>", "Your ticket 8841 was updated", "The ticket was updated by an agent.", True, False),
    ("Lan Pham <lan@northwind.example>", "Contract renewal", "Please send the renewal contract for signature.", False, True),
    ("Newsletter <news@example.org>", "November news", "Our latest articles are here.", True, False),
]


def _raw(index, sender, subject, body, html, attach):
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = sender, "projects@unknown-alias.example", subject
    msg["Message-Id"] = "<demo-orphan-%d@mail.example>" % index
    if html:
        msg.set_content(body)
        msg.add_alternative("<p>%s</p><p><b>Best regards</b></p>" % body, subtype="html")
    else:
        msg.set_content(body)
    if attach:
        msg.add_attachment(b"item,amount\nA,10\nB,20\n", maintype="text", subtype="csv", filename="details.csv")
    return msg.as_string()


def post_init_hook(env):
    Orphan = env["dwo.mail.orphan"]
    # settings: capture on, emails can be routed to contacts
    Orphan._icp_set("enabled", "1")
    Orphan._icp_set("target_models", "res.partner")
    # the demo users manage the orphan list, for every alias
    group = env.ref("dwo_mail_orphan_routing.group_dwo_orphan_manager")
    users = env["res.users"].search([("login", "in", ["demo_alice", "demo_bob", "demo_carol"])])
    users.write({"group_ids": [(4, group.id)], "dwo_orphan_all_aliases": True})
    # records the emails can be routed to
    Partner = env["res.partner"]
    Partner.create([{"name": name, "ref": code, "is_company": True} for name, code in PROJECTS])
    Partner.create([{"name": name, "email": email} for name, email in CUSTOMERS])
    for index, mail in enumerate(MAILS, 1):
        env["mail.thread"].message_process(False, _raw(index, *mail))
