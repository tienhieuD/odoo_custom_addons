# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.osv import expression

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
            checked = self.sudo().with_context(dwo_message_ids=self.ids)
            matches = checked.search(expression.AND([[("id", "in", self.ids)], checked._dwo_category_domain(category)]))
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
        """The ids of the messages that carry tracking values, to be used as ``("id", "in", ids)``.

        Odoo 13 has no way to give a subquery to a domain (no Query in a leaf, and the internal ``inselect``
        operator is refused in a domain that comes from a search method), so the ids are read first, and only
        the ones that matter: those of the messages being computed, or of the record being looked at (the
        context ``dwo_record``, set where the record is known). Without either, all of them."""
        tracking = self.env["mail.tracking.value"].sudo()
        ids = self.env.context.get("dwo_message_ids")
        record = self.env.context.get("dwo_record")
        if ids is not None:
            values = tracking.search([("mail_message_id", "in", list(ids))])
        elif record:
            values = tracking.search([("mail_message_id.model", "=", record[0]), ("mail_message_id.res_id", "=", record[1])])
        else:
            self.env.cr.execute("SELECT DISTINCT mail_message_id FROM mail_tracking_value WHERE mail_message_id IS NOT NULL")
            return [row[0] for row in self.env.cr.fetchall()]
        return values.mapped("mail_message_id").ids

    @api.model
    def _dwo_category_domain(self, category):
        """The domain of one kind of message. The kinds do not overlap: a message is looked at in this
        order, and the first kind that fits keeps it.

        1. tracking    : it carries tracking values (a field changed)
        2. email       : an email received or sent (``email``; Odoo 13 has no email_outgoing)
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
    def dwo_filter_ids(self, res_model, res_id, chip_id):
        """The ids of the messages of one chip of a record, newest first. Odoo 13 shows the messages of the
        document by their ids (the field message_ids): the chatter keeps the ones of the chosen chip.
        False when the chip is gone, archived or broken: the chatter then shows every message."""
        record = self.env[res_model].browse(res_id)
        record.check_access_rights("read")
        record.check_access_rule("read")
        chip = self.env["dwo.chatter.filter"].browse(int(chip_id)).exists()
        if not chip or not chip.active:
            return False
        try:
            chip_domain = chip._dwo_domain()
            with self.env.cr.savepoint():
                return self.with_context(dwo_record=(res_model, res_id)).search(expression.AND([
                    [("model", "=", res_model), ("res_id", "=", res_id), ("message_type", "!=", "user_notification")],
                    chip_domain])).ids
        except Exception:
            _logger.warning("Chatter Quick Filter: the filter of %r is not valid", chip.name, exc_info=True)
            return False

    @api.model
    def dwo_filter_chips(self, res_model, res_id):
        """What the chatter shows above the messages of a record: the number of messages in all, and the
        chips (in their order) with the number of messages each one shows. A chip whose filter does not work
        (a field of a module that was removed) has no number; the others are not affected."""
        # Odoo 13 has no res.users._is_internal (15)
        if not self.env.user.has_group("base.group_user"):
            raise AccessError(_("Only internal users can filter the messages."))
        record = self.env[res_model].browse(res_id)
        record.check_access_rights("read")
        record.check_access_rule("read")
        base = [("model", "=", res_model), ("res_id", "=", res_id), ("message_type", "!=", "user_notification")]
        scoped = self.with_context(dwo_record=(res_model, res_id))
        chips = []
        for chip in self.env["dwo.chatter.filter"].search([], limit=MAX_CHIPS):
            try:
                with self.env.cr.savepoint():
                    count = scoped.search_count(expression.AND([base, chip._dwo_domain()]))
            except Exception:
                _logger.warning("Chatter Quick Filter: the filter of %r is not valid", chip.name, exc_info=True)
                count = None
            chips.append({"id": chip.id, "name": chip.name, "color": chip.color, "count": count})
        return {"all": self.search_count(base), "chips": chips}
