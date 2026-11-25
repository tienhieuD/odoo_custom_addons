# -*- coding: utf-8 -*-
import datetime as dt
import json
from collections import Counter
from unittest.mock import patch

from odoo.tests.common import TransactionCase

from ..engine import dates, grouped

TZ = "Asia/Ho_Chi_Minh"  # UTC+7


def kpi(wid="k", model="res.partner", measure=None, **extra):
    return dict({"id": wid, "type": "kpi", "dataset": "orm:" + model,
                 "wells": {"value": measure or {"agg": "count"}}}, **extra)


def bar(axis, legend=None, **extra):
    wells = {"axis": axis, "values": [{"agg": "count"}]}
    if legend:
        wells["legend"] = legend
    return dict({"id": "b", "type": "bar", "dataset": "orm:res.partner", "wells": wells}, **extra)


class EngineCase(TransactionCase):

    def setUp(self):
        super().setUp()
        Users = self.env["res.users"]
        groups = [self.env.ref("base.group_user").id, self.env.ref("base.group_partner_manager").id]
        self.alice = Users.create({"name": "Alice", "login": "eng_alice", "group_ids": [(6, 0, groups)]})
        self.bob = Users.create({"name": "Bob", "login": "eng_bob", "group_ids": [(6, 0, groups)]})
        self.countries = {c: self.env["res.country"].search([("code", "=", c)]).id for c in ("BE", "FR", "DE", "ES", "IT")}

    def run_as(self, user, widget, filters=None, values=None, tz=None):
        env = self.env(user=user, context=dict(self.env.context, tz=tz)) if tz else self.env(user=user)
        return env["dwo.dashboard.engine"].run_preview(widget, filters, values)

    def partners(self, prefix, spread, **extra):
        """{country code: count} -> partners named '<prefix> n' in those countries."""
        Partner = self.env["res.partner"]
        made = Partner
        for code, count in spread.items():
            for i in range(count):
                made |= Partner.create(dict({"name": "%s %s%d" % (prefix, code, i), "country_id": self.countries[code]},
                                            **extra))
        return made

    def value_of(self, response):
        self.assertTrue(response["ok"], response)
        return response["result"]["rows"][0]["values"][0]


class TestViewerPermissions(EngineCase):

    def test_the_same_widget_gives_different_numbers_to_different_people(self):
        """The whole selling point: record rules apply, nothing runs as sudo."""
        self.env["ir.rule"].create({
            "name": "dash test: own partners", "model_id": self.env.ref("base.model_res_partner").id,
            "domain_force": "[('create_uid', '=', user.id)]"})
        Partner = self.env["res.partner"]
        for i in range(3):
            Partner.with_user(self.alice).create({"name": "Mine A%d" % i})
        for i in range(5):
            Partner.with_user(self.bob).create({"name": "Mine B%d" % i})
        widget = kpi(where=[["name", "like", "Mine "]])
        self.assertEqual(self.value_of(self.run_as(self.alice, widget)), 3)
        self.assertEqual(self.value_of(self.run_as(self.bob, widget)), 5)

    def test_a_stored_widget_the_viewer_cannot_read_fails_alone(self):
        """A page saved by somebody with more rights: the viewer gets an error in that widget, the others still run."""
        home = self.env["dwo.dashboard"].with_user(self.alice).get_my_dashboard()["pages"][0]["id"]
        page = self.env["dwo.dashboard.page"].browse(home)
        spec = {"schema": "dwo-dashboard/1", "widgets": [
            dict(kpi("secret", "ir.cron"), x=0, y=0, w=3, h=2), dict(kpi("open"), x=3, y=0, w=3, h=2)]}
        page.sudo().write({"spec": spec})  # system rights allow it; Alice cannot read ir.cron
        Engine = self.env(user=self.alice)["dwo.dashboard.engine"]
        bad = Engine.run_widget(home, "secret")
        self.assertEqual((bad["ok"], bad["error"]["code"]), (False, "access"))
        self.assertTrue(Engine.run_widget(home, "open")["ok"])
        self.assertEqual(Engine.run_widget(home, "ghost")["error"]["code"], "not_found")
        other = self.env["dwo.dashboard"].with_user(self.bob).get_my_dashboard()["pages"][0]["id"]
        self.assertEqual(Engine.run_widget(other, "open")["error"]["code"], "access")  # somebody else's page

    def test_a_preview_is_validated_before_anything_runs(self):
        with patch.object(grouped, "run", side_effect=AssertionError("must not run")):
            response = self.run_as(self.alice, kpi("p", "ir.cron"))
        self.assertEqual((response["ok"], response["error"]["code"]), (False, "access"))
        with patch.object(grouped, "run", side_effect=AssertionError("must not run")):
            response = self.run_as(self.alice, dict(kpi("p"), wells={"value": {"agg": "sum", "field": "name"}}))
        self.assertEqual(response["error"]["code"], "invalid")

    def test_nothing_from_the_client_becomes_a_domain(self):
        filters = [{"id": "c", "type": "relation", "model": "res.country",
                    "bind": [{"dataset": "orm:res.partner", "field": "country_id"}]}]
        self.partners("Inj", {"BE": 2, "FR": 1})
        widget = kpi(where=[["name", "like", "Inj "]])
        for hostile in ("1) OR (1=1", [["id", "!=", 0]], {"$ne": 1}, True, [True, "x"], None):
            self.assertEqual(self.value_of(self.run_as(self.alice, widget, filters, {"c": hostile})), 3, hostile)
        self.assertEqual(self.value_of(self.run_as(self.alice, widget, filters, {"c": [self.countries["BE"]]})), 2)


