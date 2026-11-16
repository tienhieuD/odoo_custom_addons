// Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
// Sandboxed viewer page (iframe sandbox="allow-scripts", opaque origin, CSP without network).
// The parent window sends the file bytes with postMessage; nothing is fetched from anywhere else.
// This page has an opaque origin (sandbox without allow-same-origin). Chrome refuses module Workers built from
// blob: URLs in that case, and the library only falls back to a data: URL Worker when createObjectURL throws.
// So make it throw: the library then starts its Workers from data: URLs, which work here.
URL.createObjectURL = () => {
    throw new Error("blob URLs are not used in the sandboxed viewer");
};

const parent_ = window.parent;
const stage = document.getElementById("stage");
const bar = document.getElementById("bar");
const pos = document.getElementById("pos");
const msg = document.getElementById("msg");
let viewer = null;
let kind = null;

function send(data) {
    parent_.postMessage(Object.assign({ source: "dwo_attpreview_office" }, data), "*");
}

function fail(err) {
    const text = err && err.message ? err.message : String(err);
    console.warn("[dwo_attpreview_office] cannot display the file:", (err && err.code) || "", text);
    send({ type: "error", code: (err && err.code) || "", message: text });
}

window.addEventListener("error", (e) => fail(e.error || e.message));
window.addEventListener("unhandledrejection", (e) => fail(e.reason));

// Old binary formats (Word/Excel/PowerPoint 97-2003) are read by the optional silurus legacy add-on, loaded only when
// such a file is opened (its WebAssembly parser is about 1.3 MB). maxInputBytes: the add-on has no ceiling of its own;
// the server already refused what is above the Core limit, this one is the hard stop in the browser.
const LEGACY = {
    doc: { target: "docx", module: "../lib/silurus/doc.mjs", factory: "createLegacyDoc", option: "legacyDoc" },
    xls: { target: "xlsx", module: "../lib/silurus/xls.mjs", factory: "createLegacyXls", option: "legacyXls" },
    ppt: { target: "pptx", module: "../lib/silurus/ppt.mjs", factory: "createLegacyPpt", option: "legacyPpt" },
};
const LEGACY_MAX_INPUT_BYTES = 128 * 1024 * 1024;

async function legacyOption(kind) {
    const spec = LEGACY[kind];
    const addon = await import(spec.module);
    return { [spec.option]: addon[spec.factory]({ maxInputBytes: LEGACY_MAX_INPUT_BYTES }) };
}

// OpenDocument (LibreOffice, ODF 1.3) is read by the optional silurus OpenDocument add-on into the DOCX / XLSX / PPTX
// models, so the usual viewers draw it. Loaded only when such a file is opened (WebAssembly reader of about 1.2-1.5 MB,
// started in the parser Worker). The factories take only { moduleUrl, wasmUrl }: the defaults point next to the
// module, i.e. the asset route of this module. The server sends odt/ods/odp also for the templates ott/ots/otp.
const OPENDOCUMENT = {
    odt: { target: "docx", module: "../lib/silurus/odt.mjs", factory: "createOdt", option: "odt" },
    ods: { target: "xlsx", module: "../lib/silurus/ods.mjs", factory: "createOds", option: "ods" },
    odp: { target: "pptx", module: "../lib/silurus/odp.mjs", factory: "createOdp", option: "odp" },
};

async function openDocumentOption(kind) {
    const spec = OPENDOCUMENT[kind];
    const addon = await import(spec.module);
    return { [spec.option]: addon[spec.factory]() };
}

// csv / tsv: delimited text drawn by XlsxSheetViewer (every cell stays text: no type or formula guessing).
// A larger limit than the library default (100000 rows, 250000 cells) so that a 100k-line export still opens;
// above it the library refuses and the user gets the short message and Download. UTF-8 only (BOM removed here).
const SHEET_LIMITS = { maxRows: 200000, maxCells: 1500000 };

function detectDelimiter(buffer, kind) {
    if (kind === "tsv") {
        return "\t";
    }
    // the first non-empty line, outside quotes: the most frequent of , ; tab wins (a plain comma if none occurs)
    const head = new TextDecoder("utf-8").decode(new Uint8Array(buffer, 0, Math.min(buffer.byteLength, 16384)));
    const line = head.split(/\r\n|\n|\r/).find((l) => l.trim() !== "") || "";
    const counts = { ",": 0, ";": 0, "\t": 0 };
    let quoted = false;
    for (const ch of line) {
        if (ch === '"') {
            quoted = !quoted;
        } else if (!quoted && ch in counts) {
            counts[ch]++;
        }
    }
    let best = ",";
    for (const d of [",", ";", "\t"]) {
        if (counts[d] > counts[best]) {
            best = d;
        }
    }
    return best;
}

