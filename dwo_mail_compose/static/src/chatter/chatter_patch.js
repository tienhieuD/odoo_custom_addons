/* @odoo-module */

import { Chatter } from "@mail/core/web/chatter";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useChildSubEnv, useEffect, useState } from "@odoo/owl";

import { DwoEmailComposer } from "../composer/dwo_email_composer";

patch(Chatter, {
    components: { ...Chatter.components, DwoEmailComposer },
});

patch(Chatter.prototype, {
    setup() {
        super.setup();
        // rememberedEmailId: the email the user opened last on this screen. It lives as long as this
        // chatter does: leaving the screen or reloading the page forgets it.
        this.dwo = useState({ mode: false, refMessageId: false, key: 0, hasDraft: false, rememberedEmailId: false });
        this.dwoThreadId = undefined;
        // Odoo 17: inChatter is only true, the function for Reply and Forward goes in the env of the children
        useChildSubEnv({ dwoOpenEmail: this.dwoOpenEmail.bind(this) });
        this.dwoOrm = useService("orm");
        useEffect(
            () => {
                this.dwoRefreshDraft();
            },
            () => [this.state.thread?.id, this.state.composerType]
        );
        useEffect(
            () => {
                // another record in the same screen: the choice made on the previous one is forgotten
                const id = this.state.thread?.id;
                if (this.dwoThreadId !== undefined && this.dwoThreadId !== id) {
                    this.dwo.rememberedEmailId = false;
                }
                this.dwoThreadId = id;
            },
            () => [this.state.thread?.id]
        );
    },

    async dwoRefreshDraft() {
        const thread = this.state.thread;
        if (!thread?.id || this.state.composerType === "email") {
            return;
        }
        this.dwo.hasDraft = await this.dwoOrm.call("dwo.mail.composer", "has_draft", [
            thread.model,
            thread.id,
        ]);
    },

    /** The Send email button: opens the form on the saved draft, or on the defaults. */
    dwoToggleEmail() {
        this.dwo.mode = false;
        this.dwo.refMessageId = false;
        this.dwo.key++;
        this.toggleComposer("email");
    },

    /** Reply or Forward on a message: a new email, the others are left as they are. */
    dwoOpenEmail({ mode, refMessageId }) {
        this.dwo.mode = mode;
        this.dwo.refMessageId = refMessageId;
        this.dwo.key++;
        // Odoo 18 has no "force": a click on the same mode would close it, the form is opened directly
        this.state.isSearchOpen = false;
        this.state.composerType = "email";
    },

    dwoOnEmailChange(emailId) {
        this.dwo.rememberedEmailId = emailId;
    },

    dwoOnEmailClose() {
        this.state.composerType = false;
    },

    dwoOnEmailSent() {
        this.state.composerType = false;
        this.dwo.hasDraft = false;
        this.threadService.fetchNewMessages(this.state.thread);
    },
});
