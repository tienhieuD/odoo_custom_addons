/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
// Readers of the text viewer, without OWL: line splitting, syntax colours by line, JSON / YAML / TOML / INI values,
// trees, logs, diffs, subtitles, PO files, and the documents of the sandboxed preview frame (Markdown, HTML,
// notebooks). Nothing here runs the content of a file.

/** Libraries of static/lib/text_libs (highlight.js, markdown-it, js-yaml, smol-toml), loaded on demand. */
export const TEXT_LIBS_URL = "/dwo_attpreview_text/static/lib/text_libs/text_libs.min.js";
export const libs = () => window.DwoTextLibs;

// syntax colours are computed for the whole file at once: above these sizes the raw view stays plain (fast)
export const HIGHLIGHT_MAX_CHARS = 1_500_000;
export const HIGHLIGHT_MAX_LINES = 40_000;
export const MAX_TREE_NODES = 1_000_000;
// policy of the preview frame: no script (sandbox), nothing from the network; inline styles and data: pictures only
export const FRAME_CSP = "default-src 'none'; img-src data:; style-src 'unsafe-inline'; font-src data:";

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
export function escapeHtml(text) {
    return String(text ?? "").replace(/[&<>"']/g, (ch) => ESC[ch]);
}

export function splitLines(text) {
    return (text || "").split(/\r\n|\r|\n/);
}

/**
 * highlight.js output of a whole file, cut into lines. A span may run over several lines (a comment, a string):
 * it is closed at the end of each line and opened again at the start of the next, so each line is valid HTML.
 */
export function splitHighlighted(html) {
    const out = [];
    const stack = [];
    const TAG = /<span class="[^"]*">|<\/span>/g;
    for (const line of html.split("\n")) {
        const prefix = stack.join("");
        let match;
        TAG.lastIndex = 0;
        while ((match = TAG.exec(line))) {
            if (match[0] === "</span>") {
                stack.pop();
            } else {
                stack.push(match[0]);
            }
        }
        out.push(prefix + line + "</span>".repeat(stack.length));
    }
    return out;
}

/** Highlighted lines (HTML strings) of a text, or null when it is too large or the language is unknown. */
export function highlightLines(text, language) {
    const L = libs();
    if (!language || !L || !L.hljs.getLanguage(language) || text.length > HIGHLIGHT_MAX_CHARS) {
        return null;
    }
    const normalized = text.replace(/\r\n?/g, "\n");
    if (normalized.split("\n").length > HIGHLIGHT_MAX_LINES) {
        return null;
    }
    try {
        return splitHighlighted(L.hljs.highlight(normalized, { language, ignoreIllegals: true }).value);
    } catch {
        return null;
    }
}

/** A line as HTML with every occurrence of `needle` (lower case) in a <mark>; `current` marks the active one. */
export function markLine(line, needle, current = -1) {
    if (!needle) {
        return escapeHtml(line);
    }
    const lower = line.toLowerCase();
    let html = "";
    let from = 0;
    let n = 0;
    for (let at = lower.indexOf(needle); at >= 0; at = lower.indexOf(needle, at + needle.length)) {
        html += escapeHtml(line.slice(from, at));
        const cls = n === current ? ' class="o_dwo_txt_mark_current"' : "";
        html += `<mark${cls}>${escapeHtml(line.slice(at, at + needle.length))}</mark>`;
        from = at + needle.length;
        n++;
    }
    return html + escapeHtml(line.slice(from));
}

/**
 * Same as markLine, on a line already coloured by highlight.js (`html`; `line` is its plain text): the marks are put
 * around the text between the tags, closed and opened again at each tag, so the colours stay.
 */
export function markHighlighted(html, line, needle, current = -1) {
    if (!needle) {
        return html;
    }
    const lower = line.toLowerCase();
    const ranges = [];
    for (let at = lower.indexOf(needle); at >= 0; at = lower.indexOf(needle, at + needle.length)) {
        ranges.push([at, at + needle.length]);
    }
    if (!ranges.length) {
        return html;
    }
    let out = "";
    let pos = 0; // offset in the plain text
    let r = 0; // current range
    let open = false;
    const openTag = () => (r === current ? '<mark class="o_dwo_txt_mark_current">' : "<mark>");
    const TOKEN = /<[^>]*>|&[#\w]+;|[^<&]/g;
    let match;
    while ((match = TOKEN.exec(html))) {
        const token = match[0];
        if (token[0] === "<" && token.length > 1) {
            out += open ? `</mark>${token}${openTag()}` : token;
            continue;
        }
        if (!open && r < ranges.length && pos === ranges[r][0]) {
            out += openTag();
            open = true;
        }
        out += token;
        pos++;
        if (open && pos === ranges[r][1]) {
            out += "</mark>";
            open = false;
            r++;
            if (r < ranges.length && pos === ranges[r][0]) {
                out += openTag();
                open = true;
            }
        }
    }
    return out + (open ? "</mark>" : "");
}

// --- JSON and friends -------------------------------------------------------------------------------------------
/** JSON with comments (// and /* *\/) and trailing commas removed, strings kept as they are. */
export function stripJsonComments(text) {
    let out = "";
    let i = 0;
    const n = text.length;
    while (i < n) {
        const ch = text[i];
        if (ch === '"' || ch === "'") {
            let j = i + 1;
            while (j < n && text[j] !== ch) {
                j += text[j] === "\\" ? 2 : 1;
            }
            out += text.slice(i, j + 1);
            i = j + 1;
        } else if (ch === "/" && text[i + 1] === "/") {
            while (i < n && text[i] !== "\n") {
                i++;
            }
        } else if (ch === "/" && text[i + 1] === "*") {
            const end = text.indexOf("*/", i + 2);
            i = end < 0 ? n : end + 2;
        } else {
            out += ch;
            i++;
        }
    }
    return out.replace(/,(\s*[}\]])/g, "$1");
}

