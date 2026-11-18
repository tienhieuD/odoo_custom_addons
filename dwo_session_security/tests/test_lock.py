# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import json

from odoo.tests import tagged

from .common import WEBCLIENT, DOC, PASSWORD, SessionCase


@tagged("post_install", "-at_install")
class TestServerSideLock(SessionCase):
    """The lock is kept on the server: a locked session cannot call anything, with or without the web client."""

    def _lock(self, url="/odoo/action-1/5"):
        self.set_pin()
        row = self.sign_in()
        res = self.rpc("/dwo/session/lock", url=url, reason="manual")
        self.assertEqual(res["result"]["state"], "locked", res)
        return self.row()

    def test_locked_session_refuses_rpc_pages_files_and_bus(self):
        row = self._lock()
        self.assertEqual(row.state, "locked")
        # an RPC of the web client
        res = self.rpc("/web/dataset/call_kw/res.partner/search_read", model="res.partner", method="search_read",
                       args=[[]], kwargs={"fields": ["name"], "limit": 5})
        self.assertIn("error", res)
        self.assertNotIn("result", res)
        self.assertIn("dwo_session_locked", json.dumps(res))
        # the same call with the method name in the URL, as the client does
        res = self.rpc("/web/dataset/call_kw", model="res.partner", method="search_read", args=[[]], kwargs={})
        self.assertIn("error", res)
        # a file and an image
        for path in ("/web/image/res.users/%s/avatar_128" % self.user.id, "/web/content/ir.attachment/1/datas"):
            self.assertEqual(self.url_open(path, allow_redirects=False).status_code, 403, path)
        # the web client page itself goes to the lock page
        for path in (WEBCLIENT, "/web"):
            res = self.go(path)
            self.assertEqual(res.status_code, 303, path)
            self.assertTrue(res.headers["Location"].endswith("/dwo/session/locked"), res.headers["Location"])
        # the bus
        res = self.rpc("/websocket/peek_notifications", channels=[], last=0, is_first_poll=True)
        self.assertIn("error", res)
        res = self.url_open("/websocket", allow_redirects=False)
        self.assertIn(res.status_code, (403, 400, 426))

    def test_locked_session_still_reaches_the_lock_page_and_logout(self):
        self._lock()
        page = self.go("/dwo/session/locked")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Screen locked", page.text)
        self.assertEqual(page.headers["Cache-Control"], "no-store")
        # no application data and no web client in the page
        for forbidden in ("web.assets_web", "web.assets_backend", "<script src", "odoo.__session_info__", "res.partner"):
            self.assertNotIn(forbidden, page.text)
        self.assertEqual(self.beat(tab="t1")["state"], "locked")
        out = self.post("/web/session/logout?redirect=/web/login")
        self.assertEqual(out.status_code, 303)

    def test_unlock_with_pin_returns_to_the_same_screen(self):
        self._lock("/odoo/action-1/5?debug=1")
        res = self.post("/dwo/session/unlock", pin="4826")
        self.assertEqual(res.status_code, 303)
        self.assertTrue(res.headers["Location"].endswith("/dwo/session/resume"))
        back = self.go("/dwo/session/resume")
        self.assertEqual(back.headers["Location"], "/odoo/action-1/5?debug=1")
        self.assertEqual(self.row().state, "active")
        # and the session works again
        res = self.rpc("/web/dataset/call_kw/res.users/read", model="res.users", method="read", args=[[self.user.id], ["name"]], kwargs={})
        self.assertIn("result", res)

    def test_unlock_needs_a_csrf_token(self):
        self._lock()
        res = self.post("/dwo/session/unlock", csrf=False, pin="4826")
        self.assertIn(res.status_code, (400, 403))
        self.assertEqual(self.row().state, "locked")

    def test_return_url_is_always_an_internal_path(self):
        self.set_pin()
        self.sign_in()
        for url in ("https://evil.example/x", "//evil.example/x", "/\\evil.example", "javascript:alert(1)", "/web/login",
                    "/dwo/session/relogin", "/odoo\r\nSet-Cookie: a=b", "", "http:evil.example"):
            self.rpc("/dwo/session/lock", url=url)
            self.assertEqual(self.row().state, "locked")
            self.post("/dwo/session/unlock", pin="4826")
            back = self.go("/dwo/session/resume")
            self.assertEqual(back.headers["Location"], "/web", url)
            self.assertEqual(self.row().state, "active")
        self.rpc("/dwo/session/lock", url="/odoo/action-3/7?a=1#b")
        self.post("/dwo/session/unlock", pin="4826")
        self.assertEqual(self.go("/dwo/session/resume").headers["Location"], "/odoo/action-3/7?a=1#b")

    def test_lock_needs_a_pin_and_an_active_session(self):
        self.sign_in()
        res = self.rpc("/dwo/session/lock", url="/web")
        self.assertEqual(res["result"].get("error"), "no_pin")
        self.assertEqual(self.row().state, "active")

    def test_lock_state_is_stored_on_the_server_not_in_the_session(self):
        row = self._lock()
        # a second browser context with a copy of the cookie sees the same state
        self.assertEqual(self.beat()["state"], "locked")
        self.assertTrue(row.key)
        row.write({"state": "active"})   # what an admin could do in the database
        self.assertEqual(self.beat()["state"], "active")

    def test_a_locked_session_cannot_unlock_with_a_wrong_pin_forever(self):
        self._lock()
        self.set("pin_max_tries", "5")
        for i in range(4):
            self.Pin._of(self.user.id).locked_until = False   # skip the pause
            self.post("/dwo/session/unlock", pin="1357")
            self.assertEqual(self.row().state, "locked")
        self.Pin._of(self.user.id).locked_until = False
        res = self.post("/dwo/session/unlock", pin="1357")
        self.assertEqual(self.row().state, "expired")
        self.assertEqual(self.row().end_reason, "pin_failed")
        self.assertIn("/web/login", res.headers["Location"])
        self.assertEqual(self.env["dwo.session.log"].search_count([("event", "=", "unlock_fail"), ("user_id", "=", self.user.id)]), 5)

    def test_pause_after_three_wrong_pins(self):
        self._lock()
        for i in range(3):
            self.post("/dwo/session/unlock", pin="1357")
        pin = self.Pin._of(self.user.id)
        self.assertTrue(pin.seconds_locked())
        # during the pause even the right PIN is refused
        self.post("/dwo/session/unlock", pin="4826")
        self.assertEqual(self.row().state, "locked")
        pin.locked_until = False
        self.post("/dwo/session/unlock", pin="4826")
        self.assertEqual(self.row().state, "active")

    def test_pin_never_signs_in_from_scratch(self):
        self.set_pin()
        res = self.url_open("/web/login", data={"login": self.user.login, "password": "4826", "csrf_token": self.csrf("/web/login")})
        self.assertNotIn("/odoo", res.url)
        self.assertEqual(self.env["dwo.session"].search_count([("user_id", "=", self.user.id)]), 0)

    def test_master_switch_and_exempt_group(self):
        self._lock()
        self.set("enabled", "0")
        res = self.go("/web")
        self.assertNotIn("locked", res.headers.get("Location", ""))
        res = self.rpc("/web/dataset/call_kw/res.users/read", model="res.users", method="read", args=[[self.user.id], ["name"]], kwargs={})
        self.assertIn("result", res)


