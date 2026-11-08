# -*- coding: utf-8 -*-
import re

from odoo import _, fields, models, tools
from odoo.exceptions import UserError


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    email_bcc = fields.Char(
        "Bcc",
        help="Blind carbon copy: these addresses receive the email but stay hidden "
             "from the other recipients. Separate several addresses with commas.",
    )

    def _dwo_get_bcc(self):
        """Return the cleaned Bcc as 'Name <email>, ...' or False. Raise on junk."""
        self.ensure_one()
        raw = (self.email_bcc or "").strip()
        if not raw:
            return False
        tokens = [token for token in re.split(r"[,;]", raw) if token.strip()]
        formatted = tools.mail.email_split_and_format_normalize(raw)
        if len(formatted) != len(tokens):
            raise UserError(_("Some Bcc addresses are not valid emails: %s", raw))
        return ", ".join(formatted)

    def _action_send_mail(self, auto_commit=False):
        for wizard in self:
            wizard._dwo_get_bcc()  # fail early, before anything is posted
        return super()._action_send_mail(auto_commit=auto_commit)

    def _prepare_mail_values(self, res_ids):
        """Template Bcc, rendered for each record, joins the Bcc typed in the composer.

        Mass mailing already receives the rendered ``email_bcc`` from the template
        generation. In comment mode (Send message) the recipients are not rendered
        by the template, so the Bcc is added here as ``outgoing_email_bcc``.
        """
        result = super()._prepare_mail_values(res_ids)
        if (self.composition_mode == "comment" and not self.subtype_is_log
                and self.template_id.email_bcc and self.template_id.model == self.model):
            rendered = self.template_id._render_field("email_bcc", list(result))
            for res_id, values in result.items():
                merged = tools.mail.email_split_and_format_normalize(
                    f"{values.get('outgoing_email_bcc') or ''},{rendered.get(res_id) or ''}")
                seen, unique = set(), []
                for formatted in merged:
                    normalized = tools.mail.email_normalize(formatted)
                    if normalized not in seen:
                        seen.add(normalized)
                        unique.append(formatted)
                if unique:
                    values["outgoing_email_bcc"] = ", ".join(unique)
        return result

    def _prepare_mail_values_static(self):
        values = super()._prepare_mail_values_static()
        bcc = self._dwo_get_bcc()
        if bcc and not self.subtype_is_log:
            if self.composition_mode == "mass_mail":
                values["email_bcc"] = bcc
            else:
                values["outgoing_email_bcc"] = bcc
        return values
