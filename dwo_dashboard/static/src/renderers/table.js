/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component } from "@odoo/owl";
import { formatNumber } from "../utils";

export class TableRenderer extends Component {
    static template = "dwo_dashboard.TableRenderer";
    static props = { widget: Object, result: Object };

    cell(value, meta) {
        if (value === null || value === undefined) {
            return "";
        }
        switch (meta.type) {
            case "many2one":
                return value[1];
            case "many2many":
            case "one2many":
                return value.map((v) => v[1]).join(", ");
            case "boolean":
                return value ? "✓" : "";
            case "selection":
                return (meta.selection && meta.selection[value]) || value;
            case "integer":
            case "float":
            case "monetary":
                return formatNumber(value, this.props.widget.options || {});
            default:
                return String(value);
        }
    }

    isNumber(meta) {
        return ["integer", "float", "monetary"].includes(meta.type);
    }
}
