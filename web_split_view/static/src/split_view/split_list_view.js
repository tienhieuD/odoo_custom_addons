/** @odoo-module **/

import { useState } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";

/**
 * Highlights, in the list on the left of the split view, the row of the record displayed in the form
 * on the right. `env.splitState` only exists inside a split view, so other lists are not affected.
 *
 * Patching the renderer (instead of registering a js_class) also works for the lists that declare their
 * own `js_class`, whose renderer extends ListRenderer.
 */
patch(ListRenderer.prototype, "web_split_view.ListRenderer", {
    setup() {
        this._super(...arguments);
        // `splitState` is provided by the SplitPane (sub environment of the embedded views)
        this.splitState = this.env.splitState ? useState(this.env.splitState) : null;
    },

    getRowClass(record) {
        const classes = this._super(...arguments);
        if (!this.splitState || !record.resId || record.resId !== this.splitState.activeId) {
            return classes;
        }
        return Array.isArray(classes) ? [...classes, "split_active_row"] : `${classes} split_active_row`;
    },
});
