/** @odoo-module **/
// Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";

// The viewer lives in a sandboxed iframe with an opaque origin, so the tour cannot read its canvas: it waits for the
// component to report "ready" (the iframe tells the parent that the library has drawn the file) and checks the iframe
// really is sandboxed and served by the module.
// layout: xlsx grid, docx continuous scroll (DocxScrollViewer), pptx one slide at a time (PptxViewer)
const LAYOUT = { xlsx: "grid", docx: "scroll", pptx: "slides" };
for (const kind of ["xlsx", "docx", "pptx", "docx_long"]) {
    registry.category("web_tour.tours").add(`dwo_attpreview_office_tour_${kind}`, {
        steps: () => [
            { trigger: ".o-mail-AttachmentList .o-mail-AttachmentContainer", run: "click" },
            {
                content: "Viewer is sandboxed and served by the module",
                trigger: ".modal .o_dwo_office iframe",
                run() {
                    const sandbox = this.anchor.getAttribute("sandbox");
                    if (sandbox !== "allow-scripts") {
                        throw new Error("iframe sandbox should be exactly allow-scripts, got: " + sandbox);
                    }
                    if (!this.anchor.getAttribute("src").includes("/dwo_attpreview_office/asset/viewer/viewer.html")) {
                        throw new Error("unexpected viewer url " + this.anchor.getAttribute("src"));
                    }
                },
            },
            { content: "The library drew the file", trigger: ".modal .o_dwo_office[data-state=ready]", timeout: 60000 },
            {
                content: "Layout of the viewer",
                trigger: `.modal .o_dwo_office[data-layout=${LAYOUT[kind.split("_")[0]]}]`,
            },
            {
                content: "The viewer fills the large dialog",
                trigger: ".modal .o_dwo_office iframe",
                run() {
                    const r = this.anchor.getBoundingClientRect();
                    if (r.width < window.innerWidth * 0.85 || r.height < window.innerHeight * 0.6) {
                        throw new Error(`viewer too small: ${r.width}x${r.height}`);
                    }
                },
            },
            ...(kind === "docx_long"
                ? [{
                    content: "A long docx reports its pages (continuous scroll, several pages)",
                    trigger: ".modal .o_dwo_office[data-total]:not([data-total='0']):not([data-total='1']):not([data-total='2'])",
                    timeout: 60000,
                }]
                : []),
            { trigger: ".modal .o_dwo_ap_close", run: "click" },
        ],
    });
}

// csv/tsv (a sheet of text cells) and OpenDocument (odt/ods/odp and the templates ott/ots/otp, #84): drawn, and no
// warning banner (they are not legacy formats).
const OTHER_LAYOUT = {
    csv: "grid", tsv: "grid", csv_semicolon: "grid", csv_big: "grid",
    odt: "scroll", ods: "grid", odp: "slides", ott: "scroll", ots: "grid", otp: "slides",
};
for (const kind of Object.keys(OTHER_LAYOUT)) {
    registry.category("web_tour.tours").add(`dwo_attpreview_office_tour_${kind}`, {
        steps: () => [
            { trigger: ".o-mail-AttachmentList .o-mail-AttachmentContainer", run: "click" },
            { content: "The viewer drew the file", trigger: ".modal .o_dwo_office[data-state=ready]", timeout: 60000 },
            { content: "Layout of the viewer", trigger: `.modal .o_dwo_office[data-layout=${OTHER_LAYOUT[kind]}]` },
            {
                content: "No warning banner and no error",
                trigger: ".modal .o_dwo_ap_bar",
                run() {
                    const modal = this.anchor.closest(".modal");
                    if (modal.querySelector(".o_dwo_ap_notice") || modal.querySelector(".o_dwo_office_error")) {
                        throw new Error("unexpected banner or error");
                    }
                },
            },
            {
                content: "The viewer fills the large dialog",
                trigger: ".modal .o_dwo_office iframe",
                run() {
                    const r = this.anchor.getBoundingClientRect();
                    if (r.width < window.innerWidth * 0.85 || r.height < window.innerHeight * 0.6) {
                        throw new Error(`viewer too small: ${r.width}x${r.height}`);
                    }
                },
            },
            { trigger: ".modal .o_dwo_ap_close", run: "click" },
        ],
    });
}

