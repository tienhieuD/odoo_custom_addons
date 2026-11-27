# -*- coding: utf-8 -*-
"""A model of several tables (a blend) is now also edited as lines: write the lines of the blends that exist (their document is
kept as it is: nothing is rebuilt from the lines until someone edits them)."""
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["dwo.dataset"].search([("kind", "=", "blend")])._sync_from_document()
