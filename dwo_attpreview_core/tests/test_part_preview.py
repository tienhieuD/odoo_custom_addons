# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
"""/dwo_attpreview/part_info and /dwo_attpreview/part: a file inside another file (an attachment of an email)."""
import base64
import json
from types import SimpleNamespace
from unittest.mock import patch

from odoo.tests import HttpCase, TransactionCase, new_test_user, tagged
from odoo.addons.dwo_attpreview_core.controllers.main import AttPreviewController
from .sample_engine import BOX, patch_sample_engine

REQUEST = "odoo.addons.dwo_attpreview_core.controllers.main.request"
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")
SVG = b'<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"><script>alert(2)</script></svg>'
# a.sample (text), inner.box (a box inside the box: deep.sample), pic.png, page.html
BOX_FILE = b"a.sample=hello;inner.box=deep.sample=deep text;pic.svg=" + SVG.replace(b";", b"|") + b";page.html=<b>x</b>"


@tagged("post_install", "-at_install")
class TestPartInfo(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ctrl = AttPreviewController()
        cls.partner = cls.env["res.partner"].create({"name": "Box owner"})
        cls.att = cls.env["ir.attachment"].create({
            "name": "mail.box", "raw": BOX_FILE, "res_model": "res.partner", "res_id": cls.partner.id})
        cls.portal = new_test_user(cls.env, login="dwo_part_portal", groups="base.group_portal")

    def setUp(self):
        super().setUp()
        patch_sample_engine(self, BOX)

    def _call(self, method, *args, env=None, **kw):
        with patch(REQUEST, new=SimpleNamespace(env=env or self.env)):
            return getattr(self.ctrl, method)(*args, **kw)

    def test_01_json_result_and_source_ref(self):
        out = self._call("info", self.att.id)
        self.assertEqual((out["mode"], out["type"], out["engine"]), ("rendered", "json", "box"))
        data = json.loads(out["content"])
        self.assertEqual(data["files"], ["a.sample", "inner.box", "pic.svg", "page.html"])
        self.assertEqual(data["html"], "<script>x</script>", "json is the engine's job: not touched by the Core")
        self.assertEqual(out["source_ref"], {"attachment_id": self.att.id})

    def test_02_part_rendered_in_memory(self):
        caches = self.env["dwo.attpreview.cache"].sudo().search_count([])
        atts = self.env["ir.attachment"].sudo().search_count([])
        out = self._call("part_info", {"attachment_id": self.att.id}, "0")
        self.assertEqual((out["mode"], out["engine"], out["content"], out["name"]),
                         ("rendered", "sample", "hello", "a.sample"))
        self.assertEqual(out["source"], "part")
        self.assertEqual(out["source_ref"], {"attachment_id": self.att.id, "path": "0"})
        self.assertIn("/dwo_attpreview/part?attachment_id=%d&path=0" % self.att.id, out["download_url"])
        self.assertTrue(out["download_url"].endswith("download=true"))
        self.assertEqual(out["file_url"], out["download_url"])
        self.assertEqual(self.env["dwo.attpreview.cache"].sudo().search_count([]), caches, "no cache entry")
        self.assertEqual(self.env["ir.attachment"].sudo().search_count([]), atts, "no attachment")

    def test_03_nested_path(self):
        out = self._call("part_info", {"attachment_id": self.att.id}, "1/0")
        self.assertEqual((out["mode"], out["content"], out["name"]), ("rendered", "deep text", "deep.sample"))
        self.assertEqual(out["source_ref"]["path"], "1/0")

    def test_04_native_and_unsupported(self):
        out = self._call("part_info", {"attachment_id": self.att.id}, [2])
        self.assertEqual((out["mode"], out["mimetype"]), ("native", "image/svg+xml"))
        self.assertIn("download=false", out["url"])
        out = self._call("part_info", {"attachment_id": self.att.id}, "3")
        self.assertEqual((out["mode"], out["reason"]), ("unsupported", "no_engine"))

    def test_05_bad_paths(self):
        src = {"attachment_id": self.att.id}
        for path in ("", "x", "-1", "/".join(["1"] * 21), None, [], "99999"):
            self.assertEqual(self._call("part_info", src, path)["mode"], "denied", path)
        out = self._call("part_info", src, "9")
        self.assertEqual(out["mode"], "error")
        self.assertIn("could not be found", out["error"])
        out = self._call("part_info", src, "0/0")  # a.sample is no container
        self.assertEqual(out["mode"], "error")

    def test_06_access_is_checked_on_the_outer_file(self):
        env = self.env(user=self.portal)
        self.assertEqual(self._call("part_info", {"attachment_id": self.att.id}, "0", env=env)["mode"], "denied")
        self.assertEqual(self._call("part_info", {"attachment_id": "abc"}, "0")["mode"], "denied")
        self.assertEqual(self._call("part_info", "nope", "0")["mode"], "denied")

    def test_07_binary_field_source(self):
        company = self.env.company
        company.write({"name": "c.box", "layout_background_image": base64.b64encode(b"x.sample=from field")})
        info = self._call("field_info", model="res.company", res_id=company.id, field="layout_background_image",
                          filename_field="name")
        ref = info["source_ref"]
        self.assertEqual((ref["model"], ref["field"], ref["filename_field"]),
                         ("res.company", "layout_background_image", "name"))
        out = self._call("part_info", ref, "0")
        self.assertEqual((out["mode"], out["content"]), ("rendered", "from field"))
        self.assertIn("model=res.company", out["download_url"])

    def test_08_size_limit_of_the_outer_file(self):
        self.env["ir.config_parameter"].sudo().set_param("dwo_attpreview.max_file_size_mb", 0)
        out = self._call("part_info", {"attachment_id": self.att.id}, "0")
        self.assertEqual(out["mode"], "error")
        self.assertIn("preview limit", out["error"])


@tagged("post_install", "-at_install")
class TestPartRoute(HttpCase):

    def setUp(self):
        super().setUp()
        patch_sample_engine(self, BOX)
        self.att = self.env["ir.attachment"].create({"name": "mail.box", "raw": BOX_FILE})
        self.authenticate("admin", "admin")

    def test_01_headers_and_inline_rules(self):
        base = "/dwo_attpreview/part?attachment_id=%d&path=" % self.att.id
        res = self.url_open(base + "2&download=false")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content, SVG)
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(res.headers.get("Content-Security-Policy"), "default-src 'none'")
        self.assertTrue(res.headers.get("Content-Disposition", "").startswith("inline"))
        # html is never inline, even when asked
        res = self.url_open(base + "3&download=false")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.headers.get("Content-Disposition", "").startswith("attachment"))
        res = self.url_open(base + "0&download=true")
        self.assertEqual(res.content, b"hello")
        self.assertTrue(res.headers.get("Content-Disposition", "").startswith("attachment"))

    def test_02_not_found(self):
        self.assertEqual(self.url_open("/dwo_attpreview/part?attachment_id=%d&path=9" % self.att.id).status_code, 404)
        self.assertEqual(self.url_open("/dwo_attpreview/part?attachment_id=%d&path=x" % self.att.id).status_code, 404)
        self.authenticate(None, None)
        res = self.url_open("/dwo_attpreview/part?attachment_id=%d&path=0" % self.att.id, allow_redirects=False)
        self.assertNotEqual(res.status_code, 200)
