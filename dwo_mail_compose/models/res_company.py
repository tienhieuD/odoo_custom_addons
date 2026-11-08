# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    dwo_mail_require_approval = fields.Boolean(
        "Require approval for emails",
        help="Users cannot send an email directly with the Send email button: every email goes "
             "through an approver (who can be themselves).")
