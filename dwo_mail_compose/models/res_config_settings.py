# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    dwo_mail_require_approval = fields.Boolean(
        related="company_id.dwo_mail_require_approval", readonly=False)
    dwo_mail_allow_self_approval = fields.Boolean(
        related="company_id.dwo_mail_allow_self_approval", readonly=False)
    dwo_mail_approver_ids = fields.Many2many(
        related="company_id.dwo_mail_approver_ids", readonly=False)
    dwo_mail_exempt_user_ids = fields.Many2many(
        related="company_id.dwo_mail_exempt_user_ids", readonly=False)
    dwo_mail_retention_days = fields.Integer(
        "Delete unfinished emails after (days)",
        config_parameter="dwo_mail_compose.retention_days", default=180,
        help="An email written with the Send email button (draft, waiting for approval, rejected or "
             "approved) is deleted when nothing happened to it for this number of days.")

    @api.constrains("dwo_mail_retention_days")
    def _check_dwo_mail_retention_days(self):
        for settings in self:
            if settings.dwo_mail_retention_days < 1:
                raise ValidationError(self.env._("Keep the emails at least one day."))
