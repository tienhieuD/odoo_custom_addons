/* @odoo-module */

import tour from "web_tour.tour";

// Odoo 15 clicks the element of every step that has no "run" (a step that only checks must do nothing),
// and looks for the element inside the open dialog only (the selectors here start with ".modal").
// The tours of this file are written for the newer versions, so each step gets an empty run and
// in_modal false unless it says otherwise.

// "text X" of Odoo 16 also sends a change event, which closes an autocomplete before the tour sees its
// list: an input gets its value and an input event only (the editor keeps the helper of the tour).
const typeText = (text) =>
    function (helper) {
        const el = this.$anchor[0];
        if (el.matches("input, textarea")) {
            el.focus();
            el.value = text;
            el.dispatchEvent(new InputEvent("input", { bubbles: true }));
        } else {
            helper.text(text);
        }
    };

const adapt = (step) => {
    let run = step.run;
    if (typeof run === "string" && run.startsWith("text ")) {
        run = typeText(run.slice(5));
    }
    if (run === undefined) {
        return { run: () => {}, isCheck: true, in_modal: false, ...step };
    }
    return { in_modal: false, ...step, run };
};

// the tours of Odoo 16 are registered with the legacy API
const tours = {
    add(name, definition) {
        tour.register(name, { test: true }, definition.steps().map(adapt));
    },
};

// a plain JSON-RPC call
const rpc = async (route, params) => {
    const response = await fetch(route, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", method: "call", params }),
    });
    return (await response.json()).result;
};

// The :value(text) pseudo of the newer versions (the value of an input)
if (!$.expr.pseudos.value) {
    $.expr.pseudos.value = $.expr.createPseudo((text) => (el) => el.value === text);
}

const EDITOR = ".o-dwo-emailComposer .odoo-editor-editable";

const emailBodyShows = (text) => ({
    trigger: ".o_Message:has(.o-dwo-emailBadge)",
    async run() {
        for (let i = 0; i < 50; i++) {
                        const messages = [...document.querySelectorAll(".o_Message:has(.o-dwo-emailBadge)")];
            if (messages.some((message) => message.textContent.includes(text))) {
                return;
            }
            await new Promise((resolve) => setTimeout(resolve, 100));
        }
        throw new Error(`The email message does not show "${text}"`);
    },
});

tours.add("dwo_mail_compose_send", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        {
            trigger: "#dwo_from",
            run: function () {
                const value = document.querySelector("#dwo_from").value;
                if (!value.includes("@")) {
                    throw new Error(`From should show the current user, found: "${value}"`);
                }
            },
        },
        // Cc and Bcc are behind their buttons until used
        { trigger: ".o-dwo-emailComposer:not(:has(#dwo_cc)):not(:has(#dwo_bcc))" },
        { trigger: "#dwo_to", run: "text new.person@acme.example," },
        { trigger: "[data-field='to'] .o-dwo-chip[data-email='new.person@acme.example']" },
        // a chip is grey; only the word "new" has the info colour
        { trigger: "[data-field='to'] .o-dwo-chip[data-email='new.person@acme.example'].badge-light .o-dwo-chipNew.text-info" },
        // no limit between the fields: the same address can be typed again in Cc and Bcc
        { trigger: ".o-dwo-ccBtn", run: "click" },
        { trigger: "#dwo_cc", run: "text new.person@acme.example," },
        { trigger: "#dwo_cc", run: "text second.person@acme.example," },
        { trigger: "[data-field='cc'] .o-dwo-chip[data-email='new.person@acme.example']" },
        { trigger: "[data-field='cc'] .o-dwo-chip[data-email='second.person@acme.example']" },
        { trigger: ".o-dwo-bccBtn", run: "click" },
        { trigger: "#dwo_bcc", run: "text hidden.boss@acme.example," },
        { trigger: "[data-field='bcc'] .o-dwo-chip[data-email='hidden.boss@acme.example']" },
        { trigger: "#dwo_subject", run: "text Tour subject" },
        { trigger: EDITOR, run: "click" },
        { trigger: EDITOR, run: "text Hello from the tour" },
        { trigger: ".o-dwo-sendBtn.o-dwo-sendNow", run: "click" },
        emailBodyShows("Hello from the tour"),
        { trigger: ".o_Message .o-dwo-emailMeta:contains('new.person@acme.example')" },
        { trigger: ".o_Chatter:not(:has(.o-dwo-emailComposer))" },
    ],
});

tours.add("dwo_mail_compose_draft", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: "#dwo_subject", run: "text Draft subject" },
        { trigger: EDITOR, run: "click" },
        { trigger: EDITOR, run: "text Draft body" },
        { trigger: ".o-dwo-closeBtn", run: "click" },
        { trigger: ".o_Chatter:not(:has(.o-dwo-emailComposer))" },
        // the draft dot shows once the draft is known
        { trigger: ".o-mail-Chatter-dwoSendEmail .o-dwo-draftDot" },
        {
            trigger: ".o-mail-Chatter-dwoSendEmail .o-dwo-draftDot",
            run: function () {
                const dot = document.querySelector(".o-dwo-draftDot");
                const style = getComputedStyle(dot);
                const transparent = ["rgba(0, 0, 0, 0)", "transparent"].includes(style.backgroundColor);
                if (transparent || !dot.offsetWidth || !dot.offsetHeight) {
                    throw new Error(`The draft dot is not visible: ${style.backgroundColor} ${dot.offsetWidth}x${dot.offsetHeight}`);
                }
            },
        },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: "#dwo_subject:value(Draft subject)" },
        // the reopened draft is rendered as HTML, not shown as code
        { trigger: `${EDITOR} :contains('Draft body')` },
        { trigger: `${EDITOR}:not(:contains('<'))` },
        { trigger: ".o-dwo-emailComposer:contains('Draft saved')" },
        // Delete draft is a plain outline button beside Send email
        {
            trigger: ".o-dwo-deleteDraft",
            run: function () {
                const button = document.querySelector(".o-dwo-deleteDraft");
                const send = document.querySelector(".o-dwo-sendBtn");
                if (!button.classList.contains("btn-outline-secondary") || button.parentElement !== (send.closest(".dropdown")?.parentElement || send.parentElement)) {
                    throw new Error("Delete draft should be an outline secondary button next to Send email");
                }
            },
        },
        // it asks first: Cancel keeps the draft, Delete removes it
        { trigger: ".o-dwo-deleteDraft", run: "click" },
        { trigger: ".modal .modal-footer button:contains('Cancel')", run: "click" },
        { trigger: ".o-dwo-emailComposer:contains('Draft saved')" },
        { trigger: ".o-dwo-deleteDraft", run: "click" },
        { trigger: ".modal .modal-footer button:contains('Delete')", run: "click" },
        { trigger: ".o-dwo-emailComposer:contains('No draft yet')" },
        { trigger: "#dwo_subject:value()" },
    ],
});

