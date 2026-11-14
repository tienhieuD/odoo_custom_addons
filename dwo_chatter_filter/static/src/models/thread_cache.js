/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';

registerPatch({
    name: 'ThreadCache',
    fields: {
        /**
         * Odoo 16 shows in the main cache every message of the thread that is in the store, next to the ones
         * it fetched. While a chip is chosen only the messages the server returned for that chip are shown:
         * the browser cannot tell by itself which ones the chip would show. A message that arrives is asked
         * for again (see DwoMessageFilter) and shows up if the chip holds it.
         * @override
         */
        messages: {
            compute() {
                const messages = this._super();
                if (!this.thread || (!this.thread.dwoFilter && !this.thread.dwoSearch) || !messages) {
                    return messages;
                }
                return messages.filter(message => this.rawFetchedMessages.includes(message));
            },
        },
    },
});
