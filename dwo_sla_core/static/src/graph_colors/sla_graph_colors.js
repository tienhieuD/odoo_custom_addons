import { patch } from "@web/core/utils/patch";
import { GraphRenderer } from "@web/views/graph/graph_renderer";

/**
 * Fixed, meaningful colors for the SLA report graphs (task 023).
 * Odoo colors graph series by position, so "On Time" could come out red. Here
 * the series of a graph grouped by one of the fields below get a color by
 * VALUE (green = good, orange = late, red = breached) and are stacked in
 * selection order. Other graphs and models are not touched.
 */
export const SLA_GRAPH_COLORS = {
    "sla.task": {
        outcome: {
            on_time: "#2e9e5b",
            late: "#f08c00",
            breached_open: "#d63a3a",
            running: "#5b7c99",
            paused: "#b8c4cf",
            cancelled: "#8a8f98",
        },
        stage: {
            achieved: "#2e9e5b",
            breached: "#d63a3a",
            in_progress: "#5b7c99",
            paused: "#b8c4cf",
            cancelled: "#8a8f98",
        },
        usage_bucket: {
            "0_50": "#2e9e5b",
            "50_75": "#8cc152",
            "75_100": "#f5b82e",
            "100_150": "#f08c00",
            "150_plus": "#d63a3a",
        },
    },
    "sla.event": {
        event: {
            attach: "#5b7c99",
            pause: "#b8c4cf",
            resume: "#8cc152",
            complete: "#2e9e5b",
            reset: "#7e6bb3",
            cancel: "#8a8f98",
            breach: "#d63a3a",
            escalate: "#f08c00",
            escalate_failed: "#a12a2a",
            error: "#7a1f1f",
            recalculate: "#4aa3c7",
            reevaluate: "#86c5da",
        },
    },
};

/**
 * Returns {fieldName, palette, values} when the graph series follow a field
 * that has fixed colors, otherwise null. `values` maps the displayed label to
 * its technical value and its position in the selection.
 */
export function slaSeriesInfo(metaData) {
    const palettes = SLA_GRAPH_COLORS[metaData.resModel];
    if (!palettes) {
        return null;
    }
    // pie: the slices are the first group-by; bar/line: the series are the second one
    const gb = metaData.mode === "pie" ? metaData.groupBy[0] : metaData.groupBy[1];
    const palette = gb && palettes[gb.fieldName];
    if (!palette) {
        return null;
    }
    const values = {};
    (metaData.fields[gb.fieldName]?.selection || []).forEach(([value, label], index) => {
        values[label] = { value, index };
    });
    return { fieldName: gb.fieldName, palette, values };
}

export function slaColorFor(info, label) {
    const entry = info && info.values[label];
    return (entry && info.palette[entry.value]) || null;
}

patch(GraphRenderer.prototype, {
    getBarChartData() {
        const data = super.getBarChartData(...arguments);
        this._dwoSlaColorDatasets(data);
        return data;
    },

    getLineChartData() {
        const data = super.getLineChartData(...arguments);
        this._dwoSlaColorDatasets(data);
        return data;
    },

    getPieChartData() {
        const info = slaSeriesInfo(this.model.metaData);
        if (info) {
            this._dwoSlaSortSlices(this.model.data, info);
        }
        const data = super.getPieChartData(...arguments);
        if (info) {
            const colors = data.labels.map((label, i) => slaColorFor(info, label) || null);
            for (const dataset of data.datasets) {
                const merged = dataset.backgroundColor.map((c, i) => colors[i] || c);
                dataset.backgroundColor = merged;
                dataset.hoverBackgroundColor = merged;
            }
        }
        return data;
    },

    getLegendOptions() {
        const options = super.getLegendOptions(...arguments);
        const info = slaSeriesInfo(this.model.metaData);
        if (info && this.model.metaData.mode === "pie") {
            const original = options.labels.generateLabels;
            options.labels.generateLabels = (chart) =>
                original(chart).map((item) => {
                    const color = slaColorFor(info, item.fullText);
                    return color ? { ...item, fillStyle: color } : item;
                });
        }
        return options;
    },

    /** Slices in selection order (Odoo orders groups by the stored key). */
    _dwoSlaSortSlices(data, info) {
        const position = (label) => info.values[label]?.index ?? 999;
        const order = data.labels.map((_, i) => i).sort((a, b) => position(data.labels[a]) - position(data.labels[b]));
        if (order.every((from, to) => from === to)) {
            return;
        }
        const pick = (array) => (array ? order.map((i) => array[i]) : array);
        data.labels = pick(data.labels);
        for (const dataset of data.datasets) {
            for (const key of ["data", "domains", "trueLabels", "currencyIds"]) {
                dataset[key] = pick(dataset[key]);
            }
        }
    },

    _dwoSlaColorDatasets(data) {
        const { mode } = this.model.metaData;
        const info = slaSeriesInfo(this.model.metaData);
        if (!info) {
            return;
        }
        // stack in selection order (on time, late, breached...), unknown series last
        const position = (dataset) => info.values[dataset.label]?.index ?? 999;
        data.datasets.sort((a, b) => position(a) - position(b));
        for (const dataset of data.datasets) {
            const color = slaColorFor(info, dataset.label);
            if (!color) {
                continue;
            }
            if (mode === "bar") {
                dataset.backgroundColor = color;
            } else {
                dataset.borderColor = color;
                dataset.backgroundColor = color + "66";
                dataset.hoverBackgroundColor = color;
                dataset.pointBackgroundColor = color;
            }
        }
    },
});
