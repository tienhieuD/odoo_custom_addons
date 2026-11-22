# -*- coding: utf-8 -*-
"""A small document with no state of its own: its approval steps come from an approval flow."""
from odoo import fields, models


class AwesomeBusinessTrip(models.Model):
    _name = "awesome.business.trip"
    _description = "Business Trip"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc, id desc"

    name = fields.Char(string="Trip", required=True, tracking=True)
    traveler_id = fields.Many2one("res.users", string="Traveler", default=lambda self: self.env.user, tracking=True)
    manager_id = fields.Many2one(
        "res.users", string="Line manager", tracking=True,
        default=lambda self: self.env.ref("demo_users.user_bob", raise_if_not_found=False))
    destination = fields.Char(required=True)
    date_from = fields.Date(string="From", required=True, default=fields.Date.context_today)
    date_to = fields.Date(string="To", required=True, default=fields.Date.context_today)
    transport = fields.Selection(
        [("flight", "Flight"), ("train", "Train"), ("car", "Car")], default="flight", required=True)
    total_cost = fields.Float(string="Estimated cost (USD)", tracking=True)
    purpose = fields.Text()
