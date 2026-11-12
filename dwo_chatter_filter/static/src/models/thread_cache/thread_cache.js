odoo.define('dwo_chatter_filter/static/src/models/thread_cache/thread_cache.js', function (require) {
'use strict';

const { registerInstancePatchModel } = require('mail/static/src/model/model_core.js');

/**
 * @param {mail.thread_cache} cache
 * @returns {boolean} whether the cache was made by a chip of the filter (its domain is the leaf dwo_filter_id)
 */
function isChipCache(cache) {
    let domain;
    try {
        domain = JSON.parse(cache.stringifiedDomain);
    } catch (_e) {
        return false;
    }
    return domain.length === 1 && domain[0][0] === 'dwo_filter_id';
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
