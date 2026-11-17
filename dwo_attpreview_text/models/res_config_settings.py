# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    dwo_attpreview_max_mb_text = fields.Integer(
        string="Text and code files (MB)", config_parameter="dwo_attpreview.max_mb.text", default=10)
