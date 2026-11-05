import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";

/**
 * Highlights, in the list on the left of the split view, the row of the record displayed in the form on
 * the right. `env.splitState` only exists inside a split view, so other lists are not affected.
 *
 * Patching the renderer (instead of registering a js_class) also works for the lists that declare their
 * own `js_class` (sales, accounting...), whose renderer extends ListRenderer.
 */
patch(ListRenderer.prototype, {
    getRowClass(record) {
        const classes = super.getRowClass(record);
        // reactive state provided by the SplitPane (sub environment of the embedded views)
        const splitState = this.env.splitState;
        if (!splitState || !record.resId || record.resId !== splitState.activeId) {
            return classes;
        }
        return `${classes} split_active_row`;
    },
});
