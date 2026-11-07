import { onMounted } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { patch } from "@web/core/utils/patch";
import { ControlPanel } from "@web/search/control_panel/control_panel";

/**
 * Remembers, per action, whether the user's last explicit choice for this action was the
 * "Split" view or the plain "List" view, in `localStorage` (survives closing the tab/browser).
 * The next time the action opens on its default view (always "list": "split" is only ever
 * added as an extra option, see `ir_actions.py`), it is switched to Split automatically --
 * until the user explicitly switches back to List themselves.
 */
function storageKey(actionId) {
    return `web_split_view_mode_${actionId || 0}`;
}

function getStoredMode(actionId) {
    try {
        return browser.localStorage.getItem(storageKey(actionId));
    } catch {
        return null; // localStorage unavailable
    }
}

function setStoredMode(actionId, mode) {
    try {
        browser.localStorage.setItem(storageKey(actionId), mode);
    } catch {
        // localStorage unavailable
    }
}

patch(ControlPanel.prototype, {
    setup() {
        super.setup(...arguments);
        onMounted(() => this.autoRestoreSplitView());
    },

    /**
     * Runs once, right after this control panel (and the view below it) is mounted. Only acts
     * when we just landed on the plain "List" view of an action that also has a "Split" view
     * (`viewSwitcherEntries` is forced to an empty array by `SplitPane` for the views embedded
     * *inside* a split pane itself, see split_pane.js, so this never fires for those and never
     * loops) and the user's last explicit choice for this action was "Split".
     */
    autoRestoreSplitView() {
        const { viewType, viewSwitcherEntries, actionId } = this.env.config;
        if (viewType !== "list") {
            return;
        }
        const hasSplit = (viewSwitcherEntries || []).some((view) => view.type === "split");
        if (hasSplit && getStoredMode(actionId) === "split") {
            this.switchView("split");
        }
    },

    switchView(viewType) {
        // record the user's explicit choice *before* actually switching: by the time the new
        // view's ControlPanel mounts and calls autoRestoreSplitView, the stored value already
        // reflects this click, so switching to "list" here is never immediately bounced back.
        if (viewType === "list" || viewType === "split") {
            setStoredMode(this.env.config.actionId, viewType);
        }
        return super.switchView(...arguments);
    },
});
