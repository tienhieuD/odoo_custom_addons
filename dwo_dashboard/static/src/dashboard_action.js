/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onWillStart, useEffect, useExternalListener, useRef, useState } from "@odoo/owl";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { loadCSS, loadJS } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { ExplorePanel } from "./explore_panel";
import { ShareDialog } from "./share_dialog";
import { FilterBar } from "./filter_bar";
import { FilterEditor } from "./filter_editor";
import { COLS_DEFAULT, INTERVAL_LABELS, ROW_HEIGHT, drillChain, newWidgetId, nextPosition } from "./utils";
import { WidgetCard } from "./widget_card";
import "./renderers/index";

const GRIDSTACK_JS = "/dwo_dashboard/static/lib/gridstack/gridstack-all.js";
const GRIDSTACK_CSS = "/dwo_dashboard/static/lib/gridstack/gridstack.min.css";
let gridstackLoaded = null;

function loadGridstack() {
    // lazy: gridstack is only needed to edit, never on the pages of the other apps
    gridstackLoaded = gridstackLoaded || Promise.all([loadJS(GRIDSTACK_JS), loadCSS(GRIDSTACK_CSS)]);
    return gridstackLoaded;
}

const clone = (value) => JSON.parse(JSON.stringify(value));

/** "My dashboard": pages on the left, the grid of the current page, filters on top, Explore on the right. */
export class DashboardAction extends Component {
    static template = "dwo_dashboard.Dashboard";
    static components = { WidgetCard, FilterBar, FilterEditor, ExplorePanel };
    static props = { "*": true };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.action = useService("action");
        this.gridRef = useRef("grid");
        this.grid = null;
        this.tokens = {};
        this.saved = new Map(); // widget id -> JSON of the saved widget (decides run_widget or run_preview)
        this.state = useState({
            ready: false, pages: [], shared: [], level: "owner", owner: "", pageId: null, name: "", revision: 0,
            spec: { schema: "dwo-dashboard/1", widgets: [] }, savedSpec: "", editing: false, snapshot: null,
            data: {}, filterValues: {}, explore: null, renaming: null, saving: false, pageMenu: null, filterEditor: false,
            select: null, drills: {}, pick: null, // what was clicked (cross-filter, drill-down); never saved
        });
        useExternalListener(window, "click", () => {
            this.state.pageMenu = null;
            this.state.pick = null;
        });
        onWillStart(() => this.boot());
        useEffect(
            () => {
                if (!this.state.editing) {
                    return;
                }
                let cancelled = false;
                loadGridstack().then(() => {
                    if (!cancelled) {
                        this.initGrid();
                    }
                });
                return () => {
                    cancelled = true;
                    this.destroyGrid();
                };
            },
            () => [this.state.editing, this.state.pageId, this.state.spec.widgets.map((w) => w.id).join(",")]
        );
    }

    // ------------------------------------------------------------------------------------------------- boot
    async boot() {
        const dashboard = await this.orm.call("dwo.dashboard", "get_my_dashboard", []);
        this.dashboardId = dashboard.id;
        this.state.pages = dashboard.pages;
        this.state.shared = dashboard.shared || [];
        await this.openPage(dashboard.pages[0].id, true);
        this.state.ready = true;
    }

    /** Owner or editor: the rest read only. */
    get canEdit() {
        return this.state.level !== "view";
    }

    get isOwner() {
        return this.state.level === "owner";
    }

    async refreshLists() {
        const dashboard = await this.orm.call("dwo.dashboard", "get_my_dashboard", []);
        this.state.pages = dashboard.pages;
        this.state.shared = dashboard.shared || [];
        return dashboard;
    }

    openShare() {
        this.dialog.add(ShareDialog, { pageId: this.state.pageId, pageName: this.state.name });
    }

    get cols() {
        return (this.state.spec.grid && this.state.spec.grid.cols) || COLS_DEFAULT;
    }

    get widgets() {
        return this.state.spec.widgets;
    }

    get filters() {
        return this.state.spec.filters || [];
    }

    get dirty() {
        return JSON.stringify(this.state.spec) !== this.state.savedSpec;
    }

    get rowHeight() {
        return ROW_HEIGHT;
    }

    // ------------------------------------------------------------------------------------------------ pages
    async openPage(id, force = false) {
        if (!force && id === this.state.pageId) {
            return;
        }
        if (!force && this.dirty) {
            return this.confirmDiscard(() => this.openPage(id, true));
        }
        const page = await this.orm.call("dwo.dashboard.page", "get_page", [id]);
        const s = this.state;
        s.pageId = id;
        s.name = page.name;
        s.revision = page.revision;
        s.level = page.level;
        s.owner = page.owner;
        s.spec = page.spec;
        s.savedSpec = JSON.stringify(page.spec);
        s.editing = false;
        s.explore = null;
        s.data = {};
        s.filterValues = {};
        s.select = null;
        s.drills = {};
        s.pick = null;
        this.markSaved();
        this.runAll();
    }

    markSaved() {
        this.saved = new Map(this.state.spec.widgets.map((w) => [w.id, JSON.stringify(w)]));
    }

    confirmDiscard(proceed) {
        this.dialog.add(ConfirmationDialog, {
            title: _t("Unsaved changes"),
            body: _t("This page has changes that are not saved. Discard them?"),
            confirmLabel: _t("Discard"),
            confirm: proceed,
            cancel: () => {},
        });
    }

    async addPage() {
        const created = await this.orm.create("dwo.dashboard.page", [
            { name: _t("New page"), dashboard_id: this.dashboardId },
        ]);
        const dashboard = await this.orm.call("dwo.dashboard", "get_my_dashboard", []);
        this.state.pages = dashboard.pages;
        await this.openPage(created[0]);
        this.state.renaming = { id: created[0], name: _t("New page") };
    }

    startRename(page) {
        this.state.renaming = { id: page.id, name: page.name };
    }

    async finishRename() {
        const r = this.state.renaming;
        this.state.renaming = null;
        if (!r || !r.name.trim()) {
            return;
        }
        await this.orm.write("dwo.dashboard.page", [r.id], { name: r.name.trim() });
        this.state.pages.find((p) => p.id === r.id).name = r.name.trim();
        if (r.id === this.state.pageId) {
            this.state.name = r.name.trim();
        }
    }

    async duplicatePage(page) {
        const copy = await this.orm.call("dwo.dashboard.page", "duplicate_page", [[page.id]]);
        await this.refreshLists();
        await this.openPage(copy.id);
    }

    deletePage(page) {
        this.dialog.add(ConfirmationDialog, {
            title: _t("Delete page"),
            body: _t("Delete the page “%s” and its widgets?", page.name),
            confirmLabel: _t("Delete"),
            confirm: async () => {
                await this.orm.unlink("dwo.dashboard.page", [page.id]);
                const dashboard = await this.orm.call("dwo.dashboard", "get_my_dashboard", []);
                this.state.pages = dashboard.pages;
                if (page.id === this.state.pageId) {
                    await this.openPage(dashboard.pages[0].id, true);
                }
            },
            cancel: () => {},
        });
    }

    async movePage(page, delta) {
        const ids = this.state.pages.map((p) => p.id);
        const from = ids.indexOf(page.id);
        const to = from + delta;
        if (to < 0 || to >= ids.length) {
            return;
        }
        ids.splice(to, 0, ids.splice(from, 1)[0]);
        await this.orm.call("dwo.dashboard.page", "reorder", [ids]);
        this.state.pages = ids.map((id) => this.state.pages.find((p) => p.id === id));
    }

    // --------------------------------------------------------------------------------------------- widgets
    /** What the server needs to know about the clicks: the keys it gave us, nothing else. */
    interactions() {
        const drills = {};
        for (const [id, steps] of Object.entries(this.state.drills)) {
            if (steps.length) {
                drills[id] = steps.map((step) => step.key);
            }
        }
        const sel = this.state.select;
        return sel || Object.keys(drills).length
            ? { select: sel ? { widget: sel.widget, key: sel.key } : undefined, drills }
            : undefined;
    }

    get interactive() {
        return !this.state.editing;
    }

    /** A bar, a slice or a pivot row was clicked: ask what to do with it. */
    onPick(widget, pick) {
        const steps = this.state.drills[widget.id] || [];
        const chain = drillChain(widget);
        const next = chain[steps.length + 1];
        this.state.pick = {
            widget, key: pick.key, label: pick.label, x: pick.x, y: pick.y,
            selected: !!this.state.select && this.state.select.widget === widget.id && this.state.select.key === pick.key,
            drillTo: next ? INTERVAL_LABELS[next] : null,
        };
    }

    pickFilter() {
        const { widget, key, label, selected } = this.state.pick;
        this.state.select = selected ? null : { widget: widget.id, key, label, title: widget.title || "" };
        this.state.pick = null;
        this.runAll();
    }

    pickDrill() {
        const { widget, key, label } = this.state.pick;
        this.state.drills[widget.id] = [...(this.state.drills[widget.id] || []), { key, label }];
        this.state.select = null; // the key of a selection is of the level it was made on
        this.state.pick = null;
        this.runAll();
    }

    drillUp(widget) {
        this.state.drills[widget.id] = (this.state.drills[widget.id] || []).slice(0, -1);
        this.state.select = null;
        this.runAll();
    }

    clearSelect() {
        this.state.select = null;
        this.runAll();
    }

    drillLabels(widget) {
        return (this.state.drills[widget.id] || []).map((step) => step.label);
    }

    async pickRecords() {
        const { widget, key } = this.state.pick;
        this.state.pick = null;
        const answer = await this.orm.call("dwo.dashboard.engine", "drill_records", [
            this.state.pageId, widget.id, key, this.serverValues(), this.interactions(),
        ]);
        if (!answer.ok) {
            this.notification.add(answer.error.message, { type: "warning" });
            return;
        }
        const { model, ids, total } = answer.result;
        if (total > ids.length) {
            this.notification.add(_t("Showing the first %s of %s records.", ids.length, total), { type: "info" });
        }
        this.action.doAction({
            type: "ir.actions.act_window", name: widget.title || _t("Records"), res_model: model,
            domain: [["id", "in", ids]], views: [[false, "list"], [false, "form"]], target: "current",
        });
    }

    serverValues() {
        const out = {};
        for (const [id, value] of Object.entries(this.state.filterValues)) {
            out[id] = Array.isArray(value) ? value.map((v) => (v && typeof v === "object" ? v.id : v)) : value;
        }
        return out;
    }

    async runWidget(widget) {
        const id = widget.id;
        const token = (this.tokens[id] = (this.tokens[id] || 0) + 1);
        this.state.data[id] = { loading: true };
        const stored = this.saved.get(id) === JSON.stringify(widget) && !this.state.editing;
        let answer;
        try {
            answer = stored
                ? await this.orm.call("dwo.dashboard.engine", "run_widget", [this.state.pageId, id, this.serverValues(), this.interactions()])
                : await this.orm.call("dwo.dashboard.engine", "run_preview", [widget, this.filters, this.serverValues()]);
        } catch {
            answer = { ok: false, error: { code: "failed", message: _t("This widget could not be computed.") } };
        }
        if (token !== this.tokens[id] || !this.state.data[id]) {
            return;
        }
        this.state.data[id] = answer.ok ? { loading: false, result: answer.result } : { loading: false, error: answer.error };
    }

    runAll() {
        // one RPC per widget, in parallel: a failing widget does not hold back the others
        for (const widget of this.widgets) {
            this.runWidget(widget);
        }
    }

    addFilter(filter) {
        this.state.spec.filters = [...this.filters, filter];
        this.state.filterEditor = false;
        this.runAll();
    }

    removeFilter(filter) {
        this.state.spec.filters = this.filters.filter((f) => f.id !== filter.id);
        delete this.state.filterValues[filter.id];
        this.runAll();
    }

    onFilter(id, value) {
        this.state.filterValues[id] = value;
        this.runAll();
    }

    // ---------------------------------------------------------------------------------------------- explore
    openExplore(widget) {
        this.state.explore = { widget: widget ? clone(widget) : null };
    }

    /** "Add widget" works from the view mode too: it switches to editing by itself (one click instead of two). */
    addWidget() {
        if (!this.state.editing) {
            this.startEdit();
        }
        this.openExplore(null);
    }

    get pageDatasets() {
        return [...new Set(this.widgets.map((w) => w.dataset))];
    }

    togglePageMenu(page, ev) {
        ev.stopPropagation();
        this.state.pageMenu = this.state.pageMenu === page.id ? null : page.id;
    }

    closeExplore() {
        this.state.explore = null;
    }

    applyExplore(widget) {
        const widgets = this.state.spec.widgets;
        const index = widget.id ? widgets.findIndex((w) => w.id === widget.id) : -1;
        if (index >= 0) {
            const old = widgets[index];
            widgets[index] = { ...widget, x: old.x, y: old.y, w: old.w, h: old.h };
        } else {
            widget.id = newWidgetId(widgets);
            const size = widget.type === "kpi" ? [3, 3] : widget.type === "table" ? [12, 4] : [6, 4];
            Object.assign(widget, nextPosition(widgets, ...size));
            widgets.push(widget);
        }
        this.state.explore = null;
        this.runWidget(widget.id ? this.widgets.find((w) => w.id === widget.id) : widget);
    }

    removeWidget(widget) {
        this.state.spec.widgets = this.widgets.filter((w) => w.id !== widget.id);
        delete this.state.data[widget.id];
    }

    // -------------------------------------------------------------------------------------------- edit mode
    startEdit() {
        if (!this.canEdit) {
            return;
        }
        this.state.select = null; // editing works on the widgets as they are saved
        this.state.drills = {};
        this.state.pick = null;
        this.state.snapshot = clone(this.state.spec);
        this.state.editing = true;
    }

    cancelEdit() {
        this.state.spec = this.state.snapshot;
        this.state.snapshot = null;
        this.state.editing = false;
        this.state.explore = null;
        this.state.data = {};
        this.runAll();
    }

    async done() {
        if (this.dirty && !(await this.save())) {
            return;
        }
        this.state.editing = false;
        this.state.snapshot = null;
        this.state.explore = null;
        this.runAll();
    }

    async save() {
        const s = this.state;
        s.saving = true;
        try {
            const answer = await this.orm.call("dwo.dashboard.page", "save_spec", [[s.pageId], s.spec, s.revision]);
            s.revision = answer.revision;
            s.savedSpec = JSON.stringify(s.spec);
            this.markSaved();
            this.notification.add(_t("Page saved."), { type: "success" });
            return true;
        } catch (error) {
            const message = (error && error.data && error.data.message) || _t("The page could not be saved.");
            this.notification.add(message, { type: "danger", sticky: true });
            return false;
        } finally {
            s.saving = false;
        }
    }

    // ---------------------------------------------------------------------------------------------- gridstack
    initGrid() {
        const el = this.gridRef.el;
        if (!el || !window.GridStack) {
            return;
        }
        this.destroyGrid();
        this.grid = window.GridStack.init(
            { column: this.cols, cellHeight: ROW_HEIGHT, margin: 4, float: false, animate: false,
              handle: ".dwo-card-header", disableOneColumnMode: true },
            el
        );
        this.grid.on("change", (ev, items) => {
            for (const node of items || []) {
                const widget = this.widgets.find((w) => w.id === node.id);
                if (widget) {
                    Object.assign(widget, { x: node.x, y: node.y, w: node.w, h: node.h });
                }
            }
        });
    }

    destroyGrid() {
        if (this.grid) {
            this.grid.destroy(false); // keep the DOM: Owl owns it
            this.grid = null;
        }
    }

    itemStyle(w) {
        return `grid-column: ${w.x + 1} / span ${w.w}; grid-row: ${w.y + 1} / span ${w.h}; --dwo-h: ${w.h};`;
    }

    /** Reading order (top to bottom, left to right): what a phone shows, one widget under the other. */
    get orderedWidgets() {
        return [...this.widgets].sort((a, b) => a.y - b.y || a.x - b.x);
    }
}

registry.category("actions").add("dwo_dashboard.main", DashboardAction);
