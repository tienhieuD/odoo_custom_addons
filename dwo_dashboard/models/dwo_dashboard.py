# -*- coding: utf-8 -*-
import copy
import json

import psycopg2.errors

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

MAX_PAGES = 30
MAX_SPEC_BYTES = 512 * 1024
EMPTY_SPEC = {"schema": "dwo-dashboard/1", "widgets": []}


class DwoDashboard(models.Model):
    """The dashboard of one user ("My dashboard"): a set of pages, each page a grid of widgets."""
    _name = "dwo.dashboard"
    _description = "Dashboard"
    _order = "id"

    name = fields.Char(required=True, default=lambda self: _("My dashboard"))
    user_id = fields.Many2one("res.users", required=True, default=lambda self: self.env.user, index=True,
                              ondelete="cascade", readonly=True)
    page_ids = fields.One2many("dwo.dashboard.page", "dashboard_id", string="Pages")

    _user_unique = models.Constraint("UNIQUE(user_id)", "A user has one dashboard.")

    def write(self, vals):
        if "user_id" in vals and any(rec.user_id.id != vals["user_id"] for rec in self):
            raise AccessError(_("A dashboard cannot be given to another user."))
        return super().write(vals)

    @api.model
    def get_my_dashboard(self):
        """The dashboard of the current user (created on first use) with the list of its pages (no spec)."""
        dashboard = self.search([("user_id", "=", self.env.uid)], limit=1)
        if not dashboard:
            try:  # first use in two tabs at once: the second one finds the dashboard the first one made
                with self.env.cr.savepoint():
                    dashboard = self.create({"user_id": self.env.uid})
                    self.env["dwo.dashboard.page"].create({"dashboard_id": dashboard.id, "name": _("Home")})
            except psycopg2.errors.UniqueViolation:
                dashboard = self.search([("user_id", "=", self.env.uid)], limit=1)
        pages = self.env["dwo.dashboard.page"].search([("dashboard_id", "=", dashboard.id)])
        return {"id": dashboard.id, "name": dashboard.name, "pages": [page._summary() for page in pages]}


class DwoDashboardPage(models.Model):
    """One page of a dashboard: its ``spec`` is a ``dwo-dashboard/1`` document (see SPEC.md). A page is validated, as the
    person who saves it and without sudo, every time ``spec`` is written (strict on save); it is validated again, as
    the person who views it, every time a widget runs (tolerant on render)."""
    _name = "dwo.dashboard.page"
    _description = "Dashboard page"
    _order = "dashboard_id, sequence, id"

    name = fields.Char(required=True, size=60)
    sequence = fields.Integer(default=10)
    dashboard_id = fields.Many2one("dwo.dashboard", required=True, index=True, ondelete="cascade")
    user_id = fields.Many2one(related="dashboard_id.user_id", store=True, index=True)
    spec = fields.Json(default=lambda self: copy.deepcopy(EMPTY_SPEC))
    revision = fields.Integer(default=1, readonly=True, copy=False,
                              help="Raised at every change of the spec; a save that does not know the latest "
                                   "revision is refused (two tabs, two people).")

    def _summary(self):
        self.ensure_one()
        return {"id": self.id, "name": self.name, "sequence": self.sequence, "revision": self.revision}

    # ------------------------------------------------------------------------------------------------ rules
    # Why the check is in create/write and not (only) in a constraint: ORM constraints run as superuser, so a constraint
    # cannot tell what the person saving may read. The caller's own environment validates the spec before anything is
    # written; the constraint stays as a backstop for every other path (imports, sudo code), with superuser rights.
    def _check_spec_as_caller(self, spec):
        spec = spec or copy.deepcopy(EMPTY_SPEC)
        if len(json.dumps(spec)) > MAX_SPEC_BYTES:
            raise ValidationError(_("The page is too large."))
        result = self.env["dwo.dashboard.spec"]._validate(spec, True)
        if not result["valid"]:
            raise ValidationError(_("The page is not valid:\n%s") % "\n".join(
                "%(path)s: %(message)s" % e for e in result["errors"][:5]))

    @api.constrains("spec")
    def _check_spec(self):
        for page in self:
            page._check_spec_as_caller(page.spec)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("spec"):
                self._check_spec_as_caller(vals["spec"])
        return super().create(vals_list)

    @api.constrains("dashboard_id")
    def _check_page_count(self):
        for dashboard in self.dashboard_id:
            if len(dashboard.page_ids) > MAX_PAGES:
                raise ValidationError(_("A dashboard has at most %d pages.") % MAX_PAGES)

    def write(self, vals):
        if "dashboard_id" in vals and any(page.dashboard_id.id != vals["dashboard_id"] for page in self):
            raise AccessError(_("A page cannot be moved to another dashboard."))
        if "spec" in vals:
            self._check_spec_as_caller(vals["spec"])
        if "spec" in vals and "revision" not in vals:
            for page in self:  # each page counts its own revisions
                super(DwoDashboardPage, page).write(dict(vals, revision=page.revision + 1))
            return True
        return super().write(vals)

    # -------------------------------------------------------------------------------------------- operations
    @api.model
    def get_page(self, page_id):
        """The page with its spec, for the client. Access is the one of the caller (record rules)."""
        page = self.browse(page_id)
        page.check_access("read")
        return {"id": page.id, "name": page.name, "spec": page.spec or copy.deepcopy(EMPTY_SPEC),
                "revision": page.revision}

    def save_spec(self, spec, revision):
        """Save the grid. ``revision`` is the one the client loaded: a newer one on the server means somebody else
        changed the page, and nothing is overwritten."""
        self.ensure_one()
        if revision != self.revision:
            raise UserError(_("This page was changed somewhere else (revision %(server)s, yours is %(yours)s). "
                              "Reload it before saving.", server=self.revision, yours=revision))
        self.write({"spec": spec})
        return {"revision": self.revision}

    def duplicate_page(self):
        self.ensure_one()
        copy_ = self.copy({"name": _("%s (copy)") % self.name, "sequence": self.sequence + 1,
                           "spec": copy.deepcopy(self.spec or EMPTY_SPEC)})
        return copy_._summary()

    @api.model
    def reorder(self, page_ids):
        """Give the pages the order of the list (the caller's own pages only: record rules decide)."""
        pages = self.browse(page_ids)
        pages.check_access("write")
        for index, page in enumerate(pages):
            page.sequence = (index + 1) * 10
        return True
