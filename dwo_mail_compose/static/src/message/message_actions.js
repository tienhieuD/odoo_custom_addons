import { registerMessageAction } from "@mail/core/common/message_actions";
import { _t } from "@web/core/l10n/translation";

// Reply and Forward on emails. They open the inline email form of the chatter,
// never the internal composer.
registerMessageAction("dwo-email-reply", {
    condition: ({ message, owner }) =>
        Boolean(owner?.env.inChatter?.dwoOpenEmail) && message.isDwoEmail,
    icon: "fa fa-reply-all",
    name: _t("Reply by email"),
    onSelected: ({ message, owner }) =>
        owner.env.inChatter.dwoOpenEmail({ mode: "reply", refMessageId: message.id }),
    sequence: 21,
});

registerMessageAction("dwo-email-forward", {
    condition: ({ message, owner }) =>
        Boolean(owner?.env.inChatter?.dwoOpenEmail) && message.isDwoEmail,
    icon: "fa fa-share",
    name: _t("Forward by email"),
    onSelected: ({ message, owner }) =>
        owner.env.inChatter.dwoOpenEmail({ mode: "forward", refMessageId: message.id }),
    sequence: 22,
});
