/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onWillStart, onWillUnmount, useState } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { Domain } from "@web/core/domain";
import { DomainSelector } from "@web/core/domain_selector/domain_selector";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { ICON_CHOICES, PRESET_LABELS, suggestVisual, widgetIcon } from "./utils";
import { DwoSelect, placePopup } from "./select";
import { WidgetCard } from "./widget_card";

const AGG_LABELS = {
    sum: _t("Sum"),
    avg: _t("Average"),
    min: _t("Minimum"),
    max: _t("Maximum"),
    count_distinct: _t("Distinct count"),
};
const DATE_TYPES = ["date", "datetime"];
const VISUAL_ICONS = {
    kpi: "fa-hashtag", table: "fa-table", bar: "fa-bar-chart", line: "fa-line-chart", area: "fa-area-chart",
    pie: "fa-pie-chart", doughnut: "fa-circle-o-notch", pivot: "fa-th",
};
const OPTION_LABELS = {
    format: _t("Number format"), decimals: _t("Decimals"), legend: _t("Legend"), stacked: _t("Stacked"),
    horizontal: _t("Horizontal bars"), smooth: _t("Smooth lines"), show_totals: _t("Show totals"),
    y_min: _t("Axis minimum"), y_max: _t("Axis maximum"), goal: _t("Goal"), trend_good: _t("Good news is"), prefix: _t("Prefix"), suffix: _t("Suffix"),
    show_values: _t("Show values"), target: _t("Target line"), percent: _t("100% stacked"),
    show_percent: _t("Show percentages"), other: _t("Group the rest as “Other”"), heatmap: _t("Heat map"),
    open_records: _t("Click a row to open it"),
};
const ENUM_LABELS = {
    up: _t("A rise"), down: _t("A fall"), none: _t("Hidden"), top: _t("Top"), bottom: _t("Bottom"), left: _t("Left"),
    right: _t("Right"), number: _t("Number"), currency: _t("Currency"), percent: _t("Percent"),
};
const RECENT_KEY = "dwo_dashboard.recent_datasets";

function recentDatasets() {
    try {
        return JSON.parse(browser.localStorage.getItem(RECENT_KEY) || "[]");
    } catch {
        return [];
    }
}

function rememberDataset(ref) {
    try {
        const next = [ref, ...recentDatasets().filter((r) => r !== ref)].slice(0, 5);
        browser.localStorage.setItem(RECENT_KEY, JSON.stringify(next));
    } catch {
        // private mode: nothing remembered, nothing lost
    }
}

/** Explore: pick a dataset, a visual type, drop fields in its wells, see the result, add it to the page. The same panel edits
 * an existing widget. Everything shown (datasets, fields) is what the viewer may read: the server answers for the caller. */
export class ExplorePanel extends Component {
    static template = "dwo_dashboard.ExplorePanel";
    static components = { WidgetCard, DomainSelector, DwoSelect };
    static props = {
        pageId: { type: Number, optional: true },
        widget: { type: [Object, { value: null }], optional: true },
        pageDatasets: { type: Array, optional: true },
        filters: Array,
        onApply: Function,
        onClose: Function,
    };

    setup() {
        this.orm = useService("orm");
        this.aggLabels = AGG_LABELS;
        this.presetLabels = Object.entries(PRESET_LABELS).filter(([key]) => key !== "all");
        this.state = useState({
            datasets: [], visuals: {}, dataset: "", kind: "orm", fields: [], related: {}, metrics: [], model: "", type: "bar",
            wells: {}, where: [], options: {}, limit: "", orderKey: "", title: "", icon: "", iconMenu: false,
            showFilter: false, preview: { loading: false, entry: null }, search: "", datasetOpen: false,
            compare: { enabled: false, field: "", period: "this_month", against: "previous_period" },
            trend: { enabled: false, field: "", interval: "month", points: 12 },
        });
        this.timer = null;
        this.token = 0;
        this.previousType = null;
        onWillStart(async () => {
            const [datasets, registry] = await Promise.all([
                this.orm.call("dwo.dashboard.explore", "list_datasets", []),
                this.orm.call("dwo.dashboard.spec", "get_registry", []),
            ]);
            this.state.datasets = datasets;
            this.state.visuals = registry.visuals;
            if (this.props.widget) {
                await this.loadWidget(this.props.widget);
            } else {
                this.previousType = this.state.type;
            }
        });
        onWillUnmount(() => clearTimeout(this.timer));
    }

