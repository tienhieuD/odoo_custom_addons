/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";

function key(el, name, extra = {}) {
    el.dispatchEvent(new KeyboardEvent("keydown", { key: name, code: name, bubbles: true, ...extra }));
    el.dispatchEvent(new KeyboardEvent("keyup", { key: name, code: name, bubbles: true, ...extra }));
}

function open(name) {
    return { content: `Open ${name}`, trigger: `.o-mail-AttachmentContainer[title='${name}']`, run: "click" };
}

const close = { trigger: ".modal .o_dwo_ap_close", run: "click" };
const noModal = { trigger: "body:not(:has(.modal))" };

function fewRows(selector, max) {
    return function () {
        const rows = document.querySelectorAll(selector).length;
        if (!rows || rows > max) {
            throw new Error(`${rows} rows in the page for ${selector} (expected 1..${max})`);
        }
    };
}

/** The preview frame: sandboxed without scripts nor same origin, with the CSP, and none of the payloads. */
function checkFrame(forbidden) {
    return function () {
        const frame = this.anchor;
        const sandbox = frame.getAttribute("sandbox") || "";
        if (sandbox.includes("allow-scripts") || sandbox.includes("allow-same-origin") || !frame.hasAttribute("sandbox")) {
            throw new Error(`unsafe sandbox: "${sandbox}"`);
        }
        const doc = frame.getAttribute("srcdoc") || "";
        if (!doc.includes("Content-Security-Policy") || !doc.includes("default-src 'none'")) {
            throw new Error("no CSP in the preview frame");
        }
        for (const bad of forbidden) {
            if (doc.includes(bad)) {
                throw new Error(`unsafe content in the preview frame: ${bad}`);
            }
        }
    };
}

// Markdown, HTML and SVG with script payloads: nothing runs, nothing loads from the internet; outline -> line in Raw
registry.category("web_tour.tours").add("dwo_attpreview_text_safety_tour", {
    steps: () => [
        open("README.md"),
        {
            content: "Markdown preview in a sandboxed frame",
            trigger: ".modal .o_dwo_txt[data-format=markdown][data-mode=preview] iframe.o_dwo_txt_frame",
            run: checkFrame(["<script", 'href="javascript', "<img src=\"x\"", "<img src=x", 'src="https://evil']),
        },
        { content: "The remote picture is not loaded", trigger: ".modal .o_dwo_txt_blocked:contains('1 picture')" },
        { trigger: ".modal .o_dwo_txt_view[data-view=structure]", run: "click" },
        { content: "Outline of the headings", trigger: ".modal .o_dwo_tree_row:contains('Part B')" },
        { trigger: ".modal .o_dwo_tree_row:contains('Part A')", run: "click" },
        { content: "A heading opens its line in Raw", trigger: ".modal .o_dwo_txt[data-mode=raw] .o_dwo_line_active:contains('## Part A')" },
        { content: "Syntax colours in Raw", trigger: ".modal .o_dwo_line .hljs-section:contains('Part A')" },
        { content: "The raw text shows the payload as text", trigger: ".modal .o_dwo_line:contains('<script>')" },
        close,
        noModal,
        open("page.html"),
        {
            content: "HTML preview: sanitized, in a sandboxed frame",
            trigger: ".modal .o_dwo_txt[data-format=html] iframe.o_dwo_txt_frame",
            run: checkFrame(["<script", "onclick", 'src="https://evil', "dwoPwned"]),
        },
        { trigger: ".modal .o_dwo_txt_blocked:contains('1 picture')" },
        { trigger: ".modal .o_dwo_txt_view[data-view=structure]", run: "click" },
        { content: "Elements of the page", trigger: ".modal .o_dwo_tree_row:contains('body')" },
        close,
        noModal,
        open("logo.svg"),
        {
            content: "SVG shown as a picture: <img>, never inline markup",
            trigger: ".modal .o_dwo_txt_svg img[src^='data:image/svg+xml']",
            run() {
                if (document.querySelector(".modal svg circle, .modal .o_dwo_txt_svg svg")) {
                    throw new Error("the SVG is in the page as markup");
                }
            },
        },
        { trigger: ".modal .o_dwo_txt_view[data-view=structure]", run: "click" },
        { content: "XML tree of the SVG (server, safe parser)", trigger: ".modal .o_dwo_tree_row:contains('circle')" },
        close,
        {
            content: "No payload ran",
            trigger: "body:not(:has(.modal))",
            run() {
                if (window.dwoPwned) {
                    throw new Error("a script of a file ran");
                }
            },
        },
    ],
});

