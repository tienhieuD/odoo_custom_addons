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
    module_dwo_attpreview_office = fields.Boolean(string="Secure Office Preview: DOCX, XLSX, PPTX, ODT, ODS, ODP, DOC, XLS, PPT, CSV")
    module_dwo_attpreview_mail = fields.Boolean(string="Secure Email Preview: EML, MSG, ICS, VCF")
    module_dwo_attpreview_archive = fields.Boolean(string="Secure Archive Preview: ZIP, RAR, 7Z, TAR")
    module_dwo_attpreview_text = fields.Boolean(string="Secure Text & Code Preview: MD, HTML, XML, JSON, YAML, LOG")
    module_dwo_attpreview_3d = fields.Boolean(string="Secure 3D Preview: STL, STEP, OBJ, GLB, 3DM")
    module_dwo_attpreview_cad = fields.Boolean(string="Secure CAD Preview: DXF drawings")
    module_dwo_attpreview_dwg = fields.Boolean(string="Secure DWG Preview: AutoCAD drawings (free)")
    module_dwo_attpreview_bim = fields.Boolean(string="Secure BIM Preview: IFC models")
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

    @api.depends_context("lang")
    def _compute_dwo_attpreview_engines(self):
        infos = self._dwo_attpreview_engine_infos()
        for rec in self:
            rec.dwo_attpreview_engines = infos
