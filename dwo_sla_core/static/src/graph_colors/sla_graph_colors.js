odoo.define('dwo_sla_core.graph_colors', function (require) {
"use strict";

var GraphRenderer = require('web.GraphRenderer');
var fieldUtils = require('web.field_utils');

/**
 * Fixed, meaningful colors for the SLA report graphs (task 023), legacy graph widget of Odoo 14.
 * Odoo colors graph series by position, so "On Time" could come out red. Here the series of a
 * graph grouped by one of the fields below get a color by VALUE (green = good, orange = late,
 * red = breached) and are stacked in selection order. Other graphs and models are not touched.
 */
var SLA_GRAPH_COLORS = {
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
 * The legacy graph does not know the model: the series field is recognised by its name AND by
 * the keys of its selection being exactly the ones of the palette. Returns
 * {palette, values: {label: {value, index}}} when the series follow such a field, else null.
 * Pie: the slices are the first group-by; bar/line: the series are the second one.
 */
function slaSeriesInfo(state, fields) {
    var gb = state.mode === 'pie' ? state.processedGroupBy[0] : state.processedGroupBy[1];
    var fieldName = gb && gb.split(':')[0];
    var field = fieldName && fields[fieldName];
    if (!field || !field.selection) {
        return null;
    }
    var found = null;
    Object.keys(SLA_GRAPH_COLORS).forEach(function (model) {
        var palette = SLA_GRAPH_COLORS[model][fieldName];
        if (palette && field.selection.length === Object.keys(palette).length &&
                field.selection.every(function (s) { return s[0] in palette; })) {
            found = palette;
        }
    });
    if (!found) {
        return null;
    }
    var values = {};
    field.selection.forEach(function (s, index) {
        values[s[1]] = {value: s[0], index: index};
    });
    return {palette: found, values: values};
}

function slaPosition(info, label) {
    var entry = info.values[label];
    return entry ? entry.index : 999;
}

function slaColorFor(info, label) {
    var entry = info.values[label];
    return (entry && info.palette[entry.value]) || null;
}

function labelText(label) {
    return Array.isArray(label) ? label.join('/') : label;
}

GraphRenderer.include({
    /** The legacy graph ignores `widget` on a measure: the rate of the SLA graphs is a percentage (axis and tooltip). */
    _formatValue: function (value) {
        if (this.state.measure === 'achieved_rate' && this.fields.sla_id && this.fields.achieved_rate) {
            return fieldUtils.format.percentage(value, this.fields.achieved_rate);
        }
        return this._super.apply(this, arguments);
    },

    /**
     * Series (bar/line) or slices (pie) in selection order; the colors by index are remembered for
     * `_getColor`, which Odoo calls with the index of the dataset (bar/line) or of the slice (pie).
     */
    _prepareData: function () {
        var data = this._super.apply(this, arguments);
        this._dwoSlaColors = null;
        var info = slaSeriesInfo(this.state, this.fields);
        if (!info || this.state.origins.length > 1) {
            return data;
        }
        if (this.state.mode === 'pie') {
            var order = data.labels.map(function (_l, i) { return i; }).sort(function (a, b) {
                return slaPosition(info, labelText(data.labels[a])) - slaPosition(info, labelText(data.labels[b]));
            });
            var pick = function (array) {
                return Array.isArray(array) ? order.map(function (i) { return array[i]; }) : array;
            };
            data.labels = pick(data.labels);
            data.datasets.forEach(function (dataset) {
                ['data', 'domain'].forEach(function (key) { dataset[key] = pick(dataset[key]); });
            });
            this._dwoSlaColors = data.labels.map(function (label) { return slaColorFor(info, labelText(label)); });
        } else {
            data.datasets.sort(function (a, b) {
                return slaPosition(info, a.label) - slaPosition(info, b.label);
            });
            this._dwoSlaColors = data.datasets.map(function (dataset) { return slaColorFor(info, dataset.label); });
        }
        return data;
    },

    _getColor: function (index) {
        return (this._dwoSlaColors && this._dwoSlaColors[index]) || this._super.apply(this, arguments);
    },
});

return {SLA_GRAPH_COLORS: SLA_GRAPH_COLORS, slaSeriesInfo: slaSeriesInfo};

});
