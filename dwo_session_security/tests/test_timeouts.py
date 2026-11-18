# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import time

from odoo import release

from odoo.tests import tagged

from .common import WEBCLIENT, DOC, PASSWORD, SessionCase


@tagged("post_install", "-at_install")
class TestTimeouts(SessionCase):

    def test_idle_lock_is_applied_by_the_server(self):
        self.set_pin()
        row = self.sign_in()
        self.set("lock_after_min", "10")
        self.age(row, minutes=9)
        self.assertEqual(self.beat(tab="t1")["state"], "active")
        self.age(row, minutes=11)
        self.assertEqual(self.beat(tab="t1")["state"], "locked")
        self.assertEqual(self.row().lock_reason, "idle")
        # the web client page is now the lock page
        self.assertTrue(self.go(WEBCLIENT).headers["Location"].endswith("/dwo/session/locked"))

    def test_no_pin_no_idle_lock(self):
        row = self.sign_in()
        self.age(row, minutes=60)
        self.assertEqual(self.beat(tab="t1")["state"], "active")

    def test_idle_logout_ends_the_session_and_the_session_is_gone(self):
        row = self.sign_in()
        self.set("idle_logout_min", "30")
        self.age(row, minutes=45)
        res = self.rpc("/web/dataset/call_kw/res.users/read", model="res.users", method="read", args=[[self.user.id], ["name"]], kwargs={})
        self.assertIn("error", res)
        self.assertEqual(res["error"]["code"], 100)   # Odoo's own "session expired"
        self.assertEqual(self.row().state, "expired")
        self.assertEqual(self.row().end_reason, "idle")
        # a page request goes to the login page, with the screen to come back to
        page = self.go(WEBCLIENT)
        self.assertIn("/web/login", page.headers["Location"])
        if release.version_info[0] >= 18:   # in 17 the web client page itself sends a signed-out user to the login page
            self.assertIn("redirect=", page.headers["Location"])
        self.assertEqual(self.env["dwo.session.log"].search_count([("event", "=", "expired"), ("user_id", "=", self.user.id)]), 1)

    def test_absolute_limit(self):
        row = self.sign_in()
        self.set("absolute_min", "60")
        self.set("idle_logout_min", "0")
        self.age(row, minutes=59, field="login_time")
        self.assertEqual(self.beat(tab="t1")["state"], "active")
        self.age(row, minutes=61, field="login_time")
        res = self.beat(tab="t1")
        self.assertEqual(res["state"], "expired")
        self.assertEqual(res["reason"], "absolute")
        # activity does not help against the maximum duration
        self.assertEqual(self.beat(tab="t1", idle=0)["state"], "expired")

    def test_locked_session_also_ends_when_idle_too_long(self):
        self.set_pin()
        row = self.sign_in()
        self.rpc("/dwo/session/lock", url="/web")
        self.set("idle_logout_min", "30")
        self.age(row, minutes=31)
        self.assertEqual(self.beat(tab="t1")["state"], "expired")

    def test_exempt_group_has_no_time_limit(self):
        self.user.write({("group_ids" if "group_ids" in self.user._fields else "groups_id"): [(4, self.env.ref("dwo_session_security.group_dwo_session_exempt").id)]})
        self.set_pin()
        row = self.sign_in()
        self.age(row, minutes=60 * 48)
        self.age(row, minutes=60 * 48, field="login_time")
        self.assertEqual(self.beat(tab="t1")["state"], "active")

    def test_only_the_activity_ping_counts_as_activity(self):
        row = self.sign_in()
        self.age(row, minutes=20)
        before = self.row().last_activity
        for _i in range(3):   # Odoo's own background calls are not activity
            self.rpc("/web/dataset/call_kw/res.users/read", model="res.users", method="read", args=[[self.user.id], ["name"]], kwargs={})
        self.assertEqual(self.row().last_activity, before)
        self.beat(tab="t1", idle=0)
        self.assertGreater(self.row().last_activity, before)
        # a ping is not written more often than every 30 s
        stamp = self.row().last_activity
        self.beat(tab="t1", idle=0)
        self.assertEqual(self.row().last_activity, stamp)

    def test_warning_and_extension(self):
        row = self.sign_in()
        self.set("absolute_min", "120")
        self.set("idle_logout_min", "0")
        self.set("warn_min", "30")
        self.age(row, minutes=60, field="login_time")
        res = self.beat(tab="t1")
        self.assertEqual(res["expires_kind"], "absolute")
        self.assertGreater(res["expires_in"], 59 * 60)
        self.assertEqual(res["warn"], 30 * 60)
        self.assertTrue(res["extend"])
        self.age(row, minutes=100, field="login_time")
        res = self.beat(tab="t1")
        self.assertLessEqual(res["expires_in"], 20 * 60 + 5)
        # extend
        self.set("extend_min", "60")
        self.set("extend_max", "1")
        res = self.rpc("/dwo/session/extend")["result"]
        self.assertTrue(res["extended"])
        self.assertGreater(res["expires_in"], 70 * 60)
        self.assertFalse(res["extend"])
        self.assertFalse(self.rpc("/dwo/session/extend")["result"]["extended"])
        # warning switched off
        self.set("warn_enabled", "0")
        self.assertEqual(self.beat(tab="t1")["warn"], 0)

    def test_admin_closes_a_session(self):
        row = self.sign_in()
        self.env["dwo.session"].with_user(self.admin).browse(row.id).action_force_logout()
        self.assertEqual(self.row().end_reason, "forced")
        res = self.rpc("/web/dataset/call_kw/res.users/read", model="res.users", method="read", args=[[self.user.id], ["name"]], kwargs={})
        self.assertIn("error", res)
        # a user cannot close the session of someone else
        other = self.env["dwo.session"].sudo().create({"key": "k-other", "user_id": self.admin.id, "state": "active"})
        with self.assertRaises(Exception):
            other.with_user(self.user.id).action_force_logout()

    def test_user_sees_only_own_sessions(self):
        self.env["dwo.session"].sudo().create({"key": "k-admin", "user_id": self.admin.id})
        self.env["dwo.session"].sudo().create({"key": "k-user", "user_id": self.user.id})
        visible = self.env["dwo.session"].with_user(self.user).search([])
        self.assertEqual(visible.mapped("user_id"), self.user)


