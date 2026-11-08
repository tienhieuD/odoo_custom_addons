# -*- coding: utf-8 -*-
from odoo import api, models, tools
from odoo.tools.mail import decode_message_header


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _get_message_create_valid_field_names(self):
        return super()._get_message_create_valid_field_names() | {
            "dwo_is_from_compose",
            "outgoing_email_cc",
            "dwo_incoming_email_to_all",
        }

    @api.model
    def message_parse(self, message, save_original=False):
        """Keep the To header as it was received, in the order it was written. The core stores
        only the To without the aliases (``to_filtered``), so an email sent to the catchall or to
        the alias of the record would show no To at all; and it builds that list from a set, so
        the order is lost. ``Delivered-To`` (the envelope recipient, often the catchall) comes
        after the addresses of the To header, and an address is kept once."""
        msg_dict = super().message_parse(message, save_original=save_original)
        addresses = []
        for header in ("To", "Delivered-To"):
            value = decode_message_header(message, header, separator=",")
            addresses += tools.mail.email_split_tuples(value) if value else []
        unique = {}
        for name, email in addresses:
            key = tools.email_normalize(email) or email.lower()
            if key not in unique or (name and not unique[key][0]):
                unique[key] = (name, email)
        msg_dict["dwo_incoming_email_to_all"] = ", ".join(
            tools.formataddr(pair) if pair[0] else pair[1] for pair in unique.values()) or False
        return msg_dict

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
