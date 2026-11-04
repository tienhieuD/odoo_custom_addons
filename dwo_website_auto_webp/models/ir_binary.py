import base64
import io
import logging

from PIL import Image, WebPImagePlugin  # noqa: F401 — force WebP encoder registration

from odoo import models
from odoo.http import Stream, request

_logger = logging.getLogger(__name__)

_DEFAULT_QUALITY = 85

# Cache key prefix — dùng để search/vacuum toàn bộ cache entries
WEBP_CACHE_PREFIX = 'webp_cache:'

_WEBP_SUPPORTED = None  # None = chưa check, lazy init lần đầu request


def _check_webp_encode():
    """Test thực tế encode WebP — chạy lazy (lần đầu có request) để tránh Pillow chưa init xong."""
    try:
        out = io.BytesIO()
        Image.new('RGB', (1, 1)).save(out, format='WEBP')
        result = len(out.getvalue()) > 0
        if result:
            _logger.info('dwo_website_auto_webp: WebP encode OK')
        else:
            _logger.warning('dwo_website_auto_webp: WebP encode output rỗng')
        return result
    except Exception as e:
        _logger.warning(
            'dwo_website_auto_webp: WebP encode không hoạt động (%s). '
            'Chạy: apt install -y libwebp-dev && pip install --force-reinstall --no-binary Pillow Pillow',
            e,
        )
        return False


