/** @odoo-module **/

import tour from "web_tour.tour";

// synchronous on purpose: the tours do not wait for a promise returned by a step
function writeOnServer(vals) {
    const call = (method, args) => {
        const xhr = new XMLHttpRequest();
        xhr.open("POST", `/web/dataset/call_kw/res.partner/${method}`, false);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(JSON.stringify({ jsonrpc: "2.0", method: "call", params: { model: "res.partner", method, args, kwargs: {} } }));
        return JSON.parse(xhr.responseText).result;
    };
    const [partner] = call("search_read", [[["name", "in", ["DWO Conflict Partner", "Edited by another user"]]], ["id"]]);
    call("write", [[partner.id], vals]);
}

const NAME = ".o_form_view .o_field_widget[name=name] textarea, .o_form_view .o_field_widget[name=name] input";
const noSaveButton = ".o_form_view:not(:has(.o_form_status_indicator_buttons:not(.invisible)))";

// the snapshot of the loaded record is fetched in two round trips: wait for it before the "other user" writes
// (a promise returned by a step is not waited for, so the wait is a visible marker added after a delay)
const openAndEdit = (value) => [
    { trigger: NAME, run: () => {
        $(".dwo_wait_done").remove();
        setTimeout(() => $("body").append('<div class="dwo_wait_done" style="width:2px;height:2px;overflow:hidden">.</div>'), 2000);
    } },
    { trigger: ".dwo_wait_done" },
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
