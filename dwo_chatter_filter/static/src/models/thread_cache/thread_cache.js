odoo.define('dwo_chatter_filter/static/src/models/thread_cache/thread_cache.js', function (require) {
'use strict';

const { registerInstancePatchModel } = require('mail/static/src/model/model_core.js');

/**
 * @param {mail.thread_cache} cache
 * @returns {string|undefined} the kind of message of a cache made by the filter
 */
function dwoCategoryOfCache(cache) {
    let domain;
    try {
        domain = JSON.parse(cache.stringifiedDomain);
    } catch (_e) {
        return undefined;
    }
    if (domain.length === 1 && domain[0][0] === 'dwo_category') {
        return domain[0][2];
    }
    return undefined;
}

registerInstancePatchModel('mail.thread_cache', 'dwo_chatter_filter/static/src/models/thread_cache/thread_cache.js', {
    /**
     * The cache of a kind of message follows the new messages of the thread (bus) like the main cache does,
     * and hides the ones of another kind. A search cache of the core does not follow them.
     *
     * @override
     */
    _computeMessages() {
        const category = dwoCategoryOfCache(this);
        if (!category) {
            return this._super();
        }
        if (!this.thread) {
            return [['unlink-all']];
        }
        const newer = this.lastFetchedMessage
            ? this.thread.messages.filter((message) => message.id > this.lastFetchedMessage.id)
            : this.thread.messages;
        const messages = this.fetchedMessages.concat(newer).filter((message) => message.dwoCategory === category);
        return [['replace', messages]];
    },
});

});
