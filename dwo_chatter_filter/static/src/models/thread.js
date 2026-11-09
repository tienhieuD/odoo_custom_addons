/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';
import { clear } from '@mail/model/model_field_command';

registerPatch({
    name: 'Thread',
    fields: {
        /** The kind of message shown, false for all of them. */
        dwoFilter: attr({ default: false }),
        /**
         * While a kind is chosen, the server only returns that kind (Load more included).
         * @override
         */
        fetchMessagesParams: {
            compute() {
                const params = this._super();
                if (this.dwoFilter) {
                    return { ...params, dwo_category: this.dwoFilter };
                }
                return params;
            },
        },
    },
    recordMethods: {
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
            this._dwoReloadMainCache();
        },
        /**
         * Back to all the messages, for the next time the record is opened.
         */
        dwoReset() {
            if (this.dwoFilter) {
                this.update({ dwoFilter: false });
                this._dwoReloadMainCache();
            }
        },
        /**
         * Forget the messages that were loaded: they are loaded again with the new parameters.
         *
         * @private
         */
        _dwoReloadMainCache() {
            const cache = this.cache;
            if (!cache) {
                return;
            }
            cache.update({
                rawFetchedMessages: clear(),
                isAllHistoryLoaded: false,
                hasLoadingFailed: false,
                isLoaded: false,
                isCacheRefreshRequested: true,
            });
        },
    },
});
