# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    dwo_attpreview_max_mb_cad_dxf = fields.Integer(
        string="DXF drawings (MB)", config_parameter="dwo_attpreview.max_mb.cad_dxf", default=30)
