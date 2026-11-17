/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";

const toggle = (mode) => `.o_dwo_ffm_toggle[data-mode='${mode}']`; // one button per layout, the one that is on is lit

// normal (default) -> chatter always hidden -> auto chatter (bar, drawer, width) -> normal; the shortcut
registry.category("web_tour.tours").add("dwo_form_focus_mode_tour", {
    steps: () => [
        { content: "Three buttons right after the pager of the control panel, normal is lit", trigger: `.o_control_panel .o_cp_pager + .o_dwo_ffm_switch ${toggle("normal")}.active` },
        { trigger: `.o_dwo_ffm_switch ${toggle("hide")}` },
        { trigger: `.o_dwo_ffm_switch ${toggle("auto")}` },
        { trigger: toggle("hide"), run: "click" },
        { content: "Always hide: the form got its class and the button is lit", trigger: `.o_form_view.o_dwo_ffm_hide, ${toggle("hide")}.active` },
        {
            content: "The chatter (when the form has one) is out of the page, there is no bar, and the sheet is not limited in width",
            trigger: ".o_form_view.o_dwo_ffm_hide .o_form_sheet_bg",
            run() {
                const chatter = document.querySelector(".o_form_view .o-mail-Form-chatter");
                if (chatter && getComputedStyle(chatter).display !== "none") {
                    throw new Error("the chatter is still shown in hide mode");
                }
                if (document.querySelector(".o_dwo_ffm_edge")) {
                    throw new Error("always hide must not show the bar of auto chatter");
                }
                if (getComputedStyle((this.anchor || this.$anchor[0])).maxWidth !== "none") {
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
        { content: "Auto chatter: the button is lit, the bar on the right with its words starts under the control panel, the chatter hidden", trigger: `.o_form_view.o_dwo_ffm_auto, ${toggle("auto")}.active`, run() {
            if (!document.querySelector(".o_form_view .o-mail-Form-chatter")) {
                return; // no Discuss: no chatter, no bar
            }
            const bar = document.querySelector(".o_dwo_ffm_edge");
            if (!bar || !bar.textContent.includes("Auto chatter")) {
                throw new Error("no bar with the words Auto chatter");
            }
            const panel = document.querySelector(".o_form_view .o_control_panel");
            if (panel && bar.getBoundingClientRect().top < panel.getBoundingClientRect().bottom - 1) {
                throw new Error("the bar covers the control panel");
            }
        } },
        {
            content: "The bar opens the drawer (as wide as the chatter of Odoo), the handle changes its width, a click on the dimmed background closes it",
            trigger: ".o_form_view.o_dwo_ffm_auto",
            async run() {
                const wait = () => new Promise((resolve) => setTimeout(resolve, 400));
                if (!document.querySelector(".o_form_view .o-mail-Form-chatter")) {
                    return;
                }
                document.querySelector(".o_dwo_ffm_edge").click();
                await wait();
                const drawer = document.querySelector(".o_form_view .o-mail-Form-chatter");
                if (!document.querySelector(".o_form_view.o_dwo_ffm_drawer") || !document.querySelector(".o_dwo_ffm_backdrop")) {
                    throw new Error("the drawer did not open with its dimmed background");
                }
                const wanted = Math.min(530, window.innerWidth * 0.92);
                if (drawer.getBoundingClientRect().width < wanted - 2) {
                    throw new Error("the drawer is narrower than the chatter of Odoo: " + drawer.getBoundingClientRect().width);
                }
                const panel = document.querySelector(".o_form_view .o_control_panel");
                if (panel && drawer.getBoundingClientRect().top < panel.getBoundingClientRect().bottom - 1) {
                    throw new Error("the drawer covers the control panel (New, breadcrumb, pager)");
                }
                const barTop = document.querySelector(".o_dwo_ffm_backdrop").getBoundingClientRect().top;
                if (panel && barTop < panel.getBoundingClientRect().bottom - 1) {
                    throw new Error("the dimmed background covers the control panel");
                }
                const handle = document.querySelector(".o_dwo_ffm_resizer");
                if (!handle) {
                    throw new Error("no handle to change the width");
                }
                const target = Math.min(window.innerWidth - 40, 700);
                handle.dispatchEvent(new PointerEvent("pointerdown", { bubbles: true, clientX: window.innerWidth - 530 }));
                window.dispatchEvent(new PointerEvent("pointermove", { clientX: window.innerWidth - target }));
                window.dispatchEvent(new PointerEvent("pointerup", {}));
                await wait();
                if (Math.abs(drawer.getBoundingClientRect().width - target) > 2 || localStorage.getItem("dwo_form_focus_mode.drawer_width") !== String(target)) {
                    throw new Error("the width did not change or is not remembered: " + drawer.getBoundingClientRect().width);
                }
                document.querySelector(".o_dwo_ffm_backdrop").click();
                await wait();
                if (document.querySelector(".o_form_view.o_dwo_ffm_drawer") || document.querySelector(".o_dwo_ffm_backdrop")) {
                    throw new Error("a click on the background did not close the drawer");
                }
                localStorage.removeItem("dwo_form_focus_mode.drawer_width");
                document.documentElement.style.removeProperty("--dwo-ffm-drawer-width");
            },
        },
        { content: "Back to normal", trigger: toggle("normal"), run: "click" },
        { trigger: `.o_form_view:not(.o_dwo_ffm), ${toggle("normal")}.active` },
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
        { trigger: `.o_form_view.o_dwo_ffm_hide, ${toggle("hide")}.active` },
        { content: "Leave the test browser as it was", trigger: toggle("normal"), run: "click" },
    ],
});
