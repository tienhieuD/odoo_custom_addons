# -*- coding: utf-8 -*-
import datetime as dt
from unittest.mock import patch

from ..engine import dates
from .test_engine import EngineCase, TZ, kpi

D = dt.date
TODAY = D(2026, 11, 25)  # a Wednesday


class TestCompareRanges(EngineCase):
    """Pure calendar arithmetic: what "previous" means, for each preset."""

    def ranges(self, preset, today=TODAY, against="previous_period", first=0):
        return dates.compare_ranges(preset, today, first, against)

    def test_this_month_is_period_to_date_against_the_same_span_of_the_previous_month(self):
        self.assertEqual(self.ranges("this_month"), (D(2026, 11, 1), D(2026, 11, 26), D(2026, 10, 1), D(2026, 10, 26)))

    def test_calendar_units_not_a_number_of_days(self):
        # 31 March: the previous month has no 31st, it clamps to the end of February
        self.assertEqual(self.ranges("this_month", D(2026, 3, 31)),
                         (D(2026, 3, 1), D(2026, 4, 1), D(2026, 2, 1), D(2026, 3, 1)))
        self.assertEqual(self.ranges("this_quarter"), (D(2026, 10, 1), D(2026, 11, 26), D(2026, 7, 1), D(2026, 8, 26)))
        self.assertEqual(self.ranges("this_year"), (D(2026, 1, 1), D(2026, 11, 26), D(2025, 1, 1), D(2025, 11, 26)))
        self.assertEqual(self.ranges("this_week"), (D(2026, 11, 23), D(2026, 11, 26), D(2026, 11, 16), D(2026, 11, 19)))

    def test_complete_periods_are_compared_with_the_complete_period_before(self):
        self.assertEqual(self.ranges("last_month"), (D(2026, 10, 1), D(2026, 11, 1), D(2026, 9, 1), D(2026, 10, 1)))
        self.assertEqual(self.ranges("last_quarter"), (D(2026, 7, 1), D(2026, 10, 1), D(2026, 4, 1), D(2026, 7, 1)))
        self.assertEqual(self.ranges("last_year"), (D(2025, 1, 1), D(2026, 1, 1), D(2024, 1, 1), D(2025, 1, 1)))
        self.assertEqual(self.ranges("last_week"), (D(2026, 11, 16), D(2026, 11, 23), D(2026, 11, 9), D(2026, 11, 16)))

    def test_rolling_periods_shift_back_by_their_own_length(self):
        self.assertEqual(self.ranges("last_30_days"), (D(2026, 10, 27), D(2026, 11, 26), D(2026, 9, 27), D(2026, 10, 27)))
        self.assertEqual(self.ranges("today"), (D(2026, 11, 25), D(2026, 11, 26), D(2026, 11, 24), D(2026, 11, 25)))
        self.assertEqual(self.ranges("yesterday"), (D(2026, 11, 24), D(2026, 11, 25), D(2026, 11, 23), D(2026, 11, 24)))

    def test_previous_year_and_the_leap_day(self):
        self.assertEqual(self.ranges("this_month", against="previous_year"),
                         (D(2026, 11, 1), D(2026, 11, 26), D(2025, 11, 1), D(2025, 11, 26)))
        self.assertEqual(self.ranges("this_month", D(2028, 2, 29), "previous_year"),  # 2027 has no 29 February
                         (D(2028, 2, 1), D(2028, 3, 1), D(2027, 2, 1), D(2027, 3, 1)))
        self.assertEqual(self.ranges("last_year", against="previous_year"),
                         (D(2025, 1, 1), D(2026, 1, 1), D(2024, 1, 1), D(2025, 1, 1)))

    def test_all_has_nothing_to_compare(self):
        with self.assertRaises(ValueError):
            self.ranges("all")  # callers check for it first (compare_setup returns None)


