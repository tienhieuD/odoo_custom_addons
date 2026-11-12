/** @odoo-module **/
import { registry } from "@web/core/registry";

// Refs: plan-improvement-sla-01-review 6.9 -- the SLA status chip appears next to the
// pager of a form whose model has an SLA, and opens the tasks of the record on click.
registry.category("web_tour.tours").add("dwo_sla_form_status_chip", {
    steps: () => [
        {
            content: "the chip is shown on the form of a partner that has an SLA task",
            trigger: ".o_form_view .o_sla_status_chip",
            run: () => {},
        },
        { trigger: ".o_sla_status_chip", run: "click" },
        {
            content: "clicking opens the SLA tasks list",
            trigger: ".o_list_view .o_data_row",
            run: () => {},
        },
    ],
});

// A form of a model without any SLA definition must not show the chip.
registry.category("web_tour.tours").add("dwo_sla_form_status_chip_absent", {
    steps: () => [
        { trigger: ".o_form_view .o_form_sheet", run: () => {} },
        {
            content: "no chip on a model that has no SLA",
            trigger: ".o_form_view:not(:has(.o_sla_status_chip))",
            run: () => {},
        },
    ],
});