async function openDelimited(buffer, opts, kind) {
    const { XlsxSheetViewer } = await import("../lib/silurus/xlsx.mjs");
    const bytes = new Uint8Array(buffer);
    if (bytes[0] === 0xef && bytes[1] === 0xbb && bytes[2] === 0xbf) {
        buffer = buffer.slice(3); // UTF-8 byte order mark
    }
    const delimiter = detectDelimiter(buffer, kind);
    stage.classList.add("xlsx");
    stage.style.overflow = "hidden";
    stage.innerHTML = "";
    const canvas = document.createElement("canvas");
    canvas.style.cssText = "position:absolute;inset:0;width:100%;height:100%";
    stage.append(canvas);
    viewer = new XlsxSheetViewer(canvas, Object.assign({
        onError: fail, resizable: true, showScrollbars: true, xlsxWorksheetLimits: SHEET_LIMITS,
    }, opts));
    await viewer.load(buffer, { format: "delimited-text", delimiter, encoding: "utf-8" });
}

async function openXlsx(buffer, opts) {
    const { XlsxViewer } = await import("../lib/silurus/xlsx.mjs");
    stage.classList.add("xlsx");
    stage.style.overflow = "hidden";
    stage.innerHTML = "";
    const host = document.createElement("div");
    host.style.cssText = "position:absolute;inset:0";
    stage.append(host);
    // same row/cell ceilings as csv: the library default (100000 rows) refuses a 100k-row export with its header
    // row when a sheet is parsed in full (search, scrolling to the end)
    viewer = new XlsxViewer(host, Object.assign({ onError: fail, xlsxWorksheetLimits: SHEET_LIMITS }, opts));
    await viewer.load(buffer);
}

function wireToolbar(handlers) {
    const call = (fn) => async () => {
        try {
            await fn();
        } catch (e) {
            fail(e);
        }
    };
    for (const id of Object.keys(handlers)) {
        document.getElementById(id).onclick = call(handlers[id]);
    }
}

// pptx: one slide at a time, with Previous / Next (PptxViewer draws on a canvas)
async function openSlides(buffer, opts) {
    const { PptxViewer } = await import("../lib/silurus/pptx.mjs");
    const canvas = document.createElement("canvas");
    stage.innerHTML = "";
    stage.append(canvas);
    bar.hidden = false;
    const update = () => {
        pos.textContent = `Slide ${viewer.slideIndex + 1} / ${viewer.slideCount}`;
        send({ type: "page", page: viewer.slideIndex + 1, total: viewer.slideCount, complete: true });
    };
    viewer = new PptxViewer(canvas, Object.assign({ onError: fail }, opts, { onSlideChange: () => update() }));
    await viewer.load(buffer);
    update();
    wireToolbar({
        prev: async () => { await viewer.prevSlide(); update(); },
        next: async () => { await viewer.nextSlide(); update(); },
        zin: () => viewer.zoomIn(),
        zout: () => viewer.zoomOut(),
        fit: () => viewer.fitPage(),
    });
    await viewer.fitPage();
}

// docx: continuous vertical scroll like a PDF reader (DocxScrollViewer owns the scroll host and only keeps the
// visible pages mounted, so a long document stays smooth). The container needs a bounded height: it is the stage.
async function openScroll(buffer, opts) {
    const { DocxScrollViewer } = await import("../lib/silurus/docx.mjs");
    stage.classList.add("docx");
    stage.style.overflow = "hidden";
    stage.innerHTML = "";
    const host = document.createElement("div");
    host.id = "docx-scroll";
    host.style.cssText = "position:absolute;inset:0";
    stage.append(host);
    bar.hidden = false;
    // the document scrolls: no previous/next page buttons (the "Page n / total" label stays)
    document.getElementById("prev").hidden = true;
    document.getElementById("next").hidden = true;
    const update = (top, total, complete) => {
        pos.textContent = `Page ${top + 1} / ${total}${complete ? "" : "…"}`;
        send({ type: "page", page: top + 1, total, complete });
    };
    // pages about 1000 px wide, centred (the default fits the page to the whole width: huge text in a wide dialog)
    const side = Math.max(16, Math.floor((host.clientWidth - 1000) / 2));
    viewer = new DocxScrollViewer(host, Object.assign({
        onError: fail,
        background: "#f3f4f6",
        gap: 16,
        paddingTop: 16,
        paddingLeft: side,
        paddingRight: side,
        progressiveLayout: true,
        // main thread render: Workers built from the real asset URL are refused in the opaque origin of the sandbox
        // (the library parses in a data: Worker, which works); progressive layout keeps a long document responsive
        onVisiblePageChange: update,
    }, opts));
    await viewer.load(buffer);
    update(viewer.topVisiblePage, viewer.pageCount, viewer.layoutComplete);
    wireToolbar({
        zin: () => viewer.zoomIn(),
        zout: () => viewer.zoomOut(),
        fit: () => viewer.fitWidth(),
    });
}

