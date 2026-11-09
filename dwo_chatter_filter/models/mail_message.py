# -*- coding: utf-8 -*-
from odoo import _, api, models
from odoo.exceptions import AccessError, UserError
from odoo.osv import expression

# Every message is in exactly one of them. The order is the order of the checks.
CATEGORIES = ("tracking", "email", "activity", "note", "discussion", "other")


def _not(domain):
    """The opposite of a domain (a list of leaves and operators)."""
    return ["!"] + expression.normalize_domain(domain)


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model
    def _dwo_category_domain(self, category, res_model=None, res_id=None):
        """The domain of one kind of message. The kinds do not overlap: a message is looked at in this
        order, and the first kind that fits keeps it.

        1. tracking    : it carries tracking values (a field changed)
        2. email       : an email received or sent (``email``; Odoo 16 has no email_outgoing)
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
        mt_activities = self.env.ref("mail.mt_activities").id
        # A message "carries tracking values" when a tracking value points to it. The field
        # tracking_value_ids is reserved to the administrators, so the test goes through the
        # tracking table itself, which is the same thing for every user. Odoo 16 has no way to give a
        # subquery to a domain: the ids of the messages are read first, of the record when it is known.
        tracking = [("id", "in", self._dwo_tracked_ids(res_model, res_id))]
        email = expression.AND([[("message_type", "=", "email")], _not(tracking)])
        activity = expression.AND([[("subtype_id", "=", mt_activities)], _not(tracking), _not(email)])
        comment = expression.AND([[("message_type", "=", "comment")], _not(tracking)])
        note = expression.AND([comment, [("subtype_id", "=", mt_note)]])
        discussion = expression.AND([comment, [("subtype_id", "=", mt_comment)]])
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
            return _not(expression.OR([tracking, email, activity, note, discussion]))
        raise UserError(_("Unknown kind of message: %s") % category)

    @api.model
    def _dwo_tracked_ids(self, res_model=None, res_id=None):
        """The ids of the messages that carry tracking values, of one record when it is given."""
        tracking = self.env["mail.tracking.value"].sudo()
        if res_model and res_id:
            values = tracking.search([("mail_message_id.model", "=", res_model), ("mail_message_id.res_id", "=", res_id)])
            return values.mail_message_id.ids
        self.env.cr.execute("SELECT DISTINCT mail_message_id FROM mail_tracking_value WHERE mail_message_id IS NOT NULL")
        return [row[0] for row in self.env.cr.fetchall()]

    def message_format(self, *args, **kwargs):
        formatted = super().message_format(*args, **kwargs)
        # the browser sorts the messages by kind too (a message that arrives while a kind is chosen):
        # it needs to know the ones left by a done activity
        mt_activities = self.env["ir.model.data"].xmlid_to_res_id("mail.mt_activities")  # Odoo 14 name (15: _xmlid_to_res_id)
        subtype_by_id = {message.id: message.subtype_id.id for message in self.sudo()}
        for values in formatted:
            values["dwo_is_activity"] = subtype_by_id.get(values["id"]) == mt_activities
        return formatted

    @api.model
    def dwo_filter_ids(self, res_model, res_id, category):
        """The ids of the messages of one kind of a record, newest first. Odoo 12 shows the messages of the
        document by their ids (the field message_ids): the chatter keeps the ones of the chosen kind."""
        record = self.env[res_model].browse(res_id)
        record.check_access_rights("read")
        record.check_access_rule("read")
        domain = expression.AND([
            [("model", "=", res_model), ("res_id", "=", res_id)],
            self._dwo_category_domain(category, res_model, res_id),
        ])
        return self.search(domain).ids

    @api.model
    def dwo_filter_counts(self, res_model, res_id):
        """The number of messages of a record, in total and for each kind, for the badges."""
        # Odoo 14 has no res.users._is_internal (15)
        if not self.env.user.has_group("base.group_user"):
            raise AccessError(_("Only internal users can filter the messages."))
        record = self.env[res_model].browse(res_id)
        record.check_access_rights("read")
        record.check_access_rule("read")
        base = [("model", "=", res_model), ("res_id", "=", res_id)]
        counts = {"all": self.search_count(base)}
        for category in CATEGORIES:
            counts[category] = self.search_count(expression.AND([base, self._dwo_category_domain(category, res_model, res_id)]))
        return counts
