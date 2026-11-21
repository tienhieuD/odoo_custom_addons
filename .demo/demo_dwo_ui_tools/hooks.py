# -*- coding: utf-8 -*-
"""300 contacts to filter from the list header, and a few with a busy chatter for the focus mode."""
import random
from datetime import datetime, timedelta

COUNTRIES = [("base.us", ["New York", "Austin", "Seattle", "Denver"]), ("base.fr", ["Paris", "Lyon", "Nantes", "Lille"]),
             ("base.de", ["Berlin", "Munich", "Hamburg", "Cologne"]), ("base.gb", ["London", "Leeds", "Bristol", "Glasgow"]),
             ("base.vn", ["Ha Noi", "Da Nang", "Ho Chi Minh City", "Hai Phong"]), ("base.jp", ["Tokyo", "Osaka", "Nagoya", "Kyoto"])]
FIRST = ["Alice", "Bruno", "Chloe", "Daniel", "Elena", "Felix", "Grace", "Hugo", "Iris", "Jonas", "Kira", "Liam", "Maya",
         "Noah", "Olga", "Paul", "Quinn", "Rosa", "Samir", "Tina", "Umar", "Vera", "Will", "Xenia", "Yan", "Zoe"]
LAST = ["Anders", "Bauer", "Costa", "Dubois", "Evans", "Fischer", "Garcia", "Hansen", "Ito", "Jensen", "Klein", "Lopez",
        "Moreau", "Nguyen", "Olsen", "Petit", "Rossi", "Schmidt", "Tran", "Vogel", "Weber", "Young"]
COMPANIES = ["Northwind", "Contoso", "Globex", "Initech", "Umbrella", "Hooli", "Stark Works", "Wayne Supply", "Acme Trading",
             "Blue Harbor", "Red Maple", "Green Valley", "Silver Line", "Golden Gate", "Iron Bridge"]
ROLES = ["Sales Manager", "Buyer", "Accountant", "CEO", "Logistics Lead", "Support Agent", "Marketing Lead", "Warehouse Manager"]
TAGS = ["Customer", "Vendor", "Partner", "VIP", "Prospect"]
TOTAL = 300


def post_init_hook(env):
    rnd = random.Random(7)
    countries = {xml: env.ref(xml, raise_if_not_found=False) for xml, _c in COUNTRIES}
    tags = env["res.partner.category"].create([{"name": n} for n in TAGS])
    Partner = env["res.partner"]
    companies = Partner.create([{"name": "%s %s" % (n, rnd.choice(["Ltd", "Inc", "GmbH", "SARL"])), "is_company": True,
                                 "category_id": [(6, 0, rnd.sample(tags.ids, 2))]} for n in COMPANIES])
    vals = []
    for _i in range(TOTAL - len(companies)):
        xml, cities = rnd.choice(COUNTRIES)
        first, last = rnd.choice(FIRST), rnd.choice(LAST)
        company = rnd.choice(companies)
        vals.append({
            "name": "%s %s" % (first, last), "parent_id": company.id, "function": rnd.choice(ROLES),
            "email": "%s.%s@%s.example.com" % (first.lower(), last.lower(), company.name.split()[0].lower()),
            "phone": "+%d %d %d" % (rnd.randint(1, 84), rnd.randint(100, 999), rnd.randint(1000, 9999)),
            "city": rnd.choice(cities), "country_id": countries[xml].id if countries[xml] else False,
            "category_id": [(6, 0, rnd.sample(tags.ids, rnd.randint(1, 2)))]})
    people = Partner.create(vals)
    # creation dates over the last two years, so the quick dates and the fiscal year filter have something to show
    now = datetime.now()
    env.cr.execute("SELECT id FROM res_partner WHERE id = ANY(%s)", [(companies | people).ids])
    for (pid,) in env.cr.fetchall():
        when = now - timedelta(days=rnd.randint(0, 730), hours=rnd.randint(0, 23))
        env.cr.execute("UPDATE res_partner SET create_date = %s WHERE id = %s", [when, pid])
    # contacts with a busy chatter (focus mode hides it or opens it as a drawer)
    for person in people[:6]:
        for day, text in ((20, "Called to discuss the new offer."), (12, "Offer sent by email, waiting for feedback."),
                          (5, "Customer asked for a discount on 100 units."), (1, "Discount approved, contract in preparation.")):
            person.message_post(body=text, message_type="comment", subtype_xmlid="mail.mt_note")
