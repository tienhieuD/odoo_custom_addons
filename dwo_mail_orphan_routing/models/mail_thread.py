# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def message_route(self, message, message_dict, model=None, thread_id=None, custom_values=None):
        """Keep the incoming emails that Odoo cannot route.

        Odoo raises ValueError when no route exists (the mail gateway then refuses the email), or answers with a
        bounce and returns no route (catch-all). Both cases are stored as orphan emails; the standard bounce still goes
        out. Anything unexpected keeps the standard behaviour."""
        Orphan = self.env["dwo.mail.orphan"].sudo()
        if not Orphan._capture_enabled():
            return super().message_route(message, message_dict, model, thread_id, custom_values)
        try:
            routes = super().message_route(message, message_dict, model, thread_id, custom_values)
        except ValueError as exc:
            if Orphan._capture(message, message_dict, Orphan._short_reason(exc)):
                return []
            raise
        if not routes and not message_dict.get("is_bounce"):
            Orphan._capture(message, message_dict, "Rejected by the catch-all or by the contact rules of the alias")
        return routes
