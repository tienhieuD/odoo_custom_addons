# -*- coding: utf-8 -*-
from odoo import fields, models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    email_bcc = fields.Char(
        "Bcc",
        help="Blind carbon copy recipients (placeholders may be used here). They receive the "
             "email, but their addresses are never shown to the other recipients.",
    )

    def _get_dynamic_field_names(self):
        return super()._get_dynamic_field_names() | {"email_bcc"}

    def _generate_template(self, res_ids, render_fields, recipients_allow_suggested=False,
                           find_or_create_partners=False):
        """Render the Bcc whenever the recipients are rendered.

        Core renders every requested field that is not "specific" through
        ``_render_field``, so adding ``email_bcc`` to the requested fields is
        enough: ``send_mail`` and mass mailing then receive a rendered ``email_bcc``
        and create ``mail.mail`` with it.
        """
        render_fields = set(render_fields)
        if "email_cc" in render_fields:
            render_fields.add("email_bcc")
        return super()._generate_template(
            res_ids, render_fields,
            recipients_allow_suggested=recipients_allow_suggested,
            find_or_create_partners=find_or_create_partners,
        )
