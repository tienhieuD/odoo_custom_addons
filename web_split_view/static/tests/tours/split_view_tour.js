/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("web_split_view_tour", {
    url: "/web#action=web_split_view.action_customer_split_demo",
    steps: () => [
        {
            content: "the split view shows the list on the left",
            trigger: ".o_split_view .left-side .o_list_view .o_data_row",
        },
        {
            content: "the placeholder is displayed until a record is selected",
            trigger: ".o_split_view .right-side .form-placeholder",
        },
        {
            content: "click the first record of the list",
            trigger: ".o_split_view .left-side .o_data_row:first-child .o_data_cell[name=name]",
            run: "click",
        },
        {
            content: "the form of the record is displayed on the right and the row is highlighted",
            trigger: ".o_split_view .right-side .o_form_view .o_field_widget[name=name] input",
        },
        {
            content: "the row of the selected record is highlighted",
            trigger: ".o_split_view .left-side .o_data_row.split_active_row",
        },
        {
            content: "edit the name",
            trigger: ".o_split_view .right-side .o_field_widget[name=name] input",
            run: "text Split View Renamed",
        },
        {
            content: "save the record",
            trigger: ".o_split_view .right-side .o_form_button_save",
            run: "click",
        },
        {
            content: "the list shows the new name",
            trigger: ".o_split_view .left-side .o_data_cell[name=name]:contains('Split View Renamed')",
        },
        {
            content: "click the New button of the split view",
            trigger: ".o_split_view .o_split_button_create",
            run: "click",
        },
        {
            content: "the form of the new record is displayed (no row highlighted anymore)",
            trigger: ".o_split_view .left-side .o_list_view:not(:has(.split_active_row))",
        },
        {
            content: "fill the name of the new record",
            trigger: ".o_split_view .right-side .o_field_widget[name=name] input",
            run: "text Split View Created",
        },
        {
            content: "save the new record",
            trigger: ".o_split_view .right-side .o_form_button_save",
            run: "click",
        },
        {
            content: "the new record appears in the list",
            trigger: ".o_split_view .left-side .o_data_cell[name=name]:contains('Split View Created')",
        },
    ],
});
