/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";

const toggle = (mode) => `.o_dwo_ffm_toggle[data-mode='${mode}']`; // one button per layout, the active one is lit

// normal -> wide (chatter hidden, drawer) -> focus (no top bar) -> normal again with the keyboard shortcut
registry.category("web_tour.tours").add("dwo_form_focus_mode_tour", {
    steps: () => [
        { content: "The toggle is in the control panel of the form", trigger: `.o_control_panel ${toggle("normal")}`, run: () => {} },
        { trigger: toggle("wide"), run: "click" },
        { content: "Wide: the form got its class", trigger: `.o_form_view.o_dwo_ffm_wide, ${toggle("wide")}`, run: () => {} },
        {
            content: "The chatter (when the form has one) is out of the page and the sheet is not limited in width",
            trigger: ".o_form_view.o_dwo_ffm_wide .o_form_sheet_bg",
            run() {
                const chatter = document.querySelector(".o_form_view .o-mail-Form-chatter");
                if (chatter && getComputedStyle(chatter).display !== "none") {
                    throw new Error("the chatter is still shown in wide mode");
                }
                if (getComputedStyle(this.$anchor[0]).maxWidth !== "none") {
                    throw new Error("the sheet keeps a maximum width");
                }
                if (!chatter) {
                    return;
                }
                if (!document.querySelector(".o_dwo_ffm_drawer_btn")) {
                    throw new Error("no button to open the chatter as a drawer");
                }
            },
        },
        { content: "The choice is remembered for the model", trigger: ".o_form_view.o_dwo_ffm_wide", run() {
            const key = Object.keys(localStorage).find((k) => k.startsWith("dwo_form_focus_mode.mode."));
            if (!key || localStorage.getItem(key) !== "wide") {
                throw new Error("the layout is not remembered");
            }
        } },
        {
            content: "The chatter drawer opens from its button and a click on the dimmed background closes it (when the form has a chatter)",
            trigger: ".o_form_view.o_dwo_ffm_wide",
            async run() {
                const wait = () => new Promise((resolve) => setTimeout(resolve, 400));
                if (!document.querySelector(".o_form_view .o-mail-Form-chatter")) {
                    return;
                }
                document.querySelector(".o_dwo_ffm_drawer_btn").click();
                await wait();
                if (!document.querySelector(".o_form_view.o_dwo_ffm_drawer") || !document.querySelector(".o_dwo_ffm_backdrop")) {
                    throw new Error("the drawer did not open with its dimmed background");
                }
                document.querySelector(".o_dwo_ffm_backdrop").click();
                await wait();
                if (document.querySelector(".o_form_view.o_dwo_ffm_drawer") || document.querySelector(".o_dwo_ffm_backdrop")) {
                    throw new Error("a click on the background did not close the drawer");
                }
            },
        },
        { trigger: toggle("focus"), run: "click" },
        { content: "Focus: the top bar is hidden", trigger: `.o_form_view.o_dwo_ffm_focus, ${toggle("focus")}`, run: () => {} },
        { trigger: "body.o_dwo_ffm_focus_body", run() {
            const navbar = document.querySelector(".o_main_navbar");
            if (navbar && getComputedStyle(navbar).display !== "none") {
                throw new Error("the top bar is still shown in focus mode");
            }
        } },
        {
            content: "Back to the normal form with the shortcut (Alt+Shift+F; Odoo reads Ctrl as Alt on macOS)",
            trigger: toggle("focus"),
            run() {
                const mac = /Mac/i.test(navigator.platform);
                document.body.dispatchEvent(new KeyboardEvent("keydown", {
                    key: "F", code: "KeyF", shiftKey: true, altKey: !mac, ctrlKey: mac, bubbles: true,
                }));
            },
        },
        { trigger: `${toggle("normal")}.active`, run: () => {} },
        { trigger: ".o_form_view:not(.o_dwo_ffm)", run: () => {} },
        { trigger: "body:not(.o_dwo_ffm_focus_body)", run() {
            const navbar = document.querySelector(".o_main_navbar");
            if (navbar && getComputedStyle(navbar).display === "none") {
                throw new Error("the top bar did not come back");
            }
        } },
    ],
});
