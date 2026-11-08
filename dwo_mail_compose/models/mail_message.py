# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.addons.mail.tools.discuss import Store


class MailMessage(models.Model):
    _inherit = "mail.message"

    dwo_is_official_email = fields.Boolean(
        "Official Email",
        copy=False,
        index="btree_not_null",
        help="Set when the message was sent with the Send email button. It tells an official "
             "email apart from an internal discussion message.",
    )
    outgoing_email_cc = fields.Char(
        "Outgoing Emails Cc",
        copy=False,
        groups="base.group_user",
        help="Carbon copy recipients of the outgoing official email.",
    )

    def _to_store_defaults(self, target):
        fields_ = super()._to_store_defaults(target)

        def internal(message):
            return target.is_internal(self.env)

        return fields_ + [
            "dwo_is_official_email",
            Store.Attr("outgoing_email_to", predicate=internal),
            Store.Attr("outgoing_email_cc", predicate=internal),
        ]
