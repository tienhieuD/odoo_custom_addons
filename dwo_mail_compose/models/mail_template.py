# -*- coding: utf-8 -*-
from odoo import fields, models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    # Odoo 17 has this field in core (the owner of a personal template); Odoo 16 does not: the form of the
    # composer saves its templates with their owner, and lists the templates of the user first.
    user_id = fields.Many2one("res.users", string="Owner", copy=False,
                              help="The user a template made from the email composer belongs to.")
