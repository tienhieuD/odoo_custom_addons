# -*- coding: utf-8 -*-
import datetime as dt
import json
from collections import Counter
from unittest.mock import patch

from ..engine import dates
from ..spec import validate_structure
from .test_engine import EngineCase, TZ, kpi
from .test_spec import CORE, page, pairs, widget

D = dt.date
TODAY = D(2026, 11, 25)


def codes(spec):
    return pairs(validate_structure(spec, CORE))


class TestSpecOfTheNewOptions(EngineCase):

    def test_y_axis_bounds(self):
        spec = page()
        bar = widget(spec, "by_country")
        bar["options"] = {"y_min": 0, "y_max": 100.5}
        self.assertFalse({p for p, _c in codes(spec) if "/options" in p})
        bar["options"] = {"y_min": 10, "y_max": 10}
        self.assertIn(("/widgets/2/options/y_min", "constraint"), codes(spec))
        bar["options"] = {"y_min": 5, "y_max": 1}
        self.assertIn(("/widgets/2/options/y_min", "constraint"), codes(spec))
        bar["options"] = {"y_max": "high"}
        self.assertIn(("/widgets/2/options/y_max", "type"), codes(spec))
        spec = page("sales_example")
        widget(spec, "monthly")["options"] = {"percent": True, "y_max": 50}  # a 100% stack has its own axis
        self.assertIn(("/widgets/2/options/y_max", "constraint"), codes(spec))

    def test_a_kpi_trend(self):
        spec = page()
        widget(spec, "total")["trend"] = {"field": "create_date", "interval": "week", "points": 8}
        self.assertNotIn("/widgets/0/trend", {p for p, _c in codes(spec)})
        widget(spec, "total")["trend"] = {"field": "create_date", "interval": "year", "points": 2, "x": 1}
        found = codes(spec)
        self.assertLessEqual({("/widgets/0/trend/interval", "enum"), ("/widgets/0/trend/points", "range"),
                              ("/widgets/0/trend/x", "unknown_key")}, found)
        widget(spec, "by_country")["trend"] = {"field": "create_date"}
        self.assertIn(("/widgets/2/trend", "not_allowed"), codes(spec))

    def test_the_previous_period_over_a_line_or_area_chart(self):
        spec = page()
        line = widget(spec, "by_month")  # axis create_date, one measure, no legend
        line["compare"] = {"field": "create_date", "against": "previous_year"}
        self.assertFalse({p for p, _c in codes(spec) if "compare" in p})
        line["compare"] = {"field": "write_date"}  # not the axis
        self.assertIn(("/widgets/3/compare/field", "constraint"), codes(spec))
        line["compare"] = {"field": "create_date"}
        line["wells"]["values"].append({"agg": "count_distinct", "field": "id"})
        self.assertIn(("/widgets/3/compare/field", "constraint"), codes(spec))  # one measure at a time
        line["wells"]["values"].pop()
        line["wells"]["legend"] = {"field": "type"}
        self.assertIn(("/widgets/3/compare/field", "constraint"), codes(spec))
        widget(spec, "by_country")["compare"] = {"field": "create_date"}  # a bar chart cannot
        self.assertIn(("/widgets/2/compare", "not_allowed"), codes(spec))

    def test_other_on_a_pivot_needs_rows_and_sums(self):
        spec = page()
        pivot = widget(spec, "matrix")
        pivot["options"] = {"other": True}
        self.assertFalse({p for p, c in codes(spec) if c == "constraint"})
        pivot["wells"]["values"] = [{"agg": "avg", "field": "id"}]
        self.assertIn(("/widgets/5/wells/values", "constraint"), codes(spec))
        pivot["wells"]["values"] = [{"agg": "count"}]
        pivot["wells"].pop("rows")
        pivot["wells"]["columns"] = [{"field": "create_date", "interval": "month"}]
        self.assertIn(("/widgets/5/options/other", "constraint"), codes(spec))


