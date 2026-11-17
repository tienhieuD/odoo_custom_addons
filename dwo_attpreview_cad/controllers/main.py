# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import http

from odoo.addons.dwo_attpreview_webgl.controllers.assets import serve_asset, serve_file

MODULE = "dwo_attpreview_cad"


class AttPreviewCadController(http.Controller):

    @http.route("/dwo_attpreview_cad/asset/<path:path>", type="http", auth="none", cors="*")
    def asset(self, path, **kw):
        """The page of the sandboxed viewer, the DXF viewer library and its fonts."""
        return serve_asset(MODULE, path, ("viewer/", "lib/dxf-viewer/"))

    @http.route("/dwo_attpreview_cad/file/<int:attachment_id>", type="http", auth="user")
    def file(self, attachment_id, **kw):
        return serve_file(attachment_id, "cad")
