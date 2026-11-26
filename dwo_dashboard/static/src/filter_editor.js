/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onWillStart, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { DwoSelect } from "./select";
import { PRESET_LABELS } from "./utils";

const KINDS = [
    { type: "date", label: _t("A period"), hint: _t("Today, this month, last year...") },
    { type: "relation", label: _t("Some records"), hint: _t("Customers, countries, salespeople...") },
    { type: "selection", label: _t("A choice"), hint: _t("A status, a type...") },
];
const DATE = ["date", "datetime"];

/** Creates a page filter from the fields of the datasets the page uses. Same-named fields of the same kind are bound
 * together, so one "Created" filter acts on every widget that has a "Created" field. The page spec is validated on save
 * like everything else: there is no separate path. */
export class FilterEditor extends Component {
    static template = "dwo_dashboard.FilterEditor";
    static props = { datasets: Array, existing: Array, onAdd: Function, onClose: Function };

    static components = { DwoSelect };

    setup() {
        this.orm = useService("orm");
        this.kinds = KINDS;
        this.presets = Object.entries(PRESET_LABELS);
        this.presetOptions = this.presets.map(([value, label]) => ({ value, label }));
        this.state = useState({ loading: true, candidates: [], type: "date", key: "", label: "", default: "all" });
        onWillStart(async () => {
            // every dataset of the page: an Odoo model, a blend (its dimensions) or a SQL dataset (its columns); one that cannot be
            // described for this person is simply left out
            const descriptions = await Promise.all(
                this.props.datasets.map((ref) =>
                    this.orm.call("dwo.dashboard.explore", "describe_dataset", [ref]).catch(() => null)
                )
            );
            this.state.candidates = this.collect(descriptions.filter(Boolean));
            this.state.loading = false;
            this.pick(this.visible[0]);
        });
    }

    /** One candidate per (kind, field name, target): the datasets that have it. */
    collect(descriptions) {
        const found = new Map();
        for (const d of descriptions) {
            for (const f of d.fields) {
                let type = null;
                let target = "";
                if (DATE.includes(f.type)) {
                    type = "date";
                } else if (["many2one", "many2many"].includes(f.type) && f.relation) {
                    type = "relation";
                    target = f.relation;
                } else if (f.type === "selection" && f.selection) {
                    type = "selection";
                }
                if (!type || !f.dimension) {
                    continue;
                }
                const key = `${type}|${f.name}|${target}`;
                const entry = found.get(key) || { key, type, field: f.name, label: f.label, model: target,
                                                  datasets: [], values: null };
                entry.datasets.push(d.ref);
                if (type === "selection") {
                    const keys = f.selection.map(([k]) => k);
                    entry.values = entry.values ? entry.values.filter((k) => keys.includes(k)) : keys;
                }
                found.set(key, entry);
            }
        }
        return [...found.values()].filter((c) => c.type !== "selection" || (c.values && c.values.length <= 100 && c.values.length));
    }

    get visible() {
        return this.state.candidates
            .filter((c) => c.type === this.state.type)
            .sort((a, b) => b.datasets.length - a.datasets.length || a.label.localeCompare(b.label));
    }

    setType(type) {
        this.state.type = type;
        this.pick(this.visible[0]);
    }

    pick(candidate) {
        this.state.key = candidate ? candidate.key : "";
        this.state.label = candidate ? candidate.label : "";
    }

    setDefault(ev) {
        this.state.default = ev.target.value;
    }

    get candidateOptions() {
        return this.visible.map((c) => ({ value: c.key, label: `${c.label} (${this.sources(c.datasets.length)})` }));
    }

    onField(ev) {
        this.pick(this.state.candidates.find((c) => c.key === ev.target.value));
    }

    sources(count) {
        return count === 1 ? _t("1 data source") : _t("%s data sources", count);
    }

    get chosen() {
        return this.state.candidates.find((c) => c.key === this.state.key);
    }

    get canAdd() {
        return !!this.chosen && this.props.existing.length < 10;
    }

    add() {
        const c = this.chosen;
        const taken = new Set(this.props.existing.map((f) => f.id));
        let id = c.field.slice(0, 28);
        for (let n = 2; taken.has(id); n++) {
            id = `${c.field.slice(0, 26)}_${n}`;
        }
        const filter = { id, type: c.type, label: this.state.label.trim() || c.label,
                         bind: c.datasets.map((dataset) => ({ dataset, field: c.field })) };
        if (c.type === "relation") {
            filter.model = c.model;
        } else if (c.type === "selection") {
            filter.values = c.values;
        } else if (this.state.default !== "all") {
            filter.default = this.state.default;
        }
        if (c.type === "date" && this.state.default === "all") {
            filter.default = "all";
        }
        this.props.onAdd(filter);
    }
}
