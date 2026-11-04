import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .webp_helper import WEBP_CACHE_PREFIX

_logger = logging.getLogger(__name__)


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
                raise ValidationError('WebP Quality must be between 1 and 100.')

    def write(self, vals):
        # Remember which websites change config so their cache can be cleared
        changed_ids = self.ids if ('auto_webp' in vals or 'webp_quality' in vals) else []
        res = super(Website, self).write(vals)
        if changed_ids:
            self._webp_clear_cache(changed_ids)
        return res

    def _webp_clear_cache(self, website_ids=None):
        """
        Remove all WebP cache of the given websites.
        Cache key format: webp_cache:w{website_id}:... → LIKE 'webp_cache:w5:' only hits website 5.
        Called when the user changes webp_quality or toggles auto_webp.
        """
        if website_ids is None:
            website_ids = self.ids
        for wid in website_ids:
            prefix = '{}w{}:'.format(WEBP_CACHE_PREFIX, wid)
            orphans = self.env['ir.attachment'].sudo().search([('name', 'like', prefix)])
            count = len(orphans)
            orphans.unlink()
            if count:
                _logger.info('WebP cache cleared for website %d: %d entries removed', wid, count)