class TestKpiTrend(EngineCase):

    def born(self, when, count, prefix="Trd"):
        made = self.partners("%s%s" % (prefix, when[:10].replace("-", "")), {"BE": count})
        self.env.cr.execute("UPDATE res_partner SET create_date = %s WHERE id IN %s", [when, tuple(made.ids)])
        self.env.invalidate_all()

    def setUp(self):
        super().setUp()
        self.born("2026-09-10 10:00:00", 2)
        self.born("2026-11-03 10:00:00", 3)
        self.born("2026-11-20 10:00:00", 4)   # September 2, October none, November 7
        self.born("2026-05-02 10:00:00", 9)   # outside the 4 months shown
        self.where = [["name", "like", "Trd"]]

    def trend(self, filters=None, values=None, **trend):
        widget_ = dict(kpi(where=self.where), trend=dict({"field": "create_date", "interval": "month", "points": 4}, **trend))
        with patch.object(dates, "today_in_tz", return_value=TODAY):
            response = self.run_as(self.alice, widget_, filters, values)
        self.assertTrue(response["ok"], response)
        return response["result"]

    def test_the_last_points_with_zeros_for_the_quiet_months(self):
        result = self.trend()
        points = result["trend"]["points"]
        self.assertEqual([p["value"] for p in points], [0, 2, 0, 7])  # Aug, Sep, Oct, Nov: empty months are zeros
        self.assertEqual(len(points), 4)
        self.assertIn("November", points[-1]["label"])
        self.assertEqual(result["rows"][0]["values"], [18])  # the headline number is unchanged (all of them)
        json.dumps(result)

    def test_weeks_and_days(self):
        weeks = self.trend(interval="week", points=3)["trend"]["points"]
        self.assertEqual(len(weeks), 3)
        self.assertEqual([p["value"] for p in weeks], [0, 4, 0])  # 20 Nov is in the week of 16 Nov; the 3rd is this week
        days = self.trend(interval="day", points=7)["trend"]["points"]
        self.assertEqual([p["value"] for p in days], [0, 4, 0, 0, 0, 0, 0])  # 19 to 25 Nov: the 4 of the 20th

    def test_the_page_date_filter_on_the_same_field_does_not_cut_the_trend(self):
        filters = [{"id": "p", "type": "date", "default": "this_month",
                    "bind": [{"dataset": "orm:res.partner", "field": "create_date"}]}]
        result = self.trend(filters)
        self.assertEqual(result["rows"][0]["values"], [7])  # the number follows the filter...
        self.assertEqual([p["value"] for p in result["trend"]["points"]], [0, 2, 0, 7])  # ...the trend shows the evolution

    def test_another_filter_still_applies_to_the_trend(self):
        self.env.cr.execute("UPDATE res_partner SET write_date = %s WHERE name LIKE 'Trd%%'", ["2026-11-24 10:00:00"])
        self.env.invalidate_all()
        filters = [{"id": "w", "type": "date", "default": "last_year",
                    "bind": [{"dataset": "orm:res.partner", "field": "write_date"}]}]
        result = self.trend(filters)
        self.assertEqual([p["value"] for p in result["trend"]["points"]], [0, 0, 0, 0])

    def test_an_average_has_gaps_not_zeros(self):
        widget_ = dict(kpi(where=self.where), wells={"value": {"agg": "avg", "field": "id"}},
                       trend={"field": "create_date", "interval": "month", "points": 4})
        with patch.object(dates, "today_in_tz", return_value=TODAY):
            points = self.run_as(self.alice, widget_)["result"]["trend"]["points"]
        self.assertIsNone(points[0]["value"])  # nobody in August: no average
        self.assertIsNotNone(points[3]["value"])

    def test_months_are_the_viewers_not_utc(self):
        self.born("2026-10-31 17:30:00", 1, prefix="TrdZ")  # 1 Nov in UTC+7
        widget_ = dict(kpi(where=self.where), trend={"field": "create_date", "interval": "month", "points": 4})
        with patch.object(dates, "today_in_tz", return_value=TODAY):
            utc = self.run_as(self.alice, widget_, tz="UTC")["result"]["trend"]["points"]
            local = self.run_as(self.alice, widget_, tz=TZ)["result"]["trend"]["points"]
        self.assertEqual(local[-1]["value"], utc[-1]["value"] + 1)  # 1 Nov for the viewer, still 31 Oct in UTC
        self.assertEqual(local[-2]["value"], utc[-2]["value"] - 1)