    // -------------------------------------------------------------------------------------------- loading
    async loadWidget(widget) {
        await this.chooseDataset(widget.dataset, false);
        const s = this.state;
        s.type = widget.type;
        this.previousType = widget.type;
        s.title = widget.title || "";
        s.icon = widget.icon || "";
        s.wells = JSON.parse(JSON.stringify(widget.wells || {}));
        for (const value of Object.values(s.wells)) {
            for (const item of Array.isArray(value) ? value : [value]) {
                if (item && item.field && item.field.includes(".")) {
                    const parts = item.field.split(".");
                    parts.pop();
                    item.rel = parts.join(".");
                    for (let k = 1; k <= parts.length; k++) {
                        await this.loadRelated(parts.slice(0, k).join("."));
                    }
                }
            }
        }
        s.where = JSON.parse(JSON.stringify(widget.where || []));
        s.options = JSON.parse(JSON.stringify(widget.options || {}));
        if (widget.trend) {
            s.trend = { enabled: true, field: widget.trend.field, interval: widget.trend.interval || "month",
                        points: widget.trend.points || 12 };
        }
        if (widget.compare) {
            s.compare = { enabled: true, field: widget.compare.field, period: widget.compare.period || "this_month",
                          against: widget.compare.against || "previous_period" };
        }
        s.limit = widget.limit || "";
        const first = (widget.order || [])[0];
        s.orderKey = first ? (first.field ? `d:${first.field}:${first.dir || "asc"}` : `m:${first.measure}:${first.dir || "asc"}`) : "";
        this.schedulePreview();
    }

    async chooseDataset(ref, reset = true) {
        const s = this.state;
        s.dataset = ref;
        if (!ref) {
            s.fields = [];
            return;
        }
        const description = await this.orm.call("dwo.dashboard.explore", "describe_dataset", [ref]);
        s.fields = description.fields;
        s.related = {};
        s.kind = description.kind || "orm";
        s.metrics = description.metrics || [];
        s.model = description.model;
        s.label = description.label;
        if (reset) {
            s.wells = {};
            s.where = [];
            s.orderKey = "";
            this.state.type = this.state.type || "bar";
            this.ensureWells();
            this.schedulePreview();
        }
    }

    // ------------------------------------------------------------------------------------- dataset combobox
    get datasetLabel() {
        const d = this.state.datasets.find((x) => x.ref === this.state.dataset);
        return d ? d.label : "";
    }

    /** Matching datasets: the ones already on this page first, then the recent ones, then the rest. */
    get datasetChoices() {
        const q = this.state.search.trim().toLowerCase();
        const onPage = this.props.pageDatasets || [];
        const recent = recentDatasets();
        const rank = (d) => (onPage.includes(d.ref) ? 0 : recent.includes(d.ref) ? 1 : 2);
        return this.state.datasets
            .filter((d) => !q || d.label.toLowerCase().includes(q) || d.model.includes(q))
            .map((d) => ({ ...d, group: rank(d) }))
            .sort((a, b) => a.group - b.group || a.label.localeCompare(b.label))
            .slice(0, 12);
    }

    groupTitle(group) {
        return group === 0 ? _t("On this page") : group === 1 ? _t("Recent") : _t("All data");
    }

    openDatasets(ev) {
        this.state.datasetStyle = placePopup(ev.currentTarget.getBoundingClientRect(), { minWidth: 260, height: 280 });
        this.state.datasetOpen = true;
        this.state.search = "";
    }

