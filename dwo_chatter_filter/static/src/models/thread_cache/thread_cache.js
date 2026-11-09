/** @odoo-module **/

import { registerInstancePatchModel } from '@mail/model/model_core';
import { replace } from '@mail/model/model_field_command';

registerInstancePatchModel('mail.thread_cache', 'dwo_chatter_filter/static/src/models/thread_cache/thread_cache.js', {
    /**
     * A message that arrives while a kind is chosen (bus) is hidden when it is of another kind.
     *
     * @override
     */
    _computeMessages() {
        const result = this._super();
        if (!this.thread || !this.thread.dwoFilter) {
            return result;
        }
        const messages = this.fetchedMessages.concat(
            this.lastFetchedMessage
                ? this.thread.messages.filter((message) => message.id > this.lastFetchedMessage.id)
                : this.thread.messages
        );
        return replace(messages.filter((message) => message.dwoCategory === this.thread.dwoFilter));
    },
});
