import { Component } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class ConcurrencyDialog extends Component {
    static template = "dwo_record_concurrency.ConcurrencyDialog";
    static components = { Dialog };
    static props = {
        conflicts: Array,
        onChoice: Function,
        close: Function,
    };

    get lastWriter() {
        return this.props.conflicts.find((conflict) => conflict.write_uid_name)?.write_uid_name;
    }

    choose(choice) {
        this.props.onChoice(choice);
        this.props.close();
    }
}