    pickDataset(d) {
        this.state.datasetOpen = false;
        this.state.search = "";
        rememberDataset(d.ref);
        this.chooseDataset(d.ref);
    }

    toggleIconMenu(ev) {
        if (!this.state.iconMenu) {
            this.state.iconStyle = placePopup(ev.currentTarget.getBoundingClientRect(), { minWidth: 280, height: 240 });
        }
        this.state.iconMenu = !this.state.iconMenu;
    }

    closeDatasets() {
        // a blur happens before the click on an option: wait one tick
        setTimeout(() => (this.state.datasetOpen = false), 150);
    }

    visualIcon(name) {
        return VISUAL_ICONS[name] || "fa-puzzle-piece";
    }

    enumLabel(value) {
        return ENUM_LABELS[value] || value;
    }

    optionLabel(name) {
        return OPTION_LABELS[name] || name.replace(/_/g, " ");
    }

    /** One selector per required well as soon as a visual and a dataset are chosen; "Count" already filled in. */
    ensureWells() {
        for (const well of this.wellList) {
            if (well.min >= 1 && !this.items(well).length) {
                this.addItem(well);
            }
        }
    }

    // ----------------------------------------------------------------------------------------- the visual
    get vdef() {
        return this.state.visuals[this.state.type];
    }

    get visualTypes() {
        return Object.entries(this.state.visuals).map(([name, v]) => ({ name, label: v.label }));
    }

    setType(name) {
        const keep = this.state.wells;
        this.state.type = name;
        this.state.options = {};
        this.state.orderKey = "";
        if (!this.state.visuals[name].compare) {
            this.state.compare.enabled = false;
        }
        if (!this.state.visuals[name].trend) {
            this.state.trend.enabled = false;
        }
        // keep what still fits the new visual: dimensions stay dimensions, measures stay measures
        const fresh = {};
        const old = Object.entries(this.vdefOf(this.previousType || name).wells || {});
        const dims = old.filter(([, w]) => w.accepts === "dimension").flatMap(([n]) => [].concat(keep[n] || []));
        const measures = old.filter(([, w]) => w.accepts === "measure").flatMap(([n]) => [].concat(keep[n] || []));
        for (const well of Object.entries(this.state.visuals[name].wells).map(([n, w]) => ({ name: n, ...w }))) {
            const source = well.accepts === "dimension" ? dims : well.accepts === "measure" ? measures : [];
            const take = source.splice(0, well.max);
            if (take.length) {
                fresh[well.name] = well.max === 1 ? take[0] : take;
            }
        }
        this.state.wells = fresh;
        this.previousType = name;
        this.ensureWells();
        this.schedulePreview();
    }

    vdefOf(name) {
        return this.state.visuals[name] || { wells: {} };
    }

    get wellList() {
        return Object.entries(this.vdef ? this.vdef.wells : {}).map(([name, w]) => ({ name, ...w }));
    }

    isMulti(well) {
        return well.max !== 1;
    }

    // ----------------------------------------------------------------------------------------------- wells
    fieldsFor(well, agg) {
        const all = this.state.fields;
        if (well.accepts === "dimension") {
            return all.filter((f) => f.dimension);
        }
        if (well.accepts === "column") {
            return all.filter((f) => f.column);
        }
        return all.filter((f) => f.aggs.includes(agg));
    }

    items(well) {
        const value = this.state.wells[well.name];
        if (this.isMulti(well)) {
            return value || [];
        }
        return value ? [value] : [];
    }

    canAdd(well) {
        return this.items(well).length < well.max;
    }

    addItem(well) {
        const first = this.state.kind === "blend" && this.state.metrics[0];
        const item = well.accepts === "measure"
            ? first ? { metric: first.name, agg: "", field: "" } : { agg: "count", field: "" }  // a blend has metrics only
            : { field: "", interval: "" };
        // (a measure starts as "Count": the preview works as soon as the other selectors are filled)
        if (this.isMulti(well)) {
            this.state.wells[well.name] = [...(this.state.wells[well.name] || []), item];
        } else {
            this.state.wells[well.name] = item;
        }
    }

