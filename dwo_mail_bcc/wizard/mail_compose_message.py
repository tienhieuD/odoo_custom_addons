# -*- coding: utf-8 -*-
import re

from odoo import _, fields, models, tools
from odoo.exceptions import UserError

from ..models.mail_compat import split_and_format_normalize


def merge_addresses(*texts):
    """Several address lists as one 'Name <email>, ...', an address once (first wins)."""
    seen, unique = set(), []
    for formatted in split_and_format_normalize(",".join(text or "" for text in texts)):
        normalized = tools.mail.email_normalize(formatted)
        if normalized not in seen:
            seen.add(normalized)
            unique.append(formatted)
    return ", ".join(unique)


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    email_cc = fields.Char(
        "Cc",
        help="Carbon copy: these addresses receive the email and everybody can see them. "
             "Separate several addresses with commas.",
    )
    email_bcc = fields.Char(
        "Bcc",
        help="Blind carbon copy: these addresses receive the email but stay hidden "
             "from the other recipients. Separate several addresses with commas.",
    )

    def _dwo_clean_addresses(self, raw, label):
        """Return the cleaned list as 'Name <email>, ...' or False. Raise on junk."""
        raw = (raw or "").strip()
        if not raw:
            return False
        tokens = [token for token in re.split(r"[,;]", raw) if token.strip()]
        formatted = split_and_format_normalize(raw)
        if len(formatted) != len(tokens):
            raise UserError(_("Some %(label)s addresses are not valid emails: %(value)s", label=label, value=raw))
        return ", ".join(formatted)

    def _dwo_get_cc(self):
        """Return the cleaned Cc as 'Name <email>, ...' or False. Raise on junk."""
        self.ensure_one()
        return self._dwo_clean_addresses(self.email_cc, "Cc")

    def _dwo_get_bcc(self):
        """Return the cleaned Bcc as 'Name <email>, ...' or False. Raise on junk."""
        self.ensure_one()
        return self._dwo_clean_addresses(self.email_bcc, "Bcc")

    def _dwo_check_reply_to(self):
        """Replies go to one address. A value with placeholders is checked once rendered."""
        self.ensure_one()
        reply_to = (self.reply_to or "").strip()
        if not reply_to or "{{" in reply_to or "{%" in reply_to:
            return
        if len(tools.mail.email_split(reply_to)) != 1 or not tools.mail.email_normalize(reply_to):
            raise UserError(_("Reply-To must be one valid email address: %s", reply_to))

    def _action_send_mail(self, auto_commit=False):
        for wizard in self:
            # fail early, before anything is posted
            wizard._dwo_get_cc()
            wizard._dwo_get_bcc()
            if not wizard.is_log:
                wizard._dwo_check_reply_to()
        return super()._action_send_mail(auto_commit=auto_commit)

    def get_mail_values(self, res_ids):
        """Add the Cc, the Bcc and the Reply-To to the values of each message or mail.

        In Odoo 16 this is the one place where the composer builds the values: for a message they
        go to ``message_post`` (any field of the message is accepted), for a mass mailing they go to
        ``mail.mail``. The Bcc of the template, rendered for each record, joins the Bcc typed here.
        """
        result = super().get_mail_values(res_ids)
        if self.is_log:
            return result
        cc, bcc = self._dwo_get_cc(), self._dwo_get_bcc()
        template_bcc = {}
        if self.template_id.email_bcc and self.template_id.model == self.model:
            template_bcc = {
                res_id: values.get("email_bcc")
                for res_id, values in self.template_id.generate_email(list(res_ids), ["email_bcc"]).items()
            }
        reply_to = (self.reply_to or "").strip()
        for res_id, values in result.items():
            all_bcc = merge_addresses(bcc, template_bcc.get(res_id))
            if self.composition_mode == "mass_mail":
                # a mass mailing makes mail.mail: the Cc typed joins the Cc rendered by the template
                if cc:
                    values["email_cc"] = merge_addresses(values.get("email_cc"), cc)
                if all_bcc:
                    values["email_bcc"] = all_bcc
            else:
                if cc:
                    values["outgoing_email_cc"] = cc
                if all_bcc:
                    values["outgoing_email_bcc"] = all_bcc
                # Odoo 16 forces a Reply-To only for mass mailing and for models that are not threads:
                # when sending a message with a Reply-To typed here, the answers leave the record (as
                # Odoo 19 does by itself).
                if reply_to:
                    values["reply_to"] = reply_to
                    values["reply_to_force_new"] = True
        return result
