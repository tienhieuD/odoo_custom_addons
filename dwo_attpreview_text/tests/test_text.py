# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import json
import random
from types import SimpleNamespace
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import HttpCase, TransactionCase, tagged
from odoo.addons.dwo_attpreview_core.controllers.main import AttPreviewController

from .. import text_tools

REQUEST = "odoo.addons.dwo_attpreview_core.controllers.main.request"
PNG = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x04\x00\x00\x00\xb5\x1c\x0c\x02"
       b"\x00\x00\x00\x0bIDATx\xdacd`\x00\x00\x00\x06\x00\x020\x81\xd0/\x00\x00\x00\x00IEND\xaeB`\x82")


@tagged("post_install", "-at_install")
class TestTextEngine(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Engines = cls.env["dwo.attpreview.engine"]
        cls.engine = cls.env["dwo.attpreview.engine.text"]

    def render(self, content, filename):
        out = self.engine._dwo_render(content, filename)
        self.assertEqual(out["type"], "json")
        json.dumps(out["data"], ensure_ascii=False).encode()  # what the cache stores must be valid UTF-8 JSON
        return out["data"]

    # --- kinds of files ---------------------------------------------------------------------------------------
    def test_01_extensions(self):
        for name in ("a.md", "A.MARKDOWN", "a.html", "a.xml", "a.svg", "a.json", "a.jsonl", "a.ipynb", "a.yaml",
                     "a.toml", "a.ini", "a.env", "a.properties", "a.py", "a.ts", "a.sql", "a.log", "a.diff",
                     "a.patch", "a.srt", "a.vtt", "a.po", "a.pot", "a.txt", "a.rst"):
            found = self.Engines._dwo_find_engine(name)
            self.assertIsNotNone(found, name)
            if found._dwo_engine_code != "sample":  # the core tests add a sample engine for .txt
                self.assertEqual(found._dwo_engine_code, "text", name)
        self.assertEqual(self.engine._dwo_engine_priority, 200, "a generic reader: specialised engines win")
        self.assertEqual(self.engine._dwo_engine_dialog_width, "wide")
        self.assertNotIn("csv", self.engine._dwo_engine_extensions, "csv belongs to the office engine")
        self.assertEqual(text_tools.file_format("x.Py"), ("py", "code", "python"))
        self.assertEqual(text_tools.file_format("noext"), ("", "text", ""))
        self.assertEqual(text_tools.file_format("a.svg")[1], "xml")

    def test_02_result(self):
        data = self.render(b"line 1\r\nline 2\r\n", "notes.txt")
        self.assertEqual((data["kind"], data["format"], data["encoding"], data["eol"]), ("text", "text", "ASCII", "CRLF"))
        self.assertEqual(data["text"], "line 1\r\nline 2\r\n")
        self.assertFalse(data["truncated"])
        self.assertEqual(self.render(b"x = 1\n", "a.py")["lang"], "python")
        self.assertTrue(self.engine._dwo_engine_notice("mdx"))
        self.assertFalse(self.engine._dwo_engine_notice("md"))

    # --- encodings --------------------------------------------------------------------------------------------
    def test_03_encodings(self):
        text = "Köln, déjà vu, 東京\nline 2"
        cases = [
            (text.encode(), "UTF-8"),
            (b"\xef\xbb\xbf" + text.encode(), "UTF-8 (BOM)"),
            (text.encode("utf-16"), "UTF-16 LE"),  # Python writes a BOM
            (b"\xfe\xff" + text.encode("utf-16-be"), "UTF-16 BE"),
            (text.encode("utf-32"), "UTF-32 LE"),
        ]
        for raw, label in cases:
            data = self.render(raw, "a.txt")
            self.assertEqual((data["text"], data["encoding"]), (text, label), label)
        latin = "Hello, Köln and déjà vu"
        data = self.render(latin.encode("utf-16-le"), "a.txt")
        self.assertEqual((data["text"], data["encoding"]), (latin, "UTF-16 LE (no BOM)"))
        data = self.render(latin.encode("utf-16-be"), "a.txt")
        self.assertEqual((data["text"], data["encoding"]), (latin, "UTF-16 BE (no BOM)"))
        legacy = "Café opening: déjà prêt, à côté de l'entrée. Prix: 12 € par personne."
        data = self.render(legacy.encode("cp1252"), "note.txt")
        self.assertEqual((data["text"], data["encoding"]), (legacy, "Windows-1252"))
        self.assertEqual(self.render(b"", "empty.txt")["text"], "")

    def test_04_binary_is_refused(self):
        for raw in (PNG, b"PK\x03\x04\x14\x00\x00\x00\x08\x00", b"%PDF-1.4\n%\xe2\xe3\n1 0 obj\x00\x00", bytes(range(1, 32)) * 20):
            with self.assertRaisesRegex(UserError, "not text"):
                self.engine._dwo_render(raw, "disguised.txt")
        # through the controller: an error before the dialog opens (toast)
        att = self.env["ir.attachment"].create({"name": "photo.log", "raw": PNG, "mimetype": "text/plain"})
        with patch(REQUEST, new=SimpleNamespace(env=self.env)):
            out = AttPreviewController().info(att.id)
        self.assertEqual(out["mode"], "error")
        self.assertIn("not text", out["error"])

    def test_05_large_file_is_cut(self):
        with patch.object(text_tools, "MAX_TEXT_BYTES", 1001):
            data = self.render(("é" * 800).encode() + b"<a>", "big.xml")  # 1603 bytes, cut inside a character
        self.assertTrue(data["truncated"])
        self.assertEqual(data["text"], "é" * 500)
        self.assertEqual(data["size"], 1603)
        self.assertNotIn("xml", data, "no structure for a cut file")

    # --- HTML -------------------------------------------------------------------------------------------------
    def test_06_html_is_sanitized(self):
        page = b"""<html><head><script>alert(1)</script><style>body{background:url(http://evil.example/x.png)}</style>
        </head><body onload="alert(2)"><h1 style="background:#1f5a96;color:#fff">Hi</h1>
        <img src="https://evil.example/track.gif" width="600" onerror="alert(3)">
        <img src="data:image/png;base64,iVBORw0KGgo=" alt="inline">
        <a href="javascript:alert(4)">bad</a><a href="https://ok.example/">good</a>
        <iframe src="https://evil.example/"></iframe><form action="https://evil.example/"><input name="pw"></form>
        <svg><script>alert(5)</script></svg><object data="x.swf"></object></body></html>"""
        data = self.render(page, "page.html")
        html = data["html"]
        for bad in ("<script", "alert(", "onload", "onerror", "javascript:", "<iframe", "<form", "<object",
                    "evil.example/x.png", 'src="https://evil'):
            self.assertNotIn(bad, html, bad)
        self.assertEqual(data["blocked_images"], 1)
        self.assertEqual(data["remote_urls"], ["https://evil.example/track.gif"], "fetched by the server on request (#87)")
        self.assertIn('<img data-dwo-remote="0" hidden', html, "the address itself is not in the page")
        self.assertIn('src="data:image/png;base64,iVBORw0KGgo="', html, "inline pictures are kept")
        self.assertIn("background-color:#1f5a96", html, "background shorthand kept as a colour")
        self.assertIn('href="https://ok.example/"', html)
        self.assertIn("<script>alert(1)</script>", data["text"], "the raw text is the file as it is (shown escaped)")

    def test_06b_strange_picture_addresses_become_visible_errors(self):
        page = (b'<p>x</p><img src="javascript:alert(1)" alt="js"><img src="file:///etc/passwd">'
                b'<img src="evil.sh" alt="script"><img src="https://a.example/ok.png">')
        data = self.render(page, "page.html")
        html = data["html"]
        self.assertEqual(html.count("data-dwo-bad="), 3)
        self.assertEqual(data["remote_urls"], ["https://a.example/ok.png"])
        for text in ("javascript:", "file:", "evil.sh", "passwd"):
            self.assertNotIn(text, html, text)

    # --- XML --------------------------------------------------------------------------------------------------
    def test_07_xml_tree(self):
        xml = b"""<?xml version="1.0"?>
<odoo xmlns:t="http://example.com/t">
  <!-- a comment -->
  <record id="r1" model="res.partner">
    <field name="name">Northwind</field>
    <t:item>x</t:item>
  </record>
</odoo>"""
        data = self.render(xml, "data.xml")
        nodes = data["xml"]["nodes"]
        self.assertEqual([n[1] for n in nodes], ["odoo", "record", "field", "t:item"])
        self.assertEqual(nodes[1][:2], [0, "record"])
        self.assertEqual(nodes[1][2], [["id", "r1"], ["model", "res.partner"]])
        self.assertEqual((nodes[2][0], nodes[2][3], nodes[2][4]), (1, "Northwind", 5))
        self.assertFalse(data["xml"]["truncated"])
        bad = self.render(b"<a><b></a>", "bad.xml")
        self.assertNotIn("xml", bad)
        self.assertIn("not well formed", bad["structure_error"])

    def test_08_xml_xxe_and_entity_bombs(self):
        xxe = b"""<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r><v>&x;</v></r>"""
        data = self.render(xxe, "x.xml")
        self.assertNotIn("root:", json.dumps(data), "external entities are never read")
        bomb = b"""<?xml version="1.0"?><!DOCTYPE l [<!ENTITY a "aaaaaaaaaa"><!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;">
<!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;"><!ENTITY d "&c;&c;&c;&c;&c;&c;&c;&c;&c;&c;">]><l>&d;&d;&d;</l>"""
        data = self.render(bomb, "bomb.xml")
        self.assertLess(len(json.dumps(data)), 5000, "entities are not expanded")
        svg = b'<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"><script>alert(2)</script><rect/></svg>'
        data = self.render(svg, "pic.svg")
        self.assertEqual([n[1] for n in data["xml"]["nodes"]], ["svg", "script", "rect"])
        self.assertNotIn("html", data, "an SVG is shown as a picture (<img>), never as inline markup")

    def test_09_many_xml_elements(self):
        rows = "".join("<row n='%d'/>" % i for i in range(text_tools.MAX_XML_NODES + 10))
        data = self.render(("<rows>%s</rows>" % rows).encode(), "big.xml")
        self.assertEqual(len(data["xml"]["nodes"]), text_tools.MAX_XML_NODES)
        self.assertTrue(data["xml"]["truncated"])

    # --- notebooks --------------------------------------------------------------------------------------------
    def test_10_notebook(self):
        nb = {"nbformat": 4, "metadata": {"language_info": {"name": "python"}}, "cells": [
            {"cell_type": "markdown", "source": ["# Title\n", "text"]},
            {"cell_type": "code", "execution_count": 3, "source": "print(1)", "outputs": [
                {"output_type": "stream", "name": "stdout", "text": ["1\n"]},
                {"output_type": "display_data", "data": {
                    "text/html": "<b>table</b><script>alert(1)</script><img src=x onerror=alert(2)>",
                    "text/plain": "table"}},
                {"output_type": "display_data", "data": {"application/javascript": "alert(3)"}},
                {"output_type": "display_data", "data": {"image/png": "iVBORw0KGgo=\n", "text/plain": "<Figure>"}},
                {"output_type": "display_data", "data": {"image/svg+xml": "<svg onload='alert(4)'></svg>"}},
                {"output_type": "error", "ename": "KeyError", "evalue": "'x'", "traceback": ["\x1b[0;31mKeyError\x1b[0m: 'x'"]},
            ]},
        ]}
        data = self.render(json.dumps(nb).encode(), "analysis.ipynb")
        cells = data["notebook"]["cells"]
        self.assertEqual(data["notebook"]["language"], "python")
        self.assertEqual([c["type"] for c in cells], ["markdown", "code"])
        self.assertEqual(cells[0]["source"], "# Title\ntext")
        outputs = cells[1]["outputs"]
        self.assertEqual([o["kind"] for o in outputs], ["text", "html", "image", "image", "error"],
                         "JavaScript outputs are left out")
        self.assertNotIn("script", outputs[1]["html"])
        self.assertNotIn("onerror", outputs[1]["html"])
        self.assertEqual(outputs[2]["src"], "data:image/png;base64,iVBORw0KGgo=")
        self.assertTrue(outputs[3]["src"].startswith("data:image/svg+xml;base64,"), "SVG output shown in an <img>")
        self.assertEqual(outputs[4]["text"], "KeyError: 'x'", "colour codes removed")
        self.assertEqual(cells[1]["count"], 3)
        bad = self.render(b"{not json", "broken.ipynb")
        self.assertNotIn("notebook", bad)
        self.assertTrue(bad["structure_error"])
        # escapes of lone surrogates in the JSON: the cached JSON must stay valid UTF-8
        odd = self.render(b'{"cells": [{"cell_type": "code", "source": "\\ud800x", "outputs": []}]}', "odd.ipynb")
        self.assertEqual(odd["notebook"]["cells"][0]["source"], "?x")

    # --- through the controller -------------------------------------------------------------------------------
    def test_11_info(self):
        att = self.env["ir.attachment"].create({"name": "notes.md", "raw": b"# Hello\n", "mimetype": "text/markdown"})
        with patch(REQUEST, new=SimpleNamespace(env=self.env)):
            out = AttPreviewController().info(att.id)
        self.assertEqual((out["mode"], out["type"], out["engine"], out["width"]), ("rendered", "json", "text", "wide"))
        content = json.loads(out["content"])
        self.assertEqual((content["format"], content["text"]), ("markdown", "# Hello\n"))


def make_big_json(items=24_000):
    """About 120 000 values: a list of orders with 4 fields each."""
    rng = random.Random(83)
    return json.dumps({"orders": [{"id": i, "customer": "Customer %d" % i, "amount": round(rng.random() * 1000, 2),
                                   "tags": ["a", "b"] if i % 2 else []} for i in range(items)] + [{"id": "needle-42"}]},
                      indent=1).encode()


def make_big_log(lines=200_000):
    out = []
    for i in range(lines):
        level = "ERROR" if i % 50 == 0 else "WARNING" if i % 10 == 0 else "INFO"
        out.append("10:%02d:%02d %s message %d" % (i // 60 % 60, i % 60, level, i))
    return ("\n".join(out) + "\n").encode()


@tagged("post_install", "-at_install")
class TestTextTour(HttpCase):
    browser_size = "1366,768"  # Odoo 17: Chrome does not read the default "1366x768"

    def _post(self, files):
        partner = self.env["res.partner"].create({"name": "Text tour"})
        atts = self.env["ir.attachment"].create([{"name": name, "raw": raw, "mimetype": mime, "res_model": "res.partner",
                                                  "res_id": partner.id} for name, raw, mime in files])
        partner.message_post(body="files", attachment_ids=atts.ids)
        return partner

    def test_01_markdown_html_svg_safety(self):
        pwn = b"window.top.dwoPwned=1"
        md = (b"# Title\n\n## Part A\n\nSome *text* <script>" + pwn + b"</script> <img src=x onerror='" + pwn + b"'>\n\n"
              b"[js](javascript:alert(2)) [web](https://example.com)\n\n![remote](https://evil.example/p.png)\n\n"
              b"## Part B\n\n```python\ndef f():\n    return 1\n```\n")
        html = (b"<html><body><h1>Page</h1><script>" + pwn + b"</script><img src='https://evil.example/t.gif'>"
                b"<p onclick='" + pwn + b"'>p</p></body></html>")
        svg = (b'<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" onload="' + pwn + b'"><script>' + pwn +
               b'</script><circle cx="20" cy="20" r="10"/></svg>')
        partner = self._post([("README.md", md, "text/markdown"), ("page.html", html, "text/plain"),
                              ("logo.svg", svg, "text/plain")])
        self.start_tour("/web#id=%d&model=res.partner&view_type=form" % partner.id, "dwo_attpreview_text_safety_tour", login="admin")

    def test_02_big_json_tree(self):
        partner = self._post([("orders.json", make_big_json(), "application/json")])
        self.start_tour("/web#id=%d&model=res.partner&view_type=form" % partner.id, "dwo_attpreview_text_json_tour", login="admin")

    def test_03_big_log_and_raw(self):
        log = make_big_log()
        self.assertLess(len(log), text_tools.MAX_TEXT_BYTES, "the whole log is shown (not cut)")
        partner = self._post([("server.log", log, "text/plain")])
        self.start_tour("/web#id=%d&model=res.partner&view_type=form" % partner.id, "dwo_attpreview_text_log_tour", login="admin")

    def test_04_formats(self):
        diff = (b"diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -1,2 +1,2 @@\n x = 1\n-y = 2\n+y = 3\n")
        po = b'msgid ""\nmsgstr ""\n"Language: fr\\n"\n\nmsgid "Hello"\nmsgstr "Bonjour"\n\nmsgid "Bye"\nmsgstr ""\n'
        srt = b"1\n00:00:01,000 --> 00:00:02,000\nHello there\n\n2\n00:00:03,000 --> 00:00:04,500\nBye\n"
        partner = self._post([("fix.patch", diff, "text/x-diff"), ("fr.po", po, "text/plain"),
                              ("talk.srt", srt, "text/plain"), ("conf.yaml", b"server:\n  port: 8069\n  workers: [1, 2]\n", "text/plain"),
                              ("export.txt", "Köln office\t12\n".encode("utf-16"), "text/plain")])
        self.start_tour("/web#id=%d&model=res.partner&view_type=form" % partner.id, "dwo_attpreview_text_formats_tour", login="admin")


def _png(size=(4, 3)):
    import io
    from PIL import Image
    out = io.BytesIO()
    Image.new("RGB", size, (200, 30, 30)).save(out, "PNG")
    return out.getvalue()


@tagged("post_install", "-at_install")
class TestTextRemoteRoute(HttpCase):
    """The picture route of Markdown / HTML / notebooks (#87): only addresses written in the file, clean pictures,
    the reason of a refusal, the settings."""

    MD = (b"# T\n\n![A](https://cdn.example.com/a.png)\n\n![B](https://cdn.example.com/dir/my%20pic.png)\n\n"
          b"![S](https://cdn.example.com/run.sh)\n\n![H](http://plain.example.com/h.png)\n")

    def setUp(self):
        super().setUp()
        from odoo.addons.dwo_attpreview_core import remote_image
        remote_image.CACHE.clear()
        partner = self.env["res.partner"].create({"name": "Text pictures"})
        self.att = self.env["ir.attachment"].create({"name": "doc.md", "raw": self.MD, "res_model": "res.partner",
                                                     "res_id": partner.id})
        self.fetched = []

        def fake(url, https_only=True):
            remote_image.check_url(url, https_only)
            self.fetched.append(url)
            return _png(), "image/png"

        patcher = patch("odoo.addons.dwo_attpreview_core.remote_image.fetch_picture", fake)
        patcher.start()
        self.addCleanup(patcher.stop)

    def url(self, address):
        from urllib.parse import quote
        return "/dwo_attpreview_text/remote_image?attachment_id=%d&url=%s" % (self.att.id, quote(address, safe=""))

    def test_01_settings_are_on_by_default(self):
        self.authenticate("admin", "admin")
        res = self.url_open("/dwo_attpreview_text/remote_settings", data='{"jsonrpc":"2.0","params":{}}',
                            headers={"Content-Type": "application/json"})
        self.assertEqual(res.json()["result"], {"auto": True, "https_only": True})

    def test_02_only_addresses_written_in_the_file(self):
        self.authenticate("admin", "admin")
        res = self.url_open(self.url("https://cdn.example.com/a.png"))
        self.assertEqual((res.status_code, res.headers["Content-Type"]), (200, "image/png"))
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(self.url_open(self.url("https://cdn.example.com/dir/my pic.png")).status_code, 200,
                         "a space in the file and %20 on the way are the same address")
        for other in ("http://169.254.169.254/", "https://evil.example/a.png", "https://cdn.example.com/b.png"):
            self.assertEqual(self.url_open(self.url(other)).status_code, 404, other)
        self.assertEqual(self.url_open("/dwo_attpreview_text/remote_image?attachment_id=%d" % self.att.id).status_code, 404)

    def test_03_refusals_give_a_reason(self):
        self.authenticate("admin", "admin")
        res = self.url_open(self.url("https://cdn.example.com/run.sh"))
        self.assertEqual((res.status_code, res.text), (422, "not a picture"), "a script is refused, with the reason")
        res = self.url_open(self.url("http://plain.example.com/h.png"))
        self.assertEqual((res.status_code, res.text), (422, "scheme not allowed"))
        self.assertEqual(self.fetched, [])

    def test_04_access_of_the_file(self):
        from odoo.tests import new_test_user
        new_test_user(self.env, login="dwo_text_portal", password="dwo_text_portal", groups="base.group_portal")
        self.authenticate("dwo_text_portal", "dwo_text_portal")
        self.assertEqual(self.url_open(self.url("https://cdn.example.com/a.png")).status_code, 404)
        self.assertEqual(self.fetched, [])
