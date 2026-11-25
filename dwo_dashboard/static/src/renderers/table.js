/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { deserializeDate, deserializeDateTime, formatDate } from "@web/core/l10n/dates";
import { formatDateTimeShort, formatNumber } from "../utils";

export class TableRenderer extends Component {
    static template = "dwo_dashboard.TableRenderer";
    static props = { widget: Object, result: Object, onPick: { type: Function, optional: true } };

    setup() {
        this.action = useService("action");
    }

    get canOpen() {
        return !!(this.props.widget.options && this.props.widget.options.open_records) && !!this.props.result.ids && !!this.props.result.model;
    }

    /** Open the record of a row in its form: the standard action enforces access by itself. */
    open(index) {
        if (this.canOpen) {
            this.action.doAction({
                type: "ir.actions.act_window",
                res_model: this.props.result.model,
                res_id: this.props.result.ids[index],
                views: [[false, "form"]],
                target: "current",
            });
        }
    }

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
            case "date":
                return formatDate(deserializeDate(value));
            case "datetime":
                return formatDateTimeShort(deserializeDateTime(value));
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
