# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""The image proxy of remote pictures (#79): SSRF guards, clean pictures, access, route."""
import io
import socket
from unittest.mock import patch

from PIL import Image

from odoo.tests import HttpCase, TransactionCase, new_test_user, tagged

from odoo.addons.dwo_attpreview_mail.parsers import remote

REMOTE = "odoo.addons.dwo_attpreview_mail.parsers.remote"


def png(color=(200, 30, 30), size=(4, 3), fmt="PNG"):
    out = io.BytesIO()
    Image.new("RGB", size, color).save(out, fmt)
    return out.getvalue()


def addrinfo(*ips):
    return lambda host, port, **kw: [(socket.AF_INET6 if ":" in ip else socket.AF_INET, socket.SOCK_STREAM, 6, "",
                                       (ip, port)) for ip in ips]


EML = b"""From: a@example.com
Subject: Pictures
Content-Type: text/html; charset=utf-8

<p>Hi</p><img src="https://cdn.example.com/a.png" alt="A"><img src="http://plain.example.com/b.png" alt="B">
<img src="https://cdn.example.com/c.png?x=1&amp;y=2" srcset="https://cdn.example.com/c2.png 2x">
"""


@tagged("post_install", "-at_install")
class TestRemoteGuards(TransactionCase):

    def setUp(self):
        super().setUp()
        remote.CACHE.clear()

    def test_01_urls(self):
        self.assertEqual(remote.check_url("https://cdn.example.com/a.png?x=1"), ("https", "cdn.example.com", 443, "/a.png?x=1"))
        for url in ("http://cdn.example.com/a.png", "ftp://x.example.com/a", "file:///etc/passwd", "javascript:alert(1)",
                    "https://user:pw@cdn.example.com/a.png", "https://cdn.example.com:8069/a.png", "https:///a.png",
                    "data:image/png;base64,AAAA", "https://[::1"):
            with self.assertRaises(remote.RemoteImageError, msg=url):
                remote.check_url(url)
        self.assertEqual(remote.check_url("http://cdn.example.com/a.png", https_only=False)[2], 80)

    def test_02_private_addresses_refused(self):
        for ips in (("127.0.0.1",), ("10.1.2.3",), ("192.168.1.10",), ("172.16.0.5",), ("169.254.169.254",),
                    ("100.64.0.1",), ("0.0.0.0",), ("::1",), ("fe80::1",), ("fc00::1",), ("::ffff:127.0.0.1",),
                    ("93.184.216.34", "10.0.0.1")):  # one private answer is enough to refuse
            with patch(REMOTE + ".socket.getaddrinfo", addrinfo(*ips)):
                with self.assertRaises(remote.RemoteImageError, msg=str(ips)):
                    remote.resolve("cdn.example.com", 443)
        with patch(REMOTE + ".socket.getaddrinfo", addrinfo("93.184.216.34", "2606:2800:220:1::1")):
            self.assertEqual(remote.resolve("cdn.example.com", 443), ["93.184.216.34", "2606:2800:220:1::1"])
        with patch(REMOTE + ".socket.getaddrinfo", side_effect=socket.gaierror("no")):
            with self.assertRaises(remote.RemoteImageError):
                remote.resolve("nowhere.example", 443)

    def test_03_connects_to_the_checked_address_and_follows_checked_redirects(self):
        calls = []

        def get(scheme, host, port, path, address):
            calls.append((host, address, path))
            if host == "cdn.example.com":
                return 302, "https://img.example.net/real.png", b""
            return 200, None, png()

        def resolve(host, port):
            return {"cdn.example.com": ["93.184.216.34"], "img.example.net": ["151.101.1.1"]}[host]

        with patch(REMOTE + "._get", get), patch(REMOTE + ".resolve", resolve):
            data, mimetype = remote.fetch_picture("https://cdn.example.com/a.png")
        self.assertEqual(mimetype, "image/png")
        self.assertEqual(calls, [("cdn.example.com", "93.184.216.34", "/a.png"),
                                 ("img.example.net", "151.101.1.1", "/real.png")])

    def test_04_redirect_to_internal_or_plain_http_refused(self):
        for target in ("http://169.254.169.254/latest/meta-data", "https://localhost/x.png", "http://cdn.example.com/a.png"):
            def get(scheme, host, port, path, address, target=target):
                return 302, target, b""
            with patch(REMOTE + "._get", get), patch(REMOTE + ".socket.getaddrinfo", lambda h, p, **k: addrinfo(
                    "127.0.0.1" if h == "localhost" else ("169.254.169.254" if h.startswith("169") else "93.184.216.34"))(h, p)):
                with self.assertRaises(remote.RemoteImageError, msg=target):
                    remote.fetch_picture("https://cdn.example.com/a.png")
        with patch(REMOTE + "._get", lambda *a: (302, "https://cdn.example.com/a.png", b"")), \
                patch(REMOTE + ".resolve", lambda h, p: ["93.184.216.34"]):
            with self.assertRaises(remote.RemoteImageError):
                remote.fetch_picture("https://cdn.example.com/a.png")  # redirect loop

    def test_05_only_clean_pictures(self):
        data, mimetype = remote.clean_picture(png(fmt="JPEG"))
        self.assertEqual(mimetype, "image/jpeg")
        self.assertEqual(remote.clean_picture(png(fmt="GIF"))[1], "image/png")
        try:  # WebP only when this Pillow can write it (libwebp)
            webp = png(fmt="WEBP")
        except (KeyError, OSError):
            webp = None
        if webp:
            self.assertEqual(remote.clean_picture(webp)[1], "image/png")
        svg = b'<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"/>'
        for bad in (svg, b"<html>hello</html>", b"", png()[:20], png(fmt="BMP")):
            with self.assertRaises(remote.RemoteImageError):
                remote.clean_picture(bad)
        with patch.object(remote, "MAX_PIXELS", 10):
            with self.assertRaises(remote.RemoteImageError):
                remote.clean_picture(png(size=(4, 4)))

    def test_06_cache(self):
        calls = []

        def fetch(url, https_only):
            calls.append(url)
            if "bad" in url:
                raise remote.RemoteImageError("not a picture")
            return png(), "image/png"

        self.assertEqual(remote.cached_picture("https://a.example/x.png", fetch=fetch)[1], "image/png")
        remote.cached_picture("https://a.example/x.png", fetch=fetch)
        for _ in range(2):
            with self.assertRaises(remote.RemoteImageError):
                remote.cached_picture("https://a.example/bad.png", fetch=fetch)
        self.assertEqual(calls, ["https://a.example/x.png", "https://a.example/bad.png"])


