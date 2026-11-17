/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onMounted, onWillStart, onWillUnmount, proxy, signal, useListener, useProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";
import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";
import { DwoTreeView } from "@dwo_attpreview_core/js/tree_view";
import { DwoLineView } from "./line_view";
import {
    TEXT_LIBS_URL, FlatTree, LOG_LEVELS, ValueTree, elementPath, escapeHtml, highlightLines, htmlDocument, htmlNodes,
    humanSize, logLevels, markHighlighted, markLine, markdownDocument, markdownOutline, notebookDocument, parseDiff, parseIni,
    parseJson, parseNdjson, parsePo, parseSubtitles, parseToml, parseYaml, splitLines, xmlNodes,
} from "./formats";

const MAX_MATCHES = 100_000;
const MAX_EXPAND_ALL = 5000;

// views of each group of files (server: text_tools.FORMATS); the first one opens
const VIEWS = {
    markdown: ["preview", "structure", "raw"],
    html: ["preview", "structure", "raw"],
    xml: ["structure", "raw"],
    svg: ["preview", "structure", "raw"],
    json: ["structure", "raw"],
    ndjson: ["structure", "raw"],
    notebook: ["preview", "structure", "raw"],
    yaml: ["structure", "raw"],
    toml: ["structure", "raw"],
    ini: ["structure", "raw"],
    code: ["raw"],
    log: ["preview", "raw"],
    diff: ["preview", "structure", "raw"],
    subtitles: ["preview", "raw"],
    po: ["preview", "raw"],
    text: ["raw"],
};
const LANG_NAMES = {
    xml: "XML", markdown: "Markdown", json: "JSON", yaml: "YAML", ini: "INI", properties: "Properties", python: "Python",
    javascript: "JavaScript", typescript: "TypeScript", css: "CSS", scss: "SCSS", sql: "SQL", bash: "Shell",
    powershell: "PowerShell", dos: "Batch", java: "Java", kotlin: "Kotlin", swift: "Swift", c: "C", cpp: "C++",
    csharp: "C#", go: "Go", rust: "Rust", php: "PHP", ruby: "Ruby", dart: "Dart", lua: "Lua", r: "R", perl: "Perl",
    scala: "Scala", groovy: "Groovy", gradle: "Gradle", dockerfile: "Dockerfile", makefile: "Makefile", diff: "Diff",
    latex: "LaTeX",
};
const FORMAT_NAMES = {
    markdown: "Markdown", html: "HTML", xml: "XML", svg: "SVG", json: "JSON", ndjson: "JSON Lines", notebook: "Jupyter notebook",
    yaml: "YAML", toml: "TOML", ini: "Configuration", log: "Log", diff: "Diff", subtitles: "Subtitles", po: "Translations (PO)",
    text: "Text",
};
const LEVEL_LABELS = { error: "Errors", warning: "Warnings", info: "Info", debug: "Debug", other: "Other" };

/**
 * Viewer of the "text" engine. Raw (virtual lines with numbers, syntax colours, wrap, find, go to line, copy), and
 * by kind of file a Preview (Markdown / HTML / notebook in a sandboxed frame with no script and no network, log by
 * level, diff side by side, subtitles, PO entries) and a Structure (JSON / YAML / TOML / INI / XML / HTML tree,
 * Markdown outline, files of a diff). Big data stay in plain fields, outside OWL's reactivity.
 */
export class TextViewer extends Component {
    static template = "dwo_attpreview_text.TextViewer";
    static components = { DwoTreeView, DwoLineView };
    // Odoo 20 (Owl 3): no static props; the Core reads this list (fileUrl: binary fields, source: inner files)
    static dwoAttPreviewProps = ["content", "attachmentId", "downloadUrl", "fileUrl", "source"];
    props = useProps();

