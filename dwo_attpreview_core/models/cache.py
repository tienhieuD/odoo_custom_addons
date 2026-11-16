# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
import base64
import json
import logging
import time

# Odoo 17: _() from odoo (env._ only exists from 18)
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.mail import html_sanitize

_logger = logging.getLogger(__name__)

ERROR_TTL_SECONDS = 600
# Defaults of the daily clean-up. Not shown in Settings; the system parameters
# ``dwo_attpreview.cache_ttl_days`` and ``dwo_attpreview.cache_max_mb`` override them when set.
CACHE_TTL_DAYS = 30
CACHE_MAX_MB = 500


class AttPreviewCache(models.Model):
    """Rendered result of an attachment. Direct access is denied to users
    (see ir.model.access.csv); the controller reads it with sudo after checking
    read access on the original attachment."""

    _name = "dwo.attpreview.cache"
    _description = "Attachment Preview Cache"
    _order = "last_access desc, id desc"

    attachment_id = fields.Many2one("ir.attachment", required=True, ondelete="cascade", index=True)
    checksum = fields.Char(required=True)
    engine_code = fields.Char(required=True, index=True)
    engine_version = fields.Char(required=True)
    result_type = fields.Char()
    mimetype = fields.Char()
    data = fields.Binary(attachment=True)
    data_size = fields.Integer()
    error = fields.Char()
    last_access = fields.Datetime(default=fields.Datetime.now)

    # Odoo 18: _sql_constraints (models.Constraint only exists from 19)
    _sql_constraints = [
        ("att_engine_uniq", "unique(attachment_id, engine_code)", "One cache entry per attachment and engine."),
    ]

    # ------------------------------------------------------------------
    @api.model
    def _param(self, key, default):
        return int(self.env["ir.config_parameter"].sudo().get_param("dwo_attpreview." + key, default))

    @api.model
    def _get_or_render(self, attachment, engine, filename=None):
        """Return a cache record (valid or error) for attachment/engine. Needs sudo env.
        ``filename``: real name of the file when it differs from the attachment name (the attachment of a binary
        field is named after the field); it is what the engine sees."""
        self = self.sudo()
        code = engine._dwo_engine_code
        version = str(engine._dwo_engine_version)
        rec = self.search([("attachment_id", "=", attachment.id), ("engine_code", "=", code)], limit=1)
        if rec:
            stale = rec.checksum != (attachment.checksum or "") or rec.engine_version != version
            if rec.error and time.time() - fields.Datetime.to_datetime(rec.write_date).timestamp() > ERROR_TTL_SECONDS:
                stale = True
            if not stale:
                rec.last_access = fields.Datetime.now()
                return rec
            rec.unlink()
        vals = {
            "attachment_id": attachment.id,
            "checksum": attachment.checksum or "",  # an empty file has no checksum
            "engine_code": code,
            "engine_version": version,
        }
        try:
            result = self._render(attachment, engine, filename)
            vals.update(result)
        except UserError as e:
            vals["error"] = str(e.args[0])[:500]
        except Exception as e:  # engine bug must not break the page
            _logger.exception("Preview engine %s failed on attachment %s", code, attachment.id)
            vals["error"] = ("Render failed: %s" % type(e).__name__)[:500]
        return self.create(vals)

    @api.model
    def _render(self, attachment, engine, filename=None):
        max_mb = engine._dwo_engine_max_size_mb or self._param("max_file_size_mb", 20)
        if attachment.file_size > max_mb * 1024 * 1024:
            raise UserError(_("File is larger than the preview limit (%s MB).", max_mb))
        content = attachment.raw or b""
        return self._dwo_render_values(engine, content, filename or attachment.name)

    @api.model
    def _dwo_render_values(self, engine, content, filename):
        """Run the engine on raw bytes and return the values of a cache entry (sanitized, base64). Also used
        without a cache entry for a binary field that is not stored as an attachment."""
        res = engine._dwo_render(content, filename)
        rtype = res.get("type")
        data = res.get("data")
        if rtype == "html":
            data = html_sanitize(data or "", sanitize_attributes=True, sanitize_style=True,
                                 sanitize_form=True, strip_classes=False).encode()
        elif rtype == "text":
            data = (data or "").encode()
        elif rtype == "image":
            data = data or b""
        elif rtype == "json":
            # for an engine with its own viewer; the engine sanitizes the HTML it puts inside (see _dwo_render)
            data = json.dumps(data if data is not None else {}, ensure_ascii=False).encode()
        else:
            raise UserError(_("Engine returned an unsupported output type."))
        return {
            "result_type": rtype,
            "mimetype": res.get("mimetype") or {
                "html": "text/html", "text": "text/plain", "json": "application/json"}.get(rtype),
            "data": base64.b64encode(data),
            "data_size": len(data),
        }

    # --- maintenance --------------------------------------------------
    @api.model
    def _cron_cleanup(self):
        cache = self.sudo()
        ttl = cache._param("cache_ttl_days", CACHE_TTL_DAYS)
        limit = fields.Datetime.subtract(fields.Datetime.now(), days=ttl)
        cache.search([("last_access", "<", limit)]).unlink()
        # results of an engine whose module is no longer installed
        live = [e._dwo_engine_code for e in self.env["dwo.attpreview.engine"]._dwo_get_engines()]
        cache.search([("engine_code", "not in", live)]).unlink()
        cap = cache._param("cache_max_mb", CACHE_MAX_MB) * 1024 * 1024
        total = 0
        for rec in cache.search([], order="last_access desc, id desc"):
            total += rec.data_size
            if total > cap:
                rec.unlink()