@tagged("post_install", "-at_install")
class TestRemoteEngine(TransactionCase):

    def test_01_urls_from_the_email_in_order(self):
        engine = self.env["dwo.attpreview.engine.mail"]
        d = engine._dwo_render(EML, "p.eml")["data"]
        self.assertEqual((d["remote_images"], d["remote_insecure"]), (3, 1))
        self.assertNotIn("example.com", d["body_html"])
        self.assertNotIn("srcset", d["body_html"])
        for i in range(3):
            self.assertIn('<img data-dwo-remote="%d" hidden' % i, d["body_html"])
        self.assertEqual(engine._dwo_remote_images(EML, "p.eml"), [
            "https://cdn.example.com/a.png", "http://plain.example.com/b.png", "https://cdn.example.com/c.png?x=1&y=2"])

    def test_02_defaults_on(self):
        get = self.env["ir.config_parameter"].sudo().get_bool  # Odoo 20: typed getters
        self.assertTrue(get("dwo_attpreview_mail.remote_images"))
        self.assertTrue(get("dwo_attpreview_mail.remote_https_only"))
        settings = self.env["res.config.settings"].create({})
        self.assertTrue(settings.dwo_attpreview_mail_remote_images and settings.dwo_attpreview_mail_remote_https_only)


@tagged("post_install", "-at_install")
class TestRemoteRoute(HttpCase):

    def setUp(self):
        super().setUp()
        remote.CACHE.clear()
        self.partner = self.env["res.partner"].create({"name": "Pictures"})
        self.att = self.env["ir.attachment"].create({"name": "p.eml", "raw": EML, "res_model": "res.partner",
                                                     "res_id": self.partner.id})
        self.fetched = []

        def fake(url, https_only=True):
            remote.check_url(url, https_only)  # same scheme rule as the real download
            self.fetched.append(url)
            return png(), "image/png"

        patcher = patch(REMOTE + ".fetch_picture", fake)
        patcher.start()
        self.addCleanup(patcher.stop)

    def url(self, index, **extra):
        params = "&".join("%s=%s" % kv for kv in dict({"attachment_id": self.att.id, "index": index}, **extra).items())
        return "/dwo_attpreview_mail/remote_image?" + params

    def test_01_picture_by_position_only(self):
        self.authenticate("admin", "admin")
        res = self.url_open(self.url(0))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers["Content-Type"], "image/png")
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(res.headers.get("Content-Security-Policy"), "default-src 'none'")
        self.assertEqual(res.headers.get("Referrer-Policy"), "no-referrer")
        self.assertIn("private", res.headers.get("Cache-Control", ""))
        self.assertEqual(self.fetched, ["https://cdn.example.com/a.png"])
        # any other parameter is ignored: the address always comes from the email
        res = self.url_open(self.url(2, url="http://169.254.169.254/", src="https://evil.example/x"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.fetched[-1], "https://cdn.example.com/c.png?x=1&y=2")
        for bad in (3, -1, "x"):
            self.assertEqual(self.url_open(self.url(bad)).status_code, 404)

    def test_02_https_only_setting(self):
        self.authenticate("admin", "admin")
        res = self.url_open(self.url(1))
        self.assertEqual(res.status_code, 422, "plain http is off by default")
        self.assertEqual(res.text, "scheme not allowed", "the reason is given to the viewer")
        self.env["ir.config_parameter"].sudo().set_bool("dwo_attpreview_mail.remote_https_only", False)
        remote.CACHE.clear()
        self.assertEqual(self.url_open(self.url(1)).status_code, 200)

    def test_02b_programs_and_scripts_are_refused_before_any_download(self):
        for url in ("https://x.example/a.exe", "https://x.example/run.sh?x=1", "https://x.example/p/app.JS",
                    "https://x.example/logo.svg", "https://x.example/a.zip"):
            with self.assertRaises(remote.RemoteImageError, msg=url) as ctx:
                remote.check_url(url)
            self.assertEqual(str(ctx.exception), "not a picture")
        self.assertEqual(remote.check_url("https://x.example/pixel.php?id=1")[3], "/pixel.php?id=1")

    def test_03_access_of_the_email(self):
        new_test_user(self.env, login="dwo_remote_portal", password="dwo_remote_portal", groups="base.group_portal")
        self.authenticate("dwo_remote_portal", "dwo_remote_portal")
        self.assertEqual(self.url_open(self.url(0)).status_code, 404)
        self.authenticate(None, None)
        self.assertNotEqual(self.url_open(self.url(0), allow_redirects=False).status_code, 200)
        self.assertEqual(self.fetched, [])
        other = self.env["ir.attachment"].create({"name": "x.pdf", "raw": b"%PDF-1.4"})
        self.authenticate("admin", "admin")
        self.assertEqual(self.url_open("/dwo_attpreview_mail/remote_image?attachment_id=%d&index=0" % other.id).status_code, 404)
