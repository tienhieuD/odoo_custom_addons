import { fields } from "@mail/core/common/record";
import { Thread as ThreadModel } from "@mail/core/common/thread_model";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";

patch(ThreadModel.prototype, {
    setup() {
        super.setup(...arguments);
        /** The id of the chip chosen (the messages it shows are the only ones loaded), false for all. */
        this.dwoFilter = fields.Attr(false);
    },

    /** While a chip is chosen, the server only returns the messages of that chip (Load more included). */
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
                dwo_filter_id: this.dwoFilter,
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

    /** Show the messages of one chip (false: all of them), loaded from the server. */
    async dwoSetFilter(chipId) {
        chipId = chipId || false;
        if (this.dwoFilter === chipId) {
            return;
        }
        this.dwoFilter = chipId;
        this.dwoForgetMessages();
        await this.fetchNewMessages();
    },

    /** Load the messages of the chosen chip again (a message arrived: the server says if it belongs). */
    async dwoReload() {
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
