from unittest.mock import patch

import psycopg2.errors

from odoo.tests import HttpCase, tagged

from odoo.addons.dwo_website_auto_webp.models.ir_binary import WEBP_CACHE_PREFIX

from .test_webp import ACCEPT_WEBP, make_image


class WebpHttpBase(HttpCase):
    """Fixtures and helpers, no test."""

    registry_readonly = False  # True: /web/image runs on a real read-only transaction (server with a replica)
    readonly_enabled = False  # Odoo 18: no read-only transaction for the readonly /web/image route (see setUpClass)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # /web/image is a readonly route: in test mode it gets a real read-only transaction, whereas a production
        # server without a replica gives a read/write cursor. Test the usual production setup.
        if hasattr(cls, 'set_registry_readonly_mode'):  # Odoo 19+
            cls.set_registry_readonly_mode(cls.registry_readonly)
        port = cls.http_port()
        # websites are told apart by the host of the request
        cls.site_a = cls.env['website'].create({'name': 'WebP HTTP A', 'domain': f'127.0.0.1:{port}'})
        cls.site_b = cls.env['website'].create({'name': 'WebP HTTP B', 'domain': f'localhost:{port}'})
        # public attachment: readable by the anonymous visitor of any host (no session cookie needed)
        cls.partner = cls.env['ir.attachment'].create({
            'name': 'webp-http.png', 'raw': make_image(noisy=True), 'mimetype': 'image/png', 'public': True,
        })
        cls.path = f'/web/image/{cls.partner.id}'
        cls.url_a = f'http://127.0.0.1:{port}{cls.path}'
        cls.url_b = f'http://localhost:{port}{cls.path}'

    def get(self, url, accept=ACCEPT_WEBP):
        headers = {'Accept': accept} if accept else {}
        return self.url_open(url, headers=headers)

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
        resp = self.url_open(f'http://127.0.0.1:{self.http_port()}/web/image/{self.partner.id}/80x80', headers={'Accept': ACCEPT_WEBP})
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
            'name': 'broken.png', 'raw': b'not an image', 'mimetype': 'image/png', 'public': True})
        resp = self.get(f'http://127.0.0.1:{self.http_port()}/web/image/{att.id}')
        self.assertLess(resp.status_code, 500)


@tagged('post_install', '-at_install', 'dwo_website_auto_webp')
class TestWebpHttpReadonly(WebpHttpBase):
    """Server with a replica: /web/image (readonly=True) starts on a read-only cursor.

    The cache INSERT fails there with ReadOnlySqlTransaction; the module must let it bubble up so that Odoo
    retries the request with a read/write cursor, which then stores the cache.
    """

    registry_readonly = True
    readonly_enabled = True

    def test_cache_saved_after_retry_with_write_cursor(self):
        resp = self.get(self.url_a)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers['Content-Type'].split(';')[0], 'image/webp')
        self.assertEqual(len(self.caches(self.site_a)), 1)
        # the cache is then served (no second entry)
        again = self.get(self.url_a)
        self.assertEqual(again.headers['Content-Type'].split(';')[0], 'image/webp')
        self.assertEqual(len(self.caches(self.site_a)), 1)

    def test_other_cache_error_does_not_break_response(self):
        attach_cls = type(self.env['ir.attachment'])
        with patch.object(attach_cls, 'create', side_effect=RuntimeError('disk full')):
            resp = self.get(self.url_a)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers['Content-Type'].split(';')[0], 'image/webp')
        self.assertEqual(resp.content[8:12], b'WEBP')
        self.assertFalse(self.caches(self.site_a))

    def test_database_error_on_cache_insert_does_not_break_response(self):
        attach_cls = type(self.env['ir.attachment'])
        with patch.object(attach_cls, 'create', side_effect=psycopg2.errors.UniqueViolation('dup')):
            resp = self.get(self.url_a)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers['Content-Type'].split(';')[0], 'image/webp')
        self.assertFalse(self.caches(self.site_a))