    canRemove(well) {
        return this.items(well).length > well.min;
    }

    removeItem(well, index) {
        if (this.isMulti(well)) {
            this.state.wells[well.name] = this.items(well).filter((_, i) => i !== index);
        } else {
            delete this.state.wells[well.name];
        }
        this.schedulePreview();
    }

    /** A field of the dataset, or of a record it points to ("partner_id.country_id": loaded by ``loadRelated``). */
    field(name) {
        const own = this.state.fields.find((f) => f.name === name);
        if (own || !name || !name.includes(".")) {
            return own;
        }
        const parts = name.split(".");
        const sub = parts.pop();
        const found = (this.state.related[parts.join(".")] || []).find((f) => f.name === sub);
        return found ? { ...found, name, label: `${this.pathLabel(parts)} › ${found.label}` } : undefined;
    }

    pathLabel(parts) {
        let label = "";
        let fields = this.state.fields;
        parts.forEach((part, i) => {
            const f = fields.find((x) => x.name === part);
            label = label ? `${label} › ${f ? f.label : part}` : f ? f.label : part;
            fields = this.state.related[parts.slice(0, i + 1).join(".")] || [];
        });
        return label;
    }

    /** The records a many2one path points to: their fields are loaded once, as the caller can read them. */
    async loadRelated(path) {
        if (!this.state.related[path]) {
            const answer = await this.orm.call("dwo.dashboard.explore", "describe_related", [this.state.dataset, path]);
            this.state.related[path] = answer.fields;
        }
    }

    /** Every level of the selectors of a dimension or a column: its own fields, then those of the record it points to... */
    levels(well, item) {
        const segments = item.rel ? item.rel.split(".") : [];
        const out = [];
        for (let k = 0; k <= segments.length; k++) {
            const prefix = segments.slice(0, k).join(".");
            const fields = k === 0 ? this.state.fields : this.state.related[prefix] || [];
            const wanted = (f) => (well.accepts === "dimension" ? f.dimension : f.column);
            const options = [
                ...fields.filter(wanted).map((f) => ({ value: f.name, label: f.label })),
                ...fields.filter((f) => f.expandable).map((f) => ({ value: "rel:" + f.name, label: `${f.label} ›` })),
            ];
            let selected = "";
            if (k < segments.length) {
                selected = "rel:" + segments[k];
            } else if (item.field && item.field.split(".").length === k + 1 && item.field.startsWith(prefix)) {
                selected = item.field.split(".")[k];
            }
            out.push({ level: k, options, selected });
        }
        return out;
    }

    async pick(item, level, ev) {
        const value = ev.target.value;
        const prefix = (item.rel ? item.rel.split(".") : []).slice(0, level);
        if (value.startsWith("rel:")) {
            item.rel = [...prefix, value.slice(4)].join(".");
            item.field = "";
            item.interval = "";
            await this.loadRelated(item.rel);
            return;
        }
        item.rel = prefix.join(".");
        item.field = [...prefix, value].join(".");
        item.interval = this.isDate(item) ? item.interval || "month" : "";
        this.schedulePreview();
    }

    isDate(item) {
        const f = this.field(item.field);
        return !!f && DATE_TYPES.includes(f.type);
    }

    setField(item, ev) {
        item.field = ev.target.value;
        item.interval = this.isDate(item) ? item.interval || "month" : "";
        this.schedulePreview();
    }

    metric(name) {
        return this.state.metrics.find((m) => m.name === name);
    }

    /** The "kind" selector of a value: a metric of the dataset ("metric:name") or an aggregate of a field. */
    setAgg(item, ev) {
        const value = ev.target.value;
        if (value.startsWith("metric:")) {
            item.metric = value.slice(7);
            item.agg = "";
            item.field = "";
            this.schedulePreview();
            return;
        }
        item.metric = "";
        item.agg = value;
        if (item.agg === "count") {
            item.field = "";
        } else if (!this.fieldsFor({ accepts: "measure" }, item.agg).some((f) => f.name === item.field)) {
            item.field = "";
        }
        this.schedulePreview();
    }