    setup() {
        this.notification = useService("notification");
        this.root = signal.ref(); // Odoo 20: signal ref, read as this.root()
        try {
            this.data = JSON.parse(this.props.content || "{}") || {};
        } catch {
            this.data = {};
        }
        this.text = this.data.text || "";
        this.group = this.data.format === "xml" && this.data.ext === "svg" ? "svg" : this.data.format || "text";
        this.ui = proxy({ // Odoo 20: proxy instead of useState
            mode: "raw",
            version: 0,
            treeVersion: 0,
            wrap: false,
            findOpen: false,
            query: "",
            matchCount: 0,
            matchIndex: 0,
            activeIndex: -1,
            levels: Object.fromEntries(LOG_LEVELS.map((l) => [l, true])),
            poFilter: "all",
            treeFilter: "",
            treeMatches: 0,
            focusPath: "",
            focusLine: 0,
            structureError: "",
            highlighted: false,
        });
        // a file cut at 10 MB: views that read line by line stay (log, diff, Markdown...), trees and pictures go
        const cut = (v) => this.data.truncated && (v === "structure" || (v === "preview" && this.group === "svg"));
        this.views = (VIEWS[this.group] || ["raw"]).filter((v) => this.hasView(v) && !cut(v));
        this.lines = splitLines(this.text);
        if (this.lines.length > 1 && this.lines[this.lines.length - 1] === "") {
            this.lines.pop(); // the last line break ends the last line, it does not open a new one
        }
        this.hl = null;
        this.matches = [];
        this.lineApi = {};
        onWillStart(async () => {
            await loadJS(TEXT_LIBS_URL);
            this.prepare();
        });
        onMounted(() => {
            // syntax colours after the first paint: the plain lines show at once
            this.hlTimer = setTimeout(() => this.highlight(), 30);
        });
        onWillUnmount(() => {
            clearTimeout(this.hlTimer);
            clearTimeout(this.findTimer);
            clearTimeout(this.filterTimer);
        });
        useListener(window, "keydown", (ev) => this.onKeydown(ev), { capture: true }); // Odoo 20: useListener
    }

    hasView(view) {
        const d = this.data;
        if (view === "preview") {
            if (this.group === "html") return Boolean(d.html !== undefined);
            if (this.group === "notebook") return Boolean(d.notebook);
        }
        if (view === "structure" && this.group === "xml" || (view === "structure" && this.group === "svg")) {
            return Boolean(d.xml);
        }
        if (view === "structure" && this.group === "notebook") {
            return true;
        }
        return true;
    }

    /** Parse what the first view needs; a structure that cannot be read falls back to the raw text. */
    prepare() {
        const first = this.views[0];
        this.ui.mode = first;
        if (first === "structure" && !this.buildStructure()) {
            this.ui.mode = "raw";
        }
        if (this.group === "log") {
            this.levels = logLevels(this.lines);
            this.levelCounts = Object.fromEntries(LOG_LEVELS.map((l) => [l, 0]));
            for (const level of this.levels) {
                this.levelCounts[LOG_LEVELS[level]]++;
            }
            this.applyLevels();
        }
        if (this.group === "diff") {
            this.diff = parseDiff(this.text);
        }
        if (this.group === "subtitles") {
            this.cues = parseSubtitles(this.text);
        }
        if (this.group === "po") {
            this.po = parsePo(this.text);
            this.applyPoFilter();
        }
    }

    highlight() {
        if (this.ui.mode === "raw" || this.views.includes("raw")) {
            this.hl = highlightLines(this.text, this.data.lang);
            if (this.hl && this.hl.length > this.lines.length) {
                this.hl.length = this.lines.length;
            }
            this.ui.highlighted = Boolean(this.hl);
            this.ui.version++;
        }
    }

    // --- top bar --------------------------------------------------------------------------------------------------
    get viewButtons() {
        const labels = { preview: _t("Preview"), structure: _t("Structure"), raw: _t("Raw") };
        return this.views.map((v) => ({ id: v, label: labels[v] }));
    }

