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
    const colHeads = new Map();
    const cells = new Map();
    for (const r of result.rows) {
        rowHeads.set(rowKey(r), r.labels.slice(0, nRows));
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
    return { rowDims, colDims, rowHeads, colHeads, cells, totals, SEP };
}

export class PivotRenderer extends Component {
    static template = "dwo_dashboard.PivotRenderer";
    static props = { widget: Object, result: Object };

    setup() {
        this.matrix = pivotMatrix(this.props.result);
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