/** Parse JSON (JSONC / JSON5 files: comments and trailing commas allowed). Throws with the message of JSON.parse. */
export function parseJson(text) {
    const clean = text.charCodeAt(0) === 0xfeff ? text.slice(1) : text;
    try {
        return JSON.parse(clean);
    } catch (error) {
        try {
            return JSON.parse(stripJsonComments(clean));
        } catch {
            throw error;
        }
    }
}

/** JSON Lines: an array with one value per line (a bad line becomes a short error text). */
export function parseNdjson(text) {
    const out = [];
    splitLines(text).forEach((line, i) => {
        if (line.trim()) {
            try {
                out.push(JSON.parse(line));
            } catch (error) {
                out.push(`⚠ line ${i + 1}: ${error.message}`);
            }
        }
    });
    return out;
}

export function parseYaml(text) {
    const docs = [];
    libs().yamlLoadAll(text, (doc) => docs.push(doc));
    return docs.length === 1 ? docs[0] : docs;
}

export function parseToml(text) {
    return libs().tomlParse(text);
}

/** INI, .cfg, .conf, .env and .properties: {section: {key: value}}, keys before any section at the top. */
export function parseIni(text) {
    const root = {};
    let section = root;
    let pairs = 0;
    let other = 0;
    for (const raw of splitLines(text)) {
        const line = raw.trim();
        if (!line || line[0] === "#" || line[0] === ";" || line[0] === "!") {
            continue;
        }
        const head = /^\[([^\]]+)\]$/.exec(line);
        if (head) {
            section = root[head[1].trim()] = root[head[1].trim()] || {};
            continue;
        }
        const pair = /^(?:export\s+)?([^=:\s][^=:]*?)\s*[=:]\s*(.*)$/.exec(line);
        if (pair) {
            let value = pair[2];
            if (/^(["']).*\1$/.test(value)) {
                value = value.slice(1, -1);
            }
            section[pair[1]] = value;
            pairs++;
        } else {
            other++;
        }
    }
    if (!pairs || other > pairs) {
        throw new Error("no key = value lines");
    }
    return root;
}

// --- trees --------------------------------------------------------------------------------------------------------
function kindOf(value) {
    if (value === null || value === undefined) return "null";
    if (Array.isArray(value)) return "array";
    if (value instanceof Date) return "date";
    return typeof value === "object" ? "object" : typeof value;
}

const BADGES = { object: "{ }", array: "[ ]", string: "abc", number: "123", bigint: "123", boolean: "y/n", null: "∅", date: "date" };
const IDENT = /^[A-Za-z_$][A-Za-z0-9_$]*$/;

function shortValue(value, kind) {
    let text;
    if (kind === "string") {
        text = JSON.stringify(value);
    } else if (kind === "date") {
        text = isNaN(value) ? String(value) : value.toISOString();
    } else {
        text = String(value);
    }
    return text.length > 300 ? text.slice(0, 299) + "…" : text;
}

/**
 * A JavaScript value (parsed JSON, YAML, TOML, INI) as a tree for DwoTreeView. Children are created when a node is
 * expanded (or searched), so a file of a million values opens at once; the data stays outside OWL's reactivity.
 */
export class ValueTree {
    constructor(value, rootName = "$") {
        this.values = [value];
        this.keys = [rootName];
        this.parents = [-1];
        this.isIndex = [false];
        this.kids = new Map();
        this.filter = null;
    }

    get size() {
        return this.values.length;
    }

    childIds(id) {
        const i = Number(id);
        let kids = this.kids.get(i);
        if (!kids) {
            kids = [];
            const value = this.values[i];
            const kind = kindOf(value);
            if (kind === "object" || kind === "array") {
                const entries = kind === "array" ? value.map((v, k) => [k, v]) : Object.entries(value);
                for (const [key, child] of entries) {
                    if (this.values.length >= MAX_TREE_NODES) {
                        break;
                    }
                    kids.push(String(this.values.length));
                    this.values.push(child);
                    this.keys.push(kind === "array" ? `[${key}]` : key);
                    this.isIndex.push(kind === "array");
                    this.parents.push(i);
                }
            }
            this.kids.set(i, kids);
        }
        return kids;
    }

    getChildren(id) {
        const kids = this.childIds(id);
        return this.filter ? kids.filter((k) => this.filter.has(k)) : kids;
    }

    isFolder(id) {
        const value = this.values[Number(id)];
        const kind = kindOf(value);
        return (kind === "object" || kind === "array") && Object.keys(value).length > 0;
    }

    row(id) {
        const i = Number(id);
        const value = this.values[i];
        const kind = kindOf(value);
        const container = kind === "object" || kind === "array";
        const count = container ? Object.keys(value).length : 0;
        return {
            name: this.keys[i],
            badge: BADGES[kind] || kind,
            badgeClass: `o_dwo_txt_t_${kind}`,
            nameClass: this.isIndex[i] ? "o_dwo_txt_index" : "",
            value: container ? (kind === "array" ? `${count} item${count === 1 ? "" : "s"}` : `${count} key${count === 1 ? "" : "s"}`) : shortValue(value, kind),
            valueClass: `o_dwo_txt_v_${kind}`,
            type: kind,
            title: this.path(id),
        };
    }

    /** JSONPath-like path of a node: $.items[0].name, $["a key"]. */
    path(id) {
        const parts = [];
        for (let i = Number(id); i > 0; i = this.parents[i]) {
            const key = this.keys[i];
            parts.push(this.isIndex[i] ? key : IDENT.test(key) ? `.${key}` : `[${JSON.stringify(key)}]`);
        }
        return "$" + parts.reverse().join("");
    }

    /** Create every node (for a search), up to MAX_TREE_NODES. */
    expandEverything() {
        for (let i = 0; i < this.values.length && this.values.length < MAX_TREE_NODES; i++) {
            this.childIds(String(i));
        }
    }

    /** Nodes whose key or value contains `text`, with their parents; returns {visible: Set, expand: ids, count}. */
    search(text, maxExpand = 5000) {
        this.expandEverything();
        const needle = text.toLowerCase();
        const visible = new Set(["0"]);
        const expand = new Set();
        let count = 0;
        for (let i = 1; i < this.values.length; i++) {
            const kind = kindOf(this.values[i]);
            const own = kind === "object" || kind === "array" ? "" : shortValue(this.values[i], kind);
            if (this.keys[i].toLowerCase().includes(needle) || own.toLowerCase().includes(needle)) {
                count++;
                visible.add(String(i));
                for (let p = this.parents[i]; p > 0 && !visible.has(String(p)); p = this.parents[p]) {
                    visible.add(String(p));
                    if (expand.size < maxExpand) {
                        expand.add(String(p));
                    }
                }
            }
        }
        return { visible, expand: [...expand], count };
    }

    countAll() {
        // number of values, without creating the nodes
        let n = 0;
        const stack = [this.values[0]];
        while (stack.length && n < MAX_TREE_NODES) {
            const value = stack.pop();
            n++;
            const kind = kindOf(value);
            if (kind === "object" || kind === "array") {
                for (const child of Object.values(value)) {
                    stack.push(child);
                }
            }
        }
        return n;
    }
}

/**
 * A tree given as flat rows (XML elements from the server, HTML elements, Markdown headings, files of a diff):
 * nodes = [{parent, name, badge, cols..., line, title}], parent -1 for the top nodes. Root id "r".
 */
export class FlatTree {
    constructor(nodes, pathOf = null) {
        this.nodes = nodes;
        this.kids = new Map([["r", []]]);
        nodes.forEach((node, i) => {
            const parent = node.parent < 0 ? "r" : String(node.parent);
            if (!this.kids.has(parent)) {
                this.kids.set(parent, []);
            }
            this.kids.get(parent).push(String(i));
        });
        this.filter = null;
        this.pathOf = pathOf;
    }

    get size() {
        return this.nodes.length;
    }

    getChildren(id) {
        const kids = this.kids.get(id) || [];
        return this.filter ? kids.filter((k) => this.filter.has(k)) : kids;
    }

    isFolder(id) {
        return id === "r" || (this.kids.get(id) || []).length > 0;
    }

    row(id) {
        if (id === "r") {
            return { name: "" };
        }
        const node = this.nodes[Number(id)];
        return { ...node, count: (this.kids.get(id) || []).length || undefined, title: this.path(id) };
    }

    path(id) {
        return this.pathOf ? this.pathOf(this, Number(id)) : this.nodes[Number(id)]?.name || "";
    }

    search(text, maxExpand = 5000) {
        const needle = text.toLowerCase();
        const visible = new Set(["r"]);
        const expand = new Set();
        let count = 0;
        this.nodes.forEach((node, i) => {
            const hay = `${node.name} ${node.attrs || ""} ${node.text || ""}`.toLowerCase();
            if (hay.includes(needle)) {
                count++;
                visible.add(String(i));
                for (let p = node.parent; p >= 0 && !visible.has(String(p)); p = this.nodes[p].parent) {
                    visible.add(String(p));
                    if (expand.size < maxExpand) {
                        expand.add(String(p));
                    }
                }
            }
        });
        return { visible, expand: [...expand], count };
    }
}

/** XPath-like path of an element of a FlatTree made from XML or HTML: /root/item[2]/name. */
export function elementPath(tree, index) {
    const parts = [];
    for (let i = index; i >= 0; i = tree.nodes[i].parent) {
        const node = tree.nodes[i];
        const siblings = tree.kids.get(node.parent < 0 ? "r" : String(node.parent)) || [];
        const same = siblings.filter((k) => tree.nodes[Number(k)].tag === node.tag);
        parts.push(same.length > 1 ? `${node.tag}[${same.indexOf(String(i)) + 1}]` : node.tag);
    }
    return "/" + parts.reverse().join("/");
}

function attrsText(attrs) {
    const text = attrs.map(([k, v]) => `${k}="${v}"`).join(" ");
    return text.length > 300 ? text.slice(0, 299) + "…" : text;
}

/** XML elements of the server ([parent, name, attrs, text, line]) as FlatTree nodes. */
export function xmlNodes(rows) {
    return rows.map(([parent, tag, attrs, text, line]) => ({
        parent, tag, name: tag, badge: "</>", badgeClass: "o_dwo_txt_t_tag", attrs: attrsText(attrs), text, line,
        lineText: line ? String(line) : "",
    }));
}

/** Elements of an HTML page (parsed by DOMParser: an inert document, nothing runs or loads) as FlatTree nodes. */
export function htmlNodes(text, max = 200_000) {
    const doc = new DOMParser().parseFromString(text, "text/html");
    const nodes = [];
    const walk = (el, parent) => {
        if (nodes.length >= max) {
            return;
        }
        const tag = el.tagName.toLowerCase();
        const own = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.nodeValue).join(" ");
        const textValue = own.replace(/\s+/g, " ").trim();
        const index = nodes.length;
        nodes.push({
            parent, tag, name: tag, badge: "</>", badgeClass: "o_dwo_txt_t_tag",
            attrs: attrsText([...el.attributes].map((a) => [a.name, a.value])),
            text: textValue.length > 300 ? textValue.slice(0, 299) + "…" : textValue,
        });
        for (const child of el.children) {
            walk(child, index);
        }
    };
    walk(doc.documentElement, -1);
    return nodes;
}

