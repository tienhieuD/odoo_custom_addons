# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import base64
import io

from PIL import Image

from odoo.exceptions import UserError
from odoo.tests import HttpCase, tagged

from odoo.addons.dwo_login_themes import tools


def make_image(fmt="PNG", size=(64, 48), mode="RGB", color=(200, 30, 30)):
    buf = io.BytesIO()
    Image.new(mode, size, color).save(buf, fmt)
    return buf.getvalue()


def b64(raw):
    return base64.b64encode(raw)


def b64s(raw):
    """base64 text: what the web client sends, accepted by every version for a Binary field"""
    return base64.b64encode(raw).decode()


@tagged("post_install", "-at_install")
class TestImages(HttpCase):
    """Uploaded images (background, logo, tab icon): validated, recompressed, served only from the settings."""

    @property
    def themed(self):
        """False with the Website app: its layout replaces the one the module themes."""
        return not self.env["ir.module.module"].search([("name", "=", "website"), ("state", "=", "installed")])

    def save_settings(self, **values):
        settings = self.env["res.config.settings"].create({"dwo_login_" + k: v for k, v in values.items()})
        settings.execute()

    def test_01_valid_uploads_are_recompressed(self):
        for fmt in ("PNG", "JPEG", "WEBP"):
            raw, mimetype = tools.process_image(b64(make_image(fmt, size=(3000, 2000))), "bg")
            self.assertEqual(mimetype, "image/webp")
            img = Image.open(io.BytesIO(raw))
            self.assertEqual(img.format, "WEBP")
            self.assertLessEqual(max(img.size), 1920)
        raw, mimetype = tools.process_image(b64(make_image("PNG", size=(1600, 800), mode="RGBA", color=(0, 0, 0, 0))), "logo")
        self.assertEqual(mimetype, "image/webp")
        self.assertLessEqual(Image.open(io.BytesIO(raw)).size[0], 800)
        raw, mimetype = tools.process_image(b64(make_image("PNG", size=(512, 512))), "favicon")
        self.assertEqual(mimetype, "image/png")
        self.assertLessEqual(max(Image.open(io.BytesIO(raw)).size), 128)

    def test_02_bad_uploads_are_rejected(self):
        svg = b'<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"><script>alert(1)</script></svg>'
        gif = make_image("GIF")
        huge = make_image("PNG", size=(7000, 7000), mode="1", color=1)  # 49 megapixels
        too_big = b"\x89PNG\r\n\x1a\n" + b"0" * (tools.MAX_UPLOAD_BYTES + 10)
        for label, raw in (("svg", svg), ("html", b"<html><script>1</script></html>"), ("text", b"hello"), ("gif", gif),
                           ("empty", b""), ("huge pixels", huge), ("big file", too_big),
                           ("truncated png", make_image("PNG")[:60])):
            with self.assertRaises(UserError, msg=label):
                tools.process_image(b64(raw), "bg")

    def test_03_upload_is_served_and_only_that_one(self):
        self.save_settings(bg_upload=b64s(make_image("JPEG", size=(800, 600))), bg_type="upload")
        theme = self.env["dwo.login.theme"]
        att_id = theme.attachment_id("bg")
        self.assertTrue(att_id)
        att = self.env["ir.attachment"].browse(att_id)
        self.assertEqual((att.res_model, att.name, att.mimetype), ("dwo.login.theme", "dwo_login_bg", "image/webp"))
        # the login page uses it and anonymous visitors can read it
        if self.themed:
            self.assertIn("/dwo_login/img/bg/%d" % att_id, self.url_open("/web/login").text)
        response = self.url_open("/dwo_login/img/bg/%d" % att_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "image/webp")
        self.assertEqual(Image.open(io.BytesIO(response.content)).format, "WEBP")
        self.assertIn("immutable", response.headers["Cache-Control"])
        # nothing else can be read through the route
        other = self.env["ir.attachment"].create({"name": "secret.txt", "raw": b"secret", "res_model": "res.partner", "res_id": 1})
        fake = self.env["ir.attachment"].create({"name": "dwo_login_bg", "raw": b"secret", "res_model": "res.partner", "res_id": 1})
        for url in ("/dwo_login/img/bg/%d" % other.id, "/dwo_login/img/bg/%d" % fake.id,
                    "/dwo_login/img/logo/%d" % att_id,  # right id, wrong kind
                    "/dwo_login/img/bg/999999", "/dwo_login/img/other/%d" % att_id):
            self.assertEqual(self.url_open(url).status_code, 404, url)
        # a parameter pointing at a foreign attachment is not served either
        tools.icp_set(self.env["ir.config_parameter"].sudo(), "dwo_login.logo_att", str(fake.id))
        self.assertEqual(self.url_open("/dwo_login/img/logo/%d" % fake.id).status_code, 404)

    def test_04_replace_and_remove(self):
        self.save_settings(logo_upload=b64s(make_image("PNG")))
        theme = self.env["dwo.login.theme"]
        first = theme.attachment_id("logo")
        if self.themed:
            self.assertIn("/dwo_login/img/logo/%d" % first, self.url_open("/web/login").text)
        self.save_settings(logo_upload=b64s(make_image("PNG", color=(1, 2, 3))))
        second = theme.attachment_id("logo")
        self.assertNotEqual(first, second)
        self.assertFalse(self.env["ir.attachment"].browse(first).exists(), "the old file is deleted")
        self.save_settings(logo_upload=False)
        self.assertFalse(theme.attachment_id("logo"))
        self.assertFalse(self.env["ir.attachment"].browse(second).exists())
        self.assertNotIn("/dwo_login/img/logo", self.url_open("/web/login").text)

    def test_05_bad_upload_in_settings_is_refused(self):
        with self.assertRaises(UserError):
            self.save_settings(bg_upload=b64s(b"<svg onload=alert(1)></svg>"))
        self.assertFalse(self.env["dwo.login.theme"].attachment_id("bg"))

    def test_06_settings_round_trip(self):
        self.save_settings(layout="glass", pwd_toggle=False, ann_enabled=True, ann_html="<p>x</p><script>1</script>",
                           primary="#112233", overlay=40)
        values = self.env["res.config.settings"].get_values()
        self.assertEqual(values["dwo_login_layout"], "glass")
        self.assertIs(values["dwo_login_pwd_toggle"], False)  # a False boolean stays False (default is True)
        self.assertEqual(values["dwo_login_primary"], "#112233")
        self.assertEqual(values["dwo_login_overlay"], 40)
        self.assertNotIn("script", values["dwo_login_ann_html"])  # stored already clean
        self.assertNotIn("data-dwo-pwd", self.url_open("/web/login").text)

    def test_07_preset_fills_the_colours(self):
        settings = self.env["res.config.settings"].new({"dwo_login_preset": "midnight"})
        settings._onchange_dwo_login_preset()
        self.assertEqual(settings.dwo_login_card_bg, "#1B1E2B")
        self.assertEqual(settings.dwo_login_primary, "#8B7CFF")
        settings.dwo_login_ann_html = "<p>a</p><script>x</script>"
        self.assertNotIn("script", str(settings.dwo_login_ann_preview))

    def test_08_uninstall_hook_removes_settings_and_images(self):
        from odoo.addons.dwo_login_themes import uninstall_hook
        self.save_settings(logo_upload=b64s(make_image("PNG")), layout="glass")
        self.assertTrue(self.env["dwo.login.theme"].attachment_id("logo"))
        uninstall_hook(self.env)
        self.assertFalse(self.env["ir.config_parameter"].sudo().search([("key", "=like", "dwo_login.%")]))
        self.assertFalse(self.env["ir.attachment"].sudo().search([("res_model", "=", "dwo.login.theme")]))