class TestTrendRange(EngineCase):

    def test_ranges(self):
        r = dates.trend_range
        self.assertEqual(r("day", 7, TODAY), (D(2026, 11, 19), D(2026, 11, 26)))
        self.assertEqual(r("week", 3, TODAY, 0), (D(2026, 11, 9), D(2026, 11, 30)))
        self.assertEqual(r("month", 4, TODAY), (D(2026, 8, 1), D(2026, 12, 1)))
        self.assertEqual(r("month", 12, D(2026, 1, 31)), (D(2025, 2, 1), D(2026, 2, 1)))
        with self.assertRaises(ValueError):
            r("year", 3, TODAY)


class TestPreviousPeriodOverTheChart(EngineCase):

    def born(self, when, count, prefix="Ovl"):
        made = self.partners("%s%s" % (prefix, when[:10].replace("-", "")), {"BE": count})
        self.env.cr.execute("UPDATE res_partner SET create_date = %s WHERE id IN %s", [when, tuple(made.ids)])
        self.env.invalidate_all()

    def setUp(self):
        super().setUp()
        for day, n in ((3, 2), (4, 1), (20, 4)):
            self.born("2026-11-%02d 10:00:00" % day, n)        # this month
        for day, n in ((3, 5), (10, 2), (25, 3)):
            self.born("2026-10-%02d 10:00:00" % day, n)        # last month (the 28th is outside the to-date span)
        self.born("2026-10-28 10:00:00", 7)
        self.born("2025-11-04 10:00:00", 6)                    # a year ago
        self.where = [["name", "like", "Ovl"]]

    def chart(self, kind="line", **compare):
        widget_ = {"id": "c", "type": kind, "dataset": "orm:res.partner", "where": self.where,
                   "wells": {"axis": {"field": "create_date", "interval": "day"}, "values": [{"agg": "count"}]},
                   "order": [{"field": "create_date", "dir": "asc"}],
                   "compare": dict({"field": "create_date", "period": "this_month"}, **compare)}
        with patch.object(dates, "today_in_tz", return_value=TODAY):
            response = self.run_as(self.alice, widget_)
        self.assertTrue(response["ok"], response)
        return response["result"]

    def test_the_previous_period_is_aligned_day_by_day_with_zeros_for_quiet_days(self):
        result = self.chart()
        self.assertEqual(len(result["rows"]), 25)  # 1 to 25 Nov: every day, empty ones included
        values = [r["values"][0] for r in result["rows"]]
        self.assertEqual((values[2], values[3], values[19], values[0]), (2, 1, 4, 0))
        c = result["compare"]
        self.assertEqual(len(c["series"]["values"]), 25)
        before = c["series"]["values"]
        self.assertEqual((before[2], before[9], before[24], before[0]), (5, 2, 3, 0))  # the 3rd, 10th, 25th of October
        self.assertEqual(c["range"], ["2026-11-01", "2026-11-26"])
        self.assertEqual(c["fill"]["previous_to"], "2026-10-25")  # the 28th (7 partners) is NOT in the previous span
        self.assertEqual(sum(before), 10)
        json.dumps(result)

    def test_against_the_previous_year(self):
        c = self.chart(against="previous_year")["compare"]
        self.assertEqual(c["series"]["values"][3], 6)  # 4 Nov 2025
        self.assertEqual(sum(v or 0 for v in c["series"]["values"]), 6)

    def test_an_area_chart_too(self):
        self.assertEqual(len(self.chart("area")["rows"]), 25)

    def test_the_labels_of_the_previous_period_are_its_own_days(self):
        c = self.chart()["compare"]
        self.assertEqual(len(c["series"]["labels"]), 25)
        self.assertNotEqual(c["series"]["labels"][0], self.chart()["rows"][0]["labels"][0])  # 1 Oct against 1 Nov


