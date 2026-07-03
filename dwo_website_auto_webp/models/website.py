from odoo import api, fields, models
from .ir_binary import WEBP_CACHE_PREFIX


class Website(models.Model):
    _inherit = 'website'

    auto_webp = fields.Boolean(
        string='Auto WebP Conversion',
        default=True,
        help='Automatically convert /web/image responses to WebP for supporting browsers.',
    )
    webp_quality = fields.Integer(
        string='WebP Quality',
        default=85,
        help='WebP encode quality from 1 (smallest file) to 100 (best quality). Default: 85.',
    )

    @api.constrains('webp_quality')
    def _check_webp_quality(self):
        for rec in self:
            if not (1 <= rec.webp_quality <= 100):
                raise models.ValidationError('WebP Quality must be between 1 and 100.')

    def write(self, vals):
        # Lưu website ids trước khi write để biết website nào bị thay đổi config
        changed_ids = self.ids if ('auto_webp' in vals or 'webp_quality' in vals) else []
        res = super().write(vals)
        if changed_ids:
            self._webp_clear_cache(changed_ids)
        return res

    def _webp_clear_cache(self, website_ids=None):
        """
        Xóa toàn bộ WebP cache của các website trong danh sách.

        Cache key format: webp_cache:w{website_id}:...
        → search LIKE 'webp_cache:w5:%' để xóa đúng website, không ảnh hưởng website khác.

        Gọi khi: user đổi webp_quality hoặc toggle auto_webp trong Website Settings.
        """
        if website_ids is None:
            website_ids = self.ids

        for wid in website_ids:
            prefix = f'{WEBP_CACHE_PREFIX}w{wid}:'
            orphans = self.env['ir.attachment'].sudo().search([
                ('name', 'like', prefix),
            ])
            count = len(orphans)
            orphans.unlink()
            if count:
                _logger = __import__('logging').getLogger(__name__)
                _logger.info('WebP cache cleared for website %d: %d entries removed', wid, count)
