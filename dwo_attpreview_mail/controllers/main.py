# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import logging

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request

from odoo.addons.dwo_attpreview_core.controllers.main import SOURCE_KEYS, AttPreviewController

from ..parsers import remote

_logger = logging.getLogger(__name__)
PARAM_AUTO = "dwo_attpreview_mail.remote_images"
PARAM_HTTPS = "dwo_attpreview_mail.remote_https_only"


class MailPreviewController(AttPreviewController):

    @staticmethod
    def _dwo_mail_settings():
        get = request.env["ir.config_parameter"].sudo().get_param
        return {"auto": bool(get(PARAM_AUTO)), "https_only": bool(get(PARAM_HTTPS))}

    # Odoo 18: type="json" (19 renamed it "jsonrpc")
    @http.route("/dwo_attpreview_mail/remote_settings", type="json", auth="user")
    def remote_settings(self):
        """Whether the viewer loads the remote pictures of an email by itself (Settings, both on by default)."""
        return self._dwo_mail_settings()

    @http.route("/dwo_attpreview_mail/remote_image", type="http", auth="user", methods=["GET"])
    def remote_image(self, index=None, path=None, **source):
        """Picture number ``index`` of the body of an email, downloaded by the server (the image proxy, #79).

        The email is the file ``source`` (``source_ref`` of /info, /field_info) or the file at ``path`` inside it,
        with the same access checks as the preview. The browser only sends a position: the address comes from
        the email itself, so this route cannot be used to fetch any other address. See ``parsers/remote.py``
        for the guards of the download."""
        source = {k: v for k, v in source.items() if k in SOURCE_KEYS}
        try:
            index = int(index)
            got = self._dwo_resolve_part(source, path) if path else self._dwo_source_file(source)
        except (TypeError, ValueError, UserError):
            got = None
        if got is None:
            raise request.not_found()
        name, content = got
        engine = request.env["dwo.attpreview.engine"]._dwo_find_engine(name)
        if engine is None or engine._name != "dwo.attpreview.engine.mail":
            raise request.not_found()
        try:
            urls = engine._dwo_remote_images(content, name)
        except UserError:
            urls = []
        if not 0 <= index < len(urls):
            raise request.not_found()
        try:
            data, mimetype = remote.cached_picture(urls[index], self._dwo_mail_settings()["https_only"])
        except remote.RemoteImageError as e:
            _logger.info("Email preview: remote picture %s of %s not loaded (%s)", index, name, e)
            raise request.not_found()
        stream = http.Stream(type="data", data=data, mimetype=mimetype, size=len(data), etag=False,
                             max_age=3600, as_attachment=False)
        response = stream.get_response()
        response.headers["Referrer-Policy"] = "no-referrer"
        return response
