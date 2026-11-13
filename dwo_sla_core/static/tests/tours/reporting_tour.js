odoo.define('dwo_sla_core.reporting_tour', function (require) {
"use strict";

var tour = require('web_tour.tour');

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

const VIEW = ".o_graph_renderer, .o_pivot, .o_list_view, .o_view_nocontent";

const steps = [
    { trigger: ".o_navbar_apps_menu .dropdown-toggle", run: "click" },
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
            trigger: `.dropdown-menu .dropdown-item:contains('${name}')`,
            run: "click",
        },
        { content: `${name} renders`, trigger: `.o_content ${VIEW}`, run: () => {} }
    );
}

tour.register("dwo_sla_reporting_menu", { test: true }, steps);

// Task 023 -- fixed colors by outcome and percentage axis, measured on the real Chart.js objects.
const rgb = (c) => {
    const el = document.createElement("span");
    el.style.color = c;
    document.body.appendChild(el);
    const out = getComputedStyle(el).color;
    el.remove();
    return out;
};
// Chart.js 2.9 (Odoo 16 and older) has no Chart.getChart: look the instance up by canvas
const chartOf = () => {
    const canvas = document.querySelector(".o_graph_renderer canvas");
    return Object.values(window.Chart.instances).find((c) => c.canvas === canvas);
};
const EXPECT = {
    "On Time": "#2e9e5b",
    Late: "#f08c00",
    "Breached (Open)": "#d63a3a",
    Running: "#5b7c99",
};
const ORDER = ["On Time", "Late", "Breached (Open)", "Running"];

function openScreen(name) {
    return [
        {
            trigger: ".o_menu_sections .dropdown-toggle:contains('Reporting')",
            run: "click",
        },
        { trigger: `.dropdown-menu .dropdown-item:contains('${name}')`, run: "click" },
        {
            content: `${name} is the current action`,
            trigger: `.o_control_panel .breadcrumb-item.active:contains('${name}')`,
            run: () => {},
        },
        { content: `${name} graph`, trigger: ".o_graph_renderer canvas", run: () => {} },
    ];
}

tour.register("dwo_sla_graph_colors", { test: true }, [
        { trigger: ".o_navbar_apps_menu .dropdown-toggle", run: "click" },
        { trigger: ".dropdown-item:contains('SLA')", run: "click" },
        ...openScreen("Status Mix"),
        {
            content: "pie slices use the fixed outcome colors",
            trigger: ".o_graph_renderer canvas",
            run() {
                const chart = chartOf();
                const colors = chart.data.datasets[0].backgroundColor;
                const seen = chart.data.labels.filter((l) => EXPECT[l]);
                if (seen.length < 3) {
                    throw new Error("expected On Time, Late and Running slices: " + chart.data.labels);
                }
                if (seen.join() !== ORDER.filter((l) => seen.includes(l)).join()) {
                    throw new Error("wrong slice order: " + chart.data.labels);
                }
                chart.data.labels.forEach((label, i) => {
                    if (EXPECT[label] && rgb(colors[i]) !== rgb(EXPECT[label])) {
                        throw new Error(`pie ${label}: ${colors[i]}`);
                    }
                });
            },
        },
        ...openScreen("Performance by Definition"),
        {
            content: "stacked bars: fixed colors, on time before late",
            trigger: ".o_graph_renderer canvas",
            run() {
                const labels = chartOf().data.datasets.map((d) => d.label);
                const ds = chartOf().data.datasets;
                ds.forEach((d) => {
                    if (EXPECT[d.label] && rgb(d.backgroundColor) !== rgb(EXPECT[d.label])) {
                        throw new Error(`bar ${d.label}: ${d.backgroundColor}`);
                    }
                });
                const order = ORDER.filter((l) => labels.includes(l));
                if (order.join() !== labels.filter((l) => order.includes(l)).join()) {
                    throw new Error("wrong stack order: " + labels);
                }
            },
        },
        ...openScreen("Compliance Trend"),
        {
            content: "the rate axis is a percentage",
            trigger: ".o_graph_renderer canvas",
            run() {
                const chart = chartOf();
                const y = chart.options.scales && chart.options.scales.yAxes && chart.options.scales.yAxes[0];
                if (!y) {
                    throw new Error("no y axis: " + chart.config.type + " " + chart.data.labels);
                }
                const text = y.ticks.callback(0.5);
                if (text !== "50%") {
                    throw new Error("axis label: " + text);
                }
                // task 029: lines are not stacked (no cumulated rates, axis up to 100%)
                if (y.stacked) {
                    throw new Error("trend lines are stacked");
                }
                if (chart.scales["y-axis-0"].max > 1.0001) {
                    throw new Error("rate axis above 100%: " + chart.scales["y-axis-0"].max);
                }
            },
        },
]);

});
