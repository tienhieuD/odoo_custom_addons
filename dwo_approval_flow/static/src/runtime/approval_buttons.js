import { Component, onWillStart, useEffect, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { approvalBus } from "./approval_bus";
import { ReasonDialog } from "./reason_dialog";

/** The approval buttons of the current user, in the header of a form. */
export class ApprovalButtons extends Component {
    static template = "dwo_approval_flow.Buttons";
    static props = {
        ...standardWidgetProps,
        stateField: { type: String, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.dialog = useService("dialog");
        this.action = useService("action");
        this.notification = useService("notification");
        this.bus = useState(approvalBus);
        this.state = useState({ buttons: [], busy: false });
        onWillStart(() => this.load());
        useEffect(
            () => {
                this.load();
            },
            () => [this.bus.rev, this.props.record.resId, this.stateKey]
        );
    }

    get stateKey() {
        const value = this.props.record.data[this.props.stateField];
        return JSON.stringify(value && value.id !== undefined ? value.id : value);
    }

    async load() {
        const record = this.props.record;
        if (!record.resId) {
            this.state.buttons = [];
            return;
        }
        const result = await this.orm.call("dwo.approval.flow", "get_buttons", [
            record.resModel,
            record.resId,
        ]);
        this.state.buttons = result.buttons;
    }

    btnClass(button) {
        if (button.color === 10) {
            return "btn-primary";
        }
        if (button.color === 1 || button.color === 9) {
            return "btn-danger";
        }
        return "btn-secondary";
    }

    label(button) {
        return button.needed > 1 ? `${button.name} (${button.count}/${button.needed})` : button.name;
    }

    async press(button) {
        const record = this.props.record;
        if (record.dirty && !(await record.save())) {
            return;
        }
        const run = async (reason) => {
            this.state.busy = true;
            try {
                const result = await this.orm.call("dwo.approval.flow", "press", [
                    record.resModel,
                    record.resId,
                    button.id,
                    reason || false,
                ]);
                if (result.status === "waiting") {
                    this.notification.add(
                        _t("Approval recorded (%(count)s of %(needed)s). Waiting for the others.", {
                            count: result.count,
                            needed: result.needed,
                        }),
                        { type: "info" }
                    );
                }
                if (result.action) {
                    await this.action.doAction(result.action);
                }
            } finally {
                this.state.busy = false;
                approvalBus.rev++;
                await record.load();
            }
        };
        if (button.ask_reason) {
            this.dialog.add(ReasonDialog, { title: button.name, confirm: run });
        } else {
            await run();
        }
    }
}

registry.category("view_widgets").add("dwo_approval_buttons", {
    component: ApprovalButtons,
    extractProps: ({ attrs }) => ({ stateField: attrs.state_field }),
});
