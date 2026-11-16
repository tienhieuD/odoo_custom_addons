/** @odoo-module **/
// Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onMounted, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { download } from "@web/core/network/download";
import { _t } from "@web/core/l10n/translation";
import { dwoAttPreviewIconUrl } from "@dwo_attpreview_core/js/file_kind";

const { DateTime } = luxon;

// The body is shown in a frame with no script and no network: only pictures already inside the email (data: URIs)
// and inline styles. Links open in a new tab, without referrer, when the user clicks them.
const FRAME_CSP = "default-src 'none'; img-src data:; style-src 'unsafe-inline'; font-src data:";
const FRAME_STYLE =
    "body{margin:16px 20px;font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:14px;" +
    "line-height:1.45;color:#1f2937;background:#fff;overflow-wrap:anywhere}img{max-width:100%;height:auto}" +
    "pre{white-space:pre-wrap;font-family:inherit;margin:0}table{max-width:100%}";

const REMOTE_IMG = /<img data-dwo-remote="(\d+)" hidden/g;
const MAX_PARALLEL = 4;

function escapeHtml(text) {
    return String(text || "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

export function dwoMailSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

/**
 * Viewer of the "mail" engine: an email (headers, attachments, body in a sandboxed frame), a calendar
 * invitation or contact cards. Each attachment of an email opens in its own, smaller preview dialog with the
 * engines installed (service dwo_attpreview.openPart), or is downloaded.
 */
export class MailViewer extends Component {
    static template = "dwo_attpreview_mail.MailViewer";
    static props = {
        content: String,
        attachmentId: { type: Number, optional: true },
        downloadUrl: { type: String, optional: true },
        fileUrl: { type: String, optional: true },
        source: { type: Object, optional: true },
    };

    setup() {
        this.preview = useService("dwo_attpreview");
        try {
            this.data = JSON.parse(this.props.content || "{}") || {};
        } catch {
            this.data = {};
        }
        // remote pictures of the body (#79): loaded through the Odoo server, never by the browser from outside
        // Odoo 17: rpc is a service (useService("rpc")), there is no @web/core/network/rpc function
        this.rpc = useService("rpc");
        this.remote = useState({ status: "idle", pictures: {}, failed: 0 });
        onMounted(() => this.startRemote());
    }

    get remoteCount() {
        return this.data.remote_images || 0;
    }

    async startRemote() {
        if (!this.remoteCount || !this.props.source) {
            return;
        }
        let settings = { auto: false };
        try {
            settings = await this.rpc("/dwo_attpreview_mail/remote_settings", {});
        } catch {
            // keep them blocked
        }
        if (settings.auto) {
            this.loadRemote();
        } else {
            this.remote.status = "blocked";
        }
    }

    remoteUrl(index) {
        const params = new URLSearchParams();
        for (const [key, value] of Object.entries(this.props.source || {})) {
            if (value) {
                params.set(key, value);
            }
        }
        params.set("index", String(index));
        return `/dwo_attpreview_mail/remote_image?${params.toString()}`;
    }

    async loadRemote() {
        this.remote.status = "loading";
        const pictures = {};
        let failed = 0;
        const queue = [...Array(this.remoteCount).keys()];
        const worker = async () => {
            while (queue.length) {
                const index = queue.shift();
                try {
                    const response = await fetch(this.remoteUrl(index), { credentials: "same-origin" });
                    if (!response.ok) {
                        throw new Error(String(response.status));
                    }
                    const blob = await response.blob();
                    pictures[index] = await new Promise((resolve, reject) => {
                        const reader = new FileReader();
                        reader.onload = () => resolve(reader.result);
                        reader.onerror = reject;
                        reader.readAsDataURL(blob);
                    });
                } catch {
                    failed++;
                }
            }
        };
        await Promise.all(Array.from({ length: Math.min(MAX_PARALLEL, queue.length) }, worker));
        // one update of the frame, when every picture is there
        this.remote.pictures = pictures;
        this.remote.failed = failed;
        this.remote.status = "loaded";
    }

    get isEmail() {
        return this.data.kind === "email";
    }

    get fields() {
        const d = this.data;
        return [
            [_t("From"), d.from],
            [_t("To"), d.to],
            [_t("Cc"), d.cc],
            [_t("Bcc"), d.bcc],
            [_t("Reply to"), d.reply_to],
            [_t("Date"), this.formatDate(d.date)],
        ].filter(([, value]) => value);
    }

    formatDate(value) {
        if (!value) {
            return "";
        }
        const date = DateTime.fromISO(value);
        return date.isValid ? date.toLocaleString(DateTime.DATETIME_MED_WITH_WEEKDAY) : value;
    }

    get attachments() {
        return this.data.attachments || [];
    }

    get srcdoc() {
        const pictures = this.remote.pictures;
        const body = (this.data.body_html || `<pre>${escapeHtml(this.data.body_text)}</pre>`).replace(
            REMOTE_IMG,
            (match, index) => (pictures[index] ? `<img src="${pictures[index]}"` : match)
        );
        return (
            `<!DOCTYPE html><html><head><meta charset="utf-8">` +
            `<meta http-equiv="Content-Security-Policy" content="${FRAME_CSP}">` +
            `<meta name="referrer" content="no-referrer"><base target="_blank">` +
            `<style>${FRAME_STYLE}</style></head><body>${body}</body></html>`
        );
    }

    // --- attachments ------------------------------------------------------
    /** The outer file (without the path of this file when it is itself inside another file). */
    get baseSource() {
        const { path, ...base } = this.props.source || {};
        return base;
    }

    childPath(att) {
        const path = this.props.source && this.props.source.path;
        return path ? `${path}/${att.index}` : `${att.index}`;
    }

    get canOpenParts() {
        return !!this.props.source;
    }

    iconOf(att) {
        return dwoAttPreviewIconUrl(att.name, att.mimetype);
    }

    sizeOf(att) {
        return dwoMailSize(att.size || 0);
    }

    onPreview(att) {
        if (this.canOpenParts) {
            this.preview.openPart(this.baseSource, this.childPath(att));
        }
    }

    onDownload(att) {
        if (this.canOpenParts) {
            download({ data: {}, url: this.preview.partUrl(this.baseSource, this.childPath(att)) });
        }
    }

    // --- calendar ---------------------------------------------------------
    methodLabel(method) {
        return { REQUEST: _t("Invitation"), CANCEL: _t("Cancelled"), REPLY: _t("Reply"), PUBLISH: _t("Event") }[method] || "";
    }

    statusLabel(status) {
        return {
            ACCEPTED: _t("Accepted"),
            DECLINED: _t("Declined"),
            TENTATIVE: _t("Tentative"),
            "NEEDS-ACTION": _t("No answer yet"),
            CANCELLED: _t("Cancelled"),
            CONFIRMED: _t("Confirmed"),
        }[status] || "";
    }

    isWebLink(url) {
        return /^https?:\/\//i.test(url || "");
    }
}

registry.category("dwo_attpreview.viewers").add("mail", MailViewer);
