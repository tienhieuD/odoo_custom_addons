# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from . import models
from . import controllers


def uninstall_hook(env):
    """Remove the settings and the uploaded images of the module when it is uninstalled."""
    env["ir.config_parameter"].sudo().search([("key", "=like", "dwo_login.%")]).unlink()
    env["ir.attachment"].sudo().search([("res_model", "=", "dwo.login.theme")]).unlink()
