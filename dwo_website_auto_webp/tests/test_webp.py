import base64
import io
import os
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import psycopg2.errors
import requests
from PIL import Image

from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged

from odoo.addons.dwo_website_auto_webp.models.ir_binary import WEBP_CACHE_PREFIX

IRB = 'odoo.addons.dwo_website_auto_webp.models.ir_binary'
ICFG = 'odoo.addons.dwo_website_auto_webp.models.res_config_settings'
ACCEPT_WEBP = 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8'


def make_image(fmt='PNG', size=(300, 200), noisy=False, mode='RGB'):
    """Self-generated test image (no external file)."""
    if noisy:
        img = Image.frombytes('RGB', size, os.urandom(size[0] * size[1] * 3))
    else:
        img = Image.new('RGB', size)
        px = img.load()
        for x in range(size[0]):
            for y in range(size[1]):
                px[x, y] = (x % 256, y % 256, (x + y) % 256)
    if mode == 'RGBA':
        img.putalpha(Image.linear_gradient('L').resize(size))  # real transparency
    elif mode != 'RGB':
        img = img.convert(mode)
    out = io.BytesIO()
    img.save(out, format=fmt)
    return out.getvalue()


def fake_request(accept=ACCEPT_WEBP, db=None):
    headers = {'Accept': accept} if accept is not None else {}
    return SimpleNamespace(httprequest=SimpleNamespace(headers=headers, environ={}), params={}, db=db)


class WebpCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env['website'].create({'name': 'WebP Test Site A'})
        cls.website_b = cls.env['website'].create({'name': 'WebP Test Site B'})
        cls.partner = cls.env['res.partner'].create({
            'name': 'WebP Test Partner',
            'image_1920': base64.b64encode(make_image(noisy=True)),
        })

    # helpers
    def stream(self, record=None, website=None, accept=ACCEPT_WEBP, field='image_1920', **kw):
        website = website or self.website
        record = record if record is not None else self.partner
        binary = self.env['ir.binary'].with_context(website_id=website.id)
        # the core code reads request.db / request.httprequest.environ: fake a request outside of a real one
        fake = fake_request(accept, self.env.cr.dbname)
        with patch(f'{IRB}.request', fake if accept is not False else None), \
                patch('odoo.addons.base.models.ir_binary.request', fake), \
                patch('odoo.addons.base.models.ir_attachment.request', fake):
            return binary._get_image_stream_from(record, field, **kw)

    def caches(self, website=None, record=None):
        domain = [('name', '=like', WEBP_CACHE_PREFIX + (f'w{website.id}:' if website else '') + '%')]
        if record:
            domain += [('res_model', '=', record._name), ('res_id', '=', record.id)]
        return self.env['ir.attachment'].sudo().search(domain)

    def attachment(self, raw, mimetype, name='img'):
        return self.env['ir.attachment'].create({
            'name': name, 'raw': raw, 'mimetype': mimetype, 'public': True,
        })

    def assertWebp(self, data, size=None):
        self.assertEqual(data[:4], b'RIFF')
        self.assertEqual(data[8:12], b'WEBP')
        img = Image.open(io.BytesIO(data))
        self.assertEqual(img.format, 'WEBP')
        if size:
            self.assertEqual(img.size, size)


