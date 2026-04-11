from odoo import models, tools, _


class BaseModel(models.AbstractModel):
    _inherit = "base"

    def write(self, vals):
        """
        @override
        1. Check the current model is setting for concurrency
        2. Filter the model fields in vals which is setting for concurrency
        3. If model is setting for concurrency, and field is setting for concurrency,
           send bus to mark record isStale = True
        """
        res = super().write(vals)
        if model_concurrency := self._is_setting_for_concurrency():
            if fields_concurrency := self._is_field_setting_for_concurrency(model_concurrency, vals):
                self._send_bus_to_mark_record_is_stale(fields_concurrency)
        return res

    def _is_setting_for_concurrency(self):
        return self.env['dwo.model.concurrency'].sudo().search([
            ('model', '=', self._name)
        ], limit=1)

    def _is_field_setting_for_concurrency(self, model_concurrency, vals):
        return model_concurrency.field_ids.filtered(lambda field: field.name in vals)

    def _send_bus_to_mark_record_is_stale(self, fields_concurrency):
        new_vals_list = self.read(fields_concurrency.mapped('name'))
        new_vals_by_id = {
            record_dict['id']: record_dict
            for record_dict in new_vals_list
        }
        for rec in self:
            new_vals = new_vals_by_id[rec.id]
            self.env['dwo.record.presence'].publish_presence(
                model=self._name,
                res_id=rec.id,
                state='stale',
                data=new_vals,
            )