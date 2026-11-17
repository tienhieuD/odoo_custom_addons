/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, useState } from "@odoo/owl";
import { Domain } from "@web/core/domain";
import { useBus, useService } from "@web/core/utils/hooks";
import { usePopover } from "@web/core/popover/popover_hook";
import { _t } from "@web/core/l10n/translation";
import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { DwoHeaderFilterPopover } from "./filter_popover";
import { buildFilter, filterKind } from "./filter_logic";

// columns that show something else than the value of their field: no filter icon
const NO_FILTER_WIDGETS = ["handle", "list_activity", "kanban_activity", "activity_exception", "badge_ribbon"];

/**
 * The filter icon of a list column header. A filter is a search item of the search bar (a facet) marked with
 * ``dwoHf = {field, kind, state}``: the icon is lit while such an item is in the query, so removing the facet (or
 * "clear all") in the search bar puts the icon out, and the icon's own Reset removes the facet.
 */
export class DwoHeaderFilter extends Component {
    static template = "dwo_listview_header_filter.Button";
    static props = { column: Object, list: Object };

    setup() {
        this.searchModel = this.env.searchModel;
        this.popover = usePopover(DwoHeaderFilterPopover, { position: "bottom-end", popoverClass: "o_dwo_hf_popover" });
        useBus(this.searchModel, "update", () => this.render());
    }

    get field() {
        return this.props.list.fields[this.props.column.name];
    }

    get kind() {
        return filterKind(this.field);
    }

    /** The query items of this column's filter. */
    get activeItems() {
        const { query, searchItems } = this.searchModel;
        const name = this.props.column.name;
        return query.map((q) => searchItems[q.searchItemId]).filter((item) => item && item.dwoHf && item.dwoHf.field === name);
    }

    get active() {
        return this.activeItems.length > 0;
    }

    get title() {
        const item = this.activeItems[0];
        return item ? item.description : _t("Filter this column");
    }

    onClick(ev) {
        ev.stopPropagation();
        if (this.popover.isOpen) {
            this.popover.close();
            return;
        }
        const item = this.activeItems[0];
        this.popover.open(ev.currentTarget, {
            field: { ...this.field, name: this.props.column.name },
            kind: this.kind,
            initial: item ? item.dwoHf.state : null,
            onApply: (state) => this.apply(state),
            onReset: () => this.reset(),
        });
    }

    swallow(ev) {
        ev.stopPropagation();
    }

    /** Replace the filter of this column by the one of ``state``; ``false`` when the state selects nothing. */
    apply(state) {
        const field = { ...this.field, name: this.props.column.name };
        const built = buildFilter(this.kind, field, state);
        if (!built) {
            return false;
        }
        const model = this.searchModel;
        model.blockNotification = true;
        try {
            for (const item of this.activeItems) {
                model.deactivateGroup(item.groupId);
            }
            model.createNewFilters([{
                description: built.description,
                tooltip: built.description,
                domain: new Domain(built.domain).toString(),
                invisible: "True",
                dwoHf: { field: field.name, kind: this.kind, state: JSON.parse(JSON.stringify(state)) },
            }]);
        } finally {
            model.blockNotification = false;
        }
        model._notify();
        return true;
    }

    reset() {
        const model = this.searchModel;
        model.blockNotification = true;
        try {
            for (const item of this.activeItems) {
                model.deactivateGroup(item.groupId);
            }
        } finally {
            model.blockNotification = false;
        }
        model._notify();
    }
}

patch(ListRenderer, {
    components: { ...ListRenderer.components, DwoHeaderFilter },
});

patch(ListRenderer.prototype, {
    /** The icon is shown on the lists that have a search bar (not on a list inside a form) and on fields that can be filtered. */
    dwoHfEnabled(column) {
        const searchModel = this.env.searchModel;
        const list = this.props.list;
        if (!searchModel || searchModel.resModel !== list.resModel || column.type !== "field" || !column.hasLabel) {
            return false;
        }
        if (NO_FILTER_WIDGETS.includes(column.widget)) {
            return false;
        }
        return Boolean(filterKind(list.fields[column.name]));
    },
});
