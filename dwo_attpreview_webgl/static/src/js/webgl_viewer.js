/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";

const LOAD_TIMEOUT_MS = 120000;

/**
 * Base of the viewers drawn by a sandboxed WebGL page (3D models, CAD drawings, BIM). The page runs in an iframe
 * without allow-same-origin: it cannot read the Odoo session nor the DOM of Odoo. This component fetches the file
 * with the user's session (access checked on the server) and hands the bytes to the iframe with postMessage.
 * A viewer module extends it and sets ``config``: ``viewerUrl`` (the page), ``source`` (the name in the messages)
 * and ``fileUrl(attachmentId)`` (its file route).
 */
export class DwoWebglViewer extends Component {
    static template = "dwo_attpreview_webgl.Viewer";
    static config = { viewerUrl: "", source: "", fileUrl: () => "" };
    static props = {
        content: String,
        attachmentId: { type: Number, optional: true },
        downloadUrl: { type: String, optional: true },
        fileUrl: { type: String, optional: true },
        "*": true,
    };

    setup() {
        this.frame = useRef("frame");
        this.state = useState({ loading: true, error: "", stats: "" });
        this.config = this.constructor.config;
        this.onMessage = this.onMessage.bind(this);
        onMounted(() => {
            window.addEventListener("message", this.onMessage);
            this.timer = setTimeout(() => this.state.loading && this.fail("The viewer did not answer in time."), LOAD_TIMEOUT_MS);
        });
        onWillUnmount(() => {
            window.removeEventListener("message", this.onMessage);
            clearTimeout(this.timer);
        });
    }

    fail(message) {
        console.warn("[%s] cannot display the file:", this.config.source, message);
        clearTimeout(this.timer);
        this.state.loading = false;
        this.state.error = message || "error";
    }

    async onMessage(ev) {
        const frame = this.frame.el;
        if (!frame || ev.source !== frame.contentWindow || !ev.data || ev.data.source !== this.config.source) {
            return;
        }
        const data = ev.data;
        if (data.type === "ready") {
            await this.sendFile();
        } else if (data.type === "rendered") {
            clearTimeout(this.timer);
            this.state.loading = false;
            this.state.stats = JSON.stringify(data.stats || {});
        } else if (data.type === "error") {
            this.fail(data.message || "");
        }
    }

    async sendFile() {
        try {
            const url = this.props.fileUrl || this.config.fileUrl(this.props.attachmentId);
            if (!url.startsWith("/") || url.startsWith("//")) {
                throw new Error("unexpected file URL"); // only a path of this server, never another site
            }
            const response = await fetch(url, { credentials: "same-origin" });
            if (!response.ok) {
                throw new Error(await response.text());
            }
            const buffer = await response.arrayBuffer();
            this.frame.el.contentWindow.postMessage(
                { source: this.config.source + "_parent", type: "load", kind: this.props.content, buffer },
                "*",
                [buffer]
            );
        } catch (e) {
            this.fail(String((e && e.message) || e));
        }
    }
}
