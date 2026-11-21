# -*- coding: utf-8 -*-
"""Creates the purchase approval flow and a few purchase orders at different steps."""
import json


def _flow_graph():
    def tr(name, src, dst, color, who=None, **kw):
        return dict({"name": name, "from": src, "to": dst, "color": color, "who": who}, **kw)

    users = {"type": "users", "value": "demo_bob,demo_carol"}
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
               rules=["[('amount_total', '<=', 1000)]"],
               main_step={"mode": "call_method", "method": "button_approve"}),
            tr("Approve (large order)", "to approve", "purchase", 10,
               {"approvers": [users], "approvals": {"mode": "n", "n": 2}},
               rules=["[('amount_total', '>', 1000)]"],
               main_step={"mode": "call_method", "method": "button_approve"}),
            tr("Reject", "to approve", "cancel", 1,
               {"approvers": [users], "approvals": {"mode": "any"}}, ask_reason=True),
            tr("Reopen", "cancel", "draft", 0, None),
        ],
    }


def post_init_hook(env):
    model = env["ir.model"]._get("purchase.order")
    field = env["ir.model.fields"]._get("purchase.order", "state")
    flow = env["dwo.approval.flow"].create({
        "name": "Purchase approval", "model_id": model.id, "state_mode": "field",
        "state_field_id": field.id, "replace_statusbar": True})
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
