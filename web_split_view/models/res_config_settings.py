from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    web_split_view_auto = fields.Boolean(
        string="Split view on every list",
        config_parameter='web_split_view.auto_split',
        default=True,
        help="Add a Split mode (list and form side by side) to every window action that has a list and a form view.",
    )
