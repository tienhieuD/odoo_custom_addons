# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import json
import re
from datetime import timedelta

from odoo import fields
from odoo.tests import HttpCase

from odoo.addons.dwo_session_security.models import util

PASSWORD = "Dwo-Test-Pass-1!"
DOC = {"Sec-Fetch-Dest": "document", "Accept": "text/html"}


class SessionCase(HttpCase):
    """Real HTTP requests with a signed-in session, like a browser (or a script that stole the cookie)."""

    browser_size = "1366,768"

    def setUp(self):
        super().setUp()
        util.post_init(self.env)
        self.icp = self.env["ir.config_parameter"].sudo()
        self.user = self._make_user("dwo_user")
        self.admin = self.env.ref("base.user_admin")
        self.admin.password = PASSWORD
        self.Pin = self.env["dwo.user.pin"]

    def _make_user(self, login, groups="base.group_user"):
        return self.env["res.users"].with_context(no_reset_password=True).create({
            "name": login.title(), "login": login, "email": "%s@example.com" % login, "password": PASSWORD,
            "group_ids" if "group_ids" in self.env["res.users"]._fields else "groups_id":
                [(6, 0, [self.env.ref(g).id for g in groups.split(",")])],
        })

    def set(self, key, value):
        self.icp.set_param("dwo_session." + key, value)

    def sign_in(self, user=None):
        user = user or self.user
        self.authenticate(user.login, PASSWORD)
        # the first authenticated request creates the row
        self.url_open("/dwo/session/heartbeat", data=json.dumps({"params": {"tab": "t1"}}),
                      headers={"Content-Type": "application/json"})
        return self.row(user)

    def row(self, user=None):
        user = user or self.user
        self.env.invalidate_all()
        return self.env["dwo.session"].sudo().search([("user_id", "=", user.id)], order="id desc", limit=1)

    def rpc(self, route, **params):
        res = self.url_open(route, data=json.dumps({"jsonrpc": "2.0", "method": "call", "params": params, "id": 1}),
                            headers={"Content-Type": "application/json"})
        return res.json()

    def beat(self, **params):
        return self.rpc("/dwo/session/heartbeat", **params).get("result")

    def csrf(self, path="/dwo/session/locked"):
        html = self.url_open(path, headers=DOC).text
        match = re.search(r'name="csrf_token" value="([^"]+)"', html)
        return match.group(1) if match else None

    def post(self, path, csrf=True, **data):
        if csrf:
            data["csrf_token"] = self.csrf()
        return self.url_open(path, data=data, allow_redirects=False)

    def go(self, path, **kw):
        return self.url_open(path, headers=dict(DOC, **kw.pop("headers", {})), allow_redirects=False, **kw)

    def set_pin(self, user=None, pin="4826"):
        self.Pin.set_pin((user or self.user).id, pin)

    def age(self, row, **delta):
        """Pretend the session started / was active a while ago."""
        field = delta.pop("field", "last_activity")
        row.write({field: fields.Datetime.now() - timedelta(**delta)})