class TestCompareKpi(EngineCase):

    def born(self, when, count=1, prefix="Cmp"):
        """Partners whose create_date is ``when`` (UTC, set in SQL)."""
        made = self.partners("%s%s" % (prefix, when[:10].replace("-", "")), {"BE": count})
        self.env.cr.execute("UPDATE res_partner SET create_date = %s WHERE id IN %s", [when, tuple(made.ids)])
        self.env.invalidate_all()
        return made

    def setUp(self):
        super().setUp()
        self.born("2026-11-03 10:00:00", 3)   # this month, up to the 25th
        self.born("2026-11-20 10:00:00", 2)   # this month, up to the 25th
        self.born("2026-10-05 10:00:00", 2)   # previous period (1-25 Oct)
        self.born("2026-10-28 10:00:00", 4)   # October, but after the 25th: not in the previous period-to-date
        self.born("2025-11-10 10:00:00", 4)   # a year ago, same span
        self.born("2026-09-10 10:00:00", 1)
        self.where = [["name", "like", "Cmp"]]

    def kpi(self, **compare):
        return dict(kpi(where=self.where), compare=dict({"field": "create_date"}, **compare))

    def compared(self, widget, filters=None, values=None, tz=None):
        with patch.object(dates, "today_in_tz", return_value=TODAY):
            response = self.run_as(self.alice, widget, filters, values, tz=tz)
        self.assertTrue(response["ok"], response)
        return response["result"]

    def test_this_month_against_the_previous_period_to_date(self):
        result = self.compared(self.kpi())
        c = result["compare"]
        self.assertEqual((c["current"], c["previous"]), (5, 2))  # the 4 partners of 28 Oct are NOT in the previous span
        self.assertAlmostEqual(c["change_pct"], 150.0)
        self.assertEqual(result["rows"][0]["values"], [5])  # the headline number is the current one
        self.assertEqual(c["range"], ["2026-11-01", "2026-11-26"])
        self.assertEqual(c["previous_range"], ["2026-10-01", "2026-10-26"])

    def test_against_the_previous_year(self):
        c = self.compared(self.kpi(against="previous_year"))["compare"]
        self.assertEqual((c["current"], c["previous"]), (5, 4))
        self.assertAlmostEqual(c["change_pct"], 25.0)

    def test_a_previous_period_without_records_gives_no_percentage_never_infinity(self):
        c = self.compared(self.kpi(period="last_year", against="previous_year"))["compare"]  # 2025 vs 2024
        self.assertEqual(c["current"], 4)
        self.assertEqual(c["previous"], 0)
        self.assertIsNone(c["change_pct"])

    def test_the_page_date_filter_on_the_same_field_decides_the_period(self):
        """The filter's own condition is REPLACED by the two ranges: ANDing it would leave the previous period empty."""
        filters = [{"id": "p", "type": "date", "default": "this_month",
                    "bind": [{"dataset": "orm:res.partner", "field": "create_date"}]}]
        default = self.compared(self.kpi(), filters)["compare"]
        self.assertEqual((default["current"], default["previous"]), (5, 2))
        last_month = self.compared(self.kpi(), filters, {"p": "last_month"})["compare"]  # October in full against September
        self.assertEqual((last_month["period"], last_month["current"], last_month["previous"]), ("last_month", 6, 1))
        everything = self.compared(self.kpi(), filters, {"p": "all"})  # no period: nothing to compare
        self.assertNotIn("compare", everything)
        self.assertEqual(everything["rows"][0]["values"], [16])

    def test_a_widget_that_ignores_the_filter_uses_its_own_period(self):
        filters = [{"id": "p", "type": "date", "default": "last_year",
                    "bind": [{"dataset": "orm:res.partner", "field": "create_date"}]}]
        widget = dict(self.kpi(period="this_month"), ignore_filters=["p"])
        self.assertEqual(self.compared(widget, filters)["compare"]["current"], 5)

    def test_a_filter_on_another_field_still_applies_to_both_periods(self):
        self.env.cr.execute("UPDATE res_partner SET write_date = %s WHERE name LIKE 'Cmp%%'", ["2026-11-24 10:00:00"])
        self.env.invalidate_all()
        filters = [{"id": "w", "type": "date", "default": "all",
                    "bind": [{"dataset": "orm:res.partner", "field": "write_date"}]}]
        both = self.compared(self.kpi(), filters)["compare"]
        self.assertEqual((both["current"], both["previous"]), (5, 2))  # an "all" filter changes nothing
        none = self.compared(self.kpi(), filters, {"w": "last_year"})["compare"]  # nothing was written last year
        self.assertEqual((none["current"], none["previous"]), (0, 0))

    def test_the_boundaries_are_the_viewers_not_utc(self):
        # 31 Oct 17:30 UTC is already 1 Nov in UTC+7: it belongs to this month for a Vietnamese viewer only
        self.born("2026-10-31 17:30:00", 1, prefix="Cmp2")
        utc = self.compared(self.kpi(), tz="UTC")["compare"]
        local = self.compared(self.kpi(), tz=TZ)["compare"]
        self.assertEqual(local["current"], utc["current"] + 1)

    def test_only_a_kpi_can_be_compared_and_the_field_must_be_a_date(self):
        bad = self.kpi()
        bad["compare"]["field"] = "name"
        self.assertEqual(self.run_as(self.alice, bad)["error"]["code"], "invalid")
        bar = {"id": "b", "type": "bar", "dataset": "orm:res.partner", "compare": {"field": "create_date"},
               "wells": {"axis": {"field": "country_id"}, "values": [{"agg": "count"}]}}
        self.assertEqual(self.run_as(self.alice, bar)["error"]["code"], "invalid")


