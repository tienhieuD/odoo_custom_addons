# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    dwo_attpreview_max_mb_office_sheet = fields.Integer(
        string="Spreadsheets: XLSX, XLS, ODS and variants (MB)", config_parameter="dwo_attpreview.max_mb.office_sheet", default=50)
    dwo_attpreview_max_mb_office_doc = fields.Integer(
        string="Documents: DOCX, DOC, ODT and variants (MB)", config_parameter="dwo_attpreview.max_mb.office_doc", default=30)
    dwo_attpreview_max_mb_office_slide = fields.Integer(
        string="Presentations: PPTX, PPT, ODP and variants (MB)", config_parameter="dwo_attpreview.max_mb.office_slide", default=30)
    dwo_attpreview_max_mb_office_csv = fields.Integer(
        string="CSV and TSV (MB)", config_parameter="dwo_attpreview.max_mb.office_csv", default=20)
