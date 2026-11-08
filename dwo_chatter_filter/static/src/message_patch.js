import { Message } from "@mail/core/common/message_model";
import { patch } from "@web/core/utils/patch";

/**
 * The kind of a message, for the badges of the chatter. Every message is in exactly one kind, checked in
 * this order. The same rule is written in Python (``_dwo_category_domain``): keep them equal.
 *
 *   tracking    a field changed (it carries tracking values)
 *   email       an email received or sent
 *   note        a comment with the subtype Note (Log note)
 *   discussion  a comment with the subtype Discussions (Send message)
 *   other       everything else
 */
export function dwoCategoryOf(message) {
    if (message.trackingValues?.length) {
        return "tracking";
    }
    if (["email", "email_outgoing"].includes(message.message_type)) {
        return "email";
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
    get dwoCategory() {
        return dwoCategoryOf(this);
    },
});