// --- Markdown -----------------------------------------------------------------------------------------------------
function slug(text, used) {
    let base = text.toLowerCase().replace(/[^\p{L}\p{N}\s-]/gu, "").trim().replace(/\s+/g, "-") || "section";
    let id = base;
    for (let n = 1; used.has(id); n++) {
        id = `${base}-${n}`;
    }
    used.add(id);
    return id;
}

/**
 * markdown-it set up for the preview frame: raw HTML off (shown as text), links checked by markdown-it (no
 * javascript:), outside links open in a new tab, pictures that are not data: URIs are not loaded (counted in
 * env.blocked), headings get an id (env.headings) for the table of contents, code blocks get syntax colours.
 */
export function makeMarkdown() {
    const L = libs();
    const md = new L.MarkdownIt({
        html: false,
        linkify: true,
        typographer: false,
        highlight(code, lang) {
            const name = (lang || "").toLowerCase();
            if (name && L.hljs.getLanguage(name) && code.length < 200_000) {
                try {
                    return `<pre class="hljs"><code>${L.hljs.highlight(code, { language: name, ignoreIllegals: true }).value}</code></pre>`;
                } catch {
                    // plain below
                }
            }
            return "";
        },
    });
    md.renderer.rules.image = (tokens, idx, options, env) => {
        const token = tokens[idx];
        const src = token.attrGet("src") || "";
        const alt = escapeHtml(token.content || "");
        if (/^data:image\/(png|jpe?g|gif|webp);/i.test(src)) {
            return `<img src="${escapeHtml(src)}" alt="${alt}">`;
        }
        env.blocked = (env.blocked || 0) + 1;
        return `<span class="dwo-blocked" title="${escapeHtml(src)}">\u{1F5BC} ${alt || "picture"}</span>`;
    };
    const defaultLink = md.renderer.rules.link_open || ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options));
    md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
        const href = tokens[idx].attrGet("href") || "";
        if (href.startsWith("#")) {
            tokens[idx].attrSet("target", "_self");
        } else {
            tokens[idx].attrSet("target", "_blank");
            tokens[idx].attrSet("rel", "noopener noreferrer");
        }
        return defaultLink(tokens, idx, options, env, self);
    };
    md.renderer.rules.heading_open = (tokens, idx, options, env, self) => {
        const title = tokens[idx + 1]?.content || "";
        env.used = env.used || new Set();
        env.headings = env.headings || [];
        const id = slug(title, env.used);
        tokens[idx].attrSet("id", id);
        env.headings.push({ level: Number(tokens[idx].tag.slice(1)), title, id });
        return self.renderToken(tokens, idx, options);
    };
    return md;
}

