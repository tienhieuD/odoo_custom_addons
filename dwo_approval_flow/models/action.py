# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .expression import check_expression, eval_expression

_logger = logging.getLogger(__name__)


class DwoApprovalAction(models.Model):
    _name = "dwo.approval.action"
    _description = "Approval Flow Action"
    _order = "sequence, id"

    transition_id = fields.Many2one("dwo.approval.transition", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    kind = fields.Selection([
        ("notify", "Notify in chatter"),
        ("email", "Send an email"),
        ("update", "Update a field"),
        ("server", "Run a server action"),
    ], required=True, default="notify")
    recipient_user_ids = fields.Many2many("res.users", string="To")
    recipient_expr = fields.Char(string="To (expression)")
    message = fields.Text(translate=True)
    template_id = fields.Many2one("mail.template", string="Email template")
    field_name = fields.Char(string="Field to update")
    value = fields.Char(string="New value", help="Text, number, id or true/false. {user} is the user who pressed.")
    server_action_id = fields.Many2one("ir.actions.server", ondelete="set null")

    @api.constrains("kind", "recipient_expr", "field_name")
    def _check_action(self):
        for action in self:
            model = action.transition_id.flow_id.model_name
            if action.recipient_expr:
                message = check_expression(self.env, model, action.recipient_expr)
                if message:
                    raise ValidationError(message)
            if action.kind == "update" and action.field_name not in self.env[model]._fields:
                raise ValidationError(_('Field "%s" does not exist.', action.field_name or ""))

    def _run(self, record, user):
        self.ensure_one()
        if self.kind == "update":
            return self._run_update(record, user)
        if self.kind == "server":
            if self.server_action_id:
                self.server_action_id.sudo().with_context(
                    active_model=record._name, active_id=record.id, active_ids=record.ids).run()
            return None
        if not hasattr(record, "message_post"):
            _logger.info("Approval action skipped: %s has no chatter.", record._name)
            return None
        partners = self.recipient_user_ids.partner_id
        if self.recipient_expr:
            ids = eval_expression(record, user, self.recipient_expr)
            partners |= self.env["res.users"].sudo().browse(sorted(ids)).partner_id
        if self.kind == "email" and self.template_id:
            self.template_id.sudo().send_mail(record.id, force_send=False)
            return None
        record.sudo().message_post(
            body=self.message or "",
            partner_ids=partners.ids,
            message_type="comment" if self.kind == "email" else "notification",
            subtype_xmlid="mail.mt_comment" if self.kind == "email" else "mail.mt_note",
            author_id=user.partner_id.id,
        )
        return None

    def _run_update(self, record, user):
        field = record._fields[self.field_name]
        raw = (self.value or "").strip()
        if raw == "{user}" and field.type == "many2one":
            value = user.id
        elif field.type in ("char", "text", "html"):
            value = raw.replace("{user}", user.name)
        elif field.type in ("integer", "many2one"):
            value = int(raw) if raw else False
        elif field.type in ("float", "monetary"):
            value = float(raw or 0)
        elif field.type == "boolean":
            value = raw.lower() in ("1", "true", "yes")
        else:
            value = raw
        record.sudo().write({self.field_name: value})
