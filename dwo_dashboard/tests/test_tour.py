# -*- coding: utf-8 -*-
import json
from odoo.tests import HttpCase, tagged

URL = "/odoo/action-dwo_dashboard.action_dwo_dashboard"


def widget_by_id(page, wid):
    return next(w for w in page.spec["widgets"] if w["id"] == wid)


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
        self.assertEqual(widget_by_id(page, "w1")["compare"]["field"], "create_date")
        self.assertEqual(widget_by_id(page, "w1")["trend"]["field"], "create_date")
        self.assertEqual(widget_by_id(page, "w1")["icon"], "fa-money")
        self.assertNotIn("icon", widget_by_id(page, "w2"))  # no choice: the card shows the icon of its type
        self.assertEqual(widget_by_id(page, "w1")["title"], "Count · Contact")  # written when the title was left empty
        self.assertEqual(widget_by_id(page, "w2")["title"], "Count by Country")
        date_filter, country_filter = page.spec["filters"]
        self.assertEqual(date_filter["type"], "date")
        self.assertEqual({b["dataset"] for b in date_filter["bind"]}, {"orm:res.partner"})
        self.assertEqual((country_filter["type"], country_filter["model"]), ("relation", "res.country"))
        saved_once = page.revision
        self.start_tour(URL, "dwo_dashboard_tour_reload", login="dash_tour")
        page.invalidate_recordset()
        self.assertEqual(page.revision, saved_once + 1)  # the resize was saved...
        self.assertEqual(next(w for w in page.spec["widgets"] if w["id"] == "w1")["w"], 8)
        pages = self.env["dwo.dashboard.page"].sudo().search([("user_id", "=", page.user_id.id)])
        self.assertEqual(sorted(pages.mapped("name")), ["Home", "Sales"])  # "Ghost" was cancelled
        self.start_tour(URL, "dwo_dashboard_tour_persist", login="dash_tour")
        page.invalidate_recordset()
        self.assertEqual(page.revision, saved_once + 1)  # ...and Edit then Done changed nothing


@tagged("post_install", "-at_install")
class TestShareTour(HttpCase):

    def test_share_and_view(self):
        group = self.env.ref("base.group_user")
        Users = self.env["res.users"]
        owner = Users.create({"name": "Olga Owner", "login": "dash_owner", "password": "dash_owner", "group_ids": [(6, 0, [group.id])]})
        vera = Users.create({"name": "Vera Viewer", "login": "dash_vera", "password": "dash_vera", "group_ids": [(6, 0, [group.id])]})
        self.start_tour(URL, "dwo_share_owner", login="dash_owner")
        page = self.env["dwo.dashboard.page"].sudo().search([("user_id", "=", owner.id)])
        self.assertEqual([(s.user_id, s.level) for s in page.share_ids], [(vera, "view")])
        self.start_tour(URL, "dwo_share_viewer", login="dash_vera")


@tagged("post_install", "-at_install")
class TestInteractTour(HttpCase):

    def test_click_a_pivot_row(self):
        group = self.env.ref("base.group_user")
        user = self.env["res.users"].create({
            "name": "Ivy", "login": "dash_ivy", "password": "dash_ivy",
            "group_ids": [(6, 0, [group.id, self.env.ref("base.group_partner_manager").id])]})
        be, fr = (self.env["res.country"].search([("code", "=", c)]).id for c in ("BE", "FR"))
        for i, country in enumerate([be] * 3 + [fr] * 3):
            self.env["res.partner"].create({"name": "Itour %s%d" % ("BE" if country == be else "FR", i), "country_id": country})
        where = [["name", "like", "Itour "]]
        page = self.env["dwo.dashboard"].with_user(user).get_my_dashboard()["pages"][0]["id"]
        self.env["dwo.dashboard.page"].browse(page).with_user(user).write({"spec": {
            "schema": "dwo-dashboard/1", "grid": {"cols": 12}, "widgets": [
                {"id": "total", "type": "kpi", "dataset": "orm:res.partner", "where": where, "x": 0, "y": 0, "w": 3, "h": 2,
                 "wells": {"value": {"agg": "count"}}},
                {"id": "matrix", "type": "pivot", "dataset": "orm:res.partner", "where": where, "x": 3, "y": 0, "w": 6, "h": 4,
                 "wells": {"rows": [{"field": "country_id"}], "values": [{"agg": "count"}]}}]}})
        self.start_tour(URL, "dwo_interact", login="dash_ivy")


