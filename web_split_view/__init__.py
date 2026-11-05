from . import models


def _uninstall_hook(env):
    env['create.view.split.wizard'].remove_split_view_from_action_window()
    # the setting written by Settings > Split View
    env['ir.config_parameter'].sudo().search([('key', '=', 'web_split_view.auto_split')]).unlink()
