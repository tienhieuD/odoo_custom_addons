# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import hashlib
import random
from datetime import datetime

import pytz
from markupsafe import Markup

from odoo import api, fields, models
from odoo.http import request

from .. import data, tools

IMAGE_KINDS = ("bg", "logo", "favicon")
BASE = "/dwo_login_themes/static/src/img/bg/"


class DwoLoginTheme(models.AbstractModel):
    """Reads the settings (``dwo_login.*`` ir.config_parameter) for the login page.

    Only these keys are read, always as superuser, and only the values that the page needs are returned."""
    _name = "dwo.login.theme"
    _description = "Login page theme"

    # -- parameters -----------------------------------------------------------------------------------------------
    @api.model
    def param(self, name):
        """The value of ``dwo_login.<name>`` as a string; the default when the parameter is missing."""
        default = data.DEFAULTS[name]
        raw = tools.icp_get(self.env["ir.config_parameter"].sudo(), data.PARAM_PREFIX + name)
        if raw is False or raw is None:
            return default
        if isinstance(default, bool):
            return raw in ("1", "True", "true")
        if isinstance(default, int):
            try:
                return int(raw)
            except ValueError:
                return default
        return raw

    @api.model
    def attachment_id(self, kind):
        """The id of the uploaded image of this kind stored in the settings, 0 when there is none."""
        raw = tools.icp_get(self.env["ir.config_parameter"].sudo(), "%s%s_att" % (data.PARAM_PREFIX, kind))
        try:
            return int(raw or 0)
        except ValueError:
            return 0

    @api.model
    def image_url(self, kind):
        att_id = self.attachment_id(kind)
        return "/dwo_login/img/%s/%d" % (kind, att_id) if att_id else ""

    # -- the announcement -----------------------------------------------------------------------------------------
    @api.model
    def notice_active(self, now=None):
        """The announcement to show now, as a dict, or ``False`` (switch off, empty, before the start or after the end)."""
        if not self.param("ann_enabled"):
            return False
        body = tools.sanitize_notice(self.param("ann_html"))  # second layer: the parameter may have been edited by hand
        if not body.strip():
            return False
        now = now or fields.Datetime.now()
        for name, before in (("ann_start", True), ("ann_end", False)):
            raw = self.param(name)
            if not raw:
                continue
            try:
                limit = fields.Datetime.to_datetime(raw)
            except (ValueError, TypeError):
                continue
            if limit and ((before and now < limit) or (not before and now > limit)):
                return False
        kind = self.param("ann_kind")
        pos = self.param("ann_pos")
        return {
            "html": body,
            "kind": kind if kind in dict(data.NOTICE_KINDS) else "info",
            "pos": pos if pos in dict(data.NOTICE_POSITIONS) else "above",
            "dismiss": bool(self.param("ann_dismiss")),
            "key": hashlib.sha1(str(body).encode()).hexdigest()[:12],
        }

    # -- backgrounds ----------------------------------------------------------------------------------------------
    @api.model
    def _pool_keys(self, pool):
        if pool == "light":
            return [g[0] for g in data.GALLERY if g[2] in ("morning", "day")]
        if pool == "warm":
            return [g[0] for g in data.GALLERY if g[2] in ("morning", "evening")]
        if pool == "dark":
            return [g[0] for g in data.GALLERY if g[2] == "night"]
        if pool in ("soft", "geo"):
            return [g[0] for g in data.GALLERY if g[3] == pool]
        return list(data.GALLERY_KEYS)

    @api.model
    def _time_of_day(self, now_utc=None):
        company = self.env["res.company"].sudo().search([], limit=1)
        try:
            tz = pytz.timezone(company.partner_id.tz or "UTC")
        except pytz.UnknownTimeZoneError:
            tz = pytz.utc
        hour = (now_utc or datetime.now(pytz.utc)).astimezone(tz).hour
        if 5 <= hour < 10:
            return "morning"
        if 10 <= hour < 16:
            return "day"
        if 16 <= hour < 20:
            return "evening"
        return "night"

    @api.model
    def background_images(self, now_utc=None):
        """URLs of the images of the page background (one, or several for the slideshow)."""
        bg_type = self.param("bg_type")
        if bg_type == "upload":
            url = self.image_url("bg")
            if url:
                return [url]
            bg_type = "gallery"  # the upload is gone: fall back to the bundled image
        if bg_type != "gallery":
            return []
        mode = self.param("bg_mode")
        single = self.param("bg_image")
        if single not in data.GALLERY_KEYS:
            single = data.DEFAULTS["bg_image"]
        pool = self._pool_keys(self.param("bg_pool"))
        if mode == "random":
            keys = [random.choice(pool)]
        elif mode == "daily":
            keys = [pool[datetime.now(pytz.utc).timetuple().tm_yday % len(pool)]]
        elif mode == "timeofday":
            group = [g[0] for g in data.GALLERY if g[2] == self._time_of_day(now_utc)]
            keys = [group[datetime.now(pytz.utc).timetuple().tm_yday % len(group)]]
        elif mode == "slideshow":
            start = random.randrange(len(pool))
            keys = [pool[(start + i) % len(pool)] for i in range(min(4, len(pool)))]
        else:
            keys = [single]
        return [BASE + key + ".webp" for key in keys]

    # -- the whole context ----------------------------------------------------------------------------------------
    @api.model
    def get_context(self):
        """What the login templates need. ``{}`` when the theme and the announcement are both off."""
        if request and getattr(request, "_dwo_login_ctx", None) is not None:
            return request._dwo_login_ctx
        ctx = self._build_context()
        if request:
            request._dwo_login_ctx = ctx
        return ctx

    @api.model
    def _build_context(self):
        notice = self.notice_active()
        theme_on = self.param("enabled")
        hide_brand = bool(self.param("hide_brand"))
        if not theme_on and not notice:
            return {"hide_brand": True} if hide_brand else {}
        # the login form page (web.login) draws the announcement itself; the layout draws it on the other pages
        form_page = bool(request) and request.httprequest.path.rstrip("/") == "/web/login"
        ctx = {"notice": notice, "theme": bool(theme_on), "form_page": form_page, "hide_brand": hide_brand}
        if not theme_on:
            return ctx
        layout = self.param("layout")
        if layout not in dict(data.LAYOUTS):
            layout = data.DEFAULTS["layout"]
        images = self.background_images()
        bg_type = self.param("bg_type")
        logo_size = self.param("logo_size")
        if logo_size not in dict(data.LOGO_SIZES):
            logo_size = "medium"
        intro_items = [line.strip() for line in (self.param("intro_items") or "").splitlines() if line.strip()][:6]
        d = data.DEFAULTS
        css = {
            "primary": tools.safe_color(self.param("primary"), d["primary"]),
            "button": tools.safe_color(self.param("button"), d["button"]),
            "text": tools.safe_color(self.param("text"), d["text"]),
            "card-bg": tools.safe_color(self.param("card_bg"), d["card_bg"]),
            "overlay": "%.2f" % (tools.clamp_int(self.param("overlay"), 0, 90, d["overlay"]) / 100.0),
            "blur": "%dpx" % tools.clamp_int(self.param("blur"), 0, 20, d["blur"]),
            "page-bg": tools.safe_color(self.param("bg_color"), d["bg_color"]),
            "grad-from": tools.safe_color(self.param("bg_grad_from"), d["bg_grad_from"]),
            "grad-to": tools.safe_color(self.param("bg_grad_to"), d["bg_grad_to"]),
            "grad-angle": "%ddeg" % tools.clamp_int(self.param("bg_grad_angle"), 0, 360, d["bg_grad_angle"]),
        }
        style = ".dwo_lc{%s}" % ";".join("--dwo-%s:%s" % item for item in css.items())
        ctx.update({
            "root_class": "dwo_lc dwo_l_%s dwo_logo_%s dwo_bgt_%s%s%s" % (
                layout, logo_size, bg_type if bg_type in dict(data.BG_TYPES) else "gallery",
                " dwo_has_aside" if (self.param("intro_title") or intro_items) else "",
                " dwo_card_dark" if tools.is_dark_color(css["card-bg"]) else ""),
            "style": Markup("<style>%s</style>") % Markup(style),
            "images": images,
            "logo_url": self.image_url("logo"),
            "favicon_url": self.image_url("favicon"),
            "welcome_title": self.param("welcome_title"),
            "welcome_text": self.param("welcome_text"),
            "intro_title": self.param("intro_title"),
            "intro_items": intro_items,
            "footer_text": self.param("footer_text"),
            "page_title": self.param("page_title"),
            "pwd_toggle": bool(self.param("pwd_toggle")),
        })
        return ctx