tours.add("dwo_mail_compose_reply", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        { trigger: ".o_Message:has(.o-dwo-emailBadge)", run: function () { for (const type of ["mouseover", "mouseenter", "mousemove"]) { this.$anchor[0].dispatchEvent(new MouseEvent(type, { bubbles: true })); } } },
        { trigger: ".o-dwo-emailActions .o-dwo-replyAllBtn", run: "click" },
        { trigger: ".o-dwo-formBox .o-dwo-title:contains('RE: Incoming question')" },
        { trigger: "#dwo_subject:value(RE: Incoming question)" },
        { trigger: ".o-dwo-chip[data-email='customer@acme.example']" },
        { trigger: `${EDITOR}:contains('Original message')` },
        { trigger: `${EDITOR}:contains('(JST)')` },
        // the quote is rendered as HTML: a real element, and no tag shown as text
        { trigger: `${EDITOR} #divRplyFwdMsg b:contains('From:')` },
        { trigger: `${EDITOR}:not(:contains('<div')):not(:contains('<b>')):not(:contains('<br'))` },
        // a suggestion picked, then a second click on the same field (it keeps the focus, so no focus
        // event) must open the suggestions again
        { trigger: "#dwo_to", run: "text admin" },
        { trigger: ".o-dwo-suggestions .dropdown-item", run: "click" },
        { trigger: ".o-dwo-chip:not([data-email='customer@acme.example'])" },
        { trigger: "body:not(:has(.o-dwo-suggestions))" },
        // the field still has the focus: that is the situation of the bug. Wait: a suggestion
        // request started while typing must not open the list again by itself
        {
            // the pseudo :focus needs the focus of the window; the focused element is enough here
            trigger: "#dwo_to",
            run: async function () {
                if (document.activeElement !== this.$anchor[0]) {
                    throw new Error("#dwo_to should still have the focus");
                }
                await new Promise((resolve) => setTimeout(resolve, 600));
            },
        },
        { trigger: "body:not(:has(.o-dwo-suggestions))" },
        // only a click event, like the second click of a user: the tour helper would also send a focus event
        {
            trigger: "#dwo_to",
            run: () => document.querySelector("#dwo_to").dispatchEvent(new MouseEvent("click", { bubbles: true })),
        },
        { trigger: ".o-dwo-suggestions .dropdown-item" },
    ],
});

tours.add("dwo_mail_compose_reply_buttons", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        // Reply, Reply all and Forward are always visible under From/To/Cc, not in the "more" menu
        { trigger: ".o_Message:has(.o-dwo-emailBadge) .o-dwo-emailMeta + .o-dwo-emailActions .o-dwo-replyBtn" },
        { trigger: ".o-dwo-emailActions .o-dwo-replyAllBtn" },
        { trigger: ".o-dwo-emailActions .o-dwo-forwardBtn" },
        // an email sent to the catchall still shows its To line
        { trigger: ".o-dwo-emailMeta:contains('To:'):contains('catchall@dwo.example')" },
        // Reply goes to the sender only: nobody in Cc
        { trigger: ".o-dwo-emailActions .o-dwo-replyBtn", run: "click" },
        { trigger: "#dwo_subject:value(RE: Incoming question)" },
        { trigger: ".o-dwo-chip[data-email='customer@acme.example']" },
        { trigger: "body:not(:has(#dwo_cc))" },
    ],
});

