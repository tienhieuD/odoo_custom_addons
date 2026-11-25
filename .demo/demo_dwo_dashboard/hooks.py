# -*- coding: utf-8 -*-
"""About 360 sales orders over 24 months (more in recent months) and a dashboard for each demo user."""
import random
from datetime import datetime, timedelta

from .pages import contacts_page, sales_page

CATEGORIES = {"Furniture": [("Desk", 380), ("Office chair", 210), ("Bookshelf", 150), ("Meeting table", 640)],
              "Electronics": [("Laptop", 1150), ("Monitor", 290), ("Headset", 85), ("Webcam", 60), ("Dock", 140)],
              "Services": [("Installation", 120), ("Training day", 480), ("Support plan", 300)],
              "Supplies": [("Notebook pack", 18), ("Printer paper", 9), ("Ink cartridge", 45)]}
COMPANIES = ["Northwind", "Contoso", "Globex", "Initech", "Umbrella", "Hooli", "Stark Works", "Wayne Supply", "Acme Trading",
             "Blue Harbor", "Red Maple", "Green Valley", "Silver Line", "Golden Gate", "Iron Bridge", "Sunrise Foods",
             "Pioneer Labs", "Atlas Freight", "Nova Retail", "Lakeside Clinic"]
COUNTRIES = ["base.us", "base.fr", "base.de", "base.gb", "base.vn", "base.jp"]
ORDERS = 360


def post_init_hook(env):
    rnd = random.Random(5)
    sellers = env["res.users"].browse([env.ref("demo_users.user_%s" % n).id for n in ("alice", "bob", "carol")])
    sellers.write({"group_ids": [(4, env.ref("sales_team.group_sale_salesman_all_leads").id)]})
    env = env(context=dict(env.context, tracking_disable=True, mail_notrack=True, mail_create_nolog=True))
    _orders(env, rnd, sellers)
    for user in sellers:
        _dashboards(env(user=user.id))


def _orders(env, rnd, sellers):
    countries = [c for c in (env.ref(x, raise_if_not_found=False) for x in COUNTRIES) if c] \
        or env["res.country"].search([], limit=6)
    customers = env["res.partner"].create([{"name": n, "is_company": True, "customer_rank": 1,
                                            "country_id": rnd.choice(countries).id} for n in COMPANIES])
    products = []
    for cat, items in CATEGORIES.items():
        categ = env["product.category"].create({"name": cat})
        for name, price in items:
            products.append(env["product.product"].create({"name": name, "list_price": price, "categ_id": categ.id}))
    now = datetime.now()
    weights = [1 + month * 0.12 for month in range(24, 0, -1)]  # growing business, month 24 is this month
    plan = []
    for _i in range(ORDERS):
        month = rnd.choices(range(24), weights=weights)[0]
        when = now - timedelta(days=month * 30 + rnd.randint(0, 29), hours=rnd.randint(0, 20))
        plan.append(min(when, now - timedelta(hours=1)))
    plan.sort()
    for when in plan:
        picks = rnd.sample(products, rnd.randint(1, 4))
        order = env["sale.order"].create({
            "partner_id": rnd.choice(customers).id, "user_id": rnd.choices(sellers.ids, weights=[5, 3, 2])[0],
            "order_line": [(0, 0, {"product_id": p.id, "product_uom_qty": rnd.randint(1, 8),
                                   "price_unit": round(p.list_price * rnd.uniform(0.9, 1.05), 2)}) for p in picks]})
        roll = rnd.random()
        if roll < 0.85:
            order.action_confirm()
        elif roll > 0.95:
            order.action_cancel()
        env.cr.execute("UPDATE sale_order SET date_order = %s, create_date = %s WHERE id = %s", [when, when, order.id])
        env.cr.execute("UPDATE sale_order_line SET create_date = %s WHERE order_id = %s", [when, order.id])
    env.invalidate_all()


def _dashboards(env):
    dashboard = env["dwo.dashboard"].get_my_dashboard()
    home = env["dwo.dashboard.page"].browse(dashboard["pages"][0]["id"])
    home.write({"name": "Sales", "spec": sales_page()})
    env["dwo.dashboard.page"].create({"dashboard_id": dashboard["id"], "name": "Contacts", "sequence": 20,
                                      "spec": contacts_page()})
