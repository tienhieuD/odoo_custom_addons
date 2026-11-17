# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    dwo_attpreview_mail_remote_images = fields.Boolean(
        string="Load remote pictures through the server", config_parameter="dwo_attpreview_mail.remote_images")
    dwo_attpreview_mail_remote_https_only = fields.Boolean(
        string="Only secure (HTTPS) pictures", config_parameter="dwo_attpreview_mail.remote_https_only")
    dwo_attpreview_max_mb_mail_message = fields.Integer(
        string="Emails: EML, MSG, OFT, EMLX (MB)", config_parameter="dwo_attpreview.max_mb.mail_message", default=30)
    dwo_attpreview_max_mb_mail_card = fields.Integer(
        string="Calendar and contact cards: ICS, VCF (MB)", config_parameter="dwo_attpreview.max_mb.mail_card", default=5)
