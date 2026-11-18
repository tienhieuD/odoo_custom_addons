# Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
from . import models
from . import controllers
from . import wizard


def post_init(env):
    from .models.util import post_init as _post_init
    _post_init(env)
