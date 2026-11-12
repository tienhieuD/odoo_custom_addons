import base64
import io
import os
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import requests
from werkzeug.wrappers import Response
from PIL import Image

from odoo.exceptions import UserError, ValidationError
from odoo.tests import SavepointCase, tagged

from odoo.addons.dwo_website_auto_webp.models.webp_helper import WEBP_CACHE_PREFIX

HELPER = 'odoo.addons.dwo_website_auto_webp.models.webp_helper'
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


def fake_request(accept=ACCEPT_WEBP):
    headers = {'Accept': accept} if accept is not None else {}
    return SimpleNamespace(httprequest=SimpleNamespace(headers=headers))


class WebpCommon(SavepointCase):
    """Odoo 12 (same design as 13/14/15): the module post-processes the response of the /web/image controller
    (dwo.webp.helper._webp_process_response), so the unit tests feed it a werkzeug response."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env['website'].create({'name': 'WebP Test Site A'})
        cls.website_b = cls.env['website'].create({'name': 'WebP Test Site B'})
        cls.png = make_image(noisy=True)
        cls.partner = cls.env['res.partner'].create({'name': 'WebP Test Partner'})
        cls.record = cls.env['ir.attachment'].create({
            'name': 'webp-src.png', 'datas': base64.b64encode(cls.png), 'mimetype': 'image/png', 'public': True,
        })

    # helpers
    def response(self, data=None, mimetype='image/png', etag='e1', status=200):
        resp = Response(self.png if data is None else data, status=status, mimetype=mimetype)
        resp.headers['ETag'] = '"%s"' % etag
        return resp

    def process(self, record=None, website=None, accept=ACCEPT_WEBP, field=None, data=None, mimetype='image/png',
                etag='e1', status=200, response=None, **params):
        """What the controller does after the core built the (resized) response."""
        website = website or self.website
        record = record if record is not None else self.record
        params = dict({'model': record._name, 'id': record.id}, **params)
        if field:
            params['field'] = field
        response = response or self.response(data, mimetype, etag, status)
        helper = self.env['dwo.webp.helper'].with_context(website_id=website.id)
        with patch(f'{HELPER}.request', fake_request(accept) if accept is not False else None):
            return helper._webp_process_response(response, params)

    def caches(self, website=None, record=None):
        domain = [('name', '=like', WEBP_CACHE_PREFIX + (f'w{website.id}:' if website else '') + '%')]
        if record:
            domain += [('res_model', '=', record._name), ('res_id', '=', record.id)]
        return self.env['ir.attachment'].sudo().search(domain)

    def attachment(self, data, mimetype, name='img'):
        return self.env['ir.attachment'].create({
            'name': name, 'datas': base64.b64encode(data), 'mimetype': mimetype, 'public': True,
        })

    def assertWebp(self, resp, size=None):
        self.assertEqual(resp.mimetype, 'image/webp')
        data = resp.get_data()
        self.assertEqual(data[:4], b'RIFF')
        self.assertEqual(data[8:12], b'WEBP')
        img = Image.open(io.BytesIO(data))
        self.assertEqual(img.format, 'WEBP')
        if size:
            self.assertEqual(img.size, size)


class TestWebpResponse(WebpCommon):

    def test_webp_when_accept_has_webp(self):
        r = self.process()
        self.assertWebp(r, (300, 200))
        self.assertEqual(r.headers['Content-Type'], 'image/webp')

    def test_original_when_accept_lacks_webp(self):
        r = self.process(accept='image/png,image/*;q=0.8')
        self.assertEqual(r.mimetype, 'image/png')
        self.assertEqual(r.get_data(), self.png)
        self.assertFalse(self.caches(self.website))

    def test_original_when_no_accept_header(self):
        r = self.process(accept=None)
        self.assertEqual(r.mimetype, 'image/png')
        self.assertFalse(self.caches())

    def test_original_when_no_request(self):
        r = self.process(accept=False)
        self.assertEqual(r.mimetype, 'image/png')
        self.assertFalse(self.caches())

    def test_non_200_response_untouched(self):
        for status in (304, 404):
            with self.subTest(status=status):
                r = self.process(status=status, data=b'')
                self.assertEqual(r.status_code, status)
                self.assertNotEqual(r.mimetype, 'image/webp')
        self.assertFalse(self.caches())

    def test_direct_passthrough_response_untouched(self):
        resp = self.response()
        resp.direct_passthrough = True
        r = self.process(response=resp)
        self.assertEqual(r.mimetype, 'image/png')
        self.assertFalse(self.caches())

    def test_cache_created_once(self):
        self.process()
        cache = self.caches(self.website, self.record)
        self.assertEqual(len(cache), 1)
        self.assertEqual(cache.mimetype, 'image/webp')
        self.assertEqual(cache.name, f'{WEBP_CACHE_PREFIX}w{self.website.id}:datas:0x0:0:e1:q85')
        self.assertWebp(self.response(base64.b64decode(cache.datas), 'image/webp'))

    def test_second_call_uses_cache_without_converting(self):
        first = self.process()
        helper_cls = type(self.env['dwo.webp.helper'])
        with patch.object(helper_cls, '_webp_convert', side_effect=AssertionError('converted twice')):
            second = self.process()
        self.assertEqual(len(self.caches(self.website, self.record)), 1)
        self.assertWebp(second)
        self.assertEqual(first.get_data(), second.get_data())

    def test_cache_filename_includes_size_and_crop(self):
        self.process(width=100, height=100)
        self.process(width=50, height=50)
        self.process(width=50, height=50, crop=True)
        self.process()
        names = self.caches(self.website, self.record).mapped('name')
        self.assertEqual(len(names), 4)
        self.assertTrue(any(':100x100:0:' in n for n in names))
        self.assertTrue(any(':50x50:0:' in n for n in names))
        self.assertTrue(any(':50x50:1:' in n for n in names))

    def test_field_in_cache_key(self):
        self.process(field='image_128')
        self.assertIn(':image_128:', self.caches(self.website, self.record).name)

    def test_quality_change_new_cache_and_smaller_file(self):
        self.website.webp_quality = 95
        big = self.process()
        self.website.webp_quality = 10
        small = self.process()
        self.assertLess(len(small.get_data()), len(big.get_data()))
        self.assertTrue(self.caches(self.website).filtered(lambda c: c.name.endswith(':q10')))

    def test_quality_in_cache_key(self):
        self.website.webp_quality = 70
        self.process()
        self.assertTrue(self.caches(self.website, self.record).name.endswith(':q70'))

    def test_new_etag_new_cache(self):
        """The ETag of the core response changes when the source is re-uploaded: that invalidates the cache."""
        self.process(etag='old')
        new_png = make_image(size=(120, 80), noisy=True)
        r = self.process(etag='new', data=new_png)
        self.assertWebp(r, (120, 80))
        names = self.caches(self.website, self.record).mapped('name')
        self.assertEqual(len(names), 2)
        self.assertTrue(any(':old:' in n for n in names) and any(':new:' in n for n in names))

    def test_two_websites_separate_cache(self):
        self.website.webp_quality = 90
        self.website_b.webp_quality = 20
        a = self.process(website=self.website)
        b = self.process(website=self.website_b)
        self.assertEqual(len(self.caches(self.website)), 1)
        self.assertEqual(len(self.caches(self.website_b)), 1)
        self.assertGreater(len(a.get_data()), len(b.get_data()))

    def test_auto_webp_disabled_returns_original(self):
        self.website.auto_webp = False
        r = self.process()
        self.assertEqual(r.mimetype, 'image/png')
        self.assertFalse(self.caches(self.website))

    def test_auto_webp_disabled_only_for_that_website(self):
        self.website.auto_webp = False
        self.assertWebp(self.process(website=self.website_b))

    def test_svg_not_converted(self):
        svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><rect width="10" height="10"/></svg>'
        att = self.attachment(svg, 'image/svg+xml')
        r = self.process(att, data=svg, mimetype='image/svg+xml')
        self.assertEqual(r.mimetype, 'image/svg+xml')
        self.assertFalse(self.caches(self.website, att))

    def test_gif_not_converted(self):
        gif = make_image('GIF', (20, 20))
        att = self.attachment(gif, 'image/gif')
        r = self.process(att, data=gif, mimetype='image/gif')
        self.assertEqual(r.mimetype, 'image/gif')
        self.assertFalse(self.caches(self.website, att))

    def test_webp_source_not_reconverted(self):
        webp = make_image('WEBP', (20, 20))
        att = self.attachment(webp, 'image/webp')
        r = self.process(att, data=webp, mimetype='image/webp')
        self.assertEqual(r.get_data(), webp)
        self.assertFalse(self.caches(self.website, att))

    def test_jpeg_source_converted(self):
        jpg = make_image('JPEG', (40, 30))
        att = self.attachment(jpg, 'image/jpeg')
        r = self.process(att, data=jpg, mimetype='image/jpeg')
        self.assertWebp(r, (40, 30))
        self.assertEqual(len(self.caches(self.website, att)), 1)

    def test_png_with_alpha_keeps_alpha(self):
        png = make_image('PNG', (30, 30), mode='RGBA')
        att = self.attachment(png, 'image/png')
        r = self.process(att, data=png)
        self.assertEqual(Image.open(io.BytesIO(r.get_data())).mode, 'RGBA')

    def test_palette_png_converted(self):
        png = make_image('PNG', (30, 30), mode='P')
        att = self.attachment(png, 'image/png')
        self.assertWebp(self.process(att, data=png), (30, 30))

    def test_corrupt_image_falls_back_without_error(self):
        att = self.attachment(b'this is definitely not a png', 'image/png')
        r = self.process(att, data=b'this is definitely not a png')
        self.assertEqual(r.mimetype, 'image/png')
        self.assertEqual(r.get_data(), b'this is definitely not a png')
        self.assertFalse(self.caches(self.website, att))

    def test_webp_encoder_missing_falls_back(self):
        with patch(f'{HELPER}._WEBP_SUPPORTED', False):
            r = self.process()
        self.assertEqual(r.mimetype, 'image/png')
        self.assertFalse(self.caches(self.website))

    def test_unknown_record_converts_without_cache(self):
        resp = self.process(self.record, response=self.response(), model='no.such.model')
        self.assertWebp(resp)
        self.assertFalse(self.caches())

    def test_xmlid_resolves_record(self):
        self.env['ir.model.data'].create({
            'name': 'webp_test_img', 'module': 'dwo_website_auto_webp', 'model': 'ir.attachment',
            'res_id': self.record.id,
        })
        helper = self.env['dwo.webp.helper'].with_context(website_id=self.website.id)
        with patch(f'{HELPER}.request', fake_request()):
            r = helper._webp_process_response(
                self.response(), {'xmlid': 'dwo_website_auto_webp.webp_test_img'})
        self.assertWebp(r)
        self.assertEqual(len(self.caches(self.website, self.record)), 1)

    def test_cache_save_failure_still_returns_webp(self):
        attach_cls = type(self.env['ir.attachment'])
        with patch.object(attach_cls, 'create', side_effect=RuntimeError('disk full')):
            r = self.process()
        self.assertWebp(r)

    def test_convert_helper_quality_range(self):
        helper = self.env['dwo.webp.helper']
        raw = make_image(noisy=True, size=(64, 64))
        self.assertLess(len(helper._webp_convert(raw, 1)), len(helper._webp_convert(raw, 100)))
        self.assertIsNone(helper._webp_convert(b'garbage', 80))


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
        self.process(website=self.website)
        self.process(website=self.website_b)
        self.website.webp_quality = 60
        self.assertFalse(self.caches(self.website))
        self.assertEqual(len(self.caches(self.website_b)), 1)

    def test_write_auto_webp_clears_cache(self):
        self.process(website=self.website)
        self.website.auto_webp = False
        self.assertFalse(self.caches(self.website))

    def test_write_other_field_keeps_cache(self):
        self.process(website=self.website)
        self.website.name = 'WebP Renamed'
        self.assertEqual(len(self.caches(self.website)), 1)

    def test_clear_cache_prefix_does_not_hit_other_ids(self):
        """w1: must not match w10:, w11: ... (the prefix includes the trailing colon)."""
        other = self.env['ir.attachment'].create({
            'name': f'{WEBP_CACHE_PREFIX}w{self.website.id}0:image:0x0:1:q85',
            'res_model': 'res.partner', 'res_id': self.partner.id, 'datas': base64.b64encode(b'x'), 'mimetype': 'image/webp',
        })
        self.website._webp_clear_cache()
        self.assertTrue(other.exists())

    def test_get_website_config(self):
        binary = self.env['dwo.webp.helper'].with_context(website_id=self.website.id)
        self.website.webp_quality = 42
        self.assertEqual(binary._webp_get_website_config(), (self.website.id, 42))
        self.website.auto_webp = False
        self.assertEqual(binary._webp_get_website_config(), (0, None))


class TestWebpVacuum(WebpCommon):

    def _cache_for(self, res_id, name_suffix='a'):
        return self.env['ir.attachment'].create({
            'name': f'{WEBP_CACHE_PREFIX}w1:image:0x0:{name_suffix}:q85',
            'res_model': 'res.partner', 'res_id': res_id, 'datas': base64.b64encode(b'RIFF0000WEBP'), 'mimetype': 'image/webp',
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
            'name': 'normal.txt', 'res_model': 'res.partner', 'res_id': 2_000_000_000, 'datas': base64.b64encode(b'hello'),
        })
        self.env['ir.attachment']._webp_vacuum()
        self.assertTrue(normal.exists())

    def test_vacuum_after_real_cache_and_record_deleted(self):
        tmp = self.env['res.partner'].create({
            'name': 'WebP Temp', 'image': base64.b64encode(make_image()).decode(),
        })
        self.process(tmp, field='image')
        cache = self.caches(self.website, tmp)
        self.assertEqual(len(cache), 1)
        self.env.cr.execute('DELETE FROM res_partner WHERE id=%s', [tmp.id])
        self.env['res.partner'].invalidate_cache()
        self.env['ir.attachment'].invalidate_cache()
        self.env['ir.attachment']._webp_vacuum()
        self.assertFalse(cache.exists())

    def test_autovacuum_power_on_runs_webp_vacuum(self):
        """Odoo 13 has no @api.autovacuum: the module hooks ir.autovacuum.power_on."""
        attach_cls = type(self.env['ir.attachment'])
        # the core power_on commits (it would drop the test savepoint): stub it
        with patch('odoo.addons.base.models.ir_autovacuum.AutoVacuum.power_on', return_value='core'), \
                patch.object(attach_cls, '_webp_vacuum', autospec=True) as vac:
            res = self.env['ir.autovacuum'].power_on()
        self.assertEqual(res, 'core')
        vac.assert_called_once()

    def test_vacuum_ignores_unknown_model(self):
        att = self.env['ir.attachment'].create({
            'name': f'{WEBP_CACHE_PREFIX}w1:x:0x0:1:q85', 'res_model': 'res.partner', 'res_id': 5,
            'datas': base64.b64encode(b'x'), 'mimetype': 'image/webp',
        })
        # Odoo 12 cannot create an attachment on an unknown model (recompute of res_name fails): switch it in SQL
        self.env.cr.execute('UPDATE ir_attachment SET res_model=%s WHERE id=%s', ['no.such.model', att.id])
        att.invalidate_cache()
        self.env['ir.attachment']._webp_vacuum()
        self.assertTrue(att.exists())


class TestWebpSettings(WebpCommon):

    def notice(self, res):
        """Odoo 12 has no display_notification: the result is a dialog on dwo.webp.test.result."""
        self.assertEqual(res['type'], 'ir.actions.act_window')
        rec = self.env['dwo.webp.test.result'].browse(res['res_id'])
        return {'type': 'success' if rec.success else 'danger', 'message': rec.message, 'title': rec.title}

    def _settings(self, website=None):
        return self.env['res.config.settings'].create({'website_id': (website or self.website).id})

    def test_action_clear_webp_cache(self):
        self.process(website=self.website)
        self.process(website=self.website_b)
        res = self._settings().action_clear_webp_cache()
        self.assertFalse(self.caches(self.website))
        self.assertEqual(len(self.caches(self.website_b)), 1)
        self.assertEqual(res['res_model'], 'dwo.webp.test.result')
        self.assertEqual(res['target'], 'new')
        self.assertEqual(self.notice(res)['type'], 'success')
        self.assertIn(self.website.name, self.notice(res)['message'])

    def test_action_test_python_webp_success(self):
        res = self._settings().action_test_python_webp()
        self.assertEqual(self.notice(res)['type'], 'success')

    def test_action_test_python_webp_failure(self):
        with patch('PIL.Image.Image.save', side_effect=KeyError('WEBP')):
            res = self._settings().action_test_python_webp()
        self.assertEqual(self.notice(res)['type'], 'danger')

    def _response(self, content, content_type, code=200):
        return SimpleNamespace(content=content, status_code=code, headers={'Content-Type': content_type})

    def test_action_test_webp_success(self):
        webp = make_image('WEBP', (4, 4))
        with patch(f'{ICFG}.requests.get', return_value=self._response(webp, 'image/webp')) as get:
            res = self._settings().action_test_webp()
        self.assertEqual(self.notice(res)['type'], 'success')
        self.assertEqual(get.call_args.kwargs['headers']['Accept'].split(',')[0], 'image/webp')
        self.assertIn(f'/web/image/res.company/{self.website.company_id.id}/logo', get.call_args.args[0])

    def test_action_test_webp_failure_png(self):
        with patch(f'{ICFG}.requests.get', return_value=self._response(make_image(), 'image/png')):
            res = self._settings().action_test_webp()
        self.assertEqual(self.notice(res)['type'], 'danger')

    def test_action_test_webp_bad_magic(self):
        with patch(f'{ICFG}.requests.get', return_value=self._response(b'not riff at all', 'image/webp')):
            res = self._settings().action_test_webp()
        self.assertEqual(self.notice(res)['type'], 'danger')

    def test_action_test_webp_network_error(self):
        with patch(f'{ICFG}.requests.get', side_effect=requests.ConnectionError('down')), \
                self.assertRaises(UserError):
            self._settings().action_test_webp()

    def test_action_test_webp_disabled_site(self):
        self.website.auto_webp = False
        with self.assertRaises(UserError):
            self._settings().action_test_webp()
