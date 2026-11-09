/* @odoo-module */

import { registry } from "@web/core/registry";

const badge = (kind) => `.o-dwo-messageFilter .o-dwo-filterBadge[data-kind='${kind}']`;
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
        { trigger: ".o-dwo-messageFilter", run: () => {} },
        // in this version the Thread may sit in a wrapper
        { trigger: ".o-dwo-messageFilter ~ :is(.o-mail-Thread, :has(.o-mail-Thread))", run: () => {} },
        { trigger: ".o-mail-ActivityList + .o-dwo-messageFilter", run: () => {} },
        // a label, then the badges, each with its own colour (outlined while off)
        { trigger: ".o-dwo-messageFilter .o-dwo-filterLabel:contains('Filter by:')", run: () => {} },
        { trigger: `${badge("discussion")}.text-primary.border-primary`, run: () => {} },
        { trigger: `${badge("email")}.text-info.border-info`, run: () => {} },
        { trigger: `${badge("activity")}.text-purple.border-purple`, run: () => {} },
        { trigger: `${badge("note")}.text-warning.border-warning`, run: () => {} },
        { trigger: `${badge("tracking")}.text-success.border-success`, run: () => {} },
        { trigger: `${badge("other")}.text-danger.border-danger`, run: () => {} },
        // the numbers
        { trigger: `${badge("all")}.text-bg-dark:contains('6')`, run: () => {} },
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
        { trigger: `${badge("email")}.text-bg-info`, run: () => {} },
        emailShown("Email from the customer"),
        { trigger: hidden("Talk about the order"), run: () => {} },
        { trigger: hidden("Private reminder"), run: () => {} },
        { trigger: hidden("Automatic message"), run: () => {} },
        // Activities: the message left by a done activity
        { trigger: badge("activity"), run: "click" },
        { trigger: `${badge("activity")}.text-bg-purple`, run: () => {} },
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
        { trigger: `${badge("all")}.text-bg-dark`, run: () => {} },
        { trigger: showing("Private reminder"), run: () => {} },
        { trigger: showing("Automatic message"), run: () => {} },
        emailShown("Email from the customer"),
    ],
});
