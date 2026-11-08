# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.exceptions import AccessError, UserError
from odoo.fields import Domain

# Every message is in exactly one of them. The order is the order of the checks.
CATEGORIES = ("tracking", "email", "note", "discussion", "other")


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model
    def _dwo_category_domain(self, category):
        """The domain of one kind of message. The kinds do not overlap: a message is looked at in this
        order, and the first kind that fits keeps it.

        1. tracking    : it carries tracking values (a field changed)
        2. email       : an email received or sent (``email``, ``email_outgoing``)
        3. note        : a comment with the subtype Note (Log note)
        4. discussion  : a comment with the subtype Discussions (Send message, whoever receives it:
                         internal followers or customers linked to the record)
        5. other       : everything else (automatic messages, notifications without tracking, custom
                         subtypes)

        The same rule is written in JavaScript (``dwoCategoryOf``): keep them equal.
        """
        mt_note = self.env.ref("mail.mt_note").id
        mt_comment = self.env.ref("mail.mt_comment").id
        # A message "carries tracking values" when a tracking value points to it. The field
        # tracking_value_ids is reserved to the administrators, so the test goes through the
        # tracking table itself, which is the same thing for every user.
        with_tracking = self.env["mail.tracking.value"].sudo()._search([]).subselect("mail_message_id")
        tracking = Domain("id", "in", with_tracking)
        email = Domain("message_type", "in", ["email", "email_outgoing"]) & ~tracking
        comment = Domain("message_type", "=", "comment") & ~tracking
        note = comment & Domain("subtype_id", "=", mt_note)
        discussion = comment & Domain("subtype_id", "=", mt_comment)
        if category == "tracking":
            return tracking
        if category == "email":
            return email
        if category == "note":
            return note
        if category == "discussion":
            return discussion
        if category == "other":
            return ~(tracking | email | note | discussion)
        raise UserError(self.env._("Unknown kind of message: %s", category))

    @api.model
    def _message_fetch(self, domain, *, dwo_category=None, **kwargs):
        """The chatter asks for one kind of message: the filter is applied by the server, so the
        pagination (Load more) works on the filtered list and not on what was already loaded."""
        if dwo_category:
            domain = Domain(True if domain is None else domain) & self._dwo_category_domain(dwo_category)
        return super()._message_fetch(domain, **kwargs)

    @api.model
    def dwo_filter_counts(self, res_model, res_id):
        """The number of messages of a record, in total and for each kind, for the badges."""
        if not self.env.user._is_internal():
            raise AccessError(self.env._("Only internal users can filter the messages."))
        self.env[res_model].browse(res_id).check_access("read")
        base = (Domain("model", "=", res_model) & Domain("res_id", "=", res_id)
                & Domain("message_type", "!=", "user_notification"))
        counts = {"all": self.search_count(base)}
        for category in CATEGORIES:
            counts[category] = self.search_count(base & self._dwo_category_domain(category))
        return counts
