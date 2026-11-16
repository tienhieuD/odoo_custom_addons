# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
def migrate(cr, version):
    """The engine settings model (``dwo.attpreview.engine.config``) is gone (#66): Odoo removes its model record,
    views and access rules on update but leaves the table behind."""
    cr.execute("DROP TABLE IF EXISTS dwo_attpreview_engine_config CASCADE")
