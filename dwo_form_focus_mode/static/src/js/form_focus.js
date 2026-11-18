/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
const { Component, onMounted, onPatched, onWillUnmount, useState, useSubEnv } = owl;
import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";
import { useHotkey } from "@web/core/hotkeys/hotkey_hook";
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { FormControlPanel } from "@web/views/form/control_panel/form_control_panel";

// normal: the form as Odoo shows it (default); hide: the chatter is always hidden; auto: the chatter is hidden and a bar on
// the right opens it as a drawer. The choice is for all the form views and is remembered.
const MODES = ["normal", "hide", "auto"];
const STORAGE_MODE = "dwo_form_focus_mode.mode";
const STORAGE_WIDTH = "dwo_form_focus_mode.drawer_width";
const DEFAULT_WIDTH = 530; // the width of the chatter beside the form in Odoo (px)
const MIN_WIDTH = 360;
const WIDTH_VAR = "--dwo-ffm-drawer-width";
const TOP_VAR = "--dwo-ffm-top";

function readMode() {
    try {
        const value = browser.localStorage.getItem(STORAGE_MODE);
        return MODES.includes(value) ? value : "normal";
    } catch {
        return "normal";
    }
}

function saveMode(mode) {
    try {
        if (mode === "normal") {
            browser.localStorage.removeItem(STORAGE_MODE);
        } else {
            browser.localStorage.setItem(STORAGE_MODE, mode);
        }
    } catch {
        // the layout still changes, it is just not remembered
    }
}

/** Width of the drawer, between the minimum and 92 percent of the window. */
function clampWidth(width) {
    return Math.round(Math.min(Math.max(width, MIN_WIDTH), window.innerWidth * 0.92));
}

function applyWidth(width) {
    document.documentElement.style.setProperty(WIDTH_VAR, `${clampWidth(width)}px`);
}

/** The bar, the drawer and the dimmed background start under the control panel (New, breadcrumb, pager), never over it. */
function applyTop() {
    const content = document.querySelector(".o_form_view .o_content");
    const top = content ? Math.max(Math.round(content.getBoundingClientRect().top), 0) : 106;
    document.documentElement.style.setProperty(TOP_VAR, `${top}px`);
}

/** Before the form is drawn: a model with a message_ids field most likely has a chatter (checked in the page right after). */
function dwoFfmGuessChatter(props) {
    return Boolean(props.fields && "message_ids" in props.fields);
}

function readWidth() {
    try {
        const value = Number(browser.localStorage.getItem(STORAGE_WIDTH));
        return value >= MIN_WIDTH ? value : DEFAULT_WIDTH;
    } catch {
        return DEFAULT_WIDTH;
    }
}

/**
 * Three layouts for the form views, as buttons next to the pager: normal, chatter always hidden, and auto chatter (a bar
 * on the right opens the chatter as a drawer, with a handle to change its width). The layout is a class of the form
 * (see form_focus.scss); the choice and the width of the drawer are remembered for all the forms.
 */