class TestWebpStream(WebpCommon):

    def test_webp_when_accept_has_webp(self):
        s = self.stream()
        self.assertEqual(s.mimetype, 'image/webp')
        self.assertWebp(s.data, (300, 200))

    def test_original_when_accept_lacks_webp(self):
        s = self.stream(accept='image/png,image/*;q=0.8')
        self.assertEqual(s.mimetype, 'image/png')
        self.assertFalse(self.caches(self.website))

    def test_original_when_no_accept_header(self):
        s = self.stream(accept=None)
        self.assertNotEqual(s.mimetype, 'image/webp')
        self.assertFalse(self.caches())

    def test_original_when_no_request(self):
        s = self.stream(accept=False)
        self.assertNotEqual(s.mimetype, 'image/webp')
        self.assertFalse(self.caches())

    def test_cache_created_once(self):
        self.stream()
        cache = self.caches(self.website, self.partner)
        self.assertEqual(len(cache), 1)
        self.assertEqual(cache.mimetype, 'image/webp')
        self.assertTrue(cache.name.startswith(f'{WEBP_CACHE_PREFIX}w{self.website.id}:image_1920:0x0:'))
        self.assertTrue(cache.name.endswith(':q85'))
        self.assertWebp(cache.raw)

    def test_second_call_uses_cache_without_converting(self):
        first = self.stream()
        binary_cls = type(self.env['ir.binary'])
        with patch.object(binary_cls, '_webp_convert', side_effect=AssertionError('converted twice')):
            second = self.stream()
        self.assertEqual(len(self.caches(self.website, self.partner)), 1)
        self.assertEqual(second.mimetype, 'image/webp')
        self.assertEqual(first.data, second.data)

    def test_cache_filename_includes_size(self):
        self.stream(width=100, height=100)
        self.stream(width=50, height=50)
        self.stream()
        names = self.caches(self.website, self.partner).mapped('name')
        self.assertEqual(len(names), 3)
        self.assertTrue(any(':100x100:' in n for n in names))
        self.assertTrue(any(':50x50:' in n for n in names))

    def test_resize_result_dimensions(self):
        s = self.stream(width=100, height=100)
        self.assertWebp(s.data)
        img = Image.open(io.BytesIO(s.data))
        self.assertLessEqual(img.size[0], 100)
        self.assertLessEqual(img.size[1], 100)
        self.assertEqual(max(img.size), 100)
        # aspect ratio 3:2 is kept
        self.assertAlmostEqual(img.size[0] / img.size[1], 1.5, delta=0.05)

    def test_resize_width_only(self):
        s = self.stream(width=60)
        img = Image.open(io.BytesIO(s.data))
        self.assertEqual(img.size[0], 60)
        self.assertEqual(img.format, 'WEBP')

    def test_quality_change_new_cache_and_smaller_file(self):
        self.website.webp_quality = 95
        big = self.stream()
        self.website.webp_quality = 10
        small = self.stream()
        self.assertLess(len(small.data), len(big.data))
        self.assertTrue(self.caches(self.website).filtered(lambda c: c.name.endswith(':q10')))

    def test_quality_in_cache_key(self):
        self.website.webp_quality = 70
        self.stream()
        self.assertTrue(self.caches(self.website, self.partner).name.endswith(':q70'))

    def test_rewriting_source_image_invalidates_cache(self):
        self.stream()
        old = self.caches(self.website, self.partner)
        self.partner.image_1920 = base64.b64encode(make_image(size=(120, 80), noisy=True))
        # the key uses write_date to the second: make the new write_date different
        self.env.cr.execute("UPDATE res_partner SET write_date = write_date + interval '30 seconds' WHERE id=%s",
                            [self.partner.id])
        self.partner.invalidate_recordset()
        new = self.stream()
        self.assertWebp(new.data, (120, 80))
        self.assertEqual(len(self.caches(self.website, self.partner)), 2)
        self.assertIn(old, self.caches(self.website, self.partner))

    def test_two_websites_separate_cache(self):
        self.website.webp_quality = 90
        self.website_b.webp_quality = 20
        a = self.stream(website=self.website)
        b = self.stream(website=self.website_b)
        self.assertEqual(len(self.caches(self.website)), 1)
        self.assertEqual(len(self.caches(self.website_b)), 1)
        self.assertGreater(len(a.data), len(b.data))

    def test_auto_webp_disabled_returns_original(self):
        self.website.auto_webp = False
        s = self.stream()
        self.assertEqual(s.mimetype, 'image/png')
        self.assertFalse(self.caches(self.website))

    def test_auto_webp_disabled_only_for_that_website(self):
        self.website.auto_webp = False
        s = self.stream(website=self.website_b)
        self.assertEqual(s.mimetype, 'image/webp')

    def test_svg_not_converted(self):
        svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><rect width="10" height="10"/></svg>'
        att = self.attachment(svg, 'image/svg+xml')
        s = self.stream(att, field='raw')
        self.assertEqual(s.mimetype, 'image/svg+xml')
        self.assertFalse(self.caches(self.website, att))

    def test_gif_not_converted(self):
        att = self.attachment(make_image('GIF', (20, 20)), 'image/gif')
        s = self.stream(att, field='raw')
        self.assertEqual(s.mimetype, 'image/gif')
        self.assertFalse(self.caches(self.website, att))

    def test_webp_source_not_reconverted(self):
        att = self.attachment(make_image('WEBP', (20, 20)), 'image/webp')
        s = self.stream(att, field='raw')
        self.assertEqual(s.mimetype, 'image/webp')
        self.assertFalse(self.caches(self.website, att))

    def test_jpeg_source_converted(self):
        att = self.attachment(make_image('JPEG', (40, 30)), 'image/jpeg')
        s = self.stream(att, field='raw')
        self.assertWebp(s.data, (40, 30))
        self.assertEqual(len(self.caches(self.website, att)), 1)

    def test_png_with_alpha_keeps_alpha(self):
        att = self.attachment(make_image('PNG', (30, 30), mode='RGBA'), 'image/png')
        s = self.stream(att, field='raw')
        self.assertEqual(Image.open(io.BytesIO(s.data)).mode, 'RGBA')

    def test_palette_png_converted(self):
        att = self.attachment(make_image('PNG', (30, 30), mode='P'), 'image/png')
        s = self.stream(att, field='raw')
        self.assertWebp(s.data, (30, 30))

    def test_corrupt_image_falls_back_without_error(self):
        att = self.attachment(b'this is definitely not a png', 'image/png')
        s = self.stream(att, field='raw')
        self.assertEqual(s.mimetype, 'image/png')
        self.assertFalse(self.caches(self.website, att))

    def test_unexpected_error_falls_back_to_original(self):
        binary_cls = type(self.env['ir.binary'])
        with patch.object(binary_cls, '_webp_process', side_effect=RuntimeError('boom')):
            s = self.stream()
        self.assertEqual(s.mimetype, 'image/png')

    def test_webp_encoder_missing_falls_back(self):
        with patch(f'{IRB}._WEBP_SUPPORTED', False):
            s = self.stream()
        self.assertEqual(s.mimetype, 'image/png')
        self.assertFalse(self.caches(self.website))

    def test_cache_save_failure_still_returns_webp(self):
        attach_cls = type(self.env['ir.attachment'])
        with patch.object(attach_cls, 'create', side_effect=RuntimeError('disk full')):
            s = self.stream()
        self.assertEqual(s.mimetype, 'image/webp')

    def test_cache_save_readonly_error_bubbles_up(self):
        # read-only cursor (replica): Odoo must see the error to retry with a read/write cursor
        attach_cls = type(self.env['ir.attachment'])
        with patch.object(attach_cls, 'create', side_effect=psycopg2.errors.ReadOnlySqlTransaction('read-only')):
            with self.assertRaises(psycopg2.errors.ReadOnlySqlTransaction):
                self.stream()
        self.assertFalse(self.caches(self.website))

    def test_cache_save_database_error_keeps_transaction_usable(self):
        attach_cls = type(self.env['ir.attachment'])
        with patch.object(attach_cls, 'create', side_effect=psycopg2.errors.UniqueViolation('dup')):
            s = self.stream()
        self.assertEqual(s.mimetype, 'image/webp')
        self.env.cr.execute('SELECT 1')  # not 'current transaction is aborted'

    def test_cache_save_real_database_error_keeps_transaction_usable(self):
        # a real failing INSERT (NOT NULL violation) aborts the PostgreSQL transaction unless it runs in a savepoint
        cr = self.env.cr

        def failing_create(*args, **kwargs):
            cr.execute('INSERT INTO ir_attachment (name) VALUES (NULL)')

        attach_cls = type(self.env['ir.attachment'])
        with patch.object(attach_cls, 'create', side_effect=failing_create):
            s = self.stream()
        self.assertEqual(s.mimetype, 'image/webp')
        self.assertEqual(s.data[8:12], b'WEBP')
        cr.execute('SELECT 1')  # not 'current transaction is aborted'
        self.assertFalse(self.caches(self.website))

    def test_convert_helper_quality_range(self):
        binary = self.env['ir.binary']
        raw = make_image(noisy=True, size=(64, 64))
        self.assertLess(len(binary._webp_convert(raw, 1)), len(binary._webp_convert(raw, 100)))
        self.assertIsNone(binary._webp_convert(b'garbage', 80))


