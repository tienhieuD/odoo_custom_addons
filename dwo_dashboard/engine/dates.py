# -*- coding: utf-8 -*-
"""Date presets of the page filters, computed in the viewer's timezone. Pure Python (pytz only)."""
import datetime as dt

import pytz

MONDAY = 0

# IANA "backward" links: names that browsers and old settings still send but that a minimal tzdata (PostgreSQL images
# without ``tzdata-legacy``) no longer has. Mapping them keeps the day/week/month buckets right.
LEGACY_TZ = {
    "Asia/Saigon": "Asia/Ho_Chi_Minh", "Asia/Calcutta": "Asia/Kolkata", "Asia/Katmandu": "Asia/Kathmandu",
    "Asia/Rangoon": "Asia/Yangon", "Asia/Dacca": "Asia/Dhaka", "Asia/Thimbu": "Asia/Thimphu",
    "Asia/Ulan_Bator": "Asia/Ulaanbaatar", "Asia/Macao": "Asia/Macau", "Asia/Chongqing": "Asia/Shanghai",
    "Asia/Chungking": "Asia/Shanghai", "Asia/Harbin": "Asia/Shanghai", "Asia/Kashgar": "Asia/Urumqi",
    "Asia/Istanbul": "Europe/Istanbul", "Asia/Tel_Aviv": "Asia/Jerusalem", "Asia/Ujung_Pandang": "Asia/Makassar",
    "Asia/Ashkhabad": "Asia/Ashgabat", "Europe/Kiev": "Europe/Kyiv", "Europe/Belfast": "Europe/London",
    "Atlantic/Faeroe": "Atlantic/Faroe", "America/Buenos_Aires": "America/Argentina/Buenos_Aires",
    "America/Indianapolis": "America/Indiana/Indianapolis", "America/Louisville": "America/Kentucky/Louisville",
    "America/Godthab": "America/Nuuk", "America/Montreal": "America/Toronto", "America/Ensenada": "America/Tijuana",
    "Pacific/Samoa": "Pacific/Pago_Pago", "Pacific/Truk": "Pacific/Chuuk", "Pacific/Ponape": "Pacific/Pohnpei",
    "Australia/Canberra": "Australia/Sydney", "Australia/ACT": "Australia/Sydney", "Australia/NSW": "Australia/Sydney",
    "Africa/Asmera": "Africa/Asmara", "Antarctica/South_Pole": "Pacific/Auckland",
    "US/Eastern": "America/New_York", "US/Central": "America/Chicago", "US/Mountain": "America/Denver",
    "US/Pacific": "America/Los_Angeles", "US/Alaska": "America/Anchorage", "US/Hawaii": "Pacific/Honolulu",
    "Canada/Eastern": "America/Toronto", "Canada/Pacific": "America/Vancouver",
    "Singapore": "Asia/Singapore", "Hongkong": "Asia/Hong_Kong", "Japan": "Asia/Tokyo", "PRC": "Asia/Shanghai",
    "ROK": "Asia/Seoul", "Turkey": "Europe/Istanbul", "Egypt": "Africa/Cairo", "GB": "Europe/London",
    "NZ": "Pacific/Auckland", "Israel": "Asia/Jerusalem", "Iran": "Asia/Tehran", "Cuba": "America/Havana",
}


def canonical_tz(name):
    """The current IANA name of a possibly legacy time zone name."""
    return LEGACY_TZ.get(name, name)


def tz_of(name):
    try:
        return pytz.timezone(name) if name else pytz.utc
    except pytz.UnknownTimeZoneError:
        return pytz.utc


def today_in_tz(name, now=None):
    """The current calendar date of the viewer (not of the server)."""
    now = now or dt.datetime.now(pytz.utc)
    return now.astimezone(tz_of(name)).date()


def _week_start(day, first_weekday):
    return day - dt.timedelta(days=(day.weekday() - first_weekday) % 7)


def _quarter_start(day):
    return dt.date(day.year, 3 * ((day.month - 1) // 3) + 1, 1)


def _add_months(day, months):
    index = day.year * 12 + day.month - 1 + months
    return dt.date(index // 12, index % 12 + 1, 1)


def preset_range(preset, today, first_weekday=MONDAY):
    """``(start, end)`` dates, end excluded, or None for ``all``. ``first_weekday``: 0 = Monday ... 6 = Sunday."""
    one = dt.timedelta(days=1)
    if preset == "all":
        return None
    if preset == "today":
        return today, today + one
    if preset == "yesterday":
        return today - one, today
    if preset in ("last_7_days", "last_30_days", "last_90_days"):
        days = int(preset.split("_")[1])
        return today - dt.timedelta(days=days - 1), today + one
    if preset in ("this_week", "last_week"):
        start = _week_start(today, first_weekday)
        if preset == "last_week":
            return start - dt.timedelta(days=7), start
        return start, start + dt.timedelta(days=7)
    if preset in ("this_month", "last_month"):
        start = dt.date(today.year, today.month, 1)
        if preset == "last_month":
            return _add_months(start, -1), start
        return start, _add_months(start, 1)
    if preset in ("this_quarter", "last_quarter"):
        start = _quarter_start(today)
        if preset == "last_quarter":
            return _add_months(start, -3), start
        return start, _add_months(start, 3)
    if preset in ("this_year", "last_year"):
        start = dt.date(today.year, 1, 1)
        if preset == "last_year":
            return dt.date(today.year - 1, 1, 1), start
        return start, dt.date(today.year + 1, 1, 1)
    raise ValueError("unknown date preset %r" % preset)


def to_utc(day, tz_name):
    """Midnight of ``day`` in the viewer's timezone, as a naive UTC datetime (what the database stores)."""
    local = tz_of(tz_name).localize(dt.datetime.combine(day, dt.time()))
    return local.astimezone(pytz.utc).replace(tzinfo=None)
