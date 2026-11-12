import { registry } from "@web/core/registry";

// Refs: plan-improvement-sla-01-review 6.14 -- confirm before saving a condition change
// on a definition that has running tasks.
registry.category("web_tour.tours").add("dwo_sla_definition_confirm_save", {
    steps: () => [
        { trigger: ".o_form_view .oe_stat_button" },
        { trigger: ".o_form_view .nav-link:contains('Cancel Condition')", run: "click" },
        // Odoo 18: a selection field is a native <select> (19 has the select menu)
        { trigger: ".o_field_widget[name=cancel_mode] select", run: "select \"never\"" },
        { trigger: ".o_form_button_save", run: "click" },
        {
            content: "the confirmation dialog mentions the running tasks",
            trigger: ".modal .modal-body:contains('1 task(s)')",
        },
        { trigger: ".modal button:contains('Keep editing')", run: "click" },
        {
            content: "cancel keeps the unsaved change",
            trigger: ".o_form_view .o_form_status_indicator_buttons:not(.invisible)",
        },
        { trigger: ".o_form_button_save", run: "click" },
        { trigger: ".modal .modal-footer button:contains('Save')", run: "click" },
        {
            content: "saved: the form is clean again",
            trigger: ".o_form_view:not(:has(.o_form_status_indicator_buttons:not(.invisible)))",
        },
    ],
});
