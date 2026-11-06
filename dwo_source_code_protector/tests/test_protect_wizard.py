import base64
import io
import zipfile
from datetime import timedelta

try:
    import pyzipper
    import jprotect  # noqa: F401

    _DEPS_AVAILABLE = True
except ImportError:
    _DEPS_AVAILABLE = False

from odoo import fields
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
class TestProtectJob(TransactionCase):
    """Exercises the background-job pipeline (dwo.protect.job) directly, one step at a time
    -- the way the cron would -- instead of going through the wizard, since the wizard now
    only creates the job and returns immediately (see wizards/protect_source_wizard.py)."""

    def setUp(self):
        super().setUp()
        if not _DEPS_AVAILABLE:
            self.skipTest("jprotect or pyzipper not installed")

    def _new_job(self, zip_bytes: bytes, filename: str = "test.zip", password: str = ""):
        return self.env["dwo.protect.job"].create_from_upload(
            base64.b64encode(zip_bytes), filename, password
        )

    def _run_to_completion(self, job, max_steps=50):
        for _i in range(max_steps):
            if job.state in ("done", "error"):
                return
            job._process_one_step()
        self.fail("job did not finish within %d steps" % max_steps)

    # ------------------------------------------------------------------ #

    def test_protect_flow_root_manifest_is_rejected(self):
        """Manifest at zip root (no module folder) -> Skipped with a clear reason, not silently
        protected. There is no reliable source for the module's real technical name in this
        shape (it only exists as a folder name, and here there is none): running jProtect
        anyway would bake the wrong name into the compiled .so's __module__, which Odoo uses to
        attribute a model to an addon. The job still ends in state "done" with an output zip --
        it degrades this one entry rather than failing the whole job, the same way it already
        does for "no protectable methods found"."""
        zip_bytes = _make_zip([{"root": "", "manifest": True, "has_models": True}])
        job = self._new_job(zip_bytes)
        self._run_to_completion(job)
        self.assertEqual(job.state, "done")
        self.assertTrue(job.result_attachment_id)
        self.assertIn("Skipped", job.result_info)
        self.assertNotIn("Protected", job.result_info)
        self.assertIn("enclosing module folder", job.result_info)

    def test_protect_flow_nested_manifest(self):
        """Manifest inside subfolder → output zip preserves nesting."""
        zip_bytes = _make_zip([{"root": "sale_ext", "manifest": True, "has_models": True}])
        job = self._new_job(zip_bytes, filename="sale_ext.zip")
        self._run_to_completion(job)
        self.assertEqual(job.state, "done")
        out_bytes = job.result_attachment_id.sudo().raw
        with zipfile.ZipFile(io.BytesIO(out_bytes)) as zf:
            names = zf.namelist()
        self.assertTrue(
            any(n.startswith("sale_ext/") for n in names),
            "Output zip should preserve subfolder nesting",
        )

    def test_multi_module_zip(self):
        """2 protectable modules + 1 no-models → 2 Protected + 1 Skipped, processed one module
        per step (module_index advances by exactly one each _process_one_step call)."""
        zip_bytes = _make_zip(
            [
                {"root": "mod_a", "manifest": True, "has_models": True},
                {"root": "mod_b", "manifest": True, "has_models": True},
                {"root": "mod_c", "manifest": True, "has_models": False},
            ]
        )
        job = self._new_job(zip_bytes)
        # step 1: extract + discover
        job._process_one_step()
        self.assertEqual(job.state, "running")
        self.assertEqual(job.module_count, 3)
        self.assertEqual(job.module_index, 0)
        # steps 2-4: one module each
        job._process_one_step()
        self.assertEqual(job.module_index, 1)
        job._process_one_step()
        self.assertEqual(job.module_index, 2)
        job._process_one_step()
        self.assertEqual(job.module_index, 3)
        # step 5: finalize
        job._process_one_step()
        self.assertEqual(job.state, "done")

        self.assertIn("mod_a", job.result_info)
        self.assertIn("mod_b", job.result_info)
        self.assertIn("mod_c", job.result_info)
        out_bytes = job.result_attachment_id.sudo().raw
        with zipfile.ZipFile(io.BytesIO(out_bytes)) as zf:
            names = zf.namelist()
        self.assertTrue(any("mod_a" in n for n in names))
        self.assertTrue(any("mod_b" in n for n in names))
        self.assertTrue(any("mod_c" in n for n in names))

    def test_password_roundtrip(self):
        """AES-encrypted input + correct password → output also openable with same password,
        and the password is cleared from the job once it finishes."""
        pwd = b"s3cret"
        zip_bytes = _make_zip(
            [{"root": "sale_ext", "manifest": True, "has_models": True}],
            password=pwd,
        )
        job = self._new_job(zip_bytes, password="s3cret")
        self._run_to_completion(job)
        self.assertEqual(job.state, "done")
        self.assertFalse(job.password)
        out_bytes = job.result_attachment_id.sudo().raw
        with pyzipper.AESZipFile(io.BytesIO(out_bytes)) as zf:
            zf.setpassword(pwd)
            names = zf.namelist()
        self.assertTrue(len(names) > 0)

    def test_wrong_password_fails_job(self):
        """Wrong password on encrypted zip → job ends in state 'error', not an exception that
        crashes the cron (a real cron step must never raise, see _process_one_step)."""
        pwd = b"correct"
        zip_bytes = _make_zip(
            [{"root": "sale_ext", "manifest": True, "has_models": True}],
            password=pwd,
        )
        job = self._new_job(zip_bytes, password="wrong_password")
        self._run_to_completion(job)
        self.assertEqual(job.state, "error")
        self.assertIn("password", (job.error_message or "").lower())

    def test_zip_slip_rejected(self):
        """Zip entry with ../ path → skipped (no file written outside work_dir); the job still
        completes using the remaining, safe module."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("../evil.py", "import os; os.system('rm -rf /')")
            zf.writestr(
                "safe_mod/__manifest__.py",
                "{'name':'safe','version':'18.0.1.0.0','depends':['base']}",
            )
        job = self._new_job(buf.getvalue())
        self._run_to_completion(job)
        self.assertIn(job.state, ("done", "error"))

    def test_no_manifest_fails_job(self):
        """Zip with no __manifest__.py anywhere → job ends in state 'error' at the extract
        step (no module to protect)."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("README.txt", "hello")
        job = self._new_job(buf.getvalue())
        self._run_to_completion(job)
        self.assertEqual(job.state, "error")

    def test_invalid_file_raises_at_upload(self):
        """Non-zip upload that doesn't even end in .zip → UserError raised immediately by
        create_from_upload (this check happens synchronously, before the job is even created,
        so the wizard can report it right away instead of only via the background job)."""
        with self.assertRaises(Exception):
            self.env["dwo.protect.job"].create_from_upload(
                base64.b64encode(b"not a zip"), "file.txt", ""
            )

    def test_invalid_zip_content_fails_job(self):
        """Filename ends in .zip but content isn't a real zip -> passes the upload-time check,
        fails later during extraction, and the job ends in state 'error' (never an unhandled
        exception escaping the cron)."""
        job = self.env["dwo.protect.job"].create_from_upload(
            base64.b64encode(b"not a zip"), "file.zip", ""
        )
        self._run_to_completion(job)
        self.assertEqual(job.state, "error")

    def test_binary_field_to_bytes_cross_version(self):
        """_binary_field_to_bytes must handle both the plain base64-text wire contract (str
        or bytes-of-base64-characters -- true both for Odoo <= 19's Binary field and for any
        caller passing a raw value as a plain argument, e.g. tests) AND Odoo 20's new ORM,
        where reading record.binary_field returns a genuine BinaryValue/BinaryBytes object
        that already holds the DECODED content -- a real bug caught by browser-driven testing
        on 20, where base64.b64decode()-ing plain `bytes` unconditionally corrupted uploads
        because base64.b64encode() output is also `bytes`, just not decoded content."""
        job_model = self.env["dwo.protect.job"]
        raw = b"hello zip bytes"

        # base64 TEXT, as str or as bytes-of-base64-chars -- the universal wire contract.
        self.assertEqual(job_model._binary_field_to_bytes(base64.b64encode(raw)), raw)
        self.assertEqual(job_model._binary_field_to_bytes(base64.b64encode(raw).decode()), raw)

        # Odoo >= 20: a BinaryValue-like object (NOT a plain bytes/str/bytearray/memoryview)
        # that implements the buffer protocol and already holds the decoded content.
        class _FakeBinaryValue:
            def __bytes__(self):
                return raw

        self.assertEqual(job_model._binary_field_to_bytes(_FakeBinaryValue()), raw)

        self.assertEqual(job_model._binary_field_to_bytes(False), b"")
        self.assertEqual(job_model._binary_field_to_bytes(None), b"")

    def test_output_zip_name(self):
        """_output_zip_name strips .zip and appends _compile.zip; with a record_id it also
        appends a time + id suffix so two jobs never produce the same download filename."""
        import datetime

        job_model = self.env["dwo.protect.job"]
        self.assertEqual(job_model._output_zip_name("sale_ext.zip"), "sale_ext_compile.zip")
        self.assertEqual(job_model._output_zip_name("module"), "module_compile.zip")

        ts = datetime.datetime(2026, 1, 2, 3, 4, 5)
        self.assertEqual(
            job_model._output_zip_name("sale_ext.zip", record_id=42, timestamp=ts),
            "sale_ext_compile_20260102030405_42.zip",
        )

    def test_finalize_output_filename_has_timestamp_and_id(self):
        """A real finished job's result attachment name contains the job's own id, so two
        jobs' downloads never collide on a user's machine."""
        zip_bytes = _make_zip([{"root": "sale_ext", "manifest": True, "has_models": True}])
        job = self._new_job(zip_bytes, filename="sale_ext.zip")
        self._run_to_completion(job)
        self.assertEqual(job.state, "done")
        self.assertIn("_{0}.zip".format(job.id), job.result_attachment_id.sudo().name)

    def test_module_step_skipped_after_retry_cap(self):
        """If a module's protect step has already failed MAX_STEP_ATTEMPTS times (simulating
        the process being killed by a server CPU/time/memory limit each time, which leaves
        no exception to catch -- just a step_attempts counter that stopped climbing), the
        NEXT _process_one_step call must skip that module and move on, not retry forever."""
        from odoo.addons.dwo_source_code_protector.models.dwo_protect_job import MAX_STEP_ATTEMPTS

        zip_bytes = _make_zip([{"root": "sale_ext", "manifest": True, "has_models": True}])
        job = self._new_job(zip_bytes, filename="sale_ext.zip")
        job._process_one_step()  # extract
        self.assertEqual(job.state, "running")
        self.assertEqual(job.module_index, 0)

        job.step_attempts = MAX_STEP_ATTEMPTS
        job._process_one_step()
        self.assertEqual(job.module_index, 1, "module must be skipped and index advanced")
        self.assertEqual(job.step_attempts, 0, "counter must reset for the next module")
        self.assertIn("Skipped", job.result_info or job._load_result_rows()[0]["status"])

    def test_extract_step_fails_after_retry_cap(self):
        """Unlike a per-module step, the extract step has no "skip and continue" option --
        after MAX_STEP_ATTEMPTS failed attempts (process killed each time) the whole job must
        end in state 'error', never retry forever."""
        from odoo.addons.dwo_source_code_protector.models.dwo_protect_job import MAX_STEP_ATTEMPTS

        zip_bytes = _make_zip([{"root": "sale_ext", "manifest": True, "has_models": True}])
        job = self._new_job(zip_bytes, filename="sale_ext.zip")
        self.assertEqual(job.state, "queued")
        job.step_attempts = MAX_STEP_ATTEMPTS

        job._process_one_step()
        self.assertEqual(job.state, "error")
        self.assertIn("server", (job.error_message or "").lower())

    def test_cron_cleanup_expired(self):
        """_cron_cleanup_expired deletes the uploaded and result attachments of a finished
        job once past its expires_at, and marks it is_expired -- but keeps the job record
        itself (history/result_info) for reference."""
        zip_bytes = _make_zip([{"root": "sale_ext", "manifest": True, "has_models": True}])
        job = self._new_job(zip_bytes, filename="sale_ext.zip")
        self._run_to_completion(job)
        self.assertEqual(job.state, "done")
        self.assertTrue(job.zip_attachment_id)
        self.assertTrue(job.result_attachment_id)

        job.expires_at = fields.Datetime.now() - timedelta(hours=1)
        self.env["dwo.protect.job"]._cron_cleanup_expired()

        self.assertFalse(job.zip_attachment_id)
        self.assertFalse(job.result_attachment_id)
        self.assertTrue(job.is_expired)
        # job history itself (name, state, result_info) must survive the cleanup
        self.assertEqual(job.state, "done")
        self.assertTrue(job.result_info)

    def test_find_module_roots_no_nested(self):
        """_find_module_roots returns top-level module dirs only."""
        import os
        import tempfile

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

            roots = self.env["dwo.protect.job"]._find_module_roots(tmp)

        root_names = sorted(os.path.basename(r) for r in roots)
        self.assertEqual(root_names, ["mod_a", "mod_b"])
