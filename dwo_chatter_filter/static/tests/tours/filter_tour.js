/* @odoo-module */

import { registry } from "@web/core/registry";

const NAMES = {
    all: "All", discussion: "Discussions", email: "Emails", activity: "Activities",
    note: "Notes", tracking: "Tracking", other: "Other",
};
const badge = (kind) => `.o-dwo-messageFilter .o-dwo-filterBadge[data-chip-name='${NAMES[kind]}']`;
// the colour of a chip is a CSS variable set on the chip
const colored = (hex) => `[style*='--dwo-chip: ${hex}']`;
const showing = (text) => `.o-mail-Thread .o-mail-Message:contains('${text}')`;
const hidden = (text) => `.o-mail-Thread:not(:has(.o-mail-Message:contains('${text}')))`;

/**
 * Odoo shows the body of an email message in a shadow DOM: :contains() cannot see into it.
 */
const emailTexts = () =>
    [...document.querySelectorAll(".o-mail-Thread .o-mail-Message div")]
        .filter((host) => host.shadowRoot)
        .map((host) => host.shadowRoot.textContent || "");
const emailShown = (text) => ({
    trigger: ".o-mail-Thread",
    async run() {
        for (let i = 0; i < 50; i++) {
            if (emailTexts().some((t) => t.includes(text))) {
                return;
            }
            await new Promise((resolve) => setTimeout(resolve, 100));
        }
        throw new Error(`The email "${text}" is not shown`);
    },
});
const emailHidden = (text) => ({
    trigger: ".o-mail-Thread",
    run() {
        if (emailTexts().some((t) => t.includes(text))) {
            throw new Error(`The email "${text}" is shown but it should not`);
        }
    },
});

registry.category("web_tour.tours").add("dwo_chatter_filter", {
    test: true,
    steps: () => [
        { trigger: ".o-mail-Chatter", run: () => {} },
        // the place: under the planned activities and above the messages
        { trigger: ".o-mail-ActivityList", run: () => {} },
        // in this version the Thread may sit in a wrapper
        { trigger: ".o-dwo-messageFilter ~ :is(.o-mail-Thread, :has(.o-mail-Thread))", run: () => {} },
        { trigger: ".o-mail-ActivityList + .o-dwo-messageFilter", run: () => {} },
        // a label, then the badges, each with its own colour (outlined while off)
        { trigger: ".o-dwo-messageFilter .o-dwo-filterLabel:contains('Filter by:')", run: () => {} },
        { trigger: `${badge("discussion")}${colored("#71639e")}`, run: () => {} },
        { trigger: `${badge("email")}${colored("#17a2b8")}`, run: () => {} },
        { trigger: `${badge("activity")}${colored("#6f42c1")}`, run: () => {} },
        { trigger: `${badge("note")}${colored("#ffac00")}`, run: () => {} },
        { trigger: `${badge("tracking")}${colored("#28a745")}`, run: () => {} },
        { trigger: `${badge("other")}${colored("#dc3545")}`, run: () => {} },
        // the numbers
        { trigger: `${badge("all")}.o-dwo-filterActive:contains('6')`, run: () => {} },
        { trigger: `${badge("discussion")}:contains('1')`, run: () => {} },
        { trigger: `${badge("email")}:contains('1')`, run: () => {} },
        { trigger: `${badge("activity")}:contains('1')`, run: () => {} },
        { trigger: `${badge("note")}:contains('1')`, run: () => {} },
        { trigger: `${badge("tracking")}:contains('1')`, run: () => {} },
        { trigger: `${badge("other")}:contains('1')`, run: () => {} },
        // everything is shown at first
        { trigger: showing("Talk about the order"), run: () => {} },
        { trigger: showing("Private reminder"), run: () => {} },
        emailShown("Email from the customer"),
        // Emails: only the email
        { trigger: badge("email"), run: "click" },
        // chosen: filled with its colour
        { trigger: `${badge("email")}.o-dwo-filterActive`, run: () => {} },
        emailShown("Email from the customer"),
        { trigger: hidden("Talk about the order"), run: () => {} },
        { trigger: hidden("Private reminder"), run: () => {} },
        { trigger: hidden("Automatic message"), run: () => {} },
        // Activities: the message left by a done activity
        { trigger: badge("activity"), run: "click" },
        { trigger: `${badge("activity")}.o-dwo-filterActive`, run: () => {} },
        { trigger: showing("Call done with the customer"), run: () => {} },
        { trigger: hidden("Private reminder"), run: () => {} },
        // Notes
        { trigger: badge("note"), run: "click" },
        { trigger: showing("Private reminder"), run: () => {} },
        emailHidden("Email from the customer"),
        // Tracking
        { trigger: badge("tracking"), run: "click" },
        { trigger: `.o-mail-Thread .o-mail-Message:contains('Name changed')`, run: () => {} },
        { trigger: hidden("Private reminder"), run: () => {} },
        // Other
        { trigger: badge("other"), run: "click" },
        { trigger: showing("Automatic message"), run: () => {} },
        { trigger: hidden("Talk about the order"), run: () => {} },
        // Discussions
        { trigger: badge("discussion"), run: "click" },
        { trigger: showing("Talk about the order"), run: () => {} },
        { trigger: hidden("Automatic message"), run: () => {} },
        // All: back to everything
        { trigger: badge("all"), run: "click" },
        { trigger: `${badge("all")}.o-dwo-filterActive`, run: () => {} },
        { trigger: showing("Private reminder"), run: () => {} },
        { trigger: showing("Automatic message"), run: () => {} },
        emailShown("Email from the customer"),
    ],
});

