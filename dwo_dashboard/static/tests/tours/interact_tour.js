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