class TestGrouped(EngineCase):

    def test_top_n_is_exact_with_one_and_with_two_dimensions(self):
        spread = {"BE": 6, "FR": 5, "DE": 4, "ES": 3, "IT": 2}
        made = self.partners("TopN", spread)
        made[:6].write({"is_company": True})  # the six Belgian ones... plus whatever comes first
        where = [["name", "like", "TopN "]]
        one = self.run_as(self.alice, bar({"field": "country_id"}, where=where, limit=3,
                                          order=[{"measure": "__count", "dir": "desc"}]))["result"]
        self.assertEqual([r["labels"][0] for r in one["rows"]], ["Belgium", "France", "Germany"])
        self.assertEqual([r["values"][0] for r in one["rows"]], [6, 5, 4])
        self.assertTrue(one["truncated"]["axis"])
        two = self.run_as(self.alice, bar({"field": "country_id"}, {"field": "is_company"}, where=where, limit=3,
                                          order=[{"measure": "__count", "dir": "desc"}]))["result"]
        truth = Counter()
        for p in made.filtered(lambda p: p.country_id.code in ("BE", "FR", "DE")):
            truth[(p.country_id.name, p.is_company)] += 1
        got = {(r["labels"][0], r["keys"][1]): r["values"][0] for r in two["rows"]}
        self.assertEqual(got, dict(truth))
        self.assertEqual({r["labels"][0] for r in two["rows"]}, {"Belgium", "France", "Germany"})  # nothing else
        self.assertEqual([r["labels"][0] for r in two["rows"]][0], "Belgium")  # axis order of the first pass is kept
        json.dumps(two)

    def test_series_are_capped_and_the_result_says_so(self):
        made = self.partners("Ser", {"BE": 4, "FR": 3})
        made[:2].write({"is_company": True})
        result = self.run_as(self.alice, bar({"field": "country_id"}, {"field": "is_company"},
                                             where=[["name", "like", "Ser "]], series_limit=1))["result"]
        self.assertEqual(len({r["keys"][1] for r in result["rows"]}), 1)
        self.assertTrue(result["truncated"]["series"])

    def test_time_series_in_the_viewers_timezone(self):
        a = self.partners("Tz", {"BE": 1})
        b = self.partners("Tz", {"FR": 1})
        # 2026-11-24 18:00 UTC is 2026-11-25 01:00 in UTC+7; 16:00 UTC is still the 24th there
        self.env.cr.execute("UPDATE res_partner SET create_date = %s WHERE id = %s", ["2026-11-24 18:00:00", a.id])
        self.env.cr.execute("UPDATE res_partner SET create_date = %s WHERE id = %s", ["2026-11-24 16:00:00", b.id])
        self.env.invalidate_all()
        widget = {"id": "d", "type": "line", "dataset": "orm:res.partner",
                  "wells": {"axis": {"field": "create_date", "interval": "day"}, "values": [{"agg": "count"}]},
                  "where": [["name", "like", "Tz "]], "order": [{"field": "create_date", "dir": "asc"}]}
        result = self.run_as(self.alice, widget, tz=TZ)["result"]
        # a day key is the UTC instant at which the viewer's local day starts (it is also what the domain of a drill-down
        # needs): local 24 Nov starts at 23 Nov 17:00 UTC in UTC+7
        self.assertEqual([r["keys"][0] for r in result["rows"]], ["2026-11-23 17:00:00", "2026-11-24 17:00:00"])
        self.assertEqual(["24" in r["labels"][0] for r in result["rows"]], [True, False])
        self.assertIn("25", result["rows"][1]["labels"][0])
        self.assertEqual([r["values"][0] for r in result["rows"]], [1, 1])

    def test_a_legacy_time_zone_name_gives_the_same_buckets_as_the_current_one(self):
        """A browser on macOS reports "Asia/Saigon"; a minimal tzdata no longer has it. Falling back to UTC would shift
        every day, week and month by 7 hours for the viewer: the name is mapped to Asia/Ho_Chi_Minh instead."""
        a, b = self.partners("Zone", {"BE": 1}), self.partners("Zone", {"FR": 1})
        self.env.cr.execute("UPDATE res_partner SET create_date = %s WHERE id = %s", ["2026-11-24 18:00:00", a.id])
        self.env.cr.execute("UPDATE res_partner SET create_date = %s WHERE id = %s", ["2026-11-24 16:00:00", b.id])
        self.env.invalidate_all()
        widget = {"id": "d", "type": "line", "dataset": "orm:res.partner", "where": [["name", "like", "Zone "]],
                  "wells": {"axis": {"field": "create_date", "interval": "day"}, "values": [{"agg": "count"}]},
                  "order": [{"field": "create_date", "dir": "asc"}]}
        current = self.run_as(self.alice, widget, tz="Asia/Ho_Chi_Minh")["result"]
        legacy = self.run_as(self.alice, widget, tz="Asia/Saigon")["result"]
        self.assertEqual(legacy["rows"], current["rows"])
        self.assertEqual(len(current["rows"]), 2)  # the two partners are on two different local days
        self.assertNotIn("notes", legacy)

    def test_an_unknown_time_zone_falls_back_to_utc_and_says_so(self):
        self.partners("Zone", {"BE": 2})
        widget = {"id": "d", "type": "line", "dataset": "orm:res.partner", "where": [["name", "like", "Zone "]],
                  "wells": {"axis": {"field": "create_date", "interval": "month"}, "values": [{"agg": "count"}]}}
        response = self.run_as(self.alice, widget, tz="Not/AZone")
        self.assertTrue(response["ok"], response)
        self.assertEqual(sum(r["values"][0] for r in response["result"]["rows"]), 2)
        self.assertEqual(response["result"]["notes"], ["timezone"])

    def test_a_malformed_payload_is_an_invalid_widget_not_a_traceback(self):
        Engine = self.env(user=self.alice)["dwo.dashboard.engine"]
        for widget, filters in [
            (None, None), ("x", None), ([], None), ({"dataset": 5}, None), (kpi(), "nope"), (kpi(), [None]),
            (kpi(), [{"id": "f"}]), (kpi(), [{"id": "f", "bind": "x"}]), (kpi(), [{"id": "f", "bind": [None]}]),
            (kpi(), [{"id": 5, "bind": []}]), (kpi(), {"a": 1}),
        ]:
            response = Engine.run_preview(widget, filters, "also not a dict")
            self.assertFalse(response["ok"], (widget, filters))
            self.assertIn(response["error"]["code"], ("invalid", "failed"), (widget, filters))
            self.assertNotIn("Traceback", json.dumps(response))

    def test_pivot_totals_come_from_the_database(self):
        made = self.partners("Piv", {"BE": 3, "FR": 2})
        made[:1].write({"is_company": True})
        widget = {"id": "p", "type": "pivot", "dataset": "orm:res.partner", "where": [["name", "like", "Piv "]],
                  "wells": {"rows": [{"field": "country_id"}], "columns": [{"field": "is_company"}],
                            "values": [{"agg": "avg", "field": "id"}, {"agg": "count"}]},
                  "options": {"show_totals": True}}
        result = self.run_as(self.alice, widget)["result"]
        ids = made.ids
        self.assertAlmostEqual(result["totals"]["grand"][0]["values"][0], sum(ids) / len(ids))  # not an average of averages
        self.assertEqual(result["totals"]["grand"][0]["values"][1], 5)
        self.assertEqual(sorted(r["values"][1] for r in result["totals"]["rows"]), [2, 3])
        self.assertEqual(sorted(r["values"][1] for r in result["totals"]["columns"]), [1, 4])

    def test_pie_labels_selection_and_boolean_dimensions(self):
        self.partners("Lab", {"BE": 2}, type="invoice")
        self.partners("Lab2", {"FR": 1}, type="delivery")
        widget = {"id": "pie", "type": "pie", "dataset": "orm:res.partner", "where": [["name", "like", "Lab"]],
                  "wells": {"category": {"field": "type"}, "value": {"agg": "count"}}}
        labels = {r["keys"][0]: r["labels"][0] for r in self.run_as(self.alice, widget)["result"]["rows"]}
        self.assertEqual(labels["invoice"], "Invoice")
        self.assertEqual(labels["delivery"], "Delivery")
        widget["wells"]["category"] = {"field": "is_company"}
        labels = {r["labels"][0] for r in self.run_as(self.alice, widget)["result"]["rows"]}
        self.assertEqual(labels, {"No"})

    def test_a_group_by_through_a_relation(self):
        made = self.partners("Rel", {"BE": 1, "FR": 1})
        child = self.env["res.partner"].create({"name": "Rel child", "parent_id": made[0].id})
        widget = bar({"field": "parent_id.country_id"}, where=[["id", "in", (made | child).ids]])
        rows = self.run_as(self.alice, widget)["result"]["rows"]
        self.assertIn("Belgium", {r["labels"][0] for r in rows})

    def test_context_values_belong_to_the_viewer(self):
        Partner = self.env["res.partner"]
        for i in range(2):
            Partner.with_user(self.alice).create({"name": "Ctx A%d" % i})
        Partner.with_user(self.bob).create({"name": "Ctx B"})
        widget = kpi(where=[["name", "like", "Ctx "], ["create_uid", "=", {"ctx": "uid"}]])
        self.assertEqual(self.value_of(self.run_as(self.alice, widget)), 2)
        self.assertEqual(self.value_of(self.run_as(self.bob, widget)), 1)