class TestWebpWebsite(WebpCommon):

    def test_defaults(self):
        site = self.env['website'].create({'name': 'WebP Defaults'})
        self.assertTrue(site.auto_webp)
        self.assertEqual(site.webp_quality, 85)

    def test_quality_constraint_invalid(self):
        for bad in (0, 101, -5, 1000):
            with self.subTest(quality=bad), self.assertRaises(ValidationError):
                self.website.webp_quality = bad

    def test_quality_constraint_boundaries(self):
        for ok in (1, 100, 50):
            with self.subTest(quality=ok):
                self.website.webp_quality = ok
                self.assertEqual(self.website.webp_quality, ok)

    def test_write_quality_clears_only_that_website(self):
        self.stream(website=self.website)
        self.stream(website=self.website_b)
        self.website.webp_quality = 60
        self.assertFalse(self.caches(self.website))
        self.assertEqual(len(self.caches(self.website_b)), 1)

    def test_write_auto_webp_clears_cache(self):
        self.stream(website=self.website)
        self.website.auto_webp = False
        self.assertFalse(self.caches(self.website))

    def test_write_other_field_keeps_cache(self):
        self.stream(website=self.website)
        self.website.name = 'WebP Renamed'
        self.assertEqual(len(self.caches(self.website)), 1)

    def test_clear_cache_prefix_does_not_hit_other_ids(self):
        """w1: must not match w10:, w11: ... (the prefix includes the trailing colon)."""
        other = self.env['ir.attachment'].create({
            'name': f'{WEBP_CACHE_PREFIX}w{self.website.id}0:image_1920:0x0:1:q85',
            'res_model': 'res.partner', 'res_id': self.partner.id, 'raw': b'x', 'mimetype': 'image/webp',
        })
        self.website._webp_clear_cache()
        self.assertTrue(other.exists())

    def test_get_website_config(self):
        binary = self.env['ir.binary'].with_context(website_id=self.website.id)
        self.website.webp_quality = 42
        self.assertEqual(binary._webp_get_website_config(), (self.website.id, 42))
        self.website.auto_webp = False
        self.assertEqual(binary._webp_get_website_config(), (0, None))


