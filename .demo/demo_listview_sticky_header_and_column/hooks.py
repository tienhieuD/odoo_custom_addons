# -*- coding: utf-8 -*-
"""Inserts the sample rows of the lab (the tables are real and editable, see models/models.py)."""


def post_init_hook(env):
    for model in ['lshc.test.category', 'lshc.test.tag', 'lshc.test.record', 'lshc.test.line']:
        env[model]._seed()