class TestFilters(EngineCase):

    def test_date_filter_uses_the_viewers_today(self):
        a, b = self.partners("Df", {"BE": 1}), self.partners("Df", {"FR": 1})
        self.env.cr.execute("UPDATE res_partner SET create_date = %s WHERE id = %s", ["2026-11-24 18:00:00", a.id])
        self.env.cr.execute("UPDATE res_partner SET create_date = %s WHERE id = %s", ["2026-11-24 16:00:00", b.id])
        self.env.invalidate_all()
        filters = [{"id": "d", "type": "date", "default": "today",
                    "bind": [{"dataset": "orm:res.partner", "field": "create_date"}]}]
        widget = kpi(where=[["name", "like", "Df "]])
        with patch.object(dates, "today_in_tz", return_value=dt.date(2026, 11, 25)):
            self.assertEqual(self.value_of(self.run_as(self.alice, widget, filters, tz=TZ)), 1)  # only A
            self.assertEqual(self.value_of(self.run_as(self.alice, widget, filters, {"d": "yesterday"}, tz=TZ)), 1)
            self.assertEqual(self.value_of(self.run_as(self.alice, widget, filters, {"d": "all"}, tz=TZ)), 2)
            self.assertEqual(self.value_of(self.run_as(self.alice, widget, filters, {"d": "bogus"}, tz=TZ)), 1)  # default
            widget["ignore_filters"] = ["d"]
            self.assertEqual(self.value_of(self.run_as(self.alice, widget, filters, tz=TZ)), 2)

    def test_selection_filter_keeps_only_declared_values(self):
        self.partners("Sf", {"BE": 2}, type="invoice")
        self.partners("Sf", {"FR": 1}, type="delivery")
        filters = [{"id": "t", "type": "selection", "values": ["invoice", "contact"],
                    "bind": [{"dataset": "orm:res.partner", "field": "type"}]}]
        widget = kpi(where=[["name", "like", "Sf "]])
        self.assertEqual(self.value_of(self.run_as(self.alice, widget, filters, {"t": ["invoice", "delivery"]})), 2)
        self.assertEqual(self.value_of(self.run_as(self.alice, widget, filters, {"t": ["delivery"]})), 3)  # none valid


