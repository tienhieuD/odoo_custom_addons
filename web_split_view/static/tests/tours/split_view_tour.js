/** @odoo-module **/

import tour from "web_tour.tour";

tour.register("web_split_view_tour", {
    url: "/web#action=web_split_view.action_customer_split_demo",
    test: true,
}, [
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
            content: "the form of the new record is displayed (empty name)",
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
    ]);

// Automatic mode: no <split> view record, the split view is derived from the action
tour.register("web_split_view_auto_tour", {
    url: "/web#action=base.action_partner_form&view_type=split",
    test: true,
}, [
        {
            content: "the automatic split view shows the partner list on the left",
            trigger: ".o_split_view .left-side .o_list_view .o_data_row",
        },
        {
            content: "open a record",
            trigger: ".o_split_view .left-side .o_data_row:first-child .o_data_cell",
            run: "click",
        },
        {
            content: "the partner form is displayed on the right",
            trigger: ".o_split_view .right-side .o_form_view",
        },
        {
            content: "the row of the record is highlighted",
            trigger: ".o_split_view .left-side .o_data_row.split_active_row",
        },
    ]);

// State kept per split view: pane width (browser) and the record shown on the right (tab session)
tour.register("web_split_view_state_tour", {
    url: "/web#action=base.action_partner_form&view_type=split",
    test: true,
}, [
        { trigger: ".o_split_view .left-side .o_data_row", run: () => {} },
        {
            content: "resize the panes with the divider",
            trigger: ".o_split_view .split_resizer",
            run: () => {
                const split = document.querySelector(".o_split_view .duo_split_view");
                const rect = split.getBoundingClientRect();
                const resizer = document.querySelector(".o_split_view .split_resizer");
                resizer.dispatchEvent(new MouseEvent("mousedown", { bubbles: true, clientX: rect.left + rect.width * 0.5 }));
                document.dispatchEvent(new MouseEvent("mousemove", { bubbles: true, clientX: rect.left + rect.width * 0.3 }));
                document.dispatchEvent(new MouseEvent("mouseup", { bubbles: true }));
            },
        },
        {
            content: "open the third record",
            trigger: ".o_split_view .left-side .o_data_row:nth-child(3) .o_data_cell",
            run: "click",
        },
        { trigger: ".o_split_view .right-side .o_form_view .o_field_widget", run: () => {} },
        {
            content: "the record shown on the right is kept for the tab session, the pane width in the browser",
            trigger: ".o_split_view .left-side .o_data_row.split_active_row",
            run: () => {
                const keys = (storage) => Object.keys(storage).filter((key) => key.startsWith("web_split_view_"));
                if (!keys(window.sessionStorage).some((key) => key.includes("_record_"))) {
                    throw new Error("the open record is not stored");
                }
                const widthKey = keys(window.localStorage).find((key) => key.includes("_width_"));
                const width = parseFloat(window.localStorage.getItem(widthKey));
                if (!(width > 25 && width < 35)) {
                    throw new Error("pane width not stored: " + width);
                }
            },
        },
    ]);

// The expand button opens the record in the full form view; the breadcrumb comes back to the split view
tour.register("web_split_view_expand_tour", {
    url: "/web#action=base.action_partner_form&view_type=split",
    test: true,
}, [
        { trigger: ".o_split_view .left-side .o_data_row", run: () => {} },
        {
            content: "open the second record",
            trigger: ".o_split_view .left-side .o_data_row:nth-child(2) .o_data_cell",
            run: "click",
        },
        {
            content: "expand it to the full form view",
            trigger: ".o_split_view .right-side .o_split_expand",
            run: "click",
        },
        {
            content: "the full form view is displayed (no split view anymore)",
            trigger: ".o_form_view:not(:has(.o_split_view)) .o_field_widget[name=name]",
        },
        {
            content: "go back with the breadcrumb: the split view shows the same record",
            trigger: ".o_control_panel .breadcrumb-item a",
            run: "click",
        },
        {
            trigger: ".o_split_view .left-side .o_data_row:nth-child(2).split_active_row",
        },
    ]);

// Going to the full form view and back restores the split view as it was: search facet and open record
tour.register("web_split_view_back_tour", {
    url: "/web#action=base.action_partner_form&view_type=split",
    test: true,
}, [
        { trigger: ".o_split_view .left-side .o_data_row", run: () => {} },
        {
            content: "search for Azure in the list of the split view",
            trigger: ".o_split_view .left-side .o_searchview_input",
            run: "text Azure",
        },
        {
            content: "wait for the suggestions, then validate the first one",
            trigger: ".o_searchview_autocomplete:contains('Azure')",
            run: () => {},
        },
        {
            trigger: ".o_split_view .left-side .o_searchview_input",
            run: () => {
                const input = document.querySelector(".o_split_view .left-side .o_searchview_input");
                input.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
            },
        },
        {
            trigger: ".o_split_view .left-side .o_facet_value:contains('Azure')",
            run: () => {},
        },
        {
            content: "wait for the filtered list",
            trigger: ".o_split_view .left-side .o_data_row:first-child .o_data_cell:contains('Azure')",
            run: () => {},
        },
        {
            content: "open the first record found",
            trigger: ".o_split_view .left-side .o_data_row:first-child .o_data_cell",
            run: "click",
        },
        {
            content: "expand to the full form",
            trigger: ".o_split_view .right-side .o_split_expand",
            run: "click",
        },
        {
            trigger: ".o_form_view:not(:has(.o_split_view)) .o_field_widget[name=name]",
            run: () => {},
        },
        {
            content: "back to the split view",
            trigger: ".o_control_panel .breadcrumb-item a",
            run: "click",
        },
        {
            content: "the search facet is still there",
            trigger: ".o_split_view .left-side .o_facet_value:contains('Azure')",
            run: () => {},
        },
        {
            content: "and the record is still highlighted",
            trigger: ".o_split_view .left-side .o_data_row.split_active_row",
            run: () => {},
        },
    ]);
