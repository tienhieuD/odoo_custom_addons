/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onWillStart, useEffect, useRef } from "@odoo/owl";
import { loadBundle } from "@web/core/assets";
import { cookie } from "@web/core/browser/cookie";
import { colorFor, formatNumber } from "../utils";

const SLICE_TYPES = ["pie", "doughnut"];

/** The data of a chart from the rows of the engine: one dimension (a bar per row) or two (axis x legend). */
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
                    backgroundColor: rows.map((_, i) => colorFor(i, options)),
                },
            ],
        };
    }
    const area = widget.type === "area";
    const style = (dataset, i) => {
        const color = colorFor(i, options);
        return widget.type === "bar"
            ? { ...dataset, backgroundColor: color }
            : { ...dataset, borderColor: color, backgroundColor: color + (area ? "55" : ""), fill: area,
                tension: options.smooth ? 0.35 : 0, pointRadius: 2 };
    };
    if (result.dims.length === 1) {
        return {
            labels: rows.map((r) => r.labels[0]),
            datasets: result.measures.map((m, i) =>
                style({ label: m.label, data: rows.map((r) => r.values[i]) }, i)
            ),
        };
    }
    const axis = [...new Set(rows.map((r) => r.labels[0]))];
    const series = [...new Set(rows.map((r) => r.labels[1]))];
    return {
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

export class ChartRenderer extends Component {
    static template = "dwo_dashboard.ChartRenderer";
    static props = { widget: Object, result: Object };

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

    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    scales({ stacked, horizontal, text, grid, number }) {
        // the value axis shows formatted numbers; the category axis keeps its labels (no ``callback`` key at all)
        const value = { stacked, beginAtZero: true, grid: { color: grid }, ticks: { color: text, callback: (v) => number(v) } };
        const category = { stacked, grid: { color: grid }, ticks: { color: text } };
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
        const stacked = !!options.stacked;
        const legend = options.legend || (slice || data.datasets.length > 1 ? "top" : "none");
        const number = (v) => formatNumber(v, options);
        const config = {
            type: widget.type === "area" ? "line" : widget.type,
            data,
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: horizontal ? "y" : "x",
                plugins: {
                    legend: { display: legend !== "none", position: legend === "none" ? "top" : legend,
                              labels: { color: text } },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `${ctx.dataset.label || ctx.label}: ${number(slice ? ctx.parsed : ctx.parsed[horizontal ? "x" : "y"])}`,
                        },
                    },
                },
                scales: slice ? {} : this.scales({ stacked, horizontal, text, grid, number }),
            },
        };
        this.destroy();
        // eslint-disable-next-line no-undef
        this.chart = new Chart(this.canvas.el, config);
    }
}
