/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';
import { clear } from '@mail/model/model_field_command';

registerPatch({
    name: 'Thread',
    fields: {
        /** The id of the chip chosen (the messages it shows are the only ones loaded), false for all. */
        dwoFilter: attr({ default: false }),
        /** The text searched in the messages (the server searches), empty for no search. */
        dwoSearch: attr({ default: '' }),
        /**
         * While a chip is chosen or a text searched, the server only returns the messages that fit (Load more included).
         * @override
         */
        fetchMessagesParams: {
            compute() {
                const params = this._super();
                const extra = {};
                if (this.dwoFilter) {
                    extra.dwo_filter_id = this.dwoFilter;
                }
                if (this.dwoSearch) {
                    extra.dwo_search = this.dwoSearch;
                }
                return { ...params, ...extra };
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
         * Search a text in the messages, together with the chip chosen.
         *
         * @param {string} text
         */
        dwoSetSearch(text) {
            text = (text || '').trim();
            if (this.dwoSearch === text) {
                return;
            }
            this.update({ dwoSearch: text });
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
            if (this.dwoFilter || this.dwoSearch) {
                this.update({ dwoFilter: false, dwoSearch: '' });
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
