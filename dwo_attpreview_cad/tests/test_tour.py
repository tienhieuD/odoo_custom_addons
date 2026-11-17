# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo.tests import HttpCase, tagged
from odoo.tools import file_path


@tagged("post_install", "-at_install")
class TestCadTour(HttpCase):
    browser_size = "1366,768"

    def test_01_open_dxf_from_the_attachment_form(self):
        with open(file_path("dwo_attpreview_cad/tests/files/floor-plan.dxf"), "rb") as f:
            att = self.env["ir.attachment"].create({"name": "Floor plan.dxf", "raw": f.read()})
        # the sandboxed iframe (opaque origin) loads its scripts without cookies: in test mode Odoo ignores such
        # requests unless all requests are allowed
        self.http_request_allow_all = True
        self.start_tour("/odoo/action-base.action_attachment/%d" % att.id, "dwo_attpreview_cad_tour", login="admin")
