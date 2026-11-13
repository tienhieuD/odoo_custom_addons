odoo.define('dwo_sla_core.reporting_tour', function (require) {
"use strict";

var tour = require('web_tour.tour');

// Task 006 C2 -- open the SLA app, then each screen of the Reporting menu.
// Odoo 12: no template literals (the bundle minifier removes the spaces inside them) and no color tour
// (the graph of Odoo 12 is nvd3/d3, the fixed colors and the percentage axis are not ported).
var SCREENS = [
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

var VIEW = ".o_graph_svg_container, .nvd3, .o_pivot, .o_list_view, .o_view_nocontent";

var steps = [
    { trigger: ".o_menu_apps a.full", run: "click" },
    { trigger: ".dropdown-item:contains('SLA')", run: "click" },
];
SCREENS.forEach(function (name) {
    steps.push(
        {
            content: "open the Reporting menu (" + name + ")",
            trigger: ".o_menu_sections .dropdown-toggle:contains('Reporting')",
            run: "click",
        },
        {
            content: "open " + name,
            trigger: ".dropdown-menu .dropdown-item:contains('" + name + "')",
            run: "click",
        },
        // wait for the breadcrumb of THIS screen: the previous view is still in the DOM while the action loads
        {
            content: name + " is the current action",
            trigger: ".o_control_panel .breadcrumb li.active:contains('" + name + "')",
            run: function () {},
        },
        { content: name + " renders", trigger: ".o_content " + VIEW, run: function () {} }
    );
});

tour.register("dwo_sla_reporting_menu", { test: true }, steps);

});