/** Headings of a Markdown text as FlatTree nodes (nested by level), with their line in the raw text. */
export function markdownOutline(text) {
    const tokens = new (libs().MarkdownIt)({ html: false }).parse(text, {});
    const nodes = [];
    const stack = []; // [level, index]
    tokens.forEach((token, i) => {
        if (token.type !== "heading_open") {
            return;
        }
        const level = Number(token.tag.slice(1));
        while (stack.length && stack[stack.length - 1][0] >= level) {
            stack.pop();
        }
        const line = token.map ? token.map[0] + 1 : 0;
        nodes.push({
            parent: stack.length ? stack[stack.length - 1][1] : -1,
            name: tokens[i + 1]?.content || "",
            badge: token.tag.toUpperCase(),
            badgeClass: "o_dwo_txt_t_heading",
            line,
            lineText: line ? String(line) : "",
        });
        stack.push([level, nodes.length - 1]);
    });
    return nodes;
}

const FRAME_STYLE = `
:root{color-scheme:light}
body{margin:0;font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;color:#1f2328;background:#fff}
.dwo-page{display:flex;gap:32px;max-width:1180px;margin:0 auto;padding:24px 32px 48px}
.dwo-main{flex:1 1 auto;min-width:0}
.dwo-toc{flex:0 0 220px;position:sticky;top:16px;align-self:flex-start;max-height:calc(100vh - 32px);overflow:auto;font-size:13px;border-left:1px solid #d0d7de;padding-left:12px}
.dwo-toc b{display:block;margin-bottom:6px;color:#59636e;text-transform:uppercase;font-size:11px;letter-spacing:.04em}
.dwo-toc a{display:block;color:#1f2328;text-decoration:none;padding:2px 0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dwo-toc a:hover{color:#0969da}
.dwo-toc .l2{padding-left:10px}.dwo-toc .l3{padding-left:20px}.dwo-toc .l4,.dwo-toc .l5,.dwo-toc .l6{padding-left:30px}
@media (max-width:900px){.dwo-toc{display:none}}
h1,h2{border-bottom:1px solid #d1d9e0;padding-bottom:.3em}
h1,h2,h3,h4{margin:1.4em 0 .6em;line-height:1.25}
a{color:#0969da}
code{font:13px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:#eff1f3;padding:.15em .35em;border-radius:5px}
pre{background:#f6f8fa;padding:12px 16px;border-radius:6px;overflow:auto;line-height:1.45}
pre code{background:none;padding:0}
pre.hljs{background:#f6f8fa}
blockquote{margin:0;padding:0 1em;color:#59636e;border-left:.25em solid #d1d9e0}
table{border-collapse:collapse;margin:1em 0;display:block;overflow:auto;max-width:100%}
th,td{border:1px solid #d1d9e0;padding:6px 13px}
tr:nth-child(2n){background:#f6f8fa}
img{max-width:100%}
hr{border:0;border-top:1px solid #d1d9e0}
.dwo-blocked{display:inline-block;padding:2px 8px;border:1px dashed #c4c8cf;border-radius:4px;color:#59636e;font-size:12px;background:#f6f8fa}
.dwo-cell{margin:0 0 14px}
.dwo-in{display:flex;gap:8px}
.dwo-prompt{flex:0 0 64px;text-align:right;font:12px ui-monospace,Menlo,monospace;color:#6e7781;padding-top:12px}
.dwo-prompt.out{color:#bc4c00}
.dwo-body{flex:1 1 auto;min-width:0}
.dwo-body > pre{margin:0}
.dwo-out pre{background:#fff;border:0;padding:4px 0;margin:0;white-space:pre-wrap}
.dwo-out pre.err{background:#fff0f0;color:#82071e;padding:8px}
.dwo-out pre.stderr{background:#fff8e6}
.dwo-out img{display:block;margin:6px 0}
.dwo-md{padding:0 4px}
`;

