/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onWillUnmount, proxy, useEffect } from "@odoo/owl";
import { useSubEnv } from "@web/owl2/utils";
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
        // Odoo 20 (Owl 3): proxy instead of useState
        this.dwoFfm = proxy({ mode: readMode(this.props.resModel), drawer: false });
        useHotkey("alt+shift+f", () => this.dwoFfmCycle(), { allowRepeat: false });
        // Esc closes the chatter drawer
        useHotkey("escape", () => {
            if (this.dwoFfm.drawer) {
                this.dwoFfm.drawer = false;
            }
        }, { bypassEditableProtection: true });
        // the button is in the control panel (before the pager): it reads the layout from here
        useSubEnv({ dwoFfm: this });
        // Owl 3: useEffect re-runs by itself when the signals it reads change
        useEffect(() => {
            document.body.classList.toggle(BODY_CLASS, this.dwoFfmEnabled && this.dwoFfm.mode === "focus");
        });
        onWillUnmount(() => document.body.classList.remove(BODY_CLASS));
    },

    /** Not in a dialog and not on a phone: there the form already has the whole screen. */
    get dwoFfmEnabled() {
        return !this.env.inDialog && !this.ui.isSmall;
    },

    get dwoFfmMode() {
        return this.dwoFfmEnabled ? this.dwoFfm.mode : "normal";
    },

    /** Name of a layout, for the tooltip of its button. */
    dwoFfmTitleOf(mode) {
        return {
            normal: _t("Normal form (Alt+Shift+F cycles the layouts)"),
            wide: _t("Wide form: hide the chatter and use the full width"),
            focus: _t("Focus mode: also hide the top bar"),
        }[mode];
    },

    dwoFfmSet(mode) {
        if (!this.dwoFfmEnabled || !MODES.includes(mode) || mode === this.dwoFfm.mode) {
            return;
        }
        this.dwoFfm.mode = mode;
        this.dwoFfm.drawer = false;
        saveMode(this.props.resModel, mode);
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

    // Owl 3: the layout is a proxy of the form controller; reading it in the template makes this component follow it
    get ffm() {
        return this.env.dwoFfm;
    }
}

patch(ControlPanel, {
    components: { ...ControlPanel.components, DwoFfmButton },
});
