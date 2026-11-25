/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";

// Open the dashboard, add a KPI and a bar chart through Explore, save. A second tour (after a reload) checks they are there.
registry.category("web_tour.tours").add("dwo_dashboard_tour", {
    steps: () => [
        { trigger: ".dwo-dashboard .dwo-page-item.active .dwo-page-name:contains(Home)" },
        { trigger: ".dwo-empty" },
        { trigger: ".dwo-edit", run: "click" },
        { trigger: ".dwo-add-widget", run: "click" },
        { trigger: ".dwo-dataset-select", run: "selectByLabel Contact" },
        { trigger: ".dwo-visual-kpi", run: "click" },
        { trigger: ".dwo-well[data-well=value] .dwo-add-item", run: "click" },
        { trigger: ".dwo-explore-preview .dwo-kpi-value" },
        { trigger: ".dwo-explore-apply:not(:disabled)", run: "click" },
        { trigger: ".dwo-grid-edit .dwo-card[data-widget-id=w1] .dwo-kpi-value" },
        { trigger: ".dwo-add-widget", run: "click" },
        { trigger: ".dwo-dataset-select", run: "selectByLabel Contact" },
        { trigger: ".dwo-visual-bar", run: "click" },
        { trigger: ".dwo-well[data-well=axis] .dwo-add-item", run: "click" },
        { trigger: ".dwo-well[data-well=axis] .dwo-well-item select", run: "selectByLabel Country" },
        { trigger: ".dwo-well[data-well=values] .dwo-add-item", run: "click" },
        { trigger: ".dwo-explore-preview canvas" },
        { trigger: ".dwo-explore-apply:not(:disabled)", run: "click" },
        { trigger: ".dwo-grid-edit .dwo-card[data-widget-id=w2] canvas" },
        { trigger: ".dwo-done", run: "click" },
        { trigger: ".dwo-grid .dwo-card[data-widget-id=w1] .dwo-kpi-value" },
        { trigger: ".dwo-grid .dwo-card[data-widget-id=w2] canvas" },
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
        { trigger: ".dwo-page-add", run: "click" },
        { trigger: ".dwo-page-rename", run: "edit Sales" },
        { trigger: ".dwo-title", run: "click" },
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
