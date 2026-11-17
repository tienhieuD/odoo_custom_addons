# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the GNU General Public License v3.0 (GPL-3).
from odoo import http

from odoo.addons.dwo_attpreview_webgl.controllers.assets import serve_asset, serve_file

MODULE = "dwo_attpreview_dwg"


class AttPreviewDwgController(http.Controller):

    @http.route("/dwo_attpreview_dwg/asset/<path:path>", type="http", auth="none", cors="*")
    def asset(self, path, **kw):
        """The page of the sandboxed viewer, the DXF viewer library and its fonts."""
        # 'unsafe-eval': the WebAssembly glue of LibreDWG (Emscripten embind) builds its call stubs with new Function. The page
        # is sandboxed (opaque origin), has no network and runs only the files of this module.
        return serve_asset(MODULE, path, ("viewer/", "lib/libredwg/", "lib/dxf-viewer/"), script_extra=" 'unsafe-eval'")

    @http.route("/dwo_attpreview_dwg/file/<int:attachment_id>", type="http", auth="user")
    def file(self, attachment_id, **kw):
        return serve_file(attachment_id, "dwg")
