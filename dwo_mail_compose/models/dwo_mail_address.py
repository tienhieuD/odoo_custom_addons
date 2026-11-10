# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, tools
from odoo.addons.dwo_mail_bcc.models.mail_compat import normalize_all, email_normalize
from odoo.exceptions import ValidationError


class DwoMailAddress(models.Model):
    """Address book of the emails typed by users that are not a user or a partner.

    One row per (normalized email, company). It feeds the suggestions of the
    composer, next to res.users and res.partner.
    """
    _name = "dwo.mail.address"
    _description = "Email Address Book"
    _order = "last_used desc, id desc"
    _rec_name = "email"

    email = fields.Char(required=True, index=True, help="Normalized (lower case) email address.")
    name = fields.Char()
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.user.company_id)
    use_count = fields.Integer(default=1)
    last_used = fields.Datetime(default=fields.Datetime.now)

    _sql_constraints = [
        ('email_company_uniq', "UNIQUE (email, company_id)", "This email address is already in the address book of this company."),
    ]


    @api.model
    def _dwo_clean_email(self, value):
        return email_normalize(value or "") or False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("email"):
                vals["email"] = self._dwo_clean_email(vals["email"]) or vals["email"]
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("email"):
            vals = dict(vals, email=self._dwo_clean_email(vals["email"]) or vals["email"])
        return super().write(vals)

    @api.constrains("email")
    def _check_email(self):
        for record in self:
            if not email_normalize(record.email or ""):
                raise ValidationError(_("%s is not a valid email address.") % record.email)

    # ------------------------------------------------------------
    # SUGGESTIONS
    # ------------------------------------------------------------

    @api.model
    def dwo_suggest(self, query="", limit=8, exclude=None):
        """Return up to ``limit`` suggestions: users first, then partners, then
        the address book. An address appears once whatever its sources."""
        query = (query or "").strip()
        seen = {email_normalize(e) or e.lower() for e in (exclude or [])}
        results = []

        def add(raw_email, name, source):
            for email in normalize_all(raw_email or ""):
                if email in seen or len(results) >= limit:
                    continue
                seen.add(email)
                results.append({"email": email, "name": name or "", "source": source})

        text_domain = ["|", ("name", "ilike", query), ("email", "ilike", query)] if query else []
        users = self.env["res.users"].search(
            [("share", "=", False), ("email", "!=", False)] + text_domain, limit=limit)
        for user in users:
            add(user.email, user.name, "user")
        partners = self.env["res.partner"].search(
            [("email", "!=", False)] + text_domain, limit=limit, order="write_date desc")
        for partner in partners:
            add(partner.email, partner.name, "partner")
        book = self.search(text_domain, limit=limit)
        for row in book:
            add(row.email, row.name, "book")
        return results[:limit]

    @api.model
    def dwo_register(self, addresses):
        """Remember addresses typed by the user. ``addresses`` is a list of
        dicts ``{"email": ..., "name": ...}``. Users and partners are already
        suggested, so they are not stored here."""
        now = fields.Datetime.now()
        for item in addresses or []:
            email = self._dwo_clean_email(item.get("email"))
            if not email:
                continue
            if self.env["res.partner"].search([("email", "=ilike", email)], limit=1):
                continue
            existing = self.search([("email", "=", email), ("company_id", "=", self.env.user.company_id.id)], limit=1)
            if existing:
                existing.write({
                    "use_count": existing.use_count + 1,
                    "last_used": now,
                    "name": existing.name or item.get("name") or False,
                })
            else:
                self.create({"email": email, "name": item.get("name") or False})
