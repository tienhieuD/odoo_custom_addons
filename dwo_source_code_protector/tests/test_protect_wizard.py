import base64
import getpass
import io
import json
import os
import re
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


def _make_zip(modules, password=None):
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
    """Exercises the dwo.protect.job pipeline directly, either one step at a time or via
    run_sync() (what the wizard calls), instead of going through the wizard UI."""

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
        out_bytes = base64.b64decode(job.result_attachment_id.sudo().datas)
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
        out_bytes = base64.b64decode(job.result_attachment_id.sudo().datas)
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
        out_bytes = base64.b64decode(job.result_attachment_id.sudo().datas)
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
        """_output_zip_name strips .zip and appends _compile_<py_tag>.zip; with a record_id it
        also appends a time + id suffix so two jobs never produce the same download filename.
        With no explicit python_version, it falls back to the CURRENT interpreter's."""
        import datetime
        import sys

        job_model = self.env["dwo.protect.job"]
        current_tag = "py" + "".join(str(p) for p in sys.version_info[:3])
        self.assertEqual(
            job_model._output_zip_name("sale_ext.zip"), "sale_ext_compile_{0}.zip".format(current_tag)
        )
        self.assertEqual(
            job_model._output_zip_name("module"), "module_compile_{0}.zip".format(current_tag)
        )

        ts = datetime.datetime(2026, 1, 2, 3, 4, 5)
        self.assertEqual(
            job_model._output_zip_name(
                "sale_ext.zip", record_id=42, timestamp=ts, python_version="3.11.9"
            ),
            "sale_ext_compile_py3119_20260102030405_42.zip",
        )

    def test_python_version_tag(self):
        job_model = self.env["dwo.protect.job"]
        self.assertEqual(job_model._python_version_tag("3.12.3"), "py3123")
        self.assertEqual(job_model._python_version_tag("3.9.0"), "py390")

    def test_finalize_output_filename_has_timestamp_and_id(self):
        """A real finished job's result attachment name contains the job's own id, so two
        jobs' downloads never collide on a user's machine."""
        zip_bytes = _make_zip([{"root": "sale_ext", "manifest": True, "has_models": True}])
        job = self._new_job(zip_bytes, filename="sale_ext.zip")
        self._run_to_completion(job)
        self.assertEqual(job.state, "done")
        self.assertIn("_{0}.zip".format(job.id), job.result_attachment_id.sudo().name)

    def test_job_records_python_version(self):
        """python_version is set once extraction starts and the output filename carries the
        matching tag."""
        import sys

        zip_bytes = _make_zip([{"root": "sale_ext", "manifest": True, "has_models": True}])
        job = self._new_job(zip_bytes, filename="sale_ext.zip")
        self.assertFalse(job.python_version)
        job._process_one_step()  # extract
        expected = "{0}.{1}.{2}".format(*sys.version_info[:3])
        self.assertEqual(job.python_version, expected)

        self._run_to_completion(job)
        self.assertEqual(job.state, "done")
        tag = "py" + "".join(str(p) for p in sys.version_info[:3])
        self.assertIn("_{0}_".format(tag), job.result_attachment_id.sudo().name)

    def test_run_sync_processes_whole_job(self):
        """run_sync() (called by the wizard) loops _process_one_step() until the job is done
        or errored, all within one call -- this Odoo version has no background job mechanism
        to resume across, so the whole pipeline must run synchronously."""
        zip_bytes = _make_zip([{"root": "sale_ext", "manifest": True, "has_models": True}])
        job = self._new_job(zip_bytes, filename="sale_ext.zip")
        job.run_sync()
        self.assertEqual(job.state, "done")
        self.assertIn("Protected", job.result_info)

    def test_cron_fail_stale_jobs(self):
        """A job stuck in 'running' (simulating the request having been killed mid-protect by
        a server CPU/time limit, with nothing left to resume it) must be marked 'error' by
        _cron_fail_stale_jobs() once old enough, rather than staying stuck forever."""
        zip_bytes = _make_zip([{"root": "sale_ext", "manifest": True, "has_models": True}])
        job = self._new_job(zip_bytes, filename="sale_ext.zip")
        job._process_one_step()  # extract only -> state becomes "running"
        self.assertEqual(job.state, "running")

        # backdate create_date so the job looks old enough to be considered stale
        self.env.cr.execute(
            "UPDATE dwo_protect_job SET create_date = create_date - interval '1 hour' WHERE id = %s",
            (job.id,),
        )
        job.invalidate_cache(["create_date"])

        self.env["dwo.protect.job"]._cron_fail_stale_jobs()
        self.assertEqual(job.state, "error")
        self.assertIn("minutes", (job.error_message or "").lower())

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

    # ------------------------------------------------------------------ #
    # Result zip must not leak the server's paths / user name (issue #2)

    def _result_files(self, job):
        out_bytes = base64.b64decode(job.result_attachment_id.sudo().datas)
        with zipfile.ZipFile(io.BytesIO(out_bytes)) as zf:
            return {n: zf.read(n) for n in zf.namelist() if not n.endswith("/")}

    def test_result_zip_does_not_leak_server_paths(self):
        """No file in the result zip (manifest report, stubs, .so, anything) may contain an
        absolute path of the server: the job work dir, the data dir, the home dir, the OS
        user name in a path, or any /Users/<x>/ or /home/<x>/ style path."""
        from odoo.tools import config

        zip_bytes = _make_zip([{"root": "sale_ext", "manifest": True, "has_models": True}])
        job = self._new_job(zip_bytes, filename="sale_ext.zip")
        # the work dir is deleted when the job finishes: remember it from the extract step
        job._process_one_step()
        work_dir = job.work_dir
        self._run_to_completion(job)
        self.assertEqual(job.state, "done")
        forbidden = [work_dir, os.path.dirname(work_dir), os.path.expanduser("~")]
        data_dir = config.get("data_dir")
        if data_dir:
            forbidden.append(data_dir)
        user = getpass.getuser()
        forbidden += ["/Users/%s" % user, "/home/%s" % user]
        forbidden = [f.encode() for f in forbidden if f and len(f) > 4]
        pattern = re.compile(rb"/(?:Users|home)/[A-Za-z0-9._-]+|/var/folders/|/private/(?:var|tmp)/|dwo_protect_jobs")
        files = self._result_files(job)
        self.assertTrue(files)
        for name, content in files.items():
            for bad in forbidden:
                self.assertNotIn(bad, content, "%s leaks server path %r" % (name, bad))
            self.assertIsNone(pattern.search(content), "%s leaks a server-looking path" % name)

    def test_result_manifest_uses_relative_paths(self):
        """protection-manifest.json stays (useful to the customer) but lists paths relative
        to the module folder."""
        zip_bytes = _make_zip([{"root": "sale_ext", "manifest": True, "has_models": True}])
        job = self._new_job(zip_bytes, filename="sale_ext.zip")
        self._run_to_completion(job)
        files = self._result_files(job)
        report = json.loads(files["sale_ext/protection-manifest.json"].decode())
        self.assertEqual(report["module_root"], "sale_ext")
        self.assertEqual(report["output_root"], "sale_ext")
        self.assertIn("models/test_model.py", report["selected_files"])
        self.assertTrue(report["transformed_files"])
        for key in ("selected_files", "skipped_files", "transformed_files", "compiled_artifacts"):
            for path in report[key]:
                self.assertFalse(os.path.isabs(path), "%s has absolute path %s" % (key, path))
                self.assertNotIn("..", path.split("/"))
        self.assertTrue(report["compiled_count"] == len(report["compiled_artifacts"]))
        for path in report["compile_failures"]:
            self.assertFalse(os.path.isabs(path["file"]))

    def test_result_zip_strips_uploaded_bytecode(self):
        """__pycache__/.pyc and .DS_Store in the uploaded zip embed the uploader's own build
        paths (and stale bytecode of the unprotected source): they are dropped from the
        result."""
        zip_bytes = _make_zip([
            {"root": "sale_ext", "manifest": True, "has_models": True},
            {"path": "sale_ext/models/__pycache__/test_model.cpython-312.pyc",
             "content": b"\x00/Users/uploader/proj/sale_ext/models/test_model.py"},
            {"path": "sale_ext/.DS_Store", "content": b"x"},
        ])
        job = self._new_job(zip_bytes, filename="sale_ext.zip")
        self._run_to_completion(job)
        names = list(self._result_files(job))
        self.assertFalse([n for n in names if "__pycache__" in n or n.endswith(".pyc")], names)
        self.assertFalse([n for n in names if n.endswith(".DS_Store")], names)

    # ------------------------------------------------------------------ #
    # Result zip must not leak the server's paths / user name (issue #2)

    def _result_files(self, job):
        out_bytes = base64.b64decode(job.result_attachment_id.sudo().datas)
        with zipfile.ZipFile(io.BytesIO(out_bytes)) as zf:
            return {n: zf.read(n) for n in zf.namelist() if not n.endswith("/")}

    def test_result_zip_does_not_leak_server_paths(self):
        """No file in the result zip (manifest report, stubs, .so, anything) may contain an
        absolute path of the server: the job work dir, the data dir, the home dir, the OS
        user name in a path, or any /Users/<x>/ or /home/<x>/ style path."""
        from odoo.tools import config

        zip_bytes = _make_zip([{"root": "sale_ext", "manifest": True, "has_models": True}])
        job = self._new_job(zip_bytes, filename="sale_ext.zip")
        # the work dir is deleted when the job finishes: remember it from the extract step
        job._process_one_step()
        work_dir = job.work_dir
        self._run_to_completion(job)
        self.assertEqual(job.state, "done")
        forbidden = [work_dir, os.path.dirname(work_dir), os.path.expanduser("~")]
        data_dir = config.get("data_dir")
        if data_dir:
            forbidden.append(data_dir)
        user = getpass.getuser()
        forbidden += ["/Users/%s" % user, "/home/%s" % user]
        forbidden = [f.encode() for f in forbidden if f and len(f) > 4]
        pattern = re.compile(rb"/(?:Users|home)/[A-Za-z0-9._-]+|/var/folders/|/private/(?:var|tmp)/|dwo_protect_jobs")
        files = self._result_files(job)
        self.assertTrue(files)
        for name, content in files.items():
            for bad in forbidden:
                self.assertNotIn(bad, content, "%s leaks server path %r" % (name, bad))
            self.assertIsNone(pattern.search(content), "%s leaks a server-looking path" % name)

    def test_result_manifest_uses_relative_paths(self):
        """protection-manifest.json stays (useful to the customer) but lists paths relative
        to the module folder."""
        zip_bytes = _make_zip([{"root": "sale_ext", "manifest": True, "has_models": True}])
        job = self._new_job(zip_bytes, filename="sale_ext.zip")
        self._run_to_completion(job)
        files = self._result_files(job)
        report = json.loads(files["sale_ext/protection-manifest.json"].decode())
        self.assertEqual(report["module_root"], "sale_ext")
        self.assertEqual(report["output_root"], "sale_ext")
        self.assertIn("models/test_model.py", report["selected_files"])
        self.assertTrue(report["transformed_files"])
        for key in ("selected_files", "skipped_files", "transformed_files", "compiled_artifacts"):
            for path in report[key]:
                self.assertFalse(os.path.isabs(path), "%s has absolute path %s" % (key, path))
                self.assertNotIn("..", path.split("/"))
        self.assertTrue(report["compiled_count"] == len(report["compiled_artifacts"]))
        for path in report["compile_failures"]:
            self.assertFalse(os.path.isabs(path["file"]))

    def test_result_zip_strips_uploaded_bytecode(self):
        """__pycache__/.pyc and .DS_Store in the uploaded zip embed the uploader's own build
        paths (and stale bytecode of the unprotected source): they are dropped from the
        result."""
        zip_bytes = _make_zip([
            {"root": "sale_ext", "manifest": True, "has_models": True},
            {"path": "sale_ext/models/__pycache__/test_model.cpython-312.pyc",
             "content": b"\x00/Users/uploader/proj/sale_ext/models/test_model.py"},
            {"path": "sale_ext/.DS_Store", "content": b"x"},
        ])
        job = self._new_job(zip_bytes, filename="sale_ext.zip")
        self._run_to_completion(job)
        names = list(self._result_files(job))
        self.assertFalse([n for n in names if "__pycache__" in n or n.endswith(".pyc")], names)
        self.assertFalse([n for n in names if n.endswith(".DS_Store")], names)

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
