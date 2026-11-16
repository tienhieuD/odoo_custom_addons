/** @odoo-module **/
// Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
// Odoo 17: the tour runner of 17 (jQuery) differs from the one of 18/19 (hoot). This file lets the tours keep the
// steps of 19 unchanged:
// - a step without `run` is clicked by 17 ("auto" action): it is marked `isCheck` (18/19 only check it);
// - while a dialog is open, 17 looks for the trigger inside that dialog only, so selectors that start with `.modal`
//   or that target a toast would never match: every step searches the whole page (`in_modal: false`), as 18/19 do;
// - `run()` gets `this.$anchor` (jQuery) on 17: it also gets `this.anchor` (the element), as on 18/19;
// - `test: true` so that 17 never starts the tour by itself (onboarding mode).
import { registry } from "@web/core/registry";

export function dwoTourSteps(steps) {
    return steps.map((step) => {
        const out = { in_modal: false, ...step };
        if (out.run === undefined) {
            out.isCheck = true;
        } else if (typeof out.run === "function") {
            const run = out.run;
            out.run = function (helper) {
                return run.call({ anchor: this.$anchor[0], $anchor: this.$anchor }, helper);
            };
        }
        return out;
    });
}

export function dwoAddTour(name, tour) {
    registry.category("web_tour.tours").add(name, {
        test: true,
        ...tour,
        steps: () => dwoTourSteps(tour.steps()),
    });
}
