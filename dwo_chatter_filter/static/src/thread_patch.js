import { fields } from "@mail/core/common/record";
import { Thread } from "@mail/core/common/thread";
import { Thread as ThreadModel } from "@mail/core/common/thread_model";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";

patch(ThreadModel.prototype, {
    setup() {
        super.setup(...arguments);
        /** The kind of message shown, false for all of them. */
        this.dwoFilter = fields.Attr(false);
        /** The number of messages: { all, tracking, email, note, discussion, other } */
        this.dwoCounts = fields.Attr(null);
    },

    /** While a kind is chosen, the server only returns that kind (Load more included). */
    async fetchMessagesData({ after, around, before } = {}) {
        if (!this.dwoFilter) {
            return super.fetchMessagesData(...arguments);
        }
        return await rpc(this.getFetchRoute(), {
            ...this.getFetchParams(),
            fetch_params: {
                limit:
                    !around && around !== 0 ? this.store.FETCH_LIMIT : this.store.FETCH_LIMIT * 2,
                after,
                around,
                before,
                dwo_category: this.dwoFilter,
            },
        });
    },

    /** Forget the messages that were loaded: they are loaded again for the new filter. */
    dwoForgetMessages() {
        this.messages = [];
        this.isLoaded = false;
        this.loadOlder = false;
        this.loadNewer = false;
    },

    /** Show one kind of message (false: all of them), loaded from the server. */
    async dwoSetFilter(category) {
        category = category || false;
        if (this.dwoFilter === category) {
            return;
        }
        this.dwoFilter = category;
        this.dwoForgetMessages();
        await this.fetchNewMessages();
    },

    /** Back to all the messages, for the next time the record is opened. */
    dwoReset() {
        if (this.dwoFilter) {
            this.dwoFilter = false;
            this.dwoForgetMessages();
        }
    },
});

// A message that arrives while a kind is chosen (bus) is hidden when it is of another kind.
patch(Thread.prototype, {
    get orderedMessages() {
        const messages = super.orderedMessages;
        const filter = this.props.thread.dwoFilter;
        return filter ? messages.filter((message) => message.dwoCategory === filter) : messages;
    },
});
