# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
from odoo import api, models


class AttPreviewEngine(models.AbstractModel):
    """Mixin for engine modules.

    An engine module defines an AbstractModel with ``_inherit =
    'dwo.attpreview.engine'`` and sets the ``_dwo_engine_*`` attributes, then
    implements ``_dwo_render``. The core finds it automatically (no XML needed).
    An engine is on when its module is installed: there is no other switch.
    """

    _name = "dwo.attpreview.engine"
    _description = "Attachment Preview Engine (mixin)"

    _dwo_engine_code = None  # unique code, e.g. "word"
    _dwo_engine_label = None  # display name
    _dwo_engine_extensions = ()  # lowercase, without dot
    _dwo_engine_output = "html"  # html | text | image
    _dwo_engine_priority = 10  # lower wins when several engines match
    _dwo_engine_version = "1"  # bump to invalidate cached results
    _dwo_engine_max_size_mb = 0  # 0 = use the global limit
    # Size limits by group of file types: ``((key, extensions, default_mb), ...)``. The limit of a group is the
    # system parameter ``dwo_attpreview.max_mb.<key>`` (Settings, one field per group) or ``default_mb``. A file
    # whose extension is in no group uses ``_dwo_engine_max_size_mb`` or the global limit.
    _dwo_engine_size_groups = ()
    # width of the preview dialog for this engine's files: "wide" (95% of the window: sheets, documents, slides),
    # "medium" (about 1080px: emails, cards, text) or "narrow" (about 640px)
    _dwo_engine_dialog_width = "wide"

    def _dwo_render(self, content, filename):
        """Return ``{"type": "html"|"text"|"image"|"json", "data": <str|bytes|dict|list>}``.

        ``html`` is sanitized by the core; ``image`` data are raw bytes
        (the mimetype goes in ``"mimetype"``). ``json`` is for an engine that has its own
        viewer component (registry ``dwo_attpreview.viewers``): the data are stored as JSON and given to
        the viewer as a string; the Core does NOT sanitize it, so the engine must sanitize any HTML it puts
        inside (``odoo.tools.mail.html_sanitize``) and the viewer must show it in a sandboxed frame.
        Raise ``UserError`` for a clean user-facing failure.
        """
        raise NotImplementedError

    def _dwo_extract_part(self, content, filename, index):
        """For a container format (an email with attachments, ...): the inner file number ``index`` (an int, the
        position in the list of files the engine gave in its result) as ``(file_name, raw_bytes)``, or ``None``
        when there is no such file. The Core checks the access to the outer file first and previews the inner
        file in memory (no attachment, no cache), with the engines installed. Raise ``UserError`` for a clean
        user-facing failure."""
        return None

    def _dwo_engine_notice(self, extension):
        """A short, translated warning shown in a banner of the preview dialog for files of this extension
        (for example "old format, limited support"), or ``False`` for none. ``extension``: lowercase, no dot.
        Use ``self.env._()`` so the text follows the language of the user."""
        return False

    @api.model
    def _dwo_limit_for(self, engine, filename=""):
        """The size limit (MB) of ``engine`` for this file name: its group of file types, else the engine, else the
        global one. ``engine`` may be a plain object (an engine of the tests) without the groups."""
        name = filename or ""
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        param = self.env["ir.config_parameter"].sudo()
        for key, extensions, default in getattr(engine, "_dwo_engine_size_groups", ()):
            if ext in extensions:
                value = param.get_param("dwo_attpreview.max_mb." + key)
                try:
                    return int(value) if value not in (None, False, "") else default
                except ValueError:
                    return default
        return getattr(engine, "_dwo_engine_max_size_mb", 0) or self.env["dwo.attpreview.cache"]._param(
            "max_file_size_mb", 20)

    def _dwo_size_limit_mb(self, filename=""):
        return self._dwo_limit_for(self, filename)

    @api.model
    def _dwo_max_limit_mb(self):
        """The largest limit of any file type: a file above it is refused before an engine is chosen."""
        limits = [self.env["dwo.attpreview.cache"]._param("max_file_size_mb", 20)]
        for engine in self._dwo_get_engines():
            limits.append(self._dwo_limit_for(engine, ""))
            for _key, extensions, _default in getattr(engine, "_dwo_engine_size_groups", ()):
                limits.extend(self._dwo_limit_for(engine, "x." + ext) for ext in extensions)
        return max(limits)

    # --- registry lookup -------------------------------------------------
    @api.model
    def _dwo_get_engines(self):
        """The engines of the installed modules, best priority first (a list of model records)."""
        found = []
        for name, model in self.env.registry.items():
            if getattr(model, "_dwo_engine_code", None):
                found.append(self.env[name])
        return sorted(found, key=lambda e: (e._dwo_engine_priority, e._dwo_engine_code))

    @api.model
    def _dwo_find_engine(self, filename):
        """The engine that previews this file name (by extension), or ``None``."""
        name = filename or ""
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        if not ext:
            return None
        for engine in self._dwo_get_engines():
            if ext in engine._dwo_engine_extensions:
                return engine
        return None
