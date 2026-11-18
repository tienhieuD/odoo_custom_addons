# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import base64

from odoo import api, fields, models

from .. import data, tools

PRESET_BY_KEY = {p[0]: p for p in data.PRESETS}
D = data.DEFAULTS


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # The values are stored as ir.config_parameter ``dwo_login.<name>`` (global). They are read and written by
    # get_values / set_values below, not by ``config_parameter=`` (one code for every Odoo version, and a
    # False boolean is stored as "0" instead of removing the parameter, so a default of True stays unchecked).
    dwo_login_enabled = fields.Boolean(string="Apply the login page theme", default=D["enabled"])
    dwo_login_layout = fields.Selection(data.LAYOUTS, string="Layout", default=D["layout"])
    dwo_login_preset = fields.Selection([(p[0], p[1]) for p in data.PRESETS] + [("custom", "Custom")],
                                        string="Colour preset", default=D["preset"])
    dwo_login_primary = fields.Char(string="Main colour", default=D["primary"])
    dwo_login_button = fields.Char(string="Button colour", default=D["button"])
    dwo_login_text = fields.Char(string="Text colour", default=D["text"])
    dwo_login_card_bg = fields.Char(string="Form card colour", default=D["card_bg"])
    dwo_login_overlay = fields.Integer(string="Dark overlay on the image (%)", default=D["overlay"])
    dwo_login_blur = fields.Integer(string="Blur of the image (px)", default=D["blur"])
    dwo_login_bg_type = fields.Selection(data.BG_TYPES, string="Background", default=D["bg_type"])
    dwo_login_bg_image = fields.Selection([(g[0], g[1]) for g in data.GALLERY], string="Bundled image",
                                          default=D["bg_image"])
    dwo_login_bg_mode = fields.Selection(data.BG_MODES, string="Image rotation", default=D["bg_mode"])
    dwo_login_bg_pool = fields.Selection(data.POOLS, string="Images used by the rotation", default=D["bg_pool"])
    dwo_login_bg_color = fields.Char(string="Background colour", default=D["bg_color"])
    dwo_login_bg_grad_from = fields.Char(string="Gradient from", default=D["bg_grad_from"])
    dwo_login_bg_grad_to = fields.Char(string="Gradient to", default=D["bg_grad_to"])
    dwo_login_bg_grad_angle = fields.Integer(string="Gradient angle (degrees)", default=D["bg_grad_angle"])
    dwo_login_bg_upload = fields.Binary(string="My background image", attachment=False)
    dwo_login_logo_upload = fields.Binary(string="Logo of the login form", attachment=False)
    dwo_login_logo_size = fields.Selection(data.LOGO_SIZES, string="Logo size", default=D["logo_size"])
    dwo_login_favicon_upload = fields.Binary(string="Browser tab icon", attachment=False)
    dwo_login_page_title = fields.Char(string="Browser tab title", default=D["page_title"])
    dwo_login_welcome_title = fields.Char(string="Welcome title", default=D["welcome_title"])
    dwo_login_welcome_text = fields.Char(string="Welcome text", default=D["welcome_text"])
    dwo_login_intro_title = fields.Char(string="Intro panel title", default=D["intro_title"])
    dwo_login_intro_items = fields.Text(string="Intro panel points (one per line, up to 6)", default=D["intro_items"])
    dwo_login_footer_text = fields.Char(string="Footer text", default=D["footer_text"])
    dwo_login_pwd_toggle = fields.Boolean(string="Show / hide password button", default=D["pwd_toggle"])
    dwo_login_ann_enabled = fields.Boolean(string="Show the announcement", default=D["ann_enabled"])
    dwo_login_ann_html = fields.Text(string="Announcement (HTML)", default=D["ann_html"])
    dwo_login_ann_preview = fields.Html(string="Preview", compute="_compute_dwo_login_ann_preview", sanitize=False)
    dwo_login_ann_kind = fields.Selection(data.NOTICE_KINDS, string="Kind", default=D["ann_kind"])
    dwo_login_ann_pos = fields.Selection(data.NOTICE_POSITIONS, string="Position", default=D["ann_pos"])
    dwo_login_ann_dismiss = fields.Boolean(string="Visitors can close it", default=D["ann_dismiss"])
    dwo_login_ann_start = fields.Datetime(string="Show from")
    dwo_login_ann_end = fields.Datetime(string="Show until")

    # fields stored by name: dwo_login_<name> <-> dwo_login.<name>
    _DWO_LOGIN_PLAIN = [
        "enabled", "layout", "preset", "primary", "button", "text", "card_bg", "overlay", "blur", "bg_type",
        "bg_image", "bg_mode", "bg_pool", "bg_color", "bg_grad_from", "bg_grad_to", "bg_grad_angle", "logo_size",
        "page_title", "welcome_title", "welcome_text", "intro_title", "intro_items", "footer_text", "pwd_toggle",
        "ann_enabled", "ann_html", "ann_kind", "ann_pos", "ann_dismiss",
    ]
    _DWO_LOGIN_COLORS = {"primary": "primary", "button": "button", "text": "text", "card_bg": "card_bg",
                         "bg_color": "bg_color", "bg_grad_from": "bg_grad_from", "bg_grad_to": "bg_grad_to"}

    @api.depends("dwo_login_ann_html")
    def _compute_dwo_login_ann_preview(self):
        for rec in self:
            rec.dwo_login_ann_preview = tools.sanitize_notice(rec.dwo_login_ann_html)

    @api.onchange("dwo_login_preset")
    def _onchange_dwo_login_preset(self):
        preset = PRESET_BY_KEY.get(self.dwo_login_preset)
        if preset:
            _key, _label, primary, button, text, card = preset
            self.dwo_login_primary = primary
            self.dwo_login_button = button
            self.dwo_login_text = text
            self.dwo_login_card_bg = card

    # -- read / write the parameters ------------------------------------------------------------------------------
    @api.model
    def get_values(self):
        res = super().get_values()
        theme = self.env["dwo.login.theme"]
        for name in self._DWO_LOGIN_PLAIN:
            res["dwo_login_" + name] = theme.param(name)
        for name in ("ann_start", "ann_end"):
            raw = theme.param(name)
            res["dwo_login_" + name] = fields.Datetime.to_datetime(raw) if raw else False
        for kind in tools.IMAGE_LIMITS:
            att = self._dwo_login_attachment(kind)
            res["dwo_login_%s_upload" % kind] = base64.b64encode(tools.attachment_bytes(att)).decode() if att else False
        return res

    def set_values(self):
        super().set_values()
        icp = self.env["ir.config_parameter"].sudo()
        for name in self._DWO_LOGIN_PLAIN:
            value = self["dwo_login_" + name]
            default = D[name]
            if name in self._DWO_LOGIN_COLORS:
                value = tools.safe_color(value, default)
            elif name == "ann_html":
                value = str(tools.sanitize_notice(value))  # first layer: stored clean
            elif name == "overlay":
                value = tools.clamp_int(value, 0, 90, default)
            elif name == "blur":
                value = tools.clamp_int(value, 0, 20, default)
            elif name == "bg_grad_angle":
                value = tools.clamp_int(value, 0, 360, default)
            if isinstance(default, bool):
                value = "1" if value else "0"
            else:
                value = "" if value in (False, None) else str(value)
            tools.icp_set(icp, data.PARAM_PREFIX + name, value)
        for name in ("ann_start", "ann_end"):
            value = self["dwo_login_" + name]
            tools.icp_set(icp, data.PARAM_PREFIX + name, fields.Datetime.to_string(value) if value else False)
        for kind in tools.IMAGE_LIMITS:
            self._dwo_login_store_image(kind, self["dwo_login_%s_upload" % kind])

    # -- uploaded images ------------------------------------------------------------------------------------------
    @api.model
    def _dwo_login_attachment(self, kind):
        att_id = self.env["dwo.login.theme"].attachment_id(kind)
        att = self.env["ir.attachment"].sudo().browse(att_id).exists() if att_id else self.env["ir.attachment"]
        # only an attachment made by this module
        return att if att and att.res_model == "dwo.login.theme" and att.name == "dwo_login_" + kind else att.browse()

    def _dwo_login_store_image(self, kind, value):
        """Replace (new file), keep (same file) or remove (empty field) the uploaded image of this kind."""
        att = self._dwo_login_attachment(kind)
        key = "%s%s_att" % (data.PARAM_PREFIX, kind)
        icp = self.env["ir.config_parameter"].sudo()
        if not tools.binary_b64(value):
            if att:
                att.unlink()
            tools.icp_set(icp, key, False)
            return
        value = tools.binary_b64(value)
        if att and base64.b64decode(value) == tools.attachment_bytes(att):
            return  # unchanged: the page shows the stored, recompressed file
        raw, mimetype = tools.process_image(value, kind)  # raises UserError for a bad file
        new = self.env["ir.attachment"].sudo().create({
            "name": "dwo_login_" + kind,
            "raw": raw,
            "mimetype": mimetype,
            "res_model": "dwo.login.theme",
            "res_id": 0,
            "public": False,
        })
        if att:
            att.unlink()
        tools.icp_set(icp, key, str(new.id))
