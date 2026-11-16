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

    def _dwo_render(self, content, filename):
        """Return ``{"type": "html"|"text"|"image", "data": <str|bytes>}``.

        ``html`` is sanitized by the core; ``image`` data are raw bytes
        (the mimetype goes in ``"mimetype"``). Raise ``UserError`` for a clean
        user-facing failure.
        """
        raise NotImplementedError

    def _dwo_engine_notice(self, extension):
        """A short, translated warning shown in a banner of the preview dialog for files of this extension
        (for example "old format, limited support"), or ``False`` for none. ``extension``: lowercase, no dot.
        Use ``self.env._()`` so the text follows the language of the user."""
        return False

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
