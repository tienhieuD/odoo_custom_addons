/** @odoo-module **/
// Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("dwo_attpreview_core_tour", {
    steps: () => [
        {
            content: "Click the attachment in the chatter",
            trigger: ".o-mail-AttachmentList .o-mail-AttachmentContainer",
            run: "click",
        },
        {
            content: "The preview dialog shows the rendered text",
            trigger: ".modal pre:contains('tour content')",
        },
        {
            content: "The dialog is almost as large as the window (95vw x 92vh)",
            trigger: ".modal .o_dwo_ap_dialog",
            run() {
                const r = this.anchor.getBoundingClientRect();
                if (r.width < window.innerWidth * 0.9 || r.height < window.innerHeight * 0.85) {
                    throw new Error(`dialog too small: ${r.width}x${r.height} in ${window.innerWidth}x${window.innerHeight}`);
                }
                if (r.width > window.innerWidth || r.height > window.innerHeight) {
                    throw new Error(`dialog larger than the window: ${r.width}x${r.height}`);
                }
            },
        },
        {
            content: "The title is the file name with the icon of its type next to it",
            trigger: ".modal .o_dwo_ap_bar:has(.o_dwo_ap_title:contains('notes.sample')) img.o_dwo_ap_icon",
            run() {
                if (!this.anchor.getAttribute("src").endsWith("/dwo_attpreview_core/static/img/dwo_attpreview_default.svg")) {
                    throw new Error("unexpected icon " + this.anchor.getAttribute("src"));
                }
                if (!this.anchor.naturalWidth) {
                    throw new Error("icon not loaded");
                }
            },
        },
        {
            content: "The engine's notice is a warning banner under the title bar",
            trigger: ".modal .o_dwo_ap_bar + .alert-warning.o_dwo_ap_notice:contains('Sample notice')",
            run() {
                if (!this.anchor.querySelector(".fa-exclamation-triangle")) {
                    throw new Error("the banner has no icon");
                }
            },
        },
        {
            content: "The banner can be closed",
            trigger: ".modal .o_dwo_ap_notice .o_dwo_ap_notice_close",
            run: "click",
        },
        { content: "Banner gone, file still shown", trigger: ".modal:not(:has(.o_dwo_ap_notice)) pre:contains('tour content')" },
        {
            content: "Toolbar: download, full screen, close",
            trigger: ".modal .o_dwo_ap_bar .o_dwo_ap_download",
        },
        {
            content: "Full screen",
            trigger: ".modal .o_dwo_ap_fullscreen",
            run: "click",
        },
        {
            content: "The dialog now fills the window",
            trigger: ".modal.o_modal_full .o_dwo_ap_dialog",
            run() {
                const r = this.anchor.getBoundingClientRect();
                if (r.width < window.innerWidth - 2 || r.height < window.innerHeight - 2) {
                    throw new Error(`not full screen: ${r.width}x${r.height}`);
                }
            },
        },
        {
            content: "Close",
            trigger: ".modal .o_dwo_ap_close",
            run: "click",
        },
        { content: "Dialog closed", trigger: "body:not(:has(.modal))" },
    ],
});

registry.category("web_tour.tours").add("dwo_attpreview_core_tour_unsupported", {
    steps: () => [
        {
            content: "Click a file nobody can preview",
            trigger: ".o-mail-AttachmentList .o-mail-AttachmentContainer:contains('data.xyz')",
            run: "click",
        },
        {
            content: "A toast names the file and the reason, with a Download button",
            trigger: ".o_notification:contains('data.xyz'):contains('No preview is available') button:contains('Download')",
        },
        {
            content: "No dialog was opened",
            trigger: "body",
            run() {
                if (document.querySelector(".modal")) {
                    throw new Error("a dialog is open for an unsupported file");
                }
            },
        },
    ],
});

registry.category("web_tour.tours").add("dwo_attpreview_core_tour_several", {
    steps: () => [
        {
            content: "Open the first file",
            trigger: ".o-mail-AttachmentList .o-mail-AttachmentContainer:contains('first.sample')",
            run: "click",
        },
        { trigger: ".modal .o_dwo_ap_title:contains('first.sample')" },
        { trigger: ".modal pre:contains('first content')" },
        { trigger: ".modal:not(:has(.o_dwo_ap_prev)):not(:has(.o_dwo_ap_next)):not(:has(.o_dwo_ap_count))" },
        { trigger: ".modal .o_dwo_ap_close", run: "click" },
        { trigger: "body:not(:has(.modal))" },
    ],
});

const OPEN_SETTINGS = [
    {
        content: "Open the Attachment Preview settings",
        trigger: ".settings_tab .tab[data-key='dwo_attpreview_core']",
        run: "click",
    },
    {
        content: "Max file size is there",
        trigger: ".o_form_view [name='dwo_attpreview_max_file_size_mb'] input",
    },
];

