# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import base64
import io
import os
import zipfile
from unittest.mock import Mock, patch

import odoo
from odoo import http
from odoo.exceptions import UserError
from odoo.tests import HttpCase, TransactionCase, tagged
from odoo.tools import file_path

MODULE = "dwo_attpreview_office"
OFFICE_LIMIT_KEYS = ("office_sheet", "office_doc", "office_slide", "office_csv")


def _set_limits(env, value):
    """Size limit (MB) of every Office file group; ``None`` = not set (the default of the group)."""
    param = env["ir.config_parameter"].sudo()
    for key in OFFICE_LIMIT_KEYS:
        param.set_param("dwo_attpreview.max_mb." + key, value)


def _fixture(name):
    with open(file_path("%s/tests/files/%s" % (MODULE, name)), "rb") as f:
        return f.read()


# Macro-enabled and template variants (#70), built from the samples like Office writes them: same parts, another
# content type for the main part; the macro ones also get a vbaProject.bin part (an empty OLE container: no macro).
VARIANT_TYPES = {
    "xlsm": ("xlsx", "application/vnd.ms-excel.sheet.macroEnabled.main+xml"),
    "xltx": ("xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.template.main+xml"),
    "xltm": ("xlsx", "application/vnd.ms-excel.template.macroEnabled.main+xml"),
    "docm": ("docx", "application/vnd.ms-word.document.macroEnabled.main+xml"),
    "dotx": ("docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml"),
    "dotm": ("docx", "application/vnd.ms-word.template.macroEnabledTemplate.main+xml"),
    "pptm": ("pptx", "application/vnd.ms-powerpoint.presentation.macroEnabled.main+xml"),
    "ppsx": ("pptx", "application/vnd.openxmlformats-officedocument.presentationml.slideshow.main+xml"),
    "ppsm": ("pptx", "application/vnd.ms-powerpoint.slideshow.macroEnabled.main+xml"),
    "potx": ("pptx", "application/vnd.openxmlformats-officedocument.presentationml.template.main+xml"),
    "potm": ("pptx", "application/vnd.ms-powerpoint.template.macroEnabled.main+xml"),
}
BASE_TYPES = {
    "xlsx": ("xl", "workbook.xml", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"),
    "docx": ("word", "document.xml", "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"),
    "pptx": ("ppt", "presentation.xml", "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"),
}


def _variant(ext, sample=None):
    base, content_type = VARIANT_TYPES[ext]
    folder, main, base_type = BASE_TYPES[base]
    macro = "macroEnabled" in content_type
    src = zipfile.ZipFile(io.BytesIO(_fixture(sample or "sample.%s" % base)))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as out:
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename == "[Content_Types].xml":
                text = data.decode()
                assert base_type in text
                text = text.replace(base_type, content_type)
                if macro:
                    text = text.replace(
                        "</Types>", '<Default Extension="bin" ContentType="application/vnd.ms-office.vbaProject"/></Types>')
                data = text.encode()
            elif macro and info.filename == "%s/_rels/%s.rels" % (folder, main):
                data = data.decode().replace("</Relationships>", (
                    '<Relationship Id="rIdVba1" Type="http://schemas.microsoft.com/office/2006/relationships/vbaProject"'
                    ' Target="vbaProject.bin"/></Relationships>')).encode()
            out.writestr(info.filename, data)
        if macro:
            out.writestr("%s/vbaProject.bin" % folder, b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\0" * 1528)
    return buf.getvalue()


# OpenDocument (#84): the templates are the samples with the template media type (in `mimetype` and in the manifest)
ODF_TEMPLATES = {"ott": "odt", "ots": "ods", "otp": "odp"}
ODF_MIMETYPES = {
    "odt": "application/vnd.oasis.opendocument.text",
    "ods": "application/vnd.oasis.opendocument.spreadsheet",
    "odp": "application/vnd.oasis.opendocument.presentation",
}
ENCRYPTION_DATA = (
    '<manifest:encryption-data manifest:checksum-type="SHA1/1K" manifest:checksum="AAAA">'
    '<manifest:algorithm manifest:algorithm-name="Blowfish CFB" manifest:initialisation-vector="AAAA"/>'
    '<manifest:key-derivation manifest:key-derivation-name="PBKDF2" manifest:iteration-count="1024" '
    'manifest:salt="AAAA"/></manifest:encryption-data>')


def _odf(base, template=False, encrypted=False, mimetype=None, stored_first=True):
    """sample.<base> rewritten: as a template, with content.xml marked as encrypted in the manifest (what a document
    saved with a password declares), another `mimetype`, or `mimetype` compressed and not first (re-zipped)."""
    src = zipfile.ZipFile(io.BytesIO(_fixture("sample.%s" % base)))
    media = ODF_MIMETYPES[base] + ("-template" if template else "")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as out:
        if not stored_first:
            out.writestr("aaa.txt", b"first")
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename == "mimetype":
                data = (mimetype or media).encode()
                out.writestr("mimetype", data, compress_type=zipfile.ZIP_STORED if stored_first else zipfile.ZIP_DEFLATED)
                continue
            if info.filename == "META-INF/manifest.xml":
                text = data.decode().replace('"%s"' % ODF_MIMETYPES[base], '"%s"' % media)
                if encrypted:
                    needle = 'manifest:full-path="content.xml" manifest:media-type="text/xml"/>'
                    assert needle in text
                    text = text.replace(needle, needle[:-2] + ">" + ENCRYPTION_DATA + "</manifest:file-entry>")
                data = text.encode()
            out.writestr(info.filename, data)
    return buf.getvalue()


def _zip(entries, level=1):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=level) as z:
        for name, data in entries:
            z.writestr(name, data)
    return buf.getvalue()


@tagged("post_install", "-at_install")
class TestOfficeEngine(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Engines = cls.env["dwo.attpreview.engine"]
        cls.engine = cls.env["dwo.attpreview.engine.office"]
        cls.Model = cls.engine

    def _attachment(self, name, raw):
        return self.env["ir.attachment"].create({"name": name, "raw": raw})

    def _render(self, name, raw):
        return self.env["dwo.attpreview.cache"]._get_or_render(self._attachment(name, raw), self.engine)

    def test_01_registered_client_side(self):
        self.assertEqual(set(self.engine._dwo_engine_extensions), {
            "xlsx", "docx", "pptx", "doc", "xls", "ppt", "csv", "tsv",
            "odt", "ods", "odp", "ott", "ots", "otp"} | set(VARIANT_TYPES))
        self.assertEqual(self.engine._dwo_engine_output, "text")
        for name in ("a.xlsx", "A.DOCX", "b.pptx", "a.xls", "a.DOC", "a.ppt", "a.csv", "a.TSV", "a.odt", "A.ODS",
                     "a.odp", "a.ott", "a.ots", "a.otp"):
            found = self.Engines._dwo_find_engine(name)
            self.assertIsNotNone(found, name)
            self.assertEqual(found._dwo_engine_code, "office", name)
        for name in ("a.xlsb", "a.rtf", "a.txt", "a.odg", "a.odf", "a.fodt", "a.pages"):  # out of scope
            found = self.Engines._dwo_find_engine(name)
            self.assertTrue(found is None or found._dwo_engine_code != "office", name)

    def test_02_real_files_are_accepted(self):
        for name in ("sample.xlsx", "sample.docx", "sample.pptx"):
            rec = self._render(name, _fixture(name))
            self.assertFalse(rec.error, name)
            self.assertEqual(rec.result_type, "text")
            self.assertEqual(rec.data and __import__("base64").b64decode(rec.data).decode(), name.split(".")[1])

    def test_03_damaged_files_give_friendly_errors(self):
        good = _fixture("sample.docx")
        cases = {
            "truncated.docx": good[: len(good) // 2],
            "text.xlsx": b"plain text, not a zip\n" * 10,
            "empty.pptx": b"",
            "nomain.xlsx": _zip([("hello.txt", b"hi")]),
            "wrongkind.docx": _fixture("sample.xlsx"),  # a real xlsx named .docx has no word/document.xml
            "ole.xlsx": b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\0" * 100,  # old binary / encrypted container
        }
        for name, raw in cases.items():
            rec = self._render(name, raw)
            self.assertTrue(rec.error, name)
            self.assertFalse(rec.data, name)
            self.assertNotIn("Traceback", rec.error)

    def test_04_zip_bomb_is_refused(self):
        # one part of 129 MiB once unpacked (the library allows 128 MiB): tiny on disk
        raw = _zip([("[Content_Types].xml", b"<Types/>"), ("xl/workbook.xml", b"<workbook/>"),
                    ("xl/worksheets/sheet1.xml", b"\0" * (129 * 1024 * 1024))], level=9)
        self.assertLess(len(raw), 1024 * 1024)
        rec = self._render("bomb.xlsx", raw)
        self.assertIn("too large once unpacked", rec.error)

    def test_05_many_parts_over_total_limit(self):
        entries = [("word/document.xml", b"<d/>")] + [("word/media/m%d.bin" % i, b"\0" * (100 * 1024 * 1024))
                                                      for i in range(3)]
        rec = self._render("bomb2.docx", _zip(entries, level=1))
        self.assertIn("too large once unpacked", rec.error)

    def test_06_too_many_entries(self):
        raw = _zip([("word/document.xml", b"<d/>")] + [("f%d" % i, b"") for i in range(20001)])
        rec = self._render("many.docx", raw)
        self.assertIn("too many parts", rec.error)

    def test_07_core_size_limit_applies(self):
        _set_limits(self.env, "0")
        rec = self._render("big.xlsx", _fixture("sample.xlsx"))
        self.assertIn("larger than the preview limit", rec.error)
        self.assertFalse(rec.data)

    def test_08_engine_size_override(self):
        _set_limits(self.env, "1")  # 1 MB for each group of Office files
        rec = self._render("ok.xlsx", _fixture("sample.xlsx"))
        self.assertFalse(rec.error)
        big = _zip([("xl/workbook.xml", b"<w/>"), ("x.bin", os.urandom(1100 * 1024))])
        self.assertIn("larger than the preview limit", self._render("big2.xlsx", big).error)

    def test_09_xxe_main_part_is_only_data(self):
        # The server never parses the XML; the file is accepted and the library (browser side) decides.
        xxe = (b'<?xml version="1.0"?><!DOCTYPE d [<!ENTITY x SYSTEM "file:///etc/passwd">]>'
               b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">&x;</w:document>')
        rec = self._render("xxe.docx", _zip([("word/document.xml", xxe)]))
        self.assertFalse(rec.error)
        self.assertNotIn("root:", __import__("base64").b64decode(rec.data).decode())

    def test_11_legacy_files_are_accepted(self):
        for name in ("legacy_sample.doc", "legacy_sample.xls", "legacy_sample.ppt", "legacy_rejected.doc"):
            rec = self._render(name, _fixture(name))  # the server only checks the container: the browser decides
            self.assertFalse(rec.error, name)
            self.assertEqual(rec.result_type, "text")
            self.assertEqual(__import__("base64").b64decode(rec.data).decode(), name.rsplit(".", 1)[1])

    def test_12_legacy_files_that_are_not_ole_are_refused(self):
        ole = _fixture("legacy_sample.xls")
        cases = {
            "text.xls": b"plain text, not an OLE file\n" * 40,
            "html.xls": b"<html><table><tr><td>1</td></tr></table></html>" * 20,  # a web page saved as .xls
            "zip.doc": _fixture("sample.docx"),  # a real docx named .doc: not a binary file
            "csv.ppt": b"a,b,c\n1,2,3\n",
            "short.doc": ole[:8],  # signature only
            "tiny.xls": ole[:100],
            "badsig.ppt": b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe0" + ole[8:],
        }
        for name, raw in cases.items():
            rec = self._render(name, raw)
            self.assertTrue(rec.error, name)
            self.assertFalse(rec.data, name)
            self.assertIn("not a valid", rec.error, name)
            self.assertNotIn("Traceback", rec.error)

    def test_13_legacy_empty_file(self):
        for name in ("empty.doc", "empty.xls", "empty.ppt"):
            rec = self._render(name, b"")
            self.assertEqual(rec.error, "The file is empty.", name)

    def test_14_legacy_size_limit(self):
        _set_limits(self.env, "0")
        for name in ("legacy_sample.doc", "legacy_sample.xls", "legacy_sample.ppt"):
            rec = self._render(name, _fixture(name))
            self.assertIn("larger than the preview limit", rec.error, name)
        _set_limits(self.env, False)
        _set_limits(self.env, "1")  # 1 MB for each group of Office files
        big = _fixture("legacy_sample.xls") + b"\0" * (1100 * 1024)
        self.assertIn("larger than the preview limit", self._render("big.xls", big).error)

    def test_15_the_zip_check_still_applies_to_the_new_formats_only_by_name(self):
        # an OLE file named .xlsx is still refused (old container, not a zip); a real xlsx named .xls is not OLE
        self.assertTrue(self._render("ole.xlsx", _fixture("legacy_sample.xls")).error)
        self.assertTrue(self._render("real.xls", _fixture("sample.xlsx")).error)

    def test_16_notice_only_for_legacy_extensions(self):
        for ext in ("doc", "xls", "ppt"):
            notice = self.engine._dwo_engine_notice(ext)
            self.assertIn("Legacy format", notice)
            self.assertIn("Download", notice)
        for ext in ("xlsx", "docx", "pptx", ""):
            self.assertFalse(self.engine._dwo_engine_notice(ext), ext)

    def test_17_direct_render_legacy(self):
        self.assertEqual(self.Model._dwo_render(_fixture("legacy_sample.ppt"), "A.PPT"), {"type": "text", "data": "ppt"})
        with self.assertRaises(UserError):
            self.Model._dwo_render(b"nope", "a.doc")
        with self.assertRaises(UserError):
            self.Model._dwo_render(b"", "a.xls")

    def test_19_csv_tsv_accepted_as_text(self):
        for name in ("sample.csv", "sample_semicolon.csv", "sample.tsv"):
            rec = self._render(name, _fixture(name))
            self.assertFalse(rec.error, name)
            self.assertEqual(__import__("base64").b64decode(rec.data).decode(), name.rsplit(".", 1)[1])
            self.assertFalse(self.engine._dwo_engine_notice(name.rsplit(".", 1)[1]))
        self.assertFalse(self._render("one.csv", b"a").error)
        self.assertFalse(self._render("latin.csv", "caf\xe9;1".encode("latin-1")).error)  # not UTF-8: the viewer decides

    def test_20_csv_tsv_refused_when_empty_or_binary(self):
        cases = {
            "empty.csv": b"",
            "bin.csv": b"a,b\0c\n",
            "utf16.csv": "a,b\n1,2\n".encode("utf-16"),
            "xls.tsv": _fixture("legacy_sample.xls"),
            "png.csv": b"\x89PNG\r\n\x1a\n\0\0\0\rIHDR",
        }
        for name, raw in cases.items():
            rec = self._render(name, raw)
            self.assertTrue(rec.error, name)
            self.assertFalse(rec.data, name)
            self.assertNotIn("Traceback", rec.error)
        self.assertEqual(self._render("empty.tsv", b"").error, "The file is empty.")

    def test_21_csv_size_limit(self):
        _set_limits(self.env, "0")
        self.assertIn("larger than the preview limit", self._render("a.csv", _fixture("sample.csv")).error)

    def test_22_ooxml_variants_are_checked_as_their_base_type(self):
        # xlsm/xltx/... : same zip check and main part as xlsx/docx/pptx; the viewer gets the base type
        for ext, (base, _ct) in VARIANT_TYPES.items():
            rec = self._render("file.%s" % ext.upper(), _variant(ext))
            self.assertFalse(rec.error, ext)
            self.assertEqual(__import__("base64").b64decode(rec.data).decode(), base, ext)
        # the main part of another type, a damaged zip, an empty file: refused with the extension in the message
        for ext, raw, needle in (
            ("xlsm", _fixture("sample.docx"), "main part is missing"),
            ("potx", _fixture("sample.xlsx"), "main part is missing"),
            ("dotm", _variant("dotm")[:200], "damaged"),
            ("ppsx", b"", "empty"),
            ("xltx", b"<html>not a workbook</html>", "XLTX"),
        ):
            with self.assertRaises(UserError, msg=ext) as cm:
                self.engine._dwo_render(raw, "x." + ext)
            self.assertIn(needle, str(cm.exception), ext)
        # no warning banner (they are not legacy formats)
        for ext in VARIANT_TYPES:
            self.assertFalse(self.engine._dwo_engine_notice(ext), ext)

    def test_23_opendocument_accepted_with_its_family(self):
        # odt/ods/odp and the templates: a zip whose `mimetype` names the family; the viewer gets odt/ods/odp
        for base in ("odt", "ods", "odp"):
            rec = self._render("sample.%s" % base, _fixture("sample.%s" % base))
            self.assertFalse(rec.error, base)
            self.assertEqual(base64.b64decode(rec.data).decode(), base)
        for ext, base in ODF_TEMPLATES.items():
            rec = self._render("template.%s" % ext.upper(), _odf(base, template=True))
            self.assertFalse(rec.error, ext)
            self.assertEqual(base64.b64decode(rec.data).decode(), base, ext)
            # a document saved with the template extension (and the other way round) is still the same family
            self.assertEqual(self.engine._dwo_render(_fixture("sample.%s" % base), "x." + ext)["data"], base)
            self.assertEqual(self.engine._dwo_render(_odf(base, template=True), "x." + base)["data"], base)
        # re-zipped by a general archiver: `mimetype` compressed and not the first part (the add-on reads it too)
        self.assertEqual(self.engine._dwo_render(_odf("ods", stored_first=False), "a.ods")["data"], "ods")
        # the server does not decrypt: an encrypted package passes here and the browser refuses it
        self.assertEqual(self.engine._dwo_render(_odf("odt", encrypted=True), "a.odt")["data"], "odt")
        # no warning banner (not a legacy format)
        for ext in ("odt", "ods", "odp", "ott", "ots", "otp"):
            self.assertFalse(self.engine._dwo_engine_notice(ext), ext)

    def test_24_opendocument_refused_with_the_extension(self):
        cases = (
            ("odt", _fixture("sample.ods"), "another kind of OpenDocument"),  # a spreadsheet named .odt
            ("otp", _fixture("sample.odt"), "another kind of OpenDocument"),
            ("ods", _odf("ods", mimetype="application/vnd.oasis.opendocument.graphics"), "another kind"),
            ("odp", _odf("odp", mimetype="text/plain"), "ODP"),
            ("odt", _fixture("sample.docx"), "mimetype part is missing"),  # a Word file named .odt
            ("ods", _zip([("mimetype", b"x" * 200)]), "mimetype part is missing"),  # too long to be a media type
            ("ods", _odf("ods")[:300], "damaged"),
            ("ott", b"", "empty"),
            ("odt", b"<html>not a document</html>", "ODT"),
            ("ods", _fixture("legacy_sample.xls"), "ODS"),
        )
        for ext, raw, needle in cases:
            with self.assertRaises(UserError, msg=ext) as cm:
                self.engine._dwo_render(raw, "x." + ext)
            self.assertIn(needle, str(cm.exception), ext)
        # through the Core: an error, no data, no traceback
        rec = self._render("fake.odt", _fixture("sample.xlsx"))
        self.assertTrue(rec.error)
        self.assertFalse(rec.data)
        self.assertNotIn("Traceback", rec.error)

    def test_25_opendocument_zip_limits(self):
        raw = _zip([("mimetype", ODF_MIMETYPES["ods"].encode()), ("content.xml", b"\0" * (129 * 1024 * 1024))], level=9)
        self.assertIn("too large once unpacked", self._render("bomb.ods", raw).error)
        raw = _zip([("mimetype", ODF_MIMETYPES["odt"].encode())] + [("f%d" % i, b"") for i in range(20001)])
        self.assertIn("too many parts", self._render("many.odt", raw).error)

    def test_10_direct_render_errors_are_user_errors(self):
        with self.assertRaises(UserError):
            self.Model._dwo_render(b"nope", "a.docx")
        with self.assertRaises(UserError):
            self.Model._dwo_render(b"PK", "a.txt")


class _AssetRouteWithoutTestCookie:
    """Odoo 18: tests only, see check_test_cursor (used by every class that runs office tours).
    Odoo 17: HttpCase has no check_test_cursor (the test cookie check does not exist), so this is never called."""

    def check_test_cursor(self, operation):
        """Odoo 18 test mode only: after a browser tour starts, every request must carry the test cookie, else it is
        refused (400). The viewer runs in a sandboxed iframe with an opaque origin, so the browser sends no cookie
        with its requests to the public asset route (the same happens in production, where it needs none). Let
        those through; everything else keeps the strict check. Odoo 19 does not refuse them."""
        request = http.request
        if request and not isinstance(request, Mock) \
                and request.httprequest.path.startswith("/dwo_attpreview_office/asset/") \
                and odoo.modules.module.current_test == self:
            return
        return super().check_test_cursor(operation)


@tagged("post_install", "-at_install")
class TestOfficeRoutes(_AssetRouteWithoutTestCookie, HttpCase):
    # Odoo 17: Chrome needs "w,h" (the default "1366x768" of 17 is ignored) and URLs are /web#... (no /odoo/...)
    browser_size = "1366,768"

    def _att(self, name, raw, partner=None):
        partner = partner or self.env["res.partner"].create({"name": "Office Partner"})
        att = self.env["ir.attachment"].create({
            "name": name, "raw": raw, "res_model": "res.partner", "res_id": partner.id})
        return partner, att

    def test_01_file_route_permissions(self):
        raw = _fixture("sample.xlsx")
        partner, att = self._att("a.xlsx", raw)
        _p, txt = self._att("a.txt", b"hello", partner)
        # anonymous: not served
        res = self.url_open("/dwo_attpreview_office/file/%d" % att.id, allow_redirects=False)
        self.assertNotEqual(res.status_code, 200)
        # a user who cannot read the attachment
        # Odoo 18: groups_id (19: group_ids)
        self.env["res.users"].create({"name": "Nobody", "login": "nobody_att", "password": "nobody_att",
                                      "groups_id": [(6, 0, [self.env.ref("base.group_user").id])]})
        cron = self.env["ir.cron"].search([], limit=1)  # internal users cannot read cron jobs
        private = self.env["ir.attachment"].create({"name": "p.xlsx", "raw": raw, "res_model": "ir.cron",
                                                    "res_id": cron.id})
        self.authenticate("nobody_att", "nobody_att")
        res = self.url_open("/dwo_attpreview_office/file/%d" % private.id)
        self.assertEqual(res.status_code, 403)
        # the owner of access
        self.authenticate("admin", "admin")
        res = self.url_open("/dwo_attpreview_office/file/%d" % att.id)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content, raw)
        self.assertEqual(res.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(res.headers["Content-Type"], "application/octet-stream")
        # not an office file
        self.assertEqual(self.url_open("/dwo_attpreview_office/file/%d" % txt.id).status_code, 404)
        # missing
        self.assertEqual(self.url_open("/dwo_attpreview_office/file/99999999").status_code, 403)

    def test_02_file_route_refuses_what_core_refuses(self):
        self.authenticate("admin", "admin")
        _p, bad = self._att("bad.docx", b"PK not really")
        self.assertEqual(self.url_open("/dwo_attpreview_office/file/%d" % bad.id).status_code, 422)
        _p, ok = self._att("ok.xlsx", _fixture("sample.xlsx"))
        _set_limits(self.env, "0")
        self.assertEqual(self.url_open("/dwo_attpreview_office/file/%d" % ok.id).status_code, 422)

    def test_02b_file_route_for_legacy_files(self):
        self.authenticate("admin", "admin")
        raw = _fixture("legacy_sample.xls")
        _p, ok = self._att("old.xls", raw)
        res = self.url_open("/dwo_attpreview_office/file/%d" % ok.id)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content, raw)
        _p, bad = self._att("fake.doc", b"<html>not a doc</html>" * 50)
        self.assertEqual(self.url_open("/dwo_attpreview_office/file/%d" % bad.id).status_code, 422)

    def test_02d_info_without_notice_for_text(self):
        self.authenticate("admin", "admin")
        for name, raw, content in (("a.csv", _fixture("sample.csv"), "csv"), ("a.tsv", _fixture("sample.tsv"), "tsv")):
            _p, att = self._att(name, raw)
            res = self.make_jsonrpc_request("/dwo_attpreview/info", {"attachment_id": att.id})
            self.assertEqual((res["mode"], res["engine"], res["content"]), ("rendered", "office", content), name)
            self.assertFalse(res["notice"], name)

    def test_02e_info_without_notice_for_opendocument(self):
        self.authenticate("admin", "admin")
        for name, raw, content in (("a.odt", _fixture("sample.odt"), "odt"), ("a.ods", _fixture("sample.ods"), "ods"),
                                   ("a.odp", _fixture("sample.odp"), "odp"), ("a.ott", _odf("odt", True), "odt"),
                                   ("a.ots", _odf("ods", True), "ods"), ("a.otp", _odf("odp", True), "odp")):
            _p, att = self._att(name, raw)
            res = self.make_jsonrpc_request("/dwo_attpreview/info", {"attachment_id": att.id})
            self.assertEqual((res["mode"], res["engine"], res["content"]), ("rendered", "office", content), name)
            self.assertFalse(res["notice"], name)
            self.assertEqual(res.get("width"), "wide", name)
            res = self.url_open("/dwo_attpreview_office/file/%d" % att.id)
            self.assertEqual((res.status_code, res.content), (200, raw), name)

    def test_02c_info_carries_the_notice(self):
        self.authenticate("admin", "admin")

        def info(name, raw):
            _p, att = self._att(name, raw)
            return self.make_jsonrpc_request("/dwo_attpreview/info", {"attachment_id": att.id})

        for name in ("legacy_sample.doc", "legacy_sample.xls", "legacy_sample.ppt"):
            res = info(name, _fixture(name))
            self.assertEqual(res["mode"], "rendered", name)
            self.assertEqual(res["engine"], "office")
            self.assertEqual(res["content"], name.rsplit(".", 1)[1])
            self.assertIn("Legacy format", res["notice"])
        res = info("fake.xls", b"<html></html>" * 50)  # refused by the Core: no dialog, the reason only
        self.assertEqual(res["mode"], "error")
        self.assertIn("not a valid", res["error"])
        for name in ("sample.xlsx", "sample.docx", "sample.pptx"):
            res = info(name, _fixture(name))
            self.assertEqual(res["mode"], "rendered")
            self.assertFalse(res["notice"], name)

    def test_03_asset_route_mime_cors_and_whitelist(self):
        base = "/dwo_attpreview_office/asset/"
        wasm = self.url_open(base + "lib/silurus/xlsx_parser_bg.wasm")
        self.assertEqual(wasm.status_code, 200)
        self.assertEqual(wasm.headers["Content-Type"], "application/wasm")
        self.assertEqual(wasm.headers["Access-Control-Allow-Origin"], "*")
        self.assertEqual(wasm.content[:4], b"\0asm")
        mjs = self.url_open(base + "lib/silurus/docx.mjs")
        self.assertEqual(mjs.status_code, 200)
        self.assertIn("javascript", mjs.headers["Content-Type"])
        # the legacy add-on: modules, wasm, shared chunk and the companion runtime next to them
        # and the OpenDocument add-on (#84): same companion runtime
        for name in ("doc.mjs", "xls.mjs", "ppt.mjs", "internal-companion.mjs", "legacy-source-CFRuXN53.js",
                     "legacy-doc-source-module.mjs", "legacy-xls-source-module.mjs", "legacy-ppt-source-module.mjs",
                     "odt.mjs", "ods.mjs", "odp.mjs", "odf-source-CcsC38G5.js", "odt-source-module.mjs",
                     "ods-source-module.mjs", "odp-source-module.mjs"):
            res = self.url_open(base + "lib/silurus/" + name)
            self.assertEqual(res.status_code, 200, name)
            self.assertNotIn("@silurus/", res.text.replace("@silurus/ooxml ", ""), name)  # no bare import
        for name in ("legacy_doc_direct_bg.wasm", "legacy_xls_direct_bg.wasm", "legacy_ppt_direct_bg.wasm",
                     "opendocument_odt_bg.wasm", "opendocument_ods_bg.wasm", "opendocument_odp_bg.wasm"):
            res = self.url_open(base + "lib/silurus/" + name)
            self.assertEqual(res.headers["Content-Type"], "application/wasm", name)
            self.assertEqual(res.content[:4], b"\0asm")
        # not served: licence and notices of the add-on
        self.assertEqual(self.url_open(base + "lib/silurus/LICENSE.ooxml-legacy-office").status_code, 404)
        self.assertEqual(self.url_open(base + "lib/silurus/LICENSE.ooxml-opendocument").status_code, 404)
        html = self.url_open(base + "viewer/viewer.html")
        self.assertEqual(html.status_code, 200)
        csp = html.headers["Content-Security-Policy"]
        self.assertIn("sandbox allow-scripts", csp)
        self.assertIn("default-src 'none'", csp)
        self.assertNotIn("http://", csp.replace("http://127.0.0.1", "").replace("http://localhost", ""))
        for bad in ("../__manifest__.py", "viewer/../../__manifest__.py", "models/engine.py",
                    "lib/silurus/../../../__manifest__.py", "lib/silurus/nothing.js", "viewer/x.py", "tests/files/sample.xlsx"):
            self.assertEqual(self.url_open(base + bad).status_code, 404, bad)

    def test_03b_viewer_uses_scroll_viewer_for_docx_and_slides_for_pptx(self):
        with open(file_path("%s/static/viewer/viewer.js" % MODULE)) as f:
            js = f.read()
        self.assertIn("DocxScrollViewer", js)
        self.assertIn("PptxViewer", js)
        self.assertNotIn("DocxViewer", js.replace("DocxScrollViewer", ""))
        self.assertNotIn("PptxScrollViewer", js)
        with open(file_path("%s/static/lib/silurus/docx.mjs" % MODULE)) as f:
            self.assertIn("DocxScrollViewer", f.read())

    def test_03c_viewer_passes_the_legacy_options(self):
        with open(file_path("%s/static/viewer/viewer.js" % MODULE)) as f:
            js = f.read()
        for needle in ("legacyDoc", "legacyXls", "legacyPpt", "maxInputBytes", "doc.mjs", "xls.mjs", "ppt.mjs",
                       "createOdt", "createOds", "createOdp", "odt.mjs", "ods.mjs", "odp.mjs"):
            self.assertIn(needle, js)
        # silurus 0.90: any value of the deprecated useGoogleFonts logs a warning; no `fonts` source = no web font
        self.assertNotIn("useGoogleFonts", js)
        self.assertNotIn("googleFonts", js)

    def test_03d_find_bar_in_the_viewer(self):
        # search bar and magnifier button; the library search API, not the browser's find (the page is canvas)
        with open(file_path("%s/static/viewer/viewer.html" % MODULE)) as f:
            html = f.read()
        for needle in ('id="find-open"', 'id="find-input"', 'id="find-count"', 'id="find-prev"', 'id="find-next"',
                       'id="find-close"'):
            self.assertIn(needle, html)
        with open(file_path("%s/static/viewer/viewer.js" % MODULE)) as f:
            js = f.read()
        for needle in ("findText", "findNext", "findPrev", "clearFind", "caseSensitive: false", "matchIndex"):
            self.assertIn(needle, js)

    def test_04_no_remote_reference_in_bundled_viewer(self):
        # the viewer page and its host script must not name any external host
        for rel in ("static/viewer/viewer.html", "static/viewer/viewer.js", "static/viewer/viewer.css",
                    "static/src/js/office_viewer.js"):
            with open(file_path("%s/%s" % (MODULE, rel))) as f:
                text = f.read()
            self.assertNotRegex(text, r"https?://(?!www\.w3\.org)", rel)

    def _tour(self, kind, name, raw):
        partner, att = self._att(name, raw)
        partner.message_post(body="file", attachment_ids=[att.id])
        # the sandboxed iframe (opaque origin) loads its scripts without cookies: in test mode Odoo ignores such
        # requests unless all requests are allowed
        self.http_request_allow_all = True
        self.start_tour("/web#id=%d&model=res.partner&view_type=form" % partner.id, "dwo_attpreview_office_tour_" + kind, login="admin")

    def test_10_tour_xlsx(self):
        self._tour("xlsx", "report.xlsx", _fixture("sample.xlsx"))

    def test_11_tour_docx(self):
        self._tour("docx", "report.docx", _fixture("sample.docx"))

    def test_11b_tour_docx_long_scrolls(self):
        self._tour("docx_long", "long.docx", _fixture("long.docx"))

    def test_12_tour_pptx(self):
        self._tour("pptx", "slides.pptx", _fixture("sample.pptx"))

    def test_30_tour_find_xlsx(self):
        self._tour("find_xlsx", "report.xlsx", _fixture("sample.xlsx"))

    def test_31_tour_find_docx(self):
        self._tour("find_docx", "report.docx", _fixture("sample.docx"))

    def test_32_tour_find_pptx(self):
        self._tour("find_pptx", "slides.pptx", _fixture("sample.pptx"))

    def test_33_tour_find_docx_long(self):
        self._tour("find_docx_long", "long.docx", _fixture("long.docx"))

    def test_34_tour_find_csv(self):
        self._tour("find_csv", "sample.csv", _fixture("sample.csv"))

    def test_35_tour_find_tsv(self):
        self._tour("find_tsv", "sample.tsv", _fixture("sample.tsv"))

    def _tour_variant(self, ext):
        # macro-enabled / template variant (#70): drawn by the viewer of its base type, same tour
        self._tour(VARIANT_TYPES[ext][0], "variant.%s" % ext, _variant(ext))

    def test_40_tour_xlsm(self):
        self._tour_variant("xlsm")

    def test_41_tour_xltx(self):
        self._tour_variant("xltx")

    def test_42_tour_xltm(self):
        self._tour_variant("xltm")

    def test_43_tour_docm(self):
        self._tour_variant("docm")

    def test_44_tour_dotx(self):
        self._tour_variant("dotx")

    def test_45_tour_dotm(self):
        self._tour_variant("dotm")

    def test_46_tour_pptm(self):
        self._tour_variant("pptm")

    def test_47_tour_ppsx(self):
        self._tour_variant("ppsx")

    def test_48_tour_ppsm(self):
        self._tour_variant("ppsm")

    def test_49_tour_potx(self):
        self._tour_variant("potx")

    def test_50_tour_potm(self):
        self._tour_variant("potm")

    def test_51_tour_find_in_xlsm(self):
        # search works the same in a variant (the xlsm viewer is the xlsx one)
        self._tour("find_xlsx", "macros.xlsm", _variant("xlsm"))

    # OpenDocument (#84): drawn by the viewer of its family, no banner, fills the dialog; search works the same
    def test_70_tour_odt(self):
        self._tour("odt", "notes.odt", _fixture("sample.odt"))

    def test_71_tour_ods(self):
        self._tour("ods", "sales.ods", _fixture("sample.ods"))

    def test_72_tour_odp(self):
        self._tour("odp", "deck.odp", _fixture("sample.odp"))

    def test_73_tour_ott(self):
        self._tour("ott", "notes.ott", _odf("odt", template=True))

    def test_74_tour_ots(self):
        self._tour("ots", "sales.ots", _odf("ods", template=True))

    def test_75_tour_otp(self):
        self._tour("otp", "deck.otp", _odf("odp", template=True))

    def test_76_tour_find_odt(self):
        self._tour("find_odt", "notes.odt", _fixture("sample.odt"))

    def test_77_tour_find_ods(self):
        self._tour("find_ods", "sales.ods", _fixture("sample.ods"))

    def test_78_tour_find_odp(self):
        self._tour("find_odp", "deck.odp", _fixture("sample.odp"))

    def test_79_tour_odf_refused_by_the_viewer_shows_download(self):
        self._tour("odf_refused", "locked.odt", _odf("odt", encrypted=True))

    def test_36_tour_find_legacy_xls(self):
        self._tour("find_legacy_xls", "old.xls", _fixture("legacy_sample.xls"))

    def test_37_tour_find_legacy_ppt(self):
        self._tour("find_legacy_ppt", "old.ppt", _fixture("legacy_sample.ppt"))

    def test_38_tour_find_legacy_doc(self):
        self._tour("find_legacy_doc", "old.doc", _fixture("legacy_sample.doc"))

    def test_39_tour_find_xlsx_100k_rows(self):
        # 100000 rows: the search counts every match and reaches the last rows without hanging the page
        import xlsxwriter
        buf = io.BytesIO()
        book = xlsxwriter.Workbook(buf, {"constant_memory": True, "in_memory": True})
        sheet = book.add_worksheet("Data")
        sheet.write_row(0, 0, ["Name", "Label"])
        for i in range(1, 100001):
            sheet.write_row(i, 0, ["Row %d" % i, "Item %d" % i])
        book.close()
        self._tour("find_xlsx_big", "big.xlsx", buf.getvalue())

    def test_20_tour_csv_tsv(self):
        self._tour("csv", "data.csv", _fixture("sample.csv"))

    def test_21_tour_tsv(self):
        self._tour("tsv", "data.tsv", _fixture("sample.tsv"))

    def test_22_tour_csv_semicolon_with_bom(self):
        self._tour("csv_semicolon", "euro.csv", _fixture("sample_semicolon.csv"))

    def test_23_tour_csv_100k_rows(self):
        rows = ["id,name,amount,note,city,date"] + [
            "%d,Khách hàng %d,%d,\"ghi chú, %d\",Hà Nội,2026-01-%02d" % (i, i, i * 7 % 1000, i, i % 28 + 1)
            for i in range(100000)]
        raw = ("\n".join(rows) + "\n").encode()
        self.assertGreater(len(raw), 5 * 1024 * 1024)
        self._tour("csv_big", "big.csv", raw)

    def test_24_tour_csv_over_the_limits_gives_short_message(self):
        rows = ["a,b,c,d,e,f,g,h"] + ["1,2,3,4,5,6,7,8"] * 200001  # more rows than the viewer takes
        self._tour("csv_huge", "huge.csv", ("\n".join(rows) + "\n").encode())

    def test_14_tour_legacy_xls(self):
        self._tour("legacy_xls", "old.xls", _fixture("legacy_sample.xls"))

    def test_15_tour_legacy_ppt(self):
        self._tour("legacy_ppt", "old.ppt", _fixture("legacy_sample.ppt"))

    def test_16_tour_legacy_doc(self):
        self._tour("legacy_doc", "old.doc", _fixture("legacy_sample.doc"))

    def test_17_tour_legacy_file_the_viewer_refuses_shows_download(self):
        self._tour("legacy_refused", "merged.doc", _fixture("legacy_rejected.doc"))

    def test_18_tour_legacy_not_ole_gives_toast(self):
        self._tour("legacy_toast", "fake.xls", b"<html><body>not a spreadsheet</body></html>" * 30)

    def test_13_tour_damaged_file_shows_toast_with_download(self):
        good = _fixture("sample.docx")
        self._tour("error", "broken.docx", good[: len(good) // 2])


@tagged("post_install", "-at_install")
class TestOfficeFieldPreview(_AssetRouteWithoutTestCookie, HttpCase):
    # Odoo 17: Chrome needs "w,h" (the default "1366x768" of 17 is ignored) and URLs are /web#... (no /odoo/...)
    browser_size = "1366,768"

    """An Office file held by a binary field of a record (not an ir.attachment record): the Core chooses the engine by
    the file name of the field and gives the viewer ``fileUrl`` (/web/content of the field, access checked again)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        partner_model = env["ir.model"]._get("res.partner")
        # fields made for the test only (rolled back with the test, like a field added by a user)
        env["ir.model.fields"].create([
            {"name": "x_dwo_office_file", "ttype": "binary", "field_description": "Office file",
             "model_id": partner_model.id},
            {"name": "x_dwo_office_file_name", "ttype": "char", "field_description": "Office file name",
             "model_id": partner_model.id},
        ])
        env["ir.ui.view"].create({
            "name": "dwo_attpreview_office test field",
            "model": "res.partner",
            "inherit_id": env.ref("base.view_partner_form").id,
            "arch": """
                <xpath expr="//sheet" position="inside">
                    <group name="dwo_office_file" string="Office file">
                        <field name="x_dwo_office_file_name" invisible="1"/>
                        <field name="x_dwo_office_file" filename="x_dwo_office_file_name"/>
                    </group>
                </xpath>""",
        })

    def _partner(self, name, raw):
        return self.env["res.partner"].create({
            "name": "Field Office Partner",
            "x_dwo_office_file": base64.b64encode(raw),
            "x_dwo_office_file_name": name,
        })

    def _field_info(self, model, res_id, field, filename_field):
        return self.make_jsonrpc_request("/dwo_attpreview/field_info", {
            "model": model, "res_id": res_id, "field": field, "filename_field": filename_field})

    @staticmethod
    def _counts(env):
        # every attachment (fields too) except the stored results of the render cache
        # Odoo 17: the web client makes the asset bundle of the bus worker (an attachment under /web/assets/) on the
        # first page of each test: it is not a preview attachment
        every = ["|", ("res_field", "=", False), ("res_field", "!=", False),
                 ("res_model", "!=", "dwo.attpreview.cache"), ("url", "not like", "/web/assets/")]
        return (env["ir.attachment"].sudo().search_count(every),
                env["dwo.attpreview.cache"].sudo().search_count([]))

    def test_60_field_stored_as_attachment_gives_file_url(self):
        self.authenticate("admin", "admin")
        for name, fixture, kind in (("contract.docx", "sample.docx", "docx"),
                                    ("budget.xlsx", "sample.xlsx", "xlsx"),
                                    ("macros.xlsm", None, "xlsx")):
            raw = _fixture(fixture) if fixture else _variant("xlsm")
            partner = self._partner(name, raw)
            n_att = self._counts(self.env)[0]
            out = self._field_info("res.partner", partner.id, "x_dwo_office_file", "x_dwo_office_file_name")
            self.assertEqual((out["mode"], out["engine"], out["content"], out["name"]),
                             ("rendered", "office", kind, name))
            self.assertNotIn("attachment_id", out)
            self.assertTrue(out["file_url"].startswith("/web/content?model=res.partner&id=%d" % partner.id))
            res = self.url_open(out["file_url"])
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content, raw)
            # the result is cached on the field's own attachment: no other attachment is made
            self.assertEqual(self._counts(self.env)[0], n_att)

    def test_61_field_stored_in_table_creates_nothing(self):
        # ir.mail_server.smtp_ssl_certificate is attachment=False; its name is used as the file name
        raw = _fixture("sample.xlsx")
        server = self.env["ir.mail_server"].create({
            "name": "table.xlsx", "smtp_host": "localhost", "smtp_authentication": "certificate",
            "smtp_encryption": "ssl", "smtp_ssl_certificate": base64.b64encode(raw),
            "smtp_ssl_private_key": base64.b64encode(b"key"),
        })
        self.authenticate("admin", "admin")
        before = self._counts(self.env)
        out = self._field_info("ir.mail_server", server.id, "smtp_ssl_certificate", "name")
        self.assertEqual((out["mode"], out["engine"], out["content"]), ("rendered", "office", "xlsx"))
        res = self.url_open(out["file_url"])
        self.assertEqual((res.status_code, res.content), (200, raw))
        self.assertEqual(self._counts(self.env), before)

    def test_62_field_checks_access_size_and_content(self):
        partner = self._partner("broken.docx", _fixture("sample.docx")[:2000])
        self.authenticate("admin", "admin")
        out = self._field_info("res.partner", partner.id, "x_dwo_office_file", "x_dwo_office_file_name")
        self.assertEqual(out["mode"], "error")  # the Core refuses it before any dialog (toast)
        partner.x_dwo_office_file = base64.b64encode(_fixture("sample.docx"))
        _set_limits(self.env, "0")
        out = self._field_info("res.partner", partner.id, "x_dwo_office_file", "x_dwo_office_file_name")
        self.assertEqual(out["mode"], "error")
        _set_limits(self.env, False)
        # a user who cannot read the record gets nothing, neither the answer nor the file
        server = self.env["ir.mail_server"].create({
            "name": "secret.xlsx", "smtp_host": "localhost", "smtp_authentication": "certificate",
            "smtp_encryption": "ssl", "smtp_ssl_certificate": base64.b64encode(_fixture("sample.xlsx")),
            "smtp_ssl_private_key": base64.b64encode(b"key"),
        })
        url = self._field_info("ir.mail_server", server.id, "smtp_ssl_certificate", "name")["file_url"]
        # Odoo 18: groups_id (19: group_ids)
        self.env["res.users"].create({"name": "Nobody", "login": "nobody_field", "password": "nobody_field",
                                      "groups_id": [(6, 0, [self.env.ref("base.group_user").id])]})
        self.authenticate("nobody_field", "nobody_field")
        out = self._field_info("ir.mail_server", server.id, "smtp_ssl_certificate", "name")
        self.assertEqual(out["mode"], "denied")
        self.assertNotEqual(self.url_open(url).status_code, 200)

    def test_63_viewer_takes_file_url(self):
        with open(file_path("%s/static/src/js/office_viewer.js" % MODULE)) as f:
            text = f.read()
        self.assertIn("fileUrl: { type: String, optional: true }", text)
        self.assertIn("this.props.fileUrl ||", text)

    def _field_tour(self, kind, name, raw):
        partner = self._partner(name, raw)
        n_att = self._counts(self.env)[0]
        self.http_request_allow_all = True  # see TestOfficeRoutes._tour
        self.start_tour("/web#id=%d&model=res.partner&view_type=form" % partner.id, "dwo_attpreview_office_field_tour_" + kind,
                        login="admin")
        self.assertEqual(self._counts(self.env)[0], n_att)

    def test_64_tour_docx_in_binary_field(self):
        self._field_tour("docx", "contract.docx", _fixture("sample.docx"))

    def test_65_tour_xlsx_in_binary_field(self):
        self._field_tour("xlsx", "budget.xlsx", _fixture("sample.xlsx"))


@tagged("post_install", "-at_install")
class TestViewerCss(TransactionCase):

    def test_01_xlsx_canvas_has_no_margin(self):
        """#76: the stage gives every canvas an 8px margin (docx / pdf pages); the xlsx canvas must not have it, or the
        find boxes (placed in the same box as the canvas) sit 8px above the matching cells."""
        with open(file_path("%s/static/viewer/viewer.css" % MODULE)) as f:
            css = f.read()
        self.assertRegex(css, r"#stage\.xlsx canvas\s*\{[^}]*margin:\s*0")
