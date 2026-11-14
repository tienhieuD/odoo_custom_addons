odoo.define('dwo_chatter_filter/static/src/models/chatter/chatter.js', function (require) {
'use strict';

const { registerFieldPatchModel, registerInstancePatchModel } = require('mail/static/src/model/model_core.js');
const { attr } = require('mail/static/src/model/model_field.js');

const NAME = 'dwo_chatter_filter/static/src/models/chatter/chatter.js';

registerFieldPatchModel('mail.chatter', NAME, {
    /** The id of the chip chosen (the messages it shows are the only ones loaded), false for all. */
    dwoFilter: attr({ default: false }),
    /** The text searched in all the messages of the record ('' for none). */
    dwoSearch: attr({ default: '' }),
});

registerInstancePatchModel('mail.chatter', NAME, {
    /**
     * Show the messages of one chip (false: all of them). Odoo 14 keeps one cache of messages for each domain
     * of the thread viewer: a domain with the leaf ("dwo_filter_id", "=", id) gives its own cache, loaded
     * from the server, where the server turns the leaf into the domain of the chip (see message_fetch).
     *
     * @param {number|false} chipId
     */
    dwoSetFilter(chipId) {
        chipId = chipId || false;
        if (this.dwoFilter === chipId || !this.threadViewer) {
            return;
        }
        this.update({ dwoFilter: chipId });
        this._dwoApplyDomain();
    },

    /**
     * Search a text in all the messages of the record (together with the chip chosen). The server does the
     * search, so it works on the messages that are not loaded too.
     *
     * @param {string} text
     */
    dwoSetSearch(text) {
        text = (text || '').trim();
        if (this.dwoSearch === text || !this.threadViewer) {
            return;
        }
        this.update({ dwoSearch: text });
        this._dwoApplyDomain();
    },

    /**
     * The chip and the text travel in the domain of the thread viewer as the leaves dwo_filter_id and
     * dwo_search, which the server turns into conditions (see message_fetch).
     */
    _dwoApplyDomain() {
        const domain = [];
        if (this.dwoFilter) {
            domain.push(['dwo_filter_id', '=', this.dwoFilter]);
        }
        if (this.dwoSearch) {
            domain.push(['dwo_search', '=', this.dwoSearch]);
        }
        this.threadViewer.update({ stringifiedDomain: JSON.stringify(domain) });
    },

    /**
     * Load the messages of the chosen chip again (a message arrived: the server says if it belongs).
     */
    dwoReload() {
        const cache = this.threadViewer && this.threadViewer.threadCache;
        if (!(this.dwoFilter || this.dwoSearch) || !cache) {
            return;
        }
        cache.update({
            fetchedMessages: [['unlink-all']],
            isAllHistoryLoaded: false,
            hasLoadingFailed: false,
            isLoaded: false,
            isCacheRefreshRequested: true,
        });
    },

    /**
     * Back to all the messages, for the next time the record is opened.
     */
    dwoReset() {
        if (this.dwoFilter || this.dwoSearch) {
            this.update({ dwoFilter: false, dwoSearch: '' });
            if (this.threadViewer) {
                this._dwoApplyDomain();
            }
        }
    },
});

});
