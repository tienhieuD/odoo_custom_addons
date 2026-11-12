/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';
import { clear } from '@mail/model/model_field_command';

registerPatch({
    name: 'Thread',
    fields: {
        /** The id of the chip chosen (the messages it shows are the only ones loaded), false for all. */
        dwoFilter: attr({ default: false }),
        /**
         * While a chip is chosen, the server only returns the messages of that chip (Load more included).
         * @override
         */
        fetchMessagesParams: {
            compute() {
                const params = this._super();
                if (this.dwoFilter) {
                    return { ...params, dwo_filter_id: this.dwoFilter };
                }
                return params;
            },
        },
    },
    recordMethods: {
        /**
         * Show the messages of one chip (false: all of them): they are loaded again from the server.
         *
         * @param {number|false} chipId
         */
        dwoSetFilter(chipId) {
            chipId = chipId || false;
            if (this.dwoFilter === chipId) {
                return;
            }
            this.update({ dwoFilter: chipId });
            this._dwoReloadMainCache();
        },
        /**
         * Load the messages of the chosen chip again (a message arrived: the server says if it belongs).
         */
        dwoReload() {
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