// The administrator edits the chips: the Edit link opens the list, a new chip is made and shows in the chatter.
registry.category("web_tour.tours").add("dwo_chatter_filter_edit", {
    test: true,
    steps: () => [
        { trigger: ".o-dwo-messageFilter .o-dwo-filterEdit", run: "click" },
        // the list: the six chips, each with a handle to drag it
        { trigger: ".o_list_view .o_data_row:nth-child(6) .o_row_handle", run: () => {} },
        { trigger: ".o_list_view .o_data_row:first-child .o_data_cell:contains('Discussions')", run: () => {} },
        { trigger: ".o_list_button_add", run: "click" },
        // a new chip comes with a colour of its own
        { trigger: ".o_form_view .o_field_color input", run() {
            const value = document.querySelector(".o_form_view .o_field_color input").value;
            if (!/^#[0-9a-f]{6}$/i.test(value)) {
                throw new Error(`The new chip has no colour: "${value}"`);
            }
        } },
        { trigger: ".o_form_view .o_field_widget[name=name] input", run: "text Quotes" },
        { trigger: ".o_form_button_save", run: "click" },
        { trigger: ".o_breadcrumb .o_back_button", run: "click" },
        { trigger: ".o_list_view .o_data_row:contains('Quotes')", run: () => {} },
        { trigger: ".o_breadcrumb .o_back_button", run: "click" },
        // back on the record, the chip is there
        { trigger: `.o-dwo-messageFilter .o-dwo-filterBadge[data-chip-name='Quotes']`, run: () => {} },
    ],
});

// Someone who is not an administrator sees the chips but not the link to edit them.
registry.category("web_tour.tours").add("dwo_chatter_filter_no_edit", {
    test: true,
    steps: () => [
        { trigger: `${badge("all")}`, run: () => {} },
        { trigger: ".o-mail-Chatter:not(:has(.o-dwo-filterEdit))", run: () => {} },
    ],
});

registry.category("web_tour.tours").add("dwo_chatter_filter_search", {
    test: true,
    steps: () => [
        { trigger: ".o-mail-Chatter", run: () => {} },
        { trigger: ".o-dwo-messageFilter .o-dwo-filterSearchInput", run: () => {} },
        { trigger: `${badge("all")}.o-dwo-filterActive:contains('6')`, run: () => {} },
        // typing: the server searches, the numbers follow the text
        { trigger: ".o-dwo-filterSearchInput", run: "text reminder" },
        { trigger: `${badge("all")}:contains('1')`, run: () => {} },
        { trigger: showing("Private reminder"), run: () => {} },
        { trigger: hidden("Talk about the order"), run: () => {} },
        // AND with a chip
        { trigger: badge("note"), run: "click" },
        { trigger: showing("Private reminder"), run: () => {} },
        // a disabled button is only found by a check step
        { trigger: badge("discussion") + ".o-dwo-filterEmpty", isCheck: true, run: () => {} },
        // Esc clears the text
        {
            trigger: ".o-dwo-filterSearchInput",
            run: () => {
                document.querySelector(".o-dwo-filterSearchInput").dispatchEvent(
                    new KeyboardEvent("keydown", { key: "Escape", bubbles: true })
                );
            },
        },
        { trigger: `${badge("all")}:contains('6')`, run: () => {} },
        { trigger: ".o-dwo-filterSearchInput", run: () => { if (document.querySelector(".o-dwo-filterSearchInput").value) { throw new Error("The search text is not cleared"); } } },
    ],
});
