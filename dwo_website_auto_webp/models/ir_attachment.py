import logging

from odoo import api, models

from .webp_helper import WEBP_CACHE_PREFIX

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def _webp_vacuum(self):
        """
        Delete WebP cache attachments whose source record was deleted.

        Cache entries are stored with res_model=record._name, res_id=record.id.
        Called by the daily autovacuum cron.
        """
        self.env.cr.execute("""
            SELECT DISTINCT res_model, res_id
            FROM ir_attachment
            WHERE name LIKE %s
              AND res_id > 0
        """, (WEBP_CACHE_PREFIX + '%',))
        rows = self.env.cr.fetchall()

        deleted_total = 0
        for res_model, res_id in rows:
            if res_model not in self.env:
                continue
            record = self.env[res_model].sudo().browse(res_id)
            if not record.exists():
                orphans = self.sudo().search([
                    ('res_model', '=', res_model),
                    ('res_id', '=', res_id),
                    ('name', 'like', WEBP_CACHE_PREFIX),
                ])
                count = len(orphans)
                orphans.unlink()
                deleted_total += count
                _logger.info('WebP vacuum: deleted %d cache entries for %s(%d)', count, res_model, res_id)

        if deleted_total:
            _logger.info('WebP vacuum: total %d orphan cache entries removed', deleted_total)
