/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component } from "@odoo/owl";
import { deserializeDate, formatDate } from "@web/core/l10n/dates";
import { _t } from "@web/core/l10n/translation";
import { formatNumber } from "../utils";

/** A KPI card: the number, what it is, how it moved since the previous period, and how far it is from its goal. */
export class KpiRenderer extends Component {
    static template = "dwo_dashboard.KpiRenderer";
    static props = { widget: Object, result: Object };

    get options() {
        return this.props.widget.options || {};
    }

    get row() {
        return this.props.result.rows[0];
    }

    get raw() {
        return this.row ? this.row.values[0] : null;
    }

    get value() {
        return this.raw === null ? "–" : formatNumber(this.raw, this.options);
    }

    get prefix() {
        return this.options.prefix || "";
    }

    get suffix() {
        return this.options.suffix || "";
    }

    get label() {
        // the measure is named under the number only when the widget has no title of its own
        return this.props.widget.title ? "" : this.props.result.measures[0].label;
    }

    // ------------------------------------------------------------------------------------------- the trend
    get compare() {
        return this.props.result.compare || null;
    }

    get change() {
        return this.compare ? this.compare.change_pct : null;
    }

    get deltaText() {
        const pct = this.change;
        if (pct === null || pct === undefined) {
            return "—"; // no previous figure to divide by: never "+∞ %"
        }
        const sign = pct > 0 ? "+" : "";
        return `${sign}${new Intl.NumberFormat(undefined, { maximumFractionDigits: 1 }).format(pct)}%`;
    }

    get deltaIcon() {
        const pct = this.change;
        return pct > 0 ? "fa-caret-up" : pct < 0 ? "fa-caret-down" : "fa-minus";
    }

    /** Green when the move is the good one (a rise, unless ``trend_good`` is "down": a falling cost is good news). */
    get deltaClass() {
        const pct = this.change;
        if (!pct) {
            return "text-muted";
        }
        const good = (pct > 0) === (this.options.trend_good !== "down");
        return good ? "text-success" : "text-danger";
    }

    /** The period the headline number is about, so that turning on the comparison never changes its meaning silently. */
    get periodText() {
        const [from, to] = this.compare.range.map((d) => deserializeDate(d));
        return `${formatDate(from)} – ${formatDate(to.minus({ days: 1 }))}`;
    }

    get needsPeriod() {
        return !!this.props.widget.compare && !this.compare;
    }

    /** What the change is measured against, with the dates: "vs 120 (1 Oct – 25 Oct 2026)", or why there is no change. */
    get versus() {
        const c = this.compare;
        const [from, to] = c.previous_range.map((d) => deserializeDate(d));
        const span = `${formatDate(from)} – ${formatDate(to.minus({ days: 1 }))}`;
        if (c.previous === null || c.previous === 0) {
            return _t("No data in %s", span);
        }
        return _t("vs %s (%s)", formatNumber(c.previous, this.options), span);
    }

    // ------------------------------------------------------------------------------------------ the trend line
    /** The last points as a small line (SVG, no axes): a quiet interval is a zero on the line, a missing average a gap. */
    get trend() {
        const t = this.props.result.trend;
        if (!t || t.points.length < 2) {
            return null;
        }
        const values = t.points.map((p) => p.value);
        const known = values.filter((v) => v !== null);
        if (known.length < 2) {
            return null;
        }
        const low = Math.min(...known);
        const high = Math.max(...known);
        const x = (i) => (i / (values.length - 1)) * 100;
        const y = (v) => (high === low ? 15 : 28 - ((v - low) / (high - low)) * 26);
        let line = "";
        let pen = false;
        values.forEach((v, i) => {
            if (v === null) {
                pen = false;
                return;
            }
            line += `${pen ? "L" : "M"}${x(i).toFixed(2)},${y(v).toFixed(2)} `;
            pen = true;
        });
        const last = values.length - 1;
        const lastValue = values[last];
        return {
            line,
            area: `${line} L100,30 L0,30 Z`,
            dot: lastValue === null ? null : { x: x(last), y: y(lastValue) },
            title: t.points.map((p) => `${p.label}: ${p.value === null ? "–" : formatNumber(p.value, this.options)}`).join("\n"),
        };
    }

    // -------------------------------------------------------------------------------------------- the goal
    get goal() {
        const goal = this.options.goal;
        return goal && this.raw !== null ? goal : null;
    }

    get goalPercent() {
        return Math.max(0, Math.min(100, Math.round((this.raw / this.goal) * 100)));
    }

    get goalText() {
        const pct = Math.round((this.raw / this.goal) * 100);
        return _t("%s%% of the goal (%s)", pct, formatNumber(this.goal, this.options));
    }
}
