# -*- coding: utf-8 -*-
from odoo import fields, models, tools
from odoo.addons.mail.tools.discuss import Store


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

    def _to_store_defaults(self, target):
        fields_ = super()._to_store_defaults(target)

        def internal(message):
            return target.is_internal(self.env)

        return fields_ + [
            "dwo_is_from_compose",
            Store.Attr(
                "dwo_incoming_email_to_all",
                lambda message: tools.mail.email_split_tuples(message.dwo_incoming_email_to_all or ""),
                predicate=internal,
            ),
            Store.Attr("outgoing_email_to", predicate=internal),
            Store.Attr("outgoing_email_cc", predicate=internal),
        ]
