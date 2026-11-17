# -*- coding: utf-8 -*-
# Copyright 2026 DuoTEK. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
"""Serving the files of a sandboxed viewer page. Shared by the viewer modules (3D, CAD, BIM, DWG)."""
import os

from odoo.http import Stream, request

ASSET_EXT = (".html", ".css", ".js", ".mjs", ".wasm", ".json", ".woff", ".ttf")


def viewer_csp(origin, extra_script=""):
    """CSP of a viewer page: no network, the origin of this server only for scripts (and wasm), no inline script.
    The iframe is sandboxed without allow-same-origin, so its origin is opaque: 'self' would match nothing."""
    return (
        "sandbox allow-scripts; default-src 'none'; "
        "script-src %(o)s 'wasm-unsafe-eval' blob:%(x)s; worker-src %(o)s blob: data:; "
        "connect-src %(o)s blob: data:; img-src data: blob:; font-src data: blob:; "
        "style-src %(o)s 'unsafe-inline'; frame-ancestors 'self'" % {"o": origin, "x": extra_script})


def serve_asset(module, path, allowed_dirs):
    """The file ``static/<path>`` of ``module`` when ``path`` is in one of ``allowed_dirs`` (and has a known
    extension), else a 404. Public (no session): the files are not secret; the viewer page runs in a sandbox
    without allow-same-origin, so the browser demands a CORS header (set by the route, ``cors="*"``)."""
    rel = os.path.normpath(path).replace(os.sep, "/")
    if rel.startswith("..") or not rel.startswith(tuple(allowed_dirs)) or not rel.lower().endswith(ASSET_EXT):
        return request.not_found()
    try:
        stream = Stream.from_path("%s/static/%s" % (module, rel), public=True)
    except (FileNotFoundError, ValueError, OSError):
        return request.not_found()
    response = stream.get_response(max_age=86400)
    response.headers["X-Content-Type-Options"] = "nosniff"
    if rel.endswith(".html"):
        response.headers["Content-Security-Policy"] = viewer_csp(request.httprequest.host_url.rstrip("/"))
    return response


def serve_file(attachment_id, engine_code):
    """The original file for a sandboxed viewer. Allowed only to who can read the attachment, only for the engine
    ``engine_code``, and only if the Core accepted it (size limit, content checks of the engine): the same checks as
    the Core preview."""
    from odoo.exceptions import AccessError, MissingError

    def plain(text, status):
        return request.make_response(text, status=status, headers=[("Content-Type", "text/plain")])

    att = request.env["ir.attachment"].browse(attachment_id)
    try:
        att.check_access("read")
        att.name  # record rules / existence
    except (AccessError, MissingError):
        return plain("Forbidden", 403)
    sudo = att.sudo()
    engine = request.env["dwo.attpreview.engine"]._dwo_find_engine(sudo.name)
    if engine is None or engine._dwo_engine_code != engine_code:
        return plain("Not found", 404)
    rec = request.env["dwo.attpreview.cache"]._get_or_render(sudo, engine)
    if rec.error:
        return plain(rec.error, 422)
    return request.make_response(sudo.raw or b"", headers=[
        ("Content-Type", "application/octet-stream"),
        ("X-Content-Type-Options", "nosniff"),
        ("Cache-Control", "private, max-age=0, must-revalidate"),
    ])
