# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import http

from odoo.addons.dwo_attpreview_webgl.controllers.assets import serve_asset, serve_file

MODULE = "dwo_attpreview_3d"


class AttPreview3DController(http.Controller):

    @http.route("/dwo_attpreview_3d/asset/<path:path>", type="http", auth="none", cors="*")
    def asset(self, path, **kw):
        """The page of the sandboxed viewer and its script (three.js comes from dwo_attpreview_webgl)."""
        return serve_asset(MODULE, path, ("viewer/",))

    @http.route("/dwo_attpreview_3d/file/<int:attachment_id>", type="http", auth="user")
    def file(self, attachment_id, **kw):
        return serve_file(attachment_id, "model3d")
