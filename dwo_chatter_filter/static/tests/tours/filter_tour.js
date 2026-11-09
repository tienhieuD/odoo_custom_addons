odoo.define('dwo_chatter_filter.tour', function (require) {
'use strict';

const tour = require('web_tour.tour');

const badge = (kind) => `.o-dwo-messageFilter .o-dwo-filterBadge[data-kind='${kind}']`;
const showing = (text) => `.o_ThreadView .o_Message:contains('${text}')`;
const hidden = (text) => `.o_ThreadView:not(:has(.o_Message:contains('${text}')))`;
// Odoo 16 shows the body of an email like any other message: no shadow DOM
const emailShown = (text) => ({ trigger: showing(text), run: () => {} });
const emailHidden = (text) => ({ trigger: hidden(text), run: () => {} });

tour.register("dwo_chatter_filter", { test: true }, [
        { trigger: ".o_Chatter", run: () => {} },
        // the place: under the planned activities and above the messages
        { trigger: ".o_ActivityBox", run: () => {} },
        { trigger: ".o-dwo-messageFilter", run: () => {} },
        { trigger: ".o-dwo-messageFilter + .o_ThreadView", run: () => {} },
        { trigger: ".o_ActivityBox + .o-dwo-messageFilter", run: () => {} },
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
        { trigger: `.o_ThreadView .o_Message:contains('Name changed')`, run: () => {} },
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
]);

});
