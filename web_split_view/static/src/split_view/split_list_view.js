import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";

/**
 * List renderer used by the left side of the split view (js_class="split_list"):
 * highlights the row of the record currently displayed in the form on the right.
 */
export class SplitListRenderer extends ListRenderer {
    get splitState() {
        // reactive state provided by the SplitController
        return this.env.splitState || { activeId: false };
    }

    getRowClass(record) {
        const classes = super.getRowClass(record);
        return record.resId && record.resId === this.splitState.activeId
            ? `${classes} split_active_row`
            : classes;
    }
}

registry.category("views").add("split_list", {
    ...listView,
    Renderer: SplitListRenderer,
});
