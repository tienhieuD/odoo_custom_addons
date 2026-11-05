import { Component, t, useProps } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";

export class ConcurrencyDialog extends Component {
    static template = "dwo_record_concurrency.ConcurrencyDialog";
    static components = { Dialog };
    props = useProps({
        conflicts: t.any(),
        onChoice: t.function(),
        close: t.function(),
    });

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
