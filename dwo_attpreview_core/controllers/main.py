# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
import base64
import logging
import mimetypes
from urllib.parse import urlencode

from odoo import http
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
from odoo.tools.mimetypes import guess_mimetype

_logger = logging.getLogger(__name__)

NATIVE_MIMES = (
    "application/pdf", "image/png", "image/jpeg", "image/gif", "image/webp",
    "image/avif", "image/bmp", "image/svg+xml",
)
NATIVE_PREFIXES = ("video/", "audio/")


class AttPreviewController(http.Controller):

    def _get_attachment(self, attachment_id):
        att = request.env["ir.attachment"].browse(int(attachment_id))
        try:
            att.check_access("read")
            att.name  # force the record rules / existence check
        except (AccessError, MissingError):
            return None
        return att

    @http.route("/dwo_attpreview/info", type="jsonrpc", auth="user")
    def info(self, attachment_id):
        """Tell the viewer how to show an attachment: native, rendered or unsupported (with a ``reason``)."""
        att = self._get_attachment(attachment_id)
        if not att:
            return {"mode": "denied"}
        sudo = att.sudo()
        cache = request.env["dwo.attpreview.cache"]
        return self._dwo_describe(
            sudo.name, sudo.mimetype or "",
            lambda engine: self._dwo_cache_values(cache._get_or_render(sudo, engine)),
            native_url="/web/content/%d?download=false" % att.id,
            download_url="/web/content/%d?download=true" % att.id,
        )

    # ------------------------------------------------------------------
    @staticmethod
    def _dwo_cache_values(rec):
        return {"error": rec.error, "result_type": rec.result_type, "mimetype": rec.mimetype, "data": rec.data}

    def _dwo_describe(self, name, mimetype, render, native_url, download_url):
        """Common answer of /info and /field_info. ``render(engine)`` returns the values of a cache entry."""
        base = {"name": name, "mimetype": mimetype}
        if mimetype in NATIVE_MIMES or mimetype.startswith(NATIVE_PREFIXES):
            return dict(base, mode="native", url=native_url)
        engine = request.env["dwo.attpreview.engine"]._dwo_find_engine(name)
        if engine is None:
            return dict(base, mode="unsupported", reason="no_engine")
        rec = render(engine)
        ext = name.rsplit(".", 1)[-1].lower() if "." in (name or "") else ""
        # optional warning of the engine for this extension (shown as a banner in the dialog)
        notice = engine._dwo_engine_notice(ext) or False
        if rec["error"]:
            return dict(base, mode="error", error=rec["error"], notice=notice)
        out = dict(base, mode="rendered", type=rec["result_type"], engine=engine._dwo_engine_code, notice=notice,
                   download_url=download_url)
        data = rec["data"] or b""
        if rec["result_type"] == "image":
            out["data_url"] = "data:%s;base64,%s" % (rec["mimetype"], data.decode())
        else:
            out["content"] = base64.b64decode(data).decode("utf-8", "replace")
        return out

    # --- binary fields ----------------------------------------------------
    @http.route("/dwo_attpreview/field_info", type="jsonrpc", auth="user")
    def field_info(self, model, res_id, field, filename_field=None):
        """Same answer as /info, for the file held by a binary field of any record.

        Allowed only to who can read the record and the field (and the file name field). The file of
        ``ir.attachment.datas`` is the attachment itself; a field stored as an attachment is rendered (and
        cached) through that attachment under the real file name; a field stored in its table is rendered in
        memory, within the size limit, and creates no attachment and no cache entry. The URLs of the answer
        are those of ``/web/content`` for the field, which checks the access again."""
        env = request.env
        denied = {"mode": "denied"}
        if not isinstance(model, str) or model not in env:
            return denied
        Model = env[model]
        fdef = Model._fields.get(field) if isinstance(field, str) else None
        if fdef is None or fdef.type != "binary":
            return denied
        try:
            record = Model.browse(int(res_id))
            record.check_access("read")
            record._check_field_access(fdef, "read")
            if not record.exists():
                return denied
        except (AccessError, MissingError, ValueError, TypeError):
            return denied
        if model == "ir.attachment" and field in ("datas", "raw"):
            return dict(self.info(record.id), attachment_id=record.id)

        name = ""
        ffield = Model._fields.get(filename_field) if isinstance(filename_field, str) else None
        if ffield is not None and ffield.type == "char":
            if not record._has_field_access(ffield, "read"):
                return denied
            name = record[filename_field] or ""
        else:
            filename_field = None
        name = name or str(fdef.string or field)
        params = {"model": model, "id": record.id, "field": field}
        if filename_field:
            params["filename_field"] = filename_field
        content_url = "/web/content?%s" % urlencode(params)
        native_url = content_url + "&download=false"
        download_url = content_url + "&download=true"
        extra = {"source": "field", "file_url": download_url, "download_url": download_url}
        cache = env["dwo.attpreview.cache"]

        if fdef.attachment:
            att = env["ir.attachment"].sudo().search([
                ("res_model", "=", model), ("res_id", "=", record.id), ("res_field", "=", field),
            ], limit=1)
            if not att:
                return dict(denied, mode="error", name=name, error=env._("This field holds no file."))
            out = self._dwo_describe(
                name, att.mimetype or "",
                lambda engine: self._dwo_cache_values(cache._get_or_render(att, engine, name)),
                native_url, download_url)
            return dict(out, **extra)

        # stored in the table of the model (attachment=False): base64 in a bytea column, or computed
        value = record.sudo()[field] or b""
        size = len(value) * 3 // 4
        max_mb = cache._param("max_file_size_mb", 20)
        mimetype = ""
        if size <= max_mb * 1024 * 1024:
            raw = base64.b64decode(value)
            mimetype = guess_mimetype(raw, default="")
        if not mimetype or mimetype == "application/octet-stream":
            mimetype = mimetypes.guess_type(name)[0] or "application/octet-stream"

        def render(engine):
            limit = engine._dwo_engine_max_size_mb or max_mb
            if size > limit * 1024 * 1024:
                return {"error": env._("File is larger than the preview limit (%s MB).", limit)}
            try:
                return dict(cache._dwo_render_values(engine, base64.b64decode(value), name), error=False)
            except UserError as e:
                return {"error": str(e.args[0])[:500]}
            except Exception as e:  # engine bug must not break the page
                _logger.exception("Preview engine %s failed on %s.%s of %s", engine._dwo_engine_code,
                                  model, field, record.id)
                return {"error": ("Render failed: %s" % type(e).__name__)[:500]}

        return dict(self._dwo_describe(name, mimetype, render, native_url, download_url), **extra)
