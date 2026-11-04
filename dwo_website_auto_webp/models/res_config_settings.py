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
        """Xóa toàn bộ WebP cache của website hiện tại."""
        if self.website_id:
            self.website_id._webp_clear_cache()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'WebP Cache Cleared',
                'message': f'All WebP cache for "{self.website_id.name}" has been removed. '
                           f'Images will be re-converted on next request.',
                'type': 'success',
                'sticky': False,
            },
        }

    def action_test_python_webp(self):
        """
        Test cài đặt: chạy Python trong server Odoo — import Pillow + WebP plugin rồi encode thử 1 ảnh 1x1.
        Thành công nghĩa là Pillow có WebP encoder (libwebp).
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
            title, message, notif_type = (
                _('Python Test Failed'),
                _('Pillow cannot encode WebP (%(err)s). See the Installation Guide below.', err=repr(e)),
                'danger',
            )
        else:
            title, message, notif_type = (
                _('Python Test Success'),
                _('Pillow %(ver)s imported and encoded WebP OK (%(size)d bytes).', ver=PIL.__version__, size=size),
                'success',
            )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'title': title, 'message': message, 'type': notif_type, 'sticky': notif_type != 'success'},
        }

    def action_test_webp(self):
        """
        Test WebP có hoạt động không: load thử 1 ảnh qua đường dẫn /web/image (đã được module custom)
        với header Accept: image/webp. Nếu response trả về Content-Type image/webp → test success.

        Ảnh test: logo của company thuộc website hiện tại
        (/web/image/res.company/<id>/logo — mặc định là PNG nên đủ điều kiện convert).
        """
        self.ensure_one()
        website = self.website_id
        if not website:
            raise UserError(_('Please select a website first.'))
        if not website.auto_webp:
            raise UserError(_('Auto WebP Conversion is disabled for this website. Enable and save it before testing.'))

        path = f'/web/image/res.company/{website.company_id.id}/logo'
        # Gọi lại chính server đang phục vụ request hiện tại (đúng host/port), fallback web.base.url
        base_url = request.httprequest.host_url if request else website.get_base_url()
        url = base_url.rstrip('/') + path
        try:
            resp = requests.get(url, headers={'Accept': 'image/webp,image/*;q=0.8'}, timeout=15)
        except requests.RequestException as e:
            raise UserError(_('Cannot load test image %(url)s: %(err)s', url=url, err=e))

        content_type = (resp.headers.get('Content-Type') or '').split(';')[0].strip().lower()
        is_webp = content_type == 'image/webp' and resp.content[:4] == b'RIFF' and resp.content[8:12] == b'WEBP'
        _logger.info('dwo_website_auto_webp test: GET %s -> %s %s (%d bytes)',
                     url, resp.status_code, content_type, len(resp.content))

        if is_webp:
            title, message, notif_type = (
                _('WebP Test Success'),
                _('%(path)s returned image/webp (%(size)d bytes).', path=path, size=len(resp.content)),
                'success',
            )
        else:
            title, message, notif_type = (
                _('WebP Test Failed'),
                _('%(path)s returned "%(ct)s" (HTTP %(code)s) instead of image/webp. '
                  'Check that Pillow has the WebP encoder (see Installation Guide) and see the server log.',
                  path=path, ct=content_type or 'unknown', code=resp.status_code),
                'danger',
            )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'title': title, 'message': message, 'type': notif_type, 'sticky': not is_webp},
        }
