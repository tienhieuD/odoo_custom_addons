# -*- coding: utf-8 -*-
"""Backport (Odoo 16) of two helpers that Odoo 19 has in the core.

- `ir.cron._commit_progress(processed, remaining=)`: commit and return the seconds left before the
  cron run is stopped (Odoo 17 has no cron progress records at all).
- `Model.try_lock_for_update(limit=)`: lock rows with `FOR UPDATE SKIP LOCKED`, skipping the
  rows that another transaction holds (defined here on `sla.task`, the only model that needs it).
Both keep the Odoo 19 names so that the engine code and the tests are the same in every version.
"""
import time

from odoo import api, fields, models
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


class SlaReadGroupMixin(models.AbstractModel):
    """Odoo 16 has the old `read_group`: this gives the models of the module the `_read_group` of 17+.

    `_sla_read_group(domain, groupby, aggregates)` returns a list of tuples: the groupby values first
    (a many2one as a recordset, a date with granularity as a datetime), then the aggregates in
    the order asked: `'__count'`, `'field:sum'`, `'field:avg'`, `'id:array_agg'`.
    """
    _name = 'sla.read.group.mixin'
    _description = "SLA read_group (17+ style) for Odoo 16"

    @api.model
    def _sla_read_group(self, domain, groupby=(), aggregates=()):
        # each aggregate gets its own output name (`agg0`...): 'id' would clash with the group id
        specs = {}
        for i, agg in enumerate(aggregates):
            if agg != '__count':
                name, func = agg.split(':')
                specs[agg] = ('agg%d' % i, '%s:%s(%s)' % ('agg%d' % i, func, name))
        rows = self.read_group(
            domain, [spec for _alias, spec in specs.values()] or ['id:count_distinct'],
            list(groupby), lazy=False)
        result = []
        for row in rows:
            values = []
            for gb in groupby:
                name = gb.split(':')[0]
                value = row.get(gb)
                field = self._fields[name]
                if field.type == 'many2one':
                    value = self.env[field.comodel_name].browse(value[0] if value else [])
                elif ':' in gb and field.type in ('date', 'datetime'):
                    start = (row.get('__range') or {}).get(gb, {}).get('from')
                    if not start:
                        # Odoo 15 and older: no `__range`; the start of the group is the `>=` leaf of `__domain`
                        for leaf in row.get('__domain') or []:
                            if isinstance(leaf, (list, tuple)) and leaf[0] == name and leaf[1] == '>=':
                                start = leaf[2]
                    value = fields.Datetime.to_datetime(start) if start else False
                    if value and field.type == 'datetime':
                        # `__range` is the UTC start of the group; 17+ gives the start in the user's timezone
                        value = fields.Datetime.context_timestamp(self, value).replace(tzinfo=None)
                values.append(value)
            for agg in aggregates:
                if agg == '__count':
                    values.append(row.get('__count', row.get('_count')))
                else:
                    values.append(row.get(specs[agg][0]))
            result.append(tuple(values))
        return result


class SlaDefinitionRG(models.Model):
    _inherit = ['sla.definition', 'sla.read.group.mixin']
    _name = 'sla.definition'


class SlaTaskRG(models.Model):
    _inherit = ['sla.task', 'sla.read.group.mixin']
    _name = 'sla.task'


class SlaEventRG(models.Model):
    _inherit = ['sla.event', 'sla.read.group.mixin']
    _name = 'sla.event'


class IrAutovacuum(models.AbstractModel):
    """Odoo 13 and older have no `@api.autovacuum` (14+): the daily garbage collection of the module is
    called from `ir.autovacuum.power_on`, which the daily cron `base.autovacuum_job` runs."""
    _inherit = 'ir.autovacuum'

    @api.model
    def power_on(self, *args, **kwargs):
        res = super().power_on(*args, **kwargs)
        for model, method in (('sla.event', '_gc_old_events'), ('sla.task', '_gc_orphan_tasks'),
                              ('sla.apply.job', '_gc_old_jobs')):
            getattr(self.env[model], method)()
        return res
