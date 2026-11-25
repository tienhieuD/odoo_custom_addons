# -*- coding: utf-8 -*-
import datetime as dt

from .test_engine import EngineCase, TZ

PREFIX = "Ixt "


class TestInteractions(EngineCase):
    """Cross-filter, drill-down and drill-through: what was clicked comes back as a key, the server writes the conditions."""

    def setUp(self):
        super().setUp()
        self.made = self.partners(PREFIX, {"BE": 3, "FR": 2, "DE": 1})
        # three on the last evening of 2025 in UTC (= 1 January 2026 in Ho Chi Minh City), two in March 2025, one in 2024
        stamps = ["2025-12-31 20:00:00"] * 3 + ["2025-03-10 08:00:00"] * 2 + ["2024-06-01 08:00:00"]
        for partner, stamp in zip(self.made, stamps):
            self.env.cr.execute("UPDATE res_partner SET create_date = %s WHERE id = %s", [stamp, partner.id])
        self.where = [["name", "like", PREFIX]]
        slots = iter(range(0, 12, 3))
        wid = lambda i, t, wells, **kw: dict({"id": i, "type": t, "dataset": "orm:res.partner", "where": self.where,
                                              "x": next(slots), "y": 0, "w": 3, "h": 3, "wells": wells}, **kw)
        self.spec = {"schema": "dwo-dashboard/1", "grid": {"cols": 12}, "widgets": [
            wid("by_country", "bar", {"axis": {"field": "country_id"}, "values": [{"agg": "count"}]},
                order=[{"measure": "__count", "dir": "desc"}], limit=10),
            wid("total", "kpi", {"value": {"agg": "count"}}),
            wid("by_year", "bar", {"axis": {"field": "create_date", "interval": "year"}, "values": [{"agg": "count"}]},
                order=[{"field": "create_date", "dir": "asc"}]),
            {"id": "countries", "type": "kpi", "dataset": "orm:res.country", "x": 0, "y": 3, "w": 3, "h": 3,
             "wells": {"value": {"agg": "count"}}},
        ]}
        self.page = self.env["dwo.dashboard.page"].with_user(self.alice).create({
            "dashboard_id": self.env["dwo.dashboard"].with_user(self.alice).get_my_dashboard()["id"],
            "name": "Ixt", "spec": self.spec})

    def go(self, wid, user=None, interactions=None, tz=TZ):
        env = self.env(user=user or self.alice, context=dict(self.env.context, tz=tz))
        return env["dwo.dashboard.engine"].run_widget(self.page.id, wid, None, interactions)

    def total(self, interactions=None):
        response = self.go("total", interactions=interactions)
        self.assertTrue(response["ok"], response)
        return response["result"]["rows"][0]["values"][0]

    def key_of(self, wid, label_part, interactions=None):
        rows = self.go(wid, interactions=interactions)["result"]["rows"]
        return next(r["keys"][0] for r in rows if label_part in r["labels"][0])

    # ------------------------------------------------------------------------------------ cross-filter
    def test_a_selected_bar_narrows_the_other_widgets(self):
        self.assertEqual(self.total(), 6)
        for code, expected in (("BE", 3), ("FR", 2), ("DE", 1)):
            key = self.countries[code]
            self.assertEqual(self.total({"select": {"widget": "by_country", "key": key}}), expected, code)

    def test_the_source_widget_is_not_narrowed_by_its_own_click(self):
        answer = self.go("by_country", interactions={"select": {"widget": "by_country", "key": self.countries["BE"]}})
        self.assertEqual(len(answer["result"]["rows"]), 3)  # the other bars stay

    def test_a_widget_without_that_field_does_not_take_part(self):
        answer = self.go("countries", interactions={"select": {"widget": "by_country", "key": self.countries["BE"]}})
        self.assertTrue(answer["ok"])
        self.assertEqual(answer["result"]["rows"][0]["values"][0], self.go("countries")["result"]["rows"][0]["values"][0])

    def test_nonsense_is_ignored_and_never_a_traceback(self):
        for select in ({"widget": "by_country", "key": "__other"}, {"widget": "by_country", "key": "x"},
                       {"widget": "by_country", "key": {"a": 1}}, {"widget": "nope", "key": 1}, {"widget": "total", "key": 1},
                       {"widget": "by_country"}, "string", None, {"widget": 5, "key": 1}):
            self.assertEqual(self.total({"select": select}), 6, select)
        for junk in ("x", [], 5, {"drills": "x"}, {"drills": {"by_year": "x"}}, {"drills": {"by_year": [1, {}]}}):
            self.assertTrue(self.go("by_year", interactions=junk)["ok"], junk)

    def test_the_selection_is_checked_as_the_viewer(self):
        self.env["ir.rule"].create({"name": "ixt: only mine", "model_id": self.env.ref("base.model_res_partner").id,
                                    "domain_force": "[('create_uid', '=', user.id)]"})
        denied = self.go("total", user=self.bob)
        self.assertFalse(denied["ok"] and denied["result"]["rows"][0]["values"][0])  # bob does not own the page: access

    # ------------------------------------------------------------------------------------ drill-down
    def test_drilling_a_year_gives_its_quarters_and_then_its_months(self):
        years = self.go("by_year")["result"]
        self.assertEqual([r["labels"][0] for r in years["rows"]], ["2024", "2025", "2026"])  # 1 Jan 2026 in the viewer's zone
        self.assertEqual([r["values"][0] for r in years["rows"]], [1, 2, 3])
        k2025 = self.key_of("by_year", "2025")
        quarters = self.go("by_year", interactions={"drills": {"by_year": [k2025]}})["result"]
        self.assertEqual(quarters["dims"][0]["interval"], "quarter")
        self.assertEqual([(r["labels"][0], r["values"][0]) for r in quarters["rows"]], [("Q1 2025", 2)])
        q1 = quarters["rows"][0]["keys"][0]
        months = self.go("by_year", interactions={"drills": {"by_year": [k2025, q1]}})["result"]
        self.assertEqual(months["dims"][0]["interval"], "month")
        self.assertEqual([(r["labels"][0], r["values"][0]) for r in months["rows"]], [("March 2025", 2)])

    def test_the_last_evening_of_the_year_belongs_to_next_year_in_the_viewers_zone(self):
        k2026 = self.key_of("by_year", "2026")
        quarters = self.go("by_year", interactions={"drills": {"by_year": [k2026]}})["result"]
        self.assertEqual([(r["labels"][0], r["values"][0]) for r in quarters["rows"]], [("Q1 2026", 3)])
        utc = self.go("by_year", tz="UTC")["result"]
        self.assertEqual([(r["labels"][0], r["values"][0]) for r in utc["rows"]], [("2024", 1), ("2025", 5)])

    def test_a_year_selected_in_a_drilled_chart_narrows_the_others_with_the_right_interval(self):
        k2025 = self.key_of("by_year", "2025")
        q1 = self.go("by_year", interactions={"drills": {"by_year": [k2025]}})["result"]["rows"][0]["keys"][0]
        both = {"drills": {"by_year": [k2025]}, "select": {"widget": "by_year", "key": q1}}
        self.assertEqual(self.total(both), 2)  # the quarter, not the year
        self.assertEqual(self.total({"select": {"widget": "by_year", "key": k2025}}), 2)

    # ------------------------------------------------------------------------------------ drill-through
    def drill(self, key, user=None, interactions=None, wid="by_country"):
        env = self.env(user=user or self.alice, context=dict(self.env.context, tz=TZ))
        return env["dwo.dashboard.engine"].drill_records(self.page.id, wid, key, None, interactions)

    def test_the_records_behind_a_bar(self):
        answer = self.drill(self.countries["BE"])
        self.assertTrue(answer["ok"], answer)
        expected = self.made.filtered(lambda p: p.country_id.code == "BE")
        self.assertEqual((answer["result"]["model"], sorted(answer["result"]["ids"]), answer["result"]["total"]),
                         ("res.partner", sorted(expected.ids), 3))

    def test_the_records_behind_a_drilled_bar_follow_the_drill(self):
        k2025 = self.key_of("by_year", "2025")
        q1 = self.go("by_year", interactions={"drills": {"by_year": [k2025]}})["result"]["rows"][0]["keys"][0]
        answer = self.drill(q1, interactions={"drills": {"by_year": [k2025]}}, wid="by_year")
        self.assertEqual(sorted(answer["result"]["ids"]), sorted(self.made[3:5].ids))

    def test_drill_through_obeys_access_and_junk(self):
        self.assertEqual(self.drill(self.countries["BE"], user=self.bob)["error"]["code"], "access")
        for key in ("__other", {"a": 1}, "text", [1]):
            answer = self.drill(key)
            self.assertFalse(answer["ok"] and answer["result"]["ids"], key)
        self.assertEqual(self.drill(1, wid="nope")["error"]["code"], "not_found")
