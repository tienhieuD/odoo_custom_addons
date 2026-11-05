odoo.define('web_split_view.tours', function (require) {
"use strict";
var tour = require('web_tour.tour');

const noop = () => {};

// Automatic mode: no <split> view record, the split view is derived from the action
tour.register("web_split_view_auto_tour", { url: "/web#action=base.action_partner_form&view_type=split", test: true }, [
    {
        content: "the automatic split view shows the partner list on the left",
        trigger: ".duo_split_view .left-side .o_list_view .o_data_row",
        run: noop,
    },
    {
        content: "open a record",
        trigger: ".duo_split_view .left-side .o_data_row:first-child .o_data_cell:nth-child(2)",
        run: "click",
    },
    {
        content: "the partner form is displayed on the right",
        trigger: ".duo_split_view .right-side .o_form_view .o_field_widget",
        run: noop,
    },
    {
        content: "the row of the record is highlighted",
        trigger: ".duo_split_view .left-side .o_data_row.split_active_row",
        run: noop,
    },
]);

// The expand button opens the record in the full form view; the breadcrumb comes back to the split view
tour.register("web_split_view_expand_tour", { url: "/web#action=base.action_partner_form&view_type=split", test: true }, [
    { trigger: ".duo_split_view .left-side .o_data_row", run: noop },
    {
        content: "open the second record",
        trigger: ".duo_split_view .left-side .o_data_row:nth-child(2) .o_data_cell:nth-child(2)",
        run: "click",
    },
    {
        content: "expand it to the full form view",
        trigger: ".duo_split_view .right-side .o_split_expand:not(.d-none)",
        run: "click",
    },
    {
        content: "the full form view is displayed (no split view anymore)",
        trigger: ".o_form_view:not(:has(.duo_split_view)) .o_field_widget[name=name]",
        run: noop,
    },
    {
        content: "go back with the breadcrumb: the split view shows the same record",
        trigger: ".o_control_panel .breadcrumb-item a",
        run: "click",
    },
    {
        trigger: ".duo_split_view .left-side .o_data_row:nth-child(2).split_active_row",
        run: noop,
    },
]);

// State kept per split view: pane width (browser) and the record shown on the right (tab session)
tour.register("web_split_view_state_tour", { url: "/web#action=base.action_partner_form&view_type=split", test: true }, [
    { trigger: ".duo_split_view .left-side .o_data_row", run: noop },
    {
        content: "resize the panes with the divider",
        trigger: ".duo_split_view .split_resizer",
        run: () => {
            const split = document.querySelector(".duo_split_view");
            const rect = split.getBoundingClientRect();
            const resizer = document.querySelector(".duo_split_view .split_resizer");
            resizer.dispatchEvent(new MouseEvent("mousedown", { bubbles: true, clientX: rect.left + rect.width * 0.5 }));
            split.dispatchEvent(new MouseEvent("mousemove", { bubbles: true, clientX: rect.left + rect.width * 0.3 }));
            split.dispatchEvent(new MouseEvent("mouseup", { bubbles: true }));
        },
    },
    {
        content: "open the third record",
        trigger: ".duo_split_view .left-side .o_data_row:nth-child(3) .o_data_cell:nth-child(2)",
        run: "click",
    },
    {
        content: "the record shown on the right is kept for the tab session, the pane width in the browser",
        trigger: ".duo_split_view .left-side .o_data_row.split_active_row",
        run: () => {
            const keys = (storage) => Object.keys(storage).filter((key) => key.startsWith("web_split_view_"));
            if (!keys(window.sessionStorage).some((key) => key.includes("_record_"))) {
                throw new Error("the open record is not stored");
            }
            const widthKey = keys(window.localStorage).find((key) => key.includes("_width_"));
            const width = JSON.parse(window.localStorage.getItem(widthKey))[0];
            if (!(width > 25 && width < 35)) {
                throw new Error("pane width not stored: " + width);
            }
        },
    },
]);


// A filter of the search bar of the action filters the list on the left; the facet and the open record survive
// the full form view
tour.register("web_split_view_search_tour", { url: "/web#action=base.action_partner_form&view_type=split", test: true }, [
    {
        trigger: ".duo_split_view .left-side .o_data_row",
        run: function () {
            window.__splitRowsBefore = document.querySelectorAll(".duo_split_view .left-side .o_data_row").length;
        },
    },
    {
        content: "open the Filters menu of the action",
        trigger: ".o_control_panel .o_filters_menu_button, .o_control_panel button:contains('Filters')",
        run: "click",
    },
    {
        content: "choose a filter",
        trigger: ".o_control_panel .o_menu_item a:contains('Companies')",
        run: "click",
    },
    {
        content: "the list on the left is filtered (fewer than 30 of the 36 partners)",
        trigger: ".duo_split_view .left-side .o_list_view:not(:has(.o_data_row:nth-child(30))) .o_data_row",
        run: noop,
    },
    {
        content: "open the first record found",
        trigger: ".duo_split_view .left-side .o_data_row:first-child .o_data_cell:nth-child(2)",
        run: "click",
    },
    {
        trigger: ".duo_split_view .right-side .o_split_expand:not(.d-none)",
        run: "click",
    },
    {
        trigger: ".o_form_view:not(:has(.duo_split_view)) .o_field_widget[name=name]",
        run: noop,
    },
    {
        content: "back to the split view",
        trigger: ".o_control_panel .breadcrumb-item a",
        run: "click",
    },
    {
        content: "the search facet and the record are still there",
        trigger: ".o_searchview_facet:contains('Companies')",
        run: noop,
    },
    {
        trigger: ".duo_split_view .left-side .o_data_row.split_active_row",
        run: noop,
    },
]);

});
