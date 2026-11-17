/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onMounted, onWillUnmount, proxy, signal, useProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { buildFilter, datePresets, numberOperators, textOperators } from "./filter_logic";

const PAGE = 30;
const SEARCH_DELAY = 250;

/**
 * The content of the popover of a column filter. ``kind`` decides the form: operators and a value (text, number), quick
 * dates or a day or a range (date), a Yes / No choice (boolean), or checkboxes with a search box (selection, many2one,
 * many2many): the ticked values stay together at the top, untick one to drop it.
 */
export class DwoHeaderFilterPopover extends Component {
    static template = "dwo_listview_header_filter.Popover";
    // Odoo 20 (Owl 3): no static props (field, kind, initial, onApply, onReset, close)
    props = useProps();

    setup() {
        this.orm = useService("orm");
        this.inputRef = signal.ref();
        const { kind, initial } = this.props;
        const state = initial ? JSON.parse(JSON.stringify(initial)) : {};
        this.state = proxy({
            // text and number
            op: state.op || (kind === "number" ? "=" : "ilike"),
            value: state.value ?? (kind === "boolean" ? null : ""),
            value2: state.value2 ?? "",
            // date
            preset: state.preset || null,
            mode: state.mode || "day",
            from: state.from || "",
            to: state.to || "",
            notSet: Boolean(state.notSet),
            // choice
            selected: state.values || [],
            options: [],
            search: "",
            limit: PAGE,
            more: false,
            loading: false,
        });
        this.presets = datePresets();
        this.operators = kind === "number" ? numberOperators() : textOperators();
        this.timer = null;
        onMounted(() => {
            if (this.props.kind === "choice") {
                this.load();
            }
            this.inputRef()?.focus();
        });
        onWillUnmount(() => clearTimeout(this.timer));
    }

    // --- the state that is applied -------------------------------------------------------------------------------
    get filterState() {
        const s = this.state;
        switch (this.props.kind) {
            case "text":
            case "number":
                return { op: s.op, value: s.value, value2: s.value2 };
            case "boolean":
                return { value: s.value };
            case "date":
                return s.preset
                    ? { preset: s.preset }
                    : s.notSet
                      ? { notSet: true }
                      : { mode: s.mode, from: s.from, to: s.mode === "day" ? "" : s.to };
            case "choice":
                return { values: s.selected.map((v) => ({ ...v })), notSet: s.notSet };
        }
        return {};
    }

    get canApply() {
        return Boolean(buildFilter(this.props.kind, this.props.field, this.filterState));
    }

    get hasFilter() {
        return Boolean(this.props.initial);
    }

    apply() {
        if (this.canApply && this.props.onApply(this.filterState) !== false) {
            this.props.close();
        }
    }

    reset() {
        this.props.onReset();
        this.props.close();
    }

    onKeydown(ev) {
        if (ev.key === "Enter" && ev.target.tagName !== "BUTTON") {
            ev.preventDefault();
            this.apply();
        } else if (ev.key === "Escape") {
            this.props.close();
        }
    }

    // --- text and number ----------------------------------------------------------------------------------------
    get operator() {
        return this.operators.find((o) => o.id === this.state.op) || this.operators[0];
    }

    onOperator(ev) {
        this.state.op = ev.target.value;
        this.inputRef()?.focus();
    }

    onValue(ev) {
        const raw = ev.target.value;
        this.state.value = this.props.kind === "number" ? (raw === "" ? "" : Number(raw)) : raw;
    }

    onValue2(ev) {
        const raw = ev.target.value;
        this.state.value2 = raw === "" ? "" : Number(raw);
    }

    get numberStep() {
        return this.props.field.type === "integer" ? "1" : "any";
    }

    // --- boolean ------------------------------------------------------------------------------------------------
    chooseBoolean(value) {
        this.state.value = value;
        this.apply();
    }

    // --- date ---------------------------------------------------------------------------------------------------
    choosePreset(id) {
        this.state.preset = id;
        this.state.notSet = false;
        this.apply();
    }

    onDate(name, ev) {
        this.state[name] = ev.target.value;
        this.state.preset = null;
        this.state.notSet = false;
    }

    setMode(mode) {
        this.state.mode = mode;
        this.state.preset = null;
        this.state.notSet = false;
    }

    toggleNotSetDate(ev) {
        this.state.notSet = ev.target.checked;
        if (this.state.notSet) {
            this.state.preset = null;
        }
    }

    // --- choice -------------------------------------------------------------------------------------------------
    get canBeNotSet() {
        return !this.props.field.required;
    }

    isSelected(value) {
        return this.state.selected.some((v) => v.value === value);
    }

    /** The options that are not ticked yet (the ticked ones are in the area above). */
    get freeOptions() {
        return this.state.options.filter((o) => !this.isSelected(o.value));
    }

    pick(option) {
        this.state.selected.push({ value: option.value, label: option.label });
    }

    drop(value) {
        this.state.selected = this.state.selected.filter((v) => v.value !== value);
    }

    onSearch(ev) {
        this.state.search = ev.target.value;
        this.state.limit = PAGE;
        clearTimeout(this.timer);
        this.timer = setTimeout(() => this.load(), SEARCH_DELAY);
    }

    showMore() {
        this.state.limit += PAGE;
        this.load();
    }

    async load() {
        const { field } = this.props;
        const term = this.state.search.trim();
        if (field.type === "selection") {
            const needle = term.toLowerCase();
            this.state.options = (field.selection || [])
                .filter(([value, label]) => value !== false && (!needle || String(label).toLowerCase().includes(needle)))
                .map(([value, label]) => ({ value, label }));
            this.state.more = false;
            return;
        }
        this.state.loading = true;
        try {
            const limit = this.state.limit;
            const rows = await this.orm.call(field.relation, "name_search", [], {
                name: term, args: [], operator: "ilike", limit: limit + 1,
            });
            this.state.more = rows.length > limit;
            this.state.options = rows.slice(0, limit).map(([id, name]) => ({ value: id, label: name }));
        } catch {
            this.state.options = [];
            this.state.more = false;
        } finally {
            this.state.loading = false;
        }
    }
}
