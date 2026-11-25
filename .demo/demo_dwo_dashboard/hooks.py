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
    sales = env.ref("sales_team.group_sale_salesman_all_leads")
    sellers.write({"group_ids": [(4, sales.id)]})
    # demo_admin: a normal user who manages the dashboards (datasets, metrics, the assistant) without any Settings right
    manager = env["res.users"].with_context(no_reset_password=True).create({
        "name": "Dana Admin", "login": "demo_admin", "password": "demo", "email": "dana@example.com",
        "group_ids": [(6, 0, [env.ref("base.group_user").id, env.ref("base.group_partner_manager").id, sales.id,
                              env.ref("dwo_dashboard.group_dwo_dashboard_manager").id])]})
    env = env(context=dict(env.context, tracking_disable=True, mail_notrack=True, mail_create_nolog=True))
    # the assistant is on in the demo (the owner's choice); dwo_dashboard.ai_enabled = 0 switches it off
    _metrics(env)
    _blend(env)
    _orders(env, rnd, sellers)
    for user in sellers | manager:
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


def _blend(env):
    """A blend: two readings of the sales orders (the won ones, the open quotations) side by side on the same months."""
    import json
    env["dwo.dataset"].create({"kind": "blend", "code": "won_open", "label": "Won and open sales", "definition_text": json.dumps({
        "schema": "dwo-dataset/1", "type": "blend", "code": "won_open", "label": "Won and open sales",
        "sources": [{"name": "won", "dataset": "orm:sale.order", "where": [["state", "in", ["sale", "done"]]]},
                    {"name": "open", "dataset": "orm:sale.order", "where": [["state", "in", ["draft", "sent"]]]}],
        "dimensions": [{"name": "month", "label": "Order date", "kind": "date", "map": {"won": "date_order", "open": "date_order"}},
                       {"name": "seller", "label": "Salesperson", "kind": "many2one", "comodel": "res.users",
                        "map": {"won": "user_id", "open": "user_id"}}],
        "metrics": [{"name": "won", "source": "won", "agg": "sum", "field": "amount_total", "label": "Won", "format": "currency"},
                    {"name": "open", "source": "open", "agg": "sum", "field": "amount_total", "label": "Open quotations",
                     "format": "currency"}]})})


def _metrics(env):
    """Named measures for the sales orders: what the Sales page uses, and what Explore offers under "Metrics"."""
    field = lambda model, name: env["ir.model.fields"]._get(model, name).id  # noqa: E731
    env["dwo.dataset"].create({
        "model_id": env.ref("sale.model_sale_order").id, "label": "Sales orders",
        "metric_ids": [
            (0, 0, {"name": "revenue", "label": "Revenue", "agg": "sum", "field_id": field("sale.order", "amount_total"),
                    "where": "[('state', 'in', ['sale', 'done'])]", "format": "currency"}),
            (0, 0, {"name": "orders", "label": "Orders", "agg": "count", "where": "[('state', 'in', ['sale', 'done'])]"}),
            (0, 0, {"name": "avg_order", "label": "Average order", "agg": "avg", "field_id": field("sale.order", "amount_total"),
                    "where": "[('state', 'in', ['sale', 'done'])]", "format": "currency"}),
            (0, 0, {"name": "quotations", "label": "Open quotations", "agg": "count",
                    "where": "[('state', 'in', ['draft', 'sent'])]"}),
            (0, 0, {"name": "quoted", "label": "Quoted amount", "agg": "sum", "field_id": field("sale.order", "amount_total"),
                    "where": "[('state', 'in', ['draft', 'sent'])]", "format": "currency"}),
        ]})