    setInterval(item, ev) {
        item.interval = ev.target.value;
        this.schedulePreview();
    }

    // ---------------------------------------------------------------------- choices of the autocomplete selectors
    get aggOptions() {
        const aggs = this.aggChoices.map((a) => ({ ...a, group: "" }));
        const count = { value: "count", label: _t("Count") };
        if (!this.state.metrics.length) {
            return [count, ...aggs];
        }
        const metrics = this.state.metrics.map((m) => ({ value: "metric:" + m.name, label: m.label, group: _t("Metrics of this data") }));
        const fieldGroup = _t("Aggregate of a field");
        return this.state.kind === "orm"
            ? [...metrics, ...[count, ...aggs].map((o) => ({ ...o, group: fieldGroup }))]
            : metrics;
    }

    aggValue(item) {
        return item.metric ? "metric:" + item.metric : item.agg;
    }

    fieldOptions(well, item) {
        return this.fieldsFor(well, item.agg).map((f) => ({ value: f.name, label: f.label }));
    }

    get intervalOptions() {
        return this.intervals.map((i) => ({ value: i, label: i }));
    }

    get trendIntervalOptions() {
        return ["day", "week", "month"].map((i) => ({ value: i, label: i }));
    }

    get dateFieldOptions() {
        return this.dateFields.map((f) => ({ value: f.name, label: f.label }));
    }

    get againstOptions() {
        return [
            { value: "previous_period", label: _t("the previous period") },
            { value: "previous_year", label: _t("the same period last year") },
        ];
    }

    get periodOptions() {
        return this.presetLabels.map(([value, label]) => ({ value, label }));
    }

    get orderOptions() {
        return this.orderChoices.map((o) => ({ value: o.key, label: o.label }));
    }

    setOrderKey(ev) {
        this.state.orderKey = ev.target.value;
        this.schedulePreview();
    }

    enumOptions(opt) {
        return [{ value: "", label: _t("Default") }, ...opt.values.map((v) => ({ value: v, label: this.enumLabel(v) }))];
    }

    get aggChoices() {
        return Object.entries(AGG_LABELS).map(([value, label]) => ({ value, label }));
    }

    get intervals() {
        return ["day", "week", "month", "quarter", "year"];
    }

    get hint() {
        const first = this.firstDimensionField();
        const suggested = suggestVisual(this.state.type, first, this.cleanMeasures().length);
        return suggested && suggested !== this.state.type && this.state.visuals[suggested] ? suggested : "";
    }

    firstDimensionField() {
        for (const well of this.wellList) {
            if (well.accepts === "dimension") {
                const item = this.items(well)[0];
                if (item && item.field) {
                    return this.field(item.field);
                }
            }
        }
        return null;
    }

    cleanMeasures() {
        return this.wellList
            .filter((w) => w.accepts === "measure")
            .flatMap((w) => this.items(w))
            .filter((i) => i.metric || i.agg === "count" || i.field);
    }

    // ---------------------------------------------------------------------------------- build the widget
    cleanItem(well, item) {
        if (well.accepts === "measure") {
            if (item.metric) {
                return { metric: item.metric };
            }
            if (item.agg === "count" && !item.field) {
                return { agg: "count" };
            }
            return item.field ? { field: item.field, agg: item.agg } : null;
        }
        if (!item.field) {
            return null;
        }
        if (well.accepts === "dimension") {
            return this.isDate(item) ? { field: item.field, interval: item.interval || "month" } : { field: item.field };
        }
        return { field: item.field };
    }

