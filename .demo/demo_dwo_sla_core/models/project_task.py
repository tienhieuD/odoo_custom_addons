# -*- coding: utf-8 -*-
from odoo import models


class ProjectTask(models.Model):
    """Demo-only: makes project.task inherit `sla.mixin` to show the SLA button.

    This is not part of the dwo_sla_core that is sold (there is no bridge module, only the user guide, see
    "Smart Button on the Source Record"). It uses the same four lines a customer adds to their own model.
    """
    _name = 'project.task'
    _inherit = ['project.task', 'sla.mixin']
