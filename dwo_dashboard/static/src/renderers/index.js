/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";
import { ChartRenderer } from "./chart";
import { KpiRenderer } from "./kpi";
import { PivotRenderer } from "./pivot";
import { TableRenderer } from "./table";

// One entry per visual type. A plugin adds its own: registry.category("dwo_dashboard.visuals").add("scatter", Component)
// (the component takes ``widget`` and ``result``). A type without a renderer shows a placeholder in its widget.
const visuals = registry.category("dwo_dashboard.visuals");
visuals.add("kpi", KpiRenderer);
visuals.add("table", TableRenderer);
for (const type of ["bar", "line", "area", "pie", "doughnut"]) {
    visuals.add(type, ChartRenderer);
}
visuals.add("pivot", PivotRenderer);
