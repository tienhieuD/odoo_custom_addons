import { Component, proxy, t, useProps } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class ReasonDialog extends Component {
    static template = "dwo_approval_flow.ReasonDialog";
    static components = { Dialog };
    props = useProps({ title: t.string(), confirm: t.function(), close: t.function() });

    setup() {
        this.state = proxy({ reason: "", busy: false });
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
