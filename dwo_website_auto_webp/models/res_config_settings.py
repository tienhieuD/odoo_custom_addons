from odoo import fields, models


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
