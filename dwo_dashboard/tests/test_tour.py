# -*- coding: utf-8 -*-
from odoo.tests import HttpCase, tagged

URL = "/odoo/action-dwo_dashboard.action_dwo_dashboard"


@tagged("post_install", "-at_install")
class TestDashboardTour(HttpCase):
    """The main flow in a real browser: open, add a KPI and a chart with Explore, save, reload, add a page."""

    def setUp(self):
        super().setUp()
        self.env["res.users"].create({
            "name": "Tour Tina", "login": "dash_tour", "password": "dash_tour",
            "group_ids": [(6, 0, [self.env.ref("base.group_user").id])]})

    def page(self):
        user = self.env["res.users"].search([("login", "=", "dash_tour")])
        return self.env["dwo.dashboard.page"].sudo().search([("user_id", "=", user.id)], order="id", limit=1)

    def test_main_flow(self):
        self.start_tour(URL, "dwo_dashboard_tour", login="dash_tour")
        page = self.page()
        self.assertEqual([w["id"] for w in page.spec["widgets"]], ["w1", "w2"])
        saved_once = page.revision
        self.start_tour(URL, "dwo_dashboard_tour_reload", login="dash_tour")
        page.invalidate_recordset()
        self.assertEqual(page.revision, saved_once + 1)  # the resize was saved...
        self.assertEqual(next(w for w in page.spec["widgets"] if w["id"] == "w1")["w"], 8)
        self.start_tour(URL, "dwo_dashboard_tour_persist", login="dash_tour")
        page.invalidate_recordset()
        self.assertEqual(page.revision, saved_once + 1)  # ...and Edit then Done changed nothing
