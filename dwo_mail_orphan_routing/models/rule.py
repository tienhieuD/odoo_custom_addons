# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DwoMailOrphanRule(models.Model):
    _name = "dwo.mail.orphan.rule"
    _description = "Orphan mail rule"
    _order = "sequence, id"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    sender_contains = fields.Char("Sender contains")
    subject_contains = fields.Char("Subject contains")
    recipient_contains = fields.Char("Received at contains")
    action = fields.Selection([("route", "Route to a record"), ("ignore", "Ignore")], required=True, default="route")
    model_id = fields.Many2one("ir.model", "Target model", ondelete="cascade",
                               domain="[('is_mail_thread', '=', True), ('transient', '=', False)]")
    res_model = fields.Char(related="model_id.model", store=True, string="Model name")
    res_id = fields.Many2oneReference("Target record", model_field="res_model")
    hit_count = fields.Integer("Emails handled", readonly=True)
    last_hit = fields.Datetime(readonly=True)

    @api.constrains("sender_contains", "subject_contains", "recipient_contains", "action", "model_id", "res_id")
    def _check_rule(self):
        for rule in self:
            if not (rule.sender_contains or rule.subject_contains or rule.recipient_contains):
                raise ValidationError(_("A rule needs at least one condition (sender, subject or address)."))
            if rule.action == "route" and not (rule.model_id and rule.res_id):
                raise ValidationError(_("A routing rule needs a target model and record."))

    def _match(self, orphan):
        self.ensure_one()
        for needle, haystack in (
                (self.sender_contains, orphan.email_from),
                (self.subject_contains, orphan.subject),
                (self.recipient_contains, orphan.rcpt_address)):
            if needle and needle.lower() not in (haystack or "").lower():
                return False
        return True

    def _apply(self, orphan):
        self.ensure_one()
        if self.action == "ignore":
            orphan.write({"state": "ignored", "rule_id": self.id})
        else:
            orphan._route_to(self.res_model, self.res_id, sudo=True)
            orphan.write({"rule_id": self.id})
        self.write({"hit_count": self.hit_count + 1, "last_hit": fields.Datetime.now()})
