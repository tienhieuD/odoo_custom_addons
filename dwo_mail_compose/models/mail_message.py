# -*- coding: utf-8 -*-
from odoo import fields, models, tools


class MailMessage(models.Model):
    _inherit = "mail.message"

    dwo_is_from_compose = fields.Boolean(
        "Sent from Email Composer",
        copy=False,
        index="btree_not_null",
        help="Set when the message was sent with the Send email button of the Advanced Email "
             "Composer. It tells these emails apart from an internal discussion message.",
    )
    # outgoing_email_cc and outgoing_email_bcc come from dwo_mail_bcc (Email Cc Bcc Reply-To)

    dwo_incoming_email_to_all = fields.Text(
        "Incoming Emails To (all)",
        copy=False,
        groups="base.group_user",
        help="The To of an email received, with the aliases of the system (catchall, alias of the "
             "record) that the core leaves out of incoming_email_to.",
    )

    # Odoo 19 has these two in core; Odoo 18 does not, so the module keeps them (the To and Cc of an
    # email received) under the same names.
    outgoing_email_to = fields.Char("Emails To (outgoing)", copy=False, groups="base.group_user")
    incoming_email_to = fields.Text("Emails To", copy=False, groups="base.group_user")
    incoming_email_cc = fields.Char("Emails Cc", copy=False, groups="base.group_user")

    def _to_store(self, store, *args, **kwargs):
        super()._to_store(store, *args, **kwargs)
        internal = self.env.user._is_internal()
        for message in self:
            values = {"dwo_is_from_compose": message.dwo_is_from_compose}
            if internal:
                sudo = message.sudo()
                values.update({
                    "dwo_incoming_email_to_all": tools.mail.email_split_tuples(sudo.dwo_incoming_email_to_all or ""),
                    "incoming_email_to": tools.mail.email_split_tuples(sudo.incoming_email_to or ""),
                    "incoming_email_cc": tools.mail.email_split_tuples(sudo.incoming_email_cc or ""),
                    "outgoing_email_to": sudo.outgoing_email_to or "",
                    "outgoing_email_cc": sudo.outgoing_email_cc or "",
                })
            store.add(message, values)
