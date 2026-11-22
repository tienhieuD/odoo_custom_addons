# Copyright 2026 DuoTEK. Licensed under the GNU General Public License v3.0 (GPL-3).
from odoo.exceptions import UserError
from odoo.tests import HttpCase, TransactionCase, tagged
from odoo.tools import file_path

MODULE = "dwo_attpreview_dwg"
SAMPLES = ("sample_2000.dwg", "sample_2018.dwg")


def _fixture(name):
    with open(file_path("%s/tests/files/%s" % (MODULE, name)), "rb") as f:
        return f.read()


@tagged("post_install", "-at_install")
class TestDwgEngine(TransactionCase):

    def setUp(self):
        super().setUp()
        self.engine = next(e for e in self.env["dwo.attpreview.engine"]._dwo_get_engines()
                           if e._dwo_engine_code == "dwg")

    def test_01_samples_are_accepted(self):
        for name in SAMPLES:
            self.assertEqual(self.engine._dwo_render(_fixture(name), name), {"type": "text", "data": "dwg"})
        self.assertEqual(self.env["dwo.attpreview.engine"]._dwo_find_engine("PLAN.DWG")._dwo_engine_code, "dwg")

    def test_02_wrong_content_is_refused(self):
        for content in (b"", b"just a sentence " * 50, b"PK\x03\x04 zip", b"AutoCAD Binary DXF\r\n"):
            with self.assertRaises(UserError):
                self.engine._dwo_render(content, "a.dwg")

    def test_03_core_refuses_a_big_file_before_the_engine(self):
        self.env["ir.config_parameter"].sudo().set_int("dwo_attpreview.max_mb.dwg", 0)
        att = self.env["ir.attachment"].create({"name": "plan.dwg", "raw": _fixture("sample_2000.dwg")})
        with self.assertRaises(UserError):
            self.env["dwo.attpreview.cache"]._render(att, self.engine)


@tagged("post_install", "-at_install")
class TestDwgRoutes(HttpCase):

    def test_01_asset_route_serves_only_the_viewer_and_the_libraries(self):
        for path, ok in (("viewer/viewer.html", True), ("viewer/viewer.js", True),
                         ("lib/bGlicmVkd2c/dist/libredwg-web.js", True), ("lib/bGlicmVkd2c/wasm/libredwg-web.js", True),
                         ("lib/bGlicmVkd2c/wasm/libredwg-web.wasm", True), ("lib/ZHhmLXZpZXdlcg/dxf-viewer.bundle.js", True),
                         ("lib/bGlicmVkd2c/LICENSE-GPL-3.0.txt", False), ("../__manifest__.py", False),
                         ("models/engine.py", False), ("lib/bGlicmVkd2c/../../__manifest__.py", False)):
            self.assertEqual(self.url_open("/dwo_attpreview_dwg/asset/" + path).status_code == 200, ok, path)
        res = self.url_open("/dwo_attpreview_dwg/asset/viewer/viewer.html")
        csp = res.headers["Content-Security-Policy"]
        self.assertIn("default-src 'none'", csp)
        self.assertIn("'wasm-unsafe-eval'", csp)
        self.assertIn(" 'unsafe-eval'", csp)  # the LibreDWG glue needs it; the page has no network and is sandboxed
        self.assertIn("connect-src %s" % self.base_url(), csp)
        self.assertNotIn("http:", csp.replace(self.base_url(), ""))
        wasm = self.url_open("/dwo_attpreview_dwg/asset/lib/bGlicmVkd2c/wasm/libredwg-web.wasm")
        self.assertEqual(wasm.headers["Content-Type"], "application/wasm")

    def test_02_file_route_checks_access_and_engine(self):
        att = self.env["ir.attachment"].create({"name": "plan.dwg", "raw": _fixture("sample_2000.dwg")})
        self.authenticate("admin", "admin")
        res = self.url_open("/dwo_attpreview_dwg/file/%d" % att.id)
        self.assertEqual((res.status_code, res.content), (200, _fixture("sample_2000.dwg")))
        other = self.env["ir.attachment"].create({"name": "notes.txt", "raw": b"hello"})
        self.assertEqual(self.url_open("/dwo_attpreview_dwg/file/%d" % other.id).status_code, 404)
        bad = self.env["ir.attachment"].create({"name": "bad.dwg", "raw": b"not a drawing " * 20})
        self.assertEqual(self.url_open("/dwo_attpreview_dwg/file/%d" % bad.id).status_code, 422)
        self.assertEqual(self.url_open("/dwo_attpreview_dwg/file/99999999").status_code, 403)

    def test_03_info_route_answers_with_the_viewer(self):
        self.authenticate("admin", "admin")
        att = self.env["ir.attachment"].create({"name": "plan.dwg", "raw": _fixture("sample_2018.dwg")})
        res = self.make_jsonrpc_request("/dwo_attpreview/info", {"attachment_id": att.id})
        self.assertEqual((res["mode"], res["engine"], res["content"]), ("rendered", "dwg", "dwg"))