// About 120 000 values: only the visible rows are drawn, End reaches the last one, the filter finds a deep value
registry.category("web_tour.tours").add("dwo_attpreview_text_json_tour", {
    steps: () => [
        open("orders.json"),
        { content: "Tree first", trigger: ".modal .o_dwo_txt[data-mode=structure] .o_dwo_tree_row:contains('orders')", run: "click" },
        {
            content: "24 001 items, only the visible rows in the page",
            trigger: ".modal .o_dwo_tree_row:contains('[0]')",
            run: fewRows(".modal .o_dwo_tree_row", 150),
        },
        // Odoo 20: wait until the viewer has seen the focus on the root (path shown) before pressing End: pressed during
        // the render that follows the click, the key could be lost (flaky on 20.0, passed by timing on 19.0)
        { trigger: ".modal .o_dwo_txt_path_text:contains('$.orders')" },
        {
            trigger: ".modal .o_dwo_tree_row.o_dwo_tree_focused:contains('orders')",
            run() {
                key(this.anchor, "End");
            },
        },
        { content: "The last item is drawn and focused", trigger: ".modal .o_dwo_tree_row.o_dwo_tree_focused:contains('[24000]')" },
        { content: "Path of the focused value", trigger: ".modal .o_dwo_txt_path_text:contains('$.orders[24000]')" },
        { trigger: ".modal .o_dwo_txt_tree_filter", run: "edit needle-42" },
        { trigger: ".modal .o_dwo_txt_tree_matches:contains('1 found')" },
        { content: "Found deep in the list", trigger: ".modal .o_dwo_tree_row:contains('needle-42')" },
        { trigger: ".modal .o_dwo_txt_view[data-view=raw]", run: "click" },
        {
            content: "Raw: virtual lines",
            trigger: ".modal .o_dwo_txt[data-mode=raw] .o_dwo_line",
            run: fewRows(".modal .o_dwo_line", 200),
        },
        {
            content: "Go to line 50000",
            trigger: ".modal .o_dwo_txt_goto",
            run() {
                this.anchor.value = "50000";
                key(this.anchor, "Enter");
            },
        },
        { trigger: ".modal .o_dwo_line.o_dwo_line_active .o_dwo_line_num:contains('50000')" },
        close,
    ],
});

// A log of 200 000 lines: levels, filter by level, find (Ctrl+F), wrap, go to line
registry.category("web_tour.tours").add("dwo_attpreview_text_log_tour", {
    steps: () => [
        open("server.log"),
        { content: "Levels counted", trigger: ".modal .o_dwo_txt_level[data-level=error]:contains('4,000')" },
        { trigger: ".modal .o_dwo_txt_log_shown:contains('200,000 lines shown')" },
        {
            // Odoo 20: the rows are drawn after the virtual list is measured, a step later than the counter
            content: "200 000 lines, only the visible ones in the page",
            trigger: ".modal .o_dwo_line.o_dwo_lv_error",
            run: fewRows(".modal .o_dwo_line", 200),
        },
        { content: "Hide the INFO lines", trigger: ".modal .o_dwo_txt_level[data-level=info]", run: "click" },
        { trigger: ".modal .o_dwo_txt_log_shown:contains('20,000 lines shown')" },
        {
            content: "Ctrl+F opens the find bar",
            trigger: ".modal .o_dwo_txt_log_shown",
            run() {
                key(document.body, "f", { ctrlKey: true });
            },
        },
        { trigger: ".modal .o_dwo_txt_find_input", run: "edit message 199950" },
        { trigger: ".modal .o_dwo_txt_matches:contains('1 / 1')" },
        { content: "The match is drawn", trigger: ".modal .o_dwo_line mark.o_dwo_txt_mark_current:contains('message 199950')" },
        { trigger: ".modal .o_dwo_txt_view[data-view=raw]", run: "click" },
        { trigger: ".modal .o_dwo_txt_wrap", run: "click" },
        {
            content: "Wrapped lines stay virtual",
            trigger: ".modal .o_dwo_lines_wrap .o_dwo_line",
            run: fewRows(".modal .o_dwo_line", 200),
        },
        {
            trigger: ".modal .o_dwo_txt_goto",
            run() {
                this.anchor.value = "150000";
                key(this.anchor, "Enter");
            },
        },
        { trigger: ".modal .o_dwo_line.o_dwo_line_active:contains('message 149999')" },
        close,
    ],
});

// diff side by side, PO entries, subtitles, YAML tree, UTF-16 text
registry.category("web_tour.tours").add("dwo_attpreview_text_formats_tour", {
    steps: () => [
        open("fix.patch"),
        { content: "Removed line on the left", trigger: ".modal .o_dwo_diff_del:contains('y = 2')" },
        { content: "Added line on the right", trigger: ".modal .o_dwo_diff_add:contains('y = 3')" },
        { trigger: ".modal .o_dwo_txt_view[data-view=structure]", run: "click" },
        { content: "Files changed", trigger: ".modal .o_dwo_tree_row:contains('a.py'):contains('+1')" },
        close,
        noModal,
        open("fr.po"),
        { trigger: ".modal .o_dwo_po_filter[data-filter=missing]:contains('1')", run: "click" },
        { content: "Only the untranslated entry", trigger: ".modal .o_dwo_line:contains('Bye')" },
        { trigger: ".modal .o_dwo_lines:not(:has(.o_dwo_line:contains('Bonjour')))" },
        close,
        noModal,
        open("talk.srt"),
        { trigger: ".modal .o_dwo_txt_sub:contains('2 cues')" },
        { trigger: ".modal .o_dwo_line:contains('00:00:03.000'):contains('Bye')" },
        close,
        noModal,
        open("conf.yaml"),
        { trigger: ".modal .o_dwo_tree_row:contains('server')", run: "click" },
        { trigger: ".modal .o_dwo_tree_row:contains('port'):contains('8069')" },
        close,
        noModal,
        open("export.txt"),
        { content: "UTF-16 detected", trigger: ".modal .o_dwo_txt_info:contains('UTF-16 LE')" },
        { trigger: ".modal .o_dwo_line:contains('Köln office')" },
        close,
    ],
});
