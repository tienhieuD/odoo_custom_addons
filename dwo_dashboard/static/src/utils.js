/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { cookie } from "@web/core/browser/cookie";
import { _t } from "@web/core/l10n/translation";
import { getColor } from "@web/core/colors/colors";
import { formatCurrency } from "@web/core/currency";
import { user } from "@web/core/user";

export const COLS_DEFAULT = 12;
export const ROW_HEIGHT = 80;

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
