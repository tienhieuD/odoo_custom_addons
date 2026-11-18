# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import re

from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged

from odoo.addons.dwo_session_security.models.pin import weak_reason

from .common import PASSWORD, SessionCase


@tagged("post_install", "-at_install")
class TestPinRules(TransactionCase):

    def test_weak_pins_are_refused(self):
        for pin in ("0000", "1234", "4321", "1111", "9999", "1212", "123456", "000000", "121212", "2580", "1990", "2005", "1221"):
            self.assertTrue(weak_reason(pin), pin)
        for pin in ("4826", "739105", "5081", "2947"):
            self.assertFalse(weak_reason(pin), pin)

    def test_format(self):
        Pin = self.env["dwo.user.pin"]
        for bad in ("12", "12345", "abcd", "48 26", "", "48261", "4826a"):
            with self.assertRaises(UserError):
                Pin.check_format(bad)
        Pin.check_format("4826")
        Pin.check_format("739105")
        from odoo.addons.dwo_session_security.models import util
        util.icp_set(self.env, "dwo_session.pin_digits", "6")
        with self.assertRaises(UserError):
            Pin.check_format("4826")

    def test_pin_is_stored_hashed_with_salt_and_no_group_can_read_it(self):
        user = self.env.ref("base.user_demo")
        other = self.env.ref("base.user_admin")
        Pin = self.env["dwo.user.pin"]
        rec = Pin.set_pin(user.id, "4826")
        rec2 = Pin.set_pin(other.id, "4826")
        self.assertNotIn("4826", rec.pin_hash)
        self.assertNotEqual(rec.pin_hash, rec2.pin_hash)       # salted: same PIN, different hashes
        self.assertTrue(rec.pin_hash.startswith("$pbkdf2") or rec.pin_hash.startswith("$"))
        self.assertTrue(rec.verify_pin("4826"))
        self.assertFalse(rec.verify_pin("4827"))
        for who in (user, other):
            with self.assertRaises(AccessError):
                Pin.with_user(who).search([])
        # the PIN is not in any field of res.users
        self.assertFalse([f for f in user._fields if "pin" in f and f != "dwo_has_pin"])

    def test_a_pin_cannot_be_reused_right_away(self):
        user = self.env.ref("base.user_demo")
        Pin = self.env["dwo.user.pin"]
        Pin.set_pin(user.id, "4826")
        with self.assertRaises(UserError):
            Pin.set_pin(user.id, "4826")
        Pin.set_pin(user.id, "7391")
        with self.assertRaises(UserError):
            Pin.set_pin(user.id, "4826")

    def test_wizard_needs_the_password_and_matching_pins(self):
        user = self.env.ref("base.user_demo")
        user.password = PASSWORD
        Wizard = self.env["dwo.pin.wizard"].with_user(user)
        wiz = Wizard.create({"mode": "self", "password": "wrong", "pin": "4826", "pin_confirm": "4826"})
        with self.assertRaises(UserError):
            wiz.action_confirm()
        wiz = Wizard.create({"mode": "self", "password": PASSWORD, "pin": "4826", "pin_confirm": "4827"})
        with self.assertRaises(UserError):
            wiz.action_confirm()
        wiz = Wizard.create({"mode": "self", "password": PASSWORD, "pin": "4826", "pin_confirm": "4826"})
        wiz.action_confirm()
        self.assertTrue(self.env["dwo.user.pin"].has_pin(user.id))
        self.assertFalse(wiz.pin or wiz.pin_confirm or wiz.password)   # erased at once
        self.assertTrue(user.with_user(user).dwo_has_pin)
        # nobody can set the PIN of someone else through the self mode
        admin = self.env.ref("base.user_admin")
        with self.assertRaises(AccessError):
            Wizard.create({"mode": "self", "user_id": admin.id, "password": PASSWORD, "pin": "7391", "pin_confirm": "7391"}).action_confirm()


