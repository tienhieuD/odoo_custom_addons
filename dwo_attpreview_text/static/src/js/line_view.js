/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, markup, onMounted, onPatched, onWillUnmount, useRef, useState } from "@odoo/owl";

const ROW_HEIGHT = 20;

/**
 * A virtual list of rows (lines of a file, log lines, diff rows, table rows): only the visible rows are in the page,
 * so a file of a million lines scrolls at once. Uses TanStack Virtual from the core (global DwoTreeLibs).
 *
 * props.count: number of rows; props.row(i) -> {cls, cells: [{html, cls, num}]} where `html` is an HTML string that
 * the parent has escaped (or that highlight.js made) and `num` an optional line number drawn before the cell;
 * props.columns: CSS grid-template-columns of a row; props.headers: column titles (optional);
 * props.wrap: long lines wrap (rows are then measured, heights vary); props.version: bump it to draw the rows again
 * (find marks, filter); props.onReady(api): {scrollToIndex(i), firstVisible()}; props.startIndex: first row shown.
 */
export class DwoLineView extends Component {
    static template = "dwo_attpreview_text.LineView";
    static props = {
        count: Number,
        row: Function,
        columns: { type: String, optional: true },
        headers: { type: Array, optional: true },
        wrap: { type: Boolean, optional: true },
        version: { type: Number, optional: true },
        onReady: { type: Function, optional: true },
        startIndex: { type: Number, optional: true },
        activeIndex: { type: Number, optional: true },
        label: { type: String, optional: true },
        rowHeight: { type: Number, optional: true },
    };

    setup() {
        const L = window.DwoTreeLibs;
        this.ticks = useState({ n: 0 });
        this.scrollRef = useRef("scroll");
        this.listRef = useRef("list");
        const height = this.props.rowHeight || ROW_HEIGHT;
        this.virtualOptions = {
            count: this.props.count,
            getScrollElement: () => this.scrollRef.el,
            estimateSize: () => height,
            overscan: 20,
            observeElementRect: L.observeElementRect,
            observeElementOffset: L.observeElementOffset,
            scrollToFn: L.elementScroll,
            onChange: () => this.ticks.n++,
        };
        this.virtualizer = new L.Virtualizer(this.virtualOptions);
        this.props.onReady?.({
            scrollToIndex: (index, align = "center") => this.virtualizer.scrollToIndex(index, { align }),
            firstVisible: () => this.virtualizer.getVirtualItems().find((v) => v.end > this.virtualizer.scrollOffset)?.index ?? 0,
        });
        onMounted(() => {
            this.cleanup = this.virtualizer._didMount();
            this.virtualizer._willUpdate();
            this.measure();
            if (this.props.startIndex) {
                this.virtualizer.scrollToIndex(this.props.startIndex, { align: "start" });
            }
        });
        onPatched(() => {
            this.virtualizer._willUpdate();
            this.measure();
        });
        onWillUnmount(() => this.cleanup?.());
    }

    /** Wrapped rows have their own height: measure the rows drawn (TanStack keeps the sizes). */
    measure() {
        if (!this.props.wrap) {
            return;
        }
        for (const el of this.listRef.el?.querySelectorAll(":scope > [data-index]") || []) {
            this.virtualizer.measureElement(el);
        }
    }

    get gridStyle() {
        return this.props.columns ? `grid-template-columns: ${this.props.columns};` : "";
    }

    get rows() {
        this.ticks.n; // re-read on every render
        this.props.version;
        this.virtualizer.setOptions({ ...this.virtualOptions, count: this.props.count });
        return this.virtualizer.getVirtualItems().map((v) => {
            const row = this.props.row(v.index);
            return {
                index: v.index,
                top: v.start,
                cls: (row.cls || "") + (v.index === this.props.activeIndex ? " o_dwo_line_active" : ""),
                cells: row.cells.map((cell) => ({ ...cell, html: markup(cell.html || "") })),
            };
        });
    }

    get totalHeight() {
        return this.virtualizer.getTotalSize();
    }
}
