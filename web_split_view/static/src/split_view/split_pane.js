/** @odoo-module **/

import { Component, useSubEnv } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { View } from "@web/views/view";

/**
 * Hosts one of the embedded views (list on the left, form on the right) in its own sub environment:
 * the embedded views must not hijack the breadcrumbs, the display name or the view switcher of the action,
 * and each one exports its own state (search, pager, scroll...) into its own recorders.
 */
export class SplitPane extends Component {
    static template = "web_split_view.SplitPane";
    static components = { View };
    static props = {
        viewProps: Object,
        splitState: Object,
        onClose: Function,
        // recorders (globalState, localState) where the embedded view exports its state for the controller
        recorders: Object,
    };

    setup() {
        useSubEnv({
            splitState: this.props.splitState,
            __getGlobalState__: this.props.recorders.globalState,
            __getLocalState__: this.props.recorders.localState,
            config: {
                ...this.env.config,
                viewSwitcherEntries: [],
                // the save/discard indicator of the form lives inside the (single, fixed) breadcrumb
                noBreadcrumbs: false,
                breadcrumbs: [{ jsId: "web_split_view_form", name: _t("Details") }],
                setDisplayName: () => {},
                historyBack: () => this.props.onClose(),
            },
        });
    }
}
