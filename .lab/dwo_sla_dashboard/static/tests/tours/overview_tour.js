/** @odoo-module **/

import { registry } from "@web/core/registry";

function rows(expected) {
    return {
        content: `list has ${expected} rows`,
        trigger: ".o_list_view .o_data_row",
        run() {
            const n = document.querySelectorAll(".o_list_view .o_data_row").length;
            if (n !== expected) {
                throw new Error(`expected ${expected} rows, got ${n}`);
            }
        },
    };
}

const back = [
    { trigger: ".o_breadcrumb .o_back_button, .breadcrumb-item:first-child a", run: "click" },
    { trigger: ".o_sla_overview .o_sla_kpis", run: () => {} },
];

registry.category("web_tour.tours").add("dwo_sla_overview", {
    steps: () => [
        { trigger: ".o_navbar_apps_menu button", run: "click" },
        { trigger: ".dropdown-item:contains('SLA')", run: "click" },
        // Overview is the first menu: it opens by default
        { content: "overview renders", trigger: ".o_sla_overview .o_sla_kpi_running", run: () => {} },
        {
            content: "kpi values",
            trigger: ".o_sla_kpi_breached .o_sla_kpi_value:contains('2')",
            run: () => {},
        },
        { trigger: ".o_sla_kpi_late .o_sla_kpi_value:contains('1')", run: () => {} },
        { trigger: ".o_sla_kpi_achieved_rate .o_sla_kpi_value:contains('66.7%')", run: () => {} },
        { content: "click breached", trigger: ".o_sla_kpi_breached", run: "click" },
        rows(2),
        ...back,
        { content: "click late", trigger: ".o_sla_kpi_late", run: "click" },
        rows(1),
        ...back,
        { content: "click donut slice on time", trigger: ".o_sla_slice[data-outcome='on_time']", run: "click" },
        rows(2),
        ...back,
        {
            content: "click stacked bar breached segment",
            trigger: ".o_sla_seg[data-outcome='breached_open']",
            run: "click",
        },
        rows(2),
        ...back,
        { content: "filter OLA", trigger: ".o_sla_type button:contains('OLA')", run: "click" },
        { trigger: ".o_sla_kpi_late .o_sla_kpi_value:contains('0')", run: () => {} },
        { content: "7 days", trigger: ".o_sla_period button[data-period='7']", run: "click" },
        { trigger: ".o_sla_kpi_breached .o_sla_kpi_value:contains('2')", run: () => {} },
        { content: "attention row", trigger: ".o_sla_att_row", run: "click" },
        { trigger: ".o_form_view", run: () => {} },
    ],
});

registry.category("web_tour.tours").add("dwo_sla_overview_empty", {
    steps: () => [
        { trigger: ".o_navbar_apps_menu button", run: "click" },
        { trigger: ".dropdown-item:contains('SLA')", run: "click" },
        { content: "friendly empty state", trigger: ".o_sla_overview .o_sla_ov_nodata:contains('No SLA data yet')", run: () => {} },
    ],
});
