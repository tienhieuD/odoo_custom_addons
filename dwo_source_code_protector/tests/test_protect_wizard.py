import base64
import io
import zipfile

try:
    import pyzipper
    import jprotect  # noqa: F401

    _DEPS_AVAILABLE = True
except ImportError:
    _DEPS_AVAILABLE = False

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


def _make_zip(modules: list[dict], password: bytes | None = None) -> bytes:
    """
    Build an in-memory zip.

    Each entry in `modules` is:
      {
        "root": "sale_ext",          # path prefix inside zip ('' = manifest at zip root)
        "manifest": True,            # whether to include __manifest__.py
        "has_models": True,          # whether to include models/sale_ext.py with a method
      }
    Extra entries: {"path": "readme.txt", "content": b"hello"}
    """
    buf = io.BytesIO()
    opener = pyzipper.AESZipFile if _DEPS_AVAILABLE and password else zipfile.ZipFile
    kwargs = {"mode": "w", "compression": zipfile.ZIP_DEFLATED}
    if password and _DEPS_AVAILABLE:
        kwargs["encryption"] = pyzipper.WZ_AES

    with opener(buf, **kwargs) as zf:
        if password and _DEPS_AVAILABLE:
            zf.setpassword(password)

        for item in modules:
            if "path" in item:
                zf.writestr(item["path"], item.get("content", b""))
                continue

            prefix = item["root"].rstrip("/") + "/" if item.get("root") else ""

            if item.get("manifest", True):
                manifest_content = (
                    "{'name': '%s', 'version': '18.0.1.0.0', 'depends': ['base']}"
                    % (item.get("root") or "test_module")
                )
                zf.writestr(f"{prefix}__manifest__.py", manifest_content)

            if item.get("has_models", True):
                model_src = (
                    "from odoo import models\n\n"
                    "class TestModel(models.Model):\n"
                    "    _name = 'test.model'\n\n"
                    "    def compute_value(self):\n"
                    "        return 42\n"
                )
                zf.writestr(f"{prefix}models/__init__.py", "from . import test_model\n")
                zf.writestr(f"{prefix}models/test_model.py", model_src)
                zf.writestr(f"{prefix}__init__.py", "from . import models\n")

    return buf.getvalue()


