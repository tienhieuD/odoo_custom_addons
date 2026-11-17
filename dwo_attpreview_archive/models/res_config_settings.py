# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    dwo_attpreview_max_mb_archive = fields.Integer(
        string="Archives: ZIP, RAR, 7Z, TAR, GZ, BZ2, XZ (MB)", config_parameter="dwo_attpreview.max_mb.archive", default=500)