// An OpenDocument file the add-on refuses (here: encrypted with a password): no banner, the short message and Download
// (the reason, e.g. "unsupported-encryption", only goes to the console).
registry.category("web_tour.tours").add("dwo_attpreview_office_tour_odf_refused", {
    steps: () => [
        { trigger: ".o-mail-AttachmentList .o-mail-AttachmentContainer", run: "click" },
        {
            content: "Short message, no technical code",
            trigger: ".modal .o_dwo_office[data-state=error] .alert .o_dwo_office_error:contains('This file cannot be previewed.')",
            timeout: 60000,
            run() {
                const text = this.anchor.closest(".alert").textContent;
                if (/unsupported|encrypt|code|ooxml|wasm|decrypt/i.test(text.replace("This file cannot be previewed.", ""))) {
                    throw new Error("technical detail shown to the user: " + text);
                }
            },
        },
        { content: "Download button", trigger: ".modal .o_dwo_office .alert a.o_dwo_office_download[href*='download=true']" },
        { content: "No warning banner", trigger: ".modal:not(:has(.o_dwo_ap_notice)) .o_dwo_ap_title:contains('locked.odt')" },
        { trigger: ".modal .o_dwo_ap_close", run: "click" },
        { trigger: "body:not(:has(.modal))" },
    ],
});

// A file the Core already refuses (damaged zip, over the size limit) opens no dialog: a toast with Download.
registry.category("web_tour.tours").add("dwo_attpreview_office_tour_error", {
    steps: () => [
        { trigger: ".o-mail-AttachmentList .o-mail-AttachmentContainer", run: "click" },
        {
            content: "Toast with the file name, the reason and a Download button",
            trigger: ".o_notification:contains('broken.docx'):contains('damaged') button:contains('Download')",
        },
        {
            content: "No dialog",
            trigger: "body",
            run() {
                if (document.querySelector(".modal")) {
                    throw new Error("a dialog is open for a damaged file");
                }
            },
        },
    ],
});

// Old binary formats (.doc, .xls, .ppt): preview with a warning banner under the title bar. Same signal as above for
// "drawn" (data-state=ready); a file the legacy add-on refuses shows a short message and Download, not the raw error.
const LEGACY_LAYOUT = { legacy_xls: "grid", legacy_ppt: "slides", legacy_doc: "scroll" };
const NOTICE = ".modal .o_dwo_ap_bar + .alert-warning.o_dwo_ap_notice:contains('Legacy format'):contains('Download it to see it in full')";
for (const kind of Object.keys(LEGACY_LAYOUT)) {
    registry.category("web_tour.tours").add(`dwo_attpreview_office_tour_${kind}`, {
        steps: () => [
            { trigger: ".o-mail-AttachmentList .o-mail-AttachmentContainer", run: "click" },
            { content: "Warning banner for the legacy format", trigger: NOTICE },
            { content: "The legacy add-on drew the file", trigger: ".modal .o_dwo_office[data-state=ready]", timeout: 60000 },
            { content: "Layout of the viewer", trigger: `.modal .o_dwo_office[data-layout=${LEGACY_LAYOUT[kind]}]` },
            {
                content: "No error, banner still there",
                trigger: ".modal",
                run() {
                    if (this.anchor.querySelector(".o_dwo_office_error")) {
                        throw new Error("a drawn legacy file shows an error");
                    }
                },
            },
            { content: "Close the banner", trigger: ".modal .o_dwo_ap_notice_close", run: "click" },
            { content: "Banner gone, viewer stays", trigger: ".modal:not(:has(.o_dwo_ap_notice)) .o_dwo_office[data-state=ready]" },
            { trigger: ".modal .o_dwo_ap_close", run: "click" },
        ],
    });
}

