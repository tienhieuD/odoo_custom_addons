# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
import base64
import logging
import mimetypes
from urllib.parse import urlencode

# Odoo 17: _() from odoo (env._ only exists from 18)
from odoo import _, http
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
from odoo.tools.mimetypes import guess_mimetype

_logger = logging.getLogger(__name__)

NATIVE_MIMES = (
    "application/pdf", "image/png", "image/jpeg", "image/gif", "image/webp",
    "image/avif", "image/bmp", "image/svg+xml",
)
NATIVE_PREFIXES = ("video/", "audio/")
# files inside a file (/dwo_attpreview/part_info): how deep, how many, and the keys of a source_ref
MAX_PART_DEPTH = 20  # an email in an email in an email...: far deeper than real mail, still bounded
MAX_PART_INDEX = 1_000_000  # an archive may list 100 000 files (dwo_attpreview_archive)
SOURCE_KEYS = ("attachment_id", "model", "res_id", "field", "filename_field")


class AttPreviewController(http.Controller):

    def _get_attachment(self, attachment_id):
        att = request.env["ir.attachment"].browse(int(attachment_id))
        try:
            # Odoo 17: check_access_rights + check_access_rule (check_access only exists from 18)
            att.check_access_rights("read")
            att.check_access_rule("read")
            att.name  # force the record rules / existence check
        except (AccessError, MissingError):
            return None
        return att

    @http.route("/dwo_attpreview/info", type="json", auth="user")
    def info(self, attachment_id):
        """Tell the viewer how to show an attachment: native, rendered or unsupported (with a ``reason``)."""
        att = self._get_attachment(attachment_id)
        if not att:
            return {"mode": "denied"}
        sudo = att.sudo()
        cache = request.env["dwo.attpreview.cache"]
        out = self._dwo_describe(
            sudo.name, sudo.mimetype or "",
            lambda engine: self._dwo_cache_values(cache._get_or_render(sudo, engine)),
            native_url="/web/content/%d?download=false" % att.id,
            download_url="/web/content/%d?download=true" % att.id,
        )
        # where the file comes from, for a viewer that previews files inside it (/dwo_attpreview/part_info)
        out["source_ref"] = {"attachment_id": att.id}
        return out

    # ------------------------------------------------------------------
    @staticmethod
    def _dwo_cache_values(rec):
        return {"error": rec.error, "result_type": rec.result_type, "mimetype": rec.mimetype, "data": rec.data}

    def _dwo_describe(self, name, mimetype, render, native_url, download_url):
        """Common answer of /info and /field_info. ``render(engine)`` returns the values of a cache entry."""
        base = {"name": name, "mimetype": mimetype}
        if mimetype in NATIVE_MIMES or mimetype.startswith(NATIVE_PREFIXES):
            # dialog width by kind of file: a sound needs no big window
            return dict(base, mode="native", url=native_url, width="narrow" if mimetype.startswith("audio/") else "wide")
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
                   download_url=download_url, width=getattr(engine, "_dwo_engine_dialog_width", "wide") or "wide")
        data = rec["data"] or b""
        if rec["result_type"] == "image":
            out["data_url"] = "data:%s;base64,%s" % (rec["mimetype"], data.decode())
        else:
            out["content"] = base64.b64decode(data).decode("utf-8", "replace")
        return out

    # --- binary fields ----------------------------------------------------
    # Odoo 18: type="json" (19 renamed it "jsonrpc")
    @http.route("/dwo_attpreview/field_info", type="json", auth="user")
    def field_info(self, model, res_id, field, filename_field=None):
        """Same answer as /info, for the file held by a binary field of any record.

        Allowed only to who can read the record and the field (and the file name field). The file of
        ``ir.attachment.datas`` is the attachment itself; a field stored as an attachment is rendered (and
        cached) through that attachment under the real file name; a field stored in its table is rendered in
        memory, within the size limit, and creates no attachment and no cache entry. The URLs of the answer
        are those of ``/web/content`` for the field, which checks the access again."""
        env = request.env
        denied = {"mode": "denied"}
        access = self._dwo_field_access(model, res_id, field, filename_field)
        if access is None:
            return denied
        record, fdef, name, filename_field = access
        if model == "ir.attachment" and field in ("datas", "raw"):
            return dict(self.info(record.id), attachment_id=record.id)

        params = {"model": model, "id": record.id, "field": field}
        if filename_field:
            params["filename_field"] = filename_field
        content_url = "/web/content?%s" % urlencode(params)
        native_url = content_url + "&download=false"
        download_url = content_url + "&download=true"
        extra = {"source": "field", "file_url": download_url, "download_url": download_url,
                 "source_ref": {"model": model, "res_id": record.id, "field": field,
                                "filename_field": filename_field or False}}
        cache = env["dwo.attpreview.cache"]

        if fdef.attachment:
            att = env["ir.attachment"].sudo().search([
                ("res_model", "=", model), ("res_id", "=", record.id), ("res_field", "=", field),
            ], limit=1)
            if not att:
                return dict(denied, mode="error", name=name, error=_("This field holds no file."))
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
                return {"error": _("File is larger than the preview limit (%s MB).", limit)}
            try:
                return dict(cache._dwo_render_values(engine, base64.b64decode(value), name), error=False)
            except UserError as e:
                return {"error": str(e.args[0])[:500]}
            except Exception as e:  # engine bug must not break the page
                _logger.exception("Preview engine %s failed on %s.%s of %s", engine._dwo_engine_code,
                                  model, field, record.id)
                return {"error": ("Render failed: %s" % type(e).__name__)[:500]}

        return dict(self._dwo_describe(name, mimetype, render, native_url, download_url), **extra)

    # --- access helpers ---------------------------------------------------
    @staticmethod
    def _dwo_field_access(model, res_id, field, filename_field=None):
        """``(record, field_definition, file_name, filename_field)`` when the user can read the binary field
        (and the file name field) of the record, else ``None``."""
        env = request.env
        if not isinstance(model, str) or model not in env:
            return None
        Model = env[model]
        fdef = Model._fields.get(field) if isinstance(field, str) else None
        if fdef is None or fdef.type != "binary":
            return None
        try:
            record = Model.browse(int(res_id))
            # Odoo 17: check_access_rights + check_access_rule (check_access only exists from 18)
            record.check_access_rights("read")
            record.check_access_rule("read")
            # Odoo 18/17: check_field_access_rights (19: _check_field_access)
            record.check_field_access_rights("read", [fdef.name])
            if not record.exists():
                return None
        except (AccessError, MissingError, ValueError, TypeError):
            return None
        name = ""
        ffield = Model._fields.get(filename_field) if isinstance(filename_field, str) else None
        if ffield is not None and ffield.type == "char":
            # Odoo 17: no Field.is_accessible (18) / _has_field_access (19); same rule: superuser, or no groups,
            # or the user is in them
            if not (env.su or not ffield.groups or Model.user_has_groups(ffield.groups)):
                return None
            name = record[filename_field] or ""
        else:
            filename_field = None
        return record, fdef, name or str(fdef.string or field), filename_field

    def _dwo_source_file(self, source):
        """``(file_name, raw_bytes)`` of an outer file the user may read, else ``None``. ``source``: the
        ``source_ref`` given by /info, /field_info or /part_info. Too large for a preview: ``UserError``."""
        if not isinstance(source, dict):
            return None
        env = request.env
        if source.get("attachment_id"):
            try:
                att = self._get_attachment(int(source["attachment_id"]))
            except (TypeError, ValueError):
                return None
            if not att:
                return None
            att = att.sudo()
            name, size, read = att.name, att.file_size, lambda: att.raw or b""
        else:
            access = self._dwo_field_access(source.get("model"), source.get("res_id"), source.get("field"),
                                            source.get("filename_field") or None)
            if access is None:
                return None
            record, fdef, name, _ffield = access
            if record._name == "ir.attachment" and fdef.name in ("datas", "raw"):
                return self._dwo_source_file({"attachment_id": record.id})
            if fdef.attachment:
                att = env["ir.attachment"].sudo().search([
                    ("res_model", "=", record._name), ("res_id", "=", record.id), ("res_field", "=", fdef.name),
                ], limit=1)
                if not att:
                    return None
                size, read = att.file_size, lambda: att.raw or b""
            else:
                value = record.sudo()[fdef.name] or b""
                size, read = len(value) * 3 // 4, lambda: base64.b64decode(value)
        max_mb = env["dwo.attpreview.cache"]._param("max_file_size_mb", 20)
        if size > max_mb * 1024 * 1024:
            raise UserError(_("File is larger than the preview limit (%s MB).", max_mb))
        return name, read()

    @staticmethod
    def _dwo_parse_path(path):
        """``"2/0"`` or ``[2, 0]`` -> ``[2, 0]`` (at most MAX_PART_DEPTH levels), else ``None``."""
        if isinstance(path, str):
            path = [p for p in path.split("/") if p != ""]
        if not isinstance(path, (list, tuple)) or not 0 < len(path) <= MAX_PART_DEPTH:
            return None
        try:
            out = [int(p) for p in path]
        except (TypeError, ValueError):
            return None
        return out if all(0 <= p < MAX_PART_INDEX for p in out) else None

    def _dwo_resolve_part(self, source, path):
        """``(file_name, raw_bytes)`` of the file at ``path`` inside the outer file ``source``, else ``None``
        (not allowed, bad path). Each level is opened by the engine of the file that holds it."""
        steps = self._dwo_parse_path(path)
        if steps is None:
            return None
        got = self._dwo_source_file(source)
        if got is None:
            return None
        Engine = request.env["dwo.attpreview.engine"]
        for index in steps:
            name, content = got
            engine = Engine._dwo_find_engine(name)
            extract = getattr(engine, "_dwo_extract_part", None)
            got = extract(content, name, index) if extract is not None else None
            if not got:
                raise UserError(_("This file could not be found inside %s.", name))
        return got

    @staticmethod
    def _dwo_part_mimetype(name, content):
        mimetype = guess_mimetype(content, default="")
        if not mimetype or mimetype == "application/octet-stream":
            mimetype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        return mimetype

    @staticmethod
    def _dwo_part_query(source, path):
        params = {k: v for k, v in source.items() if k in SOURCE_KEYS and v}
        params["path"] = "/".join(str(p) for p in path)
        return urlencode(params)

    # --- files inside a file (attachments of an email, ...) ----------------
    # Odoo 18: type="json" (19 renamed it "jsonrpc")
    @http.route("/dwo_attpreview/part_info", type="json", auth="user")
    def part_info(self, source, path):
        """Same answer as /info, for a file inside another file (an attachment of an email). ``source``: the
        ``source_ref`` of the outer file; ``path``: positions of the file, level by level (``"2"``, ``"2/0"``).
        The access to the outer file is checked as for /info or /field_info; the inner file is rendered in
        memory, within the size limit, and creates no attachment and no cache entry."""
        env = request.env
        steps = self._dwo_parse_path(path)
        if steps is None or not isinstance(source, dict):
            return {"mode": "denied"}
        source = {k: v for k, v in source.items() if k in SOURCE_KEYS}
        try:
            got = self._dwo_resolve_part(source, steps)
        except UserError as e:
            return {"mode": "error", "error": str(e.args[0])[:500]}
        except Exception as e:  # an engine bug must not break the page
            _logger.exception("Preview: cannot open part %s of %s", steps, source)
            return {"mode": "error", "error": ("Render failed: %s" % type(e).__name__)[:500]}
        if got is None:
            return {"mode": "denied"}
        name, content = got
        mimetype = self._dwo_part_mimetype(name, content)
        url = "/dwo_attpreview/part?%s" % self._dwo_part_query(source, steps)
        native_url, download_url = url + "&download=false", url + "&download=true"
        cache = env["dwo.attpreview.cache"]
        max_mb = cache._param("max_file_size_mb", 20)

        def render(engine):
            limit = engine._dwo_engine_max_size_mb or max_mb
            if len(content) > limit * 1024 * 1024:
                return {"error": _("File is larger than the preview limit (%s MB).", limit)}
            try:
                return dict(cache._dwo_render_values(engine, content, name), error=False)
            except UserError as e:
                return {"error": str(e.args[0])[:500]}
            except Exception as e:  # engine bug must not break the page
                _logger.exception("Preview engine %s failed on part %s of %s", engine._dwo_engine_code,
                                  steps, source)
                return {"error": ("Render failed: %s" % type(e).__name__)[:500]}

        out = self._dwo_describe(name, mimetype, render, native_url, download_url)
        return dict(out, source="part", file_url=download_url, download_url=download_url,
                    source_ref=dict(source, path="/".join(str(p) for p in steps)))

    @http.route("/dwo_attpreview/part", type="http", auth="user", methods=["GET"])
    def part(self, path=None, download=None, **source):
        """The bytes of a file inside another file, with the same checks as /part_info. Sent like
        /web/content (``nosniff``, ``Content-Security-Policy: default-src 'none'``); only the types the dialog
        shows itself (PDF, pictures, video, audio) may be shown inline, anything else is a download."""
        source = {k: v for k, v in source.items() if k in SOURCE_KEYS}
        try:
            got = self._dwo_resolve_part(source, path)
        except UserError:
            got = None
        except Exception:  # an engine bug must not give a server error page
            _logger.exception("Preview: cannot send part %s of %s", path, source)
            got = None
        if got is None:
            raise request.not_found()
        name, content = got
        mimetype = self._dwo_part_mimetype(name, content)
        inline = str(download).lower() not in ("1", "true") and (
            mimetype in NATIVE_MIMES or mimetype.startswith(NATIVE_PREFIXES))
        stream = http.Stream(type="data", data=content, mimetype=mimetype, download_name=name,
                             size=len(content), as_attachment=not inline, etag=False)
        return stream.get_response()