class TestPresets(TransactionCase):

    def test_ranges(self):
        d = dt.date
        today = d(2026, 11, 25)  # a Wednesday
        r = dates.preset_range
        self.assertEqual(r("today", today), (d(2026, 11, 25), d(2026, 11, 26)))
        self.assertEqual(r("yesterday", today), (d(2026, 11, 24), d(2026, 11, 25)))
        self.assertEqual(r("last_7_days", today), (d(2026, 11, 19), d(2026, 11, 26)))
        self.assertEqual(r("this_week", today, 0), (d(2026, 11, 23), d(2026, 11, 30)))
        self.assertEqual(r("this_week", today, 6), (d(2026, 11, 22), d(2026, 11, 29)))  # weeks start on Sunday
        self.assertEqual(r("last_week", today, 0), (d(2026, 11, 16), d(2026, 11, 23)))
        self.assertEqual(r("this_month", today), (d(2026, 11, 1), d(2026, 12, 1)))
        self.assertEqual(r("last_month", d(2026, 1, 15)), (d(2025, 12, 1), d(2026, 1, 1)))
        self.assertEqual(r("this_quarter", today), (d(2026, 10, 1), d(2027, 1, 1)))
        self.assertEqual(r("last_quarter", d(2026, 2, 1)), (d(2025, 10, 1), d(2026, 1, 1)))
        self.assertEqual(r("this_year", today), (d(2026, 1, 1), d(2027, 1, 1)))
        self.assertEqual(r("last_year", today), (d(2025, 1, 1), d(2026, 1, 1)))
        self.assertIsNone(r("all", today))
        with self.assertRaises(ValueError):
            r("someday", today)

    def test_midnight_in_the_viewers_timezone_is_stored_in_utc(self):
        self.assertEqual(dates.to_utc(dt.date(2026, 11, 25), TZ), dt.datetime(2026, 11, 24, 17, 0))
        self.assertEqual(dates.to_utc(dt.date(2026, 11, 25), None), dt.datetime(2026, 11, 25, 0, 0))

    def test_today_is_the_viewers_calendar_day(self):
        now = dt.datetime(2026, 11, 24, 18, 0, tzinfo=dates.pytz.utc)
        self.assertEqual(dates.today_in_tz(TZ, now), dt.date(2026, 11, 25))
        self.assertEqual(dates.today_in_tz("UTC", now), dt.date(2026, 11, 24))
        self.assertEqual(dates.today_in_tz("Not/AZone", now), dt.date(2026, 11, 24))