/** Full document of the preview frame: CSP first, no script, links open in a new tab. */
export function frameDocument(body, { toc = null, plain = false } = {}) {
    if (plain) {
        // an HTML page keeps its own look (its inline styles): only a neutral base
        return (
            `<!DOCTYPE html><html><head><meta charset="utf-8">` +
            `<meta http-equiv="Content-Security-Policy" content="${FRAME_CSP}">` +
            `<meta name="referrer" content="no-referrer"><base target="_blank">` +
            `<style>:root{color-scheme:light}body{margin:16px;font-family:Arial,Helvetica,sans-serif;background:#fff;color:#222}img{max-width:100%}</style>` +
            `</head><body>${body}</body></html>`
        );
    }
    const css = FRAME_STYLE + (libs()?.hljsCss || "");
    const nav = toc && toc.length >= 3
        ? `<nav class="dwo-toc" aria-label="Contents"><b>Contents</b>${toc
            .map((h) => `<a class="l${h.level}" href="#${escapeHtml(h.id)}" target="_self">${escapeHtml(h.title)}</a>`)
            .join("")}</nav>`
        : "";
    return (
        `<!DOCTYPE html><html><head><meta charset="utf-8">` +
        `<meta http-equiv="Content-Security-Policy" content="${FRAME_CSP}">` +
        `<meta name="referrer" content="no-referrer"><base target="_blank">` +
        `<style>${css}</style></head><body><div class="dwo-page">${nav}<main class="dwo-main">${body}</main></div></body></html>`
    );
}

