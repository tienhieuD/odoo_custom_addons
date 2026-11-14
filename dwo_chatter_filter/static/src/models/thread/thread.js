/** @odoo-module **/

import { registerFieldPatchModel, registerInstancePatchModel } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';
import { unlinkAll } from '@mail/model/model_field_command';

const NAME = 'dwo_chatter_filter/static/src/models/thread/thread.js';

registerFieldPatchModel('mail.thread', NAME, {
    /** The id of the chip chosen (the messages it shows are the only ones loaded), false for all. */
    dwoFilter: attr({ default: false }),
    /** The text searched in the messages (the server searches), empty for no search. */
    dwoSearch: attr({ default: '' }),
});

registerInstancePatchModel('mail.thread', NAME, {
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
        this._dwoReloadCache();
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
        this._dwoReloadCache();
    },

    /**
     * Load the messages of the chosen chip again (a message arrived: the server says if it belongs).
     */
    dwoReload() {
        this._dwoReloadCache();
    },

    /**
     * Back to all the messages, for the next time the record is opened.
     */
    dwoReset() {
        if (this.dwoFilter || this.dwoSearch) {
            this.update({ dwoFilter: false, dwoSearch: '' });
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
     * While a chip is chosen or a text searched, the server only returns the messages that fit (Load more included).
     *
     * @override
     */
    _computeFetchMessagesParams() {
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
});
