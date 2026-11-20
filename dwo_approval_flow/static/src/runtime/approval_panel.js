import { Component, onWillStart, useEffect, useState } from "@odoo/owl";
import { deserializeDateTime, formatDateTime } from "@web/core/l10n/dates";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { approvalBus } from "./approval_bus";
import { COLORS } from "../designer/palette";

/**
 * Status bar, "waiting for" and approval history of a document.
 * Options: show_statusbar, show_waiting, show_history, history_limit, statusbar_visible.
 */
export class ApprovalPanel extends Component {
    static template = "dwo_approval_flow.Panel";
    static props = {
        ...standardWidgetProps,
        stateField: { type: String, optional: true },
        showStatusbar: { type: Boolean, optional: true },
        showWaiting: { type: Boolean, optional: true },
        showHistory: { type: Boolean, optional: true },
        historyLimit: { type: Number, optional: true },
        statusbarVisible: { type: Array, optional: true },
    };
    static defaultProps = {
        showStatusbar: true,
        showWaiting: true,
        showHistory: true,
        historyLimit: 20,
    };

    setup() {
        this.orm = useService("orm");
        this.bus = useState(approvalBus);
        this.state = useState({ data: false, limit: this.props.historyLimit });
        onWillStart(() => this.load());
        useEffect(
            () => {
                this.load();
            },
            () => [this.bus.rev, this.props.record.resId, this.stateKey, this.state.limit]
        );
    }

    get stateKey() {
        const value = this.props.record.data[this.props.stateField];
        return JSON.stringify(value && value.id !== undefined ? value.id : value);
    }

    async load() {
        const record = this.props.record;
        if (!record.resId) {
            this.state.data = false;
            return;
        }
        this.state.data = await this.orm.call("dwo.approval.flow", "get_panel_data", [
            record.resModel,
            record.resId,
            this.state.limit,
        ]);
    }

    get states() {
        const data = this.state.data;
        const visible = this.props.statusbarVisible;
        return data.states.filter((s) => !visible || visible.includes(s.key) || s.id === data.current);
    }

    dot(state) {
        return COLORS[state.color] || false;
    }

    formatDate(value) {
        return formatDateTime(deserializeDateTime(value));
    }

    showMore() {
        this.state.limit += this.props.historyLimit;
    }
}

const flag = (value, fallback = true) => (value === undefined ? fallback : value !== "0");

registry.category("view_widgets").add("dwo_approval_panel", {
    component: ApprovalPanel,
    extractProps: ({ attrs }) => ({
        stateField: attrs.state_field,
        showStatusbar: flag(attrs.show_statusbar),
        showWaiting: flag(attrs.show_waiting),
        showHistory: flag(attrs.show_history),
        historyLimit: attrs.history_limit ? parseInt(attrs.history_limit, 10) : 20,
        statusbarVisible: attrs.statusbar_visible ? attrs.statusbar_visible.split(",") : undefined,
    }),
});
