from odoo import fields, models


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('split', "Split")])

    def _get_view_info(self):
        # registers the "split" view type (icon of the view switcher) for the web client
        return {**super()._get_view_info(), 'split': {'icon': 'fa fa-columns'}}
