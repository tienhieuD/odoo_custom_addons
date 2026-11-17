# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from unittest.mock import Mock

import odoo
from odoo import http
from odoo.tests import HttpCase, tagged
from odoo.tools import file_path


class _AssetRoutesWithoutTestCookie:
    """Odoo 18: tests only, see check_test_cursor. After a browser tour starts, every request must carry the test
    cookie, else it is refused (400). The viewer runs in a sandboxed iframe with an opaque origin, so the browser sends
    no cookie with its requests to the public asset routes (the same happens in production, where they need none).
    Let those through; everything else keeps the strict check. Odoo 19 does not refuse them."""

    def check_test_cursor(self, operation):
        request = http.request
        if request and not isinstance(request, Mock) \
                and request.httprequest.path.startswith(("/dwo_attpreview_bim/asset/", "/dwo_attpreview_webgl/asset/")) \
                and odoo.modules.module.current_test == self:
            return
        return super().check_test_cursor(operation)



@tagged("post_install", "-at_install")
class TestBimTour(_AssetRoutesWithoutTestCookie, HttpCase):
    browser_size = "1366,768"

    def test_01_open_ifc_from_the_attachment_form(self):
        with open(file_path("dwo_attpreview_bim/tests/files/office-building.ifc"), "rb") as f:
            att = self.env["ir.attachment"].create({"name": "Office building.ifc", "raw": f.read()})
        # the sandboxed iframe (opaque origin) loads its scripts without cookies: see the mixin above
        self.start_tour("/odoo/action-base.action_attachment/%d" % att.id, "dwo_attpreview_bim_tour", login="admin")