    get infoParts() {
        const d = this.data;
        const parts = [];
        const kind = this.group === "code" ? LANG_NAMES[d.lang] || (d.ext || "").toUpperCase() : this.group === "text"
            ? _t("Text") : FORMAT_NAMES[this.group];
        if (kind) parts.push(kind);
        if (d.encoding) parts.push(d.encoding);
        if (d.eol) parts.push(d.eol);
        parts.push(`${this.lines.length.toLocaleString()} ${this.lines.length === 1 ? _t("line") : _t("lines")}`);
        parts.push(humanSize(d.size || 0));
        return parts;
    }

    get bigNoColours() {
        return Boolean(this.data.lang) && !this.ui.highlighted && this.text.length > 0 && this.ui.version > 0;
    }

    setMode(mode) {
        if (mode === this.ui.mode) {
            return;
        }
        if (mode === "structure" && !this.tree && !this.buildStructure()) {
            this.ui.mode = "structure"; // shows the error
            return;
        }
        this.ui.mode = mode;
        this.closeFind();
    }

    get lineMode() {
        return this.ui.mode === "raw" || (this.ui.mode === "preview" && this.group === "log");
    }

    toggleWrap() {
        this.startIndex = this.lineApi.firstVisible?.() || 0;
        this.ui.wrap = !this.ui.wrap;
    }

    async copyAll() {
        try {
            await browser.navigator.clipboard.writeText(this.text);
            this.notification.add(_t("The text is copied."), { type: "success" });
        } catch {
            this.notification.add(_t("The browser did not allow copying."), { type: "warning" });
        }
    }

    // --- raw lines ------------------------------------------------------------------------------------------------
    get gutterWidth() {
        return `${String(this.lines.length).length + 2}ch`;
    }

    get rawColumns() {
        return `${this.gutterWidth} minmax(0, 1fr)`;
    }

    rawRow(i) {
        const line = this.lines[i] ?? "";
        let html;
        const current = this.currentRow === i ? this.currentOccurrence : -1;
        if (this.needle && line.toLowerCase().includes(this.needle)) {
            html = this.hl ? markHighlighted(this.hl[i], line, this.needle, current) : markLine(line, this.needle, current);
        } else {
            html = this.hl ? this.hl[i] : escapeHtml(line);
        }
        return { cells: [{ num: i + 1, html: html || " " }] };
    }

    onLineReady(api) {
        this.lineApi = api;
    }

    // --- log ------------------------------------------------------------------------------------------------------
    get levelButtons() {
        return LOG_LEVELS.filter((l) => this.levelCounts?.[l]).map((l) => ({
            id: l, label: LEVEL_LABELS[l], count: this.levelCounts[l].toLocaleString(), on: this.ui.levels[l],
        }));
    }

    toggleLevel(level) {
        this.ui.levels[level] = !this.ui.levels[level];
        this.applyLevels();
        this.ui.version++;
        if (this.ui.query) {
            this.runFind(false);
        }
    }

    applyLevels() {
        const on = LOG_LEVELS.map((l) => this.ui.levels[l]);
        const visible = new Int32Array(this.lines.length);
        let n = 0;
        for (let i = 0; i < this.lines.length; i++) {
            if (on[this.levels[i]]) {
                visible[n++] = i;
            }
        }
        this.logVisible = visible.subarray(0, n);
    }

    get logCount() {
        return this.logVisible ? this.logVisible.length : 0;
    }

    logRow(i) {
        const index = this.logVisible[i];
        const line = this.lines[index] ?? "";
        const html = this.needle && line.toLowerCase().includes(this.needle)
            ? markLine(line, this.needle, this.currentRow === i ? this.currentOccurrence : -1)
            : escapeHtml(line);
        return { cls: `o_dwo_lv_${LOG_LEVELS[this.levels[index]]}`, cells: [{ num: index + 1, html: html || " " }] };
    }

    // --- find (Ctrl+F) and go to line (Ctrl+G) ---------------------------------------------------------------------
    /** Rows searched: the raw lines, or the log lines shown. */
    rowText(i) {
        return this.ui.mode === "raw" ? this.lines[i] : this.lines[this.logVisible[i]];
    }

