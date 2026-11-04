from odoo import api, models


class IrAutovacuum(models.AbstractModel):
    _inherit = 'ir.autovacuum'

    @api.model
    def power_on(self, *args, **kwargs):
        res = super(IrAutovacuum, self).power_on(*args, **kwargs)
        self.env['ir.attachment']._webp_vacuum()
        return res
