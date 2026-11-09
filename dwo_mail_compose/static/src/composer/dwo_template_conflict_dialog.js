/* @odoo-module */

import { Component } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

/**
 * Asked when a template is chosen while the subject or the message already holds the
 * user's own text: replace it, keep it and add the template after it, or give up.
 */
export class DwoTemplateConflictDialog extends Component {
    static template = "dwo_mail_compose.TemplateConflictDialog";
    static components = { Dialog };
    static props = {
        onOverwrite: Function,
        onAppend: Function,
        close: Function,
    };

    overwrite() {
        this.props.onOverwrite();
        this.props.close();
    }

    append() {
        this.props.onAppend();
        this.props.close();
    }
}