/** The Markdown preview: {html (frame document), blocked (pictures not loaded), headings}. */
export function markdownDocument(text) {
    const env = {};
    const body = makeMarkdown().render(text, env);
    return { html: frameDocument(body, { toc: env.headings }), blocked: env.blocked || 0, headings: env.headings || [] };
}

/** A notebook of the server (cells with sanitized outputs) as a frame document. */
export function notebookDocument(notebook) {
    const L = libs();
    const md = makeMarkdown();
    const env = {};
    const lang = L.hljs.getLanguage(notebook.language) ? notebook.language : "python";
    const code = (source) => {
        try {
            return L.hljs.highlight(source, { language: lang, ignoreIllegals: true }).value;
        } catch {
            return escapeHtml(source);
        }
    };
    const cells = (notebook.cells || []).map((cell) => {
        if (cell.type === "markdown") {
            return `<div class="dwo-cell dwo-in"><div class="dwo-prompt"></div><div class="dwo-body dwo-md">${md.render(cell.source, env)}</div></div>`;
        }
        if (cell.type === "raw") {
            return `<div class="dwo-cell dwo-in"><div class="dwo-prompt"></div><div class="dwo-body"><pre>${escapeHtml(cell.source)}</pre></div></div>`;
        }
        const count = cell.count === null || cell.count === undefined ? " " : cell.count;
        const outputs = (cell.outputs || []).map((out) => {
            if (out.kind === "image") {
                return /^data:image\//.test(out.src) ? `<img src="${escapeHtml(out.src)}" alt="output">` : "";
            }
            if (out.kind === "html") {
                return `<div>${out.html}</div>`; // sanitized by the server (html_sanitize), shown in this frame
            }
            if (out.kind === "markdown") {
                return md.render(out.text, env);
            }
            const cls = out.kind === "error" ? "err" : out.stderr ? "stderr" : "";
            return `<pre class="${cls}">${escapeHtml(out.text)}</pre>`;
        }).join("");
        return (
            `<div class="dwo-cell"><div class="dwo-in"><div class="dwo-prompt">In [${escapeHtml(count)}]:</div>` +
            `<div class="dwo-body"><pre class="hljs"><code>${code(cell.source)}</code></pre></div></div>` +
            (outputs ? `<div class="dwo-in dwo-out"><div class="dwo-prompt out">${cell.count ? `Out [${escapeHtml(count)}]:` : ""}</div><div class="dwo-body">${outputs}</div></div>` : "") +
            `</div>`
        );
    });
    return { html: frameDocument(cells.join("")), blocked: env.blocked || 0 };
}

/** The HTML preview: the page sanitized by the server, in the frame (its own styles were removed by the sanitizer). */
export function htmlDocument(sanitized) {
    return frameDocument(sanitized, { plain: true });
}

