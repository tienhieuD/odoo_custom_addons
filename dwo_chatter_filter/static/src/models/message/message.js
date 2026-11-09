/** @odoo-module **/

import {
    registerClassPatchModel,
    registerFieldPatchModel,
    registerInstancePatchModel,
} from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';

const NAME = 'dwo_chatter_filter/static/src/models/message/message.js';

/**
 * The kind of a message, for the badges of the chatter. Every message is in exactly one kind, checked in
 * this order. The same rule is written in Python (``_dwo_category_domain``): keep them equal.
 *
 *   tracking    a field changed (it carries tracking values)
 *   email       an email received or sent
 *   activity    the message left by a done activity (subtype Activities)
 *   note        a comment with the subtype Note (Log note)
 *   discussion  a comment with the subtype Discussions (Send message)
 *   other       everything else
 */
export function dwoCategoryOf(message) {
    if (message.tracking_value_ids && message.tracking_value_ids.length) {
        return 'tracking';
    }
    if (message.message_type === 'email') {
        return 'email';
    }
    if (message.dwoIsActivity) {
        return 'activity';
    }
    if (message.message_type === 'comment') {
        if (message.is_note) {
            return 'note';
        }
        if (message.is_discussion) {
            return 'discussion';
        }
    }
    return 'other';
}

registerFieldPatchModel('mail.message', NAME, {
    /** Sent by the server: the message was left by a done activity. */
    dwoIsActivity: attr({ default: false }),
    dwoCategory: attr({
        compute: '_computeDwoCategory',
    }),
});

registerClassPatchModel('mail.message', NAME, {
    /**
     * @override
     */
    convertData(data) {
        const res = this._super(data);
        if ('dwo_is_activity' in data) {
            res.dwoIsActivity = data.dwo_is_activity;
        }
        return res;
    },
});

registerInstancePatchModel('mail.message', NAME, {
    /**
     * @private
     * @returns {string}
     */
    _computeDwoCategory() {
        return dwoCategoryOf(this);
    },
});
