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
        shared = self.env["dwo.dashboard.page"].search([("dashboard_id", "!=", dashboard.id)])
        return {"id": dashboard.id, "name": dashboard.name, "pages": [page._summary() for page in pages],
                "shared": [page._summary() for page in shared]}


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
    share_ids = fields.One2many("dwo.dashboard.share", "page_id", string="Shared with")
    spec = fields.Json(default=lambda self: copy.deepcopy(EMPTY_SPEC))
    revision = fields.Integer(default=1, readonly=True, copy=False,
                              help="Raised at every change of the spec; a save that does not know the latest "
                                   "revision is refused (two tabs, two people).")

    def _summary(self):
        self.ensure_one()
        return {"id": self.id, "name": self.name, "sequence": self.sequence, "revision": self.revision,
                "level": self._level(), "owner": self.sudo().user_id.name}

    def _level(self):
        """What the caller may do with the page: ``owner``, ``edit`` or ``view``."""
        self.ensure_one()
        if self.sudo().user_id.id == self.env.uid:
            return "owner"
        groups = self.env.user.all_group_ids
        for share in self.share_ids:
            if share.level == "edit" and (share.user_id == self.env.user or share.group_id in groups):
                return "edit"
        return "view"

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
        if not self.env.su and set(vals) - {"spec", "revision"} and any(page._level() != "owner" for page in self):
            raise AccessError(_("Only the owner can change more than the content of a shared page."))
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
                "revision": page.revision, "level": page._level(), "owner": page.sudo().user_id.name}

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
        """A copy in the dashboard of the caller (also for a page shared with them: nothing else is copied than the grid)."""
        self.ensure_one()
        mine = self.env["dwo.dashboard"].get_my_dashboard()["id"]
        copy_ = self.create({"dashboard_id": mine, "name": (_("%s (copy)") % self.name)[:60], "sequence": self.sequence + 1,
                             "spec": copy.deepcopy(self.spec or EMPTY_SPEC)})
        return copy_._summary()

    @api.model
    def reorder(self, page_ids):
        """Give the pages the order of the list (the caller's own pages only: record rules decide)."""
        pages = self.browse(page_ids)
        pages.check_access("write")
        if any(page._level() != "owner" for page in pages):
            raise AccessError(_("Only the owner orders the pages."))
        for index, page in enumerate(pages):
            page.sequence = (index + 1) * 10
        return True

    # ------------------------------------------------------------------------------------------------ sharing
    def get_shares(self):
        """The shares of a page (its owner only)."""
        self.ensure_one()
        self._must_own()
        return [{"id": s.id, "kind": "user" if s.user_id else "group", "name": s.target, "level": s.level,
                 "user_id": s.user_id.id, "group_id": s.group_id.id}
                for s in self.share_ids]

    def share_with(self, user_ids, group_ids, level):
        self.ensure_one()
        self._must_own()
        if level not in ("view", "edit"):
            raise UserError(_("Unknown level."))
        Share = self.env["dwo.dashboard.share"]
        have = {(s.user_id.id, s.group_id.id): s for s in self.share_ids}
        for user_id in user_ids:
            share = have.get((user_id, False))
            share.write({"level": level}) if share else Share.create({"page_id": self.id, "user_id": user_id, "level": level})
        for group_id in group_ids:
            share = have.get((False, group_id))
            share.write({"level": level}) if share else Share.create({"page_id": self.id, "group_id": group_id, "level": level})
        return self.get_shares()

    def revoke_share(self, share_id):
        self.ensure_one()
        self._must_own()
        self.share_ids.filtered(lambda s: s.id == share_id).unlink()
        return self.get_shares()

    @api.model
    def search_recipients(self, query):
        """Internal users and groups matching ``query``, to pick who a page is shared with."""
        query = (query or "").strip()
        users = self.env["res.users"].search([("share", "=", False), ("id", "!=", self.env.uid), ("name", "ilike", query)], limit=8)
        groups = self.env["res.groups"].search([("share", "=", False), ("name", "ilike", query)], limit=8) if query else self.env["res.groups"]
        return {"users": [{"id": u.id, "name": u.name} for u in users],
                "groups": [{"id": g.id, "name": g.display_name} for g in groups]}

    @api.model
    def share_log(self, limit=50):
        return self.env["dwo.dashboard.share.log"].search_read([], ["page_name", "action", "target", "level", "create_date"], limit=limit)

    def _must_own(self):
        if self.sudo().user_id.id != self.env.uid:
            raise AccessError(_("Only the owner of a page shares it."))
