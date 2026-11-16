# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import os

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import Stream, request
from odoo.tools import file_path

MODULE = "dwo_attpreview_office"
# what the sandboxed viewer may load; nothing else of static/ is served by the asset route
ASSET_DIRS = ("viewer/", "lib/silurus/")
ASSET_EXT = (".html", ".css", ".js", ".mjs", ".wasm", ".json")


class AttPreviewOfficeController(http.Controller):

    @http.route("/dwo_attpreview_office/asset/<path:path>", type="http", auth="none", cors="*")
    def asset(self, path, **kw):
        """Files of the viewer (page, silurus scripts, wasm). The viewer runs in a sandboxed iframe without
        allow-same-origin, so its origin is opaque: the browser then demands a CORS header on every script
        and wasm it loads, which the plain /static route of Odoo does not send. Public (no session needed, the
        files are not secret), whitelisted directories and extensions, correct MIME (application/wasm)."""
        rel = os.path.normpath(path).replace(os.sep, "/")
        if (rel.startswith("..") or not rel.startswith(ASSET_DIRS)
                or not rel.lower().endswith(ASSET_EXT)):
            return request.not_found()
        try:
            stream = Stream.from_path("%s/static/%s" % (MODULE, rel), public=True)
        except (FileNotFoundError, ValueError, OSError):
            return request.not_found()
        response = stream.get_response(max_age=86400)
        response.headers["X-Content-Type-Options"] = "nosniff"
        if rel.endswith(".html"):
            # the iframe is sandboxed without allow-same-origin: its origin is opaque, so 'self' would match
            # nothing; name the origin of the server. Nothing may be fetched from anywhere else.
            origin = request.httprequest.host_url.rstrip("/")
            response.headers["Content-Security-Policy"] = (
                "sandbox allow-scripts; default-src 'none'; "
                "script-src %(o)s 'wasm-unsafe-eval' blob:; worker-src %(o)s blob: data:; "
                "connect-src %(o)s blob: data:; img-src data: blob:; font-src data: blob:; "
                "style-src %(o)s 'unsafe-inline'; frame-ancestors 'self'" % {"o": origin})
        return response

    @http.route("/dwo_attpreview_office/file/<int:attachment_id>", type="http", auth="user")
    def file(self, attachment_id, **kw):
        """The original file for the sandboxed viewer. Allowed only to who can read the attachment, only for the
        Office engine, and only if the Core accepted it (size limit, sane zip): same checks as the Core preview."""
        att = request.env["ir.attachment"].browse(attachment_id)
        try:
            att.check_access("read")
            att.name  # record rules / existence
        except (AccessError, MissingError):
            return request.make_response("Forbidden", status=403, headers=[("Content-Type", "text/plain")])
        sudo = att.sudo()
        engine = request.env["dwo.attpreview.engine"]._dwo_find_engine(sudo.name)
        if engine is None or engine._dwo_engine_code != "office":
            return request.make_response("Not found", status=404, headers=[("Content-Type", "text/plain")])
        rec = request.env["dwo.attpreview.cache"]._get_or_render(sudo, engine)
        if rec.error:
            return request.make_response(rec.error, status=422, headers=[("Content-Type", "text/plain")])
        return request.make_response(sudo.raw or b"", headers=[
            ("Content-Type", "application/octet-stream"),
            ("X-Content-Type-Options", "nosniff"),
            ("Cache-Control", "private, max-age=0, must-revalidate"),
        ])
