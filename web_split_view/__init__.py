# -*- coding: utf-8 -*-
from . import models

from odoo import api, SUPERUSER_ID


def _uninstall_hook(cr, registry):
    """Remove the split mode from the actions that declare it explicitly (the automatic mode needs no cleanup)."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    for act in env['ir.actions.act_window'].search([('view_mode', 'ilike', 'split')]):
        act.view_mode = ','.join(mode for mode in act.view_mode.split(',') if mode != 'split')
        act.view_id = False
    # the setting written by Settings > Split View
    env['ir.config_parameter'].sudo().search([('key', '=', 'web_split_view.auto_split')]).unlink()
