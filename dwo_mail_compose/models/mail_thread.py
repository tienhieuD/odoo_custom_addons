# -*- coding: utf-8 -*-
from odoo import api, models, tools
from odoo.tools.mail import decode_message_header


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _get_message_create_valid_field_names(self):
        return super()._get_message_create_valid_field_names() | {
            "dwo_is_from_compose",
            "dwo_incoming_email_to_all",
            "outgoing_email_to",
            "incoming_email_to",
            "incoming_email_cc",
        }

    def _notify_compute_recipients(self, message, msg_vals):
        """Odoo 13 computes the recipients here (16 and later: _notify_get_recipients, 15: a list): the email
        of the composer is sent by the module itself, the core notifies nobody. Odoo 13 wants a dict."""
        if self.env.context.get("dwo_no_core_notification"):
            return {"partners": [], "channels": []}
        return super()._notify_compute_recipients(message, msg_vals)

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
        # Odoo 19 stores these two in core; here the module does
        msg_dict["incoming_email_to"] = msg_dict.get("to") or False
        msg_dict["incoming_email_cc"] = msg_dict.get("cc") or False
        return msg_dict