// --- logs ---------------------------------------------------------------------------------------------------------
export const LOG_LEVELS = ["error", "warning", "info", "debug", "other"];
const LEVEL_WORD = /\b(CRITICAL|FATAL|EMERG(?:ENCY)?|ALERT|CRIT|SEVERE|ERROR|ERR|WARNING|WARN|NOTICE|INFO|DEBUG|TRACE|VERBOSE)\b/i;
const LEVEL_OF = {
    critical: "error", fatal: "error", emerg: "error", emergency: "error", alert: "error", crit: "error",
    severe: "error", error: "error", err: "error", warning: "warning", warn: "warning", notice: "info",
    info: "info", debug: "debug", trace: "debug", verbose: "debug",
};

/**
 * Level of each line of a log (Uint8Array of indexes in LOG_LEVELS). A line without a level word (a traceback, a
 * wrapped message) takes the level of the line above; lines before the first level are "other".
 */
export function logLevels(lines) {
    const levels = new Uint8Array(lines.length);
    const other = LOG_LEVELS.indexOf("other");
    let current = other;
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const match = LEVEL_WORD.exec(line.length > 300 ? line.slice(0, 300) : line);
        // a level word only counts in upper case, or in brackets / after a separator ("level=info")
        if (match && (match[1] === match[1].toUpperCase() || /[[(=:<|]\s*$/.test(line.slice(0, match.index)))) {
            current = LOG_LEVELS.indexOf(LEVEL_OF[match[1].toLowerCase()]);
        }
        levels[i] = current;
    }
    return levels;
}

// --- diff / patch -------------------------------------------------------------------------------------------------
/**
 * A unified diff as rows for a side-by-side view: {type: "file"|"hunk"|"pair", file, left: {num, text, cls},
 * right: {...}} and the files changed: [{name, adds, dels, row}].
 */
export function parseDiff(text) {
    const lines = splitLines(text);
    const rows = [];
    const files = [];
    let file = null;
    let oldNum = 0;
    let newNum = 0;
    let dels = [];
    let adds = [];
    const flush = () => {
        const n = Math.max(dels.length, adds.length);
        for (let i = 0; i < n; i++) {
            rows.push({
                type: "pair",
                left: dels[i] ? { num: dels[i][0], text: dels[i][1], cls: "o_dwo_diff_del" } : { num: "", text: "", cls: "o_dwo_diff_empty" },
                right: adds[i] ? { num: adds[i][0], text: adds[i][1], cls: "o_dwo_diff_add" } : { num: "", text: "", cls: "o_dwo_diff_empty" },
            });
        }
        dels = [];
        adds = [];
    };
    const startFile = (name) => {
        flush();
        file = { name, adds: 0, dels: 0, row: rows.length, hunks: 0 };
        files.push(file);
        rows.push({ type: "file", text: name });
    };
    let inHunk = false;
    let oldLeft = 0;
    let newLeft = 0;
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (inHunk && oldLeft <= 0 && newLeft <= 0) {
            flush();
            inHunk = false;
        }
        if (line.startsWith("diff --git ")) {
            const m = / b\/(.*)$/.exec(line);
            startFile(m ? m[1] : line.slice(11));
            inHunk = false;
        } else if (line.startsWith("--- ") && lines[i + 1]?.startsWith("+++ ") && !inHunk) {
            const name = lines[i + 1].slice(4).replace(/^b\//, "").split("\t")[0];
            const oldName = line.slice(4).replace(/^a\//, "").split("\t")[0];
            const shown = name === "/dev/null" ? oldName : name;
            // "diff --git" already started this file (no hunk yet): the --- / +++ lines only confirm it
            if (!file || file.hunks) {
                startFile(shown);
            }
            i++;
        } else if (line.startsWith("@@")) {
            flush();
            const m = /^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$/.exec(line);
            if (!file) {
                startFile("(diff)");
            }
            if (m) {
                oldNum = Number(m[1]);
                newNum = Number(m[3]);
                // lines left in this hunk: a "--- x" line after them starts a new file, not a deleted line
                oldLeft = m[2] === undefined ? 1 : Number(m[2]);
                newLeft = m[4] === undefined ? 1 : Number(m[4]);
            } else {
                oldLeft = newLeft = Infinity;
            }
            inHunk = true;
            file.hunks++;
            rows.push({ type: "hunk", text: line });
        } else if (inHunk && line.startsWith("-")) {
            dels.push([oldNum++, line.slice(1)]);
            file.dels++;
            oldLeft--;
        } else if (inHunk && line.startsWith("+")) {
            adds.push([newNum++, line.slice(1)]);
            file.adds++;
            newLeft--;
        } else if (inHunk && (line.startsWith(" ") || line === "")) {
            flush();
            if (line === "" && i === lines.length - 1) {
                continue;
            }
            const content = line.slice(1);
            oldLeft--;
            newLeft--;
            rows.push({ type: "pair", left: { num: oldNum++, text: content, cls: "" }, right: { num: newNum++, text: content, cls: "" } });
        } else if (line.startsWith("\\")) {
            // "\ No newline at end of file"
        } else {
            flush();
            inHunk = false;
            if (line.trim()) {
                rows.push({ type: "meta", text: line });
            }
        }
    }
    flush();
    return { rows, files };
}

// --- subtitles ----------------------------------------------------------------------------------------------------
const CUE_TIME = /^\s*((?:\d+:)?\d{1,2}:\d{2}[.,]\d{1,3})\s*-->\s*((?:\d+:)?\d{1,2}:\d{2}[.,]\d{1,3})/;

/** SRT and WebVTT cues: [{n, start, end, text}] (formatting tags removed from the text). */
export function parseSubtitles(text) {
    const cues = [];
    const blocks = (text || "").replace(/\r\n?/g, "\n").split(/\n{2,}/);
    for (const block of blocks) {
        const lines = block.split("\n").filter((l) => l.length);
        const at = lines.findIndex((l) => CUE_TIME.test(l));
        if (at < 0) {
            continue;
        }
        const [, start, end] = CUE_TIME.exec(lines[at]);
        cues.push({
            n: at > 0 ? lines[at - 1].trim() : String(cues.length + 1),
            start: start.replace(",", "."),
            end: end.replace(",", "."),
            text: lines.slice(at + 1).join("\n").replace(/<[^>]*>/g, ""),
        });
    }
    return cues;
}

// --- PO / POT -----------------------------------------------------------------------------------------------------
function poString(rest) {
    const m = /^\s*"(.*)"\s*$/.exec(rest);
    if (!m) {
        return "";
    }
    return m[1].replace(/\\(.)/g, (all, ch) => ({ n: "\n", t: "\t", r: "\r", '"': '"', "\\": "\\" })[ch] ?? all);
}

/**
 * Entries of a gettext PO / POT file: {header: {key: value}, entries: [{context, id, plural, strs, fuzzy, obsolete,
 * refs, comment}]}. Obsolete entries (#~) are skipped.
 */
export function parsePo(text) {
    const entries = [];
    let entry = null;
    let field = null;
    const start = () => {
        entry = entry || { context: "", id: "", plural: "", strs: [], fuzzy: false, refs: [], comment: "", hasStr: false };
    };
    const finish = () => {
        if (entry && (entry.id || entry.strs.length)) {
            entries.push(entry);
        }
        entry = null;
        field = null;
    };
    const append = (value) => {
        if (field === "msgctxt") entry.context += value;
        else if (field === "msgid") entry.id += value;
        else if (field === "msgid_plural") entry.plural += value;
        else {
            const k = Number(field.slice(6));
            entry.strs[k] = (entry.strs[k] || "") + value;
        }
    };
    for (const raw of splitLines(text)) {
        const line = raw.trim();
        if (!line) {
            finish();
            continue;
        }
        if (line.startsWith("#~")) {
            continue;
        }
        if (line.startsWith("#")) {
            if (entry?.hasStr) {
                finish();
            }
            start();
            if (line.startsWith("#,")) {
                entry.fuzzy = entry.fuzzy || /\bfuzzy\b/.test(line);
            } else if (line.startsWith("#:")) {
                entry.refs.push(...line.slice(2).trim().split(/\s+/));
            } else if (line.startsWith("#.")) {
                entry.comment += (entry.comment ? "\n" : "") + line.slice(2).trim();
            }
            continue;
        }
        const m = /^(msgctxt|msgid_plural|msgid|msgstr(?:\[(\d+)\])?)\s+(.*)$/.exec(line);
        if (m) {
            if ((m[1] === "msgctxt" || m[1] === "msgid") && entry?.hasStr) {
                finish();
            }
            start();
            field = m[1].startsWith("msgstr") ? `msgstr${m[2] || 0}` : m[1];
            if (field.startsWith("msgstr")) {
                entry.hasStr = true;
                entry.strs[Number(field.slice(6))] = entry.strs[Number(field.slice(6))] || "";
            }
            append(poString(m[3]));
        } else if (line.startsWith('"') && entry && field) {
            append(poString(line));
        }
    }
    finish();
    const header = {};
    const first = entries[0];
    if (first && first.id === "" && !first.context) {
        for (const line of (first.strs[0] || "").split("\n")) {
            const cut = line.indexOf(":");
            if (cut > 0) {
                header[line.slice(0, cut).trim()] = line.slice(cut + 1).trim();
            }
        }
        entries.shift();
    }
    for (const e of entries) {
        e.translated = e.strs.length > 0 && e.strs.every((s) => s);
        delete e.hasStr;
    }
    return { header, entries };
}

/** Size in B / KB / MB. */
export function humanSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}
