# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import models
from odoo.exceptions import UserError


class AttPreviewBimEngine(models.AbstractModel):
    """BIM models (IFC), read and drawn in the browser by web-ifc (WebAssembly) and three.js in a sandboxed frame. The
    server only checks that the file looks like an IFC (STEP) file; it parses nothing."""

    _name = "dwo.attpreview.engine.bim"
    _inherit = "dwo.attpreview.engine"
    _description = "Attachment Preview: BIM models"

    _dwo_engine_code = "bim"
    _dwo_engine_label = "BIM models (IFC)"
    _dwo_engine_extensions = ("ifc",)
    _dwo_engine_output = "text"
    _dwo_engine_priority = 10
    _dwo_engine_size_groups = (("bim_ifc", ("ifc",), 100),)

    def _dwo_render(self, content, filename):
        if not content:
            raise UserError(self.env._("The file is empty."))
        head = content[:65536].lstrip(b"\xef\xbb\xbf \t\r\n")
        if not head.startswith(b"ISO-10303-21") or b"FILE_SCHEMA" not in content[:65536] or b"IFC" not in content[:65536].upper():
            raise UserError(self.env._(
                "This is not a valid IFC file (it may be damaged, compressed, or saved in another format)."))
        return {"type": "text", "data": "ifc"}
