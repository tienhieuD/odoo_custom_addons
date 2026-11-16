# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
import json
import os
import tempfile

from odoo.addons.dwo_attpreview_core import catalog, catalog_sync
from odoo.modules.module import get_module_path
from odoo.tests import TransactionCase, tagged
from odoo.tools import file_path


@tagged("post_install", "-at_install")
class TestAttPreviewCatalog(TransactionCase):

    def test_01_catalog_json_is_valid_and_has_a_description_folder(self):
        for entry in catalog.load_catalog():
            self.assertLessEqual({"module", "name", "extensions", "store_url"}, set(entry))
            folder = file_path("dwo_attpreview_core/static/catalog/%s" % entry["module"])
            self.assertTrue(os.path.isfile(os.path.join(folder, "index.html")), entry["module"])

    def test_02_catalog_html_is_static_and_safe(self):
        """The popup shows these files in a sandboxed frame, but they must not need scripts or remote content anyway."""
        for entry in catalog.load_catalog():
            folder = file_path("dwo_attpreview_core/static/catalog/%s" % entry["module"])
            with open(os.path.join(folder, "index.html"), encoding="utf-8") as f:
                html = f.read().lower()
            for bad in ("<script", "http://", "https://", "javascript:", " onerror", " onclick", "<iframe"):
                self.assertNotIn(bad, html, "%s: %s" % (entry["module"], bad))

    def test_03_catalog_copy_is_in_sync_with_each_engine(self):
        """Run ``odoo_appstore/_tools/sync_attpreview_catalog.py`` when this fails (docs/ENGINE_CATALOG.md).
        An engine that is not in the addons path of this installation is skipped: nothing to compare."""
        checked = 0
        for entry in catalog.load_catalog():
            engine_dir = get_module_path(entry["module"], display_warning=False)
            if not engine_dir:
                continue
            checked += 1
            catalog_dir = file_path("dwo_attpreview_core/static/catalog/%s" % entry["module"])
            self.assertEqual(catalog_sync.differences(engine_dir, catalog_dir), [],
                             "static/catalog/%s is out of sync with the engine: run the sync script" % entry["module"])
        if not checked:
            self.skipTest("no engine module in the addons path")

    def test_04_sync_check_detects_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            engine, cat = os.path.join(tmp, "engine"), os.path.join(tmp, "cat")
            os.makedirs(os.path.join(engine, "static", "description", "screenshots"))
            os.makedirs(os.path.join(cat, "screenshots"))
            files = {"index.html": b"<p>a</p>", "screenshots/s.png": b"png1", "icon.png": b"icon"}
            for rel, data in files.items():
                with open(os.path.join(engine, "static", "description", rel), "wb") as f:
                    f.write(data)
            self.assertEqual(set(catalog_sync.source_files(engine)), {"index.html", "screenshots/s.png"})
            self.assertEqual(sorted(r for r, _p in catalog_sync.differences(engine, cat)),
                             ["index.html", "screenshots/s.png"])
            for rel in ("index.html", "screenshots/s.png"):
                with open(os.path.join(cat, rel), "wb") as f:
                    f.write(files[rel])
            self.assertEqual(catalog_sync.differences(engine, cat), [])
            with open(os.path.join(engine, "static", "description", "index.html"), "wb") as f:
                f.write(b"<p>changed</p>")
            self.assertEqual(catalog_sync.differences(engine, cat), [("index.html", "changed in the engine")])
            # an engine without index.html: the catalog keeps its own description
            os.remove(os.path.join(engine, "static", "description", "index.html"))
            self.assertEqual(catalog_sync.differences(engine, cat), [])
            with open(os.path.join(cat, "old.png"), "wb") as f:
                f.write(b"x")
            self.assertEqual(catalog_sync.differences(engine, cat), [("old.png", "no longer in the engine")])
