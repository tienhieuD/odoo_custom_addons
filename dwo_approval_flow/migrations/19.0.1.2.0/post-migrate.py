# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Flows made before 1.2.0 get their "Approval history" server action."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["dwo.approval.flow"].with_context(active_test=False).search([])._sync_list_actions()
