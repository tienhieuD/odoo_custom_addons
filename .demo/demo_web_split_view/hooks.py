# -*- coding: utf-8 -*-
"""A hundred English contacts to browse in the split view."""
import random

FIRST = ["Alice", "Bruno", "Chloe", "Daniel", "Elena", "Felix", "Grace", "Hugo", "Iris", "Jonas", "Kira", "Liam", "Maya",
         "Noah", "Olga", "Paul", "Quinn", "Rosa", "Samir", "Tina"]
LAST = ["Anders", "Bauer", "Costa", "Dubois", "Evans", "Fischer", "Garcia", "Hansen", "Jensen", "Klein", "Lopez", "Moreau",
        "Olsen", "Petit", "Rossi", "Schmidt", "Vogel", "Weber", "Young"]
COMPANIES = ["Northwind", "Contoso", "Globex", "Initech", "Umbrella", "Hooli", "Acme Trading", "Blue Harbor", "Red Maple",
             "Green Valley"]
ROLES = ["Sales Manager", "Buyer", "Accountant", "CEO", "Logistics Lead", "Support Agent", "Marketing Lead"]
CITIES = ["New York", "Austin", "Seattle", "London", "Leeds", "Berlin", "Munich", "Paris", "Lyon", "Tokyo"]


def post_init_hook(env):
    rnd = random.Random(5)
    Partner = env["res.partner"]
    companies = Partner.create([{"name": "%s Ltd" % n, "is_company": True, "city": rnd.choice(CITIES),
                                 "website": "https://www.%s.example.com" % n.lower().replace(" ", "")} for n in COMPANIES])
    vals = []
    for _i in range(90):
        first, last, company = rnd.choice(FIRST), rnd.choice(LAST), rnd.choice(companies)
        vals.append({"name": "%s %s" % (first, last), "parent_id": company.id, "function": rnd.choice(ROLES),
                     "email": "%s.%s@%s.example.com" % (first.lower(), last.lower(), company.name.split()[0].lower()),
                     "phone": "+1 555 %04d" % rnd.randint(0, 9999), "city": company.city,
                     "comment": "Sample contact for the split view demo."})
    Partner.create(vals)