@tagged("post_install", "-at_install")
class TestPageLooksLikeOdoo(SessionCase):
    """The lock page uses the CSS of the login page of Odoo (only CSS): the gate lets that bundle through and nothing else."""

    def test_css_bundle_reachable_while_locked_but_nothing_else(self):
        import re
        self.set_pin()
        self.sign_in()
        self.rpc("/dwo/session/lock", url="/web")
        html = self.go("/dwo/session/locked").text
        links = re.findall(r'<link[^>]+href="([^"]+)"', html)
        css = [u for u in links if u.endswith(".css")]
        self.assertTrue(css, "the page loads the CSS bundle of the login page")
        for url in css:
            res = self.url_open(url, allow_redirects=False)
            self.assertEqual(res.status_code, 200, url)
            self.assertIn("text/css", res.headers["Content-Type"])
        # no script at all except the small inline one: no src, no web client bundle, no session info
        self.assertFalse(re.findall(r"<script[^>]+src=", html))
        for forbidden in ("web.assets_web", "web.assets_backend", "odoo.__session_info__", "res.partner"):
            self.assertNotIn(forbidden, html)
        self.assertIn("btn btn-primary", html)
        self.assertIn('inputmode="numeric"', html)
        # the web client, an RPC, a JS bundle of the web client and the bus stay refused
        self.assertEqual(self.go(WEBCLIENT).status_code, 303)
        res = self.rpc("/web/dataset/call_kw/res.partner/search_read", model="res.partner", method="search_read", args=[[]], kwargs={})
        self.assertIn("error", res)
        self.assertEqual(self.url_open(css[0].replace("assets_frontend", "assets_web").replace(".css", ".js"), allow_redirects=False).status_code, 403)
        self.assertEqual(self.url_open(css[0].replace(".css", ".js"), allow_redirects=False).status_code, 403)
        self.assertIn("error", self.rpc("/websocket/peek_notifications", channels=[], last=0, is_first_poll=True))

    def test_auto_unlock_script_knows_only_the_pin_length(self):
        self.set_pin(pin="739105")
        self.sign_in()
        self.rpc("/dwo/session/lock", url="/web")
        html = self.go("/dwo/session/locked").text
        self.assertIn('data-auto="6"', html)
        self.assertNotIn("739105", html)
