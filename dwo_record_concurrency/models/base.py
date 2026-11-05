from odoo import models


class BaseModel(models.AbstractModel):
    _inherit = "base"

    def write(self, vals):
        """After a successful write, tell the clients that watch this record that the fields they may be
        editing have changed. Nothing is ever refused here: the detection is soft by design.

        The notification carries *names only*, never values: a client re-reads through the ORM, so its own
        access rights apply.
        """
        res = super().write(vals)
        pool = self.pool
        if 'dwo.model.concurrency' in pool and self._name in pool and not self._abstract and not self._transient \
                and not self.env.context.get('dwo_skip_concurrency'):
            watched = self.env['dwo.model.concurrency']._get_watched_field_names(self._name)
            if watched:
                changed = [name for name in watched if name in vals]
                if changed:
                    for rec in self:
                        self.env['dwo.record.presence'].publish_presence(
                            model=self._name, res_id=rec.id, state='stale', fields=changed)
        return res
