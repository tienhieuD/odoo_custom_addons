# Copyright 2026 DuoTEK. Licensed under the GNU General Public License v3.0 (GPL-3).
from odoo.tests import HttpCase, tagged
from odoo.tools import file_path


@tagged("post_install", "-at_install")
class TestDwgTour(HttpCase):
    browser_size = "1366,768"

    def test_01_open_dwg_from_the_attachment_form(self):
        with open(file_path("dwo_attpreview_dwg/tests/files/sample_2000.dwg"), "rb") as f:
            att = self.env["ir.attachment"].create({"name": "Sample 2000.dwg", "raw": f.read()})
        # the sandboxed iframe (opaque origin) loads its scripts without cookies: in test mode Odoo ignores such
        # requests unless all requests are allowed
        self.http_request_allow_all = True
        self.start_tour("/odoo/action-base.action_attachment/%d" % att.id, "dwo_attpreview_dwg_tour", login="admin")
