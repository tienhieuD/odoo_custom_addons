/** @odoo-module **/
// Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
import { Component, onMounted, onPatched, onWillUnmount, onWillUpdateProps, proxy, signal, useProps } from "@odoo/owl";

// Headless Tree (tree state, keyboard, ARIA) + TanStack Virtual (only the visible rows are in the page), both MIT,
// shipped in static/lib/tree_libs (global DwoTreeLibs, loaded with the backend assets). The rows are drawn here, with
// OWL. Shared by the engines (archive: folder tree; text: JSON / XML / YAML tree, Markdown outline).
const ROW_HEIGHT = 30;

/**
 * A generic, virtualized tree with columns. The data stays outside OWL's reactivity (it can hold 100 000 rows):
 * the parent gives functions, and a single counter triggers a render when the tree or the scroll position changes.
 *
 * props.getChildren(id) -> ids (already sorted), props.isFolder(id), props.row(id) -> {name, icon, badge, count,
 * muted, title, nameClass, <column keys>}, props.onOpen(id) (Enter / click on a leaf), props.rootId, props.version
 * (bump it after changing what getChildren returns, e.g. a filter), props.expanded (ids expanded at start),
 * props.label (ARIA label), props.columns (extra columns after the name: [{key, label, width, align, classKey}];
 * default: none), props.nameLabel (header of the name column), props.onFocus(id) (called after a render when the
 * focused row changed), props.onDownload(id) (a download button on leaf rows), props.folderIcon(expanded).
 *
 * Rules (bugs found on #82): never call tree.rebuildTree() while rendering (onWillUpdateProps does it); change the
 * state through tree.applySubStateUpdate(...); keep the big data outside reactive state.
 */
export class DwoTreeView extends Component {
    static template = "dwo_attpreview_core.TreeView";
    // Odoo 20 (Owl 3): no static props; props come from useProps() (rootId, getChildren, isFolder, row, onOpen, version,
    // expanded, label, nameLabel, columns, onReady, onFocus, onDownload, folderIcon)
    props = useProps();

    setup() {
        const L = window.DwoTreeLibs;
        // Odoo 20 (Owl 3): proxy instead of useState, signal refs (read as this.scroll() / this.list())
        this.ticks = proxy({ n: 0 });
        this.scroll = signal.ref();
        this.list = signal.ref();
        this.version = this.props.version || 0;
        this.focusedId = null;
        const rerender = () => this.ticks.n++;
        this.tree = L.createTree({
            rootItemId: this.props.rootId,
            getItemName: (item) => String(this.props.row(item.getId()).name),
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
                    this.props.onOpen?.(item.getId());
                }
            },
            // keyboard focus may move to a row that is not in the page yet: scroll the virtual list to it first
            scrollToItem: (item) => this.virtualizer.scrollToIndex(item.getItemMeta().index, { align: "auto" }),
        });
        this.virtualOptions = {
            count: 0,
            getScrollElement: () => this.scroll(),
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
            this.tree.registerElement(this.list());
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
            this.notifyFocus();
        });
        onWillUnmount(() => {
            this.tree.setMounted(false);
            this.tree.registerElement(null);
            this.cleanupVirtualizer?.();
        });
    }

    /** Grid of a row: the name column takes the free space, then the extra columns, then the action column. */
    get gridStyle() {
        const widths = (this.props.columns || []).map((col) => col.width || "8rem");
        if (this.props.onDownload) {
            widths.push("2.25rem");
        }
        return `grid-template-columns: minmax(0, 1fr) ${widths.join(" ")};`;
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
            const folder = item.isFolder();
            const info = this.props.row(id);
            return {
                key: id,
                id,
                top: v.start,
                level: meta.level,
                folder,
                expanded: folder && item.isExpanded(),
                ariaExpanded: folder ? (item.isExpanded() ? "true" : "false") : undefined,
                focused: item.isFocused(),
                setsize: meta.setSize,
                posinset: meta.posInSet + 1,
                info,
                icon: folder && this.props.folderIcon ? this.props.folderIcon(item.isExpanded()) : info.icon,
            };
        });
    }

    get totalHeight() {
        return this.virtualizer.getTotalSize();
    }

    cellClass(row, col) {
        const cls = ["o_dwo_tree_cell", `o_dwo_tree_col_${col.key}`];
        if (col.align === "right") {
            cls.push("text-end");
        }
        if (col.classKey && row.info[col.classKey]) {
            cls.push(row.info[col.classKey]);
        }
        return cls.join(" ");
    }

    /** Headless Tree focuses rows through their element: tell it which element each drawn row is. */
    registerRows() {
        for (const el of this.list()?.querySelectorAll("[data-tree-id]") || []) {
            this.tree.getItemInstance(el.dataset.treeId).registerElement(el);
        }
    }

    notifyFocus() {
        if (!this.props.onFocus) {
            return;
        }
        const id = this.tree.getState().focusedItem ?? null;
        if (id !== this.focusedId) {
            this.focusedId = id;
            this.props.onFocus(id);
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
