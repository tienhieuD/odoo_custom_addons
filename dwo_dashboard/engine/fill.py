# -*- coding: utf-8 -*-
"""Fill the empty intervals of a time series, with keys and labels written exactly like Odoo's ``formatted_read_group`` does.

Odoo has ``fill_temporal`` for this, but with a datetime field and a time zone it fails on its own bounds (it localizes a
``date``), so the empty intervals are written here. The keys and labels follow ``_web_read_group_groupby_formatter``, and a
test compares them with real groups: if they ever differ, an interval would appear twice."""
import datetime as dt

import babel
import babel.dates
import pytz

from odoo.models import READ_GROUP_DISPLAY_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, date_utils, get_lang

from . import dates

_MONTHS = {"month": 1, "quarter": 3, "year": 12}


def bucket_starts(start, end, interval, first_weekday=0):
    """The first day of every interval that touches ``[start, end]`` (end included)."""
    out = []
    if interval == "day":
        current, step = start, dt.timedelta(days=1)
    elif interval == "week":
        current, step = dates._week_start(start, first_weekday), dt.timedelta(days=7)
    elif interval in _MONTHS:
        n = _MONTHS[interval]
        first = dt.date(start.year, start.month, 1)
        if interval == "quarter":
            first = dt.date(start.year, 3 * ((start.month - 1) // 3) + 1, 1)
        elif interval == "year":
            first = dt.date(start.year, 1, 1)
        current, step = first, None
    else:
        raise ValueError("unknown interval %r" % interval)
    while current <= end:
        out.append(current)
        current = current + step if step else dates.shift_months(current, _MONTHS[interval])
    return out


def key_and_label(env, field_type, interval, day):
    """``(key, label)`` of the interval starting on ``day``: what ``formatted_read_group`` gives for that group."""
    locale = get_lang(env).code
    display = READ_GROUP_DISPLAY_FORMAT[interval]
    tz_name = env.context.get("tz")
    if field_type == "datetime":
        tz = pytz.timezone(tz_name) if tz_name in pytz.all_timezones_set else None
        local = dt.datetime.combine(day, dt.time())
        start = tz.localize(local).astimezone(pytz.utc) if tz else local
        key = start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        label = babel.dates.format_datetime(start, format=display, tzinfo=tz, locale=locale)
        week_value = local
    else:
        key = day.strftime(DEFAULT_SERVER_DATE_FORMAT)
        label = babel.dates.format_date(day, format=display, locale=locale)
        week_value = day
    if interval == "week":
        year, week = date_utils.weeknumber(babel.Locale.parse(locale), week_value)
        label = "W%s %04d" % (week, year)
    return key, label


def _empty(spec):
    return None if spec.endswith((":avg", ":min", ":max")) else 0


def fill(env, model, spec, groups, aggregates, start, end, first_weekday=0):
    """``groups``: the formatted groups of ``spec`` (``"field:interval"``), in any order. Returns one group per interval from
    ``start`` to ``end`` (both included), in order, the empty ones with zero counts and sums (and None averages)."""
    name, interval = spec.split(":")
    field_type = model._fields[name].type
    present = {}
    for g in groups:
        value = g[spec]
        if isinstance(value, (tuple, list)) and len(value) == 2:
            present[value[0]] = g
    out = []
    for day in bucket_starts(start, end, interval, first_weekday):
        key, label = key_and_label(env, field_type, interval, day)
        out.append(present.get(key) or dict({spec: (key, label), "__extra_domain": []},
                                            **{a: _empty(a) for a in aggregates}))
    return out
