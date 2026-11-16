# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
import base64
from unittest.mock import patch

from odoo.tests import TransactionCase, tagged
from odoo.addons.dwo_attpreview_core.controllers.main import AttPreviewController
from .sample_engine import patch_sample_engine


@tagged("post_install", "-at_install")
class TestAttPreviewCore(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Engines = cls.env["dwo.attpreview.engine"]
        cls.att = cls.env["ir.attachment"].create({
            "name": "a.txt", "raw": b"hello <b>x</b>", "mimetype": "text/plain"})

    def setUp(self):
        super().setUp()
        self.sample = patch_sample_engine(self)

    def _render(self, att=None):
        return self.env["dwo.attpreview.cache"]._get_or_render(att or self.att, self.sample)

    def test_01_registry_lookup(self):
        codes = [e._dwo_engine_code for e in self.Engines._dwo_get_engines()]
        self.assertIn("sample", codes)
        self.assertEqual(codes, sorted(set(codes), key=lambda c: codes.index(c)), "one entry per engine")
        engines = self.Engines._dwo_get_engines()
        self.assertEqual([(e._dwo_engine_priority, e._dwo_engine_code) for e in engines],
                         sorted((e._dwo_engine_priority, e._dwo_engine_code) for e in engines))

    def test_02_find_engine_by_extension(self):
        self.assertIs(self.Engines._dwo_find_engine("A.TXT"), self.sample)
        self.assertIs(self.Engines._dwo_find_engine("x.sample"), self.sample)
        self.assertIsNone(self.Engines._dwo_find_engine("a.zzz"))  # no engine has this extension
        self.assertIsNone(self.Engines._dwo_find_engine("noext"))
        self.assertIsNone(self.Engines._dwo_find_engine(False))

    def test_03_render_cached_and_invalidated(self):
        rec = self._render()
        self.assertFalse(rec.error)
        self.assertEqual(base64.b64decode(rec.data), b"hello <b>x</b>")
        self.assertEqual(self._render(), rec, "second call hits the cache")
        self.att.raw = b"changed"
        new = self._render()
        self.assertEqual(base64.b64decode(new.data), b"changed")

    def test_04_cron_drops_results_of_a_gone_engine(self):
        rec = self._render()
        Mixin = type(self.Engines)
        self.assertTrue(rec.exists())
        self.env["dwo.attpreview.cache"]._cron_cleanup()
        self.assertTrue(rec.exists(), "sample engine is live")
        # the engine module is uninstalled: its results are dropped by the next clean-up
        with patch.object(Mixin, "_dwo_get_engines", lambda self: []):
            self.env["dwo.attpreview.cache"]._cron_cleanup()
        self.assertFalse(rec.exists())

    def test_05_size_limit_gives_cached_error(self):
        self.env["ir.config_parameter"].sudo().set_param("dwo_attpreview.max_file_size_mb", "0")
        rec = self._render()
        self.assertTrue(rec.error)
        self.assertFalse(rec.data)

    def test_06_engine_crash_is_contained(self):
        with patch.object(type(self.sample), "_dwo_render", lambda self, c, f: 1 / 0):
            rec = self._render()
        self.assertTrue(rec.error)

    def test_07_cache_not_readable_by_users(self):
        self._render()
        user = self.env["res.users"].create({
            # Odoo 18: groups_id (19: group_ids)
            "name": "u", "login": "u_att", "groups_id": [(6, 0, [self.env.ref("base.group_user").id])]})
        from odoo.exceptions import AccessError
        with self.assertRaises(AccessError):
            self.env["dwo.attpreview.cache"].with_user(user).search([])

    def test_08_cron_cleanup_ttl_and_cap(self):
        rec = self._render()
        rec.last_access = "2000-01-01 00:00:00"
        self.env["dwo.attpreview.cache"]._cron_cleanup()
        self.assertFalse(rec.exists())

    def test_09_cascade_with_attachment(self):
        rec = self._render()
        self.att.unlink()
        self.assertFalse(rec.exists())

    def test_10_controller_modes(self):
        ctrl = AttPreviewController()
        png = self.env["ir.attachment"].create({"name": "p.png", "raw": b"x", "mimetype": "image/png"})
        unk = self.env["ir.attachment"].create({"name": "p.xyz", "raw": b"x"})
        from types import SimpleNamespace
        with patch("odoo.addons.dwo_attpreview_core.controllers.main.request",
                   new=SimpleNamespace(env=self.env)):
            self.assertEqual(ctrl.info(png.id)["mode"], "native")
            self.assertEqual(ctrl.info(unk.id)["mode"], "unsupported")
            out = ctrl.info(self.att.id)
            self.assertEqual((out["mode"], out["type"]), ("rendered", "text"))
            self.assertFalse(out["notice"])  # the notice is per extension: none for this file
            sample = self.env["ir.attachment"].create({"name": "n.sample", "raw": b"hi"})
            self.assertEqual(ctrl.info(sample.id)["notice"], "Sample notice: this kind of file is only a sample.")
            self.assertEqual(ctrl.info(999999)["mode"], "denied")

    def test_10b_notice_is_optional(self):
        # the default of the mixin is no notice; an engine returns a string for the extensions it wants to warn about
        from types import SimpleNamespace
        mixin = self.env["dwo.attpreview.engine"]
        self.assertFalse(mixin._dwo_engine_notice("sample"))
        txt = self.env["ir.attachment"].create({"name": "n.txt", "raw": b"hi"})
        with patch("odoo.addons.dwo_attpreview_core.controllers.main.request",
                   new=SimpleNamespace(env=self.env)):
            out = AttPreviewController().info(txt.id)
        self.assertEqual(out["mode"], "rendered")
        self.assertFalse(out["notice"])

    def test_11_unsupported_reason(self):
        from types import SimpleNamespace
        ctrl = AttPreviewController()
        unk = self.env["ir.attachment"].create({"name": "p.xyz", "raw": b"x"})
        with patch("odoo.addons.dwo_attpreview_core.controllers.main.request",
                   new=SimpleNamespace(env=self.env)):
            self.assertEqual(ctrl.info(unk.id)["mode"], "unsupported")
            self.assertEqual(ctrl.info(unk.id)["reason"], "no_engine")

    def test_12_size_limit_is_reported_before_the_dialog_opens(self):
        # a refusal by the Core is known before any viewer: mode "error" (the client shows a toast, no dialog)
        from types import SimpleNamespace
        self.env["ir.config_parameter"].sudo().set_param("dwo_attpreview.max_file_size_mb", "0")
        with patch("odoo.addons.dwo_attpreview_core.controllers.main.request",
                   new=SimpleNamespace(env=self.env)):
            out = AttPreviewController().info(self.att.id)
        self.assertEqual(out["mode"], "error")
        self.assertIn("larger than the preview limit", out["error"])

    def test_13_icon_set(self):
        import os
        import re
        from odoo.tools import file_path
        kinds = ("pdf word sheet slide image video audio archive text code markdown mail cad default").split()
        with open(file_path("dwo_attpreview_core/static/src/js/file_kind.js")) as f:
            js = f.read()
        for kind in kinds:
            svg = file_path("dwo_attpreview_core/static/img/dwo_attpreview_%s.svg" % kind)
            with open(svg) as f:
                text = f.read()
            self.assertTrue(text.startswith("<svg"), kind)
            self.assertNotRegex(text, r"https?://(?!www\.w3\.org/2000/svg)", kind)
            self.assertTrue(kind in js, "kind %s is not mapped in file_kind.js" % kind)
        files = os.listdir(os.path.dirname(file_path("dwo_attpreview_core/static/img/dwo_attpreview_pdf.svg")))
        self.assertEqual(sorted(files), sorted("dwo_attpreview_%s.svg" % k for k in kinds))
