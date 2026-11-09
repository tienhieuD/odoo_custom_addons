/** @odoo-module **/

import { registerFieldPatchModel, registerInstancePatchModel } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';
import { unlinkAll } from '@mail/model/model_field_command';

const NAME = 'dwo_chatter_filter/static/src/models/thread/thread.js';

registerFieldPatchModel('mail.thread', NAME, {
    /** The kind of message shown, false for all of them. */
    dwoFilter: attr({ default: false }),
});

registerInstancePatchModel('mail.thread', NAME, {
    /**
     * Show one kind of message (false: all of them): the messages are loaded again from the server.
     *
     * @param {string|false} category
     */
    dwoSetFilter(category) {
        category = category || false;
        if (this.dwoFilter === category) {
            return;
        }
        this.update({ dwoFilter: category });
        this._dwoReloadCache();
    },

    /**
     * Back to all the messages, for the next time the record is opened.
     */
    dwoReset() {
        if (this.dwoFilter) {
            this.update({ dwoFilter: false });
            this._dwoReloadCache();
        }
    },

    /**
     * Forget the messages that were loaded: they are loaded again with the new parameters.
     *
     * @private
     */
    _dwoReloadCache() {
        const cache = this.cache;
        if (!cache) {
            return;
        }
        cache.update({
            fetchedMessages: unlinkAll(),
            isAllHistoryLoaded: false,
            hasLoadingFailed: false,
            isLoaded: false,
            isCacheRefreshRequested: true,
        });
    },

    /**
     * While a kind is chosen, the server only returns that kind (Load more included).
     *
     * @override
     */
    _computeFetchMessagesParams() {
        const params = this._super();
        if (this.dwoFilter) {
            return { ...params, dwo_category: this.dwoFilter };
        }
        return params;
    },
});
