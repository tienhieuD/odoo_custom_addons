# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import http

from odoo.addons.dwo_attpreview_webgl.controllers.assets import serve_asset, serve_file

MODULE = "dwo_attpreview_bim"


class AttPreviewBimController(http.Controller):

    @http.route("/dwo_attpreview_bim/asset/<path:path>", type="http", auth="none", cors="*")
    def asset(self, path, **kw):
        """The page of the sandboxed viewer, the web-ifc library."""
        return serve_asset(MODULE, path, ("viewer/", "lib/web-ifc/"))

    @http.route("/dwo_attpreview_bim/file/<int:attachment_id>", type="http", auth="user")
    def file(self, attachment_id, **kw):
        return serve_file(attachment_id, "bim")
