/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onWillUnmount, useEffect, useState, useSubEnv } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";
import { useHotkey } from "@web/core/hotkeys/hotkey_hook";
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { ControlPanel } from "@web/search/control_panel/control_panel";

const MODES = ["normal", "wide", "focus"];
const STORAGE = "dwo_form_focus_mode.mode.";
const BODY_CLASS = "o_dwo_ffm_focus_body";

function readMode(resModel) {
    try {
        const value = browser.localStorage.getItem(STORAGE + resModel);
        return MODES.includes(value) ? value : "normal";
    } catch {
        return "normal";
    }
}

function saveMode(resModel, mode) {
    try {
        if (mode === "normal") {
            browser.localStorage.removeItem(STORAGE + resModel);
        } else {
            browser.localStorage.setItem(STORAGE + resModel, mode);
        }
    } catch {
        // the layout still changes, it is just not remembered
    }
}

/**
 * Three layouts for a form view: normal, wide (chatter hidden, full width) and focus (also without the top bar). The
 * chatter comes back as a side drawer. The layout is a class of the form (see form_focus.scss), remembered by model.
 */
patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        this.dwoFfm = useState({ mode: readMode(this.props.resModel), drawer: false });
        useHotkey("alt+shift+f", () => this.dwoFfmCycle(), { allowRepeat: false });
        // the button is in the control panel (before the pager): it reads the layout from here
        useSubEnv({ dwoFfm: this });
        useEffect(
            (active) => {
                document.body.classList.toggle(BODY_CLASS, active);
            },
            () => [this.dwoFfmEnabled && this.dwoFfm.mode === "focus"]
        );
        onWillUnmount(() => document.body.classList.remove(BODY_CLASS));
    },

    /** Not in a dialog and not on a phone: there the form already has the whole screen. */
    get dwoFfmEnabled() {
        return !this.env.inDialog && !this.env.isSmall;
    },

    get dwoFfmMode() {
        return this.dwoFfmEnabled ? this.dwoFfm.mode : "normal";
    },

    /** What a click does, as the label of the button. */
    get dwoFfmLabel() {
        return { normal: _t("Wide form"), wide: _t("Focus mode"), focus: _t("Normal form") }[this.dwoFfmMode];
    },

    get dwoFfmTitle() {
        return {
            normal: _t("Wide form: hide the chatter and use the full width (Alt+Shift+F)"),
            wide: _t("Focus mode: also hide the top bar (Alt+Shift+F)"),
            focus: _t("Back to the normal form (Alt+Shift+F)"),
        }[this.dwoFfmMode];
    },

    get dwoFfmIcon() {
        return this.dwoFfmMode === "normal" ? "fa-expand" : this.dwoFfmMode === "wide" ? "fa-arrows-alt" : "fa-compress";
    },

    dwoFfmCycle() {
        if (!this.dwoFfmEnabled) {
            return;
        }
        const next = MODES[(MODES.indexOf(this.dwoFfm.mode) + 1) % MODES.length];
        this.dwoFfm.mode = next;
        this.dwoFfm.drawer = false;
        saveMode(this.props.resModel, next);
    },

    dwoFfmToggleDrawer() {
        this.dwoFfm.drawer = !this.dwoFfm.drawer;
    },

    get className() {
        const result = super.className;
        if (this.dwoFfmMode !== "normal") {
            result[`o_dwo_ffm_${this.dwoFfmMode}`] = true;
            result["o_dwo_ffm"] = true;
            if (this.dwoFfm.drawer) {
                result["o_dwo_ffm_drawer"] = true;
            }
        }
        return result;
    },
});

/** The button of the control panel, before the pager of a form view (the form gives its layout in the environment). */
export class DwoFfmButton extends Component {
    static template = "dwo_form_focus_mode.Button";
    static props = {};

    setup() {
        // renders again when the layout changes (the state is the one of the form controller)
        this.layout = useState(this.env.dwoFfm.dwoFfm);
    }

    get ffm() {
        this.layout.mode; // read: this component follows the layout
        return this.env.dwoFfm;
    }
}

patch(ControlPanel, {
    components: { ...ControlPanel.components, DwoFfmButton },
});
