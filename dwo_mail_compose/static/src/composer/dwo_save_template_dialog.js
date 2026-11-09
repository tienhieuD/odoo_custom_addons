import { Component, onMounted, proxy, signal, t, useProps } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

/** Asks the name of the template made from the email being written. */
export class DwoSaveTemplateDialog extends Component {
    static template = "dwo_mail_compose.SaveTemplateDialog";
    static components = { Dialog };
    props = useProps({
        onSave: t.function(),
        close: t.function(),
    });

    setup() {
        this.inputRef = signal.ref();
        this.state = proxy({ name: "", saving: false });
        onMounted(() => this.inputRef()?.focus());
    }

    async save() {
        if (!this.state.name.trim() || this.state.saving) {
            return;
        }
        this.state.saving = true;
        try {
            await this.props.onSave(this.state.name.trim());
            this.props.close();
        } finally {
            this.state.saving = false;
        }
    }

    onKeydown(ev) {
        if (ev.key === "Enter") {
            ev.preventDefault();
            this.save();
        }
    }
}