    buildWidget() {
        const s = this.state;
        const vdef = this.vdef;
        if (!s.dataset || !vdef) {
            return null;
        }
        const wells = {};
        for (const well of this.wellList) {
            const clean = this.items(well).map((i) => this.cleanItem(well, i)).filter(Boolean);
            if (clean.length < well.min) {
                return null;
            }
            if (clean.length) {
                wells[well.name] = this.isMulti(well) ? clean : clean[0];
            }
        }
        const widget = { type: s.type, dataset: s.dataset, wells };
        if (this.props.widget) {
            widget.id = this.props.widget.id;
        }
        if (s.title.trim()) {
            widget.title = s.title.trim();
        }
        if (s.icon) {
            widget.icon = s.icon; // without one, the card shows the icon of its type
        }
        if (s.where.length) {
            widget.where = s.where;
        }
        const options = {};
        for (const [name, desc] of Object.entries(vdef.options || {})) {
            if (s.options[name] !== undefined && s.options[name] !== "" && s.options[name] !== false && desc.kind !== "colors") {
                options[name] = s.options[name];
            }
        }
        if (Object.keys(options).length) {
            widget.options = options;
        }
        if (vdef.limit && s.limit) {
            widget.limit = parseInt(s.limit, 10);
        }
        const compareField = vdef.compare === "series" ? (this.axisDate || {}).field : s.compare.field;
        if (vdef.compare && s.compare.enabled && compareField) {
            widget.compare = { field: compareField, period: s.compare.period, against: s.compare.against };
        }
        if (vdef.trend && s.trend.enabled && s.trend.field) {
            widget.trend = { field: s.trend.field, interval: s.trend.interval, points: s.trend.points };
        }
        if (s.orderKey) {
            const parts = s.orderKey.split(":"); // "m:amount_total:sum:desc": the name of a measure holds a colon too
            const kind = parts[0];
            const dir = parts[parts.length - 1];
            const name = parts.slice(1, -1).join(":");
            widget.order = [kind === "d" ? { field: name, dir } : { measure: name, dir }];
        }
        return widget;
    }

    get orderChoices() {
        const out = [{ key: "", label: _t("Default") }];
        const widget = this.buildWidget();
        if (!widget) {
            return out;
        }
        for (const well of this.wellList) {
            for (const item of this.items(well)) {
                const clean = this.cleanItem(well, item);
                if (!clean) {
                    continue;
                }
                if (well.accepts === "measure") {
                    const metric = clean.metric ? this.metric(clean.metric) : null;
                    const key = clean.metric || (clean.field ? `${clean.field}:${clean.agg}` : "__count");
                    const label = metric ? metric.label : clean.field ? `${this.field(clean.field).label} (${clean.agg})` : _t("Count");
                    out.push({ key: `m:${key}:desc`, label: `${label} ↓` }, { key: `m:${key}:asc`, label: `${label} ↑` });
                } else if (well.accepts !== "measure") {
                    const label = this.field(clean.field).label;
                    out.push({ key: `d:${clean.field}:asc`, label: `${label} ↑` }, { key: `d:${clean.field}:desc`, label: `${label} ↓` });
                }
            }
        }
        return out;
    }

    get complete() {
        return !!this.buildWidget();
    }

    // ---------------------------------------------------------------------------------------------- options
    setOption(name, desc, ev) {
        const t = ev.target;
        const parse = {
            bool: () => t.checked,
            int: () => parseInt(t.value, 10) || "",
            number: () => (t.value === "" ? "" : Number(t.value)),
        };
        this.state.options[name] = (parse[desc.kind] || (() => t.value))();
        this.schedulePreview();
    }

    get optionList() {
        return Object.entries(this.vdef && this.vdef.options ? this.vdef.options : {})
            .filter(([, desc]) => desc.kind !== "colors")
            .map(([name, desc]) => ({ name, ...desc }));
    }

    // ---------------------------------------------------------------------- compare with a previous period
    get dateFields() {
        return this.state.fields.filter((f) => f.intervals.length && f.dimension);
    }

    /** A KPI picks its own date; a line or area chart compares on its axis (the date it is already drawn over). */
    get compareOnAxis() {
        return this.vdef && this.vdef.compare === "series";
    }

