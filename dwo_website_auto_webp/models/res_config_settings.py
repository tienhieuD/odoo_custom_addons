import logging

import requests

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.http import request

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_webp = fields.Boolean(
        related='website_id.auto_webp',
        readonly=False,
    )
    webp_quality = fields.Integer(
        related='website_id.webp_quality',
        readonly=False,
    )

    def action_clear_webp_cache(self):
        """Remove all WebP cache of the current website."""
        if self.website_id:
            self.website_id._webp_clear_cache()
        return self._webp_notify(
            _('WebP Cache Cleared'),
            _('All WebP cache for "%s" has been removed. Images will be re-converted on next request.')
            % self.website_id.name,
            True,
        )

    def _webp_notify(self, title, message, success):
        """Show a notification in the web client (green on success, sticky red on failure)."""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'title': title, 'message': message,
                       'type': 'success' if success else 'danger', 'sticky': not success},
        }

    def action_test_python_webp(self):
        """
        Install test: run Python inside the Odoo server — import Pillow + WebP plugin and encode a 1x1 image.
        Success means Pillow has the WebP encoder (libwebp).
        """
        self.ensure_one()
        try:
            import io

            import PIL
            from PIL import Image, WebPImagePlugin  # noqa: F401
            out = io.BytesIO()
            Image.new('RGB', (1, 1)).save(out, format='WEBP')
            size = len(out.getvalue())
            if not size:
                raise ValueError('empty WebP output')
        except Exception as e:  # ImportError, KeyError('WEBP'), OSError...
            _logger.warning('dwo_website_auto_webp python test failed: %s', e, exc_info=True)
            return self._webp_notify(
                _('Python Test Failed'),
                _('Pillow cannot encode WebP (%s). See the Installation Guide below.') % repr(e),
                False,
            )
        return self._webp_notify(
            _('Python Test Success'),
            _('Pillow %(ver)s imported and encoded WebP OK (%(size)d bytes).') % {'ver': PIL.__version__, 'size': size},
            True,
        )

    def action_test_webp(self):
        """
        Config test: load a /web/image URL (customised by this module) with Accept: image/webp.
        If the response is WebP → test success.

        Test image: logo of the company of the current website (/web/image/res.company/<id>/logo,
        PNG by default, so it is eligible for conversion).
        """
        self.ensure_one()
        website = self.website_id
        if not website:
            raise UserError(_('Please select a website first.'))
        if not website.auto_webp:
            raise UserError(_('Auto WebP Conversion is disabled for this website. Enable and save it before testing.'))

        path = '/web/image/res.company/%d/logo' % website.company_id.id
        # Call back the server that serves the current request (right host/port), fallback web.base.url
        if request:
            base_url = request.httprequest.host_url
        else:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''
        url = base_url.rstrip('/') + path
        try:
            resp = requests.get(url, headers={'Accept': 'image/webp,image/*;q=0.8'}, timeout=15)
        except requests.RequestException as e:
            raise UserError(_('Cannot load test image %(url)s: %(err)s') % {'url': url, 'err': e})

        content_type = (resp.headers.get('Content-Type') or '').split(';')[0].strip().lower()
        is_webp = content_type == 'image/webp' and resp.content[:4] == b'RIFF' and resp.content[8:12] == b'WEBP'
        _logger.info('dwo_website_auto_webp test: GET %s -> %s %s (%d bytes)',
                     url, resp.status_code, content_type, len(resp.content))

        if is_webp:
            return self._webp_notify(
                _('WebP Test Success'),
                _('%(path)s returned image/webp (%(size)d bytes).') % {'path': path, 'size': len(resp.content)},
                True,
            )
        return self._webp_notify(
            _('WebP Test Failed'),
            _('%(path)s returned "%(ct)s" (HTTP %(code)s) instead of image/webp. '
              'Check that Pillow has the WebP encoder (see Installation Guide) and see the server log.')
            % {'path': path, 'ct': content_type or 'unknown', 'code': resp.status_code},
            False,
        )
