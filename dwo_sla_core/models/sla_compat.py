# -*- coding: utf-8 -*-
"""Backport (Odoo 18) of two helpers that Odoo 19 has in the core.

- `ir.cron._commit_progress(processed, remaining=)`: save the progress of a cron run, commit,
  and return the seconds left before the cron is stopped (Odoo 18 only has `_notify_progress`).
- `Model.try_lock_for_update(limit=)`: lock rows with `FOR UPDATE SKIP LOCKED`, skipping the
  rows that another transaction holds (defined here on `sla.task`, the only model that needs it).
Both keep the Odoo 19 names so that the engine code and the tests are the same in every version.
"""
from datetime import datetime

from odoo import fields, models
from odoo.tools import config


class IrCron(models.Model):
    _inherit = 'ir.cron'

    def _commit_progress(self, processed=0, *, remaining=None, deactivate=False):
        """Report the progress of the running cron, commit, return the seconds left (inf if unknown)."""
        progress_id = self.env.context.get('ir_cron_progress_id')
        progress = self.env['ir.cron.progress'].sudo().browse(progress_id).exists() if progress_id else None
        if not progress:
            # not called by a cron run: just commit
            self.env.cr.commit()
            return float('inf')
        if remaining is None:
            remaining = max(progress.remaining - processed, 0)
        progress.write({'remaining': remaining, 'done': progress.done + processed})
        if deactivate:
            progress.write({'deactivate': True})
        self.env.cr.commit()
        limit = config['limit_time_real_cron'] or config['limit_time_real']
        if not limit or limit < 0:
            return float('inf')
        elapsed = (fields.Datetime.now() - progress.create_date).total_seconds()
        return max(limit - elapsed, 0)


class SlaTaskLock(models.Model):
    _inherit = 'sla.task'

    def try_lock_for_update(self, *, limit=None):
        """Lock the records (in the order of `self`), skip the locked ones; return the locked recordset."""
        ids = [i for i in self._ids if i]
        if not ids:
            return self
        query = ("SELECT id FROM %s WHERE id IN %%s FOR UPDATE SKIP LOCKED" % self._table)
        self.env.cr.execute(query, [tuple(ids)])
        locked = {row[0] for row in self.env.cr.fetchall()}
        result = [i for i in ids if i in locked]
        if limit is not None:
            result = result[:limit]
        return self.browse(result)
