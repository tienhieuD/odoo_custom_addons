/** @odoo-module **/
// Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { download } from "@web/core/network/download";
import { _t } from "@web/core/l10n/translation";
import { dwoAttPreviewIconUrl } from "@dwo_attpreview_core/js/file_kind";
import {
    FRAME_SANDBOX, escapeHtml, fetchPictures, frameParts, onLinkClick, pictureError, useFrameLinks,
} from "@dwo_attpreview_core/js/safe_frame";

const { DateTime } = luxon;

// The body is shown in a frame with no network: only pictures already inside the email (data: URIs), pictures the
// server fetched for the user, and inline styles. A click on a link asks the user first (safe_frame.js).
const FRAME_STYLE =
    "body{margin:16px 20px;font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:14px;" +
    "line-height:1.45;color:#1f2937;background:#fff;overflow-wrap:anywhere}img{max-width:100%;height:auto}" +
    "pre{white-space:pre-wrap;font-family:inherit;margin:0}table{max-width:100%}";

const REMOTE_IMG = /<img data-dwo-remote="(\d+)" hidden([^>]*)>/g;
const BAD_IMG = /<img data-dwo-bad="([^"]*)" hidden([^>]*)>/g;
const altOf = (rest) => {
    const m = /\salt="([^"]*)"/.exec(rest || "");
    return m ? m[1] : "";
};

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
        this.remote = useState({ status: "idle", pictures: {}, errors: {}, failed: 0 });
        this.frameRef = useRef("frame");
        this.links = useFrameLinks(() => this.frameRef.el);
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
            settings = await rpc("/dwo_attpreview_mail/remote_settings", {});
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
        const { pictures, errors } = await fetchPictures((i) => this.remoteUrl(i), this.remoteCount);
        // one update of the frame, when every picture is there
        this.remote.pictures = pictures;
        this.remote.errors = errors;
        this.remote.failed = Object.keys(errors).length;
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
        // made again only when the pictures change: a new document (new nonce) would reload the frame
        if (!this._srcdoc || this._srcdocKey !== this.remote.status) {
            this._srcdocKey = this.remote.status;
            this._srcdoc = this.buildSrcdoc();
        }
        return this._srcdoc;
    }

    buildSrcdoc() {
        const { pictures, errors } = this.remote;
        const body = (this.data.body_html || `<pre>${escapeHtml(this.data.body_text)}</pre>`)
            .replace(REMOTE_IMG, (match, index, rest) => {
                if (pictures[index]) {
                    return `<img src="${pictures[index]}"${rest}>`;
                }
                return errors[index] ? pictureError(errors[index], altOf(rest)) : match;
            })
            .replace(BAD_IMG, (match, code, rest) => pictureError(code, altOf(rest)));
        const { head, tail } = frameParts();
        return `<!DOCTYPE html><html><head>${head}<style>${FRAME_STYLE}</style></head><body>${body}${tail}</body></html>`;
    }

    get frameSandbox() {
        return FRAME_SANDBOX;
    }

    openLink(ev, url) {
        onLinkClick(this.links, ev, url);
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