class TestWebpVacuum(WebpCommon):

    def _cache_for(self, res_id, name_suffix='a'):
        return self.env['ir.attachment'].create({
            'name': f'{WEBP_CACHE_PREFIX}w1:image_1920:0x0:{name_suffix}:q85',
            'res_model': 'res.partner', 'res_id': res_id, 'raw': b'RIFF0000WEBP', 'mimetype': 'image/webp',
        })

    def test_vacuum_removes_orphans_keeps_live(self):
        self.env['ir.attachment'].search([('name', '=like', WEBP_CACHE_PREFIX + '%')]).unlink()
        live = self._cache_for(self.partner.id)
        orphan = self._cache_for(2_000_000_000)
        orphan2 = self._cache_for(2_000_000_000, 'b')
        self.env['ir.attachment']._webp_vacuum()
        self.assertTrue(live.exists())
        self.assertFalse(orphan.exists())
        self.assertFalse(orphan2.exists())

    def test_vacuum_keeps_non_cache_attachments(self):
        normal = self.env['ir.attachment'].create({
            'name': 'normal.txt', 'res_model': 'res.partner', 'res_id': 2_000_000_000, 'raw': b'hello',
        })
        self.env['ir.attachment']._webp_vacuum()
        self.assertTrue(normal.exists())

    def test_vacuum_after_real_cache_and_record_deleted(self):
        tmp = self.env['res.partner'].create({
            'name': 'WebP Temp', 'image_1920': base64.b64encode(make_image()),
        })
        self.stream(tmp)
        cache = self.caches(self.website, tmp)
        self.assertEqual(len(cache), 1)
        self.env.cr.execute('DELETE FROM res_partner WHERE id=%s', [tmp.id])
        self.env.invalidate_all()
        self.env['ir.attachment']._webp_vacuum()
        self.assertFalse(cache.exists())

    def test_vacuum_ignores_unknown_model(self):
        att = self.env['ir.attachment'].create({
            'name': f'{WEBP_CACHE_PREFIX}w1:x:0x0:1:q85', 'res_model': 'no.such.model', 'res_id': 5,
            'raw': b'x', 'mimetype': 'image/webp',
        })
        self.env['ir.attachment']._webp_vacuum()
        self.assertTrue(att.exists())


