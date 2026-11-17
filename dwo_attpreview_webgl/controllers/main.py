# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
from odoo import http

from .assets import serve_asset

MODULE = "dwo_attpreview_webgl"


class AttPreviewWebglController(http.Controller):

    @http.route("/dwo_attpreview_webgl/asset/<path:path>", type="http", auth="none", cors="*")
    def asset(self, path, **kw):
        """three.js and the common script of the viewers (lib/three/, viewer/), for the sandboxed pages."""
        return serve_asset(MODULE, path, ("lib/three/", "viewer/"))
