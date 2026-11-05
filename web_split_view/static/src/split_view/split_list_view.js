/** @odoo-module **/

import { useState } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";

/**
 * Highlights, in the list on the left of the split view, the row of the record displayed in the form
 * on the right. `env.splitState` only exists inside a split view, so other lists are not affected.
 */
patch(ListRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        this.splitState = this.env.splitState ? useState(this.env.splitState) : null;
    },

    getRowClass(record) {
        const classes = super.getRowClass(record);
        if (!this.splitState || !record.resId || record.resId !== this.splitState.activeId) {
            return classes;
        }
        return `${classes} split_active_row`;
    },
});