registry.category("web_tour.tours").add("dwo_attpreview_office_tour_legacy_refused", {
    steps: () => [
        { trigger: ".o-mail-AttachmentList .o-mail-AttachmentContainer", run: "click" },
        { content: "Warning banner, also for a file that fails", trigger: NOTICE },
        {
            content: "Short friendly message and a Download button, no technical code",
            trigger: ".modal .o_dwo_office[data-state=error] .alert .o_dwo_office_error:contains('This legacy file cannot be previewed.')",
            timeout: 60000,
            run() {
                const text = this.anchor.closest(".alert").textContent;
                if (/unsupported|content|code|ooxml|wasm|subset/i.test(text.replace("This legacy file cannot be previewed.", ""))) {
                    throw new Error("technical detail shown to the user: " + text);
                }
            },
        },
        {
            content: "Download button with the file URL",
            trigger: ".modal .o_dwo_office .alert a.o_dwo_office_download[href*='/web/content/'][href*='download=true']",
        },
        {
            content: "The dialog is intact: title bar, actions, banner",
            trigger: ".modal .o_dwo_ap_bar .o_dwo_ap_title:contains('merged.doc')",
        },
        { trigger: ".modal .o_dwo_ap_download" },
        { content: "Close works", trigger: ".modal .o_dwo_ap_close", run: "click" },
        { trigger: "body:not(:has(.modal))" },
    ],
});

// An old-format file that is not a binary Office file at all (a web page saved as .xls) is refused by the server
// before any dialog: toast with the reason and Download.
registry.category("web_tour.tours").add("dwo_attpreview_office_tour_legacy_toast", {
    steps: () => [
        { trigger: ".o-mail-AttachmentList .o-mail-AttachmentContainer", run: "click" },
        {
            content: "Toast with the file name, the reason and a Download button",
            trigger: ".o_notification:contains('fake.xls'):contains('not a valid') button:contains('Download')",
        },
        {
            content: "No dialog",
            trigger: "body",
            run() {
                if (document.querySelector(".modal")) {
                    throw new Error("a dialog is open for a fake legacy file");
                }
            },
        },
    ],
});

// csv the library cannot take (above the row/cell limits): short message and Download
registry.category("web_tour.tours").add("dwo_attpreview_office_tour_csv_huge", {
    steps: () => [
        { trigger: ".o-mail-AttachmentList .o-mail-AttachmentContainer", run: "click" },
        {
            content: "Short message and a Download button, no banner",
            trigger: ".modal .o_dwo_office[data-state=error] .o_dwo_office_error:contains('This file cannot be previewed.')",
            timeout: 60000,
        },
        { trigger: ".modal .o_dwo_office .alert a.o_dwo_office_download[href*='download=true']" },
        { trigger: ".modal:not(:has(.o_dwo_ap_notice))" },
        { trigger: ".modal .o_dwo_ap_close", run: "click" },
    ],
});

