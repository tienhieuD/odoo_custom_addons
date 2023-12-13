from odoo import _, api, fields, models

class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_id_by_xmlid(self, xml_id):
        _, res_id = self.env['ir.model.data'].sudo()._xmlid_to_res_model_res_id(xml_id)
        return res_id

class View(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('split', "Split")])

class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[('split', "Split")], ondelete={'split': 'cascade'})

class CreateViewSplitWizard(models.TransientModel):
    _name = 'create.view.split.wizard'
    _description = 'Create a Split View Wizard'

    action_id = fields.Many2one('ir.actions.act_window')
    res_model = fields.Char()
    tree_view_id = fields.Many2one('ir.ui.view')
    form_view_id = fields.Many2one('ir.ui.view')
    tree_view_ref = fields.Char()
    form_view_ref = fields.Char()
    default = fields.Boolean('Make default view')

    @api.onchange('tree_view_id')
    def _onchange_tree_ref(self):
        for rec in self:
            rec.tree_view_ref = self.env['ir.model.data'].sudo().search([
                ('model', '=', 'ir.ui.view'),
                ('res_id', '=', rec.tree_view_id.id),
            ]).complete_name if rec.tree_view_id else False

    @api.onchange('form_view_id')
    def _onchange_form_ref(self):
        for rec in self:
            rec.form_view_ref = self.env['ir.model.data'].sudo().search([
                ('model', '=', 'ir.ui.view'),
                ('res_id', '=', rec.form_view_id.id),
            ]).complete_name if rec.form_view_id else False

    def action_create(self):
        self.ensure_one()

        if 'split' not in self.action_id.view_mode:
            self.action_id.view_mode += ',split'

        split_view = self.env['ir.ui.view'].create({
            'name': self.res_model + '.split.view',
            'type': 'split',
            'model': self.res_model,
            'mode': 'primary',
            'arch_base': f'<split tree_view_ref="{self.tree_view_ref}" form_view_ref="{self.form_view_ref}"/>',
        })

        if self.default:
            self.action_id.view_id = split_view.id
        
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def remove_split_view_from_action_window(self, action_window_id=None):
        if action_window_id:
            act_windows = self.env['ir.actions.act_window'].browse(action_window_id)
        else:
            act_windows = self.env['ir.actions.act_window'].search([('view_mode', 'ilike', 'split')])
        for act in act_windows:
            view_mode_arr = [view_type for view_type in act.view_mode.split(',') if view_type != 'split']
            act.view_mode = ','.join(view_mode_arr)
            act.view_id = False