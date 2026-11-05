/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";

const { Component } = owl;

export class ConcurrencyDialog extends Component {
    static template = "dwo_record_concurrency.ConcurrencyDialog";
    static components = { Dialog };
    static props = {
        conflicts: Array,
        onChoice: Function,
        close: Function,
    };

    get title() {
        return _t("Saving Record with Concurrency Warning!");
    }

    get lastWriter() {
        return this.props.conflicts.find((conflict) => conflict.write_uid_name)?.write_uid_name;
    }

    choose(choice) {
        this.props.onChoice(choice);
        this.props.close();
    }
}
