import base64
from odoo.tests import HttpCase, tagged
from odoo.tools import config

from odoo.addons.dwo_website_auto_webp.models.webp_helper import WEBP_CACHE_PREFIX

from .test_webp import ACCEPT_WEBP, make_image


def http_port():
    # Odoo 17 and older: no HttpCase.http_port(), the port is the --http-port of the server
    return config['http_port']


class WebpHttpBase(HttpCase):
    """Fixtures and helpers, no test."""

    def setUp(self):
        super().setUp()
        cls = self  # Odoo 12/13/14: HttpCase has no setUpClass/cls.env, fixtures are built in setUp
        port = http_port()
        # websites are told apart by the host of the request
        cls.site_a = cls.env['website'].create({'name': 'WebP HTTP A', 'domain': f'127.0.0.1:{port}'})
        cls.site_b = cls.env['website'].create({'name': 'WebP HTTP B', 'domain': f'localhost:{port}'})
        # public attachment: readable by the anonymous visitor of any host (no session cookie needed)
        cls.partner = cls.env['ir.attachment'].create({
            'name': 'webp-http.png', 'datas': base64.b64encode(make_image(noisy=True)), 'mimetype': 'image/png', 'public': True,
        })
        cls.path = f'/web/image/{cls.partner.id}'
        cls.url_a = f'http://127.0.0.1:{port}{cls.path}'
        cls.url_b = f'http://localhost:{port}{cls.path}'

    def get(self, url, accept=ACCEPT_WEBP):
        headers = {'Accept': accept} if accept else {}
        # Odoo 12 url_open() takes no headers: use the opener of the test
        return self.opener.get(url, headers=headers, timeout=10)

    def caches(self, site):
        return self.env['ir.attachment'].sudo().search([
            ('name', '=like', f'{WEBP_CACHE_PREFIX}w{site.id}:%'),
            ('res_model', '=', 'ir.attachment'), ('res_id', '=', self.partner.id)])


@tagged('post_install', '-at_install', 'dwo_website_auto_webp')
class TestWebpHttp(WebpHttpBase):
    """End to end through /web/image: real request, Accept header, Content-Type."""

    def test_webp_served_with_accept(self):
        resp = self.get(self.url_a)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers['Content-Type'].split(';')[0], 'image/webp')
        self.assertEqual(resp.content[:4], b'RIFF')
        self.assertEqual(resp.content[8:12], b'WEBP')

    def test_vary_accept_header(self):
        # the format depends on Accept: shared caches/CDN must key on it
        for accept in (ACCEPT_WEBP, 'image/png,image/*;q=0.8', None):
            resp = self.get(self.url_a, accept=accept)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('accept', resp.headers.get('Vary', '').lower().replace(' ', '').split(','), accept)

    def test_png_served_without_webp_accept(self):
        resp = self.get(self.url_a, accept='image/png,image/*;q=0.8')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers['Content-Type'].split(';')[0], 'image/png')
        self.assertEqual(resp.content[:8], b'\x89PNG\r\n\x1a\n')
        self.assertFalse(self.caches(self.site_a))

    def test_cache_created_and_reused(self):
        self.get(self.url_a)
        self.assertEqual(len(self.caches(self.site_a)), 1)
        second = self.get(self.url_a)
        self.assertEqual(second.headers['Content-Type'].split(';')[0], 'image/webp')
        self.assertEqual(len(self.caches(self.site_a)), 1)

    def test_resize_over_http(self):
        resp = self.get(f'http://127.0.0.1:{http_port()}/web/image/{self.partner.id}/80x80')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers['Content-Type'].split(';')[0], 'image/webp')
        from io import BytesIO
        from PIL import Image
        img = Image.open(BytesIO(resp.content))
        self.assertEqual(max(img.size), 80)

    def test_websites_have_separate_caches(self):
        self.site_a.webp_quality = 95
        self.site_b.webp_quality = 15
        big = self.get(self.url_a)
        small = self.get(self.url_b)
        self.assertEqual(len(self.caches(self.site_a)), 1)
        self.assertEqual(len(self.caches(self.site_b)), 1)
        self.assertGreater(len(big.content), len(small.content))

    def test_disabled_website_serves_original(self):
        self.site_b.auto_webp = False
        resp = self.get(self.url_b)
        self.assertEqual(resp.headers['Content-Type'].split(';')[0], 'image/png')
        self.assertFalse(self.caches(self.site_b))
        # the other website is unaffected
        self.assertEqual(self.get(self.url_a).headers['Content-Type'].split(';')[0], 'image/webp')

    def test_corrupt_attachment_no_server_error(self):
        att = self.env['ir.attachment'].create({
            'name': 'broken.png', 'datas': base64.b64encode(b'not an image'), 'mimetype': 'image/png', 'public': True})
        resp = self.get(f'http://127.0.0.1:{http_port()}/web/image/{att.id}')
        self.assertLess(resp.status_code, 500)
