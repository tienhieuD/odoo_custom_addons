# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from datetime import timedelta

from odoo import fields
from odoo.tests import HttpCase, tagged

from odoo.addons.dwo_login_themes import data, tools


@tagged("post_install", "-at_install")
class TestLoginPage(HttpCase):
    """What an anonymous visitor gets from /web/login: the layout class, the announcement, the untouched form."""

    def setUp(self):
        super().setUp()
        self.website = bool(self.env["ir.module.module"].search([("name", "=", "website"), ("state", "=", "installed")]))
        self.icp = self.env["ir.config_parameter"].sudo()

    def set(self, **values):
        for key, value in values.items():
            tools.icp_set(self.icp, "dwo_login." + key, value)

    def notice_html(self, html):
        """The announcement block of the page (the page itself has other scripts, with words such as onerror)."""
        start = html.index("dwo_notice ")
        return html[start:html.index("</div>", html.index("dwo_notice_body", start)) + 6]

    def page(self, path="/web/login"):
        response = self.url_open(path)
        self.assertEqual(response.status_code, 200)
        return response.text

    def test_01_every_layout_keeps_the_form(self):
        if self.website:
            self.skipTest("with Website the login page is drawn in the layout of Website: the layouts do not apply")
        for layout, _label in data.LAYOUTS:
            self.set(layout=layout)
            html = self.page()
            self.assertIn("dwo_l_%s " % layout, html, layout)
            for needle in ('name="login"', 'name="password"', 'type="submit"', "oe_login_form", "csrf_token", "o_database_list"):
                self.assertIn(needle, html, "%s: %s" % (layout, needle))

    def test_02_notice_shown_to_anonymous_and_sanitized(self):
        self.set(ann_enabled="1", ann_kind="warning", ann_pos="above", ann_html=(
            "<p><strong>Planned maintenance</strong> on Sunday.</p><script>alert(1)</script>"
            '<img src=x onerror="alert(2)"><a href="javascript:alert(3)">bad</a>'
            '<a href="https://status.example.com">status</a>'))
        html = self.page()
        self.assertIn("dwo_notice", html)
        self.assertIn("dwo_notice_warning", html)
        self.assertIn("Planned maintenance", html)
        self.assertIn('href="https://status.example.com" rel="noopener noreferrer" target="_blank"', html)
        block = self.notice_html(html)
        for bad in ("alert(1)", "alert(2)", "alert(3)", "onerror", "javascript:", "<script", "<img"):
            self.assertNotIn(bad, block)
            self.assertNotIn("alert(", html)
        # still the real login form
        self.assertIn('name="login"', html)
        self.assertIn('type="submit"', html)

    def test_03_notice_param_edited_by_hand_is_sanitized_on_render(self):
        # the second layer: a parameter written straight into the database, not through the settings screen
        self.set(ann_enabled="1", ann_html="<p>hand</p><script>alert('x1')</script><b onmouseover=\"alert('x2')\">b</b>")
        html = self.page()
        self.assertIn("hand", html)
        self.assertNotIn("alert('x1')", html)
        self.assertNotIn("onmouseover", html)

    def test_04_notice_positions(self):
        for pos in ("above", "below", "top"):
            self.set(ann_enabled="1", ann_html="<p>Position %s</p>" % pos, ann_pos=pos)
            html = self.page()
            self.assertIn("dwo_notice_pos_%s" % pos, html)
        # below: after the form; above: before it
        self.set(ann_pos="above")
        html = self.page()
        self.assertLess(html.index("dwo_notice_pos_above"), html.index("oe_login_form"))
        self.set(ann_pos="below")
        html = self.page()
        self.assertGreater(html.index("dwo_notice_pos_below"), html.index("oe_login_form"))

    def test_05_notice_switch_empty_and_dates(self):
        self.set(ann_enabled="0", ann_html="<p>Hidden text</p>")
        self.assertNotIn("Hidden text", self.page())
        self.set(ann_enabled="1", ann_html="  ")
        self.assertNotIn("dwo_notice", self.page())
        now = fields.Datetime.now()
        self.set(ann_enabled="1", ann_html="<p>Dated text</p>")
        self.set(ann_start=fields.Datetime.to_string(now + timedelta(hours=1)), ann_end="")
        self.assertNotIn("Dated text", self.page(), "not started yet")
        self.set(ann_start=fields.Datetime.to_string(now - timedelta(hours=1)), ann_end=fields.Datetime.to_string(now + timedelta(hours=1)))
        self.assertIn("Dated text", self.page(), "inside the window")
        self.set(ann_start="", ann_end=fields.Datetime.to_string(now - timedelta(minutes=1)))
        self.assertNotIn("Dated text", self.page(), "already ended")

    def test_06_dismiss_button_and_theme_off(self):
        if self.website:
            self.skipTest("with Website the layouts do not apply")
        self.set(ann_enabled="1", ann_html="<p>Closable</p>", ann_dismiss="1")
        self.assertIn("dwo_notice_close", self.page())
        self.set(ann_dismiss="0")
        self.assertNotIn("dwo_notice_close", self.page())
        # the theme off: the standard page, but the announcement stays
        self.set(enabled="0")
        html = self.page()
        self.assertNotIn("dwo_lc", html)
        self.assertNotIn("dwo_bg", html)
        self.assertIn("Closable", html)
        self.assertIn('name="login"', html)

    def test_07_colours_cannot_inject_css(self):
        if self.website:
            self.skipTest("with Website the layouts do not apply")
        self.set(enabled="1", primary="red;} body{display:none", button="#ABC", text="url(javascript:1)",
                 overlay="999", blur="-5", bg_grad_angle="abc")
        html = self.page()
        self.assertNotIn("display:none", html)
        self.assertNotIn("javascript:1", html)
        self.assertIn("--dwo-primary:#714B67", html)  # back to the default
        self.assertIn("--dwo-button:#ABC", html)
        self.assertIn("--dwo-overlay:0.90", html)
        self.assertIn("--dwo-blur:0px", html)

    def test_08_texts_are_escaped(self):
        if self.website:
            self.skipTest("with Website the layouts do not apply")
        self.set(enabled="1", welcome_title="<b>Hi</b>", footer_text="<script>x</script>", intro_title="<i>t</i>",
                 intro_items="<u>a</u>\nsecond", page_title='"><script>1</script>')
        html = self.page()
        self.assertIn("&lt;b&gt;Hi&lt;/b&gt;", html)
        self.assertNotIn("<b>Hi</b>", html)
        self.assertNotIn("<script>x</script>", html)
        self.assertIn("&lt;u&gt;a&lt;/u&gt;", html)
        self.assertNotIn('"><script>1</script>', html)

    def test_09_other_pages_with_the_layout(self):
        if self.website:
            self.skipTest("with Website the layouts do not apply")
        """The reset password page uses the same layout: themed, with the announcement."""
        if not self.env["ir.module.module"].search([("name", "=", "auth_signup"), ("state", "=", "installed")]):
            self.skipTest("auth_signup is not installed")
        self.set(layout="glass", ann_enabled="1", ann_html="<p>Everywhere</p>")
        tools.icp_set(self.icp, "auth_signup.reset_password", "True")
        html = self.page("/web/reset_password")
        self.assertIn("dwo_l_glass", html)
        self.assertIn("Everywhere", html)

    def test_10_website_layout_is_left_alone(self):
        """With Website the standard layout is replaced: the page renders, the form works, the announcement shows."""
        if not self.website:
            self.skipTest("website is not installed")
        for pos in ("above", "below", "top"):
            self.set(ann_enabled="1", ann_html="<p>Site notice</p><script>alert(9)</script>", ann_pos=pos)
            html = self.page()
            self.assertIn("Site notice", html)
            self.assertNotIn("alert(9)", html)
            self.assertIn('name="login"', html)
            self.assertIn('type="submit"', html)

    def test_11_backgrounds(self):
        if self.website:
            self.skipTest("with Website the layouts do not apply")
        theme = self.env["dwo.login.theme"]
        self.set(bg_type="gallery", bg_mode="single", bg_image="aurora")
        self.assertEqual(theme.background_images(), ["/dwo_login_themes/static/src/img/bg/aurora.webp"])
        self.set(bg_mode="slideshow", bg_pool="all")
        self.assertEqual(len(set(theme.background_images())), 4)
        self.set(bg_mode="random", bg_pool="dark")
        night = {"/dwo_login_themes/static/src/img/bg/%s.webp" % g[0] for g in data.GALLERY if g[2] == "night"}
        self.assertTrue(set(theme.background_images()) <= night)
        self.set(bg_mode="timeofday")
        self.assertEqual(len(theme.background_images()), 1)
        self.set(bg_mode="single", bg_type="color")
        self.assertEqual(theme.background_images(), [])
        self.assertIn("dwo_bgt_color", self.page())
        self.set(bg_type="gradient")
        self.assertIn("dwo_bgt_gradient", self.page())
        self.set(bg_type="upload")  # nothing uploaded: falls back to the bundled image
        self.assertEqual(len(theme.background_images()), 1)

    def test_12_bundled_images(self):
        import os
        from odoo.modules import get_module_path
        base = os.path.join(get_module_path("dwo_login_themes"), "static", "src", "img", "bg")
        scss = open(os.path.join(get_module_path("dwo_login_themes"), "static", "src", "scss", "settings.scss")).read()
        self.assertGreaterEqual(len(data.GALLERY), 20)
        for key in data.GALLERY_KEYS:
            path = os.path.join(base, key + ".webp")
            self.assertTrue(os.path.isfile(path), key)
            self.assertLessEqual(os.path.getsize(path), 150 * 1024, key)
            self.assertTrue(os.path.isfile(os.path.join(base, "thumb", key + ".webp")), key)
            self.assertIn('data-value="%s"' % key, scss)
        self.assertGreaterEqual(len(data.LAYOUTS), 12)
        for key, _label in data.LAYOUTS:
            self.assertIn('data-value="%s"' % key, scss)

    def test_13_dark_card_class(self):
        """A dark card colour (the Midnight preset) puts a class on the page so the fields and buttons turn dark too."""
        self.assertTrue(tools.is_dark_color("#1B1E2B"))
        self.assertTrue(tools.is_dark_color("#000"))
        self.assertFalse(tools.is_dark_color("#FFFFFF"))
        self.assertFalse(tools.is_dark_color("#E9ECEF"))
        self.assertFalse(tools.is_dark_color("red"))  # not a hex colour: never dark
        self.set(enabled="1", layout="card", card_bg="#1B1E2B")
        self.assertIn("dwo_card_dark", self.page())
        self.set(card_bg="#FFFFFF")
        self.assertNotIn("dwo_card_dark", self.page())
