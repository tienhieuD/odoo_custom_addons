# -*- coding: utf-8 -*-
from odoo import fields, models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    email_bcc = fields.Char(
        "Bcc",
        help="Blind carbon copy recipients (placeholders may be used here). They receive the "
             "email, but their addresses are never shown to the other recipients.",
    )

    def generate_email(self, res_ids, fields=None):
        """Render the Bcc whenever the recipients are rendered.

        Core renders every requested field through ``_render_field``, so adding ``email_bcc`` to
        the requested fields is enough: ``send_mail`` then creates the ``mail.mail`` with the
        rendered ``email_bcc``.
        """
        if fields is None:
            fields = ["subject", "body_html", "email_from", "email_to", "partner_to", "email_cc", "reply_to",
                      "scheduled_date"]
        if "email_cc" in fields and "email_bcc" not in fields:
            fields = list(fields) + ["email_bcc"]
        return super().generate_email(res_ids, fields)
