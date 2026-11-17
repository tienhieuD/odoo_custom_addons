# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import base64

from odoo.exceptions import UserError
from odoo.tests import HttpCase, TransactionCase, tagged
from odoo.tools import file_path

from .test_tour import _AssetRoutesWithoutTestCookie

MODULE = "dwo_attpreview_3d"
KINDS = ("stl", "obj", "ply", "glb", "gltf", "3mf", "fbx", "dae", "step", "stp", "iges", "igs", "3dm")
FIXTURES = {"step": "rounded-cube.step", "stp": "rounded-cube.step", "iges": "cube-10x10.igs", "igs": "cube-10x10.igs",
            "3dm": "rhino-parts.3dm"}


def _sample(kind):
    return _fixture(FIXTURES.get(kind) or "spur-gear." + kind)


def _fixture(name):
    with open(file_path("%s/tests/files/%s" % (MODULE, name)), "rb") as f:
        return f.read()


@tagged("post_install", "-at_install")
class Test3DEngine(TransactionCase):

    def setUp(self):
        super().setUp()
        self.engine = next(e for e in self.env["dwo.attpreview.engine"]._dwo_get_engines()
                           if e._dwo_engine_code == "model3d")

    def _render(self, name, content):
        return self.engine._dwo_render(content, name)

    def test_01_samples_are_accepted(self):
        for kind in KINDS:
            out = self._render("gear." + kind, _sample(kind))
            self.assertEqual(out, {"type": "text", "data": kind})

    def test_02_engine_is_found_by_extension(self):
        for kind in KINDS:
            self.assertEqual(self.env["dwo.attpreview.engine"]._dwo_find_engine("a." + kind.upper())._dwo_engine_code, "model3d")

    def test_03_empty_and_wrong_content_are_refused(self):
        for kind in KINDS:
            with self.assertRaises(UserError, msg=kind):
                self._render("a." + kind, b"")
            with self.assertRaises(UserError, msg=kind):
                self._render("a." + kind, b"this is just a sentence, not a model " * 10)
        with self.assertRaises(UserError):
            self._render("a.xyz", b"data")

    def test_04_ascii_stl_and_stl_size_check(self):
        self.assertTrue(self._render("a.stl", b"solid x\nendsolid x\n"))
        with self.assertRaises(UserError):  # a binary header whose triangle count does not match the size
            self._render("a.stl", b"\0" * 80 + (999).to_bytes(4, "little") + b"\0" * 50)

    def test_05_gltf_with_external_files_is_refused_with_advice(self):
        with self.assertRaises(UserError) as cm:
            self._render("a.gltf", _fixture("spur-gear-external.gltf"))
        self.assertIn(".glb", str(cm.exception.args[0]))

    def test_06_3mf_must_be_a_zip_with_a_model(self):
        import io
        import zipfile
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("readme.txt", "no model here")
        with self.assertRaises(UserError):
            self._render("a.3mf", buf.getvalue())
        with self.assertRaises(UserError):
            self._render("a.3mf", b"PK not really")

    def test_06b_step_iges_3dm_signatures(self):
        for name in ("a.step", "a.stp"):
            with self.assertRaises(UserError):
                self._render(name, b"ISO-10303-21;\nHEADER;\nENDSEC;")  # no FILE_SCHEMA
        with self.assertRaises(UserError):
            self._render("a.iges", b"x" * 100)
        with self.assertRaises(UserError):
            self._render("a.3dm", b"PK\x03\x04" + b"0" * 50)

    def test_07_core_refuses_a_big_file_before_the_engine(self):
        self.env["ir.config_parameter"].sudo().set_param("dwo_attpreview.max_mb.model3d_mesh", "0")
        att = self.env["ir.attachment"].create({"name": "gear.stl", "raw": _fixture("spur-gear.stl")})
        with self.assertRaises(UserError):
            self.env["dwo.attpreview.cache"]._render(att, self.engine)


