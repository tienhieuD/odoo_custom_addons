# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import html as html_lib
import re
from urllib.parse import quote, unquote

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request

from odoo.addons.dwo_attpreview_core.controllers.main import SOURCE_KEYS, AttPreviewController

from .. import text_tools

PARAM_AUTO = "dwo_attpreview_text.remote_images"
PARAM_HTTPS = "dwo_attpreview_text.remote_https_only"
WEB_URL = re.compile(r"""https?://[^\s"'<>\\)\]]+""", re.I)
MAX_ADDRESSES = 5000


def _normal(url):
    """An address in one spelling, so ``a b.png``, ``a%20b.png`` and ``&amp;`` in the file all match."""
    return quote(unquote(html_lib.unescape(url)), safe="/:?&=#%+@;,~!$*'()-._[]")


def web_addresses(text):
    """The web addresses written in a text (set, normalised): the only ones the picture route may fetch."""
    found = set()
    for match in WEB_URL.finditer(text):
        found.add(_normal(match.group(0).rstrip(".,;:!?")))
        if len(found) >= MAX_ADDRESSES:
            break
    return found


class TextPreviewController(http.Controller):
    # not a subclass of the core controller: the Mail module already is one, and two sibling subclasses would hide
    # each other's routes. The core helpers are used through an instance.

    @property
    def core(self):
        return AttPreviewController()


    @staticmethod
    def _dwo_text_settings():
        get = request.env["ir.config_parameter"].sudo().get_param
        return {"auto": bool(get(PARAM_AUTO)), "https_only": bool(get(PARAM_HTTPS))}

    @http.route("/dwo_attpreview_text/remote_settings", type="json", auth="user")
    def remote_settings(self):
        """Whether the viewer loads the web pictures of Markdown, HTML and notebooks by itself (Settings)."""
        return self._dwo_text_settings()

    @http.route("/dwo_attpreview_text/remote_image", type="http", auth="user", methods=["GET"])
    def remote_image(self, url=None, path=None, **source):
        """A picture written in a text file (Markdown, HTML, notebook), downloaded by the server (#87).

        The file is ``source`` (or the file at ``path`` inside it), with the same access checks as the preview.
        ``url`` must be an address written in that file, so this route cannot be used to fetch any other address.
        The guards of the download are in dwo_attpreview_core/remote_image.py."""
        source = {k: v for k, v in source.items() if k in SOURCE_KEYS}
        try:
            got = self.core._dwo_resolve_part(source, path) if path else self.core._dwo_source_file(source)
        except (TypeError, ValueError, UserError):
            got = None
        if got is None or not isinstance(url, str) or len(url) > 2048:
            raise request.not_found()
        name, content = got
        engine = request.env["dwo.attpreview.engine"]._dwo_find_engine(name)
        if engine is None or engine._name != "dwo.attpreview.engine.text":
            raise request.not_found()
        try:
            text, _encoding = text_tools.decode_text(content[: text_tools.MAX_TEXT_BYTES])
        except text_tools.TextError:
            raise request.not_found()
        if _normal(url) not in web_addresses(text):
            raise request.not_found()
        return self.core._dwo_picture_response(url, self._dwo_text_settings()["https_only"], name)