// Search in the preview. The viewer draws on canvases in a sandboxed iframe, so the tour cannot type in it: it sends
// the same messages the dialog uses (a query, a step to the next / previous match) and reads what the viewer reports
// back on the component: data-find (the viewer can search, so the magnifier is shown), data-find-total,
// data-find-index (1-based, from the library) and data-find-where (JSON: page / slide / sheet + cell of the active
// match, and the sheet / slide really shown).
const OFFICE = ".modal .o_dwo_office";
function post(anchor, data) {
    anchor.contentWindow.postMessage(Object.assign({ source: "dwo_attpreview_office_parent" }, data), "*");
}
function where(anchor) {
    return JSON.parse(anchor.closest(".o_dwo_office").dataset.findWhere || "{}");
}
/** Search `query`, wait for the result: `total` exact (a number) or at least one match (null), first one active. */
function search(query, total, timeout = 60000) {
    const count = total === null ? ":not([data-find-total='0'])" : `[data-find-total='${total}']`;
    return [
        { content: `Search "${query}"`, trigger: `${OFFICE} iframe`, run() { post(this.anchor, { type: "find", query }); } },
        {
            content: `"${query}": ${total === null ? "some" : total} match(es), the first one active`,
            trigger: `${OFFICE}${count}[data-find-index='${total === 0 ? 0 : 1}']:not([data-find-where='pending']):not([data-find-where=''])`,
            timeout,
        },
    ];
}
function step(delta, index) {
    return [
        { content: `Go to the ${delta > 0 ? "next" : "previous"} match`, trigger: `${OFFICE} iframe`, run() { post(this.anchor, { type: "find-step", delta }); } },
        { content: `Match ${index} is active`, trigger: `${OFFICE}[data-find-index='${index}']` },
    ];
}
function check(content, fn) {
    return { content, trigger: `${OFFICE}[data-find-where]`, run() { fn(where(this.anchor)); } };
}
function expect(cond, message) {
    if (!cond) {
        throw new Error(message);
    }
}
const FIND = {
    // "Region" is in the title and in the header of the first sheet
    xlsx: () => [
        ...search("REGION", 2),
        check("First match on the first sheet", (w) => expect(w.sheet === 0 && w.shownSheet === 0, "xlsx: " + JSON.stringify(w))),
        ...step(1, 2), ...step(1, 1), ...step(-1, 2),
        // "invented" is only on the second sheet ("Notes"): the viewer switches to it
        ...search("invented", 1),
        check("The viewer switched to the sheet of the match", (w) => expect(w.sheet === 1 && w.shownSheet === 1 && w.sheetName === "Notes", "xlsx sheet: " + JSON.stringify(w))),
    ],
    docx: () => [
        ...search("Nguyễn", 1),
        ...search("MIỀN", 3), ...step(1, 2), ...step(1, 3), ...step(1, 1), ...step(-1, 3),
        check("Match on page 1", (w) => expect(w.page === 0 || w.page === 1, "docx: " + JSON.stringify(w))),
    ],
    // 15 pages: the search waits for the whole layout, then the previous of the first match is the last one, far below
    docx_long: () => [
        ...search("Doan 1", 132),
        ...step(-1, 132),
        check("The last match is on a later page", (w) => expect(typeof w.page === "number" && w.page >= 5, "docx long: " + JSON.stringify(w))),
    ],
    // "thứ" is three times on slide 2 only: the viewer goes to slide 2
    pptx: () => [
        ...search("thứ", 3),
        check("The viewer moved to slide 2", (w) => expect(w.slide === 1 && w.shownSlide === 1, "pptx: " + JSON.stringify(w))),
        { content: "Slide label follows", trigger: `${OFFICE}[data-page='2']` },
        ...step(1, 2), ...step(1, 3), ...step(1, 1),
    ],
    csv: () => [...search("PATE", 1)],
    // OpenDocument (#84): same viewers, same search
    odt: () => [
        ...search("milestone", 5), ...step(1, 2), ...step(-1, 1), ...step(-1, 5),
        check("Match on the first page", (w) => expect(w.page === 0, "odt: " + JSON.stringify(w))),
    ],
    ods: () => [
        ...search("online store", 1),
        check("Cell A6 of the first sheet", (w) => expect(w.sheet === 0 && w.ref === "A6", "ods: " + JSON.stringify(w))),
        // "Finance" is only on the second sheet ("Notes"): the viewer switches to it
        ...search("finance", 1),
        // both searches find one match: wait for the result of the second one, or the check could read the first
        { content: "The result of the new search", trigger: `${OFFICE}[data-find-where*='Notes']`, timeout: 60000 },
        check("The viewer switched to the sheet of the match", (w) => expect(w.sheet === 1 && w.shownSheet === 1 && w.sheetName === "Notes", "ods sheet: " + JSON.stringify(w))),
    ],
    // "Milestone" is on slide 2 only (title and last line): the viewer goes to slide 2
    odp: () => [
        ...search("milestone", 2),
        check("The viewer moved to slide 2", (w) => expect(w.slide === 1 && w.shownSlide === 1, "odp: " + JSON.stringify(w))),
        { content: "Slide label follows", trigger: `${OFFICE}[data-page='2']` },
        ...step(1, 2), ...step(1, 1),
    ],
    tsv: () => [...search("đá", 1)],
    legacy_xls: () => [...search("2000", null)],
    legacy_ppt: () => [...search("design pattern", 2), ...step(1, 2), ...search("title", null)],
    legacy_doc: () => [...search("list", null)],
    // 100000 rows: count every row, go back from the first match to the last one (row 100001), then a single match
    // on a far row; each step must answer within the tour timeout (it took minutes before the local patch 0003)
    xlsx_big: () => [
        ...search("item", 100000),
        ...step(-1, 100000),
        check("The last match is on the last row", (w) => expect(w.ref === "B100001" && w.shownSheet === 0, "xlsx big: " + JSON.stringify(w))),
        ...search("Row 99999", 1),
        check("Found on row 100000", (w) => expect(w.ref === "A100000", "xlsx big: " + JSON.stringify(w))),
    ],
};
for (const kind of Object.keys(FIND)) {
    registry.category("web_tour.tours").add(`dwo_attpreview_office_tour_find_${kind}`, {
        steps: () => [
            { trigger: ".o-mail-AttachmentList .o-mail-AttachmentContainer", run: "click" },
            { content: "The viewer drew the file", trigger: `${OFFICE}[data-state=ready]`, timeout: 60000 },
            { content: "The viewer can search (magnifier shown)", trigger: `${OFFICE}[data-find='1']` },
            ...FIND[kind](),
            // a word that is not there: zero, nothing active
            ...search("zzqqxx", 0),
            { content: "Close the find bar", trigger: `${OFFICE} iframe`, run() { post(this.anchor, { type: "find-close" }); } },
            { content: "Cleared", trigger: `${OFFICE}[data-find-total='0'][data-find-index='0']` },
            { trigger: ".modal .o_dwo_ap_close", run: "click" },
        ],
    });
}

