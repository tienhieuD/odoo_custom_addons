# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class MailMail(models.Model):
    _inherit = "mail.mail"

    email_bcc = fields.Char(
        "Bcc",
        help="Blind carbon copy recipients. They get the email, but their "
             "addresses are never written in the headers sent to others.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        # One message can produce several mail.mail (one per recipient group,
        # per chunk of partners, plus the email-only one). Bcc recipients must
        # be mailed exactly once, so only the first mail.mail of a message keeps
        # the value. Copies made by the core throttling (``copy()`` with the same
        # mail_message_id) are covered by the same rule: the original keeps it.
        if any(vals.get("email_bcc") and vals.get("mail_message_id") for vals in vals_list):
            vals_list = [dict(vals) for vals in vals_list]
            seen_message_ids = set()
            for vals in vals_list:
                message_id = vals.get("mail_message_id")
                if not (vals.get("email_bcc") and message_id):
                    continue
                if message_id in seen_message_ids or self.sudo().search_count([
                    ("mail_message_id", "=", message_id),
                    ("email_bcc", "!=", False),
                ], limit=1):
                    vals["email_bcc"] = False
                else:
                    seen_message_ids.add(message_id)
        return super().create(vals_list)

    def _prepare_outgoing_list(self, mail_server=False, doc_to_followers=None):
        """Attach the Bcc to exactly one outgoing email of this mail.mail.

        Core sends one SMTP email per partner plus one for the raw email
        addresses. The Bcc rides on the first one. It travels in the ``Bcc``
        header (the core builder copies ``headers`` verbatim), and core strips that
        header after computing the SMTP envelope, so nobody sees it.

        A mail.mail with only Bcc addresses and no To, Cc or partner is not
        sent: core builds no email for it.
        """
        email_list = super()._prepare_outgoing_list(
            mail_server=mail_server, doc_to_followers=doc_to_followers)
        if not (self.email_bcc and email_list):
            return email_list
        visible = set()
        for entry in email_list:
            visible.update(entry["email_to_normalized"])
        bcc_formatted = []
        bcc_normalized = []
        for formatted in tools.mail.email_split_and_format_normalize(self.email_bcc):
            normalized = tools.mail.email_normalize(formatted)
            if normalized and normalized not in visible and normalized not in bcc_normalized:
                bcc_formatted.append(formatted)
                bcc_normalized.append(normalized)
        if not bcc_formatted:
            return email_list
        carrier = email_list[0]
        # the headers dict is shared by all entries: copy it for the carrier only
        carrier["headers"] = dict(carrier["headers"], Bcc=", ".join(bcc_formatted))
        # 'send_validated_to' filters the SMTP recipients: Bcc must be listed
        carrier["email_to_normalized"] = list(carrier["email_to_normalized"]) + bcc_normalized
        return email_list
