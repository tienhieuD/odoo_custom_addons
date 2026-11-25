/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onWillStart, useEffect, useRef } from "@odoo/owl";
import { loadBundle } from "@web/core/assets";
import { cookie } from "@web/core/browser/cookie";
import { _t } from "@web/core/l10n/translation";
import { colorFor, formatNumber } from "../utils";

const SLICE_TYPES = ["pie", "doughnut"];

/** The data of a chart from the rows of the engine: one dimension (a bar per row) or two (axis x legend). With
 * ``percent`` each stack is scaled to 100. */
export function chartData(result, widget) {
    const options = widget.options || {};
    const rows = result.rows;
    if (SLICE_TYPES.includes(widget.type)) {
        return {
            labels: rows.map((r) => r.labels[0]),
            datasets: [
                {
                    label: result.measures[0].label,
                    data: rows.map((r) => r.values[0]),
                    backgroundColor: rows.map((_, i) => colorFor(i, options, rows.length)),
                },
            ],
        };
    }
    const area = widget.type === "area";
    const count = result.dims.length === 1 ? result.measures.length : new Set(rows.map((r) => r.labels[1])).size;
    const style = (dataset, i) => {
        const color = colorFor(i, options, count);
        return widget.type === "bar"
            ? { ...dataset, backgroundColor: color }
            : { ...dataset, borderColor: color, backgroundColor: color + (area ? "55" : ""), fill: area,
                tension: options.smooth ? 0.35 : 0, pointRadius: 2 };
    };
    let data;
    if (result.dims.length === 1) {
        data = {
            labels: rows.map((r) => r.labels[0]),
            datasets: result.measures.map((m, i) =>
                style({ label: m.label, data: rows.map((r) => r.values[i]) }, i)
            ),
        };
    } else {
        const axis = [...new Set(rows.map((r) => r.labels[0]))];
        const series = [...new Set(rows.map((r) => r.labels[1]))];
        data = {
            labels: axis,
            datasets: series.map((name, i) =>
                style(
                    {
                        label: name,
                        data: axis.map((a) => {
                            const row = rows.find((r) => r.labels[0] === a && r.labels[1] === name);
                            return row ? row.values[0] : 0;
                        }),
                    },
                    i
                )
            ),
        };
    }
    const previous = result.compare && result.compare.series;
    if (previous && ["line", "area"].includes(widget.type) && data.datasets.length === 1) {
        // the previous period drawn over the chart: the k-th point of one is the k-th interval of the other
        data.datasets.push({
            label: result.compare.against === "previous_year" ? _t("Same period last year") : _t("Previous period"),
            data: previous.values,
            borderColor: "#9ca3af",
            backgroundColor: "#9ca3af",
            borderDash: [6, 4],
            borderWidth: 2,
            fill: false,
            pointRadius: 0,
            tension: options.smooth ? 0.35 : 0,
            dwoPreviousLabels: previous.labels,
        });
    }
    if (options.percent) {
        // 100% stacked: every column is the share of each series in that column
        data.labels.forEach((_, k) => {
            const total = data.datasets.reduce((sum, d) => sum + (d.data[k] || 0), 0);
            data.datasets.forEach((d) => (d.data[k] = total ? ((d.data[k] || 0) / total) * 100 : 0));
        });
    }
    return data;
}

/** Writes the values on the bars, points and slices (``show_values``, ``show_percent``). */
const valuesPlugin = {
    id: "dwoValues",
    afterDatasetsDraw(chart, _args, opts) {
        if (!opts || !opts.enabled) {
            return;
        }
        const { ctx } = chart;
        ctx.save();
        ctx.font = "11px sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        chart.data.datasets.forEach((dataset, di) => {
            const meta = chart.getDatasetMeta(di);
            if (meta.hidden) {
                return;
            }
            const total = dataset.data.reduce((a, b) => a + (b || 0), 0);
            meta.data.forEach((element, i) => {
                const value = dataset.data[i];
                if (!value) {
                    return;
                }
                const text = opts.percentOfTotal ? `${Math.round((value / total) * 1000) / 10}%` : opts.format(value);
                if (opts.percentOfTotal && value / total < 0.04) {
                    return; // a slice too thin to carry a label
                }
                const point = element.getCenterPoint ? element.getCenterPoint() : element.tooltipPosition();
                const inside = chart.config.type !== "line";
                ctx.fillStyle = inside ? "#ffffff" : opts.color;
                ctx.fillText(text, point.x, inside ? point.y : point.y - 10);
            });
        });
        ctx.restore();
    },
};

/** A dashed reference line at ``target`` on the value axis. */
const targetPlugin = {
    id: "dwoTarget",
    afterDatasetsDraw(chart, _args, opts) {
        if (!opts || opts.value === undefined || opts.value === null) {
            return;
        }
        const scale = chart.scales[opts.horizontal ? "x" : "y"];
        const area = chart.chartArea;
        const pos = scale.getPixelForValue(opts.value);
        if (pos < Math.min(scale.top, scale.left) - 1) {
            return;
        }
        const { ctx } = chart;
        ctx.save();
        ctx.strokeStyle = "#EA6175";
        ctx.fillStyle = "#EA6175";
        ctx.setLineDash([6, 4]);
        ctx.beginPath();
        if (opts.horizontal) {
            ctx.moveTo(pos, area.top);
            ctx.lineTo(pos, area.bottom);
        } else {
            ctx.moveTo(area.left, pos);
            ctx.lineTo(area.right, pos);
        }
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.font = "11px sans-serif";
        ctx.textAlign = "right";
        ctx.fillText(`${_t("Target")} ${opts.format(opts.value)}`, opts.horizontal ? pos - 4 : area.right - 4,
            opts.horizontal ? area.top + 10 : pos - 6);
        ctx.restore();
    },
};