tours.add("dwo_mail_compose_template", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        // the template menu lists the templates of this kind of record
        { trigger: ".o-dwo-templateBtn", run: "click" },
        { trigger: ".o-dwo-templateMenu .dropdown-item:contains('Tour template')", run: "click" },
        // recipients, subject and body are computed on this record
        { trigger: ".o-dwo-chip[data-email='tpl.customer@acme.example']" },
        { trigger: ".o-dwo-chip[data-email='cc.tpl@acme.example']" },
        { trigger: ".o-dwo-chip[data-email='bcc.tpl@acme.example']" },
        { trigger: "#dwo_subject:value(Quote for DWO Mail Tour Partner)" },
        { trigger: `${EDITOR}:contains('Dear DWO Mail Tour Partner, here is your quote.')` },
        { trigger: `${EDITOR}:not(:contains('<'))` },
        // nothing was written: the text took the place of the two empty lines (it is the first
        // block) and the signature is still under it
        { trigger: `${EDITOR} > :first-child:contains('Dear DWO Mail Tour Partner')` },
        { trigger: `${EDITOR}:contains('Tour signature')` },
        // the editor is made again when a template is chosen: the old one must not stay in the page
        {
            trigger: ".o-dwo-editorBox",
            async run() {
                await new Promise((resolve) => setTimeout(resolve, 500));
                const count = this.$anchor[0].querySelectorAll(".note-editable").length;
                if (count !== 1) {
                    throw new Error(`The form holds ${count} editors, one expected`);
                }
            },
        },
        // removing a file asks first
        { trigger: ".o-dwo-attachment:contains('terms.txt') .o-dwo-attachmentRemove", run: "click" },
        { trigger: ".modal .modal-footer button:contains('Cancel')", run: "click" },
        { trigger: ".o-dwo-attachment:contains('terms.txt')" },
        { trigger: ".o-dwo-attachment:contains('terms.txt') .o-dwo-attachmentRemove", run: "click" },
        { trigger: ".modal .modal-footer button:contains('Remove')", run: "click" },
        { trigger: ".o-dwo-emailComposer:not(:has(.o-dwo-attachment))" },
        // removing the template takes back the recipients it added
        { trigger: ".o-dwo-templateBadge .o-dwo-templateRemove", run: "click" },
        { trigger: ".o-dwo-emailComposer:not(:has(.o-dwo-chip[data-email='cc.tpl@acme.example']))" },
        { trigger: ".o-dwo-emailComposer:not(:has(.o-dwo-chip[data-email='tpl.customer@acme.example']))" },
    ],
});

// The user already wrote something: the template asks before touching it.
tours.add("dwo_mail_compose_template_dirty", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: "#dwo_subject", run: "text My own subject" },
        { trigger: EDITOR, run: "click" },
        { trigger: EDITOR, run: "text My own words" },
        // Cancel: nothing changes and the field is empty again
        { trigger: ".o-dwo-templateBtn", run: "click" },
        { trigger: ".o-dwo-templateMenu .dropdown-item:contains('Tour template')", run: "click" },
        { trigger: ".modal-footer button:contains('Cancel')", run: "click" },
        { trigger: `${EDITOR}:contains('My own words')` },
        { trigger: `${EDITOR}:not(:contains('here is your quote'))` },
        { trigger: "#dwo_subject:value(My own subject)" },
        { trigger: ".o-dwo-emailComposer:not(:has(.o-dwo-templateBadge))" },
        // Add after my text: both texts, the subject is kept
        { trigger: ".o-dwo-templateBtn", run: "click" },
        { trigger: ".o-dwo-templateMenu .dropdown-item:contains('Tour template')", run: "click" },
        { trigger: ".modal-footer button:contains('Add after my text')", run: "click" },
        { trigger: `${EDITOR}:contains('My own words')` },
        { trigger: `${EDITOR}:contains('here is your quote')` },
        { trigger: "#dwo_subject:value(My own subject)" },
        { trigger: ".o-dwo-chip[data-email='tpl.customer@acme.example']" },
        // remove the template, then pick it again: the user's text is now mixed, so it asks again
        { trigger: ".o-dwo-templateBadge .o-dwo-templateRemove", run: "click" },
        { trigger: ".o-dwo-templateBtn", run: "click" },
        { trigger: ".o-dwo-templateMenu .dropdown-item:contains('Tour template')", run: "click" },
        { trigger: ".modal-footer button:contains('Overwrite')", run: "click" },
        { trigger: `${EDITOR}:contains('here is your quote')` },
        { trigger: `${EDITOR}:not(:contains('My own words'))` },
        { trigger: "#dwo_subject:value(Quote for DWO Mail Tour Partner)" },
    ],
});

// 1x1 transparent PNG, inserted the way a paste does: a base64 image waiting to be saved
const PIXEL =
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";

tours.add("dwo_mail_compose_image", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: "#dwo_to", run: "text image.person@acme.example," },
        { trigger: ".o-dwo-chip[data-email='image.person@acme.example']" },
        { trigger: "#dwo_subject", run: "text Image subject" },
        { trigger: EDITOR, run: "click" },
        { trigger: EDITOR, run: "text Look at this" },
        {
            trigger: EDITOR,
            run: function () {
                const editable = document.querySelector(".o-dwo-emailComposer .odoo-editor-editable");
                editable.insertAdjacentHTML(
                    "beforeend",
                    `<p><img class="o_b64_image_to_save" src="${PIXEL}"/></p>`
                );
                editable.dispatchEvent(new Event("input", { bubbles: true }));
            },
        },
        { trigger: `${EDITOR} img.o_b64_image_to_save` },
        { trigger: ".o-dwo-sendBtn.o-dwo-sendNow", run: "click" },
        emailBodyShows("Look at this"),
        // the image of the email points to an attachment of the record, not to a base64 blob
        { trigger: ".o_Message:has(.o-dwo-emailBadge) img[src*='/web/image/']" },
    ],
});

