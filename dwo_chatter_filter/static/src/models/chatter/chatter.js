odoo.define('dwo_chatter_filter/static/src/models/chatter/chatter.js', function (require) {
'use strict';

const { registerFieldPatchModel, registerInstancePatchModel } = require('mail/static/src/model/model_core.js');
const { attr } = require('mail/static/src/model/model_field.js');

const NAME = 'dwo_chatter_filter/static/src/models/chatter/chatter.js';

registerFieldPatchModel('mail.chatter', NAME, {
    /** The id of the chip chosen (the messages it shows are the only ones loaded), false for all. */
    dwoFilter: attr({ default: false }),
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
        this.threadViewer.update({
            stringifiedDomain: chipId ? JSON.stringify([['dwo_filter_id', '=', chipId]]) : '[]',
        });
    },

    /**
     * Load the messages of the chosen chip again (a message arrived: the server says if it belongs).
     */
    dwoReload() {
        const cache = this.threadViewer && this.threadViewer.threadCache;
        if (!this.dwoFilter || !cache) {
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
        if (this.dwoFilter) {
            this.dwoSetFilter(false);
        }
    },
});

});