class TestRecords(EngineCase):

    def table(self, **extra):
        return dict({"id": "t", "type": "table", "dataset": "orm:res.partner",
                     "wells": {"columns": [{"field": "name"}, {"field": "country_id"}, {"field": "parent_id.name"},
                                           {"field": "create_date"}, {"field": "is_company"}]}}, **extra)

    def test_columns_paths_order_and_truncation(self):
        made = self.partners("Rec", {"BE": 2, "FR": 1})
        child = self.env["res.partner"].create({"name": "Rec child", "parent_id": made[0].id})
        widget = self.table(where=[["name", "like", "Rec "]], order=[{"field": "name", "dir": "desc"}], limit=2)
        result = self.run_as(self.alice, widget)["result"]
        self.assertEqual(len(result["rows"]), 2)
        self.assertTrue(result["truncated"]["rows"])
        self.assertEqual([r[0] for r in result["rows"]], ["Rec child", "Rec FR0"])
        self.assertEqual(result["rows"][0][2], made[0].name)  # parent_id.name
        self.assertEqual(result["rows"][1][1][1], "France")  # a many2one cell: [id, name]
        self.assertEqual([c["label"] for c in result["columns"]][:2], ["Name", "Country"])
        json.dumps(result)
        self.assertEqual(child.parent_id, made[0])


class TestGuards(EngineCase):

    def test_a_cancelled_query_is_a_widget_error_and_the_transaction_survives(self):
        self.env["ir.config_parameter"].sudo().set_param("dwo_dashboard.query_timeout", "1")

        def slow(env, model, vdef, widget, domain, **kw):
            env.cr.execute("SELECT pg_sleep(3)")

        self.env.cr.execute("SHOW statement_timeout")
        before = self.env.cr.fetchone()[0]
        with patch.object(grouped, "run", slow):
            response = self.run_as(self.alice, kpi())
        self.assertEqual((response["ok"], response["error"]["code"]), (False, "timeout"))
        self.env.cr.execute("SHOW statement_timeout")
        self.assertEqual(self.env.cr.fetchone()[0], before)  # the setting went back with the savepoint
        self.assertTrue(self.run_as(self.alice, kpi())["ok"])  # the same transaction still works

    def test_the_timeout_setting_is_restored_after_a_good_run(self):
        self.env.cr.execute("SHOW statement_timeout")
        before = self.env.cr.fetchone()[0]
        response = self.run_as(self.alice, kpi())
        self.assertTrue(response["ok"], response)
        self.env.cr.execute("SHOW statement_timeout")
        self.assertEqual(self.env.cr.fetchone()[0], before)

    def test_an_unexpected_failure_never_leaks_details(self):
        with patch.object(grouped, "run", side_effect=RuntimeError("SELECT secret FROM hidden")):
            response = self.run_as(self.alice, kpi())
        self.assertEqual(response["error"]["code"], "failed")
        self.assertNotIn("secret", json.dumps(response))

    def test_sql_datasets_are_not_run_yet(self):
        widget = dict(kpi(), dataset="sql:anything")
        response = self.run_as(self.env.ref("base.user_admin"), widget)
        self.assertFalse(response["ok"])
