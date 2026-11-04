import base64
import io
import logging

from PIL import Image, WebPImagePlugin  # noqa: F401 — force WebP encoder registration

from odoo import models
from odoo.http import request

_logger = logging.getLogger(__name__)

_DEFAULT_QUALITY = 85

# Cache key prefix — used to search/vacuum all cache entries
WEBP_CACHE_PREFIX = 'webp_cache:'

_WEBP_SUPPORTED = None  # None = not checked yet, lazy init on first request


def _check_webp_encode():
    """Real WebP encode test — lazy (first request) so Pillow is fully initialised."""
    try:
        out = io.BytesIO()
        Image.new('RGB', (1, 1)).save(out, format='WEBP')
        result = len(out.getvalue()) > 0
        if result:
            _logger.info('dwo_website_auto_webp: WebP encode OK')
        else:
            _logger.warning('dwo_website_auto_webp: WebP encode output is empty')
        return result
    except Exception as e:
        _logger.warning(
            'dwo_website_auto_webp: WebP encode does not work (%s). '
            'Run: apt install -y libwebp-dev && pip install --force-reinstall Pillow', e,
        )
        return False


class WebpHelper(models.AbstractModel):
    _name = 'dwo.webp.helper'
    _description = 'Auto WebP helper'

    def _webp_process_response(self, response, params):
        """
        Convert a /web/image werkzeug response to WebP.

        Flow:
          1. Lazy check Pillow WebP encode support.
          2. Only touch plain 200 image responses (not SVG / WebP) when the browser sends Accept: image/webp.
          3. Read website config (auto_webp on/off, quality).
          4. Look for a cached WebP in ir.attachment (res_model/res_id of the source record).
          5. Cache miss: convert with Pillow and store the result in ir.attachment.
          6. Replace the response body and Content-Type, keep the original ETag so 304 handling still works.
        """
        global _WEBP_SUPPORTED
        if _WEBP_SUPPORTED is None:
            _WEBP_SUPPORTED = _check_webp_encode()
        if not _WEBP_SUPPORTED:
            return response
        if response.status_code != 200 or getattr(response, 'direct_passthrough', False):
            return response
        if not self._webp_browser_supports():
            return response
        if not self._webp_is_convertible(response.mimetype):
            return response

        website_id, quality = self._webp_get_website_config()
        if quality is None:
            return response  # auto_webp disabled on this website

        raw = response.get_data()
        if not raw:
            return response

        record = self._webp_resolve_record(params)
        cache_name = None
        if record:
            cache_name = self._webp_cache_key(response, params, website_id, quality)
            cached = self.env['ir.attachment'].sudo().search([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id),
                ('name', '=', cache_name),
            ], limit=1)
            if cached and cached.datas:
                return self._webp_set_response(response, base64.b64decode(cached.datas))

        webp = self._webp_convert(raw, quality)
        if not webp:
            return response

        if record:
            try:
                self.env['ir.attachment'].sudo().create({
                    'name': cache_name,
                    'res_model': record._name,
                    'res_id': record.id,
                    'datas': base64.b64encode(webp),
                    'mimetype': 'image/webp',
                })
            except Exception as e:
                _logger.debug('WebP cache save failed: %s', e)
        return self._webp_set_response(response, webp)

    def _webp_set_response(self, response, webp):
        response.set_data(webp)
        response.headers['Content-Type'] = 'image/webp'
        return response

    def _webp_resolve_record(self, params):
        """Source record of the /web/image URL (by xmlid or model+id). None if unknown."""
        try:
            xmlid = params.get('xmlid')
            if xmlid:
                rec = self.env.ref(xmlid, raise_if_not_found=False)
            else:
                model = params.get('model') or 'ir.attachment'
                rec_id = params.get('id')
                if not rec_id or model not in self.env:
                    return None
                rec = self.env[model].sudo().browse(int(rec_id))
            return rec if rec and rec.exists() else None
        except Exception:
            return None

    def _webp_get_website_config(self):
        """
        Return (website_id, quality) from the current website.
        (0, None) if the website disabled auto_webp; (0, default quality) without website context.
        """
        try:
            website = self.env['website'].get_current_website()
            if website and website.exists():
                if not website.auto_webp:
                    return (0, None)
                quality = website.webp_quality or _DEFAULT_QUALITY
                return (website.id, max(1, min(100, quality)))
        except Exception:
            pass
        return (0, _DEFAULT_QUALITY)

    def _webp_browser_supports(self):
        """True if the browser sends 'image/webp' in the Accept header."""
        try:
            if not request:
                return False
        except RuntimeError:
            return False
        return 'image/webp' in request.httprequest.headers.get('Accept', '')

    def _webp_is_convertible(self, mimetype):
        """Skip SVG (vector) and WebP (already the right format)."""
        if not mimetype or mimetype in ('image/webp', 'image/svg+xml'):
            return False
        return mimetype.startswith('image/')

    def _webp_cache_key(self, response, params, website_id, quality):
        """
        webp_cache:w{website_id}:{field}:{w}x{h}:{crop}:{etag}:q{quality}

        - website_id first → 'webp_cache:w5:' clears the cache of website 5 only.
        - the original response ETag changes when the source image is re-uploaded (invalidation).
        - size/crop/quality in the key → each variant is cached separately.
        """
        etag = (response.headers.get('ETag') or '').strip('"')
        return '{}w{}:{}:{}x{}:{}:{}:q{}'.format(
            WEBP_CACHE_PREFIX, website_id, params.get('field') or 'datas',
            params.get('width') or 0, params.get('height') or 0,
            1 if params.get('crop') else 0, etag, quality,
        )

    def _webp_convert(self, raw, quality=_DEFAULT_QUALITY):
        """
        Convert raw image bytes to WebP with Pillow (keeps alpha for PNG etc.).
        quality 1-100 from the website config; method=4 balances speed and compression.
        """
        try:
            img = Image.open(io.BytesIO(raw))
            if img.mode not in ('RGB', 'RGBA'):
                target_mode = 'RGBA' if (img.mode in ('LA', 'PA') or 'transparency' in img.info) else 'RGB'
                img = img.convert(target_mode)
            out = io.BytesIO()
            img.save(out, format='WEBP', quality=quality, method=4)
            return out.getvalue()
        except Exception as e:
            _logger.warning('WebP conversion error: %s', e, exc_info=True)
            return None
