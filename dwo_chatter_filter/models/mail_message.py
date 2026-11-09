# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.exceptions import AccessError, UserError
from odoo.fields import Domain
from odoo.addons.mail.tools.discuss import Store

# Every message is in exactly one of them. The order is the order of the checks.
CATEGORIES = ("tracking", "email", "activity", "note", "discussion", "other")


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model
    def _dwo_category_domain(self, category):
        """The domain of one kind of message. The kinds do not overlap: a message is looked at in this
        order, and the first kind that fits keeps it.

        1. tracking    : a field changed (``message_type`` is ``tracking``)
        2. email       : an email received or sent (``email``, ``email_outgoing``)
        3. activity    : the message left when a planned activity is marked as done (subtype Activities)
        4. note        : a comment with the subtype Note (Log note)
        5. discussion  : a comment with the subtype Discussions (Send message, whoever receives it:
                         internal followers or customers linked to the record)
        6. other       : everything else (automatic messages, notifications without tracking, custom
                         subtypes)

        The same rule is written in JavaScript (``dwoCategoryOf``): keep them equal.
        """
        mt_note = self.env.ref("mail.mt_note").id
        mt_comment = self.env.ref("mail.mt_comment").id
        # Odoo 20 gives the messages of a changed field their own type
        tracking = Domain("message_type", "=", "tracking")
        email = Domain("message_type", "in", ["email", "email_outgoing"]) & ~tracking
        comment = Domain("message_type", "=", "comment") & ~tracking
        activity = Domain("subtype_id", "=", self.env.ref("mail.mt_activities").id) & ~tracking & ~email
        note = comment & Domain("subtype_id", "=", mt_note)
        discussion = comment & Domain("subtype_id", "=", mt_comment)
        if category == "tracking":
            return tracking
        if category == "email":
            return email
        if category == "activity":
            return activity
        if category == "note":
            return note
        if category == "discussion":
            return discussion
        if category == "other":
            return ~(tracking | email | activity | note | discussion)
        raise UserError(self.env._("Unknown kind of message: %s", category))

    def _store_extra_fields(self, res, *, format_reply):
        super()._store_extra_fields(res, format_reply=format_reply)
        # the browser sorts the messages by kind too (a message that arrives while a kind is chosen):
        # it needs to know the ones left by a done activity, the store has no id for that subtype
        res.attr(
            "dwo_is_activity",
            lambda m: m.sudo().subtype_id.id == m.env.ref("mail.mt_activities").id,
        )

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
