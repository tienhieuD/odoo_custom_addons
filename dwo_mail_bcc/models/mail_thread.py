# -*- coding: utf-8 -*-
from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_by_email_get_base_mail_values(self, message, recipients_data, additional_values=None):
        """Hand the message Bcc over to the notification emails.

        Every ``mail.mail`` created for the message gets the value here, and
        ``mail.mail.create`` keeps it on the first one only, so that Bcc
        recipients are never mailed twice. Bcc addresses are deliberately NOT
        added to ``recipients_data``: that list feeds the visible To header
        through ``X-Msg-To-Add``.
        """
        values = super()._notify_by_email_get_base_mail_values(
            message, recipients_data, additional_values=additional_values)
        bcc = message.sudo().outgoing_email_bcc
        if bcc:
            values["email_bcc"] = bcc
        # The Cc goes the same way: written in the headers of one email, so that its people get
        # one copy (``mail.mail.create`` keeps it on the first mail.mail of the message).
        cc = message.sudo().outgoing_email_cc
        if cc:
            values["email_cc"] = cc
        return values

    def _get_message_create_valid_field_names(self):
        # core restricts the fields accepted by message_post / message_notify to
        # an allow-list; the Cc and the Bcc must be part of it to be given to message_post
        return super()._get_message_create_valid_field_names() | {"outgoing_email_bcc", "outgoing_email_cc"}
