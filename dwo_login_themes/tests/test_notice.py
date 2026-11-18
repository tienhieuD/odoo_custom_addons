# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from odoo.tests import TransactionCase, tagged

from odoo.addons.dwo_login_themes.tools import sanitize_notice


@tagged("post_install", "-at_install")
class TestNoticeSanitizer(TransactionCase):
    """The announcement is HTML typed by an administrator but shown to everybody: nothing active may get through."""

    BAD = [
        ("<p>a</p><script>alert(1)</script>", ["<script", "alert(1)"]),
        ('<p onclick="alert(1)">a</p>', ["onclick", "alert"]),
        ('<img src=x onerror="alert(1)">', ["<img", "onerror", "alert"]),
        ('<svg onload="alert(1)"><circle/></svg>', ["<svg", "onload", "alert"]),
        ('<iframe src="https://evil.example"></iframe>', ["<iframe", "evil.example"]),
        ("<style>body{display:none}</style><p>a</p>", ["<style", "display:none"]),
        ('<form action="https://evil.example"><input name="p"></form>', ["<form", "<input", "evil.example"]),
        ('<a href="javascript:alert(1)">x</a>', ["javascript", "alert"]),
        ('<a href=" JaVaScRiPt:alert(1)">x</a>', ["javascript", "alert"]),
        ('<a href="java\tscript:alert(1)">x</a>', ["script:", "alert"]),
        ('<a href="data:text/html;base64,PHNjcmlwdD4=">x</a>', ["data:"]),
        ('<a href="vbscript:msgbox(1)">x</a>', ["vbscript"]),
        ('<a href="//evil.example/x">x</a>', ["evil.example"]),
        ('<object data="x"></object><embed src="x">', ["<object", "<embed"]),
        ('<div style="background:url(javascript:alert(1))">x</div>', ["style", "javascript"]),
        ('<img src="https://tracker.example/p.gif">', ["<img", "tracker.example"]),
        ('<meta http-equiv="refresh" content="0;url=https://evil.example"><p>a</p>', ["<meta", "evil.example"]),
        ('<base href="https://evil.example/"><p>a</p>', ["<base", "evil.example"]),
        ('<button formaction="x">b</button>', ["<button", "formaction"]),
    ]

    def test_dangerous_content_is_removed(self):
        for src, forbidden in self.BAD:
            out = str(sanitize_notice(src)).lower()
            for word in forbidden:
                self.assertNotIn(word.lower(), out, "%r leaves %r in %r" % (src, word, out))

    def test_allowed_content_is_kept(self):
        src = ('<h2>Maintenance</h2><p>Sunday <b>22:00</b> to <strong>23:00</strong>, <i>sorry</i> <em>e</em> <u>u</u></p>'
               '<ul><li>one</li></ul><ol><li>two</li></ol><hr><span>s</span><div>d</div>')
        out = str(sanitize_notice(src))
        for tag in ("<h2>", "<b>", "<strong>", "<i>", "<em>", "<u>", "<ul>", "<ol>", "<li>", "<hr>", "<span>", "<div>"):
            self.assertIn(tag, out)
        self.assertIn("Maintenance", out)

    def test_links(self):
        out = str(sanitize_notice('<a href="https://example.com/a?b=1&c=2" class="x" style="color:red" onclick="x()">go</a>'
                                  '<a href="http://example.com">h</a><a href="mailto:hello@example.com">m</a>'))
        self.assertEqual(out.count('rel="noopener noreferrer"'), 3)
        self.assertEqual(out.count('target="_blank"'), 3)
        self.assertIn('href="https://example.com/a?b=1&amp;c=2"', out)
        self.assertIn('href="mailto:hello@example.com"', out)
        for word in ("class=", "style=", "onclick"):
            self.assertNotIn(word, out)

    def test_unknown_tags_keep_their_text(self):
        out = str(sanitize_notice("<marquee>moving text</marquee><font color='red'>red</font>"))
        self.assertIn("moving text", out)
        self.assertNotIn("<marquee", out)
        self.assertNotIn("<font", out)

    def test_empty_and_idempotent(self):
        self.assertEqual(str(sanitize_notice(False)), "")
        self.assertEqual(str(sanitize_notice("   ")), "")
        once = sanitize_notice('<p>a &amp; b</p><a href="https://example.com">x</a><script>1</script>')
        self.assertEqual(str(sanitize_notice(str(once))), str(once))

    def test_text_is_escaped(self):
        out = str(sanitize_notice("1 < 2 and 3 > 2 &lt;script&gt;alert(1)&lt;/script&gt;"))
        self.assertNotIn("<script", out)