    get rowCount() {
        return this.ui.mode === "raw" ? this.lines.length : this.logCount;
    }

    openFind() {
        this.ui.findOpen = true;
        setTimeout(() => {
            const input = this.root()?.querySelector(".o_dwo_txt_find_input");
            input?.focus();
            input?.select();
        });
    }

    closeFind() {
        this.ui.findOpen = false;
        this.ui.query = "";
        this.needle = "";
        this.matches = [];
        this.ui.matchCount = 0;
        this.ui.version++;
    }

    onFindInput(ev) {
        this.ui.query = ev.target.value;
        clearTimeout(this.findTimer);
        this.findTimer = setTimeout(() => this.runFind(true), 150);
    }

    /** Every occurrence: [row, occurrence in the row], at most MAX_MATCHES. */
    runFind(jump) {
        const needle = this.ui.query.toLowerCase();
        this.needle = needle;
        const matches = [];
        if (needle) {
            const count = this.rowCount;
            for (let i = 0; i < count && matches.length < MAX_MATCHES; i++) {
                const lower = (this.rowText(i) || "").toLowerCase();
                let n = 0;
                for (let at = lower.indexOf(needle); at >= 0 && matches.length < MAX_MATCHES; at = lower.indexOf(needle, at + needle.length)) {
                    matches.push([i, n++]);
                }
            }
        }
        this.matches = matches;
        this.ui.matchCount = matches.length;
        this.ui.matchIndex = 0;
        if (jump && matches.length) {
            const first = this.lineApi.firstVisible?.() || 0;
            const next = matches.findIndex(([row]) => row >= first);
            this.ui.matchIndex = next < 0 ? 0 : next;
        }
        this.showMatch();
    }

    showMatch() {
        const match = this.matches[this.ui.matchIndex];
        this.currentRow = match ? match[0] : -1;
        this.currentOccurrence = match ? match[1] : -1;
        this.ui.version++;
        if (match) {
            this.lineApi.scrollToIndex?.(match[0]);
        }
    }

    nextMatch(step = 1) {
        if (!this.matches.length) {
            return;
        }
        this.ui.matchIndex = (this.ui.matchIndex + step + this.matches.length) % this.matches.length;
        this.showMatch();
    }

    onFindKeydown(ev) {
        if (ev.key === "Enter") {
            ev.preventDefault();
            this.nextMatch(ev.shiftKey ? -1 : 1);
        } else if (ev.key === "Escape") {
            ev.preventDefault();
            ev.stopPropagation();
            this.closeFind();
        }
    }

    get matchLabel() {
        if (!this.ui.query) {
            return "";
        }
        if (!this.ui.matchCount) {
            return _t("No result");
        }
        const more = this.ui.matchCount >= MAX_MATCHES ? "+" : "";
        return `${this.ui.matchIndex + 1} / ${this.ui.matchCount.toLocaleString()}${more}`;
    }

    onGotoKeydown(ev) {
        if (ev.key === "Enter") {
            ev.preventDefault();
            this.gotoLine(parseInt(ev.target.value, 10));
        } else if (ev.key === "Escape") {
            ev.stopPropagation();
            ev.target.blur();
        }
    }

    /** Show line n (1-based) of the raw text. */
    gotoLine(n) {
        if (!n || n < 1) {
            return;
        }
        const index = Math.min(n, this.lines.length) - 1;
        this.startIndex = Math.max(index - 5, 0);
        this.ui.activeIndex = index;
        if (this.ui.mode !== "raw") {
            this.ui.mode = "raw";
            return; // the raw list opens on startIndex
        }
        this.lineApi.scrollToIndex?.(index);
    }

