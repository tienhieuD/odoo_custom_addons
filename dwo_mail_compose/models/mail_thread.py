# -*- coding: utf-8 -*-
from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _get_message_create_valid_field_names(self):
        return super()._get_message_create_valid_field_names() | {
            "dwo_is_official_email",
            "outgoing_email_cc",
        }

    def _notify_by_email_get_base_mail_values(self, message, recipients_data, additional_values=None):
        """Official emails carry a real Cc: it goes to the mail.mail so the header is written.

        Cc is only supported for the single email-only mail.mail that Send email
        produces. It is not deduplicated across several mail.mail (unlike Bcc).
        """
        values = super()._notify_by_email_get_base_mail_values(
            message, recipients_data, additional_values=additional_values)
        cc = message.sudo().outgoing_email_cc
        if cc:
            values["email_cc"] = cc
        return values
