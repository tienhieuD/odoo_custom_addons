import { registry } from "@web/core/registry";

// Task 006 C2 -- open the SLA app, then each screen of the Reporting menu.
const SCREENS = [
    "Compliance Trend",
    "Response Time Distribution",
    "Status Mix",
    "Open Backlog & Ageing",
    "Performance by Definition and Source",
    "Performance by Source",
    "Pause Analysis",
    "Escalation Activity",
    "Source Heatmap",
    "Calendar Impact",
];

const VIEW = ".o_graph_renderer, .o_pivot, .o_list_renderer, .o_view_nocontent";

const steps = [
    { trigger: ".o_navbar_apps_menu button", run: "click" },
    { trigger: ".dropdown-item:contains('SLA')", run: "click" },
];
for (const name of SCREENS) {
    steps.push(
        {
            content: `open the Reporting menu (${name})`,
            trigger: ".o_menu_sections .dropdown-toggle:contains('Reporting')",
            run: "click",
        },
        {
            content: `open ${name}`,
            trigger: `.o-dropdown--menu .dropdown-item:contains('${name}')`,
            run: "click",
        },
        { content: `${name} renders`, trigger: `.o_content ${VIEW}` }
    );
}

registry.category("web_tour.tours").add("dwo_sla_reporting_menu", { steps: () => steps });
