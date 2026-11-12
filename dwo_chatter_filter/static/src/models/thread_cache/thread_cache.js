/** @odoo-module **/

import { registerInstancePatchModel } from '@mail/model/model_core';
import { replace } from '@mail/model/model_field_command';

registerInstancePatchModel('mail.thread_cache', 'dwo_chatter_filter/static/src/models/thread_cache/thread_cache.js', {
    /**
     * Odoo 15 shows in the main cache the messages it fetched and every newer message of the thread that is in
     * the store. While a chip is chosen only the messages the server returned for that chip are shown: the
     * browser cannot tell by itself which ones the chip would show. A message that arrives is asked for again
     * (see DwoMessageFilter) and shows up if the chip holds it.
     *
     * @override
     */
    _computeMessages() {
        const result = this._super();
        if (!this.thread || !this.thread.dwoFilter) {
            return result;
        }
        return replace(this.fetchedMessages);
    },
});
