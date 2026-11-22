/** @odoo-module **/
import widgetRegistry from "web.widgetRegistry";
import { makeOrm } from "../designer/compat";
import { approvalBus } from "./approval_bus";

const { Component } = owl;
const { onMounted, onWillStart, onWillUnmount, onWillUpdateProps, useState } = owl.hooks;

const flag = (value, fallback = true) => (value === undefined ? fallback : value !== "0");

/**
 * Status bar, "waiting for" and approval history of a document.
 * Options: show_statusbar, show_waiting, show_history, history_limit, statusbar_visible.
 */
export class ApprovalPanel extends Component {
    setup() {
        this.orm = makeOrm(this.env);
        const attrs = this.props.node.attrs;
        this.options = {
            showStatusbar: flag(attrs.show_statusbar),
            showWaiting: flag(attrs.show_waiting),
            showHistory: flag(attrs.show_history),
            historyLimit: attrs.history_limit ? parseInt(attrs.history_limit, 10) : 20,
            statusbarVisible: attrs.statusbar_visible ? attrs.statusbar_visible.split(",") : undefined,
        };
        this.state = useState({ data: false, limit: this.options.historyLimit });
        this.onChanged = () => this.load(this.props);
        onWillStart(() => this.load(this.props));
        onWillUpdateProps((next) => this.load(next));
        onMounted(() => approvalBus.on("changed", this, this.onChanged));
        onWillUnmount(() => approvalBus.off("changed", this, this.onChanged));
    }

    async load(props) {
        const record = props.record;
        if (!record.res_id) {
            this.state.data = false;
            return;
        }
        this.state.data = await this.orm.call("dwo.approval.flow", "get_panel_data", [record.model, record.res_id, this.state.limit]);
    }

    get states() {
        const data = this.state.data;
        const visible = this.options.statusbarVisible;
        // Odoo's own status bar lists the states in reverse (the bar is laid out right to left)
        const shown = (s) => (visible ? visible.includes(s.key) : s.visible !== false);
        return data.states.filter((s) => shown(s) || s.id === data.current).reverse();
    }

    formatDate(value) {
        return new Date(value.replace(" ", "T") + "Z").toLocaleString();
    }

    showMore() {
        this.state.limit += this.options.historyLimit;
        this.load(this.props);
    }
}
ApprovalPanel.template = "dwo_approval_flow.Panel";

widgetRegistry.add("dwo_approval_panel", ApprovalPanel);
