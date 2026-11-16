# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import base64
import gzip
import io
import json
import tarfile
import zipfile
from types import SimpleNamespace
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import HttpCase, TransactionCase, tagged
from odoo.tools.misc import file_path

from odoo.addons.dwo_attpreview_core.controllers.main import AttPreviewController

MODULE = "dwo_attpreview_archive"
REQUEST = "odoo.addons.dwo_attpreview_core.controllers.main.request"
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")


def make_zip(entries, flag_utf8=True):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in entries:
            if name.endswith("/"):
                zf.writestr(zipfile.ZipInfo(name), b"")
            else:
                zf.writestr(name, data)
    return buf.getvalue()


def make_tar(entries, mode="w:gz"):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode=mode) as tf:
        for name, data in entries:
            info = tarfile.TarInfo(name)
            if data is None:
                info.type, info.linkname = tarfile.SYMTYPE, "target"
                tf.addfile(info)
            else:
                info.size = len(data)
                tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def sample(name):
    with open(file_path("%s/tests/files/%s" % (MODULE, name)), "rb") as f:
        return f.read()


INNER = make_zip([("deep/readme.txt", b"inside")])
ZIP = make_zip([("Report 2024/summary.pdf", b"%PDF-1.4"), ("Report 2024/data/sales.csv", b"a,b\n1,2\n"),
                ("Report 2024/logo.png", PNG), ("Report 2024/inner.zip", INNER), ("empty dir/", b""),
                ("../outside.txt", b"x")])


