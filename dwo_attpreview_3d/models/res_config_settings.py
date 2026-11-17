# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    dwo_attpreview_max_mb_model3d_mesh = fields.Integer(
        string="Meshes: STL, OBJ, PLY (MB)", config_parameter="dwo_attpreview.max_mb.model3d_mesh", default=50)
    dwo_attpreview_max_mb_model3d_scene = fields.Integer(
        string="Scenes: GLB, GLTF, 3MF, FBX, DAE (MB)", config_parameter="dwo_attpreview.max_mb.model3d_scene", default=50)
    dwo_attpreview_max_mb_model3d_step = fields.Integer(
        string="CAD solids: STEP, IGES (MB)", config_parameter="dwo_attpreview.max_mb.model3d_step", default=25)
    dwo_attpreview_max_mb_model3d_rhino = fields.Integer(
        string="Rhino: 3DM (MB)", config_parameter="dwo_attpreview.max_mb.model3d_rhino", default=50)