    /** Ctrl+F / Ctrl+G in the top dialog, on a view of lines; other views keep the browser's own find. */
    onKeydown(ev) {
        const modal = this.root()?.closest(".modal");
        const modals = document.querySelectorAll(".modal");
        if (!modal || modals[modals.length - 1] !== modal || !(ev.ctrlKey || ev.metaKey) || ev.altKey) {
            return;
        }
        const key = ev.key.toLowerCase();
        if (key === "f" && (this.lineMode || this.group === "subtitles" || this.group === "po" || this.ui.mode === "structure")) {
            ev.preventDefault();
            ev.stopPropagation();
            if (this.ui.mode === "structure") {
                this.root().querySelector(".o_dwo_txt_tree_filter")?.focus();
            } else if (!this.lineMode) {
                this.setMode("raw");
                this.openFind();
            } else {
                this.openFind();
            }
        } else if (key === "g" && this.views.includes("raw")) {
            ev.preventDefault();
            ev.stopPropagation();
            this.root().querySelector(".o_dwo_txt_goto")?.focus();
        }
    }

    // --- structure (trees) ----------------------------------------------------------------------------------------
    /** Build the tree of the file once; false (and ui.structureError) when the file cannot be read. */
    buildStructure() {
        const d = this.data;
        try {
            switch (this.group) {
                case "json":
                case "notebook":
                    this.tree = new ValueTree(parseJson(this.text));
                    break;
                case "ndjson":
                    this.tree = new ValueTree(parseNdjson(this.text));
                    break;
                case "yaml":
                    this.tree = new ValueTree(parseYaml(this.text));
                    break;
                case "toml":
                    this.tree = new ValueTree(parseToml(this.text));
                    break;
                case "ini":
                    this.tree = new ValueTree(parseIni(this.text));
                    break;
                case "xml":
                case "svg":
                    if (!d.xml) {
                        throw new Error(d.structure_error || _t("The XML is not well formed."));
                    }
                    this.tree = new FlatTree(xmlNodes(d.xml.nodes), elementPath);
                    this.treeTruncated = d.xml.truncated;
                    break;
                case "html":
                    this.tree = new FlatTree(htmlNodes(this.text), elementPath);
                    break;
                case "markdown":
                    this.tree = new FlatTree(markdownOutline(this.text));
                    break;
                case "diff":
                    this.diff = this.diff || parseDiff(this.text);
                    this.tree = new FlatTree(this.diff.files.map((f) => ({
                        parent: -1, name: f.name, badge: "±", badgeClass: "o_dwo_txt_t_tag",
                        adds: `+${f.adds}`, dels: `−${f.dels}`, row: f.row,
                    })));
                    break;
                default:
                    throw new Error(_t("No structure for this kind of file."));
            }
        } catch (error) {
            this.tree = null;
            this.ui.structureError = this.structureMessage(error);
            return false;
        }
        this.ui.structureError = "";
        return true;
    }

    structureMessage(error) {
        const what = {
            json: _t("This is not valid JSON"), notebook: _t("This is not valid JSON"), ndjson: _t("This is not valid JSON"),
            yaml: _t("This is not valid YAML"), toml: _t("This is not valid TOML"), ini: _t("No key = value settings found"),
        }[this.group];
        const detail = String(error?.message || error || "").split("\n")[0].slice(0, 300);
        return what ? `${what}: ${detail}` : detail;
    }

    get treeRoot() {
        return this.tree instanceof ValueTree ? "0" : "r";
    }

    get treeExpanded() {
        if (this.tree instanceof ValueTree) {
            return ["0"];
        }
        if (this.group === "markdown") {
            // an outline is short: all its headings open
            return ["r", ...[...this.tree.kids.keys()].filter((id) => id !== "r").slice(0, 2000)];
        }
        return this.tree.nodes.length && this.group !== "diff" ? ["r", "0"] : ["r"];
    }

