# -*- coding: utf-8 -*-
from odoo import models


class ProjectTask(models.Model):
    """Demo-only: cho project.task kế thừa `sla.mixin` để chụp ảnh nút SLA.

    Logic: module này KHÔNG phải một phần của dwo_sla_core bán ra (quyết
    định của user: không ship bridge module, chỉ hướng dẫn trong docs,
    xem 070_User-Guide.md "Smart Button on the Source Record"); đây chỉ là
    bản demo nội bộ để lấy screenshot/kiểm tra thật, dùng đúng công thức
    4 dòng mà user sẽ tự làm trên model của họ.
    """
    _name = 'project.task'
    _inherit = ['project.task', 'sla.mixin']
