/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

const PRESET_LABELS = {
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

/** The filters of a page. ``values``: {filter id: value}; relation filters hold [{id, name}] so chips can be drawn. */
export class FilterBar extends Component {
    static template = "dwo_dashboard.FilterBar";
    static props = { filters: Array, values: Object, onChange: Function };

    setup() {
        this.orm = useService("orm");
        this.state = useState({ openId: null, query: "", options: [] });
        this.presets = PRESET_LABELS;
    }

    presetOf(flt) {
        return this.props.values[flt.id] || flt.default || "all";
    }

    label(flt) {
        return flt.label || flt.id;
    }

    setPreset(flt, ev) {
        this.props.onChange(flt.id, ev.target.value);
    }

    chips(flt) {
        return this.props.values[flt.id] || [];
    }

    selectionValue(flt) {
        const v = this.props.values[flt.id];
        return Array.isArray(v) ? v : v ? [v] : flt.default ? [flt.default] : [];
    }

    toggleValue(flt, value) {
        const current = this.selectionValue(flt);
        const next = current.includes(value) ? current.filter((v) => v !== value) : [...current, value];
        this.props.onChange(flt.id, next);
    }

    async open(flt) {
        this.state.openId = flt.id;
        this.state.query = "";
        await this.search(flt, "");
    }

    async search(flt, query) {
        this.state.query = query;
        const found = await this.orm.call("dwo.dashboard.explore", "filter_options", [flt.model, query, 12]);
        this.state.options = found.map(([id, name]) => ({ id, name }));
    }

    pick(flt, option) {
        const current = this.chips(flt);
        if (!current.some((c) => c.id === option.id)) {
            this.props.onChange(flt.id, [...current, option]);
        }
        this.state.openId = null;
    }

    unpick(flt, option) {
        this.props.onChange(flt.id, this.chips(flt).filter((c) => c.id !== option.id));
    }
}