// An Office file in a binary field of a record (not an ir.attachment record): the Preview button of the field opens
// the same viewer, which loads the file through the fileUrl given by the Core (/web/content of the field).
const FIELD_LAYOUT = { docx: "scroll", xlsx: "grid" };
for (const kind of Object.keys(FIELD_LAYOUT)) {
    registry.category("web_tour.tours").add(`dwo_attpreview_office_field_tour_${kind}`, {
        steps: () => [
            {
                content: "Preview button of the binary field",
                trigger: ".o_field_widget[name=x_dwo_office_file] .o_dwo_ap_field_preview",
                run: "click",
            },
            {
                content: "The dialog opens on the office viewer (no toast)",
                trigger: `.modal .o_dwo_ap_title:contains('.${kind}')`,
                run() {
                    if (document.querySelector(".o_notification")) {
                        throw new Error("a toast was shown for an office file of a field");
                    }
                },
            },
            { content: "The library drew the file", trigger: ".modal .o_dwo_office[data-state=ready]", timeout: 60000 },
            { content: "Layout of the viewer", trigger: `.modal .o_dwo_office[data-layout=${FIELD_LAYOUT[kind]}]` },
            {
                content: "No error",
                trigger: ".modal .o_dwo_office",
                run() {
                    if (this.anchor.querySelector(".o_dwo_office_error")) {
                        throw new Error("the viewer shows an error");
                    }
                },
            },
            { trigger: ".modal .o_dwo_ap_close", run: "click" },
            { content: "Dialog closed", trigger: "body:not(:has(.modal))" },
        ],
    });
}