    get treeColumns() {
        if (this.tree instanceof ValueTree) {
            return [
                { key: "value", label: _t("Value"), width: "minmax(0, 1.5fr)", classKey: "valueClass" },
                { key: "type", label: _t("Type"), width: "5.5rem" },
            ];
        }
        if (this.group === "markdown") {
            return [{ key: "lineText", label: _t("Line"), width: "4.5rem", align: "right" }];
        }
        if (this.group === "diff") {
            return [
                { key: "adds", label: _t("Added"), width: "5rem", align: "right", classKey: "addsClass" },
                { key: "dels", label: _t("Removed"), width: "5rem", align: "right" },
            ];
        }
        const cols = [
            { key: "attrs", label: _t("Attributes"), width: "minmax(0, 1.4fr)" },
            { key: "text", label: _t("Text"), width: "minmax(0, 1fr)" },
        ];
        if (this.group !== "html") {
            cols.push({ key: "lineText", label: _t("Line"), width: "4.5rem", align: "right" });
        }
        return cols;
    }

    get treeNameLabel() {
        return { markdown: _t("Heading"), diff: _t("File"), xml: _t("Element"), svg: _t("Element"), html: _t("Element") }[this.group] || _t("Key");
    }

    get treeFilterLabel() {
        return {
            markdown: _t("Filter headings"), diff: _t("Filter files"), xml: _t("Filter elements and attributes"),
            svg: _t("Filter elements and attributes"), html: _t("Filter elements and attributes"),
        }[this.group] || _t("Filter keys and values");
    }

    get treeSize() {
        if (!this.tree) {
            return 0;
        }
        if (this.treeCount === undefined) {
            this.treeCount = this.tree instanceof ValueTree ? this.tree.countAll() : this.tree.size;
        }
        return this.treeCount;
    }

    get canExpandAll() {
        return this.treeSize <= MAX_EXPAND_ALL;
    }

    treeChildren(id) {
        return this.tree.getChildren(id);
    }

    treeIsFolder(id) {
        return this.tree.isFolder(id);
    }

    treeRow(id) {
        return this.tree.row(id);
    }

    onTreeReady(api) {
        this.treeApi = api;
    }

    onTreeFocus(id) {
        if (!id || !this.tree) {
            this.ui.focusPath = "";
            this.ui.focusLine = 0;
            return;
        }
        this.ui.focusPath = this.tree.path(id);
        this.ui.focusLine = this.tree instanceof FlatTree && id !== "r" ? this.tree.nodes[Number(id)].line || 0 : 0;
    }

    /** Enter / click on a leaf: a heading or an element goes to its line, a file of a diff to its changes. */
    onTreeOpen(id) {
        if (!(this.tree instanceof FlatTree) || id === "r") {
            return;
        }
        const node = this.tree.nodes[Number(id)];
        if (this.group === "diff") {
            this.ui.mode = "preview";
            this.startIndex = node.row;
            this.ui.version++;
        } else if (node.line) {
            this.gotoLine(node.line);
        }
    }

    showFocusLine() {
        this.gotoLine(this.ui.focusLine);
    }

    async copyPath() {
        try {
            await browser.navigator.clipboard.writeText(this.ui.focusPath);
            this.notification.add(_t("Path copied: %s", this.ui.focusPath), { type: "success" });
        } catch {
            // nothing: the path stays visible
        }
    }

    onTreeFilterInput(ev) {
        clearTimeout(this.filterTimer);
        const value = ev.target.value;
        this.filterTimer = setTimeout(() => this.applyTreeFilter(value), 250);
    }

    applyTreeFilter(value) {
        const text = value.trim();
        this.ui.treeFilter = value;
        if (!text) {
            this.tree.filter = null;
            this.ui.treeVersion++;
            return;
        }
        const { visible, expand, count } = this.tree.search(text);
        this.tree.filter = visible;
        this.ui.treeMatches = count;
        this.ui.treeVersion++;
        this.treeApi?.expandItems(expand);
    }

    expandAll() {
        this.treeApi?.expandAll();
    }

    collapseAll() {
        this.treeApi?.collapseAll();
    }

