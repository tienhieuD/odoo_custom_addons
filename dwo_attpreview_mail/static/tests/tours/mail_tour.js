/** @odoo-module **/
// Copyright 2026 Duotek. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";
// Odoo 18: file cards in the chatter are .o-mail-AttachmentCard (19: .o-mail-AttachmentContainer)

// An .eml in the chatter: headers, attachments and a sandboxed body with no script and no network; then one
// attachment of the email opens in a second, smaller preview dialog above the first one.
registry.category("web_tour.tours").add("dwo_attpreview_mail_tour", {
    steps: () => [
        { trigger: ".o-mail-AttachmentList .o-mail-AttachmentCard", run: "click" },
        {
            content: "An email gets a medium dialog, not the wide one of sheets and documents",
            trigger: ".modal .o_dwo_ap_dialog.o_dwo_ap_w_medium",
            run() {
                const width = this.anchor.closest(".modal-dialog").getBoundingClientRect().width;
                if (width > 1100 || width < 600) {
                    throw new Error("unexpected email dialog width: " + width);
                }
            },
        },
        {
            content: "Subject shown as text, not HTML",
            trigger: ".modal .o_dwo_mail_subject",
            run() {
                if (this.anchor.textContent !== "Hi <b>there</b>" || this.anchor.querySelector("b")) {
                    throw new Error("subject not escaped: " + this.anchor.innerHTML);
                }
            },
        },
        { content: "From", trigger: ".modal .o_dwo_mail_fields td:contains('anna@example.com')" },
        {
            content: "The remote picture is loaded through the server (#79), not by the browser",
            trigger: ".modal .o_dwo_mail_proxied:not(:contains('Loading'))",
            run() {
                const doc = document.querySelector(".modal iframe.o_dwo_mail_body").getAttribute("srcdoc") || "";
                if (doc.includes("data-dwo-remote") || doc.split("data:image/png").length < 3) {
                    throw new Error("remote picture not replaced by the proxied one");
                }
            },
        },
        {
            content: "Body frame: only the link script (nonce), no same origin, no popups, CSP without network",
            trigger: ".modal iframe.o_dwo_mail_body",
            run() {
                const sandbox = this.anchor.getAttribute("sandbox") || "";
                if (sandbox.includes("allow-same-origin") || sandbox.includes("allow-popups") || sandbox.includes("allow-top-navigation")) {
                    throw new Error("unsafe sandbox: " + sandbox);
                }
                const doc = this.anchor.getAttribute("srcdoc") || "";
                if (!doc.includes("Content-Security-Policy") || !doc.includes("default-src 'none'")) {
                    throw new Error("no CSP in the body frame");
                }
                const scripts = doc.match(/<script\b[^>]*>/g) || [];
                if (scripts.length !== 1 || !/nonce="[A-Za-z0-9]{16,}"/.test(scripts[0]) || !/script-src 'nonce-/.test(doc)) {
                    throw new Error("the frame must have exactly one script, allowed by a nonce");
                }
                if (doc.includes("alert(") || doc.includes("evil.example")) {
                    throw new Error("unsafe content in the body frame");
                }
            },
        },
        { content: "Two attachments listed", trigger: ".modal .o_dwo_mail_att:nth-child(2) .o_dwo_mail_att_name:contains('Inner note.eml')" },
        { trigger: ".modal .o_dwo_mail_att_name:contains('Inner note.eml')", run: "click" },
        { content: "Second dialog above the first", trigger: ".modal:last .o_dwo_mail_subject:contains('Inner note')" },
        { content: "Its own attachment", trigger: ".modal:last .o_dwo_mail_att_name:contains('deep.txt')" },
        { trigger: ".modal:last .o_dwo_ap_close", run: "click" },
        { content: "The first dialog is still open", trigger: ".modal .o_dwo_mail_blocked" },
        { trigger: ".modal .o_dwo_ap_close", run: "click" },
    ],
});