patch(FormController.prototype, "dwo_form_focus_mode", {
    setup() {
        this._super(...arguments);
        this.dwoFfm = useState({ mode: readMode(), drawer: false, hasChatter: dwoFfmGuessChatter(this.props) });
        useHotkey("alt+shift+f", () => this.dwoFfmCycle(), { allowRepeat: false });
        // Esc closes the chatter drawer
        useHotkey("escape", () => {
            if (this.dwoFfm.drawer) {
                this.dwoFfm.drawer = false;
            }
        }, { bypassEditableProtection: true });
        // the buttons are in the control panel (after the pager): they read the layout from here
        useSubEnv({ dwoFfm: this });
        applyWidth(readWidth());
        // the control panel can change its height (a long breadcrumb): the top follows
        const onResize = () => applyTop();
        window.addEventListener("resize", onResize);
        // a form without a chatter has nothing to hide: no buttons, no bar (checked in the page, after each drawing)
        const checkChatter = () => {
            applyTop();
            const has = Boolean(document.querySelector(".o_action_manager .o_form_view .o_FormRenderer_chatterContainer"));
            if (has !== this.dwoFfm.hasChatter) {
                this.dwoFfm.hasChatter = has;
            }
        };
        let watcher = null;
        let frame = 0;
        onMounted(() => {
            checkChatter();
            // the chatter can be drawn a little later than the form (it loads its own parts): watch the page for it
            const root = document.querySelector(".o_action_manager .o_form_view");
            if (root) {
                watcher = new MutationObserver(() => {
                    cancelAnimationFrame(frame);
                    frame = requestAnimationFrame(checkChatter);
                });
                watcher.observe(root, { childList: true, subtree: true });
            }
        });
        onPatched(checkChatter);
        onWillUnmount(() => {
            watcher?.disconnect();
            cancelAnimationFrame(frame);
        });
        onWillUnmount(() => window.removeEventListener("resize", onResize));
    },

    /** Not in a dialog (nor on a phone: there the form already has the whole screen) and only when the form has a chatter. */
    dwoFfmEnabled() {
        return !this.env.inDialog && !this.env.isSmall && this.dwoFfm.hasChatter;
    },

    dwoFfmMode() {
        return this.dwoFfmEnabled() ? this.dwoFfm.mode : "normal";
    },

    /** What a button does, for its tooltip. */
    dwoFfmTitleOf(mode) {
        return {
            normal: _t("Normal: the chatter is shown beside the form, as Odoo does."),
            hide: _t("Always hide the chatter: the form uses the full width, on every form."),
            auto: _t("Auto chatter: the chatter is hidden; a bar on the right opens it as a drawer."),
        }[mode];
    },

    /** Choose a layout for all the forms. */
    dwoFfmSet(mode) {
        if (!this.dwoFfmEnabled() || !MODES.includes(mode) || mode === this.dwoFfm.mode) {
            return;
        }
        this.dwoFfm.mode = mode;
        this.dwoFfm.drawer = false;
        saveMode(mode);
        setTimeout(applyTop); // the edge bar needs the top once the form is drawn
    },

    dwoFfmCycle() {
        this.dwoFfmSet(MODES[(MODES.indexOf(this.dwoFfm.mode) + 1) % MODES.length]);
    },

    /** The handle on the left edge of the drawer: drag it to change the width (remembered). */
    dwoFfmStartResize(ev) {
        ev.preventDefault();
        let width = readWidth();
        const move = (e) => {
            width = clampWidth(window.innerWidth - e.clientX);
            applyWidth(width);
        };
        const stop = () => {
            window.removeEventListener("pointermove", move);
            window.removeEventListener("pointerup", stop);
            try {
                browser.localStorage.setItem(STORAGE_WIDTH, String(width));
            } catch {
                // the width is used now, it is just not remembered
            }
        };
        window.addEventListener("pointermove", move);
        window.addEventListener("pointerup", stop);
    },

    dwoFfmToggleDrawer() {
        applyTop();
        this.dwoFfm.drawer = !this.dwoFfm.drawer;
    },

    get className() {
        const result = this._super();
        if (this.dwoFfmMode() !== "normal") {
            result[`o_dwo_ffm_${this.dwoFfmMode()}`] = true;
            result["o_dwo_ffm"] = true;
            if (this.dwoFfm.drawer) {
                result["o_dwo_ffm_drawer"] = true;
            }
        }
        return result;
    },
});

/** The buttons of the control panel, after the pager of a form view (the form gives its layout in the environment). */
export class DwoFfmButton extends Component {
    setup() {
        // renders again when the layout changes (the state is the one of the form controller)
        this.layout = useState(this.env.dwoFfm.dwoFfm);
    }

    get ffm() {
        this.layout.mode; // read: this component follows the layout and the presence of a chatter
        this.layout.hasChatter;
        return this.env.dwoFfm;
    }
}

FormControlPanel.components = { ...FormControlPanel.components, DwoFfmButton };
DwoFfmButton.template = "dwo_form_focus_mode.Button";
DwoFfmButton.props = {};
