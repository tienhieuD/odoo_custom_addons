import { Chatter } from "@mail/chatter/web_portal/chatter";
import { patch } from "@web/core/utils/patch";

import { DwoMessageFilter } from "./filter/dwo_message_filter";

patch(Chatter, {
    components: { ...Chatter.components, DwoMessageFilter },
});
