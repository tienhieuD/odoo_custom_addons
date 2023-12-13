# -*- coding: utf-8 -*-
from . import models

from odoo import api, SUPERUSER_ID

def _uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['create.view.split.wizard'].remove_split_view_from_action_window()
