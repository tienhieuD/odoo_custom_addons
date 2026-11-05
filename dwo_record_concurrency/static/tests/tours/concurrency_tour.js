/** @odoo-module **/

import { registry } from "@web/core/registry";
import { jsonrpc as rpc } from "@web/core/network/rpc_service";

async function writeOnServer(vals) {
    const [partner] = await rpc("/web/dataset/call_kw/res.partner/search_read", {
        model: "res.partner",
        method: "search_read",
        args: [[["name", "in", ["DWO Conflict Partner", "Edited by another user"]]], ["id"]],
        kwargs: {},
    });
    await rpc("/web/dataset/call_kw/res.partner/write", {
        model: "res.partner",
        method: "write",
        args: [[partner.id], vals],
        kwargs: {},
    });
}

const openAndEdit = (value) => [
    { trigger: ".o_form_view .o_field_widget[name=name] textarea" },
    // let the snapshot of the loaded record arrive before the other user writes
    { trigger: ".o_form_view", run: () => new Promise((resolve) => setTimeout(resolve, 800)) },
    { trigger: ".o_form_view .o_field_widget[name=name] textarea", run: `text ${value}` },
];

registry.category("web_tour.tours").add("dwo_concurrency_conflict", {
    steps: () => [
        ...openAndEdit("Mine"),
        {
            content: "another user saves the same field",
            trigger: ".o_form_view",
            run: () => writeOnServer({ name: "Edited by another user" }),
        },
        { trigger: ".o_form_button_save", run: "click" },
        {
            content: "the conflict dialog shows both values",
            trigger: ".modal-title:contains('Concurrency Warning')",
        },
        { trigger: "table td:contains('Edited by another user')" },
        { trigger: "table td:contains('Mine')" },
        { trigger: "button:contains('Cancel')", run: "click" },
        {
            content: "cancel keeps the unsaved changes",
            trigger: ".o_form_view .o_form_status_indicator_buttons:not(.invisible)",
        },
        { trigger: ".o_form_button_save", run: "click" },
        { trigger: "button:contains('Force Save')", run: "click" },
        {
            content: "force save overwrites and the form is clean again",
            trigger: ".o_form_view:not(:has(.o_form_status_indicator_buttons:not(.invisible)))",
        },
    ],
});

registry.category("web_tour.tours").add("dwo_concurrency_no_conflict", {
    steps: () => [
        ...openAndEdit("Mine"),
        {
            content: "another user changes an unwatched field and the name is untouched",
            trigger: ".o_form_view",
            run: () => writeOnServer({ website: "https://example.com" }),
        },
        { trigger: ".o_form_button_save", run: "click" },
        {
            content: "no dialog: the save goes through",
            trigger: ".o_form_view:not(:has(.o_form_status_indicator_buttons:not(.invisible)))",
        },
        { trigger: "body:not(:has(.modal))" },
    ],
});

registry.category("web_tour.tours").add("dwo_concurrency_discard", {
    steps: () => [
        ...openAndEdit("Mine"),
        {
            content: "another user saves the same field",
            trigger: ".o_form_view",
            run: () => writeOnServer({ name: "Edited by another user" }),
        },
        { trigger: ".o_form_button_save", run: "click" },
        { trigger: "button:contains('Discard My Updates')", run: "click" },
        {
            content: "my edits are dropped and the form shows the latest data of the server",
            trigger: ".o_form_view .o_field_widget[name=name] textarea",
            async run() {
                for (let i = 0; i < 40 && this.$anchor.val() !== "Edited by another user"; i++) {
                    await new Promise((resolve) => setTimeout(resolve, 200));
                }
                if (this.$anchor.val() !== "Edited by another user") {
                    throw new Error("the form does not show the latest data: " + this.$anchor.val());
                }
            },
        },
        { trigger: ".o_form_view:not(:has(.o_form_status_indicator_buttons:not(.invisible)))" },
    ],
});
