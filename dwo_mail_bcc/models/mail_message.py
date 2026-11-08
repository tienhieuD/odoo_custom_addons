# -*- coding: utf-8 -*-
from odoo import fields, models


class MailMessage(models.Model):
    _inherit = "mail.message"

    # Kept readable by internal users only: a Bcc list is confidential, so it
    # must never reach portal or public chatter payloads.
    outgoing_email_bcc = fields.Char(
        "Outgoing Emails Bcc",
        copy=False,
        groups="base.group_user",
        help="Blind carbon copy recipients of the outgoing email. They receive the "
             "email but are hidden from every other recipient.",
    )