@tagged("post_install", "-at_install")
class TestWideTour(HttpCase):

    def test_a_widget_far_to_the_right_keeps_its_column_and_slides_up(self):
        user = self.env["res.users"].create({"name": "Wade", "login": "dash_wade", "password": "dash_wade",
                                             "group_ids": [(6, 0, [self.env.ref("base.group_user").id])]})
        page_id = self.env["dwo.dashboard"].with_user(user).get_my_dashboard()["pages"][0]["id"]
        page = self.env["dwo.dashboard.page"].browse(page_id).with_user(user)
        page.write({"spec": {"schema": "dwo-dashboard/1", "grid": {"cols": 12}, "widgets": [
            {"id": "total", "type": "kpi", "dataset": "orm:res.partner", "x": 0, "y": 0, "w": 3, "h": 3,
             "wells": {"value": {"agg": "count"}}}]}})
        self.start_tour(URL, "dwo_wide", login="dash_wade")
        page.invalidate_recordset()
        widget = page.spec["widgets"][0]
        self.assertEqual((widget["x"], widget["y"]), (30, 0))  # its column stays; it slides up, nothing is left hanging
        self.assertEqual(page.spec["grid"]["cols"], 33)         # the page grew to its content


@tagged("post_install", "-at_install")
class TestAiTour(HttpCase):

    def test_ask_the_assistant_then_save(self):
        user = self.env["res.users"].create({"name": "Ada", "login": "dash_ada", "password": "dash_ada",
                                             "group_ids": [(6, 0, [self.env.ref("base.group_user").id])]})
        page_id = self.env["dwo.dashboard"].with_user(user).get_my_dashboard()["pages"][0]["id"]
        page = self.env["dwo.dashboard.page"].browse(page_id).with_user(user)
        spec = {"schema": "dwo-dashboard/1", "grid": {"cols": 12}, "widgets": [
            {"id": "total", "type": "kpi", "dataset": "orm:res.partner", "x": 0, "y": 0, "w": 3, "h": 3,
             "wells": {"value": {"agg": "count"}}}]}
        page.write({"spec": spec})
        proposal = dict(spec, widgets=spec["widgets"] + [
            {"id": "w9", "type": "kpi", "title": "Contacts again", "dataset": "orm:res.partner", "x": 3, "y": 0, "w": 3, "h": 3,
             "wells": {"value": {"agg": "count"}}}])

        def answer(model, prompt, history):
            return json.dumps(proposal)
        self.patch(self.env.registry["dwo.dashboard.ai"], "_complete_olg", answer)
        self.start_tour(URL, "dwo_ai", login="dash_ada")
        page.invalidate_recordset()
        self.assertEqual([w["id"] for w in page.spec["widgets"]], ["total", "w9"])


@tagged("post_install", "-at_install")
class TestMetricTour(HttpCase):

    def test_pick_a_metric_on_a_new_widget(self):
        self.env["res.users"].create({"name": "Mel", "login": "dash_mel", "password": "dash_mel",
                                      "group_ids": [(6, 0, [self.env.ref("base.group_user").id])]})
        self.env["dwo.dataset"].create({"model_id": self.env.ref("base.model_res_partner").id, "label": "Contacts",
                                        "metric_ids": [(0, 0, {"name": "companies", "label": "Companies", "agg": "count",
                                                               "where": "[('is_company', '=', True)]"})]})
        self.start_tour(URL, "dwo_metric_pick", login="dash_mel")
        user = self.env["res.users"].search([("login", "=", "dash_mel")])
        page = self.env["dwo.dashboard.page"].sudo().search([("user_id", "=", user.id)], limit=1)
        self.assertEqual(page.spec["widgets"][0]["wells"], {"value": {"metric": "companies"}})
        self.assertEqual(page.spec["widgets"][0]["title"], "Companies · Contact")