class TestPieOther(EngineCase):

    def test_the_rest_becomes_one_slice_and_the_total_is_kept(self):
        spread = {"BE": 6, "FR": 5, "DE": 4, "ES": 3, "IT": 2}
        self.partners("Oth", spread)
        widget = {"id": "p", "type": "pie", "dataset": "orm:res.partner", "where": [["name", "like", "Oth "]],
                  "wells": {"category": {"field": "country_id"}, "value": {"agg": "count"}},
                  "order": [{"measure": "__count", "dir": "desc"}], "limit": 3, "options": {"other": True}}
        result = self.run_as(self.alice, widget)["result"]
        self.assertEqual([r["labels"][0] for r in result["rows"]], ["Belgium", "France", "Germany", "Other"])
        self.assertEqual([r["values"][0] for r in result["rows"]], [6, 5, 4, 5])
        self.assertEqual(sum(r["values"][0] for r in result["rows"]), 20)  # the total is the real total
        widget["options"] = {}
        self.assertEqual(len(self.run_as(self.alice, widget)["result"]["rows"]), 3)  # without the option: top 3 only

    def test_no_other_slice_when_everything_fits(self):
        self.partners("Fit", {"BE": 2, "FR": 1})
        widget = {"id": "p", "type": "doughnut", "dataset": "orm:res.partner", "where": [["name", "like", "Fit "]],
                  "wells": {"category": {"field": "country_id"}, "value": {"agg": "count"}}, "options": {"other": True}}
        self.assertEqual(len(self.run_as(self.alice, widget)["result"]["rows"]), 2)

    def test_other_is_refused_for_aggregates_that_do_not_add_up(self):
        for agg in ("avg", "min", "max", "count_distinct"):
            widget = {"id": "p", "type": "pie", "dataset": "orm:res.partner",
                      "wells": {"category": {"field": "country_id"}, "value": {"agg": agg, "field": "id"}},
                      "options": {"other": True}}
            self.assertEqual(self.run_as(self.alice, widget)["error"]["code"], "invalid", agg)


class TestTableOpensRecords(EngineCase):

    def test_the_result_carries_the_ids_and_the_model(self):
        made = self.partners("Opn", {"BE": 2})
        widget = {"id": "t", "type": "table", "dataset": "orm:res.partner", "where": [["name", "like", "Opn "]],
                  "wells": {"columns": [{"field": "name"}]}, "order": [{"field": "name", "dir": "asc"}],
                  "options": {"open_records": True}}
        result = self.run_as(self.alice, widget)["result"]
        self.assertEqual(result["model"], "res.partner")
        self.assertEqual(result["ids"], made.sorted("name").ids)

    def test_dates_travel_in_server_format_without_microseconds(self):
        self.partners("Dfm", {"BE": 1})
        widget = {"id": "t", "type": "table", "dataset": "orm:res.partner", "where": [["name", "like", "Dfm "]],
                  "wells": {"columns": [{"field": "create_date"}]}}
        value = self.run_as(self.alice, widget)["result"]["rows"][0][0]
        self.assertRegex(value, r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d$")
