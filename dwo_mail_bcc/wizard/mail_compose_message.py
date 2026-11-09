# -*- coding: utf-8 -*-
import re

from odoo import _, fields, models, tools
from odoo.exceptions import UserError


def merge_addresses(*texts):
    """Several address lists as one 'Name <email>, ...', an address once (first wins)."""
    seen, unique = set(), []
    for formatted in tools.mail.email_split_and_format_normalize(",".join(text or "" for text in texts)):
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
        formatted = tools.mail.email_split_and_format_normalize(raw)
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
            if not wizard.subtype_is_log:
                wizard._dwo_check_reply_to()
        return super()._action_send_mail(auto_commit=auto_commit)

    def _prepare_mail_values(self, res_ids):
        """Template Bcc, rendered for each record, joins the Bcc typed in the composer. In mass
        mailing the Cc typed is the Cc of each email.

        Mass mailing already receives the rendered ``email_bcc`` from the template generation.
        In comment mode (Send message) the recipients are not rendered by the template, so the
        Bcc is added here as ``outgoing_email_bcc``. (By default core turns the Cc of a template
        into recipients, not into a Cc header; when it does keep one, the typed Cc is added to it.)
        """
        result = super()._prepare_mail_values(res_ids)
        if (self.composition_mode == "comment" and not self.subtype_is_log
                and self.template_id.email_bcc and self.template_id.model == self.model):
            rendered = self.template_id._render_field("email_bcc", list(result))
            for res_id, values in result.items():
                merged = merge_addresses(values.get("outgoing_email_bcc"), rendered.get(res_id))
                if merged:
                    values["outgoing_email_bcc"] = merged
        if self.composition_mode == "mass_mail" and not self.subtype_is_log:
            cc = self._dwo_get_cc()
            if cc:
                for values in result.values():
                    values["email_cc"] = merge_addresses(values.get("email_cc"), cc)
        return result

    def _prepare_mail_values_static(self):
        values = super()._prepare_mail_values_static()
        if self.subtype_is_log:
            return values
        bcc = self._dwo_get_bcc()
        if bcc:
            if self.composition_mode == "mass_mail":
                values["email_bcc"] = bcc
            else:
                values["outgoing_email_bcc"] = bcc
        cc = self._dwo_get_cc()
        if cc and self.composition_mode != "mass_mail":
            values["outgoing_email_cc"] = cc
        # Odoo 18 only forces a Reply-To for mass mailing and for models that are not threads: when
        # sending a message with a Reply-To typed here, it is given to the message, and the answers leave
        # the record (as Odoo 19 does by itself).
        reply_to = (self.reply_to or "").strip()
        if self.composition_mode == "comment" and reply_to:
            values["reply_to"] = reply_to
            values["reply_to_force_new"] = True
        return values
