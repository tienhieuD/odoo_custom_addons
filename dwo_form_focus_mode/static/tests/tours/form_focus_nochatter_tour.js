/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";

// a form without a chatter (a country) shows no buttons and no bar, whatever layout is remembered
registry.category("web_tour.tours").add("dwo_form_focus_mode_nochatter_tour", {
    steps: () => [
        { content: "Remember auto chatter for the forms", trigger: ".o_list_renderer", run() {
            localStorage.setItem("dwo_form_focus_mode.mode", "auto");
        } },
        { content: "Open a country", trigger: ".o_data_row .o_data_cell", run: "click" },
        {
            content: "No layout buttons, no bar, no layout class on a form without a chatter",
            trigger: ".o_form_view .o_form_sheet",
            async run() {
                await new Promise((resolve) => setTimeout(resolve, 700));
                if (document.querySelector(".o_dwo_ffm_switch") || document.querySelector(".o_dwo_ffm_edge")
                    || document.querySelector(".o_form_view.o_dwo_ffm")) {
                    throw new Error("a form without a chatter shows the layout buttons or the bar");
                }
                localStorage.removeItem("dwo_form_focus_mode.mode");
            },
        },
    ],
});
