# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
"""Engine catalog: the engine modules of the family, whether or not they are present in this database.

``data/engine_catalog.json`` lists them (module, name, file types, store page). The text and the pictures
shown in the Settings popup are in ``static/catalog/<module>/``; see ``docs/ENGINE_CATALOG.md``.
"""
import json

from odoo.tools import file_open

CATALOG_FILE = "dwo_attpreview_core/data/engine_catalog.json"
CATALOG_STATIC = "/dwo_attpreview_core/static/catalog/"


def load_catalog():
    """The catalog entries (a list of dicts)."""
    with file_open(CATALOG_FILE) as f:
        return json.load(f)