@tagged("post_install", "-at_install")
class TestForgotPin(SessionCase):

    def _locked(self):
        self.set_pin()
        self.sign_in()
        self.rpc("/dwo/session/lock", url="/odoo/action-1/5")
        self.assertEqual(self.row().state, "locked")

    def test_forgot_with_password_then_new_pin(self):
        self._locked()
        res = self.post("/dwo/session/unlock_password", password="wrong")
        self.assertEqual(self.row().state, "locked")
        res = self.post("/dwo/session/unlock_password", password=PASSWORD)
        row = self.row()
        self.assertEqual(row.state, "locked")
        self.assertTrue(row.can_set_pin)                         # forced to choose a new PIN
        page = self.go("/dwo/session/locked").text
        self.assertIn("Choose a new PIN", page)
        # weak PIN, different PINs, the old PIN: refused
        self.post("/dwo/session/setpin", pin="1234", pin2="1234")
        self.assertTrue(self.row().can_set_pin)
        self.assertIn("too easy", self.go("/dwo/session/locked").text)
        self.post("/dwo/session/setpin", pin="7391", pin2="7392")
        self.post("/dwo/session/setpin", pin="4826", pin2="4826")
        self.assertEqual(self.row().state, "locked")
        self.post("/dwo/session/setpin", pin="7391", pin2="7391")
        self.assertEqual(self.row().state, "active")
        self.assertTrue(self.Pin._of(self.user.id).verify_pin("7391"))
        self.assertEqual(self.go("/dwo/session/resume").headers["Location"], "/odoo/action-1/5")

    def test_forgot_with_password_keeps_the_pin_when_not_forced(self):
        self.set("force_new_pin_after_relogin", "0")
        self._locked()
        self.post("/dwo/session/unlock_password", password=PASSWORD)
        self.assertEqual(self.row().state, "active")
        self.assertTrue(self.Pin._of(self.user.id).verify_pin("4826"))

    def test_wrong_passwords_count_like_wrong_pins(self):
        self._locked()
        self.set("pin_max_tries", "3")
        for _i in range(3):
            self.Pin._of(self.user.id).locked_until = False
            self.post("/dwo/session/unlock_password", password="wrong")
        self.assertEqual(self.row().state, "expired")

    def test_relogin_sends_to_the_login_page_and_forces_a_new_pin(self):
        self._locked()
        res = self.go("/dwo/session/relogin")
        self.assertEqual(res.status_code, 303)
        self.assertIn("/web/login", res.headers["Location"])
        self.assertIn("redirect=%2Fodoo%2Faction-1%2F5", res.headers["Location"])
        self.assertEqual(self.row().state, "expired")
        self.assertEqual(self.row().end_reason, "relogin")
        self.assertTrue(self.Pin._of(self.user.id).must_change)
        # the next sign-in lands on the "choose a PIN" page
        self.sign_in()
        row = self.row()
        self.assertEqual((row.state, row.can_set_pin), ("locked", True))

    def test_relogin_is_not_offered_when_switched_off(self):
        self.set("forgot_relogin", "0")
        self._locked()
        self.go("/dwo/session/relogin")
        self.assertEqual(self.row().state, "locked")
        self.assertNotIn("Sign in again", self.go("/dwo/session/locked").text)
        self.post("/dwo/session/unlock_password", password=PASSWORD)
        self.assertEqual(self.row().state, "locked")
        self.assertFalse(self.row().can_set_pin)

    def test_ask_the_administrator_to_reset(self):
        self.set("forgot_admin", "1")
        self._locked()
        self.post("/dwo/session/request_reset")
        request = self.env["dwo.session.request"].search([("user_id", "=", self.user.id)])
        self.assertEqual((request.kind, request.state), ("pin_reset", "pending"))
        self.assertIn("Waiting for an administrator", self.go("/dwo/session/locked").text)
        # asking twice does not create another request
        self.post("/dwo/session/request_reset")
        self.assertEqual(self.env["dwo.session.request"].search_count([("user_id", "=", self.user.id)]), 1)
        # an activity for the approvers and a toast message
        self.assertTrue(request.activity_ids)
        # the user cannot decide
        with self.assertRaises(AccessError):
            request.with_user(self.user).action_approve()
        # the administrator approves: the PIN is gone and the user must choose another one
        request.with_user(self.admin).action_approve()
        self.assertFalse(self.Pin._of(self.user.id).pin_hash)
        row = self.row()
        self.assertTrue(row.can_set_pin)
        self.assertEqual(self.beat(tab="t1")["can_set_pin"], True)
        self.post("/dwo/session/setpin", pin="7391", pin2="7391")
        self.assertEqual(self.row().state, "active")
        self.assertTrue(self.env["dwo.session.log"].search([("event", "=", "pin_reset"), ("user_id", "=", self.user.id)]))

    def test_old_pin_does_not_work_after_the_reset(self):
        self.set("forgot_admin", "1")
        self._locked()
        self.post("/dwo/session/request_reset")
        self.env["dwo.session.request"].search([("user_id", "=", self.user.id)]).with_user(self.admin).action_approve()
        self.post("/dwo/session/unlock", pin="4826")
        self.assertEqual(self.row().state, "locked")

    def test_reset_rejected_and_rate_limited(self):
        self.set("forgot_admin", "1")
        self.set("reset_request_limit", "2")
        self._locked()
        for _i in range(2):
            self.post("/dwo/session/request_reset")
            self.env["dwo.session.request"].search([("user_id", "=", self.user.id), ("state", "=", "pending")]).with_user(self.admin).action_reject()
        self.assertEqual(self.row().state, "locked")
        self.assertTrue(self.Pin._of(self.user.id).pin_hash)       # a rejected request changes nothing
        self.post("/dwo/session/request_reset")
        self.assertEqual(self.env["dwo.session.request"].search_count([("user_id", "=", self.user.id)]), 2)
        self.assertIn("Too many reset requests", self.go("/dwo/session/locked").text)

    def test_reset_request_is_off_when_switched_off(self):
        self.set("forgot_admin", "0")
        self._locked()
        self.post("/dwo/session/request_reset")
        self.assertFalse(self.env["dwo.session.request"].search([("user_id", "=", self.user.id)]))

    def test_email_code(self):
        self.set("forgot_otp", "1")
        self._locked()
        self.post("/dwo/session/send_otp")
        mail = self.env["mail.mail"].sudo().search([("email_to", "=", self.user.email)], order="id desc", limit=1)
        code = re.search(r"<b>(\d{6})</b>", mail.body_html).group(1)
        self.post("/dwo/session/verify_otp", code="000000" if code != "000000" else "111111")
        self.assertFalse(self.row().can_set_pin)
        self.post("/dwo/session/verify_otp", code=code)
        self.assertTrue(self.row().can_set_pin)
        self.post("/dwo/session/setpin", pin="7391", pin2="7391")
        self.assertEqual(self.row().state, "active")
        # the code is single use
        self.assertFalse(self.Pin._of(self.user.id).check_otp(code))

    def test_email_code_expires_and_is_limited(self):
        self.set("forgot_otp", "1")
        self._locked()
        pin = self.Pin._of(self.user.id)
        code = pin.new_otp()
        from datetime import timedelta
        from odoo import fields
        pin.otp_expires = fields.Datetime.now() - timedelta(minutes=1)
        self.assertFalse(pin.check_otp(code))
        pin.new_otp()
        pin.new_otp()
        with self.assertRaises(UserError):
            pin.new_otp()                                          # 3 codes per hour

    def test_temporary_pin_from_the_administrator(self):
        self.set("forgot_temp", "1")
        self._locked()
        wiz = self.env["dwo.pin.wizard"].with_user(self.admin).create({"mode": "temp", "user_id": self.user.id, "pin": "5917", "pin_confirm": "5917"})
        wiz.action_confirm()
        self.assertTrue(self.Pin._of(self.user.id).must_change)
        self.post("/dwo/session/unlock", pin="4826")                # the old PIN is gone
        self.assertEqual(self.row().state, "locked")
        self.post("/dwo/session/unlock", pin="5917")                # the temporary one leads to a new PIN
        self.assertTrue(self.row().can_set_pin)
        self.assertEqual(self.row().state, "locked")
        self.post("/dwo/session/setpin", pin="7391", pin2="7391")
        self.assertEqual(self.row().state, "active")
        self.assertFalse(self.Pin._of(self.user.id).must_change)
        # off by default, and only for administrators
        self.set("forgot_temp", "0")
        with self.assertRaises(UserError):
            self.env["dwo.pin.wizard"].with_user(self.admin).create({"mode": "temp", "user_id": self.user.id}).action_confirm()
        self.set("forgot_temp", "1")
        with self.assertRaises(AccessError):
            self.env["dwo.pin.wizard"].with_user(self.user).create({"mode": "temp", "user_id": self.admin.id}).action_confirm()

    def test_temporary_pin_can_be_generated(self):
        self.set("forgot_temp", "1")
        wiz = self.env["dwo.pin.wizard"].with_user(self.admin).create({"mode": "temp", "user_id": self.user.id})
        res = wiz.action_confirm()
        self.assertRegex(res["params"]["message"], r"Temporary PIN for .*: \d{6}\.")
        self.assertTrue(self.Pin._of(self.user.id).must_change)
