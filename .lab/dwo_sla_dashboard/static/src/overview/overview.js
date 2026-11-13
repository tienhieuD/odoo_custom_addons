/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { deserializeDateTime } from "@web/core/l10n/dates";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { Component, onWillStart, useState } from "@odoo/owl";

const PERIODS = [7, 30, 90];

// good: which direction of change is an improvement (null = neutral)
const KPI_META = {
    running: { icon: "fa-play-circle", cls: "neutral", good: null },
    due_soon: { icon: "fa-hourglass-half", cls: "warn", good: "down" },
    breached: { icon: "fa-bolt", cls: "bad", good: "down" },
    achieved_rate: { icon: "fa-check-circle", cls: "ok", good: "up" },
    late: { icon: "fa-exclamation-circle", cls: "warn", good: "down" },
};

const OUTCOME_CLASS = {
    on_time: "ok",
    late: "warn",
    breached_open: "bad",
    running: "run",
    paused: "pause",
    cancelled: "cancel",
};

export class SlaOverview extends Component {
    static template = "dwo_sla_dashboard.Overview";
    static components = { Dropdown, DropdownItem };
    static props = { "*": true };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.periods = PERIODS;
        this.state = useState({
            loading: true,
            period: 30,
            sla_type: false,
            sla_target: false,
            sla_ids: [],
            data: null,
        });
        onWillStart(() => this.load());
    }

    async load() {
        const { period, sla_type, sla_target, sla_ids } = this.state;
        const data = await this.orm.call("sla.task", "get_dashboard_data", [], {
            period,
            filters: { sla_type, sla_target, sla_ids },
        });
        this.state.data = data;
        this.state.loading = false;
    }

    async refresh() {
        await this.load();
    }

    setPeriod(period) {
        this.state.period = period;
        return this.refresh();
    }

    setType(value) {
        this.state.sla_type = this.state.sla_type === value ? false : value;
        return this.refresh();
    }

    setTarget(value) {
        this.state.sla_target = this.state.sla_target === value ? false : value;
        return this.refresh();
    }

    toggleDefinition(id) {
        const ids = this.state.sla_ids;
        const index = ids.indexOf(id);
        if (index >= 0) {
            ids.splice(index, 1);
        } else {
            ids.push(id);
        }
        return this.refresh();
    }

    clearDefinitions() {
        this.state.sla_ids = [];
        return this.refresh();
    }

    get definitionLabel() {
        const count = this.state.sla_ids.length;
        if (!count) {
            return _t("All definitions");
        }
        if (count === 1) {
            const def = this.state.data.definitions.find((d) => d.id === this.state.sla_ids[0]);
            return def ? def.name : _t("1 definition");
        }
        return _t("%s definitions", count);
    }

    // ---------------------------------------------------------------- KPI

    get kpiCards() {
        const kpis = this.state.data.kpis;
        const labels = {
            running: _t("Running"),
            due_soon: _t("Due soon"),
            breached: _t("Breached"),
            achieved_rate: _t("Achieved rate"),
            late: _t("Late"),
        };
        const hints = {
            running: _t("Tasks with the clock running now"),
            due_soon: _t("Running tasks close to their deadline"),
            breached: _t("Open tasks already past their deadline"),
            achieved_rate: _t("Share of tasks finished on time in the period"),
            late: _t("Tasks finished after their deadline in the period"),
        };
        return Object.keys(KPI_META).map((key) => {
            const kpi = kpis[key];
            const meta = KPI_META[key];
            const isRate = key === "achieved_rate";
            const delta = kpi.delta;
            let trend = "flat";
            let trendCls = "flat";
            if (delta) {
                trend = delta > 0 ? "up" : "down";
                trendCls = meta.good === null ? "flat" : trend === meta.good ? "good" : "bad";
            }
            return {
                key,
                label: labels[key],
                hint: hints[key],
                icon: meta.icon,
                cls: meta.cls,
                value: kpi.value === null ? "-" : isRate ? `${kpi.value}%` : `${kpi.value}`,
                trend,
                trendCls,
                delta:
                    delta === null
                        ? null
                        : `${delta > 0 ? "+" : ""}${delta}${isRate ? " pt" : ""}`,
            };
        });
    }

    openKpi(key) {
        const titles = {
            running: _t("Running"),
            due_soon: _t("Due soon"),
            breached: _t("Breached"),
            achieved_rate: _t("Finished in the period"),
            late: _t("Late"),
        };
        this.openList(titles[key], this.state.data.kpis[key].domain);
    }

    // ------------------------------------------------------------- charts

    get hasChartData() {
        return this.state.data.donut.length > 0;
    }

    outcomeClass(key) {
        return OUTCOME_CLASS[key] || "run";
    }

    get donutTotal() {
        return this.state.data.donut.reduce((sum, item) => sum + item.count, 0);
    }

    /** Circle of circumference 100: each slice is a dash of its percentage. */
    get donutSlices() {
        const total = this.donutTotal || 1;
        let offset = 25; // start at 12 o'clock
        return this.state.data.donut.map((item) => {
            const pct = (item.count / total) * 100;
            const slice = {
                key: item.key,
                label: this.state.data.outcome_labels[item.key],
                count: item.count,
                pct: Math.round(pct),
                dash: `${Math.max(pct - 0.4, 0.2)} ${100 - Math.max(pct - 0.4, 0.2)}`,
                offset,
            };
            offset -= pct;
            return slice;
        });
    }

    openOutcome(key) {
        const label = this.state.data.outcome_labels[key];
        this.openList(label, [...this.state.data.scope_domain, ["outcome", "=", key]]);
    }

    get barRows() {
        const rows = this.state.data.bars;
        const max = Math.max(1, ...rows.map((r) => r.total));
        return rows.map((r) => ({
            ...r,
            segments: ["on_time", "late", "breached_open"]
                .filter((k) => r[k])
                .map((k) => ({
                    key: k,
                    count: r[k],
                    width: (r[k] / max) * 100,
                    label: this.state.data.outcome_labels[k],
                })),
        }));
    }

    openBar(row, segment) {
        this.openList(`${row.name} - ${segment.label}`, [
            ...this.state.data.scope_domain,
            ["sla_id", "=", row.id],
            ["outcome", "=", segment.key],
        ]);
    }

    openBarRow(row) {
        this.openList(row.name, [...this.state.data.scope_domain, ["sla_id", "=", row.id]]);
    }

    /** SVG polyline for the weekly achieved-rate line (viewBox 600x200). */
    get lineChart() {
        const weekly = this.state.data.weekly;
        const left = 36;
        const width = 548;
        const top = 12;
        const height = 150;
        const step = weekly.length > 1 ? width / (weekly.length - 1) : 0;
        const points = weekly.map((w, i) => ({
            x: weekly.length > 1 ? left + i * step : left + width / 2,
            y: w.rate === null ? null : top + height * (1 - w.rate / 100),
            rate: w.rate,
            count: w.count,
            label: this.weekLabel(w.week),
        }));
        const segments = [];
        let current = [];
        for (const p of points) {
            if (p.y === null) {
                if (current.length) {
                    segments.push(current);
                }
                current = [];
            } else {
                current.push(p);
            }
        }
        if (current.length) {
            segments.push(current);
        }
        const baseY = top + height;
        return {
            points,
            lines: segments.map((s) => s.map((p) => `${p.x},${p.y}`).join(" ")),
            areas: segments
                .filter((s) => s.length > 1)
                .map(
                    (s) =>
                        `${s[0].x},${baseY} ` +
                        s.map((p) => `${p.x},${p.y}`).join(" ") +
                        ` ${s[s.length - 1].x},${baseY}`
                ),
            grid: [0, 25, 50, 75, 100].map((v) => ({
                v,
                y: top + height * (1 - v / 100),
                x1: left,
                x2: left + width,
            })),
            baseY,
            left,
        };
    }

    weekLabel(isoDate) {
        const [, m, d] = isoDate.split("-");
        return `${d}/${m}`;
    }

    // ----------------------------------------------------------- attention

    get attentionRows() {
        const now = luxon.DateTime.now();
        return this.state.data.attention.map((row) => {
            const planned = row.planned_end_time ? deserializeDateTime(row.planned_end_time) : null;
            const percent = Math.max(row.percent, 0);
            return {
                ...row,
                cls: row.breached ? "bad" : "warn",
                barWidth: Math.min(percent, 100),
                due: planned ? this.formatDue(planned, now) : "",
            };
        });
    }

    formatDue(planned, now) {
        const text = planned.toFormat("dd/MM HH:mm");
        return planned < now ? _t("Late since %s", text) : _t("Due %s", text);
    }

    openTask(row) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "sla.task",
            res_id: row.id,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openAttention() {
        this.openList(_t("Needs attention"), this.state.data.attention_domain);
    }

    // --------------------------------------------------------------- drill

    /** Opens the SLA Tasks list of dwo_sla_core with a server-built domain. */
    openList(name, domain) {
        const views = this.state.data.action.view_mode
            .split(",")
            .map((type) => [false, type]);
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: this.state.data.action.res_model,
            domain,
            views,
            context: {},
            target: "current",
        });
    }
}

registry.category("actions").add("dwo_sla_dashboard.overview", SlaOverview);
