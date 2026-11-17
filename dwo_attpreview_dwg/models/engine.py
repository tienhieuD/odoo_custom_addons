# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the GNU General Public License v3.0 (GPL-3).
from odoo import models
from odoo.exceptions import UserError

# AutoCAD release signatures: AC1012 (R13) ... AC1032 (2018 and later), and the older AC1.50 / AC2.x
KNOWN_PREFIXES = (b"AC10", b"AC1.", b"AC2.", b"MC0.")


class AttPreviewDwgEngine(models.AbstractModel):
    """AutoCAD drawings (DWG), converted to DXF by LibreDWG (WebAssembly) in the browser, then drawn by dxf-viewer, all
    in a sandboxed frame. The server only checks the signature of the file; it parses nothing."""

    _name = "dwo.attpreview.engine.dwg"
    _inherit = "dwo.attpreview.engine"
    _description = "Attachment Preview: DWG drawings"

    _dwo_engine_code = "dwg"
    _dwo_engine_label = "AutoCAD drawings (DWG)"
    _dwo_engine_extensions = ("dwg",)
    _dwo_engine_output = "text"
    _dwo_engine_priority = 10
    _dwo_engine_size_groups = (("dwg", ("dwg",), 30),)

    def _dwo_render(self, content, filename):
        if not content:
            raise UserError(self.env._("The file is empty."))
        if not content.startswith(KNOWN_PREFIXES):
            raise UserError(self.env._(
                "This is not a valid DWG file (it may be damaged or saved in another format)."))
        return {"type": "text", "data": "dwg"}
