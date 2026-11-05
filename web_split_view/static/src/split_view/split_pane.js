import { Component, useSubEnv } from "@odoo/owl";
import { View } from "@web/views/view";

/**
 * Hosts one of the embedded views (list on the left, form on the right) in its own sub environment:
 * the embedded views must not hijack the breadcrumbs, the display name or the view switcher of the action.
 */
export class SplitPane extends Component {
    static template = "web_split_view.SplitPane";
    static components = { View };
    static props = {
        viewProps: Object,
        splitState: Object,
        onClose: Function,
    };

    setup() {
        useSubEnv({
            splitState: this.props.splitState,
            config: {
                ...this.env.config,
                viewSwitcherEntries: [],
                noBreadcrumbs: true,
                setDisplayName: () => {},
                historyBack: () => this.props.onClose(),
            },
        });
    }
}