@tagged("post_install", "-at_install")
class TestArchiveEngine(TransactionCase):

    def setUp(self):
        super().setUp()
        self.engine = self.env["dwo.attpreview.engine.archive"]

    def render(self, content, name):
        out = self.engine._dwo_render(content, name)
        self.assertEqual(out["type"], "json")
        json.dumps(out["data"])
        return out["data"]

    def test_01_zip_tree(self):
        d = self.render(ZIP, "report.zip")
        self.assertEqual(d["format"], "zip")
        self.assertEqual(d["dirs"], ["", "Report 2024", "Report 2024/data", "empty dir", ".."],
                         "folders made from the paths; '..' is only a name")
        names = [(d["dirs"][row[0]], row[1]) for row in d["files"]]
        self.assertEqual(names[:4], [("Report 2024", "summary.pdf"), ("Report 2024/data", "sales.csv"),
                                     ("Report 2024", "logo.png"), ("Report 2024", "inner.zip")])
        self.assertEqual(d["size"], sum(row[2] for row in d["files"]))
        self.assertEqual((d["truncated"], d["encrypted"], d["extract_hint"]), (False, 0, ""))

    def test_02_extract_by_position_and_nested(self):
        self.assertEqual(self.engine._dwo_extract_part(ZIP, "report.zip", 1), ("sales.csv", b"a,b\n1,2\n"))
        name, inner = self.engine._dwo_extract_part(ZIP, "report.zip", 3)
        self.assertEqual(self.engine._dwo_extract_part(inner, name, 0), ("readme.txt", b"inside"))
        self.assertIsNone(self.engine._dwo_extract_part(ZIP, "report.zip", 99))

    def test_03_utf8_names_without_the_utf8_flag(self):
        name = "Hợp đồng/Báo cáo.txt".encode()
        # UTF-8 bytes stored without the UTF-8 flag (what many zip tools do): Python reads them as cp437
        buf = io.BytesIO()
        placeholder = b"q" * len(name)  # ASCII name of the same length, so the UTF-8 flag is not set
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr(zipfile.ZipInfo(placeholder.decode()), b"1")
        raw = buf.getvalue().replace(placeholder, name)
        self.assertFalse(zipfile.ZipFile(io.BytesIO(raw)).infolist()[0].flag_bits & 0x800)
        d = self.render(raw, "vn.zip")
        self.assertEqual((d["dirs"][1], d["files"][0][1]), ("Hợp đồng", "Báo cáo.txt"))

    def test_04_tar_family_and_single_gz(self):
        tgz = make_tar([("proj/src/main.py", b"print(1)"), ("proj/README.md", b"# hi"), ("proj/link", None)])
        d = self.render(tgz, "proj.tar.gz")  # the Core sees the extension "gz"
        self.assertEqual(d["format"], "tar.gz")
        self.assertEqual([row[1] for row in d["files"]], ["main.py", "README.md", "link"])
        self.assertEqual(d["files"][2][4], 2, "a link is marked, it has no content")
        self.assertEqual(self.engine._dwo_extract_part(tgz, "proj.tar.gz", 1), ("README.md", b"# hi"))
        with self.assertRaises(UserError):
            self.engine._dwo_extract_part(tgz, "proj.tar.gz", 2)
        for mode, name in (("w:bz2", "p.tbz2"), ("w:xz", "p.tar.xz"), ("w", "p.tar")):
            self.assertEqual(self.render(make_tar([("a.txt", b"1")], mode), name)["files"][0][1], "a.txt")
        single = gzip.compress(b"a,b\n")
        d = self.render(single, "export.csv.gz")
        self.assertEqual((d["format"], d["files"][0][1]), ("gz", "export.csv"))
        self.assertEqual(self.engine._dwo_extract_part(single, "export.csv.gz", 0), ("export.csv", b"a,b\n"))

    def test_05_bombs_and_limits(self):
        with self.assertRaises(UserError):
            self.render(gzip.compress(b"\0" * (600 * 1024 * 1024)), "bomb.gz")
        self.env["ir.config_parameter"].sudo().set_int("dwo_attpreview.max_file_size_mb", 1)  # Odoo 20: typed setters
        with patch("odoo.addons.dwo_attpreview_archive.models.engine.MIN_EXTRACT_MB", 1):
            big = make_zip([("big.bin", b"\0" * (2 * 1024 * 1024))])
            with self.assertRaises(UserError):
                self.engine._dwo_extract_part(big, "big.zip", 0)

    def test_06_garbage(self):
        for content in (b"", b"not an archive", b"PK\x03\x04broken"):
            with self.assertRaises(UserError):
                self.render(content, "x.zip")

    def test_07_rar(self):
        d = self.render(sample("rar5-subdirs.rar"), "s.rar")
        self.assertEqual(d["format"], "rar")
        self.assertIn("sub/üȵĩöḋè", d["dirs"])
        self.assertIn(["file2.txt"], [[row[1]] for row in d["files"]])
        d = self.render(sample("rar3-comment-psw.rar"), "p.rar")
        self.assertEqual(d["encrypted"], 2)
        with self.assertRaises(UserError):
            self.engine._dwo_extract_part(sample("rar3-comment-psw.rar"), "p.rar", 0)
        self.assertEqual(self.render(sample("unicode.rar"), "u.rar")["files"][1][1], "𝐀𝐁𝐁𝐂.txt")

    def test_08_7z_without_py7zr_says_how_to_install(self):
        try:
            import py7zr  # noqa: F401
            self.skipTest("py7zr is installed on this server")
        except ImportError:
            pass
        with self.assertRaisesRegex(UserError, "pip install py7zr"):
            self.render(b"7z\xbc\xaf\x27\x1c" + b"\0" * 64, "a.7z")

    def test_09_large_archive_index_above_10000(self):
        big = make_zip([("folder%02d/file%05d.txt" % (i // 1000, i), b"%d" % i) for i in range(12000)])
        att = self.env["ir.attachment"].create({"name": "big.zip", "raw": big})
        ctrl = AttPreviewController()
        with patch(REQUEST, new=SimpleNamespace(env=self.env)):
            info = ctrl.info(att.id)
            self.assertEqual((info["mode"], info["engine"], info["width"]), ("rendered", "archive", "medium"))
            self.assertEqual(len(json.loads(info["content"])["files"]), 12000)
            out = ctrl.part_info(info["source_ref"], "11999")
        self.assertEqual((out["name"], out["mode"]), ("file11999.txt", "unsupported"))

    def test_10_zip_in_an_email_level_after_level(self):
        if "dwo.attpreview.engine.mail" not in self.env:
            self.skipTest("the email engine is not installed")
        from email.message import EmailMessage
        msg = EmailMessage()
        msg["Subject"] = "Files"
        msg.set_content("see attached")
        msg.add_attachment(ZIP, maintype="application", subtype="zip", filename="report.zip")
        att = self.env["ir.attachment"].create({"name": "files.eml", "raw": msg.as_bytes()})
        ctrl = AttPreviewController()
        with patch(REQUEST, new=SimpleNamespace(env=self.env)):
            ref = ctrl.info(att.id)["source_ref"]
            zip_info = ctrl.part_info(ref, "0")
            self.assertEqual((zip_info["engine"], zip_info["name"]), ("archive", "report.zip"))
            deep = ctrl.part_info(ref, "0/3/0")
        self.assertEqual(deep["name"], "readme.txt")


@tagged("post_install", "-at_install")
class TestArchiveTour(HttpCase):

    def test_01_tree_filter_and_preview(self):
        partner = self.env["res.partner"].create({"name": "Archive tour"})
        files = [("Project/docs/page%05d.txt" % i, b"x") for i in range(20000)]
        files += [("Project/logo.png", PNG), ("Project/inner.zip", INNER)]
        att = self.env["ir.attachment"].create({"name": "Project files.zip", "raw": make_zip(files),
                                                "res_model": "res.partner", "res_id": partner.id})
        partner.message_post(body="archive", attachment_ids=[att.id])
        self.start_tour("/odoo/res.partner/%d" % partner.id, "dwo_attpreview_archive_tour", login="admin")
