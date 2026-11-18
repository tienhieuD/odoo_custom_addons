/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import tour from "web_tour.tour";

const toggle = (mode) => `.o_dwo_ffm_toggle[data-mode='${mode}']`; // one button per layout, the one that is on is lit
const CHATTER = ".o_form_view .o_FormRenderer_chatterContainer";
const noop = () => {};

// normal (default) -> chatter always hidden -> auto chatter (bar, drawer, width) -> normal; the shortcut
tour.register("dwo_form_focus_mode_tour", { test: true }, [
    { content: "Three buttons right after the pager of the control panel, normal is lit", trigger: `.o_control_panel .o_cp_pager + .o_dwo_ffm_switch ${toggle("normal")}.active`, run: noop },
    { trigger: `.o_dwo_ffm_switch ${toggle("hide")}`, run: noop },
    { trigger: `.o_dwo_ffm_switch ${toggle("auto")}`, run: noop },
    { trigger: toggle("hide"), run: "click" },
    { content: "Always hide: the form got its class and the button is lit", trigger: `.o_form_view.o_dwo_ffm_hide ${toggle("hide")}.active`, run: noop },
    {
        content: "The chatter is out of the page, there is no bar, and the sheet is not limited in width",
        trigger: ".o_form_view.o_dwo_ffm_hide .o_form_sheet_bg",
        run() {
            const chatter = document.querySelector(CHATTER);
            if (chatter && getComputedStyle(chatter).display !== "none") {
                throw new Error("the chatter is still shown in hide mode");
            }
            if (document.querySelector(".o_dwo_ffm_edge")) {
                throw new Error("always hide must not show the bar of auto chatter");
            }
            if (getComputedStyle(document.querySelector(".o_form_view .o_form_sheet")).maxWidth !== "none") {
                throw new Error("the sheet keeps a maximum width");
            }
        },
    },
    { content: "The choice is remembered for all the forms", trigger: ".o_form_view.o_dwo_ffm_hide", run() {
        if (localStorage.getItem("dwo_form_focus_mode.mode") !== "hide") {
            throw new Error("the layout is not remembered");
        }
    } },
    { trigger: toggle("auto"), run: "click" },
    { content: "Auto chatter: the button is lit, the bar on the right with its words starts under the control panel, the chatter hidden", trigger: `.o_form_view.o_dwo_ffm_auto ${toggle("auto")}.active`, run: noop },
    { content: "The bar", trigger: ".o_dwo_ffm_edge", run() {
        const bar = document.querySelector(".o_dwo_ffm_edge");
        if (!bar.textContent.includes("Auto chatter")) {
            throw new Error("no bar with the words Auto chatter");
        }
        const panel = document.querySelector(".o_form_view .o_control_panel");
        if (panel && bar.getBoundingClientRect().top < panel.getBoundingClientRect().bottom - 1) {
            throw new Error("the bar covers the control panel");
        }
        if (getComputedStyle(document.querySelector(CHATTER)).display !== "none") {
            throw new Error("the chatter is shown in auto mode before the drawer is opened");
        }
    } },
    { content: "The bar opens the drawer", trigger: ".o_dwo_ffm_edge", run: "click" },
    {
        content: "The drawer is as wide as the chatter of Odoo, under the control panel, with a dimmed background",
        trigger: ".o_form_view.o_dwo_ffm_drawer .o_dwo_ffm_backdrop",
        run() {
            const drawer = document.querySelector(CHATTER);
            const wanted = Math.min(530, window.innerWidth * 0.92);
            if (drawer.getBoundingClientRect().width < wanted - 2) {
                throw new Error("the drawer is narrower than the chatter of Odoo: " + drawer.getBoundingClientRect().width);
            }
            const panel = document.querySelector(".o_form_view .o_control_panel");
            if (panel && drawer.getBoundingClientRect().top < panel.getBoundingClientRect().bottom - 1) {
                throw new Error("the drawer covers the control panel (New, breadcrumb, pager)");
            }
            const backTop = document.querySelector(".o_dwo_ffm_backdrop").getBoundingClientRect().top;
            if (panel && backTop < panel.getBoundingClientRect().bottom - 1) {
                throw new Error("the dimmed background covers the control panel");
            }
            if (!drawer.querySelector(".o_ChatterContainer")) {
                throw new Error("the chatter is not in the drawer");
            }
        },
    },
    {
        content: "The handle changes the width, which is remembered",
        trigger: ".o_dwo_ffm_resizer",
        run() {
            const target = Math.min(window.innerWidth - 40, 700);
            document.querySelector(".o_dwo_ffm_resizer").dispatchEvent(
                new PointerEvent("pointerdown", { bubbles: true, clientX: window.innerWidth - 530 }));
            window.dispatchEvent(new PointerEvent("pointermove", { clientX: window.innerWidth - target }));
            window.dispatchEvent(new PointerEvent("pointerup", {}));
        },
    },
    {
        content: "The drawer got the new width",
        trigger: ".o_form_view.o_dwo_ffm_drawer",
        run() {
            const target = Math.min(window.innerWidth - 40, 700);
            const width = document.querySelector(CHATTER).getBoundingClientRect().width;
            if (Math.abs(width - target) > 2 || localStorage.getItem("dwo_form_focus_mode.drawer_width") !== String(target)) {
                throw new Error("the width did not change or is not remembered: " + width);
            }
        },
    },
    { content: "A click on the dimmed background closes the drawer", trigger: ".o_dwo_ffm_backdrop", run: "click" },
    { content: "Closed, and the bar is back", trigger: ".o_form_view.o_dwo_ffm_auto:not(.o_dwo_ffm_drawer) .o_dwo_ffm_edge", run() {
        localStorage.removeItem("dwo_form_focus_mode.drawer_width");
        document.documentElement.style.removeProperty("--dwo-ffm-drawer-width");
    } },
    { content: "Back to normal", trigger: toggle("normal"), run: "click" },
    { trigger: `.o_form_view:not(.o_dwo_ffm) ${toggle("normal")}.active`, run: noop },
    {
        content: "The shortcut (Alt+Shift+F; Odoo reads Ctrl as Alt on macOS) goes to the next layout: always hide",
        trigger: toggle("normal"),
        run() {
            const mac = /Mac/i.test(navigator.platform);
            document.body.dispatchEvent(new KeyboardEvent("keydown", {
                key: "F", code: "KeyF", shiftKey: true, altKey: !mac, ctrlKey: mac, bubbles: true,
            }));
        },
    },
    { trigger: `.o_form_view.o_dwo_ffm_hide ${toggle("hide")}.active`, run: noop },
    { content: "Leave the test browser as it was", trigger: toggle("normal"), run: "click" },
]);
