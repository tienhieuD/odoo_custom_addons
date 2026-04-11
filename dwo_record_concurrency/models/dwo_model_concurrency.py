import logging
import json

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class DwoModelConcurrency(models.Model):
    _name = 'dwo.model.concurrency'
    _description = 'Concurrency Model Configuration'
    _rec_name = 'model'

    model_id = fields.Many2one('ir.model', string='Model', index=True)
    model = fields.Char('Technical Model Name', related='model_id.model', readonly=True, store=True, index=True)
    field_ids = fields.Many2many('ir.model.fields', relation='dwo_model_concurrency_field_rel', column1='concurrency_model_id', column2='field_id', string='Fields')
    field_domain = fields.Char(compute='_compute_field_domain')
    active = fields.Boolean(string='Active', default=True, index=True)

    @api.depends('model_id')
    def _compute_field_domain(self):
        for rec in self:
            rec.field_domain = json.dumps([
                ('model', '=', rec.model_id.model),
                ('store', '=', True),
                ('readonly', '=', False),
            ])
