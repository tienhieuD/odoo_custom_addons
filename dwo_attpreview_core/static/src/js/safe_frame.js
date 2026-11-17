/** @odoo-module **/
// Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
// Shared by the Mail and Text previews: the sandboxed frame that shows a document written by someone else.
//  - the frame has no network and no navigation: its only script (allowed by a random nonce) catches a click on a link
//    and tells the parent, which asks the user before opening the address in a new tab (noopener, no referrer);
//  - pictures from the internet are fetched by the Odoo server (see remote_image.py); one that cannot be shown gets a
//    visible error chip that says why, never an empty hole.
import { onMounted, onWillUnmount } from "@odoo/owl";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

export const FRAME_SANDBOX = "allow-scripts";

export function escapeHtml(text) {
    return String(text ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

function nonce() {
    const bytes = new Uint8Array(16);
    crypto.getRandomValues(bytes);
    return btoa(String.fromCharCode(...bytes)).replace(/[^A-Za-z0-9]/g, "");
}

/** What is put in a click on a link: it must not open anything by itself (the frame cannot navigate or open windows). */
const LINK_SCRIPT = `
document.addEventListener("click", function (e) {
  var a = e.target && e.target.closest ? e.target.closest("a[href]") : null;
  if (!a) return;
  var raw = a.getAttribute("href") || "";
  if (raw.charAt(0) === "#") return;
  e.preventDefault();
  parent.postMessage({ dwoLink: a.href }, "*");
}, true);
document.addEventListener("auxclick", function (e) { if (e.target && e.target.closest && e.target.closest("a[href]")) e.preventDefault(); }, true);
`;

export const ERROR_STYLE =
    ".dwo-pic-error{display:inline-block;margin:2px 0;padding:3px 9px;border:1px solid #e0a4a4;border-radius:4px;" +
    "background:#fdf0f0;color:#8a1f1f;font-size:12px;line-height:1.4}" +
    ".dwo-pic-error:before{content:'\\26A0\\00a0'}";

/**
 * The start of a frame document: charset, policy (nothing from the network, pictures as data: only, one script by
 * nonce), no referrer. Returns ``{head, tail}``: put ``head`` first in <head> and ``tail`` at the end of <body>.
 */
export function frameParts() {
    const n = nonce();
    const csp = `default-src 'none'; img-src data:; style-src 'unsafe-inline'; font-src data:; script-src 'nonce-${n}'`;
    return {
        head:
            `<meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="${csp}">` +
            `<meta name="referrer" content="no-referrer"><style>${ERROR_STYLE}</style>`,
        tail: `<script nonce="${n}">${LINK_SCRIPT}</script>`,
    };
}

/** Allowed targets of a link: web and mail addresses only. */
export function linkTarget(raw) {
    try {
        const url = new URL(String(raw));
        return ["http:", "https:", "mailto:"].includes(url.protocol) ? url : null;
    } catch {
        return null;
    }
}

/**
 * Ask the user, then open the address in a new tab. ``dialog`` and ``notification`` are the Odoo services.
 * The address is shown in full, so a lookalike host is easy to see.
 */
export function confirmOpen(dialog, notification, raw) {
    const url = linkTarget(raw);
    if (!url) {
        notification.add(_t("This kind of link cannot be opened from a preview."), { type: "warning" });
        return;
    }
    dialog.add(ConfirmationDialog, {
        title: _t("Open this link?"),
        body: _t("You are about to leave Odoo. This address will open in a new tab:\n\n%s\n\nOpen it only if you trust the sender.", url.href),
        confirmLabel: _t("Open in a new tab"),
        cancelLabel: _t("Stay here"),
        confirm: () => window.open(url.href, "_blank", "noopener,noreferrer"),
        cancel: () => {},
    });
}

/** Listen to the links clicked in the frame found by ``getFrame()`` (the <iframe> element, or null). */
export function useFrameLinks(getFrame) {
    const dialog = useService("dialog");
    const notification = useService("notification");
    const onMessage = (ev) => {
        const frame = getFrame();
        if (!frame || ev.source !== frame.contentWindow || !ev.data || typeof ev.data.dwoLink !== "string") {
            return;
        }
        confirmOpen(dialog, notification, ev.data.dwoLink);
    };
    onMounted(() => window.addEventListener("message", onMessage));
    onWillUnmount(() => window.removeEventListener("message", onMessage));
    return { open: (raw) => confirmOpen(dialog, notification, raw) };
}

/** A click on a link written in the page itself (not in the frame): ask first. */
export function onLinkClick(link, ev, url) {
    ev.preventDefault();
    link.open(url);
}

/** Why the server refused a picture, as a sentence (the reasons of remote_image.py). */
export function pictureReason(code) {
    const reasons = {
        "not a picture": _t("this address is not a picture (programs, scripts and other files are never opened)"),
        "scheme not allowed": _t("only secure https addresses are loaded"),
        "address not allowed": _t("this address points inside a private network"),
        "port not allowed": _t("this address uses an unusual port"),
        "bad address": _t("the address is not valid"),
        "host not found": _t("the host does not exist"),
        "picture too large": _t("the picture is too large"),
        "too many redirects": _t("too many redirects"),
        "network error": _t("the server could not reach it"),
        "unsupported address": _t("this kind of address is not allowed for pictures"),
    };
    return reasons[code] || (/^http \d+$/.test(code) ? _t("the website answered %s", code.slice(5)) : _t("it could not be loaded"));
}

/** The visible error that replaces a picture that cannot be shown. */
export function pictureError(code, alt) {
    const what = alt ? `“${alt}”: ` : "";
    return `<span class="dwo-pic-error">${escapeHtml(_t("Picture blocked"))} – ${escapeHtml(what)}${escapeHtml(pictureReason(code))}</span>`;
}

/**
 * Fetch pictures through the server: ``urlFor(i)`` is the route of picture ``i`` (of ``count``). Returns
 * ``{pictures: {i: data-URI}, errors: {i: code}}``; at most ``parallel`` requests at a time.
 */
export async function fetchPictures(urlFor, count, parallel = 4) {
    const pictures = {};
    const errors = {};
    const queue = [...Array(count).keys()];
    const worker = async () => {
        while (queue.length) {
            const i = queue.shift();
            try {
                const response = await fetch(urlFor(i), { credentials: "same-origin" });
                if (!response.ok) {
                    errors[i] = response.status === 422 ? (await response.text()).slice(0, 40) : "network error";
                    continue;
                }
                const blob = await response.blob();
                if (!/^image\/(png|jpeg|gif|webp)$/.test(blob.type)) {
                    errors[i] = "not a picture";
                    continue;
                }
                pictures[i] = await new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve(reader.result);
                    reader.onerror = reject;
                    reader.readAsDataURL(blob);
                });
            } catch {
                errors[i] = "network error";
            }
        }
    };
    await Promise.all(Array.from({ length: Math.min(parallel, queue.length) }, worker));
    return { pictures, errors };
}
