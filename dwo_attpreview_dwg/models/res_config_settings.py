# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the GNU General Public License v3.0 (GPL-3).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    dwo_attpreview_max_mb_dwg = fields.Integer(
        string="DWG drawings (MB)", config_parameter="dwo_attpreview.max_mb.dwg", default=30)
