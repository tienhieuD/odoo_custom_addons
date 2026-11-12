odoo.define('dwo_sla_core.definition_form_tour', function (require) {
"use strict";

var tour = require('web_tour.tour');

// Refs: plan-improvement-sla-01-review 6.14 -- confirm before saving a condition change
// on a definition that has running tasks.
tour.register("dwo_sla_definition_confirm_save", { test: true }, [
        { trigger: ".o_form_view .oe_stat_button", run: () => {} },
        // Odoo 12 to 15: an existing record opens read-only
        { trigger: ".o_form_button_edit", run: "click" },
        { trigger: ".o_form_view .nav-link:contains('Cancel Condition')", run: "click" },
        // Odoo 17: with a dialog open the tour looks for the trigger INSIDE the .modal, so no `.modal` prefix.
        // Odoo 17/18: a selection field is a native <select> (the tour has no `select` action in 17)
        {
            trigger: "select.o_field_widget[name=cancel_mode], .o_field_widget[name=cancel_mode] select",
            run: () => {
                const select = document.querySelector("select.o_field_widget[name=cancel_mode], .o_field_widget[name=cancel_mode] select");
                select.value = select.querySelector("option[value='\"never\"']").value;
                select.dispatchEvent(new Event("change", { bubbles: true }));
            },
        },
        { trigger: ".o_form_button_save", run: "click" },
        {
            content: "the confirmation dialog mentions the running tasks",
            trigger: ".modal-body:contains('are running or paused')",
            run: () => {},
        },
        { trigger: ".modal-footer button:contains('Keep editing')", run: "click" },
        {
            content: "cancel keeps the unsaved change",
            trigger: ".o_form_button_save",
            run: () => {},
        },
        { trigger: ".o_form_button_save", run: "click" },
        { trigger: ".modal-footer button:contains('Save')", run: "click" },
        {
            content: "saved: the form is clean again",
            trigger: ".o_form_view.o_form_readonly",
            run: () => {},
        },
]);

});
