/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';

registerPatch({
    name: 'ThreadCache',
    fields: {
        /**
         * A message that arrives while a kind is chosen (bus) is hidden when it is of another kind.
         * @override
         */
        messages: {
            compute() {
                const messages = this._super();
                if (!this.thread || !this.thread.dwoFilter || !messages) {
                    return messages;
                }
                return messages.filter(message => message.dwoCategory === this.thread.dwoFilter);
            },
        },
    },
});
