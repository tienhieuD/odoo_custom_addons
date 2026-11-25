/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";

// A click on a pivot row filters the KPI next to it, a second click on the chip clears it; "Show records" opens the list.
registry.category("web_tour.tours").add("dwo_interact", {
    steps: () => [
        { trigger: ".dwo-card[data-widget-id=total] .dwo-kpi-value:contains(6)" },
        { trigger: ".dwo-card[data-widget-id=matrix] th.dwo-pick:contains(Belgium)", run: "click" },
        { trigger: ".dwo-pick-filter", run: "click" },
        { trigger: ".dwo-selection:contains(Belgium)" },
        { trigger: ".dwo-card[data-widget-id=total] .dwo-kpi-value:contains(3)" },
        { trigger: ".dwo-selection-clear", run: "click" },
        { trigger: ".dwo-card[data-widget-id=total] .dwo-kpi-value:contains(6)" },
        { trigger: ".dwo-card[data-widget-id=matrix] th.dwo-pick:contains(Belgium)", run: "click" },
        { trigger: ".dwo-pick-records", run: "click" },
        { trigger: ".o_list_view .o_data_row:contains(Itour BE0)" },
    ],
});

// A page is as wide as its widgets: a widget dropped far to the right stays in its column, and slides up (no gaps).
registry.category("web_tour.tours").add("dwo_wide", {
    steps: () => [
        { trigger: ".dwo-card[data-widget-id=total]" },
        { trigger: ".dwo-edit", run: "click" },
        { trigger: ".grid-stack-item[gs-id=total]" },
        {
            trigger: ".grid-stack",
            run: () => {
                const grid = document.querySelector(".grid-stack");
                grid.gridstack.update(grid.querySelector(".grid-stack-item[gs-id=total]"), { x: 21, y: 8 }); // the last column of 24
            },
        },
        // twelve spare columns follow the widget: 21 + 3 + 12
        { trigger: ".grid-stack[style*='--dwo-cols: 36']" },
        {
            // growing the grid must not collapse the widgets (they had a width of 0 once)
            trigger: ".grid-stack-item[gs-id=total]",
            run: () => {
                const width = document.querySelector(".grid-stack-item[gs-id=total]").getBoundingClientRect().width;
                if (width < 100) {
                    throw new Error("the widget collapsed after the grid grew: width " + width);
                }
            },
        },
        {
            trigger: ".grid-stack",
            run: () => {
                const grid = document.querySelector(".grid-stack");
                grid.gridstack.update(grid.querySelector(".grid-stack-item[gs-id=total]"), { x: 30 });
            },
        },
        { trigger: ".dwo-done", run: "click" },
        { trigger: ".dwo-grid-item[style*='grid-column: 31'][style*='grid-row: 1 /'] [data-widget-id=total]" },
        {
            trigger: ".dwo-canvas",
            run: () => {
                const canvas = document.querySelector(".dwo-canvas");
                if (canvas.scrollWidth <= canvas.clientWidth) {
                    throw new Error("the page does not scroll sideways");
                }
            },
        },
    ],
});

// Ask the assistant: the proposal is loaded as a draft; Discard throws it away, Save keeps it.
registry.category("web_tour.tours").add("dwo_ai", {
    steps: () => [
        { trigger: ".dwo-card[data-widget-id=total]" },
        { trigger: ".dwo-edit", run: "click" },
        { trigger: ".dwo-ai", run: "click" },
        { trigger: ".dwo-ai-generate:disabled" },
        { trigger: ".dwo-ai-request", run: "edit add a count of contacts" },
        { trigger: ".dwo-ai-generate:not(:disabled)", run: "click" },
        { trigger: ".dwo-ai-proposal:contains(Added)" },
        { trigger: ".dwo-ai-apply", run: "click" },
        { trigger: ".dwo-grid-edit .dwo-card[data-widget-id=w9]" },
        { trigger: ".dwo-done", run: "click" },
        { trigger: ".dwo-grid .dwo-card[data-widget-id=w9]" },
    ],
});

// A metric of the dataset in the value of a new widget: the spec keeps {"metric": name}.
registry.category("web_tour.tours").add("dwo_metric_pick", {
    steps: () => [
        { trigger: ".dwo-main" },
        { trigger: ".dwo-edit", run: "click" },
        { trigger: ".dwo-add-widget", run: "click" },
        { trigger: ".dwo-dataset-input", run: "edit Contact" },
        { trigger: ".dwo-dataset-option:contains(res.partner)", run: "click" },
        { trigger: ".dwo-visual-kpi", run: "click" },
        { trigger: ".dwo-well-item select:has(option[value='metric:companies'])" },
        { trigger: ".dwo-well-item select", run: "select metric:companies" },
        { trigger: ".dwo-explore-preview .dwo-kpi-value" },
        { trigger: ".dwo-explore-apply:not(:disabled)", run: "click" },
        { trigger: ".dwo-grid-edit .dwo-card[data-widget-id=w1] .dwo-kpi-value" },
        { trigger: ".dwo-done", run: "click" },
        { trigger: ".dwo-grid .dwo-card[data-widget-id=w1] .dwo-kpi-value" },
    ],
});