class IrBinary(models.AbstractModel):
    _inherit = 'ir.binary'

    def _get_image_stream_from(self, record, field_name='raw', **kwargs):
        """
        Override ir.binary._get_image_stream_from để tự động serve WebP cho browser hỗ trợ.

        Flow:
          1. Lazy check Pillow WebP encode support (lần đầu tiên có request).
          2. Kiểm tra browser có support WebP không (Accept header).
          3. Lấy website hiện tại → kiểm tra auto_webp, lấy website_id + webp_quality.
          4. Tìm WebP đã cache trong ir.attachment (res_model=record._name, res_id=record.id):
             - Cache hit  → trả về ngay, super() KHÔNG được gọi.
             - Cache miss → gọi super() để fetch ảnh gốc và resize.
          5. Convert ảnh đã resize sang WebP với quality từ website config.
          6. Lưu WebP vào ir.attachment cache.
          7. Trả WebP stream.

        Cache key format: webp_cache:w{website_id}:{field}:{w}x{h}:{write_date_ts}:q{quality}
        — website_id trong key cho phép mỗi website có cache riêng với quality riêng.
        — Đổi quality trên website X chỉ invalidate cache của website X, không ảnh hưởng website khác.
        """
        try:
            return self._webp_process(record, field_name, **kwargs)
        except Exception:
            _logger.warning('dwo_website_auto_webp: unexpected error, fallback to original', exc_info=True)
            return super()._get_image_stream_from(record, field_name, **kwargs)

    def _webp_process(self, record, field_name, **kwargs):
        global _WEBP_SUPPORTED

        # [1] Lazy check Pillow WebP encode support
        if _WEBP_SUPPORTED is None:
            _WEBP_SUPPORTED = _check_webp_encode()
        if not _WEBP_SUPPORTED:
            return super()._get_image_stream_from(record, field_name, **kwargs)

        # [2] Browser không support WebP → bypass
        if not self._webp_browser_supports():
            return super()._get_image_stream_from(record, field_name, **kwargs)

        # [3] Lấy website hiện tại → website_id + quality
        website_id, quality = self._webp_get_website_config()
        if quality is None:
            # auto_webp=False trên website này
            return super()._get_image_stream_from(record, field_name, **kwargs)

        # [4] Tìm cache — key bao gồm website_id để mỗi website có cache riêng
        cache_name = self._webp_cache_key(record, field_name, kwargs, website_id, quality)
        cached = self.env['ir.attachment'].sudo().search([
            ('res_model', '=', record._name),
            ('res_id', '=', record.id),
            ('name', '=', cache_name),
        ], limit=1)
        if cached:
            # Cache hit: không gọi super(), không resize, không convert
            return Stream(
                type='data',
                data=cached.raw,
                mimetype='image/webp',
                etag=cached.checksum,
                last_modified=cached.write_date,
            )

        # [4b] Cache miss: gọi super() để fetch + resize
        stream = super()._get_image_stream_from(record, field_name, **kwargs)

        # [5a] Kiểm tra mimetype (SVG và WebP không convert)
        if not self._webp_is_convertible(stream):
            return stream

        # [5b] Đọc bytes từ stream đã resize
        raw = self._webp_read_stream(stream)
        if not raw:
            return stream

        # [5c] Convert sang WebP với quality của website
        webp = self._webp_convert(raw, quality)
        if not webp:
            return stream

        # [6] Lưu cache với res_model/res_id thật để vacuum tìm được
        try:
            self.env['ir.attachment'].sudo().create([{
                'name': cache_name,
                'res_model': record._name,
                'res_id': record.id,
                'datas': base64.b64encode(webp),
                'mimetype': 'image/webp',
            }])
        except Exception as e:
            _logger.debug('WebP cache save failed: %s', e)

        # [7] Trả WebP stream
        return Stream(
            type='data',
            data=webp,
            mimetype='image/webp',
            last_modified=stream.last_modified,
        )

    def _webp_get_website_config(self):
        """
        Trả về (website_id, quality) từ website hiện tại.
        Trả về (0, None) nếu website tắt auto_webp.
        Trả về (0, _DEFAULT_QUALITY) nếu không có website context.

        website_id = 0 khi không có website context — các request này dùng chung 1 cache bucket,
        tránh tạo cache entries thừa cho cùng 1 ảnh trên nhiều non-website contexts.
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
        """True nếu browser gửi 'image/webp' trong Accept header."""
        try:
            if not request:
                return False
        except RuntimeError:
            return False
        return 'image/webp' in request.httprequest.headers.get('Accept', '')

    def _webp_is_convertible(self, stream):
        """
        True nếu stream là ảnh có thể convert sang WebP.
        Loại trừ: SVG (vector, không convert được), WebP (đã đúng format rồi).
        """
        mimetype = getattr(stream, 'mimetype', None)
        if not mimetype:
            return False
        if mimetype in ('image/webp', 'image/svg+xml'):
            return False
        return mimetype.startswith('image/')

    def _webp_cache_key(self, record, field_name, kwargs, website_id, quality):
        """
        Build cache key từ metadata — không hash bytes, zero CPU overhead.

        Format: webp_cache:w{website_id}:{field}:{w}x{h}:{write_date_ts}:q{quality}

        website_id ở đầu key → search 'webp_cache:w5:%' để clear cache của website 5.
        write_date đảm bảo invalidation khi ảnh gốc được upload lại.
        quality trong key → đổi quality → cache miss → convert lại với quality mới.
        """
        ts = int(record.write_date.timestamp()) if getattr(record, 'write_date', None) else 0
        w = kwargs.get('width', 0)
        h = kwargs.get('height', 0)
        return f'{WEBP_CACHE_PREFIX}w{website_id}:{field_name}:{w}x{h}:{ts}:q{quality}'

    def _webp_read_stream(self, stream):
        """Đọc raw bytes từ stream. Hỗ trợ type 'data' (in-memory) và 'path' (file)."""
        if stream.type == 'data' and stream.data:
            return stream.data
        if stream.type == 'path' and stream.path:
            try:
                with open(stream.path, 'rb') as f:
                    return f.read()
            except OSError:
                pass
        return None

    def _webp_convert(self, raw, quality=_DEFAULT_QUALITY):
        """
        Convert raw bytes ảnh sang WebP bằng Pillow.

        - quality (1-100): lấy từ website config, default 85
        - method=4: tốc độ encode trung bình, nén tốt hơn method 0-3
        - Giữ alpha channel (RGBA) nếu ảnh gốc có transparency (PNG, v.v.)
        """
        try:
            img = Image.open(io.BytesIO(raw))
            if img.mode not in ('RGB', 'RGBA'):
                # Giữ alpha nếu ảnh có transparency, ngược lại convert về RGB
                target_mode = 'RGBA' if (img.mode in ('LA', 'PA') or 'transparency' in img.info) else 'RGB'
                img = img.convert(target_mode)
            out = io.BytesIO()
            img.save(out, format='WEBP', quality=quality, method=4)
            return out.getvalue()
        except Exception as e:
            _logger.warning('WebP conversion error: %s', e, exc_info=True)
            return None