// Find in the document (Ctrl+F, "/" or the magnifier button): the page is drawn on canvases, so the browser's own
// find cannot see the text. The library searches the whole document (also pages, slides and sheets not shown), keeps
// every match highlighted and moves to the active one (page, slide, or sheet + cell). Case-insensitive, plain text.
// The count is the library's own (matchIndex of the active match); the search waits for the full layout of a long
// document, the count shows "…" meanwhile. A newer query or Esc makes an older pending search drop its result.
const findBox = document.getElementById("find");
const findInput = document.getElementById("find-input");
const findCount = document.getElementById("find-count");
const findOpen = document.getElementById("find-open");
let findTotal = 0;
let findIndex = 0;
let findWhere = null;
let findPending = false;
let findRun = 0;

function findSupported() {
    return !!viewer && ["findText", "findNext", "findPrev", "clearFind"].every((m) => typeof viewer[m] === "function");
}

/** Where the active match is, as plain data for the parent (tests read it): page, slide or sheet + cell. */
function describeMatch(match) {
    const loc = (match && match.location) || {};
    const where = {};
    for (const key of ["page", "slide", "sheet", "sheetName", "ref"]) {
        if (typeof loc[key] === "number" || typeof loc[key] === "string") {
            where[key] = loc[key];
        }
    }
    // the sheet / slide really shown after the move (not only where the match is)
    if (viewer && typeof viewer.sheetIndex === "number") {
        where.shownSheet = viewer.sheetIndex;
    }
    if (viewer && typeof viewer.slideIndex === "number") {
        where.shownSlide = viewer.slideIndex;
    }
    return where;
}

function showFindCount() {
    const fmt = (n) => n.toLocaleString("en-US");
    findCount.textContent = !findInput.value ? "" : findPending ? "…" : findTotal ? `${fmt(findIndex)} / ${fmt(findTotal)}` : "0 / 0";
    findCount.classList.toggle("none", !!findInput.value && !findPending && !findTotal);
    send({ type: "find", query: findInput.value, pending: findPending, total: findTotal, index: findIndex, where: findWhere });
}

function activate(match) {
    findIndex = match && typeof match.matchIndex === "number" ? match.matchIndex + 1 : 0;
    findWhere = match ? describeMatch(match) : null;
}

async function runFind() {
    const run = ++findRun;
    const query = findInput.value;
    findTotal = 0;
    findIndex = 0;
    findWhere = null;
    findPending = !!query;
    showFindCount();
    const started = performance.now();
    try {
        if (!query) {
            viewer.clearFind();
        } else {
            const matches = await viewer.findText(query, { caseSensitive: false });
            if (run !== findRun) {
                return; // a newer query or Esc came meanwhile
            }
            findTotal = matches ? matches.length : 0;
            if (findTotal) {
                const match = await viewer.findNext();
                if (run !== findRun) {
                    return;
                }
                activate(match);
            }
            console.info(`[dwo_attpreview_office] find: ${findTotal} match(es) in ${Math.round(performance.now() - started)} ms`);
        }
    } catch (e) {
        console.warn("[dwo_attpreview_office] search failed:", e && e.message ? e.message : e);
        findTotal = 0;
    }
    if (run === findRun) {
        findPending = false;
        showFindCount();
    }
}

async function stepFind(delta) {
    if (!findTotal || findPending) {
        return;
    }
    const run = findRun;
    try {
        const match = await (delta > 0 ? viewer.findNext() : viewer.findPrev());
        if (run !== findRun) {
            return;
        }
        activate(match);
    } catch (e) {
        console.warn("[dwo_attpreview_office] search failed:", e && e.message ? e.message : e);
    }
    showFindCount();
}

