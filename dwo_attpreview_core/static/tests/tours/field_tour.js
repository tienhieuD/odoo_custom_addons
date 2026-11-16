/** @odoo-module **/
// Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
import { registry } from "@web/core/registry";

function closeDialog() {
    return [
        { content: "Close the preview", trigger: ".modal .o_dwo_ap_close", run: "click" },
        { content: "Dialog closed", trigger: "body:not(:has(.modal))" },
    ];
}

function openAndCheck(content, button, text, title) {
    return [
        { content, trigger: button, run: "click" },
        {
            content: `The preview shows ${title}`,
            trigger: `.modal .o_dwo_ap_dialog:has(.o_dwo_ap_title:contains('${title}')) pre:contains('${text}')`,
        },
        ...closeDialog(),
    ];
}

registry.category("web_tour.tours").add("dwo_attpreview_core_field_binary_tour", {
    steps: () => [
        {
            // Odoo 20: the field is "raw" and has no Edit button (the file name input opens the file chooser)
            content: "The Preview button stands right after the file name of the File Content field",
            trigger: ".o_field_widget[name=raw] input.o_select_file_button + button.o_dwo_ap_field_preview",
        },
        { content: "Download is still there", trigger: ".o_field_widget[name=raw] .o_download_file_button" },
        {
            content: "Watch for a click on the hidden file input",
            trigger: ".o_field_widget[name=raw] .o_select_file_button",
            run() {
                window.__dwoFileChooser = false;
                document.addEventListener(
                    "click",
                    (ev) => {
                        if (ev.target.matches && ev.target.matches("input[type=file]")) {
                            window.__dwoFileChooser = true;
                        }
                    },
                    true
                );
            },
        },
        ...openAndCheck(
            "Preview the file",
            ".o_field_widget[name=raw] .o_dwo_ap_field_preview",
            "binary tour content",
            "notes.sample"
        ),
        {
            content: "The button did not open the file chooser and the field is unchanged",
            trigger: ".o_field_widget[name=raw] input.o_input",
            run() {
                if (window.__dwoFileChooser) {
                    throw new Error("the Preview button opened the file chooser");
                }
                if (this.anchor.value !== "notes.sample") {
                    throw new Error("unexpected file name " + this.anchor.value);
                }
            },
        },
        { content: "Clear still works", trigger: ".o_field_widget[name=raw] .o_clear_file_button", run: "click" },
        {
            content: "Empty field: upload button, no Preview",
            trigger: ".o_field_widget[name=raw]:not(:has(.o_dwo_ap_field_preview)) .o_select_file_button",
        },
        { content: "Discard", trigger: ".o_form_button_cancel", run: "click" },
        { content: "The file is back", trigger: ".o_field_widget[name=raw] .o_dwo_ap_field_preview" },
    ],
});

