/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { cookie } from "@web/core/browser/cookie";
import { formatDateTime } from "@web/core/l10n/dates";
import { localization } from "@web/core/l10n/localization";
import { _t } from "@web/core/l10n/translation";
import { getColor } from "@web/core/colors/colors";
import { formatCurrency } from "@web/core/currency";
import { user } from "@web/core/user";

export const COLS_DEFAULT = 12;
export const COLS_MAX = 120; // as the spec (spec/constants.py)
export const COLS_SPARE = 12; // empty columns kept to the right of the last widget while editing
export const ROW_HEIGHT = 80;
export const GAP = 12; // px between two cards: the same as --dwo-gap in dashboard.scss

/** The colour of the ``index``-th series or slice. ``total``: how many there are, so that a short list gets the
 * 6 clearly different colours of Odoo's small palette (the default palette is a gradient of blues). */
export function colorFor(index, options, total = 6) {
    const custom = options && options.colors;
    if (custom && custom.length) {
        return custom[index % custom.length];
    }
    return getColor(index, cookie.get("color_scheme") || "light", total);
}

/** A number as the viewer reads it: grouping, at most ``decimals`` (default: up to 2) digits, ``format`` option. */
export function formatNumber(value, options = {}) {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return "";
    }
    const decimals = options.decimals;
    const digits =
        decimals === undefined
            ? { maximumFractionDigits: Number.isInteger(value) ? 0 : 2 }
            : { minimumFractionDigits: decimals, maximumFractionDigits: decimals };
    if (options.format === "currency") {
        const company = user.activeCompany;
        return formatCurrency(value, company && company.currency_id, {
            digits: [16, decimals === undefined ? 2 : decimals],
        });
    }
    const text = new Intl.NumberFormat(user.lang, digits).format(value);
    return options.format === "percent" ? `${text}%` : text;
}

export function newWidgetId(widgets) {
    const used = new Set(widgets.map((w) => w.id));
    let n = widgets.length + 1;
    while (used.has(`w${n}`)) {
        n += 1;
    }
    return `w${n}`;
}

/** Where a new widget goes: left edge, under the lowest one. */
export function nextPosition(widgets, w, h) {
    const bottom = widgets.reduce((max, x) => Math.max(max, x.y + x.h), 0);
    return { x: 0, y: bottom, w, h };
}

/** Metabase/Tableau-style hint: which visual suits the fields chosen (null when nothing to say). */
export function suggestVisual(currentType, firstDimension, measureCount) {
    if (!firstDimension) {
        return measureCount ? "kpi" : null;
    }
    const kind = firstDimension.type;
    if ((kind === "date" || kind === "datetime") && !["line", "area"].includes(currentType)) {
        return "line";
    }
    if ((kind === "selection" || kind === "boolean") && !["pie", "doughnut", "bar"].includes(currentType)) {
        return "doughnut";
    }
    return null;
}


export const PRESET_LABELS = {
    all: _t("All time"),
    today: _t("Today"),
    yesterday: _t("Yesterday"),
    last_7_days: _t("Last 7 days"),
    last_30_days: _t("Last 30 days"),
    last_90_days: _t("Last 90 days"),
    this_week: _t("This week"),
    last_week: _t("Last week"),
    this_month: _t("This month"),
    last_month: _t("Last month"),
    this_quarter: _t("This quarter"),
    last_quarter: _t("Last quarter"),
    this_year: _t("This year"),
    last_year: _t("Last year"),
};

export const INTERVALS = ["year", "quarter", "month", "week", "day"];
export const INTERVAL_LABELS = { year: _t("year"), quarter: _t("quarter"), month: _t("month"), week: _t("week"), day: _t("day") };

/** The first dimension of a widget (what a click on a bar, a slice or a pivot row stands for). Same rule as the server's. */
export function primaryItem(widget) {
    const wells = widget.wells || {};
    for (const name of ["axis", "category", "rows"]) {
        const item = Array.isArray(wells[name]) ? wells[name][0] : wells[name];
        if (item && item.field) {
            return item;
        }
    }
    return null;
}

/** The intervals a time axis goes through when drilled, from its own interval down to the day. */
export function drillChain(widget) {
    const item = primaryItem(widget);
    return item && INTERVALS.includes(item.interval) ? INTERVALS.slice(INTERVALS.indexOf(item.interval)) : [];
}

/** A date and time in the viewer's format, without the seconds. */
export function formatDateTimeShort(value) {
    return formatDateTime(value, { format: localization.dateTimeFormat.replace(/[:.]ss/, "") });
}

/** The icon in front of a widget's title when the author chose none: one per kind of widget (Font Awesome 4, as in Odoo). */
export const DEFAULT_ICONS = {
    kpi: "fa-hashtag", table: "fa-list", pivot: "fa-th", bar: "fa-bar-chart", line: "fa-line-chart",
    area: "fa-area-chart", pie: "fa-pie-chart", doughnut: "fa-circle-o-notch",
};
export const DEFAULT_ICON = "fa-square-o"; // a widget type added by a plugin

/** A short list to choose from (any `fa-*` name is valid in the spec). */
export const ICON_CHOICES = [
    "fa-hashtag", "fa-list", "fa-th", "fa-table", "fa-bar-chart", "fa-line-chart", "fa-area-chart", "fa-pie-chart",
    "fa-money", "fa-usd", "fa-shopping-cart", "fa-credit-card", "fa-percent", "fa-balance-scale",
    "fa-users", "fa-user", "fa-handshake-o", "fa-building", "fa-briefcase", "fa-globe",
    "fa-truck", "fa-cube", "fa-cubes", "fa-tags", "fa-ticket", "fa-wrench",
    "fa-calendar", "fa-clock-o", "fa-envelope", "fa-phone", "fa-comments", "fa-bell",
    "fa-star", "fa-heart", "fa-flag", "fa-bolt", "fa-fire", "fa-trophy", "fa-bullseye", "fa-rocket",
    "fa-check-circle", "fa-exclamation-triangle", "fa-info-circle", "fa-eye",
];

export function widgetIcon(widget) {
    return widget.icon || DEFAULT_ICONS[widget.type] || DEFAULT_ICON;
}