class TestPivotOther(EngineCase):
    """Every row and column adds up to the real total: the beyond-the-limit rows and columns become "Other"."""

    def setUp(self):
        super().setUp()
        self.spread = {"BE": 6, "FR": 5, "DE": 4, "ES": 3, "IT": 2}
        made = self.partners("Pvo", self.spread)
        # alternate is_company so that there are two columns, with a different split in each country
        for i, p in enumerate(made):
            p.is_company = i % 3 == 0
        self.made = made
        self.truth = Counter((p.country_id.name, p.is_company) for p in made)

    def pivot(self, limit=2, series_limit=None, totals=True, columns=True):
        widget_ = {"id": "p", "type": "pivot", "dataset": "orm:res.partner", "where": [["name", "like", "Pvo "]],
                   "wells": {"rows": [{"field": "country_id"}], "values": [{"agg": "count"}]},
                   "limit": limit, "options": {"other": True, "show_totals": totals}}
        if columns:
            widget_["wells"]["columns"] = [{"field": "is_company"}]
        if series_limit:
            widget_["series_limit"] = series_limit
        return self.run_as(self.alice, widget_)

    def cells(self, result):
        return {(r["keys"][0], r["keys"][1] if len(r["keys"]) > 1 else None): r["values"][0] for r in result["rows"]}

    def test_the_other_row_has_the_cells_of_everything_beyond_the_limit(self):
        response = self.pivot(limit=2)
        self.assertTrue(response["ok"], response)
        cells = self.cells(response["result"])
        countries = {c.name: c.id for c in self.env["res.country"].search([("code", "in", list(self.spread))])}
        top = ["Belgium", "France"]  # 6 and 5
        for name in top:
            for flag in (True, False):
                self.assertEqual(cells.get((countries[name], flag), 0), self.truth.get((name, flag), 0), (name, flag))
        for flag in (True, False):
            rest = sum(n for (name, f), n in self.truth.items() if f == flag and name not in top)
            self.assertEqual(cells.get(("__other", flag), 0), rest, flag)
        self.assertEqual(sum(cells.values()), 20)  # nothing is lost
        self.assertTrue(response["result"]["truncated"]["axis"])

    def test_totals_are_the_real_totals(self):
        result = self.pivot(limit=2)["result"]
        totals = result["totals"]
        self.assertEqual(totals["grand"][0]["values"], [20])
        by_row = {r["keys"][0]: r["values"][0] for r in totals["rows"]}
        self.assertEqual(by_row["__other"], 9)  # DE 4 + ES 3 + IT 2
        self.assertEqual(sorted(by_row.values()), [5, 6, 9])
        self.assertEqual(sum(c["values"][0] for c in totals["columns"]), 20)  # the columns add up too

    def test_every_cell_carries_the_labels_of_its_row_and_column(self):
        """Regression: the cells of the Other column wrote an empty label over the name of their own row."""
        result = self.pivot(limit=2, series_limit=1)["result"]
        for r in result["rows"]:
            self.assertEqual(len(r["labels"]), 2)
            self.assertTrue(r["labels"][0], r)  # a row name, or "Other"
            self.assertTrue(r["labels"][1], r)  # a column name, or "Other"
        named = {r["keys"][0]: r["labels"][0] for r in result["rows"]}
        self.assertEqual(named["__other"], "Other")
        self.assertTrue({"Belgium", "France"} <= set(named.values()))

    def test_the_other_column_and_the_corner(self):
        result = self.pivot(limit=2, series_limit=1)["result"]
        self.assertTrue(result["truncated"]["series"] and result["truncated"]["axis"])
        cells = self.cells(result)
        self.assertEqual(sum(cells.values()), 20)  # rows x columns, Other row, Other column and the corner: all of it
        self.assertEqual(len({k[1] for k in cells if k[1] != "__other"}), 1)  # one series kept
        self.assertIn(("__other", "__other"), cells)  # the corner: Other x Other
        row_totals = {r["keys"][0]: r["values"][0] for r in result["totals"]["rows"]}
        for row, total in row_totals.items():
            self.assertEqual(sum(v for (r, _c), v in cells.items() if r == row), total, row)
        col_totals = {r["keys"][0]: r["values"][0] for r in result["totals"]["columns"]}
        for col, total in col_totals.items():
            self.assertEqual(sum(v for (_r, c), v in cells.items() if c == col), total, col)

    def test_rows_only(self):
        result = self.pivot(limit=3, columns=False, totals=False)["result"]
        cells = {r["keys"][0]: r["values"][0] for r in result["rows"]}
        self.assertEqual(cells["__other"], 5)  # ES 3 + IT 2
        self.assertEqual(sum(cells.values()), 20)

    def test_nothing_added_when_everything_fits(self):
        result = self.pivot(limit=10)["result"]
        self.assertNotIn("__other", {r["keys"][0] for r in result["rows"]})
        self.assertEqual(sum(r["values"][0] for r in result["rows"]), 20)

    def test_without_the_option_the_rest_is_dropped_as_before(self):
        widget_ = {"id": "p", "type": "pivot", "dataset": "orm:res.partner", "where": [["name", "like", "Pvo "]],
                   "wells": {"rows": [{"field": "country_id"}], "columns": [{"field": "is_company"}],
                             "values": [{"agg": "count"}]}, "limit": 2}
        result = self.run_as(self.alice, widget_)["result"]
        self.assertEqual(sum(r["values"][0] for r in result["rows"]), 11)


