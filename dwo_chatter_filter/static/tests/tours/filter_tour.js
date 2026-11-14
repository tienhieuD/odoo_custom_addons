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
    [...document.querySelectorAll(".o-mail-Thread .o-mail-Message div.overflow-x-auto")].map(
        (host) => host.shadowRoot?.textContent || ""
    );
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
    steps: () => [
        { trigger: ".o-mail-Chatter" },
        // the place: under the planned activities and above the messages
        { trigger: ".o-mail-ActivityList + .o-dwo-messageFilter + .o-mail-Thread" },
        // a label, then the badges, each with its own colour (outlined while off)
        { trigger: ".o-dwo-messageFilter .o-dwo-filterLabel:contains('Filter by:')" },
        { trigger: `${badge("discussion")}${colored("#71639e")}` },
        { trigger: `${badge("email")}${colored("#17a2b8")}` },
        { trigger: `${badge("activity")}${colored("#6f42c1")}` },
        { trigger: `${badge("note")}${colored("#ffac00")}` },
        { trigger: `${badge("tracking")}${colored("#28a745")}` },
        { trigger: `${badge("other")}${colored("#dc3545")}` },
        // the numbers
        { trigger: `${badge("all")}.o-dwo-filterActive:contains('6')` },
        { trigger: `${badge("discussion")}:contains('1')` },
        { trigger: `${badge("email")}:contains('1')` },
        { trigger: `${badge("activity")}:contains('1')` },
        { trigger: `${badge("note")}:contains('1')` },
        { trigger: `${badge("tracking")}:contains('1')` },
        { trigger: `${badge("other")}:contains('1')` },
        // everything is shown at first
        { trigger: showing("Talk about the order") },
        { trigger: showing("Private reminder") },
        emailShown("Email from the customer"),
        // Emails: only the email
        { trigger: badge("email"), run: "click" },
        // chosen: filled with its colour
        { trigger: `${badge("email")}.o-dwo-filterActive` },
        emailShown("Email from the customer"),
        { trigger: hidden("Talk about the order") },
        { trigger: hidden("Private reminder") },
        { trigger: hidden("Automatic message") },
        // Activities: the message left by a done activity
        { trigger: badge("activity"), run: "click" },
        { trigger: `${badge("activity")}.o-dwo-filterActive` },
        { trigger: showing("Call done with the customer") },
        { trigger: hidden("Private reminder") },
        // Notes
        { trigger: badge("note"), run: "click" },
        { trigger: showing("Private reminder") },
        emailHidden("Email from the customer"),
        // Tracking
        { trigger: badge("tracking"), run: "click" },
        { trigger: `.o-mail-Thread .o-mail-Message:contains('Name changed')` },
        { trigger: hidden("Private reminder") },
        // Other
        { trigger: badge("other"), run: "click" },
        { trigger: showing("Automatic message") },
        { trigger: hidden("Talk about the order") },
        // Discussions
        { trigger: badge("discussion"), run: "click" },
        { trigger: showing("Talk about the order") },
        { trigger: hidden("Automatic message") },
        // All: back to everything
        { trigger: badge("all"), run: "click" },
        { trigger: `${badge("all")}.o-dwo-filterActive` },
        { trigger: showing("Private reminder") },
        { trigger: showing("Automatic message") },
        emailShown("Email from the customer"),
    ],
});

// The administrator edits the chips: the Edit link opens the list, a new chip is made and shows in the chatter.
registry.category("web_tour.tours").add("dwo_chatter_filter_edit", {
    steps: () => [
        { trigger: ".o-dwo-messageFilter .o-dwo-filterEdit", run: "click" },
        // the list: the six chips, each with a handle to drag it
        { trigger: ".o_list_view .o_data_row:nth-child(6) .o_row_handle" },
        { trigger: ".o_list_view .o_data_row:first-child .o_data_cell:contains('Discussions')" },
        { trigger: ".o_list_button_add", run: "click" },
        // a new chip comes with a colour of its own
        { trigger: ".o_form_view .o_field_color input:not(:visible)", run() {
            if (!/^#[0-9a-f]{6}$/i.test(this.anchor.value)) {
                throw new Error(`The new chip has no colour: "${this.anchor.value}"`);
            }
        } },
        { trigger: ".o_form_view .o_field_widget[name=name] input", run: "edit Quotes" },
        { trigger: ".o_form_button_save", run: "click" },
        { trigger: ".o_breadcrumb .o_back_button", run: "click" },
        { trigger: ".o_list_view .o_data_row:contains('Quotes')" },
        { trigger: ".o_breadcrumb .o_back_button", run: "click" },
        // back on the record, the chip is there
        { trigger: `.o-dwo-messageFilter .o-dwo-filterBadge[data-chip-name='Quotes']` },
    ],
});

// Someone who is not an administrator sees the chips but not the link to edit them.
registry.category("web_tour.tours").add("dwo_chatter_filter_no_edit", {
    steps: () => [
        { trigger: `${badge("all")}` },
        { trigger: ".o-mail-Chatter:not(:has(.o-dwo-filterEdit))" },
    ],
});

registry.category("web_tour.tours").add("dwo_chatter_filter_search", {
    steps: () => [
        { trigger: ".o-mail-Chatter" },
        { trigger: ".o-dwo-messageFilter .o-dwo-filterSearchInput" },
        { trigger: `${badge("all")}.o-dwo-filterActive:contains('6')` },
        // typing: the server searches, the numbers follow the text
        { trigger: ".o-dwo-filterSearchInput", run: "edit reminder" },
        { trigger: `${badge("all")}:contains('1')` },
        { trigger: showing("Private reminder") },
        { trigger: hidden("Talk about the order") },
        // AND with a chip
        { trigger: badge("note"), run: "click" },
        { trigger: showing("Private reminder") },
        { trigger: badge("discussion") + ".o-dwo-filterEmpty" },
        // Esc clears the text
        {
            trigger: ".o-dwo-filterSearchInput",
            run() {
                this.anchor.dispatchEvent(
                    new KeyboardEvent("keydown", { key: "Escape", bubbles: true })
                );
            },
        },
        { trigger: `${badge("all")}:contains('6')` },
        { trigger: ".o-dwo-filterSearchInput", run() { if (this.anchor.value) { throw new Error("The search text is not cleared"); } } },
    ],
});
