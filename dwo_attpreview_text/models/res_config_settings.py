# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    dwo_attpreview_max_mb_text = fields.Integer(
        string="Text and code files (MB)", config_parameter="dwo_attpreview.max_mb.text", default=10)
    dwo_attpreview_text_remote_images = fields.Boolean(
        string="Load web pictures through the server", config_parameter="dwo_attpreview_text.remote_images")
    dwo_attpreview_text_remote_https_only = fields.Boolean(
        string="Only secure (HTTPS) pictures", config_parameter="dwo_attpreview_text.remote_https_only")
