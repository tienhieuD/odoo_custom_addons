odoo.define('dwo_chatter_filter/static/src/models/thread_cache/thread_cache.js', function (require) {
'use strict';

const { registerInstancePatchModel } = require('mail/static/src/model/model_core.js');

/**
 * @param {mail.thread_cache} cache
 * @returns {boolean} whether the cache was made by a chip of the filter (its domain has only the leaves dwo_filter_id and dwo_search)
 */
function isChipCache(cache) {
    let domain;
    try {
        domain = JSON.parse(cache.stringifiedDomain);
    } catch (_e) {
        return false;
    }
    return domain.length > 0 && domain.every((leaf) => leaf[0] === 'dwo_filter_id' || leaf[0] === 'dwo_search');
}

registerInstancePatchModel('mail.thread_cache', 'dwo_chatter_filter/static/src/models/thread_cache/thread_cache.js', {
    /**
     * The cache of a chip shows only the messages the server returned for that chip: the browser cannot tell
     * by itself which ones the chip would show. A message that arrives is asked for again (see
     * DwoMessageFilter) and shows up if the chip holds it.
     *
     * @override
     */
    _computeMessages() {
        if (!isChipCache(this)) {
            return this._super();
        }
        return [['replace', this.fetchedMessages]];
    },
});

});
