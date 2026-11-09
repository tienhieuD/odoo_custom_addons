import { registry } from "@web/core/registry";

const badge = (kind) => `.o-dwo-messageFilter .o-dwo-filterBadge[data-kind='${kind}']`;
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
        { trigger: `${badge("discussion")}.text-primary.border-primary` },
        { trigger: `${badge("email")}.text-info.border-info` },
        { trigger: `${badge("activity")}.text-purple.border-purple` },
        { trigger: `${badge("note")}.text-warning.border-warning` },
        { trigger: `${badge("tracking")}.text-success.border-success` },
        { trigger: `${badge("other")}.text-danger.border-danger` },
        // the numbers
        { trigger: `${badge("all")}.text-bg-dark:contains('6')` },
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
        { trigger: `${badge("email")}.text-bg-info` },
        emailShown("Email from the customer"),
        { trigger: hidden("Talk about the order") },
        { trigger: hidden("Private reminder") },
        { trigger: hidden("Automatic message") },
        // Activities: the message left by a done activity
        { trigger: badge("activity"), run: "click" },
        { trigger: `${badge("activity")}.text-bg-purple` },
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
        { trigger: `${badge("all")}.text-bg-dark` },
        { trigger: showing("Private reminder") },
        { trigger: showing("Automatic message") },
        emailShown("Email from the customer"),
    ],
});
