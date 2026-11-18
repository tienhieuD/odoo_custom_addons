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


@tagged("post_install", "-at_install")
class TestHideBrand(HttpCase):
    """The option "Hide Powered by Odoo": the layout emits a flag, the small script of the module hides the link."""

    def setUp(self):
        super().setUp()
        if self.env["ir.module.module"].search([("name", "=", "website"), ("state", "=", "installed")]):
            self.skipTest("with Website the login page is drawn in the layout of Website")
        self.icp = self.env["ir.config_parameter"].sudo()

    def test_01_off_by_default_no_flag(self):
        html = self.url_open("/web/login").text
        self.assertNotIn("data-dwo-hidebrand", html)
        self.assertIn("Powered by", html)  # the link of Odoo is untouched in the HTML

    def test_02_flag_emitted_with_and_without_theme(self):
        for theme in ("1", "0"):
            tools.icp_set(self.icp, "dwo_login.enabled", theme)
            tools.icp_set(self.icp, "dwo_login.hide_brand", "1")
            html = self.url_open("/web/login").text
            self.assertIn('data-dwo-hidebrand="1"', html, theme)
            self.assertIn("Powered by", html)  # hidden by the script, never removed from the page
            self.assertIn('name="login"', html)
            tools.icp_set(self.icp, "dwo_login.hide_brand", "0")
            self.assertNotIn("data-dwo-hidebrand", self.url_open("/web/login").text, theme)

    def test_03_js_hides_the_link(self):
        tools.icp_set(self.icp, "dwo_login.hide_brand", "1")
        self.start_tour("/web/login", "dwo_login_themes_brand_hidden_tour")

    def test_04_js_leaves_the_link_when_off(self):
        self.start_tour("/web/login", "dwo_login_themes_brand_shown_tour")
