# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    dwo_mail_require_approval = fields.Boolean(
        "Use the approval flow",
        help="Off: an email written with the Send email button is sent right away, there is no approval. "
             "On: it must be approved before it is sent, and only the people in \"Can send without "
             "approval\" can still send right away.")
    dwo_mail_allow_self_approval = fields.Boolean(
        "Allow approving your own emails", default=True,
        help="Off: the author of an email cannot be one of its approvers.")
    dwo_mail_approver_ids = fields.Many2many(
        "res.users", "dwo_mail_company_approver_rel", "company_id", "user_id",
        string="Approvers", domain=[("share", "=", False)],
        help="The people who can be chosen to approve an email. Empty: every internal user can approve.")
    dwo_mail_exempt_user_ids = fields.Many2many(
        "res.users", "dwo_mail_company_exempt_rel", "company_id", "user_id",
        string="Can send without approval", domain=[("share", "=", False)],
        default=lambda self: self.env.ref("base.user_admin", raise_if_not_found=False).ids,
        help="When the approval flow is on, these people can still send an email right away.")
