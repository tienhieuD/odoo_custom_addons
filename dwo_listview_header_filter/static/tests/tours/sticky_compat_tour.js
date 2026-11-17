/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
// Next to listview_sticky_header_and_column (pin button in the header, frozen column): the two icons do not overlap,
// both work, and the frozen column and the sticky header stay in place when a filter is applied.
import { registry } from "@web/core/registry";

const th = (name) => `.o_list_renderer th[data-name='${name}']`;

registry.category("web_tour.tours").add("dwo_listview_header_filter_sticky_tour", {
    steps: () => [
        {
            trigger: ".o_action_manager .o_control_panel",
            run() {
                document.querySelector(".o_switch_view.o_list:not(.active)")?.click();
            },
        },
        { content: "Both icons are in the header (the pin button shows on hover only)", trigger: `${th("name")}:has(.js_pin_this_column):has(.o_dwo_hf_btn)`, run: () => {} },
        {
            content: "The pin button and the filter icon (both shown on hover) do not overlap",
            trigger: th("name"),
            run() {
                const header = this.anchor || this.$anchor[0];
                const pin = header.querySelector(".js_pin_this_column");
                const filter = header.querySelector(".o_dwo_hf_btn");
                for (const el of [pin, filter]) {
                    el.style.setProperty("display", "block", "important");
                }
                const a = filter.getBoundingClientRect();
                const b = pin.getBoundingClientRect();
                for (const el of [pin, filter]) {
                    el.style.removeProperty("display");
                }
                const overlap = a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;
                if (!a.width || !b.width || overlap) {
                    throw new Error(`the filter icon and the pin button overlap or are not drawn: ${JSON.stringify([a, b])}`);
                }
            },
        },
        { content: "Freeze the first column", trigger: th("name"), run() {
            this.$anchor[0].querySelector(".js_pin_this_column").click();
        } },
        { content: "The pinned column is sticky", trigger: `${th("name")}`, run() {
            if (getComputedStyle(this.$anchor[0]).position !== "sticky") {
                throw new Error("the header is not sticky");
            }
        } },
        { trigger: th("type"), run() {
            (this.anchor || this.$anchor[0]).querySelector(".o_dwo_hf_btn").click();
        } },
        { trigger: ".o_dwo_hf[data-kind=choice] .o_dwo_hf_row:contains('URL')", run: "click" },
        { trigger: ".o_dwo_hf .o_dwo_hf_apply", run: "click" },
        { trigger: `.o_searchview_facet:contains('Type: URL')`, run: () => {} },
        { content: "The pinned column is still frozen after the filter", trigger: `${th("name")}`, run() {
            if (getComputedStyle(this.$anchor[0]).position !== "sticky") {
                throw new Error("the frozen column was lost");
            }
        } },
        { content: "Unpin, to leave the browser storage clean", trigger: th("name"), run() {
            this.$anchor[0].querySelector(".js_pin_this_column").click();
        } },
    ],
});
