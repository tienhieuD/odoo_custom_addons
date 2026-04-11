/** @odoo-module */

import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { patch } from '@web/core/utils/patch';


patch(
    ConfirmationDialog.prototype,
    {
        _discard() {
            return this.execButton(this.props.discard);
        },
    }
)

ConfirmationDialog.props = {
    ...ConfirmationDialog.props,
    bodyPrewrap: { type: Boolean, optional: true },
    discard: { type: Function, optional: true },
    discardLabel: { type: String, optional: true },
    discardClass: { type: String, optional: true },
};

ConfirmationDialog.defaultProps = {
    ...ConfirmationDialog.defaultProps,
    bodyPrewrap: true,
}