@tagged("post_install", "-at_install")
class TestSessionCookie(SessionCase):

    def _cookies(self, response):
        return response.raw.headers.getlist("Set-Cookie")

    def test_session_cookie_has_no_expiry(self):
        page = self.url_open("/web/login")
        import re
        token = re.search(r'name="csrf_token" value="([^"]+)"', page.text).group(1)
        res = self.url_open("/web/login", data={"login": self.user.login, "password": PASSWORD, "csrf_token": token}, allow_redirects=False)
        cookies = [c for c in self._cookies(res) if c.startswith("session_id=")]
        self.assertTrue(cookies, "the login sets the session cookie")
        for cookie in cookies:
            low = cookie.lower()
            self.assertNotIn("expires=", low)
            self.assertNotIn("max-age", low)
            self.assertIn("httponly", low)
        # a plain RPC and an authenticated page keep it a browser-session cookie
        for path in (WEBCLIENT, "/web/login"):
            res = self.url_open(path, allow_redirects=False)
            for cookie in [c for c in self._cookies(res) if c.startswith("session_id=")]:
                self.assertNotIn("max-age", cookie.lower())
                self.assertNotIn("expires=", cookie.lower())

    def test_cookie_is_normal_when_the_option_is_off(self):
        self.set("close_browser", "0")
        page = self.url_open("/web/login")
        import re
        token = re.search(r'name="csrf_token" value="([^"]+)"', page.text).group(1)
        res = self.url_open("/web/login", data={"login": self.user.login, "password": PASSWORD, "csrf_token": token}, allow_redirects=False)
        cookies = [c for c in self._cookies(res) if c.startswith("session_id=")]
        self.assertTrue(any("max-age" in c.lower() for c in cookies))


@tagged("post_install", "-at_install")
class TestCloseBrowser(SessionCase):
    """The server watches the heartbeat of the tabs: a browser that comes back after it was closed (cookie restored)
    is refused, a reload and a second tab are not."""

    def test_reload_and_second_tab_are_fine(self):
        self.sign_in()
        self.assertEqual(self.beat(tab="t1")["state"], "active")
        self.assertEqual(self.beat(tab="t2")["state"], "active")           # a new tab: another tab is alive
        self.assertEqual(self.go(WEBCLIENT).status_code, 200)               # a page load: fine
        # reload of the only tab: bye, then a page and a heartbeat within seconds
        self.rpc("/dwo/session/bye", tab="t1")
        self.rpc("/dwo/session/bye", tab="t2")
        self.assertNotEqual(self.go(WEBCLIENT).status_code, 303)
        self.assertEqual(self.beat(tab="t1")["state"], "active")

    def test_cookie_restored_after_the_browser_was_closed(self):
        row = self.sign_in()
        self.beat(tab="t1")
        # the browser is closed: every tab said bye, a while ago
        tabs = row._tabs()
        old = time.time() - 120
        row.tabs = '{"t1": [%s, %s]}' % (old - 5, old)
        res = self.go(WEBCLIENT)
        self.assertEqual(res.status_code, 303)
        self.assertIn("/web/login", res.headers["Location"])
        self.assertEqual(self.row().state, "expired")
        self.assertEqual(self.row().end_reason, "browser_closed")
        self.assertTrue(self.env["dwo.session.log"].search([("event", "=", "browser_closed")]))

    def test_browser_killed_without_bye_is_found_by_the_missing_heartbeat(self):
        row = self.sign_in()
        self.beat(tab="t1")
        row.tabs = '{"t1": [%s, 0]}' % (time.time() - 400)
        self.assertEqual(self.beat(tab="t1")["state"], "expired")
        self.assertEqual(self.row().end_reason, "browser_closed")

    def test_new_tab_when_no_tab_is_alive_is_refused(self):
        row = self.sign_in()
        row.tabs = '{"t1": [%s, 0]}' % (time.time() - 400)
        self.assertEqual(self.beat(tab="new")["state"], "expired")

    def test_switch_off(self):
        row = self.sign_in()
        self.set("close_browser", "0")
        row.tabs = '{"t1": [%s, 0]}' % (time.time() - 4000)
        self.assertEqual(self.beat(tab="t1")["state"], "active")
        self.assertNotEqual(self.go(WEBCLIENT).status_code, 303)
