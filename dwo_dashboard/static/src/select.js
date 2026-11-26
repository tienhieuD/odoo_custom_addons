/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onWillUnmount, useExternalListener, useRef, useState } from "@odoo/owl";

export const MARGIN = 8; // px kept between a popup and the edge of the screen

/** Put a fixed-position popup next to ``anchor`` (a DOMRect) and inside the screen: below it, above it when there is
 * no room, never past an edge; a bottom sheet on a phone. Returns the inline style. */
export function placePopup(anchor, { minWidth = 0, height = 260 } = {}) {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    if (vw < 576) {
        return `left: ${MARGIN}px; right: ${MARGIN}px; bottom: ${MARGIN}px; max-height: ${Math.round(vh * 0.6)}px;`;
    }
    const width = Math.min(Math.max(anchor.width, minWidth), vw - 2 * MARGIN);
    const left = Math.max(MARGIN, Math.min(anchor.left, vw - width - MARGIN));
    const below = vh - anchor.bottom - MARGIN;
    const above = anchor.top - MARGIN;
    if (below >= Math.min(height, 200) || below >= above) {
        return `left: ${left}px; width: ${width}px; top: ${anchor.bottom + 2}px; max-height: ${Math.min(360, Math.max(120, below - 2))}px;`;
    }
    return `left: ${left}px; width: ${width}px; bottom: ${vh - anchor.top + 2}px; max-height: ${Math.min(360, Math.max(120, above - 2))}px;`;
}

/** A selector with a search box: type to narrow the choices (instead of a native <select>).
 * Props: ``options`` [{value, label, group?}], ``value``, ``placeholder``, ``onChange`` (called with an event-like
 * {target: {value}} so the handlers written for a <select> keep working), ``clearable`` (show an empty choice). */
export class DwoSelect extends Component {
    static template = "dwo_dashboard.Select";
    static props = {
        options: Array,
        value: { optional: true },
        placeholder: { type: String, optional: true },
        onChange: Function,
        args: { type: Array, optional: true }, // handed to onChange before the event, as a handler of a list row needs its row
        class: { type: String, optional: true },
        dataLevel: { optional: true },
    };

    setup() {
        this.state = useState({ open: false, query: "", index: 0, style: "" });
        this.root = useRef("root");
        this.input = useRef("input");
        useExternalListener(window, "resize", () => this.state.open && this.place());
        useExternalListener(window, "scroll", (ev) => {
            if (this.state.open && !(ev.target.closest && ev.target.closest(".dwo-select-popup"))) {
                this.place();
            }
        }, { capture: true });
        useExternalListener(window, "pointerdown", (ev) => {
            if (this.state.open && !ev.target.closest(".dwo-select-popup") && !this.root.el.contains(ev.target)) {
                this.close();
            }
        }, { capture: true });
        onWillUnmount(() => this.close());
    }

    get current() {
        return this.props.options.find((o) => o.value === this.props.value);
    }

    get shown() {
        const q = this.state.query.trim().toLowerCase();
        return q ? this.props.options.filter((o) => String(o.label).toLowerCase().includes(q)) : this.props.options;
    }

    /** The shown choices with a heading before the first one of each group. */
    get rows() {
        const out = [];
        let group = null;
        this.shown.forEach((option, index) => {
            if (option.group && option.group !== group) {
                out.push({ heading: option.group });
            }
            group = option.group || null;
            out.push({ option, index });
        });
        return out;
    }

    place() {
        if (this.root.el) {
            this.state.style = placePopup(this.root.el.getBoundingClientRect(), { minWidth: 200 });
        }
    }

    open() {
        if (this.state.open) {
            return;
        }
        this.state.query = "";
        const at = this.props.options.findIndex((o) => o.value === this.props.value);
        this.state.index = Math.max(0, at);
        this.place();
        this.state.open = true;
        setTimeout(() => {
            if (this.input.el) {
                this.input.el.focus({ preventScroll: true });
            }
            const active = document.querySelector(".dwo-select-popup .dwo-select-option.active");
            if (active) {
                active.scrollIntoView({ block: "nearest" });
            }
        }, 0);
    }

    close() {
        this.state.open = false;
    }

    choose(option) {
        this.close();
        if (option.value !== this.props.value) {
            this.props.onChange(...(this.props.args || []), { target: { value: option.value } });
        }
        if (this.root.el) {
            this.root.el.focus({ preventScroll: true });
        }
    }

    onQuery(ev) {
        this.state.query = ev.target.value;
        this.state.index = 0;
    }

    onKey(ev) {
        const count = this.shown.length;
        const keys = { ArrowDown: 1, ArrowUp: -1 };
        if (ev.key in keys) {
            this.state.index = count ? (this.state.index + keys[ev.key] + count) % count : 0;
            const active = document.querySelectorAll(".dwo-select-popup .dwo-select-option")[this.state.index];
            if (active) {
                active.scrollIntoView({ block: "nearest" });
            }
        } else if (ev.key === "Enter" && this.shown[this.state.index]) {
            this.choose(this.shown[this.state.index]);
        } else if (ev.key === "Escape" || ev.key === "Tab") {
            this.close();
        } else {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation(); // a dialog around must not close on this Escape
    }

    onTriggerKey(ev) {
        if (["Enter", " ", "ArrowDown"].includes(ev.key)) {
            ev.preventDefault();
            this.open();
        }
    }
}