tours.add("dwo_mail_compose_ui", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        // the title is the subject; "Compose email" until there is one. A long one is cut with an ellipsis
        { trigger: ".o-dwo-formBox .o-dwo-title:contains('Compose email')" },
        { trigger: "#dwo_subject", run: "text A very long subject that goes on and on and on and on and on and on and on and on and on and on and on and on" },
        {
            trigger: ".o-dwo-formBox .o-dwo-title:contains('A very long subject')",
            run: function () {
                const style = getComputedStyle(document.querySelector(".o-dwo-formBox .o-dwo-title"));
                if (style.textOverflow !== "ellipsis" || style.whiteSpace !== "nowrap") {
                    throw new Error(`The title is not cut with an ellipsis: ${style.textOverflow} ${style.whiteSpace}`);
                }
                if (style.color === "rgb(25, 135, 84)") {
                    throw new Error("The title is green");
                }
            },
        },
        { trigger: "#dwo_subject", run: function () { const el = this.$anchor[0]; el.value = ""; el.dispatchEvent(new InputEvent("input", { bubbles: true })); } },
        { trigger: ".o-dwo-formBox .o-dwo-title:contains('Compose email')" },
        // the close button is an icon only
        { trigger: ".o-dwo-closeBtn:not(:contains('Close'))" },
        // the required marks are red
        {
            trigger: ".o-dwo-required",
            run: function () {
                const color = getComputedStyle(document.querySelector(".o-dwo-required")).color;
                if (color === getComputedStyle(document.body).color) {
                    throw new Error(`The required mark is not highlighted: ${color}`);
                }
            },
        },
        // the info icon stays on the line of its label
        {
            trigger: ".o-dwo-label",
            run: function () {
                for (const label of document.querySelectorAll(".o-dwo-emailComposer .o-dwo-label")) {
                    const text = label.querySelector("span").getBoundingClientRect();
                    const info = label.querySelector(".o-dwo-info").getBoundingClientRect();
                    if (Math.abs(text.top - info.top) > text.height) {
                        throw new Error(`The info icon is on another line than its label: ${label.textContent}`);
                    }
                }
            },
        },
        { trigger: ".o-dwo-directNote:contains('followers of the record are not notified')" },
        { trigger: ".o-dwo-sendBtn .fa-paper-plane" },
        // Reply-To is added from Advanced, with its default, and goes back to it
        { trigger: ".o-dwo-emailComposer:not(:has(#dwo_replyto))" },
        { trigger: ".o-dwo-advancedBtn", run: "click" },
        { trigger: ".o-dwo-addReplyTo:contains('Reply to'):contains('default:')", run: "click" },
        {
            trigger: "#dwo_replyto",
            run: function () {
                if (!document.querySelector("#dwo_replyto").value.includes("@")) {
                    throw new Error("The default Reply-To should be shown in the field");
                }
            },
        },
        { trigger: ".o-dwo-emailComposer:not(:has(.o-dwo-replyToReset))" },
        { trigger: "#dwo_replyto", run: "text someone.else@elsewhere.example" },
        { trigger: ".o-dwo-replyToReset", run: "click" },
        { trigger: ".o-dwo-emailComposer:not(:has(.o-dwo-replyToReset))" },
        { trigger: "#dwo_replyto:not(:value(someone.else@elsewhere.example))" },
        // a custom Reply-To is shown by default when the draft is opened again
        { trigger: "#dwo_replyto", run: "text keep.me@elsewhere.example" },
        { trigger: ".o-dwo-closeBtn", run: "click" },
        { trigger: ".o_Chatter:not(:has(.o-dwo-emailComposer))" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: "#dwo_replyto:value(keep.me@elsewhere.example)" },
        { trigger: ".o-dwo-replyToReset" },
    ],
});

tours.add("dwo_mail_compose_save_template", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: "#dwo_subject", run: "text My reusable subject" },
        { trigger: EDITOR, run: "click" },
        { trigger: EDITOR, run: "text My reusable text" },
        { trigger: ".o-dwo-templateBtn", run: "click" },
        { trigger: ".o-dwo-saveTemplate", run: "click" },
        { trigger: "#dwo_template_name", run: "text Saved from the composer" },
        { trigger: ".modal-footer button:contains('Save')", run: "click" },
        { trigger: ".o_notification:contains('Template saved')" },
        // the new template is in the menu
        { trigger: ".o-dwo-templateBtn", run: "click" },
        { trigger: ".o-dwo-templateMenu .dropdown-item:contains('Saved from the composer')" },
    ],
});

tours.add("dwo_mail_compose_shown_values", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        { trigger: ".o_Message:has(.o-dwo-emailBadge)", run: function () { for (const type of ["mouseover", "mouseenter", "mousemove"]) { this.$anchor[0].dispatchEvent(new MouseEvent(type, { bubbles: true })); } } },
        { trigger: ".o-dwo-emailActions .o-dwo-replyAllBtn", run: "click" },
        // the reply-all has Cc people: the Cc line is shown, Bcc stays behind its button
        { trigger: "#dwo_cc" },
        { trigger: "[data-field='cc'] .o-dwo-chip[data-email='cc.person@acme.example']" },
        { trigger: ".o-dwo-emailComposer:not(:has(#dwo_bcc))" },
        { trigger: ".o-dwo-bccBtn" },
        { trigger: ".o-dwo-emailComposer:not(:has(.o-dwo-ccBtn))" },
    ],
});