registry.category("web_tour.tours").add("dwo_attpreview_core_field_partner_tour", {
    steps: () => [
        // binary field stored as an attachment, with a file name field
        {
            // Odoo 20: no Edit button; the eye follows the file name
            content: "Preview after the file name on a binary field of the partner",
            trigger: ".o_field_widget[name=x_dwo_file] input.o_select_file_button + button.o_dwo_ap_field_preview",
        },
        ...openAndCheck(
            "Preview the binary field",
            ".o_field_widget[name=x_dwo_file] .o_dwo_ap_field_preview",
            "contract tour content",
            "contract.sample"
        ),
        // many2many_binary
        {
            content: "many2many_binary keeps its download link and delete cross",
            trigger: ".o_field_widget[name=x_dwo_file_ids] .o_attachment:contains('report.sample'):has(a[download]):has(.o_attachment_delete)",
        },
        ...openAndCheck(
            "Preview a file of the many2many_binary field",
            ".o_field_widget[name=x_dwo_file_ids] .o_attachment:contains('report.sample') .o_dwo_ap_m2mb_preview",
            "m2m tour content",
            "report.sample"
        ),
        // list of attachments (many2many)
        {
            content: "The list of attachments keeps its remove button",
            trigger: ".o_field_widget[name=x_dwo_list_ids] .o_data_row:contains('listed.sample') .o_list_record_remove",
        },
        ...openAndCheck(
            "Preview a row of the list",
            ".o_field_widget[name=x_dwo_list_ids] .o_data_row:contains('listed.sample') .o_dwo_ap_list_preview",
            "list tour content",
            "listed.sample"
        ),
        {
            content: "A row that cannot be previewed",
            trigger: ".o_field_widget[name=x_dwo_list_ids] .o_data_row:contains('archive.xyz') .o_dwo_ap_list_preview",
            run: "click",
        },
        {
            content: "A toast with a Download button, no dialog",
            trigger: ".o_notification:contains('archive.xyz'):has(button:contains('Download'))",
            run() {
                if (document.querySelector(".modal")) {
                    throw new Error("a dialog opened");
                }
            },
        },
        // many2one to ir.attachment
        {
            content: "The many2one keeps its internal link",
            trigger: ".o_field_widget[name=x_dwo_attachment_id]:has(.o_external_button) .o_dwo_ap_m2o_preview",
        },
        ...openAndCheck(
            "Preview the many2one",
            ".o_field_widget[name=x_dwo_attachment_id] .o_dwo_ap_m2o_preview",
            "m2o tour content",
            "main.sample"
        ),
        // read-only binary: file name link + "Preview" button
        {
            content: "Read-only binary: the download link then the Preview button",
            trigger: ".o_field_widget[name=x_dwo_ro_file] a.o_form_uri:contains('archived.sample') + button.o_dwo_ap_field_preview",
        },
        ...openAndCheck(
            "Preview the read-only binary",
            ".o_field_widget[name=x_dwo_ro_file] .o_dwo_ap_field_preview",
            "readonly binary content",
            "archived.sample"
        ),
        // read-only many2one: link to the record + eye
        {
            content: "Read-only many2one: the link to the attachment then the eye",
            trigger: ".o_field_widget[name=x_dwo_ro_attachment_id] a.o_form_uri:contains('old.sample') + button.o_dwo_ap_m2o_preview",
        },
        ...openAndCheck(
            "Preview the read-only many2one",
            ".o_field_widget[name=x_dwo_ro_attachment_id] .o_dwo_ap_m2o_preview",
            "readonly m2o content",
            "old.sample"
        ),
        {
            content: "Still on the partner (the eye did not follow the link)",
            trigger: ".o_form_view .o_field_widget[name=name]:has(input), .o_form_view .o_field_widget[name=name]",
            run() {
                if (!/res\.partner/.test(window.location.pathname)) {
                    throw new Error("navigated to " + window.location.pathname);
                }
            },
        },
    ],
});

registry.category("web_tour.tours").add("dwo_attpreview_core_field_menu_list_tour", {
    steps: () => [
        {
            content: "The Attachments menu opens on the kanban: each card has a Preview eye",
            trigger: ".o_kanban_record:contains('menu list.sample') .o_dwo_ap_kanban_preview",
            run: "click",
        },
        {
            content: "The preview opens from the card",
            trigger: ".modal .o_dwo_ap_dialog pre:contains('menu list content')",
        },
        ...closeDialog(),
        {
            content: "Still on the kanban, no form opened",
            trigger: ".o_kanban_view .o_kanban_record:contains('menu list.sample')",
            run() {
                if (document.querySelector(".o_form_view")) {
                    throw new Error("a form view opened");
                }
            },
        },
        { content: "Switch to the list", trigger: ".o_switch_view.o_list", run: "click" },
        {
            content: "The Attachments list has a Preview column",
            trigger: ".o_list_view .o_data_row:contains('menu list.sample') .o_dwo_ap_list_preview",
            run: "click",
        },
        {
            content: "The preview opens",
            trigger: ".modal .o_dwo_ap_dialog pre:contains('menu list content')",
        },
        ...closeDialog(),
        {
            content: "Still on the list, no form opened",
            trigger: ".o_list_view .o_data_row:contains('menu list.sample')",
            run() {
                if (document.querySelector(".o_form_view")) {
                    throw new Error("a form view opened");
                }
            },
        },
        {
            content: "Selecting the row still works",
            trigger: ".o_data_row:contains('menu list.sample') .o_list_record_selector input",
            run: "click",
        },
        { content: "Row selected", trigger: ".o_data_row.o_data_row_selected:contains('menu list.sample')" },
    ],
});

registry.category("web_tour.tours").add("dwo_attpreview_core_field_table_tour", {
    steps: () => [
        {
            content: "Preview the certificate (a binary field stored in its table)",
            trigger: ".o_field_widget[name=smtp_ssl_certificate] .o_dwo_ap_field_preview",
            run: "click",
        },
        {
            content: "The image is shown",
            trigger: ".modal .o_dwo_ap_content img",
            async run() {
                if (!this.anchor.complete) {
                    await new Promise((resolve) => {
                        this.anchor.addEventListener("load", resolve, { once: true });
                        this.anchor.addEventListener("error", resolve, { once: true });
                    });
                }
                if (!this.anchor.naturalWidth) {
                    throw new Error("image not loaded");
                }
            },
        },
        ...closeDialog(),
    ],
});
