# -*- coding: utf-8 -*-
"""Upgrade from 19.0.1.x: the badges were fixed in the code, now they are records.

The chips that come with the module are created here, once, so a user who had the badges sees the same
ones (same names, colours and order). The data file has forcecreate="0", so a plain update never creates
them again: a chip the administrator deletes stays deleted.
"""
from odoo import SUPERUSER_ID, api, tools


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    tools.convert_file(
        env, "dwo_chatter_filter", "data/dwo_chatter_filter_data.xml", None,
        mode="init", noupdate=True)
