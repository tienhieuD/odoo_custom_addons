/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";

// Open the dashboard, add a KPI and a bar chart through Explore, save. A second tour (after a reload) checks they are there.
registry.category("web_tour.tours").add("dwo_dashboard_tour", {
    steps: () => [
        { trigger: ".dwo-dashboard .dwo-page-item.active .dwo-page-name:contains(Home)" },
        { trigger: ".dwo-empty" },
        // "Add widget" lives in the edit mode only
        { trigger: ".dwo-dashboard:not(:has(.dwo-add-widget))" },
        { trigger: ".dwo-edit", run: "click" },
        { trigger: ".dwo-add-widget", run: "click" },
        { trigger: ".dwo-dataset-input", run: "edit Contact" },
        { trigger: ".dwo-dataset-option:contains(res.partner)", run: "click" },
        { trigger: ".dwo-visual-kpi", run: "click" },
        { trigger: ".dwo-explore-preview .dwo-kpi-value" },
        // the change since the previous period (this month by default, as there is no date filter on the page yet)
        { trigger: ".dwo-compare-toggle", run: "click" },
        { trigger: ".dwo-explore-preview .dwo-kpi-delta" },
        // and a small trend line under the number
        { trigger: ".dwo-trend-toggle", run: "click" },
        { trigger: ".dwo-explore-preview .dwo-kpi-trend svg" },
        // the icon in front of the title: the default of the type until one is chosen
        { trigger: ".dwo-icon-button .fa-hashtag" },
        { trigger: ".dwo-icon-button", run: "click" },
        { trigger: ".dwo-icon-choice[title=fa-money]", run: "click" },
        { trigger: ".dwo-icon-button .fa-money" },
        { trigger: ".dwo-explore-apply:not(:disabled)", run: "click" },
        { trigger: ".dwo-grid-edit .dwo-card[data-widget-id=w1] .dwo-card-icon.fa-money" },
        { trigger: ".dwo-grid-edit .dwo-card[data-widget-id=w1] .dwo-kpi-delta" },
        // a bar chart: the axis selector is already there, "Count" is already chosen
        { trigger: ".dwo-add-widget", run: "click" },
        { trigger: ".dwo-dataset-input", run: "edit Contact" },
        { trigger: ".dwo-dataset-option:contains(res.partner)", run: "click" },
        { trigger: ".dwo-visual-bar", run: "click" },
        { trigger: ".dwo-well[data-well=axis] .dwo-well-item select", run: "select country_id" },
        { trigger: ".dwo-explore-preview canvas" },
        { trigger: ".dwo-explore-apply:not(:disabled)", run: "click" },
        { trigger: ".dwo-grid-edit .dwo-card[data-widget-id=w2] canvas" },
        { trigger: ".dwo-grid-edit .dwo-card[data-widget-id=w2] .dwo-card-icon.fa-bar-chart" },
        // a page filter, bound by itself to both widgets
        { trigger: ".dwo-add-filter", run: "click" },
        { trigger: ".dwo-filter-add:not(:disabled)", run: "click" },
        { trigger: ".dwo-filter .dwo-filter-remove" },
        // a second filter, "some records" on the country: its model must match what the field points to
        { trigger: ".dwo-add-filter", run: "click" },
        { trigger: ".dwo-filter-kind-relation", run: "click" },
        { trigger: ".dwo-filter-field", run: "select relation|country_id|res.country" },
        { trigger: ".dwo-filter-add:not(:disabled)", run: "click" },
        { trigger: ".dwo-filter[data-filter-id=country_id]" },
        { trigger: ".dwo-done", run: "click" },
        { trigger: ".dwo-grid .dwo-card[data-widget-id=w1] .dwo-kpi-value" },
        // the date filter is on "All time": nothing to compare, and the card says what to do
        { trigger: ".dwo-grid .dwo-card[data-widget-id=w1] .dwo-kpi-hint" },
        { trigger: ".dwo-grid .dwo-card[data-widget-id=w2] canvas" },
        { trigger: ".dwo-filter select" },
    ],
});

registry.category("web_tour.tours").add("dwo_dashboard_tour_reload", {
    steps: () => [
        { trigger: ".dwo-grid .dwo-card[data-widget-id=w1] .dwo-kpi-value" },
        { trigger: ".dwo-grid .dwo-card[data-widget-id=w2] canvas" },
        // resize a widget through the gridstack instance, then Done: the width is saved
        { trigger: ".dwo-edit", run: "click" },
        { trigger: ".grid-stack-item[gs-id=w1]" },
        {
            trigger: ".grid-stack",
            run: () => {
                const grid = document.querySelector(".grid-stack");
                grid.gridstack.update(grid.querySelector(".grid-stack-item[gs-id=w1]"), { w: 8 });
            },
        },
        { trigger: ".dwo-done", run: "click" },
        { trigger: ".dwo-grid .dwo-grid-item[style*='span 8'] [data-widget-id=w1]" },
        // a second page, with the "+" of the page list
        // Cancel creates nothing
        { trigger: ".dwo-page-add", run: "click" },
        { trigger: ".dwo-page-name-input", run: "edit Ghost" },
        { trigger: ".dwo-page-name-cancel", run: "click" },
        { trigger: ".dwo-pages:not(:has(.dwo-page-name:contains(Ghost)))" },
        // an empty name cannot be confirmed; OK creates the page and opens it
        { trigger: ".dwo-page-add", run: "click" },
        { trigger: ".dwo-page-name-ok:disabled" },
        { trigger: ".dwo-page-name-input", run: "edit Sales" },
        { trigger: ".dwo-page-name-ok:not(:disabled)", run: "click" },
        { trigger: ".dwo-page-item .dwo-page-name:contains(Sales)" },
        { trigger: ".dwo-empty" },
    ],
});

registry.category("web_tour.tours").add("dwo_dashboard_tour_persist", {
    steps: () => [
        { trigger: ".dwo-grid .dwo-grid-item[style*='span 8'] [data-widget-id=w1]" },
        // Edit then Done with no change must not save anything (gridstack must not re-pack the layout by itself)
        { trigger: ".dwo-edit", run: "click" },
        { trigger: ".grid-stack-item[gs-id=w2]" },
        { trigger: ".dwo-done", run: "click" },
        { trigger: ".dwo-grid .dwo-card[data-widget-id=w2] canvas" },
    ],
});
