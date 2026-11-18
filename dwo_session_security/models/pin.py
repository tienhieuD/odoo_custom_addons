# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import re
import secrets
from datetime import timedelta

from odoo import api, fields, models, release
from odoo.exceptions import AccessDenied, UserError

from .util import cfg, cfg_int, tr

WEAK = {
    "0000", "1111", "1234", "4321", "1212", "2580", "0852", "1004", "2000", "2001", "6969", "1122", "1313", "2222",
    "000000", "111111", "123456", "654321", "121212", "123123", "112233", "159753", "147258", "258369", "696969",
    "010203", "102030", "123321", "000001", "999999", "555555", "666666", "888888", "789456", "456789", "012345",
}


def weak_reason(pin):
    """Why a PIN is too easy to guess (or ``None``)."""
    if len(set(pin)) == 1:
        return "all digits are the same"
    if pin in WEAK:
        return "it is one of the most common PINs"
    digits = [int(c) for c in pin]
    steps = {digits[i + 1] - digits[i] for i in range(len(digits) - 1)}
    if steps in ({1}, {-1}):
        return "the digits are a sequence"
    half = len(pin) // 2
    if len(pin) % 2 == 0 and pin[:half] == pin[half:]:
        return "the PIN is a repeated pair"
    if len(pin) == 4 and pin[:2] == pin[2:][::-1] and pin[0] != pin[1]:
        return "the PIN is a mirror"
    if len(pin) == 4 and pin[:2] in ("19", "20") and 1900 <= int(pin) <= 2035:
        return "it looks like a year"
    return None


class DwoUserPin(models.Model):
    """The PIN of a user: only a salted hash is stored; no group can read this table (the code reads it as sudo)."""

    _name = "dwo.user.pin"
    _description = "Session lock PIN (hash only)"
    _log_access = True

    user_id = fields.Many2one("res.users", required=True, ondelete="cascade", index=True)
    pin_hash = fields.Char()
    previous_hash = fields.Char()
    length = fields.Integer()
    must_change = fields.Boolean(help="The next time the user unlocks, a new PIN has to be chosen.")
    fail_count = fields.Integer()
    locked_until = fields.Datetime()
    otp_hash = fields.Char()
    otp_expires = fields.Datetime()
    otp_tries = fields.Integer()
    otp_sent = fields.Text(help="Timestamps of the codes sent in the last hour (anti-abuse).")

    if release.version_info[0] >= 19:
        _user_uniq = models.Constraint("unique(user_id)", "One PIN record per user.")
    else:
        _sql_constraints = [("user_uniq", "unique(user_id)", "One PIN record per user.")]

    # -- helpers -------------------------------------------------------------------------------------------
    @api.model
    def _of(self, user, create=False):
        rec = self.sudo().search([("user_id", "=", int(user))], limit=1)
        if not rec and create:
            rec = self.sudo().create({"user_id": int(user)})
        return rec

    @api.model
    def has_pin(self, user):
        return bool(self._of(user).pin_hash)

    def _ctx(self):
        return self.env["res.users"]._crypt_context()

    @api.model
    def check_format(self, pin):
        """Raise ``UserError`` if the PIN is not acceptable."""
        pin = pin or ""
        if not re.fullmatch(r"\d+", pin):
            raise UserError(tr(self.env, "The PIN must contain digits only."))
        allowed = cfg(self.env, "pin_digits")
        lengths = {"4": (4,), "6": (6,)}.get(allowed, (4, 6))
        if len(pin) not in lengths:
            raise UserError(tr(self.env, "The PIN must have %s digits.", " or ".join(str(n) for n in lengths)))
        reason = weak_reason(pin)
        if reason:
            raise UserError(tr(self.env, "This PIN is too easy to guess (%s). Choose another one.", reason))

    def set_pin(self, user, pin, must_change=False, check=True):
        """Store the hash of a new PIN; the PIN is never kept. The previous one cannot be reused."""
        if check:
            self.check_format(pin)
        rec = self._of(user, create=True)
        if rec.pin_hash and self._ctx().verify(pin, rec.pin_hash):
            raise UserError(tr(self.env, "Choose a PIN that is different from the previous one."))
        if rec.previous_hash and self._ctx().verify(pin, rec.previous_hash):
            raise UserError(tr(self.env, "Choose a PIN that is different from the previous one."))
        rec.write({
            "previous_hash": rec.pin_hash or rec.previous_hash,
            "pin_hash": self._ctx().hash(pin),
            "length": len(pin),
            "must_change": must_change,
            "fail_count": 0,
            "locked_until": False,
            "otp_hash": False,
            "otp_expires": False,
        })
        return rec

    def clear_pin(self, user, must_change=True):
        rec = self._of(user)
        if rec:
            rec.write({"previous_hash": rec.pin_hash or rec.previous_hash, "pin_hash": False,
                       "must_change": must_change, "fail_count": 0, "locked_until": False})
        return rec

    def verify_pin(self, pin):
        """True if the PIN is right. Does not touch the counters."""
        self.ensure_one()
        if not self.pin_hash or not pin:
            return False
        try:
            return bool(self._ctx().verify(pin, self.pin_hash))
        except Exception:
            return False

    def register_failure(self):
        """Count a wrong attempt. Returns ``(left, cooldown_seconds, too_many)``."""
        self.ensure_one()
        maxi = cfg_int(self.env, "pin_max_tries") or 5
        count = self.fail_count + 1
        vals = {"fail_count": count}
        cooldown = 0
        if count < maxi and count % 3 == 0:
            cooldown = cfg_int(self.env, "pin_lock_sec") or 30
            vals["locked_until"] = fields.Datetime.now() + timedelta(seconds=cooldown)
        self.write(vals)
        return max(0, maxi - count), cooldown, count >= maxi

    def seconds_locked(self):
        self.ensure_one()
        if self.locked_until and self.locked_until > fields.Datetime.now():
            return int((self.locked_until - fields.Datetime.now()).total_seconds()) + 1
        return 0

    def register_success(self):
        self.write({"fail_count": 0, "locked_until": False})

    # -- one-time code by email ---------------------------------------------------------------------------
    def new_otp(self):
        """Create a 6-digit code, valid 10 minutes; at most 3 codes per hour. Returns the clear code (to mail it)."""
        self.ensure_one()
        now = fields.Datetime.now()
        recent = [t for t in (self.otp_sent or "").split(",") if t and fields.Datetime.to_datetime(t) > now - timedelta(hours=1)]
        if len(recent) >= 3:
            raise UserError(tr(self.env, "Too many codes were requested. Try again later."))
        code = "%06d" % secrets.randbelow(1000000)
        recent.append(fields.Datetime.to_string(now))
        self.write({"otp_hash": self._ctx().hash(code), "otp_expires": now + timedelta(minutes=10),
                    "otp_tries": 0, "otp_sent": ",".join(recent)})
        return code

    def check_otp(self, code):
        self.ensure_one()
        if not self.otp_hash or not self.otp_expires or self.otp_expires < fields.Datetime.now():
            return False
        if self.otp_tries >= 5:
            return False
        self.otp_tries += 1
        ok = bool(code) and self._ctx().verify(code.strip(), self.otp_hash)
        if ok:
            self.write({"otp_hash": False, "otp_expires": False, "otp_tries": 0})
        return ok
