# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .expression import check_expression, eval_expression


class DwoApprovalApprover(models.Model):
    _name = "dwo.approval.approver"
    _description = "Approval Flow Approver"
    _order = "sequence, id"

    transition_id = fields.Many2one("dwo.approval.transition", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    kind = fields.Selection([
        ("users", "Specific users"),
        ("group", "A group"),
        ("dept", "Same department as the document"),
        ("field", "User named on the document"),
        ("expr", "An expression"),
    ], required=True, default="users")
    user_ids = fields.Many2many("res.users", string="Users")
    group_id = fields.Many2one("res.groups", string="Group")
    value = fields.Char(help="Field name (kind: field) or expression (kind: expr).")

    @api.constrains("kind", "value", "user_ids", "group_id")
    def _check_approver(self):
        for line in self:
            model = line.transition_id.flow_id.model_name
            if line.kind == "users" and not line.user_ids:
                raise ValidationError(_("Pick at least one user."))
            if line.kind == "group" and not line.group_id:
                raise ValidationError(_("Pick a group."))
            if line.kind == "expr":
                message = check_expression(self.env, model, line.value)
                if message:
                    raise ValidationError(message)
            if line.kind == "field":
                field = self.env[model]._fields.get(line.value or "")
                if not field or field.comodel_name != "res.users":
                    raise ValidationError(_(
                        'Field "%s" must be a user field of the document.', line.value or ""))

    def _matches(self, record, user):
        """True when ``user`` is one of the people this line stands for."""
        self.ensure_one()
        user = user.sudo()
        if self.kind == "users":
            return user in self.user_ids
        if self.kind == "group":
            return self.group_id in user.groups_id
        if self.kind == "dept":
            rec = record.sudo()
            if "department_id" not in rec._fields or "employee_id" not in user._fields:
                return False
            return bool(rec.department_id) and rec.department_id in user.employee_ids.department_id
        if self.kind == "field":
            return user.id in eval_expression(record, user, "record." + (self.value or "id"))
        return user.id in eval_expression(record, user, self.value)

    def _label(self):
        self.ensure_one()
        if self.kind == "users":
            return ", ".join(self.user_ids.mapped("name"))
        if self.kind == "group":
            return self.group_id.display_name or ""
        if self.kind == "dept":
            return _("Same department as the document")
        return self.value or ""
