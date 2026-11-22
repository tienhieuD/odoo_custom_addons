# -*- coding: utf-8 -*-
"""Creates the purchase approval flow and a few purchase orders at different steps."""
import json
from datetime import timedelta

from odoo import fields


NOTIFY = {"followers": {"bus": False, "activity": False, "email": True}, "creator": True}


def _flow_graph():
    def tr(name, src, dst, color, who=None, **kw):
        return dict({"name": name, "from": src, "to": dst, "color": color, "who": who}, **kw)

    users = {"type": "users", "value": "demo_bob,demo_carol", "notify": {"bus": True, "activity": True, "email": False}}
    return {
        "schema": "dwo_approval_flow/1",
        "states": [
            {"key": "draft", "name": "Draft", "x": 10, "y": 80},
            {"key": "to approve", "name": "To Approve", "x": 270, "y": 80},
            {"key": "purchase", "name": "Purchase Order", "x": 540, "y": 20, "color": 10},
            {"key": "cancel", "name": "Cancelled", "x": 540, "y": 190, "color": 1},
        ],
        "transitions": [
            tr("Submit", "draft", "to approve", 0,
               {"approvers": [{"type": "group", "value": "purchase.group_purchase_user"}], "approvals": {"mode": "any"}},
               list_action=True),
            tr("Approve", "to approve", "purchase", 10,
               {"approvers": [users], "approvals": {"mode": "any"}},
               rules=["[('amount_total', '<=', 1000)]"], notify=NOTIFY,
               main_step={"mode": "call_method", "method": "button_approve"}),
            tr("Approve (large order)", "to approve", "purchase", 10,
               {"approvers": [users], "approvals": {"mode": "n", "n": 2}},
               rules=["[('amount_total', '>', 1000)]"], notify=NOTIFY,
               main_step={"mode": "call_method", "method": "button_approve"}),
            tr("Reject", "to approve", "cancel", 1,
               {"approvers": [users], "approvals": {"mode": "any"}}, ask_reason=True,
               notify=NOTIFY),
            tr("Reopen", "cancel", "draft", 0, None),
        ],
    }


def post_init_hook(env):
    model = env["ir.model"]._get("purchase.order")
    field = env["ir.model.fields"]._get("purchase.order", "state")
    flow = env["dwo.approval.flow"].create({
        "name": "Purchase approval", "model_id": model.id, "state_mode": "field",
        "state_field_id": field.id, "replace_statusbar": True,
        "remind_after": 24})
    flow.graph = json.dumps(_flow_graph())

    alice = env.ref("demo_users.user_alice")
    vendor = env.ref("demo_dwo_approval_flow.vendor_gemini")
    chair = env.ref("demo_dwo_approval_flow.product_chair")
    desk = env.ref("demo_dwo_approval_flow.product_desk")
    lamp = env.ref("demo_dwo_approval_flow.product_lamp")

    def order(product, qty, price, user=alice):
        return env["purchase.order"].with_user(user).create({
            "partner_id": vendor.id,
            "order_line": [(0, 0, {"product_id": product.id, "product_qty": qty, "price_unit": price})]})

    def press(po, name, user):
        tr = flow.transition_ids.filtered(lambda t: t.name == name)[:1]
        env["dwo.approval.flow"].with_user(user).press("purchase.order", po.id, tr.id)

    order(lamp, 5, 80)                       # draft, up to 1000: one approval
    order(desk, 4, 450)                      # draft, over 1000: two approvals
    press(order(chair, 3, 120), "Submit", alice)  # waiting for approval
    press(order(desk, 6, 450), "Submit", alice)
    _create_trips(env)


