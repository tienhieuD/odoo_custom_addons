/* @odoo-module */

import { Thread } from "@mail/core/common/thread_model";
import { ThreadService } from "@mail/core/common/thread_service";
import { patch } from "@web/core/utils/patch";

const FETCH_LIMIT = 30;

patch(Thread.prototype, {
    setup() {
        super.setup(...arguments);
        /** The id of the chip chosen (the messages it shows are the only ones loaded), false for all. */
        this.dwoFilter = false;
    },
});

patch(ThreadService.prototype, {
    /** While a chip is chosen, the server only returns the messages of that chip (Load more included). */
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
                dwo_filter_id: thread.dwoFilter,
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

    /** Show the messages of one chip (false: all of them), loaded from the server. */
    async dwoSetFilter(thread, chipId) {
        chipId = chipId || false;
        if (thread.dwoFilter === chipId) {
            return;
        }
        thread.dwoFilter = chipId;
        this.dwoForgetMessages(thread);
        await this.fetchNewMessages(thread);
    },

    /** Load the messages of the chosen chip again (a message arrived: the server says if it belongs). */
    async dwoReload(thread) {
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