// The author asks an approver (oneself here) and the form shows the waiting state.
tours.add("dwo_mail_compose_request_approval", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: "#dwo_to", run: "text approval.customer@acme.example," },
        { trigger: "[data-field='to'] .o-dwo-chip[data-email='approval.customer@acme.example']" },
        { trigger: "#dwo_subject", run: "text Needs approval" },
        { trigger: EDITOR, run: "click" },
        { trigger: EDITOR, run: "text Please check this text" },
        { trigger: ".o-dwo-sendBtn", run: "click" },
        // two ways to send
        { trigger: ".o-dwo-sendNow" },
        { trigger: ".o-dwo-requestApproval", run: "click" },
        // the popup: approvers are required, the comment is not
        { trigger: ".modal .o-dwo-approvalConfirm:disabled" },
        { trigger: "#dwo_approver_input", run: "text Administrator" },
        { trigger: ".o-dwo-approverMatches .dropdown-item:contains('Administrator')", run: "click" },
        { trigger: ".modal .o-dwo-approverChip:contains('Administrator')" },
        { trigger: "#dwo_approval_comment", run: "text Could you look at it?" },
        { trigger: ".modal .o-dwo-approvalConfirm:not(:disabled)", run: "click" },
        { trigger: ".o-dwo-stateBadge:contains('Waiting for approval')" },
        { trigger: ".o-dwo-pendingNote:contains('Administrator'):contains('Could you look at it?')" },
        // it is in the list, and still editable
        { trigger: ".o-dwo-emailRow.active:contains('Needs approval')" },
        { trigger: "#dwo_subject", run: "text Needs approval edited" },
        { trigger: ".o-dwo-emailRow:contains('Needs approval edited')" },
        // approved while the form is still open (admin is his own approver)
        {
            trigger: ".o-dwo-stateBadge",
            run: async function () {
                const [email] = await rpc("/web/dataset/call_kw/dwo.mail.email/search_read", {
                    model: "dwo.mail.email", method: "search_read",
                    args: [[["state", "=", "pending"]], ["id"]], kwargs: { limit: 1 },
                });
                await rpc("/web/dataset/call_kw/dwo.mail.email/action_approve", {
                    model: "dwo.mail.email", method: "action_approve",
                    args: [[email.id], "approved while open"], kwargs: {},
                });
            },
        },
        // the next autosave learns it left: the form says so and does not raise an error
        { trigger: "#dwo_subject", run: "text Edited after approval" },
        { trigger: ".o-dwo-sentNote:contains('approved'):contains('sent')" },
        { trigger: ".o-dwo-stateBadge:contains('Approved and sent')" },
        { trigger: ".o-dwo-sendBtn:disabled, .o-dwo-sendBtn.disabled" },
        { trigger: "body:not(:has(.o_error_dialog))" },
        // and the form can be closed
        { trigger: ".o-dwo-closeBtn", run: "click" },
        { trigger: ".o_Chatter:not(:has(.o-dwo-emailComposer))" },
        { trigger: "body:not(:has(.o_error_dialog))" },
    ],
});

// With the approval flow on, somebody who cannot send without approval has one button: request approval.
tours.add("dwo_mail_compose_approval_required", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: ".o-dwo-sendBtn.o-dwo-requestApproval:contains('Request approval')" },
        { trigger: ".o-dwo-emailComposer:not(:has(.o-dwo-sendNow)):not(:has(.o-dwo-sendMenu))" },
        { trigger: ".o-dwo-directNote:contains('An approver must approve')" },
        // the popup does not offer the author when the company does not allow it
        { trigger: ".o-dwo-sendBtn.o-dwo-requestApproval", run: "click" },
        { trigger: ".modal:contains('Request approval')" },
        { trigger: ".modal:not(:contains('You can choose yourself'))" },
    ],
});

// Without the approval flow there is one way to send: right away.
tours.add("dwo_mail_compose_direct_only", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: ".o-dwo-sendBtn.o-dwo-sendNow:contains('Send email')" },
        { trigger: ".o-dwo-emailComposer:not(:has(.o-dwo-requestApproval)):not(:has(.o-dwo-sendMenu))" },
        { trigger: ".o-dwo-directNote:contains('sent directly')" },
    ],
});