class TestFillMatchesOdoo(EngineCase):
    """The empty intervals are written by us; their keys and labels must be those of ``formatted_read_group``, or an
    interval would show up twice."""

    def check(self, model, spec, days, make):
        from ..engine import fill
        if not hasattr(self, "_made"):
            self._made = {}
        if model not in self._made:  # the rows are made once, then grouped in every interval and time zone
            self._made[model] = make()
        made = self._made[model]
        make = lambda: made  # noqa: E731
        for tz in (None, "UTC", TZ, "America/New_York"):
            Model = self.env[model].with_context(tz=tz) if tz else self.env[model]
            groups = Model.formatted_read_group([("id", "in", make().ids)], [spec], ["__count"])
            name, interval = spec.split(":")
            ours = {fill.key_and_label(Model.env, Model._fields[name].type, interval, d) for d in days}
            theirs = {tuple(g[spec]) for g in groups}
            self.assertTrue(theirs <= ours, (model, spec, tz, theirs - ours))

    def test_datetime_intervals(self):
        stamps = ["2026-03-01 00:00:00", "2026-03-31 23:59:00", "2026-11-23 12:00:00", "2026-12-31 18:00:00",
                  "2027-01-01 03:00:00"]

        def make():
            made = self.partners("Fil", {"BE": len(stamps)})
            for p, stamp in zip(made, stamps):
                self.env.cr.execute("UPDATE res_partner SET create_date = %s WHERE id = %s", [stamp, p.id])
            self.env.invalidate_all()
            return made

        from ..engine import fill
        for interval in ("day", "week", "month", "quarter", "year"):
            days = fill.bucket_starts(D(2026, 2, 20), D(2027, 1, 5), interval, 0)
            days += fill.bucket_starts(D(2026, 2, 20), D(2027, 1, 5), interval, 6) if interval == "week" else []
            self.check("res.partner", "create_date:%s" % interval, days, make)

    def test_date_intervals(self):
        def make():
            Rate = self.env["res.currency.rate"]
            currency = self.env["res.currency"].create({"name": "ZZQ", "symbol": "z", "rounding": 0.01})
            return Rate.create([{"name": d, "currency_id": currency.id, "rate": 1.0}
                                for d in ("2025-03-01", "2025-03-31", "2025-11-23", "2025-12-31", "2026-01-01")])

        from ..engine import fill
        for interval in ("day", "week", "month", "quarter", "year"):
            days = fill.bucket_starts(D(2025, 2, 20), D(2026, 1, 5), interval, 0)
            days += fill.bucket_starts(D(2025, 2, 20), D(2026, 1, 5), interval, 6) if interval == "week" else []
            self.check("res.currency.rate", "name:%s" % interval, days, make)

    def test_filling_gives_one_group_per_interval_in_order(self):
        from ..engine import fill
        groups = self.env["res.partner"].formatted_read_group([("id", "=", -1)], ["create_date:month"], ["__count"])
        filled = fill.fill(self.env, self.env["res.partner"], "create_date:month", groups, ["__count"],
                           D(2026, 1, 15), D(2026, 4, 2))
        self.assertEqual(len(filled), 4)
        self.assertTrue(all(g["__count"] == 0 for g in filled))
        self.assertEqual(fill.bucket_starts(D(2026, 1, 15), D(2026, 4, 2), "month")[0], D(2026, 1, 1))
        with self.assertRaises(ValueError):
            fill.bucket_starts(D(2026, 1, 1), D(2026, 1, 2), "decade")
