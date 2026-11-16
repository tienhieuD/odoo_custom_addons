# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import base64

from odoo.tests import TransactionCase, tagged

EML = b"""From: A <a@x.com>
To: b@x.com
Subject: Hi <b>there</b>
Date: Mon, 1 Jan 2024 10:00:00 +0000
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="B"

--B
Content-Type: text/html; charset=utf-8

<p>Hello</p><img src="https://evil.example/track.png"><img src="cid:logo"><script>alert(1)</script>
--B
Content-Type: image/png
Content-ID: <logo>
Content-Transfer-Encoding: base64

iVBORw0KGgo=
--B
Content-Type: application/pdf; name="f.pdf"
Content-Disposition: attachment; filename="f.pdf"
Content-Transfer-Encoding: base64

JVBERi0=
--B--
"""


@tagged("post_install", "-at_install")
class TestMail(TransactionCase):

    def setUp(self):
        super().setUp()
        self.engine = self.env["dwo.attpreview.engine.mail"]

    def test_eml_headers_body_attachments(self):
        html = self.engine._dwo_render(EML, "a.eml")["data"]
        self.assertIn("a@x.com", html)
        self.assertIn("Hi &lt;b&gt;there&lt;/b&gt;", html)
        self.assertIn("<p>Hello</p>", html)
        self.assertIn("f.pdf", html)

    def test_remote_blocked_cid_inlined(self):
        html = self.engine._dwo_render(EML, "a.eml")["data"]
        self.assertNotIn("evil.example", html)
        self.assertIn("data:image/png;base64,", html)

    def test_script_removed_after_core_sanitize(self):
        att = self.env["ir.attachment"].create({"name": "a.eml", "raw": EML})
        eng = self.env["dwo.attpreview.engine"]._dwo_find_engine("a.eml")
        rec = self.env["dwo.attpreview.cache"]._get_or_render(att, eng)
        self.assertFalse(rec.error)
        data = base64.b64decode(rec.data)
        self.assertNotIn(b"<script", data)
        self.assertNotIn(b"evil.example", data)

    def test_plain_text_mail(self):
        html = self.engine._dwo_render(b"Subject: s\n\n<b>x</b>\n", "a.eml")["data"]
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", html)

    def test_ics_vcf(self):
        ics = b"BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nSUMMARY:Meet <b>\r\n ing\r\nDTSTART:20240101T100000Z\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n"
        html = self.engine._dwo_render(ics, "a.ics")["data"]
        self.assertIn("SUMMARY", html)
        self.assertIn("Meet &lt;b&gt;ing", html)
        vcf = b"BEGIN:VCARD\nFN:John\nTEL;TYPE=cell:123\nEND:VCARD\n"
        self.assertIn("John", self.engine._dwo_render(vcf, "a.vcf")["data"])

    def test_garbage_does_not_crash(self):
        self.engine._dwo_render(b"\x00\x01\x02", "a.eml")
