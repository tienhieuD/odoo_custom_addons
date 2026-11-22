# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo.exceptions import UserError
from odoo.tests import HttpCase, TransactionCase, tagged
from odoo.tools import file_path

MODULE = "dwo_attpreview_bim"


def _fixture(name):
    with open(file_path("%s/tests/files/%s" % (MODULE, name)), "rb") as f:
        return f.read()


@tagged("post_install", "-at_install")
class TestBimEngine(TransactionCase):

    def setUp(self):
        super().setUp()
        self.engine = next(e for e in self.env["dwo.attpreview.engine"]._dwo_get_engines()
                           if e._dwo_engine_code == "bim")

    def test_01_sample_is_accepted(self):
        self.assertEqual(self.engine._dwo_render(_fixture("office-building.ifc"), "model.ifc"), {"type": "text", "data": "ifc"})
        self.assertEqual(self.env["dwo.attpreview.engine"]._dwo_find_engine("MODEL.IFC")._dwo_engine_code, "bim")

    def test_02_wrong_content_is_refused(self):
        for content in (b"", b"just a sentence " * 50, b"PK\x03\x04 zip", b"ISO-10303-21;\nHEADER;\nFILE_SCHEMA(('AP214'));\nENDSEC;"):
            with self.assertRaises(UserError):
                self.engine._dwo_render(content, "a.ifc")

    def test_04_core_refuses_a_big_file_before_the_engine(self):
        self.env["ir.config_parameter"].sudo().set_int("dwo_attpreview.max_mb.bim_ifc", 0)
        att = self.env["ir.attachment"].create({"name": "model.ifc", "raw": _fixture("office-building.ifc")})
        with self.assertRaises(UserError):
            self.env["dwo.attpreview.cache"]._render(att, self.engine)


@tagged("post_install", "-at_install")
class TestBimRoutes(HttpCase):

    def test_01_asset_route_serves_only_the_viewer_and_its_library(self):
        for path, ok in (("viewer/viewer.html", True), ("viewer/viewer.js", True), ("lib/d2ViLWlmYw/web-ifc-api.js", True), ("lib/d2ViLWlmYw/web-ifc.wasm", True),
                         ("lib/d2ViLWlmYw/LICENSE-web-ifc-MPL-2.0.txt", False), ("../__manifest__.py", False),
                         ("models/engine.py", False), ("lib/d2ViLWlmYw/../../__manifest__.py", False)):
            self.assertEqual(self.url_open("/dwo_attpreview_bim/asset/" + path).status_code == 200, ok, path)
        res = self.url_open("/dwo_attpreview_bim/asset/viewer/viewer.html")
        self.assertIn("default-src 'none'", res.headers["Content-Security-Policy"])
        self.assertEqual(res.headers["Access-Control-Allow-Origin"], "*")

    def test_03_file_route_checks_access_and_engine(self):
        att = self.env["ir.attachment"].create({"name": "model.ifc", "raw": _fixture("office-building.ifc")})
        self.authenticate("admin", "admin")
        res = self.url_open("/dwo_attpreview_bim/file/%d" % att.id)
        self.assertEqual((res.status_code, res.content), (200, _fixture("office-building.ifc")))
        other = self.env["ir.attachment"].create({"name": "notes.txt", "raw": b"hello"})
        self.assertEqual(self.url_open("/dwo_attpreview_bim/file/%d" % other.id).status_code, 404)
        bad = self.env["ir.attachment"].create({"name": "bad.ifc", "raw": b"not a drawing " * 20})
        self.assertEqual(self.url_open("/dwo_attpreview_bim/file/%d" % bad.id).status_code, 422)
        self.assertEqual(self.url_open("/dwo_attpreview_bim/file/99999999").status_code, 403)

    def test_04_info_route_answers_with_the_viewer(self):
        self.authenticate("admin", "admin")
        att = self.env["ir.attachment"].create({"name": "model.ifc", "raw": _fixture("office-building.ifc")})
        res = self.make_jsonrpc_request("/dwo_attpreview/info", {"attachment_id": att.id})
        self.assertEqual((res["mode"], res["engine"], res["content"]), ("rendered", "bim", "ifc"))
