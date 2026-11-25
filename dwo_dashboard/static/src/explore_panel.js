/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onWillStart, onWillUnmount, useState } from "@odoo/owl";
import { Domain } from "@web/core/domain";
import { DomainSelector } from "@web/core/domain_selector/domain_selector";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { suggestVisual } from "./utils";
import { WidgetCard } from "./widget_card";

const AGG_LABELS = {
    sum: _t("Sum"),
    avg: _t("Average"),
    min: _t("Minimum"),
    max: _t("Maximum"),
    count_distinct: _t("Distinct count"),
};
const DATE_TYPES = ["date", "datetime"];

/** Explore: pick a dataset, a visual type, drop fields in its wells, see the result, add it to the page. The same panel edits
 * an existing widget. Everything shown (datasets, fields) is what the viewer may read: the server answers for the caller. */
export class ExplorePanel extends Component {
    static template = "dwo_dashboard.ExplorePanel";
    static components = { WidgetCard, DomainSelector };
    static props = {
        widget: { type: [Object, { value: null }], optional: true },
        filters: Array,
        onApply: Function,
        onClose: Function,
    };

    setup() {
        this.orm = useService("orm");
        this.aggLabels = AGG_LABELS;
        this.state = useState({
            datasets: [], visuals: {}, dataset: "", fields: [], model: "", type: "bar",
            wells: {}, where: [], options: {}, limit: "", orderKey: "", title: "",
            showFilter: false, preview: { loading: false, entry: null }, search: "",
        });
        this.timer = null;
        this.token = 0;
        onWillStart(async () => {
            const [datasets, registry] = await Promise.all([
                this.orm.call("dwo.dashboard.explore", "list_datasets", []),
                this.orm.call("dwo.dashboard.spec", "get_registry", []),
            ]);
            this.state.datasets = datasets;
            this.state.visuals = registry.visuals;
            if (this.props.widget) {
                await this.loadWidget(this.props.widget);
            }
        });
        onWillUnmount(() => clearTimeout(this.timer));
    }

    // -------------------------------------------------------------------------------------------- loading
    async loadWidget(widget) {
        await this.chooseDataset(widget.dataset, false);
        const s = this.state;
        s.type = widget.type;
        s.title = widget.title || "";
        s.wells = JSON.parse(JSON.stringify(widget.wells || {}));
        s.where = JSON.parse(JSON.stringify(widget.where || []));
        s.options = JSON.parse(JSON.stringify(widget.options || {}));
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
        s.model = description.model;
        if (reset) {
            s.wells = {};
            s.where = [];
            s.orderKey = "";
            this.state.type = this.state.type || "bar";
            this.schedulePreview();
        }
    }

    onDataset(ev) {
        this.chooseDataset(ev.target.value);
    }

    // ----------------------------------------------------------------------------------------- the visual
    get vdef() {
        return this.state.visuals[this.state.type];
    }

    get visualTypes() {
        return Object.entries(this.state.visuals).map(([name, v]) => ({ name, label: v.label }));
    }

    setType(name) {
        this.state.type = name;
        this.state.wells = {};
        this.state.options = {};
        this.state.orderKey = "";
        this.schedulePreview();
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
        const item = well.accepts === "measure" ? { agg: "count", field: "" } : { field: "", interval: "" };
        if (this.isMulti(well)) {
            this.state.wells[well.name] = [...(this.state.wells[well.name] || []), item];
        } else {
            this.state.wells[well.name] = item;
        }
    }

    removeItem(well, index) {
        if (this.isMulti(well)) {
            this.state.wells[well.name] = this.items(well).filter((_, i) => i !== index);
        } else {
            delete this.state.wells[well.name];
        }
        this.schedulePreview();
    }

    field(name) {
        return this.state.fields.find((f) => f.name === name);
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

    setAgg(item, ev) {
        item.agg = ev.target.value;
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
            .filter((i) => i.agg === "count" || i.field);
    }

    // ---------------------------------------------------------------------------------- build the widget
    cleanItem(well, item) {
        if (well.accepts === "measure") {
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
        if (s.orderKey) {
            const [kind, name, dir] = s.orderKey.split(":");
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
                    const key = clean.field ? `${clean.field}:${clean.agg}` : "__count";
                    const label = clean.field ? `${this.field(clean.field).label} (${clean.agg})` : _t("Count");
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
        this.state.options[name] = desc.kind === "bool" ? t.checked : desc.kind === "int" ? parseInt(t.value, 10) || "" : t.value;
        this.schedulePreview();
    }

    get optionList() {
        return Object.entries(this.vdef && this.vdef.options ? this.vdef.options : {})
            .filter(([, desc]) => desc.kind !== "colors")
            .map(([name, desc]) => ({ name, ...desc }));
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
        const answer = await this.orm.call("dwo.dashboard.engine", "run_preview", [widget, this.props.filters, {}]);
        if (token !== this.token) {
            return;
        }
        p.loading = false;
        p.entry = answer.ok ? { loading: false, result: answer.result } : { loading: false, error: answer.error };
    }

    get previewWidget() {
        return this.buildWidget() || { type: this.state.type };
    }

    apply() {
        const widget = this.buildWidget();
        if (widget) {
            this.props.onApply(widget);
        }
    }

    // ---------------------------------------------------------------------------------------- dataset list
    get filteredDatasets() {
        const q = this.state.search.trim().toLowerCase();
        return q ? this.state.datasets.filter((d) => d.label.toLowerCase().includes(q) || d.model.includes(q)) : this.state.datasets;
    }
}
