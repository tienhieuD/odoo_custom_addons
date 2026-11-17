/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
// The logic of the column filters, without OWL: which operators a field has, the quick date ranges (with the time zone
// of the user and the fiscal year), and the domain and the text of the facet that a filter makes.
import { _t } from "@web/core/l10n/translation";

const { DateTime } = luxon;

/** The fiscal year of this module: 1 April to 31 March of the next year (not read from the company). */
export const FISCAL_START_MONTH = 4;

export const MAX_FACET_VALUES = 3;

// --- what kind of filter a field gets -------------------------------------------------------------------------------
const KIND_OF_TYPE = {
    char: "text",
    text: "text",
    html: "text",
    integer: "number",
    float: "number",
    monetary: "number",
    boolean: "boolean",
    date: "date",
    datetime: "date",
    selection: "choice",
    many2one: "choice",
    many2many: "choice",
    one2many: "choice",
};

/** ``text``, ``number``, ``boolean``, ``date`` or ``choice``; ``null`` when the field cannot be filtered. */
export function filterKind(field) {
    if (!field || field.searchable === false) {
        return null;
    }
    return KIND_OF_TYPE[field.type] || null;
}

// --- operators (the ones of the Odoo filters) -----------------------------------------------------------------------
export function textOperators() {
    return [
        { id: "ilike", label: _t("contains"), needsValue: true },
        { id: "not ilike", label: _t("does not contain"), needsValue: true },
        { id: "=", label: _t("is equal to"), needsValue: true },
        { id: "!=", label: _t("is not equal to"), needsValue: true },
        { id: "set", label: _t("is set"), needsValue: false },
        { id: "not_set", label: _t("is not set"), needsValue: false },
    ];
}

export function numberOperators() {
    return [
        { id: "=", label: _t("is equal to"), needsValue: true },
        { id: "!=", label: _t("is not equal to"), needsValue: true },
        { id: ">", label: _t("is greater than"), needsValue: true },
        { id: ">=", label: _t("is greater than or equal to"), needsValue: true },
        { id: "<", label: _t("is lower than"), needsValue: true },
        { id: "<=", label: _t("is lower than or equal to"), needsValue: true },
        { id: "between", label: _t("is between"), needsValue: true, range: true },
    ];
}

// --- quick date ranges ----------------------------------------------------------------------------------------------
/** The first day of the fiscal year that contains ``day`` (a luxon DateTime). */
export function fiscalYearStart(day) {
    const year = day.month >= FISCAL_START_MONTH ? day.year : day.year - 1;
    return DateTime.fromObject({ year, month: FISCAL_START_MONTH, day: 1 }, { zone: day.zone });
}

/**
 * The quick ranges: ``[id, label, (now) => [first day, last day]]``. Days are whole days in the zone of ``now`` (the
 * time zone of the user): a range ends on its last day, the domain turns it into "before the next day starts".
 */
export function datePresets() {
    const day = (now, n = 0) => now.startOf("day").plus({ days: n });
    const unit = (name) => (now, n = 0) => {
        const start = now.startOf(name).plus({ [`${name}s`]: n });
        return [start, start.endOf(name).startOf("day")];
    };
    const week = unit("week");
    const month = unit("month");
    const quarter = unit("quarter");
    const year = unit("year");
    const fiscal = (now, n = 0) => {
        const start = fiscalYearStart(now).plus({ years: n });
        return [start, start.plus({ years: 1, days: -1 })];
    };
    return [
        ["today", _t("Today"), (now) => [day(now), day(now)]],
        ["yesterday", _t("Yesterday"), (now) => [day(now, -1), day(now, -1)]],
        ["tomorrow", _t("Tomorrow"), (now) => [day(now, 1), day(now, 1)]],
        ["last_7_days", _t("Last 7 days"), (now) => [day(now, -6), day(now)]],
        ["last_30_days", _t("Last 30 days"), (now) => [day(now, -29), day(now)]],
        ["next_7_days", _t("Next 7 days"), (now) => [day(now), day(now, 6)]],
        ["next_30_days", _t("Next 30 days"), (now) => [day(now), day(now, 29)]],
        ["this_week", _t("This week"), (now) => week(now)],
        ["last_week", _t("Last week"), (now) => week(now, -1)],
        ["next_week", _t("Next week"), (now) => week(now, 1)],
        ["this_month", _t("This month"), (now) => month(now)],
        ["last_month", _t("Last month"), (now) => month(now, -1)],
        ["next_month", _t("Next month"), (now) => month(now, 1)],
        ["this_quarter", _t("This quarter"), (now) => quarter(now)],
        ["last_quarter", _t("Last quarter"), (now) => quarter(now, -1)],
        ["next_quarter", _t("Next quarter"), (now) => quarter(now, 1)],
        ["this_year", _t("This year"), (now) => year(now)],
        ["last_year", _t("Last year"), (now) => year(now, -1)],
        ["next_year", _t("Next year"), (now) => year(now, 1)],
        ["this_fiscal_year", _t("This fiscal year (Apr-Mar)"), (now) => fiscal(now)],
        ["last_fiscal_year", _t("Last fiscal year (Apr-Mar)"), (now) => fiscal(now, -1)],
        ["next_fiscal_year", _t("Next fiscal year (Apr-Mar)"), (now) => fiscal(now, 1)],
    ];
}

/**
 * ``[first day, last day]`` (luxon DateTimes, whole days) of a date state, or ``null`` when nothing is chosen. A state is
 * a ``preset``, a single ``day`` (``from``) or a range (``from`` and/or ``to``: an empty end is open, so one of the two
 * ends is ``null``).
 */
