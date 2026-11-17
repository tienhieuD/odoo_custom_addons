# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import models
from odoo.exceptions import UserError

BINARY_DXF = b"AutoCAD Binary DXF"


class AttPreviewCadEngine(models.AbstractModel):
    """CAD drawings (DXF), drawn in the browser by dxf-viewer in a sandboxed frame. The server only checks that the
    file looks like a DXF; it parses nothing."""

    _name = "dwo.attpreview.engine.cad"
    _inherit = "dwo.attpreview.engine"
    _description = "Attachment Preview: CAD drawings"

    _dwo_engine_code = "cad"
    _dwo_engine_label = "CAD drawings (DXF)"
    _dwo_engine_extensions = ("dxf",)
    _dwo_engine_output = "text"
    _dwo_engine_priority = 10
    _dwo_engine_size_groups = (("cad_dxf", ("dxf",), 30),)

    def _dwo_render(self, content, filename):
        if not content:
            raise UserError(self.env._("The file is empty."))
        if content.startswith(BINARY_DXF):
            raise UserError(self.env._("Binary DXF files are not supported. Save the drawing as an ASCII DXF."))
        head = content[:8192]
        if b"\0" in head or b"SECTION" not in head:
            raise UserError(self.env._(
                "This is not a valid DXF file (it may be damaged or saved in another format)."))
        return {"type": "text", "data": "dxf"}
