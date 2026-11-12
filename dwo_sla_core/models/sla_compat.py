# -*- coding: utf-8 -*-
"""Backport (Odoo 17) of two helpers that Odoo 19 has in the core.

- `ir.cron._commit_progress(processed, remaining=)`: commit and return the seconds left before the
  cron run is stopped (Odoo 17 has no cron progress records at all).
- `Model.try_lock_for_update(limit=)`: lock rows with `FOR UPDATE SKIP LOCKED`, skipping the
  rows that another transaction holds (defined here on `sla.task`, the only model that needs it).
Both keep the Odoo 19 names so that the engine code and the tests are the same in every version.
"""
import time

from odoo import models
from odoo.tools import config


class IrCron(models.Model):
    _inherit = 'ir.cron'

    def _commit_progress(self, processed=0, *, remaining=None, deactivate=False):
        """Commit and return the seconds left in the cron run (inf if unknown).

        Odoo 17 has neither `ir.cron.progress` nor `_notify_progress`: the caller stamps the start of
        its run in the context (`dwo_sla_started`, a `time.monotonic()` value) and the budget is the
        server limit for cron threads.
        """
        self.env.cr.commit()
        started = self.env.context.get('dwo_sla_started')
        limit = config['limit_time_real_cron'] or config['limit_time_real']
        if not started or not limit or limit < 0:
            return float('inf')
        # keep a margin: the server kills the run at the limit
        return max(limit * 0.8 - (time.monotonic() - started), 0)


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
