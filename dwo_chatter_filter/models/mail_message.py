# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.osv import expression
from odoo.tools.query import Query

_logger = logging.getLogger(__name__)

def _not(domain):
    """The opposite of a domain (a list of leaves and operators)."""
    return ["!"] + expression.normalize_domain(domain)


# Every message is in exactly one of them. The order is the order of the checks.
CATEGORIES = ("tracking", "email", "activity", "note", "discussion", "other")
# The chips shown at most: each one costs a count when a record is opened
MAX_CHIPS = 15


class MailMessage(models.Model):
    _inherit = "mail.message"

    dwo_kind = fields.Selection(
        [("tracking", "Tracking"), ("email", "Email"), ("activity", "Activity"),
         ("note", "Note"), ("discussion", "Discussion"), ("other", "Other")],
        string="Kind of message", compute="_compute_dwo_kind", search="_search_dwo_kind",
        help="The kind of the message for the Chatter Quick Filter: every message is in exactly one kind. "
             "Used to filter, not stored.\nExample: email")

    def _compute_dwo_kind(self):
        found = {}
        for category in CATEGORIES:
            matches = self.sudo().search(expression.AND([[("id", "in", self.ids)], self._dwo_category_domain(category)]))
            for message_id in matches.ids:
                found.setdefault(message_id, category)
        for message in self:
            message.dwo_kind = found.get(message.id, False)

    def _search_dwo_kind(self, operator, value):
        if operator not in ("=", "!=", "in", "not in"):
            raise UserError(_("The kind of a message can only be compared with =, !=, in or not in."))
        # the ORM turns "=" into "in" and hands over any collection (an OrderedSet, for one)
        values = [value] if isinstance(value, (str, bool)) or value is None else list(value)
        domain = expression.OR([self._dwo_category_domain(kind) for kind in values if kind in CATEGORIES]) or [expression.FALSE_LEAF]
        return domain if operator in ("=", "in") else _not(domain)

    @api.model
    def _dwo_tracked_messages(self):
        """A query on the messages that carry tracking values, to be used as ``("id", "in", query)``.

        Odoo 16: a Query can only be selected on its id and ``subselect()`` returns a tuple, so the query
        of the tracking values is told to select ``mail_message_id`` instead."""
        query = self.env["mail.tracking.value"].sudo()._search([])
        subselect = Query.subselect
        query.subselect = lambda *args: subselect(query, '"mail_tracking_value"."mail_message_id"')
        return query

    @api.model
    def _dwo_category_domain(self, category):
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

                """
        mt_note = self.env.ref("mail.mt_note").id
        mt_comment = self.env.ref("mail.mt_comment").id
        # A message "carries tracking values" when a tracking value points to it. The field
        # tracking_value_ids is reserved to the administrators, so the test goes through the
        # tracking table itself, which is the same thing for every user.
        with_tracking = self._dwo_tracked_messages()
        tracking = [("id", "in", with_tracking)]
        email = expression.AND([[("message_type", "in", ["email"])], _not(tracking)])
        activity = expression.AND([[("subtype_id", "=", self.env.ref("mail.mt_activities").id)], _not(tracking), _not(email)])
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
    def _message_fetch(self, domain, *args, dwo_filter_id=None, **kwargs):
        """The chatter asks for the messages of one chip: the filter is applied by the server, so the
        pagination (Load more) works on the filtered list and not on what was already loaded. A chip that
        is gone, archived or broken filters nothing.

        Odoo 16 has no way to pass an extra parameter from the browser to here: the controller
        (see controllers/thread.py) puts the chip in the context."""
        dwo_filter_id = dwo_filter_id or self.env.context.get("dwo_filter_id")
        if dwo_filter_id:
            chip = self.env["dwo.chatter.filter"].browse(int(dwo_filter_id)).exists()
            if chip and chip.active:
                try:
                    chip_domain = chip._dwo_domain()
                    with self.env.cr.savepoint():
                        self.search_count(chip_domain, limit=1)   # does the filter work at all?
                    domain = expression.AND([domain or [], chip_domain])
                except Exception:
                    _logger.warning("Chatter Quick Filter: the filter of %r is not valid", chip.name, exc_info=True)
        return super()._message_fetch(domain, *args, **kwargs)

    @api.model
    def dwo_filter_chips(self, res_model, res_id):
        """What the chatter shows above the messages of a record: the number of messages in all, and the
        chips (in their order) with the number of messages each one shows. A chip whose filter does not work
        (a field of a module that was removed) has no number; the others are not affected."""
        if not self.env.user._is_internal():
            raise AccessError(_("Only internal users can filter the messages."))
        record = self.env[res_model].browse(res_id)
        record.check_access_rights("read")
        record.check_access_rule("read")
        base = [("model", "=", res_model), ("res_id", "=", res_id), ("message_type", "!=", "user_notification")]
        chips = []
        for chip in self.env["dwo.chatter.filter"].search([], limit=MAX_CHIPS):
            try:
                with self.env.cr.savepoint():
                    count = self.search_count(expression.AND([base, chip._dwo_domain()]))
            except Exception:
                _logger.warning("Chatter Quick Filter: the filter of %r is not valid", chip.name, exc_info=True)
                count = None
            chips.append({"id": chip.id, "name": chip.name, "color": chip.color, "count": count})
        return {"all": self.search_count(base), "chips": chips}
