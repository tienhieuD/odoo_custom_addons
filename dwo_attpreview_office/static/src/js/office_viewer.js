/** @odoo-module **/
// Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

// Old binary formats: opened with limited support; a failure shows a short message and a Download button
const LEGACY_KINDS = ["doc", "xls", "ppt"];
const TEXT_KINDS = ["csv", "tsv"];
const LEGACY_LOAD_TIMEOUT_MS = 90000;
const VIEWER_URL = "/dwo_attpreview_office/asset/viewer/viewer.html";

/**
 * xlsx / docx / pptx viewer. The page of the viewer (silurus, canvas) runs in a sandboxed iframe without
 * allow-same-origin: it cannot read the Odoo session nor the DOM of Odoo. This component fetches the file with
 * the user's session (access checked on the server) and hands the bytes to the iframe with postMessage: an
 * attachment through /dwo_attpreview_office/file/<id>, a binary field of a record through ``fileUrl``.
 */
export class OfficeViewer extends Component {
    static template = "dwo_attpreview_office.OfficeViewer";
    // fileUrl: set by the Core for a binary field of a record (no attachment id then); /web/content of the field,
    // which checks the read access again. The Core already validated the file (engine chosen by the file name of
    // the field, size limit, sane zip) before opening the dialog.
    static props = {
        content: String,
        attachmentId: Number,
        downloadUrl: { type: String, optional: true },
        fileUrl: { type: String, optional: true },
        "*": true,
    };

    setup() {
        this.frame = useRef("frame");
        this.state = useState({ loading: true, error: "", layout: "", page: 0, total: 0, findOk: false, findTotal: 0, findIndex: 0, findWhere: "" });
        this.viewerUrl = VIEWER_URL;
        this.onMessage = this.onMessage.bind(this);
        this.onKeydown = this.onKeydown.bind(this);
        onMounted(() => {
            window.addEventListener("message", this.onMessage);
            document.addEventListener("keydown", this.onKeydown);
            if (this.isShortError) {
                // a legacy/text parser that never answers must not leave the dialog loading forever
                this.timer = setTimeout(() => {
                    if (this.state.loading) {
                        this.fail("The viewer did not answer in time.");
                    }
                }, LEGACY_LOAD_TIMEOUT_MS);
            }
        });
        onWillUnmount(() => {
            window.removeEventListener("message", this.onMessage);
            document.removeEventListener("keydown", this.onKeydown);
            clearTimeout(this.timer);
        });
    }

    get isLegacy() {
        return LEGACY_KINDS.includes(this.props.content);
    }

    get isText() {
        return TEXT_KINDS.includes(this.props.content);
    }

    /** Legacy and delimited-text files: a short message, the reason stays in the console. */
    get isShortError() {
        return this.isLegacy || this.isText;
    }

    /** The technical detail only goes to the console; a legacy file just gets a short message and Download. */
    fail(message, code = "") {
        console.warn("[dwo_attpreview_office] cannot display the file:", code, message);
        clearTimeout(this.timer);
        this.state.loading = false;
        this.state.error = message || code || "error";
    }

    /**
     * Ctrl+F while the focus is in the dialog but outside the iframe: open the search bar of the viewer. Only when the
     * viewer can search; elsewhere (other dialogs, the rest of Odoo) the key keeps its usual meaning.
     */
    onKeydown(ev) {
        const frame = this.frame.el;
        if (!frame || this.state.loading || this.state.error || !this.state.findOk || !frame.isConnected) {
            return;
        }
        if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === "f" && frame.closest(".modal")?.contains(ev.target)) {
            ev.preventDefault();
            frame.focus();
            frame.contentWindow.postMessage({ source: "dwo_attpreview_office_parent", type: "find" }, "*");
        }
    }

    async onMessage(ev) {
        const frame = this.frame.el;
        if (!frame || ev.source !== frame.contentWindow || !ev.data || ev.data.source !== "dwo_attpreview_office") {
            return;
        }
        const data = ev.data;
        if (data.type === "ready") {
            await this.sendFile();
        } else if (data.type === "rendered") {
            clearTimeout(this.timer);
            this.state.loading = false;
            this.state.layout = data.layout || "";
            this.state.findOk = !!data.find;
        } else if (data.type === "page") {
            this.state.page = data.page;
            this.state.total = data.total;
        } else if (data.type === "find") {
            this.state.findTotal = data.total || 0;
            this.state.findIndex = data.index || 0;
            // where the active match is (page, slide, sheet + cell) and what is shown: for tests
            this.state.findWhere = data.pending ? "pending" : JSON.stringify(data.where || {});
        } else if (data.type === "error") {
            this.fail(data.message || "", data.code || "");
        }
    }

    async sendFile() {
        try {
            const url = this.props.fileUrl || `/dwo_attpreview_office/file/${this.props.attachmentId}`;
            if (!url.startsWith("/") || url.startsWith("//")) {
                // only a path of this server, never another site
                throw new Error("unexpected file URL");
            }
            const response = await fetch(url, {
                credentials: "same-origin",
            });
            if (!response.ok) {
                throw new Error(await response.text());
            }
            const buffer = await response.arrayBuffer();
            this.frame.el.contentWindow.postMessage(
                { source: "dwo_attpreview_office_parent", type: "load", kind: this.props.content, buffer },
                "*",
                [buffer]
            );
        } catch (e) {
            this.fail(String((e && e.message) || e));
        }
    }
}

registry.category("dwo_attpreview.viewers").add("office", OfficeViewer);