    // --- preview: frames, svg -------------------------------------------------------------------------------------
    get frame() {
        if (!this._frame) {
            if (this.group === "markdown") {
                this._frame = markdownDocument(this.text);
            } else if (this.group === "notebook") {
                this._frame = notebookDocument(this.data.notebook);
            } else {
                this._frame = { html: htmlDocument(this.data.html || ""), blocked: this.data.blocked_images || 0 };
            }
        }
        return this._frame;
    }

    get svgUrl() {
        return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(this.text)}`;
    }

    // --- preview: diff ----------------------------------------------------------------------------------------------
    get diffColumns() {
        return "4.5ch minmax(0, 1fr) 4.5ch minmax(0, 1fr)";
    }

    diffRow(i) {
        const row = this.diff.rows[i];
        if (row.type !== "pair") {
            return { cls: `o_dwo_diff_${row.type}`, cells: [{ html: escapeHtml(row.text) || " ", cls: "o_dwo_line_span" }] };
        }
        return {
            cells: [
                { num: row.left.num, html: escapeHtml(row.left.text) || " ", cls: row.left.cls },
                { num: row.right.num, html: escapeHtml(row.right.text) || " ", cls: row.right.cls },
            ],
        };
    }

    get diffStats() {
        const files = this.diff?.files || [];
        return {
            files: files.length,
            adds: files.reduce((n, f) => n + f.adds, 0),
            dels: files.reduce((n, f) => n + f.dels, 0),
        };
    }

    // --- preview: subtitles ---------------------------------------------------------------------------------------
    cueRow(i) {
        const cue = this.cues[i];
        return {
            cells: [
                { html: escapeHtml(cue.n), cls: "text-muted" },
                { html: escapeHtml(cue.start), cls: "o_dwo_txt_mono" },
                { html: escapeHtml(cue.end), cls: "o_dwo_txt_mono" },
                { html: escapeHtml(cue.text) || " " },
            ],
        };
    }

    // --- preview: PO ------------------------------------------------------------------------------------------------
    get poStats() {
        const entries = this.po?.entries || [];
        const translated = entries.filter((e) => e.translated && !e.fuzzy).length;
        const fuzzy = entries.filter((e) => e.fuzzy).length;
        return { total: entries.length, translated, fuzzy, missing: entries.length - translated - fuzzy };
    }

    get poLanguage() {
        const h = this.po?.header || {};
        return [h.Language, h["Project-Id-Version"]].filter(Boolean).join(" · ");
    }

    setPoFilter(filter) {
        this.ui.poFilter = filter;
        this.applyPoFilter();
        this.ui.version++;
    }

    applyPoFilter() {
        const f = this.ui.poFilter;
        this.poRows = this.po.entries.filter((e) =>
            f === "all" || (f === "missing" && !e.translated && !e.fuzzy) || (f === "fuzzy" && e.fuzzy) || (f === "done" && e.translated && !e.fuzzy));
    }

    poRow(i) {
        const e = this.poRows[i];
        const source = (e.context ? `<span class="o_dwo_po_ctx">${escapeHtml(e.context)}</span>` : "") +
            escapeHtml(e.id) + (e.plural ? `<span class="o_dwo_po_plural">${escapeHtml(e.plural)}</span>` : "");
        const strs = e.strs.length > 1
            ? e.strs.map((s, k) => `<span class="o_dwo_po_n">[${k}]</span> ${escapeHtml(s)}`).join("\n")
            : escapeHtml(e.strs[0] || "");
        const refs = e.refs.slice(0, 3).join("\n") + (e.refs.length > 3 ? `\n+${e.refs.length - 3}` : "");
        return {
            cls: e.fuzzy ? "o_dwo_po_fuzzy" : e.translated ? "" : "o_dwo_po_missing",
            cells: [
                { html: source || " " },
                { html: strs || (e.fuzzy ? "" : `<span class="o_dwo_po_empty">${escapeHtml(_t("not translated"))}</span>`) },
                { html: escapeHtml(refs) || " ", cls: "o_dwo_po_refs" },
            ],
        };
    }
}

registry.category("dwo_attpreview.viewers").add("text", TextViewer);
