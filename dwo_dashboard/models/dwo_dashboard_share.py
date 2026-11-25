# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

LEVELS = [("view", "View"), ("edit", "Edit")]


class DwoDashboardShare(models.Model):
    """A page shared with one user or one group. Only the owner of the page creates, changes or deletes shares (record
    rules); the recipient can read the shares that concern them, which is what the page rule looks at."""
    _name = "dwo.dashboard.share"
    _description = "Dashboard page share"
    _order = "page_id, id"

    page_id = fields.Many2one("dwo.dashboard.page", required=True, ondelete="cascade", index=True)
    user_id = fields.Many2one("res.users", ondelete="cascade", index=True, domain=[("share", "=", False)])
    group_id = fields.Many2one("res.groups", ondelete="cascade", index=True)
    level = fields.Selection(LEVELS, required=True, default="view")
    target = fields.Char(compute="_compute_target")

    _one_target = models.Constraint("CHECK((user_id IS NULL) != (group_id IS NULL))",
                                    "A share is for one user or one group.")
    _unique_user = models.Constraint("UNIQUE(page_id, user_id)", "The page is already shared with this user.")
    _unique_group = models.Constraint("UNIQUE(page_id, group_id)", "The page is already shared with this group.")

    @api.depends("user_id", "group_id")
    def _compute_target(self):
        for share in self:
            share.target = share.sudo().user_id.name or share.sudo().group_id.display_name or ""

    @api.constrains("user_id", "group_id", "page_id")
    def _check_target(self):
        outsiders = (self.env.ref("base.group_portal"), self.env.ref("base.group_public"))
        for share in self.sudo():
            owner = share.page_id.dashboard_id.user_id
            if share.user_id and share.user_id.share:
                raise ValidationError(_("A page can be shared with internal users only."))
            if share.user_id == owner:
                raise ValidationError(_("The owner already has the page."))
            if share.group_id and (share.group_id in outsiders or share.group_id.sudo().share):
                raise ValidationError(_("A page cannot be shared with portal or public users."))

    @api.model_create_multi
    def create(self, vals_list):
        shares = super().create(vals_list)
        shares._log("grant")
        return shares

    def write(self, vals):
        if set(vals) - {"level"}:  # the page and the target never change: revoke and share again
            raise AccessError(_("Only the level of a share can be changed."))
        old = {share.id: share.level for share in self}
        result = super().write(vals)
        self.filtered(lambda s: old[s.id] != s.level)._log("change")
        return result

    def unlink(self):
        self._log("revoke")
        return super().unlink()

    def _log(self, action):
        Log = self.env["dwo.dashboard.share.log"].sudo()
        Log.create([{"actor_id": self.env.uid, "page_id": share.page_id.id, "page_name": share.page_id.sudo().name, "action": action,
                     "target": share.target, "level": share.level} for share in self])


class DwoDashboardShareLog(models.Model):
    """Who shared which page with whom, and when (readable by the person who did it)."""
    _name = "dwo.dashboard.share.log"
    _description = "Dashboard share log"
    _order = "id desc"

    actor_id = fields.Many2one("res.users", required=True, ondelete="cascade", index=True)
    page_id = fields.Integer(index=True)  # not a Many2one: the log outlives the page
    page_name = fields.Char()
    action = fields.Selection([("grant", "Shared"), ("change", "Level changed"), ("revoke", "Revoked")], required=True)
    target = fields.Char()
    level = fields.Selection(LEVELS)
