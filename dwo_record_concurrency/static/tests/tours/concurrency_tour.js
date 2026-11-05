import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

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
    { trigger: ".o_form_view .o_field_widget[name=name] textarea", run: `edit ${value}` },
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
            trigger: ".modal .modal-title:contains('Concurrency Warning')",
        },
        { trigger: ".modal table td:contains('Edited by another user')" },
        { trigger: ".modal table td:contains('Mine')" },
        { trigger: ".modal button:contains('Cancel')", run: "click" },
        {
            content: "cancel keeps the unsaved changes",
            trigger: ".o_form_view .o_form_status_indicator_buttons:not(.invisible)",
        },
        { trigger: ".o_form_button_save", run: "click" },
        { trigger: ".modal button:contains('Force Save')", run: "click" },
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
        { trigger: ".modal button:contains('Discard My Updates')", run: "click" },
        {
            content: "my edits are dropped and the form shows the latest data of the server",
            trigger: ".o_form_view .o_field_widget[name=name] textarea:value(Edited by another user)",
        },
        { trigger: ".o_form_view:not(:has(.o_form_status_indicator_buttons:not(.invisible)))" },
    ],
});
