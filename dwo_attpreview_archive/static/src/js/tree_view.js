/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onMounted, onPatched, onWillUnmount, onWillUpdateProps, useRef, useState } from "@odoo/owl";

// Headless Tree (tree state, keyboard, ARIA) + TanStack Virtual (only the visible rows are in the page), both MIT,
// shipped in static/lib/tree_libs (global DwoTreeLibs). The rows are drawn here, with OWL.
const ROW_HEIGHT = 30;

/**
 * A generic, virtualized tree with columns. The data stays outside OWL's reactivity (it can hold 100 000 rows):
 * the parent gives functions, and a single counter triggers a render when the tree or the scroll position changes.
 *
 * props.getChildren(id) -> ids (already sorted), props.isFolder(id), props.row(id) -> {name, icon, size, date, muted,
 * title}, props.onOpen(id) (Enter / click on a file), props.rootId, props.version (bump it after changing what
 * getChildren returns, e.g. a filter), props.expanded (ids expanded at start), props.label (ARIA label).
 */
export class DwoTreeView extends Component {
    static template = "dwo_attpreview_archive.TreeView";
    static props = {
        rootId: String,
        getChildren: Function,
        isFolder: Function,
        row: Function,
        onOpen: Function,
        version: { type: Number, optional: true },
        expanded: { type: Array, optional: true },
        label: { type: String, optional: true },
        onReady: { type: Function, optional: true },
        onDownload: { type: Function, optional: true },
        folderIcon: { type: Function, optional: true },
        slots: { type: Object, optional: true },
    };

    setup() {
        const L = window.DwoTreeLibs;
        this.ticks = useState({ n: 0 });
        this.scrollRef = useRef("scroll");
        this.listRef = useRef("list");
        this.version = this.props.version || 0;
        const rerender = () => this.ticks.n++;
        this.tree = L.createTree({
            rootItemId: this.props.rootId,
            getItemName: (item) => this.props.row(item.getId()).name,
            isItemFolder: (item) => this.props.isFolder(item.getId()),
            dataLoader: {
                getItem: (id) => id,
                getChildren: (id) => this.props.getChildren(id),
            },
            initialState: { expandedItems: this.props.expanded || [] },
            features: [L.syncDataLoaderFeature, L.selectionFeature, L.hotkeysCoreFeature, L.expandAllFeature],
            setState: rerender,
            onPrimaryAction: (item) => {
                if (!item.isFolder()) {
                    this.props.onOpen(item.getId());
                }
            },
            // keyboard focus may move to a row that is not in the page yet: scroll the virtual list to it first
            scrollToItem: (item) => this.virtualizer.scrollToIndex(item.getItemMeta().index, { align: "auto" }),
        });
        this.virtualOptions = {
            count: 0,
            getScrollElement: () => this.scrollRef.el,
            estimateSize: () => ROW_HEIGHT,
            overscan: 12,
            observeElementRect: L.observeElementRect,
            observeElementOffset: L.observeElementOffset,
            scrollToFn: L.elementScroll,
            onChange: rerender,
        };
        this.virtualizer = new L.Virtualizer(this.virtualOptions);
        this.props.onReady?.(this);
        onMounted(() => {
            this.cleanupVirtualizer = this.virtualizer._didMount();
            this.tree.registerElement(this.listRef.el);
            this.tree.setMounted(true);
            this.tree.rebuildTree();
            this.virtualizer._willUpdate();
            this.registerRows();
        });
        // what getChildren returns changed (filter): rebuild BEFORE rendering, never while rendering (a rebuild
        // notifies a change, which would start another render)
        onWillUpdateProps((next) => {
            if ((next.version || 0) !== this.version) {
                this.version = next.version || 0;
                this.tree.rebuildTree();
            }
        });
        onPatched(() => {
            this.virtualizer._willUpdate();
            this.registerRows();
        });
        onWillUnmount(() => {
            this.tree.setMounted(false);
            this.tree.registerElement(null);
            this.cleanupVirtualizer?.();
        });
    }

    /** Rows drawn now: tree items (flat, in display order) cut to the visible window of the virtual list. */
    get rows() {
        this.ticks.n; // re-read on every render
        const items = this.tree.getItems();
        this.items = items;
        this.virtualizer.setOptions({ ...this.virtualOptions, count: items.length });
        return this.virtualizer.getVirtualItems().map((v) => {
            const item = items[v.index];
            const id = item.getId();
            const meta = item.getItemMeta();
            return {
                key: id,
                id,
                top: v.start,
                level: meta.level,
                folder: item.isFolder(),
                expanded: item.isFolder() && item.isExpanded(),
                ariaExpanded: item.isFolder() ? (item.isExpanded() ? "true" : "false") : undefined,
                focused: item.isFocused(),
                setsize: meta.setSize,
                posinset: meta.posInSet + 1,
                info: this.props.row(id),
            };
        });
    }

    get totalHeight() {
        return this.virtualizer.getTotalSize();
    }

    /** Headless Tree focuses rows through their element: tell it which element each drawn row is. */
    registerRows() {
        for (const el of this.listRef.el?.querySelectorAll("[data-tree-id]") || []) {
            this.tree.getItemInstance(el.dataset.treeId).registerElement(el);
        }
    }

    onRowClick(ev, id) {
        this.tree.getItemInstance(id).getProps().onClick(ev);
    }

    expandAll() {
        this.tree.expandAll();
    }

    collapseAll() {
        this.tree.collapseAll();
    }

    expandItems(ids) {
        // tree.setState() only notifies: state changes go through applySubStateUpdate (as the library does itself)
        this.tree.applySubStateUpdate("expandedItems", (current) => [...new Set([...current, ...ids])]);
        this.tree.rebuildTree();
    }
}
