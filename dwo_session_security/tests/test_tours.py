# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo import release
from odoo.tests import HttpCase, tagged

from odoo.addons.dwo_session_security.models import util


ACTION_URL = "/odoo/action-base.action_res_users" if release.version_info[0] >= 18 else "/web#action=base.action_res_users"


@tagged("post_install", "-at_install")
class TestTours(HttpCase):
    """In the real web client (Chrome). The lock page and the waiting page load no tours: they are checked by the
    HTTP tests and by the browser script of the module (see docs/CHANGELOG.md)."""

    browser_size = "1366,768"

    def setUp(self):
        super().setUp()
        util.post_init(self.env)
        self.icp = self.env["ir.config_parameter"].sudo()
        for key in ("absolute_min", "idle_logout_min", "close_browser"):   # a headless browser has one tab: be explicit
            util.icp_set(self.env, "dwo_session." + key, "0")

    def test_expiry_dialog_returns_to_the_same_screen(self):
        self.start_tour(ACTION_URL, "dwo_session_expiry_tour", login="admin")

    def test_warning_toast_with_extend(self):
        self.start_tour(ACTION_URL, "dwo_session_toast_tour", login="admin")
        self.assertEqual(self.env["dwo.session"].sudo().search([("user_id.login", "=", "admin")], limit=1).extensions, 1)
