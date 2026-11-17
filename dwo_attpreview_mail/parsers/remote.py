# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
"""The image proxy now lives in the core module (Text previews use it too): this name stays for the Mail code and
tests. It is the same module object, so patching ``parsers.remote.X`` patches the real one."""
import sys

from odoo.addons.dwo_attpreview_core import remote_image

sys.modules[__name__] = remote_image
