/** @odoo-module **/

import tour from "web_tour.tour";

async function writeOnServer(vals) {
    const call = async (method, args) => {
        const response = await fetch(`/web/dataset/call_kw/res.partner/${method}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ jsonrpc: "2.0", method: "call", params: { model: "res.partner", method, args, kwargs: {} } }),
        });
        return (await response.json()).result;
    };
    const [partner] = await call("search_read", [[["name", "in", ["DWO Conflict Partner", "Edited by another user"]]], ["id"]]);
    await call("write", [[partner.id], vals]);
}

const NAME = ".o_form_view .o_field_widget[name=name] textarea, .o_form_view .o_field_widget[name=name] input";
const noSaveButton = ".o_form_view:not(:has(.o_form_status_indicator_buttons:not(.invisible)))";

const openAndEdit = (value) => [
    { trigger: NAME },
    // let the snapshot of the loaded record arrive before the other user writes
    { trigger: ".o_form_view", run: () => new Promise((resolve) => setTimeout(resolve, 800)) },
    { trigger: NAME, run: `text ${value}` },
];

tour.register("dwo_concurrency_conflict", { test: true }, [
    ...openAndEdit("Mine"),
    { content: "another user saves the same field", trigger: ".o_form_view", run: () => writeOnServer({ name: "Edited by another user" }) },
    { trigger: ".o_form_button_save", run: "click" },
    { content: "the conflict dialog shows both values", trigger: ".modal-title:contains('Concurrency Warning')" },
    { trigger: "table td:contains('Edited by another user')" },
    { trigger: "table td:contains('Mine')" },
    { trigger: "button:contains('Cancel')", run: "click" },
    { content: "cancel keeps the unsaved changes", trigger: ".o_form_view .o_form_status_indicator_buttons:not(.invisible)" },
    { trigger: ".o_form_button_save", run: "click" },
    { trigger: "button:contains('Force Save')", run: "click" },
    { content: "force save overwrites and the form is clean again", trigger: noSaveButton },
]);

tour.register("dwo_concurrency_no_conflict", { test: true }, [
    ...openAndEdit("Mine"),
    { content: "another user changes an unwatched field and the name is untouched", trigger: ".o_form_view", run: () => writeOnServer({ website: "https://example.com" }) },
    { trigger: ".o_form_button_save", run: "click" },
    { content: "no dialog: the save goes through", trigger: noSaveButton },
    { trigger: "body:not(:has(.modal))" },
]);

tour.register("dwo_concurrency_discard", { test: true }, [
    ...openAndEdit("Mine"),
    { content: "another user saves the same field", trigger: ".o_form_view", run: () => writeOnServer({ name: "Edited by another user" }) },
    { trigger: ".o_form_button_save", run: "click" },
    { trigger: "button:contains('Discard My Updates')", run: "click" },
    {
        content: "my edits are dropped and the form shows the latest data of the server",
        trigger: NAME,
        async run() {
            for (let i = 0; i < 40 && this.$anchor.val() !== "Edited by another user"; i++) {
                await new Promise((resolve) => setTimeout(resolve, 200));
            }
            if (this.$anchor.val() !== "Edited by another user") {
                throw new Error("the form does not show the latest data: " + this.$anchor.val());
            }
        },
    },
    { trigger: noSaveButton },
]);
