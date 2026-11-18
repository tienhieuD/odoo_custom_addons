# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo.tests import HttpCase, tagged

from odoo.addons.dwo_login_themes import tools

LAYOUTS = ("card", "split_left", "glass", "topbar", "dark", "material")


@tagged("post_install", "-at_install")
class TestLoginTour(HttpCase):
    """The form of Odoo still signs a user in through the themed page, with the riskiest layouts.
    One test per layout: each one starts with a browser that is not signed in."""

    def _login_tour(self, layout):
        if self.env["ir.module.module"].search([("name", "=", "website"), ("state", "=", "installed")]):
            self.skipTest("with Website the login page is drawn in the layout of Website: the layouts do not apply")
        icp = self.env["ir.config_parameter"].sudo()
        tools.icp_set(icp, "dwo_login.ann_enabled", "1")
        tools.icp_set(icp, "dwo_login.ann_html", "<p>Tour announcement</p>")
        tools.icp_set(icp, "dwo_login.ann_pos", "above")
        tools.icp_set(icp, "dwo_login.layout", layout)
        self.start_tour("/web/login", "dwo_login_themes_tour")


def _make_test(layout):
    def test(self):
        self._login_tour(layout)
    test.__name__ = "test_login_%s" % layout
    return test


for _layout in LAYOUTS:
    _test = _make_test(_layout)
    setattr(TestLoginTour, _test.__name__, _test)
