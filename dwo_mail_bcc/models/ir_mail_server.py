# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.tools import mail as mail_tools

from .mail_compat import normalize_all


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    @api.model
    def build_email(self, *args, **kwargs):
        """The first email built for a mail.mail carries its Bcc; the next ones lose its Cc.

        ``mail.mail._send`` (see mail_mail.py) calls this with keyword arguments, including the
        ``message_id`` of the mail, which tells which mail it is.
        """
        pool = getattr(self.env.cr, "dwo_mail_pool", None)
        entry = pool.get(kwargs.get("message_id")) if pool else None
        if entry:
            if entry["built"] == 0:
                visible = set(normalize_all(kwargs.get("email_to")) + normalize_all(kwargs.get("email_cc")))
                bcc = [
                    formatted for formatted in entry["bcc"]
                    if all(address not in visible for address in normalize_all(formatted))
                ]
                if bcc:
                    kwargs["email_bcc"] = list(kwargs.get("email_bcc") or []) + bcc
            elif entry["has_cc"]:
                kwargs["email_cc"] = []
            entry["built"] += 1
        return super().build_email(*args, **kwargs)

    def send_email(self, message, *args, **kwargs):
        """Core lets only the pre-validated addresses (To and Cc) into the SMTP envelope: the hidden
        Bcc addresses are validated by ``mail.mail`` too, so they are added to that list."""
        validated = self.env.context.get("send_validated_to")
        bcc = message["Bcc"]
        if validated and bcc:
            extra = [a for a in mail_tools.email_normalize_all(str(bcc)) if a not in validated]
            if extra:
                self = self.with_context(send_validated_to=list(validated) + extra)
        return super(IrMailServer, self).send_email(message, *args, **kwargs)
