/** @odoo-module **/
// Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
import { Component, onWillStart, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { download } from "@web/core/network/download";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";
import { dwoAttPreviewIconUrl } from "./file_kind";

const PREVIEWABLE_MODES = ["native", "rendered"];

function downloadUrlOf(attachmentId) {
    return `/web/content/${attachmentId}?download=true`;
}

/** The sentence of the toast (and of the in-dialog message) for a file that cannot be previewed. */
export function dwoAttPreviewReason(info) {
    if (info.mode === "denied") {
        return _t("You are not allowed to see this file.");
    }
    if (info.reason === "viewer") {
        return _t("This file type can be previewed from the attachments, not yet from this field.");
    }
    if (info.mode === "error") {
        return info.error || _t("This file could not be displayed.");
    }
    return _t("No preview is available for this file type.");
}

export class AttPreviewDialog extends Component {
    static template = "dwo_attpreview_core.Dialog";
    static components = { Dialog };
    static props = {
        attachmentId: { type: Number, optional: true },
        close: Function,
        info: { type: Object, optional: true },
        ids: { type: Array, optional: true },
    };

    setup() {
        this.state = useState({
            attachmentId: this.props.attachmentId || 0,
            info: this.props.info || null,
            loading: false,
            fullscreen: false,
            noticeClosed: false,
        });
        onWillStart(async () => {
            if (!this.state.info) {
                this.state.info = await this.fetchInfo(this.state.attachmentId);
            }
        });
    }

    fetchInfo(attachmentId) {
        return rpc("/dwo_attpreview/info", { attachment_id: attachmentId });
    }

    // --- display -------------------------------------------------------
    /** Engines that render in the browser register a component in "dwo_attpreview.viewers". */
    get viewerComponent() {
        const info = this.state.info;
        if (info && info.mode === "rendered") {
            const reg = registry.category("dwo_attpreview.viewers");
            return reg.contains(info.engine) ? reg.get(info.engine) : null;
        }
        return null;
    }

    get fileName() {
        return (this.state.info && this.state.info.name) || "";
    }

    get iconUrl() {
        return dwoAttPreviewIconUrl(this.fileName, this.state.info && this.state.info.mimetype);
    }

    get downloadUrl() {
        // a binary field gives its own URL (/web/content of the field); an attachment its id
        return (this.state.info && this.state.info.download_url) || downloadUrlOf(this.state.attachmentId);
    }

    /** URL of the original file for viewers that load it in the browser (only set for a binary field). */
    get fileUrl() {
        return (this.state.info && this.state.info.file_url) || "";
    }

    /** Props of an engine viewer; ``fileUrl`` only for a binary field (see viewerTakesFileUrl). */
    get viewerProps() {
        const props = {
            content: this.state.info.content,
            attachmentId: this.state.attachmentId,
            downloadUrl: this.downloadUrl,
        };
        if (this.fileUrl) {
            props.fileUrl = this.fileUrl;
        }
        return props;
    }

    get canOpenInTab() {
        return !!(this.state.info && this.state.info.mode === "native");
    }

    /** Warning of the engine for this kind of file (a translated string from the server), shown as a banner. */
    get notice() {
        return (this.state.info && this.state.info.notice) || "";
    }

    closeNotice() {
        this.state.noticeClosed = true;
    }

    get reason() {
        return dwoAttPreviewReason(this.state.info);
    }

    get nativeKind() {
        const mime = this.state.info.mimetype || "";
        if (mime === "application/pdf") return "pdf";
        if (mime.startsWith("video/")) return "video";
        if (mime.startsWith("audio/")) return "audio";
        return "image";
    }

    onDownload() {
        download({ data: {}, url: this.downloadUrl });
    }

    onOpenInTab() {
        browser.open(this.state.info.url, "_blank");
    }

    toggleFullscreen() {
        this.state.fullscreen = !this.state.fullscreen;
    }
}

/**
 * A viewer registered in "dwo_attpreview.viewers" that loads the original file itself must declare a
 * ``fileUrl`` prop to be used for a binary field (there is no attachment id to give it then).
 */
function viewerTakesFileUrl(info) {
    if (info.mode !== "rendered") {
        return true;
    }
    const reg = registry.category("dwo_attpreview.viewers");
    if (!reg.contains(info.engine)) {
        return true; // shown by the dialog itself (html, text, image)
    }
    const props = reg.get(info.engine).props || {};
    return "fileUrl" in props;
}

/**
 * Service: this.env.services.dwo_attpreview.open(attachmentId, { ids })
 *          this.env.services.dwo_attpreview.openField({ model, resId, field, filenameField })
 * The server is asked first. A file that cannot be previewed (no engine, engine switched off, not allowed, refused
 * by the Core: too large, damaged archive...) opens no dialog: a toast says which file and why, with a Download
 * button. A failure that only the browser can see (a viewer that cannot draw the file) is shown inside the dialog.
 */
registry.category("services").add("dwo_attpreview", {
    dependencies: ["dialog", "notification"],
    start(env, { dialog, notification }) {
        function toast(attachmentId, info, name) {
            const url = (info && info.download_url) || (attachmentId && downloadUrlOf(attachmentId));
            const fileName = (info && info.name) || name || "";
            notification.add(dwoAttPreviewReason(info), {
                title: fileName || _t("Cannot preview this file"),
                type: "warning",
                className: "o_dwo_ap_toast",
                autocloseDelay: 10000,
                buttons: url
                    ? [{ name: _t("Download"), primary: true, onClick: () => download({ data: {}, url }) }]
                    : [],
            });
        }
        return {
            /**
             * @param {number} attachmentId
             * @param {{ids?: number[]}} [options] ids: accepted but unused (no Previous/Next any more)
             * @returns {Promise<boolean>} true when the dialog opened
             */
            async open(attachmentId, { ids } = {}) {
                let info;
                try {
                    info = await rpc("/dwo_attpreview/info", { attachment_id: attachmentId });
                } catch {
                    info = { mode: "error", error: _t("The preview could not be loaded.") };
                }
                if (!PREVIEWABLE_MODES.includes(info.mode)) {
                    toast(attachmentId, info);
                    return false;
                }
                dialog.add(AttPreviewDialog, { attachmentId, info, ids });
                return true;
            },
            /**
             * Preview the file of a binary field of a saved record (any model, stored as an attachment or not).
             * @param {{model: string, resId: number, field: string, filenameField?: string}} params
             * @returns {Promise<boolean>} true when the dialog opened
             */
            async openField({ model, resId, field, filenameField }) {
                let info;
                try {
                    info = await rpc("/dwo_attpreview/field_info", {
                        model,
                        res_id: resId,
                        field,
                        filename_field: filenameField || null,
                    });
                } catch {
                    info = { mode: "error", error: _t("The preview could not be loaded.") };
                }
                const attachmentId = info.attachment_id || 0;
                if (PREVIEWABLE_MODES.includes(info.mode) && !attachmentId && !viewerTakesFileUrl(info)) {
                    // the viewer of this engine only knows how to load an attachment by id
                    info = { ...info, mode: "unsupported", reason: "viewer" };
                }
                if (!PREVIEWABLE_MODES.includes(info.mode)) {
                    toast(attachmentId, info);
                    return false;
                }
                dialog.add(AttPreviewDialog, { attachmentId, info });
                return true;
            },
        };
    },
});
