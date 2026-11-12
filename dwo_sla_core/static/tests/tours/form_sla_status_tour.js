odoo.define('dwo_sla_core.form_sla_status_tour', function (require) {
"use strict";

var tour = require('web_tour.tour');

// Refs: plan-improvement-sla-01-review 6.9 -- the SLA status chip appears next to the
// pager of a form whose model has an SLA, and opens the tasks of the record on click.
tour.register("dwo_sla_form_status_chip", { test: true }, [
        {
            content: "the chip is shown on the form of a partner that has an SLA task",
            trigger: ".o_sla_status_chip",
            run: () => {},
        },
        { trigger: ".o_sla_status_chip", run: "click" },
        {
            content: "clicking opens the SLA tasks list",
            trigger: ".o_list_view .o_data_row",
            run: () => {},
        },
]);

// A form of a model without any SLA definition must not show the chip.
tour.register("dwo_sla_form_status_chip_absent", { test: true }, [
        { trigger: ".o_form_view", run: () => {} },
        {
            content: "no chip on a model that has no SLA",
            trigger: ".o_form_view:not(:has(.o_sla_status_chip))",
            run: () => {},
        },
]);

});
