# -*- coding: utf-8 -*-
"""Turns the conflict check on for the main contact fields and creates contacts to collide on."""
WATCHED = ["name", "email", "phone", "function", "street", "city", "website"]
CONTACTS = [("Northwind Traders", "contact@northwind.example.com", "+1 555 0101", "Seattle"),
            ("Contoso Ltd", "hello@contoso.example.com", "+44 20 5550 102", "London"),
            ("Globex Corporation", "sales@globex.example.com", "+49 30 5550103", "Berlin"),
            ("Initech", "info@initech.example.com", "+1 555 0104", "Austin"),
            ("Umbrella Supplies", "office@umbrella.example.com", "+33 1 5550 105", "Paris")]


def post_init_hook(env):
    model = env["ir.model"]._get("res.partner")
    fields = env["ir.model.fields"].search([("model", "=", "res.partner"), ("name", "in", WATCHED)])
    env["dwo.model.concurrency"].create({"model_id": model.id, "field_ids": [(6, 0, fields.ids)]})
    env["res.partner"].create([{"name": n, "email": e, "phone": p, "city": c, "is_company": True} for n, e, p, c in CONTACTS])
