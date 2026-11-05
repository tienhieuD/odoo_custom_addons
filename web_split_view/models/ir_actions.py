from odoo import api, fields, models

AUTO_PARAM = 'web_split_view.auto_split'


class IrActionsActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[('split', "Split")], ondelete={'split': 'cascade'})


class IrActionsActWindow(models.Model):
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
            if 'list' not in types or 'form' not in types or 'split' in types:
                continue
            position = types.index('list') + 1
            act.views = act.views[:position] + [(False, 'split')] + act.views[position:]
