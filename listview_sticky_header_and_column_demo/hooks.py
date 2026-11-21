# -*- coding: utf-8 -*-
"""Creates 500 sample contacts: a list long enough to scroll down and wide enough to scroll sideways."""
import random

COUNTRIES = [("base.us", "United States", ["New York", "Austin", "Seattle", "Denver"]),
             ("base.fr", "France", ["Paris", "Lyon", "Nantes", "Lille"]),
             ("base.de", "Germany", ["Berlin", "Munich", "Hamburg", "Cologne"]),
             ("base.gb", "United Kingdom", ["London", "Leeds", "Bristol", "Glasgow"]),
             ("base.vn", "Vietnam", ["Ha Noi", "Da Nang", "Ho Chi Minh City", "Hai Phong"])]
FIRST = ["Alice", "Bruno", "Chloe", "Daniel", "Elena", "Felix", "Grace", "Hugo", "Iris", "Jonas", "Kira", "Liam",
         "Maya", "Noah", "Olga", "Paul", "Quinn", "Rosa", "Samir", "Tina", "Umar", "Vera", "Will", "Xenia", "Yan", "Zoe"]
LAST = ["Anders", "Bauer", "Costa", "Dubois", "Evans", "Fischer", "Garcia", "Hansen", "Ito", "Jensen", "Klein",
        "Lopez", "Moreau", "Nguyen", "Olsen", "Petit", "Rossi", "Schmidt", "Tran", "Vogel", "Weber", "Young"]
COMPANIES = ["Northwind", "Contoso", "Globex", "Initech", "Umbrella", "Hooli", "Stark Works", "Wayne Supply",
             "Acme Trading", "Blue Harbor", "Red Maple", "Green Valley", "Silver Line", "Golden Gate", "Iron Bridge"]
TOTAL = 500
ROLES = ["Sales Manager", "Buyer", "Accountant", "CEO", "Logistics Lead", "Support Agent", "Marketing Lead",
         "Warehouse Manager", "HR Manager", "Project Manager"]


def post_init_hook(env):
    rnd = random.Random(42)
    countries = {xml: env.ref(xml, raise_if_not_found=False) for xml, _n, _c in COUNTRIES}
    tags = env["res.partner.category"].create([{"name": n} for n in ("Customer", "Vendor", "Partner", "VIP")])
    Partner = env["res.partner"]
    companies = Partner.create([{"name": "%s %s" % (n, suffix), "is_company": True,
                                 "website": "https://www.%s.example.com" % n.lower().replace(" ", "")}
                                for n, suffix in zip(COMPANIES, ["Ltd", "Inc", "GmbH", "SARL", "LLC"] * 3)])
    vals = []
    for index in range(TOTAL - len(companies)):
        xml, _name, cities = rnd.choice(COUNTRIES)
        first, last = rnd.choice(FIRST), rnd.choice(LAST)
        company = rnd.choice(companies)
        domain = company.website.split("www.")[1]
        vals.append({
            "name": "%s %s" % (first, last), "parent_id": company.id, "function": rnd.choice(ROLES),
            "email": "%s.%s@%s" % (first.lower(), last.lower(), domain),
            "phone": "+%d %d %d %d" % (rnd.randint(1, 84), rnd.randint(100, 999), rnd.randint(100, 999), rnd.randint(1000, 9999)),
            "street": "%d %s Street" % (rnd.randint(1, 250), rnd.choice(LAST)), "city": rnd.choice(cities),
            "zip": str(rnd.randint(10000, 99999)), "ref": "C%04d" % (index + 1),
            "vat": "%s%d" % (xml[-2:].upper(), rnd.randint(10**8, 10**9 - 1)), "country_id": countries[xml].id if countries[xml] else False,
            "category_id": [(6, 0, rnd.sample(tags.ids, rnd.randint(1, 2)))],
            "comment": "Sample contact %d for the list view demo." % (index + 1)})
    Partner.create(vals)