@tagged("post_install", "-at_install")
class Test3DRoutes(_AssetRoutesWithoutTestCookie, HttpCase):

    def _att(self, name, content):
        return self.env["ir.attachment"].create({"name": name, "raw": content})

    def test_01_asset_route_serves_only_the_viewer(self):
        for path, ok in (("viewer/viewer.html", True), ("viewer/viewer.js", True), ("../__manifest__.py", False),
                         ("viewer/../__manifest__.py", False), ("models/engine.py", False), ("viewer/nothing.js", False)):
            res = self.url_open("/dwo_attpreview_3d/asset/" + path)
            self.assertEqual(res.status_code == 200, ok, path)
        res = self.url_open("/dwo_attpreview_3d/asset/viewer/viewer.html")
        csp = res.headers["Content-Security-Policy"]
        self.assertIn("default-src 'none'", csp)
        self.assertIn("sandbox allow-scripts", csp)
        self.assertNotIn("unsafe-eval", csp.replace("wasm-unsafe-eval", ""))
        self.assertEqual(res.headers["Access-Control-Allow-Origin"], "*")
        self.assertEqual(res.headers["X-Content-Type-Options"], "nosniff")

    def test_01b_only_the_solid_page_may_use_unsafe_eval(self):
        for page, eval_ok in (("viewer.html", False), ("solid.html", True)):
            csp = self.url_open("/dwo_attpreview_3d/asset/viewer/" + page).headers["Content-Security-Policy"]
            self.assertEqual(" 'unsafe-eval'" in csp, eval_ok, page)
            self.assertIn("default-src 'none'", csp)
        for path in ("lib/occt/occt-import-js.bundle.js", "lib/occt/occt-import-js.wasm", "lib/rhino3dm/rhino3dm.module.min.js",
                     "lib/rhino3dm/rhino3dm.wasm"):
            self.assertEqual(self.url_open("/dwo_attpreview_3d/asset/" + path).status_code, 200, path)
        self.assertEqual(self.url_open("/dwo_attpreview_3d/asset/lib/occt/LICENSE-LGPL-2.1.txt").status_code, 404)

    def test_02_webgl_asset_route_serves_three_and_nothing_else(self):
        for path, ok in (("lib/three/build/three.module.js", True), ("viewer/common.js", True),
                         ("lib/three/examples/jsm/loaders/STLLoader.js", True), ("controllers/main.py", False),
                         ("lib/three/../../__manifest__.py", False), ("lib/three/LICENSE", False)):
            self.assertEqual(self.url_open("/dwo_attpreview_webgl/asset/" + path).status_code == 200, ok, path)

    def test_03_file_route_checks_access_and_engine(self):
        att = self._att("gear.stl", _fixture("spur-gear.stl"))
        # not logged in: the login page, never the file
        self.assertNotEqual(self.url_open("/dwo_attpreview_3d/file/%d" % att.id).content, _fixture("spur-gear.stl"))
        self.authenticate("admin", "admin")
        res = self.url_open("/dwo_attpreview_3d/file/%d" % att.id)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content, _fixture("spur-gear.stl"))
        other = self._att("notes.txt", b"hello")
        self.assertEqual(self.url_open("/dwo_attpreview_3d/file/%d" % other.id).status_code, 404)
        bad = self._att("bad.stl", b"not a model at all " * 10)
        self.assertEqual(self.url_open("/dwo_attpreview_3d/file/%d" % bad.id).status_code, 422)
        self.assertEqual(self.url_open("/dwo_attpreview_3d/file/99999999").status_code, 403)

    def test_04_info_route_answers_with_the_viewer(self):
        self.authenticate("admin", "admin")
        att = self._att("gear.glb", _fixture("spur-gear.glb"))
        res = self.make_jsonrpc_request("/dwo_attpreview/info", {"attachment_id": att.id})
        self.assertEqual(res["mode"], "rendered")
        self.assertEqual(res["engine"], "model3d")
        self.assertEqual(res["content"], "glb")
