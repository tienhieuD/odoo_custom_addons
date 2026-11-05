from lxml import etree

from odoo import api, fields, models


class CreateViewSplitWizard(models.TransientModel):
    _name = 'create.view.split.wizard'
    _description = 'Create a Split View Wizard'

    action_id = fields.Many2one('ir.actions.act_window')
    res_model = fields.Char()
    list_view_id = fields.Many2one('ir.ui.view')
    form_view_id = fields.Many2one('ir.ui.view')
    list_view_ref = fields.Char()
    form_view_ref = fields.Char()
    default = fields.Boolean('Make default view')

    def _get_view_xmlid(self, view):
        return view.get_external_id().get(view.id) or False if view else False

    @api.onchange('list_view_id')
    def _onchange_list_view_id(self):
        for rec in self:
            rec.list_view_ref = rec._get_view_xmlid(rec.list_view_id)

    @api.onchange('form_view_id')
    def _onchange_form_view_id(self):
        for rec in self:
            rec.form_view_ref = rec._get_view_xmlid(rec.form_view_id)

    def action_create(self):
        self.ensure_one()
        modes = (self.action_id.view_mode or '').split(',')
        if 'split' not in modes:
            self.action_id.view_mode = ','.join(modes + ['split'])

        arch = etree.Element('split')
        if self.list_view_ref:
            arch.set('list_view_ref', self.list_view_ref)
        if self.form_view_ref:
            arch.set('form_view_ref', self.form_view_ref)

        split_view = self.env['ir.ui.view'].create({
            'name': f'{self.res_model}.split.view',
            'type': 'split',
            'model': self.res_model,
            'mode': 'primary',
            'arch_base': etree.tostring(arch, encoding='unicode'),
        })
        if self.default:
            self.action_id.view_id = split_view.id
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def remove_split_view_from_action_window(self, action_window_id=None):
        domain = [('view_mode', 'ilike', 'split')]
        if action_window_id:
            domain = [('id', '=', action_window_id)]
        for act in self.env['ir.actions.act_window'].search(domain):
            act.view_mode = ','.join(m for m in act.view_mode.split(',') if m != 'split')
            if act.view_id.type == 'split':
                act.view_id = False
