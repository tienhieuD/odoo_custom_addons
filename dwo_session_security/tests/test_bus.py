# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo.tests import tagged

from odoo.addons.dwo_session_security.models.ir_websocket import session_is_active

from .common import SessionCase


@tagged("post_install", "-at_install")
class TestBus(SessionCase):

    def test_websocket_check_follows_the_state_of_the_row(self):
        row = self.env["dwo.session"].sudo().create({"key": "kb", "user_id": self.user.id})
        session = {"dwo_key": "kb"}
        self.assertTrue(session_is_active(session, self.env))
        row.state = "locked"
        self.assertFalse(session_is_active(session, self.env))
        row.state = "pending_approval"
        self.assertFalse(session_is_active(session, self.env))
        row.state = "expired"
        self.assertFalse(session_is_active(session, self.env))
        row.state = "active"
        self.assertTrue(session_is_active(session, self.env))
        self.assertTrue(session_is_active({}, self.env))      # a session without a row: not ours to judge
        self.set("enabled", "0")
        row.state = "locked"
        self.assertTrue(session_is_active(session, self.env))

    def test_the_websocket_loop_uses_the_check(self):
        from odoo import release
        if release.version_info[0] >= 20:
            from odoo.addons.bus import bus_dispatcher as module
            function = module.check_sessions
        else:
            from odoo.addons.bus import websocket as module
            function = module.check_session
        self.assertTrue(getattr(function, "_dwo_session", False))
