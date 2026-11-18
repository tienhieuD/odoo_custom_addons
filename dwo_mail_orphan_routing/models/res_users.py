# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    dwo_orphan_all_aliases = fields.Boolean(
        "Orphan mail: all aliases", default=True,
        help="Orphan Mail Managers see the orphan emails of every alias. Untick to see only the aliases below.")
    dwo_orphan_alias_ids = fields.Many2many(
        "mail.alias", "dwo_orphan_user_alias_rel", "user_id", "alias_id", string="Orphan mail: aliases")