export function dateRange(state, now = DateTime.now()) {
    if (state.preset) {
        const preset = datePresets().find((p) => p[0] === state.preset);
        return preset ? preset[2](now) : null;
    }
    const zone = now.zone;
    const parse = (iso) => {
        const value = iso ? DateTime.fromISO(iso, { zone }) : null;
        return value && value.isValid ? value.startOf("day") : null;
    };
    const from = parse(state.from);
    if (state.mode === "day") {
        return from ? [from, from] : null;
    }
    const to = parse(state.to);
    return from || to ? [from, to] : null;
}

// --- the domain ---------------------------------------------------------------------------------------------------
const pad = (n) => String(n).padStart(2, "0");
const isoDay = (dt) => `${dt.year}-${pad(dt.month)}-${pad(dt.day)}`;
/** A moment in UTC, as Odoo stores a datetime: "YYYY-MM-DD HH:mm:ss". */
export function utcString(dt) {
    return dt.toUTC().toFormat("yyyy-MM-dd HH:mm:ss");
}

/**
 * The domain (a list) of a date filter. A ``date`` field is compared with days; a ``datetime`` field with the moments
 * where the first day starts and the day after the last one starts, in the time zone of the user, in UTC.
 */
export function dateDomain(fieldName, fieldType, state, now = DateTime.now()) {
    if (state.notSet) {
        return [[fieldName, "=", false]];
    }
    const range = dateRange(state, now);
    if (!range) {
        return null;
    }
    const [first, last] = range;
    const domain = [];
    if (fieldType === "date") {
        first && domain.push([fieldName, ">=", isoDay(first)]);
        last && domain.push([fieldName, "<=", isoDay(last)]);
    } else {
        first && domain.push([fieldName, ">=", utcString(first)]);
        last && domain.push([fieldName, "<", utcString(last.plus({ days: 1 }))]);
    }
    return domain;
}

/** Text of a date filter for the facet. */
export function dateDescription(state, now = DateTime.now()) {
    if (state.notSet) {
        return _t("not set");
    }
    if (state.preset) {
        const preset = datePresets().find((p) => p[0] === state.preset);
        return preset ? preset[1] : "";
    }
    const range = dateRange(state, now);
    if (!range) {
        return "";
    }
    const format = (dt) => dt.toLocaleString(DateTime.DATE_SHORT);
    const [first, last] = range;
    if (first && last) {
        return first.equals(last) ? format(first) : `${format(first)} - ${format(last)}`;
    }
    return first ? `${_t("from")} ${format(first)}` : `${_t("until")} ${format(last)}`;
}

/** Domain of a text or number filter. ``state``: ``{op, value, value2}``. */
export function operatorDomain(fieldName, state) {
    const { op } = state;
    if (op === "set") {
        return [[fieldName, "!=", false]];
    }
    if (op === "not_set") {
        return [[fieldName, "=", false]];
    }
    if (op === "between") {
        if (state.value === null || state.value === undefined || state.value === "" ||
            state.value2 === null || state.value2 === undefined || state.value2 === "") {
            return null;
        }
        return [[fieldName, ">=", state.value], [fieldName, "<=", state.value2]];
    }
    if (state.value === null || state.value === undefined || state.value === "") {
        return null;
    }
    return [[fieldName, op, state.value]];
}

export function operatorDescription(operators, state) {
    const operator = operators.find((o) => o.id === state.op);
    if (!operator) {
        return "";
    }
    if (!operator.needsValue) {
        return operator.label;
    }
    return operator.range ? `${state.value} - ${state.value2}` : `${operator.label} ${state.value}`;
}

/**
 * Domain of a many-values filter. ``state``: ``{values: [{value, label}], notSet}``. ``in`` the chosen values, or empty
 * when "not set" is ticked too.
 */
export function choiceDomain(fieldName, state) {
    const values = (state.values || []).map((v) => v.value);
    if (!values.length && !state.notSet) {
        return null;
    }
    if (!values.length) {
        return [[fieldName, "=", false]];
    }
    const some = [fieldName, "in", values];
    return state.notSet ? ["|", some, [fieldName, "=", false]] : [some];
}

export function choiceDescription(state) {
    const names = (state.values || []).map((v) => v.label);
    if (state.notSet) {
        names.push(_t("not set"));
    }
    return names.length > MAX_FACET_VALUES
        ? `${names.slice(0, MAX_FACET_VALUES).join(", ")} +${names.length - MAX_FACET_VALUES}`
        : names.join(", ");
}

export function booleanDomain(fieldName, state) {
    if (state.value === true) {
        return [[fieldName, "=", true]];
    }
    if (state.value === false) {
        return [[fieldName, "=", false]];
    }
    return null;
}

/**
 * ``{domain, description}`` of a filter state of the given kind, or ``null`` when the state selects nothing yet.
 * ``field`` is the field of the view (name, type, string).
 */
export function buildFilter(kind, field, state, now = DateTime.now()) {
    let domain = null;
    let text = "";
    switch (kind) {
        case "text":
            domain = operatorDomain(field.name, state);
            text = operatorDescription(textOperators(), state);
            break;
        case "number":
            domain = operatorDomain(field.name, state);
            text = operatorDescription(numberOperators(), state);
            break;
        case "boolean":
            domain = booleanDomain(field.name, state);
            text = state.value ? _t("yes") : _t("no");
            break;
        case "date":
            domain = dateDomain(field.name, field.type, state, now);
            text = dateDescription(state, now);
            break;
        case "choice":
            domain = choiceDomain(field.name, state);
            text = choiceDescription(state);
            break;
    }
    if (!domain) {
        return null;
    }
    return { domain, description: `${field.string || field.name}: ${text}` };
}
