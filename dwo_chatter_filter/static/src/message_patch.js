import { Message } from "@mail/core/common/message_model";
import { fields } from "@mail/model/export";
import { patch } from "@web/core/utils/patch";

/**
 * The kind of a message, for the badges of the chatter. Every message is in exactly one kind, checked in
 * this order. The same rule is written in Python (``_dwo_category_domain``): keep them equal.
 *
 *   tracking    a field changed (its type is tracking)
 *   email       an email received or sent
 *   activity    the message left by a done activity (subtype Activities)
 *   note        a comment with the subtype Note (Log note)
 *   discussion  a comment with the subtype Discussions (Send message)
 *   other       everything else
 */
export function dwoCategoryOf(message) {
    if (message.message_type === "tracking") {
        return "tracking";
    }
    if (["email", "email_outgoing"].includes(message.message_type)) {
        return "email";
    }
    if (message.dwo_is_activity) {
        return "activity";
    }
    if (message.message_type === "comment") {
        if (message.isNote) {
            return "note";
        }
        if (message.isDiscussion) {
            return "discussion";
        }
    }
    return "other";
}

patch(Message.prototype, {
    setup() {
        super.setup(...arguments);
        /** Sent by the server: the message was left by a done activity. */
        this.dwo_is_activity = fields.Attr(false);
    },

    get dwoCategory() {
        return dwoCategoryOf(this);
    },
});
