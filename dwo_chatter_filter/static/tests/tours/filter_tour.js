odoo.define('dwo_chatter_filter.tour', function (require) {
'use strict';

const tour = require('web_tour.tour');

const NAMES = {
    all: "All", discussion: "Discussions", email: "Emails", activity: "Activities",
    note: "Notes", tracking: "Tracking", other: "Other",
};
const badge = (kind) => `.o-dwo-messageFilter .o-dwo-filterBadge[data-chip-name='${NAMES[kind]}']`;
// the colour of a chip is a CSS variable set on the chip
const colored = (hex) => `[style*='--dwo-chip: ${hex}']`;
const showing = (text) => `.o_ThreadView .o_Message:contains('${text}')`;
const hidden = (text) => `.o_ThreadView:not(:has(.o_Message:contains('${text}')))`;

// Odoo 16 shows the body of an email like any other message: no shadow DOM
const emailShown = (text) => ({ trigger: showing(text), run: () => {} });
const emailHidden = (text) => ({ trigger: hidden(text), run: () => {} });

tour.register("dwo_chatter_filter", { test: true }, [
        { trigger: ".o_Chatter", run: () => {} },
        // the place: under the planned activities and above the messages
        { trigger: ".o_ActivityBox", run: () => {} },
        { trigger: ".o-dwo-messageFilter + .o_ThreadView", run: () => {} },
        { trigger: ".o_ActivityBox + .o-dwo-messageFilter", run: () => {} },
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
        { trigger: `${badge("all")}.o-dwo-filterActive`, run: () => {} },
        { trigger: showing("Private reminder"), run: () => {} },
        { trigger: showing("Automatic message"), run: () => {} },
        emailShown("Email from the customer"),
]);

// The administrator edits the chips: the Edit link opens the list, a new chip is made and shows in the chatter.
tour.register("dwo_chatter_filter_edit", { test: true }, [
        { trigger: ".o-dwo-messageFilter .o-dwo-filterEdit", run: "click" },
        // the list: the six chips, each with a handle to drag it
        { trigger: ".o_list_view .o_data_row:nth-child(6) .o_row_handle", run: () => {} },
        { trigger: ".o_list_view .o_data_row:first-child .o_data_cell:contains('Discussions')", run: () => {} },
        { trigger: ".o_list_button_add", run: "click" },
        // a new chip comes with a colour of its own
        // Odoo 15: the colour widget is a swatch (its title is the colour); a click opens the colour picker
        { trigger: ".o_form_view .o_field_color", run() {
            const value = document.querySelector(".o_form_view .o_field_color").title;
            if (!/^#[0-9a-f]{6}$/i.test(value)) {
                throw new Error(`The new chip has no colour: "${value}"`);
            }
        } },
        { trigger: ".o_form_view input.o_field_widget[name=name]", run: "text Quotes" },
        { trigger: ".o_form_button_save", run: "click" },
        { trigger: ".o_control_panel .o_back_button", run: "click" },
        { trigger: ".o_list_view .o_data_row:contains('Quotes')", run: () => {} },
        { trigger: ".o_control_panel .o_back_button", run: "click" },
        // back on the record, the chip is there
        { trigger: `.o-dwo-messageFilter .o-dwo-filterBadge[data-chip-name='Quotes']`, run: () => {} },
]);

// Someone who is not an administrator sees the chips but not the link to edit them.
tour.register("dwo_chatter_filter_no_edit", { test: true }, [
        { trigger: `${badge("all")}`, run: () => {} },
        { trigger: ".o_Chatter:not(:has(.o-dwo-filterEdit))", run: () => {} },
]);

});
