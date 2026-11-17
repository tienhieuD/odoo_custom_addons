/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";

const th = (name) => `.o_list_renderer th[data-name='${name}']`;
const btn = (name) => `${th(name)} .o_dwo_hf_btn`;
// the icon shows when the pointer is on the header (not reproduced here): click it from the header cell
const press = (name, content) => ({
    ...(content ? { content } : {}),
    trigger: th(name),
    run() {
        (this.anchor || this.$anchor[0]).querySelector(".o_dwo_hf_btn").click();
    },
});
const facet = (text) => `.o_searchview_facet:contains('${text}')`;

function rowCount(expected) {
    return {
        content: `${expected} row(s) in the list`,
        trigger: ".o_list_renderer .o_data_row",
        run() {
            const n = document.querySelectorAll(".o_list_renderer .o_data_row").length;
            if (n !== expected) {
                throw new Error(`expected ${expected} rows, found ${n}`);
            }
        },
    };
}

// Checkboxes (selection), a quick date, operators (text), and the two-way link with the search bar
registry.category("web_tour.tours").add("dwo_listview_header_filter_tour", {
    steps: () => [
        {
            content: "The list view (the attachments open in kanban when Discuss is installed)",
            trigger: ".o_action_manager .o_control_panel",
            run() {
                document.querySelector(".o_switch_view.o_list:not(.active)")?.click();
            },
        },
        { content: "A filter icon in the header of a text, a selection and a date column", trigger: `${th("name")}:has(.o_dwo_hf_btn)`, run: () => {} },
        press("type"),
        { content: "Checkboxes of the selection field", trigger: ".o_dwo_hf[data-kind=choice] .o_dwo_hf_row:contains('URL')", run: "click" },
        { content: "The ticked value moves to the area on top", trigger: ".o_dwo_hf .o_dwo_hf_selected .o_dwo_hf_picked:contains('URL')", run: () => {} },
        { trigger: ".o_dwo_hf .o_dwo_hf_apply", run: "click" },
        { content: "The condition is a facet of the search bar", trigger: facet("Type: URL"), run: () => {} },
        { content: "The icon is lit", trigger: `${btn("type")}.o_dwo_hf_active`, run: () => {} },
        { content: "Only the URL attachment is left", trigger: ".o_list_renderer .o_data_row:contains('dwo-hf-link')", run: () => {} },
        { trigger: ".o_list_renderer:not(:has(.o_data_row:contains('dwo-hf-a.txt')))", run: () => {} },
        { content: "Removing the facet in the search bar puts the icon out", trigger: `${facet("Type: URL")} .o_facet_remove`, run: "click" },
        { trigger: `${th("type")}:not(:has(.o_dwo_hf_active))`, run: () => {} },
        // many2one: the records of the related model, with a search box
        press("create_uid"),
        { content: "Many2one values are loaded from the related model", trigger: ".o_dwo_hf[data-kind=choice] .o_dwo_hf_row[data-value]:not([data-value=__not_set])", run: () => {} },
        { trigger: ".o_dwo_hf .o_dwo_hf_search", run: "edit a" },
        { content: "The search box narrows the values", trigger: ".o_dwo_hf .o_dwo_hf_row[data-value]:not([data-value=__not_set])", run: "click" },
        { trigger: ".o_dwo_hf .o_dwo_hf_selected .o_dwo_hf_picked", run: () => {} },
        { trigger: ".o_dwo_hf .o_dwo_hf_apply", run: "click" },
        { trigger: facet("Created by:"), run: () => {} },
        press("create_uid", "Reset from the icon"),
        { trigger: ".o_dwo_hf .o_dwo_hf_reset", run: "click" },
        { trigger: `${th("create_uid")}:not(:has(.o_dwo_hf_active))`, run: () => {} },
        // text: operators of the Odoo filters
        press("name"),
        { content: "Operators of a text field", trigger: ".o_dwo_hf[data-kind=text] select.o_dwo_hf_op", run() { if (!this.anchor.querySelector("option[value='not ilike']")) { throw new Error("no 'does not contain' operator"); } } },
        { trigger: ".o_dwo_hf .o_dwo_hf_value", run: "edit dwo-hf-a" },
        { trigger: ".o_dwo_hf .o_dwo_hf_value", run: "press Enter" },
        { trigger: facet("Name: contains dwo-hf-a"), run: () => {} },
        rowCount(1),
        // the filter of the icon can be changed: it reopens with its values
        press("name"),
        { content: "Reopened with the value of the filter", trigger: ".o_dwo_hf .o_dwo_hf_value", run() { if (this.anchor.value !== "dwo-hf-a") { throw new Error("value not restored: " + this.anchor.value); } } },
        { trigger: ".o_dwo_hf .o_dwo_hf_reset", run: "click" },
        { content: "Reset removes the facet", trigger: ".o_searchview:not(:has(.o_searchview_facet:contains('dwo-hf-a')))", run: () => {} },
        // date: a quick range
        press("create_date"),
        { content: "Quick dates, with the fiscal year", trigger: ".o_dwo_hf[data-kind=date] .o_dwo_hf_preset[data-preset=this_fiscal_year]", run: () => {} },
        { trigger: ".o_dwo_hf .o_dwo_hf_preset[data-preset=today]", run: "click" },
        { trigger: facet("Created on: Today"), run: () => {} },
        { trigger: `${btn("create_date")}.o_dwo_hf_active`, run: () => {} },
        { content: "Clear the whole search bar: every icon goes out", trigger: ".o_searchview .o_searchview_facet .o_facet_remove", run: "click" },
        { trigger: `${th("create_date")}:not(:has(.o_dwo_hf_active))`, run: () => {} },
    ],
});