# ---------------------------------------------------------------------------------------------
# Business trips: a document with no state of its own, eight steps, notifications everywhere
# ---------------------------------------------------------------------------------------------
def _trip_graph():
    def line(kind, value, **channels):
        return {"type": kind, "value": value, "notify": dict({"bus": False, "activity": False, "email": False}, **channels)}

    def who(*lines, **approvals):
        return {"approvers": list(lines), "approvals": approvals or {"mode": "any"}}

    def tr(name, src, dst, color, who=None, creator=False, followers=None, **kw):
        notify = {"followers": dict({"bus": False, "activity": False, "email": False}, **(followers or {})),
                  "creator": creator}
        return dict({"name": name, "from": src, "to": dst, "color": color, "who": who, "notify": notify}, **kw)

    manager = who(line("field", "manager_id", bus=True, activity=True))
    finance = who(line("group", "demo_dwo_approval_flow.group_finance", bus=True, activity=True, email=True))
    director = who(line("users", "demo_carol", bus=True, activity=True, email=True))
    desk = who(line("group", "demo_dwo_approval_flow.group_travel_desk", activity=True, email=True))
    traveler = who(line("field", "traveler_id", bus=True))
    followers = {"email": True}

    return {
        "schema": "dwo_approval_flow/1",
        "states": [
            {"key": "draft", "name": "Draft", "x": 10, "y": 120},
            {"key": "rejected", "name": "Rejected", "x": 370, "y": 10, "color": 1, "visible": False},
            {"key": "manager_review", "name": "Manager review", "x": 250, "y": 120, "color": 4},
            {"key": "finance_check", "name": "Finance check", "x": 490, "y": 120, "color": 4},
            {"key": "director_approval", "name": "Director approval", "x": 730, "y": 120, "color": 4},
            {"key": "travel_booking", "name": "Travel booking", "x": 670, "y": 290, "color": 2},
            {"key": "booked", "name": "Booked", "x": 450, "y": 290, "color": 10},
            {"key": "expense_report", "name": "Expense report", "x": 230, "y": 290, "color": 8},
            {"key": "settled", "name": "Settled", "x": 10, "y": 290, "color": 10},
        ],
        "transitions": [
            tr("Submit", "draft", "manager_review", 0, None),
            tr("Approve", "manager_review", "finance_check", 10, manager, creator=True, followers=followers),
            tr("Reject", "manager_review", "rejected", 1, manager, creator=True, ask_reason=True),
            tr("Approve", "finance_check", "travel_booking", 10, finance, creator=True,
               rules=["[('total_cost', '<=', 3000)]"]),
            tr("To director", "finance_check", "director_approval", 10, finance, creator=True,
               rules=["[('total_cost', '>', 3000)]"]),
            tr("Reject", "finance_check", "rejected", 1, finance, creator=True, ask_reason=True),
            tr("Approve", "director_approval", "travel_booking", 10, director, creator=True),
            tr("Reject", "director_approval", "rejected", 1, director, creator=True, ask_reason=True),
            tr("Book trip", "travel_booking", "booked", 10, desk, creator=True, followers=followers),
            tr("File expenses", "booked", "expense_report", 0, traveler),
            tr("Settle", "expense_report", "settled", 10, finance, creator=True, followers=followers),
            tr("Send back", "expense_report", "booked", 2, finance, creator=True, ask_reason=True),
            tr("Reopen", "rejected", "draft", 0, traveler),
        ],
    }


def _create_trips(env):
    flow = env["dwo.approval.flow"].create({
        "name": "Business trip approval", "model_id": env["ir.model"]._get("awesome.business.trip").id,
        "state_mode": "custom", "remind_after": 24})
    flow.graph = json.dumps(_trip_graph())

    alice = env.ref("demo_users.user_alice")
    bob = env.ref("demo_users.user_bob")
    fiona = env.ref("demo_dwo_approval_flow.user_finance")
    tom = env.ref("demo_dwo_approval_flow.user_travel")
    today = fields.Date.today()

    def trip(name, destination, cost, days, transport="flight"):
        return env["awesome.business.trip"].with_user(alice).create({
            "name": name, "destination": destination, "total_cost": cost, "transport": transport,
            "date_from": today + timedelta(days=days), "date_to": today + timedelta(days=days + 3),
            "manager_id": bob.id, "purpose": "Meet the customer team and agree the next steps."})

    def press(doc, name, src, user, reason=None):
        arrow = flow.transition_ids.filtered(lambda t: t.name == name and t.from_state_id.key == src)[:1]
        env["dwo.approval.flow"].with_user(user).press(doc._name, doc.id, arrow.id, reason)

    trip("Sales summit in Berlin", "Berlin", 2400, 40)                                   # draft
    press(trip("Customer workshop in Lyon", "Lyon", 1150, 30, "train"), "Submit", "draft", alice)  # manager review
    doc = trip("Partner conference in Singapore", "Singapore", 5200, 60)                 # finance check
    press(doc, "Submit", "draft", alice)
    press(doc, "Approve", "manager_review", bob)
    doc = trip("Annual kickoff in Lisbon", "Lisbon", 3800, 50)                           # director approval
    for name, src, user in (("Submit", "draft", alice), ("Approve", "manager_review", bob),
                            ("To director", "finance_check", fiona)):
        press(doc, name, src, user)
    doc = trip("Training in Amsterdam", "Amsterdam", 1900, 25, "train")                  # travel booking
    for name, src, user in (("Submit", "draft", alice), ("Approve", "manager_review", bob),
                            ("Approve", "finance_check", fiona)):
        press(doc, name, src, user)
    doc = trip("Supplier visit in Milan", "Milan", 2600, 15)                             # expense report
    for name, src, user in (("Submit", "draft", alice), ("Approve", "manager_review", bob),
                            ("Approve", "finance_check", fiona), ("Book trip", "travel_booking", tom),
                            ("File expenses", "booked", alice)):
        press(doc, name, src, user)
    doc = trip("Onboarding visit in Prague", "Prague", 1400, -20, "train")              # settled
    for name, src, user in (("Submit", "draft", alice), ("Approve", "manager_review", bob),
                            ("Approve", "finance_check", fiona), ("Book trip", "travel_booking", tom),
                            ("File expenses", "booked", alice), ("Settle", "expense_report", fiona)):
        press(doc, name, src, user)
    doc = trip("Team retreat in Bali", "Bali", 900, 70)                                  # rejected
    press(doc, "Submit", "draft", alice)
    press(doc, "Reject", "manager_review", bob, reason="Not in this quarter's budget.")
