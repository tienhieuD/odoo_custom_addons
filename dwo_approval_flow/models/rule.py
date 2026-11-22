# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class DwoApprovalRule(models.Model):
    _name = "dwo.approval.rule"
    _description = "Approval Flow Rule"
    _order = "sequence, id"

    transition_id = fields.Many2one("dwo.approval.transition", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    domain = fields.Char(required=True, default="[]", help="Odoo domain on the document. You can use `user`.")

    @api.constrains("domain")
    def _check_domain(self):
        for rule in self:
            try:
                value = safe_eval(rule.domain, self.env["ir.access"]._eval_context())
            except Exception as error:
                raise ValidationError(self.env._("Invalid domain: %s", error)) from error
            if not isinstance(value, (list, tuple)):
                raise ValidationError(self.env._("A domain must be a list."))

    def _holds(self, record, user):
        """True when the document satisfies the domain for ``user``."""
        self.ensure_one()
        context = self.with_user(user).env["ir.access"]._eval_context()
        domain = safe_eval(self.domain or "[]", context)
        return bool(record.sudo().filtered_domain(domain))
