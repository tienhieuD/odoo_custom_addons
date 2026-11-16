# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
"""Which files of an engine module are mirrored in ``static/catalog/<module>/`` (shared by the sync script
``odoo_appstore/_tools/sync_attpreview_catalog.py`` and the test ``tests/test_catalog.py``). Pure standard library.

An engine keeps its listing in ``<engine>/static/description/``. The catalog copy is what the Settings popup shows:
- ``index.html`` is mirrored when the engine has one; else the catalog keeps its own short description;
- every picture of ``static/description/`` is mirrored (same relative path), except icon, banner and large files.
"""
import hashlib
import os

IMAGE_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")
SKIP_NAMES = ("icon.png", "banner.png")
MAX_BYTES = 600 * 1024


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def source_files(engine_dir):
    """``{relative path: absolute path}`` of the files of ``<engine_dir>/static/description`` that the catalog mirrors."""
    root = os.path.join(engine_dir, "static", "description")
    found = {}
    for folder, _dirs, files in os.walk(root):
        for name in files:
            path = os.path.join(folder, name)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            if rel == "index.html":
                found[rel] = path
            elif name.lower().endswith(IMAGE_EXT) and name not in SKIP_NAMES and os.path.getsize(path) <= MAX_BYTES:
                found[rel] = path
    return dict(sorted(found.items()))


def catalog_files(catalog_dir):
    found = {}
    for folder, _dirs, files in os.walk(catalog_dir):
        for name in files:
            path = os.path.join(folder, name)
            found[os.path.relpath(path, catalog_dir).replace(os.sep, "/")] = path
    return found


def differences(engine_dir, catalog_dir):
    """What is out of sync: a list of ``(relative path, problem)``; empty when the catalog copy is up to date.
    The catalog's own ``index.html`` is not a problem when the engine has none."""
    source, copy = source_files(engine_dir), catalog_files(catalog_dir)
    problems = []
    for rel, path in source.items():
        if rel not in copy:
            problems.append((rel, "missing in the catalog"))
        elif sha256(path) != sha256(copy[rel]):
            problems.append((rel, "changed in the engine"))
    for rel in copy:
        if rel not in source and not (rel == "index.html" and "index.html" not in source):
            problems.append((rel, "no longer in the engine"))
    return problems
