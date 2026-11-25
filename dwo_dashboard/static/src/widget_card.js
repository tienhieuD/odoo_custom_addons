/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

/** One widget of the grid: title, state (loading / error / data) and the renderer of its visual type. Tolerant on
 * render: an unknown type or an error in this widget never touches the others. */
export class WidgetCard extends Component {
    static template = "dwo_dashboard.WidgetCard";
    static props = {
        widget: Object,
        entry: { type: Object, optional: true },
        editing: { type: Boolean, optional: true },
        onEdit: { type: Function, optional: true },
        onRemove: { type: Function, optional: true },
    };

    get Renderer() {
        return registry.category("dwo_dashboard.visuals").get(this.props.widget.type, null);
    }

    get title() {
        return this.props.widget.title || "";
    }

    get truncatedNote() {
        const result = this.props.entry && this.props.entry.result;
        const t = result && result.truncated;
        if (!t) {
            return "";
        }
        if (t.axis) {
            // "Top 8": the number of groups of the first dimension that are shown
            const keys = result.rows.map((r) => String(r.keys[0]));
            const shown = new Set(keys.filter((k) => k !== "__other")).size;
            return keys.includes("__other") ? _t("Top %s + Other", shown) : _t("Top %s", shown);
        }
        if (t.rows) {
            return _t("First %s rows", result.rows.length);
        }
        return t.series ? _t("Main series only") : "";
    }

    get isEmpty() {
        const result = this.props.entry && this.props.entry.result;
        return !!result && result.kind !== "grouped" ? !result.rows.length : !!result && result.dims.length > 0 && !result.rows.length;
    }

    get timezoneNote() {
        const r = this.props.entry && this.props.entry.result;
        return r && r.notes && r.notes.includes("timezone") ? _t("Times in UTC") : "";
    }

    get errorIcon() {
        const code = this.props.entry && this.props.entry.error && this.props.entry.error.code;
        return code === "access" ? "fa-lock" : code === "timeout" ? "fa-clock-o" : "fa-exclamation-triangle";
    }
}