/** The group key of each label of the chart (the first dimension), in the order of ``chartData().labels``. */
export function axisKeys(result, widget) {
    if (SLICE_TYPES.includes(widget.type) || result.dims.length === 1) {
        return result.rows.map((r) => r.keys[0]);
    }
    const seen = new Map();
    for (const r of result.rows) {
        if (!seen.has(r.labels[0])) {
            seen.set(r.labels[0], r.keys[0]);
        }
    }
    return [...seen.values()];
}

export class ChartRenderer extends Component {
    static template = "dwo_dashboard.ChartRenderer";
    static props = { widget: Object, result: Object, onPick: { type: Function, optional: true } };

    setup() {
        this.canvas = useRef("canvas");
        this.chart = null;
        onWillStart(() => loadBundle("web.chartjs_lib"));
        useEffect(
            () => {
                this.draw();
                return () => this.destroy();
            },
            () => [JSON.stringify(this.props.result), JSON.stringify(this.props.widget)]
        );
    }

    click(event, elements) {
        const { onPick, result, widget } = this.props;
        if (!onPick || !elements.length) {
            return;
        }
        const index = elements[0].index;
        const key = axisKeys(result, widget)[index];
        if (key === undefined || key === "__other") {
            return;
        }
        event.native.stopPropagation(); // the popover opens under the pointer: the click must not close it again
        onPick({ key, label: this.chart.data.labels[index], x: event.native.clientX, y: event.native.clientY });
    }

    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    scales({ stacked, horizontal, text, grid, number, percent, options }) {
        // the value axis shows formatted numbers; the category axis keeps its labels (no ``callback`` key at all)
        const value = {
            stacked, beginAtZero: true, grid: { color: grid },
            ticks: { color: text, callback: (v) => (percent ? `${v}%` : number(v)) },
        };
        if (percent) {
            value.max = 100;
        }
        if (options.y_min !== undefined) {
            value.min = options.y_min;
            value.beginAtZero = false;
        }
        if (options.y_max !== undefined) {
            value.max = options.y_max;
        }
        const category = { stacked, grid: { color: grid }, ticks: { color: text, maxRotation: 0, autoSkip: true } };
        return horizontal ? { x: value, y: category } : { x: category, y: value };
    }

    draw() {
        const { widget, result } = this.props;
        const options = widget.options || {};
        const data = chartData(result, widget);
        const dark = cookie.get("color_scheme") === "dark";
        const text = dark ? "#E4E4E4" : "#111827";
        const grid = dark ? "rgba(255,255,255,.15)" : "rgba(0,0,0,.1)";
        const slice = SLICE_TYPES.includes(widget.type);
        const horizontal = widget.type === "bar" && options.horizontal;
        const percent = !!options.percent;
        const stacked = !!options.stacked || percent;
        const legend = options.legend || (slice || data.datasets.length > 1 ? "top" : "none");
        const metricFormat = result.measures && result.measures[0] && result.measures[0].format;
        const number = (v) => formatNumber(v, metricFormat ? { format: metricFormat, decimals: 0, ...options } : options);
        const config = {
            type: widget.type === "area" ? "line" : widget.type,
            data,
            options: {
                onClick: (event, elements) => this.click(event, elements),
                onHover: (event, elements) => {
                    event.native.target.style.cursor = this.props.onPick && elements.length ? "pointer" : "default";
                },
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: horizontal ? "y" : "x",
                plugins: {
                    legend: { display: legend !== "none", position: legend === "none" ? "top" : legend,
                              labels: { color: text, usePointStyle: true, boxWidth: 8, boxHeight: 8 } },
                    tooltip: {
                        callbacks: {
                            title: (items) => {
                                const item = items[0];
                                const before = item && item.dataset.dwoPreviousLabels;
                                return before ? `${item.label} · ${before[item.dataIndex] || ""}` : item.label;
                            },
                            label: (ctx) => {
                                const v = slice ? ctx.parsed : ctx.parsed[horizontal ? "x" : "y"];
                                return `${ctx.dataset.label || ctx.label}: ${percent ? Math.round(v * 10) / 10 + "%" : number(v)}`;
                            },
                        },
                    },
                    dwoValues: {
                        enabled: slice ? !!(options.show_values || options.show_percent) : !!options.show_values,
                        percentOfTotal: slice && !!options.show_percent && !options.show_values,
                        format: percent ? (v) => `${Math.round(v)}%` : number,
                        color: text,
                    },
                    dwoTarget: options.target === undefined || slice
                        ? undefined
                        : { value: options.target, horizontal, format: number },
                },
                scales: slice ? {} : this.scales({ stacked, horizontal, text, grid, number, percent, options }),
            },
            plugins: [valuesPlugin, targetPlugin],
        };
        this.destroy();
        // eslint-disable-next-line no-undef
        this.chart = new Chart(this.canvas.el, config);
    }
}