class TestWebpSettings(WebpCommon):

    def _settings(self, website=None):
        return self.env['res.config.settings'].create({'website_id': (website or self.website).id})

    def test_action_clear_webp_cache(self):
        self.stream(website=self.website)
        self.stream(website=self.website_b)
        res = self._settings().action_clear_webp_cache()
        self.assertFalse(self.caches(self.website))
        self.assertEqual(len(self.caches(self.website_b)), 1)
        self.assertEqual(res['tag'], 'display_notification')
        self.assertEqual(res['params']['type'], 'success')
        self.assertIn(self.website.name, res['params']['message'])

    def test_action_test_python_webp_success(self):
        res = self._settings().action_test_python_webp()
        self.assertEqual(res['params']['type'], 'success')
        self.assertFalse(res['params']['sticky'])

    def test_action_test_python_webp_failure(self):
        with patch('PIL.Image.Image.save', side_effect=KeyError('WEBP')):
            res = self._settings().action_test_python_webp()
        self.assertEqual(res['params']['type'], 'danger')
        self.assertTrue(res['params']['sticky'])

    def _response(self, content, content_type, code=200):
        return SimpleNamespace(content=content, status_code=code, headers={'Content-Type': content_type})

    def test_action_test_webp_success(self):
        webp = make_image('WEBP', (4, 4))
        with patch(f'{ICFG}.requests.get', return_value=self._response(webp, 'image/webp')) as get:
            res = self._settings().action_test_webp()
        self.assertEqual(res['params']['type'], 'success')
        self.assertEqual(get.call_args.kwargs['headers']['Accept'].split(',')[0], 'image/webp')
        self.assertIn(f'/web/image/res.company/{self.website.company_id.id}/logo', get.call_args.args[0])

    def test_action_test_webp_failure_png(self):
        with patch(f'{ICFG}.requests.get', return_value=self._response(make_image(), 'image/png')):
            res = self._settings().action_test_webp()
        self.assertEqual(res['params']['type'], 'danger')

    def test_action_test_webp_bad_magic(self):
        with patch(f'{ICFG}.requests.get', return_value=self._response(b'not riff at all', 'image/webp')):
            res = self._settings().action_test_webp()
        self.assertEqual(res['params']['type'], 'danger')

    def test_action_test_webp_network_error(self):
        with patch(f'{ICFG}.requests.get', side_effect=requests.ConnectionError('down')), \
                self.assertRaises(UserError):
            self._settings().action_test_webp()

    def test_action_test_webp_disabled_site(self):
        self.website.auto_webp = False
        with self.assertRaises(UserError):
            self._settings().action_test_webp()
