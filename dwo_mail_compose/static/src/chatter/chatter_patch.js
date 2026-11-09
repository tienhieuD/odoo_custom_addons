import { Chatter } from "@mail/chatter/web_portal_project/chatter";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { proxy, useLayoutEffect } from "@odoo/owl";

import { DwoEmailComposer } from "../composer/dwo_email_composer";

patch(Chatter, {
    components: { ...Chatter.components, DwoEmailComposer },
});

patch(Chatter.prototype, {
    setup() {
        super.setup();
        // rememberedEmailId: the email the user opened last on this screen. It lives as long as this
        // chatter does: leaving the screen or reloading the page forgets it.
        this.dwo = proxy({ mode: false, refMessageId: false, key: 0, hasDraft: false, rememberedEmailId: false });
        this.dwoThreadId = undefined;
        this.dwoOrm = useService("orm");
        useLayoutEffect(
            () => {
                this.dwoRefreshDraft();
            },
            () => [this.state.thread?.id, this.state.composerType]
        );
        useLayoutEffect(
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

    get subEnv() {
        const env = super.subEnv;
        env.inChatter.dwoOpenEmail = this.dwoOpenEmail.bind(this);
        return env;
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
        this.toggleComposer("email", { force: true });
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
        this.state.thread.fetchNewMessages();
    },
});
