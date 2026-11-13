# -*- coding: utf-8 -*-
"""Tour: mở Overview, bấm thẻ / lát donut / cột và kiểm danh sách đã lọc; JS lỗi làm tour đỏ."""
from odoo.tests import HttpCase, tagged

from .test_dashboard_data import DashboardCase


@tagged('post_install', '-at_install', 'dwo_sla_dashboard', 'dash_tour')
class TestOverviewTour(HttpCase, DashboardCase):

    def setUp(self):
        super().setUp()
        self.Task.sudo().search([]).unlink()
        for days in (2, 5):
            self.mk(self.d_resp, 'on_time', ended_days_ago=days)
        self.mk(self.d_resp, 'late', ended_days_ago=3)
        self.mk(self.d_res, 'breached_open')
        self.mk(self.d_res, 'breached_open')
        self.mk(self.d_res, 'running')

    def test_overview_tour(self):
        self.start_tour('/odoo', 'dwo_sla_overview', login='admin')

    def test_overview_empty(self):
        self.Task.sudo().search([]).unlink()
        self.start_tour('/odoo', 'dwo_sla_overview_empty', login='admin')
