import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class ReasonDialog extends Component {
    static template = "dwo_approval_flow.ReasonDialog";
    static components = { Dialog };
    static props = { title: String, confirm: Function, close: Function };

    setup() {
        this.state = useState({ reason: "", busy: false });
    }

    async onConfirm() {
        const reason = this.state.reason.trim();
        if (!reason || this.state.busy) {
            return;
        }
        this.state.busy = true;
        try {
            await this.props.confirm(reason);
            this.props.close();
        } finally {
            this.state.busy = false;
        }
    }
}
