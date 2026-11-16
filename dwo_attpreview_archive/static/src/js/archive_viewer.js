/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { download } from "@web/core/network/download";
import { _t } from "@web/core/l10n/translation";
import { dwoAttPreviewIconUrl, dwoAttPreviewSpecialIconUrl } from "@dwo_attpreview_core/js/file_kind";
import { DwoTreeView } from "./tree_view";

const { DateTime } = luxon;
const F_ENCRYPTED = 1;
const F_SPECIAL = 2;
const MAX_EXPAND_ALL = 3000; // folders: "Expand all" is offered up to this many
const MAX_MATCH_EXPAND = 5000;

export function dwoArchiveSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
    return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} GB`;
}

/**
 * Viewer of the "archive" engine: the content of a zip / tar / rar / 7z file as a folder tree (virtualized, fine with
 * 100 000 entries). Enter or a click on a file opens it in its own preview dialog with the engines installed (service
 * dwo_attpreview.openPart); each row has a Download button. Folders first, names in natural order (file2 < file10).
 */
export class ArchiveViewer extends Component {
    static template = "dwo_attpreview_archive.ArchiveViewer";
    static components = { DwoTreeView };
    static props = {
        content: String,
        attachmentId: { type: Number, optional: true },
        downloadUrl: { type: String, optional: true },
        fileUrl: { type: String, optional: true },
        source: { type: Object, optional: true },
    };

    setup() {
        this.preview = useService("dwo_attpreview");
        this.treeRef = useRef("tree");
        this.ui = useState({ filter: "", version: 0, matchCount: 0 });
        this.matches = null; // ids shown while filtering (plain Set, not reactive)
        // plain fields, outside OWL reactivity: they can be large
        try {
            this.data = JSON.parse(this.props.content || "{}") || {};
        } catch {
            this.data = {};
        }
        this.build();
    }

    // --- model ----------------------------------------------------------------------------------------------------
    build() {
        const dirs = this.data.dirs || [""];
        const files = this.data.files || [];
        const collator = new Intl.Collator(undefined, { numeric: true, sensitivity: "base" });
        this.names = dirs.map((path) => path.slice(path.lastIndexOf("/") + 1));
        // dirs are created parents first, so a map is enough to find the parent quickly
        const indexOf = new Map(dirs.map((path, i) => [path, i]));
        this.parentOf = dirs.map((path) => {
            const cut = path.lastIndexOf("/");
            return path ? (cut < 0 ? 0 : indexOf.get(path.slice(0, cut)) ?? 0) : -1;
        });
        const subDirs = dirs.map(() => []);
        const subFiles = dirs.map(() => []);
        this.dirSize = dirs.map(() => 0);
        this.dirCount = dirs.map(() => 0);
        for (let d = 1; d < dirs.length; d++) {
            subDirs[this.parentOf[d]].push(d);
        }
        files.forEach((row, i) => {
            subFiles[row[0]].push(i);
            for (let d = row[0]; d >= 0; d = this.parentOf[d]) {
                this.dirSize[d] += row[2];
                this.dirCount[d]++;
            }
        });
        const byName = (names) => (a, b) => collator.compare(names(a), names(b));
        this.children = dirs.map((_, d) => [
            ...subDirs[d].sort(byName((i) => this.names[i])).map((i) => `d${i}`),
            ...subFiles[d].sort(byName((i) => files[i][1])).map((i) => `f${i}`),
        ]);
        this.files = files;
        this.dirs = dirs;
    }

    getChildren(id) {
        const all = this.children[Number(id.slice(1))] || [];
        const visible = this.matches;
        return visible ? all.filter((child) => visible.has(child)) : all;
    }

    isFolder(id) {
        return id[0] === "d";
    }

    row(id) {
        const i = Number(id.slice(1));
        if (id[0] === "d") {
            return {
                name: this.names[i] || this.data.format || "/",
                size: dwoArchiveSize(this.dirSize[i]),
                date: "",
                count: this.dirCount[i],
                folder: true,
            };
        }
        const [, name, size, mtime, flags] = this.files[i];
        return {
            name,
            size: dwoArchiveSize(size),
            date: mtime ? DateTime.fromSeconds(mtime).toLocaleString(DateTime.DATETIME_SHORT) : "",
            icon: flags & F_ENCRYPTED ? dwoAttPreviewSpecialIconUrl("lock") : flags & F_SPECIAL
                ? dwoAttPreviewSpecialIconUrl("link") : dwoAttPreviewIconUrl(name, ""),
            muted: Boolean(flags & (F_ENCRYPTED | F_SPECIAL)),
            title: flags & F_ENCRYPTED ? _t("Protected by a password") : flags & F_SPECIAL ? _t("Link (no content)") : name,
        };
    }

    folderIcon(expanded) {
        return dwoAttPreviewSpecialIconUrl(expanded ? "folder_open" : "folder");
    }

    // --- header ---------------------------------------------------------------------------------------------------
    get summary() {
        const d = this.data;
        return {
            format: (d.format || "").toUpperCase(),
            files: (d.files || []).length,
            folders: Math.max((d.dirs || [""]).length - 1, 0),
            size: dwoArchiveSize(d.size || 0),
            packed: dwoArchiveSize(d.packed || 0),
        };
    }

    get canExpandAll() {
        return (this.dirs.length - 1) <= MAX_EXPAND_ALL;
    }

    get initialExpanded() {
        // a single top folder (most archives): open it
        const top = this.children[0] || [];
        return top.length === 1 && top[0][0] === "d" ? ["d0", top[0]] : ["d0"];
    }

    // --- filter by name -------------------------------------------------------------------------------------------
    onFilterInput(ev) {
        clearTimeout(this.filterTimer);
        const value = ev.target.value;
        this.filterTimer = setTimeout(() => this.applyFilter(value), 200);
    }

    applyFilter(value) {
        const text = value.trim().toLowerCase();
        this.ui.filter = value;
        if (!text) {
            this.matches = null;
            this.ui.version++;
            return;
        }
        const visible = new Set(["d0"]);
        const toExpand = new Set();
        const addParents = (d) => {
            for (; d > 0 && !visible.has(`d${d}`); d = this.parentOf[d]) {
                visible.add(`d${d}`);
                if (toExpand.size < MAX_MATCH_EXPAND) {
                    toExpand.add(`d${d}`);
                }
            }
        };
        this.files.forEach((row, i) => {
            if (row[1].toLowerCase().includes(text)) {
                visible.add(`f${i}`);
                addParents(row[0]);
            }
        });
        this.names.forEach((name, d) => {
            if (d && name.toLowerCase().includes(text)) {
                addParents(d);
            }
        });
        this.matches = visible;
        this.ui.matchCount = [...visible].filter((id) => id[0] === "f").length;
        this.ui.version++;
        this.tree?.expandItems([...toExpand]);
    }

    /** The tree view gives its small API (expand / collapse) when it is created. */
    onTreeReady(tree) {
        this.tree = tree;
    }

    clearFilter() {
        const input = this.treeRef.el?.querySelector(".o_dwo_arc_filter");
        if (input) {
            input.value = "";
        }
        this.applyFilter("");
    }

    expandAll() {
        this.tree?.expandAll();
    }

    collapseAll() {
        this.tree?.collapseAll();
    }

    // --- files ----------------------------------------------------------------------------------------------------
    get baseSource() {
        const { path, ...base } = this.props.source || {};
        return base;
    }

    childPath(index) {
        const path = this.props.source && this.props.source.path;
        return path ? `${path}/${index}` : `${index}`;
    }

    onOpen(id) {
        if (this.props.source && id[0] === "f") {
            this.preview.openPart(this.baseSource, this.childPath(Number(id.slice(1))));
        }
    }

    onDownload(id) {
        if (this.props.source && id[0] === "f") {
            download({ data: {}, url: this.preview.partUrl(this.baseSource, this.childPath(Number(id.slice(1)))) });
        }
    }
}

registry.category("dwo_attpreview.viewers").add("archive", ArchiveViewer);
