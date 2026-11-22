/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { sprintf } from "@web/core/utils/strings";
import widgetRegistry from "web.widgetRegistry";
import { makeOrm, notify, doAction } from "../designer/compat";
import { approvalBus } from "./approval_bus";

const { Component } = owl;
const { onMounted, onWillStart, onWillUnmount, onWillUpdateProps, useState } = owl.hooks;

/** The approval buttons of the current user, in the header of a form (a widget of Odoo 15). */
export class ApprovalButtons extends Component {
    setup() {
        this.orm = makeOrm(this.env);
        this.state = useState({ buttons: [], busy: false, asking: null, reason: "" });
        this.onChanged = () => this.load(this.props);
        onWillStart(() => this.load(this.props));
        onWillUpdateProps((next) => this.load(next));
        onMounted(() => approvalBus.on("changed", this, this.onChanged));
        onWillUnmount(() => approvalBus.off("changed", this, this.onChanged));
    }

    async load(props) {
        const record = props.record;
        if (!record.res_id) {
            this.state.buttons = [];
            return;
        }
        const result = await this.orm.call("dwo.approval.flow", "get_buttons", [record.model, record.res_id]);
        this.state.buttons = result.buttons;
    }

    btnClass(button) {
        if (button.color === 10) {
            return "btn-outline-primary";
        }
        if (button.color === 1 || button.color === 9) {
            return "btn-outline-danger";
        }
        return "btn-outline-secondary";
    }

    label(button) {
        return button.needed > 1 ? `${button.name} (${button.count}/${button.needed})` : button.name;
    }

    press(button) {
        if (button.ask_reason) {
            this.state.asking = button;
            this.state.reason = "";
        } else {
            this.run(button, false);
        }
    }

    confirmReason() {
        const reason = this.state.reason.trim();
        if (!reason || this.state.busy) {
            return;
        }
        const button = this.state.asking;
        this.state.asking = null;
        this.run(button, reason);
    }

    cancelReason() {
        this.state.asking = null;
    }

    async run(button, reason) {
        const record = this.props.record;
        this.state.busy = true;
        try {
            const result = await this.orm.call("dwo.approval.flow", "press", [record.model, record.res_id, button.id, reason || false]);
            if (result.status === "waiting") {
                notify(this.env, sprintf(_t("Approval recorded (%(count)s of %(needed)s). Waiting for the others."), {
                    count: result.count,
                    needed: result.needed,
                }), "info");
            }
            if (result.action) {
                doAction(this.env, result.action);
            }
        } catch (error) {
            if (error && error.event) {
                error.event.preventDefault();
            }
            const data = error && error.message && error.message.data;
            notify(this.env, (data && data.message) || _t("The button could not be pressed."), "danger");
        } finally {
            this.state.busy = false;
            approvalBus.trigger("changed");
            this.trigger("reload", { db_id: record.id, keepChanges: true });
        }
    }
}
ApprovalButtons.template = "dwo_approval_flow.Buttons";

widgetRegistry.add("dwo_approval_buttons", ApprovalButtons);
