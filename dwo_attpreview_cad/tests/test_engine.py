# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo.exceptions import UserError
from odoo.tests import HttpCase, TransactionCase, tagged
from odoo.tools import file_path

MODULE = "dwo_attpreview_cad"


def _fixture(name):
    with open(file_path("%s/tests/files/%s" % (MODULE, name)), "rb") as f:
        return f.read()


@tagged("post_install", "-at_install")
class TestCadEngine(TransactionCase):

    def setUp(self):
        super().setUp()
        self.engine = next(e for e in self.env["dwo.attpreview.engine"]._dwo_get_engines()
                           if e._dwo_engine_code == "cad")

    def test_01_sample_is_accepted(self):
        self.assertEqual(self.engine._dwo_render(_fixture("floor-plan.dxf"), "plan.dxf"), {"type": "text", "data": "dxf"})
        self.assertEqual(self.env["dwo.attpreview.engine"]._dwo_find_engine("PLAN.DXF")._dwo_engine_code, "cad")

    def test_02_wrong_content_is_refused(self):
        for content in (b"", b"just a sentence " * 50, b"\0\1\2 SECTION", b"AutoCAD Binary DXF\r\n\x1a\0"):
            with self.assertRaises(UserError):
                self.engine._dwo_render(content, "a.dxf")

    def test_03_binary_dxf_gets_advice(self):
        with self.assertRaises(UserError) as cm:
            self.engine._dwo_render(b"AutoCAD Binary DXF\r\n\x1a\0" + b"\0" * 50, "a.dxf")
        self.assertIn("ASCII", str(cm.exception.args[0]))

    def test_04_core_refuses_a_big_file_before_the_engine(self):
        self.env["ir.config_parameter"].sudo().set_int("dwo_attpreview.max_mb.cad_dxf", 0)
        att = self.env["ir.attachment"].create({"name": "plan.dxf", "raw": _fixture("floor-plan.dxf")})
        with self.assertRaises(UserError):
            self.env["dwo.attpreview.cache"]._render(att, self.engine)


@tagged("post_install", "-at_install")
class TestCadRoutes(HttpCase):

    def test_01_asset_route_serves_only_the_viewer_and_its_library(self):
        for path, ok in (("viewer/viewer.html", True), ("viewer/viewer.js", True), ("lib/dxf-viewer/dxf-viewer.bundle.js", True),
                         ("lib/dxf-viewer/fonts/noto-sans-latin-400-normal.woff", True),
                         ("lib/dxf-viewer/LICENSE-dxf-viewer-MPL-2.0.txt", False), ("../__manifest__.py", False),
                         ("models/engine.py", False), ("lib/dxf-viewer/../../__manifest__.py", False)):
            self.assertEqual(self.url_open("/dwo_attpreview_cad/asset/" + path).status_code == 200, ok, path)
        res = self.url_open("/dwo_attpreview_cad/asset/viewer/viewer.html")
        self.assertIn("default-src 'none'", res.headers["Content-Security-Policy"])
        self.assertEqual(res.headers["Access-Control-Allow-Origin"], "*")

    def test_02_bundle_imports_three_from_the_webgl_module_only(self):
        res = self.url_open("/dwo_attpreview_cad/asset/lib/dxf-viewer/dxf-viewer.bundle.js")
        text = res.text
        self.assertIn('from"/dwo_attpreview_webgl/asset/lib/three/build/three.module.js"', text)
        self.assertNotIn('from"three"', text)
        self.assertNotRegex(text, r'(?:from|import\()\s*"https?:')

    def test_03_file_route_checks_access_and_engine(self):
        att = self.env["ir.attachment"].create({"name": "plan.dxf", "raw": _fixture("floor-plan.dxf")})
        self.authenticate("admin", "admin")
        res = self.url_open("/dwo_attpreview_cad/file/%d" % att.id)
        self.assertEqual((res.status_code, res.content), (200, _fixture("floor-plan.dxf")))
        other = self.env["ir.attachment"].create({"name": "notes.txt", "raw": b"hello"})
        self.assertEqual(self.url_open("/dwo_attpreview_cad/file/%d" % other.id).status_code, 404)
        bad = self.env["ir.attachment"].create({"name": "bad.dxf", "raw": b"not a drawing " * 20})
        self.assertEqual(self.url_open("/dwo_attpreview_cad/file/%d" % bad.id).status_code, 422)
        self.assertEqual(self.url_open("/dwo_attpreview_cad/file/99999999").status_code, 403)

    def test_04_info_route_answers_with_the_viewer(self):
        self.authenticate("admin", "admin")
        att = self.env["ir.attachment"].create({"name": "plan.dxf", "raw": _fixture("floor-plan.dxf")})
        res = self.make_jsonrpc_request("/dwo_attpreview/info", {"attachment_id": att.id})
        self.assertEqual((res["mode"], res["engine"], res["content"]), ("rendered", "cad", "dxf"))
