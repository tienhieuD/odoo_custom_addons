/* @odoo-module */

import { Thread } from "@mail/core/common/thread_model";
import { ThreadService } from "@mail/core/common/thread_service";
import { patch } from "@web/core/utils/patch";

const FETCH_LIMIT = 30;

patch(Thread.prototype, {
    setup() {
        super.setup(...arguments);
        /** The kind of message shown, false for all of them. */
        this.dwoFilter = false;
    },

    // A message that arrives while a kind is chosen (bus) is hidden when it is of another kind.
    get nonEmptyMessages() {
        const messages = super.nonEmptyMessages;
        return this.dwoFilter
            ? messages.filter((message) => message.dwoCategory === this.dwoFilter)
            : messages;
    },
});

patch(ThreadService.prototype, {
    /** While a kind is chosen, the server only returns that kind (Load more included). */
    async fetchMessages(thread, { after, before } = {}) {
        if (!thread.dwoFilter) {
            return super.fetchMessages(...arguments);
        }
        thread.status = "loading";
        try {
            // ordered messages received: newest to oldest
            const { messages: rawMessages } = await this.rpc(this.getFetchRoute(thread), {
                ...this.getFetchParams(thread),
                limit: FETCH_LIMIT,
                after,
                before,
                dwo_category: thread.dwoFilter,
            });
            const messages = this.store.Message.insert(rawMessages.reverse(), { html: true });
            thread.isLoaded = true;
            return messages;
        } catch (e) {
            thread.hasLoadingFailed = true;
            throw e;
        } finally {
            thread.status = "ready";
        }
    },

    /** Forget the messages that were loaded: they are loaded again for the new filter. */
    dwoForgetMessages(thread) {
        thread.messages = [];
        thread.isLoaded = false;
        thread.loadOlder = false;
        thread.loadNewer = false;
    },

    /** Show one kind of message (false: all of them), loaded from the server. */
    async dwoSetFilter(thread, category) {
        category = category || false;
        if (thread.dwoFilter === category) {
            return;
        }
        thread.dwoFilter = category;
        this.dwoForgetMessages(thread);
        await this.fetchNewMessages(thread);
    },

    /** Back to all the messages, for the next time the record is opened. */
    dwoReset(thread) {
        if (thread.dwoFilter) {
            thread.dwoFilter = false;
            this.dwoForgetMessages(thread);
        }
    },
});