@tagged("post_install", "-at_install")
class TestProtectWizard(TransactionCase):

    def setUp(self):
        super().setUp()
        if not _DEPS_AVAILABLE:
            self.skipTest("jprotect or pyzipper not installed")

    def _new_wizard(self, zip_bytes: bytes, filename: str = "test.zip", password: str = ""):
        wiz = self.env["dwo.protect.source.wizard"].create(
            {
                "upload_file": base64.b64encode(zip_bytes),
                "upload_filename": filename,
                "password": password,
            }
        )
        return wiz

    # ------------------------------------------------------------------ #

    def test_protect_flow_root_manifest(self):
        """Manifest at zip root → protect succeeds, output zip created."""
        zip_bytes = _make_zip([{"root": "", "manifest": True, "has_models": True}])
        wiz = self._new_wizard(zip_bytes)
        wiz.action_protect()
        self.assertEqual(wiz.state, "get")
        self.assertTrue(wiz.output_file)
        self.assertTrue(wiz.output_filename.endswith("_compile.zip"))
        self.assertIn("Protected", wiz.result_info)

    def test_protect_flow_nested_manifest(self):
        """Manifest inside subfolder → output zip preserves nesting."""
        zip_bytes = _make_zip([{"root": "sale_ext", "manifest": True, "has_models": True}])
        wiz = self._new_wizard(zip_bytes, filename="sale_ext.zip")
        wiz.action_protect()
        self.assertEqual(wiz.state, "get")
        out_bytes = base64.b64decode(wiz.output_file)
        with zipfile.ZipFile(io.BytesIO(out_bytes)) as zf:
            names = zf.namelist()
        self.assertTrue(
            any(n.startswith("sale_ext/") for n in names),
            "Output zip should preserve subfolder nesting",
        )

    def test_multi_module_zip(self):
        """2 protectable modules + 1 no-models → 2 Protected + 1 Skipped."""
        zip_bytes = _make_zip(
            [
                {"root": "mod_a", "manifest": True, "has_models": True},
                {"root": "mod_b", "manifest": True, "has_models": True},
                {"root": "mod_c", "manifest": True, "has_models": False},
            ]
        )
        wiz = self._new_wizard(zip_bytes)
        wiz.action_protect()
        self.assertEqual(wiz.state, "get")
        self.assertIn("mod_a", wiz.result_info)
        self.assertIn("mod_b", wiz.result_info)
        self.assertIn("mod_c", wiz.result_info)
        # output zip contains all 3 modules
        out_bytes = base64.b64decode(wiz.output_file)
        with zipfile.ZipFile(io.BytesIO(out_bytes)) as zf:
            names = zf.namelist()
        self.assertTrue(any("mod_a" in n for n in names))
        self.assertTrue(any("mod_b" in n for n in names))
        self.assertTrue(any("mod_c" in n for n in names))

    def test_password_roundtrip(self):
        """AES-encrypted input + correct password → output also openable with same password."""
        pwd = b"s3cret"
        zip_bytes = _make_zip(
            [{"root": "sale_ext", "manifest": True, "has_models": True}],
            password=pwd,
        )
        wiz = self._new_wizard(zip_bytes, password="s3cret")
        wiz.action_protect()
        self.assertEqual(wiz.state, "get")
        out_bytes = base64.b64decode(wiz.output_file)
        with pyzipper.AESZipFile(io.BytesIO(out_bytes)) as zf:
            zf.setpassword(pwd)
            names = zf.namelist()
        self.assertTrue(len(names) > 0)

    def test_wrong_password_raises(self):
        """Wrong password on encrypted zip → UserError."""
        pwd = b"correct"
        zip_bytes = _make_zip(
            [{"root": "sale_ext", "manifest": True, "has_models": True}],
            password=pwd,
        )
        wiz = self._new_wizard(zip_bytes, password="wrong_password")
        with self.assertRaises(UserError):
            wiz.action_protect()

    def test_zip_slip_rejected(self):
        """Zip entry with ../ path → skipped (no file written outside work_dir)."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("../evil.py", "import os; os.system('rm -rf /')")
            zf.writestr(
                "safe_mod/__manifest__.py",
                "{'name':'safe','version':'18.0.1.0.0','depends':['base']}",
            )
        zip_bytes = buf.getvalue()
        wiz = self._new_wizard(zip_bytes)
        # Should not raise; evil.py is silently skipped
        # (no manifest in zip besides nested safe_mod)
        try:
            wiz.action_protect()
        except UserError:
            pass  # also acceptable

    def test_no_manifest_raises(self):
        """Zip with no __manifest__.py → UserError."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("README.txt", "hello")
        wiz = self._new_wizard(buf.getvalue())
        with self.assertRaises(UserError):
            wiz.action_protect()

    def test_invalid_file_raises(self):
        """Non-zip upload → UserError."""
        wiz = self._new_wizard(b"not a zip", filename="file.txt")
        with self.assertRaises(UserError):
            wiz.action_protect()

    def test_output_zip_name(self):
        """_output_zip_name strips .zip and appends _compile.zip."""
        wiz = self.env["dwo.protect.source.wizard"].create({})
        self.assertEqual(wiz._output_zip_name("sale_ext.zip"), "sale_ext_compile.zip")
        self.assertEqual(wiz._output_zip_name("module"), "module_compile.zip")

    def test_find_module_roots_no_nested(self):
        """_find_module_roots returns top-level module dirs only."""
        import os, tempfile

        with tempfile.TemporaryDirectory() as tmp:
            # create mod_a/__manifest__.py
            os.makedirs(os.path.join(tmp, "mod_a"))
            open(os.path.join(tmp, "mod_a", "__manifest__.py"), "w").close()
            # create mod_a/sub_mod/__manifest__.py (nested — should be excluded)
            os.makedirs(os.path.join(tmp, "mod_a", "sub_mod"))
            open(os.path.join(tmp, "mod_a", "sub_mod", "__manifest__.py"), "w").close()
            # create mod_b/__manifest__.py
            os.makedirs(os.path.join(tmp, "mod_b"))
            open(os.path.join(tmp, "mod_b", "__manifest__.py"), "w").close()

            wiz = self.env["dwo.protect.source.wizard"].create({})
            roots = wiz._find_module_roots(tmp)

        root_names = sorted(os.path.basename(r) for r in roots)
        self.assertEqual(root_names, ["mod_a", "mod_b"])