// Several emails on one record: the list opens them in the form.
tours.add("dwo_mail_compose_email_list", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        // the newest created is open (the draft), the rejected one is in the list
        { trigger: "#dwo_subject:value(Second draft)" },
        { trigger: ".o-dwo-emailRow:contains('Rejected one'):contains('Rejected')" },
        { trigger: ".o-dwo-emailRow:contains('Second draft'):contains('Draft')" },
        // newest created first, with the creation and last update dates
        {
            trigger: ".o-dwo-emailRow",
            run: function () {
                const rows = [...document.querySelectorAll(".o-dwo-emailRow")];
                if (!rows[0].textContent.includes("Second draft") || !rows[1].textContent.includes("Rejected one")) {
                    throw new Error(`The list is not newest first: ${rows.map((r) => r.textContent.trim()).join(" | ")}`);
                }
                for (const row of rows) {
                    const dates = row.querySelector(".o-dwo-emailDates").textContent;
                    if (!dates.includes("Created") || !dates.includes("Updated")) {
                        throw new Error(`A row has no dates: ${dates}`);
                    }
                }
            },
        },
        // a long list scrolls
        {
            trigger: ".o-dwo-emailRows",
            run: function () {
                const style = getComputedStyle(document.querySelector(".o-dwo-emailRows"));
                if (style.overflowY !== "auto" || style.maxHeight === "none") {
                    throw new Error(`The list does not scroll: ${style.overflowY} ${style.maxHeight}`);
                }
            },
        },
        { trigger: ".o-dwo-emailRow:contains('Rejected one')", run: "click" },
        { trigger: "#dwo_subject:value(Rejected one)" },
        { trigger: ".o-dwo-rejectedNote:contains('Not like this')" },
        { trigger: ".o-dwo-stateBadge:contains('Rejected')" },
        { trigger: ".o-dwo-emailRow.active:contains('Rejected one')" },
        // another email is created elsewhere (here by a call to the server) while the form is open ...
        {
            trigger: ".o-dwo-closeBtn",
            run: async function () {
                const resId = parseInt(new URLSearchParams(location.hash.slice(1)).get("id"));
                await rpc("/web/dataset/call_kw/dwo.mail.composer/save_email", {
                    model: "dwo.mail.composer", method: "save_email",
                    args: ["res.partner", resId, false, { from: "admin@dwo.example", subject: "Created elsewhere", body: "<p>e</p>" }],
                    kwargs: {},
                });
            },
        },
        // ... the choice is remembered, and the list is fetched again each time the form opens
        { trigger: ".o-dwo-closeBtn", run: "click" },
        { trigger: ".o_Chatter:not(:has(.o-dwo-emailComposer))" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: "#dwo_subject:value(Rejected one)" },
        { trigger: ".o-dwo-emailRow.active:contains('Rejected one')" },
        { trigger: ".o-dwo-emailRow:contains('Created elsewhere')" },
        // a new email is created in the database at once: it is in the list, in the form, saved
        { trigger: ".o-dwo-newEmail", run: "click" },
        { trigger: "#dwo_subject:value()" },
        { trigger: ".o-dwo-emailRow.active:contains('(No subject)')" },
        { trigger: ".o-dwo-emailComposer:contains('Draft saved')" },
        { trigger: ".o-dwo-emailRow:contains('Rejected one')" },
        { trigger: ".o-dwo-emailRow:contains('Second draft')" },
        // and it is the one shown when the form is opened again
        { trigger: ".o-dwo-closeBtn", run: "click" },
        { trigger: ".o_Chatter:not(:has(.o-dwo-emailComposer))" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: ".o-dwo-emailRow.active:contains('(No subject)')" },
        // the form and the list are two areas, each with its own border
        {
            trigger: ".o-dwo-emailList",
            run: function () {
                const form = document.querySelector(".o-dwo-formBox");
                const list = document.querySelector(".o-dwo-emailList");
                if (form.contains(list) || list.contains(form)) {
                    throw new Error("The form and the list must be two separate boxes");
                }
                for (const [name, box] of [["form", form], ["list", list]]) {
                    if (parseFloat(getComputedStyle(box).borderTopWidth) < 1) {
                        throw new Error(`The ${name} box has no border`);
                    }
                }
            },
        },
        // every deletion asks: a draft too, and "Cancel" keeps it
        { trigger: ".o-dwo-emailRow:contains('Second draft') .o-dwo-rowDelete", run: "click" },
        { trigger: ".modal .modal-footer button:contains('Cancel')", run: "click" },
        { trigger: ".o-dwo-emailRow:contains('Second draft')" },
        { trigger: ".o-dwo-emailRow:contains('Second draft') .o-dwo-rowDelete", run: "click" },
        { trigger: ".modal .modal-footer button:contains('Delete')", run: "click" },
        { trigger: ".o-dwo-emailList:not(:has(.o-dwo-emailRow:contains('Second draft')))" },
        { trigger: ".o-dwo-emailRow:contains('Created elsewhere') .o-dwo-rowDelete", run: "click" },
        { trigger: ".modal .modal-footer button:contains('Delete')", run: "click" },
        { trigger: ".o-dwo-emailList:not(:has(.o-dwo-emailRow:contains('Created elsewhere')))" },
        // a rejected email is deleted too
        { trigger: ".o-dwo-emailRow:contains('Rejected one') .o-dwo-rowDelete", run: "click" },
        { trigger: ".modal .modal-footer button:contains('Delete')", run: "click" },
        { trigger: ".o-dwo-emailList:not(:has(.o-dwo-emailRow:contains('Rejected one')))" },
        // the empty new email is the last one: deleting the one in the form resets the form
        { trigger: ".o-dwo-emailRow.active .o-dwo-rowDelete", run: "click" },
        { trigger: ".modal .modal-footer button:contains('Delete')", run: "click" },
        { trigger: ".o_Chatter:not(:has(.o-dwo-emailList))" },
        { trigger: ".o-dwo-emailComposer:contains('No draft yet')" },
    ],
});

// The form takes the room of the chatter, the message is lower, and it can use the whole screen.
tours.add("dwo_mail_compose_layout", {
    test: true,
    steps: () => [
        { trigger: ".o_Message:contains('History message')" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: ".o-dwo-emailComposer" },
        // the messages are hidden while the form is open ...
        {
            trigger: ".o-dwo-emailComposer",
            run: function () {
                const display = getComputedStyle(document.querySelector(".o_Chatter_scrollPanel")).display;
                if (display !== "none") {
                    throw new Error(`The messages should be hidden, display is ${display}`);
                }
            },
        },
        // ... the body is lower (two thirds of before: 6rem to 19rem) ...
        {
            trigger: ".o-dwo-editor",
            run: function () {
                const style = getComputedStyle(document.querySelector(".o-dwo-editor"));
                const rem = parseFloat(getComputedStyle(document.documentElement).fontSize);
                if (parseFloat(style.minHeight) > 6.1 * rem || parseFloat(style.maxHeight) > 19.1 * rem) {
                    throw new Error(`The body is too tall: ${style.minHeight} to ${style.maxHeight}`);
                }
            },
        },
        // a sticky statusbar like the one of a form with a header (z-index 1020)
        {
            trigger: ".o_form_view",
            run: function () {
                // in its own wrapper in the body: the form is rendered again and would drop it
                const form = document.createElement("div");
                form.className = "o_form_view o-dwo-fakeForm";
                const bar = document.createElement("div");
                bar.className = "o_form_statusbar o-dwo-fakeStatusbar";
                bar.style.cssText = "position: sticky; top: 0; z-index: 1020; height: 20px;";
                bar.textContent = "Statusbar";
                form.append(bar);
                document.body.prepend(form);
            },
        },
        // ... and it can use the whole screen, only the body
        { trigger: ".o-dwo-expandBtn", run: "click" },
        {
            // ... and then the statusbar goes under it
            trigger: ".o-dwo-editorBox.o-dwo-expanded",
            run: function () {
                const z = getComputedStyle(document.querySelector(".o-dwo-fakeStatusbar")).zIndex;
                if (z !== "0") {
                    throw new Error(`The statusbar stays above the expanded body: z-index ${z}`);
                }
            },
        },
        {
            trigger: ".o-dwo-editorBox.o-dwo-expanded",
            run: function () {
                const box = document.querySelector(".o-dwo-editorBox.o-dwo-expanded").getBoundingClientRect();
                if (Math.abs(box.width - window.innerWidth) > 2 || Math.abs(box.height - window.innerHeight) > 2) {
                    throw new Error(`The expanded body does not fill the screen: ${box.width}x${box.height}`);
                }
            },
        },
        { trigger: EDITOR, run: "click" },
        { trigger: EDITOR, run: "text Written on the whole screen" },
        { trigger: ".o-dwo-collapseBtn", run: "click" },
        { trigger: ".o-dwo-emailComposer:not(:has(.o-dwo-expanded))" },
        {
            // back to the form: the statusbar has its own z-index again
            trigger: ".o-dwo-fakeStatusbar",
            run: function () {
                const z = getComputedStyle(document.querySelector(".o-dwo-fakeStatusbar")).zIndex;
                if (z !== "1020") {
                    throw new Error(`The statusbar did not get its z-index back: ${z}`);
                }
                document.querySelector(".o-dwo-fakeForm").remove();
            },
        },
        { trigger: `${EDITOR}:contains('Written on the whole screen')` },
        // Esc brings it back too
        { trigger: ".o-dwo-expandBtn", run: "click" },
        { trigger: ".o-dwo-editorBox.o-dwo-expanded", run: function () { window.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true })); } },
        { trigger: ".o-dwo-emailComposer:not(:has(.o-dwo-expanded))" },
        // closing the form brings the messages back
        { trigger: ".o-dwo-closeBtn", run: "click" },
        { trigger: ".o_Chatter:not(:has(.o-dwo-emailComposer))" },
        {
            trigger: ".o_Chatter_scrollPanel",
            run: function () {
                const display = getComputedStyle(document.querySelector(".o_Chatter_scrollPanel")).display;
                if (display === "none") {
                    throw new Error("The messages should be visible again once the form is closed");
                }
            },
        },
        { trigger: ".o_Message:contains('History message')" },
    ],
});