registry.category("web_tour.tours").add("dwo_attpreview_core_tour_engine_popup", {
    steps: () => [
        ...OPEN_SETTINGS,
        {
            content: "Nothing of the old settings is left",
            trigger: ".o_form_view",
            run() {
                const text = this.anchor.textContent;
                for (const gone of ["Render timeout", "Cache lifetime", "Cache max size", "Clear cache", "Manage engines"]) {
                    if (text.includes(gone)) {
                        throw new Error("old setting still shown: " + gone);
                    }
                }
            },
        },
        {
            content: "Office engine is installed and ticked, with its name, file types and state",
            trigger: ".o_dwo_ap_engine[data-module='dwo_attpreview_office'][data-state='installed']:has(input:checked):contains('.xlsx .docx .pptx'):contains('Installed')",
        },
        {
            content: "Mail engine is not in the addons: not ticked, state Not installed",
            trigger: ".o_dwo_ap_engine[data-module='dwo_attpreview_mail'][data-state='missing']:has(input:not(:checked)):contains('.eml .msg .oft'):contains('Not installed')",
        },
        {
            content: "Tick the engine that is not in the addons",
            trigger: ".o_dwo_ap_engine[data-module='dwo_attpreview_mail'] input",
            run: "click",
        },
        {
            content: "A popup names the engine, and its file types",
            trigger: ".modal:contains('Secure Email Preview: EML, MSG, ICS, VCF'):contains('.eml, .msg, .oft')",
        },
        {
            content: "The neutral note says what to do after getting the module",
            trigger: ".modal:contains('copy it to your addons folder, update the apps list'):contains('Odoo Online cannot install third-party apps')",
        },
        {
            content: "The store button is a plain link to the store page, in a new tab",
            trigger: ".modal a.o_dwo_ap_store_link[href='https://apps.odoo.com/apps/modules/dwo_attpreview_mail'][target='_blank']:contains('Open on Odoo Apps')",
            run() {
                if (!this.anchor.rel.includes("noopener")) {
                    throw new Error("the link has no rel=noopener");
                }
            },
        },
        {
            content: "The description is in a sandboxed frame without scripts, with a policy that blocks remote content",
            trigger: ".modal iframe.o_dwo_ap_store_desc",
            run() {
                const sandbox = this.anchor.getAttribute("sandbox");
                if (sandbox !== "") {
                    throw new Error("unexpected sandbox: " + sandbox);
                }
                const doc = this.anchor.getAttribute("srcdoc");
                if (!doc.includes("Content-Security-Policy") || !doc.includes("default-src 'none'")) {
                    throw new Error("no content security policy in the description");
                }
                if (/<script/i.test(doc) || /https?:\/\//i.test(doc.replaceAll(location.origin, ""))) {
                    throw new Error("script or remote address in the description");
                }
                if (!doc.includes("Read saved emails without leaving Odoo")) {
                    throw new Error("the description of the catalog is not shown");
                }
            },
        },
        {
            content: "Close the popup",
            trigger: ".modal .o_dwo_ap_store_close",
            run: "click",
        },
        { content: "Popup closed", trigger: "body:not(:has(.modal))" },
        {
            content: "The tick did not stay",
            trigger: ".o_dwo_ap_engine[data-module='dwo_attpreview_mail'] input:not(:checked)",
        },
        {
            content: "Discard the changes (the tour must not leave the form modified)",
            trigger: ".o_form_button_cancel",
            run: "click",
        },
        { content: "Form is clean", trigger: ".o_form_view:not(.o_form_dirty)" },
    ],
});

registry.category("web_tour.tours").add("dwo_attpreview_core_tour_engine_tick", {
    steps: () => [
        ...OPEN_SETTINGS,
        {
            content: "Engine in the addons, not installed: state Available",
            trigger: ".o_dwo_ap_engine[data-module='dwo_attpreview_mail'][data-state='available']:has(input:not(:checked)):contains('Available')",
        },
        {
            content: "Tick it",
            trigger: ".o_dwo_ap_engine[data-module='dwo_attpreview_mail'] input",
            run: "click",
        },
        {
            content: "The tick stays and no popup is shown",
            trigger: ".o_dwo_ap_engine[data-module='dwo_attpreview_mail'] input:checked",
            run() {
                if (document.querySelector(".modal")) {
                    throw new Error("a popup opened for an engine that can be installed");
                }
            },
        },
        {
            content: "Untick it again",
            trigger: ".o_dwo_ap_engine[data-module='dwo_attpreview_mail'] input:checked",
            run: "click",
        },
        { content: "Unticked", trigger: ".o_dwo_ap_engine[data-module='dwo_attpreview_mail'] input:not(:checked)" },
        {
            content: "Discard the changes (the tour must not leave the form modified)",
            trigger: ".o_form_button_cancel",
            run: "click",
        },
        { content: "Form is clean", trigger: ".o_form_view:not(.o_form_dirty)" },
    ],
});
