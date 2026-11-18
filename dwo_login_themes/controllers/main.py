# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request

from .. import tools
from ..models.login_theme import IMAGE_KINDS


class DwoLoginImages(http.Controller):

    @http.route("/dwo_login/img/<string:kind>/<int:att_id>", type="http", auth="none", methods=["GET"],
                sitemap=False)
    def image(self, kind, att_id, **_kw):
        """The images of the settings (background, logo, tab icon) for the login page, which is public.

        It serves only the one attachment whose id is stored in the module settings for this kind, and only if that
        attachment was created by the module: no other record can be read through this route."""
        if kind not in IMAGE_KINDS or not request.db:
            raise NotFound()
        env = request.env(su=True)
        if env["dwo.login.theme"].attachment_id(kind) != att_id:
            raise NotFound()
        att = env["ir.attachment"].browse(att_id).exists()
        if not att or att.res_model != "dwo.login.theme" or att.name != "dwo_login_" + kind:
            raise NotFound()
        mimetype = att.mimetype if att.mimetype in ("image/webp", "image/png", "image/jpeg") else "application/octet-stream"
        return request.make_response(tools.attachment_bytes(att), headers=[
            ("Content-Type", mimetype),
            ("Cache-Control", "public, max-age=31536000, immutable"),  # the id changes with every new upload
            ("X-Content-Type-Options", "nosniff"),
        ])
