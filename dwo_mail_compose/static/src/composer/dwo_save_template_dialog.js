/* @odoo-module */

import { Component, useRef, useState, onMounted } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

/** Asks the name of the template made from the email being written. */
export class DwoSaveTemplateDialog extends Component {
    static template = "dwo_mail_compose.SaveTemplateDialog";
    static components = { Dialog };
    static props = {
        onSave: Function,
        close: Function,
    };

    setup() {
        this.inputRef = useRef("name");
        this.state = useState({ name: "", saving: false });
        onMounted(() => this.inputRef.el?.focus());
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