// The approver opens the email and decides: three buttons, each with a popup.
tours.add("dwo_mail_compose_approver_approves", {
    test: true,
    steps: () => [
        { trigger: ".o_form_view .o_statusbar_status" },
        { trigger: ".o_form_view:contains('Please check this text')" },
        { trigger: ".o_form_statusbar button[name='action_open_reject']" },
        { trigger: ".o_form_statusbar button[name='action_open_reassign']" },
        { trigger: ".o_form_statusbar button[name='action_open_approve']", run: "click" },
        { trigger: ".modal textarea", run: "text Looks good" },
        { trigger: ".modal button:contains('Confirm')", run: "click" },
        { trigger: ".o_form_view .o_arrow_button.btn-primary:contains('Approved and sent')" },
        // the legacy form of Odoo 15 hides a button with a class, it does not remove it
        { trigger: ".o_form_statusbar:not(:has(button[name='action_open_approve']:not(.o_invisible_modifier)))" },
    ],
});

// Clicking the rows of the list again and again must never create an email.
tours.add("dwo_mail_compose_rapid_clicks", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: ".o-dwo-emailRow:contains('Mail A')" },
        { trigger: ".o-dwo-emailRow:contains('Mail B')" },
        { trigger: ".o-dwo-emailRow:contains('Mail C')" },
        {
            trigger: ".o-dwo-emailRows",
            run: async function () {
                const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
                const names = ["Mail B", "Mail C", "Mail A", "Mail C", "Mail B", "Mail A", "Mail A", "Mail B", "Mail C", "Mail A"];
                for (const [i, name] of names.entries()) {
                    const row = [...document.querySelectorAll(".o-dwo-emailRow")].find((r) => r.textContent.includes(name));
                    row?.click();
                    // from "at once" to "a moment later": the clicks overlap with the loading of the previous one
                    await sleep([0, 20, 60, 120, 300][i % 5]);
                }
                await sleep(4000);
            },
        },
        {
            trigger: ".o-dwo-emailRows",
            run: async function () {
                const resId = parseInt(new URLSearchParams(location.hash.slice(1)).get("id"));
                const count = await rpc("/web/dataset/call_kw/dwo.mail.email/search_count", {
                    model: "dwo.mail.email", method: "search_count",
                    args: [[["res_id", "=", resId], ["res_model", "=", "res.partner"]]], kwargs: {},
                });
                if (count !== 3) {
                    throw new Error(`Clicking the list created emails: ${count} instead of 3`);
                }
            },
        },
    ],
});

// Deleting the email in the form leaves the defaults on screen; nothing is created until the user writes.
tours.add("dwo_mail_compose_delete_then_idle", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: "#dwo_subject:value(Mail B)" },
        { trigger: ".o-dwo-deleteDraft", run: "click" },
        { trigger: ".modal .modal-footer button:contains('Delete')", run: "click" },
        { trigger: ".o-dwo-emailComposer:contains('No draft yet')" },
        {
            trigger: ".o-dwo-emailRow:contains('Mail A')",
            run: async function () {
                await new Promise((resolve) => setTimeout(resolve, 4500));
            },
        },
        {
            trigger: ".o-dwo-emailRow:contains('Mail A')",
            run: async function () {
                const resId = parseInt(new URLSearchParams(location.hash.slice(1)).get("id"));
                const count = await rpc("/web/dataset/call_kw/dwo.mail.email/search_count", {
                    model: "dwo.mail.email", method: "search_count",
                    args: [[["res_id", "=", resId], ["res_model", "=", "res.partner"]]], kwargs: {},
                });
                if (count !== 1) {
                    throw new Error(`Nothing should be created after a deletion, found ${count} emails instead of 1`);
                }
            },
        },
        // clicking the remaining row then opens it, still without creating anything
        { trigger: ".o-dwo-emailRow:contains('Mail A')", run: "click" },
        { trigger: "#dwo_subject:value(Mail A)" },
    ],
});

