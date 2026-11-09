# -*- coding: utf-8 -*-
from odoo import api, fields, models

from .mail_compat import split_and_format_normalize


class MailMail(models.Model):
    _inherit = "mail.mail"

    email_bcc = fields.Char(
        "Bcc",
        help="Blind carbon copy recipients. They get the email, but their "
             "addresses are never written in the headers sent to others.",
    )

    @api.model
    def create(self, values):
        # One message can produce several mail.mail (one per recipient group, per chunk of partners,
        # plus the email-only one). Odoo 12 creates them in ``res.partner._notify`` with no hook for
        # extra values, so the Cc and the Bcc typed with the composer, stored on the message, are
        # added here. Only the first mail.mail of a message keeps them: the Bcc recipients are mailed
        # exactly once, and the Cc people do not get one copy per recipient either. Copies made by
        # the core throttling (``copy()`` with the same mail_message_id) follow the same rule.
        message_id = values.get("mail_message_id")
        if message_id:
            values = dict(values)
            message = self.env["mail.message"].sudo().browse(message_id)
            for name, stored in (("email_bcc", "outgoing_email_bcc"), ("email_cc", "outgoing_email_cc")):
                if not values.get(name) and message[stored]:
                    values[name] = message[stored]
                if values.get(name) and self.sudo().search([
                    ("mail_message_id", "=", message_id),
                    (name, "!=", False),
                ], limit=1):
                    values[name] = False
        return super(MailMail, self).create(values)

    def _send(self, *args, **kwargs):
        """Give the Bcc and the Cc to exactly one email of each mail.mail.

        Core sends one SMTP email per partner plus one for the raw email addresses, and writes the
        Cc of the mail in every one of them. ``IrMailServer.build_email`` (see ir_mail_server.py)
        adds the Bcc to the first email of a mail and drops the Cc from the next ones; the
        information is handed over through the cursor, keyed by the Message-Id of the mail.
        A Bcc travels in the ``Bcc`` header, which core strips after computing the SMTP
        recipients, so nobody sees it.

        A mail.mail with only Bcc addresses and no To, Cc or partner is not sent: core builds no
        email for it.
        """
        pool = {}
        for mail in self:
            if (mail.email_bcc or mail.email_cc) and mail.message_id:
                pool[mail.message_id] = {
                    "bcc": split_and_format_normalize(mail.email_bcc),
                    "has_cc": bool(mail.email_cc),
                    "built": 0,
                }
        if not pool:
            return super()._send(*args, **kwargs)
        cr = self.env.cr
        previous = getattr(cr, "dwo_mail_pool", None)
        cr.dwo_mail_pool = dict(previous or {}, **pool)
        try:
            return super()._send(*args, **kwargs)
        finally:
            cr.dwo_mail_pool = previous
