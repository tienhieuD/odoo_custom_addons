from lxml import etree

from odoo import _, api, fields, models

AUTO_PARAM = 'web_split_view.auto_split'

class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_id_by_xmlid(self, xml_id):
        _, res_id = self.env['ir.model.data'].sudo()._xmlid_to_res_model_res_id(xml_id)
        return res_id

    @api.model
    def _get_default_split_view(self):
        """Default split view of any model: ``<split/>``. The client builds it from the list, form and search
        views of the action it is opened from."""
        return etree.Element('split')

class View(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('split', "Split")])

class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[('split', "Split")], ondelete={'split': 'cascade'})

class ActWindow(models.Model):
    _inherit = 'ir.actions.act_window'

    no_split_view = fields.Boolean(
        string="No split view",
        help="Do not offer the automatic split view (list + form side by side) for this action.",
    )

    @api.depends('no_split_view')
    def _compute_views(self):
        """Offer the "Split" mode on every window action that has a list and a form view.

        The split view is derived from the action itself (its list, form and search views): there is no
        view record to create. It is added right after the list view, so the default view of the action
        does not change. Actions that already declare a ``split`` view are left alone.
        """
        super()._compute_views()
        if self.env['ir.config_parameter'].sudo().get_param(AUTO_PARAM, 'True') != 'True':
            return
        registry = self.env.registry
        for act in self:
            if act.no_split_view or act.target == 'new' or not act.res_model:
                continue
            model = registry.get(act.res_model)
            if model is None or model._transient or act.res_model == 'res.config.settings':
                continue
            types = [view_type for _view_id, view_type in act.views]
            if 'tree' not in types or 'form' not in types or 'split' in types:
                continue
            position = types.index('tree') + 1
            act.views = act.views[:position] + [(False, 'split')] + act.views[position:]


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    web_split_view_auto = fields.Boolean(
        string="Split view on every list",
        config_parameter=AUTO_PARAM,
        default=True,
        help="Add a Split mode (list and form side by side) to every window action that has a list and a form view.",
    )


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