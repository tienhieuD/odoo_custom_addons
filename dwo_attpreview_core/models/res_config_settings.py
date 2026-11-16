# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
from odoo import api, fields, models
from odoo.addons.dwo_attpreview_core import catalog

INSTALLED_STATES = ("installed", "to upgrade", "to remove", "to install")


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    dwo_attpreview_max_file_size_mb = fields.Integer(
        string="Max file size (MB)", config_parameter="dwo_attpreview.max_file_size_mb", default=20)
    # One tick per engine module: Odoo installs it on Save and asks to uninstall it when unticked.
    # A module that is not in the addons path cannot be installed: the widget shows its page instead.
    module_dwo_attpreview_office = fields.Boolean(string="Secure Office Preview: DOCX, DOC, XLSX, XLS, PPTX, PPT, CSV, TSV")
    module_dwo_attpreview_mail = fields.Boolean(string="Secure Email Preview: EML, MSG, ICS, VCF")
    # what the widget `dwo_attpreview_engine_boolean` shows (name, file types, state), by engine module
    dwo_attpreview_engines = fields.Json(compute="_compute_dwo_attpreview_engines")

    @api.model
    def _dwo_attpreview_module_state(self, module):
        """``installed`` | ``available`` (in the addons path, not installed) | ``missing`` (not in the addons path)."""
        row = self.env["ir.module.module"].sudo().search([("name", "=", module)], limit=1)
        if not row or row.state == "uninstallable":
            return "missing"
        return "installed" if row.state in INSTALLED_STATES else "available"

    @api.model
    def _dwo_attpreview_engine_infos(self):
        infos = {}
        for entry in catalog.load_catalog():
            module = entry["module"]
            infos[module] = {
                "module": module,
                "name": entry["name"],
                "extensions": entry["extensions"],
                "store_url": entry["store_url"],
                "state": self._dwo_attpreview_module_state(module),
                "description_url": "%s%s/index.html" % (catalog.CATALOG_STATIC, module),
                "base_url": "%s%s/" % (catalog.CATALOG_STATIC, module),
            }
        return infos

    @api.model
    def default_get(self, fields):
        # Odoo 18: the first onchange of the Settings form fills every field of the view that has no default with
        # False and never runs a compute without dependencies (19 does), so the widget would get no engine info.
        # Give the field its value as a default too.
        res = super().default_get(fields)
        if "dwo_attpreview_engines" in fields:
            res["dwo_attpreview_engines"] = self._dwo_attpreview_engine_infos()
        return res

    @api.depends_context("lang")
    def _compute_dwo_attpreview_engines(self):
        infos = self._dwo_attpreview_engine_infos()
        for rec in self:
            rec.dwo_attpreview_engines = infos