function openFind() {
    if (!findSupported()) {
        return;
    }
    findBox.hidden = false;
    findInput.focus();
    findInput.select();
}

function closeFind() {
    findRun++;
    clearTimeout(findTimer);
    findDirty = false;
    findBox.hidden = true;
    findInput.value = "";
    findTotal = 0;
    findIndex = 0;
    findWhere = null;
    findPending = false;
    try {
        if (findSupported()) {
            viewer.clearFind();
        }
    } catch {
        // nothing to clear
    }
    showFindCount();
}

/** After the file is drawn: show the magnifier only where the viewer can search. */
function setupFind() {
    const ok = findSupported();
    findOpen.hidden = !ok;
    return ok;
}

let findTimer = null;
let findDirty = false;
findInput.addEventListener("input", () => {
    clearTimeout(findTimer);
    findDirty = true;
    findTimer = setTimeout(() => { findDirty = false; runFind(); }, 250);
});
findInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        clearTimeout(findTimer);
        if (findDirty) {
            findDirty = false;
            runFind();
        } else {
            stepFind(e.shiftKey ? -1 : 1);
        }
    } else if (e.key === "Escape") {
        e.preventDefault();
        e.stopPropagation();
        closeFind();
    }
});
findOpen.onclick = openFind;
document.getElementById("find-next").onclick = () => stepFind(1);
document.getElementById("find-prev").onclick = () => stepFind(-1);
document.getElementById("find-close").onclick = closeFind;
document.addEventListener("keydown", (e) => {
    if (((e.ctrlKey || e.metaKey) && !e.altKey && e.key.toLowerCase() === "f") || (e.key === "/" && e.target !== findInput)) {
        if (findSupported()) {
            e.preventDefault();
            openFind();
        }
    }
});
// From the parent: Ctrl+F pressed in the Odoo dialog (outside the iframe) opens the bar; tests also send a query
// or a step (the canvas content cannot be read from outside the sandbox).
window.addEventListener("message", (e) => {
    if (e.source !== parent_ || !e.data || e.data.source !== "dwo_attpreview_office_parent") {
        return;
    }
    if (e.data.type === "find") {
        openFind();
        if (e.data.query !== undefined && findSupported()) {
            findInput.value = e.data.query;
            clearTimeout(findTimer);
            findDirty = false;
            runFind();
        }
    } else if (e.data.type === "find-step") {
        stepFind(e.data.delta < 0 ? -1 : 1);
    } else if (e.data.type === "find-close") {
        closeFind();
    }
});

async function open(data) {
    kind = data.kind;
    // No call to the outside, no hyperlink navigation. No `fonts` source is given, so no web font is requested
    // (silurus 0.90 deprecated its old Google Fonts switch: any value of it, even false, logs a warning).
    const opts = { enableHyperlinks: false };
    const addon = LEGACY[kind] || OPENDOCUMENT[kind];
    const target = addon ? addon.target : kind;
    if (LEGACY[kind]) {
        Object.assign(opts, await legacyOption(kind));
    } else if (OPENDOCUMENT[kind]) {
        Object.assign(opts, await openDocumentOption(kind));
    }
    let layout;
    if (kind === "csv" || kind === "tsv") {
        await openDelimited(data.buffer, opts, kind);
        layout = "grid";
    } else if (target === "xlsx") {
        await openXlsx(data.buffer, opts);
        layout = "grid";
    } else if (target === "docx") {
        await openScroll(data.buffer, opts);
        layout = "scroll";
    } else if (target === "pptx") {
        await openSlides(data.buffer, opts);
        layout = "slides";
    } else {
        throw new Error("Unsupported file type");
    }
    if (layout === "grid") {
        gridBar();
    }
    send({ type: "rendered", layout, find: setupFind() });
}

/** Sheets (xlsx, csv, tsv) have their own tabs and scrollbars: the bar only carries the find button. */
function gridBar() {
    for (const id of ["prev", "pos", "next", "zout", "zin", "fit"]) {
        document.getElementById(id).hidden = true;
    }
    bar.hidden = false;
}

window.addEventListener("message", async (e) => {
    if (e.source !== parent_ || !e.data || e.data.source !== "dwo_attpreview_office_parent") {
        return;
    }
    if (e.data.type === "load") {
        try {
            await open(e.data);
        } catch (err) {
            fail(err);
        }
    }
});
send({ type: "ready" });
