# -*- coding: utf-8 -*-
from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_by_email_add_values(self, base_mail_values):
        """Hand the message Cc and Bcc over to the notification emails.

        Every ``mail.mail`` created for the message gets the values here, and
        ``mail.mail.create`` keeps them on the first one only, so that Cc and Bcc
        recipients are never mailed twice. Bcc addresses are deliberately NOT
        added to the recipients: they would then show in the To header.
        """
        values = super()._notify_by_email_add_values(base_mail_values)
        message = self.env["mail.message"].sudo().browse(values.get("mail_message_id"))
        if message.outgoing_email_bcc:
            values["email_bcc"] = message.outgoing_email_bcc
        if message.outgoing_email_cc:
            values["email_cc"] = message.outgoing_email_cc
        return values
