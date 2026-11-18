# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo.tests import HttpCase, tagged

from odoo.addons.dwo_session_security.models import util


@tagged("post_install", "-at_install")
class TestTours(HttpCase):
    """In the real web client (Chrome). The lock page and the waiting page load no tours: they are checked by the
    HTTP tests and by the browser script of the module (see docs/CHANGELOG.md)."""

    browser_size = "1366,768"

    def setUp(self):
        super().setUp()
        util.post_init(self.env)
        self.icp = self.env["ir.config_parameter"].sudo()
        self.icp.set_param("dwo_session.absolute_min", "0")
        self.icp.set_param("dwo_session.idle_logout_min", "0")
        self.icp.set_param("dwo_session.close_browser", "0")   # the headless browser keeps one tab, but be explicit

    def test_expiry_dialog_returns_to_the_same_screen(self):
        self.start_tour("/odoo/action-base.action_res_users", "dwo_session_expiry_tour", login="admin")

    def test_warning_toast_with_extend(self):
        self.start_tour("/odoo/action-base.action_res_users", "dwo_session_toast_tour", login="admin")
        self.assertEqual(self.env["dwo.session"].sudo().search([("user_id.login", "=", "admin")], limit=1).extensions, 1)