// Close always keeps what was typed, however fast; and a form nobody wrote in stores nothing.
tours.add("dwo_mail_compose_close_saves", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: ".o-dwo-emailComposer:contains('No draft yet')" },
        // opened and closed without writing: nothing is created
        { trigger: ".o-dwo-closeBtn", run: "click" },
        { trigger: ".o_Chatter:not(:has(.o-dwo-emailComposer))" },
        {
            trigger: ".o-mail-Chatter-dwoSendEmail:not(:has(.o-dwo-draftDot))",
            run: async function () {
                const resId = parseInt(new URLSearchParams(location.hash.slice(1)).get("id"));
                const count = await rpc("/web/dataset/call_kw/dwo.mail.email/search_count", {
                    model: "dwo.mail.email", method: "search_count",
                    args: [[["res_id", "=", resId], ["res_model", "=", "res.partner"]]], kwargs: {},
                });
                if (count !== 0) {
                    throw new Error(`Opening and closing the form must create nothing, found ${count}`);
                }
            },
        },
        // only the body was typed, Close at once
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: EDITOR, run: "click" },
        { trigger: EDITOR, run: "text Only the body" },
        { trigger: ".o-dwo-closeBtn", run: "click" },
        { trigger: ".o_Chatter:not(:has(.o-dwo-emailComposer))" },
        { trigger: ".o-mail-Chatter-dwoSendEmail .o-dwo-draftDot" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: `${EDITOR}:contains('Only the body')` },
        { trigger: ".o-dwo-emailComposer:contains('Draft saved')" },
        // an address typed but not validated yet, Close at once
        { trigger: ".o-dwo-newEmail", run: "click" },
        { trigger: ".o-dwo-emailRow.active:contains('(No subject)')" },
        { trigger: "#dwo_to", run: "text pending.person@acme.example" },
        { trigger: ".o-dwo-closeBtn", run: "click" },
        { trigger: ".o_Chatter:not(:has(.o-dwo-emailComposer))" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: "[data-field='to'] .o-dwo-chip[data-email='pending.person@acme.example']" },
        // a second new email: typed, Close at once
        // the editor is made again for the new email, and it starts a moment later: wait for the new one
        { trigger: EDITOR, run: function () { window.dwoPreviousEditor = this.$anchor[0]; } },
        { trigger: ".o-dwo-newEmail", run: "click" },
        // the list has its third row once the new email is stored
        { trigger: ".o-dwo-emailRows:has(.o-dwo-emailRow:nth-child(3)) .o-dwo-emailRow.active:contains('(No subject)')" },
        {
            trigger: EDITOR,
            async run() {
                for (let i = 0; i < 100; i++) {
                    const editor = document.querySelector(EDITOR);
                    if (editor && editor !== window.dwoPreviousEditor && editor.isConnected) {
                        return;
                    }
                    await new Promise((resolve) => setTimeout(resolve, 100));
                }
                throw new Error("The editor of the new email did not start");
            },
        },
        { trigger: EDITOR, run: "click" },
        { trigger: EDITOR, run: "text Third body" },
        { trigger: ".o-dwo-closeBtn", run: "click" },
        { trigger: ".o_Chatter:not(:has(.o-dwo-emailComposer))" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: `${EDITOR}:contains('Third body')` },
        // three emails, no more
        {
            trigger: ".o-dwo-emailRows",
            run: async function () {
                const resId = parseInt(new URLSearchParams(location.hash.slice(1)).get("id"));
                const count = await rpc("/web/dataset/call_kw/dwo.mail.email/search_count", {
                    model: "dwo.mail.email", method: "search_count",
                    args: [[["res_id", "=", resId], ["res_model", "=", "res.partner"]]], kwargs: {},
                });
                if (count !== 3) {
                    throw new Error(`Expected 3 emails, found ${count}`);
                }
            },
        },
    ],
});

// An approver chosen in the "Search more..." popup keeps its name in the field.
tours.add("dwo_mail_compose_approver_search_more", {
    test: true,
    steps: () => [
        { trigger: ".o_Chatter" },
        { trigger: ".o-mail-Chatter-dwoSendEmail", run: "click" },
        { trigger: "#dwo_to", run: "text search.customer@acme.example," },
        { trigger: "[data-field='to'] .o-dwo-chip[data-email='search.customer@acme.example']" },
        { trigger: ".o-dwo-sendBtn", run: "click" },
        { trigger: ".o-dwo-requestApproval", run: "click" },
        // Odoo 15 has no "Search more..." popup: the person is found by typing the name in the field
        { trigger: "#dwo_approver_input", run: "text Searchable User 3" },
        { trigger: ".o-dwo-approverMatches .dropdown-item:contains('Searchable User 3')", run: "click" },
        // back in the approval popup: the person is listed with a name, and can be asked
        { trigger: ".modal .o-dwo-approverChip:contains('Searchable User 3')" },
        {
            trigger: ".modal .o-dwo-approverChip",
            run: function () {
                for (const chip of document.querySelectorAll(".o-dwo-approverChip")) {
                    if (!chip.textContent.trim()) {
                        throw new Error("An approver chip has no name");
                    }
                }
            },
        },
        { trigger: ".modal .o-dwo-approvalConfirm:not(:disabled)", run: "click" },
        { trigger: ".o-dwo-pendingNote:contains('Searchable User 3')" },
    ],
});

