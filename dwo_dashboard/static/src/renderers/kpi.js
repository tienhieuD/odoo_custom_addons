/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component } from "@odoo/owl";
import { formatNumber } from "../utils";

export class KpiRenderer extends Component {
    static template = "dwo_dashboard.KpiRenderer";
    static props = { widget: Object, result: Object };

    get row() {
        return this.props.result.rows[0];
    }

    get value() {
        const v = this.row ? this.row.values[0] : null;
        return v === null ? "–" : formatNumber(v, this.props.widget.options || {});
    }

    get label() {
        return this.props.result.measures[0].label;
    }
}