    get axisDate() {
        const well = this.wellList.find((w) => w.name === "axis");
        const axis = well ? this.items(well)[0] : null;
        return axis && axis.field && this.isDate(axis) ? axis : null;
    }

    get canCompare() {
        return !!this.vdef && !!this.vdef.compare && (this.compareOnAxis ? !!this.axisDate : this.dateFields.length > 0);
    }

    get preferredDate() {
        const preferred = this.dateFields.find((f) => ["date_order", "create_date"].includes(f.name));
        return (preferred || this.dateFields[0] || { name: "" }).name;
    }

    toggleCompare(ev) {
        const c = this.state.compare;
        c.enabled = ev.target.checked;
        if (c.enabled && !c.field) {
            c.field = this.preferredDate;
        }
        this.schedulePreview();
    }

    toggleTrend(ev) {
        const t = this.state.trend;
        t.enabled = ev.target.checked;
        if (t.enabled && !t.field) {
            t.field = this.preferredDate;
        }
        this.schedulePreview();
    }

    setTrend(key, ev) {
        this.state.trend[key] = key === "points" ? parseInt(ev.target.value, 10) || 12 : ev.target.value;
        this.schedulePreview();
    }

    setCompare(key, ev) {
        this.state.compare[key] = ev.target.value;
        this.schedulePreview();
    }

    // ----------------------------------------------------------------------------------- filter (domain)
    get domainString() {
        try {
            return new Domain(this.state.where).toString();
        } catch {
            return "[]";
        }
    }

    onDomain(str) {
        try {
            this.state.where = new Domain(str).toJson();
        } catch {
            return;
        }
        this.schedulePreview();
    }

    // ----------------------------------------------------------------------------------------------- preview
    schedulePreview() {
        clearTimeout(this.timer);
        this.timer = setTimeout(() => this.preview(), 350);
    }

    async preview() {
        const widget = this.buildWidget();
        const p = this.state.preview;
        if (!widget) {
            p.entry = null;
            return;
        }
        const token = ++this.token;
        p.loading = true;
        const answer = await this.orm.call("dwo.dashboard.engine", "run_preview", [widget, this.props.filters, {}, this.props.pageId]);
        if (token !== this.token) {
            return;
        }
        p.loading = false;
        p.entry = answer.ok ? { loading: false, result: answer.result } : { loading: false, error: answer.error };
    }

    get previewWidget() {
        return this.buildWidget() || { type: this.state.type };
    }

    get iconChoices() {
        return ICON_CHOICES;
    }

    get currentIcon() {
        return this.state.icon || widgetIcon({ type: this.state.type });
    }

    setIcon(icon) {
        this.state.icon = icon;
        this.state.iconMenu = false;
    }

    /** "Count by Country", "Sum of Total by Month": written into the spec when the title is left empty. */
    get autoTitle() {
        const parts = [];
        const measure = this.cleanMeasures()[0];
        const dim = this.firstDimensionField();
        if (measure) {
            const field = measure.field ? this.field(measure.field) : null;
            const metric = measure.metric ? this.metric(measure.metric) : null;
            parts.push(metric ? metric.label : field ? `${this.aggLabels[measure.agg] || measure.agg} ${_t("of")} ${field.label}` : _t("Count"));
            if (!field && !dim && this.state.label) {
                parts.push(`· ${this.state.label}`);
            }
        }
        if (dim && this.state.type !== "kpi") {
            parts.push(`${_t("by")} ${dim.label}`);
        }
        return parts.length ? parts.join(" ") : this.state.label || "";
    }

    apply() {
        const widget = this.buildWidget();
        if (widget) {
            if (!widget.title) {
                widget.title = this.autoTitle;
            }
            this.props.onApply(widget);
        }
    }

    // ---------------------------------------------------------------------------------------- dataset list
    get filteredDatasets() {
        const q = this.state.search.trim().toLowerCase();
        return q ? this.state.datasets.filter((d) => d.label.toLowerCase().includes(q) || d.model.includes(q)) : this.state.datasets;
    }
}
