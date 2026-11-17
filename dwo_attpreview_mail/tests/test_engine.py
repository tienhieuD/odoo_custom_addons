# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import base64
import json
from types import SimpleNamespace
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import HttpCase, TransactionCase, tagged
from odoo.tools.misc import file_path

from odoo.addons.dwo_attpreview_core.controllers.main import AttPreviewController

MODULE = "dwo_attpreview_mail"
REQUEST = "odoo.addons.dwo_attpreview_core.controllers.main.request"
PNG = base64.b64encode(base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")).decode()

EML = ("""From: Anna Berg <anna@example.com>
To: b@example.com, "Chen, Li" <li@example.com>
Cc: team@example.com
Subject: Hi <b>there</b>
Date: Mon, 1 Jan 2024 10:00:00 +0000
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="B"

--B
Content-Type: multipart/related; boundary="R"

--R
Content-Type: multipart/alternative; boundary="A"

--A
Content-Type: text/plain; charset=utf-8

Hello plain
--A
Content-Type: text/html; charset=utf-8

<p onclick="x()">Hello</p><img src="https://evil.example/track.png"><img src="cid:logo@x">
<div style="background:url(https://evil.example/bg.png)">bg</div><script>alert(1)</script>
<a href="javascript:alert(2)">j</a><a href="https://odoo.com">ok</a>
--A--
--R
Content-Type: image/png
Content-ID: <logo@x>
Content-Disposition: inline
Content-Transfer-Encoding: base64

%s
--R--
--B
Content-Type: application/pdf; name="f.pdf"
Content-Disposition: attachment; filename="f.pdf"
Content-Transfer-Encoding: base64

JVBERi0xLjQK
--B
Content-Type: message/rfc822

From: inner@example.com
Subject: Inner note
Content-Type: multipart/mixed; boundary="I"

--I
Content-Type: text/plain

Inner body
--I
Content-Type: text/plain; name="deep.txt"
Content-Disposition: attachment; filename="deep.txt"

deep text
--I--
--B--
""" % PNG).encode()


def sample(name):
    with open(file_path("%s/tests/files/%s" % (MODULE, name)), "rb") as f:
        return f.read()


@tagged("post_install", "-at_install")
class TestMailEngine(TransactionCase):

    def setUp(self):
        super().setUp()
        self.engine = self.env["dwo.attpreview.engine.mail"]

    def render(self, content, name):
        out = self.engine._dwo_render(content, name)
        self.assertEqual(out["type"], "json")
        json.dumps(out["data"], ensure_ascii=False).encode()  # must be storable
        return out["data"]

    # --- EML ------------------------------------------------------------------
    def test_01_eml_headers_and_attachments(self):
        d = self.render(EML, "a.eml")
        self.assertEqual(d["kind"], "email")
        self.assertEqual(d["subject"], "Hi <b>there</b>", "plain text: the viewer escapes it")
        self.assertEqual(d["from"], "Anna Berg <anna@example.com>")
        self.assertIn("Chen, Li", d["to"])
        self.assertEqual(d["cc"], "team@example.com")
        self.assertEqual(d["date"], "2024-01-01T10:00:00+00:00")
        names = [(a["index"], a["name"], a["mimetype"]) for a in d["attachments"]]
        self.assertEqual(names, [(1, "f.pdf", "application/pdf"), (2, "Inner note.eml", "message/rfc822")],
                         "the picture shown in the body is not listed")

    def test_02_eml_body_is_safe(self):
        d = self.render(EML, "a.eml")
        body = d["body_html"]
        self.assertIn("Hello", body)
        self.assertIn("data:image/png;base64,", body, "the cid: picture is inlined")
        for bad in ("<script", "onclick", "javascript:", "evil.example"):
            self.assertNotIn(bad, body)
        self.assertIn('href="https://odoo.com"', body)
        self.assertTrue(d["remote_blocked"])
        self.assertEqual(d["body_text"], "", "html wins over the plain alternative")

    def test_02b_backgrounds_kept_and_blocked_pictures_dropped(self):
        html = ('<table><tr style="background:#1f5a96;color:#fff"><th>Role</th></tr>'
                '<tr bgcolor="#eeeeee"><td style="background: url(https://x.example/y.png) no-repeat #ff0000">a</td></tr>'
                '</table><img src="https://x.example/banner.jpg" alt="Banner"><img src="cid:none">')
        raw = ("Subject: s\nContent-Type: text/html; charset=utf-8\n\n" + html).encode()
        d = self.render(raw, "a.eml")
        body = d["body_html"]
        self.assertIn("background-color:#1f5a96", body)
        self.assertIn("background-color:#eeeeee", body)
        self.assertIn("background-color:#ff0000", body)
        self.assertNotIn("x.example", body)
        self.assertEqual(body.count("<img"), 1, "the missing cid: picture is dropped, not shown broken")
        self.assertIn('<img data-dwo-remote="0" hidden', body, "the remote picture waits for the proxy (#79)")
        self.assertEqual((d["remote_images"], d["remote_insecure"]), (1, 0))
        self.assertTrue(d["remote_blocked"])

    def test_02c_pictures_with_a_strange_address_become_visible_errors(self):
        html = ('<p>x</p><img src="javascript:alert(1)" alt="js"><img src="file:///etc/passwd">'
                '<img src="evil.sh" alt="script"><img src="https://x.example/ok.png">')
        raw = ("Subject: s\nContent-Type: text/html; charset=utf-8\n\n" + html).encode()
        body = self.render(raw, "a.eml")["body_html"]
        self.assertEqual(body.count("data-dwo-bad="), 3, "each one is kept as an error marker, not dropped")
        self.assertEqual(body.count('data-dwo-remote="0"'), 1)
        for text in ("javascript:", "file:", "evil.sh", "passwd"):
            self.assertNotIn(text, body, "the strange address itself is never kept")
        self.assertIn('alt="script"', body, "the alt text is kept for the message")

    def test_03_plain_text_email_and_bogus_charset(self):
        raw = b"Subject: s\nContent-Type: text/plain; charset=x-unknown-cs\n\n<b>caf\xc3\xa9</b>\n"
        d = self.render(raw, "a.eml")
        self.assertEqual(d["body_html"], "")
        self.assertIn("<b>café</b>", d["body_text"], "kept as text; the viewer escapes it")
        self.assertFalse(d["remote_blocked"])

    def test_04_malformed_headers_do_not_break(self):
        raw = b'From: "unclosed <a@x\nTo: ,,,@@\nSubject: =?bogus?Q?x?=\nDate: not a date\n\nbody\n'
        d = self.render(raw, "a.eml")
        self.assertEqual(d["date"], "not a date")
        self.assertIn("body", d["body_text"])

    def test_05_garbage_is_a_clean_error(self):
        for content in (b"", b"\x00\x01\x02", b"no headers at all"):
            with self.assertRaises(UserError):
                self.engine._dwo_render(content, "a.eml")

    def test_06_emlx(self):
        inner = b"Subject: Apple\nFrom: x@example.com\n\nHello from Mail.app\n"
        raw = b"%d\n" % len(inner) + inner + b'<?xml version="1.0"?><plist><dict/></plist>'
        d = self.render(raw, "1234.emlx")
        self.assertEqual(d["subject"], "Apple")
        self.assertIn("Hello from Mail.app", d["body_text"])
        self.assertNotIn("plist", d["body_text"])

    def test_07_attachments_are_parts(self):
        name, data = self.engine._dwo_extract_part(EML, "a.eml", 1)
        self.assertEqual((name, data), ("f.pdf", b"%PDF-1.4\n"))
        name, data = self.engine._dwo_extract_part(EML, "a.eml", 2)
        self.assertEqual(name, "Inner note.eml")
        inner = self.render(data, name)
        self.assertEqual(inner["subject"], "Inner note")
        self.assertEqual([a["name"] for a in inner["attachments"]], ["deep.txt"])
        self.assertEqual(self.engine._dwo_extract_part(data, name, 0), ("deep.txt", b"deep text"))
        self.assertIsNone(self.engine._dwo_extract_part(EML, "a.eml", 9))

    # --- MSG ------------------------------------------------------------------
    def test_10_msg_plain(self):
        d = self.render(sample("quick.msg"), "quick.msg")
        self.assertEqual((d["format"], d["subject"]), ("msg", "Test the content transformer"))
        self.assertEqual(d["from"], "Kevin Roast", "an Exchange address is not shown as an email")
        self.assertEqual(d["to"], "Kevin Roast <kevin.roast@alfresco.org>")
        self.assertTrue(d["date"].startswith("2007-06-14T09:42:53"))
        self.assertIn("quick brown fox", d["body_text"])

    def test_11_msg_code_pages(self):
        d = self.render(sample("chinese_traditional.msg"), "c.msg")
        self.assertIn("格式測試", d["subject"], "8 bit subject read with the code page of the language")
        d = self.render(sample("html_body_cp1251.msg"), "h.msg")
        self.assertIn("автоматически", d["body_html"],
                      "binary HTML body read with the internet code page")
        self.assertEqual(d["subject"], "Subject öäü Subject")

    def test_12_msg_attachments_and_embedded_message(self):
        content = sample("attachment_pdf.msg")
        d = self.render(content, "a.msg")
        self.assertEqual([(a["name"], a["mimetype"]) for a in d["attachments"]],
                         [("Test Attachment.eml", "message/rfc822"), ("smbprn.00009008.KdcPjl.pdf", "application/pdf")])
        name, data = self.engine._dwo_extract_part(content, "a.msg", 1)
        self.assertTrue(data.startswith(b"%PDF"))
        name, data = self.engine._dwo_extract_part(content, "a.msg", 0)
        inner = self.render(data, name)
        self.assertEqual((inner["format"], inner["subject"]), ("eml", "Test Attachment"))

    def test_13_msg_inline_pictures(self):
        d = self.render(sample("inline_images.msg"), "i.msg")
        self.assertEqual(d["body_html"].count("data:image/"), 4)
        self.assertEqual(d["attachments"], [], "all four pictures are shown in the body")

    def test_14_damaged_msg_and_renamed_files(self):
        try:
            self.render(sample("fuzz_damaged.msg"), "f.msg")
        except UserError:
            pass
        with self.assertRaises(UserError):
            self.engine._dwo_render(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 600, "x.msg")
        # a MIME email saved as .msg, an Outlook message saved as .eml
        self.assertEqual(self.render(EML, "renamed.msg")["format"], "eml")
        self.assertEqual(self.render(sample("quick.msg"), "renamed.eml")["format"], "msg")

    # --- ICS / VCF ---------------------------------------------------------------
    def test_20_ics(self):
        ics = (b"BEGIN:VCALENDAR\r\nMETHOD:REQUEST\r\nBEGIN:VTIMEZONE\r\nTZID:Asia/Tokyo\r\nEND:VTIMEZONE\r\n"
               b"BEGIN:VEVENT\r\nSUMMARY:Quarterly <b>\r\n review\r\nDTSTART;TZID=Asia/Tokyo:20261120T090000\r\n"
               b"DTEND;TZID=Asia/Tokyo:20261120T103000\r\nLOCATION:Room 4\\, Tokyo\r\n"
               b"ORGANIZER;CN=Anna Berg:mailto:anna@example.com\r\n"
               b"ATTENDEE;CN=Li Chen;PARTSTAT=ACCEPTED:mailto:li@example.com\r\n"
               b"DESCRIPTION:Line 1\\nLine 2\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n")
        d = self.render(ics, "invite.ics")
        self.assertEqual((d["kind"], d["method"]), ("calendar", "REQUEST"))
        event = d["events"][0]
        self.assertEqual(event["summary"], "Quarterly <b>review")
        self.assertEqual(event["start"], "2026-11-20 09:00 (Asia/Tokyo)")
        self.assertEqual(event["location"], "Room 4, Tokyo")
        self.assertEqual(event["organizer"], "Anna Berg <anna@example.com>")
        self.assertEqual(event["attendees"], [{"name": "Li Chen <li@example.com>", "status": "ACCEPTED"}])
        self.assertEqual(event["description"], "Line 1\nLine 2")

    def test_21_vcf(self):
        vcf = (b"BEGIN:VCARD\r\nVERSION:2.1\r\nN:Berg;Anna\r\nORG:Northwind;Sales\r\nTITLE:Manager\r\n"
               b"TEL;CELL:+81 90 1234\r\nEMAIL;INTERNET;WORK:anna@example.com\r\n"
               b"NOTE;ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8:Caf=C3=A9 =\r\nlover\r\nEND:VCARD\r\n"
               b"BEGIN:VCARD\r\nVERSION:3.0\r\nFN:Li Chen\r\nADR;TYPE=home:;;1 Main St;Osaka;;530;Japan\r\nEND:VCARD\r\n")
        d = self.render(vcf, "people.vcf")
        first, second = d["contacts"]
        self.assertEqual((first["name"], first["organization"], first["title"]), ("Anna Berg", "Northwind, Sales", "Manager"))
        self.assertEqual(first["phones"], [{"value": "+81 90 1234", "type": "cell"}])
        self.assertEqual(first["emails"], [{"value": "anna@example.com", "type": "work"}])
        self.assertEqual(first["note"], "Café lover")
        self.assertEqual(second["addresses"], [{"value": "1 Main St, Osaka, 530, Japan", "type": "home"}])
        self.assertIsNone(self.engine._dwo_extract_part(vcf, "people.vcf", 0))

    # --- through the Core -----------------------------------------------------------
    def test_30_core_cache_keeps_json_and_no_script(self):
        att = self.env["ir.attachment"].create({"name": "a.eml", "raw": EML})
        engine = self.env["dwo.attpreview.engine"]._dwo_find_engine("a.eml")
        self.assertEqual(engine._name, "dwo.attpreview.engine.mail")
        rec = self.env["dwo.attpreview.cache"]._get_or_render(att, engine)
        self.assertFalse(rec.error)
        self.assertEqual(rec.result_type, "json")
        data = bytes(rec.data)  # Odoo 20: binary fields read as raw bytes
        self.assertNotIn(b"<script", data)
        self.assertNotIn(b"evil.example", data)
        for ext in ("eml", "emlx", "msg", "oft", "ics", "vcf"):
            self.assertEqual(self.env["dwo.attpreview.engine"]._dwo_find_engine("x." + ext)._name, engine._name)

    def test_31_part_info_of_an_attachment_of_an_email(self):
        partner = self.env["res.partner"].create({"name": "Mail owner"})
        att = self.env["ir.attachment"].create({"name": "a.eml", "raw": EML, "res_model": "res.partner",
                                                "res_id": partner.id})
        ctrl = AttPreviewController()
        with patch(REQUEST, new=SimpleNamespace(env=self.env)):
            info = ctrl.info(att.id)
            self.assertEqual((info["mode"], info["engine"]), ("rendered", "mail"))
            pdf = ctrl.part_info(info["source_ref"], "1")
            self.assertEqual((pdf["mode"], pdf["name"]), ("native", "f.pdf"))
            inner = ctrl.part_info(info["source_ref"], "2")
            self.assertEqual((inner["mode"], inner["engine"]), ("rendered", "mail"))
            self.assertEqual(json.loads(inner["content"])["subject"], "Inner note")
            deep = ctrl.part_info(inner["source_ref"], "2/0")
            self.assertEqual((deep["name"], deep["source_ref"]["path"]), ("deep.txt", "2/0"))

    def test_32_attachments_many_levels_deep(self):
        """An email in an email in an email... (6 levels, a PDF at the bottom): each level opens through /part_info."""
        from email.message import EmailMessage
        inner = EmailMessage()
        inner["Subject"] = "Level 6"
        inner.set_content("bottom")
        inner.add_attachment(b"%PDF-1.4\n", maintype="application", subtype="pdf", filename="contract.pdf")
        for level in range(5, 0, -1):
            outer = EmailMessage()
            outer["Subject"] = "Level %d" % level
            outer.set_content("level %d" % level)
            outer.add_attachment(inner)
            inner = outer
        att = self.env["ir.attachment"].create({"name": "deep.eml", "raw": inner.as_bytes()})
        ctrl = AttPreviewController()
        with patch(REQUEST, new=SimpleNamespace(env=self.env)):
            ref = ctrl.info(att.id)["source_ref"]
            for depth in range(1, 6):
                out = ctrl.part_info(ref, "/".join(["0"] * depth))
                self.assertEqual(json.loads(out["content"])["subject"], "Level %d" % (depth + 1))
            pdf = ctrl.part_info(ref, "/".join(["0"] * 6))
            self.assertEqual((pdf["mode"], pdf["name"]), ("native", "contract.pdf"))


@tagged("post_install", "-at_install")
class TestMailTour(HttpCase):

    def test_01_email_and_its_attachment(self):
        partner = self.env["res.partner"].create({"name": "Mail tour"})
        att = self.env["ir.attachment"].create({"name": "Quarterly review.eml", "raw": EML,
                                                "res_model": "res.partner", "res_id": partner.id})
        partner.message_post(body="email", attachment_ids=[att.id])
        from odoo.addons.dwo_attpreview_mail.parsers import remote
        remote.CACHE.clear()
        fetched = []

        def fake(url, https_only=True):  # no network in tests: the remote picture of EML is answered here
            fetched.append(url)
            return base64.b64decode(PNG), "image/png"

        with patch("odoo.addons.dwo_attpreview_mail.parsers.remote.fetch_picture", fake):
            self.start_tour("/odoo/res.partner/%d" % partner.id, "dwo_attpreview_mail_tour", login="admin")
        self.assertEqual(fetched, ["https://evil.example/track.png"], "loaded by the server, once")
