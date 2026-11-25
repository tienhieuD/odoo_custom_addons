/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component } from "@odoo/owl";
import { formatNumber } from "../utils";

const SEP = "\u0001";

/** The matrix of a pivot from the flat rows of the engine. */
export function pivotMatrix(result) {
    const rowDims = result.dims.filter((d) => d.well === "rows");
    const colDims = result.dims.filter((d) => d.well === "columns");
    const nRows = rowDims.length;
    const rowKey = (r) => r.keys.slice(0, nRows).map(String).join(SEP);
    const colKey = (r) => r.keys.slice(nRows).map(String).join(SEP);
    const rowHeads = new Map();
    const rowRaw = new Map(); // row key -> the keys as the server wrote them (a click sends them back)
    const colHeads = new Map();
    const cells = new Map();
    for (const r of result.rows) {
        rowHeads.set(rowKey(r), r.labels.slice(0, nRows));
        rowRaw.set(rowKey(r), r.keys.slice(0, nRows));
        colHeads.set(colKey(r), r.labels.slice(nRows));
        cells.set(rowKey(r) + SEP + SEP + colKey(r), r.values);
    }
    const totalOf = (list, keyOf) => new Map((list || []).map((r) => [keyOf(r), r.values]));
    const totals = result.totals
        ? {
              rows: totalOf(result.totals.rows, rowKey),
              columns: totalOf(result.totals.columns, (r) => r.keys.map(String).join(SEP)),
              grand: result.totals.grand && result.totals.grand[0] ? result.totals.grand[0].values : null,
          }
        : null;
    return { rowDims, colDims, rowHeads, rowRaw, colHeads, cells, totals, SEP };
}

export class PivotRenderer extends Component {
    static template = "dwo_dashboard.PivotRenderer";
    static props = { widget: Object, result: Object, onPick: { type: Function, optional: true } };

    setup() {
        this.matrix = pivotMatrix(this.props.result);
        // min and max of each measure over the cells, for the heat map
        this.span = this.props.result.measures.map((_, i) => {
            const values = [...this.matrix.cells.values()].map((v) => v[i]).filter((v) => v !== null && v !== undefined);
            return [Math.min(...values), Math.max(...values)];
        });
    }

    pickRow(rowKey, ev) {
        const raw = this.matrix.rowRaw.get(rowKey);
        if (this.props.onPick && raw && raw[0] !== "__other") {
            ev.stopPropagation();
            this.props.onPick({ key: raw[0], label: this.matrix.rowHeads.get(rowKey)[0], x: ev.clientX, y: ev.clientY });
        }
    }

    /** Background of a cell: the larger the value in its column of measures, the stronger the blue. */
    heat(rowKey, colKey, i) {
        if (!(this.props.widget.options || {}).heatmap) {
            return "";
        }
        const values = this.matrix.cells.get(rowKey + SEP + SEP + colKey);
        const [low, high] = this.span[i];
        if (!values || values[i] === null || high === low) {
            return "";
        }
        return `background-color: rgba(78, 167, 242, ${(0.08 + 0.55 * (values[i] - low) / (high - low)).toFixed(2)})`;
    }

    get measures() {
        return this.props.result.measures;
    }

    get rowEntries() {
        return [...this.matrix.rowHeads.entries()];
    }

    get colEntries() {
        const entries = [...this.matrix.colHeads.entries()];
        return entries.length ? entries : [["", []]];
    }

    value(rowKey, colKey, i) {
        const values = this.matrix.cells.get(rowKey + SEP + SEP + colKey);
        return values ? this.fmt(values[i]) : "";
    }

    rowTotal(rowKey, i) {
        const values = this.matrix.totals && this.matrix.totals.rows.get(rowKey);
        return values ? this.fmt(values[i]) : "";
    }

    colTotal(colKey, i) {
        const values = this.matrix.totals && this.matrix.totals.columns.get(colKey);
        return values ? this.fmt(values[i]) : "";
    }

    grand(i) {
        const g = this.matrix.totals && this.matrix.totals.grand;
        return g ? this.fmt(g[i]) : "";
    }

    fmt(v) {
        return v === null || v === undefined ? "" : formatNumber(v, this.props.widget.options || {});
    }

    get showTotals() {
        return !!this.matrix.totals;
    }

    colLabel(labels) {
        return labels.join(" / ");
    }
}
