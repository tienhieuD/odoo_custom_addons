/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export const PAGE_NAME_MAX = 60; // the size of the field on the server

/** Asks for the name of a page, to create it or to rename it. Nothing happens before OK. */
export class PageNameDialog extends Component {
    static template = "dwo_dashboard.PageNameDialog";
    static components = { Dialog };
    static props = {
        title: String,
        initial: { type: String, optional: true },
        confirmLabel: { type: String, optional: true },
        onConfirm: Function,
        close: Function,
    };

    setup() {
        this.max = PAGE_NAME_MAX;
        this.input = useRef("input");
        this.state = useState({ name: this.props.initial || "", busy: false });
        onMounted(() => {
            this.input.el.focus();
            this.input.el.select();
        });
    }

    get valid() {
        return !!this.state.name.trim();
    }

    async confirm() {
        if (!this.valid || this.state.busy) {
            return;
        }
        this.state.busy = true;
        try {
            await this.props.onConfirm(this.state.name.trim());
            this.props.close();
        } finally {
            this.state.busy = false;
        }
    }

    onKeydown(ev) {
        if (ev.key === "Enter") {
            ev.preventDefault();
            this.confirm();
        }
    }
}
